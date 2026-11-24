# Specifikacija Feature 06 — Evaluacija sistema i priprema predaje

- **Grana** `006-capstone-evaluation`
- **Datum** 21. novembar 2026.
- **Status** Nacrt za pregled tima
- **Polazna verzija** `71f34dd`, React integracija istrage koju su mentori pregledali
- **Povod** Formativni pregled od 20. novembra. Predaja dokaza do 24. novembra, demo 25. novembra. [Sažetak zahteva i polazno stanje](../../evidence/tasks/feature-006-specification.md)

## Korisničke priče i provere *(obavezno)*

### US1 — Analitičar završava živu istragu (P1)

Analitičar u postojećoj aplikaciji otvara slučaj nastao iz označene transakcije, pokreće istragu sa stvarnim modelom, proverava dokaz i sam donosi odluku.

**Nezavisna provera**. Na kandidatu za predaju pokrenuti uspešnu istragu i još jednu sa nedovoljnim dokazima. Proveriti poreklo skora, izvor tvrdnje i sačuvanu odluku posle osvežavanja.

1. Ako označena transakcija ima objavljen skor i dostupne dokaze, aplikacija prikazuje isti slučaj i poreklo skora, prelazi kroz stanja obrade, proverava strukturisani izlaz i prikazuje nacrt za pregled. Citirani odlomak ili činjenica iz slučaja mogu se otvoriti i sadržajno potkrepljuju proverenu tvrdnju.
2. Ako nedostaje obavezan podatak ili nema dovoljno primenljivih dokaza, aplikacija jasno navodi šta nedostaje i prikazuje zahtev za dopunu ili kontrolisano stanje. Sačuvani kontekst zadržava nepoznate vrednosti.
3. Kada analitičar sačuva odluku sa obrazloženjem, može da je ponovo otvori posle osvežavanja sa istim slučajem i nacrtom. Izvršavanje istrage ostavlja trag najmanje jednog determinističkog alata koji koristi validirane argumente i vraća proverljiv rezultat u dozvoljenom opsegu.

### US2 — Tim meri isti tok pre i posle ciljane izmene (P1)

Tim evidentira stvarni početni rezultat za 16 unapred definisanih slučajeva, bira jednu ciljanu izmenu na osnovu traga greške ili slabosti i ponavlja provere sa istim ulazima.

**Nezavisna provera**. Nezavisni pregledalac može iz tabele da poveže svaki ulaz i očekivanje sa stvarnim početnim i završnim ishodom, kao i sa dokazom koji objašnjava izmenu.

1. Postoje tačno 16 jedinstvenih ID-jeva, od EV-01 do EV-16. Svaki ima fiksirane ulaz i početno stanje, očekivanje, režim provere i pravilo prolaza pre početnog merenja.
2. Za EV-01–EV-10 aplikacija je podešena za stvarni model. Opravdano zaustavljanje pre poziva modela ima razlog i trag izvršavanja. EV-11–EV-16 koriste determinističke provere ili simulirane kvarove prema slučaju.
3. Završni prolaz ponavlja iste ulaze, kriterijume i uporedive uslove. Rezultat zadržava neuspehe i blokade, pokazuje razliku po slučaju i povezuje ciljanu izmenu sa početnim tragom. Ako je ispravljen sam slučaj, sačuvati obe verzije i izdvojiti njihov rezultat iz direktnog poređenja, osim ako su oba merenja ponovljena na istoj ispravljenoj verziji.

### US3 — Izvršilac reprodukuje predaju (P1)

Imenovani član tima iz čistog checkouta pokreće označenu verziju i nalazi dokaze za timsku i individualnu ocenu. Za ovu predaju Vedran Mitic preuzima izvođenje jer je planirani izvršilac zauzet. Odluka od 22. novembra 2026. dopušta da izvršilac bude prethodni učesnik. [Dopuna zahteva](../../prompts/development/006-capstone-phase-05.md).

**Provera iz čistog checkouta**. Imenovani izvršilac pokreće aplikaciju iz uputstva, proverava sačuvani tok i nalazi svih osam CAP stavki na istoj označenoj reviziji.

1. Završni živi prolaz, završni EV rezultati i negativne provere referenciraju isti commit ili tag za predaju. Početno merenje zasebno navodi reviziju i podešavanja koja su stvarno korišćena.
2. Uputstvo iz čistog checkouta obuhvata preduslove, dostupnost potrebnih lokalnih artefakata, pokretanje aplikacije i početni slučaj. Imenovani izvršilac beleži stvarnu reprodukciju i sve preostale prepreke.
3. Za probnu odbranu su spremni uspešna istraga, stanje sa nedovoljno dokaza ili potrebom za dopunom i kontrolisana greška. Predaja povezuje doprinos, odluku i stvarnu proveru svakog od četiri člana sa predatom verzijom. Vedran Mitic za ovu predaju preuzima i potvrđuje zajednički pregled sva četiri zapisa jer ostali članovi rade druge zadatke. Postojeći pregledi rada kolega navode se prema dostupnom dokazu. [Dopuna zahteva](../../prompts/development/006-capstone-phase-05.md).

