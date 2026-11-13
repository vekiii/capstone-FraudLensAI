# Originalni prompt — 2026-11-13

Ispravi potvrđenu T020 grešku na grani 002-data-and-risk-scoring.
Referentni objavljeni commit je 0f5ad9ac0b04cc406e3c19b0f1934da4cc29d10d.
Pročitaj AGENTS.md i next_work.md. Sačuvaj ovaj prompt u prompts/development/.

U backend/tests/integration/test_feature_store.py dodaj determinističku
RED regresiju s dvije DatasetStore konekcije prema istoj privremenoj
bazi i istom ključu (dataset version, feature version). U testu
isprepleti dva builda tako da drugi pokuša graditi dok prvi ima
staged build. U postojećem kodu drugi može završiti, a prvi zatim
na UNIQUE grešci obriše njegov kompletan rezultat. Reprodukovano
stanje: objavljeni broj 3, stvarni broj 0, retry dataset_incompatible.

Ispravi upravljanje konkurentnim buildovima tako da svaki pokušaj
može završiti ili očistiti samo svoj rad. Drugi pokušaj može dobiti
kontrolisani odgovor da je build u toku ili ponovo koristiti rezultat
nakon završetka prvog. Sačuvaj oporavak napuštenog staged builda,
upis u ograničenim batchovima i ponavljanje kompletne verzije.
Regresija treba potvrditi da objavljeni snapshotovi ostaju čitljivi
i da retry uspijeva. Zadrži provjeru oporavka nakon prekida.

U tasks.md ukloni zastarjelu rečenicu uz T017 da su T018/T019 otvoreni.
U evidence/tasks/feature-002-feature-rules.md zapiši reprodukciju,
stvarne RED/GREEN komande, rezultate i link na prompt. Ažuriraj
next_work.md i zadrži T026 kao prvi sljedeći zadatak.

Pokreni ciljane SQLite/CLI testove, puni backend suite, Ruff i
git diff --check. Koristi sintetičku bazu. Puni IBM replay ponovi samo
ako ispravka promijeni sadržaj ili format spremljenih snapshotova.
Sačuvaj obje postojeće IBM baze. Stani prije T026 i vrati izmijenjene
fajlove i rezultate provjera. Bez commita ili pusha u ovoj sesiji.
