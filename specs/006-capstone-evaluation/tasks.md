---
description: "Implementation and verification tasks for the Capstone evaluation"
---

# Zadaci — Feature 06: Evaluacija sistema i priprema predaje

**Ulazi** [Specifikacija](spec.md), [plan](plan.md), [istraživanje](research.md), [model podataka](data-model.md), [ugovor](contracts/evaluation.md), [EV matrica](contracts/ev-cases.md) i [quickstart](quickstart.md).

**Format** `[ID] [P?] [US?]`. `[P]` označava zadatke sa odvojenim fajlovima koji mogu da se rade paralelno posle navedenih preduslova. Putanje su relativne u odnosu na koren repozitorijuma.

**Provere** Poslovno ponašanje razvijati kroz RED → GREEN → REFACTOR. Čekirati zadatak tek posle stvarne izvršene provere. Za merenja sačuvati neuspešne i blokirane ishode. Evidentirati komande, revizije i rezultate u evidence zapisima i osvežiti `next_work.md` posle svake celine.

## Faza 1 — Setup

- [x] T001 Izabrati `specs/006-capstone-evaluation` u PowerShell sesiji, izvršiti zaključani setup iz `specs/006-capstone-evaluation/quickstart.md` i snimiti granu, reviziju, verzije, početne ciljane Cases/investigation i React provere u `evidence/tasks/feature-006-setup.md`. Svaki postojeći pad opisati sa izvršenom komandom.

## Faza 2 — Preduslovi

- [ ] T002 [P] Proveriti T098 transfer digest za `data/processed/feature-003-t098-20261118/model-bounded.sqlite`, `data/processed/feature-003-t098-20261118/source.sqlite` i `data/processed/feature-003-t098-20261118/history-index.sqlite`. Read-only proveriti aktivni kompletni `run_boosted_candidate_smoke`, vezu indeksa sa izvornim store-om, oba case ID-ja i provenance skora. Snimiti nalaz u `evidence/tasks/feature-006-t098-inputs.md`. Za nedostupan ili nekompatibilan paket evidentirati blokadu ili odobren kompatibilan snapshot.
- [x] T003 [P] Obnoviti neophodne runtime zavisnosti za postojeći provider i validaciju u `pyproject.toml` i generisati `uv.lock`. Uporediti verzije SDK-a i transporta sa Feature 03, proveriti zaključani sync i lokalne importe SDK-a, transporta i validatora bez modelskog poziva. Zabeležiti u `evidence/tasks/feature-006-provider-setup.md`.

## Faza 3 — US1: Živa istraga označene transakcije (P1)

**Nezavisna provera**. Otvoriti objavljeni dataset slučaj u React Cases. Proveriti isti snapshot i poreklo skora kroz nacrt, sadržaj citata, deterministički alat i obnovljivu odluku. Zasebno probati pripremljen slučaj sa nedovoljno dokaza.

