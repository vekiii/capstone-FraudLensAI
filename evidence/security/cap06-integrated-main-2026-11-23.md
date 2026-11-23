# CAP-06 · Završne provere integrisanog MVP-a

23. novembar 2026, Europe/Belgrade. Lokalni Capstone demo koristi sintetičke podatke i loopback. Provere su izvršene na Windowsu, sa Pythonom 3.14.3 i zavisnostima iz `uv.lock` i `web/package-lock.json`.

- Početni `main` je `156e25b`. Isidorin audit iz `0783ead` dao je 15 prolaza i jedan neuspeh. Zahtev za skor sa query parametrima stigao je do modelskog puta i vratio 503 umesto 422. Novi ciljani test sa običnim nepodržanim parametrom pao je na pozivu skladišta pre izmene.
- Testirani kandidat je `0151facb3ca46cfd99d8ee79f27d0292f819bc8b` na `fix/cap06-final-verification`. API vraća 422 `invalid_request` pre čitanja skladišta ili skoringa, po istom obrascu kao rezultati modela i EDA. Zahtevi bez query parametara prolaze postojeće regresione provere. Model i prag nisu ponovo računati, a sve CAP-06 provere koriste lokalne test dvojnike i simulirane kvarove.

| Provera na kandidatu | Ishod |
| --- | --- |
| Isidorin audit | 16/16 |
| CAP-06 EV-11–EV-16 | 6/6. Nevalidan ulaz i izlaz, nedostupan citat, nedozvoljen alat, simulirani timeout i greška čitanja istorije. |
| API skora, ugovori skora i investigation API | 17/17 |
| React/Vitest, svih 19 fajlova | 290/290 |
| TypeScript, Vite build, ciljani Ruff i `git diff --check` | Prošli. Vite je prijavio upozorenje za veličinu jednog paketa. |

Prvi pokušaj kombinovanog izvršavanja imao je šest grešaka pri postavci, jer testovi iz ignorisanog direktorijuma nisu automatski učitali `knowledge_factory`. Nakon eksplicitnog učitavanja istog `backend/tests/conftest.py`, svih 22 audit i CAP-06 testa prošlo je na čistom kandidatu. Nije bilo poziva stvarnom provideru. Puna backend regresija i novi živi demo nisu izvršeni u ovoj proveri.

## Reprodukcija

Iz korena izdvojenog checkout-a kandidata, nakon `uv sync --locked --group investigation` i `npm.cmd --prefix web ci`:

```powershell
$h = '.cache/checks'
New-Item -ItemType Directory -Force "$h/backend/tests/integration","$h/evals/capstone/inputs" | Out-Null
git show 0783ead:backend/tests/integration/test_security_audit.py | Set-Content -Encoding utf8 "$h/backend/tests/integration/test_security_audit.py"
git show 3eee1d6:backend/tests/integration/test_capstone_negative.py | Set-Content -Encoding utf8 "$h/backend/tests/integration/test_capstone_negative.py"
git show 3eee1d6:evals/capstone/inputs/cases.json | Set-Content -Encoding utf8 "$h/evals/capstone/inputs/cases.json"
$env:PYTHONPATH = 'backend/src;backend/tests;backend/tests/integration'
.venv/Scripts/python.exe -m pytest -q -p conftest "$h/backend/tests/integration" --basetemp .cache/cap06-pinned-audit
.venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_risk_api.py backend/tests/contracts/test_risk_contracts.py backend/tests/integration/test_investigation_api.py --basetemp .cache/cap06-pinned-regression
npm.cmd --prefix web run test -- --run
npm.cmd --prefix web run build
```

Ovaj zapis potvrđuje CAP-06 proveru na integrisanom kandidatu. Konačna verzija za predaju treba da sadrži ovu popravku, a ako se njen izvršni kod promeni, povezati dokaz sa ponovljenom proverom.
