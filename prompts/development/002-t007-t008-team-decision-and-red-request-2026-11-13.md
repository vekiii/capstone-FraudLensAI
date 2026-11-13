# Feature 002 T007/T008 team decision and T009–T011 RED request

Received 2026-11-13 Europe/Belgrade. Exact original user instruction:

```text
Nastavi rad na FraudLens AI na grani `002-data-and-risk-scoring`. Na osnovu
dogovora tima usvajamo tehnički smjer za T007/T008 opisan u nastavku.
Evidentiraj ga kao zajedničku tehničku odluku tima, uz moju poruku kao
izvor potvrde. Ne dodjeljuj pojedinačne uloge i ne upisuj pojedinačne
potpise, odobrenja ili nalaze koje ti niko nije dostavio.

Prvo pročitaj `AGENTS.md`, `next_work.md`,
`evidence/tasks/feature-002-macos-handoff.md` i relevantne dijelove
`specs/002-data-and-risk-scoring/tasks.md`. Zabilježi stvarni HEAD i stanje
radnog stabla. Koristi `182d0b290c8819e602fc5d77e8df8e904228b032` kao
referencu prethodnog pregleda i sačuvaj zatečene lokalne izmjene.
Prije rada sačuvaj ovaj originalni prompt u `prompts/development/`.

1. Usaglasi pravila identiteta i verzionisanja za T007

   Uskladi `data-model.md` i `contracts/data-and-scoring.md` s tačnim
   bajtnim receptom i oglednim vektorima iz macOS handoffa. Zapiši domene,
   redoslijed polja, kodiranje, širine dužina i ordinala, redoslijed
   bajtova i dužinu izlaza.

   D/C identitet zavisi od namespacea, člana izvora i ordinala zapisa
   prije filtriranja. Koristi odvojene domene za D i C. Javni ID koristi
   prvih 128 bita SHA-256, a puni digest i ulazi služe za provjeru kolizija.
   `DatasetVersion` koristi `dv_` i puni SHA-256 izveden iz tri puna
   32-bajtna hasha izvora, mappinga i vremenske politike, prema receptu
   iz handoffa. Promjena samo oznake u sintetičkom primjeru mijenja
   `DatasetVersion`, uz iste D/C ID-jeve. Izmijenjeni IBM v8 CSV mora pasti
   na provjeri izvornog SHA-256.

2. Preciziraj hash mappinga i evidentiraj pregledanu verziju

   Računaj SHA-256 nad UTF-8 bajtovima mappinga nakon zamjene CRLF sa LF.
   Ostale bajtove sačuvaj. Odobreni hash veži za zaseban zapis o pregledu
   izvan mapping fajla, kako zapisivanje hasha ne bi mijenjalo sadržaj
   koji se hashira. Provjeri zavisne upotrebe samoreferentnog polja
   `approved_mapping_sha256` i ukloni ga uz usklađivanje tih upotreba.

   Razlikuj SHA-256 originalnih bajtova CSV-a, sirovi SHA-256 mapping
   fajla koji postojeći inspector prijavljuje, normalizovani SHA-256
   mappinga za `DatasetVersion` i postojeći hash vremenske politike.
   Sačuvaj istorijski manifest i zabilježi hashove konačnih pregledanih
   fajlova u novom zapisu. Ako se hashirani sadržaj mappinga kasnije
   promijeni, prethodna potvrda ostaje vezana za prethodnu verziju.

   Ponovi ogledne provjere. Ako usklađivanje promijeni sadržaj mappinga,
   izračunaj nove `dv_` vektore za konačne ulaze i jasno označi kojem
   mappingu pripadaju stari i novi vektori. Zabilježi komande, izlazne
   kodove i stvarne vrijednosti.

3. Evidentiraj zajedničku odluku za T007/T008

   U `evidence/tasks/feature-002-source-audit.md` i
   `evidence/tasks/feature-002-contract-review.md` zapiši šta je tim
   dogovorio, obrazloženje, datum, pregledanu reviziju ili radni diff,
   tačne hashove i rezultate provjera. Odvoji zajedničku odluku koju sam
   prenijela od tehničkih nalaza dobijenih uz Codex.

   Zadrži postojeći v2 format odgovora i kompatibilnost s Foundation v1.
   Opiši obaveze po komponentama, bez dodjele ljudi. Backend provjerava
   vezu detalja s aktivnim runom, snapshotom i verzijom dataseta. Frontend
   strogo dekodira v1/v2 i provjerava usklađenost liste i detalja.
   Investigation i priority/simulation koriste verzionisane operativne
   podatke uz postojeća pravila o porijeklu, objašnjenju i poretku.
   Privatne oznake ostaju izvan API-ja i operativnih ulaza. Importer
   primjenjuje tačne nazive valuta iz mappinga. Zabilježi koje provjere
   pripadaju kasnijoj integraciji.

4. Provjeri rezultat i nastavi prema stanju zadataka

   Pokreni ciljane provjere identiteta, hashiranja i v2 ugovora, relevantne
   regresije za promijenjene fajlove i `git diff --check`. U evidenciju
   upiši samo stvarno izvršene provjere i njihove rezultate.

   Provjeri pokrivaju li zajednička odluka i zabilježeni nalazi kriterijume
   za T007/T008. Ako pokrivaju, ažuriraj statuse u `tasks.md` i
   `next_work.md`, pa kreni s T009–T011 prema Promptu 2. Napiši i pokreni
   RED testove za parsiranje i računanje redova, stabilne identitete i
   ponašanje SQLite importa pri prekidu i ponavljanju. Zabilježi očekivani
   i stvarni razlog pada svakog testa. U ovom koraku stani nakon
   T009–T011, prije GREEN implementacije T012–T016.

   Ako neki kriterijum za T007/T008 ostane otvoren, dovrši tehnički rad
   koji možeš i navedi tačno koji nalaz ili odluka nedostaje. Označi
   zadatke prema dokazima i u `next_work.md` ostavi jedan konkretan
   sljedeći korak.

Na kraju vrati sažetak odluka, spisak izmijenjenih fajlova, stvarne
rezultate provjera i status T007–T011. Bez automatskog commit/push/merge.
```
