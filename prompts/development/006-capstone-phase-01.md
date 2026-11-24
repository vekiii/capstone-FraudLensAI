Implementiraj fazu 1 — Setup, isključivo T001, za feature `specs/006-capstone-evaluation`. Nemoj samo predložiti plan ili generisati novi prompt. Stani pre T002.

FraudLens AI koristi FastAPI/Python i jednu React/TypeScript/Vite aplikaciju u `web/`. Ova faza proverava zaključani setup i postojeći Cases/investigation tok kroz automatizovane provere. Ne implementira dataset binding, provider setup ili evaluaciju.

Sve putanje su relativne u odnosu na koren projekta. Oslanjaj se na aktuelni checkout, bez prethodnih razgovora.

## 1. Obavezna priprema

Pročitaj primenljive `AGENTS.md` instrukcije, zatim odmah root `next_work.md`, pre planiranja i rada. Ponovi pri nastavku sesije. Aktuelni zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/006-capstone-evaluation/{tasks.md,spec.md,plan.md,quickstart.md}`
- `evidence/tasks/feature-006-task-generation.md`
- `evidence/tasks/feature-006-technical-plan.md`
- relevantne setup/test delove `README.md`
- `pyproject.toml`, `.python-version`, `uv.lock`
- `web/package.json`, `web/package-lock.json`, Vite/Vitest konfiguraciju
- postojeće ciljane testove navedene ispod
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md` i ignore pravila.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` samo za T001. Eksplicitan opseg ima prednost nad opštim zahtevom da se izvrši ceo tasks.md. Poštuj stvarne checklist/hook zahteve; ne menjaj oznake radi prolaska. Ne traži ponovno odobrenje rutinskih već autorizovanih koraka.

U PowerShell sesiji postavi:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
```
To bira feature, ne menja Git granu.

Read-only pregled pri generisanju ovog prompta pokazao je granu `006-capstone-evaluation`, prazan `git status --short` i neoznačen T001. Postojeće evidence navodi da setup grane još ne uključuje live SDK i da je puna backend regresija istorijski imala padove. To nisu sveže izvršene aplikacione provere.

Proveri stvarnu granu, HEAD i radno stablo. Radi na postojećoj grani `006-capstone-evaluation`; ako checkout ne odgovara, prijavi neslaganje bez automatskog prebacivanja. Sačuvaj sve postojeće izmene. Bez pull-a, merge-a, reset/clean/stash ili stvaranja „čistog” checkout-a brisanjem rada.

## 2. T001 — zaključani setup i početne provere

Tačan zahtev:
Izabrati Feature 006, izvršiti zaključani setup iz quickstart-a i snimiti granu, reviziju, verzije i početne ciljane Cases/investigation i React provere u:
`evidence/tasks/feature-006-setup.md`

Svaki postojeći pad opisati stvarno izvršenom komandom.

