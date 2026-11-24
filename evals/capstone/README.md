# Evidencija Capstone evaluacije

Zamrznuti `run.py` i `manifest.json` pripadaju istorijskom T098 toku.
Na integrisanom `main`-u modelski slučajevi koriste objavljeni bridge i
`APP_MODE=model`. [Odvojeno merenje integrisanog kandidata](../../evidence/tasks/feature-006-integrated-recheck-2026-11-24.md)
navodi prilagođene ulaze, izvršene provere i ishod. Istorijski rezultati
ostaju vezani za svoje revizije.

[Izvršni scenariji](inputs/cases.json) sadrže 16 javnih ulaza i pravila za
početno stanje. [Očekivanja](reference/expectations.json) otvara ocenjivač
offline, tek pošto sačuva opažanja. API-ju i worker-u prosleđuju se samo
parametri odgovarajućeg scenarija. Objavljivanje korpusa polazi od verzija
navedenih u ulazu. Za EV-10 kopirati korpus van `evals/`, normalizovati tekst
izvornog dokumenta postojećom funkcijom `knowledge.normalized` i dodati
`append_text` u sekciju `Review` kao novi red sa završnim LF. Pregled izmenjenog
izvora i njegov objavljeni corpus ID su preduslovi tog scenarija.

## Izvršavanje i trag

1. Pre prvog merenja T012 potvrđuje i zamrzava paket, konkretne seed konfiguracije,
   model i budžet. Pokrenuti postojeći React, API i eksplicitni worker po
   [quickstart-u](../../specs/006-capstone-evaluation/quickstart.md). Za svaku
   fazu i scenario koristiti izolovano stanje iz ulaza. EV-06 nastavlja EV-01
   iste faze uz iste identifikatore i store. Kad nedostaju sačuvani pokušaj,
   izveštaj, citat ili odluka, upisati `blocked` i tačan razlog.
2. Za istragu sačuvati Cases detalj, kreiranje i čitanje attempt-a preko postojećih
   API granica, korake worker-a, tačno otvoreni dokaz i ponovo učitanu odluku.
   [Timing observer](../../backend/src/fraudlens/investigation/timing_observer.py)
   može da zabeleži trajnu nameru sa idempotency ključem, POST i naknadne GET
   odgovore za API istrage. Zapis browsera dopunjava otvaranje dokaza i odluku.
   Za semantičku pretragu sačuvati POST sa `query`, vezanim `corpus` i posebnim
   idempotency ključem, pa `GET /api/knowledge/semantic-search/status` sa istim
   ključem i sadržaj primenljivih odlomaka. Za EV-02 zabeležiti oba upita u
   istom redu. Za EV-10 pokazati da je izmenjeni odlomak stigao do granice
   providera. Za EV-11–EV-16 koristiti [lokalne backend kontrole](../../backend/tests/integration/test_capstone_negative.py)
   i [web proveru citata](../../web/tests/investigation-reports.test.ts).
3. Vezati odobrenje i maksimalan broj zahteva za zamrznuti manifest po obrascu
   iz [acceptance harness-a](../../backend/src/fraudlens/investigation/acceptance_harness.py).
   U odobrenom živom režimu koristiti `DispatchLedger` i `metered_transport`
   na transportnoj granici provider adaptera za worker i semantičku pretragu.
   Povezati rezervacije i odgovore sa EV redom preko tragova, redosleda i
   request ID-jeva gde su dostupni. Obuhvatiti repair i retry. `build_service`
   iz istog modula je vezan za fixture i koristi se za njegove postojeće
   evaluacije. Za Capstone ostaju postojeći dataset reader i HTTP granice.
4. Čuvati stvarne odgovore, store-ove i sirove tragove pod
   `evals/results/capstone/<faza>/` ili drugim ignorisanim lokalnim putanjama.
   U deljenoj evidenciji koristiti pročišćene sažetke i proverljive
   identifikatore. Zabeležiti prvi ishod i razlog svakog naknadnog pokušaja.
   Sačuvani trag ostaje dostupan za offline ocenu i pregled vernosti citata.

