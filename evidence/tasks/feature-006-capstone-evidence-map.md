# Feature 06 · T023 · CAP-01–CAP-08 mapa dokaza

**Status: završeno.** Mapa pokriva svih osam stavki i beleži rezultate
T021 i T022, kao i otvorene kriterijume evaluacije.
[Završna regresija T024](feature-006-regression.md) ·
[Završni audit T025](feature-006-final-audit.md).
Izabrana aplikaciona revizija za predaju je `d8acc2a335d95e2402f586006925949f4d9f7739`.
Baseline poređenja je `5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`.
[Odluka o predaji i pinovi](feature-006-release-candidate.md).

**Dopuna za CAP-05, 22. novembar 2026.** [Ponovljeno živo poređenje](feature-006-sc002-live-v2.md)
zatvara CAP-05 i SC-002 sa 16 stvarnih parova na `d8acc2a` i `a814eb0`.
U obe faze EV-06 je potvrđen bez dodatnog LLM zahteva. Poređenje beleži
EV-07 kao poboljšanje i EV-01 i EV-08 kao regresije. Tabela ispod čuva
originalno merenje i zaključke za tadašnji referentni kandidat `d8acc2a`.

**Dopuna od 24. novembra 2026.** Na integrisanom kandidatu ponovo su izvršene
žive i determinističke provere. EV-01 i EV-06 koriste modelski slučaj iz
trenutnog demoa. [Zaseban zapis merenja](feature-006-integrated-recheck-2026-11-24.md).

