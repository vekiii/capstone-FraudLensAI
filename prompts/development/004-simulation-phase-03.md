Implementiraj izabrani deo faze 3 — US1: Compare review strategies, isključivo taskove T005–T007, za `specs/004-simulation-and-prioritization`. Nemoj samo napisati plan ili novi prompt.

Ovaj opseg obuhvata pisanje i izvršavanje RED testova. T008–T011 nisu odobreni: ne implementiraj replay, API ili UI da bi novi testovi prošli. Završetak T005–T007 ne znači završetak cele faze 3.

FraudLens AI je obrazovni AML prototip. Feature 004 poredi tri determinističke strategije pod jednakim kapacitetom, koristeći zamrznuti sintetički scenario. Sve putanje su relativne u odnosu na koren projekta; koristi aktuelni checkout, bez prethodnih razgovora.

## 1. Početno čitanje i provera

Pročitaj primenljive `AGENTS.md` instrukcije, zatim odmah root `next_work.md`, pre planiranja i rada, uključujući nastavak sesije. Aktuelni zahtev određuje opseg.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/004-simulation-and-prioritization/{tasks.md,spec.md,plan.md,research.md,data-model.md,quickstart.md}`
- `specs/004-simulation-and-prioritization/contracts/replay-v1.md`
- `evidence/tasks/feature-004-phase-02-handoff.md`
- `evidence/tasks/feature-004-phase-02-validation.md`
- postojeće `backend/src/fraudlens/simulation/{models.py,scenarios.py}`
- oba `data/fixtures/simulation/review-capacity-demo-v1*` fajla
- postojeće app factory, backend API testove i frontend test/client/lifecycle konvencije
- evidence/prompt konvencije, runtime konfiguracije i lockfile-ove.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` isključivo za T005–T007. Eksplicitan opseg ima prednost nad opštim zahtevom da se završi ceo tasks.md. Poštuj checklist/hook zahteve; ne menjaj oznake radi prolaska. Ne traži ponovno odobrenje odobrenih rutinskih koraka.

