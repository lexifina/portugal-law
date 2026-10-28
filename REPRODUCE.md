# How this history was made, and how to make it again

This file records exactly how the repository was built: the source, the commands, the software, the decisions made
by hand, and what an AI model did and did not do. The build writes it, so it describes the build that made this
commit.

## Short version

```sh
git clone https://github.com/lexifina/portugal-law && cd portugal-law
python -X utf8 tools/build.py --repo ../rebuilt --today 2026-10-28
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
| `LegCons_Detalhe/DataActionGetDiplomaFragByIdAndApplicationSetting` | the act's record: its id, title, kind, issuer, day of publication | 3 |
| `AlteracoesTimelineByDiplomaLegisId/DataActionGetConsolidacaoByDiplomaFrag` | the amendment timeline: every amending act, with each provision it added (Adita), changed (Altera), repealed (Revoga), eliminated (Elimina), suspended (Suspende) or corrected (Retifica), the version it made and the day that version took effect | 3 |
| `LegCons_Detalhe/DataActionGetData` | the whole consolidated text in force on a chosen day, provision by provision, each with its version id, its state (in force, repealed, suspended) and the day that version took effect | 107 |

| Act | Short name | Folder | In force from | Texts by day read | Commits | Files today |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Decreto de Aprovação da Constituição | Constituição | `constituicao/` | 1976-04-25 | 9 | 10 | 298 |
| Lei n.º 7/2009 | Código do Trabalho | `codigo-do-trabalho/` | 2009-02-17 | 25 | 29 | 615 |
| Decreto-Lei n.º 47344 | Código Civil | `codigo-civil/` | 1967-06-01 | 73 | 109 | 2364 |

The data was retrieved on 2026-10-28, at most four requests at a time and a request started
at most every 0.25 seconds, with the user agent `lexifina-watch/1.0 (+https://lexifina.com/watch; corpus@lexifina.com)`
and the site's own anonymous CSRF header (which its script sends for every visitor who is not logged in; the build
checks it against the site's script). No login, no challenge and no rate limit were met. The site's robots.txt
address redirects to its error page, so it states no rules; its legal notice ("Avisos Legais") is quoted in LICENSE.

## The build, step by step

1. `python -X utf8 scripts/portugal-law/build.py --today 2026-10-28` in Lexifina's own repository fetched the data into
   its cache and wrote this repository. `tools/build.py`, `tools/model.py` and `tools/source.py` here are the same
   files as in `scripts/portugal-law/` there (git blobs `78defb996f7e30b0d8f6e23eb2f738df16a8791e`, `af5ec733d27c4691b05c90f90f33712a26ef5d53`,
   `3a47b95b9ca4c266fb2475fb776a088687d2f614`), with `tools/reproduce.py`, which writes this file, `tools/check_repo.py` and
   `tools/test_repo.py`. Every later build ran with `--offline`, from the cache.
2. `python -X utf8 scripts/portugal-law/check_repo.py` read each act back from this repository with
   `tools/em_vigor.py` on every day a version took effect and compared it file by file with the text worked out
   afresh from the cached responses; then it compared the whole act, word for word, with the words of the DR's own
   text for that day, read from the raw responses without the build's renderer. Result: `111 days checked (196180 files), 0 mismatches; 111 days word for word (16587703 words) against the DR's own text, 0 mismatches`.
3. `python -X utf8 scripts/portugal-law/test_repo.py --record` ran the functional smoke test (6 of 6 passed):
   - pass: blame names an act: constituicao/artigo-007.md lines by Decreto de Aprovação da Constituição, Lei Constitucional n.º 1/2001, Lei Constitucional n.º 1/2004, Lei Constitucional n.º 1/89, Lei Constitucional n.º 1/92, Lei Constitucional n.º 1/97
   - pass: text before and after an amendment: constituicao/artigo-007.md 2004-07-28 != 2004-07-29; codigo-do-trabalho/artigo-003.md 2023-04-30 != 2023-05-01
   - pass: log --follow in date order: constituicao/artigo-007.md 7 commits; codigo-do-trabalho/artigo-003.md 4 commits; codigo-do-trabalho/artigo-127.md 8 commits
   - pass: tags resolve, In-force on every law commit: 249 tags resolve; 148 law commits carry In-force
   - pass: only the documentation commit is by Lexifina: only the documentation commit 77d300aa26 is by Lexifina; 130 distinct authors
   - pass: README commands run: 13 README commands ran and printed output
4. `python -X utf8 scripts/portugal-law/build.py --offline --verify-rebuild` built the repository a second time from
   the same cache into a temporary folder and compared the hashes. A second build from the same cache into an empty folder gave the same history: the last law commit was `97858156bd9764091a84f59ae25a10666e2f9be7` in both, and every one of the 148 law commits and 249 tags had the same hash.
5. The build was run once more to write these results into this file, and the final `main` was rebuilt again in a
   temporary folder and compared hash for hash before it was pushed.
6. `git push -f origin main --tags` published it to the private GitHub repository `lexifina/portugal-law`, replacing
   its placeholder commit.

It ran with Python 3.12.10 and git version 2.46.0.windows.1 on Windows 11. `scripts/test_corpus.py` (Lexifina's shared corpus smoke test) was run on
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
  version's own day; 434 provision-days where the DR's text for the day shows another version are listed below
  and in `data/versoes.json`, and the check applies the same rule. A version the DR gives no day (the empty date
  1900-01-01) is dated by the first consolidated text that shows it, or, when it is a correction (Retifica) the DR
  shows only later, by the day the declaration of rectification was published.
- **Cause.** The amendment timeline names, for each amending act, the provision versions it made. Tried in order:
  1. the timeline names one act for the new version (for a provision that disappears: for its repeal or
     elimination): that act (1984 file changes);
  2. the DR names no act for it, the version is dated that day, and only one act has changes in force that day: that
     act, labelled "date only" (79);
  3. a heading that moved to another file with a provision an act changed: that act (38);
  4. two acts named, or two acts that day: neither; committed by the publisher naming both in `Candidate:` trailers
     (19);
  5. otherwise: no act; committed by the publisher and labelled (122).
  New versions with the same words (the DR renews version ids at each revision) change no file and make no commit.
- **Commits.** One commit per act of the record, per day and per amending act (136 law commits), one for the text
  of each act as it first took effect (3), 1 for changes with two candidate acts and 8 for
  changes the DR names no act for, in the order they took effect (acts of one day in order of publication), then one
  for this documentation.
  - The author is the amending act, `Lei n.º 93/2019`, at an address ending `@diariodarepublica.invalid`
    (`lei-93-2019@diariodarepublica.invalid`, from the DR's own address for the act). Declarations of rectification
    and judgments of the Constitutional Court that the DR lists in the timeline are authors in the same way. The first
    text of each act is credited to the act itself.
  - Author and committer dates are noon in Lisbon on the day the change took effect, with the offsets of
    Europe/Lisbon written into the code (this machine has no time-zone database). The committer is
    `Lexifina <portugal-law@lexifina.com>`. 1 commits are before 1970.
  - The message has the act's title and summary (sumário), the provisions it added, changed or removed (Aditado,
    Alterado, Revogado ou eliminado) and the trailers `Evidence:`, `Kind:`, `Published:`, `In-force:`, `Affecting:`,
    `Source:` (the act on the DR) and `Consolidated-text:` (the consolidated act on the DR). `Date-note:` marks an
    in-force day before the act's publication, as the DR gives it.
  - Tags: each act's days (`constituicao/2005-08-17`) and each amending act (`atos/lei-constitucional-1-2005`; an act
    that took effect on several days has one tag per day, `atos/lei-13-2023/2023-05-01`); 249 in all.
- **Documentation commit.** Dated 2026-10-28, the day the data was retrieved, not the day of the run, so a later rebuild
  of the same data gives the same hash.

Changes credited by date only:

- codigo-civil 1976-03-16: Artigo 1491.º
- codigo-civil 1976-03-16: Artigo 1492.º
- codigo-civil 1976-03-16: Artigo 1493.º
- codigo-civil 1976-03-16: Artigo 1494.º
- codigo-civil 1976-03-16: Artigo 1495.º
- codigo-civil 1976-03-16: Artigo 1496.º
- codigo-civil 1976-03-16: Artigo 1497.º
- codigo-civil 1976-03-16: Artigo 1498.º
- codigo-civil 1976-03-16: Artigo 1499.º
- codigo-civil 1976-03-16: Artigo 1500.º
- codigo-civil 1976-03-16: Artigo 1501.º
- codigo-civil 1976-03-16: Artigo 1502.º
- codigo-civil 1976-03-16: Artigo 1503.º
- codigo-civil 1976-03-16: Artigo 1504.º
- codigo-civil 1976-03-16: Artigo 1505.º
- codigo-civil 1976-03-16: Artigo 1506.º
- codigo-civil 1976-03-16: Artigo 1507.º
- codigo-civil 1976-03-16: Artigo 1508.º
- codigo-civil 1976-03-16: Artigo 1509.º
- codigo-civil 1976-03-16: Artigo 1510.º
- codigo-civil 1976-03-16: Artigo 1511.º
- codigo-civil 1976-03-16: Artigo 1512.º
- codigo-civil 1976-03-16: Artigo 1513.º
- codigo-civil 1976-03-16: Artigo 1514.º
- codigo-civil 1976-03-16: Artigo 1515.º
- codigo-civil 1976-03-16: Artigo 1516.º
- codigo-civil 1976-03-16: Artigo 1517.º
- codigo-civil 1976-03-16: Artigo 1518.º
- codigo-civil 1976-03-16: Artigo 1519.º
- codigo-civil 1976-03-16: Artigo 1520.º
- codigo-civil 1976-03-16: Artigo 1521.º
- codigo-civil 1976-03-16: Artigo 1522.º
- codigo-civil 1976-03-16: Artigo 1523.º
- codigo-civil 1978-04-01: Artigo 1767.º
- codigo-civil 1978-04-01: Artigo 1773.º
- codigo-civil 1978-04-01: Artigo 1778.º
- codigo-civil 1978-04-01: Artigo 1786.º
- codigo-civil 1978-04-01: Artigo 1815.º
- codigo-civil 1978-04-01: Artigo 1824.º
- codigo-civil 1978-04-01: Artigo 1827.º
- codigo-civil 1978-04-01: Artigo 1841.º
- codigo-civil 1978-04-01: Artigo 1846.º
- codigo-civil 1978-04-01: Artigo 1852.º
- codigo-civil 1978-04-01: Artigo 1857.º
- codigo-civil 1978-04-01: Artigo 1859.º
- codigo-civil 1978-04-01: Artigo 1867.º
- codigo-civil 1978-04-01: Artigo 1873.º
- codigo-civil 1978-04-01: Artigo 1876.º
- codigo-civil 1978-04-01: Artigo 1879.º
- codigo-civil 1978-04-01: Artigo 1900.º
- codigo-civil 1978-04-01: Artigo 1904.º
- codigo-civil 1978-04-01: Artigo 1910.º
- codigo-civil 1978-04-01: Artigo 1919.º
- codigo-civil 1978-04-01: Artigo 1987.º
- codigo-civil 1978-04-01: Artigo 1999.º
- codigo-civil 1978-04-01: Artigo 2015.º
- codigo-civil 1978-04-01: Artigo 2020.º
- codigo-civil 1978-04-01: Artigo 2149.º
- codigo-civil 1978-04-01: Artigo 2317.º
- constituicao 1989-08-07: Artigo 89.º
- constituicao 1989-08-07: Artigo 109.º
- constituicao 1989-08-07: Artigo 277.º
- constituicao 1989-08-07: Artigo 284.º
- constituicao 1989-08-07: Artigo 299.º
- constituicao 1989-08-07: Artigo 300.º
- codigo-civil 1995-01-01: Artigo 1422.º
- codigo-civil 1995-01-01: Artigo 1429.º
- codigo-civil 1995-01-01: Artigo 1429.º-A
- constituicao 2004-07-29: Artigo 296.º
- constituicao 2004-07-29: Artigo 297.º
- constituicao 2004-07-29: Artigo 298.º
- constituicao 2004-07-29: Artigo 299.º
- constituicao 2005-08-17: Artigo 24.º
- codigo-civil 2012-09-13: Artigo 1425.º
- codigo-civil 2012-09-13: Artigo 1426.º
- codigo-civil 2015-10-01: Artigo 1905.º
- codigo-civil 2018-09-01: Artigo 152.º
- codigo-civil 2022-04-10: Artigo 1424.º
- codigo-civil 2022-04-10: Artigo 1427.º

Headings that moved with a provision:

- codigo-civil 1975-02-19: Artigo 1069.º
- codigo-civil 1975-02-19: Artigo 1071.º
- codigo-civil 1975-02-19: Artigo 1079.º
- codigo-civil 1975-02-19: Artigo 1083.º
- codigo-civil 1975-02-19: Artigo 1088.º
- codigo-civil 1975-02-19: Artigo 1091.º
- codigo-civil 1975-02-19: Artigo 1092.º
- codigo-civil 1975-02-19: Artigo 1095.º
- codigo-civil 1975-02-19: Artigo 1101.º
- codigo-civil 1975-02-19: Artigo 1104.º
- codigo-civil 1975-02-19: Artigo 1107.º
- codigo-civil 1975-02-19: Artigo 1108.º
- codigo-civil 1975-02-19: Artigo 1112.º
- codigo-civil 1975-02-19: Artigo 1114.º
- codigo-civil 1975-02-19: Artigo 1789.º
- codigo-civil 1975-02-19: Artigo 1792.º
- codigo-civil 1975-02-19: Artigo 1794.º
- codigo-civil 1975-02-19: Artigo 1801.º
- codigo-civil 1975-02-19: Artigo 1807.º
- codigo-civil 1975-02-19: Artigo 1874.º
- codigo-civil 1975-02-19: Artigo 1877.º
- codigo-civil 1975-02-19: Artigo 1992.º
- codigo-civil 1975-02-19: Artigo 2141.º
- codigo-civil 1975-02-19: Artigo 2142.º
- codigo-civil 1975-02-19: Artigo 2143.º
- codigo-civil 1975-02-19: Artigo 2145.º
- codigo-civil 1975-02-19: Artigo 2146.º
- codigo-civil 1975-02-19: Artigo 2147.º
- constituicao 1982-10-30: Artigo 111.º
- constituicao 1982-10-30: Artigo 161.º
- constituicao 1982-10-30: Artigo 187.º
- constituicao 1982-10-30: Artigo 197.º
- constituicao 1982-10-30: Artigo 209.º
- constituicao 1982-10-30: Artigo 219.º
- constituicao 1982-10-30: Artigo 224.º
- constituicao 1982-10-30: Artigo 245.º
- constituicao 1982-10-30: Artigo 255.º
- codigo-civil 2025-04-02: Artigo 1650.º

Changes the DR names no act for (publisher commits):

- codigo-civil 1975-02-19: Artigo 152.º, Artigo 1069.º, Artigo 1071.º, Artigo 1079.º, Artigo 1083.º, Artigo 1088.º, Artigo 1091.º, Artigo 1092.º, Artigo 1093.º, Artigo 1095.º, Artigo 1101.º, Artigo 1104.º, Artigo 1107.º, Artigo 1108.º, Artigo 1112.º, Artigo 1114.º, Artigo 1119.º, Artigo 1767.º, Artigo 1771.º, Artigo 1772.º, Artigo 1773.º, Artigo 1778.º, Artigo 1786.º, Artigo 1789.º, Artigo 1792.º, Artigo 1794.º, Artigo 1801.º, Artigo 1807.º, Artigo 1815.º, Artigo 1824.º, Artigo 1827.º, Artigo 1841.º, Artigo 1846.º, Artigo 1852.º, Artigo 1857.º, Artigo 1859.º, Artigo 1867.º, Artigo 1873.º, Artigo 1874.º, Artigo 1876.º, Artigo 1877.º, Artigo 1879.º, Artigo 1900.º, Artigo 1904.º, Artigo 1910.º, Artigo 1919.º, Artigo 1987.º, Artigo 1992.º, Artigo 1999.º, Artigo 2015.º, Artigo 2020.º, Artigo 2141.º, Artigo 2142.º, Artigo 2143.º, Artigo 2145.º, Artigo 2146.º, Artigo 2147.º, Artigo 2149.º, Artigo 2317.º, Assinatura, Assinatura
- codigo-civil 1977-07-21: Artigo 1491.º, Artigo 1492.º, Artigo 1493.º, Artigo 1494.º, Artigo 1495.º, Artigo 1496.º, Artigo 1497.º, Artigo 1498.º, Artigo 1499.º, Artigo 1500.º, Artigo 1501.º, Artigo 1502.º, Artigo 1503.º, Artigo 1504.º, Artigo 1505.º, Artigo 1506.º, Artigo 1507.º, Artigo 1508.º, Artigo 1509.º, Artigo 1510.º, Artigo 1511.º, Artigo 1512.º, Artigo 1513.º, Artigo 1514.º, Artigo 1515.º, Artigo 1516.º, Artigo 1517.º, Artigo 1518.º, Artigo 1519.º, Artigo 1520.º, Artigo 1521.º, Artigo 1522.º, Artigo 1523.º
- constituicao 1982-10-30: Artigo 1.º, Artigo 89.º, Artigo 277.º, Artigo 292.º, Assinatura
- codigo-civil 1993-08-22: Artigo 1083.º, Artigo 1084.º, Artigo 1085.º, Artigo 1086.º, Artigo 1087.º, Artigo 1088.º, Artigo 1089.º, Artigo 1090.º, Artigo 1091.º, Artigo 1092.º, Artigo 1093.º, Artigo 1094.º, Artigo 1095.º, Artigo 1096.º, Artigo 1097.º, Artigo 1098.º, Artigo 1099.º, Artigo 1100.º, Artigo 1101.º, Artigo 1102.º, Artigo 1103.º, Artigo 1104.º, Artigo 1105.º, Artigo 1106.º, Artigo 1107.º, Artigo 1108.º, Artigo 1109.º, Artigo 1110.º, Artigo 1111.º, Artigo 1112.º, Artigo 1113.º, Artigo 1114.º, Artigo 1115.º, Artigo 1116.º, Artigo 1117.º, Artigo 1118.º, Artigo 1119.º, Artigo 1120.º
- codigo-civil 2006-06-27: Artigo 1114.º, Artigo 1115.º, Artigo 1116.º, Artigo 1117.º, Artigo 1118.º, Artigo 1119.º, Artigo 1120.º
- codigo-civil 2008-11-30: Artigo 1777.º, Artigo 2021.º, Artigo 2022.º, Artigo 2023.º
- codigo-do-trabalho 2009-09-15: Assinatura
- codigo-civil 2024-08-24: Artigo 1424.º-A

Provision-days where the record follows the version's own day, not the DR's text for that day:

- constituicao 1982-10-30: Artigo 268.º (shown with in-force day 1983-10-01; the record keeps the version in force from 1976-04-25)
- codigo-do-trabalho 2009-02-17: Artigo 12.º (shown without a day; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2017-10-02: Artigo 563.º (shown with in-force day 2017-10-01; the record keeps the version in force from 2017-10-02)
- codigo-do-trabalho 2019-09-09: Artigo 3.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 44.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 46.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 63.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2019-09-09: Artigo 85.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 86.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 87.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 112.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 114.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 127.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2017-10-01)
- codigo-do-trabalho 2019-09-09: Artigo 131.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 139.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 140.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 142.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2019-09-09: Artigo 143.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 144.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2015-09-06)
- codigo-do-trabalho 2019-09-09: Artigo 148.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 149.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 159.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 160.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 173.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 177.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2013-10-01)
- codigo-do-trabalho 2019-09-09: Artigo 181.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 182.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 185.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 208.º-A (shown with in-force day 2019-10-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2019-09-09: Artigo 208.º-B (shown with in-force day 2019-10-01; the record keeps the version in force from 2015-09-06)
- codigo-do-trabalho 2019-09-09: Artigo 249.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 255.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 268.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2019-09-09: Artigo 331.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2017-10-01)
- codigo-do-trabalho 2019-09-09: Artigo 344.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2013-10-01)
- codigo-do-trabalho 2019-09-09: Artigo 370.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2019-09-09: Artigo 394.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2018-03-20)
- codigo-do-trabalho 2019-09-09: Artigo 447.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 456.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 497.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 500.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 501.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2014-09-01)
- codigo-do-trabalho 2019-09-09: Artigo 501.º-A (shown with in-force day 2019-10-01; not yet in force, left out)
- codigo-do-trabalho 2019-09-09: Artigo 502.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2014-09-01)
- codigo-do-trabalho 2019-09-09: Artigo 512.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 513.º (shown with in-force day 2019-10-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-09-09: Artigo 515.º-A (shown with in-force day 2019-10-01; not yet in force, left out)
- codigo-do-trabalho 2019-10-01: Artigo 44.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-10-01: Artigo 46.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-10-01: Artigo 114.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-10-01: Artigo 144.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2015-09-06)
- codigo-do-trabalho 2019-10-01: Artigo 249.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2019-10-01: Artigo 255.º (shown with in-force day 2019-10-04; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 3.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2022-01-01)
- codigo-do-trabalho 2023-04-04: Artigo 5.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 10.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 12.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 24.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2015-05-01)
- codigo-do-trabalho 2023-04-04: Artigo 25.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 35.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 40.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 41.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 42.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 43.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 44.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-04)
- codigo-do-trabalho 2023-04-04: Artigo 45.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 51.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 63.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 64.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 65.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Subsecção X (shown with in-force day 2023-05-01; not yet in force, left out)
- codigo-do-trabalho 2023-04-04: Artigo 106.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2013-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 107.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 108.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 109.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 111.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 112.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 114.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-04)
- codigo-do-trabalho 2023-04-04: Artigo 127.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 129.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 141.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 142.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 143.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 144.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-04)
- codigo-do-trabalho 2023-04-04: Artigo 159.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 166.º-A (shown with in-force day 2023-05-01; the record keeps the version in force from 2022-01-01)
- codigo-do-trabalho 2023-04-04: Artigo 168.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2022-01-01)
- codigo-do-trabalho 2023-04-04: Artigo 173.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 179.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 182.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 183.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 185.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 186.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 189.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 191.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2013-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 192.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2013-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 196.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 206.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2015-09-06)
- codigo-do-trabalho 2023-04-04: Artigo 207.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 208.º-B (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 209.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2023-04-04: Artigo 211.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2023-04-04: Artigo 249.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-04)
- codigo-do-trabalho 2023-04-04: Artigo 250.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 251.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2022-01-04)
- codigo-do-trabalho 2023-04-04: Artigo 252.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 252.º-A (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 254.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 255.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-04)
- codigo-do-trabalho 2023-04-04: Artigo 257.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 268.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 269.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2023-04-04: Artigo 277.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 278.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 285.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2021-04-09)
- codigo-do-trabalho 2023-04-04: Artigo 305.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2023-04-04: Artigo 313.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 337.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 344.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 345.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2013-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 354.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 360.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2023-04-04: Artigo 361.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 362.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 363.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 366.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2013-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 371.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2023-04-04: Artigo 383.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2012-08-01)
- codigo-do-trabalho 2023-04-04: Artigo 400.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 401.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 419.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 424.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 433.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 438.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 439.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 447.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 449.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 460.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 461.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 466.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 485.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-04-04: Artigo 497.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-10-01)
- codigo-do-trabalho 2023-04-04: Artigo 515.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 516.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2019-09-09)
- codigo-do-trabalho 2023-04-04: Artigo 517.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2009-02-17)
- codigo-do-trabalho 2023-05-29: Artigo 12.º-A (shown without a day; the record keeps the version in force from 2023-05-29)
- codigo-do-trabalho 2023-05-29: Artigo 112.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2023-05-29)
- codigo-do-trabalho 2023-05-29: Artigo 168.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2023-05-29)
- codigo-do-trabalho 2023-05-29: Artigo 251.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2023-05-29)
- codigo-do-trabalho 2023-05-29: Artigo 466.º (shown with in-force day 2023-05-01; the record keeps the version in force from 2023-05-29)
- codigo-civil 1975-02-19: Artigo 1029.º (shown with in-force day 1975-02-20; the record keeps the version in force from 1967-06-01)
- codigo-civil 1975-02-19: Artigo 1051.º (shown with in-force day 1975-02-20; the record keeps the version in force from 1967-06-01)
- codigo-civil 1975-04-30: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1975-07-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1975-07-01: Artigo 1778.º (shown without a day; the record keeps the version in force from 1975-07-01)
- codigo-civil 1975-10-11: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1975-10-11: Artigo 1605.º (shown without a day; the record keeps the version in force from 1975-10-11)
- codigo-civil 1975-10-11: Artigo 1778.º (shown without a day; the record keeps the version in force from 1975-07-01)
- codigo-civil 1976-03-16: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1977-07-21: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1978-04-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1978-04-01: Secção II (shown with in-force day 1978-04-06; the record keeps the version in force from 1967-06-01)
- codigo-civil 1978-04-01: Artigo 1817.º (shown with in-force day 1978-07-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1978-04-06: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1978-04-06: Artigo 1817.º (shown with in-force day 1978-07-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1978-07-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1980-07-18: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1980-07-18: Artigo 410.º (shown with in-force day 1980-07-18; the record keeps the version in force from 1980-07-18)
- codigo-civil 1985-09-21: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1985-09-21: Artigo 508.º (shown with in-force day 1985-10-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1985-09-21: Artigo 510.º (shown with in-force day 1985-10-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1985-09-21: Artigo 1143.º (shown with in-force day 1985-10-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1985-10-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1986-12-31: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1986-12-31: Artigo 412.º (shown without a day; the record keeps the version in force from 1986-12-31)
- codigo-civil 1993-08-22: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1995-01-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1995-01-01: Artigo 1889.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1978-04-01)
- codigo-civil 1995-01-01: Artigo 1890.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1978-04-01)
- codigo-civil 1995-01-01: Artigo 1892.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1978-04-01)
- codigo-civil 1995-01-01: Artigo 1937.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1995-01-01: Artigo 1938.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1978-04-01)
- codigo-civil 1995-01-01: Artigo 2053.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1995-01-01: Artigo 2083.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1995-01-01: Artigo 2084.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1995-01-01: Artigo 2086.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1995-01-01: Artigo 2102.º (shown with in-force day 1995-03-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 1995-03-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1995-09-15: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1996-03-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1996-03-01: Artigo 1410.º (shown without a day; the record keeps the version in force from 1996-03-01)
- codigo-civil 1996-03-11: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1996-03-11: Artigo 1410.º (shown without a day; the record keeps the version in force from 1996-03-01)
- codigo-civil 1997-04-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1998-05-13: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1998-05-13: Artigo 1978.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1993-08-22)
- codigo-civil 1998-05-13: Artigo 1979.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1993-08-22)
- codigo-civil 1998-05-13: Artigo 1980.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1993-08-22)
- codigo-civil 1998-05-13: Artigo 1981.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1993-08-22)
- codigo-civil 1998-05-13: Artigo 1982.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1993-08-22)
- codigo-civil 1998-05-13: Artigo 1984.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1993-08-22)
- codigo-civil 1998-06-08: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1998-06-08: Artigo 1979.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1998-06-08)
- codigo-civil 1998-06-08: Artigo 1980.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1998-06-08)
- codigo-civil 1998-06-08: Artigo 1981.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1998-06-08)
- codigo-civil 1998-06-08: Artigo 1984.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1998-06-08)
- codigo-civil 1998-06-08: Artigo 1992.º (shown with in-force day 1998-06-08; the record keeps the version in force from 1998-06-08)
- codigo-civil 1998-08-15: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1998-11-11: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 1999-07-30: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2001-06-27: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2002-01-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2003-09-15: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2003-09-15: Artigo 1974.º (shown with in-force day 2003-09-22; the record keeps the version in force from 1993-08-22)
- codigo-civil 2003-09-15: Artigo 1978.º (shown with in-force day 2003-09-22; the record keeps the version in force from 1998-06-08)
- codigo-civil 2003-09-15: Artigo 1978.º-A (shown with in-force day 2003-09-22; not yet in force, left out)
- codigo-civil 2003-09-15: Artigo 1979.º (shown with in-force day 2003-09-22; the record keeps the version in force from 1998-06-08)
- codigo-civil 2003-09-15: Artigo 1980.º (shown with in-force day 2003-09-22; the record keeps the version in force from 1998-06-08)
- codigo-civil 2003-09-15: Artigo 1981.º (shown with in-force day 2003-09-22; the record keeps the version in force from 1998-06-08)
- codigo-civil 2003-09-15: Artigo 1983.º (shown with in-force day 2003-09-22; the record keeps the version in force from 1993-08-22)
- codigo-civil 2003-09-15: Artigo 1992.º (shown with in-force day 2003-09-22; the record keeps the version in force from 1998-06-08)
- codigo-civil 2003-09-22: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2004-03-24: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2006-06-27: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2006-06-27: Artigo 1073.º (shown with in-force day 2007-06-27; the record keeps the version in force from 1975-04-30)
- codigo-civil 2007-06-27: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2007-07-24: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2007-09-29: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2007-09-29: Artigo 158.º (shown with in-force day 2007-10-31; the record keeps the version in force from 1978-04-01)
- codigo-civil 2007-09-29: Artigo 168.º (shown with in-force day 2007-10-31; the record keeps the version in force from 1978-04-01)
- codigo-civil 2007-09-29: Artigo 174.º (shown with in-force day 2007-10-31; the record keeps the version in force from 1967-06-01)
- codigo-civil 2007-09-29: Artigo 185.º (shown with in-force day 2007-10-31; the record keeps the version in force from 1967-06-01)
- codigo-civil 2007-09-29: Artigo 201.º-A (shown with in-force day 2007-10-31; not yet in force, left out)
- codigo-civil 2007-10-31: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2008-07-21: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2008-11-30: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2009-04-02: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2009-05-31: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2009-09-16: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2009-09-16: Artigo 1770.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1978-04-01)
- codigo-civil 2009-09-16: Artigo 2053.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2009-09-16: Artigo 2083.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2009-09-16: Artigo 2084.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2009-09-16: Artigo 2085.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1967-06-01)
- codigo-civil 2009-09-16: Artigo 2086.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2009-09-16: Artigo 2102.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2010-06-05: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2010-06-05: Artigo 1770.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1978-04-01)
- codigo-civil 2010-06-05: Artigo 2053.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2010-06-05: Artigo 2083.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2010-06-05: Artigo 2084.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2010-06-05: Artigo 2085.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1967-06-01)
- codigo-civil 2010-06-05: Artigo 2086.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2010-06-05: Artigo 2102.º (shown with in-force day 2010-07-18; the record keeps the version in force from 1995-03-01)
- codigo-civil 2010-07-18: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2010-09-04: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2012-07-14: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2012-09-13: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2012-09-13: Artigo 1048.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1055.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1069.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1072.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1080.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1083.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1084.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1085.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1087.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1094.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1095.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1096.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1097.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1098.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1100.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1101.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1102.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1103.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1104.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1106.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1110.º (shown with in-force day 2012-11-12; the record keeps the version in force from 2006-06-27)
- codigo-civil 2012-09-13: Artigo 1424.º (shown with in-force day 1995-01-01; the record keeps the version in force from 2012-09-13)
- codigo-civil 2012-09-13: Artigo 1425.º (shown without a day; the record keeps the version in force from 2012-09-13)
- codigo-civil 2012-09-13: Artigo 1426.º (shown with in-force day 1995-01-01; the record keeps the version in force from 2012-09-13)
- codigo-civil 2012-11-12: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2013-09-02: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2015-01-18: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2015-01-18: Artigo 2036.º (shown with in-force day 2015-01-29; the record keeps the version in force from 1967-06-01)
- codigo-civil 2015-01-29: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2015-05-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2015-09-26: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2015-09-26: Artigo 1905.º (shown with in-force day 2015-10-01; the record keeps the version in force from 2008-11-30)
- codigo-civil 2015-10-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2017-04-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2017-04-01: Artigo 1302.º (shown with in-force day 2017-05-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 2017-04-01: Artigo 1305.º (shown with in-force day 2017-05-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 2017-04-01: Secção II (shown with in-force day 2017-05-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 2017-04-01: Artigo 1318.º (shown with in-force day 2017-05-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 2017-04-01: Artigo 1321.º (shown with in-force day 2017-05-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 2017-04-01: Artigo 1323.º (shown with in-force day 2017-05-01; the record keeps the version in force from 2002-01-01)
- codigo-civil 2017-04-01: Artigo 1733.º (shown with in-force day 2017-05-01; the record keeps the version in force from 1967-06-01)
- codigo-civil 2017-04-01: Artigo 1775.º (shown with in-force day 2017-05-01; the record keeps the version in force from 2008-11-30)
- codigo-civil 2017-04-01: Artigo 1793.º-A (shown with in-force day 2017-05-01; not yet in force, left out)
- codigo-civil 2017-05-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2017-06-15: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2017-06-15: Artigo 1906.º-A (shown with in-force day 2017-06-23; not yet in force, left out)
- codigo-civil 2017-06-23: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2018-09-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2018-09-01: Artigo 32.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 85.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Secção V (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 131.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Subsecção III (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 138.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 139.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 140.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 141.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 142.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 143.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 144.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 145.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 146.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 147.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 148.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 149.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 150.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 151.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 320.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 488.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2017-04-01)
- codigo-civil 2018-09-01: Artigo 705.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 706.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1003.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1174.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1175.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1176.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1601.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 1604.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2015-09-26)
- codigo-civil 2018-09-01: Artigo 1621.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1633.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2007-09-29)
- codigo-civil 2018-09-01: Artigo 1639.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1643.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 1650.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 1708.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1769.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 1785.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2008-11-30)
- codigo-civil 2018-09-01: Artigo 1821.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 1850.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 1857.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2007-09-29)
- codigo-civil 2018-09-01: Artigo 1860.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 1861.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 1913.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2008-11-30)
- codigo-civil 2018-09-01: Artigo 1914.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2008-11-30)
- codigo-civil 2018-09-01: Artigo 1933.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 1970.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 2082.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-09-01: Artigo 2189.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 2192.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 2195.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-09-01: Artigo 2298.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2018-10-30: Artigo 32.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 85.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Secção V (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 131.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Subsecção III (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 138.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 139.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 140.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 141.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 142.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 143.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 144.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 145.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 146.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 147.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 148.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 149.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 150.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 151.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 320.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 488.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2017-04-01)
- codigo-civil 2018-10-30: Artigo 705.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 706.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1003.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1174.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1175.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1176.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1601.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 1604.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2015-09-26)
- codigo-civil 2018-10-30: Artigo 1621.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1633.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2007-09-29)
- codigo-civil 2018-10-30: Artigo 1639.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1643.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 1650.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 1708.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1769.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 1785.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2008-11-30)
- codigo-civil 2018-10-30: Artigo 1821.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 1850.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 1857.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2007-09-29)
- codigo-civil 2018-10-30: Artigo 1860.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 1861.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 1913.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2008-11-30)
- codigo-civil 2018-10-30: Artigo 1914.º (shown with in-force day 2019-02-10; the record keeps the version in force from 2008-11-30)
- codigo-civil 2018-10-30: Artigo 1933.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 1970.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 2082.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2018-10-30: Artigo 2189.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 2192.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 2195.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1978-04-01)
- codigo-civil 2018-10-30: Artigo 2298.º (shown with in-force day 2019-02-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2019-02-10: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2019-02-13: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2019-10-01: Diploma (shown without a day; the record keeps the version in force from 1975-02-19)
- codigo-civil 2022-01-11: Artigo 1419.º (shown with in-force day 2022-04-10; the record keeps the version in force from 2008-07-21)
- codigo-civil 2022-01-11: Artigo 1424.º (shown with in-force day 2022-04-10; the record keeps the version in force from 2012-09-13)
- codigo-civil 2022-01-11: Artigo 1424.º-A (shown with in-force day 2022-04-10; not yet in force, left out)
- codigo-civil 2022-01-11: Artigo 1427.º (shown with in-force day 2022-04-10; the record keeps the version in force from 1995-01-01)
- codigo-civil 2022-01-11: Artigo 1431.º (shown with in-force day 2022-04-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2022-01-11: Artigo 1432.º (shown with in-force day 2022-04-10; the record keeps the version in force from 1995-01-01)
- codigo-civil 2022-01-11: Artigo 1436.º (shown with in-force day 2022-04-10; the record keeps the version in force from 1995-01-01)
- codigo-civil 2022-02-08: Artigo 1419.º (shown with in-force day 2022-04-10; the record keeps the version in force from 2008-07-21)
- codigo-civil 2022-02-08: Artigo 1424.º (shown with in-force day 2022-04-10; the record keeps the version in force from 2012-09-13)
- codigo-civil 2022-02-08: Artigo 1424.º-A (shown with in-force day 2022-04-10; the record keeps the version in force from 2022-02-08)
- codigo-civil 2022-02-08: Artigo 1427.º (shown with in-force day 2022-04-10; the record keeps the version in force from 1995-01-01)
- codigo-civil 2022-02-08: Artigo 1431.º (shown with in-force day 2022-04-10; the record keeps the version in force from 1967-06-01)
- codigo-civil 2022-02-08: Artigo 1432.º (shown with in-force day 2022-04-10; the record keeps the version in force from 1995-01-01)
- codigo-civil 2022-02-08: Artigo 1436.º (shown with in-force day 2022-04-10; the record keeps the version in force from 1995-01-01)
- codigo-civil 2022-04-10: Artigo 1424.º-A (shown without a day; the record keeps the version in force from 2022-04-10)
- codigo-civil 2023-01-01: Artigo 1424.º-A (shown without a day; the record keeps the version in force from 2022-04-10)
- codigo-civil 2023-01-17: Artigo 1424.º-A (shown without a day; the record keeps the version in force from 2022-04-10)
- codigo-civil 2023-08-18: Artigo 148.º (shown with in-force day 2023-08-20; the record keeps the version in force from 2019-02-10)
- codigo-civil 2023-08-18: Artigo 1424.º-A (shown without a day; the record keeps the version in force from 2022-04-10)
- codigo-civil 2023-08-20: Artigo 1424.º-A (shown without a day; the record keeps the version in force from 2022-04-10)
- codigo-civil 2024-01-01: Artigo 1422.º (shown with in-force day 1995-01-01; the record keeps the version in force from 2024-01-01)
- codigo-civil 2024-01-01: Artigo 1424.º-A (shown without a day; the record keeps the version in force from 2022-04-10)

Undated corrections dated by their publication:

- codigo-do-trabalho 2017-10-02: Artigo 563.º (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-do-trabalho 2023-05-29: Artigo 112.º (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-do-trabalho 2023-05-29: Artigo 12.º-A (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-do-trabalho 2023-05-29: Artigo 168.º (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-do-trabalho 2023-05-29: Artigo 251.º (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-do-trabalho 2023-05-29: Artigo 466.º (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-civil 1975-07-01: Artigo 1778.º (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-civil 1975-10-11: Artigo 1605.º (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-civil 1986-12-31: Artigo 412.º (undated in the DR; dated by the publication of the correction that the DR names for it)
- codigo-civil 2022-02-08: Artigo 1424.º-A (undated in the DR; dated by the publication of the correction that the DR names for it)

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

This repository was built on 2026-10-28 in **Claude Code**, Anthropic's coding tool, by the model **Claude Opus 5.5**
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
