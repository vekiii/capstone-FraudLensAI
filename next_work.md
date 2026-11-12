# Sledeći korak — FraudLens AI

Poslednje ažuriranje: 2026-11-12, Europe/Belgrade. Grana pri proveri: initialization.
Početni HEAD faze 5: f17ff8f. Aktuelni zahtev određuje opseg rada.

## Provereno stanje
- **T001–T023 završeni; T024–T027 pending.** Feature 1 još nije završen.
- Faza 5, T020–T023, završena je prema korisnikovom zahtevu.
  [Instrukcija faze 5](prompts/development/001-foundation-phase-05.md) prvobitno je
  zabeležena pre implementacije; na zahtev autora naknadno je uređena u strukturiran
  format, uz jasnu napomenu da nije doslovan prepis razgovora. Opseg nije promenjen.
- [T020/T021 dokaz](evidence/tasks/T020.md): 19 novih test-only rules-scorer provera
  prošlo je odmah; puna backend regresija **310 passed**, Ruff PASS. T015/T016 već
  ispunjavaju zahtev, pa produkcioni kod nije menjan niti je izmišljan RED pad.
- T022 dokumentuje privremene foundation i buduće produktne odgovornosti A/B/C/D,
  zamenljive granice, review ugovora i scope approval. T023 indeksira svih 13
  razvojnih zapisa. Detalji/provere: [predaja faze 5](evidence/tasks/phase-05-handoff.md).
- Spec-kit prerequisites i checklist 11/11 PASS. Nema extension hook-ova.
  Produkcioni moduli, frontend, šeme, fixture-i, lockfile-ovi i governance nisu menjani.
- Raniji [T019 dokaz](evidence/tasks/T019.md) pokriva 16 headless Chrome scenarija,
  Enter aktivaciju i 390px viewport, uz dokumentovan fault injection i ograničenja.
  To nije ručno kliktanje, screen-reader provera ili peer reprodukcija.
- Frontend 151 tests/typecheck/build i lokalni HTTP smoke prošli su ranije u T019/setup-u;
  nisu ponavljani u fazi 5, jer aplikacioni kod/ugovori nisu menjani.
- Poznato neblokirajuće Starlette/httpx upozorenje ostaje. Ljudski review i stvarna
  reprodukcija drugog člana (T025/SC-001) ostaju pending.
- Lokalni setup koristi Python 3.14.7 u repozitorijumskom `.venv`, uv 0.10.9,
  Node 24.20.0 i npm 11.19.0; runtime zahtevi ostaju Python 3.14 / Node 24.
  Ako uv nije na PATH-u, dostupan je preko `py -3.14 -m uv`.

## Jedan konkretan sledeći korak
Početi **T024**: proveriti FR/SC pokrivenost i uskladiti stvarno zastarele statuse
u README.md, frontend/README.md, spec.md, plan.md i quickstart.md sa aktuelnim dokazima.
T025 zatim zahteva stvarnog drugog učesnika; agentski setup nije dokaz peer reprodukcije.

Pre nastavka pročitati AGENTS.md, ovaj fajl, aktuelni tasks.md i relevantni evidence.
Povući dogovorene Git izmene i sačuvati postojeće lokalne izmene. Status taskova proveravati
prema dokazima. Posle implementacione celine ažurirati ovaj pregled i detaljan handoff.

## Nakon predaje
Faza 6: T024–T027, uključujući stvarnu peer reprodukciju, završne provere i konvergenciju.
Nakon završenog/proverenog foundation-a razraditi 002-data-and-risk-scoring, pa ostale
odobrene feature specifikacije 003–005. Nezavisne oblasti mogu se razvijati paralelno
prema ugovorima; RAG/AI workflow ne čekaju završetak ML treninga.

## Git
Izmene faze 5 su nekomitovane. Korisnik sam radi commit/push; agent ih nije izvršio.
Predlog: `test(backend): verify scorer substitution and document US3 handoff`.
