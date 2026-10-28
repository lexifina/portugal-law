"""Checks the git repository against the Diário da República: on every day a provision version of an act took effect,
the act read back from git with tools/em_vigor.py must equal the DR's consolidated text in force that day.

    python -X utf8 scripts/portugal-law/check_repo.py [--repo ../portugal-law] [--no-record]

Two checks per act and day, from the cached DR responses (no network):
1. File by file: the act's files in git on that day are exactly the files the build makes from that day's text (same
   set of files, same bytes).
2. Word for word: the words of each file in git equal the words of the DR's own fields for the provisions of that file
   (heading, epigraph and text of each provision, as the raw JSON gives them, markup removed), grouped without the
   build's renderer: a file begins at each article (or preamble, or signatures) and takes the headings before it.
The text in force on a day is the version of each provision whose own in-force day is the latest on or before that day
(see model.py); the days where that differs from the DR's text for the day are listed in REPRODUCE.md.
The result is written to verification.json next to this script (unless --no-record), for REPRODUCE.md.
"""
import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402
import model  # noqa: E402

TOKEN = re.compile(r'\w+|[^\w\s]')


def raw_words(s: str) -> list[str]:
    s = re.sub(r'<br\s*/?>', ' ', s or '', flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    return TOKEN.findall(html.unescape(s).replace('­', ''))


def repo_words(text: str) -> list[str]:
    lines = [re.sub(r'^\s*#+ ', '', l) for l in text.split('\n')]
    lines = [l for l in lines if l != '*(Suspenso)*']
    return TOKEN.findall(' '.join(lines))


def official_blocks(act: dict, rows: list[dict]) -> list[tuple]:
    """Each file's words from the DR's raw rows: a block starts at an article, the whole act's own text or the
    signatures (or any row with text); rows without text (division headings) join the next block of the same part,
    or the last one of their part."""
    blocks: dict[str, list] = {}
    pending: dict[str, list[str]] = {}
    last: dict[str, list] = {}
    out = []
    for row in rows:
        fv, cf = row['FragmentoVersao'], row['ConsolidacaoFragmento']
        if fv['VersaoEstadoId'] == 4:
            continue
        top = cf['FullName'].split(' > ')[1] if ' > ' in cf['FullName'] else ''
        part = 'annex' if top.startswith('Anexo') and 'Anexo' in act['parts'] else 'act'
        name = fv['Tituo'] if isinstance(fv['Tituo'], str) else cf['Name']
        words = ([] if fv['TipoFragmentoId'] in (15, 7) else raw_words(name)) + raw_words(fv['Epigrafe']) + \
            raw_words(fv['Texto'])
        if fv['TipoFragmentoId'] in (11, 15, 7) or (fv['Texto'] or '').strip():
            b = pending.pop(part, []) + words
            out.append(b)
            last[part] = b
        else:
            pending.setdefault(part, []).extend(words)
    for part, w in pending.items():
        if part in last:
            last[part].extend(w)
    return sorted(tuple(b) for b in out)


def tool(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, 'tools/em_vigor.py', *args], cwd=repo, capture_output=True, text=True,
                          encoding='utf-8')


def files_at(repo: str, commit: str, slug: str) -> dict[str, str]:
    """The act's files at a commit, read with one ls-tree and one cat-file --batch."""
    out = subprocess.run(['git', 'ls-tree', '-r', commit, f'{slug}/'], cwd=repo, capture_output=True,
                         text=True, encoding='utf-8').stdout.split('\n')
    blobs = []
    for line in out:
        if not line:
            continue
        info, f = line.split('\t', 1)
        if f.endswith('.md') and not f.endswith(f'{slug}/README.md'):
            blobs.append((f, info.split()[2]))
    if not blobs:
        return {}
    data = subprocess.run(['git', 'cat-file', '--batch'], cwd=repo, input=''.join(f'{sha}\n' for _, sha in blobs).encode(),
                          capture_output=True).stdout
    res, pos = {}, 0
    for name, _ in blobs:
        nl = data.index(b'\n', pos)
        size = int(data[pos:nl].split()[2])
        res[name] = data[nl + 1:nl + 1 + size].decode('utf-8')
        pos = nl + 1 + size + 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(build.ROOT.parent / 'portugal-law'))
    ap.add_argument('--no-record', action='store_true')
    args = ap.parse_args()
    days = files = bad = wbad = nwords = 0
    per_act = {}
    for act in build.ACTS:
        data = model.load(act, offline=True)
        h = model.history(act, data)
        V = h['versions']
        raw = {}
        for d in h['snap_days']:
            for row in model.rows_of(data['snaps'][d]):
                raw.setdefault(row['FragmentoVersao']['Id'], row)
        for d in h['days']:
            state, order = h['states'][d], h['orders'][d]
            expected = {p: f['text'] for p, f in build.render(act, [(f, V[state[f]]) for f in order if f in state]).items()}
            commit = subprocess.run([sys.executable, '-B', '-c', 'import sys; sys.path.insert(0, "tools"); import em_vigor; '
                                     f'print(em_vigor.commit_on("{d}", "{act["slug"]}"))'],
                                    cwd=args.repo, capture_output=True, text=True).stdout.strip()
            got = files_at(args.repo, commit, act['slug']) if commit else {}
            days += 1
            files += len(expected)
            per_act[act['slug']] = per_act.get(act['slug'], 0) + 1
            if got != expected:
                bad += 1
                diff = sorted(set(got) ^ set(expected)) or [k for k in expected if got.get(k) != expected[k]]
                print(f'MISMATCH {act["slug"]} {d}: {diff[:5]}')
            official = official_blocks(act, [raw[state[f]] for f in order if f in state])
            mine = sorted(tuple(repo_words(t)) for t in got.values())
            nwords += sum(len(b) for b in official)
            if official != mine:
                wbad += 1
                a, b = set(official) - set(mine), set(mine) - set(official)
                print(f'WORDS {act["slug"]} {d}: {len(a)} official blocks not in git, {len(b)} git files not official; '
                      f'e.g. {" ".join(sorted(a)[0][:25]) if a else ""!r} / {" ".join(sorted(b)[0][:25]) if b else ""!r}')
            whole = tool(args.repo, d, act['slug'])
            if whole.returncode or sorted(repo_words(whole.stdout)) != sorted(w for t in got.values() for w in repo_words(t)):
                wbad += 1
                print(f'TOOL {act["slug"]} {d}: em_vigor.py does not print the files of the day')
    print(f'{days} days checked ({files} files), {bad} mismatches; {days} days word for word ({nwords} words), '
          f'{wbad} mismatches')
    print('per act:', per_act)
    if not args.no_record:
        p = HERE / 'verification.json'
        rec = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
        rec['check'] = {'days': days, 'files': files, 'mismatches': bad, 'wordcheck': days, 'words': nwords,
                        'word_mismatches': wbad, 'per_act': per_act}
        p.write_text(json.dumps(rec, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    raise SystemExit(1 if bad or wbad else 0)


if __name__ == '__main__':
    main()