### Rubni slučajevi

- Nedostupan model, neizvršen slučaj i neuspešan slučaj imaju zasebne statuse. Pad ili blokada ostaju u evidenciji i zbiru svih 16 slučajeva. Testni provider se u izveštaju označava kao testni.
- Činjenice o slučaju, skoring i izvori imaju različito poreklo. Očekivanja, oznake ishoda i evaluacione beleške ostaju van modelskog ulaza i pretrage.
- Važeći identifikator citata uz nepodržanu tvrdnju predstavlja neuspeh sadržajne provere. Za ključeve, sadržaj koji ne pripada slučaju i neovlašćene radnje primenjuje se zatvoren opseg.
- Ako skoring, odobren pristup stvarnom modelu ili verzionisani ulazi nedostaju, odgovarajući kriterijumi ostaju otvoreni. Sintetičke probe i postojeće evaluacije komponenti mogu poslužiti za pripremu.

## Zahtevi *(obavezno)*

### Funkcionalni zahtevi

- **FR-001** (CAP-02) Predaja mora da pokaže povezani tok od označene transakcije i skora sa verzijom i poreklom do istrage kroz postojeću aplikaciju sa stvarnim modelom. Zabeležiti stvarni provider, verziju modela i identitet slučaja.
- **FR-002** (CAP-03, CAP-04) Sistem mora da prikaže status obrade, validiran nacrt i otvaranje tačno citiranog dokaza. Živi prolaz mora da pokaže sadržajnu vezu citata i tvrdnje, kontrolisano ponašanje pri nedovoljno dokaza i izvršen deterministički alat sa validiranim argumentima. Konačna odluka pripada analitičaru i njen zapis ostaje dostupan posle osvežavanja.
- **FR-003** (CAP-05) Tim mora da zamrzne 16 evaluacionih slučajeva iz matrice ispod. Za svaki sačuvati verziju ulaza i početnog stanja, očekivanje i pravilo ocene. Odvojiti očekivanja od ulaza za izvršavanje i čuvati ih van konteksta i pretrage.
- **FR-004** (CAP-05) Za svaki od 16 slučajeva sačuvati stvarni početni i završni ishod, režim, status, trag i reviziju. Sačuvati verzije konfiguracije, korpusa, ulaza i relevantnih artefakata. U oba merenja koristiti istu rubriku i fiksne slučajeve, a svako odstupanje navesti.
- **FR-005** (CAP-05) Jedan konkretan početni trag mora da obrazloži ciljanu izmenu. Poređenje mora da pokaže šta se promenilo na pogođenom slučaju i da prijavi eventualne regresije na ostalim slučajevima. Ovaj skup služi poređenju pre i posle, dok se postojeći nezavisni holdout koristi u granicama sopstvenog protokola.
- **FR-006** (CAP-06) Završna revizija mora da ima stvarne negativne provere za nevalidan ulaz ili izlaz, nedostupan izvor, izlazak iz opsega, nedostupnost modela i grešku alata. Objavljeni dokazi moraju biti očišćeni od tajni i privatnih podataka. Test scenariji i simulirani kvarovi moraju biti kontrolisani.
- **FR-007** (CAP-07) Priložiti jedan završni commit ili tag, komande proverene iz čistog checkouta, evidenciju potrebnih preduslova i rezultate završnog prolaza i negativnih provera sa te revizije. Mapa CAP-01–CAP-08 mora da pokaže dokaze i status za svaku stavku.
- **FR-008** (CAP-01, CAP-08) U mapi povezati specifikaciju, tehnički dogovor i glavne kriterijume prihvatanja. Za svakog od četiri člana zabeležiti suštinski tehnički doprinos, odluku, njenu proveru i vezu sa glavnim tokom. Priložiti dokumentovane primere pregleda rada kolega gde postoje i stvarnu objedinjenu potvrdu imenovanog pregledaoca iz US3.

### Matrica EV-01–EV-16

Ovo je raspodela scenarija i očekivanih ishoda. Konkretne identifikatore slučajeva, sadržaj ulaza i verzije podataka treba fiksirati pre prikupljanja prvog rezultata. Koristiti podržane ulaze postojećeg toka.

