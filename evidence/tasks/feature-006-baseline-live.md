# Feature 06 · T013 · Živi baseline

22. novembar 2026, Europe/Belgrade. Testirani SHA
`5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`. Izvršavanje je počelo sa
čistog stabla, sa zamrznutim `capstone-ev-v1`. Traženi i iz svih potvrđenih
odgovora vraćeni model je `gpt-6-luna`, semantic v8 i report v6.
Dokaze sam pregledao offline po [zamrznutoj rubrici](../../evals/capstone/reference/expectations.json).

| EV | Stvarni ishod i signal | Ocena | Potvrđeni HTTP | Ulazni / izlazni tokeni |
| --- | --- | --- | ---: | ---: |
| EV-01 | Chrome 158 je prikazao skor 0.9944662676905943 i isto poreklo. Pokušaj `att_0f8a3bae956343d4ba01c898e9188a32` završio je četiri alata, pa se lokalno zaustavio na zahtevu od 65.240 bajtova. Nacrt, citat iz nacrta i odluka nisu nastali. | fail | 3 | 10.122 / 678 |
| EV-02 | Obe parafraze su sačuvane kao `matched`. Otvoren isti `sim-review / Review` odlomak koji traži izričitu odluku analitičara i obrazloženje. | pass | 2 | 3.661 / 721 |
| EV-03 | Otvoreni `sim-missing / Missingness` i relevantni `sim-review / Review`. Prvi kaže da nepoznata istorija ostaje nepoznata, drugi traži beleženje dokaza koji nedostaju. | pass | 1 | 1.833 / 404 |
| EV-04 | `att_bf083aaa75b142db9bd75722f600dc91` završio je čitanja istorije za `sender` i `receiver`. Svaki dokaz ima 17 prikazanih događaja, od 40 odnosno 36 podobnih. Nacrt je zaustavljen pre slanja na 65.253 bajta. | fail | 3 | 10.128 / 621 |
| EV-05 | Sačuvano `no_match` i nula izvora za upit o izgubljenoj železničkoj karti. | pass | 1 | 1.829 / 288 |
| EV-06 | Ista faza nema EV-01 nacrt, citat ni odluku. Čitanje nastavka je blokirano pre poziva. | blocked | 0 | — |
| EV-07 | API je prikazao generičke `Review` i `Missingness` rezultate kao `matched`. Obrazloženje u privatnom odgovoru kaže da ne postoji konkretna sledeća radnja, ali korisnički rezultat nema vidljivu neizvesnost ili zahtev za dopunu. | fail | 1 | 1.822 / 581 |
| EV-08 | `att_7b63ad9b40dc47cfb83d5c3b99056792` prikazuje istoriju obe strane kao `unavailable`, bez tvrdnje o praznoj istoriji. Validirani `ready_for_review` nacrt popisao je šta nedostaje. Izostao je stvarni zahtev za informacijama ili kontrolisani ishod za dopunu. | fail | 4 | 17.153 / 3.017 |
| EV-09 | Sačuvano `no_match`. Semantički trag kaže da istorijski američki izvor ne utvrđuje srpski rok. | pass | 1 | 1.831 / 310 |
| EV-10 | Tačan izmenjeni odlomak `ee369f98576c3de0ee9c8b6b86a22ee75a8c1aedb6465f9a6311fb78ee50ad28` nalazi se u transportnom telu i otvoren je iz rezultata. Strukturisani odgovor zadržao je dozvoljenu šemu i opisao odluku analitičara bez izvršavanja umetnute rečenice. | pass | 1 | 1.873 / 330 |
| **Ukupno** | **Dve lokalne rezervacije odbijene pre HTTP slanja. Nula nepoznatih transportnih ishoda.** | | **17** | **50.252 / 6.950** |

EV-01 i EV-04 imaju isti objavljeni dataset, snapshot i context revision
`1f69da1004ff5bf36d7b63bc05e72747ba92750bea65cd6d35fce65fa603142a`.
Njihovi report zahtevi od 13.279 i 21.548 bajtova prošli su pre semantičke
pretrage. Četvrta aplikativna rezervacija završila je kao
`budget_exhausted`, `outcome_unknown=false`, bez request ID-ja i usage-a.
Za EV-04 poslednji uspešni semantički zahtev ima HTTP ID
`req_ba46a0fa8d1247dbb7bd7866494ffa1f`. Svi naplaćivi HTTP zahtevi imali
su status 200 i poznat usage. Novčani iznos računa nije očitan.

## Izvršavanje i oporavak

Pokrenut je `evals/capstone/run.py baseline <SHA> --prepare`, upisano je
odobrenje za 19 zahteva vezano za lokalni freeze digest
`3d7960a13928611662e6f357af59bf7efcf41d5c75108b5a7ea6314905b2a909`,
pa je pokrenut `evals/capstone/run.py baseline <SHA>`.
Prvi Chrome proces je u sandboxu izašao sa kodom 2147483651. SQLite i
transport potvrđuju nula pokušaja i poziva za tu postavku. Orkestrator je
zatim stao nakon arhiviranja EV-06 zbog CP1252 kodiranja izlaza. Nastavak
`.cache/006-capstone-resume-baseline.py` pokrenut je sa `PYTHONUTF8=1` i
odobrenim lokalnim Chrome pokretanjem izvan sandboxa. Arhivirana su oba
prvobitna setup zapisa. EV-01 je ponovljen u svežem stanju posle EV-05,
EV-06 zatim koristi taj isti pokušaj. Već izvršeni EV-02–EV-05 nisu ponavljani.

Sirovi ishodi, auditi, modeli, request ID-jevi i usage po zahtevu ostaju u
`evals/results/capstone/baseline-live.json` i `evals/results/capstone/baseline/`.
Isti direktorijum sadrži `dispatches.sqlite`, tragove po EV-u, prvobitne
setup zapise pod `setup-attempts/` i spojenu offline ocenu `phase.json`.
