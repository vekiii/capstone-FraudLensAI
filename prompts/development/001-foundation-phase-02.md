Implementiraj, nemoj samo predložiti plan ili generisati novi prompt.

Radi na FraudLens AI feature-u `specs/001-project-foundation`, isključivo fazi 2 — Foundational (Blocking Prerequisites), taskovima T006–T007. Završi ovaj opseg i stani pre T008.

FraudLens AI je Bootcamp AML prototip. Foundation koristi lokalne sintetičke podatke i FastAPI + vanilla TypeScript/Vite; ne zahteva ML trening, RAG, stvarne podatke ili LLM ključ. Oslanjaj se na checkout, bez konteksta prethodnih razgovora. Sve putanje ispod relativne su u odnosu na koren repozitorijuma.

## 1. Pročitaj i proveri početno stanje

Odmah nakon primenljivih `AGENTS.md` instrukcija pročitaj root `next_work.md`, pre planiranja ili implementacije. Ponovi to pri nastavku prekinute sesije. Ovaj zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/001-project-foundation/{tasks.md,spec.md,plan.md,data-model.md}`
- `specs/001-project-foundation/contracts/{schemas.json,api.md}`
- relevantne delove `specs/001-project-foundation/{research.md,quickstart.md}`
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md`
- `evidence/tasks/phase-01-handoff.md`, naročito završni runtime amendment
- `docs/decisions/foundation.md`
- postojeće `pyproject.toml`, `.python-version`, `uv.lock` i backend kod/testove.
Za širi odobreni kontekst koristi `original_idea.md` po potrebi.

Pročitaj i primeni dostupni lokalni skill `.agents/skills/speckit-implement/SKILL.md`, isključivo za T006–T007. Eksplicitan opseg ima prednost nad opštim zahtevom da se izvrši ceo tasks.md. Poštuj stvarne checklist/hook zahteve; ne menjaj oznake radi prolaska. Ako postoji zahtev za odlukom koja nije već odobrena, navedi tačan izvor i razlog. Ne traži ponovnu potvrdu za odobrene rutinske korake.

