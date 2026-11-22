# Plan implementacije — Feature 06

**Grana** `006-capstone-evaluation` | **Datum** 21. novembar 2026. | [Specifikacija](spec.md)

## Sažetak

Na jednoj verziji aplikacije povezati postojeći React prikaz označene dataset transakcije sa Feature 03 istragom. Zatim izvršiti zamrznutih 16 Capstone slučajeva, obrazložiti jednu izmenu početnim tragom i ponoviti ista merenja. Predaja objedinjuje završnu živu istragu, negativne provere, reprodukciju i CAP-01–CAP-08 dokaze na jednoj reviziji.

## Tehnički kontekst

| Oblast | Plan |
| --- | --- |
| Okruženje | Postojeći FastAPI/Python 3.14, React/TypeScript/Vite, Node 24, zaključane zavisnosti. |
| Tok | React Cases → objavljeni dataset snapshot → postojeći investigation API → eksplicitni worker → dokaz i odluka analitičara. |
| Podaci | Odobren, kompletan, kompatibilan dataset/run-store par i pregledan korpus. SQLite istrage i rezultati provera koriste izolovane lokalne putanje. |
| Provider | OpenAI sa eksplicitnim modelom i profilom koje tim može da koristi. Obnoviti zaključane runtime zavisnosti za preuzeti adapter i verifikovati ih iz čistog checkouta. Testni provider za probe i simulirane kvarove. |
| Provere | pytest i Vitest, Chrome kroz Vite proxy, deterministički EV-11–EV-16, stvarni model za EV-01–EV-10 i pregled vernosti citata. |
| Ograničenja | Jedan par početnog i završnog merenja sa po 16 primarnih ishoda. Ograničiti i evidentirati pozive pre slanja. Čuvati i neuspehe i izvršene retry/repair pozive. |

## Provera ustava

| Načelo | Pre istraživanja | Posle dizajna |
| --- | --- | --- |
| Obim i kompleksnost | Koristiti postojeći proizvod i odobreni MVP. | Jedan React panel i isti workflow. Iskoristiti postojeći skoring i ugovore. Bez novog treninga ili streaming infrastrukture. |
| TDD i ugovori | Kritične integracione granice proveriti prvo testovima. | RED slučajevi pokrivaju identitet snapshot-a, zastareli kontekst i nedostupnost izvora. Validirani API odgovori i postojeći fixture tok ostaju regresioni kriterijumi. |
| Dokazi i autoritet | LLM daje potkrepljeni nacrt. Analitičar odlučuje. | Proveriti tačnu verziju izvora, opseg alata i sačuvanu odluku. Za score i ovlašćenja koristi se deterministički kod. |
| Nezavisnost | Očekivanja i labele van izvršnog konteksta. | Izvršni ulazi odvojeni od offline reference. EV pre/posle predstavlja regresionu evaluaciju, a postojeći holdout ima sopstveni protokol. |
| Reprodukcija | Sačuvati stvarne nalaze i njihove verzije. | Dve faze i jedna označena završna revizija. Imenovani izvršilac iz US3 potvrđuje pokretanje iz čistog checkouta. |

Dizajn prolazi proveru obima i načela. Dostupan dataset snapshot, potvrđen model i završna revizija su preduslovi izvršavanja.

## Struktura projekta

- [Istraživanje i odluke](research.md)
- [Model podataka](data-model.md)
- [Ugovor integracije i evaluacije](contracts/evaluation.md)
- [Kandidati za 16 scenarija](contracts/ev-cases.md)
- [Uputstvo za izvršavanje i proveru](quickstart.md)

Implementacija dodiruje postojeće `web/src/pages/Cases.tsx`, `InvestigationPanel.tsx` i `web/src/investigation/` samo gde se prosleđuje i proverava dataset identitet. Backend ponovo koristi `backend/src/fraudlens/investigation/`, postojeći v2 Cases API i adapter za skorovani snapshot. `evals/capstone/` čuva verzionisani protokol, sintetičke ulaze i odvojene reference. `evals/results/` je lokalni izlaz. `evidence/tasks/` čuva pročišćene rezultate i mapu predaje. `tasks.md` nastaje u sledećem Spec Kit koraku.

## Redosled isporuke

| Korak | Ishod | Veza sa specifikacijom |
| --- | --- | --- |
| 1. Povezivanje i provera preduslova | Dokaz istog slučaja, transakcije, snapshot-a, skora i konteksta kroz Cases i istragu. Zaključan SDK i dozvoljeni model provereni zasebno pre evaluacije. | FR-001–002, SC-001 |
| 2. Zamrzavanje paketa | Konkretne vrednosti svih 16 ulaza, identiteti korpusa i početnih stanja, odvojena očekivanja i rubrika. Uslovi revizije, budžet, postupak ocene i eventualno nedostupni ulazi dokumentovani. | FR-003–004 |
| 3. Početno merenje i ciljana izmena | Jedan primarni ishod po EV slučaju. Trag objašnjava izbor jedne izmene. Dodati nameravani RED kada je u pitanju poslovno ponašanje, zatim GREEN i regresiju. Verzije svega što izmena dotiče dokumentovane. | FR-004–006, SC-002 |
| 4. Završno merenje | Ista matrica i kriterijumi na kandidatu za predaju. Živi browser prolaz, ponovljene negativne provere, uporedni rezultat sa imeniteljem 16. | FR-001–007, SC-001–003 |
| 5. Predaja | Jedna revizija, čist checkout, tri scenarija za odbranu i CAP-01–CAP-08 mapa sa stvarnim zapisima za četiri člana i objedinjenom potvrdom prema US3. | FR-007–008, SC-004 |

Priprema scenarija i determinističkih provera može da ide paralelno sa povezivanjem izvora. Stabilizacija i probni pozivi pripadaju pripremi. Početno merenje počinje tek kada se zamrznu ulazi i potvrde preduslovi. Cilj je paket do 24. novembra i demo 25. novembra.
