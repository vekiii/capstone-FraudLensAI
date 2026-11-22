Implementiraj fazu 6 — Završna provera i predaja rada, isključivo T024–T025, za `specs/006-capstone-evaluation`. Nemoj samo napisati plan ili novi prompt.

Cilj je stvarna završna regresija na testiranom kandidatu i pošten audit pokrivenosti, revizija i dokaza. Ne menjaj produkt da bi raniji neuspešni EV rezultati izgledali uspešno i ne ponavljaj plaćenu evaluaciju.

Sve putanje su relativne u odnosu na koren projekta. Koristi aktuelni checkout, bez prethodnih razgovora.

## 1. Početno čitanje i provera

Pročitaj primenljive `AGENTS.md`, zatim odmah root `next_work.md`, pre planiranja i rada. Ponovi pri nastavku sesije. Aktuelni zahtev određuje opseg.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/006-capstone-evaluation/{tasks.md,spec.md,plan.md,quickstart.md}`
- relevantne delove `contracts/evaluation.md` i modela podataka
- `evidence/tasks/feature-006-phase-05-handoff.md`
- `evidence/tasks/feature-006-release-candidate.md`
- `evidence/tasks/feature-006-before-after.md`
- `evidence/tasks/feature-006-final-live.md`
- `evidence/tasks/feature-006-final-negative.md`
- `evidence/tasks/feature-006-capstone-evidence-map.md`
- `evidence/tasks/feature-006-peer-reproduction.md`
- `evidence/tasks/feature-006-cap08-contributions.md`
- početni setup i relevantne postojeće regresione zapise
- runtime/lockfile konfiguracije, test podešavanja i evidence/prompt konvencije.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` samo za T024–T025. Eksplicitan opseg ima prednost nad opštim zahtevom da se završi ceo tasks.md. Poštuj checklist/hook zahteve; ne menjaj oznake radi prolaska. Ne traži ponovo već evidentirana odobrenja ili potvrde.

U PowerShell sesiji:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
```
To ne menja Git granu.

Pri generisanju prompta read-only pregled pokazao je granu `006-capstone-evaluation`, prazan `git status --short`, završene T020–T023 i otvorene T024–T025. Ponovo proveri stvarno stanje.

Sačuvaj postojeće izmene. Bez automatskog pull-a, merge-a, reset/clean/stash ili prebacivanja glavnog checkout-a na drugu reviziju.

## 2. Kandidat i poznata ograničenja

Testirani aplikacioni kandidat:
`d8acc2a335d95e2402f586006925949f4d9f7739`

Baseline:
`5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`

Postojeći evidence beleži:
- baseline: 11 pass, 4 fail, 1 blocked, od 16;
- final: 13 pass, 3 fail, od 16;
- final EV-01 nema zahtevani proceduralni odlomak;
- final EV-04 ima `citation_set_mismatch`;
- final EV-07 vraća generičke pogotke bez potrebnog razjašnjenja;
- svih šest finalnih negativnih kontrola prošlo je;
- SC-002 ostaje otvoren zbog blokiranog baseline EV-06.

Faza 5 beleži Vedranovu reprodukciju i objedinjenu potvrdu četiri doprinosa prema izmenjenom US3/FR-008/SC-004. Proveri te izvore i prenesi tačan oblik potvrde; ne pretvaraj objedinjenu potvrdu u četiri zasebna potpisa i ne vraćaj ranije prevaziđene zahteve.

Sirovi rezultati faze 4 prema poslednjem handoff-u nisu lokalno dostupni u dokumentovanom `evals/results/capstone/`. Razlikuj proveru deljenih sažetaka/Git objekata od ponovne agregacije sirovih rezultata. Ne rekonstruiši nedostajuće tragove iz sažetaka.

Posle merenja ispravljena je execution schema evidencije (`run_` → `inv_`), uz zaseban digest. Sačuvaj razliku između testiranog aplikacionog SHA-a i kasnijih dokumentacionih/evidence izmena.

## 3. T024 — puna završna regresija

Tačan zahtev:
Izvrši završne pytest, Ruff, Vitest i produkcijski build komande iz quickstart-a na kandidatu. Stvarne izlaze i poređenje sa polaznim stanjem zabeleži u:
`evidence/tasks/feature-006-regression.md`

Radi u izolovanom checkout-u tačnog kandidata. Možeš ponovo koristiti postojeći izolovani checkout samo ako potvrdiš njegov HEAD, čisto stablo i odgovarajuće uslove. Inače pripremi novu lokalnu izolovanu kopiju pod `.cache`, bez menjanja glavne grane i bez brisanja postojećih kopija.

Pre izvršavanja zabeleži:
- stvarni SHA i radno stablo;
- putanju izolovanog checkout-a;
- Python, uv, Node i npm verzije;
- lockfile identitete;
- potrebne dostupne/nedostupne lokalne artefakte;
- relevantne bezbedne konfiguracione uslove.

Koristi zaključane instalacije po potrebi:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix web ci
```

