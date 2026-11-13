# Phase 5 — Independent Contribution Boundaries (T020–T023)

Datum: 2026-11-12, Europe/Belgrade. Početna grana: `initialization`.
Početni HEAD: `f17ff8f` (`did T019`); radno stablo je bilo čisto.

Implementiraj fazu 5 feature-a `specs/001-project-foundation`, taskove T020–T023,
počev od T020. Završi povezanu celinu i stani pre T024. Oslanjaj se na aktuelni
checkout i dokumentovane zahteve, bez proširivanja foundation opsega.

## 1. Priprema i pregled postojećeg stanja

Pročitaj primenljive `AGENTS.md` instrukcije, zatim root `next_work.md`, aktuelni
`tasks.md`, specifikaciju, plan, ugovore i relevantne evidence zapise. Ponovo
proveri koje fajlove zahteva izabrani opseg i šta je već implementirano.
Primeni lokalni `.agents/skills/speckit-implement/SKILL.md` isključivo za T020–T023.

Lokalno okruženje je prethodno pripremljeno u repozitorijumskom `.venv`, uz
Python 3.14.7 i zaključane backend/frontend zavisnosti. Setup nije menjao
aplikacioni kod ni statuse taskova. Mašinski lokalno uputstvo za pokretanje,
sačuvano van repozitorijuma, nije preduslov za reprodukciju zajedničkih dokaza.

## 2. Opseg implementacije

- **T020:** dodaj testove zamene scorer-a test-only rules adapterom u
  `backend/tests/unit/test_scoring_boundary.py`. Proveri izvor `rules`, identitet
  transakcije i odbacivanje nevalidnih skorova i neuspeha adaptera.
- **T021:** dopuni injection/validaciju u `scoring.py` i `cases.py` samo ako
  provere pokažu da zahtevano ponašanje nedostaje. Ne uvodi produkcioni rules
  servis, provider integraciju ili izmene postojećih fixture podataka.
- **T022:** dokumentuj odgovornosti A/B/C/D, zamenljive granice, review zajedničkih
  ugovora i zavisnosti budućih specifikacija u `docs/decisions/foundation.md`.
- **T023:** poveži razvojne instrukcije i njihove evidence zapise kroz
  `prompts/development/001-foundation.md` i proveri postojeće konvencije beleženja.

## 3. Provere i evidencija

Za nedostajuće poslovno ponašanje primeni RED → GREEN → REFACTOR. Ako postojeći
kod već ispunjava zahtev, pokreni provere i zabeleži stvarni rezultat, bez
namernog kvarenja implementacije radi RED pada. Sačuvaj postojeće ugovore i
negativne testove; ne ublažavaj validaciju da bi provere prošle.

Izvrši ciljane testove, relevantnu backend regresiju, Ruff i `git diff --check`.
Zabeleži komande, stvarne ishode i ograničenja u `evidence/tasks/T020.md` i
`evidence/tasks/phase-05-handoff.md`. Fixture provere nisu ML evaluacija;
ljudski review i nezavisnu reprodukciju ne označavaj završenim bez stvarnog dokaza.

## 4. Predaja rada

Ažuriraj statuse samo završenih i proverenih taskova i osveži `next_work.md`.
U završnom izveštaju navedi izmene, rezultate provera, ograničenja i sledeći korak.
Pripremi predlog commit poruke u stilu postojeće istorije repozitorijuma.
Korisnik sam izvršava commit i push.

## Napomena o zapisu

Zahtev je prvobitno zabeležen pre implementacije. Na zahtev autora, 2026-11-12,
tekst je urednički usklađen sa formatom ranijih faza: razgovorni citat zamenjen
je strukturiranom instrukcijom. Ovo je uređeni zapis odobrenog opsega, a ne
doslovan prepis razgovora. Opseg rada i zabeleženi rezultati nisu promenjeni.
