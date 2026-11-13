Implementiraj navedene taskove, nemoj samo napisati plan ili novi prompt.

Radi isključivo fazu 2 — Foundational boundaries, taskove T005–T012, za feature `specs/003-ai-investigation`. Završi izabrani opseg i stani pre T013. T012 je namerni RED za kasnije rute: njegovo završavanje ne znači da te rute treba sada implementirati ili da ceo suite mora biti GREEN.

FraudLens AI je obrazovni AML prototip. Feature 003 obuhvata kurirani RAG, kontrolisanu AI istragu, izveštaj sa dokazima i ljudski pregled, nezavisno od ML-a. Ova faza uvodi ugovore, fixture kontekst, minimalni trajni repository i početnu prompt/retrieval konfiguraciju, bez provider poziva.

Koristi aktuelni checkout, bez istorije prethodnih razgovora. Sve putanje su relativne u odnosu na koren projekta.

## 1. Početno čitanje i provera

Pročitaj primenljive `AGENTS.md` instrukcije, zatim odmah root `next_work.md`, pre planiranja i implementacije. Ponovi pri nastavku sesije. Aktuelni zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/003-ai-investigation/{spec.md,plan.md,tasks.md,data-model.md,research.md}`
- relevantne delove `evaluation.md` i `quickstart.md`
- `specs/003-ai-investigation/contracts/{schemas.json,api.md,tools-and-provider.md,producer-v2.snapshot.json}`
- autorske primere u `specs/003-ai-investigation/contracts/examples/`
- `evidence/tasks/feature-003-phase-01-handoff.md` i `feature-003-setup.md`
- `evidence/tasks/feature-003-plan-and-tasks.md`
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md`
- `data/knowledge/README.md`, `evals/investigation/README.md`, `data/fixtures/investigation/README.md`
- postojeće investigation settings i njihove testove
- postojeće foundation modele, scorer, case servis, main/settings i startup/API testove
- runtime konfiguracije, lockfile-ove i ignore pravila.

Pročitaj i primeni dostupni `.agents/skills/speckit-implement/SKILL.md` samo za T005–T012. Eksplicitan opseg ima prednost nad opštom instrukcijom da se izvrši ceo tasks.md. Poštuj stvarne checklist/hook zahteve, bez menjanja oznaka radi prolaska. Ne traži ponovno odobrenje odobrenih rutinskih koraka. Za stvarnu neodobrenu odluku navedi tačan izvor i razlog.