- [ ] T004 [P] [US1] U `web/tests/investigation-dataset-binding.test.tsx` napisati RED provere za otvaranje panela iz v2 detalja, dataset ID i izričit režim pri kreiranju, odbijanje zastarelog snapshot-a pre mutacije i ignorisanje rezultata prethodnog slučaja nakon promene selekcije. Dodati regresiju za postojeći fixture tok.
- [ ] T005 [P] [US1] Proveriti postojeći backend ugovor u `backend/tests/integration/test_investigation_dataset_binding.py`. Koristiti deterministički testni snapshot. Obuhvatiti neslaganje identiteta, režima, skora i snapshot-a, nedostupnost istorije i odsustvo prelaska na fixture. Gde ugovor već prolazi, voditi proveru kao regresiju. Ako nedostaje ugovoreno ponašanje, zabeležiti nameravani RED i najmanju potrebnu popravku u `backend/src/fraudlens/investigation/dataset.py` pre GREEN.
- [ ] T006 [US1] Povezati v2 Cases detalj sa postojećim panelom u `web/src/pages/Cases.tsx`, `web/src/pages/InvestigationPanel.tsx`, `web/src/investigation/controller.ts`, `web/src/investigation/api.ts` i `web/src/investigation/contracts.ts`. „Dataset binding koristi istu objavljenu reviziju u Cases i investigation čitanju.“ Prihvatiti režimski odgovarajući ID, proveriti očekivani snapshot i serverov `context_revision`, vezati pokušaj, citat i review za isti slučaj. Sačuvati fixture tok, otkazivanje zastarelih operacija i postojeći Vite Host/proveru porekla. Pokrenuti T004 i T005.
- [ ] T007 [US1] Pokrenuti React, API i worker na odobrenom snapshot-u po `specs/006-capstone-evaluation/quickstart.md`, sa testnim providerom i svežim lokalnim store-om. Potvrditi objavljen skor, pravilno vezan kontekst, stvarno nedostupnu istoriju u kontrolisanom EV-08 scenariju i čuvanje i ponovno otvaranje odluke. Zabeležiti rezultate u `evidence/tasks/feature-006-dataset-smoke.md`.
- [ ] T008 [US1] Posle potvrde obima plaćenih poziva izvesti postojeću sintetičku proveru modela, zatim živi browser preflight sa izdvojenim slučajem izvan zamrznutog EV paketa ili varijantom namenjenom samo pripremi. Potvrditi stvarni model i odabrani profil, izvršen alat, validiran nacrt, proverljiv odlomak i obnovljivu odluku. Stvarni broj poziva i ishod upisati u `evidence/tasks/feature-006-live-preflight.md`. Preflight je priprema za primarno merenje.

## Faza 4 — US2: Poređenje na 16 fiksnih slučajeva (P1)

**Nezavisna provera**. Pregledalac može za svaki EV red da poveže isti ulaz i pravilo ocene sa stvarnim početnim i završnim ishodom. Jedan početni trag mora da objasni ciljanu izmenu.

