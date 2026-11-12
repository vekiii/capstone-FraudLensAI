# Sledeći korak — FraudLens AI

Poslednje ažuriranje: 2026-11-12. Grana: initialization.
Feature: specs/001-project-foundation. Početni HEAD sesije:
56aaa1060e1671f2c281a8d384f5ec7ac235d343. Novi commit-i su u publication evidence.

## Trenutno provereno stanje
- T001–T018 završeni. T019 PARTIAL: regresija i stvarni HTTP/proxy PASS;
  interaktivni browser acceptance nije izvršen. T020–T027 pending.
- UI ima tri sintetička slučaja, list/detail/back, loading/empty/error/not-found,
  retry, stalnu synthetic notice, responsive CSS i tastaturne kontrole.
  Generation guard i abort sprečavaju zastarele rezultate; stari detalji nestaju odmah.
- T018: svih 101 originalnih T013 testova GREEN. Dodatna četiri UI lifecycle testa
  proveravaju ignorisanje abort-a, kasni uspeh/grešku, disposal i fokus na povratku.
- T019 locked setup prolazi. Backend 291 passed, frontend 151 passed: ukupno 442,
  0 failed. Typecheck/build/Ruff prolaze. Frontend lint nije konfigurisan.
- Stvarni Uvicorn 8000 + Vite 5173: direktni/proxy JSON su isti, validirani šemom.
  Tri ponovljiva slučaja/detalja; 404/422 generički; nema labela ili ML tvrdnji.
  Privremene test aplikacije potvrđuju empty i 500 za neispravan skor, pogrešan
  transaction_id i privatni exception. Fixture nije promenjen.
- Namerno gašenje backend-a daje proxy 502; restart vraća 200 sa tri slučaja.
  To nije dokaz browser klika na Retry. Prva provera je ugasila svoje servere;
  kasniji T019 retry ih je ponovo pokrenuo i ostavio aktivne zbog obaveznog prekida.
- Browser host nije dostupan; prvi native Chrome access approval je istekao.
  Na ponovljenom T019 pokušaju Chrome pristup je uspeo, ali je Computer Use zaustavio
  otvaranje taba jer nije mogao pouzdano da utvrdi trenutni URL za primenu pravila.
  Izvršeno 0/16 browser scenarija, nema screenshot-a niti console pregleda.
  Realni visual/mobile/keyboard i screen-reader output ostaju neprovereni.
- US2 je implementiran i automatizovane/API provere prolaze, ali pun acceptance
  nije potvrđen bez browser provere. SC-002/003 detaljno mapirani u T019 evidence.
- Nema pronađenih funkcionalnih defekata u izvršenim proverama. Poznat neblokirajući
  Starlette/httpx deprecation warning ostaje. Human review i peer SC-001/T025 pending.
- Node 24.21.0, npm 11.19.0, Python 3.14.10, uv 0.13.7. Nema novih zavisnosti.
  Fixture skorovi su sintetička demonstracija, a ne ML evaluacija.

## Jedan konkretan sledeći korak
Omogućiti browser pristup i dovršiti 16 T019 scenarija, uključujući console,
retry i rapid switching; dopuniti evidence stvarnim rezultatima. Ne tvrditi browser
PASS na osnovu jsdom ili HTTP provera. T019 ostaje otvoren dok se ovo ne završi.
Pre rada pročitati AGENTS.md, ovaj fajl i relevantne taskove/evidence; proveriti
status/granu i sačuvati postojeće izmene. Novi taskovi nisu automatski odobreni.

## Preostali redosled
- T019 browser acceptance gap.
- T020–T023: rules scorer substitution i handoff.
- T024–T027: konačne provere, peer reprodukcija i konvergencija.
- Zatim specifikacije 002–005 prema odobrenom planu.

## Dokazi
- [Commit-i i publikacija sesije](evidence/tasks/session-commits-2026-11-12.md)
- [T019 integrisana provera i ograničenja](evidence/tasks/T019.md)
- [Stvarni JSON odgovori](evidence/tasks/T019-responses.json)
- [Ponovljiva live provera](evidence/tasks/T019-live-verification.py)
- [T018 UI i DOM GREEN](evidence/tasks/T018.md)
- [T017 API i dekoderi](evidence/tasks/T017.md)
- [T016 backend API](evidence/tasks/T016.md)
- [T015 scorer](evidence/tasks/T015.md), [T014 fixture](evidence/tasks/T014.md)
- [T013 frontend RED](evidence/tasks/T013.md), [T012 backend RED](evidence/tasks/T012.md)
- Originalni zahtevi su u prompts/development/001-foundation-T012.md do T019.md.

## Git i autorstvo
Korisnik je eksplicitno odobrio komitovanje svih izmena i push na initialization.
T012–T019 rad je grupisan u test/backend/frontend/documentation commit-e pod autorom
i committer-om Isidora Popovic <popovicisidora17@gmail.com>. Revizije i stvarni push
rezultat su u publication evidence. Postojeća istorija nije menjana. Nema merge/deploy.
Budući commit/push nije automatski odobren ovim handoff-om.
