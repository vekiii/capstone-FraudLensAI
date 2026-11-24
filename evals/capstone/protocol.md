# Zamrznuti Capstone protokol

Paket `capstone-ev-v1` koristi [manifest](manifest.json), 16 verzionisanih
[izvršnih ulaza](inputs/cases.json) i odvojenu [offline rubriku](reference/expectations.json).
Digest svakog reda i konkretnog početnog stanja koristi kanonski JSON projekta.
Digest fajla odnosi se na njegove bajtove u lokalnom checkoutu. Vezani izvor
skora je kompletni T098 `run_boosted_candidate_smoke` sa kompatibilnim lokalnim
indeksom. EV-08 koristi isti skorovani store i zaista odsutan izvor istorije.
EV-10 koristi zaseban sintetički odlomak sa stvarnim [ljudskim pregledom](../../prompts/development/006-capstone-phase-04.md).

## Dve primarne faze

1. Izabrati tačan testirani commit u čistom stablu. Paket je pripremljen posle T009–T011.
   Pripremna komanda vezuje tačan SHA baseline-a i zaseban finalni SHA za isti manifest,
   javne ulaze i drajver. Manifest nezavisno beleži digest offline očekivanja.
2. Koristiti isti model i profil u obe faze. Ovaj prolaz koristi `gpt-6-luna`, semantic
   v8 i report v6 sa grupisanim alatima, niskim reasoning-om i striktnim sekcijama.
   Ukupno su planirana najviše 38 HTTP zahteva, do 19 po fazi. Svaki od tri
   sveža pokušaja istrage dobija do četiri rezervacije, a sedam semantičkih upita
   po jedan transportni zahtev. EV-06 je samo čitanje. Prikupiti request ID,
   model, status i usage gde postoje, uključujući svaku izvršenu popravku ili retry.
3. Početi iz praznog lokalnog stanja za svaku fazu i svaki scenario. EV-06 preuzima
   tačan EV-01 pokušaj, nacrt, citat i review iste faze. Ako preduslov nedostaje,
   evidentirati blokadu i razlog. Browser koristi zasebne profile za kreiranje i
   ponovno otvaranje. Za EV-01 i EV-06 koriste se React, Vite proxy, FastAPI i
   Chrome. Ostale žive API operacije idu kroz FastAPI TestClient i isti eksplicitni
   worker gde je primenljivo.
4. Jedan primarni ishod po EV-u. Sačuvati prvi ishod i eventualne interne retry
   ili repair korake. Dodatni pokušaj zahteva razlog, sačuvan prvi trag i preostali
   autorizovani obim. Kod nepoznatog transportnog ishoda ili greške pristupa/budžeta
   zajednički ledger zaustavlja slanje po pravilima postojećeg harness-a.
5. Tek posle arhiviranja ishoda offline spojiti opažanja sa zamrznutom rubrikom.
   Proveriti sadržaj otvorenih izvora i navodâ. Upisati po jedan status na svih
   16 redova. Očuvati stvarne padove, blokade, neizvršenja, potrošnju i razloge.
   Cena sa računa je zaseban podatak od potvrđenih usage tokena.

## Komande

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:PYTHONPATH = 'backend/src'
$phase = 'baseline' # ili final, na odgovarajućem čistom commitu
$revision = git rev-parse HEAD
.venv/Scripts/python.exe evals/capstone/run.py $phase $revision --prepare
```

U ignorisanom `evals/results/capstone/<faza>/approval.json` operater beleži stvarno
odobrenje. Polja su `approved` (true), `stage`, `model`, `maximum_requests`,
`freeze_sha256` (digest lokalnog `freeze.json`) i `user_authorization` (tačan zapis
odobrenja). Transport proverava taj zapis pre dispatcha. Ključ se čita kroz
postojeće serversko podešavanje. Kada je Chrome van standardne Windows putanje,
postaviti `CAPSTONE_CHROME`. Portovi 5173, 8000 i 9229 moraju biti slobodni.

```powershell
.venv/Scripts/python.exe evals/capstone/run.py $phase $revision
.venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_capstone_negative.py --basetemp "evals/results/capstone/$phase/negative-state" --junitxml "evals/results/capstone/$phase/negative.xml"
npm.cmd --prefix web run test -- --run tests/investigation-reports.test.ts
```

Sirova opažanja, SQLite stanje, transportni zahtevi i odgovori su lokalni u
`evals/results/capstone/`. EV-10 korpus se rekonstruiše i proverava u zasebnoj
ignorisanoj putanji van evaluacionog stabla. Git dokazi sadrže pročišćene
sažetke, digeste i identifikatore potrebne za proveru.
