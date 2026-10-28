# Portuguese law, change by change

Three Portuguese acts as a git repository: the Constitution (Constituição da República Portuguesa, 1976), the Civil
Code (Código Civil, approved by Decreto-Lei n.º 47344 of 1966) and the Labour Code (Código do Trabalho, approved by
Lei n.º 7/2009). Each amending act is one commit, credited to that act and dated
the day its change took effect, at noon in Lisbon. The text is the consolidated text published in the
[Diário da República](https://diariodarepublica.pt) (Legislação Consolidada).

*Em português: [abaixo](#em-português).*

## The questions, as git commands

| Question | Command |
| --- | --- |
| What did artigo 7.º of the Constitution say on 1 January 2000? | `python tools/em_vigor.py 2000-01-01 constituicao 7` |
| The whole Constitution as it stood in 1980 | `python tools/em_vigor.py 1980-01-01 constituicao` |
| Artigo 3.º of the Labour Code on 1 January 2020 | `python tools/em_vigor.py 2020-01-01 codigo-do-trabalho 3` |
| Artigo 1577.º of the Civil Code (marriage) on 1 January 2009 | `python tools/em_vigor.py 2009-01-01 codigo-civil 1577` |
| Every change to the Civil Code's artigo 1577.º | `git log --follow --format="%ad %an" --date=short codigo-civil/artigo-1577.md` |
| Which act wrote each paragraph of artigo 7.º? | `git blame constituicao/artigo-007.md` |
| Every change to artigo 7.º, with the act and the day | `git log --follow constituicao/artigo-007.md` |
| The word-level change of each revision | `git log -p --word-diff constituicao/artigo-007.md` |
| Everything one act changed | `git show --stat atos/lei-constitucional-1-2004` |
| What changed in the Labour Code on one day | `git show --stat codigo-do-trabalho/2019-10-01` |
| The amending acts with all their days | [`atos.csv`](atos.csv) |
| Changes credited by date only (the DR names no act) | `git log --grep="Evidence: date only"` |
| Changes the DR names no act for | `git log --grep="sem ato indicado"` |
| Acts amending the Labour Code in 2019 | `git log --format="%an %s" --author="/2019" -- codigo-do-trabalho` |

## The dates, and which one we use

A Portuguese act has the day it was published in the Diário da República (`Published:`) and the day its change took
effect (`In-force:`). **Commits are dated the day the change took effect**, at noon in Lisbon, because that day
decides which text applies. It is the day the DR gives for each provision version (`DataEntradaVigor`). Where the DR
gives none, the commit says so and how it was dated. The Civil Code took effect on 1 June 1967; git cannot store a
date before 1970, so that one commit is dated 1 January 1970 and its real day is in `In-force:`.

`tools/em_vigor.py` reads the `In-force:` trailer, so it gives the same answer in any time zone; raw
`git rev-list --before` takes the reader's local time. In PowerShell, put a `ref:path` argument to `git show` in
double quotes. After a rebuild of this repository, refresh tags with `git fetch --force --tags`.

## What "author" means

The author of a commit is the act that made the change: `Lei n.º 93/2019` (with an address ending
`@diariodarepublica.invalid`, which cannot exist), so `git blame` names the act. Declarations of rectification and
Constitutional Court judgments the DR lists are authors too. The DR keeps, for each act it consolidates, an amendment
timeline that names the provision versions each amending act made; a change is credited to the act the timeline names
for it. A change the timeline names no act for is credited by date only when exactly one act has changes in force that
day (labelled `Evidence: date only`); otherwise it is committed by `Diário da República (INCM)`, labelled. The
committer is always `Lexifina`.

## How it is checked

`tools/check_repo.py` reads each act back from git on every day a version took effect and compares it with the DR's
consolidated text for that day: file by file, and word for word against the raw text read without the build's
renderer. `tools/test_repo.py` checks that the commands above work. The results are in [`REPRODUCE.md`](REPRODUCE.md).

## Files

Each act is a folder. Each article is one file named after its number: `constituicao/artigo-007.md` is artigo 7.º,
`codigo-do-trabalho/artigo-208-a.md` is artigo 208.º-A of the Labour Code, and `codigo-do-trabalho/lei-7-2009/` holds
the articles of Lei n.º 7/2009 itself (the Code is its annex); the Civil Code's articles have four digits
(`codigo-civil/artigo-1577.md`), and `codigo-civil/decreto-lei-47344/` holds the approving decree-law's. The headings of the divisions that begin before an article
are `##` lines at the top of its file; the article's number is the `#` line and its heading the `###` line; each
paragraph is one line. `preambulo.md` is the text before the first article, `assinatura.md` the signatures. A
repealed article is removed, as it leaves the text in force; a suspended one is marked `*(Suspenso)*`.

## What it does not show

- Versions the DR does not consolidate: the Constitution's record starts with the DR's consolidated original text
  (25 April 1976), which ends at artigo 295.º and has no signatures until 1982.
- Commencement the DR does not model: Lei n.º 7/2009, artigo 14.º, deferred some articles of the Labour Code to later
  legislation, and the Civil Code's artigos 1841.º to 1850.º took effect on 1 January 1968; the DR's consolidation,
  and this record, show them from the act's first day.
- Civil Code amendments between 1967 and 1975: the DR's timeline starts in 1975, so earlier changes appear in its
  first later version, committed by the publisher and labelled.
- Where the DR's text for a day and its version days disagree, the record follows the version days; every case is
  listed in REPRODUCE.md and `data/versoes.json`.
- Any act beyond these three. The same build works for any act the DR consolidates: add it to `ACTS` in
  `tools/build.py`.

The DR's consolidated texts have no legal value ("sem valor legal"); only the Diário da República as published is
authoritative.

## How it is built

`tools/build.py` reads the DR and writes this repository from scratch; the same data gives the same hashes. Every
step, the software, the decisions made by hand and what an AI model did are in [`REPRODUCE.md`](REPRODUCE.md). Each
act's folder has a `README.md` listing its articles with how often each changed. [`corpus.json`](corpus.json)
describes the corpus for tools that read several of Lexifina's law repositories.

## Licence

See [LICENSE](LICENSE): the legal text comes from the Diário da República (INCM), under the public service of
universal and free access to it; the history, commit messages, tables and tools are released under CC0 1.0. Whether
the DR's consolidated texts may be republished is not settled here, and the repository is private.

---

## Em português

Três atos portugueses como repositório git: a Constituição da República Portuguesa, o Código Civil e o Código do
Trabalho, no texto consolidado do Diário da República.

- **Cada commit é um ato modificativo**, registado como autor (`Lei n.º 93/2019`), para que `git blame` mostre que ato
  escreveu cada parágrafo. O ato é o que a cronologia de alterações do DR indica para cada versão.
- **Cada commit tem a data de entrada em vigor**, ao meio-dia em Lisboa. A mensagem indica também a data de publicação.
- **Cada artigo é um ficheiro**, cada parágrafo uma linha.
- **Alterações que o DR não atribui a um ato** não são atribuídas a nenhum; o commit é do Diário da República e
  diz porquê.

Os textos consolidados do DR não têm valor legal; só faz fé o Diário da República publicado.
