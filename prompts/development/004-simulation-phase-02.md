Implementiraj fazu 2 — Foundational prerequisites, isključivo T002–T004, za feature `specs/004-simulation-and-prioritization`. Nemoj samo napisati plan ili novi prompt. Stani pre T005.

Cilj je zamrznuti sintetički scenario sa odvojenim ishodima, strogom validacijom i kanonskim fingerprint-om. FraudLens AI je obrazovni AML prototip; ova faza ne implementira replay, API ili UI.

Sve putanje su relativne u odnosu na koren projekta. Koristi aktuelni checkout, bez prethodne istorije razgovora.

## 1. Početno čitanje i provera

Pročitaj primenljive `AGENTS.md` instrukcije, zatim odmah root `next_work.md`, pre planiranja i implementacije, uključujući nastavak sesije. Ovaj zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/004-simulation-and-prioritization/{tasks.md,spec.md,plan.md,research.md,data-model.md,quickstart.md}`
- `specs/004-simulation-and-prioritization/contracts/replay-v1.md`
- `evidence/tasks/feature-004-setup.md`
- `evidence/tasks/feature-004-phase-01-handoff.md`
- postojeće backend modele/test konfiguraciju, `pyproject.toml`, `.python-version`, `uv.lock`
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md` i ignore pravila.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` samo za T002–T004. Eksplicitan opseg ima prednost nad opštim zahtevom da se završi ceo tasks.md. Poštuj stvarne checklist/hook zahteve; ne menjaj oznake radi prolaska. Ne traži ponovno odobrenje već autorizovanih rutinskih koraka.

U PowerShell Spec-kit sesiji postavi:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/004-simulation-and-prioritization'
```
Ovo ne menja Git granu.

Read-only pregled pri generisanju prompta pokazao je:
- granu `004-simulation-and-prioritization` i prazan `git status --short`;
- T001 završen, T002–T004 neoznačene;
- nema simulation implementacije;
- faza-1 evidence navodi uspešne locked instalacije, 8 startup i 82 frontend API testa, bez punog suite-a ili browser provere.

Ponovo proveri stvarno stanje. Sačuvaj granu i postojeće izmene. Bez automatskog pull-a, promene grane, merge-a, reset/clean/stash. Prljavo stablo nije samo po sebi blokada.

## 2. T002 — autorski scenario i odvojeni ishodi

Napravi:
- `data/fixtures/simulation/review-capacity-demo-v1.json`
- `data/fixtures/simulation/review-capacity-demo-v1.outcomes.json`

Koristi tačne quickstart vrednosti:

| Alert | Score | Review minutes | Weight | Privatni outcome |
|---|---|---:|---|---|
| A | "0.40" | 2 | "1" | negative |
| B | "0.90" | 2 | "1" | positive |
| C | "0.80" | 1 | "1" | positive |
| D | "0.20" | 1 | "1" | positive |
| E | "0.80" | 1 | "1" | negative |

Scenario ID je `review-capacity-demo`, verzija 1. Jedan window počinje na početku horizonta; svi alert-i dostupni su tada. Defaults su threshold `"0.30"` i budget 2 minuta. Sačuvaj C/E tie i stabilne ID-jeve.

Dodaj:
- eksplicitno sintetički izvor i source data version;
- dokumentovan UTC time basis i validan horizon;
- `fixture` / `illustrative_score` / scorer version provenance;
- assumptions sa stabilnim ID-jevima, na koje weight/duration reference zaista upućuju;
- `generation_seed: null` za ručno autorstvo.

Ako konkretni timestamp ili naziv verzije nije unapred propisan, izaberi jednostavnu determinističku vrednost i dokumentuj je kao autorsku pretpostavku, bez izmišljanja opaženih podataka.

Outcome fajl sadrži samo matching `scenario_id`, `scenario_version` i zasebne `{alert_id, outcome}` stavke. Ne ugrađuj outcome u alert facts ili buduću javnu projekciju. Missing outcome znači unknown.

