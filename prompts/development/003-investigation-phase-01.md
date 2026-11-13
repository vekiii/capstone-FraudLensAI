Implementiraj navedene taskove, nemoj samo napisati plan ili novi prompt.

Radi isključivo fazu 1 — Setup, taskove T001–T004, za feature `specs/003-ai-investigation`. Izvrši T001 → T002 → T003 → T004 i stani pre T005.

FraudLens AI je obrazovni AML prototip. Feature 003 obuhvata kurirani RAG, kontrolisanu AI istragu, izveštaj sa dokazima i ljudski pregled, nezavisno od završetka ML-a. Ova faza uvodi samo izolovan setup, konfiguraciju i pravila razdvajanja podataka. Ne implementira retrieval, provider, izveštaje, bazu ili UI.

Koristi fajlove iz aktuelnog checkout-a, bez oslanjanja na prethodne razgovore. Sve putanje su relativne u odnosu na koren projekta.

## 1. Obavezno početno čitanje

Pročitaj primenljive `AGENTS.md` instrukcije, zatim odmah root `next_work.md`, pre planiranja i implementacije. Ponovi to pri nastavku sesije. Ovaj zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/003-ai-investigation/{spec.md,plan.md,tasks.md}`
- relevantne delove `research.md`, `data-model.md`, `evaluation.md` i `quickstart.md` iz istog direktorijuma
- `specs/003-ai-investigation/contracts/tools-and-provider.md`, posebno limite i outbound granicu
- `evidence/tasks/feature-003-plan-and-tasks.md`
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md`
- postojeće `backend/src/fraudlens/settings.py`, `main.py` i startup testove
- `pyproject.toml`, `.python-version`, `uv.lock`, `frontend/package.json`, `frontend/package-lock.json`, `.gitignore` i postojeći `.env.example`, ako postoji.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` samo za T001–T004. Eksplicitan opseg ima prednost nad opštom instrukcijom da se završi ceo tasks.md. Poštuj stvarne checklist/hook zahteve; ne menjaj oznake radi prolaska. Ne traži ponovno odobrenje već autorizovanih rutinskih koraka. Ako postoji stvaran neodobren zahtev za odlukom, navedi tačan izvor i razlog.

Za svaku PowerShell Spec-kit sesiju postavi:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
```
Ovo ne menja Git granu.

## 2. Početno stanje i preduslovi

Pri generisanju ovog prompta read-only pregled je pokazao:
- granu `feature03`;
- neversionisan `specs/003-ai-investigation/feature3_tasks_prompt.md`;
- svih 67 taskova neoznačenih;
- plan/evidence navode samo dizajn, bez feature 003 runtime implementacije;
- postojeći foundation Settings podržava samo `APP_MODE=fixture`;
- `.cache/`, `data/processed/`, `evals/results/` i stvarne `.env` vrednosti već su ignorisani;
- `evals/` još nije postojao;
- stvarni model ID/pristup, korpus i producer review ostaju neprovereni.

Ponovo proveri Git status, granu, kod i evidence. Sačuvaj trenutnu granu i sve postojeće izmene, uključujući neversionisani šablon. Ne radi reset/clean/stash, automatski pull, merge ili promenu grane. Prljavo stablo samo po sebi nije blokada.

Preduslovi su postojeći projektni toolchain i dostupni dizajn dokumenti. Model, ključ, korpus, producer integracija i završen ML nisu preduslovi ove faze. Ne popravljaj feature 002 ili njegovu ML granu.

## 3. T001 — izolovan setup

Tačan zahtev:
Napravi package/test/fixture/evaluation direktorijume prema `specs/003-ai-investigation/plan.md`, dodaj:
`backend/src/fraudlens/investigation/__init__.py`

Uspostavi evidence zapis:
`evidence/tasks/feature-003-setup.md`

Pregledaj postojeći Git rad i lockfile-ove, sačuvaj feature 002 fajlove i verzionisane deljene instrukcije. Bez novog runtime ponašanja. Zahtevi: FR-003, FR-028; nema prethodnih task zavisnosti.

Pripremi potrebnu organizaciju za:
- `backend/src/fraudlens/investigation/`
- backend testove za investigation
- `data/fixtures/investigation/`
- `data/knowledge/`
- `evals/investigation/`

Ne dodaj prazne buduće Python module, lažne fixture podatke ili `.gitkeep` samo radi brojanja direktorijuma. Prazan direktorijum nije verzionisan rezultat; smisleni fajlovi ove faze dovoljni su za predaju. Setup ne zahteva veštački RED.

## 4. T002 — konfiguracioni RED

Napiši i izvrši testove u:
`backend/tests/unit/test_investigation_settings.py`

