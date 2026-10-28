"""Builds a git repository of Portuguese law from the Diário da República (diariodarepublica.pt), in which every amending
act is one commit, dated the day its change took effect.

    python -X utf8 scripts/portugal-law/build.py [--repo ../portugal-law] [--today 2026-10-28] [--offline]
                                                 [--verify-rebuild]

The Diário da República (DR), published by the Imprensa Nacional-Casa da Moeda (INCM), keeps consolidated texts of the
main acts (Legislação Consolidada): every provision in every version, each version with the day it took effect, and an
amendment timeline naming, for each amending act, the provision versions it made. source.py reads those, model.py
works out the text in force on each day, and this file writes the history: on each day a version takes effect, one
commit per amending act the DR names for it, then (labelled) the changes no single act explains.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

import model
import source

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMMITTER = ('Lexifina', 'portugal-law@lexifina.com')
PUBLISHER = ('Diário da República (INCM)', 'incm@diariodarepublica.invalid')
FUTURE = 'futuro'
CONSOLIDATED = 'https://diariodarepublica.pt/dr/legislacao-consolidada'

# The acts in the record: the DR's address of the consolidated text (type and key, whose last number is the fragment
# id of the whole act), a folder, a short name, the day the act first took effect with the sentence that says so, and
# where the parts of the act go (the act's own articles and its annex, which for a code is the code itself).
ACTS = [
    {'tipo': 'decreto-aprovacao-constituicao', 'key': '1976-34520775', 'frag': '34520775', 'slug': 'constituicao',
     'short': 'Constituição', 'start': '1976-04-25', 'width': 3,
     # The consolidated original in the DR stops at Artigo 295.º; the article on the day of entry into force came back
     # into the text in 2005 as Artigo 296.º, which the build checks for this sentence.
     'start_evidence': ('Artigo 296.º', '2. A Constituição da República Portuguesa entra em vigor no dia 25 de Abril de 1976.',
                        'no texto em vigor desde 2005-08-17 (in the text in force since 2005-08-17)'),
     'parts': {'': ''}},
    {'tipo': 'lei', 'key': '2009-34546475', 'frag': '34546475', 'slug': 'codigo-do-trabalho',
     'short': 'Código do Trabalho', 'start': '2009-02-17', 'width': 3,
     'start_evidence': None,   # Lei n.º 7/2009 names no day: the general rule (Lei n.º 74/98, art. 2.º, n.º 2) gives the 5th day
     'parts': {'': 'lei-7-2009', 'Anexo': ''}},
    {'tipo': 'decreto-lei', 'key': '1966-34509075', 'frag': '34509075', 'slug': 'codigo-civil',
     'short': 'Código Civil', 'start': '1967-06-01', 'width': 4,
     'start_evidence': ('Artigo 2.º', '1. O Código Civil entra em vigor no continente e ilhas adjacentes no dia 1 de Junho de 1967',
                        'do Decreto-Lei n.º 47344 (of Decreto-Lei n.º 47344)'),
     'parts': {'': 'decreto-lei-47344', 'Anexo': ''}},
]


# ---------------------------------------------------------------- names

def ascii_slug(s: str) -> str:
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


ARTICLE = re.compile(r'Artigo\s+(\d+)\s*\.?\s*[º°o]?\s*(?:-\s*([A-Z]+))?\s*$', re.I)


def article_file(name: str, width: int) -> str | None:
    m = ARTICLE.match(name)
    if not m:
        return None
    return f'artigo-{int(m.group(1)):0{width}d}' + (f'-{m.group(2).lower()}' if m.group(2) else '')


def file_order(path: str) -> tuple:
    """The order of an act's files: the preamble, the articles by number, the signatures, other files by name."""
    name = path.rsplit('/', 1)[-1][:-3]
    if name == 'preambulo':
        return (0, 0, '')
    m = re.fullmatch(r'artigo-(\d+)(-[a-z]+)?', name)
    if m:
        suf = m.group(2) or ''
        return (1, int(m.group(1)), f'{len(suf):02d}{suf}')
    if name == 'assinatura':
        return (3, 0, '')
    return (2, 0, name)


# ---------------------------------------------------------------- rendering a day's text into files

FILE_KINDS = {11, 15, 7}       # article, the whole act (its preamble), signatures


def part_of(act: dict, path: str) -> str:
    """The folder (under the act's) of a fragment, from its place in the act: 'Diploma > Anexo > ...' is the annex."""
    bits = path.split(' > ')
    top = bits[1] if len(bits) > 1 else ''
    for k, folder in act['parts'].items():
        if k and (top == k or top.startswith(k + ' ')):
            return folder
    return act['parts']['']


