# Original development prompt — validation review queue

Na grani model-implementations uradi jedan istraživački eksperiment
s redom za pregled od najviše 20 transakcija. Koristi isključivo
zamrznutu validation particiju za FraudLens Feature 002.

Pročitaj AGENTS.md, next_work.md, T029 protokol i prethodnu validacionu
dijagnostiku u evidence/tasks/feature-002-model-metrics.md. Sačuvaj
zatečene izmjene i ovaj prompt u prompts/development/. Iskoristi
postojeći dijagnostički skript, provjereni model i history-v1 bazu
otvorenu read-only.

1. Prije računanja ishoda evidentiraj ovo pravilo redoslijeda:
   - Primarni ključ je postojeći skor scorera, silazno.
   - Kod jednakog skora prednost imaju transakcije za koje se može
     izračunati omjer trenutnog plaćenog iznosa i prosječnog ranijeg
     plaćenog iznosa istog pošiljaoca u istoj valuti u [t−24h,t).
   - Omjer računaj samo uz najmanje 3 prethodne transakcije u istoj
     valuti i strogo pozitivan raniji zbir. Poredi omjere silazno,
     bez zaokruživanja koje bi promijenilo redoslijed. Nedostupan
     omjer u istoj grupi ide iza dostupnih.
   - Preostala izjednačenja razriješi ID-jem transakcije uzlazno.
   - Uzmi prvih 20. Oznake koristi tek nakon što je lista formirana.
     Oznake, budući događaji i raw redoslijed ne smiju uticati na izbor.

2. Na istim podobnim validacionim redovima uporedi četiri kombinacije:
   stablo i R1–R3, svako sa starim ID redoslijedom i novim sekundarnim
   redoslijedom. Za svaku vrati broj odabranih i pozitivnih, Precision@20
   i Recall@20. Provjeri da stari redoslijed reprodukuje 0 pozitivnih
   kod oba scorera. Zabilježi koliko je odabranih imalo dostupan omjer
   i potvrdi da ponovljeno pokretanje daje istih 20 ID-jeva istim redom.

3. Vrati tabelu i odgovori konkretno:
   - Da li je novi redoslijed pronašao više pozitivnih od starog?
   - Da li je stablo uz isto sekundarno pravilo pronašlo više
     pozitivnih od R1–R3 pri istih 20 pregleda?

U evidence/tasks/feature-002-model-metrics.md dodaj pravilo, komande,
izlazne kodove, rezultate i ograničenje da je ovo istraživački nalaz
na već pregledanoj validaciji. Koristi samo ovo unaprijed navedeno
pravilo, bez naknadnog isprobavanja varijanti na osnovu rezultata.

Zadrži postojeći model, zamrznuti protokol, no_alert politiku i benchmark.
Ova lista od 20 služi eksperimentu. Bez novog treninga, pristupa testnim
oznakama ili predikcijama, izmjene baze, commita ili pusha.