## Zapis i zbir

Za lokalni pytest fixture korpus koristi `--basetemp` u ignorisanom
`.cache/` direktorijumu. Rezultat testa može biti u `evals/results/`.
Trag iz faze 4 i ispravka šeme evidencije za stvarni `inv_` identitet
opisani su u [poređenju](../../evidence/tasks/feature-006-before-after.md).

Validan zapis faze prati [JSON šemu](execution.schema.json). Sadrži fazu,
testirani commit SHA, verziju paketa i po jedan red za svaki EV ID. Po redu
upisati sledeće.

| Polja | Vrednost |
| --- | --- |
| `id`, `mode` | EV ID i zamrznuti režim `live` ili `deterministic`. |
| `input_sha256`, `seed_sha256` | SHA-256 kanonskog JSON-a javnog reda i SHA-256 odgovarajućeg konkretnog seed zapisa iz T012. Za kanonski JSON koristiti postojeći `fraudlens.investigation.models.digest`. |
| `status`, `outcome`, `reason` | Status offline ocene i sažetak stvarnog ishoda. `pass` zahteva prihvatljiv ishod i obavezni trag. Za `fail`, `blocked` i `not_run` upisati konkretan razlog. |
| `trace`, `binding` | Putanje ili identifikatori dokaza i sačuvane veze iz Cases/Investigation. U dataset režimu sačuvati transakciju, dataset, izvor i verziju skora i vrstu skora kad su dostupni. U EV-01 i EV-06 uneti i identitete pokušaja, nacrta, odluke i ponovo otvorenog dokaza. Koristiti isti redosled za iste dokazne ID-jeve. |
| `versions` | Digest stvarne konfiguracije, identiteti korpusa i retrieval-a, digest prompta, traženi i vraćeni model. Nedostupne ili neprimenljive verzije su `null`. |
| `metering` | Rezervacije, potvrđeni zahtevi, nepoznati ishodi, lokalna odbijanja pre slanja i simulirani zahtevi. Ove četiri kategorije moraju dati broj rezervacija. Za modele koji su vratili usage upisati subtotal tokena i broj takvih zahteva. Bez potvrđene potrošnje koristiti `usage: null`. Simulirani timeout i njegov nepoznat ishod ostaju vidljivi u lokalnom tragu, a zahtevi idu pod `simulated_requests`. |
| `retries` | Dodatni pokušaji sa razlogom, stvarnim ishodom, tragom, vezom i potrošnjom. Popravka i transportni retry unutar istog workflow pokušaja ulaze u njegov trag i metering. |

`not_run` ima prazan trag i `null` ishod i metering. `blocked` može imati
trag i potrošnju ako je izvršavanje stiglo do blokade. `pass` i `fail`
zahtevaju stvarno opažanje, trag i metering, uključujući eksplicitne nule pri
potvrđenom zaustavljanju pre dispatcha.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
uv run --locked python evals/capstone/execution.py evals/results/capstone/baseline/phase.json evals/results/capstone/final/phase.json
uv run --locked python -m pytest -q backend/tests/unit/test_capstone_execution.py backend/tests/integration/test_capstone_negative.py
npm.cmd --prefix web run test -- --run tests/investigation-reports.test.ts
```

Agregator proverava šemu, tačan skup ID-jeva, režime, zbir rezervacija i
sačuvanu vezu za prolaz EV-06. Ispisuje sva četiri statusa sa imeniteljem
16 po fazi. Pojedinačni neuspesi i blokade ostaju u zapisu. Poređenje u T019
koristi isti EV ID, digest ulaza i seed-a, zamrznutu rubriku i stvarne
kontrolne uslove. Svako odstupanje treba opisati uz odgovarajući red.
