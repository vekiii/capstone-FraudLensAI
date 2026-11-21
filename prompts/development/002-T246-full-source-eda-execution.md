# Original development prompt — T246 full-source EDA

Odobravam jedan puni label-free prolaz nad provjerenim lokalnim
T210 snapshot-om radi izrade EDA agregata i dovršetka T246.

Radi iz:
/Users/ladylazarus/Desktop/FraudLensAI-StageC

Pročitaj AGENTS.md, next_work.md i:
evidence/tasks/T246-label-free-preparation-2026-11-21.md

1. Pregledaj pripremljeni publisher i runner prije izvršavanja.
   Potvrdi da se is_laundering token uklanja prije json.loads
   i da agregacija ne koristi niti prikazuje vrijednosti labela.

2. Provjeri manifest, COMPLETE i accepted.jsonl prema postojećim
   zamrznutim identitetima. Potvrdi resursne granice i kontrolisano
   postupanje pri prekidu. Ne prepisuj postojeće izlaze.

3. Pokreni evidence/tasks/T246-publish-eda.py s odgovarajućim
   argumentima provjerenim iz koda/--help.

   Obradi cijeli izvor, bez tihog uzorkovanja.
   Prati izvršavanje i prijavljuj napredak.
   Ako pokušaj padne, sačuvaj dijagnostiku i ne ponavljaj automatski.

4. Provjeri stvarni sažetak:
   - usklađenost s 5.078.345 prihvaćenih redova;
   - identitete izvora, vremenski obuhvat i warm-up;
   - denominatore, jedinice i granice veličine odgovora;
   - odvojene iznose po valuti;
   - odsustvo labela, pojedinačnih transakcija i računa.

   Sačuvaj porijeklo i pune hash-eve agregata.
   Nepotpun izlaz ne objavljuj kao pouzdan sažetak.

5. Poveži provjereni sažetak s postojećim /api/eda/summary
   endpointom prema ugovoru i provjeri stvarni HTTP 200 odgovor.
   Provjeri i kontrolisano ponašanje za nedostajući ili izmijenjeni
   sažetak, bez oštećivanja originalnog izlaza.

6. Pokreni relevantne testove, Ruff i git diff --check.
   Zapiši komande, trajanje, opaženu memoriju, rezultate i ograničenja
   u evidence. Ažuriraj next_work.md i indeks.

T246 označi završenim samo ako su svi njegovi kriterijumi ispunjeni.
T243 ostaje pending; ne implementiraj T247/T248 EDA UI.
T252 ostaje otvoren do stvarnog pregleda recenzenta.

Bez novog treninga, ponavljanja T230, parsiranja test/showcase
labela, showcase replaya, commita ili pusha.
