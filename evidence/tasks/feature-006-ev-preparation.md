# Feature 06 · T009–T011 · Lokalna priprema EV paketa

22. novembar 2026. · Europe/Belgrade · Grana `006-capstone-evaluation` ·
početni HEAD `df8a79945844414c7f903d0149bc75358b7e21f4`, početno radno
stablo čisto. Provere su izvršene nad lokalnim izmenama na toj reviziji.
Spec Kit prerequisites exit 0 i checklist 14/14. Python 3.14.7, uv 0.10.9,
pytest 9.2.0, Ruff 0.17.4, jsonschema 4.26.0, OpenAI SDK 3.51.0, httpx2 2.16.0,
Node 24.20.0, npm 11.19.0 i Vitest 5.1.0.
[Originalni nalog](../../prompts/development/006-capstone-t009-t011.md).

## T009 · Ulazi, reference i početna stanja

Provera paketa našla je tačno 16 EV ID-jeva u svakom fajlu, deset živih
i šest determinističkih ulaza. Paketi imaju odvojene SHA-256 digeste.
EV-06 koristi sačuvane identifikatore i store EV-01 iz tekuće faze i
beleži blokadu ako sačuvani preduslov nedostaje.

| Fajl | SHA-256 lokalnih bajtova |
| --- | --- |
| [Javni scenariji](../../evals/capstone/inputs/cases.json) | `7a52db065205cb3721596c6f6452d991948a6f42c5b28d23989b217c8162ba26` |
| [Offline očekivanja](../../evals/capstone/reference/expectations.json) | `57a84eb527a694eb33e2b312438f94a582741a225d42f30ea322d6950ed85953` |
| [Šema evidencije](../../evals/capstone/execution.schema.json) | `0433ef503461a604030936b68831e4dafa57fcd8b8142aa743308a7d717f1307` |

Postojeća T098 skripta je ponovo potvrdila sva tri transfer digesta,
kompatibilni lokalni indeks od 5.078.345 redova sa SHA-256
`8745ec13848f5ce0f76417fd0c2f7c731a2189cb634034aea5eeaa3a205c5a9f`,
isti Cases i investigation sadržaj i objavljeni model score za oba
slučaja iz matrice. EV-04 pripremna proba nad javnim ulazom potvrdila je
dostupnu istoriju sa pokrivenošću `full`, uz 40 podobnih prethodnih
događaja pošiljaoca i 36 primaoca. Za EV-08 korišćen je isti scored store
i nepostojeći fajl iz zasebnog privremenog direktorijuma bez podešavanja
indeksa. `DatasetReader.resolve` potvrdio je isti snapshot i transakciju.
Oba poziva `DatasetReader.read` vratila su `unavailable`, `eligible_count=null`
i `returned_count=0`. Prva inline proba je koristila pogrešnu putanju do
transakcije u kontekstu (`KeyError`, exit 1). Ponovljena proba je pročitala
`source_payload.transaction` i završila sa exit 0. Browser ponašanje za
ovaj seed prethodno je provereno u T007.
[T098 dokazi](feature-006-t098-inputs.md) · [T007](feature-006-dataset-smoke.md).

`knowledge.stage` je potvrdio osnovni corpus ID iz ulaza. Za EV-10 napravljena
je kopija manifesta i korpusa u ignorisanom `.cache/006-ev10-staged-525rf_p6/`.
Dodat je tačan javni tekst u `sim-review.md`, sa novim ID-jem korpusa, verzijom
dokumenta i SHA-256 `88dda81273e078b0d602c663943ec403cbbab2315f1856cbf616aa9d38adc6a8`.
Lokalna provera je potvrdila da `knowledge.stage` odbija ovaj `staged` manifest
porukom `Complete reviewed corpus required`. Čekaju stvarni pregled izmene i
objavljeni corpus ID.

## T010 · Stvarni rezultati lokalnih kontrola

[Backend testovi](../../backend/tests/integration/test_capstone_negative.py)
koriste postojeći API fixture, privremeni SQLite store i javne parametre iz
paketa. [EV-13 web test](../../web/tests/investigation-reports.test.ts)
koristi postojeći klijent i kontroler sa simuliranim HTTP odgovorima.

| EV | Opažen ishod | Trag kontrole |
| --- | --- | --- |
| EV-11 | HTTP 422 `invalid_request` bez `snapshot_ref`. | Nula upisanih istraga i rezervacija. Worker je idle, provider factory se nije izvršio. |
| EV-12 | `failed/output_invalid` posle ponovljenog nevalidnog strukturisanog nacrta. | Dva lokalna odgovora, jedan repair sa isključenim alatima, nula redova u tabeli izveštaja. |
| EV-13 | Tačan prethodno dostupan citat vratio je HTTP 404 `evidence_not_found` pri simulaciji nedostupnog arhiviranog dokaza. | Drugi tačan citat, nacrt i audit ostali su isti. Web je uklonio tekst prethodno otvorenog citata, prikazao poruku o nedostupnosti i zatražio samo isti URL. |
| EV-14 | `failed/context_unavailable` za nepoznato ime alata. | Jedan lokalni odgovor i audit `invalid_arguments_or_scope`. Nula rezervisanih alata, dokaza i izveštaja. |
| EV-15 | `failed/provider_failure` i `outcome_unknown=true`. | Adapter je poslao dva zahteva isključivo u `MockTransport`, uz dve rezervacije i jedan retry. Oba su `unknown` sa `request_timeout` i `usage=null`. Nema objavljenog izveštaja. |
| EV-16 | `failed/context_unavailable` posle simuliranog `OSError` pri čitanju istorije. | Dva lokalna odgovora. Korak istorije je `failed` bez dokaza istorije. Sačuvani kontekst, činjenice i procena ostali su dostupni. Nema objavljenog izveštaja. |

