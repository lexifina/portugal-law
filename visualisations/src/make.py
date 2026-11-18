"""Rebuild visualisations/o-direito-portugues-em-20-graficos.html from this repository.

    python visualisations/src/make.py [--repo PATH] [--ref REF] [--skip-extract]

Steps (all read-only on the repository; scratch output goes to visualisations/src/.build/):
  1. git log of REF (default origin/main), streamed once, one record per commit; each commit is sorted by its author's
     e-mail domain and its trailers (Kind, Law, Published, In-force, In-force-basis, Act-path, Record-type, Legislature,
     Court, Process, Record-path) into small tables:
       dr.tsv        every act of the Diário do Governo and the Diário da República (1.ª and 2.ª série): its record kind
                     (original, metadata, consolidated, correction), name, day and series of publication, folder,
                     day in force and how that day was found, and its summary (sumário)
       dr_amend.tsv  every amending act the consolidated histories name, with the act it changed and its summary
       ar_*.tsv      the Assembleia da República's open data: initiatives and their phases, State Budget amendment
                     proposals, MPs' written questions and requests and the Government's answers, petitions
       tc.tsv, caad.tsv, joram.tsv   Constitutional Court rulings, CAAD tax-arbitration decisions, the Madeira journal
       counts.json   records of every other kind, counted by year (DGSI courts, PGR opinions, Tribunal de Contas...)
  2. git log --name-status of the Constitution and the codes (code/, constitution/, and their folders before the
     move of 10 November 2026: constituicao/, codigo-civil/, codigo-do-trabalho/)            -> codes.tsv
  3. blobs, fetched in batches in a blobless clone: the record.json of every Constitutional Court ruling (its kind
     of proceedings) and every version of every file of the Constitution                    -> tc-records.jsonl, const.jsonl
  4. prep.py turns those into .build/data.json; build.py fills page.tpl.html with it.
Works in a blobless (--filter=blob:none) or --no-checkout clone: the history is read from commit objects and only
some 34,000 small blobs are read. Nothing large is held in memory; the history is streamed line by line.
"""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--repo', default=os.path.abspath(os.path.join(HERE, '..', '..')))
ap.add_argument('--ref', default=None, help='default: origin/main if present, else HEAD')
ap.add_argument('--out', default=os.path.join(HERE, '..', 'o-direito-portugues-em-20-graficos.html'))
ap.add_argument('--skip-extract', action='store_true', help='reuse .build/ from a previous run (prep and build only)')
a = ap.parse_args()
B = os.path.join(HERE, '.build')
os.makedirs(B, exist_ok=True)
NOLAZY = dict(os.environ, GIT_NO_LAZY_FETCH='1')
GIT = ['git', '-C', a.repo, '-c', 'core.quotepath=off']


def git(*args):
    return subprocess.run([*GIT, *args], check=True, capture_output=True, env=NOLAZY).stdout


def has(ref):
    return subprocess.run([*GIT, 'rev-parse', '--verify', '-q', ref], capture_output=True).returncode == 0


ref = a.ref or ('origin/main' if has('origin/main') else 'HEAD')
sha = git('rev-parse', ref).decode().strip()
print('ref', ref, sha, flush=True)


def stream(args):
    """yield the records of a git log whose format starts each record with \\x1e"""
    p = subprocess.Popen([*GIT, *args], stdout=subprocess.PIPE, env=NOLAZY)
    buf = b''
    for chunk in iter(lambda: p.stdout.read(1 << 16), b''):
        buf += chunk
        *recs, buf = buf.split(b'\x1e')
        for r in recs:
            if r.strip():
                yield r.decode('utf-8', 'replace')
    if buf.strip():
        yield buf.decode('utf-8', 'replace')
    p.wait()
    if p.returncode:
        sys.exit('git ' + ' '.join(args[:2]) + ' failed')


def fetch_missing(oids, batch=4000):
    """batched fetches for the blobs a partial clone does not have yet"""
    oids = sorted(set(oids))
    chk = subprocess.run([*GIT, 'cat-file', '--batch-check'], input=''.join(o + '\n' for o in oids).encode(),
                         capture_output=True, env=NOLAZY).stdout.decode().split('\n')
    missing = [l.split()[0] for l in chk if l.endswith(' missing')]
    for i in range(0, len(missing), batch):
        part = missing[i:i + batch]
        print('fetching', len(part), 'blobs', f'({i + len(part)} of {len(missing)})', flush=True)
        subprocess.run([*GIT, '-c', 'fetch.negotiationAlgorithm=noop', 'fetch', 'origin', '--no-tags', '--no-write-fetch-head',
                        '--recurse-submodules=no', '--filter=blob:none', '--stdin'], input=''.join(m + '\n' for m in part).encode(), check=False)


