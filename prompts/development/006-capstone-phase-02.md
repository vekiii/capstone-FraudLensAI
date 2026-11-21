Implementiraj fazu 2 — Preduslovi, isključivo T002–T003, za feature `specs/006-capstone-evaluation`. Nemoj samo napisati plan ili novi prompt. Stani pre T004.

Cilj je proveriti lokalni T098 snapshot i obnoviti neophodne zaključane runtime zavisnosti postojećeg provider adaptera i validacije. Ova faza ne izvršava model, dataset browser tok ili EV evaluaciju.

Sve putanje su relativne u odnosu na koren projekta. Koristi aktuelni checkout, bez prethodnih razgovora.

## 1. Početno čitanje i provera

Pročitaj primenljive `AGENTS.md`, zatim odmah root `next_work.md`, pre planiranja i implementacije. Ponovi pri nastavku sesije. Aktuelni zahtev određuje opseg.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/006-capstone-evaluation/{tasks.md,spec.md,plan.md,research.md,data-model.md,quickstart.md}`
- relevantne delove `contracts/evaluation.md` i `contracts/ev-cases.md`
- `evidence/tasks/feature-006-setup.md`
- `evidence/tasks/feature-006-phase-01-handoff.md`
- `evidence/tasks/feature-006-technical-plan.md`
- postojeći T098 transfer manifest i povezane evidence zapise, koje prvo pronađi u checkout-u ili lokalnom paketu
- postojeće Cases dataset reader-e i investigation dataset/history-index granice
- `backend/src/fraudlens/investigation/provider.py`, modele i validatore
- `pyproject.toml`, `uv.lock`, `.python-version`
- relevantne Feature 03 dependency verzije i provider testove
- evidence/prompt konvencije i ignore pravila.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` samo za T002–T003. Eksplicitan opseg ima prednost nad opštim zahtevom da se završi ceo tasks.md. Poštuj stvarne checklist/hook zahteve; ne menjaj oznake radi prolaska i ne traži ponovno odobrenje već autorizovanih rutinskih koraka.

