"""Portugal (portugal-law, 1.47M commits, 2.2M files, 11 GB of current Markdown), in a copy of global-law's
vulnerabilities/scripts (once, after the kit's patches; every change carries a marker that later edits keep):

Size (any large corpus):
- ingest/extract.py, ingest/trailers.py (STREAM_EXTRACT, STREAM_TRAILERS): git log's output was read whole and every row
  held in memory; now read as it comes and the tables written in batches;
- ingest/headings.py (STREAM_HEADINGS): 1,500 characters of every blob version held at once; now written in batches;
- detectors/dead_fine.py, detectors/placeholder_ref.py (STREAM_ACTS) and detectors/dup_labels.py (STREAM_DUP): one
  `git cat-file --batch` read every current Markdown file into memory at once (11 GB here, twice over as text); now
  the files are streamed, one act (folder) at a time where the detector compares files of the same act
  (textscan.act_texts);
- map_moved.py (MOVED_NESTED, MOVED_UNIQUE): only files directly in a moved folder were mapped, not files in its
  subfolders (lei-35-2014/anexo/artigo-001.md); each distinct path is now mapped once instead of a list of every row.

European Portuguese:
- ingest/refscan.py (PT_ARTIGO_PATH): files named artigo-0001.md, artigo-010-a.md gave no key, so a first article whose
  file opens with chapter headings (Código Civil, artigo-0001.md) had none, and its own heading was read as a reference;
- detectors/currency_scan.py (PT_ESCUDO, PT only): the escudo in its own notation ("1.000$00"), "Esc. 2.500", "20
  contos" and the real ("1.000 réis") were not read; "$" counts only between digits.

    python -X utf8 patch_pt_pt.py <scripts dir>      (apply_patches.py runs it last)
"""
import sys
from pathlib import Path


def patch(rel, pairs):
    p = Path(sys.argv[1]) / rel
    s = p.read_text(encoding="utf-8")
    for name, a, b, marker in pairs:
        if marker in s:
            print("in place:", name)
        elif a in s:
            s = s.replace(a, b, 1)
            print("patched:", name)
        else:
            raise SystemExit(f"not found: {name} in {rel}")
    p.write_text(s, encoding="utf-8", newline="\n")


READER = r'''
    def records():
        buf = b""
        while True:
            chunk = p.stdout.read(1 << 24)
            if not chunk:
                break
            buf += chunk
            cut = buf.rfind(b"\x1e")
            if cut > 0:
                for r in buf[:cut].split(b"\x1e"):
                    if r:
                        yield r.decode("utf-8", errors="replace")
                buf = buf[cut:]
        for r in buf.split(b"\x1e"):
            if r:
                yield r.decode("utf-8", errors="replace")
'''

patch("ingest/extract.py", [
    ("stream git log --raw", r'''    out = git("log", "--raw", "--no-abbrev", "-M", "-z", "--format=%x1e%H%x1f%P%x1f%aI%x1f%s",
              c["sha"], cwd=repo, binary=True).decode("utf-8", errors="replace")
    cols = {k: [] for k in ("commit", "author_date", "status", "old_blob", "new_blob", "old_path", "path")}
    for rec in out.split("\x1e")[1:]:
''', r'''    # STREAM_EXTRACT (portugal-law, 1.47M commits): read git log's output as it comes and write the table in batches,
    # instead of holding the whole log (several GB) and every row in memory at once
    import subprocess
    from common import FLAGS
    p = subprocess.Popen(["git", "-c", "core.quotepath=false", "log", "--raw", "--no-abbrev", "-M", "-z",
                          "--format=%x1e%H%x1f%P%x1f%aI%x1f%s", c["sha"]], cwd=repo, stdout=subprocess.PIPE,
                         creationflags=FLAGS, bufsize=1 << 20)
    (INDEX / "changes").mkdir(parents=True, exist_ok=True)
    schema = pa.schema([(k, pa.string()) for k in ("commit", "author_date", "status", "old_blob", "new_blob", "old_path", "path", "corpus")])
    writer = pq.ParquetWriter(INDEX / "changes" / f"{c['repo']}.parquet", schema, compression="zstd")
    total = 0
    cols = {k: [] for k in ("commit", "author_date", "status", "old_blob", "new_blob", "old_path", "path")}

    def flush():
        nonlocal cols, total
        n = len(cols["commit"])
        if n:
            writer.write_table(pa.table({**cols, "corpus": [c["path"]] * n}, schema=schema))
            total += n
        cols = {k: [] for k in cols}
''' + READER + r'''    for rec in records():
        if len(cols["commit"]) >= 500_000:
            flush()
''', "# STREAM_EXTRACT"),
    ("write in batches", r'''            cols["old_path"].append(old); cols["path"].append(new)
    t = pa.table(cols).append_column("corpus", pa.array([c["path"]] * len(cols["commit"]), pa.string()))
    (INDEX / "changes").mkdir(parents=True, exist_ok=True)
    pq.write_table(t, INDEX / "changes" / f"{c['repo']}.parquet", compression="zstd")
    return c["repo"], len(cols["commit"]), time.time() - t0''', r'''            cols["old_path"].append(old); cols["path"].append(new)
    flush()
    writer.close()
    if p.wait():  # STREAM_EXTRACT_END
        raise RuntimeError(f"git log failed in {repo}")
    return c["repo"], total, time.time() - t0''', "# STREAM_EXTRACT_END"),
])

