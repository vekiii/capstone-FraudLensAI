# Reprodukcija kandidata — Feature 06

Testirani aplikacioni kandidat je `d8acc2a335d95e2402f586006925949f4d9f7739`.
Baseline `5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca` služi za poređenje.
Ovo uputstvo i [mapu dokaza](../../evidence/tasks/feature-006-capstone-evidence-map.md)
čitaj iz dokumentacione revizije, a komande izvršavaj iz korena zasebnog
checkout-a kandidata. [Pinovi T016](../../evidence/tasks/feature-006-release-candidate.md).

## 1. Čist checkout i zaključane zavisnosti

U sopstvenoj kopiji repozitorijuma koja sadrži kandidata pokreni sledeće.
Ako imaš lokalne izmene, koristi zasebnu kopiju. Provera treba da vrati
tačan SHA i prazan `git status --short`.

```powershell
$candidate = 'd8acc2a335d95e2402f586006925949f4d9f7739'
if (git status --short) { throw 'Koristi čist checkout.' }
git switch --detach $candidate
if ($LASTEXITCODE -ne 0 -or (git rev-parse HEAD) -ne $candidate -or (git status --short)) {
  throw 'Proveri reviziju i radno stablo.'
}
git rev-parse HEAD
git status --short
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
if ($LASTEXITCODE -ne 0) { throw 'Python instalacija nije uspela.' }
npm.cmd --prefix web ci
if ($LASTEXITCODE -ne 0) { throw 'Web instalacija nije uspela.' }
uv --version
uv run --locked python --version
node --version
npm.cmd --version
```

