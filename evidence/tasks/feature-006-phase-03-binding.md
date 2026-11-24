# Feature 06 · T004–T006 · Dataset binding

22. novembar 2026. · Europe/Belgrade · Grana `006-capstone-evaluation` ·
početni HEAD `b61916a13add61e703f055440dae0027bc6059f0`, čisto radno stablo.
Provere su izvršene nad radnim stablom sa izmenama ove faze.
[Originalni zahtev](../../prompts/development/006-capstone-phase-03.md) ·
[Taskovi](../../specs/006-capstone-evaluation/tasks.md).

## RED

- T004, `npm.cmd --prefix web run test -- --run tests/investigation-dataset-binding.test.tsx`.
  Prvi pokušaj nije prikupio testove zbog jsdom URL-a pri učitavanju JSON primera.
  Posle direktnog JSON importa, četiri v2 provere su pale na nedostajućem panelu,
  a fixture regresija je prošla.
- T005, `python -m pytest -q backend/tests/integration/test_investigation_dataset_binding.py`
  sa jedinstvenim `--basetemp` pod `.cache/`. Početno prikupljanje je tražilo
  `psycopg`, pa je obnovljen zaključani dev setup. Prvi izvršeni testovi su
  utvrdili postojeći 404 za fixture ID u dataset režimu i zaštitu od izmene
  objavljenog reda. Za probu oštećenog skora zaštita je uklonjena isključivo u
  privremenoj test bazi. U ponovljenom RED-u **9 je prošlo, 3 su pala**.
  Dataset testni nacrt sa dostupnom istorijom završavao je kao
  `needs_information`, nacrt sa nedostupnom istorijom izostavljao je poznate
  činjenice, a različit skor između javnog reda i assessment JSON-a bio je prihvaćen.
- T007 je zatim otkrio da inicijalna provera digesta u ovom checkoutu traje
  12,30 i 13,61 s pri dva odvojena čitanja. React je čekao 5 s.
  Dodatni `pytest ... -k index` pao je jer su oba reader-a ponovo izračunala
  oba digesta. [Browser tok](feature-006-dataset-smoke.md).

## GREEN i regresije

- React panel koristi case ID odgovarajućeg formata i dataset snapshot iz v2
  detalja. Aktiviranje mutacija traži uspešno vezivanje za snapshot i serverski
  context revision. Otkazivanje zahteva pri promeni selekcije i kontrole attempt-a,
  citata i odluke pokrivaju isti kontekst. Vite proxy prosleđuje browser Host.
- Dataset reader poredi skor iz assessment JSON-a sa vrednošću koja je
  objavljena u redu skoringa. Testni provider čita dataset putanje iznosa i
  valute i navodi proverljive činjenice i razlog za dopunu kad istorija
  nije dostupna. Odsustvo istorije čuva se kao nepoznat broj, uz nula vraćenih
  stavki.
- Inicijalni list/create zahtev u dataset toku ima rok od 60 s. Validaciju
  indeksa i source digesta dele reader-i unutar procesa uz ograničen keš.
  Potpisi fajlova i stanje WAL-a se proveravaju pri korišćenju. Dodatna
  regresija potvrđuje da izmenjeni indeks sa starim digestom daje `stale_snapshot`.
- **97 backend testova prošlo**. Obuhvaćeni su startup, Cases, investigation
  API, knowledge, recovery, review i binding. T005 ima 13 prolaznih provera.
  **210 web testova prošlo**, uključujući svih pet novih T004 provera.
  Ruff za ceo backend, TypeScript, produkcijski build i lock check su prošli.
  Build zadržava postojeće upozorenje za veličinu Three.js chunk-a.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
$env:npm_config_cache = Join-Path $PWD '.cache/npm'
$env:PYTHONPATH = 'backend/src'
.cache/004-phase06-tools/uv.exe sync --locked --group dev
.cache/004-phase06-tools/uv.exe lock --check
npm.cmd --prefix web ci
$modules = @('startup','cases','investigation_api','investigation_knowledge_api',
  'investigation_recovery_api','investigation_review_api','investigation_dataset_binding')
$files = $modules | ForEach-Object { "backend/tests/integration/test_$_.py" }
.venv/Scripts/python.exe -m pytest -q @files --basetemp ".cache/006-reg-$([guid]::NewGuid())" --tb=short
.venv/Scripts/ruff.exe check backend
npm.cmd --prefix web run test -- --run
npm.cmd --prefix web run typecheck
npm.cmd --prefix web run build
git diff --check
```

Python 3.14.7, uv 0.10.9, Node v24.20.0, npm 11.19.0, Vitest 5.1.0,
Vite 8.3.8. Spec Kit prerequisites exit 0, checklist 14/14.
`.specify/extensions.yml` odsutan. Puna backend regresija i ljudski pregled
ostaju za naredne faze.