Za svaku PowerShell Spec-kit sesiju postavi:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
```
Ovo ne menja Git granu.

Read-only pregled pri generisanju prompta pokazao je granu `feature03`, prazan `git status --short`, T001–T004 označene završenim i T005–T012 neoznačene. Postoje investigation initializer/settings i konfiguracioni testovi; faza-1 evidence navodi 81 GREEN konfiguracioni test, 8 startup testova, 391 backend test i Ruff PASS. To nisu sveže izvršene provere ovog razgovora.

Ponovo proveri stanje i preduslove. Sačuvaj trenutnu granu i sve postojeće izmene. Bez automatskog pull-a, promene grane, reset/clean/stash ili merge-a. Prljavo radno stablo nije samo po sebi blokada.

Provider pristup/model, pregled korpusa i stvarna producer integracija nisu preduslovi ove fixture faze. Ako stvaran drugi preduslov nedostaje, završi nezavisan rad i dokumentuj blokadu; ne popravljaj neizabrane taskove neprimetno.

## 2. Redosled i TDD

Radi sekvencijalno po zavisnostima:
T005 RED → T006 GREEN → T007 RED → T008 GREEN → T009 RED → T010 GREEN → T011 → T012 RED.

T009 i T011 zavise od T006; navedeni redosled je praktičan za ovu predaju. `[P]` nije zahtev za subagentima ili paralelnim izmenama.

Za kritično ponašanje prvo napiši i izvrši test koji pada zbog očekivano nedostajućeg ponašanja, zatim implementiraj minimalnu promenu, izvrši GREEN i regresiju. Collection/import/environment greška nije poslovni RED. Po potrebi uvedi minimalnu importabilnu granicu bez gotove implementacije da bi testovi zaista izvršili assertions. Već ispravno ponašanje ne kvari radi veštačkog RED-a.

## 3. T005–T006 — ugovori i semantička validacija

**T005** — zavisi od T003/T004; FR-001–FR-004, FR-013–FR-015.

Napiši i izvrši RED:
`backend/tests/contracts/test_investigation_contracts.py`

Koristi autoritativni `contracts/schemas.json`, pinned producer snapshot i autorske primere. Pokrij:
- zatvorene objekte, obavezna polja i obavezne nullable vrednosti;
- `contract_version=1`, nepoznata polja/verzije;
- validne UTC instants, opaque ID-jeve i digeste;
- trimmed queries 1–500 znakova;
- rationale/text 1–2000, actor 1–80;
- najviše 20 stavki po report sekciji;
- nonfinite score i pogrešne tipove;
- međusobnu jednakost case/transaction/run/dataset identiteta;
- promenjene fixture metapodatke/score skalu i eksplicitno nedostupnu istoriju.

**T006** — zavisi od T005; isti zahtevi.

Implementiraj:
`backend/src/fraudlens/investigation/models.py`

Modeli i semantički validatori moraju odgovarati šemi. Izvorni foundation i producer objekti ostaju nepromenjeni. Novac ostaje izvorni string; nema float konverzije, preimenovanja directional valuta ili gubitka preciznosti.

Dodatno:
- `context_revision` računa se iz kanonskog konteksta bez samog revision polja;
- koristi pravila kanonskog JSON-a iz data-model.md: UTF-8, sorted keys, compact separators, bez NaN;
- proveri identitete i digest, ne samo JSON oblik;
- fixture `dataset_version` ostaje null, bez izmišljenih v2 metapodataka;
- dataset wrapper mora očuvati producer run/snapshot/dataset/transaction značenje;
- provider `ReportDraft` ne dobija aplikacione ID-jeve, permissions, state ili review ovlašćenja;
- ponovo validiraj mutated/constructed instance; nemoj verovati samo konstruktoru modela;
- JSON Schema validaciju testiraj sa eksplicitnim format checker-om i pravilnim lokalnim `$ref` razrešavanjem, bez mreže.

Pinned producer snapshot na `2dd815d85bfc9c2fc70a28baef9c142d551e57e0` je referenca za ugovorne testove, ne aktuelna integracija ili human approval. Njegova hash provera normalizuje checkout CRLF u LF prema dokumentovanom pravilu, bez preformatiranja JSON-a.

RED/GREEN zabeleži u:
`evidence/tasks/feature-003-contracts.md`

Ne implementiraj punu report evidence/quote validaciju iz T025/T026 unapred. Strukturna validnost i validan citation ID nisu dokaz semantičke vernosti.

## 4. T007–T008 — fixture kontekst, istorija i outbound aliasi

**T007** — zavisi od T006; FR-002–FR-004, FR-011, FR-024.

Napiši i izvrši RED:
`backend/tests/unit/test_investigation_context.py`

Pokrij:
- zamrznuti fixture snapshot digest;
- nepromenjeni foundation CaseDetail;
- nedostupne metapodatke bez lažnih v2 polja;
- stabilnost aliasa u propisanom scope-u;
- istoriju strogo pre cutoff-a;
- isključenje same-minute, budućeg i focal event-a;
- identitet bank+account;
- lookback od 7 dana;
- najviše 50 vraćenih događaja;
- razliku empty/available, unavailable i truncated.

**T008** — zavisi od T007; FR-001–FR-004, FR-011, FR-024.

Implementiraj fixture `CaseContextReader`, `HistoryReader` i outbound alias mapper u:
`backend/src/fraudlens/investigation/context.py`

Dodaj jasno autorske/sintetičke:
- `data/fixtures/investigation/contexts.json`
- `data/fixtures/investigation/history.json`

Sačuvaj originalni `data/fixtures/cases.json` i foundation odgovore.

Fixture snapshot mora vezati fixture sadržaj i scorer verziju. Promena relevantnog sadržaja mora promeniti identitet; fixture snapshot nije dataset run.

Ne zaključuj banku, timezone basis, istorijsku pokrivenost ili dataset provenance iz v1 polja ako ih izvor ne daje. Autorska istorija može biti eksplicitno označena kao takva; nedostupna istorija nije prazna istorija.

Poštuj deterministički redosled, strict cutoff, 7-day prozor i eksplicitne count/coverage/truncation metapodatke prema ugovorima. Različite valute se ne sabiraju bez odobrene konverzije.

Outbound projection mora koristiti eksplicitni field allowlist i case/run-scoped aliasing prema ugovoru. Isključi privatne labele, reference, reviewer beleške, source putanje/raw redove, tajne i nepovezane račune. Ne implementiraj stvarne tools/provider pozive.

GREEN zabeleži u:
`evidence/tasks/feature-003-context.md`

## 5. T009–T010 — minimalni transaction repository

**T009** — zavisi od T006; FR-018–FR-020, FR-022–FR-023.

Napiši i izvrši RED:
`backend/tests/integration/test_investigation_store.py`

Pokrij:
- zaseban schema v1;
- immutable contexts/evidence/reports;
- request-key replay istog payload-a i konflikt promenjenog;
- state/revision compare-and-swap;
- atomsku disposition/audit operaciju;
- rezervisanje budžeta pre dispatch-a;
- rollback i foreign keys;
- odbacivanje nekompatibilne šeme;
- konkurentne claims kroz nezavisne konekcije, bez mreže.

**T010** — zavisi od T009; isti zahtevi.

Implementiraj minimalni repository u:
`backend/src/fraudlens/investigation/store.py`

Poštuj data-model.md i ugovore:
- posebna SQLite baza, schema version 1;
- jedan aktivni worker claim globalno u investigation store-u;
- busy timeout najviše 1 sekunda;
- jedinstveni actor/operation/request identity i attempt/sequence;
- parametrizovan SQL i foreign keys;
- optimistic revisions od 1 naviše;
- kratke eksplicitne transakcije, rollback na grešku;
- nema write lock-a preko spoljnog I/O;
- nepoznata schema verzija odbija upis, bez tihe migracije;
- sačuvani context/evidence/report sadržaj se ne prepisuje;
- report digest vezuje attempt_id, context_revision i draft;
- rezervacija dispatch intent/counter-a je trajna pre simuliranog I/O; ovo nije provider implementacija.

Ne otvaraj ili menjaj feature 002 bazu. Test baze drži u jedinstvenim temp putanjama pod `.cache`; produkcioni default ostaje ignorisani `data/processed/investigations.sqlite`.

Ova faza implementira storage primitive i njihove invariants, ne puni worker/recovery/review workflow ili API iz kasnijih taskova.

GREEN zabeleži u:
`evidence/tasks/feature-003-state.md`

## 6. T011 — početni application prompt i retrieval konfiguracija

Zavisi od T006; FR-004, FR-012–FR-017, FR-028.

Zamrzni početni application prompt:
`prompts/application/investigation-v1.md`

I početnu netuniranu retrieval konfiguraciju:
`data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json`

Prompt mora razlikovati:
- činjenice, smernice i hipoteze;
- source i pravo značenje score-a;
- nedostajuće podatke i ograničenja objašnjenja;
- dozvoljeni tool scope i zabranu proizvoljnih URL/SQL/path operacija;
- nepoverljivost instrukcija unutar dokumenata/case/tool sadržaja;
- izlaz na srpskom i citiranje dozvoljenih dokaza;
- strukturnu validaciju naspram ljudske semantičke provere;
- ljudsku nadležnost za disposition.

Runtime context ne uključuje originalne razvojne promptove ili evaluacione reference.

Konfiguraciju zasnuj na research.md: početni BM25 baseline `k1=1.2`, `b=0.75`, propisana normalizacija i deterministički passage-ID tie-break, najviše 5 rezultata. Ne implementiraj retrieval ili poboljšanje iz T054. Početni cutoff/config jasno označi kao netunirani dizajn; ne tvrdi da je kvalitet potvrđen i ne tuniraj bez zamrznutog development paka.

Zabeleži stvarne verzije/hash-eve prompta i konfiguracije u setup/phase evidence-u, uz tačnu politiku hash-ovanja. To su početni dizajn artefakti, ne ljudsko odobrenje ili LLM evaluacija. Ne kreiraj zvanični korpus, glossary ili held-out odgovore.

## 7. T012 — namerni composition/error-isolation RED

Zavisi od T008/T010/T011; FR-003, FR-010, FR-021, FR-024.

Napiši i stvarno izvrši:
`backend/tests/integration/test_investigation_feature_toggle.py`

Testiraj propisano buduće ponašanje:
- isključen feature čuva originalni fixture tok i odgovore;
- nove route greške su feature-specific, odvojene od foundation `case_not_found`;
- startup ne poziva mrežu/provider;
- mutation rute imaju JSON i same-origin zaštitu;
- nema permissive CORS-a.

Testovi treba da se kolektuju i izvršavaju protiv stvarne aplikacione granice. Nedostajuće rute/guard ponašanje treba da daju konkretne assertion padove, a ne import/collection greške.

Sačuvaj postojeće prolazne disabled/foundation provere. Buduće knowledge i run rute ostavi RED do T019/T035. Ne dodaj rute, mock produkcione endpoint-e, skip ili xfail samo radi zelenog suite-a.

Zabeleži tačne node ID-jeve, očekivane razloge i stvarne ishode u:
`evidence/tasks/feature-003-api.md`

T012 može biti završen kao stvarno izvršen RED task, dok implementacija njegovih budućih ponašanja ostaje neizvršena. To jasno navedi u tasks/handoff-u.

## 8. Provere i regresija

Koristi postojeće Python 3.14 / Node 24 zahteve, konfiguracije i lockfile-ove. Proveri stvarne verzije. Po potrebi:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
```