- [ ] T009 [P] [US2] Iz [EV matrice](contracts/ev-cases.md) materijalizovati javne korake, ulaze, seed pravila i preduslove u `evals/capstone/inputs/cases.json`, a prihvatljive ishode i obavezne signale u `evals/capstone/reference/expectations.json`. „Podaci za ocenu su odvojeno skladišteni.“ Predvideti istu vezu EV-06 → EV-01 unutar oba izvršavanja. Priprema može da počne uz US1. Konačne identitete T098 slučajeva i nedostupne istorije potvrditi pre zamrzavanja.
- [ ] T010 [P] [US2] Pripremiti determinističke negativne provere u `backend/tests/integration/test_capstone_negative.py` i po potrebi `web/tests/capstone-negative.test.ts`. Mapirati EV-11–EV-16 na nevalidan zahtev, nevalidan strukturisani izlaz, nedostupan citirani izvor, nedozvoljen alat ili opseg, kontrolisani timeout ili limit i kvar dozvoljenog alata. Gde postoje, ponovo koristiti postojeće testove i granice ubrizgavanja kvara. Potvrditi očekivani status i stvarno izostajanje neželjenih poziva ili objave nacrta. Svi ovi slučajevi koriste lokalne kontrolisane uslove.
- [ ] T011 [P] [US2] U `evals/capstone/README.md` definisati ponovljivu evidenciju izvršenja preko postojećih aplikacionih granica. Ponovo koristiti zamrzavanje, metering i trag iz `backend/src/fraudlens/investigation/acceptance_harness.py` i `backend/src/fraudlens/investigation/timing_observer.py` tamo gde odgovaraju. Zapis uključuje „faza `baseline` ili `final`“, commit, digest ulaza, režim, ishod, trag, binding, verzije i potrošnju. „Dozvoljeni statusi rezultata su `pass`, `fail`, `blocked` i `not_run`.“ Proveriti šemu i agregaciju na lokalnim test podacima, sa 16 mesta po fazi i bez referenci u izvršnom ulazu.
- [ ] T012 [US2] Proveriti spremnost T007–T011 i zamrznuti `evals/capstone/manifest.json` i `evals/capstone/protocol.md`. Paket ima „spisak tačno 16 EV ID-jeva“ i „verzija i digest svakog ulaza, početnog stanja i očekivanja“. Evidentirati model i profil, odvojene hash-eve ulaza i referenci, artefakte, reset i retry pravila, reviziju i potvrđeni budžet. Potvrditi podrazumevane uslove i blokade pre prvog primarnog izvršavanja.
- [ ] T013 [P] [US2] Izvršiti baseline EV-01–EV-10 na identifikovanoj reviziji i uz ovlašćen režim pravog modela. U `evidence/tasks/feature-006-baseline-live.md` zabeležiti stvarne ishode, sanitizovane tragove, model, opravdana zaustavljanja pre poziva, ponavljanja i potrošnju. EV-06 čita pokušaj iz EV-01 iste faze. Sirove izlaze držati van Git-a u `evals/results/capstone/baseline-live.json`.
- [ ] T014 [P] [US2] Izvršiti deterministički baseline EV-11–EV-16 na istoj reviziji sa odvojenim lokalnim stanjem. Sačuvati komande, kontrolu i stvarni ishod svakog slučaja u `evidence/tasks/feature-006-baseline-negative.md`.
- [ ] T015 [US2] Offline oceniti svih 16 početnih rezultata, bez slanja očekivanja u model ili pretragu. U `evidence/tasks/feature-006-targeted-change.md` povezati „početni trag i EV ID, hipoteza o uzroku, tačna promena, commit ili diff, očekivani uticaj i rezultat ponovljene provere“. Za promenu ponašanja dodati ciljani RED, primeniti jednu promenu i proveriti GREEN i relevantne regresije. Konkretna putanja implementacije utvrđuje se po stvarnom tragu.
- [ ] T016 [US2] Identifikovati završnu reviziju za predaju i u `evidence/tasks/feature-006-release-candidate.md` upisati tačan SHA, stanje radnog stabla, konfiguraciju, digeste, raspoloživi odobreni budžet i sve promene u odnosu na baseline. Potvrditi da paketi ulaza i kriterijumi ostaju isti. Svaku izmenu ulaza posebno prijaviti i primeniti pravilo za uporedivost.
- [ ] T017 [P] [US2] Izvršiti final EV-01–EV-10 na reviziji iz T016, sa istim ulazima, ocenom i proverljivim poreklom rezultata. U `evidence/tasks/feature-006-final-live.md` evidentirati browser trag za označenu transakciju, sadržajni pregled citata, nedovoljno dokaza i stvarne ishode i trošak svih živih EV redova.
- [ ] T018 [P] [US2] Ponoviti EV-11–EV-16 na istoj završnoj reviziji i u `evidence/tasks/feature-006-final-negative.md` potvrditi da je svaka od šest predviđenih kontrola stvarno izvršena i prošla. Pad ostavlja kriterijum SC-003 otvorenim.
- [ ] T019 [US2] U `evidence/tasks/feature-006-before-after.md` prikazati tabelu istih 16 EV ID-jeva sa očekivanjem, stvarnim ishodom obe faze, statusom, dokazom i uporedivošću. Zbir prikazati sa imeniteljem 16 po fazi. Izdvojiti poboljšanja i regresije, obrazložiti odstupanja i povezati ih sa T015. Blokada ili neizvršenje nisu ispunjen kriterijum stvarnog merenja.

## Faza 5 — US3: Reprodukcija i predaja (P1)

**Nezavisna provera**. Drugi član iz čistog checkouta izvršava dogovoreni tok i pronalazi CAP dokaze i individualne doprinose na referentnoj reviziji.

