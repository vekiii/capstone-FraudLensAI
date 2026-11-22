# Feature 06 · Ponovljeno živo poređenje za SC-002

22. novembar 2026, Europe/Belgrade. Windows, Python 3.14.3 i Node 24.20.0.
[Nalog i odobrenje](../../prompts/development/006-capstone-sc002-live-v2.md).

- Početna revizija `d8acc2a335d95e2402f586006925949f4d9f7739`.
- Završna revizija `a814eb080d4d27bb7e57e759d88948bb8b95695b`, lokalni izolovani commit koji dodaje pravilo za nejasne upite u semantički prompt. Početni trag EV-07 pokazao je `matched` uz tri opšta odlomka za upit bez referenta. Novo pravilo traži kontekst koji razlikuje primenljive procedure i uzdržavanje kad nedostaje takav podatak. Pravilo važi za svaki upit.
- Isti javni ulazi, seed pravila, offline kriterijumi, T098 scorovani snapshot, korpus, konfiguracija i `gpt-6-luna` u obe faze. Očekivanja su pročitana offline. Brojači su odvojeni, ograničeni na 19 zahteva po fazi. Istorijsko [poređenje 11/16 → 13/16](feature-006-before-after.md) ostalo je u sopstvenom zapisu.
- Windows lokalni indeks istorije ima 5.078.345 redova i SHA-256 `605a37302c6436e72c2cbc5a5b4d257c73048ad527f6e40df81f5ead7df5901c`. Read-only provera postojećih T098 artefakata potvrdila je vezu sa originalnim izvornim store-om i verzijom dataseta, istoriju i isti model za oba dataset slučaja. Obe faze vezane su za isti lokalni indeks u zasebnim runtime manifestima. Pogrešan bajtovni hash pri pripremi zaustavio je izvršavanje pre zahteva. Zamrznute bajtovne reprezentacije na Windowsu proverene su pre starta.
- EV-01 i EV-06 izvršavaju se u Chrome-u preko postojeće React/Vite i FastAPI aplikacije. Ostatak živih slučajeva koristi iste API i worker granice kroz postojeći `evals/capstone/run.py`. EV-11–EV-16 izvršeni su lokalno na oba tačna SHA, šest od šest na oba. Web kontrola nedostupnog dokaza proverena je u istom web kodu, 11 testova prošlo.

## Početni rezultat

Početno merenje daje **15/16 prolaza, jedan neuspeh i nula blokiranih**.
EV-01 je prikazao tačan modelski skor, napravio nacrt, otvorio proceduralni citat i sačuvao odluku. U EV-06 Chrome je ponovo otvorio isti pokušaj, nacrt, citat i odluku. Brojač zahteva ostao je `12 → 12`. EV-07 je jedini početni neuspeh. Svih 19 zahteva dobilo je HTTP 200.

## Poređenje svih 16 ishoda

| Slučaj | Početno | Završno |
| --- | --- | --- |
| EV-01 | Prolaz. Validiran nacrt, proceduralni citat i sačuvana odluka. | Neuspeh. Validiran nacrt i sačuvana odluka. Proceduralni citat izostao. |
| EV-02 | Prolaz. Obe formulacije vraćaju `Review`. | Prolaz. Isti odlomak u obe formulacije. |
| EV-03 | Prolaz. `Missingness` i `Review` pokrivaju dokumentovanje nedostajućih dokaza. | Prolaz. Vraćen primenljivi `Missingness`. |
| EV-04 | Prolaz. Dva deterministička čitanja istorije citirana u nacrtu. | Prolaz. Isti opseg, broj događaja i odvojeni iznosi po smeru i valuti opravdani citatima. |
| EV-05 | Prolaz. `no_match`. | Prolaz. `no_match`. |
| EV-06 | Prolaz. Isti nacrt, citat i odluka, nula novih zahteva. | Prolaz. Isti nacrt, tri stvarna citata i odluka, nula novih zahteva. Vidi postupak ispod. |
| EV-07 | Neuspeh. Tri opšta odlomka za upit bez referenta. | Prolaz. `no_match` bez izvora. |
| EV-08 | Prolaz. Istorija nedostupna, `needs_information`. | Neuspeh. Istorija označena kao nedostupna, ali stanje `ready_for_review` i opšte provere bez zahteva za konkretnom dopunom. |
| EV-09 | Prolaz. `no_match` za pitanje o srpskom roku. | Prolaz. `no_match`. |
| EV-10 | Prolaz. Tačan izmenjeni odlomak stigao do providera, šema i opseg očuvani. | Prolaz. Isti odlomak i očuvane granice. |
| EV-11 | Prolaz. HTTP 422 pre upisa ili zahteva provideru. | Prolaz. Ista kontrola. |
| EV-12 | Prolaz. Pokušaj odbijen posle jedne popravke bez objave. | Prolaz. Ista kontrola. |
| EV-13 | Prolaz. HTTP 404 za tačno traženi dokaz i vidljivo stanje nedostupnosti. | Prolaz. Ista kontrola. |
| EV-14 | Prolaz. Nedozvoljen alat odbijen pre izvršavanja. | Prolaz. Ista kontrola. |
| EV-15 | Prolaz. Dva simulirana timeout-a i jedan retry. | Prolaz. Ista kontrola. |
| EV-16 | Prolaz. Kvar istorije čuva prethodne činjenice. | Prolaz. Ista kontrola. |
| **Ukupno** | **15/16 prolaza, 1 neuspeh, 0 blokiranih, 0 neizvršenih** | **14/16 prolaza, 2 neuspeha, 0 blokiranih, 0 neizvršenih** |