Za Spec-kit eksplicitno postavi sesijski izbor:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/001-project-foundation'
```
To ne menja Git granu.

Pri generisanju ovog prompta read-only pregled je pokazao:
- granu `initialization` i prazan `git status --short`;
- T001–T005 označene završenim, T006–T007 neoznačene;
- u backend-u samo `backend/src/fraudlens/__init__.py`, bez ugovora i testova;
- postojeće faza-1 evidence zapise o setup proverama, bez behavior testova;
- Python 3.14 i Node 24 kao usvojene runtime-e.

Ponovo proveri stvarno stanje; ovo nije dokaz da su provere sada izvršene. Raniji Python 3.12 / Node 22 zapisi su istorijski. Aktuelni evidence navodi projektni Python 3.14.3, ali zabeleži stvarno korišćenu verziju. Generički „design only/not started” naslovi u starijim dokumentima nisu pouzdan status implementacije: uporedi taskove, kod i evidence bez usputnog prepisivanja specifikacija.

Sačuvaj trenutnu granu i postojeće izmene. Ne radi automatski pull, promenu grane, reset, clean ili stash. Prljavo radno stablo samo po sebi nije blokada.

## 2. Tačan opseg

**T006 — FR-006/FR-010**

Napiši i izvrši RED validacione testove u:
`backend/tests/contracts/test_models.py`

Koristi autoritativni ugovor:
`specs/001-project-foundation/contracts/schemas.json`

Pokrij:
- zatvorene objekte, uključujući ugnježdene objekte;
- ID-jeve `^TX-[0-9]{3}$` i `^CASE-[0-9]{3}$`;
- neprazne account stringove, najviše 120 znakova;
- amount kao nenegativan decimalni string sa tačno dve decimale;
- currency kao tačno tri velika slova;
- UTC timestampove;
- konačan numerički score u opsegu [0, 1];
- source `fixture`, `rules` ili `model`;
- neprazan `scorer_version`, najviše 80 znakova;
- neprazno `explanation`, najviše 500 znakova;
- odsustvo ground-truth labela.

Sačuvaj stvarni RED dokaz u `evidence/tasks/T006.md`.

**T007 — FR-006**

Implementiraj:
`backend/src/fraudlens/contracts.py`

Implementacija mora zadovoljiti T006 i postojeći JSON Schema. Eksplicitno testiraj JSON Schema date-time format checking, izvrši GREEN i rezultate dopiši u isti `evidence/tasks/T006.md`. Ne proširuj šemu prećutno.

Očekivani rezultat je validirana zajednička ugovorna granica, bez API ruta, servisa slučajeva, fixture scorer-a ili UI-ja.

## 3. Testovi i implementacija

Radi sekvencijalno: T006 RED → T007 implementacija → GREEN → potrebni refactor i regresija.

Koristi Pydantic 2 za backend modele, prema planu. U testovima proveravaj ponašanje i usklađenost sa izvornim JSON Schema ugovorom, uključujući validaciju JSON serijalizovanih modela. Ne oslanjaj se samo na šemu koju generiše sama implementacija.

Obuhvati relevantne definicije iz `$defs`: Transaction, RiskAssessment, CaseSummary, CaseDetail, CaseList, Health i Error. Za zajednička ograničenja koristi parametrizaciju i razumljive validne primere. Nisu potrebni endpoint-i da bi se proverili ovi oblici.

Važni detalji:
- Sva propisana polja su obavezna; dodatna polja se odbacuju, uključujući labele poput `isFraud`, `Is Laundering` i referentne odluke na ugnježdenim nivoima.
- `amount` ostaje string; ne pretvaraj ga u binary float. Pokrij pogrešan tip, negativan iznos, pogrešan broj decimala i nedozvoljene vodeće nule prema postojećem pattern-u.
- Pokrij granične dužine i score 0/1, pogrešne tipove, score van opsega, NaN i ±Infinity. Boolean nije JSON broj. Spreči da implicitne konverzije prihvate nevalidan ulaz.
- Timestamp mora zadovoljiti `format: date-time` i postojeći `Z$` pattern. Pokrij validan UTC primer, nevalidan datum koji se završava sa Z, nedostajuću zonu i offset zapis koji ne zadovoljava ugovor.
- Eksplicitno uključi JSON Schema format checker i dokaži testom da nevalidan date-time zaista biva odbijen. Sam `pattern: Z$` nije dovoljna provera.
- Razlikuj ograničenja izražena šemom od dodatnog zahteva konačnosti broja; JSON Schema biblioteka sama ne mora odbiti sve Python nonfinite vrednosti.
- Ne uvodi proizvoljna stroža pravila, npr. nove formate account-a, ako nisu propisana.
- Provera score/transaction identiteta pri isporuci i repository jedinstvenost pripadaju kasnijim T014–T016. Ne implementiraj njihove servise u ovoj fazi.

Napiši testove pre produkcionih validatora i stvarno ih pokreni. RED mora pokazati očekivano odsustvo ugovora/validacije; pad zbog pokvarenog okruženja nije odgovarajući RED. Ako početno nedostaje modul, jasno zabeleži taj razlog i obezbedi da konačna parametrizovana provera izvršava stvarne pozitivne i negativne validacione scenarije. Već ispravno ponašanje ne kvari radi veštačkog RED-a.

Ako naiđeš na suštinsku kontradikciju ugovora, prijavi je i sačuvaj nalaz; ne menjaj šemu ili očekivanja testa samo da dobiješ prolaz.

## 4. Preduslovi i provere

Proveri postojeći faza-1 toolchain i zaključane zavisnosti pre koda. Koristi Python 3.14 preko projekta i postojeći `uv.lock`. Po potrebi:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
```

