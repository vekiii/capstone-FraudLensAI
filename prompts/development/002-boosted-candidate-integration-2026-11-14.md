Radi u mom lokalnom FraudLensAI repozitorijumu na grani `model-implementations`. Nastavljamo od završenog `HistGradientBoosting` eksperimenta. Cilj je da Feature 002 iz kompletne baze sam izračuna skorove, izdvoji korisne slučajeve u okviru kapaciteta analitičara i prikaže ih u aplikaciji s provjerljivim objašnjenjima. Analitičar donosi konačnu odluku.

Prethodni eksperiment je na zamrznutoj validaciji dao **19 pozitivnih u prvih 20**, **AP 0,172129** i **20 simuliranih upozorenja, od kojih je 19 pozitivnih**. Refit starog stabla i R1–R3 dali su 0 pogodaka u prvih 20. Objavljeni run još koristi postojeći scorer i politiku `no_alert`. Nastavi kroz korake ispod i izvrši sve što možeš provjeriti lokalno.

### 1. Sačuvaj i reprodukuj kandidata koji je dao 19/20

- Pročitaj `AGENTS.md`, `next_work.md`, specifikaciju, ugovore i zadatke Feature 002, te `evidence/tasks/feature-002-boosted-validation.md`. Provjeri granu, HEAD i lokalne izmjene. Sačuvaj postojeći rad i koristi već implementirano poređenje.
- Provjeri da li je sačuvan kompletan pipeline iz eksperimenta. Ako postoje samo rezultati, ponovi isti trening nad postojećom `data/processed/feature-002-ibm-v8-rules-work.sqlite` bazom koristeći isti train uzorak, iste karakteristike, istu pripremu ulaza i iste parametre. Čitaj bazu u read-only režimu. Koristi postojeće kompletne `history-v1` snapshotove.
- Sačuvaj pipeline, uključujući pripremu ulaza, u novom lokalnom direktorijumu za artefakte. Zapiši porijeklo dataseta, verziju `history-v1`, redoslijed ulaza, parametre, verzije biblioteka, hash protokola, hash artefakta i **puni prag iz rezultata**. Vrijednost `0,9936687168` iz sažetka je zaokružena.
- Iz novog Python procesa učitaj provjereni lokalni artefakt i ponovi predikcije na istoj validaciji. Provjeri skorove prema rezultatu ponovljenog fita, 19 pogodaka među prvih 20 i 20 upozorenja sa 19 pogodaka. Ako reprodukcija odstupa, dijagnostikuj uzrok prije korišćenja kandidata. Drži artefakt, bazu i predikcije po transakciji van Gita.

### 2. Pripremi nezavisnu provjeru i izvrši je ako postoji odgovarajući izvor

- Provjeri dostupne izvore i evidenciju ranijih eksperimenata. Traži kompatibilan period od 24 sata čije oznake i rezultati nisu korišćeni za razvoj, uz dovoljnu prethodnu istoriju za računanje karakteristika. Postojeći IBM testni period je već obuhvaćen ranijim eksperimentom. Ako razmatraš drugi dataset ili release, prvo provjeri kompatibilnost mapiranja, semantiku oznaka i preklapanje transakcija.
- Prije uvida u oznake fiksiraj izvor, granice perioda, modele za poređenje, puni zamrznuti prag, budžet od 20 pregleda, redoslijed pri jednakim skorovima i kriterijum prihvatanja. Koristi već dogovoreni kriterijum ako postoji. Ako ga treba dogovoriti, predloži konkretnu vrijednost i zatraži odluku prije otvaranja oznaka. U međuvremenu nastavi tehničku pripremu.
- Na istim transakcijama izračunaj skorove kandidata, starog stabla i R1–R3. Sačuvaj predikcije i izabrane slučajeve prije spajanja s oznakama. Izvijesti koliko označenih transakcija svaki scorer nalazi u prvih 20 i koliko upozorenja i pogodaka daje njegova zamrznuta politika. **Prag koji je na validaciji dao 20 može na novom periodu dati više ili manje.**
- Ako kandidat dobro rangira, a prag probija kapacitet, utvrdi posljedicu i pripremi prijedlog za izbor najviše 20 slučajeva po periodu. Svaku novu politiku razvij i provjeri na razvojnim podacima. Sačuvaj nezavisni period za provjeru unaprijed fiksirane politike.
- Ako odgovarajući period trenutno nije dostupan, dokumentuj koje si izvore provjerio, šta nedostaje i tačan način pokretanja provjere čim se izvor obezbijedi. Status modela ostaje **istraživački kandidat**.

### 3. Pripremi i testiraj integraciju u Feature 002

- Pregledaj postojeći `ModelScorer`, provjeru manifesta, ugovor za objašnjenja i tok `score-run` → `activate-run` → API → UI. Pripremi unaprijed provjerljiv način da objašnjenje podrži baš boosted model na skali vraćenog skora. Ako postojeći ugovor traži izmjenu, prvo je evidentiraj u specifikaciji i zadacima.
- Implementiraj i provjeri podršku za kandidata u lokalnom, izdvojenom runu. Pokrij učitavanje tačnog artefakta, slaganje predikcije s učitanim pipelineom, vjernost objašnjenja, odbijanje nekompatibilnog artefakta i listu i detalj iz istog snapshot-a. Privatne oznake koristi isključivo u offline evaluaciji. Provjeri i postojeće rule i fixture tokove.
- U izdvojenom run storeu provjeri da se iz kompletnog runa slučajevi stvarno pojave u API-ju i UI-ju sa skorom, verzijom i objašnjenjem. Aktivni zajednički run zamijeni tek kad nezavisna provjera ispuni dogovoreni kriterijum i kad integracija prođe. Ako još nema nezavisnih podataka, završi tehničke provjere izdvojenog runa i evidentiraj šta je ostalo za aktivaciju.

### 4. Pripremi zatvaranje Feature 002

Sačuvaj ovaj prompt u `prompts/development/`. Dopuni `evidence/tasks/feature-002-boosted-validation.md` i povezanu evidenciju stvarnim komandama, izlaznim kodovima, hashovima, metrikama i rezultatima integracije. Ažuriraj `next_work.md`, relevantne zadatke i quickstart prema stvarnom stanju.

Pokreni ciljane testove i relevantnu backend i frontend regresiju, Ruff i `git diff --check`. Pripremi drugi član tima da pregleda pet objašnjenja za **T065** i nezavisno reprodukuje postupak za **T066**. Te zadatke zatvori tek kad postoje stvarni zapisi pregleda i reprodukcije. U **T067** evidentiraj koji su kriterijumi zadovoljeni i koji još čekaju dokaz. Ostavi izmjene lokalno za pregled prije pusha.

Na kraju mi vrati kratak pregled onoga što je stvarno izvršeno. Posebno navedi **da li se 19/20 reprodukuje iz sačuvanog artefakta, da li postoji nezavisan rezultat, da li API i UI prikazuju slučajeve iz novog runa i šta još tačno nedostaje za aktivaciju i zatvaranje Feature 002**.