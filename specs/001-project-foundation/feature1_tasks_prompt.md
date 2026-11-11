# Feature 1 — šablon za generisanje prompta za jednu fazu

## Namena i upotreba

Ovaj fajl je **instrukcija generatoru prompta**, a ne zahtev za implementaciju.
Generator čita repozitorijum i vraća samo prompt koji član tima prosleđuje zasebnom
Codex razgovoru za implementaciju. Oba razgovora moraju imati pristup odgovarajućem
checkout-u projekta. Kontekst prethodnih razgovora nije potreban.

Primer zahteva generatoru:

> Iskoristi specs/001-project-foundation/feature1_tasks_prompt.md i napiši mi prompt
> za poseban Codex chat za implementaciju faze 1, odnosno taskova T001–T005.

Primer nastavka nakon predaje rada:

> Iskoristi specs/001-project-foundation/feature1_tasks_prompt.md i generiši prompt
> za nastavak faze 4 iz trenutnog stanja i poslednjeg handoff zapisa.

Uvodna mapa za orijentaciju (uvek proveri aktuelni tasks.md):

| Faza | Početni taskovi | Oblast |
|---|---|---|
| 1 | T001–T005 | Setup |
| 2 | T006–T007 | Ugovori i validacija |
| 3 | T008–T011 | Pokretanje okruženja |
| 4 | T012–T019 | Lista, detalj i sintetički skor |
| 5 | T020–T023 | Zamenljivost i predaja rada |
| 6 | T024–T027 | Završne provere i konvergencija |

## Instrukcije generatoru — samo čitanje

1. **Ne implementiraj ništa.** Ne menjaj fajlove, checkbox-ove, Git stanje ili lokalni
   Spec-kit pokazivač. Ne instaliraj pakete, ne pokreći aplikaciju/testove, ne aktiviraj
   implementacione skill-ove i ne kreiraj druge agente. Dozvoljeno je čitanje fajlova,
   pretraga i read-only provera Git grane/diff-a radi tačnog konteksta.
2. Iz zahteva izdvoji broj faze i eventualni opseg taskova. Proveri da postoje i da
   odgovaraju jedno drugom u aktuelnom tasks.md. Ako je naveden samo broj faze, sam
   pronađi njen opseg. Ako je naveden samo opseg, izvedi fazu kada je jednoznačno.
   Ako izbor nedostaje ili je protivrečan, postavi jedno kratko pitanje; ne nagađaj.
3. Pročitaj važeće AGENTS.md instrukcije ako postoje, zatim
   obavezno root `next_work.md` pre generisanja prompta, pa
   `.specify/memory/constitution.md`, `specs/001-project-foundation/tasks.md`, `spec.md`
   i `plan.md` iz istog direktorijuma. Iz data-model.md, contracts/, quickstart.md i
   research.md pročitaj delove relevantne za izabranu fazu. `original_idea.md` koristi
   samo ako je potrebna šira odluka koja nije objašnjena u tim dokumentima. Ne učitavaj
   ceo PDF sa kursa, sirove datasetove ili celu istoriju razgovora.
4. Proveri postojeći kod, označene zadatke i relevantne evidence/handoff zapise samo
   koliko je potrebno za izbor. Checkbox nije dovoljan dokaz izvršavanja, a neoznačen
   task može biti delimično implementiran. Razdvoji potvrđeno stanje od pretpostavki.
   Ako evidence ili prompt direktorijumi još ne postoje, to nije prepreka za fazu 1.
   Pri generisanju ne menjaj next_work.md. Ako nedostaje ili nije čitljiv, prijavi
   to i utvrdi stanje iz taskova/evidence zapisa, bez izmišljanja prethodne predaje.
5. Utvrdi spoljne preduslove, relevantne FR/SC kriterijume, redosled testova i
   implementacije, ciljane putanje i provere koje su ostvarive u toj fazi.
   Ne dodaj kasnije funkcionalnosti da bi buduća kompletna provera već sada prošla.
6. Ne tumači čitanje implementacionog skill-a kao njegovo izvršavanje. U generisani
   prompt uključi upotrebu lokalnog `speckit-implement` skill-a ako je dostupan,
   **isključivo za traženi opseg**. Eksplicitan opseg korisnika ima prednost nad
   opštom instrukcijom skill-a da završi ceo tasks.md. Za fazu 6 uključi
   `speckit-converge` zbog T027, ali bez automatske implementacije novododatih taskova.
7. Vrati **samo jedan kopirljiv Markdown code block** sa gotovim implementacionim
   promptom na srpskom. Ne dodaj uvod, analizu, rezultat implementacije ili ponudu za
   nastavak. Ako unutra trebaju code block-ovi, koristi spolja četiri backtick znaka.
   Izuzetak je neophodno pitanje iz tačke 2 ili obaveštenje da ključni izvorni fajl
   nije dostupan; ne izmišljaj nedostajuće zadatke.