patch("ingest/trailers.py", [
    ("stream git log bodies", r'''    out = git("log", "--format=%x1e%H%x1f%aI%x1f%cI%x1f%B", c["sha"], cwd=CORPUS / f"{c['repo']}.git")
    rows = {k: [] for k in ("commit", "author_date", "commit_date", "subject", "trailers")}
    for rec in out.split("\x1e")[1:]:
''', r'''    # STREAM_TRAILERS (portugal-law, 1.47M commits): read the log as it comes and write the table in batches
    import subprocess
    from common import FLAGS
    p = subprocess.Popen(["git", "-c", "core.quotepath=false", "log", "--format=%x1e%H%x1f%aI%x1f%cI%x1f%B", c["sha"]],
                         cwd=CORPUS / f"{c['repo']}.git", stdout=subprocess.PIPE, creationflags=FLAGS, bufsize=1 << 20)
''' + READER + r'''    (INDEX / "commits").mkdir(parents=True, exist_ok=True)
    schema = pa.schema([(k, pa.string()) for k in ("commit", "author_date", "commit_date", "subject", "trailers", "corpus")])
    writer = pq.ParquetWriter(INDEX / "commits" / f"{c['repo']}.parquet", schema, compression="zstd")
    total = 0

    def flush(rows):
        nonlocal total
        n = len(rows["commit"])
        if n:
            writer.write_table(pa.table({**rows, "corpus": [c["path"]] * n}, schema=schema))
            total += n
        return {k: [] for k in rows}
    rows = {k: [] for k in ("commit", "author_date", "commit_date", "subject", "trailers")}
    for rec in records():
        if len(rows["commit"]) >= 200_000:
            rows = flush(rows)
''', "# STREAM_TRAILERS"),
    ("write in batches", r'''    t = pa.table(rows).append_column("corpus", pa.array([c["path"]] * len(rows["commit"]), pa.string()))
    (INDEX / "commits").mkdir(parents=True, exist_ok=True)
    pq.write_table(t, INDEX / "commits" / f"{c['repo']}.parquet", compression="zstd")
    return c["repo"], len(rows["commit"])''', r'''    flush(rows)
    writer.close()
    if p.wait():  # STREAM_TRAILERS_END
        raise RuntimeError("git log failed")
    return c["repo"], total''', "# STREAM_TRAILERS_END"),
])

patch("ingest/headings.py", [
    ("batches", r'''    H = {"blob": [], "heading": [], "head": []}
    for sha, text in stream(repo, blobs):
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        H["blob"].append(sha)
        H["heading"].append(lines[0].lstrip("#").strip()[:300] if lines else "")
        H["head"].append(text[:1500])
    (INDEX / "headings").mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table(H), INDEX / "headings" / f"{c['repo']}.parquet", compression="zstd")''',
     r'''    # STREAM_HEADINGS (portugal-law): written in batches; 1,500 characters of every blob ever do not fit in memory
    (INDEX / "headings").mkdir(parents=True, exist_ok=True)
    schema = pa.schema([("blob", pa.string()), ("heading", pa.string()), ("head", pa.string())])
    w = pq.ParquetWriter(INDEX / "headings" / f"{c['repo']}.parquet", schema, compression="zstd")
    H = {"blob": [], "heading": [], "head": []}
    for sha, text in stream(repo, blobs):
        lines = [l.strip() for l in text[:20000].splitlines() if l.strip()]
        H["blob"].append(sha)
        H["heading"].append(lines[0].lstrip("#").strip()[:300] if lines else "")
        H["head"].append(text[:1500])
        if len(H["blob"]) >= 100_000:
            w.write_table(pa.table(H, schema=schema)); H = {k: [] for k in H}
    w.write_table(pa.table(H, schema=schema)); w.close()''', "# STREAM_HEADINGS"),
])

