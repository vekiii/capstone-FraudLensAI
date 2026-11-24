# Feature 06 — dopunski upareni EV-06

22. novembar 2026, Europe/Belgrade. [Protokol](../../specs/006-capstone-evaluation/contracts/sc-002-supplemental-ev06.md).

## Zamrznuto stanje

- Isti T098 dataset slučaj `C6c481448f7d25af15beea1309f44ee58`, transakcija `D4e050598f0f526f6fe690bb4874e2ee5` i snapshot `run_boosted_candidate_smoke`.
- Jedan test-provider pokušaj `att_158cb6ec205b4fdb8e19091a9be81b0c`, sa dva sačuvana citata i testnom odlukom `rev_1e9fcc7d0d2c4d0686aaa67ccd2bcc43`, pripremljen pre oba otvaranja. SQLite backup je napravio checkpointovanu kopiju.
- SHA-256 seed baze `29abaace88be09d8863388c57f01d8d6d08b07f4f430029f3b04d08db3d55204`. SHA-256 zapisa očekivanog pokušaja, odluke i kompletnog sadržaja citata `621b813c7b2df9326126d46af276bbffce483f1b28a4a8aa9129bdce633c69c1`. T098 digest manifest `68f2538e410808de237729b737bb04327b4a0cd2c6cd3ad51c7dc1ae435ab70c`.
- Backend, ugovori i pripadajuće fixture datoteke izvučeni su iz tačnih revizija pomoću `git archive`. `git diff --exit-code` potvrdio je identičan web kod i zaključane verzije između obe revizije i zajedničkog checkouta. Postojeći browser drajver `evals/capstone/browser.ts` je korišćen u režimu `reopen` uz zaseban Chrome profil po reviziji.

## Izvršavanje

`prepare-knowledge`, kreiranje pokušaja i `worker --once` izvršeni su samo
pri izradi seed-a. Za svaku reviziju provereni su SHA radne kopije, direktna
HTTP čitanja i browser čitanje kroz React, Vite i FastAPI. Browser API je
prihvatao samo GET, inicijalizacija OpenAI adaptera bila je zabranjena u
provernom procesu, a svaka radna kopija je korišćena uz test konfiguraciju.

| Backend revizija | Direktni HTTP | Chrome 157.0.8103.79 kroz React/Vite | Novi provider zahtevi | SHA radne baze posle |
| --- | --- | --- | --- | --- |
| `5974f94` | Isti pokušaj, odluka i dva citata | Prošao, otvorena oba citata i obnovljena odluka | 0 | Isti kao seed |
| `d8acc2a` | Isti pokušaj, odluka i dva citata | Prošao, otvorena oba citata i obnovljena odluka | 0 | Isti kao seed |

Oba browser procesa izašla su sa kodom 0. Četiri zabeležena provider
zahteva pripadaju lokalnom testnom provideru pri pravljenju zajedničkog
seed-a. Brojač je ostao četiri pri oba ponovna otvaranja.

Sirovi manifest i tragovi su u ignorisanom
`.cache/sc002-ev06-3692a77e1b4d4e24996b204b22781511/`. Python launcher za
pripremu i proveru je u lokalnom `check.py`, a browser ulazi i izlazi u
`<revision>-observed/parameters.json` i `result.json`.

## Šta još treba za originalni SC-002

Istorijski baseline ostaje blokiran za EV-06. Njegov EV-01 je prešao limit
ulaza sa 65.240 bajtova pre nego što je dobio nacrt. Ciljana izmena na
`d8acc2a` smanjila je zahtev i omogućila EV-06 iz sačuvanog EV-01 pokušaja.
Ponovno čitanje iz zajedničkog seed-a izoluje funkciju ponovnog otvaranja i
ne može proizvesti istorijski nacrt koji ranije nije nastao.

Za originalni kriterijum pripremiti nov verzionisan ciklus od 16 slučajeva
po fazi. Predlog početne revizije je `d8acc2a`, na kojoj je već dokazana
mogućnost da EV-01 napravi sačuvani pokušaj. Odrediti jednu ciljanu promenu
iz stvarnog početnog traga i vezati isti paket i rubriku za završnu reviziju.
Svaki EV-06 mora da koristi EV-01 svoje nove faze. Arhivirati zasebne
rezultate i ledger bez menjanja starog para. Pri postojećem rasporedu
19 zahteva po fazi planira se najviše 38 novih zahteva, uz odobren obim i
zasebne freeze zapise pre plaćene evaluacije.