Nema potrebe za OpenAI SDK-om ili provider probe-om u ovoj fazi. Ne čitaj ključeve. Ne regeneriši lockfile-ove rutinski; nužne promene obrazloži i koristi stvarne alate.

Ciljane komande iz korena:
```powershell
uv run --locked pytest backend/tests/contracts/test_investigation_contracts.py
uv run --locked pytest backend/tests/unit/test_investigation_context.py
uv run --locked pytest backend/tests/integration/test_investigation_store.py
uv run --locked pytest backend/tests/unit/test_investigation_settings.py backend/tests/integration/test_startup.py
uv run --locked pytest backend/tests/integration/test_investigation_feature_toggle.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
git diff --check
```

Pokreni relevantne RED komande pre njihovih implementacija, potom GREEN. Posle T012:
- izvrši i pošteno prijavi puni suite sa očekivanim preostalim RED failures;
- po potrebi posebno pokreni regresiju bez namernog T012 modula i jasno navedi da je izostavljen samo radi odvojenog izveštavanja;
- ne tvrdi da je puni suite GREEN.

Za Windows temp/cache probleme koristi jedinstvene apsolutne `.cache` putanje preko `--basetemp` i `-o cache_dir`. Setup problem nije poslovni RED. Ne isključuj behavior testove radi prolaza.

