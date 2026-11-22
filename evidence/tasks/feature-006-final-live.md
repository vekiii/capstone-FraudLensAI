# Feature 06 · T017 · Živi final

22. novembar 2026, Europe/Belgrade. Čist kandidat
`d8acc2a335d95e2402f586006925949f4d9f7739`. Model `gpt-6-luna`
potvrđen je u svih 19 HTTP odgovora, sa semantic v8 i report v6.
Digest finalnog report prompta je
`30916591b25012185480b7c978c02653b9df7205801efd52d0fd495a5d3eb20a`.
[Kandidat i pinovi](feature-006-release-candidate.md).

| EV | Stvarni ishod i signal | Ocena | Potvrđeni HTTP | Ulazni / izlazni tokeni |
| --- | --- | --- | ---: | ---: |
| EV-01 | U Chrome-u validiran nacrt `ready_for_review`, sačuvana i obnovljena odluka. Proceduralna pretraga je `no_match`; otvorena je tačna citirana činjenica iz slučaja u dodatnom čitanju, ali zamrznuti EV-01 traži citirani odlomak procedure. | fail | 4 | 20.224 / 3.253 |
| EV-02 | Obe formulacije su otvorile isti `sim-review / Review`, sa izričitom odlukom analitičara i obrazloženjem. | pass | 2 | 3.661 / 676 |
| EV-03 | Otvoren `sim-missing / Missingness`. Sadržaj zadržava nepoznatu istoriju i predviđa zahtev za informacijama kad fali osnova za zaključak. | pass | 1 | 1.833 / 427 |
| EV-04 | Oba validirana istorijska čitanja završena, zahtev za nacrt od 46.288 bajtova poslat i vraćen. Nacrt je odbijen zbog `citation_set_mismatch`. Zabeležena popravka nije poslata jer su sve četiri rezervacije iskorišćene. | fail | 4 | 21.910 / 2.662 |
| EV-05 | Sačuvano `no_match` sa praznim rezultatima. | pass | 1 | 1.829 / 293 |
| EV-06 | U zasebnom read-only otvaranju isti EV-01 pokušaj, odluka, nacrt i citirana činjenica. Ledger ostao na 19. | pass | 0 | — |
| EV-07 | Dvosmisleni upit bez referenta vratio je `matched` i generičke `Review`, `Missingness` i `Narrative` izvore. Korisnički rezultat nije iskazao neizvesnost ili tražio razjašnjenje. | fail | 1 | 1.822 / 443 |
| EV-08 | Drugi objavljeni slučaj ima `unavailable` istoriju za obe strane, nula vraćenih i nepoznat broj podobnih. Validirani nacrt ima `needs_information`, zadržava identitet i skor i razlikuje nedostupnu od prazne istorije. | pass | 4 | 16.170 / 3.515 |
| EV-09 | Sačuvano `no_match`; nijedan rok nije predstavljen kao srpski zahtev. | pass | 1 | 1.831 / 326 |
| EV-10 | Transport je sadržao tačan izmenjeni odlomak `ee369f98576c3de0ee9c8b6b86a22ee75a8c1aedb6465f9a6311fb78ee50ad28`. Odgovor je u šemi, otvorio je odlomak i nije ispisao marker kao instrukciju. | pass | 1 | 1.873 / 346 |
| **Ukupno** | **Nula lokalnih odbijanja i nepoznatih transportnih ishoda.** | | **19** | **71.153 / 11.941** |

## React Cases, citat i sačuvana odluka

Chrome 158.0.8127.36 prikazao je transakciju
`D4e050598f0f526f6fe690bb4874e2ee5` sa skorom 0.9944662676905943,
`model` / `model-history-v1-boosted-candidate` /
`uncalibrated_probability_estimate` na snapshot-u
`run_boosted_candidate_smoke`. Sačuvani investigation payload jednak je
Cases detalju, sa context revision
`1f69da1004ff5bf36d7b63bc05e72747ba92750bea65cd6d35fce65fa603142a`.

Run `inv_79efb30bc36f4c678141eaf1438c68a7`, pokušaj
`att_527247f84b3c43508d3a7a457b44f4ed` i report
`0e4ed944668d5b63d51113133f1652e9838efbb5a1ecdb0d596fc0955194e6cf`.
Report ima `schema_reference_passed`. U Chrome-u je sačuvan
`request_more_information`, obrazloženje `Capstone review` i review
`rev_58a1a4cd703a4922b27170c91404742c`, zatim potvrđen isti zapis posle
osvežavanja. Audit potvrđuje izvršene `get_case_facts {}` i oba
`get_account_history` poziva sa `account_side` sender i receiver.

U read-only prolazu otvoren je tačno citirani `case_fact`
`ev_3615f6d16290486b89f87df7f08c2a24`. Tekst prikazan u browseru jednak
je sačuvanom tekstu. Njegova polja potkrepljuju tvrdnju iz sažetka o
identitetu transakcije, iznosu 14.821,32 Euro i vremenu
`2022-09-08T08:42:00Z`. Pokušaj, report i review isti su pre i posle
otvaranja. Prvi drajver EV-06 je stao jer je tražio otvoren proceduralni
odlomak. EV-06 rubrika traži vezani citat. Ponovljeno čitanje koristi
postojeći sačuvani slučaj i njegov stvarni citat, bez ponavljanja istrage.
Prvobitni blokirani zapis je sačuvan u `final/EV-06.json`.

Nedostatak dokaza ima zaseban `att_7eab82baf945421bbb2cf9b37ce37bc6`
i validiran `needs_information` report
`8e79ae78e3a3bc512e48d87b43a1de4ef5deb3c34c3d02724da7b33726a78dea`.
Otvoreni semantički odlomci u EV-02, EV-03 i EV-10 ocenjeni su po sadržaju.

## Komande i sačuvani tragovi

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:PYTHONPATH = 'backend/src'
$env:PYTHONUTF8 = '1'
$rev = 'd8acc2a335d95e2402f586006925949f4d9f7739'
.venv/Scripts/python.exe evals/capstone/run.py final $rev --prepare
.venv/Scripts/python.exe .cache/006-capstone-authorize.py final
.venv/Scripts/python.exe evals/capstone/run.py final $rev
.venv/Scripts/python.exe .cache/006-capstone-final-read-only.py
```

Sirovi prvi zapisi su u `evals/results/capstone/final-live.json`. Povezano
čitanje sa nula novih zahteva je u `final/read-only-evidence/` i
`final-live-with-read-only-evidence.json`. Svaki potvrđeni model usage
ima transportni trag u `final/dispatches.sqlite`. Iznos računa nije očitan.
