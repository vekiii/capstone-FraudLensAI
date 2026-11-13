Implementiraj, nemoj samo predložiti plan ili generisati novi prompt.

Implementiraj isključivo fazu 3 — US1: Reproduce the Shared Environment (P1), taskove T008–T011, za feature `specs/001-project-foundation`. Radi redom T008 → T009 → T010 → T011 i stani pre T012.

FraudLens AI je Bootcamp AML prototip. Foundation je lokalna demonstracija sa sintetičkim podacima, FastAPI backend-om i vanilla TypeScript/Vite frontend-om. Ne zahteva ML trening, RAG korpus, stvarni dataset ili LLM ključ. Koristi checkout kao izvor konteksta, bez oslanjanja na prethodne razgovore. Putanje su relativne u odnosu na koren projekta.

## 1. Obavezno čitanje i početna provera

Odmah nakon primenljivih `AGENTS.md` instrukcija pročitaj root `next_work.md`, pre planiranja i implementacije. Ponovi to pri nastavku prekinute sesije. Ovaj zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/001-project-foundation/{tasks.md,spec.md,plan.md}`
- relevantne delove `specs/001-project-foundation/{research.md,data-model.md,quickstart.md}`
- `specs/001-project-foundation/contracts/{api.md,schemas.json}`, posebno Health i Error
- `evidence/tasks/phase-02-handoff.md` i `evidence/tasks/T006.md`, naročito završne zapise koji zamenjuju ranije delimične statuse
- `evidence/tasks/phase-01-handoff.md`, posebno završni runtime amendment
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md`
- `docs/decisions/foundation.md`, `frontend/README.md`
- postojeći backend kod i testove, `pyproject.toml`, `.python-version`, `uv.lock`
- `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.ts` i postojeći scaffold.
Za širi odobreni kontekst koristi `original_idea.md` po potrebi.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` isključivo za T008–T011. Ovaj eksplicitan opseg ima prednost nad opštim zahtevom skill-a da završi ceo tasks.md. Poštuj stvarne checklist/hook zahteve; ne menjaj oznake radi prolaska. Ako zahtevaju odluku koja nije već odobrena, objasni tačan izvor i razlog. Ne traži dodatne potvrde za odobrene rutinske korake.

Za Spec-kit eksplicitno izaberi feature za ovu PowerShell sesiju:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/001-project-foundation'
```
Ovo ne menja Git granu.

Read-only pregled pri generisanju prompta pokazao je:
- granu `initialization` i prazan `git status --short`;
- T001–T007 označene završenim, T008–T011 neoznačene;
- implementirane stroge Pydantic ugovore i ugovorne testove;
- završni evidence faze 2 navodi 93 prolazna testa, Ruff i diff proveru, bez ponovnog izvršavanja u razgovoru koji je generisao ovaj prompt;
- nema startup implementacije; frontend je setup scaffold bez behavior testova;
- ljudski pregled i peer reprodukcija/SC-001 ostaju pending.

Ponovo proveri stanje. Sačuvaj postojeću radnu granu, originalno `initialization`, i sve tuđe izmene. Ne radi automatski pull, promenu grane, reset, clean ili stash. Prljavo radno stablo samo po sebi nije blokada.

## 2. Tačni taskovi

**T008 [US1] — FR-001/FR-002**

Napiši i izvrši RED testove u:
`backend/tests/integration/test_startup.py`

Pokrij:
- health status i mode;
- podrazumevana fixture podešavanja;
- pokretanje bez ključeva, modela i korpusa;
- odbacivanje nepodržanog `APP_MODE`;
- dokaz da startup ne poziva provider.

**T009 [US1] — FR-002**

Implementiraj:
- `backend/src/fraudlens/main.py`
- `backend/src/fraudlens/settings.py`

Obezbedi application factory, dependency injection point, lokalna fixture podešavanja i `GET /api/health`. Zadovolji T008 i zabeleži GREEN u:
`evidence/tasks/T008.md`

**T010 [US1] — FR-001**

Dodaj tačna uputstva za preduslove, setup, pokretanje, provere i build u root `README.md`, usklađena sa:
`specs/001-project-foundation/quickstart.md`

Razlikuj:
- prvo generisanje lockfile-ova od instalacije postojećih zaključanih zavisnosti;
- preuzimanja tokom instalacije od runtime-a koji ne zahteva spoljne servise.

**T011 [US1] — doprinos SC-001**

