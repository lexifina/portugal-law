"""Prints an act, or one provision of it, as it stood on a given day, from this repository's history.

    python tools/em_vigor.py 2000-01-01 constituicao 7              # artigo 7.º of the Constitution on 1 January 2000
    python tools/em_vigor.py 2020-01-01 constituicao                # the whole Constitution on 1 January 2020
    python tools/em_vigor.py 2015-01-01 codigo-do-trabalho 3        # artigo 3.º of the Código do Trabalho
    python tools/em_vigor.py 2015-01-01 codigo-do-trabalho 208-A    # artigo 208.º-A
    python tools/em_vigor.py 2015-01-01 codigo-do-trabalho lei-7-2009/7   # artigo 7.º of Lei n.º 7/2009 itself

Each commit carries the day its change took effect in an `In-force:` trailer (git cannot store dates before 1970, so
the trailer, not the commit date, is the source of truth). The text in force on a day is the last commit on or before
it. Changes published but not yet in force would be on the branch "futuro"; a date after today reads from there.
Standard library only.
"""
import datetime as dt
import re
import subprocess
import sys


def git(*args: str) -> str:
    return subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8', check=True).stdout


def order(path: str) -> tuple:
    """The order of the act's files: the parts in their own folders (the act's own articles, for a code) first, then
    the preamble, the articles by number and the signatures."""
    parts = path.split('/')
    sub = '/'.join(parts[1:-1])
    name = parts[-1][:-3]
    if name == 'preambulo':
        k = (0, 0, '')
    elif name == 'assinatura':
        k = (3, 0, '')
    else:
        m = re.fullmatch(r'artigo-(\d+)(-[a-z]+)?', name)
        k = (1, int(m.group(1)), f'{len(m.group(2) or ""):02d}{m.group(2) or ""}') if m else (2, 0, name)
    return (0 if sub else 1, sub) + k


def file_for(act: str, key: str) -> str:
    """'7' -> artigo-007.md, '208-A' -> artigo-208-a.md, 'lei-7-2009/7' -> lei-7-2009/artigo-007.md; anything else is
    a file name ('preambulo', 'assinatura')."""
    sub, _, key = key.rpartition('/')
    m = re.fullmatch(r'(\d+)(?:\.?º)?(?:-?([A-Za-z]+))?', key)
    name = (f'artigo-{int(m.group(1)):03d}' + (f'-{m.group(2).lower()}' if m.group(2) else '')) if m else key
    name = name if name.endswith('.md') else f'{name}.md'
    return f'{sub}/{name}' if sub else name


def commit_on(day: str, act: str) -> str:
    branch = 'futuro' if day > dt.date.today().isoformat() and git('branch', '--list', 'futuro').strip() else 'main'
    out = git('log', '--no-merges', '--format=%H%x09%(trailers:key=In-force,valueonly,separator=)', branch, '--', act)
    for line in out.splitlines():
        h, _, d = line.partition('\t')
        if d.strip() and d.strip() <= day:
            return h
    return ''


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    day, act = sys.argv[1], sys.argv[2].strip('/')
    dt.date.fromisoformat(day)
    commit = commit_on(day, act)
    if not commit:
        sys.exit(f'{act} is not in the record on {day}.')
    if len(sys.argv) > 3:
        name = file_for(act, sys.argv[3])
        try:
            sys.stdout.write(git('show', f'{commit}:{act}/{name}'))
        except subprocess.CalledProcessError:
            sys.exit(f'{act}/{name} was not in the text on {day}.')
        return
    files = [f for f in git('ls-tree', '-r', '--name-only', commit, f'{act}/').split('\n')
             if f.endswith('.md') and not f.endswith('/README.md')]
    files = sorted(files, key=order)
    # One git cat-file --batch for the whole act, not one git show per file.
    data = subprocess.run(['git', 'cat-file', '--batch'], input=''.join(f'{commit}:{f}\n' for f in files).encode('utf-8'),
                          capture_output=True, check=True).stdout
    pos = 0
    for _ in files:
        nl = data.index(b'\n', pos)
        size = int(data[pos:nl].split()[2])
        sys.stdout.write(data[nl + 1:nl + 1 + size].decode('utf-8') + '\n')
        pos = nl + 1 + size + 1


if __name__ == '__main__':
    main()
