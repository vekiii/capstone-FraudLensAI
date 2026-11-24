# Feature 06 · T012 · Zamrzavanje EV paketa

22. novembar 2026, Europe/Belgrade. Grana `006-capstone-evaluation`.
Rad je počeo sa čistog `d78febd`. Spec Kit prerequisites exit 0 i checklist
zahteva 14/14. Python 3.14.7, Node 24.20.0, npm 11.19.0. [Nalog, budžet i pregled](../../prompts/development/006-capstone-phase-04.md).

| Preduslov | Stvarni nalaz |
| --- | --- |
| T007–T008 | Pregledani browser dokazi vezanog skora, validnog nacrta, citata, obnovljive odluke i izdvojenog slučaja bez istorije. T008 je imao 9 potvrđenih pripremnih zahteva, odvojeno od ovog budžeta. [T007](feature-006-dataset-smoke.md) · [T008](feature-006-live-preflight.md). |
| T009 | Ponovljena provera sva tri transfer digesta i kompatibilnog indeksa od 5.078.345 redova. Cases i investigation identitet oba slučaja su se poklopili. [T098](feature-006-t098-inputs.md). |
| T010–T011 | Ponovljene ciljane investigation i Capstone provere daju 64 backend i 21 web prolaz. Verifikovani su svi 16-redni ulazi i odvojena rubrika, EV-06 veza i kontrolisane negativne provere. [Priprema](feature-006-ev-preparation.md). |
| EV-01 i EV-04 seed | Primarna transakcija `D4e050598f0f526f6fe690bb4874e2ee5`, objavljeni skor 0.9944662676905943, istorija dostupna za obe strane sa 40 odnosno 36 podobnih događaja. |
| EV-08 seed | Objavljeni slučaj i skorovani store ostaju vezani. Izostavljen je indeks, izvor istorije je odsutan, status `unavailable`, oba podobna broja su `null`. Context revision `c9db364c4315ead10d9b06a690e4cf57c53df6c6eab645af04122fda50e156b9`. |
| EV-10 seed | Milan je potvrdio pregled tačnog novog reda. Standardni loader je objavio izolovani corpus `corpus_82c0f43fb55e1957f8aebdd0bc605f300d19d2f86653f3d4906818b3253dbe8d` sa izmenjenim odlomkom `ee369f98576c3de0ee9c8b6b86a22ee75a8c1aedb6465f9a6311fb78ee50ad28`. |
| Model i limiti | Potvrđeno prisustvo serverskog ključa bez ispisivanja vrednosti. Sedam semantičkih payload provera lokalno je dalo 8.265–8.437 bajtova. Kompletan nastavak worker-a posle stvarnih odgovora i upotrebe alata meri se u primarnom prolazu. |

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:PYTHONPATH = 'backend/src'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
.venv/Scripts/python.exe evidence/tasks/feature-006-t098-local-check.py
$tests = @(rg --files backend/tests/integration | rg 'test_(investigation_|capstone_negative)')
.venv/Scripts/python.exe -m pytest -q @tests backend/tests/unit/test_capstone_execution.py --basetemp ".cache/006-readiness-$([guid]::NewGuid())" --tb=short
npm.cmd --prefix web run test -- --run tests/investigation-reports.test.ts tests/investigation-dataset-binding.test.tsx tests/investigation-knowledge.test.ts
.venv/Scripts/python.exe .cache/006-capstone-freeze.py
.venv/Scripts/python.exe -m ruff check evals/capstone/run.py
node --check evals/capstone/browser.ts
git diff --check
```

U ovoj pripremi je bilo nula modelskih poziva. Paket je zamrznut pre
primarnog dispatcha. Odabrani plafon je 19 zahteva po fazi, ukupno do 38.
Tačan testirani SHA i hash-vezano lokalno odobrenje ulaze u zapis svake faze.
[Manifest](../../evals/capstone/manifest.json) · [Protokol](../../evals/capstone/protocol.md).
