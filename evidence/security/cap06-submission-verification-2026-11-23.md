# CAP-06 na integrisanom kandidatu za predaju

23. novembar 2026, Windows. Testirani čist checkout `55444ce13d8f9ef03705ab8f0ae34a2c3a38cd02` polazi od `main` revizije `c297ceb`. Na toj osnovi je već uključen PR #6 sa odbijanjem nepodržanih query parametara pre skoringa. Diff između `c297ceb` i testiranog SHA dodaje backend test i dopunjuje web test. Koriste se isti izvršni kod, zaključane zavisnosti, model i budžetska pravila integrisanog demoa.

| Provera | Rezultat iz čistog checkout-a |
| --- | --- |
| EV-11–EV-16 | 6/6. Nevalidan zahtev, nevalidan nacrt, nedostupan citat, nedozvoljen naziv alata, simulirani timeout i greška čitanja istorije. |
| Budžetski prekid | 1/1. Sintetički kontekst prolazi validaciju, ali je ceo zahtev sa šemom i instrukcijama veći od limita. Stvarni serverski adapter završava pokušaj kao `failed / budget_exhausted` pre ulaska u mock transport. Nema izveštaja, ponovnog pokušaja ili dodatnog rada pri narednom prolazu worker-a. Jedna lokalna rezervacija, nula poslatih zahteva. |
| Ostale ciljane backend provere | 49/49. Skor, API istrage, ugovori, OpenAI adapter i popravka izlaza. Ukupno sa gornja dva reda 56/56. |
| Isidorin audit iz `0783ead` | 16/16, uključujući odbijanje query parametara pre pristupa modelu. |
| Frontend | 291/291. Dodatna provera potvrđuje da ponovno otvaranje budžetskog prekida prikazuje grešku, bez nacrta, automatskog pokretanja ili retry-ja. |
| Serverski ključ i build | TypeScript i Vite prošli. U izlazu `web/dist` nema sintetičkog markera postavljenog samo kroz serversku promenljivu `OPENAI_API_KEY`. Test budžeta proverava i da sintetička vrednost ključa i sirovi kontekst ostaju van HTTP odgovora. |
| Ruff i provera diffa | Prošli. Vite je prijavio upozorenje za veličinu paketa. |

Sve kontrole su offline. Za `--basetemp` prvo je trebalo napraviti roditeljski `.cache` direktorijum. Nakon toga su sve navedene provere izvršene. Puna backend regresija i novi živi browser demo nisu deo ovog zapisa.

## Reprodukcija iz checkout-a kandidata

```powershell
uv sync --locked --group investigation
npm.cmd --prefix web ci --no-audit --no-fund
New-Item -ItemType Directory -Force .cache/audit | Out-Null
.venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_capstone_negative.py backend/tests/integration/test_risk_api.py backend/tests/integration/test_investigation_api.py backend/tests/contracts/test_risk_contracts.py backend/tests/unit/test_investigation_openai.py backend/tests/unit/test_investigation_repair_v5.py --basetemp .cache/cap06-backend-temp
git show 0783ead:backend/tests/integration/test_security_audit.py | Set-Content -Encoding utf8 .cache/audit/test_security_audit.py
$env:PYTHONPATH = 'backend/src;backend/tests'
.venv/Scripts/python.exe -m pytest -q -p conftest .cache/audit/test_security_audit.py --basetemp .cache/cap06-audit-temp
.venv/Scripts/ruff.exe check backend/tests/integration/test_capstone_negative.py
npm.cmd --prefix web run test -- --run
$env:OPENAI_API_KEY = 'synthetic-server-only-cap06-build-marker'
npm.cmd --prefix web run build
rg --text -l -F $env:OPENAI_API_KEY web/dist
# Očekivano za rg: exit 1, bez poklapanja.
Remove-Item Env:OPENAI_API_KEY
```

Pokrenuti provere u zasebnom terminalu bez učitanog stvarnog API ključa. Audit je dostupan iz postojeće Git istorije, a sedam kontrola je u testovima kandidata i ne zavisi od audit grane.

## Živi dokaz za isti SHA predaje

Prethodno [živo Windows merenje](../tasks/pr3-live-demo-2026-11-23.md) izvršeno je na `747ff97`. Uključuje kompaktan prolaz sa proceduralnim citatima i sačuvanom odlukom i duži slučaj sa kontrolisanim prekidom. Kada tim odabere SHA predaje sa CAP-06 popravkom, ponoviti kompaktan slučaj i kontrolisani prekid na tom SHA. Sačuvati stanje, broj stvarnih slanja, ishod čitanja odluke i pročišćeni trag. [Windows quickstart](../../specs/003-ai-investigation/quickstart.md#pr-3-demo-with-the-real-openai-provider-on-windows).