Potreban je Python 3.14 i Node 24. U nalaz upiši i OS i verziju browser-a.
[Zaključani setup](../../README.md#prerequisites-and-setup).

## 2. T098 transfer, lokalni indeks i provera binding-a

Od vlasnika T098 paketa pribavi odobrene kopije `model-bounded.sqlite`,
`source.sqlite` i `history-index.sqlite`. Git ih ne isporučuje. Smesti ih
u `data/processed/feature-003-t098-20261118/`. Za transfer koristi timski
dogovoreni kanal. Sačuvaj originalne fajlove kao primljene. Ako source ili
indeks imaju neprazan WAL, traži zamrznutu kopiju od vlasnika.

```powershell
$root = 'data/processed/feature-003-t098-20261118'
$pin = '62f099134c57a3129d28f333545a1398f6e812e4:evidence/tasks/feature-003-t098-transfer-20261118.json'
$rawManifest = git show $pin
if ($LASTEXITCODE -ne 0) { throw 'Potreban je originalni feature03 commit sa T098 manifestom.' }
$transfer = ($rawManifest -join "`n") | ConvertFrom-Json
foreach ($name in @('model-bounded.sqlite', 'source.sqlite', 'history-index.sqlite')) {
  $file = @($transfer.files | Where-Object { $_.name -ceq $name })
  if ($file.Count -ne 1) { throw "T098 manifest ne vezuje $name." }
  $file = $file[0]
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $file.name) -ErrorAction Stop).Hash.ToLowerInvariant()
  if ($actual -cne $file.sha256 -or $actual -cne $file.expected) {
    throw "T098 digest mismatch: $($file.name)"
  }
  "{0} {1}" -f $file.name, $actual
}
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
$index = Join-Path $root 'history-index-feature006-local.sqlite'
uv run --locked python -m fraudlens.investigation.cli prepare-history-index --source-store "$root/source.sqlite" --output $index
if ($LASTEXITCODE -ne 0) { throw 'Priprema indeksa nije uspela.' }
uv run --locked python evidence/tasks/feature-006-t098-local-check.py
if ($LASTEXITCODE -ne 0) { throw 'T098 binding ili indeks nisu potvrđeni.' }
```

Za originalni Git objekat dovoljan je lokalno dostupan commit sa grane
`feature03`, bez promene aplikacionog checkout-a. Za ponavljanje koraka na
istom checkout-u eventualni već izgrađen lokalni indeks prvo proveri istom
skriptom. CLI za izgradnju zahteva slobodnu izlaznu putanju.

Indeks čuva apsolutnu putanju i potpis izvornog store-a (veličinu i mtime).
Zato se priprema lokalno, a njegov SHA-256 izračunava iz sopstvenog fajla.
Provera treba da potvrdi stanje `complete`, 5.078.345 indeksiranih redova,
`dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`,
`run_boosted_candidate_smoke` i istovetan Cases i investigation payload
za oba propisana slučaja. Sačuvaj digest i izlaz provere. Istorija u ovoj
proveri treba da bude dostupna. [Izvorni digesti i T002 nalaz](../../evidence/tasks/feature-006-t098-inputs.md).

## 3. Proba bez naplate kroz API, Vite i worker

Otvori tri PowerShell terminala u korenu istog checkout-a. Izaberi jedno
slobodno ime za probu i upiši ga kao `$runName` u **oba backend terminala**.
U oba izvrši blok podešavanja ispod. Za ovu probu koristi checkout bez
serverskog `.env` da podešavanja autora ili ključevi ne utiču na ishod.

```powershell
$runName = 'peer-grounded-01'
$peer = Join-Path $PWD ".cache/006-peer/$runName"
$root = Join-Path $PWD 'data/processed/feature-003-t098-20261118'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
$env:APP_MODE = 'dataset'
$env:APP_SCORER = 'model'
$env:APP_RUN_STORE = Join-Path $root 'model-bounded.sqlite'
$env:INVESTIGATION_ENABLED = 'true'
$env:INVESTIGATION_SOURCE = 'dataset'
$env:INVESTIGATION_DATASET_SCORE_SOURCE = $env:APP_SCORER
$env:INVESTIGATION_DATASET_RUN_STORE = $env:APP_RUN_STORE
$env:INVESTIGATION_DATASET_STORE = Join-Path $root 'source.sqlite'
$env:INVESTIGATION_DATASET_HISTORY_INDEX = Join-Path $root 'history-index-feature006-local.sqlite'
$env:INVESTIGATION_DATASET_HISTORY_INDEX_SHA256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $env:INVESTIGATION_DATASET_HISTORY_INDEX -ErrorAction Stop).Hash.ToLowerInvariant()
$env:INVESTIGATION_STORE = Join-Path $peer 'investigation.sqlite'
$env:INVESTIGATION_PROVIDER = 'test'
$env:INVESTIGATION_TEST_SCENARIO = 'grounded'
$env:INVESTIGATION_SEMANTIC_RETRIEVAL = 'false'
$env:INVESTIGATION_REPORT_PROMPT = 'v4'
```

U **API terminalu** prvo pripremi korpus u novom store-u, pa pokreni API.
Proveri da ispis odgovara korpusu
`corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3`
i retrieval-u `071f1a593fa17471295860bb5abc3a0064261a7e159bdf3d530494881001bccb`.

```powershell
if (Test-Path -LiteralPath $peer) { throw 'Izaberi novo ime probe u oba backend terminala.' }
New-Item -ItemType Directory -Path $peer -ErrorAction Stop | Out-Null
$knowledge = 'data/knowledge/fraudlens-aml-knowledge-v1'
uv run --locked python -m fraudlens.investigation.cli prepare-knowledge --manifest "$knowledge/manifest.json" --retrieval "$knowledge/retrieval.json" --store $env:INVESTIGATION_STORE
if ($LASTEXITCODE -ne 0) { throw 'Priprema korpusa nije uspela.' }
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

U **web terminalu** pokreni jedinu React aplikaciju.

```powershell
$env:VITE_APP_MODE = 'dataset'
npm.cmd --prefix web run dev
```

