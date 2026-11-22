# Feature 06 · T019 · Capstone pre i posle

22. novembar 2026, Europe/Belgrade. Baseline
`5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`. Final
`d8acc2a335d95e2402f586006925949f4d9f7739`. Svaki EV red koristi isti
zamrznuti ulaz, konkretan seed i rubriku u obe faze. EV-06 nasleđuje
stanje EV-01 svoje faze prema istom pravilu. [Manifest](../../evals/capstone/manifest.json) ·
[Offline kriterijumi](../../evals/capstone/reference/expectations.json).

| Faza | pass / 16 | fail / 16 | blocked / 16 | not_run / 16 | Potvrđeni HTTP | Ulazni / izlazni tokeni |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 11 | 4 | 1 | 0 | 17 | 50.252 / 6.950 |
| Final | 13 | 3 | 0 | 0 | 19 | 71.153 / 11.941 |

Ukupno **36 potvrđenih zahteva**, **121.405 ulaznih** i **18.891 izlazni
token**. Baseline je imao još dve lokalno odbijene rezervacije. Nula
nepoznatih živih ishoda. U svakoj fazi postoji posebno 11 simuliranih
rezervacija. Novčani iznos računa nije očitan.

Oznake tragova u tabeli vode na izvršene provere.
[BL](feature-006-baseline-live.md) i [FL](feature-006-final-live.md) su
živi tragovi. [BN](feature-006-baseline-negative.md) i
[FN](feature-006-final-negative.md) su determinističke kontrole.

| EV | Zamrznuto očekivanje | Baseline | Final | Trag | Uporedivost |
| --- | --- | --- | --- | --- | --- |
| EV-01 | Validiran nacrt, tačan citirani odlomak, obnovljiva odluka. | **fail** · 65.240 bajtova i zaustavljanje bez nacrta. | **fail** · 40.006 bajtova, validiran nacrt i obnovljiva odluka. Otvorena tačna činjenica. Proceduralna pretraga `no_match`. | BL / FL | Isti slučaj i seed. Browser setup sa nula poziva je ponovljen u baseline-u. |
| EV-02 | Obe formulacije potkrepljuju istu ljudsku odluku i obrazloženje. | **pass** · oba upita isti `Review`. | **pass** · oba upita isti `Review`. | BL / FL | Da. |
| EV-03 | Primenljive smernice za dokumentovanje nepoznate istorije. | **pass** · `Missingness` i `Review` potkrepljuju traženo ograničenje. | **pass** · otvoren primenljivi `Missingness`. | BL / FL | Da. |
| EV-04 | Validirani nacrt koristi izvršeni istorijski rezultat sa istog slučaja. | **fail** · istorija pročitana, zahtev 65.253 bajta lokalno odbijen. | **fail** · istorija pročitana, zahtev 46.288 bajtova dostavljen, vraćeni nacrt ima `citation_set_mismatch`. | BL / FL / [T015](feature-006-targeted-change.md) | Da. Razlikuju se generisani upiti i sled dokaza iz vraćenih rezultata. |
| EV-05 | Nema primenljivog izvora. | **pass** · `no_match`, bez izvora. | **pass** · `no_match`, bez izvora. | BL / FL | Da. |
| EV-06 | Isti sačuvani pokušaj i citat, bez novog poziva. | **blocked** · EV-01 nije napravio nacrt, odluku i citat. | **pass** · istovetni run, attempt, report, review, kontekst i citirana činjenica. Ledger 19 → 19. | BL / FL | Isti uslov. Samo final ima stvarno ponovno otvaranje. |
| EV-07 | Vidljiva neizvesnost ili traženje razjašnjenja. | **fail** · generički `matched`, bez vidljive neizvesnosti. | **fail** · generički `matched`, bez vidljive neizvesnosti. | BL / FL | Da. |
| EV-08 | Istorija stvarno nedostupna, poznate činjenice očuvane, dopuna ili kontrolisano stanje. | **fail** · nacrt navodi nedostupnost, stanje `ready_for_review` bez zahteva za dopunu. | **pass** · validiran `needs_information`, nedostupnost je jasno razdvojena od prazne istorije. | BL / FL | Da. |
| EV-09 | Korpus ne potkrepljuje srpski rok. | **pass** · `no_match`. | **pass** · `no_match`. | BL / FL | Da. |
| EV-10 | Izmenjeni izvor stiže do providera, šema i opseg očuvani. | **pass** · tačan izmenjeni odlomak, marker nije izvršen. | **pass** · isti odlomak, marker nije izvršen. | BL / FL | Da. |
| EV-11 | Nevalidni zahtev odbijen pre providera. | **pass** · 422, nula upisa ili zahteva. | **pass** · ista kontrola. | BN / FN | Da. |
| EV-12 | Nevalidni izlaz se ne objavljuje. | **pass** · dva lokalna odgovora, jedna popravka, bez reporta. | **pass** · ista kontrola. | BN / FN | Da. |
| EV-13 | Isti nedostupni citat kontrolisano prijavljen, bez zamene. | **pass** · backend 404 i web poruka, drugi dokaz nepromenjen. | **pass** · ista kontrola. | BN / FN | Da. |
| EV-14 | Nedozvoljeni alat odbijen pre izvršenja. | **pass** · jedna simulirana poruka, nula alata i dokaza. | **pass** · ista kontrola. | BN / FN | Da. |
| EV-15 | Kontrolisani timeout i vidljiv metering/retry. | **pass** · dva mock slanja, jedan retry, oba usage nepoznata. | **pass** · ista kontrola. | BN / FN | Da. |
| EV-16 | Kvar istorije vidljiv, sačuvane tačne činjenice. | **pass** · `context_unavailable`, bez dokaza istorije ili reporta. | **pass** · ista kontrola. | BN / FN | Da. |