def render(act: dict, frags: list[tuple[str, model.Version]]) -> dict[str, dict]:
    """Files of the act from its fragments in order: each article (and the preamble, and the signatures) is a file; the
    headings of the parts that begin before an article are '##' lines at the top of its file. Returns path -> {text,
    fids, label}."""
    files: dict[str, dict] = {}
    pending: dict[str, list[tuple[str, list[str]]]] = {}
    last: dict[str, str] = {}
    for fid, v in frags:
        if v.state == 4:
            continue                    # revoked: the provision leaves the text in force
        folder = part_of(act, v.path)
        base = f'{act["slug"]}/{folder}/' if folder else f'{act["slug"]}/'
        if v.kind in FILE_KINDS or v.text:
            if v.kind == 15:
                name, title = 'preambulo', ([f'# {v.epigraph}'] if v.epigraph else [])
            elif v.kind == 7:
                name, title = 'assinatura', []
            else:
                name = article_file(v.name, act['width']) or ascii_slug(v.name) or f'fragmento-{fid}'
                title = [f'# {v.name}'] + ([f'### {v.epigraph}'] if v.epigraph else [])
            path = base + name + '.md'
            if path in files:
                raise SystemExit(f'{act["slug"]}: two fragments for {path} ({files[path]["fids"]}, {fid})')
            heads = pending.pop(folder, [])
            lines = [l for _, hl in heads for l in hl] + title
            if v.state == 2:
                lines.append('*(Suspenso)*')
            lines += v.text
            files[path] = {'lines': lines, 'fids': [h for h, _ in heads] + [fid], 'label': v.name if v.kind == 11 else
                           ('Preâmbulo' if v.kind == 15 else 'Assinatura' if v.kind == 7 else v.name)}
            last[folder] = path
        else:
            hl = [f'## {v.name}'] + ([f'## {v.epigraph}'] if v.epigraph else [])
            pending.setdefault(folder, []).append((fid, hl))
    for folder, heads in pending.items():   # headings after the last article of a part: at the end of that article
        if folder in last:
            f = files[last[folder]]
            f['lines'] += [l for _, hl in heads for l in hl]
            f['fids'] += [h for h, _ in heads]
    for f in files.values():
        f['text'] = '\n\n'.join(f['lines']) + '\n'
    return files


def merged_order(prev: list[str], new: list[str]) -> list[str]:
    """The new day's order, with fragments only the previous day had kept after their predecessor there."""
    out = list(new)
    have = set(new)
    for i, f in enumerate(prev):
        if f in have:
            continue
        j = i - 1
        while j >= 0 and prev[j] not in have:
            j -= 1
        at = out.index(prev[j]) + 1 if j >= 0 else 0
        out.insert(at, f)
        have.add(f)
    return out


# ---------------------------------------------------------------- one act: days, changes, causes

def label_list(labels: list[str]) -> str:
    return ', '.join(labels)