## Obavezni sadržaj generisanog implementacionog prompta

Popuni sledeće celine konkretnim vrednostima iz repozitorijuma. Ne ostavljaj slotove
poput `<FAZA>` ili `<TASKOVI>`. Ne prepisuj ceo ovaj fajl ni ceo tasks.md. Prenesi
tačne zahteve izabranih taskova, uključujući njihove ID-jeve, ograničenja i putanje;
okolne dokumente referenciraj putanjama. Dužinu prilagodi složenosti faze.

### 1. Zadatak i dovoljan kontekst

- Napiši: **„Implementiraj, nemoj samo predložiti plan ili generisati novi prompt.”**
- Navedi feature `specs/001-project-foundation`, broj/naziv faze i tačne taskove.
- Ukratko: FraudLens AI je Bootcamp AML prototip. Foundation je lokalna demonstracija
  sa fixture podacima; ne zahteva ML trening, RAG korpus ili LLM ključ.
- Oslanjaj se na fajlove u checkout-u, ne na prethodne chatove. Putanje su relativne
  u odnosu na koren projekta; ne hardkoduj Windows putanju ili korisničko ime.
- Navedi da se čuva postojeća radna grana; originalno je initialization, ali izvršilac
  mora proveriti stvarnu granu i ne sme je sam menjati.

### 2. Pročitaj pre izmena

- Prompt mora zahtevati da izvršilac, odmah nakon važećih AGENTS.md instrukcija,
  pročita root `next_work.md` pre planiranja i implementacije, uključujući nastavak
  prekinutog rada. Aktuelni zahtev određuje opseg; next_work.md ga ne proširuje.
- Konkretne relevantne putanje iz prethodnog postupka, uključujući postojeća pravila,
  constitution, tasks/spec/plan i samo potrebne ugovore i evidence zapise.
- Za Spec-kit odaberi `specs/001-project-foundation` eksplicitno za ovu sesiju umesto
  oslanjanja na tuđi lokalni feature.json. Na PowerShell-u koristi sesijsku promenljivu
  `SPECIFY_FEATURE_DIRECTORY`; time ne menjaš Git granu.
- Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md`
  samo za navedene taskove. Poštuj stvarne checklist/hook zahteve; ne menjaj njihove
  oznake radi prolaska. Ako traže odluku koja već nije odobrena, objasni tačan izvor
  i razlog potrebne odluke. Ne uvodi dodatne potvrde za već odobrene rutinske korake.

### 3. Opseg i preduslovi

- Navedi taskove za implementaciju i spoljne preduslove. Proveri preduslove pre koda;
  ne popravljaj druge faze neprimetno. Ako nedostaje stvaran blokirajući preduslov,
  sačuvaj nalaz i traži odluku o proširenju opsega, uz završavanje nezavisnog rada.
- Navedi očekivane putanje iz taskova i usko povezane config/evidence/prompt fajlove.
  To nije dozvola za preuređenje repozitorijuma ili regenerisanje specifikacija.
- Ako je task već završen, proveri relevantan dokaz i dopuni samo ono što nedostaje.
  Sačuvaj tuđe postojeće izmene; ne radi reset/clean/stash ili automatsko prebacivanje
  grane da bi dobio čist početak. Prljavo radno stablo samo po sebi nije blokada.
- Sačuvaj postojeće original_idea.md, constitution, ugovore, pravila ignorisanja i
  deljeni `.agents`/`.specify` sadržaj. Suštinske kontradikcije prijavi, ne menjaj
  zahtev ili test samo da dobiješ prolaz.
- Ne uvodi out-of-course tehnike/funkcionalnosti bez eksplicitnog odobrenja tima.
  Ne pokreći subagente osim ako ih korisnik ili primenljive instrukcije zahtevaju.
- Bez commit-a, push-a, merge-a ili deploy-a, osim kada ih korisnik eksplicitno zatraži.

### 4. Izvršavanje i TDD

- Izvrši celu izabranu fazu po zavisnostima i stani na njenoj granici. `[P]` označava
  mogućnost paralelnog rada, ne obavezu; za ovaj način predaje radi sekvencijalno.
- Za poslovno ponašanje prvo napiši i pokreni smislen RED test, zabeleži razlog,
  implementiraj najmanju promenu, pokreni GREEN i relevantnu regresiju. Za mehanički
  setup ne izmišljaj RED. Već ispravno ponašanje proveri bez namernog kvarenja.
- Generiši lockfile-ove stvarnim alatom; ne izmišljaj verzije ili hash-eve. Posle
  prvog razrešavanja koristi zaključane zavisnosti i stvarne runtime verzije.
- Izaberi provere za trenutni obim. U fazi 1 nema modela, fixture case UI-ja ni
  kasnijih behavior testova. Razdvoji odsustvo još neimplementirane provere od pada
  onoga što ova faza mora da isporuči; ne predstavljaj „nema testova” kao test uspeh.
- Popravljaj greške svog opsega do dovršetka; stvarne spoljne blokere zabeleži.
  Ne radi beskonačne retry petlje i ne dodaj novu infrastrukturu zbog instalacionog kvara.

### 5. Trajan trag i predaja sledećem članu

- Pre implementacionih izmena sačuvaj originalni primljeni prompt u
  `prompts/development/001-foundation-phase-NN.md` (NN je dvocifren broj faze).
  Ako direktorijum još ne postoji, napravi ga. Postojeći original ne prepisuj;
  nastavke dodaj kao datirane dopune i označi ih kao takve. Bez tajni.
- Ovo čuvanje važi već za fazu 1, iako T023 kasnije objedinjuje evidenciju. Ne označavaj
  T023 završenim unapred. Kada T023 dođe na red, `001-foundation.md` može biti indeks
  originalnih zapisa po fazama, bez njihovog naknadnog rekonstruisanja.
- Koristi evidence/README.md i evidence/templates/task.md kada postoje. Zadrži tačne
  task evidence putanje iz tasks.md. Dodatno održavaj kratak zapis
  `evidence/tasks/phase-NN-handoff.md`: grana/početni commit, završeni i delimični
  taskovi, menjani fajlovi, komande/ishodi, blokere i sledeći konkretan korak.
- Ažuriraj task checkbox tek posle implementacije i propisane provere. Delimičan ili
  blokiran task ostaje neoznačen, uz opis napretka. Ne menjaj stanje drugih faza.
- Handoff osveži posle završenog taska ili koherentne celine, ne samo na kraju:
  sesija može biti prekinuta bez prilike za završni odgovor. Prekid zbog kvote ne
  garantuje automatsko čuvanje dodatnog zapisa; već sačuvani fajlovi su osnova nastavka.
- Posle implementacione celine ažuriraj i root `next_work.md`: trenutno stanje,
  evidence linkovi, blokade/neizvršene provere i jedan konkretan sledeći korak.
  Ovaj fajl je kratka predaja, dok tasks.md i evidence/ čuvaju detaljan status i dokaz.
- Ne tvrdi da postoji ljudski review ili da je drugi član reprodukovao setup ako se
  to nije dogodilo. Posebno T025/SC-001 ostaju pending do stvarnog drugog učesnika.

### 6. Provere i završni izveštaj

- Navedi konkretne ciljane provere izabrane faze, očekivano ponašanje i uslove završetka.
  Posle završnog editovanja ponovi pogođene provere; ne pokreći nepotrebne pune suite-ove
  posle svake male izmene. Pregledaj diff i `git diff --check`.
- Kratak završni izveštaj: završeni/delimični/nepočeti taskovi, šta je promenjeno,
  izvršene provere sa stvarnim ishodom, šta nije provereno i zašto, putanja handoff-a
  i prvi sledeći dozvoljeni korak. Ne prelazi u sledeću fazu.

## Provera generatora pre vraćanja odgovora

- Izabrana faza/opseg odgovara aktuelnom tasks.md; svi njeni taskovi su obuhvaćeni.
- Prompt eksplicitno traži implementaciju u drugom razgovoru, a generator ništa nije izmenio.
- Drugi razgovor može postupiti bez istorije ovog razgovora, uz isti ažurirani checkout.
- Navedeni su preduslovi, putanje, TDD/provere, ograničenje faze i predaja rada.
- Nema izmišljenog stanja, nedostupnih prethodnih odgovora ili nerešenih slotova.
- Konačan izlaz je samo jedan prompt u code block-u.

## Napomena timu

Faza po razgovoru je organizacioni izbor, a ne garancija manje potrošnje tokena.
Ako je faza prevelika, sledeći član nastavlja istu fazu iz handoff-a; ne započinje sledeću.
Pri promeni računara/checkout-a prenesite aktuelni kod, task status, prompt i evidence zapise
kroz svoj dogovoreni Git postupak. Sam kopirani prompt ne prenosi nezabeležene izmene.
Za ovu funkcionalnost običan verzionisan fajl je dovoljan. Ako isti workflow postane zajednički
za više feature-a, može se pretvoriti u projektni skill koji referencira ovaj postupak.

Pristup sa ciljanim repo kontekstom usklađen je sa
[OpenAI primerom razvoja workflow-a](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex).
