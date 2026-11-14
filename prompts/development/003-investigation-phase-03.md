# Received phase 3 instruction — 2026-11-14

The following records the received user instruction as rendered text; chat escape/line-continuation artifacts are decoded. Subsequent clarification is recorded separately below.

Implementiraj navedene taskove, nemoj samo napisati plan ili novi prompt.

Radi isključivo fazu 3 — US1: Knowledge search and sources (P1), taskove T013–T022, za feature `specs/003-ai-investigation`. Stani pre T023. Ako ljudski pregled izvora nije dostupan, završi nezavisan rad, sačuvaj konkretnu predaju i ostavi zavisne taskove pošteno delimičnim/blokiranim.

FraudLens AI je obrazovni AML prototip. Feature 003 obuhvata kurirani RAG, kontrolisanu AI istragu, izveštaje sa dokazima i ljudski pregled, nezavisno od ML-a. Ova faza isporučuje lokalnu pretragu i pregled tačnih izvora, bez provider ključa ili generisanja izveštaja.

Koristi aktuelni checkout, bez istorije prethodnih razgovora. Sve putanje su relativne u odnosu na koren projekta.

## 1. Početno čitanje i provera

Pročitaj primenljive `AGENTS.md` instrukcije, zatim odmah root `next_work.md`, pre planiranja i implementacije. Ponovi pri nastavku sesije. Ovaj zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/003-ai-investigation/{spec.md,plan.md,tasks.md,data-model.md,research.md}`
- relevantne delove `evaluation.md` i `quickstart.md`
- `specs/003-ai-investigation/contracts/{api.md,schemas.json,tools-and-provider.md}`
- `evidence/tasks/feature-003-phase-02-handoff.md`
- `evidence/tasks/feature-003-{contracts,context,state,api}.md`
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md`
- `data/knowledge/README.md`, `evals/investigation/README.md`
- `data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json`
- postojeće investigation modele/settings/store i njihove testove
- `backend/tests/integration/test_investigation_feature_toggle.py`
- postojeći backend main/settings i frontend main/views/API/ugovore, testove i konfiguracije.
Za širi odobreni produktni kontekst koristi `original_idea.md` po potrebi.

Pročitaj i primeni dostupni `.agents/skills/speckit-implement/SKILL.md` samo za T013–T022. Eksplicitan opseg ima prednost nad opštim zahtevom da se završi ceo tasks.md. Poštuj stvarne checklist/hook zahteve, bez menjanja oznaka radi prolaska. Ne traži ponovno odobrenje već autorizovanih rutinskih koraka. Za stvarno neodobrenu odluku navedi tačan izvor i razlog.

