# Sledeći korak — FraudLens AI

Poslednje ažuriranje: 2026-11-12. Grana: initialization.
Aktivni feature: specs/001-project-foundation.

## Trenutno provereno stanje
- Faze 1 i 2 završene: T001–T007; T008 i kasniji taskovi nisu započeti.
- Faza 2: strogi Pydantic modeli i 93 ugovorna testa. Ciljani i puni backend pytest:
  93 passed; Ruff i git diff --check prolaze. Regresija obuhvata samo ugovorne testove.
- Korisnik je odobrio ciljanu korekciju završnih regex sidara u schemas.json;
  završni newline se odbacuje. Nema drugih promena ugovora ili lockfile-ova.
- Runtime-i: Python 3.14 / Node 24; ova faza proverena na Python 3.14.3.
- Dokazi: [T006/T007](evidence/tasks/T006.md),
  [handoff faze 2](evidence/tasks/phase-02-handoff.md),
  [setup faze 1](evidence/tasks/phase-01-handoff.md).
- Nema aktivnih blokera. Ljudski pregled i peer reprodukcija/SC-001 ostaju pending.
- Aplikacija, browser smoke i frontend suite nisu pokretani u ovoj backend fazi.
  Ugovorni testovi nisu ML evaluacija. Nema commit/push/merge/deploy radnji.

## Jedan konkretan sledeći korak
Zasebno pokrenuti fazu 3 od T008: RED startup/health testovi prema tasks.md,
zatim T009 implementacija. Trenutni zahtev ne odobrava početak te faze.
Pre rada pročitati AGENTS.md, ovaj fajl i relevantne taskove/evidence; proveriti
aktuelnu granu i status i sačuvati postojeće izmene.

## Preostali redosled
- Faza 3: T008–T011 — startup/health i onboarding.
- Faza 4: T012–T019 — lista, detalj, sintetički skor.
- Faza 5: T020–T023 — scorer granica i handoff.
- Faza 6: T024–T027 — završna verifikacija, peer reprodukcija i konvergencija.
Tek nakon završenog feature-a 1 razraditi 002-data-and-risk-scoring, zatim
003-knowledge-and-retrieval, 004-case-investigation i 005-priority-and-simulation.
Ne implementirati buduće specifikacije bez njihovog definisanja i odobrenog zahteva.

Održavati ovaj pregled posle implementacione celine/predaje; detaljne komande i
istoriju čuvati u evidence/. Read-only i prompt-only zahtevi ne menjaju napredak.
