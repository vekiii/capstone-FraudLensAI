# SC-002 — protokol dopunskog uparenog EV-06 testa

**Status** Definisan, čeka izradu i zamrzavanje materijalizovanog početnog stanja.

## Šta se meri

Istorijski `capstone-ev-v1` ostaje nepromenjen. Baseline `5974f94` ima
blokirani EV-06 jer njegov EV-01 nije proizveo sačuvani pokušaj za pregled.
Final `d8acc2a` ima prolaz EV-06 i provider ledger 19 → 19. Dopunski par
meri ponovno otvaranje kada stanje već postoji, pa izoluje ponašanje čitanja
od sposobnosti modela da prvi put generiše nacrt.

## Unapred definisan početni uslov

1. Napraviti **jedan** sintetički, potpuno sačuvani pokušaj lokalno sa testnim
   providerom na zajedničkoj kompatibilnoj šemi, pre oba merenja. Predložak je
   isti dataset slučaj i T098 run iz zamrznutog EV-01. Zadržati vezani korpus,
   kontekst, validiran nacrt, citiranu činjenicu i sačuvanu testnu odluku. Ako
   verzije ne čitaju isti validni seed, evidentirati neuporedivost.
2. U manifestu pre izvršavanja evidentirati SHA-256 checkpointovane SQLite
   kopije i relevantnih artefakata, case/run/attempt/report/review identitete,
   digest konteksta i citata, verzije izvršavanja i dve tačne Git revizije.
   Za svaku reviziju koristiti byte-identičnu radnu kopiju seed-a, sa zasebnim
   browser profilom i istim fiksnim uslovima.
3. Na `5974f94` i `d8acc2a` izvršiti isti React → Vite → FastAPI postupak
   ponovnog otvaranja. Provera koristi samo čitanje. Provider transport mora
   ostati nepozvan. Zabeležiti lokalni brojač pre i posle i stvarne HTTP ishode.
4. Prolaz zahteva istovetne identitete, obnovljeni nacrt i odluku, sadržaj
   citata koji odgovara zamrznutom dokazu i nula novih provider poziva. Za oba
   reda zabeležiti prvi stvarni ishod. Razliku objasniti tragom, uključujući
   moguće probleme sa kompatibilnošću.

## Tumačenje

Objaviti kao zaseban upareni dokaz za ponašanje ponovnog otvaranja. Sačuvati
postojeće 11/16 i 13/16 i istorijski blokirani red. Dopunski par ne ispunjava
samostalno originalni SC-002. Za zatvaranje po originalnom protokolu potreban
je uporediv ciklus svih 16 sa stvarno izvršenim EV-06 koji je nastao iz EV-01
iste faze. Za prihvatanje drugačijeg kriterijuma potrebna je evidentirana
odluka tima. Svako novo živo merenje ide preko postojećeg odobrenja obima.