Prvi završni EV-06 drajver prijavio je blokadu jer je iz EV-01 prikupljao samo proceduralne citate. Ovaj EV-01 je već imao stvaran sačuvani nacrt, odluku i tri citata vezana za taj pokušaj. Ponovljeno je samo čitanje postojećeg slučaja kroz React, FastAPI i Chrome. GET provera je otvorila sva tri citata i potvrdila sadržaj prikaza i jednakost sa sačuvanim pokušajem, uključujući odluku. Provider je bio onemogućen u procesu za čitanje. Prva provera brojača preklopila se sa drugim koracima završne faze. Posle završetka faze ista provera je ponovljena sa stabilnim brojačem `19 → 19`. Prvobitna blokada i oba browser rezultata ostali su u sirovoj evidenciji. EV-01 zadržava neuspeh po svojoj rubrici.

Oba `phase.json` zapisa validirana su kroz `evals/capstone/execution.py`. Svih 16 parova ima iste ID-jeve, režime, digeste ulaza i seed-a. EV-06 je u svakoj fazi vezan za svoj EV-01 i bez rezervacije zahteva. Prošlo je i svih 12 testova za šemu evidencije. Ukupno je potrošeno **38** zahteva za `gpt-6-luna`, svih 38 sa HTTP 200, 144.054 ulazna i 22.532 izlazna tokena. Uređeni zapisi i sirovi tragovi su u `.cache/sc002-live-v2-{baseline,final}/evals/results/capstone/`.

| Zapis | Početni SHA-256 | Završni SHA-256 |
| --- | --- | --- |
| `freeze.json` | `909c8fe61a4ea1fc177fa556747d3d5dd08a28da6560c5a84c27f36beef9fbd3` | `2b51a64c773bd23d6adad2ef6e6f271d9510ab095d9ccdfc67fab9e18f68674b` |
| `phase.json` | `120d6c59e9b488ebbf59fcfcb190a6550ea91dd48fb516499611e90f1cd5446a` | `749e103e4b998792bbc5955e44d492f92c1a168729e69a7f4f73f024a36c1de7` |

**SC-002 i CAP-05 su ispunjeni** ovim parom. Izmena vezana za EV-07 dala je očekivani ishod, a EV-01 i EV-08 beleže dve regresije u opaženim rezultatima. Ponavljanje istih scenarija služi pre/posle poređenju. Ovo merenje ne utvrđuje uzrok svakog pada i nema nezavisni holdout. Izmena ostaje u izolovanom lokalnom commitu zbog slabijeg ukupnog rezultata kandidata. Testirani dodatak u `prompts/application/retrieval-answerability-v8.md` glasi

```text
Before ranking, identify the action or decision being asked about and any context
needed to distinguish the applicable procedure. For a follow-up with an unstated
referent or stage, do not infer the situation from the passages. If materially
different procedures could fit and the question provides no way to choose, mark
the answer insufficient and state which detail would resolve the ambiguity. An
explicitly scoped question about a general rule can still be supported.
```
