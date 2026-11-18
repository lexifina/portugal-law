"""Compute every number of the 20 charts and the data profile from the tables make.py extracted.

    python prep.py <.build folder>          -> <.build folder>/data.json

All classification rules are here, in plain regular expressions over the names and summaries (sumários) the
Diário da República gives each act, the Assembleia da República's open data and the courts' records. Whatever no
rule recognises is counted as "other". The tables are read line by line.
"""
import calendar, collections, datetime as dt, json, os, re, statistics, sys

B = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '.build')
D = {}
P = {}
C = collections.Counter
dd = collections.defaultdict


def rows(name):
    with open(os.path.join(B, name), encoding='utf-8') as f:
        for line in f:
            yield line.rstrip('\n').split('\t')


def day(s):
    try:
        return dt.date.fromisoformat(s[:10])
    except (ValueError, TypeError):
        return None


BUILT = None   # the last day the record reaches (the latest act of the 1.ª série)

# ------------------------------------------------------------------------------------------- the acts of the 1.ª série
# A name like "Decreto-Lei n.º 10-A/2020", "Lei n.º 1883", "Portaria de 1990-12-26": its kind is the words before " n.º"
# or " de <date>".
KIND_OF = [
    ('lc', r'^Lei Constitucional\b'), ('lo', r'^Lei Orgânica\b'), ('lei', r'^Lei\b'),
    ('dl', r'^Decreto-Lei\b'), ('dlr', r'^Decreto Legislativo Regional\b'), ('drr', r'^Decreto Regulamentar Regional\b'),
    ('dreg', r'^Decreto Regulamentar\b'), ('dpr', r'^Decreto do Presidente da República\b'),
    ('dec', r'^Decreto\b'), ('port', r'^Portaria\b'),
    ('rcm', r'^Resolução do Conselho de Ministros\b'), ('rar', r'^Resolução da Assemb?lei?a (da República|Nacional)\b'),
    ('res', r'^Resolução\b'), ('ret', r'^(Declaração de Re(c)?tificação|Re(c)?tificação|Nova Publicação \(Re(c)?tificação\))'),
    ('dn', r'^Despacho Normativo\b'), ('desp', r'^Despacho\b'), ('aviso', r'^Aviso\b'), ('decl', r'^Declaração\b'),
    ('ac', r'^(Acórdão|Assento)\b'), ('orc', r'^Orçamento\b'),
]
KIND_RX = [(k, re.compile(r)) for k, r in KIND_OF]


def kind_of(name):
    for k, r in KIND_RX:
        if r.search(name):
            return k
    return 'other'


NUM = re.compile(r'n\.º\s*(\d+)(?:-([A-Z][A-Z0-9]*))?(?:/(\d{2,4}))?')
NUMBERED = re.compile(r' n\.(?:º|os) ')
acts = {}       # (name, pub) -> [kind, pub date, series, path, inforce, basis, clause, summary, record kind]
s2 = C()        # 2.ª série records by (kind word, year)
s2_sum = []     # (yyyy-mm, summary) of 2.ª série acts with a summary, for the spelling chart
RANK = {'original': 3, 'consolidated': 3, 'metadata': 1, 'correction': 2}
for f in rows('dr.tsv'):
    if len(f) < 9:
        continue
    rk, name, pub, series, path, inforce, basis, clause, summ = f[:9]
    if not name or not pub:
        continue
    if series == 'DR2':
        kw = path.split('/')[1] if path.startswith('serie-2/') else 'other'
        s2[(kw, pub[:4])] += 1
        if summ:
            s2_sum.append((pub[:7], summ))
        continue
    key = (name, pub) if NUMBERED.search(name) else (name, pub, path)
    old = acts.get(key)
    if old and RANK[old[8]] >= RANK.get(rk, 0) and (old[7] or not summ):
        continue
    acts[key] = [kind_of(name), pub, series, path, inforce, basis, clause, summ, rk]
# the first texts of consolidated acts and the amending acts the histories name fill in acts the tables above lack
for f in rows('dr_amend.tsv'):
    if len(f) < 7:
        continue
    an, pub, inforce, path, files, orig, summ = f[:7]
    if not pub or not re.search(r' n\.º ', an):
        continue
    if NUMBERED.search(an) and (an, pub) not in acts:
        acts[(an, pub)] = [kind_of(an), pub, 'DR', path if orig else '', inforce, '', '', summ, 'amend']
# before 1991 a rectification is a "Declaração de <date>" whose summary begins "De ter sido rectificado..."
RET_DECL = re.compile(r'^De ter(?:em)? sido re(?:c)?tificad', re.I)
for k, v in acts.items():
    if v[0] == 'decl' and RET_DECL.match(v[7] or ''):
        v[0] = 'ret'
ALL = sorted((((k[0], k[1]), v) for k, v in acts.items()), key=lambda kv: kv[1][1])
BUILT = max(v[1] for _, v in ALL if v[1] <= '2026-12-31')
Y0, Y1 = 1910, int(BUILT[:4])
print('acts of the 1.ª série', len(ALL), 'to', BUILT)

# ------------------------------------------------------------------------------------------- 1. the 1.ª série, year by year
G1 = {'lei': 'lei', 'lo': 'lei', 'lc': 'lei', 'dl': 'dl', 'dec': 'dec', 'port': 'port', 'rcm': 'res', 'res': 'res', 'rar': 'res',
      'dpr': 'other', 'ret': 'ret', 'dreg': 'other', 'dn': 'other', 'desp': 'other', 'aviso': 'aviso', 'decl': 'aviso',
      'ac': 'other', 'orc': 'other', 'dlr': 'other', 'drr': 'other', 'other': 'other'}
