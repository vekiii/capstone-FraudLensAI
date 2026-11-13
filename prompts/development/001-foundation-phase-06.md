Implementiraj, nemoj samo predložiti plan ili generisati novi prompt.

Radi isključivo fazu 6 — Polish & Cross-Cutting Concerns, taskove T024–T027, za feature `specs/001-project-foundation`. Izvrši sav nezavisan rad koji je moguć, pošteno evidentiraj zavisnosti od ljudi i stani na granici ovog opsega. Taskove koje konvergencija eventualno doda nemoj automatski implementirati.

FraudLens AI je Bootcamp AML prototip: lokalna FastAPI + vanilla TypeScript/Vite demonstracija sa tri sintetička slučaja. Foundation ne zahteva ML trening, stvarni dataset, RAG korpus ili LLM ključ. Oslanjaj se na checkout, bez istorije prethodnih razgovora. Sve putanje su relativne u odnosu na koren projekta.

## 1. Pročitaj i proveri stanje pre izmena

Odmah nakon primenljivih `AGENTS.md` instrukcija pročitaj root `next_work.md`, pre planiranja ili implementacije, uključujući nastavak prekinute sesije. Ovaj zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/001-project-foundation/{tasks.md,spec.md,plan.md,research.md,data-model.md,quickstart.md}`
- `specs/001-project-foundation/contracts/{api.md,schemas.json}`
- `README.md`, `frontend/README.md`
- `docs/decisions/foundation.md` i `docs/decisions/fixture-scoring.md`
- `evidence/README.md`, `evidence/templates/task.md`, `prompts/README.md`
- `evidence/tasks/phase-05-handoff.md`, `evidence/tasks/T020.md`
- `evidence/tasks/T019.md`, posebno završni browser continuation i njegove granice, i povezane rezultate/verifikator
- `prompts/development/001-foundation.md`
- relevantne ranije task evidence zapise, produkcioni kod i testove prema proveri FR/SC pokrivenosti
- postojeće runtime konfiguracije, lockfile-ove i ignore pravila.
Za širi odobreni kontekst koristi `original_idea.md` po potrebi.

Pročitaj i primeni dostupne lokalne skill-ove:
- `.agents/skills/speckit-implement/SKILL.md`, samo za T024–T027;
- `.agents/skills/speckit-converge/SKILL.md`, za T027.

Eksplicitan opseg ima prednost nad opštim zahtevom da se završi ceo tasks.md ili novododati taskovi. Poštuj stvarne checklist/hook zahteve; ne menjaj njihove oznake radi prolaska. Ako traže odluku koja nije već odobrena, navedi tačan izvor i razlog. Ne uvodi dodatne potvrde za odobrene rutinske korake.

Za Spec-kit eksplicitno postavi:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/001-project-foundation'
```
Ovo bira feature, ne Git granu.

Pri generisanju ovog prompta read-only pregled je pokazao:
- granu `initialization` i prazan `git status --short`;
- T001–T023 označene završenim, T024–T027 neoznačene;
- završni evidence faze 5 navodi 310 backend testova i Ruff PASS; prethodni T019 navodi 151 frontend test, typecheck/build i browser proveru;
- T019 završni zapis pokriva 16 headless Chrome scenarija plus Enter i 390px viewport, uz eksplicitno dokumentovan fault injection;
- to nije ručno kliktanje, screen-reader provera ili reprodukcija drugog člana;
- postoje zastarele tvrdnje u README.md, frontend/README.md, spec.md, plan.md i quickstart.md;
- trenutni constitution nema privremeni Sync Impact Report;
- ljudski review i stvarna peer reprodukcija ostaju pending.

To su nalazi iz čitanja, ne sveže izvršene provere. Ponovo proveri aktuelno stanje. `next_work.md` navodi da su izmene faze 5 nekomitovane, dok je pri generisanju ovog prompta status bio prazan: razreši neslaganje proverom Git stanja, bez nagađanja.

Sačuvaj stvarnu radnu granu, originalno `initialization`, i sve postojeće izmene. Bez automatskog pull-a, promene grane, reset/clean/stash operacija. Prljavo radno stablo nije samo po sebi blokada.

## 2. T024 — proveri sve zahteve i ispravi stvarno zastarele izvore

Tačan zahtev:
Pregledaj pokrivenost svih FR i SC u `specs/001-project-foundation/tasks.md` i `specs/001-project-foundation/spec.md`; stvarne promene ažuriraj na njihovom izvoru, bez slabljenja assertions radi prolaska testova.

Proveri FR-001–FR-011 i SC-001–SC-005 prema:
- implementaciji;
- konkretnim pozitivnim, negativnim i regresionim testovima;
- stvarnim evidence rezultatima;
- preostalim ljudskim i tehničkim uslovima.

Sačuvaj preglednu matricu zahtev → kod/test → dokaz → status/ograničenje u `evidence/tasks/T024.md`, a postojeću traceability tabelu u tasks.md uskladi gde je potrebno. Broj prolaznih testova sam po sebi nije dokaz da je svaki zahtev pokriven.

