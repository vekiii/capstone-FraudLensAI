Implementiraj navedene taskove, nemoj samo napisati plan ili novi prompt.

Radi preostali deo faze 7 — US5: Evaluation, taskove T053–T061, za `specs/003-ai-investigation`. T052 je završen i paket je zamrznut. T033 ostaje otvoren i blokira stvarno provider izvršavanje T058. Završi nezavisan rad, a zavisne taskove evidentiraj kao delimične/blokirane. Ne započinji T062+ i ne proširuj opseg na dijagnostiku T033.

FraudLens AI je obrazovni AML prototip sa kuriranim retrieval-om, kontrolisanim investigation workflow-om i ljudskim pregledom. Razlikuj determinističke testove, retrieval evaluaciju, test-provider workflow i kvalitet stvarnih LLM izveštaja.

Sve putanje su relativne u odnosu na koren projekta. Koristi checkout, bez prethodnih razgovora.

## 1. Početno čitanje i potvrđeno stanje

Pročitaj primenljive `AGENTS.md`, zatim odmah root `next_work.md`, pre planiranja i implementacije, uključujući nastavak sesije. Aktuelni zahtev određuje opseg.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/003-ai-investigation/{spec.md,plan.md,tasks.md,evaluation.md}`
- relevantne delove `research.md`, `data-model.md`, `quickstart.md` i `contracts/tools-and-provider.md`
- završni T052 approval/freeze status na početku `evidence/tasks/feature-003-evaluation-protocol.md`
- `evidence/tasks/feature-003-provider-access.md`
- relevantne prethodne workflow/recovery/review evidence zapise, bez učitavanja held-out očekivanja iz review kartica ili istorije razgovora
- postojeće `retrieval.py`, `cli.py`, provider/tools/workflow/validation module i njihove testove
- evidence/prompt konvencije i runtime/lockfile konfiguracije.

Pročitaj i primeni dostupni `.agents/skills/speckit-implement/SKILL.md` isključivo za T053–T061. Eksplicitan opseg ima prednost nad opštim zahtevom da se završi ceo tasks.md. Poštuj checklist/hook zahteve; ne menjaj oznake radi prolaska. Ne traži ponovno odobrenje za već odobreni T052 pregled.

Za svaku PowerShell Spec-kit sesiju:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
```
To ne menja Git granu.

Read-only pregled pri generisanju prompta pokazao je:
- granu `feature03` i prazan `git status --short`;
- T052 označen završenim, T053–T061 neoznačene;
- završni T052 evidence beleži Vedranovo odobrenje i freeze nad bundle-om `5cb654213934cbe11f6378eb6121ee40bfd046051d3671dbdaa082c4824f4700`;
- strukturna provera paketa i Ruff imaju zabeležen PASS; to nije model evaluacija;
- T033 capability gate nije prošao: poslednji stvarni HTTP odgovor bio je 400, bez potvrđenih tool/report-schema sposobnosti, returned model-a ili usage-a;
- prethodna autorizacija za dve transport probe je iscrpljena;
- CLI trenutno ima prepare-knowledge/probe-provider/worker, dok evaluation komande treba implementirati;
- budući ocenjivači stvarnih izveštaja nisu dodeljeni.

Ponovo proveri aktuelno stanje. Sačuvaj granu i postojeće izmene. Bez automatskog pull-a, merge-a, promene grane, reset/clean/stash, commit-a, push-a ili deploy-a.

## 2. Stroga granica development/held-out

Ovaj implementacioni razgovor mora ostati development-only do završene implementacije, development izbora i zamrzavanja konfiguracija.

- Ne učitavaj cele kombinovane inputs/reference fajlove, scenario review kartice ili istorijske evidence odeljke koji otkrivaju held-out pitanja/odgovore.
- Ne koristi široki `Get-Content`, `cat`, pretragu ili debug dump nad evaluacionim paketom.
- Za identitet/freeze proveru koristi samo neophodne metapodatke i hash-eve; sadržaj held-out stavki ne prikazuj modelu.
- Za T053 koristi male nezavisne autorske test primere i canary vrednosti.
- Za T055 koristi samo 10 development pitanja i njihove development reference. Ako su pomešani u zajedničkim fajlovima, napravi split-aware loader/projekciju koja modelu izlaže samo development stavke. Ne preuređuj zamrznuti paket radi pogodnosti.
- Tek posle T055 konfiguracionog freeze-a sme eksplicitna T056 komanda mašinski obraditi svih 20 held-out pitanja i zasebno offline pridružiti reference.
- Tokom held-out izvršavanja ne prikazuj sirova pitanja/odgovore u razgovoru; čuvaj ih u lokalnim rezultatima. Prijavljuj ID-jeve, metrike, brojeve i hash-eve.
- Posle held-out rezultata nema popravljanja prompta, glossary-ja, cutoff-a ili deployment izbora prema tim rezultatima.
- Ako otkriješ stvarni defekt, sačuvaj rezultate i exposure history; dokumentuj novu verziju/protokol. Ne predstavljaj ponovljenu evaluaciju na već izloženom holdout-u kao nezavisnu novu procenu.