c01 = dd(C)
for (name, pub), v in ALL:
    c01[int(pub[:4])][G1[v[0]]] += 1
D['c01'] = {'rows': [dict(y=y, **c01[y]) for y in range(Y0, Y1 + 1)], 'built': BUILT,
            'kinds': C(v[0] for _, v in ALL), 'first': ALL[0][1][1]}

# ------------------------------------------------------------------------------------------- 2. laws and decree-laws
REG = [('rep1', '1910-10-05', '1926-05-28'), ('dit', '1926-05-28', '1933-04-11'), ('en', '1933-04-11', '1974-04-25'),
       ('rev', '1974-04-25', '1976-04-25'), ('dem', '1976-04-25', '9999-12-31')]
c02 = dd(lambda: [0, 0])
reg = {r[0]: [0, 0] for r in REG}
first_dl = None
for (name, pub), v in ALL:
    k = v[0]
    if k not in ('lei', 'lo', 'lc', 'dl'):
        continue
    i = 1 if k == 'dl' else 0
    c02[int(pub[:4])][i] += 1
    for r, a0, a1 in REG:
        if a0 <= pub < a1:
            reg[r][i] += 1
    if k == 'dl' and (first_dl is None or pub < first_dl[1]):
        first_dl = (name, pub)
regs = []
for r, a0, a1 in REG:
    e = min(a1, BUILT)
    yrs = (day(e) - day(a0)).days / 365.2425
    regs.append({'k': r, 'from': a0, 'to': a1 if a1 < '9999' else None, 'laws': reg[r][0], 'dls': reg[r][1], 'yrs': round(yrs, 2)})
D['c02'] = {'rows': [[y, *c02[y]] for y in range(1911, Y1 + 1)], 'regimes': regs, 'first_dl': first_dl}

# ------------------------------------------------------------------------------------------- 3. the overseas territories
TERR = {'AO': r'\bAngola\b', 'MZ': r'\bMo[çc]ambique\b', 'GW': r'\bGuin[ée]\b(?!\s+Equatorial)', 'CV': r'\bCabo\s+Verde\b',
        'ST': r'\bS(?:ão|\.)\s*Tom[ée]\b', 'TL': r'\bTimor\b', 'MO': r'\bMacau\b', 'IN': r'\b(?:Estado\s+da\s+[ÍI]ndia|Goa|Dam[ãa]o|Diu)\b'}
TRX = {k: re.compile(v) for k, v in TERR.items()}
ULT = re.compile(r'\b(ultramar\w*|ultra-mar\w*|col[óo]nias?|coloniais|colonial|prov[íi]ncias?\s+ultramarinas?)\b', re.I)
c03y = dd(lambda: [0, 0, 0])          # year -> [acts with a summary, naming a territory or the ultramar, any territory]
c03t = dd(C)                          # territory -> year -> acts
for (name, pub), v in ALL:
    s = v[7]
    if not s:
        continue
    y = int(pub[:4])
    hit = [k for k, r in TRX.items() if r.search(s)]
    c03y[y][0] += 1
    if hit or ULT.search(s):
        c03y[y][1] += 1
    if hit:
        c03y[y][2] += 1
    for k in hit:
        c03t[k][y] += 1
D['c03'] = {'years': [[y, *c03y[y]] for y in range(Y0, Y1 + 1)], 'terr': {k: dict(c03t[k]) for k in TERR}}

# ------------------------------------------------------------------------------------------- 4. nationalisations and privatisations
NAC = re.compile(r'\bnacionaliza\w*|\bnacionalizad\w*', re.I)
NAC_NOT = re.compile(r'\b(desnacionaliz\w*|mercadorias\s+(?:nacionais\s+ou\s+)?nacionalizad\w*|nacionais\s+ou\s+nacionalizad\w*|não\s+nacionalizad\w*)', re.I)
PRIV = re.compile(r'\b(re)?privatiza\w*', re.I)
c04 = dd(lambda: [0, 0])
ex04 = {'n': [], 'p': []}
for (name, pub), v in ALL:
    if v[0] not in ('dl', 'lei', 'lo', 'rcm', 'res', 'dec'):
        continue
    s = v[7]
    y = int(pub[:4])
    if y < 1960:
        continue
    if NAC.search(NAC_NOT.sub('', s)):
        c04[y][0] += 1
        ex04['n'].append([pub, name, s[:220]])
    if PRIV.search(s):
        c04[y][1] += 1
        ex04['p'].append([pub, name, s[:220]])
D['c04'] = {'rows': [[y, *c04[y]] for y in range(1960, Y1 + 1)],
            'ex': {k: [[a, b, c[:170]] for a, b, c in sorted(v)] for k, v in ex04.items()}}

# ------------------------------------------------------------------------------------------- 5. the weekday of publication
c05 = dd(lambda: [0] * 7)
for (name, pub), v in ALL:
    d = day(pub)
    if d:
        c05[d.year][d.weekday()] += 1
sat_last = max((pub for (name, pub), v in ALL if day(pub) and day(pub).weekday() == 5 and pub < '2006-01-01'), default=None)
late_sat = C(pub[:4] for (name, pub), v in ALL if day(pub) and day(pub).weekday() >= 5 and pub >= '2006-01-01')
late_days = sorted(C(pub for (name, pub), v in ALL if day(pub) and day(pub).weekday() >= 5 and pub >= '2006-01-01').items())
D['c05'] = {'rows': [[y, *c05[y]] for y in range(1911, Y1 + 1)], 'sat_last_regular': sat_last, 'weekend_after_2005': late_days}

