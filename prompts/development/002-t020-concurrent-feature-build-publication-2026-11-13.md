# Original T020 publication request — 2026-11-13

Objavi završnu T020 ispravku na grani 002-data-and-risk-scoring.
Pročitaj AGENTS.md, next_work.md i zapis o ispravci u
evidence/tasks/feature-002-feature-rules.md. Provjeri lokalni diff
i trenutno stanje remote grane. Sačuvaj zatečeni rad.

Prije commita provjeri da zaključavanje radi između dva zasebna CLI
procesa nad istom privremenom SQLite bazom. Ako postojeći test to već
dokazuje, koristi njegov rezultat. Ako koristi samo dvije konekcije
unutar jednog procesa, dodaj ciljanu provjeru između procesa.
Potvrdi da preklopljeni pokušaj dobije feature_build_in_progress,
da kompletni snapshotovi ostanu čitljivi i da ponavljanje uspije.
Zabilježi stvarni rezultat u evidenciji.

Kad provjere prođu, stageuj samo T020 ispravku, regresiju i pripadajuću
dokumentaciju, prompt i evidenciju. Pokreni git diff --cached --check.
CSV, obje IBM SQLite baze i lokalni pomoćni fajlovi ostaju van commita.

Commit poruka:
fix(feature-002): protect concurrent feature snapshot builds

Pushuj na origin/002-data-and-risk-scoring i potvrdi da lokalni i
udaljeni HEAD imaju isti SHA. Ako je remote napredovao, sačuvaj rad
kolega i ponovi pogođene provjere. Bez force pusha ili mergea u main.

Vrati puni SHA, GitHub link, rezultate provjera i git status.
Stani prije T026.
