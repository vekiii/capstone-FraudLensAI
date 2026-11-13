Završi T017 za FraudLens AI na grani 002-data-and-risk-scoring.
Referentni commit završene faze 3 je 55306089b506458fcaec9b621f49c00dd971d46e.
Provjeri stvarni HEAD i sačuvaj zatečeni rad. Prvo pročitaj AGENTS.md,
next_work.md, T017–T019 u tasks.md, data-model.md, offline ugovor i
Prompt 3 iz prompts/development/002-implementation-prompts.md.
Sačuvaj ovaj originalni prompt u prompts/development/.

1. U specs/002-data-and-risk-scoring/contracts/data-and-scoring.md
   dovrši i zamrzni katalog karakteristika prema postojećem modelu:
   - pošiljalac: broj izlaznih transakcija, broj različitih primalaca,
     broj izlaznih transakcija u istoj valuti plaćanja i njihov Decimal zbir;
   - primalac: broj ulaznih transakcija, broj različitih pošiljalaca,
     broj ulaznih transakcija u istoj valuti prijema i njihov Decimal zbir;
   - trenutna transakcija: plaćeni iznos i valuta te samo opcioni
     Payment Format koji je obuhvaćen auditom izvora.

   Za svaku karakteristiku navedi tačan naziv, izvore polja, smjer,
   jedinicu, pravilo računanja, trenutak dostupnosti, ko je smije
   koristiti i šta znači nedostajuća ili nepoznata vrijednost.
   Koristi banku i račun zajedno za povezivanje istorije. Identifikatori
   služe povezivanju; ne ulaze u prediktore. Plaćenu i primljenu valutu
   obrađuj odvojeno.

2. Preciziraj vremenska pravila i pokrivenost.
   Zadrži [t−24h,t), uključenu donju i isključenu gornju granicu.
   Sve transakcije s istim vremenom računaju se iz iste ranije istorije
   i tek zatim ulaze u istoriju za kasnije događaje. Prvih 24 h od
   početka posmatranja služi samo kao kontekst. Razlikuj full,
   incomplete i unavailable. Prikaži razliku između mjerene nule
   za račun bez ranijih transakcija uz punu pokrivenost i nedostajuće
   istorije. Valjane činjenice ostaju u istoriji i kad je privatna
   oznaka nepodobna. Oznaka i njena podobnost ne ulaze u replay ni skor.

3. Zamrzni postojeći RulePolicy v1 prema ugovoru:
   - R1: najmanje 3 izlazne transakcije pošiljaoca → 0.35.
   - R2: najmanje 3 ulazne transakcije primaoca → 0.30.
   - R3: najmanje 3 prethodne izlazne transakcije u istoj valuti
     plaćanja i trenutni iznos najmanje 2× njihov prosjek → 0.35.

   Preciziraj Decimal poređenje bez preranog zaokruživanja, nedostupno
   R3 poređenje kod manjeg broja prethodnih transakcija i uslove pod
   kojima se skor uopšte može izračunati. Zadrži ordinalni skor kao
   zbir doprinosa. Pripremi ručno izračunate sintetičke primjere za
   granice vremena, isti timestamp, početak posmatranja, izmjerenu
   nulu, nepotpunu pokrivenost i pragove R1–R3, uključujući tačnu
   jednakost na pragu R3. Ne koristi evaluacione oznake za izbor
   karakteristika, pragova ili težina.

4. Provjeri primjere i usklađenost sa zahtjevima FR-005–FR-007.
   U evidence/tasks/feature-002-feature-rules.md zabilježi odluke,
   sintetičke primjere, stvarno izvršene provjere, pregledanu reviziju
   i link na originalni prompt. Ako mijenjaš offline ugovor čiji je
   raniji hash vezan za T007/T008, sačuvaj taj istorijski zapis i
   evidentiraj novi hash i šta obuhvata dopuna za T017. Označi T017
   kao završen samo ako je ugovor potpun i primjeri su provjereni.
   Ažuriraj tasks.md i next_work.md. Pokreni git diff --check.

Stani poslije T017. T018/T019 su naredni RED testovi, a implementacija
replaya počinje u T020. Za T017 koristi sintetičke primjere.
Bez ponovnog IBM importa, izmjene SQLite baze, commita ili pusha.
Vrati sažetak kataloga, pravila, provjera i status T017.