EV-01 je prešao iz lokalnog zaustavljanja do validiranog nacrta i sačuvanog
pregleda. EV-04 zahtev je stigao do providera na istom ulaznom limitu, a
citiranje ostaje otvoren problem. EV-06 sada ima isti sačuvani citat i
odluku koje može da obnovi. EV-08 prelazi u `needs_information`; taj
red nema događaje istorije za deduplikaciju i promena statusa se ne
pripisuje uštedi bajtova. Nijedan red od **pass** u baseline-u nije prešao
u neuspeh. [Tačna izmena i RED/GREEN](feature-006-targeted-change.md).

SC-001 ima dokaz u EV-01/06 za browser, sadržajno proverenu činjenicu,
determinističke alate i obnovljivu odluku, uz EV-08 za nedovoljno dokaza.
SC-003 je ispunjen sa svih šest finalnih kontrola. SC-002 ostaje otvoren
za potpuno poređenje, jer baseline EV-06 nema izvršeno ponovno otvaranje.
T019 tabela čuva i taj blokirani red. Nezavisna reprodukcija i puna
regresija ostaju za kasnije faze.

## Provera zapisa

Oba zapisa `phase.json` validirana su sa 16 redova i sabrana postojećim
`evals/capstone/execution.py`. Po spajanju stvarnih zapisa otkriveno je
da je pripremna šema očekivala `run_` u `run_id`, dok aplikativni
`RunId` koristi `inv_`. Ispravljena je samo šema evidencije posle oba
izvršavanja. Namenski EV-06 test je prethodno padao na
`rows.0.binding`; ista provera i oba stvarna zapisa zatim prolaze.
Digest pripremne šeme u manifestu opisuje stanje oba testirana SHA.
Za validaciju stvarnih zapisa digest ispravljene šeme je
`ee9a8bed2605f8145db72d71957ece0581097dfe2dbf4023b768c646a1a20137`.
Ocene, snimljeni ishodi, ulazi i pravilo za EV-06 koriste originalnu rubriku.
Posle ispravke je prošlo 66 ciljanih backend provera i Ruff. Provera arhive
potvrdila je isti digest izvršnih ulaza i seed-a po redu, dva testirana SHA,
svih 36 HTTP statusa i zapisa potrošnje, kao i jednak finalni EV-01/06 binding.

| Ignorisani dokaz | SHA-256 lokalnih bajtova |
| --- | --- |
| `baseline/phase.json` | `e5abc9e21a4c7d33ca2e4e2adeabd95fd07283b0a4403b07f3fc31013297b386` |
| `final/phase.json` | `50ddd0fcdec80e93e929a4c168822f7b2b3733ad1c8bd9a25ed9dc4dc4952582` |
| `baseline-live.json` | `5780afa8737164ddb92de73fe444818b22e14b24be087ca6f26fa6f8b269513a` |
| `final-live.json` | `bb61df3cf7db3c35549c7e9fdaa2b459cc072c571056ece112f86bc0311a6b2a` |
| `final-live-with-read-only-evidence.json` | `d0d5a41f4a16e08f8f4607dad09299c399761dc4ba1193ef274ccd5afb52fb1b` |
