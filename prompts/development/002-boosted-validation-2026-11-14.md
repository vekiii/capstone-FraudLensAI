Radimo na FraudLensAI, na zajedničkoj grani `model-implementations`. Želim da Feature 002 automatski boduje transakcije i izdvaja korisne slučajeve za analitičara, uz objašnjenje skora. Analitičar donosi konačnu odluku. **U ovom koraku implementiraj i izvrši kontrolisano poređenje na postojećoj IBM bazi.** Treba nam stvarni rezultat koji će pokazati da li prvo popravljamo model, ulazne karakteristike ili način izbora upozorenja.

Postojeće stablo tehnički radi, ali je na zamrznutoj validaciji imalo 0 označenih transakcija u prvih 20. Njegov najviši skor dijelilo je 18.909 transakcija. Važeća politika inkluzivnog praga uz budžet od 20 izabrala je `no_alert`. Raniji pokušaj razrješenja izjednačenja omjerom iznosa takođe je dao 0 pogodaka u prvih 20.

### 1. Provjeri lokalno stanje i pripremi eksperiment

- Pročitaj `AGENTS.md`, `next_work.md`, relevantne zahtjeve Feature 002 i postojeću evidenciju o rangiranju. Provjeri granu, HEAD i radno stablo. Referentni commit za pripremljeni patch je `c88c684f3b9be96b50124b067ff4848f518da4d9`. Sačuvaj postojeće lokalne i timske izmjene.
- Ako sam priložila `fraudlens-boosted-validation.patch`, pregledaj ga i primijeni nakon `git apply --check`. Ako je dio već primijenjen ili patch nije dostupan, iskoristi postojeći kod iz `fraudlens.train_phase5` i `fraudlens.evaluation` i dopuni samo ono što nedostaje za poređenje opisano ispod.
- Koristi postojeću `data/processed/feature-002-ibm-v8-rules-work.sqlite` bazu u read-only režimu. Provjeri da ima kompletnu `history-v1` izgradnju, da porijeklo dataseta odgovara protokolu i da se poklapaju broj redova i hashovi članstva train i validation particija. Ako baza nije na toj putanji, provjeri postoji li druga lokalna kopija sa istim datasetom i kompletnim snapshotovima. Koristi postojeće snapshotove kad su dostupni.
- Koristi zaključano projektno okruženje i `evals/protocols/feature_002_v1.json`. Očekujem 693.230 redova u postojećem determinističkom train uzorku i punu validaciju od 594.715 redova, od kojih je 588 pozitivnih. Ograniči čitanje privatnih oznaka na train i validation. Ako provjera porijekla ili članstva ne prođe, utvrdi tačan uzrok prije poređenja.

### 2. Pokreni stvarni trening i poređenje

Uporedi **R1–R3, refit postojećeg stabla dubine 5 s najmanje 500 primjera po listu i jedan `HistGradientBoostingClassifier`** na identičnim validacionim transakcijama. Za oba trenirana modela koristi istih 11 `history-v1` karakteristika, isti train uzorak i istu pripremu ulaza fitovanu samo na trainu. Za boosting koristi definiciju iz patcha. Ako ga implementiraš lokalno, koristi `max_iter=150`, `max_leaf_nodes=15`, `min_samples_leaf=100`, `learning_rate=0.1`, `class_weight='balanced'`, `early_stopping=False`, seed 42 i najviše dvije računske niti.

Za prvih 20 sortiraj po skoru silazno, zatim po stabilnom ID-ju transakcije uzlazno. Za upozorenja primijeni postojeću validacionu politiku inkluzivnog praga, s cijelim grupama izjednačenih skorova, budžetom od najviše 20 i mogućnošću `no_alert`.

Za svaki scorer zapiši AP, broj pogodaka u prvih 20, Precision@20, Recall@20, broj transakcija s najvišim skorom i da li izjednačenje prelazi 20. mjesto. Zasebno zapiši izabrani prag, broj upozorenja i broj pozitivnih među upozorenjima. Prije tumačenja kandidata provjeri da refit stabla i pravila reprodukuju referentnu validaciju, uključujući 0 pogodaka u prvih 20. Ako odstupaju, provjeri ulaze i implementaciju prije donošenja zaključka.

Ako je modul iz patcha dostupan, pokreni iz korijena repozitorijuma:

```sh
mkdir -p evals/results
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.compare_boosted_phase5 \
  --store data/processed/feature-002-ibm-v8-rules-work.sqlite \
  --protocol evals/protocols/feature_002_v1.json \
  > evals/results/boosted-validation.json
```

### 3. Zaključi šta rezultat opravdava

- **Ako kandidat ima više pogodaka u prvih 20 i više pogodaka među stvarnim upozorenjima od oba poređenja**, evidentiraj ga kao kandidata za dalje. Predloži kako unaprijed definisati prihvatljiv broj pogodaka i period na koji se odnosi budžet od 20, pa provjeriti rezultat na prethodno nepregledanim, kompatibilnim podacima. Za kasniju integraciju navedi kako će se provjeriti objašnjenje boosted modela, objava runa i prikaz u API-ju i UI-ju.
- **Ako se popravi vrh liste, a upozorenja ostanu na nuli**, utvrdi zašto prag nije izabrao koristan skup. Prikaži veličinu grupe izjednačenih skorova oko 20. mjesta i koliko transakcija uključuje najviši prag. Predloži konkretan eksperiment za izbor upozorenja pri istom kapacitetu.
- **Ako kandidat ne popravi broj pogodaka u prvih 20**, evidentiraj rezultat i predloži jedan naredni eksperiment. Prvi kandidat za novu karakteristiku je broj različitih pošiljalaca od kojih je isti primalac dobio uplatu u prethodnih sat vremena. Uzmite samo događaje iz `[t−1h,t)` i identitet računa vežite za banku i račun. Objasni šta ta karakteristika dodaje uz postojeći broj različitih pošiljalaca u 24 sata.

Ovaj prolaz je istraživački jer je validacija već pregledana. Objavljeni model i politika `no_alert` ostaju referenca dok ne pregledamo stvarne rezultate. Rad završi lokalnim izmjenama za pregled.

### 4. Sačuvaj dokaz i vrati rezultat

Sačuvaj ovaj originalni prompt u `prompts/development/`, stvarne komande, izlazne kodove, trajanje i agregatne rezultate u `evidence/tasks/feature-002-boosted-validation.md`, te konkretan naredni korak u `next_work.md`. Izvrši ciljane testove, Ruff i `git diff --check`. Jasno označi provjere koje zahtijevaju lokalni artefakt ili podatke koji nedostaju.

Na kraju mi vrati jednu tabelu za sva tri scorera i objasni **da li smo popravili rangiranje, da li smo dobili korisna automatska upozorenja i šta tačno radimo sljedeće**. Ako trening ne može krenuti, navedi tačnu komandu, izlazni kod i ulaz koji nedostaje.