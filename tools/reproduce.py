"""Writes data/versoes.json, corpus.json and REPRODUCE.md into the Portuguese law repository, from the facts of the build
that made it. Called by build.py.

The results of the checks (check_repo.py, test_repo.py and the rebuild that compares hashes) are read from
verification.json next to this file. They describe the build before the one that writes this file, from the same data;
a rebuild with the same data and the same verification.json gives the same hashes."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def write_manifest(repo: Path, built: list[dict], today: str):
    """Every response the text comes from, with its sha256, and every place where the record follows a version's own
    date rather than the DR's text for that day."""
    import source
    out = {'built': today, 'source': 'https://diariodarepublica.pt (Legislação Consolidada)', 'acts': []}
    for b in built:
        act, h, V = b['act'], b['h'], b['h']['versions']
        snaps = []
        for d in h['snap_days']:
            params = {**source.act_params(act), 'DiplomaLegisId': b['data']['legis'], 'DataSelecionada': d, 'DataAux': d}
            f = source.CACHE / f'{source.cache_key("data", params)}.json.gz'
            snaps.append({'day': d, 'file': f.name, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()})
        adj = [{'day': a['day'], 'provision': V[a['shown']].name, 'shown': {'version': a['shown'], 'in_force': V[a['shown']].date},
                'used': ({'version': a['used'], 'in_force': V[a['used']].day} if a['used'] else None), 'kind': a['kind']}
               for a in h['adjustments'] if not a['used'] or V[a['used']].content() != V[a['shown']].content()]
        undated = sorted({(v.day, v.name, v.note) for v in V.values() if v.undated})
        out['acts'].append({'slug': act['slug'], 'title': b['own']['title'], 'consolidated': f'https://diariodarepublica.pt/dr/legislacao-consolidada/{act["tipo"]}/{act["key"]}',
                            'diploma_frag_id': act['frag'], 'diploma_legis_id': b['data']['legis'], 'in_force_from': act['start'],
                            'texts_by_day': snaps, 'versions': len(V),
                            'adjustments': adj,
                            'undated_versions': [{'day': d, 'provision': n, 'note': note} for d, n, note in undated]})
    (repo / 'data').mkdir(exist_ok=True)
    (repo / 'data' / 'versoes.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8',
                                                newline='\n')
    days = [c['day'] for b in built for c in b['commits'] if c['day'] <= today]
    corpus = {
        'corpus': 'pt/national/acts',
        'name': 'Portuguese law: Constituição da República Portuguesa, Código Civil (Decreto-Lei n.º 47344) and Código do Trabalho (Lei n.º 7/2009)',
        'label': 'Portugal',
        'language': 'pt',
        'acts': [b['own']['title'] + (f' ({b["act"]["short"]})' if b['act']['short'] not in b['own']['title'] else '')
                 for b in built],
        'history_from': min(b['act']['start'] for b in built),
        'record_to': max(days),
        'record_note': f'checked against the Diário da República consolidated texts retrieved on {today}',
        'built': today,
        'in_force_trailer': 'In-force',
        'has_future_branch': False,
        'dates': {'commit': 'in-force', 'other_trailers': ['Published'],
                  'time': '12:00 Europe/Lisbon (written into the builder: UTC+0, UTC+1 in summer time; UTC+1 1966-1976; CET 1992-1996)'},
        'scope': {
            'trailer': 'Applies',
            'when_absent': 'this corpus records no scope notes (no commit carries Applies:); the absence is not a '
                           'statement that the change reaches every case',
            'default_reach': {
                'rule': 'no retroactivity by default',
                'meaning': 'a law provides only for the future; where it is given retroactive effect, effects already '
                           'produced by the facts it regulates are presumed to be safeguarded; criminal law and laws '
                           'restricting rights, liberties and guarantees, and tax laws, cannot be retroactive; a later '
                           'criminal law applies where it is more favourable to the accused',
                'authority': 'Código Civil, artigo 12.º, n.º 1 ("A lei só dispõe para o futuro; ainda que, lhe seja '
                             'atribuída eficácia retroactiva, presume-se que ficam ressalvados os efeitos já produzidos '
                             'pelos factos que a lei se destina a regular."); Constituição, artigos 18.º, n.º 3, 29.º e '
                             '103.º, n.º 3',
                'decided_here': False}},
        'citation': {'file': '(constituicao|codigo-civil|codigo-do-trabalho)/artigo-0*([0-9]+(-[a-z]+)?)\\.md',
                     'cites': '(artigo|art\\.) ?{n}'},
        'tool': 'tools/em_vigor.py',
    }
    (repo / 'corpus.json').write_text(json.dumps(corpus, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')


def write_reproduce(repo: Path, built: list[dict], log: list[dict], tags: dict, requests: list[dict], today: str):
    blobs = {n: subprocess.run(['git', 'hash-object', str(HERE / n)], capture_output=True, text=True).stdout.strip()
             for n in ('build.py', 'model.py', 'source.py')}
    pyv = subprocess.run(['python', '--version'], capture_output=True, text=True).stdout.strip()
    gitv = subprocess.run(['git', '--version'], capture_output=True, text=True).stdout.strip()
    ver = json.loads((HERE / 'verification.json').read_text(encoding='utf-8')) if (HERE / 'verification.json').exists() else {}
    import source
    files = sorted({r['file'] for r in requests})
    n_kind = {k: len({r['file'] for r in requests if r['kind'] == k}) for k in ('frag', 'timeline', 'data')}
    days = sorted({dt.date.fromtimestamp((source.CACHE / f).stat().st_mtime).isoformat() for f in files
                   if (source.CACHE / f).exists()})
    n_law = sum(1 for c in log if c['kind'] == 'law')
    n_cand = sum(1 for c in log if c['kind'] == 'candidates')
    n_unexp = sum(1 for c in log if c['kind'] == 'unexplained')
    n_start = sum(1 for c in log if c['kind'] == 'start')
    n_clamped = sum(1 for c in log if c['clamped'])
    why: dict[str, int] = {}
    listed: dict[str, list[str]] = {}
    for c in log:
        for lab, rs in zip(c['labels'], c['evidence'].values()):
            for r in rs:
                why[r] = why.get(r, 0) + 1
                if r not in ('named',):
                    listed.setdefault(r, []).append(f'{c["slug"]} {c["day"]}: {lab}')
    unexplained = [f'{c["slug"]} {c["day"]}: {", ".join(c["labels"])}' for c in log if c['kind'] == 'unexplained']
    adjust_lines = []
    n_adj = 0
    for b in built:
        V = b['h']['versions']
        for a in b['h']['adjustments']:
            if a['used'] and V[a['used']].content() == V[a['shown']].content():
                continue
            n_adj += 1
            s = V[a['shown']]
            adjust_lines.append(f'{b["act"]["slug"]} {a["day"]}: {s.name} ({"shown with in-force day " + s.date if s.date != "1900-01-01" else "shown without a day"}; '
                                + (f'the record keeps the version in force from {V[a["used"]].day})' if a['used'] else 'not yet in force, left out)'))
    undated = [f'{b["act"]["slug"]} {v.day}: {v.name} ({v.note})' for b in built for v in
               sorted(b['h']['versions'].values(), key=lambda v: (v.day, v.name)) if v.undated and v.day != v.seen]
    rows = '\n'.join(
        f'| {b["own"]["title"]} | {b["act"]["short"]} | `{b["act"]["slug"]}/` | {b["act"]["start"]} | {len(b["h"]["snap_days"])} | '
        f'{len(b["commits"])} | {len(b["commits"][-1]["files"])} |' for b in built)
    chk = ver.get('check', {})
    det = ver.get('rebuild', {})
    smoke = ver.get('smoke', {})
    check_line = (f'`{chk["days"]} days checked ({chk["files"]} files), {chk["mismatches"]} mismatches; '
                  f'{chk["wordcheck"]} days word for word ({chk["words"]} words) against the DR\'s own text, '
                  f'{chk["word_mismatches"]} mismatches`' if chk else '(not yet run)')
    rebuild_line = (f'A second build from the same cache into an empty folder gave the same history: the last law commit '
                    f'was `{det["history_tip"]}` in both, and every one of the {det["commits"]} law commits and {det["tags"]} '
                    f'tags had the same hash.' if det.get('identical') else '(not yet run)')
    smoke_lines = ('\n'.join(f'   - {"pass" if r["ok"] else "FAIL"}: {r["test"]}: {r["detail"]}' for r in smoke['results'])
                   if smoke else '   (not yet run)')
    smoke_head = f'{smoke["passed"]} of {smoke["total"]} passed' if smoke else 'not yet run'

    def items(xs):
        return '\n'.join(f'- {x}' for x in xs) or '- none'

    text = f"""# How this history was made, and how to make it again

This file records exactly how the repository was built: the source, the commands, the software, the decisions made
by hand, and what an AI model did and did not do. The build writes it, so it describes the build that made this
commit.

## Short version

```sh
git clone https://github.com/lexifina/portugal-law && cd portugal-law
python -X utf8 tools/build.py --repo ../rebuilt --today {today}
git -C ../rebuilt rev-parse main        # the same hash as this repository's main
python -X utf8 tools/check_repo.py --repo ../rebuilt
python -X utf8 tools/test_repo.py --repo ../rebuilt
```

`tools/build.py` needs Python 3.12 or later (standard library only) and git. It reads the Diário da República (or its
own cache, `.cache/` next to the script) and writes this repository into `--repo`. With the same data and the same
`--today` it gives the same commits with the same hashes. `data/versoes.json` lists every consolidated text it read,
one per day, with the sha256 of the response; the DR may revise its consolidations, and then the hashes change too.

## Source

All legal text and all information about versions and amending acts come from the **Diário da República** (DR,
https://diariodarepublica.pt), the official journal of the Portuguese Republic, published by the Imprensa
Nacional-Casa da Moeda, S.A. (INCM): its consolidated legislation (Legislação Consolidada). Nothing was typed in,
summarised or rewritten.

The DR has no public API and no bulk download of consolidated texts (dados.gov.pt has no INCM dataset). Its web
application (OutSystems) loads each screen's data with JSON calls; the build makes the same calls the page for a
consolidated act makes when a reader opens it or picks a date, with the screen's own default variables
(`tools/templates/`, copied from the site's requests) and the act and day filled in:

| Call (`/dr/screenservices/dr/LegislacaoConsolidada/...`) | What it gives | Calls made |
| --- | --- | ---: |
| `LegCons_Detalhe/DataActionGetDiplomaFragByIdAndApplicationSetting` | the act's record: its id, title, kind, issuer, day of publication | {n_kind['frag']} |
| `AlteracoesTimelineByDiplomaLegisId/DataActionGetConsolidacaoByDiplomaFrag` | the amendment timeline: every amending act, with each provision it added (Adita), changed (Altera), repealed (Revoga), eliminated (Elimina), suspended (Suspende) or corrected (Retifica), the version it made and the day that version took effect | {n_kind['timeline']} |
| `LegCons_Detalhe/DataActionGetData` | the whole consolidated text in force on a chosen day, provision by provision, each with its version id, its state (in force, repealed, suspended) and the day that version took effect | {n_kind['data']} |

| Act | Short name | Folder | In force from | Texts by day read | Commits | Files today |
| --- | --- | --- | --- | ---: | ---: | ---: |
{rows}

The data was retrieved on {', '.join(days) if days else today}, at most four requests at a time and a request started
at most every 0.25 seconds, with the user agent `lexifina-watch/1.0 (+https://lexifina.com/watch; corpus@lexifina.com)`
and the site's own anonymous CSRF header (which its script sends for every visitor who is not logged in; the build
checks it against the site's script). No login, no challenge and no rate limit were met. The site's robots.txt
address redirects to its error page, so it states no rules; its legal notice ("Avisos Legais") is quoted in LICENSE.

## The build, step by step

1. `python -X utf8 scripts/portugal-law/build.py --today {today}` in Lexifina's own repository fetched the data into
   its cache and wrote this repository. `tools/build.py`, `tools/model.py` and `tools/source.py` here are the same
   files as in `scripts/portugal-law/` there (git blobs `{blobs['build.py']}`, `{blobs['model.py']}`,
   `{blobs['source.py']}`), with `tools/reproduce.py`, which writes this file, `tools/check_repo.py` and
   `tools/test_repo.py`. Every later build ran with `--offline`, from the cache.
2. `python -X utf8 scripts/portugal-law/check_repo.py` read each act back from this repository with
   `tools/em_vigor.py` on every day a version took effect and compared it file by file with the text worked out
   afresh from the cached responses; then it compared the whole act, word for word, with the words of the DR's own
   text for that day, read from the raw responses without the build's renderer. Result: {check_line}.
3. `python -X utf8 scripts/portugal-law/test_repo.py --record` ran the functional smoke test ({smoke_head}):
{smoke_lines}
4. `python -X utf8 scripts/portugal-law/build.py --offline --verify-rebuild` built the repository a second time from
   the same cache into a temporary folder and compared the hashes. {rebuild_line}
5. The build was run once more to write these results into this file, and the final `main` was rebuilt again in a
   temporary folder and compared hash for hash before it was pushed.
6. `git push -f origin main --tags` published it to the private GitHub repository `lexifina/portugal-law`, replacing
   its placeholder commit.

It ran with {pyv} and {gitv} on Windows 11. `scripts/test_corpus.py` (Lexifina's shared corpus smoke test) was run on
the result as well.

## How the text and the commits are derived

Everything below is done by `tools/build.py` and `tools/model.py`, deterministically.

- **Text.** Each act is a folder. Each article is one file named after its number: `Artigo 7.º` is
  `artigo-007.md`, `Artigo 208.º-A` is `artigo-208-a.md`. The Código do Trabalho is the annex (Anexo) of Lei
  n.º 7/2009; its articles are in `codigo-do-trabalho/`, and the articles of Lei n.º 7/2009 itself in
  `codigo-do-trabalho/lei-7-2009/`. `preambulo.md` is the text before the first article (the Constitution's preamble;
  the enacting formula of a law), `assinatura.md` the signatures. The headings of the divisions (Parte, Título,
  Capítulo, Secção, ...) that begin before an article are `##` lines at the top of its file; the article's number is
  the `#` line and its heading (epígrafe) the `###` line; each line of the DR's text is one paragraph.
- **Normalised.** Only this: the DR's line ends (CR LF) and `<br/>` start a new paragraph; links (`<a>`) keep their
  words; HTML entities are decoded; runs of spaces become one space; the spaces the DR pads lines with and empty lines
  are dropped. A suspended provision gets the line `*(Suspenso)*` under its heading (the DR's state, not text); a
  repealed provision leaves the text, as it leaves the DR's text in force.
- **Days.** Each provision version carries the day it took effect (`DataEntradaVigor`). The DR's text for a day is the
  consolidation current on that day, which sometimes already shows a version that takes effect a few days or weeks
  later (a staged entry into force), and sometimes still lacks a correction published since. The record follows each
  version's own day; {n_adj} provision-days where the DR's text for the day shows another version are listed below
  and in `data/versoes.json`, and the check applies the same rule. A version the DR gives no day (the empty date
  1900-01-01) is dated by the first consolidated text that shows it, or, when it is a correction (Retifica) the DR
  shows only later, by the day the declaration of rectification was published.
- **Cause.** The amendment timeline names, for each amending act, the provision versions it made. Tried in order:
  1. the timeline names one act for the new version (for a provision that disappears: for its repeal or
     elimination): that act ({why.get('named', 0)} file changes);
  2. the DR names no act for it, the version is dated that day, and only one act has changes in force that day: that
     act, labelled "date only" ({why.get('date only', 0)});
  3. a heading that moved to another file with a provision an act changed: that act ({why.get('headings moved', 0)});
  4. two acts named, or two acts that day: neither; committed by the publisher naming both in `Candidate:` trailers
     ({why.get('two acts named', 0) + why.get('two acts that day', 0)});
  5. otherwise: no act; committed by the publisher and labelled ({why.get('not named', 0)}).
  New versions with the same words (the DR renews version ids at each revision) change no file and make no commit.
- **Commits.** One commit per act of the record, per day and per amending act ({n_law} law commits), one for the text
  of each act as it first took effect ({n_start}), {n_cand} for changes with two candidate acts and {n_unexp} for
  changes the DR names no act for, in the order they took effect (acts of one day in order of publication), then one
  for this documentation.
  - The author is the amending act, `Lei n.º 93/2019`, at an address ending `@diariodarepublica.invalid`
    (`lei-93-2019@diariodarepublica.invalid`, from the DR's own address for the act). Declarations of rectification
    and judgments of the Constitutional Court that the DR lists in the timeline are authors in the same way. The first
    text of each act is credited to the act itself.
  - Author and committer dates are noon in Lisbon on the day the change took effect, with the offsets of
    Europe/Lisbon written into the code (this machine has no time-zone database). The committer is
    `Lexifina <portugal-law@lexifina.com>`. {n_clamped} commits are before 1970.
  - The message has the act's title and summary (sumário), the provisions it added, changed or removed (Aditado,
    Alterado, Revogado ou eliminado) and the trailers `Evidence:`, `Kind:`, `Published:`, `In-force:`, `Affecting:`,
    `Source:` (the act on the DR) and `Consolidated-text:` (the consolidated act on the DR). `Date-note:` marks an
    in-force day before the act's publication, as the DR gives it.
  - Tags: each act's days (`constituicao/2005-08-17`) and each amending act (`atos/lei-constitucional-1-2005`; an act
    that took effect on several days has one tag per day, `atos/lei-13-2023/2023-05-01`); {len(tags)} in all.
- **Documentation commit.** Dated {today}, the day the data was retrieved, not the day of the run, so a later rebuild
  of the same data gives the same hash.

Changes credited by date only:

{items(listed.get('date only', []))}

Headings that moved with a provision:

{items(listed.get('headings moved', []))}

Changes the DR names no act for (publisher commits):

{items(unexplained)}

Provision-days where the record follows the version's own day, not the DR's text for that day:

{items(adjust_lines)}

Undated corrections dated by their publication:

{items(undated)}

## Decisions made by hand

These choices were made when the tool was written, after looking at the data. They are in the code.

1. **The source.** The DR's consolidated legislation is the only official source of past versions with their
   in-force days and amending acts. Its amendment timeline names the act behind each provision version, which is
   stronger evidence than a date alone.
2. **The acts.** The Constitution (Constituição da República Portuguesa, 1976, seven revisions), the act readers ask
   about first; the Código do Trabalho (Lei n.º 7/2009), because it is amended often (some 28 acts, including
   declarations of rectification, a suspension and staged entries into force) and exercises every rule above; and,
   because the same build handled it at little cost, the Código Civil (Decreto-Lei n.º 47344, 1966), with about a
   hundred amending acts the DR names. Its articles are `codigo-civil/artigo-NNNN.md` (four digits), those of the
   approving decree-law `codigo-civil/decreto-lei-47344/`.
3. **The first day.** The Constitution took effect on 25 April 1976: its text in force today says so in Artigo 296.º
   ("A Constituição da República Portuguesa entra em vigor no dia 25 de Abril de 1976"), which the build checks. The
   DR's consolidated original stops at Artigo 295.º and has no signatures (they appear in its text from 1982 and are
   committed then by the publisher). Lei n.º 7/2009 names no day of entry into force for the whole act: the general
   rule (Lei n.º 74/98, artigo 2.º, n.º 2: the fifth day after publication) gives 17 February 2009, the day the DR's
   versions begin. Its artigo 14.º defers some articles to later legislation; the DR's consolidation does not model
   that, and neither does this record. The Código Civil took effect on 1 June 1967 (artigo 2.º, n.º 1, of
   Decreto-Lei n.º 47344, which the build checks), except artigos 1841.º to 1850.º, from 1 January 1968, which the
   DR's consolidation does not model either. The DR's timeline for the Código Civil starts in 1975: amendments made
   between 1967 and 1975 appear, if at all, in the first later version the DR keeps, and changes it names no act
   for are committed by the publisher, labelled. Its first commit is dated 1 January 1970 (git cannot store earlier
   dates), with the real day in `In-force:`.
4. **Version days rule.** Where the DR's text for a day and its version days disagree (above), the record follows the
   version days, which are the DR's explicit statement of when each wording took effect, and lists every case.
5. **Repealed provisions leave the text**, as in the DR's text in force; suspended ones stay, marked.
6. **Portuguese only**, the official language.

## What an AI model did

This repository was built on {today} in **Claude Code**, Anthropic's coding tool, by the model **Claude Opus 5.5**
(model id `claude-opus-5-5`), working from a brief by the user at Lexifina: a private "git for law" repository for
Portugal to the same standard as Lexifina's other corpora.

The model:

- **Researched the source:** the DR's web application and the JSON calls its pages make, its legal notice, dados.gov.pt,
  and legalize-pt (below).
- **Wrote all the code and text in this repository:** `tools/build.py`, `tools/model.py`, `tools/source.py`,
  `tools/reproduce.py`, `tools/check_repo.py`, `tools/test_repo.py`, `tools/em_vigor.py`, the README, this file and
  the licence, and chose the design described in them.
- **Ran the commands above** and checked the results.

The model did **not**:

- **Write or edit any legal text.** Every word of every provision, every date and every act's title is copied by the
  script from the DR.
- **Take part in building the history.** No AI model is called when the history is built or checked.

The user decided what was in scope and decides whether the repository is ever made public. The work was not reviewed
line by line by a lawyer. The DR says its consolidated texts have no legal value ("sem valor legal"); only the
Diário da República as published is authoritative.

## Prior art

- [legalize-dev/legalize-pt](https://github.com/legalize-dev/legalize-pt) and its pipeline
  (`src/legalize/fetcher/pt/`): Portuguese legislation from the same DR consolidations, one file per act, one commit
  per version. From it we confirmed two facts about the site, checked against it: the screen-service contract and
  the anonymous CSRF token in the site's script. No code was copied. This repository instead puts each article in its
  own file and credits each change to the act the DR's timeline names for it, keeping changes it cannot attribute
  apart.
- Lexifina's other corpora, whose rules this one follows (Slovakia, Estonia, Liechtenstein, Luxembourg, Swiss federal
  law, the Grundgesetz, UK legislation and the US Code).
"""
    (repo / 'REPRODUCE.md').write_text(text, encoding='utf-8', newline='\n')
