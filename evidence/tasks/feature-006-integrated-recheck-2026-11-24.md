# Feature 006 · Provera na integrisanom kandidatu

24. novembar 2026. Aplikaciona osnova `527020c` i evaluacioni commit `218c35735d9337ffe81f1049f6aaaeb6820819e8`. Pokrenuto na Windowsu sa Python 3.14.10. [Zahtev](../../prompts/development/006-capstone-integrated-recheck-2026-11-24.md).

Rezultati iz istorijskog poređenja i kasnijeg uparenog merenja važe za svoje revizije. Njihov runner koristi `APP_MODE=dataset` i stare Cases rute. Preflight na trenutnoj aplikaciji odbio je taj `APP_MODE` sa `literal_error`. [Istorijsko poređenje](feature-006-before-after.md) · [Upareno merenje](feature-006-sc002-live-v2.md).

Novi prolaz koristio je aktuelne API i worker granice uz sledeće razlike u postavci.

- EV-02, EV-03, EV-05, EV-07, EV-09 i EV-10 zadržali su iste upite i korpus, uključujući isti pregledani EV-10 odlomak. Manifest i digest ulaza i seed-a provereni su pre slanja.
- EV-04 i EV-08 zadržali su istorijske T098 ID-jeve i proverene podatke. Novi harness proverio je binding kroz Investigation API i dataset kontekst. EV-08 i dalje koristi namerno nedostupan izvor istorije.
- EV-01 i EV-06 su varijanta za integrisani demo. Koriste stvarno objavljeni modelski bridge i `row:2959955`, umesto istorijskog T098 slučaja. EV-06 i dalje zavisi od tačno istog EV-01 pokušaja u svojoj fazi. Provera čuvanja i ponovnog čitanja ide kroz API. Browser proba na ovoj reviziji za novi slučaj može da usledi tek ako nastane sačuvana odluka.
- EV-11–EV-16 koriste postojeće determinističke integracione testove. Sedma CAP-06 provera budžeta i 12 testova validatora takođe su prošli. Prošlo je i 300 frontend testova i build.

Prvi živi prolaz imao je plafon od 19 zahteva, četiri workflow zahteva po istrazi, 4.096 izlaznih tokena, 45 s po zahtevu i 48.000 B ulaza. Sačuvano je 18 završenih HTTP 200 zahteva, 58.426 ulaznih i 10.695 izlaznih tokena. Sirovi trag i sledeći eksperiment ostaju u ignorisanoj `.cache/` putanji.

| EV | Ishod na integrisanom kandidatu `218c357` |
| --- | --- |
| EV-01 | Pad. Bridge binding i skor potvrđeni. Nacrt posle jedne popravke nije objavljen pre `budget_exhausted`. |
| EV-02 | Prolaz. Obe formulacije vratile isti otvoreni `sim-review/Review`, sa ovlašćenjem analitičara i obaveznim obrazloženjem. |
| EV-03 | Prolaz. Otvoren `sim-missing/Missingness`, primenljiv za dokumentovanje nedostajuće istorije. |
| EV-04 | Pad. Oba deterministička čitanja istorije su uspela. Četvrta rezervacija nije otišla provideru, nema nacrta koji citira istoriju. |
| EV-05 | Prolaz. `no_match`, bez izvora. |
| EV-06 | Blokiran. EV-01 iste faze nema objavljen nacrt i sačuvanu odluku. |
| EV-07 | Pad. Upit bez referenta dobio tri opšta odlomka uz `matched`. |
| EV-08 | Pad. Vezani kontekst stvarno ima nedostupnu istoriju, ali tok posle popravke završava kao `budget_exhausted`, bez nacrta ili zahteva za dopunu. |
| EV-09 | Prolaz. `no_match` za aktuelni srpski rok. |
| EV-10 | Prolaz. Tačan izmenjeni odlomak prosleđen je provideru i vraćen kroz ugovoreni izbor izvora. |
| EV-11 | Prolaz. Nedostajuće obavezno polje odbijeno pre kreiranja. |
| EV-12 | Prolaz. Nevalidan nacrt odbijen posle jedne popravke. |
| EV-13 | Prolaz. Nedostupan citat vraća kontrolisanu grešku uz očuvan ostali dokaz. |
| EV-14 | Prolaz. Nepoznat naziv alata odbijen pre izvršenja. |
| EV-15 | Prolaz. Kontrolisani timeout i ograničen retry. |
| EV-16 | Prolaz. Greška istorije zadržava prethodno vezane činjenice. |