U PowerShell sesiji:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
```
Ovo ne menja Git granu.

Read-only pregled pri generisanju prompta pokazao je:
- granu `006-capstone-evaluation` i prazan `git status --short`;
- T001 završen, T002–T003 neoznačene;
- T001 evidence navodi uspešne locked instalacije, backend 84/84 i React 47/47, typecheck/build PASS;
- postojeći provider koristi `openai` i `httpx2`, koji nisu deklarisani u trenutnim runtime dependencies;
- `jsonschema[format]` je trenutno u dev grupi, iako ga runtime validacija koristi.

Ponovo proveri stanje. Sačuvaj granu i sve postojeće izmene. Bez automatskog pull-a, merge-a, promene grane, reset/clean/stash. Ako checkout nije odgovarajući, prijavi neslaganje.

## 2. T002 — T098 integritet i read-only kompatibilnost

Tačan zahtev:
Proveri transfer digeste za:
- `data/processed/feature-003-t098-20261118/model-bounded.sqlite`
- `data/processed/feature-003-t098-20261118/source.sqlite`
- `data/processed/feature-003-t098-20261118/history-index.sqlite`

Read-only proveri:
- aktivni kompletni `run_boosted_candidate_smoke`;
- vezu history indeksa sa izvornim store-om;
- oba propisana case ID-ja;
- provenance skora.

Nalaz sačuvaj u:
`evidence/tasks/feature-006-t098-inputs.md`

Postupak:
1. Pronađi autoritativni transfer manifest i potvrdi na koje fajlove/verzije se odnosi.
2. Izračunaj stvarne SHA-256 vrednosti sva tri fajla i uporedi ih sa manifestom. Ne menjaj očekivani hash da bi provera prošla.
3. Otvaraj SQLite baze eksplicitno read-only, bez migracija, reindex-a, aktivacije run-a ili popravljanja artefakata. Sačuvaj izvorne fajlove nepromenjenim.
4. Proveri da je run kompletan i objavljen/aktivan prema postojećoj šemi, a ne samo da njegov naziv postoji.
5. Proveri source/dataset/run identitete i history-index binding prema postojećem ugovoru, uključujući digest izvornog store-a.
6. Preko postojećih read granica, gde je moguće, potvrdi oba slučaja:
   - `C6c481448f7d25af15beea1309f44ee58`
   - `C4af2f03a9d1bca5fc14d76e05af12140`
7. Potvrdi case/transaction/snapshot/dataset identitet i sačuvan score source/kind/version. Uporedi Cases i investigation čitanje iste revizije bez kreiranja istrage ili provider poziva.

Planning evidence istorijski navodi model-store digest:
`13cde42167cac02f257748633034a9461aa00648f6737ade813779845882d384`

Quickstart navodi history-index digest:
`8745ec13848f5ce0f76417fd0c2f7c731a2189cb634034aea5eeaa3a205c5a9f`

To su reference za proveru, ne zamena za autoritativni manifest ili dokaz današnjeg sadržaja. Source-store digest pronađi u odgovarajućem manifestu; ne izmišljaj ga.

Ako manifest/fajl nedostaje ili je nekompatibilan:
- zabeleži šta je provereno, šta nije i tačnu blokadu;
- ne preuzimaj, rekonstruiši ili treniraj dataset/model;
- ne zameni izvor fixture-om;
- alternativni snapshot koristi samo ako postoji stvarno odobrenje i kompatibilan ugovor;
- nastavi nezavisni T003.

Ovaj bounded snapshot je priprema demonstracije DS→LLM toka, ne nezavisna modelska holdout evaluacija. Ne čitaj privatne labele ili evaluacione reference radi provere integracije.

Drugi kandidat sam po sebi nije dokaz nedostupne istorije za EV-08. Priprema tog kontrolisanog stanja pripada kasnijem radu.

## 3. T003 — runtime dependencies i zaključano okruženje

Tačan zahtev:
Obnovi neophodne runtime zavisnosti postojećeg provider-a i validacije u `pyproject.toml`, generiši `uv.lock`, uporedi SDK/transport verzije sa Feature 03 i proveri locked sync i lokalne importe bez modelskog poziva.

Evidence:
`evidence/tasks/feature-006-provider-setup.md`

Postupak:
- Pregledaj stvarne runtime importe, postojeće adapter testove i dostupne Feature 03 verzione dokaze.
- Dodaj odgovarajuće runtime zavisnosti za `openai`, `httpx2` i validator sa potrebnom format podrškom.
- Premesti/usk­ladi `jsonschema[format]` iz dev-only položaja ako runtime zavisi od njega. Ne uklanjaj postojeći `httpx` koji koriste drugi delovi/testovi i ne prepravljaj adapter na drugi transport.
- Verzije zasnuj na proverljivom Feature 03 poreklu i kompatibilnosti sa Python 3.14. Ako istorijska verzija nije dostupna, zabeleži to umesto tvrdnje da je reprodukovana.
- Sačuvaj postojeće unrelated dependency ograničenja i pregledaj eventualne transitive promene.

Ovaj task eksplicitno odobrava stvarno generisanje lockfile-a:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv lock
uv sync --locked --group dev
uv lock --check
```

Ne piši ručno verzije/integrity hash-eve u `uv.lock`. Posle rezolucije koristi zaključane instalacije. Ne radi široku nadogradnju ostalih biblioteka radi ovog taska.

Proveri:
- stvarni projektni Python i resolved verzije relevantnih paketa;
- importe `openai`, `httpx2`, `jsonschema` i format podrške;
- import postojećih provider/model/validation modula uz odgovarajući `backend/src` import path;
- da runtime paketna deklaracija više ne zavisi od slučajnog prisustva dev-only validatora.

Ne instanciraj stvarni provider, ne čitaj `.env` ili ključeve i ne šalji zahtev. Uspešan import nije dokaz modelskog pristupa, tool/schema capability ili live kvaliteta.

Ovo je mehaničko obnavljanje dependencies: nema veštačkog RED-a. Ako pronađeš da je neophodna promena poslovnog ponašanja, prvo zabeleži nalaz i potrebni opseg; ne implementiraj T004+ prećutno.