Izvrši dokumentovane automatizovane provere, build i health smoke. Zabeleži stvarne verzije i rezultate u:
`evidence/tasks/T011.md`

Peer reprodukciju označi pending osim ako je drugi član zaista sam izvršio postupak. Sopstveni setup nije dokaz SC-001.

## 3. Ponašanje i TDD

Pre produkcione implementacije napiši i pokreni smislene RED testove, zabeleži stvarni razlog pada, implementiraj najmanju potrebnu promenu, zatim izvrši GREEN i relevantnu regresiju. Pad zbog neispravnog okruženja nije odgovarajući RED. Već ispravno ponašanje proveri bez namernog kvarenja. Mehanička dokumentacija ne zahteva veštački RED.

Za T008/T009:
- `GET /api/health` vraća HTTP 200 i tačno `{"status":"ok","mode":"fixture"}`, kao `application/json`, u skladu sa postojećim Health ugovorom.
- Podrazumevani i jedini podržani `APP_MODE` je `fixture`. Nepodržana vrednost se jasno odbacuje; nema tihog vraćanja na fixture niti uspešnog health-a za nevalidnu konfiguraciju.
- Testiraj stvarno čitanje okruženja uz izolaciju promenljivih, a ne samo direktno kreiranje settings objekta. Ne beleži postojeće tajne.
- Nedostajući provider ključevi, model i korpus ne blokiraju kreiranje aplikacije, startup ili health.
- Obezbedi test koji bi detektovao neželjeni spoljni poziv tokom startup-a, uz dozvoljen lokalni TestClient transport. Ne dodaj provider SDK ili lažnu produkcionu integraciju radi testa.
- Pokreni lifecycle u integracionim testovima; sam import modula nije dokaz startup ponašanja.
- Factory i dependency injection point treba da budu mali i stvarno upotrebljivi za konfiguraciju/testiranje. Ne implementiraj budući scorer ili case servis.
- Lokalnu fixture putanju rešavaj bez hardkodovanog korisničkog ili apsolutnog Windows puta. Fajl `data/fixtures/cases.json` pripada T014: njegovo odsustvo sada ne sme onemogućiti startup/health. Ne kreiraj slučajeve unapred.
- Koristi postojeće ugovore i plan. Ako implementiraš obradu grešaka relevantnu za ovu granicu, prati generički Error envelope bez traceback-a, putanja i tajni; puna case 404/422/500 normalizacija pripada T016.
- Obezbedi `fraudlens.main:app` da dokumentovana Uvicorn komanda radi.

Ne implementiraj `/api/cases`, fixture scoring, case UI, frontend boundary decoder ili testove budućeg korisničkog toka. Ne uvodi bazu, ML, RAG, LLM, CI, kontejnere ili deployment.

Sačuvaj faza-2 ugovore, uključujući odobrenu korekciju završnih regex sidara i postojeće negativne testove. Suštinske kontradikcije prijavi; ne menjaj ugovore ili očekivanja da bi provere prošle.

## 4. Onboarding i stvarne provere

Proveri preduslove faza 1–2 pre koda. Koristi usvojene Python 3.14 i Node 24, postojeće konfiguracije i lockfile-ove. Zabeleži stvarne patch verzije i verzije alata, bez pretpostavljanja da su jednake ranijim zapisima.

Za instalaciju postojećeg checkout-a:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix frontend ci
```

Workspace-local uv cache koristi ako je potreban zbog pristupa podrazumevanom cache-u. Na PowerShell-u koristi `npm.cmd` ako `npm.ps1` blokira execution policy; ne menjaj trajnu politiku sistema.

Ne regeneriši ili nadograđuj zavisnosti rutinski. Ako je promena zavisnosti neophodna za odobreni opseg, obrazloži je i generiši lockfile stvarnim alatom; nikada ručno ne izmišljaj verzije ili hash-eve.

U `README.md` navedi komande iz korena projekta:
```powershell
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Objasni dva terminala, loopback granicu, Vite `/api` proxy i health proveru. Aplikacija se ne opisuje kao bezbedan višekorisnički ili ML-ready sistem.

Quickstart opisuje i budući kompletan tok sa tri slučaja. README mora jasno pokazati šta je ostvarivo posle faze 3: startup, health i postojeći frontend scaffold. Kasniji case tok i browser acceptance označi kao buduće provere; ne tvrdi da već rade i ne implementiraj ih radi usklađivanja dokumentacije.

Izvrši:
```powershell
uv run --locked pytest backend/tests/integration/test_startup.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
git diff --check
```

