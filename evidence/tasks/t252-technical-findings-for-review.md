# T252 — tehnički nalazi za ljudski pregled

**Predmet pregleda** PR #3, izvršna revizija `d46699fbd11219ebc92c6ef002d4924a4c7d4b34`. Tehnički pregled obavio je Codex 22. novembra 2026. Ljudski zaključak je otvoren.

| Oblast | Nalaz i trag |
| --- | --- |
| Protokol i poreklo modela | Istorijski T228 izbor imao je zasićenje i prag 1.0. Na pregledanoj reviziji T229 beleži kasniji zaseban izbor neponderisanog LightGBM-a, uz isti prethodno istreniran artefakt, zamrznuti prag `0.2489517623052024` i transformacije naučene samo na treningu. SHA modela `3b4e4019…` i manifesta `c766e901…` potvrđeni su pri proveri paketa. |
| Podaci i razdvajanje | T203 dopušta pripremu tačno hashirane lokalne kopije. Kasnija odluka pokriva trening te kopije. Kaggle revizija, datum pribavljanja, uslovi listinga i izvorna vremenska zona ostaju nepoznati. Koristi se dokumentovana UTC pretpostavka. Izvršeni split po celim danima ima 1.169.261 / 482.650 / 233.070 razvojnih redova za trening, validaciju i test. Showcase je zaseban i ima zabeleženo odstupanje prevalencije. |
| Agregati i račun | `GET /api/model/results` na zamrznutom checkoutu vratio je 200, isti prag i `calibration_status=not_assessed`. Validacija ima 482.650 redova, 471 pozitivan i 229 upozorenja. T230 test ima 233.070 redova, 218 pozitivnih i 65 upozorenja. TP/FP/TN/FN = 44/21/232.831/174. Ponovnim računom iz agregata potvrđeni su precision 0,6769, recall 0,2018 i F1 0,3110. Prvi pokušaj čitanja proverne skripte tretirao je listu particija kao mapu. Ispravljena provera prošla je. |
| Značenje rezultata | T230 se odnosi na sintetički test 6. septembra 2022. od 00:00 do 11:12 UTC. P@20/50/100 je 0,90/0,76/0,52 preko cele test particije, a 65 upozorenja je broj pri fiksnom pragu bez dnevnog ograničenja. Validacija je ponovo korišćena za izbor i dijagnostiku. U odbrani navesti nisku prevalenciju, neprocenjenu kalibraciju i ograničenje na sintetički izvor. |
| Aplikacija i reprodukcija | [Windows provera](t252-windows-reproduction-2026-11-22.md) potvrdila je hash-eve, 8/8 tačan paritet, 1/1 HTTP paritet i sačuvanu testnu odluku. Pregledani su T233/T236, T240/T242 i T251 zapisi o kontrolisanom učitavanju, granicama API-ja i agregatnom prikazu. Ovaj pregled nije ponavljao fit ili T230, otvarao labele niti proveravao browser. |

## Šta ljudski pregledalac potvrđuje

Zabeležiti ime, datum, reviziju, koje izvore i ograničenja je lično pregledao,
koje lokalne komande je izvršio, njihove stvarne ishode i primedbe ili potvrdu
za pregledani opseg. Ovaj zapis može da prati dopunu PR-a #5. T252 ostaje
otvoren dok nezavisni član ne potvrdi odgovarajući opseg po kriterijumima zadatka.
