# Sledeći korak — FraudLens AI

Poslednje ažuriranje: 2026-11-11.
Ovaj fajl je kratka predaja rada između članova i Codex razgovora.
Detaljan status taskova ostaje u odgovarajućem tasks.md, a rezultati u evidence/.
Ne zahteva čitanje istorije razgovora.

## Trenutno stanje

- Radna grana pri poslednjoj proveri: `initialization`; proveriti aktuelnu nakon pull-a.
- Aktivni feature: [001-project-foundation](specs/001-project-foundation/spec.md).
- **Završena je samo faza 1, T001–T005**, prema task statusu i postojećem evidence zapisu.
- **Sledeća je faza 2, T006–T007.** Ceo feature 1 još nije završen.
- Usvojeni runtime-i: Python 3.14 i Node 24; koristiti projektne konfiguracije i lockfile-ove.
- Setup i runtime provere su opisani u
  [phase-01-handoff.md](evidence/tasks/phase-01-handoff.md), naročito završni runtime amendment.
  Raniji Python 3.12 / Node 22 unosi su istorijski.
- Behavior testovi još nisu napisani. „No tests collected” nije prolaz test suite-a.
- Ljudski pregled setup-a i kasnija reprodukcija drugog člana ostaju pending.
- Pri ovom ažuriranju pročitani su postojeći dokumenti i stanje fajlova;
  prethodne instalacione/build provere nisu ponovo izvršavane.

## Šta naredni član radi sada

1. Povuci poslednje dogovorene izmene iz Git repozitorijuma i proveri granu/status.
   Ne menjaj granu ili briši lokalne izmene automatski.
2. Pročitaj [AGENTS.md](AGENTS.md), ovaj fajl,
   [tasks.md](specs/001-project-foundation/tasks.md) i poslednji phase handoff.
   Pregledaj postojeći setup/lockfile-ove; ne prijavljuj pregled kao završen dok ga ne uradiš.
3. U razgovoru za generisanje prompta zatraži:

   ```text
   Iskoristi specs/001-project-foundation/feature1_tasks_prompt.md
   i generiši prompt za poseban Codex chat za implementaciju
   faze 2, taskova T006–T007. Samo generiši prompt, bez implementacije.
   ```

4. Generisani prompt pošalji u novi implementacioni razgovor sa pristupom checkout-u.
   Cilj faze 2: RED testovi ugovora, zatim implementacija validacije i GREEN;
   detalji su u taskovima i contracts/.
5. Po završetku ili predaji delimičnog rada ažuriraj task status, stvarni evidence,
   phase handoff i ovaj fajl. Zatim pregledaj, commituj i pushuj kroz dogovoreni timski
   Git postupak. Codex to ne izvršava automatski bez posebnog zahteva.

Ako u toku rada nestane raspoložive kvote, naredni član nastavlja nezavršenu fazu,
ne prelazi automatski na sledeću. Redovno čuvanje stanja smanjuje zavisnost od
završne poruke razgovora.

## Preostali redosled unutar feature-a 1

| Faza | Taskovi | Rezultat |
|---|---|---|
| 2 | T006–T007 | Validirani zajednički ugovori |
| 3 | T008–T011 | Pokretanje lokalnog okruženja i health |
| 4 | T012–T019 | Lista → detalj → sintetički skor |
| 5 | T020–T023 | Dokaz zamenljivosti scorer-a i predaja rada |
| 6 | T024–T027 | Završne provere, stvarna peer reprodukcija i konvergencija |

Ako konvergencija pronađe nedovršen posao, prvo rešiti dopisane taskove.
Feature 1 nije završen samo zato što su početni T001–T027 označeni: dokazi,
prihvatni kriterijumi i stvarni rezultat moraju da se slažu. Posebno ne označavati
T025/SC-001 dok drugi član zaista ne ponovi pokretanje.

## Šta dolazi nakon proverenog feature-a 1

Sledeća funkcionalnost za detaljnu specifikaciju je **002-data-and-risk-scoring**:
uvoz IBM AML podataka, mapiranje, vremenska obeležja, baseline/model, objašnjenja
i uključivanje kroz postojeći scoring ugovor. Ovaj feature još nije kreiran.

Tok je: specifikacija → razjašnjenja po potrebi → plan i ugovori → taskovi →
provera usklađenosti → implementacija po fazama → evaluacija i konvergencija.
Ne generisati kod narednog feature-a pre njegovog definisanja.

Naredne planirane oblasti su:

- 003-knowledge-and-retrieval — korpus, pretraga, citati i retrieval evaluacija.
- 004-case-investigation — alati, AI workflow, izveštaj i pregled analitičara.
- 005-priority-and-simulation — prioriteti, kapacitet i ponovljivi eksperimenti.

Brojevi označavaju organizaciju specifikacija, ne obavezan potpuno serijski razvoj.
Posle stabilnog foundation-a i dogovorenih ugovora više članova može razrađivati i
implementirati nezavisne oblasti paralelno. RAG i AI workflow ne čekaju završetak
ML treninga: koriste dogovorene fixture/adapterske granice.

## Pravilo održavanja ovog fajla

Posle svake implementacione celine i pre predaje drugom članu ažurirati:

- datum i trenutno provereni feature/fazu;
- završene i delimične taskove, uz linkove ka stvarnom evidence/handoff-u;
- blokere i provere koje nisu izvršene;
- jedan konkretan naredni korak i uslov za nastavak.

Održavati kratak aktuelni pregled, bez kopiranja cele istorije logova ili tajni.
Detaljne stare rezultate ostaviti u evidence/. Ako pregled nije ponovo izvršen,
navesti da se status oslanja na postojeći zapis. Ne označavati unapred buduće uspehe.
