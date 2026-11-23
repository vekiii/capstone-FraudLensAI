# Feature 3 — šablon za generisanje implementacionog prompta

## Namena i upotreba

Ovaj fajl je **instrukcija generatoru prompta**, ne zahtev da generator implementira
aplikaciju. Generator čita aktuelni checkout i vraća gotov prompt koji član tima
šalje zasebnom razgovoru za implementaciju. Nije potreban kontekst prethodnih
razgovora. Direktni implementacioni prompt iz ranijeg razgovora nije preduslov.

Primer zahteva generatoru:

> Iskoristi specs/003-ai-investigation/feature3_tasks_prompt.md i generiši mi prompt
> za poseban Codex chat za implementaciju faze 1, taskova T001–T004.
> Samo generiši prompt, bez implementacije.

Primer nastavka:

> Iskoristi specs/003-ai-investigation/feature3_tasks_prompt.md i generiši prompt
> za nastavak faze 4 iz aktuelnog stanja i poslednjeg handoff zapisa.

Orijentaciona mapa; **aktuelni [tasks.md](tasks.md) je izvor tačnog opsega**:

| Faza | Taskovi | Oblast |
|---|---|---|
| 1 | T001–T004 | Setup i konfiguracija |
| 2 | T005–T012 | Ugovori, fixture kontekst i osnovno čuvanje stanja |
| 3 | T013–T022 | US1: korpus, retrieval i izvori znanja |
| 4 | T023–T038 | US2: alati, provider i AI izveštaj |
| 5 | T039–T044 | US3: oporavak, retry i trajno stanje |
| 6 | T045–T051 | US4: ljudski pregled i odluka |
| 7 | T052–T061 | US5: evaluacija |
| 8 | T062–T067 | Dataset integracija, regresija i konvergencija |

Velika faza može se tražiti i kao uži koherentan opseg. Ne prelazi automatski u
sledeću fazu ako je prethodna delimična. Broj razgovora nije garancija uštede tokena.

## Instrukcije generatoru — samo čitanje

1. Ne menjaj fajlove, task checkbox-ove, `next_work.md`, Git granu/stanje ili lokalni
   Spec-kit pokazivač. Ne instaliraj pakete, ne pokreći testove/aplikaciju/provider
   probe, ne koristi ključeve i ne pokreći implementacione skill-ove ili subagente.
   Dozvoljeni su čitanje/pretraga i read-only Git status/log/diff radi konteksta.
2. Pročitaj važeće AGENTS.md instrukcije, **zatim root `next_work.md`**, pa
   `.specify/memory/constitution.md`, `spec.md`, `plan.md` i `tasks.md` ovog feature-a.
   Iz `data-model.md`, `research.md`, `evaluation.md`, `contracts/` i `quickstart.md`
   čitaj delove relevantne za izbor. Ne učitavaj sirove datasetove, ceo PDF, tajne,
   held-out odgovore ili kompletnu istoriju projekta radi generisanja prompta.
3. Proveri broj faze/opseg prema aktuelnom tasks.md. Ako je naveden samo broj faze,
   izvedi taskove; ako je naveden samo opseg, izvedi fazu kada je jednoznačno.
   Za nedostajući/protivrečan izbor postavi jedno kratko pitanje umesto nagađanja.
4. Proveri postojeći kod i relevantne evidence/handoff zapise. Checkbox nije dovoljan
   dokaz završetka, a neoznačen task može biti delimično urađen. Razdvoji potvrđeno,
   delimično i neprovereno stanje. Ako next_work.md nedostaje/ne može da se pročita,
   prijavi to i koristi tasks/evidence bez izmišljanja predaje. Ne menjaj status.
5. Izvuci tačne zadatke, njihove preduslove, FR/SC, putanje, ograničenja i uslove
   završetka. Navedi spoljne blokere i nezavisan rad koji ipak može da se uradi.
   Ne proširuj izbor da bi popravio prethodnu fazu ili tuđu ML granu.
6. Vrati **samo jedan kopirljiv Markdown code block** sa gotovim promptom na srpskom,
   bez uvoda, analize, implementacije ili ponude. Za unutrašnje code block-ove koristi
   spolja četiri backtick znaka. Izuzetak su neophodno pitanje ili obaveštenje da
   ključni izvorni dokument nedostaje; ne izmišljaj taskove.

