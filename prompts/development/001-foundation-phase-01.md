Implementiraj fazu 1 — Setup, taskove T001–T005 iz
specs/001-project-foundation/tasks.md.
Implementiraj, nemoj samo predložiti plan ili generisati novi prompt.

Kontekst:
FraudLens AI je Bootcamp AML prototip. Ova faza priprema razvojno okruženje,
projektna uputstva i evidenciju. Ne implementira aplikaciono ponašanje,
ML trening, RAG, LLM integraciju ili prikaz slučajeva.
Ne treba ti kontekst prethodnih razgovora; izvori istine su projektni fajlovi.

## 1. Pročitaj i proveri početno stanje

Proveri Git granu, status i postojeće fajlove. Očekivana grana je initialization,
ali sačuvaj stvarnu granu i ne prebacuj je automatski. Sačuvaj postojeće izmene;
nemoj koristiti reset, clean ili stash da bi dobio čist početak.

Pročitaj:
- Važeće AGENTS.md instrukcije ako postoje.
- .specify/memory/constitution.md
- specs/001-project-foundation/spec.md
- specs/001-project-foundation/plan.md
- Fazu 1 i relevantne zavisnosti u specs/001-project-foundation/tasks.md
- specs/001-project-foundation/research.md
- Relevantne setup/check komande iz specs/001-project-foundation/quickstart.md
- Postojeći .gitignore, .specify/.gitignore i eventualne evidence zapise.

original_idea.md koristi ciljano ako je potreban širi kontekst za T001.
Ne učitavaj PDF sa kursa, datasetove ili nepovezane dokumente.

Pročitaj i primeni lokalni .agents/skills/speckit-implement/SKILL.md ako postoji,
isključivo za T001–T005. Ovaj izričiti opseg ima prednost nad opštom instrukcijom
da se završi ceo tasks.md. Poštuj primenljive checklist i hook zahteve.
Nemoj menjati njihove oznake radi prolaska.

Pre Spec-kit komandi odaberi feature za ovu PowerShell sesiju:
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/001-project-foundation'

To ne menja Git granu. Ne oslanjaj se na tuđi lokalni feature.json.

## 2. Sačuvaj originalnu instrukciju

Pre implementacionih izmena sačuvaj ovaj primljeni prompt u:
prompts/development/001-foundation-phase-01.md

Ako fajl već postoji, sačuvaj original i dodaj jasno označenu datiranu dopunu.
Ovo je trag rada za fazu 1; ne označavaj budući T023 završenim.

## 3. Implementiraj isključivo ove taskove

T001 — AGENTS.md
Dokumentuj granice obima, pravilo timskog odobrenja za out-of-course dodatke,
SDD/TDD i obavezu stvarnih provera. Referenciraj constitution i original_idea.md.
Ne uvodi nova projektna ograničenja ili ponovljene potvrde za rutinski odobren rad.

T002 — Evidence i prompt konvencije
Napravi:
- evidence/README.md
- evidence/templates/task.md
- prompts/README.md

Obuhvati originalne razvojne promptove u prompts/development/ i verzionisane
aplikacione promptove u prompts/app/. Šablon evidence zapisa treba da sadrži:
task/requirement reference, originalni prompt, verzije, komande, stvarne rezultate,
RED/GREEN kada je primenljivo, regresiju, ograničenja i status ljudskog pregleda.
Ne popunjavaj šablon izmišljenim izvršavanjima. Bez tajni i osetljivih podataka.
Ne kreiraj prazne direktorijume samo radi izgleda strukture.

T003 — Backend razvojno okruženje
Inicijalizuj:
- pyproject.toml
- .python-version
- uv.lock

Koristi Python 3.12 i zavisnosti FastAPI, Uvicorn, pytest, httpx, Ruff i jsonschema,
uz Pydantic u skladu sa planom. Podesi dev grupu i pytest import putanju backend/src.
Napravi samo minimalni potreban paket/kostur, bez ruta i poslovne logike.
Zabeleži stvarne runtime i razrešene verzije u docs/decisions/foundation.md.
Lockfile generiši stvarnim alatom, bez ručnog izmišljanja verzija ili hash-eva.

T004 — Frontend razvojno okruženje
Inicijalizuj minimalni Vite vanilla TypeScript projekat, uključujući:
- frontend/package.json
- frontend/package-lock.json
- frontend/tsconfig.json
- frontend/index.html
- frontend/vite.config.ts
- minimalne ulazne fajlove potrebne za uspešan build

Podesi Vitest/jsdom i komande test, typecheck i build.
Razvojni server je lokalni 127.0.0.1:5173, sa strictPort; /api proxy usmeri na
127.0.0.1:8000. Backend još nije implementiran i njegovo odsustvo ne blokira setup.
Koristi Node 22, najmanje 22.12, sa kompatibilnim verzijama zavisnosti.
Stvarne Node/npm verzije zabeleži u frontend/README.md.
Ne implementiraj case list/detail UI, API klijent ili buduće behavior testove.