# ------------------------------------------------------------------------------------------- 6. the spelling of 1990
PAIRS = [('acção', r'\bac[çc][ãa]o\b|\bac[çc][õo]es\b', r'\ba[çc][ãa]o\b|\ba[çc][õo]es\b', 'ação'),
         ('actividade', r'\bactividades?\b', r'\batividades?\b', 'atividade'),
         ('direcção', r'\bdirec[çc](?:ão|ões)\b', r'\bdire[çc](?:ão|ões)\b', 'direção'),
         ('efectivo', r'\befectiv\w*', r'\befetiv\w*', 'efetivo'),
         ('projecto', r'\bprojectos?\b', r'\bprojetos?\b', 'projeto'),
         ('sector', r'\bsector(?:es|ial|iais)?\b', r'\bsetor(?:es|ial|iais)?\b', 'setor')]
PRX = [(a, re.compile(o, re.I), re.compile(n, re.I), b) for a, o, n, b in PAIRS]
OLDW = re.compile(r'\b(ac[çc][ãa]o|ac[çc][õo]es|actividades?|actua(?:l|is|lmente|liza\w*)|efectiv\w*|colectiv\w*|direc[çc](?:ão|ões)|direct(?:or|ora|ores|iva|ivas|o|a|os|as|amente)\b|project\w*|protec[çc]\w*|objectiv\w*|electr\w*|selec[çc]\w*|inspec[çc]\w*|infrac[çc]\w*|sector\w*|adop[çc]\w*|rectifica\w*|exact\w*|óptim\w*|baptis\w*|lectiv\w*|correcç\w*)\b', re.I)
NEWW = re.compile(r'\b(a[çc][ãa]o|a[çc][õo]es|atividades?|atua(?:l|is|lmente|liza\w*)|efetiv\w*|coletiv\w*|dire[çc](?:ão|ões)|diret(?:or|ora|ores|iva|ivas|o|a|os|as|amente)\b|projet\w*|prote[çc]\w*|objetiv\w*|eletr\w*|sele[çc]\w*|inspe[çc]\w*|infra[çc]\w*|setor\w*|ado[çc]\w*|retifica\w*|exat\w*|ótim\w*|batis\w*|letiv\w*|correç\w*)\b', re.I)
m06 = dd(lambda: [0, 0])     # month -> [old forms, new forms]
y06 = dd(lambda: dd(lambda: [0, 0]))
ex06 = {}
for src in (((pub[:7], v[7]) for (name, pub), v in ALL if v[7] and pub >= '1990'), iter(s2_sum)):
    for ym, s in src:
        o = len(OLDW.findall(s)); n = len(NEWW.findall(s))
        if o or n:
            m06[ym][0] += o; m06[ym][1] += n
        y = ym[:4]
        for a, ro, rn, b in PRX:
            no, nn = len(ro.findall(s)), len(rn.findall(s))
            if no or nn:
                y06[a][y][0] += no; y06[a][y][1] += nn
RCM_AO = [[name, pub, v[7]] for (name, pub), v in ALL if re.search(r'Acordo Ortogr', v[7] or '') and v[0] in ('rcm', 'dl', 'lei', 'dec', 'res', 'rar')]
D['c06'] = {'months': sorted([k, *v] for k, v in m06.items() if k >= '1990'), 'pairs': [[a, b] for a, _, _, b in PRX],
            'years': {a: sorted([y, *v] for y, v in y06[a].items()) for a, _, _, _ in PRX}, 'ao_acts': RCM_AO}

# ------------------------------------------------------------------------------------------- 7. declarations of rectification
# the act a declaration corrects: the first act name in its summary that the record holds, matched with the year its
# number carries (or, for numbers without a year, the date the summary gives)
by_num = {}
for (name, pub), v in ALL:
    m = NUM.search(name)
    k = name.split(' n.º')[0]
    if m:
        yy = m.group(3)
        if yy:
            yy = int(yy); yy = yy if yy > 999 else (1900 + yy if yy > 30 else 2000 + yy)
        by_num.setdefault((k, m.group(1) + ('-' + m.group(2) if m.group(2) else ''), yy or int(pub[:4])), pub)