Za svaku PowerShell Spec-kit sesiju:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
```
To ne menja Git granu.

Read-only pregled pri generisanju prompta pokazao je:
- granu `feature03` i prazan `git status --short`;
- T001–T012 završene prema tipu taska, T013–T022 neoznačene;
- postoje models/context/store/settings, ali nema knowledge/retrieval/API/CLI modula ili investigation frontend-a;
- knowledge direktorijum sadrži policy README i početni retrieval.json, bez šest izvora/manifest-a;
- faza-2 evidence navodi 480 passed / 4 namerna T012 pada u punom backend suite-u, Ruff PASS;
- četiri pada pripadaju knowledge error-u, investigation attempt ruti i mutation guard-ovima;
- `retrieval.json` je `untuned_design`, sa `adequacy_cutoff: null`;
- ljudski pregled korpusa, provider i producer review ostaju pending.

To su rezultati čitanja, ne sveže izvršene provere. Ponovo proveri stvarno stanje. Sačuvaj trenutnu granu i tuđe izmene. Bez automatskog pull-a, promene grane, reset/clean/stash ili merge-a. Prljavo stablo nije samo po sebi blokada.

## 2. T013 — šest izvora i stvarni pregled

Zavisnost: T011. FR-005–FR-007, doprinos SC-001.

Pripremi:
- `data/knowledge/fraudlens-aml-knowledge-v1/manifest.json`
- izvore u `data/knowledge/fraudlens-aml-knowledge-v1/documents/`
- `evidence/tasks/feature-003-corpus-review.md`

Početni korpus mora sadržati šest tematskih dokumenata:
1. simulirana procedura pregleda/escalation;
2. simulirana procedura narrative/citation;
3. simulirana procedura za missing/conflicting facts;
4. IBM field/limitations guide;
5. i 6. najmanje dve official-source sekcije.

Za zvanične izvore i IBM značenja proveri primarne izvore. Sačuvaj tačno obuhvaćene sekcije i stvarne izvore/reuse uslove; nemoj izmišljati dozvolu ili predstavljati parafrazu kao originalni citat. Ne kopiraj sadržaj ako uslovi ne dozvoljavaju planirano čuvanje. Simulirani tekst jasno označi; strane smernice nisu srpski zakon ili stvarna politika banke.

Manifest/provenance treba da sadrže propisane source, section, version, publication date ili eksplicitno unknown sa razlogom, retrieval date, jurisdiction, historical/applicability kontekst, reuse terms i content hash.

Pripremi konkretne dokumente i manifest pre traženja ljudskog pregleda. Stvarni reviewer/date/odluka ne smeju se izmišljati niti zameniti agentskim pregledom. Ako pregled nije dostupan, zatraži pregled pripremljenih artefakata kroz ovaj razgovor, objasni da ga T013 i FR-005 zahtevaju i nastavi nezavisan rad. Ne šalji poruke kolegama preko spoljnih servisa bez ovlašćenja.

Nepregledan korpus ostaje staged/unreviewed; ne označavaj T013 ili stvarni šestodokumentni ingest završenim.

## 3. T014–T015 — knowledge loader i istorijski izvori

**T014** — zavisi od T006; FR-004–FR-007, FR-025.

Napiši i izvrši RED:
`backend/tests/unit/test_investigation_knowledge.py`

Koristi nezavisne autorske test izvore, bez oslanjanja na zvanična preuzimanja. Pokrij:
- proveru content hash-a, datuma i stvarnih review metapodataka;
- CRLF → LF normalizaciju bez trimovanja teksta;
- odbacivanje BOM i bare CR;
- passage najviše 2400 znakova i najviše 200 početnih passage-a;
- zabranu spajanja preko section granica;
- stabilne identitete subpassage-a;
- očuvanje arhiviranih verzija;
- zabranu runtime ingest-a evaluation/reference/development-prompt putanja.

**T015** — zavisi od T010/T013/T014; FR-005–FR-007, doprinos SC-001.

Implementiraj:
- `backend/src/fraudlens/investigation/knowledge.py`
- komandu `prepare-knowledge` u `backend/src/fraudlens/investigation/cli.py`

Stage/publish mora biti validiran i potpun: odbaci promenjene pregledane hash-eve, nevalidan manifest i nedozvoljene putanje. Čuvaj tačan istorijski passage tekst i provenance u zasebnom investigation store-u. Novi korpus ne menja stare passage-e ili reference.

Za long section/paragraph napravi stabilne ordinalne subpassage-e prema dizajnu, bez prelaska section granice. Corpus/passage identiteti moraju vezati verziju, sadržaj i chunker konfiguraciju.

Ne dozvoli path traversal ili zaobilaženje document-root granice, uključujući resolved putanje. Runtime ne preuzima web sadržaj i ne čita reference, razvojne promptove ili proizvoljne fajlove.

Ako T013 human review nedostaje, možeš razviti i proveriti loader na jasno sintetičkim test podacima i pripremiti staging. T015 kao celina i pravi šestodokumentni publish ostaju pending dok zavisnost nije ispunjena. Sintetički test reviewer podatak nije stvarni pregled korpusa.

GREEN i stvarni ingest, samo kada zaista izvršen, zabeleži u:
`evidence/tasks/feature-003-knowledge.md`

## 4. T016–T017 — deterministički BM25 baseline

**T016** — zavisi od T006/T011; FR-007–FR-008.

Napiši i izvrši RED:
`backend/tests/unit/test_investigation_retrieval.py`

Pokrij:
- `k1=1.2`, `b=0.75`;
- NFKC + casefold i Unicode alphanumeric tokenizaciju;
- deduplikovane query termine;
- najviše pet rangiranih passage-a;
- passage-ID ascending tie-break;
- cutoff/no-match semantiku;
- trimmed query 1–500 znakova i nepodržane ulaze;
- arhiviranu corpus/retrieval verziju;
- empty corpus/avgdl=0 kao unavailable.

**T017** — zavisi od T015/T016; FR-007–FR-008.

Implementiraj:
`backend/src/fraudlens/investigation/retrieval.py`

Prati tačnu BM25 formulu iz research.md: baseline koristi samo body tf/dl, dokumentovanu idf formulu, determinističko sortiranje i verzionisane configuration hash-eve. Rezultat razlikuje no_match, unavailable i truncation; BM25 score nije verovatnoća relevantnosti.

Početni `retrieval.json` trenutno ima null cutoff. Ne izmišljaj razvojno potvrđen threshold i ne tuniraj na pitanjima ili held-out odgovorima. Jasno definiši netunirano ponašanje prema dokumentima; ako oni ne razrešavaju null cutoff za demonstraciju, evidentiraj konkretnu odluku/kontradikciju i traži samo neophodno razjašnjenje, uz nastavak nezavisnog rada. Ne predstavljaj početni cutoff kao evaluiran.

Ne implementiraj title/glossary poboljšanje iz T054, embedding model ili mrežni servis. Testovi cutoff ponašanja mogu koristiti eksplicitne autorske test konfiguracije, bez tvrdnje da je deployment threshold izabran.

GREEN zabeleži u `evidence/tasks/feature-003-knowledge.md`. Nedostajući pravi corpus review ne opravdava lažni publish ili označavanje zavisnog taska potpuno završenim.

## 5. T018–T019 — knowledge API i minimalna kompozicija

**T018** — zavisi od T006/T012; FR-005–FR-008, FR-024.

Napiši i izvrši RED:
`backend/tests/integration/test_investigation_knowledge_api.py`

Pokrij document/search/passage endpoint-e, zatvorene šeme, bezbedne 404/422/503 odgovore, corpus pinning, path traversal odbijanje i odsustvo runtime scraping/provider poziva.

**T019** — zavisi od T017/T018; FR-003, FR-005–FR-008, FR-021.

Implementiraj knowledge rute u:
`backend/src/fraudlens/investigation/api.py`

Minimalno ih uključi u:
`backend/src/fraudlens/main.py`

Tačne rute prema ugovoru:
- `GET /api/knowledge/documents?corpus={id}`
- `GET /api/knowledge/search?q={query}&corpus={id}&retrieval={id}`
- `GET /api/knowledge/passages/{passage_id}?corpus={id}`

Koristi postojeće zatvorene modele, `contract_version=1`, kontrolisane poruke i code/status dogovor. Search ima trimmed query 1–500, najviše pet rezultata i nema browser override limita. Corpus/retrieval parametri su identiteti konfigurisanih verzija, ne putanje.

Sačuvaj foundation handler-e i postojeće odgovore. Nove knowledge greške koriste sopstveni envelope i `knowledge_unavailable`/`evidence_not_found` prema ugovoru, bez stack trace-a ili lokalnih putanja. Ne menjaj sve stare 404 greške u feature envelope.

Feature isključen ili bez korpusa ne sme pokvariti originalni case browser ili startup; nema provider inicijalizacije/mreže.

Razreši knowledge/disabled deo T012. Investigation attempt rutu i mutation guard-ove za buduće run rute ostavi stvarno RED do T035; ne dodaj placeholder rute niti skip/xfail radi zelenog suite-a.

GREEN i preostale namerne padove zabeleži u:
`evidence/tasks/feature-003-api.md`

## 6. T020–T021 — knowledge frontend

**T020** — zavisi od T006; FR-006–FR-008, FR-012, FR-021.

Napiši i izvrši RED:
`frontend/tests/investigation-knowledge.test.ts`

Pokrij:
- strogo dekodiranje zatvorenih odgovora;
- relativne URL-ove i pravilno encoded query parametre;
- source version/jurisdiction/simulation prikaz;
- no-match, error i retry;
- bezbedan literal text rendering;
- keyboard focus;
- cancellation i ignorisanje zastarelih search/selection odgovora.

**T021** — zavisi od T019/T020; isti zahtevi.

Implementiraj knowledge types/client/views/controller u:
- `frontend/src/investigation/contracts.ts`
- `frontend/src/investigation/api.ts`
- `frontend/src/investigation/views.ts`
- `frontend/src/investigation/controller.ts`

Minimalno uključi knowledge navigaciju kroz:
`frontend/src/main.ts`

Sačuvaj originalni case list/detail/back tok. Ne migriraj feature 002 case decoding. Prikazuj tačan izabrani passage i njegovu verziju/provenance, uključujući simulation/jurisdiction/historical ograničenja.

Ne koristi unchecked cast kao validaciju ili untrusted HTML. Promena upita/izbora i napuštanje pogleda moraju otkazati ili ignorisati stare rezultate. Prikaži eksplicitno unavailable/no-match, bez izmišljenih pogodaka ili AI odgovora.

GREEN, typecheck i build zabeleži u:
`evidence/tasks/feature-003-ui.md`

## 7. T022 — stvarni API/proxy/UI tok

Zavisi od T021; FR-005–FR-008, FR-021, doprinos SC-001.

Izvrši stvarno:
- knowledge pretragu;
- otvaranje i poređenje tačnog passage teksta/provenance;
- pregled istorijske verzije posle kontrolisane promene korpusa;
- no-match i missing-corpus stanje;
- originalni three-case list/detail/back/retry tok i 404/422 ponašanje.

Koristi dokumentovane lokalne backend/Vite komande, bez javnog hostovanja. Zabeleži šta je posmatrano preko realnog API-ja, proxy-ja i browser-a, sa stvarnim verzijama i ishodima u:
`evidence/tasks/feature-003-knowledge.md`

Ako koristiš headless browser, nazovi proveru automatizovanom browser proverom; nemoj je predstavljati kao ljudsko kliktanje ili peer review. Ako browser nije dostupan, evidentiraj neizvršene scenarije i ostavi T022 delimičnim. Ako koristiš autorski test korpus jer pravi review nedostaje, jasno razdvoji taj dokaz od prihvatanja šestodokumentnog korpusa.

Za background procese na Windows-u koristi skriven prozor; na kraju zaustavi samo svoje procese. Ne menjaj korisnikove browser profile ili tuđe servise.

Fixture search uspeh nije live LLM evaluacija. Ova faza ne završava automatski ceo SC-001, čiji report/citation deo pripada kasnijem radu.

## 8. TDD, regresija i komande

Radi redom po zavisnostima. RED mora biti izvršen assertion pad očekivano nedostajućeg ponašanja; collection/import/environment greška nije poslovni RED. Po potrebi uvedi minimalnu importabilnu granicu bez gotovog ponašanja. Već ispravne delove proveri bez veštačkog kvarenja.

Koristi postojeće Python 3.14 / Node 24 zahteve i lockfile-ove. Zabeleži stvarne verzije. Po potrebi:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix frontend ci
```