T005 — Git pravila i podaci
Dopuni .gitignore uz očuvanje postojećih unosa. Isključi:
- .venv/
- node_modules/
- dist/
- Python, lint, test i coverage cache/generisane izlaze
- lokalne .env fajlove, uz izuzetak za .env.example
- data/raw/
- data/processed/
- lokalne generisane evaluacione izlaze

Ne isključuj cele .agents/ ili .specify/ direktorijume.
Poštuj postojeći .specify/.gitignore za lokalno stanje.
Ne isključuj uv.lock, frontend/package-lock.json, male pregledane fixture fajlove,
specifikacije, promptove i evidence dokumente.
Dokumentuj pravila za podatke i Git u data/README.md.

## 4. Način rada i granice

Radi sekvencijalno: T001 → T002 → T003 → T004 → T005.
Oznaka [P] dozvoljava paralelizaciju, ali je ne zahteva.
Ne pokreći subagente osim ako ih primenljive instrukcije izričito zahtevaju.

Ovo je pretežno mehanički setup: ne izmišljaj RED testove.
Ako se pojavi stvarno poslovno ponašanje unutar odobrenog opsega, primeni TDD.
Ne implementiraj T006 ili kasnije taskove da bi imao testove u ovoj fazi.

Rutinske odluke unutar plana razreši sam. Za suštinsku kontradikciju ili dodatak
van obima zabeleži nalaz i traži potrebnu odluku, uz nastavak nezavisnog rada.
Ne menjaj specifikacije, constitution ili ugovore da bi zaobišao problem.

Instaliraj potrebne projektne zavisnosti uz važeće dozvole okruženja.
Ne menjaj trajne sistemske politike niti globalne runtime instalacije neprimetno.
Posle prvog razrešavanja koristi zaključane instalacije.
Ne radi beskonačne pokušaje ako mreža ili okruženje stvarno blokiraju instalaciju.

Bez commit-a, push-a, merge-a ili deploy-a; to članovi tima rade svojim Git postupkom.

## 5. Proveri isporučeni setup

Izvrši provere koje odgovaraju ovoj fazi:
- Stvarna Python/uv/Node/npm verzija i usklađenost sa planom.
- uv sync --locked --group dev
- Dostupnost backend zavisnosti u projektnom okruženju.
- Dostupnost i ispravnost pytest/Ruff konfiguracije.
- npm --prefix frontend ci
- npm --prefix frontend run typecheck
- npm --prefix frontend run build
- Provera Vitest konfiguracije/dostupnosti.
- Git ignore pravila pomoću git check-ignore, uključujući proveru da deljeni fajlovi
  i lockfile-ovi nisu nenamerno ignorisani.
- Pregled svih nastalih, uključujući untracked, fajlova i git diff --check.

Ako behavior testovi još ne postoje, prijavi da još nisu napisani.
Nemoj odsustvo testova predstavljati kao uspešan test suite i nemoj dodavati
besmislene testove ili globalno prikrivati odsustvo testova radi zelenog izlaza.

Ne pokreći health/case smoke testove jer pripadaju kasnijim fazama.
Ne tvrdi da je SC-001 ispunjen: stvarna reprodukcija drugog člana dolazi kasnije.

## 6. Evidencija, nastavak i završetak

Koristi evidence konvencije napravljene u T002.
Održavaj evidence/tasks/phase-01-handoff.md sa:
- granom i početnim commit-om;
- završenim, delimičnim i preostalim taskovima;
- promenjenim fajlovima;
- stvarnim komandama i ishodima;
- blokadama i prvim sledećim korakom.

Osveži zapis nakon svakog završenog taska ili koherentne celine, ne samo na kraju.
Naredni član nastavlja iz fajlova povučenih kroz Git, bez istorije ovog razgovora.

Označi T001–T005 završenim u tasks.md samo kada su stvarno isporučeni i provereni.
Delimični ili blokirani taskovi ostaju neoznačeni. Ne označavaj druge taskove.

Nastavi do završetka faze ili stvarnog spoljnog blokera. Na kraju kratko navedi:
- status svakog taska T001–T005;
- šta je napravljeno;
- izvršene provere i njihove stvarne rezultate;
- šta nije provereno i zašto;
- putanju handoff zapisa i prvi sledeći korak.

Stani na granici faze 1. Ne započinji fazu 2.
## User amendment — 2026-11-11

Samo dodaj jos jednu minimalnu izmenu, umesto Node 22 koristice se Node 24 i umesto Python 3.12 koristice se Python 3.14. Da li mozes da prodjes kroz fazu 1 ponovo i ispravis to tamo gde treba?