def build_act(act: dict, offline: bool) -> dict:
    data = model.load(act, offline)
    h = model.history(act, data)
    V = h['versions']
    acts = h['acts']
    rec = data['record']
    own = {'id': data['legis'], 'title': clean_title(rec['DiplomaLegis']['ConteudoTitle'], rec['DiplomaLegis']['Numero']),
           'kind': rec['TipoDiploma']['Tipo'], 'number': rec['DiplomaLegis']['Numero'],
           'published': rec['DiplomaLegis']['DataPublicacao'][:10], 'summary': model.clean_line(rec['DiplomaLegis']['Sumario']),
           'link': source.SITE + rec['DiplomaLegis']['LinkSitemap'], 'issuer': rec['DiplomaLegis']['Emissor']}
    for a in acts.values():
        a['issuer'] = ''
        if not a['number']:     # old declarations without a number: named with their day of publication
            a['title'] = f'{a["title"]} de {a["published"]}'
    if act['start_evidence'] and not any(act['start_evidence'][1] in ' '.join(v.text) for v in V.values()
                                         if v.name == act['start_evidence'][0]):
        raise SystemExit(f'{act["slug"]}: the sentence giving the day of entry into force is not in the DR text')
    # The acts with changes the DR dates to each day (notes aside).
    acts_by_day: dict[str, set[str]] = {}
    for lid, a in acts.items():
        for x in a['mods']:
            if x['TipoModificacao'] != 'Nota' and x['DataEntradaVigor'] != model.NO_DAY:
                acts_by_day.setdefault(x['DataEntradaVigor'], set()).add(lid)
    removal_names: dict[str, set[str]] = {}     # fragment -> acts the timeline names for eliminating or repealing it
    for lid, a in acts.items():
        for x in a['mods']:
            if x['TipoModificacao'] in ('Elimina', 'Revoga') and x['FragmentoVersaoDestinoId'] in V:
                removal_names.setdefault(V[x['FragmentoVersaoDestinoId']].fid, set()).add(lid)

    def causes(vid: str) -> list[str]:
        named = [(l, t) for l, t in h['names'].get(vid, []) if l in acts]
        real = sorted({l for l, t in named if t != 'Nota'})
        return real or sorted({l for l, _ in named})

    def cause_of(f: str, old: str | None, vid: str | None, d: str) -> tuple[str, str]:
        """The act a change of one fragment on day d is credited to, and why."""
        c = causes(vid) if vid else sorted(removal_names.get(f, set()))
        if len(c) == 1:
            return c[0], 'named'
        if len(c) > 1:
            return 'candidates:' + ','.join(c), 'two acts named'
        day_acts = sorted(acts_by_day.get(d, set()))
        dated = vid is None or (not V[vid].undated and V[vid].date == d)
        if dated and len(day_acts) == 1:
            return day_acts[0], 'date only'
        if dated and day_acts:
            return 'candidates:' + ','.join(day_acts), 'two acts that day'
        return 'unexplained', 'not named'

    commits = []
    problems = []
    start = act['start']
    first_snap = h['snap_days'][0]
    cur = {f: v for f, v in h['shown'][first_snap].items()}     # the act as the DR prints its original text
    order = h['orders'][start]
    files = render(act, [(f, V[cur[f]]) for f in order if f in cur])
    commits.append({'day': start, 'kind': 'start', 'files': files, 'changed': sorted(files, key=file_order),
                    'before': {}, 'law': own['id'], 'evidence': {}})
    prev_order = order
    for d in h['days']:
        target = h['states'][d]
        new_order = h['orders'][d]
        delta = [f for f in sorted(set(cur) | set(target)) if cur.get(f) != target.get(f)]
        group: dict[str, list[str]] = {}
        why: dict[str, str] = {}
        for f in delta:
            vid, old = target.get(f), cur.get(f)
            if vid and old and V[vid].content() == V[old].content():
                group.setdefault('same', []).append(f)
                continue
            g, w = cause_of(f, old, vid, d)
            group.setdefault(g, []).append(f)
            why[f] = w
        steps = sorted((g for g in group if g in acts), key=lambda l: (acts[l]['published'], int(l)))
        steps = steps + sorted(g for g in group if g.startswith('candidates:')) + ['unexplained'] * ('unexplained' in group)
        order_now = merged_order(prev_order, new_order)
        # New versions with the same words (the DR renews version ids at each revision) change nothing by themselves;
        # a provision that only moves (a new order of the parts) goes with the first commit of the day.
        for f in group.get('same', []):
            cur[f] = target[f]
        if not steps and render(act, [(f, V[cur[f]]) for f in order_now if f in cur]) != files:
            steps = ['unexplained']
            group['unexplained'] = []
        for g in steps:
            for f in group[g]:
                if f in target:
                    cur[f] = target[f]
                else:
                    cur.pop(f, None)
            before = files
            files = render(act, [(f, V[cur[f]]) for f in order_now if f in cur])
            changed = sorted({p for p in set(before) | set(files) if (before.get(p) or {}).get('text') !=
                              (files.get(p) or {}).get('text')}, key=file_order)
            if not changed:
                continue
            kind = 'law' if g in acts else 'candidates' if g.startswith('candidates:') else 'unexplained'
            # Why each file changed: the reasons of the fragments of this step that sit in it (a file whose own
            # fragments did not change took headings that moved with a provision of this step).
            evidence: dict[str, list[str]] = {}
            for p in changed:
                fids = set((files.get(p) or {}).get('fids', [])) | set((before.get(p) or {}).get('fids', []))
                rs = sorted({why[f] for f in group[g] if f in fids})
                evidence[p] = rs or ['headings moved']
            commits.append({'day': d, 'kind': kind, 'law': g if kind == 'law' else None,
                            'candidates': g.split(':', 1)[1].split(',') if kind == 'candidates' else [],
                            'files': files, 'before': before, 'changed': changed, 'evidence': evidence,
                            'versions': [target[f] for f in group[g] if f in target]})
            if kind != 'law':
                problems.append(f'{d} {kind}: {", ".join(changed[:6])}')
        files = render(act, [(f, V[cur[f]]) for f in new_order if f in cur])
        expected = render(act, [(f, V[target[f]]) for f in new_order if f in target])
        if set(cur) != set(target) or {p: x['text'] for p, x in files.items()} != {p: x['text'] for p, x in expected.items()}:
            raise SystemExit(f'{act["slug"]} {d}: the commits of the day do not add up to the text of the day')
        prev_order = new_order
    return {'act': act, 'h': h, 'data': data, 'acts': acts, 'own': own, 'commits': commits, 'problems': problems}


