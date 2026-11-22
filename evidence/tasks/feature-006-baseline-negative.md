# Feature 06 · T014 · Deterministički baseline

22. novembar 2026, Europe/Belgrade. Testirani SHA
`5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`, odvojeni test store-ovi.
Primarna kontrola 6/6, exit 0. Browser klijent/kontroler: 11/11, uključujući
poseban EV-13 test. Nijedan poziv nije otišao pravom provideru.

| EV | Opažena kontrola | Lokalne rezervacije |
| --- | --- | ---: |
| EV-11 | Izostavljen je `snapshot_ref`. HTTP 422 `invalid_request`, nula upisa i provider nije konstruisan. | 0 |
| EV-12 | Dva nevalidna scripted izlaza, jedna popravka sa isključenim alatima, `failed/output_invalid` i bez izveštaja. | 2 |
| EV-13 | Originalni citat je pre kvara otvoren; zatim 404 `evidence_not_found` za istu referencu. Drugi dokaz, nacrt i audit ostali isti. Web je uklonio prikaz ranijeg teksta i prijavio nedostupnost. | 4 |
| EV-14 | Nepoznat naziv alata odbijen pre rezervacije alata. `failed/context_unavailable`, bez dokaza ili izveštaja. | 1 |
| EV-15 | `MockTransport` je proizveo dva timeout-a i jedan dozvoljen retry. `failed/provider_failure`, oba ishoda nepoznata sa `usage=null`. | 2 |
| EV-16 | Dozvoljeni alat za istoriju dobio je `OSError`. `failed/context_unavailable`, sačuvani kontekst i tačne činjenice, bez dokaza istorije i izveštaja. | 2 |

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_capstone_negative.py --basetemp .cache/006-capstone-baseline-controls --junitxml evals/results/capstone/baseline/negative-controlled.xml --tb=short
npm.cmd --prefix web run test -- --run tests/investigation-reports.test.ts --reporter=json --outputFile=../evals/results/capstone/baseline/negative-web.json
```

Prvobitna komanda iz zamrznutog protokola koristila je `--basetemp` pod
`evals/`, gde aplikativni loader odbija lokalni fixture korpus. Šest
setup grešaka je sačuvano u `baseline/negative.xml`. Isti testovi i isti
SHA zatim su izvršeni sa `.cache/` stanjem iz gornje komande. Potrošnja je
proverena i kroz izolate testova, ukupno 11 lokalnih rezervacija.