Nema potrebe za OpenAI SDK-om, ključem, model probe-om ili ML merge-om. Lockfile promene radi samo ako su stvarno nužne i obrazložene; koristi alat, ne ručno izmišljene hash-eve/verzije.

Ciljane provere:
```powershell
uv run --locked pytest backend/tests/unit/test_investigation_knowledge.py
uv run --locked pytest backend/tests/unit/test_investigation_retrieval.py
uv run --locked pytest backend/tests/integration/test_investigation_knowledge_api.py
uv run --locked pytest backend/tests/integration/test_investigation_feature_toggle.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run tests/investigation-knowledge.test.ts
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
git diff --check
```

Izvrši relevantne RED komande pre implementacije, zatim GREEN. Posle T019 puna regresija može zadržati samo konkretne buduće T035 padove iz T012. Zabeleži tačne preostale node ID-jeve i razloge; ne tvrdi da je puni backend suite GREEN. Dodatni regresioni podskup prijavi odvojeno sa preciznim izuzecima, bez skrivanja punog rezultata.

Za Windows temp/cache ograničenja koristi jedinstvene apsolutne `.cache` putanje sa `--basetemp` i `-o cache_dir`. Razlikuj environment grešku od business RED-a. Posle završnih izmena ponovi pogođene provere i pregledaj diff/nove fajlove.