def clean_title(title: str, number: str) -> str:
    t = model.clean_line(title)
    return f'{t} n.º {number}' if number and number not in t else t


def act_label(a: dict) -> str:
    """'Lei n.º 7/2009', 'Lei Constitucional n.º 1/2005', 'Decreto de Aprovação da Constituição'."""
    return a['title']


def law_email(a: dict) -> str:
    kind = a['link'].rstrip('/').split('/')[-2] if '/detalhe/' in a['link'] else ascii_slug(a['kind'])
    # Acts without a number (old declarations of rectification) are told apart by their day and the DR's id.
    num = ascii_slug(a['number'].replace('/', '-')) if a['number'] else f'{a["published"]}-{a["id"]}'
    return f'{kind}-{num}@diariodarepublica.invalid'


def tag_of(a: dict) -> str:
    return 'atos/' + law_email(a).split('@')[0]


# ---------------------------------------------------------------- the git repository

def git(repo: Path, *args: str, env: dict | None = None, input: str | None = None) -> str:
    out = subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True, encoding='utf-8', env=env, input=input)
    if out.returncode:
        raise SystemExit(f'git {" ".join(args)} failed: {out.stderr}')
    return out.stdout


def last_sunday(year: int, month: int) -> dt.date:
    d = (dt.date(year, month + 1, 1) if month < 12 else dt.date(year + 1, 1, 1)) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def lisbon_offset(day: dt.date) -> int:
    """Hours ahead of UTC at noon on a day in Lisbon, written out because this machine has no time-zone database
    (after the tz database's Europe/Lisbon). 3 April 1966 to 26 September 1976: UTC+1 all year. Then Western European
    Time (UTC+0) with summer time (UTC+1): 1977 from 27 March to 25 September; 1978 from 2 April to 1 October; 1979
    from 1 April to 30 September; 1980 to 1983 from the last Sunday in March to the last Sunday in September; 1984 to
    1991 the same. From 27 September 1992 to 31 March 1996, Central European Time: UTC+1, UTC+2 from the last Sunday in
    March to the last Sunday in September. From 31 March 1996: UTC+0, UTC+1 from the last Sunday in March to the last
    Sunday in October (summer time at noon on the day it starts; standard time at noon on the day it ends)."""
    y = day.year
    if dt.date(1966, 4, 3) <= day < dt.date(1976, 9, 26):
        return 1
    if day < dt.date(1966, 4, 3):
        return 0
    if dt.date(1992, 9, 27) <= day < dt.date(1996, 3, 31):
        return 2 if last_sunday(y, 3) <= day < last_sunday(y, 9) else 1
    if y == 1976:
        return 0
    if y == 1977:
        start, end = dt.date(1977, 3, 27), dt.date(1977, 9, 25)
    elif y == 1978:
        start, end = dt.date(1978, 4, 2), dt.date(1978, 10, 1)
    elif y == 1979:
        start, end = dt.date(1979, 4, 1), dt.date(1979, 9, 30)
    elif y <= 1995:
        start, end = last_sunday(y, 3), last_sunday(y, 9)
    else:
        start, end = last_sunday(y, 3), last_sunday(y, 10)
    return 1 if start <= day < end else 0


def commit_date(day: str, seq: list[int]) -> str:
    """Noon in Lisbon on the day. Git cannot record a time before 1970, so changes in force before then are dated
    1 January 1970 (UTC), one second apart in the order they took effect; the real day is in the In-force trailer."""
    d = dt.date.fromisoformat(day)
    if d.year < 1970:
        seq[0] += 1
        return f'@{seq[0]} +0000'
    off = lisbon_offset(d)
    stamp = int(dt.datetime(d.year, d.month, d.day, 12, tzinfo=dt.timezone(dt.timedelta(hours=off))).timestamp())
    return f'@{stamp} +0{off}00'