Prvo pokretanje dalo je 5 prolaza i jednu grešku u postavci EV-16. Fixture
kreira podrazumevani `HistoryReader` unutar izvršioca, pa je ubacivanje
greške premešteno na njegovu metodu `read`. Ponovljeno pokretanje T010
dalo je **6 prolaza**, exit 0. Ovo su pripremne provere za kasnije T014 i T018.

## T011 · Šema i zbir

[Uputstvo](../../evals/capstone/README.md) opisuje granice izvršavanja,
provenance, tragove i metering. [Validator i agregator](../../evals/capstone/execution.py)
proveravaju zapise bez učitavanja offline referenci. Pre implementacije,
pytest je prijavio **11 očekivanih padova** zbog nedostajućeg modula i
**1 prolaz** za već pripremljen paket. Po implementaciji je prošlo **12/12**
provera, uključujući odbijanje nedostajućeg ili dupliranog ID-ja, nevažećeg
statusa, digest-a, mode-a, nepotpunog traga, nekonzistentne potrošnje,
referentnog polja u zapisu i EV-06 koji ne odgovara sačuvanom pokušaju.

`Draft202012Validator.check_schema` je prošao. CLI je pročitao dva lokalno
generisana sintetička fajla u ignorisanom
`evals/results/capstone/preparation-008058ba-bcc2-4849-99d3-9d0473d6e617/`,
exit 0. Uzorak proverava zbir, sa izmišljenim ishodima isključivo u testu
agregacije.

| Sintetička faza | pass | fail | blocked | not_run | Ukupno |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 5 | 3 | 1 | 7 | 16 |
| final | 6 | 0 | 0 | 10 | 16 |

## Izvršene komande i granice

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
.cache/004-phase06-tools/uv.exe lock --check --offline
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-006-t098-local-check.py
$capstoneTests = @(rg --files backend/tests/integration | rg 'test_(investigation_|capstone_negative)')
.venv/Scripts/python.exe -m pytest -q @capstoneTests backend/tests/unit/test_capstone_execution.py --basetemp ".cache/006-phase4-$([guid]::NewGuid())" --tb=short
.venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_capstone_negative.py backend/tests/unit/test_capstone_execution.py --basetemp ".cache/006-t009-t011-final-$([guid]::NewGuid())" --tb=short
.venv/Scripts/python.exe -m ruff check backend/tests/unit/test_capstone_execution.py backend/tests/integration/test_capstone_negative.py evals/capstone/execution.py
npm.cmd --prefix web run test -- --run tests/investigation-reports.test.ts tests/investigation-dataset-binding.test.tsx tests/investigation-knowledge.test.ts
npm.cmd --prefix web run typecheck
$sample = 'evals/results/capstone/preparation-008058ba-bcc2-4849-99d3-9d0473d6e617'
.venv/Scripts/python.exe evals/capstone/execution.py "$sample/baseline.json" "$sample/final.json"
git diff --check
```

Ciljana backend regresija **64 prošla**, završni fokus **18 prošlo**, web
**21 prošao**, Ruff, typecheck, offline lock i diff provere exit 0. U ovoj
celini zabeleženo je **0 živih poziva**. Primarna merenja, završna puna
regresija i nezavisna reprodukcija ostaju otvoreni. Git commit i push nisu
izvršeni. [Istorijski T008 preflight](feature-006-live-preflight.md).

## Šta ostaje za T012

- Potvrditi spremnost T007–T011 i lokalne putanje, artefakte i seed-ove.
  Završiti ljudski pregled izmenjenog EV-10 dokumenta i potvrditi
  njegov objavljeni corpus ID. Ponovo potvrditi kontrolisanu nedostupnost
  istorije za konačni EV-08 seed.
- Potvrditi reviziju, stvarni model i semantic/report profil, limite i
  budžet za primarna merenja i dogovorena ponavljanja. T008 odobrenje
  pokrivalo je preflight. Proveriti da primarni ulaz sa potvrđenom istorijom
  može da stane u dogovoreni profil i evidentirati eventualnu blokadu.
- Zamrznuti `evals/capstone/manifest.json` i `evals/capstone/protocol.md`
  sa svih 16 ID-jeva, verzijama i digestima svakog ulaza, početnog stanja i
  očekivanja, odvojenim hash-evima izvršnog i offline paketa, referencama
  na artefakte i procedurom za reset, retry i blokade. Sačuvati pravilo
  EV-06 o podacima iz EV-01 iste faze.