Ciljani startup pytest pokreni za RED pre implementacije, potom za GREEN. Puna backend regresija uključuje postojeće ugovorne testove. Posle završnog editovanja ponovi pogođene provere.

Frontend behavior testovi još nisu implementirani. Ako Vitest prijavi „no test files”, zabeleži stvarni exit kod i odsustvo testova; to nije prolaz suite-a. Ne dodaj `passWithNoTests`, trivijalne testove ili fazu 4 da prikriješ taj očekivani nedostatak.

Za T011 stvarno pokreni backend dokumentovanom komandom i proveri:
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health'
```
Zabeleži status i telo odgovora, ne samo uspešan import ili TestClient test. Proveri dokumentovano pokretanje Vite scaffold-a i proxy health gde je ostvarivo. Ako koristiš background procese, pokreni ih skriveno i na kraju zaustavi samo procese koje si sam pokrenuo; ne prekidaj tuđe servise.

Jasno razdvoji dokaz rada bez ključeva/modela/korpusa i bez spoljnih runtime poziva od tvrdnje da si testirao fizički isključenu mrežu. Ne tvrdi ono što nisi proverio.

Popravi greške unutar ovog opsega. Ako nedostaje stvaran blokirajući preduslov van njega, sačuvaj nalaz, završi nezavisan rad i traži odluku o proširenju. Ne radi beskonačne retry petlje ili novu infrastrukturu radi instalacionog kvara.

## 5. Originalni prompt, evidence i handoff

Pre implementacionih izmena sačuvaj originalni primljeni prompt u:
`prompts/development/001-foundation-phase-03.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune. Bez tajni. Ovo ne završava T023.

Koristi postojeće evidence konvencije:
- `evidence/tasks/T008.md`: stvarni T008 RED i T009 GREEN, regresija, veze ka zahtevima i originalnom promptu.
- `evidence/tasks/T011.md`: izvršene setup/check/build/smoke komande, verzije, exit kodovi i opaženi rezultati, ograničenja i pending peer reprodukcija.
- `evidence/tasks/phase-03-handoff.md`: grana/početni commit, završeni i delimični taskovi, menjani fajlovi, komande/ishodi, blokade i konkretan sledeći korak.
- `specs/001-project-foundation/tasks.md`: označi samo stvarno implementirane i proverene T008–T011. Delimični ili blokirani task ostaje neoznačen uz opis. Uskladi kratak status, bez menjanja drugih faza.
- `next_work.md`: stvarno stanje, evidence linkovi, blokade/neizvršene provere i jedan konkretan naredni korak.

Handoff i `next_work.md` osvežavaj posle završenog taska ili koherentne celine, uključujući delimičnu predaju. Detaljna istorija ostaje u evidence-u.

Za svaki rezultat razlikuj uspeh, pad, nije pokrenuto, blokirano i nema testova. Zabeleži početni commit/diff, stvarne runtime/dependency verzije i status ljudskog pregleda. Ne izmišljaj review ili reprodukciju drugog člana. T025/SC-001 ostaju pending do stvarnog nezavisnog izvršavanja; T011 može dokumentovati završene provere ove faze uz jasno naveden pending SC-001.

## 6. Granice i završetak

Dozvoljeni su ciljni testovi, `main.py`, `settings.py`, root `README.md` i usko povezani nužni config/prompt/evidence/status fajlovi. Ovo nije dozvola za preuređenje repozitorijuma ili regenerisanje specifikacija.

Sačuvaj `original_idea.md`, constitution, ugovore, ignore pravila i deljeni `.agents`/`.specify` sadržaj. Ne menjaj checklist markere radi prolaska. Ne uvodi tehnike van odobrenog obima i ne pokreći subagente osim ako ih korisnik ili primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

Faza je završena kada startup/health testovi i backend regresija prolaze, onboarding odgovara stvarnom stanju, dokumentovane provere i smoke imaju stvarne zabeležene ishode, a task status i handoff im odgovaraju. Odsustvo budućih frontend testova evidentiraj kao ograničenje, bez predstavljanja kao uspeh.

Završni odgovor neka kratko navede:
- završene, delimične i nepočete taskove;
- promene i stvarne RED/GREEN, regresione, build i smoke rezultate;
- neizvršene provere i razloge, uključujući pending ljudski pregled/SC-001;
- putanju `evidence/tasks/phase-03-handoff.md`;
- prvi sledeći korak: zasebno pokretanje faze 4, T012–T019, nakon završene faze 3.

Ne započinji fazu 4.