Sačuvaj odobrene inputs/reference/splits/rubric i T052 approval dokaz. T055 dopunjava razvojno izabrane konfiguracije i njihove hash-eve; to nije dozvola da prepišeš T052 freeze ili očekivanja. Sačuvaj prethodni seal i eksplicitnu istoriju konfiguracionog freeze-a. Ako postojeći integrity format to ne podržava, uvedi sledljiv verzionisani zapis bez lažnog pripisivanja novog ljudskog odobrenja.

## 3. T053 — evaluation RED

Zavisnosti: T052, T028. FR-004, FR-025–FR-028.

Napiši i izvrši:
`backend/tests/unit/test_investigation_evaluation.py`

Pokrij:
- ručno izračunljive Recall@5/MRR@5 primere;
- isključivanje no-answer pitanja iz recall/MRR imenilaca;
- eksplicitne no-answer imenioce i false-answer/correct-no-match brojeve;
- overall i split-specific `en`, `sr-Latn`, `sr-Cyrl` izveštavanje;
- N/A za prazne grupe;
- zero-claim rubric, bez automatske savršene ocene;
- provider/validation failure u imenitelju;
- očuvanje originalnih neslaganja ocenjivača;
- hash/version mismatch;
- input-only generation i odvojen offline reference join;
- canary reference/label zabranu kroz tools/prompts/index i sve outbound turn/continuation putanje.

RED mora biti izvršen pad zbog očekivano nedostajućeg ponašanja. Import/collection/environment greška nije poslovni RED. Već ispravno ponašanje ne kvari radi veštačkog pada.

## 4. T054 — evaluator, CLI i jedno ograničeno retrieval poboljšanje

Zavisnost: T053. FR-025–FR-028.

Implementiraj:
- `backend/src/fraudlens/investigation/evaluation.py`
- evaluation komande u `backend/src/fraudlens/investigation/cli.py`
- poboljšanje u `backend/src/fraudlens/investigation/retrieval.py`
- pregledani `data/knowledge/fraudlens-aml-knowledge-v1/glossary.json`

Sačuvaj baseline i tačnu research.md formulu:
- `k1=1.2`, `b=0.75`;
- improved tf = body_count + 2 × title_section_count;
- dl/avgdl i dalje iz body tokena;
- original term weight 1, synonym 0.5;
- deduplikacija sa maksimalnom težinom po terminu;
- deterministički passage-ID tie-break.

Glosar pripremi iz korpusa i development konteksta, bez held-out pitanja. Stvarni zahtev za pregled ne zamenjuj agentskim ili izmišljenim ljudskim potpisom. Ako pregled nedostaje, pripremi konkretan artefakt za pregled i nastavi nezavisan rad; zavisni freeze/izvršavanje ostaju pending.

Generation putanja prima samo dozvoljene inputs. Reference se otvaraju samo u eksplicitnom offline metric/review join-u nakon zamrznutih predikcija. Runtime knowledge/tools/provider ne importuju reference loader.

CLI mora eksplicitno birati split/config; bez podrazumevanog held-out izvršavanja. Implementiraj potrebne evaluate-retrieval, evaluate-reports i summarize-reviews granice prema protokolu, ali ne pokreći stvarni provider.

GREEN zabeleži u:
`evidence/tasks/feature-003-evaluation.md`

## 5. T055 — development izbor i freeze

Zavisnost: T054. FR-025–FR-026.

Na samo 10 development pitanja:
- izračunaj obe konfiguracije;
- izaberi njihove adequacy cutoff-e prema evaluation.md;
- prvo zahtevaj nula false answers na development no-answer stavkama;
- zatim maksimalan recall na answerable stavkama, uz viši cutoff kao propisani tie-break;
- unapred izaberi deployment konfiguraciju samo prema development rezultatima.

Ako ne postoji upotrebljiv feasible cutoff, prijavi ineligible/failed quality. Ne prilagođavaj očekivanja i ne koristi held-out radi izbora.

U `evals/investigation/protocol.json` i sledljivom freeze zapisu veži corpus/tokenizer/glossary/rank/cutoff/prompt/model/settings/rubric hash-eve. Model konfiguracija može biti poznata kao zahtevana, ali capability status mora ostati neproveren dok T033 nije završen. Ne izmišljaj returned model ili uspešan live freeze.