## Obavezni sadržaj generisanog prompta

Popuni konkretne vrednosti, bez nerešenih slotova. Ne kopiraj ceo šablon/tasks.md.
Prenesi izabrane taskove sa ID-jevima, ograničenjima, preduslovima i putanjama;
ostatak konteksta referenciraj repo putanjama. Dužinu prilagodi obimu.

### Zadatak i početno čitanje

- Počni sa: **„Implementiraj navedene taskove, nemoj samo napisati plan ili novi prompt.”**
- Navedi feature `specs/003-ai-investigation`, broj/naziv faze i tačan opseg.
  Ukratko: FraudLens AI je obrazovni AML prototip; ovaj feature obrađuje kurirani
  RAG, kontrolisanu AI istragu, izveštaj sa dokazima i ljudski pregled, nezavisno od ML-a.
- Zahtevaj čitanje važećeg AGENTS.md pa aktuelnog root next_work.md pre planiranja,
  uključujući nastavak sesije. Aktuelni zahtev određuje opseg, ne handoff sam po sebi.
- Navedi konkretne relevantne projektne/ugovorne/evidence putanje. Izvršilac mora
  proveriti Git status i sačuvati trenutnu granu i tuđe izmene; grana je prvobitno
  `feature03`, ali ne pretpostavljaj da je to i dalje stvarno stanje.
- Eksplicitno odaberi feature u svakoj PowerShell Spec-kit sesiji:
  `$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'`.
  To ne menja Git granu; ne oslanjaj se na tuđi lokalni feature.json.
- Ako je dostupan, pročitaj/primeni `.agents/skills/speckit-implement/SKILL.md`
  **samo za izabrani opseg**; eksplicitan zahtev ima prednost nad opštom instrukcijom
  da se izvrši ceo tasks.md. Za T067 uključi `speckit-converge` bez automatskog
  izvršavanja novododatih taskova. Poštuj stvarne checklist/hook zahteve; ne menjaj
  njihove oznake radi prolaska. Ne traži ponovno odobrenje već autorizovanih koraka.

### Opseg i granice

- Proveri preduslove prema taskovima i dokazima pre koda. Ako su nedostupni,
  završi nezavisan rad, zabeleži blokadu i ne označavaj blokirani task završenim.
  Ne implementiraj neizabrane preduslove/naredne faze neprimetno. Za nužno proširenje
  objasni konkretan razlog i zatraži odluku, bez izmišljanja novih approval gate-ova.
- Čuvaj originalne feature 001 odgovore i feature 002/ML ugovore/scorere/bazu.
  Izoluj investigation module/store; koordiniraj zajedničke main.py, frontend
  main.ts/views.ts i lockfile izmene. Ne importuj nezavršen ML radi fixture testa.
- Fixture/test-provider/rules/model rezultati moraju ostati jasno razlikovani.
  Nema tihog fallback-a, izmišljenih podataka ili automatske odluke analitičara.
- Ne čitaj/ispisuj tajne; ne šalji reference/privatne oznake provideru ili retrieval-u.
  Model ID se ne izvodi iz naziva OpenAI projekta ili neformalnog Luna naziva.
- Bez reset/clean/stash, automatske promene grane, merge-a, commit-a, push-a ili
  deploy-a bez posebnog zahteva. Prljavo stablo samo po sebi nije blokada.
  `[P]` znači mogućnost rada na nezavisnim fajlovima, ne obavezu pokretanja agenata.

### TDD i provere za konkretan obim

- Izvrši zavisnosti unutar izbora redom, RED -> GREEN -> REFACTOR za kritično
  ponašanje, bez veštačkog RED-a za setup ili namernog kvarenja već ispravnog koda.
  Proveri da RED pada zbog očekivano nedostajućeg ponašanja, ne environment greške.
- Koristi stvarne alate za lockfile-ove; posle prvog razrešavanja locked instalacije.
  Ne izmišljaj verzije, hash-eve, rezultate, ljudski review ili API pristup.
- Navedi konkretne ciljane testove/komande za izabranu fazu i relevantnu regresiju.
  Komande iz quickstart-a su planirani cilj dok nisu implementirane. Odsustvo
  budućeg testa nije prolaz testa; neuspešna kolekcija nije poslovni RED.
