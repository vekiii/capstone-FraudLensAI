# Feature 06 · T021 · Nezavisna reprodukcija

**Status: pending.** Nema potvrđenog izvršavanja drugog člana na kandidatu
`d8acc2a335d95e2402f586006925949f4d9f7739`. Nalaz pripremiti prema
[quickstart-u](../../specs/006-capstone-evaluation/quickstart.md).
Vedran je 22. novembra 2026. rekao da će tim poslati nalaz posle probe.
Aktuelna provera alata, lokalnih fajlova i korpusa evidentirana je u
[predaji faze](feature-006-phase-05-handoff.md). Raniji automatizovani
[browser tok](feature-006-dataset-smoke.md) i [živi final](feature-006-final-live.md)
su referentni dokazi.

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
