# Ugovor integracije i evaluacije

## Aplikaciona granica

- Cases koristi postojeći `GET /api/cases` i detalj odgovarajućeg snapshot-a. Podaci za analitičara su jedini izvor prikazanog identiteta i skora. Fixture identitet koristi `CASE-NNN`, dataset identitet koristi `C` i 32 heksadecimalna znaka prema postojećem ugovoru.
- Investigation panel prosleđuje isti `case_id` i `source_mode`. Odgovor liste istraga ili čitanja konteksta potvrđuje `snapshot_ref` i `context_revision` pre kreiranja. U dataset režimu neslaganje sa izabranim detaljem znači kontrolisano odbijanje i osvežavanje. Nema prebacivanja na fixture.
- Kreiranje koristi postojeći `POST /api/investigation/runs`. Čitanje pokušaja, citata i review zapis koriste postojeće zatvorene endpoint-e vezane za attempt i kontekst. Worker jedini preuzima posao. Ponovno otvaranje koristi sačuvano stanje. Sačuvati podršku za fixture i trenutnu proveru porekla mutacije.
- Ako EV slučaj koristi semantičku pretragu, koristi se postojeći `POST /api/knowledge/semantic-search` sa `query`, opcionim vezanim `corpus` i postojećim idempotency ključem. Prateći GET čita stanje, a ponovljeno čitanje ne troši budžet.

## Izvršavanje i ocenjivanje

1. Pre baseline-a sačuvati manifest sa 16 ID-jeva, digestima izvršnih ulaza i početnih stanja, hash-em offline referenci i verzijom kriterijuma. Potvrditi sve identitete i razdvojiti input od expected materijala.
2. Za obe faze koristiti identične ulaze, pravilo za reset ili seed, profile i provere. Ako je ciljana izmena profil, zabeležiti tačno njegovo polje, početnu i završnu vrednost. Sve druge kontrolne uslove zadržati. Opravdana odstupanja moraju biti vidljiva u poređenju.
3. Prvo evidentirati stvarne rezultate, stvarne pozive i reviziju. Zatim offline povezati očekivanja po EV ID-ju i hashu ulaza. Prolaz zahteva očekivano ponašanje i obavezni trag. Samo HTTP uspeh ili validan identifikator citata nisu dovoljni za sadržajni prolaz.
4. Ako je stvarno ponovljeno izvršavanje opravdano, zabeležiti prvi ishod i razlog. Zbir faze navodi `pass`, `fail`, `blocked` i `not_run` od 16. Prikaz pre i posle identifikuje poboljšanja, regresije i neuporedive redove.
5. Potvrditi da je izmena obrazložena konkretnim početnim tragom. Rezultat bez dokazivog poboljšanja navesti kao takav i zadržati nerešenu stavku otvorenu.
6. Za završnu reviziju povezati browser dokaz, svih 16 završnih rezultata, šest negativnih provera, uputstvo, reprodukciju i CAP mapu. Baseline zadržava zasebnu reviziju. Dokazi izrađeni posle provere mogu biti predati uz referencu na nepromenjeni testirani commit.
