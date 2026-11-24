# Feature 06 · T018 · Deterministički final

22. novembar 2026, Europe/Belgrade. Sve kontrole izvršene su na kandidatu
`d8acc2a335d95e2402f586006925949f4d9f7739` dok je radno stablo bilo čisto.
Backend **6/6**, exit 0. Web **11/11**, exit 0, uključujući named EV-13
kontrolu klijenta i prikaza. Nula HTTP zahteva pravom provideru.

| EV | Kontrola i potvrđeni rezultati |
| --- | --- |
| EV-11 | Bez `snapshot_ref` dobija se 422 `invalid_request`. Store ostaje bez istrage i rezervacije, worker idle. |
| EV-12 | Dva lokalna nevalidna nacrta. Jedna popravka sa isključenim alatima. `failed/output_invalid` bez objave. |
| EV-13 | Isti prethodno otvoreni citat je 404 `evidence_not_found` kad je arhivski dokaz nedostupan. Drugi originalni dokaz, nacrt i audit ostaju isti. Web uklanja prethodni tekst i prikazuje nedostupnost. |
| EV-14 | Nepoznati alat odbijen je pre rezervacije alata. `failed/context_unavailable` posle lokalnog odgovora, bez dokaza ili nacrta. |
| EV-15 | Dva `MockTransport` timeout-a uz jedan retry. `failed/provider_failure`, oba ishoda su nepoznata u simulaciji, `usage=null`, izveštaj nije objavljen. |
| EV-16 | Dozvoljeno čitanje istorije daje simulirani `OSError`. `failed/context_unavailable`, sačuvane činjenice i kontekst, bez dokaza istorije ili nacrta. |

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_capstone_negative.py --basetemp .cache/006-capstone-final-controls --junitxml evals/results/capstone/final/negative-controlled.xml --tb=short
npm.cmd --prefix web run test -- --run tests/investigation-reports.test.ts --reporter=json --outputFile=../evals/results/capstone/final/negative-web.json
```

Koristi se odvojeni `.cache` za fixture korpus i SQLite i ignorisani
`evals/results/capstone/final/` za rezultate.