**Ishod integrisane varijante** 11/16 prolaza, četiri pada i jedan blokiran scenario. Ovaj rezultat je zaseban zbog promenjene aplikacione granice i modelskog slučaja za EV-01/06.

## Prvi eksperiment `6d58dfb`

Eksperimentalna revizija prenosi ranije proverenu deduplikaciju činjenica o istoriji u kopiji za slanje modelu i pravilo za nedovoljno određen upit pri semantičkoj pretrazi. Git istorija izvornog koda je `d8acc2a` i `a814eb0`. Svi zapisi i reference koje čuva aplikacija ostaju punog oblika. U odnosu na prvi prolaz, eksperimenti koriste demonstracioni limit od osam workflow zahteva, 60 s po zahtevu i 8.192 izlazna tokena za istrage; granica ulaza iznosi 48.000 B. Učinak pojedinačnih promena ovim merenjem nije izolovan.

Poslato je 20 zahteva modelu. EV-01 je u API-ju objavio `ready_for_review` i vezao preporuku za edukativni `sim-review/Review`. Chrome je prikazao isti modelski skor `0.26731622570809`, otvorio tačnu činjenicu o iznosu i citiranu proceduru, osvežio stranicu i otvorio istu automatizovanu testnu odluku `request_more_information`. Broj zahteva ostao je pet, a digest SQLite kopije se nije promenio. EV-04 je objavio nacrt sa vezanim dokazima obe istorije, tačnim granicama prozora, brojem vraćenih i podobnih događaja i odgovarajućim valutnim sumama. EV-07 se uzdržao od odgovora. EV-08 je pravilno naveo da istorija nije dostupna i očuvao poznate činjenice, ali je vratio `ready_for_review` bez konkretnog zahteva za istorijom. Prema postojećoj rubrici EV-08 je pad. Ostali scenariji su imali prolazne ishode.

**Ishod prvog eksperimenta** 15/16, uključujući šest determinističkih kontrola. Reprodukcija u Chrome-u je automatizovana provera. Lokalni rezultat ne zamenjuje nezavisnu evaluaciju.

## Završni prolaz `3cfadcc`

Na istim integracionim ulazima i limitima ponovljeno je svih 16 provera. Opcioni `INVESTIGATION_REPORT_PROMPT=v7` zadržava v6 uputstvo i dodaje obavezu da se zatraži konkretan nedostajući dokaz kada istorija obe strane nedostaje i raspoložive činjenice ne potkrepljuju nijedan indikator ili alternativu. Zamrznuta rubrika je ostala ista.

Model `gpt-6-luna` obradio je 19 zahteva sa HTTP 200, ukupno 71.122 ulazna i 12.028 izlaznih tokena. Chrome je otvorio tačan iznos, citiranu proceduru i sačuvanu testnu odluku, proverio obrazloženje i ponovio proveru posle osvežavanja. Brojač je ostao 4/8, a digest SQLite kopije ostao je isti.

| Scenariji | Završni ishod |
| --- | --- |
| EV-01 i EV-06 | Isti skor i isti slučaj od procene do nacrta. Otvoren `sim-review/Review` sadržajno podržava preporuku. Posle osvežavanja vraćena ista odluka `request_more_information` i isti dokazi uz nula novih zahteva. |
| EV-02 i EV-03 | Obe EV-02 formulacije vraćaju `sim-review/Review`. EV-03 otvara `sim-missing/Missingness` i `sim-review/Review`. |
| EV-04 | Dva izvršena istorijska upita i vezani dokazi. Nacrt zadržava 17/40 i 17/36 događaja, skraćivanje, vremenske granice i odvojene valutne iznose. |
| EV-05, EV-07 i EV-09 | `no_match` u sva tri slučaja. |
| EV-08 | `needs_information`, uz izričit zahtev za istorijom pošiljaoca i primaoca. Nacrt čuva potvrđene činjenice i razlikuje nedostupnu istoriju od prazne. |
| EV-10 | Primljen je tačan pregledani i izmenjeni odlomak. Rezultat vraća primenljivi `sim-review/Review` iz tog korpusa. |
| EV-11–EV-16 | Šest prolaznih determinističkih negativnih kontrola. |

**Ishod završnog prolaza** 16/16 u adaptiranoj integracionoj proveri. Rezultat služi kao regresiona provera na poznatom paketu. Istorijsko merenje 15/16, nezavisna procena generalizacije i dogovoreni timski SHA vode se zasebno.

Na istoj reviziji kompletna backend regresija sa `PYTHONUTF8=1` dala je 1.476 prolaza i jedan preskočen test. Bez UTF-8 režima postojeći test koji čita srpski prompt oslanja se na Windows podrazumevano kodiranje.