## 4. Provere i regresija

T002 i T003 su nezavisni; ako jedan blokira, završi drugi. `[P]` ne zahteva subagente.

Pokreni relevantne postojeće offline provider/transport/validation testove koje pronađeš u checkout-u. Navedi tačne izabrane putanje i obrazloži njihovu vezu sa promenjenim dependencies. Proveri da testovi koriste mock/test transport i ne pokreću opt-in live probe.

Ponovi T001 ciljanu backend regresiju:
```powershell
uv run --locked python -m pytest backend/tests/integration/test_startup.py backend/tests/integration/test_cases.py backend/tests/integration/test_investigation_api.py backend/tests/integration/test_investigation_knowledge_api.py backend/tests/integration/test_investigation_recovery_api.py backend/tests/integration/test_investigation_review_api.py
uv run --locked ruff check backend
git diff --check
```

Koristi jedinstvene workspace-local temp putanje ako Windows pytest setup zahteva. Zabeleži stvarne komande, verzije, exit kodove i upozorenja. Razlikuj assertion pad, import/collection problem, nedostupan artefakt i environment blokadu. Ne skrivaj neuspehe skip/xfail markerima ili slabljenjem testova.

Ako dependencies promene opravdavaju dodatnu regresiju, izvrši je i prijavi stvarni obim. Ne tvrdi da je puna suite prošla kada su pokrenuti samo ciljani testovi. React nije menjan; ne uvodi frontend izmene ili drugi frontend.

## 5. Granice rada

Bez:
- izmene T098 baza, treninga/importa ili rekonstrukcije artefakata;
- React dataset binding implementacije;
- pokretanja API/worker/browser investigation toka;
- `probe-provider` ili drugog plaćenog poziva;
- EV pripreme/freeze-a, baseline/final evaluacije ili otvaranja holdout odgovora;
- promene modela, prompt profila ili provider sigurnosnih limita.

Mrežni pristup za preuzimanje Python paketa nije provider autorizacija. Model preflight pripada T008 i traži zaseban potvrđen obim/budžet.

Sačuvaj Cases/investigation ugovore, originalne artefakte, postojeću jednu React/TypeScript aplikaciju, ignore pravila i deljeni `.agents`/`.specify` sadržaj. Tajne i lokalni artefakti ostaju van Git-a.

## 6. Prompt, evidence i predaja

Pre izmena sačuvaj tačan primljeni prompt u:
`prompts/development/006-capstone-phase-02.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune.

Održavaj:
- `evidence/tasks/feature-006-t098-inputs.md`
- `evidence/tasks/feature-006-provider-setup.md`
- `evidence/tasks/feature-006-phase-02-handoff.md`
- status T002/T003 u `specs/006-capstone-evaluation/tasks.md`
- kratak aktuelni `next_work.md`.

Beleži početnu granu/commit, postojeće izmene, stvarne digeste i poreklo manifesta, kompatibilnost/identitete, dependency promene, verzije, komande/ishode, blokade i neizvršene provere.

Checkbox označi tek kada je stvarni zahtev ispunjen. Pending zapis sam po sebi ne završava T002 ako integritet/kompatibilnost nisu potvrđeni. T003 ne predstavlja provider capability proveru.

Posle koherentne celine osveži handoff i next_work.md; ne čekaj samo završni odgovor. Pregledaj diff i nove fajlove, posebno `pyproject.toml`/`uv.lock`, i proveri da pregledani izvorni artefakti nisu promenjeni.

Bez subagenata osim ako ih primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

Završni odgovor neka kratko navede status T002 i T003, proverene artefakte i dependencies, stvarne provere, blokade i handoff putanju. Sledeći korak je zasebna faza 3, T004–T008, ili konkretan nerešeni preduslov ove faze.

Ne započinji T004.

## Nastavak T002 — 21. novembar 2026.

> Rekao mi je da mozemo.

Korisnik prenosi Milanovu potvrdu za izgradnju zasebnog lokalnog indeksa iz
proverenog T098 source.sqlite i ponavljanje T002 čitanja.