REF = re.compile(r'(Decreto-Lei|Decreto Regulamentar|Decreto Legislativo Regional|Decreto do Presidente da República|Decreto|Lei Orgânica|Lei Constitucional|Lei|Portaria|Resolução do Conselho de Ministros|Resolução da Assembleia da República|Despacho Normativo|Declaração de Re(?:c)?tificação)\s+n\.º\s*(\d+)(?:-([A-Z][A-Z0-9]*))?(?:/(\d{2,4}))?')
MONTHS = {'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}
c07 = dd(lambda: [0, 0])     # year -> [declarations, published on the last day of a month]
lags = []                    # (year, days)
for (name, pub), v in ALL:
    if v[0] != 'ret' or int(pub[:4]) < 1976:
        continue
    d = day(pub)
    y = d.year
    c07[y][0] += 1
    if d.day == calendar.monthrange(y, d.month)[1]:
        c07[y][1] += 1
    m = REF.search(v[7] or '')
    if not m:
        continue
    k, num, let, yy = m.group(1), m.group(2), m.group(3), m.group(4)
    if yy:
        yy = int(yy); yy = yy if yy > 999 else (1900 + yy if yy > 30 else 2000 + yy)
    else:
        yy = y
    tp = by_num.get((k, num + ('-' + let if let else ''), yy)) or (by_num.get((k, num + ('-' + let if let else ''), yy - 1)) if not m.group(4) else None)
    if tp and tp <= pub:
        lags.append([y, (d - day(tp)).days])
LAGB = [(0, 30), (31, 60), (61, 90), (91, 10 ** 6)]
PER7 = [(1976, 1982), (1983, 1990), (1991, 1998), (1999, 2004), (2005, 2011), (2012, Y1)]
lagrows = []
for a0, a1 in PER7:
    v = [l for y, l in lags if a0 <= y <= a1]
    lagrows.append({'p': [a0, a1], 'n': len(v), 'b': [sum(1 for l in v if lo <= l <= hi) for lo, hi in LAGB],
                    'med': statistics.median(v) if v else None})
D['c07'] = {'rows': [[y, *c07[y]] for y in range(1976, Y1 + 1)], 'lagrows': lagrows, 'matched': len(lags),
            'n': sum(r[0] for r in c07.values())}

# ------------------------------------------------------------------------------------------- 8. the State Budget
BUD = re.compile(r'^(?:Aprova o |Aprova a |Aprova as linhas gerais do )?Orçamento (?:Geral )?do Estado p[ae]ra (\d{4})\s*(\(provisório\)|e fundamentais da organização do orçamento da segurança social para o mesmo ano)?\.?$')
TRANS = re.compile(r'regime (?:transitório de execução orçamental|de execução orçamental duodecimal)', re.I)
EXE = re.compile(r'^Estabelece (?:as )?normas de execução do Orçamento do Estado para (\d{4})\.?$')
bud, exe, trans = {}, {}, []
for (name, pub), v in ALL:
    s = (v[7] or '').strip()
    if v[0] in ('lei',):
        m = BUD.match(s)
        if m:
            y = int(m.group(1))
            if y not in bud or pub < bud[y][1]:
                bud[y] = [name, pub, s[:160], bool(m.group(2))]
    if v[0] == 'dl' and TRANS.search(s):
        trans.append([name, pub, s[:200]])
    if v[0] == 'dl':
        m = EXE.match(s)
        if m:
            y = int(m.group(1))
            if y not in exe or pub < exe[y][1]:
                exe[y] = [name, pub]
# budgets approved before 1983 by a decree-law or a law on the "linhas gerais" (kept as they are, for the table)
pre = []
for (name, pub), v in ALL:
    s = (v[7] or '')
    if '1975' <= pub[:4] <= '1982' and re.search(r'Orçamento Geral do Estado para \d{4}', s) and not re.search(r'[Aa]ltera|revisão|suplementar|execução', s):
        pre.append([name, pub, s[:160]])
D['c08'] = {'bud': {y: bud[y] for y in sorted(bud)}, 'exe': {y: exe[y] for y in sorted(exe)}, 'trans': trans}

# ------------------------------------------------------------------------------------------- 9. EU directives
DIR = re.compile(r'\bDire(?:c)?tivas?\b')
DIRN = re.compile(r'\b(?:(?:\((?:UE|CE|CEE|Euratom)\)\s*)?(?:n\.º\s*)?(\d{2,4})/(\d{1,4})(?:/(CE|CEE|UE|Euratom|EU))?)')
c09 = dd(lambda: [0, 0, 0, 0])     # year -> [decree-laws, citing a directive, laws, citing a directive]
dirs = dd(set)
c09t = [0, 0]   # summaries citing a directive, of which saying they transpose
for (name, pub), v in ALL:
    y = int(pub[:4])
    if y < 1986 or v[0] not in ('dl', 'lei', 'lo'):
        continue
    i = 0 if v[0] == 'dl' else 2
    c09[y][i] += 1
    s = v[7]
    if DIR.search(s):
        c09[y][i + 1] += 1
        c09t[0] += 1
        c09t[1] += bool(re.search(r'\btranspo|\btransposição', s, re.I))
        for seg in re.split(r'\bDire(?:c)?tivas?\b', s)[1:]:
            for m in DIRN.finditer(seg[:220]):
                a_, b_ = m.group(1), m.group(2)
                if len(a_) == 4 or (len(a_) == 2 and m.group(3)):
                    dirs[y].add(f'{a_}/{b_}' if len(a_) == 4 or int(a_) > 50 else f'{b_}/{a_}')
D['c09'] = {'rows': [[y, *c09[y], len(dirs[y])] for y in range(1986, Y1 + 1)],
            'distinct': len(set().union(*dirs.values())) if dirs else 0, 'transp': c09t}

# ------------------------------------------------------------------------------------------- 10. Madeira (JORAM, I série)
JK = [('rcgr', r'^resolucao(-do-conselho-do-governo-regional)?$'), ('port', r'^(portaria|poraria|portaria-conjunta)$'),
      ('dlr', r'^decreto-legislativo-regional$'), ('drr', r'^decreto-regulamentar-?regional$'),
      ('ralram', r'^resolucao-da-assembleia-legislativa'), ('ret', r'^declaracao-de-re(c)?tificacao$'), ('dn', r'^despacho-normativo$')]
JKR = [(k, re.compile(r)) for k, r in JK]
c10 = dd(C)
jn = C()
for f in rows('joram.tsv'):
    if len(f) < 4:
        continue
    k = next((kk for kk, r in JKR if r.search(f[0])), 'other')
    if not f[1]:
        continue
    c10[int(f[1][:4])][k] += 1
    jn[f[0]] += 1
D['c10'] = {'rows': [dict(y=y, **c10[y]) for y in sorted(c10)], 'kinds_raw': jn}

# ------------------------------------------------------------------------------------------- the Assembleia da República
LEG = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII']
ini = {}
legspan = dd(lambda: ['9999', '0000'])
maxnum = dd(int)
for f in rows('ar_ini.tsv'):
    if len(f) < 7:
        continue
    key, leg, typ, num, d_, author, title = f[:7]
    ini[key] = [leg, typ, num, d_, author, title]
    if d_:
        legspan[leg][0] = min(legspan[leg][0], d_); legspan[leg][1] = max(legspan[leg][1], d_)
    try:
        maxnum[(leg, typ)] = max(maxnum[(leg, typ)], int(num))
    except ValueError:
        pass
ph = dd(set)
phd = dd(list)
for f in rows('ar_fase.tsv'):
    if len(f) < 3:
        continue
    ph[f[0]].add(f[2])
    phd[f[0]].append((f[1], f[2]))
    if f[1]:
        lg = f[0].split('/')[0].upper()
        legspan[lg][0] = min(legspan[lg][0], f[1]); legspan[lg][1] = max(legspan[lg][1], f[1])
inidates = dd(list)
for k_, v_ in ini.items():
    if v_[3]:
        inidates[v_[0]].append(v_[3])
legstart = {}
for lg in LEG:
    ds = sorted(inidates.get(lg, []))
    if ds:
        legstart[lg] = ds[int(len(ds) * 0.01)]
LEGSTART = {'I': '1976-06-03', 'II': '1980-11-13', 'III': '1983-05-31', 'IV': '1985-11-04', 'V': '1987-08-13', 'VI': '1991-11-04',
            'VII': '1995-10-27', 'VIII': '1999-10-25', 'IX': '2002-04-05', 'X': '2005-03-10', 'XI': '2009-10-15', 'XII': '2011-06-20',
            'XIII': '2015-10-23', 'XIV': '2019-10-25', 'XV': '2022-03-29', 'XVI': '2024-03-26', 'XVII': '2025-06-03'}
for i, lg in enumerate(LEG):
    legspan[lg] = [LEGSTART[lg], LEGSTART[LEG[i + 1]] if i + 1 < len(LEG) else None]
BECAME = lambda k: any(p.startswith('Lei (Publicação DR)') for p in ph.get(k, ()))
# 11. government bills and MPs' bills
c11 = {}
for leg in LEG:
    r = {'leg': leg, 'span': legspan[leg]}
    for typ, short in (('proposta-de-lei', 'gov'), ('projeto-de-lei', 'mps')):
        ks = [k for k, v in ini.items() if v[0] == leg and v[1] == typ]
        r[short] = [len(ks), sum(1 for k in ks if BECAME(k)), maxnum[(leg, typ)]]
    c11[leg] = r
D['c11'] = [c11[l] for l in LEG]
# 12. parties: MPs' bills by the party that signed them (a bill signed by several parties counts for each)
PARTY = re.compile(r'^(PS|PSD|PPD|PPD/PSD|PCP|BE|CDS-PP|CDS|PEV|PAN|CH|IL|L|PRD|MDP/CDE|UDP|ASDI|UEDS|PPM|JPP|LIVRE)$')
c12 = dd(lambda: [0, 0, set()])
for k, (leg, typ, num, d_, author, title) in ini.items():
    if typ != 'projeto-de-lei':
        continue
    ps = {('PSD' if p in ('PPD', 'PPD/PSD') else 'CDS-PP' if p == 'CDS' else 'L' if p == 'LIVRE' else p) for p in re.split(r'\s*,\s*', author.split(';')[0].strip()) if PARTY.match(p)}
    b = BECAME(k)
    for p in ps:
        c12[p][0] += 1; c12[p][1] += b; c12[p][2].add(leg)
D['c12'] = sorted([[p, v[0], v[1], sorted(v[2], key=LEG.index)] for p, v in c12.items() if v[0] >= 40], key=lambda r: -r[1])
# 13. State Budget amendment proposals
OE_ST = [('ok', r'^Aprovad'), ('no', r'^Rejeitad'), ('wd', r'^(Retirad|Prejudicad|Não Admitida|Substituíd|Avocad)'), ('pend', r'')]
OEX = [(k, re.compile(r)) for k, r in OE_ST]
c13 = dd(C)
c13p = dd(lambda: [0, 0, 0])
for f in rows('ar_oe.tsv'):
    if len(f) < 4:
        continue
    budget, leg, d_, first = f[:4]
    m = re.match(r'(\d{4})-or$', budget)
    if not m:
        continue
    y = int(m.group(1))
    parts = first.split(' — ')
    st = parts[-1] if len(parts) >= 3 else ''
    k = next(kk for kk, r in OEX if r.search(st))
    c13[y][k] += 1
    who = parts[0] if len(parts) >= 3 else ''
    ps = {('CDS-PP' if p == 'CDS' else p) for p in re.split(r'\s*,\s*', who) if PARTY.match(p)}
    for p in ps:
        c13p[p][0] += 1
        c13p[p][1] += (k == 'ok')
        c13p[p][2] += (k == 'pend')
D['c13'] = {'rows': [dict(y=y, **c13[y]) for y in sorted(c13) if y >= 2006], 'party': sorted([[p, *v] for p, v in c13p.items() if v[0] >= 200], key=lambda r: -r[1]),
            'early': {y: dict(c13[y]) for y in c13 if y < 2006}}
# 14. MPs' written questions and the Government's answers
q = {}
for f in rows('ar_q.tsv'):
    if len(f) < 6:
        continue
    q[f[0]] = (f[1], f[2], f[3])
first_ans = {}
for f in rows('ar_ans.tsv'):
    if len(f) < 3:
        continue
    k, d_ = f[0], f[1]
    if k in q and d_ and (k not in first_ans or d_ < first_ans[k]):
        first_ans[k] = d_
c14 = dd(lambda: [0, 0, 0, 0, 0, []])   # leg -> [questions, <=30 days, 31-90, >90, none, delays]
for k, (rt, leg, d_) in q.items():
    if rt != 'pergunta':
        continue
    r = c14[leg]
    r[0] += 1
    if k in first_ans:
        lag = (day(first_ans[k]) - day(d_)).days
        r[5].append(lag)
        r[1 if lag <= 30 else 2 if lag <= 90 else 3] += 1
    else:
        r[4] += 1
D['c14'] = [{'leg': leg, 'n': r[0], 'b': r[1:5], 'med': statistics.median(r[5]) if r[5] else None, 'span': legspan[leg],
             'req': sum(1 for kk, (rt, lg, dd_) in q.items() if rt == 'requerimento' and lg == leg)} for leg, r in sorted(c14.items(), key=lambda kv: LEG.index(kv[0]))]

# ------------------------------------------------------------------------------------------- the Constitution and the codes
code_rows = list(rows('codes.tsv'))
# 15. the Constitution: every file each revision changed, and the words it changed
const = dd(dict)        # commit -> path -> text
for line in open(os.path.join(B, 'const.jsonl'), encoding='utf-8'):
    r = json.loads(line)
    const[r['c']][r['p'].split('/')[-1]] = r['t']
cmeta = {}
cfiles = dd(list)
for h, an, inf, kind, pubd, st, oid, path in code_rows:
    if not (path.startswith('constituicao/') or path.startswith('constitution/constituicao/')) or kind == 'documentation' or an == 'Lexifina':
        continue
    cmeta[h] = (an, inf)
    cfiles[h].append((st, path.split('/')[-1]))
order = sorted(cmeta, key=lambda h: (cmeta[h][1], 1 if cmeta[h][0].startswith('Diário da República') else 0, h))
WORD = re.compile(r'\w+', re.U)
HEAD = re.compile(r'^#{1,2} ')


def body(t):
    """the article's own words: no part/title/chapter headings (they sit in the file of the first article of each division)"""
    out = []
    for line in t.split('\n'):
        if line.startswith('## ') or (line.startswith('# ') and not line.startswith('# Artigo')):
            continue
        out.append(line)
    return '\n'.join(out)


import difflib
PARTS = ['pf', 'p1', 'p2', 'p3', 'p4', 'dft']
PART_RX = [('pf', r'^## Princípios fundamentais'), ('p1', r'^## Parte I$'), ('p2', r'^## Parte II$'), ('p3', r'^## Parte III$'),
           ('p4', r'^## Parte IV$'), ('dft', r'^## Disposições finais e transitórias')]


def paras(state):
    """the Constitution as a list of (part, paragraph words): articles in number order, without the 'Artigo N.º' and
    division headings, so that an article that only changed its number does not count as changed"""
    out, part = [], 'pf'
    fns = sorted(fn for fn in state if fn.startswith('artigo'))
    for fn in (['preambulo.md'] if 'preambulo.md' in state else []) + fns:
        for line in state[fn].split('\n'):
            ls = line.strip()
            for k, rx in PART_RX:
                if re.match(rx, ls):
                    part = k
            if not ls or ls.startswith('#') and not ls.startswith('###'):
                continue
            w = WORD.findall(ls)
            if w:
                out.append(('pre' if fn == 'preambulo.md' else part, w))
    return out


cur, revs, prev = {}, [], []
for h in order:
    an, inf = cmeta[h]
    nf = {'A': 0, 'M': 0, 'D': 0}
    for st, fn in cfiles[h]:
        if st == 'D':
            if fn in cur:
                cur.pop(fn); nf['D'] += 1
            continue
        new = const.get(h, {}).get(fn)
        if new is None:
            continue
        nf['A' if fn not in cur else 'M'] += 1
        cur[fn] = new
    now = paras(cur)
    add, rem = C(), C()
    a_ = [' '.join(w) for _, w in prev]
    b_ = [' '.join(w) for _, w in now]
    sm = difflib.SequenceMatcher(None, a_, b_, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        wa = [(p, x) for p, w in prev[i1:i2] for x in w]
        wb = [(p, x) for p, w in now[j1:j2] for x in w]
        sw = difflib.SequenceMatcher(None, [x for _, x in wa], [x for _, x in wb], autojunk=False)
        for t2, k1, k2, l1, l2 in sw.get_opcodes():
            if t2 in ('replace', 'delete'):
                for p, _ in wa[k1:k2]:
                    rem[p] += 1
            if t2 in ('replace', 'insert'):
                for p, _ in wb[l1:l2]:
                    add[p] += 1
    size = C()
    for p, w in now:
        size[p] += len(w)
    revs.append({'act': an, 'day': inf, 'files': nf, 'add': dict(add), 'rem': dict(rem), 'size': dict(size),
                 'articles': sum(1 for fn in cur if fn.startswith('artigo'))})
    prev = now
# fold the changes the DR does not attribute and the deferred day of the 1982 revision into the revision they belong to
merged = []
for r in revs:
    if merged and (not r['act'].startswith('Lei Constitucional') and r['act'] != 'Decreto de Aprovação da Constituição' or r['act'] == merged[-1]['act']):
        m = merged[-1]
        for k in ('add', 'rem'):
            for p, v in r[k].items():
                m[k][p] = m[k].get(p, 0) + v
        for k in m['files']:
            m['files'][k] += r['files'][k]
        m['size'], m['articles'] = r['size'], r['articles']
        m.setdefault('also', []).append([r['act'], r['day']])
    else:
        merged.append(r)
revs = merged
part_of = {}
D['c15'] = {'revs': revs}

# 16. the codes: amending acts per year
c16 = dd(lambda: dd(set))
c16first = {}
for h, an, inf, kind, pubd, st, oid, path in code_rows:
    seg = path.split('/')
    code = seg[1] if seg[0] in ('code', 'constitution') else seg[0]
    if kind in ('documentation', 'consolidated') or an in ('Lexifina',) or not inf:
        continue
    if code not in c16first or inf < c16first[code]:
        c16first[code] = inf
for h, an, inf, kind, pubd, st, oid, path in code_rows:
    seg = path.split('/')
    code = seg[1] if seg[0] in ('code', 'constitution') else seg[0]
    if kind in ('documentation', 'consolidated') or an in ('Lexifina',) or not inf or inf == c16first.get(code):
        continue
    if not re.search(r' n\.º ', an) or an.startswith('Declaração') or an.startswith('Decreto de Aprovação') or kind == '':
        continue
    c16[code][int(inf[:4])].add(an)
D['c16'] = {'codes': {c: {str(y): len(v) for y, v in ys.items()} for c, ys in c16.items()},
            'acts': {c: len(set().union(*ys.values())) for c, ys in c16.items()}, 'first': c16first}

# 17. the Civil Code: the last change to each article
cc = dd(list)
for h, an, inf, kind, pubd, st, oid, path in code_rows:
    if not (path.startswith('codigo-civil/') or path.startswith('code/codigo-civil/')) or kind == 'documentation' or an == 'Lexifina':
        continue
    fn = path.split('/')[-1]
    if not fn.startswith('artigo-'):
        continue
    cc[fn].append((inf, st, an))
arts = []
for fn, vs in cc.items():
    vs.sort()
    m = re.match(r'artigo-0*(\d+)', fn)
    n = int(m.group(1))
    alive = vs[-1][1] != 'D'
    first = vs[0][0]
    last = vs[-1][0]
    nchg = len([1 for v in vs if v[0] > '1967-06-01'])
    arts.append([fn, n, first, last, nchg, alive])
BOOKS = [('I', 1, 396), ('II', 397, 1250), ('III', 1251, 1575), ('IV', 1576, 2023), ('V', 2024, 2334)]
c17 = []
for b, a0, a1 in BOOKS:
    inb = [r for r in arts if a0 <= r[1] <= a1]
    alive = [r for r in inb if r[5]]
    row = {'b': b, 'from': a0, 'to': a1, 'n': len(alive), 'gone': len(inb) - len(alive), 'orig': sum(1 for r in alive if r[4] == 0)}
    for dec in ('1970', '1980', '1990', '2000', '2010', '2020'):
        row['d' + dec] = sum(1 for r in alive if r[4] and r[3][:3] == dec[:3])
    row['most'] = sorted([[r[1], r[4]] for r in alive], key=lambda x: -x[1])[:3]
    c17.append(row)
D['c17'] = {'books': c17, 'n': sum(r['n'] for r in c17), 'orig': sum(r['orig'] for r in c17),
            'top': sorted([[r[1], r[4], r[3]] for r in arts if r[5]], key=lambda x: -x[1])[:12]}

# ------------------------------------------------------------------------------------------- the courts
# 18. constitutional review in the 1.ª série: the Conselho da Revolução's resolutions (1976-1982) and the Tribunal
# Constitucional's rulings with general binding force (1983-)
PRON = re.compile(r'(\bnão\s+(?:se\s+)?)?\bpronunci(?:a|ar)(?:-se)?\b[^;]{0,300}?\b(?:pela|por|no sentido da)\s+(?:inconstitucionalidade|ilegalidade)', re.I)
DECLX = re.compile(r'(\bnão\s+)?\bdeclar(?:a|ar)(?:-se)?\b[^;]{0,300}?\b(?:inconstitucionalidade|insconstitucionalidade|ilegalidade|inconstitucional|ilegal)', re.I)
OMIS = re.compile(r'\bomissão\b', re.I)


def outcome(s):
    pr = [m.group(1) is None for m in PRON.finditer(s)]
    if pr:
        return 'pre' if any(pr) else 'preno'
    de = [m.group(1) is None for m in DECLX.finditer(s)]
    if de:
        return 'yes' if any(de) else 'no'
    if OMIS.search(s):
        return 'omis'
    return 'other'
c18 = dd(C)
ex18 = []
for (name, pub), v in ALL:
    s = v[7] or ''
    y = int(pub[:4])
    if v[0] not in ('res', 'ac', 'other', 'rcm') or y < 1976:
        continue
    if not re.search(r'inconstitucional|constitucionalidade|ilegalidade', s, re.I):
        continue
    if v[0] == 'rcm':
        continue
    if y <= 1982 and v[0] == 'res':
        who = 'cr'
    elif v[0] == 'ac' and (name.startswith('Acórdão do Tribunal Constitucional') or (name.startswith('Acórdão n.º') and 1983 <= y <= 2008)):
        who = 'tc'
    else:
        continue
    k = outcome(s)
    c18[y][who + '_' + k] += 1
    ex18.append([pub, name, who, k, s[:170]])
bud18 = []
budlaw = {v[0]: y for y, v in bud.items()}      # 'Lei n.º 66-B/2012' -> 2013
for (name, pub), v in ALL:
    s = v[7] or ''
    if v[0] != 'ac' or int(pub[:4]) < 1983 or outcome(s) != 'yes':
        continue
    m = re.search(r'Orçamento (?:Geral )?do Estado para (\d{4})', s)
    ys = {int(m.group(1))} if m else set()
    for r_ in re.finditer(r'Lei n\.º \d+(?:-[A-Z])?/\d{2,4}', s):
        if r_.group(0) in budlaw:
            ys.add(budlaw[r_.group(0)])
    if ys:
        bud18.append([pub, name, sorted(ys)])
D['c18'] = {'rows': [dict(y=y, **c18[y]) for y in range(1976, Y1 + 1)], 'ex': ex18, 'budget': bud18}

# 19. the Tribunal Constitucional's rulings, by kind of proceedings
TCK = [('rec', r'^Recurso'), ('recl', r'^Reclama'), ('pre', r'^Preventiv'), ('suc', r'^Sucessiv'), ('ele', r'^Eleitoral|^Referendo|^Mandato'),
       ('par', r'^Partido|^Contas|^Financiamento|^Declara'), ('oth', r'')]
TCKR = [(k, re.compile(r)) for k, r in TCK]
c19 = dd(C)
kinds19 = C()
for line in open(os.path.join(B, 'tc-records.jsonl'), encoding='utf-8'):
    r = json.loads(line)
    y = (r.get('day') or '')[:4]
    if not y:
        continue
    if '/tc-decisoes-sumarias/' in r['p']:
        c19[int(y)]['sum'] += 1
        continue
    kd = r.get('kind') or ''
    kinds19[kd] += 1
    k = next(kk for kk, rx in TCKR if rx.search(kd))
    c19[int(y)][k] += 1
D['c19'] = {'rows': [dict(y=y, **c19[y]) for y in sorted(c19)], 'kinds': kinds19}

# 20. tax arbitration (CAAD): decisions by tax
TAX = [('csr', r'\bCSR\b|Contribuição (?:de |sobre o )?(?:Serviço|Se(?:c)?tor) Rodoviário'),
       ('irc', r'\bIRC\b|\bCIRC\b|Pessoas Cole(?:c)?tivas|\bDerrama|[Tt]ributaç(?:ão|ões) [Aa]utónoma|[Pp]rejuízos fiscais|\bRETGS\b|Regime Especial de Tributação dos Grupos|[Ee]stabelecimento estável|\bOIC\b|Organismos? de Investimento Cole(?:c)?tivo|\bSIFIDE|\bDLRR\b|\bRFAI\b|[Ll]ucro tribut'),
       ('irs', r'\bIRS\b|\bCIRS\b|Pessoas Singulares|[Rr]esidentes? [Nn]ão [Hh]abitua|\bRNH\b|[Mm]ais-valias?\b|[Cc]ategoria [A-H]\b|[Rr]endimentos? (?:do trabalho|prediais|de capitais|empresariais)'),
       ('iva', r'\bIVA\b|\bCIVA\b|Valor Acrescentado|\bRITI\b'),
       ('is', r'\bIS\b|Imposto (?:do|de) Selo|\bTGIS\b|\bCIS\b|Verba 28'),
       ('imi', r'\bA?IMI\b|\bCIMI\b|Imposto Municipal sobre Im[óo]veis|Adicional ao IMI|[Vv]alor [Pp]atrimonial [Tt]ribut|\bVPT\b'),
       ('imt', r'\bIMT\b|\bCIMT\b|Transmissões Onerosas'),
       ('veh', r'\bIUC\b|\bISV\b|Imposto Único de Circulação|Imposto sobre Veículos'),
       ('cont', r'\bCESE\b|Contribuição|\bISP\b|\bIABA\b|\bIEC\b|Impostos? Especia(?:l|is)|Produtos Petrolíferos|\bTaxas?\b|\bASSB\b|Sobretaxa')]
TAXR = [(k, re.compile(r)) for k, r in TAX]


def tax_of(s):
    best = None
    for k, rx in TAXR:
        m = rx.search(s)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), k)
    return best[1] if best else 'other'
