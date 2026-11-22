# Feature 06 · T025 · Završni audit dokaza

22. novembar 2026, Europe/Belgrade. Testirani kandidat
`d8acc2a335d95e2402f586006925949f4d9f7739` (D), baseline
`5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca` (B), dokumentacioni HEAD na
početku faze `82e931d2749feb612cbf3ad2fee98123cba4e63e`.
[Specifikacija](../../specs/006-capstone-evaluation/spec.md) ·
[T024 puna regresija](feature-006-regression.md) ·
[CAP mapa](feature-006-capstone-evidence-map.md).

## Sledljivost i status

| Zahtev | Revizija i konkretan dokaz | Stanje |
| --- | --- | --- |
| FR-001 | D, [živi browser tok EV-01](feature-006-final-live.md) povezuje označeni slučaj, objavljeni run i provenance skora sa kontekstom, pokušajem i potvrđenim modelom `gpt-6-luna`. | Dokaz postoji za povezani živi tok. EV-01 kao celina ima pad zbog proceduralnog odlomka. |
| FR-002 | D, [EV-01 i EV-06](feature-006-final-live.md#react-cases-citat-i-sačuvana-odluka) pokazuju validiran nacrt, sadržaj citata, validirane argumente alata i obnovljivu odluku; EV-08 potvrđuje dopunu pri nedostupnoj istoriji. | Potvrđeni zahtevani elementi toka. |
| FR-003 | B i D, [zamrznuti manifest](../../evals/capstone/manifest.json), [ulazi](../../evals/capstone/inputs/cases.json), [offline očekivanja](../../evals/capstone/reference/expectations.json), [protokol](../../evals/capstone/protocol.md). | Potvrđeni 16 ID-jeva, pinovi 16 ulaza, seed-ova i očekivanja, rubrika i konfiguracija. |
| FR-004 | B i D, [pre/posle](feature-006-before-after.md) i povezani pojedinačni tragovi. | Delimično. Baseline EV-06 ima evidentiranu blokadu; sirova arhiva nije dostupna za ponovno proveravanje. |
| FR-005 | B → D, [ciljana izmena](feature-006-targeted-change.md) vezuje veličinu početnog zahteva za deduplikaciju istorije i finalni ishod. [Pre/posle](feature-006-before-after.md) čuva preostale padove. | Izmena i uporedni efekat dokumentovani. Baseline EV-06 ograničava potpunost poređenja. |
| FR-006 | D, [EV-11–EV-16](feature-006-final-negative.md), šest izvršenih kontrola. | Potvrđeno 6/6; ograničena provera deljenih dokaza ispod. |
| FR-007 | D, [kandidat](feature-006-release-candidate.md), [quickstart](../../specs/006-capstone-evaluation/quickstart.md), [T021](feature-006-peer-reproduction.md), [T024](feature-006-regression.md), [CAP mapa](feature-006-capstone-evidence-map.md). | Revizija i predaja sledljive. T021 koristi testni provider, a puni backend suite ima evidentirane padove i greške. |
| FR-008 | D, [specifikacija i ugovor](../../specs/006-capstone-evaluation/contracts/evaluation.md), [CAP-08](feature-006-cap08-contributions.md) i [CAP mapa](feature-006-capstone-evidence-map.md). | Potvrđeno prema izmenjenom US3. Vedran je dao jednu objedinjenu potvrdu četiri zapisa, uz dostupne primere ranijeg pregleda rada. |
| SC-001 | D, [živi EV-01/06/08](feature-006-final-live.md). | Potvrđen validiran nacrt sa sadržajno proverenom činjenicom, izvršenim determinističkim alatom, obnovljivom odlukom i zasebnim slučajem nedovoljnih dokaza. |
| SC-002 | B i D, [svih 16 parova](feature-006-before-after.md). | **Otvoren.** Baseline EV-06 je blokiran jer baseline EV-01 nije proizveo nacrt i odluku za ponovno otvaranje. |
| SC-003 | D, [finalne negativne kontrole](feature-006-final-negative.md). | Potvrđeno 6/6. |
| SC-004 | D, [T021](feature-006-peer-reproduction.md), [T022](feature-006-cap08-contributions.md) i [T023](feature-006-capstone-evidence-map.md). | Potvrđeno prema izmenjenom US3. Vedran je iz čistog checkout-a proverio citate u prvom prolazu. U drugom je sačuvao odluku, a naknadni GET je potvrdio isti sadržaj. |

Završeni T024 i T025 beleže obavljene provere. Prihvatanje feature-a
ostaje otvoreno zbog SC-002, otvorenih EV nalaza i backend regresionog
ishoda. Konkretni uzroci, preskoci i poređenje sa B su u T024.

## Identitet merenja i 16 EV redova

Final live, final negative i final redovi u pre/posle evidenciji koriste D;
baseline evidence čuva B. Poređenje Git objekata sa
`git diff --name-only B D -- evals/capstone uv.lock web/package-lock.json`
daje prazan izlaz (B i D su puni SHA-ovi iz zaglavlja). Za svaki od 16 EV
ID-jeva verifikovan je kanonski SHA-256 izvršnog ulaza, seed-a i očekivanja,
uz digest rubrike i konfiguracije. EV-06 referencira EV-01 unutar svoje faze.
Runner čita javne ulaze i manifest, protokol drži offline referencu izvan
izvršnog konteksta, a knowledge loader odbija `evals/` i razvojne promptove.

| Faza | Pass | Fail | Blocked | Not run | Imenilac |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 11 | 4 | 1 | 0 | 16 |
| Final | 13 | 3 | 0 | 0 | 16 |

Final EV-01 ima validiran nacrt i citiranu činjenicu uz `no_match`
proceduralne pretrage. EV-04 ima `citation_set_mismatch`. EV-07 je vratio
generičke pogotke bez potrebnog razjašnjenja. Sirovi `phase.json`, live
tragovi i freeze nisu dostupni u dokumentovanoj putanji
`evals/results/capstone/` u glavnom i izdvojenom checkout-u. Zbir je
proveren iz 16 redova deljenog sažetka, bez ponovne agregacije sirove
arhive ili živog izvršavanja. Nezavisni holdout nije otvaran.

| Fajl | SHA-256 Git/LF na B i D | Lokalni SHA-256 glavnog checkout-a |
| --- | --- | --- |
| Manifest | `d99668287527529495cc7fc649764e5747cf53f91a347e50d275094c37cb7c12` | `7bc9b5b0ca296c27f184cd7883f55b4a53c5b2a6e9eecaa0ba1020b5f16fda8f` (CRLF, pin T016) |
| Izvršni ulazi | `7a52db065205cb3721596c6f6452d991948a6f42c5b28d23989b217c8162ba26` | `ee7de1d5bcd4cfa40b85fa2cf485fb8bdc897104644da9d712316a259ec349e7` (CRLF) |
| Offline očekivanja | `57a84eb527a694eb33e2b312438f94a582741a225d42f30ea322d6950ed85953` | `6aa4e8a3959579f871d7bc7808386a93dfb0f8eef141c9472dbd26a557d06abf` (CRLF) |
| Execution šema | `0433ef503461a604030936b68831e4dafa57fcd8b8142aa743308a7d717f1307` (staro `run_`) | `040d9a9c4db1d3435942b553a3cb803de9ca5721fd1e404202b6c7afd363a6c0` (CRLF posle ispravke) |

Naknadna ispravka execution šeme u `02ab4061d2e7bae459ebf0d7c2be8885a05f6450`
uvodi `inv_`. Git/LF digest ispravljene šeme je
`ee9a8bed2605f8145db72d71957ece0581097dfe2dbf4023b768c646a1a20137`.
Razlike lokalnih bajtova su proverene normalizacijom CRLF u LF u memoriji.

## CAP i provera deljenih fajlova

Mapa sadrži po jedan red za CAP-01–CAP-08, dokaz, reviziju i ograničenje.
Tri scenario traga za odbranu su EV-01/06 (nacrt, činjenica i vraćena
odluka, EV-01 zadržava pad), EV-08 (potrebna dopuna) i EV-13 (kontrolisana
nedostupnost dokaza). CAP-05 ostaje delimičan zbog baseline EV-06.

Popis je obuhvatio `git ls-files -z --cached --others --exclude-standard`,
veličine, lokalne ignore granice i ograničeno skeniranje obrazaca ključeva
u tekstu. Proveren je popis 587 fajlova. Od toga je 579 tekstualno
provereno, a osam samo po metapodacima. Izlaz sadrži samo putanje i broj
nalaza. Binarnim prikazima i
evaluacionim fajlovima izvan Capstone paketa provereni su putanje, tipovi i
veličine. Ograničena provera radnog checkout-a ne pokriva Git istoriju ni
OCR slika. Sirove transakcije, generisane baze, modeli, `.env` i EV arhive
ostaju izvan predloženih fajlova. Provereno je da su njihove dokumentovane
putanje ignorisane. Šest postojećih slika u evidence-u ostaje na mestu.

Prvobitna pretraga formata tokena označila je dva ista tekstualna fragmenta
u Markdown anchoru reči `task`. Provera konteksta uklonila je ta lažna
poklapanja. U auditovanom tekstu nema potvrđenog obrasca ključa.
T098 i EV evidencija deli samo pregledane sažetke i sintetičke identitete.
Zahtev faze sačuvan je bajt-po-bajt, SHA-256
`cf89b5d74497ab8e3c0081586d15e7194e33957c4715c2e08a1ba038013721c0`.
