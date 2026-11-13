Završi Prompt 2 za FraudLens AI na grani 002-data-and-risk-scoring.
Uradi T015 i T016 do kraja, zatim commituj i pushuj cijelu završenu
fazu 3 na origin/002-data-and-risk-scoring. Prethodni plan za commit
nakon T014 zamijeni ovim redoslijedom.

Prvo pročitaj AGENTS.md, next_work.md, zadatke T015/T016, offline
ugovor i evidence/tasks/feature-002-import-identity.md. Provjeri
stvarnu granu, HEAD, lokalni diff i stanje remote grane. Sačuvaj
zatečene izmjene i ovaj originalni prompt u prompts/development/.

1. T015 — poveži import s lokalnim CLI-jem

   U backend/src/fraudlens/pipeline_cli.py dodaj lokalnu import
   komandu prema postojećem ugovoru. Ponovo iskoristi parser,
   identitet i SQLite repozitorijum iz T012–T014.

   Zahtijevaj odobreni mapping, eksplicitni namespace i očekivani
   SHA-256 izvora. Poveži dozvolu za import sa zapisom o odobrenju
   T007/T008 i provjeri da se pregledani hash mappinga poklapa.
   Razriješi postojeće inspect-only stanje prema tom odobrenju.
   Ne uvodi zaobilazni flag niti globalno omogućavanje importa.
   Sačuvaj ponašanje inspect komande i Foundation v1.

   U backend/tests/integration/test_data_store.py provjeri stvarni
   CLI ulaz za uspješan import i brojanje redova, kontrolisani
   neuspjeh s nenultim izlaznim kodom, ponavljanje i oporavak
   poslije prekinutog pokušaja. Uključi odbijanje izvora ili
   mappinga s pogrešnim hashom. CLI izvještaj neka sadrži zbirne
   rezultate bez sirovih redova i pojedinačnih privatnih oznaka.

2. T016 — uvezi stvarni IBM CSV i ponovi import

   Koristi postojeći data/raw/HI-Small_Trans.csv. Provjeri da mu
   je SHA-256 prije importa
   b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040.
   Smjesti novu SQLite bazu u ignorisanu putanju i provjeri slobodan
   prostor. Pokreni puni import preko T015 CLI-ja, pa istu komandu
   ponovi nad istom bazom. Sačekaj oba stvarna rezultata.

   Iz izvještaja i baze provjeri:
   - source_records = event_valid + event_rejected
   - event_valid = label_eligible + label_ineligible
   - label_eligible = positives + negatives
   - obrađeno je svih 5.078.345 zapisa iz deklarisanog izvora
   - drugi import daje isti DatasetVersion, bez dodatnih identiteta,
     duplikata ili izmjene postojeće kompletne verzije
   - SHA-256 originalnog CSV-a poslije oba importa je isti

   Zabilježi stvarne brojeve. Prethodni inspect je dokaz broja
   pročitanih zapisa; valjanost transakcija utvrđuje ovaj import.
   Ako run zakaže, dijagnostikuj problem i ponovi provjeru nakon
   ispravke. Sačuvaj stanje prethodne kompletne verzije.

3. Zatvori fazu 3 i objavi rezultat

   Pokreni ciljane CLI/import testove, cijeli backend suite, Ruff
   i git diff --check. U evidence/tasks/feature-002-import-identity.md
   upiši link na originalni prompt, komande, izlazne kodove, stvarne
   brojeve, hashove izvora i mappinga, DatasetVersion, verziju SQLite
   šeme i rezultate oba importa. Dodaj trajanje i veličinu baze.
   Ažuriraj tasks.md i next_work.md prema dokazima.

   Kad T015 i T016 prođu, pripremi commit za cijelu završenu fazu 3
   i prethodne lokalne izmjene T007–T014 koje joj pripadaju. Pregledaj
   staged spisak i git diff --cached --check. CSV, SQLite baza i
   journal/WAL fajlovi, generisani artefakti i nepovezane lokalne
   izmjene ostaju van commita.

   Commit poruka:
   feat(feature-002): complete and verify local dataset import

   Pushuj na origin/002-data-and-risk-scoring i potvrdi da remote
   pokazuje na isti SHA. Ako remote ima nove commitove, provjeri
   razliku i sačuvaj rad oba autora. Bez force pusha i bez mergea
   u main. Ako T015 ili T016 ostane otvoren zbog stvarnog blokatora,
   sačuvaj dokaze i vrati konkretan problem prije pusha.

Vrati status T015/T016, rezultate oba importa, testove, commit SHA,
GitHub link i potvrdu pusha. Stani na kraju faze 3.