c20 = dd(C)
for f in rows('caad.tsv'):
    if len(f) < 3 or not f[0]:
        continue
    s = f[2]
    c20[int(f[0][:4])][tax_of(s)] += 1
D['c20'] = {'rows': [dict(y=y, **c20[y]) for y in sorted(c20)]}

# ------------------------------------------------------------------------------------------- profile
counts = json.load(open(os.path.join(B, 'counts.json'), encoding='utf-8'))
cnt = lambda g: {k: sum(v.values()) for k, v in counts.get(g, {}).items()}
P['built'] = BUILT
P['head'] = os.environ.get('HEAD_SHA', '')
P['commits'] = counts.get('commits')
P['acts1'] = len(ALL)
P['acts1_from'] = ALL[0][1][1]
P['s2'] = sum(s2.values())
P['s2_kinds'] = C(k for (k, y) in s2.elements())
P['ar'] = cnt('ar')
P['dgsi'] = cnt('dgsi')
P['other'] = cnt('other')
P['joram'] = cnt('joram')
P['tc'] = sum(1 for _ in rows('tc.tsv'))
P['caad'] = sum(1 for _ in rows('caad.tsv'))
P['joram_acts'] = sum(1 for _ in rows('joram.tsv'))
P['codes'] = len(c16)
P['ini'] = len(ini)
P['q'] = sum(1 for v in q.values() if v[0] == 'pergunta')
json.dump({'charts': D, 'profile': P}, open(os.path.join(B, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), default=list)
print('data.json', os.path.getsize(os.path.join(B, 'data.json')))
