# Feature 06 · T008 · Živi preflight

22. novembar 2026. · Europe/Belgrade · Grana `006-capstone-evaluation` ·
HEAD `8bae72147f79a353e457bdb8495638c427c7efae`, početno radno stablo čisto.
Python 3.14.7, OpenAI SDK 3.51.0, httpx2 2.16.0, Node v24.20.0,
Chrome 158.0.8127.36. Spec Kit prerequisites exit 0, checklist 14/14.
[Odobrenje](../../prompts/development/006-capstone-t008-approval.md) ·
[Quickstart](../../specs/006-capstone-evaluation/quickstart.md).

## Sintetička proba

`fraudlens.investigation.cli probe-provider --synthetic-only` pokrenut je
kroz zaključani Python sa `INVESTIGATION_PROVIDER=openai` i granicom od dva
zahteva. Brojač lokalnog HTTP transporta zabeležio je **2/2 HTTP 200**.
`capability_probe_passed`, exit 0. Traženi i vraćeni model `gpt-6-luna`
zatražio je sintetički alat bez argumenata i vratio strukturisani
nacrt. Ukupno 1.413 ulaznih i 118 izlaznih tokena.

## Podešavanje browser toka

Izabran je profil semantic v8/report v6 sa grupisanim alatima, niskim
reasoning-om i striktnim sekcijama nakon činjenica o slučaju, prema kandidatu
iz T101. Rokovi su 45 s za zahtev i 120 s za pokušaj, uz 4.096 izlaznih
tokena i 48.000 bajtova ulaza. Ukupan plafon bio je dva sintetička i osam
browser dispatcha. Svaki pokušaj koristi svež lokalni store, pregledani
korpus i izolovani Chrome profil. Pokretanje kroz React Cases/Vite
na 5173, FastAPI na 8000 i eksplicitni `worker --once`.

Dataset binding obuhvata objavljeni `run_boosted_candidate_smoke`, model
`model-history-v1-boosted-candidate` i dataset
`dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`.
Kompatibilni lokalni indeks ima digest
`8745ec13848f5ce0f76417fd0c2f7c731a2189cb634034aea5eeaa3a205c5a9f`.
Izabrani slučajevi su izdvojene pripremne probe van kandidata navedenih u EV matrici.

## Prvi pokušaj

Slučaj `C13238fc408d0919e730ecd2e1b5b1c56`, pokušaj
`att_670bde089d754efba9653ec6ce2f101e`. Browser je potvrdio prikaz skora
0.994096671545522 i isti Cases/Investigation binding. Završeni su
`get_case_facts`, istorija pošiljaoca i primaoca i `search_procedures`.
Prva tri dispatcha imaju odgovor `gpt-6-luna` i metering, zbir 10.124
ulazna i 656 izlaznih tokena. Četvrta rezervacija je lokalno završila kao
`failed`, `budget_exhausted`, `outcome_unknown=false`, bez request ID-ja
ili usage-a. Ovaj ishod odgovara ograničenju ulazne veličine u adapteru.
Istorija pošiljaoca imala je 52 podobna događaja i alat je vratio ograničenu
projekciju od 17 događaja. Nacrt, otvaranje citata iz nacrta i odluka ostali
su nedostupni za ovaj pokušaj.

## Ponovljeni preflight i odluka

**Prošao, exit 0.** Za drugi svež store izabran je
`C87bd60ce9e4d9620d9bad71e6492542f` sa istim run-om i profilom. Istorija
je dostupna sa pokrivenošću `full`; pošiljalac ima nula, a primalac šest
podobnih događaja. Limit svežeg pokušaja bio je četiri preostala dispatcha.
Browser je ponovo potvrdio identičan v2 detalj i sačuvani `source_payload`,
transakciju `Da110c7038da06de58a5f8d082c4cb29a` i skor 0.9951315775272921.

- Pokušaj `att_09c3d15c2e1a49caa9128122a3396536` prešao je iz `created` u
  `ready_for_review`. Oba istorijska čitanja, činjenice i proceduralna
  pretraga završili su kao `completed`. Sva četiri dispatcha imaju
  request ID, usage i vraćeni model `gpt-6-luna`.
- Validirani nacrt `d8f5e1d7b9d66ecbd433855b1dc88f2e5b2fa2f211c787098e4b90b4a823f263`
  ima `schema_reference_passed`. U panelu je otvoren odlomak **Review** iz
  simuliranog izvora *Simulated review and escalation*, passage
  `8d167c603b9634f1411a8203239863ba4b82af22c290f6900010701404ff060d`.
  Odlomak traži pregled konkretne transakcije i ograničenja skora,
  beleženje nedostajućih dokaza i obrazloženu odluku analitičara. Time
  potkrepljuje preporuku u nacrtu. Browser i API potvrdili su tačan citirani
  tekst i vezu dokaza sa pokušajem i kontekstom.
- Odluka `request_more_information`, ID
  `rev_a242562de6fb45f5a81df39186b87229`, sačuvana je kroz browser.
  Posle potpunog osvežavanja i ponovne selekcije prikazani su isto
  obrazloženje, pokušaj i izveštaj. Čitanje se završilo bez novog dispatcha.

Sačuvani context revision
`7498d882e7552a1c125b3e187996acf415a155679401143822f04f9fcbbcf27a`,
korpus `corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3`,
retrieval `071f1a593fa17471295860bb5abc3a0064261a7e159bdf3d530494881001bccb`,
semantic policy `610990e201245ce8a477ab6b6de03e4a8f640e5143c48ba2ee3e0b3c7afd353b`
i report prompt digest `f0e044eaf4015363808e2b4672d84d7e4ce4bd7c7db17f5201996ecca1b8efb5`.

## Potrošnja

| Korak | Potvrđeni zahtevi providera | Ulazni tokeni | Izlazni tokeni |
| --- | ---: | ---: | ---: |
| Sintetička proba | 2 | 1.413 | 118 |
| Prvi browser pokušaj | 3 | 10.124 | 656 |
| Ponovljeni browser pokušaj | 4 | 19.148 | 2.144 |
| **Ukupno** | **9** | **30.685** | **2.918** |

Browser audit ima osam rezervacija, od toga sedam potvrđenih odgovora i
jedno lokalno odbijanje ulaza. Tokeni su iz provider usage zapisa. Iznos
računa nije očitan. Lokalne komande `node .cache/006-t008-live-browser.mjs`
i `node .cache/006-t008-recovery-browser.mjs` koristile su konfiguraciju
iznad. Browser rezultati, store-ovi i sirovi trag ostaju u odgovarajućim
`.cache/006-t008-live-*/` direktorijumima. `uv lock --check` je prošao.
T008 je pripremna provera. T009 i primarno merenje ostaju otvoreni.
