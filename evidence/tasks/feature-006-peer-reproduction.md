# Feature 06 · T021 · Reprodukcija iz čistog checkout-a

**Status: završeno prema izmenjenom US3.** Vedran Mitic je reprodukovao tok na kandidatu
`d8acc2a335d95e2402f586006925949f4d9f7739`. Nalaz pripremiti prema
[quickstart-u](../../specs/006-capstone-evaluation/quickstart.md).
Vedran je 22. novembra 2026. odobrio promenu jer je prvobitno planirani
izvršilac zauzet. Ova predaja koristi njegovu stvarnu reprodukciju,
uz zabeleženo učešće u ranijoj pripremi Feature 06.
[Dopuna zahteva](../../prompts/development/006-capstone-phase-05.md).
Aktuelna provera alata, lokalnih fajlova i korpusa evidentirana je u
[predaji faze](feature-006-phase-05-handoff.md). Raniji automatizovani
[browser tok](feature-006-dataset-smoke.md) i [živi final](feature-006-final-live.md)
su referentni dokazi.

## Lokalna proba za Vedrana

Na ovoj mašini pripremljen je zaseban checkout u
`.cache/006-t021/vedran-checkout`. Tehnička priprema je proverena:
isti T098 transfer digesti, izgrađen novi indeks sa 5.078.345 redova,
proveren Cases/Investigation payload za oba slučaja, zdravlje API-ja
direktno i kroz Vite na objavljenom `run_boosted_candidate_smoke`.
To su automatizovani rezultati pripreme. Browser nalaz je zabeležen ispod.
[Komande, izlazi i lokalni digest](feature-006-phase-05-handoff.md#nastavak-istog-dana--promena-izvršioca-i-priprema).

Iz korena glavnog repozitorijuma
pokreni lokalni launcher. Koristi testni provider i svež lokalni store.
Prvi pokušaj je zaustavila Git provera vlasništva nad kopijom koju je
napravio sandbox nalog. Launcher sada prosleđuje tu tačnu putanju kao
`safe.directory` samo tokom dve lokalne Git provere.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/006-t021/start-vedran.ps1
```

1. Kada oba health odgovora pokažu `ok dataset`, otvori
   `http://127.0.0.1:5173/cases`. Izaberi transakciju
   `D4e050598f0f526f6fe690bb4874e2ee5` i proveri skor i snapshot.
2. U panelu **AI istraga** klikni **Pokreni novu istragu** i sačekaj
   nacrt. Otvori jedan citat i uporedi tvrdnju sa prikazanim dokazom.
3. Sačuvaj odluku sa kratkim obrazloženjem. Osveži stranicu i ponovo
   otvori isti pokušaj. Proveri da se vraćaju odluka, obrazloženje i citat.
4. Pritisni Enter u terminalu da zaustaviš pokrenute procese. Prijavi
   browser, datum, jednu proverenu tvrdnju i dokaz i ishod ponovnog
   otvaranja. Ostatak tehničkog zapisa može se dopuniti iz lokalnih logova.

## Browser nalaz · 22. novembar 2026.

Vedran Mitic je na Windows-u otvorio dataset slučaj
`C6c481448f7d25af15beea1309f44ee58` sa snapshot-om
`run_boosted_candidate_smoke` i skorom 0.9944662676905943. Browser i
njegova verzija nisu navedeni. Pokušaj
`att_ec44c6db64b546fea0f9b047fc858936` stigao je do `ready_for_review`;
nacrt `b312b4267dad5666fe11befc8992409ebf5b7b48de7d84ca5cb3a870a097cb78`
prošao je proveru šeme i referenci uz testni provider.

- Tvrdnju o iznosu 14.821,32 EUR pokriva otvoreni dokaz
  `ev_00e60986ff594ba2987a0804f6bb8fd6` u poljima
  `transaction.paid.amount` i `transaction.paid.currency`.
- Preporuku da se provere nedostajući podaci pokriva otvoreni odlomak
  `Missingness` iz simuliranog izvora `sim-missing`, verzija
  `authored-v1-2026-11-14`, dokaz `ev_8166ff7da9034950b1c8285eaeedcb5f`.

Vedran je prijavio isti prikaz posle osvežavanja. API log beleži ponovno
učitavanje slučaja i oba otvorena dokaza. Dostavljeni prikaz još ima
status `ready_for_review`, reviziju 4 i formular za odluku. U lokalnom
logu tog pokušaja nema `POST .../reviews`, a read-only SQLite upit
`select review_id from reviews` vratio je praznu listu za prvi prolaz.

Vedran je zatim dostavio prikaz sačuvane odluke `escalate`, sa
obrazloženjem „Test odluka” i ID-jem `rev_e928a6e319e44a3a94ad3ee2b1108bfd`.
Odluka je sačuvana 22. novembra u 11:21:28 UTC u drugom pokušaju
`att_c99ce5e8716f4bdf9171765c531dddb1` za isti slučaj, snapshot i
reviziju konteksta, uz nacrt
`dc0be4aaff54c7ffb5b488363ed3867ca3996e823a00788fed320ab2150709db`.
API log potvrđuje `POST .../reviews` (201), read-only SQLite proverom
potvrđena je veza odluke i nacrta, a naknadni GET istog pokušaja kroz
Vite vratio je `reviewed`, reviziju 5 i istu odluku sa obrazloženjem.
Provera citata je iz prvog prolaza, a čuvanje i ponovno čitanje odluke
iz drugog. Oba prolaza su sa testnim providerom.

## Zapis koji dostavlja član koji je izvršio probu

| Stavka | Potreban nalaz |
| --- | --- |
| Izvršilac, datum, okruženje | Ime ili timski alias, datum i vremenska zona, OS, browser, Python iz `uv run`, uv, Node i npm. |
| Checkout | Ispis `git rev-parse HEAD` i rezultat `git status --short` pre izvršavanja. |
| Transfer i indeks | Od koga su preuzete autorizovane kopije, tri originalna SHA-256, komanda izgradnje, novi lokalni digest, broj redova i rezultat T098 provere. |
| Setup i konfiguracija | Izvršene komande i izlazni kodovi, korpus/retrieval ID, režim providera i potvrda da je investigation store svež. |
| API, worker i web | Pokretanje API/Vite, health direktno i kroz proxy, poreklo i status mutacije, izlaz worker-a. |
| Cases i investigation | Case i transaction ID, snapshot, dataset, prikazan skor i verzija skora, context revision; šta se poklopilo pri poređenju. |
| Citat i odluka | ID pokušaja, nacrta, citata i odluke, jedna proverena tvrdnja i polje ili odlomak koji je potkrepljuje; odluka, obrazloženje i ishod ponovnog otvaranja. |
| Dopuna i odstupanja | Ishod opcione probe odsutne istorije, neizvršeni koraci, doslovne kontrolisane greške i razlog odstupanja. |

Zabeleži stvarne ishode i pročišćene isečke. Sirovi logovi i lokalni
store ostaju u ignorisanim putanjama. Proba iz quickstart-a koristi
testni provider bez živog izvršavanja. Eventualno ponavljanje sa pravim
modelom je neizvršeno i traži nov, eksplicitno odobren obim.