Ispravi zastarele statuse u njihovim izvornim dokumentima, posebno:
- README tvrdnje o početnim fazama i 291 backend testu;
- tvrdnje da browser nije bio dostupan, uz očuvanje razlike između završene headless automatizacije i neizvršenog ljudskog pregleda;
- spec/plan tvrdnje „implementation not started” odnosno „design only”;
- runtime patch tvrdnje u frontend/README.md prema stvarno datiranim dokazima;
- quickstart status i druga potvrđena neslaganja.

Ne prepisuj istorijske evidence rezultate kao da su tada bili drugačiji. Dodaj datirane dopune ili link ka zapisu koji ih zamenjuje. Ne pretvaraj istorijske verzije u tvrdnju o današnjem okruženju. Ne menjaj zahteve, ugovore ili kriterijume prihvatanja da bi feature izgledao završen.

Ako pronađeš stvaran nedostajući produktni zahtev, dokumentuj ga za T027. Ovaj pregled nije dozvola za širok refactor ili neprimetnu implementaciju novog obima.

## 3. T025 — stvarna reprodukcija drugog člana

Tačan zahtev:
Drugi član treba da prati README.md; njegov stvarni rezultat ili pending status zabeleži u `evidence/tasks/peer-reproduction.md` i otkloni probleme reprodukcije. SC-001 nije završen dok je ta provera pending.

Najpre proveri postoji li autentičan zapis drugog učesnika. Ako postoji, evidentiraj stvarni datum, učesnika kako je naveden, checkout/commit, runtime-e, komande, ishode i probleme. Ne izmišljaj identitet ili rezultate.

Ako nema stvarnog drugog učesnika:
- napravi pošten pending zapis sa konkretnim koracima za njega i očekivanim rezultatima;
- zatraži njegov stvarni nalaz kroz ovaj razgovor, uz objašnjenje da T025/SC-001 izričito zahtevaju drugu osobu;
- nastavi T026 i T027 bez čekanja na taj odgovor;
- ostavi T025 neoznačen i SC-001 pending ako dokaz ne stigne.

Drugi agent, drugi terminal, nova virtuelna sredina ili tvoje ponavljanje instalacije nisu drugi član tima. Ne šalji poruke kolegama preko spoljnih servisa bez eksplicitnog odobrenja.

Otkloni konkretne probleme dokumentacije/setup-a unutar T025. Ako ispravka zahteva poslovno ponašanje, prvo napiši i izvrši odgovarajući RED regresioni test, zatim minimalnu ispravku i GREEN. Za mehaničku dokumentaciju ne izmišljaj RED. Šire blokirajuće preduslove dokumentuj i traži odluku o proširenju, uz završavanje nezavisnog rada.

## 4. T026 — završne provere i pregled verzionisanih fajlova

Tačan zahtev:
Pokreni backend testove/Ruff, frontend testove/typecheck/build i `git diff --check`; pregledaj tracked fajlove za tajne i velike podatke. Sve ishode i ograničenja zabeleži u:
`evidence/tasks/foundation-validation.md`

Koristi Python 3.14 i Node 24, postojeće lockfile-ove i stvarne runtime verzije. Poslednji handoff navodi Python 3.14.7, uv 0.10.9, Node 24.20.0 i npm 11.19.0; proveri, ne pretpostavljaj.