- Uključi `git diff --check` i pregled diff-a. Ponovi pogođene provere nakon izmena,
  bez nepotrebnog ponavljanja celog suite-a. Ne slabi ugovore/testove radi prolaza.
- Poštuj tačne task limite, cutoff/time/currency/score semantiku i granice alata.
  Validan citation ID ne dokazuje semantičku vernost; schema test nije LLM evaluacija.

### Posebne zavisnosti faza

- Faza 2: T012 je namerni RED za kasnije routes. Ne implementiraj T019/T035 unapred
  i ne proglašavaj ceo suite GREEN dok ti budući behavior testovi opravdano padaju.
- Faza 3: stvarna selekcija izvora, uslovi korišćenja i ljudski pregled nisu već
  završeni samim postojanjem plana. Ne izmišljaj dokumente, dozvole ili potpise.
- Faza 4: T033 je stvaran synthetic-only provider probe kada je taj task u izboru
  i pristup dostupan; ne pokreći ga za offline taskove ili ponovo bez potrebe.
  Proveri aktuelno ovlašćenje za mrežni poziv i koristi privatno konfigurisan ključ.
  Nedostupan model/pristup ne blokira T034–T038 offline, ali ostavlja T033 pending.
- Faza 7: pre tuninga zamrzni pakove/podele; ne otvaraj held-out odgovore radi
  popravke modela/prompta. T058 traži provereni stvarni provider, T059 stvarne ljude.
  Test-provider uspeh nije zamena za live izveštaje ili nezavisne ocene.
- Faza 8: T062–T064 zahtevaju aktuelan producer ugovor/pregled i stvaran adapter.
  Pinned snapshot je referenca, ne već odobrena integracija. Nedostupan producer
  ostaje eksplicitna blokada; nema preuzimanja koleginicine ML odgovornosti.

### Prompt, evidence i predaja

- Pre implementacionih izmena sačuvaj tačan primljeni prompt u
  `prompts/development/003-investigation-phase-NN.md` (NN = konkretna dvocifrena faza).
  Ne prepisuj postojeći original; nastavak sačuvaj kao datiranu dopunu sa opsegom.
- Prati evidence/README.md i evidence/templates/task.md gde postoje. Koristi
  tačne evidence putanje iz taskova, a za predaju kratak
  `evidence/tasks/feature-003-phase-NN-handoff.md`. Zabeleži početnu granu/commit,
  postojeće izmene, task status, komande/ishode, verzije, blokere i neizvršene provere.
- Checkbox označi tek kada je stvarno ispunjen njegov tip: namerni RED, GREEN,
  evidence ili ljudski pregled. RED task završen ne znači da je ponašanje GREEN.
  Delimične/blokirane taskove ostavi neoznačene. Ne menjaj stanje drugih faza.
- Posle koherentne implementacione celine ažuriraj kratko root next_work.md:
  stvarni napredak, evidence linkovi, blokade/neprovereno i jedan konkretan sledeći
  korak. Detalji ostaju u evidence; ne čekaj završni odgovor za jedinu predaju.
- Stani na granici izbora. Završni izveštaj: završeni/delimični/nepočeti taskovi,
  promene, stvarni rezultati provera, ograničenja, handoff putanja i sledeći korak.
  Ne garantuj automatsko čuvanje nakon isteka kvote; osnova nastavka su sačuvani fajlovi.

## Završna provera generatora

- Faza/opseg i preduslovi provereni prema trenutnom tasks.md i evidence.
- Generator nije implementirao, pokretao provere/provider ili menjao fajlove/status.
- Prompt je samostalan uz pristup aktuelnom checkout-u, bez istorije razgovora.
- Nema praznih slotova, hardkodovanih korisničkih putanja, tajni ili izmišljenog stanja.
- Izvršilac dobija tačne taskove, potrebne granice, TDD/provere i predaju.
- Izlaz je samo jedan gotov prompt u code block-u.

Oba razgovora koriste ažurirani checkout. Uobičajeni Git push/pull prenosi sačuvane
i commitovane projektne fajlove; kopirani prompt sam ne prenosi necommitovan rad.
Ovaj verzionisani fajl je dovoljan za dogovoreni workflow; poseban skill nije potreban.

Zabeleženi zahtev za ovaj šablon, 2026-11-13: „Hajde napravi mi taj fajl”.
Kreiranje šablona ne izvršava nijedan implementacioni task niti menja napredak feature-a.