Stvarni content hash izračunaj implementiranim kanonskim postupkom; ne upisuj izmišljeni digest kao konačan. T002 proveri kroz uspešno učitavanje T004.

## 3. T003 — RED ugovorni testovi

Napiši i izvrši:
`backend/tests/contracts/test_simulation_contracts.py`

Koristi inline/temp podatke tako da testovi ne zavise samo od bundled primera. Pokrij:
- duplicate/mismatched scenario i alert identitete;
- nevalidne ID-jeve i unresolved assumption reference;
- nevalidan UTC, horizon i window redosled;
- first window različit od horizon start-a;
- 0 i više od 12 window starts, start van horizonta;
- do 250 alerts i odbacivanje 251;
- dostupnost alert-a u `[horizon_start, horizon_end)`;
- nevalidan score/weight/minutes i numeric tipove;
- foreign/duplicate outcome ID-jeve i pogrešan scenario identitet;
- duplirani scenario ID/version sa konfliktnim sadržajem;
- unknown polja u zatvorenim objektima;
- validan prazan scenario i prazan ili delimičan outcome set.

Posebno proveri kanonske fingerprint-e:
- ekvivalentni decimalni zapisi daju isti hash;
- ekvivalentna UTC preciznost daje isti hash;
- promenjen ulazni redosled alerts/outcomes/assumptions ne menja hash;
- promena outcome sadržaja menja hash;
- stvarna promena relevantnih facts/metadata menja hash;
- `content_sha256` se ne uključuje u sopstveni hash.

RED mora pasti zbog nedostajuće validacije ili fingerprint ponašanja. Import/collection/environment problem nije dovoljan RED. Po potrebi uvedi minimalnu importabilnu granicu bez gotovog ponašanja da testovi izvrše assertions.

Ne implementiraj replay testove iz T005. Postojeće ispravno ponašanje ne kvari radi veštačkog pada.

## 4. T004 — strogi modeli i lokalni katalog

Implementiraj:
- `backend/src/fraudlens/simulation/models.py`
- `backend/src/fraudlens/simulation/scenarios.py`
- minimalni package initializer ako je potreban.

Poštuj ugovor i data-model:

**Tipovi i granice**
- Closed payloads; odbacivanje nepoznatih polja.
- Case-sensitive ASCII ID: 1–80 slova, cifara, `_` ili `-`.
- Positive JavaScript-safe integers za verzije i durations; nonnegative safe integers za budget i seed. Boolean nije validan integer.
- Score/threshold/weight su decimalni JSON stringovi do 128 znakova: unsigned plain decimal, bez eksponenta i integralnih vodećih nula.
- Score/threshold u [0,1]; weight strogo pozitivan; nema nonfinite vrednosti ili tihog float/string coercion-a.
- RFC3339 UTC sa sekundama, završnim `Z` i najviše šest fractional digits; proveri stvarni datum, ne samo regex.
- Horizon start < end; 1–12 strictly increasing window instants unutar horizonta, prvi jednak start-u.
- Najviše 250 jedinstvenih alert-a; svi available_at unutar horizonta.
- Jedan scenario-wide score source/version i sve assumption reference razrešene.
- Outcome set zasebno validiran i vezan za isti scenario ID/version.

**Kanonski hash**
- SHA-256, lowercase hex.
- Hash objekta sa ključevima `scenario` i `outcomes`.
- Scenario metadata bez `content_sha256`, uz normalizovane facts i odvojeni outcome objekat.
- Sorted object keys, compact UTF-8 JSON, bez ASCII escaping-a i NaN.
- Decimalima ukloni završne fractional nule i preostalu decimalnu tačku.
- UTC canonical forma uvek ima šest fractional digits.
- Sortiraj alerts, outcomes i assumptions po ascending ID; ostali array redosledi ostaju.
- Odsutan seed kanonski predstavljaj kao null.