Iz korena izolovanog checkout-a izvrši:
```powershell
$tempRoot = Join-Path $PWD ('.cache/006-regression-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot -ErrorAction Stop | Out-Null
uv run --locked python -m pytest backend/tests --basetemp "$tempRoot/tmp" -o "cache_dir=$tempRoot/cache"
uv run --locked ruff check backend
npm.cmd --prefix web run test -- --run
npm.cmd --prefix web run build
git diff --check
```

Build uključuje postojeći TypeScript typecheck; ne tvrdi da je dodatni zaseban typecheck izvršen ako nije.

Pre pokretanja proveri da podrazumevani testovi ne pokreću opt-in provider/evaluacione poslove. Ne učitavaj stvarni `.env`, ne šalji model zahteve i ne menjaj production store. Testovi koriste kontrolisane lokalne/mock uslove.

Za svaku komandu zabeleži:
- tačnu komandu i radni direktorijum;
- exit kod;
- collected/passed/failed/skipped/error brojeve;
- failing node ID-jeve i sažet razlog;
- upozorenja i build rezultat;
- blokade ili neizvršene delove.

Nastavi nezavisne provere kada jedna padne. Ne skrivaj padove skraćenim suite-om, skip/xfail markerima ili oslabljenim assertions.

Uporedi padove sa stvarno dokumentovanim polaznim stanjem:
- T001 je imao ciljane 84 backend i 47 React provera, ne pun suite;
- istorijska tvrdnja „puni backend je red” nije dokaz da je svaki današnji pad već postojao;
- klasifikuj nalaz kao potvrđeno postojeći, nova regresija, nedostupan preduslov ili neutvrđeno;
- dodatno lokalno poređenje na drugoj reviziji radi samo kada je potrebno da razjasni nalaz i ne menja izvore.

Nedostajuće artefakte ne zamenjuj fixture-om bez jasnog označavanja. Lokalni history indeks može zavisiti od putanje i potpisa izvora; ne kopiraj tuđi digest kao dokaz kompatibilnosti. Ne pokreći višegigabajtni rebuild ako ga testovi ne zahtevaju.

Ovaj task je izvršavanje i evidencija regresije, ne široka popravka svih feature-a. Za potreban produktni zahvat dokumentuj nalaz i konkretan predlog opsega. Ako se kandidat naknadno promeni, nova provera mora navesti novi SHA i pogođene ponovljene provere; ne prepisuj stare rezultate.

## 4. T025 — pokrivenost, revizije i bezbednost dokaza

Zavisi od T023 i izvršavanja T024.

Tačan zahtev:
Proveri FR-001–FR-008 i SC-001–SC-004, usklađenost SHA referenci, svih 16 EV i osam CAP stavki i da deljeni dokazi nemaju tajne ili zaštićene podatke. Ažuriraj `next_work.md` stvarnim stanjem, linkom na CAP mapu i narednim korakom.

U `evidence/tasks/feature-006-capstone-evidence-map.md` dopuni završni audit ili poveži poseban:
`evidence/tasks/feature-006-final-audit.md`

Audit mora obuhvatiti:

1. **FR/SC sledljivost**
   - zahtev → konkretan dokaz/test → revizija → stvarni status;
   - razlikuj task completion od prihvatanja proizvoda;
   - sačuvaj otvoreni SC-002 i sve stvarne regresione nalaze;
   - proveri SC-001, SC-003 i izmenjeni SC-004 prema aktuelnim dokazima.

2. **Revizije i digesti**
   - final live, final negative i final EV rezultati vezani su za isti kandidat;
   - baseline ima zaseban SHA;
   - T024 navodi stvarno testirani SHA;
   - kasnija dokumentacija i ispravka execution schema imaju sopstveno poreklo;
   - mismatch prijavi, ne popravljaj istorijske SHA reference radi prividne saglasnosti;
   - razlikuj Git/LF pinove i lokalne CRLF bajtove prema dokumentovanom postupku.