- [ ] T020 [US3] U `specs/006-capstone-evaluation/quickstart.md` ažurirati stvarne komande i preduslove za završnu reviziju, uključujući proveru izvora i artefakata, server, worker i pregled. Povezati uspešan prolaz, slučaj za dopunu i kontrolisanu grešku sa stvarnim rezultatima predaje.
- [ ] T021 [US3] Organizovati i zabeležiti stvarnu reprodukciju drugog člana iz čistog checkouta u `evidence/tasks/feature-006-peer-reproduction.md`. Sačuvati člana, reviziju, komande, nalaze i eventualne blokade. Ako su potrebni dodatni živi pozivi, uračunati ih u ovlašćeni obim.
- [ ] T022 [P] [US3] Prikupiti i povezati potvrde sva četiri člana u `evidence/tasks/feature-006-cap08-contributions.md`. Za svakog zapisati tehnički doprinos, odluku sa stvarnom proverom, vezu sa glavnim tokom i primer pregleda rada kolege, uz reference na predatu reviziju.
- [ ] T023 [US3] Sastaviti `evidence/tasks/feature-006-capstone-evidence-map.md` sa svih osam CAP stavki, referentnim commitom ili tagom, statusima, dokazima i tri scenarija za odbranu. Potvrditi da završna živa i negativna provera i final EV rezultati upućuju na isti testirani SHA.

## Faza 6 — Završna provera i predaja rada

- [ ] T024 Izvršiti završne pytest, Ruff, Vitest i produkcijski build komande iz `specs/006-capstone-evaluation/quickstart.md` na kandidatu i zapisati stvarne izlaze u `evidence/tasks/feature-006-regression.md`. Uporediti zabeležene padove sa polaznim stanjem. Ponoviti pogođene provere ako se kandidat menja.
- [ ] T025 Proveriti pokrivenost FR-001–FR-008 i SC-001–SC-004, usklađenost SHA referenci, svih 16 EV i osam CAP stavki i da deljeni dokazi nemaju tajne ili zaštićene podatke. U `next_work.md` upisati stvarno stanje, link na `evidence/tasks/feature-006-capstone-evidence-map.md` i naredni korak. Git objavljivanje ide po dogovoru tima.

## Zavisnosti i paralelan rad

| Celina | Zavisnosti |
| --- | --- |
| Setup i preduslovi | T001 → T002 i T003. |
| US1 | Posle faze 2 paralelno T004 i T005. Zatim T006 → T007 → T008. |
| US2 priprema | T009, T010 i T011 rade na odvojenim izlazima paralelno sa US1. T012 spaja T007–T011. |
| US2 izvršavanje | T012 → T013 i T014 → T015 → T016 → T017 i T018 → T019. Žive i simulirane provere koriste odvojena stanja. |
| US3 | T020 može da počne posle T016, a završava se posle T019. T021 sledi posle T020. Evidencija doprinosa T022 može paralelno sa T020 i T021 od identifikovanja kandidata. T023 spaja T019–T022. |
| Završetak | T024 posle T016, u izolovanom okruženju i paralelno sa pripremom predaje. T025 zavisi od T023 i T024. |

Primer paralelnog rada: provera T098 artefakata može da ide uz zaključavanje SDK-a. Frontend RED za binding i backend provera granice mogu istovremeno jer koriste odvojene test fajlove. Treći član može da pripremi EV ulaze, dok četvrti mapira postojeće negativne provere.

## Sledljivost

| Zahtev | Glavni zadaci |
| --- | --- |
| FR-001, SC-001 | T002–T008, T017 |
| FR-002 | T004–T008, T017 |
| FR-003 | T009, T011–T012 |
| FR-004 | T011–T014, T016–T019 |
| FR-005, SC-002 | T013–T019 |
| FR-006, SC-003 | T010, T014, T018, T024 |
| FR-007, SC-004 | T016, T020–T025 |
| FR-008 | T022–T023, T025 |

## Strategija isporuke

Prvi dokazivi inkrement je **T001–T008**, od iste označene dataset transakcije do stvarnog nacrta, citata i sačuvane odluke. T009–T012 pripremaju merenje paralelno. Početni EV ciklus mora prethoditi ciljanoj izmeni. Svih 16 završnih rezultata, negativne kontrole i čist checkout čine završnu predaju.