Pokrij:
- feature je podrazumevano isključen;
- postojeća aplikacija može da se pokrene bez ključa, korpusa ili modela;
- provider prihvata samo `test|openai`;
- source prihvata samo `fixture|dataset`;
- investigation store je odvojen od feature 002 store-a;
- ključ i model konfiguracija se ne ispisuju kroz repr, logove ili validacione greške;
- limiti su konačni, pozitivni i ograničeni odozgo;
- stvarni provider zahteva eksplicitni real-model ID, bez pogađanja ili fallback-a.

Zavisnost: T001. Zahtevi: FR-017, FR-018, FR-024.

Testiraj stvarno učitavanje environment promenljivih i izoluj ih po testu. Koristi samo izmišljene canary vrednosti za proveru redakcije; ne čitaj postojeće ključeve ili `.env` tajne. Testiraj nepodržane vrednosti i granične limite, ne samo podrazumevane vrednosti.

RED mora pasti zbog očekivano nedostajuće konfiguracione validacije. Collection/import/environment greška nije poslovni RED. Obezbedi minimalnu importabilnu granicu po potrebi, bez unapred implementirane validacije, tako da se relevantni testovi zaista izvrše. Zabeleži tačan RED razlog i ishod pre T003.

Već ispravno foundation startup ponašanje proveri bez namernog kvarenja.

## 5. T003 — implementacija konfiguracije i GREEN

Implementiraj:
`backend/src/fraudlens/investigation/settings.py`

Dodaj dokumentovane primere sa praznim vrednostima za tajne/model u:
`.env.example`

Zavisnost: T002. Zahtevi: FR-003, FR-017, FR-018, FR-024.

Sačuvaj originalni Settings i `APP_MODE` bez promene njihovog značenja. Investigation konfiguracija je zasebna; ne proširuj foundation mode i ne uvodi feature composition iz kasnijih taskova.

Prati nazive iz quickstart-a:
- `INVESTIGATION_ENABLED`
- `INVESTIGATION_PROVIDER`
- `INVESTIGATION_SOURCE`
- `INVESTIGATION_STORE`
- `INVESTIGATION_ANALYST`
- `OPENAI_MODEL`
- `OPENAI_API_KEY`, isključivo privatna backend konfiguracija.

Podrazumevani režim treba da omogući isključen feature bez ključa/modela/korpusa, sa test provider-om i fixture izvorom. Ako izabrana real-provider konfiguracija zahteva model ID, nedostatak jasno odbaci prema dokumentima, uz očuvanje isključenog startup-a bez tih preduslova.

Ne izvodi model ID iz OpenAI projekta ili neformalnog „Luna” naziva. Provera prisustva eksplicitnog model ID-ja nije dokaz API pristupa ili sposobnosti modela.

Zamrzni sledeće maksimalne limite i odbaci veće override vrednosti:
- 8 provider zahteva po pokušaju;
- 12 izvršenih tool poziva;
- 120 sekundi ukupno;
- najviše 30 sekundi po zahtevu;
- najviše 48.000 UTF-8 bajtova ulaza;
- najviše 4096 izlaznih tokena;
- najviše 2 MiB odgovora, odnosno 2.097.152 bajta.

Dokumentuj jedinice i dozvoljene manje vrednosti. Ne prihvataj nulu, negativne, nonfinite ili nevalidne vrednosti. Veza timeout-a sa preostalim deadline-om i stvarna naplata budžeta pripadaju kasnijem workflow-u; ovde definiši i validiraj konfiguracione granice.

Koristi postojeće zavisnosti gde su dovoljne. Nema provider inicijalizacije na import-u, učitavanju settings-a ili startup-u; nema mrežnog poziva, probe ili instalacije OpenAI SDK-a samo radi ovog setup-a. Stvarni provider adapter pripada kasnijim taskovima.

Ne otvaraj niti kreiraj SQLite bazu, indeks ili korpus pri učitavanju konfiguracije. Default store putanja je `data/processed/investigations.sqlite`, odvojena od producer baze. Bez hardkodovanih korisničkih ili apsolutnih Windows putanja.

`.env.example` je dokumentacija, ne nova automatska `.env` loading funkcionalnost. Sačuvaj postojeće primere ako postoje. Nikakve stvarne tajne ili pretpostavljeni model ID ne ulaze u fajl.

Pokreni GREEN i rezultate zabeleži u `evidence/tasks/feature-003-setup.md`.

## 6. T004 — razdvajanje runtime/evaluation podataka

Definiši politiku u:
- `data/knowledge/README.md`
- `evals/investigation/README.md`

Zavisnost: T003. Zahtevi: FR-004–FR-006, FR-025, FR-028.

