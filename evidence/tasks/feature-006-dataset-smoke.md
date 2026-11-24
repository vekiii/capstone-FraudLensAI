# Feature 06 · T007 · Dataset provera u Chrome-u

22. novembar 2026. · Europe/Belgrade · Chrome 158.0.8127.36, headless.
**Oba scenarija prošla**, exit 0, nad radnim stablom faze 3 na HEAD-u
`b61916a13add61e703f055440dae0027bc6059f0`. Testni provider `grounded`, report
`v4`, semantički retrieval isključen, **0 živih poziva**.
[RED, GREEN i verzije](feature-006-phase-03-binding.md).

## Podaci i rezultati

Za oba slučaja Cases je iz Vite-a učitao isti kompletan objavljeni
`run_boosted_candidate_smoke`. Browser je prikazao vrednost i poreklo
modelskog skora `model-history-v1-boosted-candidate`,
`uncalibrated_probability_estimate`. Kompletan Cases v2 payload bio je
identičan sačuvanom investigation `source_payload`, a revision iz list
zaglavlja odgovarao je pokušaju, izveštaju i otvorenom dokazu.
Dataset ID je `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`.

| Proba | Slučaj i transakcija | Objavljeni skor | Stanje nacrta | Odluka ponovo otvorena posle reload-a |
| --- | --- | ---: | --- | --- |
| Primarna | `C6c481448f7d25af15beea1309f44ee58` · `D4e050598f0f526f6fe690bb4874e2ee5` | 0.9944662676905943 | `ready_for_review` · istorija `available/full` | `close` · `rev_29574c2878a2480bbca8e55aed3cc502` |
| Kontrolisani EV-08 | `C4af2f03a9d1bca5fc14d76e05af12140` · `Dcc88ddb85039576f141172f225b63a35` | 0.9949877910390978 | `needs_information` · istorija `unavailable` | `request_more_information` · `rev_13c14241a7e8428484eb36d93a0ca8b2` |

- Primarni pokušaj `att_54c5d529a4484b878a5255a8e402dc09` koristio je revision
  `1f69da1004ff5bf36d7b63bc05e72747ba92750bea65cd6d35fce65fa603142a`.
  Nacrt je prošao `schema_reference_passed`. Otvoreni su dokaz o transakciji
  i sačuvani proceduralni odlomak. Vrednosti tačnih tvrdnji o iznosu i valuti
  poklapaju se sa otvorenim dokazom i prikazanim slučajem.
- EV-08 pokušaj `att_f6cfbbedbf6f460bb7ee8212990cf83b` koristio je revision
  `c9db364c4315ead10d9b06a690e4cf57c53df6c6eab645af04122fda50e156b9`.
  Izvor istorije pokazivao je na nepostojeći fajl unutar izolovanog
  direktorijuma, uz isti objavljeni scored store. Sačuvani kontekst i
  otvoreni dokaz potvrđuju `unavailable`, `eligible_count=null` i
  `returned_count=0`. Validiran nacrt prikazuje poznati iznos i valutu,
  citira nedostupnost istorije i traži istoriju pošiljaoca za dopunu.
- Obe probe su prošle kroz `created` i eksplicitni worker. Zabeležena su po četiri
  lokalna odgovora testnog providera i tri završena alata
  `get_case_facts`, `get_account_history` i `search_procedures`. Obrazloženje
  je sačuvano kroz stvarni browser POST. Posle reload-a, ponovne selekcije i
  ponovnog otvaranja panela, API je vratio identičan pokušaj, izveštaj i odluku.

Korpus `corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3`,
retrieval `071f1a593fa17471295860bb5abc3a0064261a7e159bdf3d530494881001bccb`.

## Reprodukcija

Korišćena je konfiguracija iz [quickstart-a](../../specs/006-capstone-evaluation/quickstart.md)
sa runtime digestom indeksa za ovaj checkout i sa zasebnim investigation
store-om za svaku probu. Lokalni indeks `history-index-feature006-local.sqlite`
izgrađen je komandom ispod i ima 5.078.345 redova. Njegov SHA-256 je
`8745ec13848f5ce0f76417fd0c2f7c731a2189cb634034aea5eeaa3a205c5a9f`.
Transfer indeks u ovom checkoutu ima isti digest i isti potpis izvora.
Početni i završni `Get-FileHash` za `model-bounded.sqlite`,
`source.sqlite` i transfer `history-index.sqlite` dali su iste SHA-256
vrednosti iz [T098 manifesta provere](feature-006-t098-inputs.md).

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:PYTHONPATH = 'backend/src'
$p = 'data/processed/feature-003-t098-20261118'
.venv/Scripts/python.exe -m fraudlens.investigation.cli prepare-history-index --source-store "$p/source.sqlite" --output "$p/history-index-feature006-local.sqlite"
node .cache/006-dataset-browser.mjs
```

Izvršeni lokalni CDP kontroler je pokrenuo Vite na 5173, Uvicorn na 8000,
i Chrome sa svežim profilom i loopback debug portom 9229. Za svaku probu
pozvao je `prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store <fresh-store>`
i `worker --store <fresh-store> --once`. Process override je izabrao testni
provider sa praznim modelom i ključem. Za EV-08 oba podešavanja history
indeksa su izostavljena, a `INVESTIGATION_DATASET_STORE` je preusmeren na
nepostojeći lokalni fajl. UI potvrde, kontroler i sirovi log su lokalni
pod `.cache/`; izvršni `result.json` je u `.cache/006-browser-5882eb1e-c5ad-484d-a37f-7a258a6379c1/`.

Dva početna Chrome pokušaja u sandboxu pala su na GPU procesu. Uz odobreno
lokalno izvršavanje Chrome je stigao do panela, gde je prvi dataset GET
istekao posle 5 s. Ponovljena provera izvan sandboxa prošla je posle izmene
roka za dataset kontekst i ponovne upotrebe potvrđenog indeksa.

T008 čeka potvrđen budžet. Primarni EV paket i nezavisna ljudska reprodukcija
pripadaju narednim fazama.