patch("map_moved.py", [
    ("nested folders, distinct paths", r'''def m(p):
    if not p:
        return p
    head, _, name = p.rpartition("/")
    return f"{moved[head]}/{name}" if head in moved else p


n = 0
cols = {}
for c in ("path", "old_path"):
    vals = t.column(c).to_pylist()
    new = [m(v) for v in vals]
    n += sum(a != b for a, b in zip(vals, new))
    cols[c] = pa.array(new, pa.string())''', r'''def m(p):
    if not p:
        return p
    # MOVED_NESTED (portugal-law): a file in a subfolder of a moved act (lei-35-2014/anexo/artigo-001.md) moves with it;
    # the nearest moved ancestor folder decides
    head = p
    while "/" in head:
        head = head.rpartition("/")[0]
        if head in moved:
            return moved[head] + p[len(head):]
    return p


import pyarrow.compute as pc
n = 0
cols = {}
for c in ("path", "old_path"):
    # MOVED_UNIQUE (portugal-law): map each distinct path once, not a Python list of every row (millions)
    col = t.column(c).combine_chunks()
    uniq = pc.unique(col)
    mapped = pa.array([m(v) for v in uniq.to_pylist()], pa.string())
    new = pc.take(mapped, pc.index_in(col, value_set=uniq))
    n += pc.sum(pc.cast(pc.not_equal(col, new), pa.int64())).as_py() or 0
    cols[c] = new''', "# MOVED_NESTED"),
])

patch("ingest/textscan.py", [
    ("act_texts", r'''

def is_law_file(path: str) -> bool:''', r'''

def act_texts(repo: Path, sha: str, keep=lambda p: p.endswith(".md")):
    """(act folder, {path: text}) for every act at a commit, one act at a time (STREAM_ACTS: the detectors that compare
    files of the same act read all current files into memory at once, 11 GB for portugal-law)."""
    ls = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", sha],
                        capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", "replace").split("\0")
    items = []
    for x in ls:
        if x and " " in x:
            o, path = x.split(" ", 1)
            if keep(path):
                items.append((path.rsplit("/", 1)[0] if "/" in path else "", path, o))
    del ls
    items.sort()
    cur, files = None, {}
    for (_, text), (a, path, _o) in zip(stream(repo, [o for _, _, o in items]), items):
        if a != cur and files:
            yield cur, files
            files = {}
        cur = a
        files[path] = text
    if files:
        yield cur, files


def is_law_file(path: str) -> bool:''', "STREAM_ACTS: the detectors"),
])

patch("ingest/textscan.py", [
    ("cat-file must not die silently", r'''        head = p.stdout.readline().split()
        if len(head) < 3 or head[1] != b"blob":
            yield sh, ""''', r'''        head = p.stdout.readline().split()
        if not head:  # STREAM_CHECK: cat-file ended early (killed, out of memory): stop, do not read every later blob as empty
            raise RuntimeError(f"git cat-file ended early in {repo} at {sh}")
        if len(head) < 3 or head[1] != b"blob":
            yield sh, ""''', "# STREAM_CHECK"),
    ("cat-file exit code", r'''        yield sh, data.decode("utf-8", errors="replace")
    p.wait()
''', r'''        if len(data) < int(head[2]):  # STREAM_CHECK_RC: a short read is a dead cat-file too
            raise RuntimeError(f"git cat-file ended early in {repo} at {sh}")
        yield sh, data.decode("utf-8", errors="replace")
    if p.wait():
        raise RuntimeError(f"git cat-file failed in {repo} (exit {p.returncode})")
''', "# STREAM_CHECK_RC"),
])

patch("detectors/notes_scan.py", [
    ("pt: ordinary wording and SIC", r'''        out.append({"corpus": c["path"], "repo": c["repo"], "path": path, "line": int(ln), "text": text[:600]})
    return out
''', r'''        out.append({"corpus": c["path"], "repo": c["repo"], "path": path, "line": int(ln), "text": text[:600]})
    if (c.get("language") or "").lower() == "pt" and (c.get("code") or "").upper() == "PT":  # PT_NOTES
        # European Portuguese law text says "não pode ser realizado/efetuada" as a rule (a form "cannot be filled in
        # for more than 30 days"), and "(SIC)" is the Sítios de Importância Comunitária of Natura 2000: a note is
        # "(sic)"/"[sic]" in lower case or the past "não pôde ser efetuada/incorporada/realizada"
        import re as _re
        _note = _re.compile(r"\[sic\]|\(sic\)|não pôde ser (?:efetuad|incorporad|realizad)")
        out = [o for o in out if _note.search(o["text"])]
    return out
''', "# PT_NOTES"),
])

