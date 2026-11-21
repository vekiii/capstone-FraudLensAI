# Istraživanje i odluke — Feature 06

## Izvor skora za živi prolaz

**Odluka**. Prvo koristiti lokalni kompatibilni T098 paket, sa objavljenim `model-bounded.sqlite`, izvornim `source.sqlite` i odgovarajućim `history-index.sqlite`. Bounded snapshot sadrži prethodno sačuvane inferencije za sintetičke IBM transakcije. Paket je izvan Git-a. Dugotrajni import i trening Feature 02 nisu deo pripreme dok taj snapshot prođe proveru integriteta, dostupnosti i kompatibilnosti.

**Razlog**. Na grani već postoje dataset v2 Cases API i Feature 03 dataset reader. Potvrditi da oba čitaju isti run, da slučaj postoji u objavljenom snapshot-u i da se verzija dataseta, identitet transakcije i vrsta skora poklapaju. Upariti indeks istorije sa istim izvornim store-om i potvrditi hash-eve prema transfer manifestu. Bounded kohorta služi demonstraciji DS→LLM toka i nema status modelskog holdout rezultata.

**Alternativa**. Ako T098 paket ne prođe proveru, prihvatiti kompatibilan, objavljen snapshot od tima Feature 02 po istom ugovoru. Označiti stvarnu vrstu skora i zadržati status blokade dok je izvor nedostupan. Fixture slučaj ostaje pripremna proba.

## Identitet kroz React i istragu

**Odluka**. U postojećoj React aplikaciji koristiti isti panel i kontroler za oba režima sa eksplicitnom vezom `case_id`, `source_mode` i, za dataset, očekivanim `snapshot_ref` iz prikazanog detalja.

**Razlog**. Trenutno `Cases.tsx` montira panel samo za fixture, `investigation/api.ts` šalje hardkodovan `fixture`, a decoder prihvata samo `CASE-NNN`. Backend već ima dataset režim. Uz lokalne promene React granice, postojeći kontekst, API, worker i čuvanje odluke ostaju upotrebljivi. Čitanje konteksta mora potvrditi očekivani snapshot pre mutacije, a odgovor prolazi validaciju identiteta, režima, konteksta i attempt-a. Promena selekcije ili izvora odbacuje stare odgovore. Sačuvati Vite prosleđivanje Host zaglavlja zbog provere porekla zahteva.

**Alternativa**. Dupliranje panela ili novi javni endpoint povećali bi obim i razdvojili postojeći tok. Testirati zatvorenu granicu uz postojeće endpoint-e.

## Model i režim izvršavanja

**Odluka**. Obnoviti zaključane runtime zavisnosti prema Feature 03, uključujući SDK `openai`, transport `httpx2` i postojeći validator šeme koji je na ovoj grani u dev grupi. Proveriti njihove kompatibilne verzije u zaključanom okruženju. Eksplicitno vezati potvrđeni model, korpus, retrieval profil i verziju report prompta za početno i završno merenje.

**Razlog**. Adapter je prenet, ali SDK i transport nisu deklarisani na integracionoj osnovi. Raniji T101 je proverio profil semantic v8/report v6 na sintetičkoj kohorti i daje početnog kandidata za pripremu. Dostupnost modela i rad podešavanja na predatoj dataset verziji i dalje traže odobrenu proveru. Postojeći `probe-provider --synthetic-only` proverava osnovne sposobnosti u do dva zahteva. Proba ne dokazuje tačno ponašanje odabranog profila ni browser toka.

**Alternativa**. Testni provider daje ponovljivu pripremu i kontrolisane negativne slučajeve. Živi EV rezultati koriste stvarni model, uz eksplicitnu evidenciju opravdanih zaustavljanja pre poziva.

## Pre/posle i završni dokaz

**Odluka**. Ponovo koristiti obrasce iz `acceptance_harness.py` i `timing_observer.py` za zamrzavanje, metering i trag. Primarne rezultate dobiti kroz stvarne aplikacione granice iz ugovora. Pregled vernosti citata radi član tima uz offline referencu.

**Razlog**. Postojeći acceptance harness je vezan za fixture reader, a CLI `evaluate-reports` nije ulaz za živu evaluaciju. Pre merenja zamrznuti inpute, očekivanja, pristup proveri i gornji broj poziva za pripremu, dva merenja i odbranu. Ponovljeni GET i otvaranje dokaza treba da budu bez poziva modelu. Opravdani retry i repair ostaju vidljivi u tragu i zbiru. Nepoznata potrošnja se tako i evidentira.

**Alternativa**. Raniji T101/T102 ostaju dokaz za komponentu. Poređenje različitih kohorti ne može izmeriti ciljanu promenu na istim EV ulazima. Zasebni holdout ostaje zapečaćen po svom protokolu.