Dokumentuj:
- runtime koristi samo namerno ingestovan, pregledan korpus sa provenance/reuse podacima;
- zvanični sadržaj se ne kopira bez stvarnog porekla i uslova upotrebe;
- simulirane procedure ostaju označene kao simulirane;
- runtime open-web istraga nije dozvoljena;
- evaluation inputs, privatne reference, split/rubric i generated rezultati imaju odvojene uloge;
- runtime retrieval, alati i prompts ne smeju učitavati reference, privatne labele, skrivene reviewer beleške ili razvojne promptove;
- samo odobreni sintetički/autorski case podaci smeju kasnije izlaziti ka provider-u, kroz eksplicitni allowlist;
- stvarni customer podaci, tajne i proizvoljan pristup bazama/fajlovima nisu dozvoljeni;
- fixture/test-provider rezultati nisu live AI ili ML evaluacija.

Ne kreiraj held-out odgovore, evaluacione pakove, corpus dokumente, manifest ili stvarni outbound mapper u ovoj fazi. Njihovi kasniji taskovi ostaju nepočeti.

U `evidence/tasks/feature-003-setup.md` dokumentuj:
- jedinstvene apsolutne test temp/cache putanje pod ignorisanim root `.cache`;
- generisanu/lokalnu prirodu SQLite, indeksa i evaluation output-a;
- proverene ignore granice i eventualne nužne ciljane dopune.

Sačuvaj postojeće ignore stavke i deljeni `.agents`/`.specify` sadržaj. Ne ignoriši planirane pregledane izvore ili reproducibilnu konfiguraciju blanket pravilom.

## 7. Provere

Koristi projektne Python 3.14 / Node 24 zahteve i postojeće lockfile-ove. Zabeleži stvarno korišćene verzije.

Po potrebi:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
```

Ne regeneriši lockfile-ove ili nadograđuj zavisnosti bez nužne obrazložene promene unutar opsega. Lockfile-ovi se generišu stvarnim alatom, nikada ručno.

Iz korena projekta izvrši:
```powershell
uv run --locked pytest backend/tests/unit/test_investigation_settings.py
uv run --locked pytest backend/tests/integration/test_startup.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
git diff --check
```

Prvu komandu izvrši za RED, zatim za GREEN. Za Windows temp/cache ograničenja koristi jedinstven lokalni `--basetemp` i `-o cache_dir` pod `.cache`, uz zapis stvarnih putanja i komandi. Environment problem razlikuj od pada poslovnog ponašanja.

Proveri import postojeće aplikacije sa investigation isključenim i bez ključa/korpusa/modela, bez provider inicijalizacije ili mreže. Ne pokreći budući CLI, ingestion, worker, provider probe ili evaluaciju iz quickstart-a: oni su planirani cilj, još nisu implementirani.

Proveri relevantna ignore pravila i pregledaj diff, uključujući nove fajlove. Posle završnih izmena ponovi pogođene provere. Ne predstavljaj nedostajuće buduće testove kao prolaz. Ako puna postojeća regresija ima nezavisan pad, dokumentuj tačan nalaz; ne popravljaj neizabrani feature neprimetno.

Frontend nije predmet ove faze; ne menjaj ga niti nepotrebno ponavljaj browser tok bez nalaza koji to opravdava.

## 8. Evidence i predaja

Pre implementacionih izmena sačuvaj tačan primljeni prompt u:
`prompts/development/003-investigation-phase-01.md`

Postojeći original ne prepisuj; nastavke čuvaj kao datirane dopune sa opsegom.

Održavaj:
- `evidence/tasks/feature-003-setup.md`: T001–T004, relevantni FR, prompt, početna grana/commit, postojeće izmene, verzije, komande/exit kodovi, stvarni RED/GREEN, regresija, ograničenja i pending human review;
- `evidence/tasks/feature-003-phase-01-handoff.md`: završeni/delimični taskovi, menjani fajlovi, provere, blokade i konkretan sledeći korak;
- `specs/003-ai-investigation/tasks.md`: označi samo stvarno završene T001–T004;
- root `next_work.md`: kratak stvarni napredak, evidence linkovi, neizvršene provere/blokade i jedan naredni korak.

Osvežavaj handoff i next_work.md posle taska ili koherentne celine, ne samo na kraju. Delimičan/blokiran task ostaje neoznačen. Ne menjaj status drugih faza. Ne izmišljaj ljudski pregled, producer approval, model pristup ili nezavisnu reprodukciju.

Sačuvaj feature 001 odgovore i feature 002 ugovore/scorere/bazu. Ne importuj nezavršen ML radi fixture provere. Bez novih produktnih tehnika van odobrenog obima. Ne pokreći subagente osim ako ih primenljive instrukcije izričito zahtevaju.

Bez commit-a, push-a, merge-a ili deploy-a.

Na kraju kratko navedi završene/delimične/nepočete taskove, promene, stvarne rezultate provera, ograničenja i putanju handoff-a. Ako je faza završena, sledeći korak je zasebna faza 2, T005–T012, počev od T005 ugovornih RED testova. Ne započinji je.