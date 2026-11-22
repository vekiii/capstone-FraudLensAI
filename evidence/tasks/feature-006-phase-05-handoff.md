# Feature 06 · Predaja faze 5

22. novembar 2026, Europe/Belgrade. Početna grana `006-capstone-evaluation`,
HEAD `02ab4061d2e7bae459ebf0d7c2be8885a05f6450`, početno radno stablo
čisto. [Originalni zahtev](../../prompts/development/006-capstone-phase-05.md)
je sačuvan pre izmena kao identična kopija primljenog fajla.

| Task | Stanje |
| --- | --- |
| T020 | Završeno i čekirano. Uputstvo za čist checkout, lokalni indeks, API/worker/Vite i tri scenarija iz finalnih dokaza. [Quickstart](../../specs/006-capstone-evaluation/quickstart.md). |
| T021 | Čeka nalaz drugog člana iz čistog checkout-a. [Zapis i koraci](feature-006-peer-reproduction.md). |
| T022 | Popisana četiri dokaziva tehnička doprinosa; čekaju individualne potvrde i konkretni pregledi rada kolega. [Doprinosi](feature-006-cap08-contributions.md). |
| T023 | Mapa pokriva osam CAP stavki i tri scenarija za odbranu; završetak zavisi od T021/T022. [CAP mapa](feature-006-capstone-evidence-map.md). |

Testirani kandidat je `d8acc2a335d95e2402f586006925949f4d9f7739`.
Poređenje sa baseline-om `5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`
ostaje 11/16 → 13/16. Finalni EV-01 (procedura `no_match`), EV-04
(`citation_set_mismatch`) i EV-07 (generički pogoci bez razjašnjenja)
ostaju neuspešni. SC-001 i SC-003 imaju izvršen dokaz. SC-002 ostaje
otvoren zbog baseline EV-06; SC-004 čeka reprodukciju i potvrde.
[Istorijski nalazi](feature-006-before-after.md).

## Šta je provereno u ovoj sesiji

PowerShell u korenu checkout-a, uv 0.10.9, zaključani Python 3.14.3, Node
v24.20.0, npm 11.19.0, Vite 8.3.8. Spec Kit sa
`SPECIFY_FEATURE_DIRECTORY=specs/006-capstone-evaluation`: prvo je sistemska
PowerShell policy blokirala direktan poziv; postojeća komanda
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks`
je potom vratila exit 0. Checklist `requirements.md` ima 14/14 stavki,
bez pre ili post hookova (`.specify/extensions.yml` nije prisutan).

| Komanda ili provera | Ishod |
| --- | --- |
| `git cat-file -t <baseline>` i `git cat-file -t <final>`; `git diff --exit-code 5974f94 d8acc2a -- evals/capstone uv.lock web/package-lock.json` | Exit 0, oba objekta su commit, paket i lockfile-ovi su isti između merenja. |
| `git diff --exit-code d8acc2a HEAD -- backend/src web data/knowledge uv.lock` i `git merge-base --is-ancestor <commit> d8acc2a` (Vedran, Isidora, Elena) | Exit 0, proba koristi isti aplikacioni kod i proverene doprinose iz istorije kandidata. |
| `uv run --locked --no-sync python -m fraudlens.investigation.cli <komanda> --help` za `prepare-history-index`, `prepare-knowledge`, `worker` i `probe-provider`; `uv run --locked --no-sync uvicorn --help`; `npm.cmd --prefix web exec --offline -- vite --version` | Exit 0, pročitane stvarne opcije i lokalna Vite verzija. |
| `uv run --locked --no-sync python evidence/tasks/feature-006-t098-local-check.py` uz `PYTHONPATH=backend/src` | Exit 0, sva tri originalna digesta ista, lokalni indeks `605a37302c6436e72c2cbc5a5b4d257c73048ad527f6e40df81f5ead7df5901c`, 5.078.345 redova, pun Cases/Investigation payload jednak za oba slučaja; istorija `available/full`. |
| `uv run --locked --no-sync python -m fraudlens.investigation.cli prepare-knowledge --manifest <manifest> --retrieval <retrieval> --store <svež-ignorisani-store>` | Exit 0, objavljeni korpus `corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3`, retrieval `071f1a593fa17471295860bb5abc3a0064261a7e159bdf3d530494881001bccb`. |
| Offline poređenje Git blobova, deljenih tabela i lokalnih linkova; PowerShell parser za blokove u quickstart-u; provera obrazaca ključeva; `git check-ignore` | Potvrđeni isti finalni SHA u tri deljena zapisa, obe liste po 16 EV redova, zbir i tačni padovi, CAP mapa sa osam stavki. Istorijski CRLF manifest, LF pinovi i zaseban LF digest ispravke šeme potvrđeni iz Git blobova. Proverene ignorisane putanje store-a, izvora i sirovih rezultata. |
| `uv run --locked --no-sync python .cache/006-t020-quickstart-check.py` uz `PYTHONPATH=backend/src` | Exit 0 u završnom prolazu. Dve stvarne lokalne HTTP probe kroz Vite/FastAPI sa eksplicitnim `worker --once`, testnim providerom i svežim store-ovima. Zdravlje direktno/proxy i Cases 200, isti snapshot i context revision, create 202 uz isti origin, validirani `ready_for_review` i `needs_information`, potkrepljena citirana tvrdnja, čuvanje 201 i ponovno otvaranje istog nacrta, citata i odluke 200. U drugom scenariju istorija `unavailable` uz `eligible_count=null` i nula vraćenih. |
| `git diff --check` i provera novih Markdown fajlova | Exit 0 za diff, bez grešaka whitespace-a u novim fajlovima. |

Prvi agentski HTTP prolaz čuva odluku, ali njegova završna asercija poredi
ceo report pre i posle odluke. Polje `semantic_review` se očekivano menja
sa `not_reviewed` na `reviewed_with_notes`. Druga proba potvrđuje osnovni
tok, ali provera citata za nedostupnu istoriju ne obuhvata odgovarajuće
sekcije nacrta. Obe probe imaju exit 1 u skripti. Završni prolaz poredi
isti report ID, nacrt i review i proverava sve ugovorene sekcije. Izlazi
su lokalni u `.cache/006-t020-api-7b0a7d5676d348598550d7fd25cd31d2/`.
Procesi su zaustavljeni. Ovo je automatizovana HTTP provera sa Vite proxy-jem.
Browser ponavljanje i nezavisni čist checkout idu kroz T021.

T001 i T003 beleže ranije zaključane instalacije. T002 i T007 beleže
raniju izgradnju indeksa i browser izvršavanje. U ovoj sesiji korišćene su
postojeće zaključane zavisnosti i već pripremljen kompatibilni indeks.
Sirovi Capstone rezultati iz faze 4 nisu lokalno dostupni u dokumentovanom
`evals/results/capstone/`. Poređenje ove sesije proverava Git objekte i
deljene sažetke, uz istorijske digeste iz T019. Nije izvršena ponovna
agregacija iz sirovih rezultata.

RED nije primenljiv na dokumentaciju. Novih plaćenih poziva i novog
živog merenja nije bilo. T024/T025 su van ove faze.

Sledeći korak je stvarni nalaz drugog člana prema quickstart-u, iz
sopstvenog čistog checkout-a kandidata, sa testnim providerom i novim store-om.