3. **Svih 16 EV redova**
   - svaki ID postoji u obe faze;
   - pass/fail/blocked/not_run ostaju u imenitelju 16;
   - sačuvani su isti ulazi, kriterijumi i pravilo EV-06 → EV-01;
   - 13/16 final nije „sve prošlo”;
   - nedostupne sirove rezultate jasno označi; ne tvrdi da si ih ponovo validirao.

4. **Svih osam CAP stavki**
   - dokaz, status, SHA i ograničenja;
   - tri scenarija za odbranu imaju stvarne reference;
   - validiran nacrt/citirana činjenica ne preimenuju EV-01 u pass;
   - reprodukcija i doprinosi opisani su tačno prema potvrđenom evidence-u.

5. **Deljeni fajlovi**
   - pregledaj tracked i nove predložene fajlove, relevantne veličine i ignore granice;
   - proveri da `.env`, ključevi, privatni raw rezultati, baze i lokalni artefakti ne ulaze u Git;
   - ne prikazuj potencijalne tajne u izlazu ili evidence-u;
   - ne čitaj stvarne ključeve radi poređenja;
   - ne briši legitimne pregledane sintetičke podatke ili evidence slike samo zbog tipa fajla;
   - pregled opiši kao ograničenu proveru, ne sertifikaciju cele Git istorije.

Očekivanja i evaluacione oznake ostaju van runtime/modelskog konteksta i retrieval-a. Ne otvaraj nezavisni holdout radi tuninga ili konačnog „popravljanja” rezultata.

Ako postoje nerešene rupe, ostavi ih eksplicitno otvorenim i navedi jedan konkretan naredni korak. Nema potrebe da menjaš zahteve kako bi predaja izgledala prihvaćena.

## 5. Evidence, status i granice

Pre izmena sačuvaj tačan primljeni prompt u:
`prompts/development/006-capstone-phase-06.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune.

Održavaj:
- `evidence/tasks/feature-006-regression.md`;
- završni audit i CAP mapu;
- `evidence/tasks/feature-006-phase-06-handoff.md`;
- T024/T025 status u `specs/006-capstone-evaluation/tasks.md`;
- aktuelni `next_work.md`.

Beleži početnu granu/HEAD, izolovani testirani kandidat, stvarne komande/ishode, blokade, neizvršene provere i otvorene kriterijume. Osvežavaj predaju nakon koherentne celine, ne samo na kraju.

T024 može završiti kao stvarno izvršena i dokumentovana regresija sa padovima; to nije PASS suite-a. Ako obavezne komande nisu izvršene zbog blokade, task ostaje delimičan. T025 završava audit kada je on stvarno obavljen i svi nalazi evidentirani; njegov checkbox ne znači automatsko zatvaranje otvorenih SC kriterijuma.

Za mehaničko izvršavanje/dokumentaciju nema veštačkog RED-a. Ako se zasebno odobri kritična poslovna ispravka, koristi RED → GREEN → REFACTOR i novi sledljiv dokaz, bez menjanja istorijskog merenja.

Sačuvaj aplikacioni kod, lockfile-ove, zamrznuti EV paket, izvorne baze, postojeće rezultate i deljeni `.agents`/`.specify` sadržaj. Ne uvodi drugi frontend, novu infrastrukturu ili promene modela/prompta. Ne pokreći subagente osim ako ih primenljive instrukcije zahtevaju.

Bez novih plaćenih poziva, probe-provider izvršavanja, ponavljanja live EV merenja, commit-a, tagovanja, push-a, merge-a ili deploy-a bez posebnog zahteva.

Posle završnih dokumentacionih izmena pregledaj diff i nove fajlove i pokreni `git diff --check` u glavnom checkout-u. Razlikuj tu proveru od regresije kandidata.

Završni odgovor neka kratko navede:
- status T024 i T025;
- tačan testirani SHA i stvarne pytest/Ruff/Vitest/build ishode;
- postojeće/nove/neutvrđene padove i neizvršene provere;
- otvorene EV/SC/CAP nalaze;
- putanje regresije, CAP mape i handoff-a;
- jedan konkretan sledeći korak.

Ne proglašavaj ceo feature prihvaćenim dok stvarni kriterijumi ostaju otvoreni. Git objavljivanje ostaje korisniku.