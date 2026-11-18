Implementiraj fazu 1 — Setup, isključivo task T001, za feature `specs/004-simulation-and-prioritization`. Nemoj samo predložiti plan ili generisati novi prompt. Stani pre T002.

FraudLens AI je obrazovni AML prototip. Feature 004 planira determinističko poređenje tri strategije pregleda nad zamrznutim sintetičkim scenarijem. Ova faza proverava postojeće okruženje i početnu regresiju; ne implementira simulaciju.

Sve putanje su relativne u odnosu na koren projekta. Koristi aktuelni checkout, bez istorije prethodnih razgovora.

## 1. Pročitaj i proveri početno stanje

Pročitaj primenljive `AGENTS.md` instrukcije, zatim odmah root `next_work.md`, pre planiranja i rada. Ponovi pri nastavku sesije. Aktuelni zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/004-simulation-and-prioritization/{tasks.md,spec.md,plan.md,quickstart.md}`
- `evidence/tasks/feature-004-task-generation.md`
- relevantne setup delove `specs/001-project-foundation/quickstart.md`
- `pyproject.toml`, `.python-version`, `uv.lock`
- `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.ts`
- `backend/tests/integration/test_startup.py`
- `frontend/tests/api.test.ts`
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md`
- relevantne ignore pravila i postojeći setup evidence, ako postoji.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` samo za T001. Eksplicitan opseg ima prednost nad opštim zahtevom da se izvrši ceo tasks.md. Poštuj stvarne checklist/hook zahteve; ne menjaj oznake radi prolaska. Ne traži ponovno odobrenje za rutinske već odobrene korake. Ako postoji stvarna neodobrena odluka, navedi tačan izvor i razlog.

Pri generisanju ovog prompta read-only pregled je pokazao:
- granu `004-simulation-and-prioritization`;
- neversionisan `specs/004-simulation-and-prioritization/feature4_tasks_prompt.md`;
- T001 neoznačen;
- postojeće Python 3.14 i Node 24 konfiguracije i lockfile-ove;
- planning/task evidence bez izvršenih application provera za feature 004.

Ponovo proveri granu, HEAD, status i relevantne fajlove. Sačuvaj postojeće izmene, uključujući neversionisani šablon. Ne menjaj granu, ne radi automatski pull, merge, reset, clean ili stash. Prljavo stablo samo po sebi nije blokada.

## 2. T001 — zaključana instalacija i početna regresija

Tačan zahtev:
Izaberi Feature 004 u PowerShell sesiji, izvrši locked setup iz quickstart-a, pokreni postojeće `backend/tests/integration/test_startup.py` i `frontend/tests/api.test.ts` kao baseline i zabeleži verzije, komande i rezultate u:
`evidence/tasks/feature-004-setup.md`

Iz korena projekta:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/004-simulation-and-prioritization'
uv sync --locked --group dev
npm.cmd --prefix frontend ci
```

Izbor feature-a ne menja Git granu. Koristi postojeće Python 3.14 i Node 24 zahteve. Zabeleži stvarne verzije uv, projektnog Python interpretera, Node-a i npm-a; razlikuj projektni interpreter od sistemskog.

Ako je potreban workspace-local uv cache:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
```
Koristi `npm.cmd` na PowerShell-u bez menjanja trajne execution politike.

Ne pokreći `uv lock`, `npm install`, upgrade ili ručno uređivanje lockfile-ova radi rutinskog setup-a. Locked instalacija mora koristiti postojeće rezolucije. Ako lockfile ili runtime preduslov nije kompatibilan, dokumentuj konkretan problem; ne nadograđuj ili regeneriši zavisnosti prećutno.

Pokreni ciljane provere:
```powershell
uv run --locked pytest backend/tests/integration/test_startup.py
npm.cmd --prefix frontend run test -- --run tests/api.test.ts
```

Ovo su postojeće regresione provere. Za mehanički setup nema veštačkog RED-a i ne piši nove simulation testove. Razlikuj prolaz, pad, environment blokadu, nije pokrenuto i nema prikupljenih testova. Odsustvo testova nije uspeh.

Za Windows temp/cache ograničenja koristi jedinstvene apsolutne putanje pod ignorisanim root `.cache`, uz `--basetemp` i `-o cache_dir` po potrebi. Zabeleži tačne komande. Environment grešku ne predstavljaj kao pad poslovnog ponašanja.

Ako instalacija ili testovi zahtevaju sandbox eskalaciju, koristi propisani approval mehanizam. Ne zaobilazi ograničenja i ne uvodi novu infrastrukturu radi setup problema.

## 3. Granice rada

T001 je završen kada:
- eksplicitno odabrani feature odgovara ovom zahtevu;
- obe zaključane instalacije uspeju;
- oba navedena baseline test modula zaista prođu;
- evidence i handoff odgovaraju stvarnom izvršavanju.

Ako je task već delimično urađen, proveri dokaz i dovrši samo ono što nedostaje. Ako provera padne, istraži dovoljno da razdvojiš setup problem od postojeće regresije. Bez implementacije drugih faza ili širokih popravki; za nužno proširenje navedi konkretan razlog i traži odluku, uz završavanje nezavisnog rada.

Ne kreiraj sintetički scenario, outcomes fajl, simulation module, endpoint-e ili frontend prikaz. Oni pripadaju T002+. Ne pokreći Simulation browser walkthrough iz quickstart-a: taj tok još nije implementiran.

Sačuvaj postojeći Cases tok i ugovor. Feature 02 adapter, ML, Feature 05 infrastruktura i LLM integracija su van opsega. Nema dataset preuzimanja, provider ključeva, Docker-a ili izmene scorer-a/baze.

Za kasniju simulaciju ostaje pravilo: outcome oznake koriste se tek posle izbora i ne ulaze u javni payload. Ovaj task ih ne kreira niti obrađuje.

Ne pokreći subagente osim ako ih primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

## 4. Originalni prompt, evidence i predaja

Pre implementacionih/setup izmena sačuvaj tačan primljeni prompt u:
`prompts/development/004-simulation-phase-01.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune.

U `evidence/tasks/feature-004-setup.md` zabeleži:
- datum i vremensku zonu;
- T001 i veze ka feature dokumentima;
- originalni prompt;
- početnu granu, commit i postojeće izmene;
- stvarne runtime/tool verzije i korišćene lockfile-ove;
- radni direktorijum, komande, exit kodove i sažete stvarne rezultate;
- RED: nije primenljivo za mehanički setup;
- blokade/neizvršene provere i status ljudskog pregleda.

Održavaj kratku predaju:
`evidence/tasks/feature-004-phase-01-handoff.md`

Posle završene celine ili delimične predaje ažuriraj root `next_work.md`: stvarni napredak, evidence linkovi, blokade/neizvršene provere i jedan konkretan sledeći korak. Detaljna istorija ostaje u evidence-u.

Označi samo T001 i tek kada je isporučen i obe propisane provere prođu. Ako je delimičan/blokiran, ostavi ga neoznačenim uz precizan opis. Ne menjaj stanje drugih taskova. Ne tvrdi da je drugi član reprodukovao setup ili da je ljudski review izvršen bez stvarnog dokaza.

Na kraju pregledaj diff i nove fajlove, proveri da zavisnosti/lockfile-ovi i aplikacioni kod nisu nenamerno promenjeni i izvrši:
```powershell
git diff --check
```

Završni odgovor neka kratko navede status T001, stvarne ishode locked instalacija i oba baseline modula, ograničenja i putanju handoff-a. Ako je T001 završen, sledeći korak je zasebna faza 2, T002–T004. Ne započinji je.