Razdvoji freeze dovoljan za deterministički retrieval od nezavršenog live-provider gate-a. Ako neki zahtev T055 nije ispunjen, ostavi task delimičnim i ne zaobilazi njegov preduslov za T056.

Development izbor, hash-eve i ograničenja zabeleži u:
`evidence/tasks/feature-003-evaluation-protocol.md`

## 6. T056 — zamrznuta retrieval evaluacija

Zavisnost: završen T055. FR-026, SC-002, retrieval deo SC-006.

Pokreni obe zamrznute konfiguracije nad svih 20 held-out pitanja preko CLI-ja. Ovo je eksplicitna offline evaluacija nakon freeze-a, nije tuning.

Sačuvaj ranks/IDs/scores i sirove latencije u:
`evals/results/feature-003/`

Prijavi:
- macro Recall@5 i MRR@5 samo na answerable pitanjima;
- no-answer correct-no-match/false-answer rezultate i imenioce;
- overall i posebno `en`, `sr-Latn`, `sr-Cyrl`, odvojeno po split-u;
- N/A za prazne imenioce;
- obe konfiguracije, uključujući pogoršanje;
- target achievement odvojeno od unapred izabrane deployment konfiguracije.

Nema novih per-language acceptance pragova.

Izmeri 20 stvarnih lokalnih pretraga, uz zabeleženu mašinu, verzije i warm/cold politiku. Nearest-rank p95 je 19. sortirana latencija od 20; target je <=2 s. Ne izvodi latenciju iz fixture vrednosti.

Recall@5 target >=0.80, MRR@5 >=0.70 na answerable pitanjima i pravilni no-match na svim propisanim held-out no-answer stavkama. Below-target je stvarni rezultat, ne razlog za menjanje testa.

Rezultate i hash-eve zabeleži u:
`evidence/tasks/feature-003-evaluation.md`

## 7. T057 — bezbednosni/recovery paket

Zavisnosti: T042, T051, T054. FR-004, FR-010–FR-012, FR-015, FR-018, FR-024, FR-027; SC-004.

Izvrši najmanje 12 zamrznutih security/recovery scenarija. Koristi:
`backend/tests/integration/test_investigation_safety.py`
za nedostajuću RED/GREEN pokrivenost.

Pokrij injection, nedozvoljene alate/drugi case, bank/account i cutoff granice, reference/label canary, nepoznate citate, izmenjene assertions, SDK retry/budget, unknown dispatch restart, deadline, stale update/review/browser i late cancellation.

Proveravaj sve stvarno emitovane outbound turn/continuation stavke u kontrolisanom test transportu, ne samo početni prompt. Očekivani broj neovlašćenih tool/action izvršavanja je nula.

Možeš završiti deterministički/test-provider deo bez T033. Nazovi ga tako; ne tvrdi da si proverio stvarni provider saobraćaj. Ne menjaj zamrznute scenarije ili zahteve da bi prošli.

Kompletne ishode i granice zabeleži u:
`evidence/tasks/feature-003-safety.md`

## 8. T058–T061 — blokade i dozvoljen nezavisan rad

**T058** — zavisi od T033, T038, T051, T055; FR-017, FR-027–FR-028, SC-003, live deo SC-006.

Zahteva osam stvarnih held-out izveštaja i pet preizabranih ordinary live demo slučajeva, actual verified model, sve pokušaje/greške/usage/durations/tool traces.

T033 je otvoren: ne pokreći probe, evaluate-reports sa openai, real worker ili drugi provider poziv. Prethodni dvopokušajni budžet je iscrpljen. Ovaj zahtev ne odobrava T033 dijagnostiku ili novi mrežni budžet.

Pripremi input-only runner i sledljiv plan izvršavanja ako već nisu pokriveni T054. U:
`evidence/tasks/feature-003-live-reports.md`
zabeleži `blocked_by_T033`, neizvršene korake i tačne uslove nastavka. Bez fixture zamene za stvarne izveštaje. T058 ostaje neoznačen.

**T059** — zavisi od T058; FR-027, SC-003.

Zahteva stvarne ocene svih osam izveštaja i nezavisne druge ocene najmanje četiri unapred izabrana izveštaja, prema već zamrznutom subset-u. Sačuvaj originalna neslaganja i posebno razrešenje.

Možeš pripremiti validaciju/import format i uputstvo za ocenjivače. Ne popunjavaj ocene, imena, datume ili potpise. T052 odobrenje paketa nije ocena generisanih izveštaja.

Buduće stvarne ocene pripadaju:
`evals/results/feature-003/reviews.json`

Status i potrebne ljudske korake zabeleži u:
`evidence/tasks/feature-003-human-evaluation.md`

T059 ostaje blokiran dok nema T058 i stvarnih ocena.