Koristi tačnu decimalnu/kanonsku obradu koja ne gubi dozvoljenu preciznost. Ne uvodi zavisnost od mašinskog newline-a, putanje ili neodređenog redosleda.

**Katalog i izolacija**
- Učitavaj bundled facts/outcomes samo pod trusted catalog root-om.
- Ne uvodi caller-supplied filesystem putanje ili proizvoljne source podatke.
- Jedan scenario ID/version označava nepromenljivu reviziju; konflikt sadržaja je catalog error.
- Proveri izračunati digest i deklarisani scenario fingerprint.
- Odvoji label-free facts od privatnih outcomes u povratnoj granici, tako da budući replay ne dobija labels.
- Hash sme vezati oba skupa radi reprodukcije; to nije dozvola da outcome vrednosti dospeju u ranking input ili javni catalog payload.
- Ne dodaj bazu, migracije ili runtime zavisnost od Feature 02.

Pokreni T003 GREEN i proveri stvarno učitavanje oba T002 fajla. Sačuvaj dokaz da dobijena revizija ima validan fingerprint i odvojene facts/outcomes.

## 5. Provere i opseg

T002/T003 mogu logički napredovati nezavisno, ali radi sekvencijalno radi jasnog evidence-a: T002 priprema → T003 RED → T004 GREEN → završna provera T002. `[P]` ne zahteva subagente.

Koristi postojeći Python 3.14 i zaključane zavisnosti. Zabeleži stvarne verzije. Po potrebi:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
```

Pokreni iz korena:
```powershell
uv run --locked pytest backend/tests/contracts/test_simulation_contracts.py
uv run --locked pytest backend/tests/integration/test_startup.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
git diff --check
```

Prvu komandu izvrši za RED pre validatora, zatim za GREEN. Za Windows temp/cache probleme koristi jedinstvene apsolutne `.cache` putanje sa `--basetemp` i `-o cache_dir`. Environment problem razlikuj od business RED-a.

Posle poslednjih izmena ponovi pogođene provere i pregledaj nove fajlove/diff. Ne tvrdi da su stare brojke sveži rezultati. Frontend nije menjan ovom fazom; ne uvodi UI ili browser tok radi provere buduće funkcionalnosti.

Ako pronađeš suštinsku kontradikciju, zabeleži je umesto slabljenja ugovora/testa. Za neophodno proširenje opsega navedi razlog i traži odluku, uz završavanje nezavisnog rada. Ne popravljaj druge feature-e prećutno.

## 6. Evidence i predaja

Pre implementacionih izmena sačuvaj tačan primljeni prompt u:
`prompts/development/004-simulation-phase-02.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune.

Pošto T002–T004 ne propisuju poseban task evidence filename, vodi detaljan zapis:
`evidence/tasks/feature-004-phase-02-validation.md`

Predaju vodi u:
`evidence/tasks/feature-004-phase-02-handoff.md`

Zabeleži početnu granu/commit, postojeće izmene, prompt, task/FR veze, stvarne verzije, komande/exit kodove, očekivani i opaženi RED, GREEN/regresiju, fixture fingerprint, ograničenja i pending human review.

Posle koherentne celine ažuriraj `next_work.md` sa stvarnim napretkom, evidence linkovima, blokadama/neizvršenim proverama i jednim narednim korakom. Detaljna istorija ostaje u evidence-u.

Označi samo stvarno završene T002–T004. Delimični ostaju neoznačeni. Ne menjaj status drugih faza.

Sačuvaj originalne Cases ugovore, fixture-e i ponašanje, lockfile-ove i deljeni `.agents`/`.specify` sadržaj. Feature 02 adapter, Feature 05 infrastruktura, ML i LLM integracija su van opsega. Bez subagenata osim ako ih primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

Završni odgovor: status T002–T004, promene, stvarni RED/GREEN/regresioni rezultati, šta nije provereno, fingerprint i handoff putanja. Ako je faza završena, sledeći korak je zasebna faza 3, T005–T011.

Ne započinji replay, endpoint-e ili UI iz faze 3.