PRE_1970 = ['O git não regista datas anteriores a 1970: este commit tem a data de 1 de janeiro de 1970, e o dia em que',
            'a alteração entrou em vigor está na linha In-force. (Git cannot record dates before 1970: the real day is',
            'In-force.)', '']


def kinds_of(before: dict, after: dict, changed: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in changed:
        if p not in before:
            out.setdefault('Aditado', []).append(after[p]['label'])
        elif p not in after:
            out.setdefault('Revogado ou eliminado', []).append(before[p]['label'])
        else:
            out.setdefault('Alterado', []).append(after[p]['label'])
    return out


def labels_of(before: dict, after: dict, changed: list[str]) -> list[str]:
    return [(after.get(p) or before[p])['label'] for p in changed]


def subject_for(short: str, labels: list[str], tail: str) -> str:
    s = f'{short}: {", ".join(labels)} ({tail})'
    if len(s) > 72 or len(labels) > 4:
        s = f'{short}: {len(labels)} disposições ({tail})' if len(labels) != 1 else s
    return s


def published_note(a: dict, day: str) -> tuple[list[str], list[str]]:
    if a['published'] and day < a['published']:
        return ([f'Nota: o DR dá a esta versão o dia de entrada em vigor {day}, anterior à publicação do ato',
                 f'({a["published"]}).', '',
                 f'Note: the DR gives this version the in-force day {day}, before the act was published ({a["published"]});',
                 'it is kept as the source gives it.', ''],
                ['Date-note: the in-force day in the source is earlier than the day of publication'])
    return [], []


def message(b: dict, c: dict, day: str):
    act, acts, own = b['act'], b['acts'], b['own']
    short = act['short']
    cons = f'{CONSOLIDATED}/{act["tipo"]}/{act["key"]}'
    if c['kind'] == 'start':
        a = own
        author = (act_label(a), law_email(a))
        msg = [f'{short}: texto original ({a["title"]})', '', a['summary'], '',
               f'O texto tal como entrou em vigor, a {day}, na versão consolidada do Diário da República.', '',
               f'The text as it took effect on {day}, in the Diário da República\'s consolidated version.', '']
        trailers = [f'Kind: {a["kind"]}', f'Issuer: {a["issuer"]}', f'Published: {a["published"]} (Diário da República)']
        if act['start_evidence']:
            art, quote, where = act['start_evidence']
            msg += [f'{art}, {where}:', '', f'> {quote}', '']
            trailers.append(f'Evidence: in-force day from {art} of the act, in its text in force today')
        else:
            msg += ['O ato não fixa o dia da sua entrada em vigor: vale a regra geral do n.º 2 do artigo 2.º da Lei',
                    'n.º 74/98 (quinto dia após a publicação), que é também o dia em que o DR começa a consolidação.', '',
                    'The act names no day: the general rule (Lei n.º 74/98, art. 2(2): the fifth day after publication)',
                    'gives this day, which is also the day the DR\'s consolidated text begins.', '']
            trailers.append('Evidence: in-force day by the general rule, Lei n.º 74/98, art. 2.º, n.º 2')
        trailers += [f'In-force: {day}', f'Source: {a["link"]}', f'Consolidated-text: {cons}']
        if day < '1970-01-01':
            msg += PRE_1970
        return author, msg, trailers
    labels = labels_of(c['before'], c['files'], c['changed'])
    listing = [f'{k}: {", ".join(v)}' for k, v in kinds_of(c['before'], c['files'], c['changed']).items()]
    affecting = ', '.join(f'{short} {l}' for l in labels)
    trailers = []
    if c['kind'] == 'law':
        a = acts[c['law']]
        author = (act_label(a), law_email(a))
        msg = [subject_for(short, labels, a['title']), '', a['summary'], ''] + listing + ['']
        note, tr = published_note(a, day)
        msg += note
        ev = c['evidence']
        if any('named' in r for r in ev.values()):
            trailers.append('Evidence: the DR amendment timeline names this act for the new version of the provision')
        for reason, pt, en in (
                ('date only', 'O DR não indica o ato que fez estas versões; são atribuídas ao único ato com alterações em vigor neste dia',
                 'the DR names no act for the new version; credited to the only act with changes in force that day'),
                ('headings moved', 'Títulos de divisões que mudaram de ficheiro com uma disposição alterada por este ato',
                 'part headings that moved with a provision this act changed')):
            files_r = [(c['files'].get(p) or c['before'][p])['label'] for p, r in ev.items() if reason in r]
            if files_r:
                msg += [f'{pt}: {", ".join(files_r)}.', '']
                trailers.append(f'Evidence: {reason} ({en}) for {", ".join(files_r)}')
        und = [b['h']['versions'][v] for v in c['versions'] if b['h']['versions'][v].undated]
        if und:
            fixed = any('correction' in v.note for v in und)
            if fixed:
                msg += ['O DR não dá dia de entrada em vigor a esta correção; a data é a da publicação da declaração de',
                        'retificação. (The DR gives no in-force day for this correction: it is dated by the publication of',
                        'the declaration of rectification.)', '']
                trailers.append('Evidence: undated in the DR; dated by the publication of the rectification')
            else:
                msg += ['O DR não dá dia de entrada em vigor a estas versões; a data é a do primeiro texto consolidado',
                        f'que as mostra. (The DR gives no in-force day for these versions: they are dated by the first',
                        'consolidated text that shows them.)', '']
                trailers.append('Evidence: undated in the DR; dated by the first consolidated text that shows it')
        trailers += [f'Kind: {a["kind"]}', f'Published: {a["published"]} (Diário da República)', f'In-force: {day}']
        trailers += tr
        trailers += [f'Affecting: {affecting}', f'Source: {a["link"]}']
    elif c['kind'] == 'candidates':
        author = PUBLISHER
        names = [acts[l]['title'] for l in c['candidates']]
        msg = [subject_for(short, labels, 'dois atos no mesmo dia'), '',
               f'Neste dia entraram em vigor {" e ".join(names)}. O DR não diz qual alterou estas disposições, pelo',
               'que a alteração não é atribuída a nenhum deles.', ''] + listing + [''] + [
               f'{" and ".join(names)} took effect on this day. The DR does not say which changed these provisions, so',
               'the change is credited to neither.', '']
        trailers += [f'In-force: {day}', f'Affecting: {affecting}'] + [f'Candidate: {n}' for n in names]
    else:
        author = PUBLISHER
        msg = [subject_for(short, labels, 'alteração sem ato indicado'), '',
               'O texto consolidado do DR mudou neste dia, mas o DR não indica o ato que fez esta alteração.', ''] + \
            listing + [''] + ['The DR\'s consolidated text changed on this day, but the DR names no act for this change.', '']
        trailers += [f'In-force: {day}', f'Affecting: {affecting}']
    trailers.append(f'Consolidated-text: {cons}')
    if day < '1970-01-01':
        msg += PRE_1970
    return author, msg, trailers


def write_file(repo: Path, path: str, f: dict | None):
    p = repo / path
    if f is None:
        p.unlink(missing_ok=True)
        if p.parent.exists() and not any(p.parent.iterdir()):
            p.parent.rmdir()
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f['text'], encoding='utf-8', newline='\n')


