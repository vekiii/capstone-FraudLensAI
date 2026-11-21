# Uputstvo za proveru — Feature 06

Ovo su koraci za implementaciju i verifikaciju. Rezultate popuniti tek posle
stvarnog izvršavanja. Za očekivano ponašanje pogledati [EV matricu](contracts/ev-cases.md).

## 1. Čist checkout i lokalni preduslovi

U čistom checkoutu izabrane revizije zabeležiti `git rev-parse HEAD`, radno
stablo, verzije okruženja i digest odobrenih artefakata. Koristiti Python 3.14,
Node 24 i [postojeći zaključani setup](../../README.md#run-in-two-terminals).

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix web ci
```

U čist checkout pripremiti autorizovane lokalne kopije artefakata, koje
Git ne dostavlja. Uporediti SHA-256 vrednosti sa T098 transfer manifestom,
pa preko Cases potvrditi aktivan `run_boosted_candidate_smoke` i oba kandidata
iz EV matrice. Sačuvati tačan rezultat provere. Ako store nije kompatibilan,
označiti živi tok kao blokiran dok tim ne isporuči kompatibilan izvor.

## 2. Pokretanje dataset slučaja

Konfiguraciju izvora ponoviti u API i worker terminalu. Koristiti relativne
putanje iz korena repozitorijuma i svež, ignorisan investigation store.

```powershell
$env:PYTHONPATH = 'backend/src'
$env:APP_MODE = 'dataset'
$env:APP_SCORER = 'model'
$env:APP_RUN_STORE = 'data/processed/feature-003-t098-20261118/model-bounded.sqlite'
$env:INVESTIGATION_ENABLED = 'true'
$env:INVESTIGATION_SOURCE = 'dataset'
$env:INVESTIGATION_DATASET_SCORE_SOURCE = $env:APP_SCORER
$env:INVESTIGATION_DATASET_RUN_STORE = $env:APP_RUN_STORE
$env:INVESTIGATION_DATASET_STORE = 'data/processed/feature-003-t098-20261118/source.sqlite'
$env:INVESTIGATION_DATASET_HISTORY_INDEX = 'data/processed/feature-003-t098-20261118/history-index.sqlite'
$env:INVESTIGATION_DATASET_HISTORY_INDEX_SHA256 = '8745ec13848f5ce0f76417fd0c2f7c731a2189cb634034aea5eeaa3a205c5a9f'
$env:INVESTIGATION_STORE = 'data/processed/capstone-baseline.sqlite'
```

Za probu bez naplate postaviti `INVESTIGATION_PROVIDER=test` i
`INVESTIGATION_SEMANTIC_RETRIEVAL=false`. Za odobren živi prolaz koristiti
`INVESTIGATION_PROVIDER=openai`, serverske `OPENAI_API_KEY` i `OPENAI_MODEL`
i tačnu konfiguraciju iz manifesta izvršavanja. Potvrditi zaključane runtime
zavisnosti pre poziva. Po odobrenju obračuna, postojeća sintetička proba je
`uv run --locked python -m fraudlens.investigation.cli probe-provider --synthetic-only`.
Sačuvati ishod i računati zahteve u budžet. Pripremna proba ide u odvojeni store.

Pripremiti korpus pre pokretanja servera. Za ovo osnovno uputstvo koristi se
podrazumevani `retrieval.json` iz direktorijuma manifesta. Ako se pri
zamrzavanju izabere druga, proslediti njen konkretan fajl opcijom `--retrieval`
i sačuvati rezultujući identitet.

```powershell
uv run --locked python -m fraudlens.investigation.cli prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store $env:INVESTIGATION_STORE
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

U drugom terminalu pokrenuti postojeći React frontend:

```powershell
$env:VITE_APP_MODE = 'dataset'
npm.cmd --prefix web run dev
```

U pregledaču na lokalnoj aplikaciji otvoriti Cases, izabrati primarni
slučaj i pokrenuti istragu. U worker terminalu sa istom konfiguracijom:

```powershell
uv run --locked python -m fraudlens.investigation.cli worker --store $env:INVESTIGATION_STORE --once
```

Očekivano je da se status ažurira, izabrani slučaj i snapshot ostanu isti,
citirani odlomak može da se otvori, a odluka sa obrazloženjem može da se ponovo
učita posle osvežavanja. Posebno proveriti prikaže li drugi slučaj
nedostupnu istoriju i potrebu za dopunom prema zamrznutom ulazu.

## 3. Pre i posle na istim ulazima

1. Zamrznuti paket, manifest i budžet. Pripremiti po jedan izolovan ekvivalent početnog stanja za obe faze.
2. Izvršiti baseline po EV matrici. Čuvati primarne ishode i prateće tragove, pa ih offline oceniti.
3. Izabrati jednu izmenu iz stvarnog traga. Za promene ponašanja pokrenuti RED, implementirati ciljanu izmenu i pokrenuti GREEN i regresiju.
4. Zamrznuti završnu reviziju, pokrenuti istu matricu i browser prolaz. Porediti po identičnom ulazu i rubrici. Zadržati blokirane, neizvršene i neuspešne redove.
5. Objaviti pročišćene dokaze i mapu. Nezavisni član ponavlja završno pokretanje bez korišćenja radnog store-a autora.

Za lokalnu regresiju uz nove ciljane provere koristiti postojeći setup:

```powershell
uv run --locked python -m pytest backend/tests
uv run --locked ruff check backend
npm.cmd --prefix web run test -- --run
npm.cmd --prefix web run build
git diff --check
```

Puna backend provera je istorijski imala nedostajuće artefakte i otvorene
provere van ove integracije. Zabeležiti tačne rezultate na završnoj reviziji,
razlikovati stvarne regresije, nedostupne preduslove i neuspešne testove.

## 4. Mapa predaje

| Stavka | Dokaz sa završne revizije |
| --- | --- |
| CAP-01 | Specifikacija, plan, ugovor i tačan glavni tok. |
| CAP-02 | Browser dokaz, poreklo skora i stvarni model. |
| CAP-03 | Otvoren izvor, vernost citata i slučaj bez dovoljno dokaza. |
| CAP-04 | Trag determinističkog alata, stanja i sačuvana odluka. |
| CAP-05 | Šesnaest uparenih rezultata i obrazložena izmena. |
| CAP-06 | Šest izvršenih negativnih provera i njihove kontrole. |
| CAP-07 | Oznaka revizije, komande i potvrda drugog člana iz čistog checkouta. |
| CAP-08 | Četiri tehnička doprinosa, odluke, provere i pregledi rada kolega. |

Za demo pripremiti uspešan prolaz, dopunu zbog nedovoljno dokaza i kontrolisanu grešku.
