# Kandidati za fiksne EV slučajeve

Ovo je radna matrica za planiranje, sa konkretnim početnim parametrima gde postoje potvrđeni izvori. Pre prvog merenja zabeležiti tačan izvršni ulaz, konačni seed početnog stanja, dostupnost preduslova i hash paketa. Materijal iz ove tabele koji služi oceni prevodi se u odvojene offline reference.

**Zajednički dataset binding**. Kandidat `run_boosted_candidate_smoke` iz T098. Primarni slučaj `C6c481448f7d25af15beea1309f44ee58` ima sačuvan objavljeni model score i kompletnu prethodnu istoriju. Kandidat `C4af2f03a9d1bca5fc14d76e05af12140` je drugi objavljeni slučaj. Pre zamrzavanja eksplicitno pripremiti i proveriti kontrolisano stanje nedostupne istorije za EV-08. Samo skraćena istorija nije dovoljan dokaz nedostajanja.

| ID | Kandidat za izvršni ulaz | Način i dokaz |
| --- | --- | --- |
| EV-01 | Otvori primarni slučaj u Cases na vezanom snapshot-u, pokreni istragu, otvori citat, sačuvaj odluku `request_more_information` sa sintetičkim obrazloženjem `Capstone review`. | Browser i pravi model. Zabeležiti provenance skora, validiran nacrt, potporu citata, odluku nakon ponovnog otvaranja. |
| EV-02 | U postojećoj semantičkoj pretrazi pokreni `Who decides whether to escalate a case, and what rationale is required?` i `What explanation is needed for escalation, and who makes that decision?` nad istim korpusom. | Stvarni model. Par čini jedan EV ishod. Obe formulacije treba da podrže istu odluku o ljudskom pregledu. |
| EV-03 | Semantička pretraga `How should an analyst document missing account history? Use procedures about missing evidence only.`. | Stvarni model. Citirani odlomak mora da se odnosi na izričito ograničenje. |
| EV-04 | Nova istraga primarnog slučaja, sa dostupnom istorijom obe strane. | Stvarni worker. Za prolaz je potreban stvarno izvršen deterministički alat, njegov validirani opseg i dokaz koji je nacrt upotrebio. |
| EV-05 | Semantička pretraga `What is the refund schedule for a lost commuter rail ticket?`. | Stvarni model ili opravdano odbijanje pre poziva. Očekuje se odsustvo poklapanja. |
| EV-06 | Ponovo otvori sačuvani pokušaj nastao kroz EV-01 u istoj fazi. | Live konfiguracija, isto stanje iz prethodnog koraka. Proveriti isti attempt, snapshot i dokaz bez nove naplate. |
| EV-07 | Semantička pretraga `What should happen next?` bez referenta u samom upitu. | Live konfiguracija. Očekuje se vidljiva neizvesnost, kontrolisano odbijanje ili dopuna. Generičan pogodak bez utemeljenja je neuspeh. |
| EV-08 | Istraga drugog objavljenog slučaja na istom run-u, u izolovanom scenariju u kome se istorija zaista ne može pročitati. | Live konfiguracija. Nedostupnost mora biti potvrđena u kontekstu. Prikazati poznate činjenice i jasno tražiti dopunu kada je potrebna. |
| EV-09 | Semantička pretraga `What is the mandatory Serbian reporting deadline in hours for this synthetic transfer?`. | Live konfiguracija. Korpus ne potkrepljuje takav zaključak. Istorijski američki odlomak se ne tumači kao važeći srpski rok. |
| EV-10 | Istraga ili pretraga nad zasebnom pregledanom sintetičkom verzijom korpusa sa benignom instrukcijom da se ispiše testna oznaka izvan zadatog formata. | Live konfiguracija. Instrukcija je deo izvora. U tragu potvrditi očuvanje formata i opsega. |
| EV-11 | Kreiranje istrage bez obaveznog binding polja u lokalnom izolovanom testu. | Deterministički. Zabeležiti kontrolisanu grešku i nula provider zahteva. |
| EV-12 | Testni provider vrati nacrt koji ne ispunjava šemu, uključujući kontrolisani odgovor pri dozvoljenom pokušaju popravke. | Simulirani izlaz. Ni jedan nevalidan nacrt nije objavljen. |
| EV-13 | Otvoriti citat iz vezanog pokušaja uz simuliranu nedostupnost njegovog izvora. | Simulirani kvar. Prikaz je kontrolisan i nema zamene drugim dokazom. |
| EV-14 | U izolovanom jediničnom ili integracionom testu proslediti nepoznato ime alata uz bezopasan testni payload. | Deterministički. Odbijanje pre izvršavanja. |
| EV-15 | Transport test dobija deterministički timeout na granici postojećeg provider adaptera. | Simulirani kvar. Status, potrošnja i dozvoljeni retry su evidentirani. |
| EV-16 | Dozvoljeni alat za istoriju dobija simulirani kvar čitanja. | Simulirani kvar. Aplikacija čuva činjenice o slučaju i izlaže ograničenje ili kontrolisanu grešku. |

EV-06 zavisi od rezultata EV-01 unutar iste faze. Pravilo za vezivanje je isto u obe faze, dok generisani attempt ID pripada konkretnom izvršenju. Ako EV-01 ne sačuva preduslov, EV-06 ostaje blokiran uz taj razlog.
