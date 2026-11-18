# Feature 04 — šablon za prompt po fazi

## Kako se koristi

U Codex razgovoru koji ima pristup repozitorijumu pošalji:

> Iskoristi specs/004-simulation-and-prioritization/feature4_tasks_prompt.md i generiši mi prompt za poseban Codex chat za fazu 1, odnosno T001.

Kopiraj generisani prompt u novi razgovor koji ima pristup istoj ažuriranoj grani. Za nastavak prekinutog rada možeš tražiti „prompt za nastavak faze 3 iz aktuelnog handoffa“. Pri prelasku na drugi računar, povucite kroz Git poslednje izmene i zapise sa zajedničke grane.

| Faza | Trenutni zadaci | Cilj |
| --- | --- | --- |
| 1 | T001 | Zaključane zavisnosti i početna provera okruženja |
| 2 | T002–T004 | Sintetički scenario, odvojeni ishodi i validacija izvora |
| 3 | T005–T011 | Replay, API i prvi demo poređenja tri strategije |
| 4 | T012–T014 | Promena budžeta i praga, provere rubnih slučajeva |
| 5 | T015–T017 | Čuvanje i ponovno otvaranje podešavanja, pregled redosleda |
| 6 | T018–T021 | Završni testovi, pregled u pregledaču i predaja |

Opsege i zavisnosti uvek potvrdi prema aktuelnom [tasks.md](tasks.md).

## Instrukcije generatoru prompta

1. Radi samo čitanje. Posle važećih `AGENTS.md` instrukcija obavezno pročitaj korenski `next_work.md`. Zatim pročitaj `.specify/memory/constitution.md` i `tasks.md`, `spec.md` i `plan.md` iz ovog direktorijuma. Iz `quickstart.md`, `data-model.md`, `contracts/replay-v1.md`, `research.md` i evidence zapisa uzmi samo ono što je relevantno za fazu. Ako handoff nedostaje ili je nečitljiv, navedi to i utvrdi stanje iz preostalih izvora.
2. Izvedi tačan opseg iz broja faze ili navedenih taskova. Pri nastavku proveri checkboxove, kod i povezana evidence merenja pre nego što oceniš šta je završeno. U opseg nastavka uključi preostale delove nepotpunih taskova iz tražene faze. Ako je zahtev nejasan ili su faza i ID-jevi u sukobu, postavi jedno kratko pitanje.
3. Proveri granu i potreban Git diff samo radi konteksta. Ne menjaj fajlove, checkboxove ni Git stanje, ne pokreći testove, aplikaciju ili implementacione skill-ove.
4. Vrati **samo jedan Markdown code block** sa promptom na srpskom, spremnim za kopiranje. Popuni konkretne ID-jeve, preduslove, putanje i provere. Referenciraj dokumente iz checkout-a i izostavi nepopunjene slotove. Ako prompt sadrži unutrašnje code block-ove, koristi četiri backtick znaka za spoljašnji blok.

## Šta generisani implementacioni prompt mora da sadrži

- **Zadatak i granica**. Reci izvršiocu da implementira odabrani opseg. Navedi `004-simulation-and-prioritization`, broj faze, ID-jeve i šta znači završetak svakog zadatka. Proveri preduslove, završi sav nezavisan rad i zabeleži stvarne blokere. Stani na granici odabrane faze. `[P]` označava mogućnost paralelizacije.
- **Priprema**. Pročitaj `AGENTS.md` pa korenski `next_work.md` i navedene relevantne dokumente. Koristi `$env:SPECIFY_FEATURE_DIRECTORY = 'specs/004-simulation-and-prioritization'` u PowerShell sesiji. Ako je dostupan, primeni lokalni `speckit-implement` za zadati opseg. Čuvaj postojeće izmene i proveri da checkout odgovara traženom radu. Commit, push i merge zahtevaju zaseban korisnički zahtev.
- **Provere**. Za poslovno ponašanje koristi RED → GREEN → REFACTOR, potvrdi nameravani razlog pada i ponovi pogođene provere posle izmena. Za T001 koristi zaključanu instalaciju i postojeće ciljane testove iz zadatka. Postojeće prolazne provere tretiraj kao regresione. U fazi 6 koristi pune provere i uslove iz quickstarta. T020 čekiraj posle stvarnog pregleda člana tima i njegovog zabeleženog ishoda.
- **Granice Feature 04**. Koristi zamrznuti sintetički scenario. Oznake ishoda koristi tek posle odabira slučajeva i drži ih van javnog payload-a. Čuvaj postojeći tok Cases i njegov ugovor. Feature 02 adapter, Feature 05 infrastruktura i LLM integracija su izvan ovog opsega.
- **Trag rada**. Pre izmena sačuvaj primljeni prompt u `prompts/development/004-simulation-phase-NN.md`, sa dvocifrenim brojem faze. Pri nastavku dodaj datiranu dopunu i sačuvaj original. Vodi evidence na putanjama iz zadataka i kratku predaju u `evidence/tasks/feature-004-phase-NN-handoff.md`. Zabeleži početni commit, stvarne komande i ishode, nepotpune zadatke i prvi naredni korak.
- **Završetak**. Čekiraj zadatak kad je isporučen i propisana provera prođe. Posle svake završene celine osveži `next_work.md` sa stvarnim stanjem, linkovima na dokaze, blokadama i jednim narednim korakom. Pregledaj diff i pokreni `git diff --check`. U završnom odgovoru sažmi završene i otvorene zadatke, izvršene provere i gde je sačuvana predaja.
