# Portuguese law in 20 charts

[Português](README.md)

Charts on every country's law, from the whole of global-law: [global-law visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations). These are the charts on Portugal alone.

Twenty charts on Portuguese law, drawn only from the data in this repository: the 248,256 acts of the 1.ª série (first series) of the Diário do Governo and the Diário da República since 5 October 1910, each with its summary; the Constitution and 28 codes with every version the Diário da República consolidates; the 21,375 acts of the I série of the official journal of the Autonomous Region of Madeira; the Assembleia da República's open data (initiatives and their steps, amendments proposed to the State Budget, questions to the Government and the answers); the Constitutional Court's 32,822 rulings and summary decisions; and the CAAD's 10,745 tax-arbitration decisions.

Open [`o-direito-portugues-em-20-graficos.html`](o-direito-portugues-em-20-graficos.html) in a browser. The page is one file with all its data inside; it loads only the d3 and topojson-client libraries, the map of chart 3 and its fonts from the web. The controls at the top right switch the language (Portuguese or English) and the theme (light or dark). Each chart names its data path in the repository, its record count and its limits, and has a table of every number under it. Hover over a mark for the exact values.

The charts are descriptive: they show what the record holds, not why.

## The charts

### I. The official gazette, 1910–2026

#### 1. The 1.ª série year by year

The 248,256 acts of the 1.ª série from 1910 to 2026, by kind, over the political periods: the most in 1994 (3,757); ministerial orders (portarias) are 33% of all.

![The 1.ª série year by year](stills/en/01.png)

#### 2. Laws and decree-laws

Under the Estado Novo, 41 decree-laws for each law (12,283 and 296); since 1976, 4.3 (17,711 and 4,150); the first decree-law came out on 11 April 1933.

![Laws and decree-laws](stills/en/02.png)

#### 3. The overseas empire

The overseas territories in the summaries, on a map and year by year: 30% of the summaries of 1969 name a territory or the colonies; Angola is named most (4,047 acts to 1975).

![The overseas empire](stills/en/03.png)

#### 4. Nationalise and privatise

43 acts on nationalisation in 1975, beginning with the banks; 281 on (re)privatisation since 1988, up to 20 a year.

![Nationalise and privatise](stills/en/04.png)

#### 5. Madeira

Madeira's official journal (JORAM), I série, 2001–2026: 21,375 acts, 58% of them resolutions of the Regional Government, and 382 regional legislative decrees.

![Madeira](stills/en/05.png)

### II. Form, calendar and Europe

#### 6. The weekday

Until 2004, 15% of acts came out on a Saturday; since 2006, only 112 in weekend issues, 48 of them on a single Saturday in 2022.

![The weekday](stills/en/06.png)

#### 7. The spelling

The 1990 spelling in the summaries: 88% old spellings in December 2011, 24% in January 2012 and none by April; and six words year by year.

![The spelling](stills/en/07.png)

#### 8. Rectifications

8,550 rectifications since 1976: from 1983 to 2003, 79% came out on the last day of a month; since 2012, 98% within the 60 days of Lei n.º 74/98.

![Rectifications](stills/en/08.png)

#### 9. The State Budget

The budget law published after 1 January in 15 years since 1977; the 2022 one came out on 27 June.

![The State Budget](stills/en/09.png)

#### 10. EU directives

33% of the decree-laws of 2010 cite a directive in their summary; 1,845 directives cited since 1986.

![EU directives](stills/en/10.png)

### III. The Assembleia da República

#### 11. Government and MPs' bills

By legislature, I to XVII: 73% of the Government's bills (propostas de lei) became law, against 24% of MPs' bills (projetos de lei).

