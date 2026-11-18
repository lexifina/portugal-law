# Tools

The scripts behind this Portugal-only run of global-law's vulnerability detectors. They run inside a copy of
[global-law/vulnerabilities/scripts](https://github.com/lexifina/global-law/tree/main/vulnerabilities/scripts) (Python 3.11+,
`pip install duckdb pyarrow`), with a bare clone of this repository at `sources/corpus/portugal-law.git`, a blobless bare
clone of global-law at `sources/global-law.git`, and a `pins.json` that names only portugal-law, its commit, its language
(`pt`) and its code (`PT`). `build_vulns.py`, `flags_chart.py`, `late_ext_select.py`, `late_ext_rebut.py` and `config.json`
sit three folders up, next to the copy of global-law (`gl/vulnerabilities/scripts/`).

| Script | What it does |
| --- | --- |
| `run.sh` | Indexes the history and texts, maps the history to the act folders since the move, adds this repository's history rows, and runs the detectors (`bash run.sh <shards>`; run here as `bash run.sh 16`, 6 processes at a time) |
| `map_moved.py` | This repository moved its acts from folders named by id (`codigo-civil/`, `lei-35-2014/`) to `<kind>/<year>/<number>/` on 10 November 2026; using `data/paths.json` at the pin, it rewrites the paths in the history table to each act's folder since the move, so an act's history is not split in two (here 2,057 folders, 388,373 paths) |
| `add_root.py` | Builds the history rows from this repository's own commits, so the history detectors read every change; changed here (below) |
| `run_triage.sh` | The model review: the 40 strongest flags per category, the 40 strongest lapsed time limits in law texts, and the empty periods |
| `late_ext_select.py` | Chooses the empty periods for global-law's review of that category: those whose old and new dates open the same sentence (here 10), and, below 40, the shortest of the rest (here all 15) |
| `late_ext_rebut.py` | Adds the second, arguing-against pass to the empty-period review, as `triage.py` does for the other categories |
| `build_vulns.py` | Builds `data/flags/*.csv`, `data/reviewed.csv` and `data/by_category.csv` from the findings and the model review; changed here (below) |
| `flags_chart.py` | Draws the chart at the top of the READMEs, in Portuguese and English, light and dark |
| `config.json` | The repository, the Portuguese category names, the folders and files that are not law (case law, parliamentary records, opinions, rectifications and declarations, notices, election maps, ANACOM's decisions, README files, `data/`, `tools/`), the split of the flags into one file per category, and the chart's labels |
| `patch_detectors.py` | Fixes blind spots found in runs on several country repositories in the copy of global-law's scripts (`python -X utf8 patch_detectors.py <scripts dir>`; a fix already in place is skipped) |
| `patch_pt_pt.py` | The fixes found by this run (below) |
| `patch_pt.py`, `patch_mo.py` | The Portuguese fixes made for Brazil and Macau (Brazilian dates and references, "até ao dia", "artigo 5.º", "artigos 7.º a 9.º"); they apply here as they are |
| `patch_detectors_vi.py`, `patch_es.py`, `patch_ca.py`, `patch_en.py`, `patch_de.py`, `patch_en_et.py`, `patch_co.py`, `patch_sv.py`, `patch_ru.py`, `patch_r18.py`, `patch_xk.py`, `patch_lu.py`, `patch_li.py`, `patch_mx.py`, `patch_mn.py`, `patch_mt.py`, `patch_np.py`, `patch_en_nr.py`, `patch_dv.py`, `patch_az.py`, `patch_ar.py`, `patch_en_nz.py`, `patch_nb.py`, `patch_mk.py`, `patch_pa.py`, `patch_py.py`, `patch_pe.py`, `patch_en_ph.py`, `patch_qa.py`, `patch_nl.py`, `patch_it.py`, `patch_pl.py`, `patch_ru_fz.py`, `patch_sl.py`, `patch_sk.py` | The same for other languages and countries (found by other runs); applied here before the run, they change little or nothing in Portuguese text, but `redo.py` runs them on every repository |
| `apply_patches.py` | Runs the patches above once each, in a fixed order (`patch_pt_pt.py` last), and records them in the scripts folder (`.kit_patches.json`) |
| `redo.py` | Runs the patches, then again only the scans and detectors the fixes change, the model review of lapsed time limits, references to deleted provisions and empty periods, and the build (`python -X utf8 redo.py <run folder> [--keep-reviews] [--full]`; `--keep-reviews` keeps every review already made and reviews only new strong flags; `--full` runs every step again through `run.sh`, sends every category to the model and keeps every review already made; `EMBED_FONTS` names the script that embeds the chart's fonts) |

The model review needs `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` and `LLM_AUTH` set for an OpenAI-compatible Responses API.
`run_triage.sh` was given the folders that are not law in `config.json` (the court decisions, `parlamento/`, the opinions,
rectifications, declarations, notices, election maps, `anacom/`, `data/`, `tools/`), the root files and the README files.

## Changes made for this repository

`add_root.py` (in this copy only): this repository marks each change with the type of the act that made it (`Kind:
Decreto-Lei`, `Lei`, `Portaria`, `Decreto Legislativo Regional`, `Declaração de Retificação`, 28 act types in all, and two
`Acórdão` entries for decisions of the Constitutional Court and the Supreme Court of Justice that the amendment timeline names),
and each act's current consolidated text with `Kind: consolidated`; these now count as law, with `original` (an act as
published) and commits with no `Kind` (a change the Diário da República makes without naming an act), which already did:
228,752 commits. Without this the history detectors saw only the acts as published and none of their amendments. Left out:
`correction` (7,854 earlier versions added after the current text, so their order in git is not their order in time),
`metadata` and `issue` (records without text), `decision`, `parliamentary-record`, `opinion`, `report`, `act` (records of
the Court of Auditors) and `documentation` (among them the 10 November move).

`patch_pt_pt.py` (markers that survive later edits; `apply_patches.py` runs it after all the others):

- Size. With 1,466,570 commits, 2,352,573 file changes and 11 GB of current Markdown, several steps held everything in
  memory at once and would not have fitted on the machine: `ingest/extract.py` and `ingest/trailers.py` read the whole
  `git log` output and kept every row (`STREAM_EXTRACT`, `STREAM_TRAILERS`: now read as it comes and written in batches);
  `ingest/headings.py` kept 1,500 characters of every blob version (`STREAM_HEADINGS`: batches); `detectors/dead_fine.py`,
  `detectors/placeholder_ref.py` and `detectors/dup_labels.py` read every current Markdown file with one `git cat-file`
  call (`STREAM_ACTS`, `STREAM_DUP`: now one act folder at a time through a new `textscan.act_texts()`, or file by file).
  The text and reference scans ran in 16 shards, 6 at a time and later 3 or 4, so that each process holds a sixteenth of
  the acts.
- A dying `git cat-file` was read as the end of the input: under memory pressure from other jobs on the same machine, one
  text-scan shard lost its `cat-file` process and recorded 2,335 time limits instead of about 6,800, without an error
  (`STREAM_CHECK`, `STREAM_CHECK_RC`: `textscan.stream()` now stops with an error when `cat-file` ends early, returns a short
  read or exits with an error). That shard was scanned again: 6,615.
- `map_moved.py`: only files directly in a moved folder were mapped, not files in its subfolders (`lei-35-2014/anexo/artigo-001.md`
  stayed apart from `lei/2014/35/anexo/artigo-001.md`); the nearest moved ancestor now decides (`MOVED_NESTED`), and each
  distinct path is mapped once (`MOVED_UNIQUE`).
- `ingest/refscan.py` (read by the reference, placeholder and dead-fine detectors): `artigo-0001.md` and `artigo-010-a.md`
  gave no article number, so the first article of a chapter, whose file opens with the chapter's headings, had none, and
  its own heading was read as a reference (`PT_ARTIGO_PATH`).
- `detectors/currency_scan.py` (code `PT`): the escudo in its own notation ("1.000$00", "50$00"; "$" counts only between
  digits), "Esc." before an amount, "contos" and "réis" were not read, only the word "escudos" (`PT_ESCUDO`); after the hand
  check, "Esc. 1:1000", the scale of a plan, is no longer read as escudos (`PT_ESC_SCALE`; 38 flags fewer).
- `detectors/notes_scan.py` (code `PT`): "não pode ser realizado/efetuada" (a rule: "cannot be done") and "(SIC)", the Sítios
  de Importância Comunitária of Natura 2000, were read as publisher notes; a note is now "(sic)" or "[sic]" in lower case or
  the past "não pôde ser efetuada/incorporada/realizada" (`PT_NOTES`). Publisher notes went from 13,983 to 10,548.

`build_vulns.py` (in this copy only): with `split_flags` in `config.json` it writes one `data/flags/<category>.csv` per
category instead of one `flags.csv` (which would be over 200 MB), and gzips a file over 50 MB (`SPLIT_FLAGS`); and the
commit of a retroactive date is chosen in a fixed order when an act made two commits on the same day (`ROOT_ORDER`: the
path shown for Decreto-Lei 10/2024 changed between two builds).

Checked on real text and left as they were: references in European Portuguese ("artigo 5.º, n.º 2", "alínea a) do n.º 1 do
artigo 3.º", "artigo 3.º-A", "artigos 7.º a 9.º", other acts named after the article), dates ("até 31 de dezembro de 2020",
"até ao dia 30 de junho de 2021", "prorrogado até 31 de março de 2022") and placeholders ("(Revogado.)", "(Revogada.)",
"[Revogado]", "(Revogado pelo Decreto-Lei n.º ...)") are read by `patch_pt.py` and `patch_mo.py` as they are.

Not changed, and stated in the README and EDGE-CASES: `dup_labels.py` reads the restarting "§ 1.º" of the articles of an act
held as one file (`texto.md`) as duplicate numbers; the history detectors take the in-force days the Diário da República
gives, including days before an act's publication and days it gives no source for.