| ID | Provera | Očekivani ishod |
| --- | --- | --- |
| EV-01 | Tipična istraga označene transakcije | Validiran nacrt stiže do pregleda i prikazuje proverljiv dokaz. |
| EV-02 | Parafraza relevantnog upita ili tekstualnog konteksta | Isti relevantni izvori i materijalne činjenice ostaju dostupni. |
| EV-03 | Dodatno ograničenje u podržanom ulazu | Izveštaj poštuje ograničenje i zadržava primenljive dokaze. |
| EV-04 | Slučaj koji zahteva deterministički alat | Trag potvrđuje poziv i upotrebu rezultata u istom slučaju. |
| EV-05 | Pretraga bez relevantnog poklapanja | Aplikacija prijavljuje odsustvo primenljivog izvora. |
| EV-06 | Nastavak prethodno sačuvane istrage | Nastavak zadržava identitet pokušaja, kontekst i vezane dokaze. |
| EV-07 | Dvosmislen kontekst | Izveštaj beleži neizvesnost ili traži razjašnjenje. |
| EV-08 | Nedostaje obavezan podatak | Zabeleženo je šta nedostaje i zašto tok traži dopunu ili staje. |
| EV-09 | Tvrdnja za koju korpus nema potporu | Tvrdnja se izostavlja ili je jasno označena kao nepotvrđena. |
| EV-10 | Nepouzdani izvor pokušava da proširi opseg | Instrukcija ostaje podatak. Zabeleženo je očuvanje opsega. |
| EV-11 | Nevalidan serverski zahtev | Kontrolisana greška i trag da model nije pozvan. |
| EV-12 | Nevalidan strukturisani izlaz modela | Nevalidan nacrt se ne objavljuje. Ishod popravke ili greške je zabeležen. |
| EV-13 | Nedostupan citirani izvor | Izvor se prikazuje kao nedostupan bez zamene neproverenim dokazom. |
| EV-14 | Nedozvoljen alat ili opseg | Zaštita odbija zahtev pre izvršenja van opsega. |
| EV-15 | Timeout ili limit servisa | Kontrolisan ishod sa vidljivim statusom i zabeleženom potrošnjom. |
| EV-16 | Greška alata | Stanje ili ograničenje objašnjava kvar i čuva tačnost prikazanih činjenica. |

### Ključni entiteti

- **Evaluacioni slučaj**. EV identitet, ulaz, početno stanje, verzija podataka, očekivanje, režim i pravilo ocene.
- **Zapis izvršavanja**. Faza merenja, revizija, konfiguracija, stvarni ishod, status i trag za jedan EV slučaj.
- **Kandidat za predaju**. Označena revizija, provereni preduslovi, verzije izvora i dokazi iz završnog prolaza.
- **Mapa dokaza**. CAP stavka, provera, revizija, veza do dokaza i status. Za CAP-08 uključuje člana i njegov stvarni doprinos.

## Kriterijumi uspeha *(obavezno)*

### Merljivi ishodi

- **SC-001**. Na završnom commitu zabeležen je bar jedan živi prolaz označene transakcije do validiranog nacrta i obnovljive odluke, sa najmanje jednim sadržajno proverenim citatom i jednim izvršenim determinističkim alatom. Zabeležen je i slučaj nedovoljnih dokaza.
- **SC-002**. Svaki od 16 fiksiranih ID-jeva ima stvarni početni i završni rezultat. Bar jedna izmena ima vezu do početnog traga i ponovljene provere. Uporedni prikaz sadrži promene, regresije i ukupne ishode sa imeniteljem 16.
- **SC-003**. Izvršeno je svih šest završnih negativnih provera EV-11–EV-16 na završnom commitu. Rezultati jasno beleže da li je očekivana kontrola prošla. Za prihvatanje sve predviđene kontrole moraju proći.
- **SC-004**. Imenovani izvršilac iz US3 reprodukovao je pokretanje iz čistog checkouta, svih osam CAP stavki ima evidentiran status, a zapisi o doprinosima sva četiri člana imaju objedinjenu potvrdu prema US3. Tri scenarija za odbranu koriste isti označeni commit.

## Pretpostavke i zavisnosti

- Lokalna grana polazi od verzije React istrage koju su mentori pregledali. Konačni kandidat nastaje kada se na istoj reviziji poveže odobreni izvor skora i proveri stvarni model. Poreklo skora mora biti vidljivo. Završen trening konkretnog kandidata se ne pretpostavlja.
- Režim sa testnim providerom služi za lokalnu pripremu i simulirane kvarove. Živi rezultati zahtevaju dostupnu, pripremljenu integraciju sa stvarnim modelom i ovlašćen režim korišćenja. Otvaranje ove specifikacije ne izvršava evaluaciju.
- Feature 06 koristi sintetičke podatke i postojeći interfejs i workflow. Streaming, novi frontend i razvoj novog modela nisu deo ovog obima. Ranije metrike skoringa i Feature 03 evaluacije služe kao dokaz za komponente.