Iz korena projekta:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix web ci
```

Koristi postojeće Python 3.14 i Node 24 zahteve. Zabeleži stvarne verzije projektnog Python interpretera, uv, Node-a i npm-a; razlikuj projektni od sistemskog interpretera.

Ne pokreći `uv lock`, upgrade ili nezaključanu instalaciju radi rutinskog setup-a. Obnova provider zavisnosti i generisanje `uv.lock` pripadaju T003, ne ovom tasku. Ako nedostajuća zavisnost blokira proveru, zabeleži to bez prećutnog proširenja opsega.

## 3. Konkretna početna regresija

Nakon pregleda testova pokreni postojeće backend granice:
```powershell
uv run --locked python -m pytest backend/tests/integration/test_startup.py backend/tests/integration/test_cases.py backend/tests/integration/test_investigation_api.py backend/tests/integration/test_investigation_knowledge_api.py backend/tests/integration/test_investigation_recovery_api.py backend/tests/integration/test_investigation_review_api.py
```

Pokreni ciljane React Cases/investigation provere:
```powershell
npm.cmd --prefix web run test -- --run tests/cases-page.test.tsx tests/investigation-knowledge.test.ts tests/investigation-reports.test.ts tests/investigation-recovery.test.ts tests/investigation-review.test.ts
npm.cmd --prefix web run typecheck
npm.cmd --prefix web run build
```

Koristi postojeće testove; ne kreiraj još nepostojeće T004/T005 dataset-binding testove.

Ovo su baseline/regresione provere. Za mehanički setup nema veštačkog RED-a. Ne kvari postojeće ponašanje, ne dodaj skip/xfail i ne slabi assertions radi prolaza.

Za svaku komandu zabeleži:
- radni direktorijum i bezbedne sesijske postavke;
- stvarni exit kod;
- broj izvršenih/prolaznih/neuspešnih testova;
- konkretne failing node ID-jeve i sažet razlog;
- razliku između pada ponašanja, import/collection greške, nedostupnog artefakta i environment problema;
- stvarna build/typecheck upozorenja.

„Nema testova” nije uspeh. Istorijski broj testova nije aktuelni rezultat. Ne tvrdi da je puna regresija prošla ako su pokrenuti samo ciljani moduli.

Za Windows temp/cache ograničenja koristi jedinstvene apsolutne putanje pod ignorisanim root `.cache`, uz `--basetemp` i `-o cache_dir` po potrebi. Ako testovi zahtevaju konfiguraciju, koristi kontrolisani test režim i izolovane lokalne putanje. Ne učitavaj stvarni `.env` ili ključeve radi baseline-a i ne dozvoli provider pozive.

Ne popravljaj postojeće produktne padove u ovom tasku. Dijagnostikuj dovoljno da ostaviš upotrebljiv nalaz i odgovarajući naredni korak. Završi nezavisne provere čak i kada jedna komanda padne.

## 4. Granice ove faze

Ne izvršavaj ostale quickstart korake:
- nema T098 digest/source/index inspekcije iz T002;
- nema provider dependency popravke iz T003;
- nema dataset binding implementacije;
- nema ingest-a, API/worker/browser demo-a ili model probe-a;
- nema plaćenih poziva, EV freeze-a, baseline/final merenja ili ocenjivanja.

Ne učitavaj evaluation reference ili postojeći held-out paket radi setup-a.

Sačuvaj postojeće Cases/investigation ugovore i aplikacioni kod. Koristi jedinu React aplikaciju u `web/`; ne kreiraj drugi frontend ili JavaScript aplikacioni kod.

Čist checkout i reprodukcija drugog člana pripadaju kasnijim taskovima. Sopstveni setup ne predstavljaj kao peer reproduction, ljudski review ili CAP prihvatanje.

## 5. Trag rada i uslov završetka

Pre setup izmena sačuvaj tačan primljeni prompt u:
`prompts/development/006-capstone-phase-01.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune.

Vodi:
- detaljan evidence: `evidence/tasks/feature-006-setup.md`
- kratak handoff: `evidence/tasks/feature-006-phase-01-handoff.md`

Zabeleži početni commit, granu, postojeće izmene, verzije, locked instalacije, sve ciljane rezultate, blokade i neizvršene provere. Posebno označi već postojeće padove; ne pripisuj ih novoj implementaciji.

T001 je baseline task: završetak znači uspešno pripremljen locked setup i stvarno izvršene, dokumentovane ciljane provere. Postojeći pad ne skrivaj i ne predstavljaj kao PASS; task može dokumentovati završen baseline sa padovima, ali ne ako potrebne provere ostanu neizvršene zbog blokade. U tom slučaju ostavi ga delimičnim uz razlog.

Posle koherentne celine ažuriraj `next_work.md` stvarnim stanjem, evidence linkovima, blokadama/neizvršenim proverama i jednim konkretnim narednim korakom. Označi samo T001 kada njegov zahtev zaista bude ispunjen. Ne menjaj status drugih taskova.

Pregledaj diff i nove fajlove, potvrdi da aplikacioni kod, dependency konfiguracije i lockfile-ovi nisu nenamerno promenjeni i izvrši:
```powershell
git diff --check
```

Bez subagenata osim ako ih primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

Završni odgovor neka kratko navede status T001, locked setup rezultate, stvarne ciljane test/typecheck/build ishode, otvorene padove/blokade i handoff putanju. Sledeći korak je zasebna faza 2, T002–T003, ili konkretan nedovršen preduslov T001.

Ne započinji T002.