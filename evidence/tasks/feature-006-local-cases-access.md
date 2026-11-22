# Feature 06 · Provera pristupa Cases u lokalnom demou

22. novembar 2026, Europe/Belgrade. Rad je počeo na čistoj grani
`006-capstone-evaluation` na `b92430ba76953bbc8232b2d26f68a007089dea83`.
[Zahtev](../../prompts/development/006-capstone-local-cases-access.md) ·
[Odluka](../../specs/006-capstone-evaluation/quickstart.md#3-proba-bez-naplate-kroz-api-vite-i-worker).

Prethodni test je očekivao odbijanje anonimnog zahteva, uz pozivanje na
Feature 05 T028. Lokalni ugovor dopušta čitanje Cases bez prijave, a T028
pokriva API za live upozorenja. Test sada koristi lokalnu adresu i sintetički
fixture i proverava HTTP 200 i prisustvo `CASE-001` u listi.

Komande su izvršene na Windows-u u postojećem `.venv` okruženju. Python
3.14.7, pytest 9.2.0, Ruff 0.17.4, FastAPI 0.162.4, Starlette 1.10.0, httpx
0.28.1 i httpx2 2.16.0. Za svaki pytest poziv korišćena je zasebna putanja
`$runPath` unutar `.cache/`, uz prazan `PYTEST_ADDOPTS` i
`SPECIFY_FEATURE_DIRECTORY=specs/006-capstone-evaluation`.

```powershell
& .venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_security_boundaries.py::test_case_listing_requires_an_authenticated_principal --basetemp $runPath
& .venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_security_boundaries.py backend/tests/integration/test_cases.py backend/tests/integration/test_dataset_api.py backend/tests/integration/test_investigation_dataset_binding.py backend/tests/unit/test_local_api.py --basetemp $runPath
& .venv/Scripts/python.exe -m ruff check backend
git diff --check
```

Prva komanda, pre izmene testa, završila je izlazom 1. Stari test je dobio
200 umesto očekivanog 401/403. Druga komanda, posle izmene, imala je **72
prošla testa** i izlaz 0. Ruff i `git diff --check` prošli su sa izlazom 0.

Test zahteva radi u procesu, bez pokretanja mrežnog servera. Postojeći test
pokretača zasebno potvrđuje vezivanje API-ja za `127.0.0.1`. Puna regresija,
browser i živo EV merenje nisu ponovljeni. Produkcioni kod je neizmenjen,
SC-002 ostaje otvoren. Izmene su ostavljene za korisnikov commit i push.