def plan(built: list[dict]) -> list[tuple]:
    out = []
    for ai, b in enumerate(built):
        for i, c in enumerate(b['commits']):
            out.append((c['day'], ai, i, b, c))
    out.sort(key=lambda x: x[:3])
    return out


def write_repo(repo: Path, built: list[dict], docs: Path, today: str) -> tuple[list[dict], dict]:
    remote = None
    if (repo / '.git').exists():
        out = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=repo, capture_output=True, text=True)
        remote = out.stdout.strip() or None
        root = subprocess.run(['git', 'log', '--format=%s', '--max-parents=0', 'main'], cwd=repo, capture_output=True,
                              text=True).stdout.strip()
        if root.endswith('sources, before any law'):
            raise SystemExit('the target holds the placeholder history; clone into an empty folder instead')
    elif repo.exists() and any(repo.iterdir()):
        raise SystemExit(f'{repo} is not empty and not an earlier build')

    def force(fn, path, _exc):
        os.chmod(path, 0o700)
        fn(path)
    if repo.exists():
        for p in repo.iterdir():
            shutil.rmtree(p, onexc=force) if p.is_dir() else p.unlink()
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'config', 'core.autocrlf', 'false')
    git(repo, 'config', 'core.quotepath', 'false')
    if remote:
        git(repo, 'remote', 'add', 'origin', remote)
    seq = [0]
    tags: dict[str, str] = {}
    law_days: dict[str, list[tuple[str, str]]] = {}
    log = []
    switched = False
    for day, ai, _, b, c in plan(built):
        slug = b['act']['slug']
        if day > today and not switched:
            git(repo, 'checkout', '-q', '-b', FUTURE)
            switched = True
        for p in c['changed']:
            write_file(repo, p, c['files'].get(p))
        author, msg, trailers = message(b, c, day)
        git(repo, 'add', '-A')
        when = commit_date(day, seq)
        env = {**os.environ, 'GIT_AUTHOR_NAME': author[0], 'GIT_AUTHOR_EMAIL': author[1], 'GIT_AUTHOR_DATE': when,
               'GIT_COMMITTER_NAME': COMMITTER[0], 'GIT_COMMITTER_EMAIL': COMMITTER[1], 'GIT_COMMITTER_DATE': when}
        git(repo, 'commit', '-q', '--cleanup=verbatim', '-F', '-', env=env,
            input='\n'.join(msg).rstrip('\n') + '\n\n' + '\n'.join(trailers) + '\n')
        head = git(repo, 'rev-parse', 'HEAD').strip()
        tags[f'{slug}/{day}'] = head
        law = c.get('law')
        if law:
            a = b['own'] if c['kind'] == 'start' else b['acts'][law]
            t = tag_of(a)
            days = law_days.setdefault(t, [])
            if days and days[-1][0] == day:
                days[-1] = (day, head)
            else:
                days.append((day, head))
        log.append({'day': day, 'slug': slug, 'kind': c['kind'], 'author': author[0], 'files': len(c['changed']),
                    'clamped': day < '1970-01-01', 'evidence': c.get('evidence', {}),
                    'labels': labels_of(c['before'], c['files'], c['changed']) if c['kind'] != 'start' else []})
    for t, days in law_days.items():
        if len(days) == 1:
            tags[t] = days[0][1]
        else:
            for day, head in days:
                tags[f'{t}/{day}'] = head
    for name in sorted(tags):
        git(repo, 'tag', '-f', name, tags[name])
    if switched:
        git(repo, 'checkout', '-q', 'main')
    for p in sorted(docs.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            dest = repo / p.relative_to(docs)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
    for name in ('build.py', 'model.py', 'source.py', 'reproduce.py', 'check_repo.py', 'test_repo.py'):
        (repo / 'tools' / name).write_bytes((HERE / name).read_bytes())
    for p in sorted((HERE / 'templates').glob('*.json')):
        (repo / 'tools' / 'templates').mkdir(parents=True, exist_ok=True)
        (repo / 'tools' / 'templates' / p.name).write_bytes(p.read_bytes())
    write_tables(repo, built)
    from reproduce import write_manifest, write_reproduce
    write_manifest(repo, built, today)
    write_reproduce(repo, built, log, tags, source.REQUESTS, today)
    git(repo, 'add', '-A')
    when = commit_date(today, seq)
    env = {**os.environ, 'GIT_AUTHOR_NAME': COMMITTER[0], 'GIT_AUTHOR_EMAIL': COMMITTER[1], 'GIT_AUTHOR_DATE': when,
           'GIT_COMMITTER_NAME': COMMITTER[0], 'GIT_COMMITTER_EMAIL': COMMITTER[1], 'GIT_COMMITTER_DATE': when}
    git(repo, 'commit', '-q', '-m', 'Documentação, tabelas, ferramentas e REPRODUCE.md', env=env)
    return log, tags


def write_tables(repo: Path, built: list[dict]):
    rows = []
    for b in built:
        a = b['own']
        rows.append({'ato_consolidado': b['act']['short'], 'ato': a['title'], 'tipo': a['kind'], 'publicado': a['published'],
                     'em_vigor': b['act']['start'], 'ficheiros': len(b['commits'][0]['changed']), 'nota': 'texto original',
                     'fonte': a['link']})
        seen = {}
        for c in b['commits'][1:]:
            if c['kind'] != 'law':
                continue
            seen.setdefault((c['law'], c['day']), 0)
            seen[(c['law'], c['day'])] += len(c['changed'])
        for lid, a in sorted(b['acts'].items(), key=lambda x: (x[1]['published'], int(x[0]))):
            days = sorted(d for (l, d) in seen if l == lid)
            for d in days or ['']:
                rows.append({'ato_consolidado': b['act']['short'], 'ato': a['title'], 'tipo': a['kind'],
                             'publicado': a['published'], 'em_vigor': d, 'ficheiros': seen.get((lid, d), 0),
                             'nota': '' if d else 'sem alteração do texto (nota, declaração ou alteração já contada)',
                             'fonte': a['link']})
    rows.sort(key=lambda r: (r['ato_consolidado'], r['em_vigor'] or '9999', r['publicado'], r['ato']))
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    (repo / 'atos.csv').write_text(buf.getvalue(), encoding='utf-8', newline='\n')
    for b in built:
        act = b['act']
        counts: dict[str, int] = {}
        lastday: dict[str, str] = {}
        for c in b['commits'][1:]:
            for p in c['changed']:
                counts[p] = counts.get(p, 0) + 1
                lastday[p] = c['day']
        final = b['commits'][-1]['files']
        a = b['own']
        out = [f'# {act["short"]}', '', f'{a["title"]} · {a["summary"]}', '',
               f'<{CONSOLIDATED}/{act["tipo"]}/{act["key"]}>', '',
               f'Em vigor desde {act["start"]}; {len(b["h"]["days"])} dias com versões no DR '
               f'(o último em {b["h"]["days"][-1]}).', '',
               '| Disposição | Ficheiro | Alterações | Última alteração |', '| --- | --- | ---: | --- |']
        for p in sorted(final, key=lambda p: (p.count('/'), p.rsplit('/', 1)[0], file_order(p))):
            rel = p[len(act['slug']) + 1:]
            out.append(f'| {final[p]["label"]} | [{rel}]({rel}) | {counts.get(p, 0)} | {lastday.get(p, "")} |')
        (repo / act['slug'] / 'README.md').write_text('\n'.join(out) + '\n', encoding='utf-8', newline='\n')


# ---------------------------------------------------------------- main

def data_day() -> str:
    files = [p for p in source.CACHE.iterdir() if p.name != '.gitignore'] if source.CACHE.exists() else []
    if not files:
        return dt.date.today().isoformat()
    return dt.date.fromtimestamp(max(p.stat().st_mtime for p in files)).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(ROOT.parent / 'portugal-law'))
    ap.add_argument('--offline', action='store_true', help='read only the cache; fail on anything not cached')
    ap.add_argument('--today', default=None, help='the build day (default: the day the cached data was retrieved)')
    ap.add_argument('--verify-rebuild', action='store_true',
                    help='build again into a temporary folder from the cache, compare every hash with --repo, and record the result')
    args = ap.parse_args()
    if args.verify_rebuild:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = subprocess.run([os.sys.executable, '-X', 'utf8', str(HERE / 'build.py'), '--offline', '--repo', tmp]
                                 + (['--today', args.today] if args.today else []), capture_output=True, text=True)
            if out.returncode:
                raise SystemExit(out.stderr)

            def hashes(r):
                log = git(Path(r), 'log', '--format=%H', 'main').split()
                tags = dict(l.split(' ', 1)[::-1] for l in git(Path(r), 'show-ref', '--tags').split('\n') if l)
                return log, tags
            a, b = hashes(args.repo), hashes(tmp)
            same_history = a[0][1:] == b[0][1:]
            rec = {'identical': same_history and a[1] == b[1], 'history_tip': a[0][1], 'commits': len(a[0]) - 1,
                   'tags': len(a[1]), 'main_identical': a[0][0] == b[0][0], 'main': a[0][0], 'rebuilt_main': b[0][0]}
            print(json.dumps(rec, indent=1))
            p = HERE / 'verification.json'
            ver = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
            ver['rebuild'] = {k: rec[k] for k in ('identical', 'history_tip', 'commits', 'tags')}
            p.write_text(json.dumps(ver, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
            for f in Path(tmp).rglob('*'):
                os.chmod(f, 0o700)
            raise SystemExit(0 if rec['identical'] else 1)
    built = [build_act(a, args.offline) for a in ACTS]
    today = args.today or data_day()
    for b in built:
        n = sum(len(c['changed']) for c in b['commits'][1:])
        print(f'{b["act"]["slug"]}: {len(b["h"]["days"])} days {b["h"]["days"][0]}..{b["h"]["days"][-1]}, '
              f'{len(b["commits"])} commits, {n} file changes, {len(b["h"]["adjustments"])} version-date adjustments, '
              f'{len(b["problems"])} not credited to one act')
        for p in b['problems']:
            print('   ', p)
    log, tags = write_repo(Path(args.repo), built, HERE / 'repo', today)
    print(f'repo: {len(log)} commits + 1 documentation commit, {len(tags)} tags -> {args.repo}')


if __name__ == '__main__':
    main()