U slobodnom **worker terminalu** proveri zdravlje direktno i kroz proxy.
Oba odgovora treba da imaju `status=ok` i `mode=dataset`.

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/health'
Invoke-RestMethod 'http://127.0.0.1:5173/api/health'
```

1. Otvori `http://127.0.0.1:5173/` i Cases. Izaberi
   `C6c481448f7d25af15beea1309f44ee58`. Proveri transakciju
   `D4e050598f0f526f6fe690bb4874e2ee5`, snapshot
   `run_boosted_candidate_smoke`, skor 0.9944662676905943 i verziju skora
   `model-history-v1-boosted-candidate`.
2. U panelu **AI istraga** klikni **Pokreni novu istragu**. U browser Network
   prikazu proveri da `POST /api/investigation/runs` ide na istu adresu i port
   kao stranica, sa `Origin: http://127.0.0.1:5173`. Vite prosleđuje `/api` na
   8000 i čuva Host (`changeOrigin: false`). Zabeleži status odgovora i
   `case_id`, `snapshot_ref` i `context_revision` iz pokušaja.
3. Kad UI prikaže da posao čeka worker, u worker terminalu pokreni
   `uv run --locked python -m fraudlens.investigation.cli worker --store $env:INVESTIGATION_STORE --once`.
   Zabeleži izlaz i identitet pokušaja. U panelu proveri validiran nacrt i
   otvori njegov citat. U nalaz upiši jednu tvrdnju i tačno polje ili deo
   teksta koji je potkrepljuje. Za odlomak navedi i naslov, sekciju i verziju.
4. U panelu izaberi odluku, upiši kratko obrazloženje i klikni **Sačuvaj
   odluku**. Osveži stranicu, ponovo otvori isti slučaj, pokušaj i citat.
   Proveri da se isti attempt, report, evidence i review ID, odluka i
   obrazloženje vraćaju čitanjem sačuvanog stanja. Sačuvaj stvarne ishode.

Za probu nedostupne istorije koristi novo ime probe i svež store. Zaustavi
svoj API, pa po istom postupku podesi oba backend terminala. Pre pokretanja
API-ja i workera u oba terminala izvrši sledeće.

```powershell
$env:INVESTIGATION_DATASET_STORE = Join-Path $peer 'absent-history.sqlite'
if (Test-Path -LiteralPath $env:INVESTIGATION_DATASET_STORE) { throw 'Izvor istorije mora biti odsutan.' }
Remove-Item Env:INVESTIGATION_DATASET_HISTORY_INDEX,Env:INVESTIGATION_DATASET_HISTORY_INDEX_SHA256 -ErrorAction SilentlyContinue
```

Ponovi pripremu korpusa i otvori `C4af2f03a9d1bca5fc14d76e05af12140`
(transakcija `Dcc88ddb85039576f141172f225b63a35`, skor 0.9949877910390978).
Proveri da skor i transakcija ostaju iz istog scored store-a, da istorija
ima `unavailable`, `eligible_count=null` i `returned_count=0` i da testni
nacrt traži dopunu. To je kontrolisana proba bez OpenAI zahteva.
[Ranije izvršen testni tok](../../evidence/tasks/feature-006-dataset-smoke.md).

## 4. Stvarni model i granice ponavljanja

Finalno merenje koristilo je `gpt-6-luna`, semantic `v8`, report `v6`,
grupisane alate, striktne sekcije, reasoning `low` i iste pakete korpusa i
retrieval-a. Tačan skup podešavanja i limiti su u `live_environment` u
[zamrznutom manifestu](../../evals/capstone/manifest.json). SHA-256 finalnog
report prompta je `30916591b25012185480b7c978c02653b9df7205801efd52d0fd495a5d3eb20a`.
Ključ ostaje u privatnom serverskom okruženju. Za nov živi prolaz potreban
je zasebno odobren obim i praćenje transporta po
[protokolu](../../evals/capstone/protocol.md), uključujući eventualnu
sintetičku probu `probe-provider --synthetic-only`. Koraci iz odeljka 3
koriste testni provider.