patch("detectors/dead_fine.py", [
    ("one act at a time", r'''    lower_priority()
    text = _corpus_texts(c, only_acts)
    deleted = _deleted_keys(c)
    acts: dict[str, dict[str, str]] = {}
    for p, t in text.items():
        acts.setdefault(act_of(p), {})[p] = t
    out = []
    for a, files in acts.items():''', r'''    lower_priority()
    from textscan import act_texts  # STREAM_ACTS: one act at a time, not every current file at once
    deleted = _deleted_keys(c)
    out = []
    for a, files in act_texts(CORPUS / f"{c['repo']}.git", c["sha"],
                              lambda p: p.endswith(".md") and (not only_acts or act_of(p) in only_acts)):''',
     "# STREAM_ACTS: one act at a time"),
])

patch("detectors/placeholder_ref.py", [
    ("one act at a time", r'''    ls = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "-z", "--format=%(objectname) %(path)", c["sha"]],
                        capture_output=True, creationflags=FLAGS).stdout.decode("utf-8", "replace").split("\0")
    files = {}
    for x in ls:
        if x and x.endswith(".md"):
            sha, path = x.split(" ", 1)
            if path_key(path) or True:
                files[path] = sha
    if not files:
        return []
    p = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], input=("\n".join(files.values()) + "\n").encode(),
                       capture_output=True, creationflags=FLAGS).stdout
    text, pos = {}, 0
    for path in files:
        nl = p.index(b"\n", pos); size = int(p[pos:nl].split()[2]); text[path] = p[nl + 1: nl + 1 + size].decode("utf-8", "replace"); pos = nl + 2 + size
''', r'''    from textscan import act_texts  # STREAM_ACTS: holders and references are per act, so one act at a time
    res = []
    for _a, text in act_texts(repo, c["sha"]):
        res += _one_act(c, text)
    return res


def _one_act(c, text):
''', "# STREAM_ACTS: holders"),
])

patch("detectors/dup_labels.py", [
    ("stream", r'''    p = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], input=("\n".join(s for s, _ in items) + "\n").encode(),
                       capture_output=True, creationflags=FLAGS).stdout
    out, pos = [], 0
    for sha, path in items:
        nl = p.index(b"\n", pos); size = int(p[pos:nl].split()[2]); body = p[nl + 1: nl + 1 + size].decode("utf-8", "replace"); pos = nl + 2 + size
''', r'''    from textscan import stream  # STREAM_DUP: file by file, not every current file in memory at once
    out = []
    for (sha, body), (_, path) in zip(stream(repo, [s for s, _ in items]), items):
''', "# STREAM_DUP"),
])

patch("ingest/refscan.py", [
    ("artigo-0001.md", r'''    m = re.match(r"(?i)^(?:(?:ugovor|naredba)[-_])?''', r'''    if _LANG["v"] == "pt":  # PT_ARTIGO_PATH: portugal-law's artigo-0001.md, artigo-010-a.md (article 10.º-A)
        r = re.match(r"^artigo-0*(\d{1,4})(?:-([a-z]{1,2}))?$", base)
        if r:
            return key(r.group(1), r.group(2))
    m = re.match(r"(?i)^(?:(?:ugovor|naredba)[-_])?''', "# PT_ARTIGO_PATH"),
])

patch("detectors/currency_scan.py", [
    ("escudo notation", r'''EXTRA_CURRENCY_CODE = {''', r'''EXTRA_CURRENCY_CODE = {"PT": r"|(?<=[0-9])\$(?=[0-9]{2}(?![0-9]))|(?-i:contos?)\b|(?-i:Esc\.)(?=\s?[0-9])|(?-i:réis)\b(?#PT_ESCUDO)", ''',
     "(?#PT_ESCUDO)"),
    # PT_ESC_SCALE: "Esc. 1:1000" on a plan is a scale (escala), not escudos
    ("Esc. 1:1000 is a scale", r'''(?-i:Esc\.)(?=\s?[0-9])|''', r'''(?-i:Esc\.)(?=\s?[0-9])(?!\s?[0-9]+\s?[:/])(?#PT_ESC_SCALE)|''',
     "(?#PT_ESC_SCALE)"),
])