![Government and MPs' bills](stills/en/11.png)

#### 12. The parties

MPs' bills by party since 1976: the PCP filed the most (2,908); the PSD saw the most become law (903).

![The parties](stills/en/12.png)

#### 13. Budget amendments

The amendments proposed to the State Budget, from 741 (OE 2006) to 2,917 (OE 2027); 76% of the PS's passed and 2% of Chega's.

![Budget amendments](stills/en/13.png)

#### 14. Questions to the Government

MPs' written questions since 2005: between 11% and 33% answered within the 30 days the Rules set, by legislature.

![Questions to the Government](stills/en/14.png)

### IV. The Constitution and the codes

#### 15. The seven revisions of the Constitution

From 21,864 words in 1976 to 31,796 since 2005, by part; the 1982 revision added or removed 16,403.

![The seven revisions of the Constitution](stills/en/15.png)

#### 16. The codes

28 codes year by year: the Civil Code amended by 84 acts, the Penal Code by 63 since 1995.

![The codes](stills/en/16.png)

#### 17. The Civil Code

74% of its articles keep their original 1966 wording; in the book on the family, only 33%.

![The Civil Code](stills/en/17.png)

### V. The courts

#### 18. Constitutional review

342 declarations of unconstitutionality with general binding force by the Constitutional Court since 1983, 58 by the Council of the Revolution before; 17 on State Budget laws.

![Constitutional review](stills/en/18.png)

#### 19. The Constitutional Court

27,794 rulings since 1983, 75% on appeals in concrete cases; 766 in abstract review.

![The Constitutional Court](stills/en/19.png)

#### 20. Tax arbitration

The CAAD's 10,745 decisions since 2011, by tax: corporate income tax first (2,959); 228 on the road service levy in 2024 alone.

![Tax arbitration](stills/en/20.png)

## Data

As of commit `6a2506e545` (origin/main on 17 November 2026); the 1.ª série to 13 November 2026.

| Dataset | Where in the repository | Records | Coverage |
| --- | --- | ---: | --- |
| Acts of the 1.ª série | `<kind>/<year>/<number>/`, `act/<year>/`, git log (`Law:`, `Published:`, summary) | 248,256 acts | Diário do Governo and Diário da República, 5 October 1910 to 13 November 2026: each act's name, day of publication and summary, united from the records with text, the metadata-only records and the consolidated texts in force |
| Records of the 2.ª série | `serie-2/` | 87,469 records | regulations, portarias, normative despachos, notices and edicts; metadata only for kinds that may identify persons |
| Constitution and codes | `constitution/`, `code/` (and `constituicao/`, `codigo-civil/`, `codigo-do-trabalho/` before 10/11/2026), git log `--raw` | 30,359 file changes; 1,320 versions of the Constitution's articles read | every version of every article since the start of the consolidated text; the Civil Code from 1975 in the DR's timeline |
| Madeira | `joram/atos/` | 21,375 acts | the JORAM's I série, 2001–2026 |
| Assembleia da República | `parlamento/` | 27,241 initiatives and 243,242 steps; 26,898 budget amendments; 56,974 questions and 83,386 answers | the parliament's open data, legislatures I–XVII; questions from legislature X (2005) |
| Constitutional Court | `jurisprudencia/tc/`, `jurisprudencia/tc-decisoes-sumarias/` (`record.json`) | 27,794 rulings and 5,028 summary decisions | rulings since 1983 with the kind of proceedings; summary decisions since 1998 |
| Tax arbitration | `jurisprudencia/caad-tributario/` | 10,745 decisions | CAAD, 2011–2026, with their descriptors |
| Git history | git log | 1,466,570 commits | one commit per version, dated the day it took effect |

## Limits

- **Categories are read from names and summaries.** Each act's kind, rectifications, the overseas territories, nationalisations and privatisations, directives, budget laws, the outcome of constitutional rulings and each arbitration decision's tax follow the rules in `src/prep.py`; whatever no rule recognises counts as "other".
- **The 1.ª série unites several sources.** Before 1960 many acts have only a record without text (the DR has only a scanned PDF), but all have a summary; the day of entry into force is read for only some acts and is not used.
- **The Assembly's open data are incomplete** for the initiatives of legislatures III, XIII and XIV, drawn lighter; XVII is under way (charts 11 to 14).
- **The codes' history is the Diário da República's.** The Civil Code starts in 1975 (changes from 1967 to 1975 appear in the next version); the five tax codes published by the Tax Authority have only their current text and are left out; the 1976 text of the Constitution is the one the DR consolidates (it ends at article 295).
- **The outcome of Constitutional Court rulings** is not in their records: it is read from the summaries of the rulings published in the 1.ª série (chart 18).
- **The Azores are not in the repository**; the higher courts' rulings from the DGSI are not used.
- **2026 is partial** (to mid-November) and drawn lighter.

## Rebuilding

```sh
python visualisations/src/make.py            # history, trees and records -> src/.build/ -> o-direito-portugues-em-20-graficos.html
node visualisations/src/stills.cjs           # images for these READMEs (needs Playwright; PLAYWRIGHT=<path> if not global)
```

`make.py` reads everything from git objects, so it also works in a blobless (`--filter=blob:none`) or `--no-checkout` clone, where it downloads only the `record.json` of the Constitutional Court's rulings and the versions of the Constitution's articles: about 34,000 small files. It reads `origin/main` (or `HEAD`) by default; `--ref` picks another. The history is read line by line. It writes nothing into the repository except the page and the `src/.build/` folder (which git ignores).

| File | What it does |
| --- | --- |
| `src/make.py` | extracts the history, the codes' changes and the records into `src/.build/`, then runs `prep.py` and `build.py` |
| `src/prep.py` | computes every number for the 20 charts and the data profile into `src/.build/data.json` |
| `src/page.tpl.html` | the page: text in both languages, the charts (d3), the tables |
| `src/build.py` | puts `data.json` into the template and writes the page |
| `src/stills.cjs` | draws each chart as a PNG into `stills/pt/` and `stills/en/` |

## Source and licence

The texts and records are those of the Diário da República, published by the INCM under the public service of universal and free access (Decreto-Lei n.º 83/2016), and of the other official sources each folder names (Assembleia da República, Tribunal Constitucional, CAAD, Autonomous Region of Madeira); official texts such as laws are not protected by copyright. The code, tables and this documentation are CC0 1.0. See [`LICENSE`](../LICENSE).