Po potrebi:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix frontend ci
```
Ako uv nije na PATH-u, proveri postojeću mogućnost `py -3.14 -m uv`. Ne menjaj globalne runtime-e ili trajne execution politike. Ne regeneriši lockfile-ove i ne nadograđuj zavisnosti rutinski; neophodne promene obrazloži i koristi stvarne alate.

Iz korena projekta izvrši:
```powershell
uv run --locked pytest backend/tests
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
git diff --check
```

Ako koristiš ekvivalentne komande preko potvrđenog projektnog `.venv` interpretera, dokumentuj tačan razlog, verziju i komandu. Pad zbog sandbox/cache/temp ograničenja razlikuj od pada aplikacije. Ne isključuj behavior testove da bi dobio prolaz.

Zabeleži stvarne brojeve testova, exit kodove, build rezultate i upozorenja. Ranije poznato Starlette/httpx upozorenje nije razlog za automatsku nadogradnju; proceni aktuelni ishod. „Nema testova” nije prolaz.

Pregledaj tracked fajlove, njihove veličine, dodate/izmenjene fajlove i relevantna ignore pravila. Proveri da tajne, `.env`, sirovi/obrađeni datasetovi, `.venv`, node_modules, build/cache i mašinski lokalno stanje nisu uključeni, uz očuvanje deljenih `.agents`/`.specify` fajlova. Ne prikazuj vrednosti potencijalnih tajni u izlazu ili evidence-u. Ne briši legitimne pregledane sintetičke fixture-e ili postojeće browser evidence slike samo zbog vrste fajla.

Pregled je ograničena provera repozitorijuma, ne sertifikacija bezbednosti niti dokaz da u celoj Git istoriji nema tajni.

Posle završnih izmena ponovi pogođene provere i završni diff pregled. Ne ponavljaj pune suite-ove nakon svake sitne tekstualne izmene. Browser proveru ponovi ako promene ili nalaz to opravdavaju; raniji T019 rezultat jasno navedi kao raniji, bez tvrdnje da je ponovo izvršen.

## 5. T027 — konvergencija bez automatske implementacije novih taskova

Tačan zahtev:
Pokreni Spec-kit convergence prema `spec.md`, `plan.md` i `tasks.md`; dopiši preostali rad u tasks.md ako postoji. Privremeni Sync Impact Report u constitution ukloni posle njegovog pregleda, pre eventualnog commit-a.

Primeni lokalni `speckit-converge` skill na eksplicitno odabrani feature. Uporedi stvarni kod, testove i dokaze sa specifikacijom i planom. Sačuvaj nalaz/izvršene komande u `evidence/tasks/T027.md` ili tačnoj putanji koju skill propisuje, uz link iz handoff-a.

Ako postoje praznine:
- dodaj konkretne, proverljive taskove sa novim jedinstvenim ID-jevima, zavisnostima i zahtevima prema konvenciji skill-a;
- ne dupliraj postojeći otvoreni T025 samo zato što čeka drugog učesnika;
- ne označavaj nove taskove završenim;
- ne implementiraj ih automatski u ovoj sesiji.

Konvergencija može biti izvršena i dati nalaz otvorenog rada; to ne znači da je feature završen.

Pri generisanju prompta Sync Impact Report već nije postojao u constitution. Proveri trenutno stanje: ako je odsutan, evidentiraj već ispunjen uslov bez izmišljanja izmene ili vraćanja komentara. Ako je prisutan, pregledaj ga i ukloni samo privremeni komentar prema T027; ne menjaj principe ili governance verziju.

Ako skill zahteva subagente, prati njegov stvarni zahtev; inače ih ne pokreći. Ne koristi dodatnog agenta kao zamenu za peer reprodukciju.

## 6. Trajan trag, granice i predaja

Pre prvih izmena sačuvaj originalni primljeni prompt u:
`prompts/development/001-foundation-phase-06.md`

Postojeći original ne prepisuj; nastavke čuvaj kao datirane dopune. Ne rekonstruiši original naknadno. Dodaj stvarni zapis u postojeći indeks `prompts/development/001-foundation.md`, bez menjanja ranijih originala ili njihove deklarisane prirode.

Održavaj:
- `evidence/tasks/T024.md`
- `evidence/tasks/peer-reproduction.md`
- `evidence/tasks/foundation-validation.md`
- T027 evidence prema prethodnom odeljku
- `evidence/tasks/phase-06-handoff.md`
- aktuelni `specs/001-project-foundation/tasks.md`
- root `next_work.md`.

Koristi `evidence/templates/task.md`: task/FR/SC, originalni prompt, početna grana/commit/diff, verzije, tačne komande, stvarni rezultati, ograničenja i review status. Handoff osvežavaj nakon taska ili koherentne celine, ne samo na kraju. `next_work.md` drži kao kratak aktuelni pregled sa evidence linkovima, blokadama/neizvršenim proverama i jednim konkretnim narednim korakom.

Checkbox označi tek kada je stvarni zahtev taska ispunjen. Delimični task ostaje neoznačen. Ne menjaj oznake prethodnih faza bez konkretnog nalaza i objašnjenja.

Sačuvaj postojeći rad, original_idea.md, ugovore, fixture-e, ignore politiku i deljeni `.agents`/`.specify` sadržaj, osim preciznih izmena odobrenih ovim opsegom. Ne regeneriši specifikacije niti slabi zahteve. Ne uvodi ML, RAG, LLM, stvarne podatke, nove produktne funkcionalnosti ili tehnike van odobrenog obima. Bez commit-a, push-a, merge-a ili deploy-a.

Ako su potrebne izmene kritičnog ponašanja unutar dozvoljenih ispravki, koristi RED → GREEN → REFACTOR. Već ispravno ponašanje proveri bez veštačkog pada. Produktne praznine pronađene konvergencijom ostaju novi taskovi za zasebnu implementaciju.

Feature 1 ne proglašavaj završenim samo zato što su automatizovane provere zelene ili je T027 izvršen. Stanje mora odgovarati svim kriterijumima, novim taskovima, stvarnoj peer reprodukciji i evidentiranom ljudskom pregledu.

Završni odgovor neka kratko navede:
- završene, delimične i blokirane T024–T027;
- šta je promenjeno i stvarne rezultate provera;
- status T025/SC-001 i ljudskog pregleda;
- rezultat konvergencije i eventualne nove taskove koji nisu implementirani;
- putanju `evidence/tasks/phase-06-handoff.md`;
- jedan konkretan sledeći korak prema stvarnom preostalom radu.

Ako peer dokaz nedostaje, predaj tačan postupak drugom članu; ako konvergencija nađe praznine, navedi prvi novi task. Ne počinji feature 002 ili bilo koji drugi budući feature.
## User clarification - 2026-11-12
Ne postoji. To mi dodatno napisi korake kako taj deo treba da se odradi.