## 9. Evidence, granice i predaja

Pre implementacionih izmena sačuvaj tačan primljeni prompt u:
`prompts/development/003-investigation-phase-03.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune.

Održavaj:
- `evidence/tasks/feature-003-corpus-review.md`
- `evidence/tasks/feature-003-knowledge.md`
- `evidence/tasks/feature-003-api.md`
- `evidence/tasks/feature-003-ui.md`
- `evidence/tasks/feature-003-phase-03-handoff.md`
- task status u `specs/003-ai-investigation/tasks.md`
- kratak aktuelni root `next_work.md`.

Beleži početnu granu/commit, postojeće izmene, verzije, tačne komande/exit kodove, stvarni RED/GREEN, browser rezultate, blokade i neizvršene provere. Osvežavaj predaju nakon taska ili koherentne celine, ne samo na kraju.

Checkbox označi tek kada je ispunjen stvarni tip/zahtev taska. Human review ne zamenjuj agentskim odobrenjem. Delimični/blokirani taskovi ostaju neoznačeni; nastavi nezavisan rad kada je moguć.

Sačuvaj feature 001 odgovore, feature 002/ML ugovore/scorere/bazu, postojeće fixture-e i deljeni `.agents`/`.specify` sadržaj. Koordiniraj minimalne shared main/frontend izmene kroz postojeće stanje; ne prepisuj tuđi rad. Ne slabi šeme ili zahteve radi prolaza. Za neophodno proširenje opsega navedi konkretan razlog i zatraži odluku.

Ne implementiraj T023+ tools/provider/report/worker/review/evaluation, ne otvaraj held-out reference radi razvoja i ne tuniraj cutoff. Ne pokreći subagente osim ako ih primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

Završni odgovor: završeni/delimični/nepočeti T013–T022, promene, stvarni rezultati provera, konkretni preostali namerni RED padovi, review/source ograničenja, handoff putanja i jedan naredni korak. Ako je faza delimična, sledeći korak je njen prvi nedovršeni uslov; tek nakon završene faze predloži zasebnu fazu 4 od T023.

Ne započinji fazu 4.

## Clarification received during work

User: „Ne znam ni na sta mislis” (regarding null cutoff).
After plain-language explanation, user: „Mislim da je pre bolje da odradimo prag, da to bude neka logicna vrednost.”
Implementation decision communicated: initial demo BM25 cutoff 0.5, explicitly not development-evaluated, no held-out tuning. This supersedes keeping null/unavailable for demo use, not later quality-evaluation gates.

## Human review clarification - 2026-11-14

User first pasted staged manifest: "Izgleda mi da ima sve". Asked whether all six
texts and source/reuse/jurisdiction notes were actually reviewed. User replied:
"Proverio sam samo manifest". This is not approval of source texts or reuse.
Actual review metadata stays null; real corpus stays staged/unpublished.