Pre odobrenog živog prolaza proveri bajtove zamrznutih fajlova. Na Windows-u
Git može da konvertuje završetke redova. Istorijski manifest u T016 ima
CRLF digest `7bc9b5b0ca296c27f184cd7883f55b4a53c5b2a6e9eecaa0ba1020b5f16fda8f`;
javni ulazi, offline očekivanja i tadašnja execution šema pinovani su na
LF bajtove iz Git objekata. Ako lokalni digest odstupa, dostavi nalaz uz
konvenciju završetaka redova. Za stvarno izvršavanje uskladi bajtove u
izolovanom checkout-u sa pinovima pre pokretanja. `run.py` zahteva i
istorijski digest konkretnog indeksa iz manifesta. Novi lokalni indeks
drugačijeg digesta zahteva zasebno dogovoreno i evidentirano vezivanje
pre novog živog merenja. Sačuvaj zamrznuti istorijski paket.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'evals/capstone/manifest.json','evals/capstone/inputs/cases.json','evals/capstone/reference/expectations.json','evals/capstone/execution.schema.json'
```

Dokumentacioni HEAD `02ab4061d2e7bae459ebf0d7c2be8885a05f6450` ima
naknadnu ispravku samo execution šeme evidencije (`run_` → `inv_`).
Digest ispravljene LF šeme je
`ee9a8bed2605f8145db72d71957ece0581097dfe2dbf4023b768c646a1a20137`.
Ocene i izvršni ulazi oba merenja su očuvani.
[Zapis provere i istorijski digesti](../../evidence/tasks/feature-006-before-after.md#provera-zapisa).

## 5. Tri scenarija za odbranu i predaja nalaza

| Scenario | Šta pokazati na kandidatu | Izvršeni dokaz i granica |
| --- | --- | --- |
| Validiran nacrt i obnovljiva odluka | Otvori sačuvani EV-01 pokušaj, njegovu citiranu činjenicu o transakciji i odluku; zatim obnovi iste ID-jeve čitanjem u EV-06. | [Final EV-01/06](../../evidence/tasks/feature-006-final-live.md#react-cases-citat-i-sačuvana-odluka). Citat potvrđuje transakciju, 14.821,32 Euro i vreme. EV-01 je **fail** jer procedura ima `no_match`; EV-06 je **pass** sa nula novih poziva. |
| Dopuna | U EV-08 pokaži sačuvane poznate činjenice i citirani `unavailable` za istoriju. | [Final EV-08](../../evidence/tasks/feature-006-final-live.md). Validirani `needs_information`, nula vraćenih i nepoznat broj podobnih događaja. |
| Kontrolisana greška | Pokaži EV-13 kada pokušaj otvori baš citirani dokaz, a API vrati kontrolisanu nedostupnost. | [Final EV-13](../../evidence/tasks/feature-006-final-negative.md). HTTP 404 `evidence_not_found`, UI uklanja prethodni tekst, drugi dokaz ostaje dostupan. Izvršeno u determinističkoj proveri. |

Sačuvane finalne artefakte za odbranu traži preko odobrenog timskog
transfera. Lokalni store iz odeljka 3 služi nezavisnoj probi.
Na kraju zaustavi svoj API i Vite pomoću `Ctrl+C`. Worker sa `--once`
se završava sam. Sačuvaj lokalni store i sirove izlaze u ignorisanim
putanjama, a u [peer zapis](../../evidence/tasks/feature-006-peer-reproduction.md)
upiši pročišćene nalaze, komande, digeste i sve preskočene korake.

## Završna regresija

Izvršava se u T024 na kandidatu. Za pytest koristi svež lokalni privremeni
direktorijum u `.cache` ako sistemski temp ima ograničen pristup.

```powershell
$tempRoot = Join-Path $PWD ('.cache/006-regression-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot -ErrorAction Stop | Out-Null
uv run --locked python -m pytest backend/tests --basetemp "$tempRoot/tmp" -o "cache_dir=$tempRoot/cache"
uv run --locked ruff check backend
npm.cmd --prefix web run test -- --run
npm.cmd --prefix web run build
git diff --check
```
