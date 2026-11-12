# Sledeći korak — FraudLens AI

Poslednje ažuriranje: 2026-11-12. Grana: initialization.
Aktivni feature: specs/001-project-foundation.

## Trenutno provereno stanje
- Faze 1–3 završene: T001–T011; T012 i kasniji taskovi nisu započeti.
- Faza 3: fixture-only settings, application factory/DI i GET /api/health.
  Osam startup testova prolazi; puna backend regresija 101 passed; Ruff prolazi.
- README opisuje zaključan setup, dva terminala, health/proxy i postojeći scaffold.
- Zaključane instalacije uspešne. Frontend typecheck/build prolaze; Vitest nema
  test fajlove (exit 1), što nije prolaz test suite-a.
- Stvarni Uvicorn i Vite smoke: backend/proxy health HTTP 200 sa tačnim JSON-om;
  Vite scaffold HTML HTTP 200. Sopstveni server procesi ugašeni.
- Runtime-i provereni: Python 3.14.3, Node 24.20.0, uv 0.10.9, npm 11.19.0.
- Dokazi: [startup RED/GREEN](evidence/tasks/T008.md),
  [provere i smoke](evidence/tasks/T011.md),
  [handoff faze 3](evidence/tasks/phase-03-handoff.md).
- Nema aktivnih blokera. Starlette/httpx deprecation warning ostaje bez pada testova.
- Ljudski pregled i peer reprodukcija/SC-001/T025 ostaju pending.
- Nisu izvršeni budući case browser tok, ML evaluacija niti test fizički ugašene mreže.
  Frontend behavior testovi još ne postoje. Nema commit/push/merge/deploy radnji.

## Jedan konkretan sledeći korak
Zasebno zatražiti fazu 4, T012–T019, počev od RED testova cases/fixture-scoring
ponašanja i frontend granice. Ovaj handoff ne odobrava njeno pokretanje.
Pre rada pročitati AGENTS.md, ovaj fajl i relevantne taskove/evidence; proveriti
aktuelnu granu i status i sačuvati postojeće izmene.

## Preostali redosled
- Faza 4: T012–T019 — lista, detalj, sintetički skor.
- Faza 5: T020–T023 — scorer granica i handoff.
- Faza 6: T024–T027 — završna verifikacija, peer reprodukcija i konvergencija.
Tek nakon završenog feature-a 1 razraditi 002-data-and-risk-scoring, zatim
003-knowledge-and-retrieval, 004-case-investigation i 005-priority-and-simulation.
Ne implementirati buduće specifikacije bez njihovog definisanja i odobrenog zahteva.

Održavati ovaj pregled posle implementacione celine/predaje; detaljne komande i
istoriju čuvati u evidence/. Read-only i prompt-only zahtevi ne menjaju napredak.