Pregledaj nove fajlove i diff, source/schema/model parity i proveri da stare fixture bajtove/odgovore nisi promenio. Posle završnih izmena ponovi pogođene provere. Frontend, browser, live producer i provider evaluacija nisu deo ove faze.

## 9. Evidence, granice i predaja

Pre implementacionih izmena sačuvaj tačan primljeni prompt u:
`prompts/development/003-investigation-phase-02.md`

Postojeći original ne prepisuj; nastavke čuvaj kao datirane dopune.

Održavaj tačne task evidence putanje:
- `evidence/tasks/feature-003-contracts.md`
- `evidence/tasks/feature-003-context.md`
- `evidence/tasks/feature-003-state.md`
- `evidence/tasks/feature-003-api.md`

Za T011 dodaj jasan zapis sa hash-evima i proverama u odgovarajući phase evidence, bez izmišljanja novog approval gate-a.

Predaja:
`evidence/tasks/feature-003-phase-02-handoff.md`

Beleži početnu granu/commit, postojeće izmene, stvarne verzije, komande/exit kodove, RED/GREEN, očekivane preostale padove, blokere, pending ljudski review i neizvršene provere. Osvežavaj handoff i root `next_work.md` posle koherentne celine, ne samo na kraju.

Task checkbox označi tek kada je ispunjen njegov tip: izvršen namerni RED, implementirani GREEN ili sačuvan/proveren artefakt. Delimični/blokirani ostaju neoznačeni. Ne menjaj stanje drugih faza.

Sačuvaj foundation odgovore, feature 002/ML ugovore/scorere/bazu, ignore politiku i deljeni `.agents`/`.specify` sadržaj. Ne importuj nezavršen ML i ne menjaj producer snapshot prećutno. Suštinsku kontradikciju prijavi umesto slabljenja šeme/testa. Za nužno proširenje opsega navedi konkretan razlog i zatraži odluku, uz završavanje nezavisnog rada.

Ne uvodi retrieval, provider, worker, review UI, korpus ingestion ili dataset adapter iz kasnijih taskova. Ne pokreći subagente osim ako ih primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

Završni odgovor neka navede:
- završene/delimične/nepočete T005–T012;
- promene i stvarne rezultate provera;
- konkretne namerne T012 RED padove i buduće T019/T035 koji ih rešavaju;
- šta nije provereno i zašto;
- putanju handoff-a;
- jedan naredni korak: ako je faza završena, zasebna faza 3 od T013; inače prvi nedovršeni task ove faze.

Ne započinji fazu 3.