Ne nadograđuj pakete ili runtime-e bez potrebe. Lockfile se generiše stvarnim alatom, nikada ručno. Ako nedostaje blokirajući preduslov van opsega, dokumentuj ga, završi nezavisan rad i traži odluku o potrebnom proširenju; ne popravljaj drugu fazu neprimetno.

Iz korena projekta izvrši i zabeleži stvarne ishode:
```powershell
uv run --locked pytest backend/tests/contracts/test_models.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
git diff --check
```

Prvu ciljanu pytest komandu pokreni za RED pre implementacije, zatim za GREEN. Posle završnih izmena ponovi pogođene provere. Pregledaj diff i nove fajlove. Ako ostali backend testovi još ne postoje, jasno navedi obim regresije.

Ne pokreći aplikaciju, browser smoke ili frontend suite radi ove backend faze. Odsustvo kasnijih testova nije uspeh suite-a niti razlog za implementaciju kasnijih faza. Ne dodaj novu infrastrukturu radi instalacionog problema i ne radi beskonačne retry petlje.

## 5. Evidence i trajna predaja

Pre implementacionih izmena sačuvaj originalni primljeni prompt u:
`prompts/development/001-foundation-phase-02.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune. Ne rekonstruiši prompt naknadno i ne označavaj T023 završenim.

Koristi postojeće evidence konvencije:
- `evidence/tasks/T006.md`: T006 i T007, veze ka FR-006/FR-010, originalnom promptu i ugovoru; početni commit/diff; stvarne verzije; komande, exit kodovi, očekivani i stvarni RED razlog, GREEN i regresija; ograničenja i pending human review.
- `evidence/tasks/phase-02-handoff.md`: grana/početni commit, završeni i delimični taskovi, menjani fajlovi, provere i ishodi, blokade i konkretan sledeći korak.
- `specs/001-project-foundation/tasks.md`: označi samo stvarno završene i proverene T006/T007; delimični ostaju neoznačeni uz objašnjenje. Uskladi kratak status ako je potrebno, bez menjanja drugih faza.
- `next_work.md`: ažuriraj stvarni napredak, evidence linkove, blokere/neizvršene provere i jedan konkretan naredni korak.

Osvežavaj handoff i `next_work.md` nakon taska ili koherentne celine, i pri delimičnoj predaji. Detaljne logove drži u evidence-u. Razlikuj uspeh, pad, nije pokrenuto, blokirano i nema prikupljenih testova.

Ljudski pregled i druga osoba koja reprodukuje setup ostaju pending dok se stvarno ne dogode. Ne označavaj T025/SC-001 i ne predstavljaj sintetičke ugovorne testove kao ML evaluaciju.

## 6. Granice i završni odgovor

Dozvoljene su izmene ciljnih testova i `contracts.py`, kao i usko povezanih nužnih fajlova i navedenih prompt/evidence/status zapisa. Sačuvaj `original_idea.md`, constitution, postojeće ugovore, pravila ignorisanja i deljeni `.agents`/`.specify` sadržaj. Ne regeneriši specifikacije niti preuređuj repozitorijum.

Ne uvodi stvarne podatke, ML, RAG, LLM, bazu, nove produktne funkcionalnosti ili tehnike van odobrenog obima. Ne pokreći subagente osim ako ih korisnik ili primenljive instrukcije zahtevaju. Bez commit-a, push-a, merge-a ili deploy-a.

Faza je završena kada su T006–T007 implementirani, relevantni pozitivni/negativni ugovorni testovi i format checking zaista prolaze, lint i diff provera su izvršeni, a evidence/status/handoff odgovaraju stvarnom stanju.

Na kraju kratko navedi:
- završene, delimične i nepočete taskove;
- šta je promenjeno;
- stvarne RED/GREEN i regresione rezultate;
- šta nije provereno i zašto;
- putanju `evidence/tasks/phase-02-handoff.md`;
- prvi sledeći dozvoljeni korak: nakon završene faze 2, zasebno pokretanje faze 3 od T008.

Ne započinji fazu 3.
## Odobrenje — 2026-11-12
Odobravam ciljanu ispravku šeme