def read_blobs(oids):
    """yield (oid, bytes) one blob at a time"""
    p = subprocess.Popen([*GIT, 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=NOLAZY)
    for oid in oids:
        p.stdin.write((oid + '\n').encode()); p.stdin.flush()
        head = p.stdout.readline().split()
        if len(head) < 3:
            sys.exit('cannot read blob ' + oid)
        data = p.stdout.read(int(head[2])); p.stdout.read(1)
        yield oid, data
    p.stdin.close(); p.wait()


TR = re.compile(r'^([A-Z][A-Za-z-]+): (.*)$')
clean = lambda s, n=None: (s if n is None else s[:n]).replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').strip()


def basis_code(b):
    if b.startswith('own commencement') or b.startswith('earliest of'):
        return 'clause'
    if 'general rule' in b or 'Lei n.º 74/98' in b:
        return 'rule'
    if b.startswith('publication day') or b.startswith('issue day'):
        return 'pub'
    return 'other'


if not a.skip_extract:
    # ---------------------------------------------------------------- 1. the history, streamed once
    out = {n: open(os.path.join(B, n + '.tsv'), 'w', encoding='utf-8', newline='\n') for n in
           ['dr', 'dr_amend', 'ar_ini', 'ar_fase', 'ar_oe', 'ar_q', 'ar_ans', 'ar_pet', 'tc', 'caad', 'joram']}
    counts = {}

    def bump(group, key, year):
        g = counts.setdefault(group, {}).setdefault(key, {})
        g[year] = g.get(year, 0) + 1

    def w(name, row):
        out[name].write('\t'.join(clean(str(x)) for x in row) + '\n')

    n = 0
    fmt = '%x1e%H%x1f%an%x1f%ae%x1f%aI%x1f%s%x1f%b'
    for rec in stream(['log', ref, '--format=' + fmt]):
        n += 1
        parts = rec.split('\x1f')
        if len(parts) < 6:
            continue
        h, an, ae, ad, subj, body = parts[0].strip(), parts[1], parts[2], parts[3], parts[4], parts[5]
        tr = {}
        for line in body.split('\n'):
            m = TR.match(line.rstrip('\r'))
            if m:
                tr.setdefault(m.group(1), []).append(m.group(2).strip())
        g = lambda k: (tr.get(k) or [''])[0]
        dom = ae.split('@')[-1]
        kind = g('Kind')
        first = body.split('\n\n')[0].replace('\n', ' ').strip()
        if dom == 'diariodarepublica.invalid':
            pub = g('Published')
            series = 'DG' if 'Diário do Governo' in pub else ('DR2' if '2.ª série' in pub else ('DR1' if '1.ª série' in pub else 'DR'))
            if kind in ('original', 'metadata', 'consolidated', 'correction'):
                if 'Registo sem texto' in first:
                    first = ''
                basis = g('In-force-basis')
                clause = ''
                m = re.search(r'"([^"]{0,200})', basis)
                if m and basis_code(basis) == 'clause':
                    clause = m.group(1)
                w('dr', [kind, g('Law'), pub[:10], series, g('Act-path'), g('In-force'), basis_code(basis), clause, clean(first, 500)])
            elif kind:
                orig = 'texto original' in subj
                w('dr_amend', [an, pub[:10], g('In-force'), g('Act-path'), g('Files'), 'O' if orig else '', clean(first, 400)])
        elif dom == 'parlamento-pt.invalid':
            rt, leg = g('Record-type'), g('Legislature')
            path = g('Record-path') or g('Act-path')
            p = path.split('/')
            if rt == 'iniciativa' and len(p) >= 6:
                author = first[len('Autoria: '):] if first.startswith('Autoria: ') else ''
                w('ar_ini', ['/'.join([p[2], p[3], p[5]]), leg, p[3], p[5], ad[:10], author, clean(subj.split(': ', 1)[-1], 160)])
            elif rt == 'iniciativa-fase' and len(p) >= 6:
                w('ar_fase', ['/'.join([p[2], p[3], p[5]]), ad[:10], subj.split(': ', 1)[-1]])
            elif rt == 'proposta-alteracao-oe' and len(p) >= 3:
                w('ar_oe', [p[2], leg, ad[:10], clean(first, 300)])
            elif rt in ('pergunta', 'requerimento'):
                rec_ = first.split('Destinatário(s):', 1)
                w('ar_q', [path[:-5] if path.endswith('.json') else path, rt, leg, ad[:10], an, clean(rec_[1], 200) if len(rec_) > 1 else ''])
            elif rt == 'resposta':
                w('ar_ans', [path.split('.resposta')[0], ad[:10], an])
            elif rt == 'peticao':
                w('ar_pet', [leg, ad[:10], clean(first, 200)])
            bump('ar', rt, leg or ad[:4])
        elif dom == 'tribunalconstitucional-pt.invalid':
            w('tc', [g('Act-path'), g('In-force') or ad[:10], g('Process'), clean(subj, 160)])
        elif dom == 'caad-org-pt.invalid':
            w('caad', [g('In-force') or ad[:10], g('Process'), clean(first, 300)])
        elif dom == 'madeira-gov-pt.invalid':
            if kind == 'original':
                ap_ = g('Act-path').split('/')
                w('joram', [ap_[3] if len(ap_) > 3 else '', g('Published')[:10], g('Law'), clean(first, 300)])
            else:
                bump('joram', kind or 'other', ad[:4])
        elif dom == 'dgsi-pt.invalid':
            ap_ = g('Act-path').split('/')
            bump('dgsi', ap_[1] if len(ap_) > 1 else '?', (g('In-force') or ad)[:4])
        elif dom != 'lexifina.com':
            bump('other', dom.split('.')[0] + ':' + (kind or '?'), (g('In-force') or ad)[:4])
        if n % 200000 == 0:
            print('commits read', n, flush=True)
    for f in out.values():
        f.close()
    counts['commits'] = n
    json.dump(counts, open(os.path.join(B, 'counts.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('commits', n, flush=True)

    # ---------------------------------------------------------------- 2. the Constitution and the codes, file by file
    paths = ['code', 'constitution', 'constituicao', 'codigo-civil', 'codigo-do-trabalho']
    fmt = '%x1e@@%h%x1f%an%x1f%(trailers:key=In-force,valueonly,separator=;)%x1f%(trailers:key=Kind,valueonly,separator=;)%x1f%(trailers:key=Published,valueonly,separator=;)'
    nc = 0
    with open(os.path.join(B, 'codes.tsv'), 'w', encoding='utf-8', newline='\n') as fo:
        for rec in stream(['log', ref, '--no-renames', '--raw', '--no-abbrev', '--format=' + fmt, '--', *paths]):
            head, _, rest = rec.partition('\n')
            p = head[2:].split('\x1f')
            if len(p) < 5:
                continue
            for line in rest.split('\n'):
                if not line.startswith(':'):
                    continue
                meta, path = line.split('\t', 1)
                mm = meta.split()
                fo.write('\t'.join([p[0], clean(p[1]), p[2][:10], clean(p[3]), p[4][:10], mm[4][:1], mm[3], path]) + '\n')
                nc += 1
    print('code file changes', nc, flush=True)

    # ---------------------------------------------------------------- 3. blobs: Constitutional Court records, Constitution versions
    tcs = []
    lt = subprocess.run([*GIT, 'ls-tree', '-r', ref, '--', 'jurisprudencia/tc', 'jurisprudencia/tc-decisoes-sumarias'],
                        capture_output=True, env=NOLAZY, check=True).stdout.decode('utf-8', 'replace')
    for line in lt.split('\n'):
        if line.endswith('/record.json'):
            meta, path = line.split('\t', 1)
            tcs.append((meta.split()[2], path))
    const = []
    for line in open(os.path.join(B, 'codes.tsv'), encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        if (f[7].startswith('constituicao/') or f[7].startswith('constitution/')) and f[5] in 'AM' and not set(f[6]) <= {'0'}:
            const.append((f[6], f[0], f[7]))
    fetch_missing([o for o, _ in tcs] + [o for o, _, _ in const])
    with open(os.path.join(B, 'tc-records.jsonl'), 'w', encoding='utf-8', newline='\n') as fo:
        paths_of = dict((o, p) for o, p in tcs)
        for oid, data in read_blobs([o for o, _ in tcs]):
            try:
                r = json.loads(data.decode('utf-8'))
            except ValueError:
                continue
            fo.write(json.dumps({'p': paths_of[oid], 'kind': r.get('kind'), 'formation': r.get('formation'), 'number': r.get('number'),
                                 'day': r.get('decision_day') or r.get('in_force')}, ensure_ascii=False) + '\n')
    with open(os.path.join(B, 'const.jsonl'), 'w', encoding='utf-8', newline='\n') as fo:
        meta_of = {}
        for o, c, p in const:
            meta_of.setdefault(o, []).append((c, p))
        for oid, data in read_blobs(sorted(meta_of)):
            for c, p in meta_of[oid]:
                fo.write(json.dumps({'c': c, 'p': p, 'oid': oid, 't': data.decode('utf-8', 'replace')}, ensure_ascii=False) + '\n')
    print('TC records', len(tcs), '| Constitution file versions', len(const), flush=True)

# ---------------------------------------------------------------- 4. prep + build
env = dict(os.environ, HEAD_SHA=sha, HEAD_REF=ref)
subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'prep.py'), B], check=True, env=env)
subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'build.py'), os.path.join(B, 'data.json'), os.path.abspath(a.out)], check=True)