| CAP | Zahtev | Testirani SHA | Dokaz i način provere | Stanje i ograničenje |
| --- | --- | --- | --- | --- |
| CAP-01 | Specifikacija, tehnički dogovor i glavni tok (FR-008). | Final `d8acc2a` | Pratiti identitet i scorovani snapshot iz Cases kroz kreiranje pokušaja, evidence, review i reload. [Specifikacija](../../specs/006-capstone-evaluation/spec.md) · [Plan](../../specs/006-capstone-evaluation/plan.md) · [Ugovor](../../specs/006-capstone-evaluation/contracts/evaluation.md) · [Browser trag](feature-006-final-live.md). | Dokaz povezan. Prihvatanje celog feature-a ostaje otvoreno. |
| CAP-02 | Poreklo skora, ista transakcija i stvarni model (FR-001). | Final `d8acc2a` | (EV-01) Uporediti Cases v2 payload sa sačuvanim investigation payload-om, run i scorer, prikazani skor i traženi/vraćeni `gpt-6-luna`. [T098](feature-006-t098-inputs.md) · [Final live](feature-006-final-live.md). | Izvršeno. Bounded objavljeni snapshot sintetičkih podataka služi integraciji. |
| CAP-03 | Sadržajna potpora tačnog citata i kontrola nedovoljnih dokaza (FR-002). | Final `d8acc2a` | EV-01/06 otvoriti tačno vezani `case_fact`, uporediti transakciju, iznos i vreme sa tvrdnjom; EV-08 proveriti `needs_information` i `unavailable`. EV-02/03/10 imaju zasebno otvorene odlomke. [Final live](feature-006-final-live.md). | Sadržajna provera činjenice i slučaj za dopunu zabeleženi. Proceduralni kriterijum EV-01 ostaje neuspešan. |
| CAP-04 | Stanje, deterministički alat i obnovljiva odluka analitičara (FR-002). | Final `d8acc2a` | EV-01 proveriti `ready_for_review`, validaciju `schema_reference_passed`, trag `get_case_facts {}` i oba `get_account_history` poziva. EV-06 poredi iste ID-jeve pokušaja, nacrta, citata i odluke posle ponovnog otvaranja. Ledger 19 → 19. [Browser i audit](feature-006-final-live.md#react-cases-citat-i-sačuvana-odluka). | Izvršeno. Stanje obnovljeno bez novih poziva. |
| CAP-05 | Zamrznutih 16 redova pre/posle, ciljana izmena i odstupanja (FR-003–005). | Baseline `5974f94` i final `d8acc2a` | Uporediti **svih 16 redova** sa istim ID-jem, digestima ulaza/seed-a i pravilom ocenjivanja. T015 vezuje ulazni limit za transportnu deduplikaciju i RED/GREEN. [Manifest](../../evals/capstone/manifest.json) · [Parovi i zbir](feature-006-before-after.md) · [Ciljana izmena](feature-006-targeted-change.md). | **Delimično.** Baseline 11 pass / 4 fail / 1 blocked, final 13 pass / 3 fail, oba od 16. Baseline EV-06 blokiran, pa SC-002 ostaje otvoren. EV-01/04/07 ostaju finalni padovi. |
| CAP-06 | Šest završnih negativnih kontrola (FR-006). | Final `d8acc2a` | Uporediti ishode EV-11–EV-16 sa kontrolama: zahtev, nacrt, nedostupan citat, nepoznat alat, timeout i kvar istorije. [Final negative](feature-006-final-negative.md). | **6/6** prošlo. Kontrole koriste lokalne simulacije sa nula pravih provider poziva. |
| CAP-07 | Jedna revizija, uputstvo, lokalni artefakti i reprodukcija (FR-007). | Final `d8acc2a` | Proveriti SHA, transfer digeste i lokalni indeks, potom reprodukovati dataset binding, citat i ponovno otvaranje odluke. [Quickstart](../../specs/006-capstone-evaluation/quickstart.md) · [Zapis reprodukcije](feature-006-peer-reproduction.md). | **Potvrđeno prema izmenjenom US3.** Vedran je iz čistog checkout-a proverio citate i sačuvao odluku. Naknadni GET je vratio istu odluku. |
| CAP-08 | Doprinos, odluka, provera i veza sa tokom za sva četiri člana, uz objedinjenu potvrdu i dostupne primere pregleda (FR-008, US3). | Final `d8acc2a` | Povezati četiri zapisa sa commitima i izvršenim proverama. [Potvrda i dokazi](feature-006-cap08-contributions.md). | **Potvrđeno prema izmenjenom US3.** Vedran je 22. novembra pregledao i potvrdio sva četiri zapisa. |

## Revizije, granice merenja i odbrana

Final live, final negative i poređenje 16 finalnih EV redova u sačuvanim
evidence zapisima navode isti puni `d8acc2a335d95e2402f586006925949f4d9f7739`.
Baseline zadržava `5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`.
Ukupno je evidentirano 36 potvrđenih provider zahteva, 121.405 ulaznih
i 18.891 izlazni token. Novčani iznos nije očitan. Sirovi lokalni
`phase.json` i live/negative arhivski tragovi nisu prisutni u ovom
checkout-u. Provera ove faze obuhvata deljene evidence zapise i Git
objekte. [Istorijski digesti](feature-006-before-after.md#provera-zapisa).

Execution šema je naknadno ispravljena iz `run_` u `inv_` na
dokumentacionom HEAD-u `02ab4061d2e7bae459ebf0d7c2be8885a05f6450`.
LF digest ispravke je
`ee9a8bed2605f8145db72d71957ece0581097dfe2dbf4023b768c646a1a20137`;
oba merena SHA zadržavaju isti stari blob i originalne statuse.

1. EV-01/06 — validiran nacrt, citirana činjenica proverena po sadržaju
   i ista odluka posle ponovnog otvaranja. EV-01 ostaje **fail** zbog
   nedostajućeg proceduralnog odlomka. EV-06 je **pass**.
   [Final live](feature-006-final-live.md#react-cases-citat-i-sačuvana-odluka).
2. EV-08 — stvarno odsutna istorija, poznati skor i iznos, validiran
   `needs_information`. [Final live](feature-006-final-live.md).
3. EV-13 — kontrolisani 404 `evidence_not_found` pri otvaranju vezanog
   citata, uz ispravan prikaz nedostupnosti i nepromenjen drugi dokaz.
   [Final negative](feature-006-final-negative.md).

SC-001 i SC-003 imaju dokumentovan dokaz. SC-002 je otvoren zbog baseline
EV-06. SC-004 je potvrđen prema izmenjenom US3. [Predaja faze](feature-006-phase-05-handoff.md).