**T060** — zavisi od T056, T057, T059; FR-026–FR-028, SC-002–SC-004, SC-006, SC-008.

Implementiraj i proveri agregacione primitive na autorskim podacima; sažmi stvarno dostupne retrieval/safety rezultate. Ne izmišljaj report support/coverage, kritične greške, usage ili live deadline rezultate.

Pravila:
- uncertain tvrdnje ostaju unsupported do stvarnog razrešenja;
- zero observational claims je N/A, ne automatski pass;
- provider/validation failures ne ispadaju iz imenitelja;
- target >=7/8 izveštaja sa >=90% support i >=80% essential coverage;
- svih osam bez critical unsupported claims;
- no-guidance slučajevi bez unsupported procedural recommendations;
- pet live demo slučajeva: >=4/5 validated/needs-information <=90 s, svi terminalni <=120 s.

Bez T059 nema kompletnog T060. Zabeleži partial/blocked, dostupne metrike i immutable result hash-eve u `feature-003-evaluation.md`.

**T061** — zavisi od T060; FR-004, FR-025–FR-028, SC-008.

Izvrši dostupan leakage/reproducibility audit: runtime reference imports, corpus/question/result binding, freeze/exposure istorija, rezultati i poznate praznine. Ne izmišljaj cene/spend ili live kvalitet i ne mešaj workflow, retrieval i ML evaluaciju.

Završni T061 ostaje delimičan/blokiran dok T060 nije kompletan. Audit već dostupnih artefakata ipak dokumentuj.

## 9. Provere, trag i predaja

Koristi postojeći Python 3.14 / Node 24 i zaključane zavisnosti. Zabeleži stvarne verzije. Ne nadograđuj SDK/runtime niti menjaj lockfile rutinski.

Iz korena, uz jedinstven workspace-local temp/cache po potrebi:
```powershell
uv run --locked pytest backend/tests/unit/test_investigation_evaluation.py
uv run --locked pytest backend/tests/unit/test_investigation_retrieval.py
uv run --locked pytest backend/tests/integration/test_investigation_safety.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
git diff --check
```

Podrazumevani suite ne sme pokrenuti provider ili stvarni held-out evaluation posao. Proveri da canary/unit testovi ne učitavaju pravi holdout. Evaluation komande pokreni tek kada implementirane i preduslovi ispunjeni; quickstart komanda nije dokaz izvršavanja.

Posle poslednjih izmena ponovi pogođene provere i pregledaj nove fajlove/diff. Environment problem razlikuj od business RED-a. Ne slabi testove, ne dodaj skip/xfail radi prolaza. Frontend proveravaj ako ga stvarno menjaš ili nalaz zahteva; ne širi ovu fazu na T065.

Pre implementacionih izmena sačuvaj tačan primljeni prompt u:
`prompts/development/003-investigation-phase-07.md`
Ako već postoji T052 original, sačuvaj ga i dodaj datiranu dopunu T053–T061, bez prepisivanja ili predstavljanja rekonstrukcije kao originala.

Održavaj:
- navedene task evidence fajlove;
- `evidence/tasks/feature-003-phase-07-handoff.md`;
- `specs/003-ai-investigation/tasks.md`;
- kratak aktuelni `next_work.md`.

Beleži početnu granu/commit, postojeće izmene, verzije, komande/exit kodove, RED/GREEN, configuration/result hash-eve, development/held-out razdvajanje, exposure istoriju i blokade. Ažuriraj predaju posle koherentne celine, ne samo na kraju.

T052 ostaje završen; ne otvaraj ponovo odobreni pregled bez konkretnog integrity nalaza. T033 ostaje otvoren. Delimični/blokirani T058–T061 ne dobijaju checkbox samo zato što su runner, šablon ili pending zapis napravljeni.

Sačuvaj foundation, feature 002/ML ugovore/scorere/bazu i deljeni `.agents`/`.specify` sadržaj. Ne uvodi produktne tehnike van odobrenog obima. Ne pokreći subagente osim ako ih primenljive instrukcije zahtevaju; agenta ili LLM judge ne koristi kao zamenu za stvarne ocenjivače.

Na kraju kratko navedi:
- završene, delimične i blokirane T053–T061;
- stvarne testove, retrieval/safety rezultate i kvalitetne promašaje;
- T033 → T058 → T059 → T060 → T061 blokirajući lanac;
- šta nije izvršeno i zašto;
- handoff putanju i jedan konkretan sledeći korak.

Ne proglašavaj celu fazu ili feature završenim dok live/human uslovi nedostaju. Ne započinji T062+ niti samostalno ponavljaj provider probe.

## Glossary review deferral - 2026-11-15

User: "Vazi, pregledacu kada zavrsis sve". Review is deferred, not approved.
Finish independent work, preserve staged/null review metadata and pending gates.
