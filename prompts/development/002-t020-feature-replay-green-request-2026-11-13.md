Nastavi fazu 4 projekta FraudLens AI na grani 002-data-and-risk-scoring.
Implementiraj T020 i provedi T018/T019 iz RED u GREEN.

Prvo pročitaj AGENTS.md, next_work.md, T017–T020 u tasks.md, data-model.md,
lokalno dopunjeni offline ugovor i evidence/tasks/feature-002-feature-rules.md.
Sačuvaj nekomitovane T017–T019 izmjene i ovaj prompt u prompts/development/.
Ponovi postojeći RED skup i zabilježi stvarni početni rezultat.

1. Implementiraj feature replay u backend/src/fraudlens/feature_history.py.
   Koristi svih 11 karakteristika iz zamrznutog T017 kataloga. Za događaj
   u vremenu t koristi [t−24h,t). Izračunaj karakteristike za cijelu grupu
   događaja s vremenom t prije nego što bilo koji od njih dodaš u istoriju.
   Rezultat mora biti determinističan i za drugačiji redoslijed ulaza.

   Povezuj račune kombinacijom banke i računa. Odvojeno agregiraj plaćene
   i primljene iznose po valuti, uz tačnu Decimal aritmetiku. Zadrži prvih
   24 sata kao kontekst. Razlikuj full, incomplete i unavailable te
   izmjerenu nulu od nedostajuće istorije.

   Replay neka koristi operativne činjenice, uključujući valjane događaje
   čije oznake nisu podobne za evaluaciju. Primijeni zatvoren katalog i
   pravila porijekla iz T017. Identifikatore koristi za povezivanje i
   vezivanje rezultata, bez prosljeđivanja u prediktore. Provjeri zabranu
   oznaka, njihovih kopija, budućih agregata i nedozvoljenih polja.

2. Poveži lokalnu komandu build-features u pipeline_cli.py i spremanje
   snapshotova u data_store.py prema ugovoru. Čitaj samo kompletan,
   kompatibilan DatasetVersion. Djelimično izračunati snapshotovi ne smiju
   postati dostupni poslije greške ili prekida. Sačuvaj prethodne kompletne
   rezultate. Provjeri CLI i spremanje na privremenoj sintetičkoj SQLite
   bazi, uključujući odbijanje nekompletne ili nekompatibilne verzije.
   Izbjegni učitavanje cijelog IBM skupa u memoriju kroz CLI.

3. Pokreni svih 50 T018/T019 testova, ciljane CLI/SQLite provjere, cijeli
   backend suite, Ruff i git diff --check. Ako treba ispraviti test,
   obrazloži promjenu prema T017 ugovoru i sačuvaj njegovu pokrivenost.

   U evidence/tasks/feature-002-feature-rules.md zabilježi originalni
   prompt, stvarne komande, izlazne kodove, RED/GREEN rezultate i šta je
   provjereno na sintetičkim podacima. Ažuriraj tasks.md i next_work.md
   prema dokazima. Vrati status T020, rezultate i prvi sljedeći zadatak.

Stani poslije T020. T021 je naredni RED korak za v2 scorer. Bez treniranja
modela, punog IBM replaya, izmjene postojeće IBM baze, commita ili pusha.