U PowerShell Spec-kit sesiji:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/004-simulation-and-prioritization'
```
Ovo ne menja Git granu.

Read-only pregled pri generisanju prompta pokazao je:
- granu `004-simulation-and-prioritization` i prazan `git status --short`;
- T001–T004 završene, T005–T007 neoznačene;
- implementirane scenario modele/katalog i odvojene facts/outcomes;
- faza-2 evidence navodi 56 contract testova, 8 startup i 366 punih backend testova PASS, Ruff/diff PASS;
- nema replay/API/UI implementacije.

Bundled fingerprint u evidence-u je:
`894136f422d013cf0d1d52820acf26e3a3a95076a4b8ab044c4e24faf4105198`

Ponovo proveri stanje i dokaz; ne predstavljaj ranije rezultate kao sveže izvršene. Sačuvaj granu i postojeće izmene. Bez automatskog pull-a, merge-a, promene grane ili reset/clean/stash.

## 2. Pravila ovog RED opsega

Radi sekvencijalno T005 → T006 → T007. `[P]` označava mogućnost nezavisnog rada, ne zahtev za subagentima.

Testovi moraju stvarno izvršiti assertions i pasti zbog očekivano nedostajućeg ponašanja. Import/collection/SyntaxError, nevalidna test fixture ili pokvareno okruženje nisu odgovarajući RED.

Za buduće nepostojeće replay/frontend module dozvoljena je samo minimalna importabilna granica, ako je neophodna za izvršavanje testova: bez algoritma, validacije, renderovanja, ruta ili hardkodovanih uspešnih rezultata. Takvu promenu eksplicitno evidentiraj. Ne koristi skip/xfail/importorskip da prikriješ odsustvo ponašanja.

Postojeće prolazne provere ostaju regresione; ne kvari ih radi RED-a. GREEN za novo ponašanje pripada T008–T010 i ostaje „nije izvršeno — van opsega“.

## 3. T005 — replay RED testovi

Putanja:
`backend/tests/unit/test_simulation_replay.py`

Zahtevi: FR-002–FR-004, FR-006, SC-001–SC-002.

Napiši i izvrši testove za:
- troalertni primer iz specifikacije;
- A–E primer iz quickstart-a;
- score jednak threshold-u;
- tačno poređenje weighted prioriteta, bez float grešaka;
- tie-break: availability instant, zatim ascending ID;
- alert dostupan tačno na window start-u;
- zabranu pregleda pre dostupnosti;
- exclusive horizon end;
- nezavisan reset budžeta u svakom prozoru;
- scanning preko alert-a koji ne staje u preostali budžet;
- carry-over;
- late arrivals u final backlog-u;
- svaki alert pregledan najviše jednom po strategiji;
- konkretne ranked/reviewed redoslede i used minutes.

Za A–E, threshold 0.30 i budget 2:
- FIFO pregledava A;
- highest score pregledava B;
- weighted score per minute pregledava C, E;
- D ostaje ispod threshold-a.

Za troalertni primer, threshold 0 i budget 2: FIFO A, highest score B, weighted C.

Replay input mora biti label-free. Ne prosleđuj OutcomeSet algoritmu i ne računaj očekivano sortiranje istom formulom/helper-om koji tek treba testirati. Koristi ručno proverljive očekivane rezultate.

Ne implementiraj `replay.py` ponašanje iz T008.

## 4. T006 — API RED testovi

Putanja:
`backend/tests/integration/test_simulation_api.py`

Zahtevi: FR-001, FR-005–FR-009.

Testiraj stvarni app factory i buduće rute:
- `GET /api/simulation/scenarios`
- `POST /api/simulation/comparisons`

Pokrij:
- catalog metadata i sortiranje po scenario ID/version;
- comparison oblik i redosled prema `contracts/replay-v1.md`;
- tačne defaults i canonical recipe echo;
- strategies redom FIFO, highest score, weighted score per minute;
- admitted alerts i pending redosled;
- tačne default outcome counts;
- odsustvo per-alert outcome/label polja;
- odsustvo Cases mutacija i očuvanje postojećih odgovora;
- strogo odbacivanje malformed input-a i nepoznate contract verzije: 422;
- nepostojeća scenario revizija, pogrešan digest ili nepodržana strategy verzija: 409 `simulation_version_unavailable`;
- sanitizovan service failure: 500 `internal_error`, bez putanja, outcome redova, traceback-a ili delimičnog comparison-a.

Default counts pri threshold-u 0.30 i budget-u 2:
- FIFO: found 0, missed threshold 1, missed backlog 2, reviewed negatives 1, backlog 3;
- highest score: found 1, missed threshold 1, missed backlog 1, reviewed negatives 0, backlog 3;
- weighted: found 1, missed threshold 1, missed backlog 1, reviewed negatives 1, backlog 2.

Koristi validan stvarni catalog digest ili kontrolisan privremeni katalog. Ne šalji caller-supplied labels/alerts/putanje umesto propisane recipe granice.

Ne mock-uj same HTTP odgovore koje proveravaš. Test-only dependency double sme kontrolisati katalog/service kvar, ali zahtev mora proći stvarnu aplikacionu granicu. Ne registruj uspešne simulation rute u testu umesto buduće produkcione implementacije.

Ne implementiraj rute, response modele ili app registration iz T009.

## 5. T007 — frontend RED testovi

Putanja:
`frontend/tests/simulation.test.ts`

Zahtevi: FR-001, FR-005, FR-008–FR-009.

Koristi fake simulation client sa jasno autorskim odgovorima usklađenim sa javnim ugovorom. Napiši i izvrši testove za:
- ulazak u Simulation & Evaluation prikaz;
- izbor scenarija;
- prikaz sintetičkog izvora, score provenance i pretpostavki;
- korišćenje catalog defaults za prvi comparison;
- prikaz tri default rezultata i njihovog redosleda;
- malformed catalog;
- malformed comparison odgovor;
- failed request;
- čitljivu grešku bez prikazanog comparison-a kada zahtev ili payload nije validan.

Poštuj postojeće Vitest/jsdom konvencije i odaberi minimalnu buduću testabilnu granicu za `frontend/src/simulation.ts`, dokumentovanu za T010. Ne uvodi okvir ili novu frontend arhitekturu.

Fake client ne sme obaviti validaciju umesto sistema koji testiraš. Ne renderuj očekivani UI u samom testu. Assertions treba da proveravaju stvarni budući view/client boundary, uz minimalnu importabilnu granicu samo ako je neophodna za izvršen RED.

Ne implementiraj frontend client/decoder/view ni main navigaciju iz T010. Kontrole promene budžeta/praga, recipe download/reopen i stale-result proširenja pripadaju kasnijim taskovima.

## 6. Izvršavanje i regresija

Koristi postojeće Python 3.14 / Node 24 konfiguracije i lockfile-ove. Zabeleži stvarne verzije. Po potrebi izvrši zaključanu instalaciju; ne nadograđuj zavisnosti ili regeneriši lockfile rutinski.

Pokreni:
```powershell
uv run --locked pytest backend/tests/unit/test_simulation_replay.py
uv run --locked pytest backend/tests/integration/test_simulation_api.py
npm.cmd --prefix frontend run test -- --run tests/simulation.test.ts
uv run --locked pytest backend/tests/contracts/test_simulation_contracts.py backend/tests/integration/test_startup.py
npm.cmd --prefix frontend run test -- --run tests/api.test.ts
uv run --locked ruff check backend
git diff --check
```

Za Windows temp/cache ograničenja koristi jedinstvene apsolutne putanje pod ignorisanim `.cache`, uz `--basetemp` i `-o cache_dir` po potrebi.

Za svaki novi modul zabeleži collected/executed/passed/failed brojeve, exit kodove, konkretne failing test ID-jeve i očekivani razlog. Proveri da testovi ne padaju zbog sopstvenih grešaka. Posle završnih izmena ponovi pogođene provere.

Ako izvršiš pune suite-ove, prijavi namerne nove RED padove odvojeno od regresija. Ne tvrdi da je puni suite GREEN. Ne ignoriši nove testove u konfiguraciji radi prolaza. Odsustvo testova ili neuspešna kolekcija nisu uspeh.

Ne pokreći aplikacioni/browser demo iz T011. Nema potrebe za ML-om, provider ključem, dataset download-om, Feature 02 adapterom ili Feature 05 infrastrukturom.

## 7. Evidence i predaja

Pre izmena sačuvaj tačan primljeni prompt u:
`prompts/development/004-simulation-phase-03.md`

Ako već postoji, sačuvaj original i dodaj datiranu dopunu sa opsegom T005–T007.

Vodi RED evidence u:
`evidence/tasks/feature-004-us1.md`

Za ovaj deo jasno označi:
- T005/T006/T007: izvršeni RED nalazi;
- T008–T011: nepočeti;
- GREEN/refactor novog ponašanja: van trenutnog opsega.

Predaju vodi u:
`evidence/tasks/feature-004-phase-03-handoff.md`

Beleži početnu granu/commit, postojeće izmene, prompt, zahteve, menjane fajlove, eventualne minimalne importabilne granice, verzije, stvarne komande/ishode, regresiju, namerne preostale padove i ograničenja.

Checkbox T005/T006/T007 označi tek kada je propisana test pokrivenost napisana i odgovarajući RED stvarno izvršen. Delimični task ostaje neoznačen. Nemoj završetak ovih test taskova predstavljati kao implementiran proizvod ili završenu fazu 3.

Posle koherentne celine ažuriraj `next_work.md` sa stvarnim stanjem, evidence linkovima, preostalim RED padovima i jednim narednim korakom. Sačuvaj faza-2 scenario, fingerprint, modele/katalog, stare Cases ugovore i ponašanje, lockfile-ove i deljeni `.agents`/`.specify` sadržaj.

Bez subagenata osim ako ih primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

Završni odgovor: status T005–T007, šta je testirano, stvarni RED i regresioni rezultati, šta nije izvršeno, handoff putanja i sledeći korak — zasebna implementacija T008–T010, počev od replay engine-a T008.

Ne započinji T008.