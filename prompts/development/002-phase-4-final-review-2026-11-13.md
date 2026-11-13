# Originalni prompt — 2026-11-13

Uradi završni pregled faze 4 (T017–T025 / Prompt 3) za FraudLens AI na
grani 002-data-and-risk-scoring. Pregledaj stvarni lokalni diff, uključujući
nove fajlove koji još nisu praćeni. Pročitaj AGENTS.md, next_work.md,
tasks.md, Feature 002 spec i data-model, zamrznuti offline ugovor i
evidence/tasks/feature-002-feature-rules.md. Sačuvaj zatečeni rad i
originalni prompt u prompts/development/.

1. Uporedi svaki T017–T025 s kodom, testovima i evidencijom.
   Provjeri katalog, vremenski replay i zaštitu od curenja oznaka,
   kompatibilnost i potpunost SQLite builda, v2 scorer granicu,
   R1–R3 i dokaze za T025. Potvrdi ručno izračunate primjere,
   semantičko ponavljanje skora i rules-only rad bez modela/providera.
   Provjeri da Foundation v1 scorer nije promijenjen.
   Ispravi konkretne nedostatke unutar faze 4 i dodaj regresiju tamo
   gdje postojeći testovi ne pokrivaju potvrđenu grešku.

2. Na postojećoj radnoj SQLite kopiji izvrši read-only provjeru.
   Uskladi broj event-valid zapisa sa snapshotovima i razdvoji
   full, incomplete i unavailable, uključujući nulu ako je nema.
   Objasni 1.114.921 incomplete snapshotova prema stvarnom vremenu
   početka izvora, prvih 24 sata i svim drugim razlozima koje kod
   primjenjuje. Provjeri tačnu granicu warm-upa i ponašanje scorera
   za nescoreabilnu pokrivenost. Ako brojevi ne slijede ugovor,
   dijagnostikuj problem i ispravi ga. Puni replay ponovi samo ako
   ispravka utiče na spremljene snapshotove ili su dokazi nevažeći.
   Originalnu IBM bazu i CSV sačuvaj.

3. Uskladi dokumentaciju.
   - U feature-002-feature-rules.md odvoji puni replay karakteristika,
     ponovno korištenje builda (`repeated: true`) i semantičko ponavljanje
     bodovanja tri stvarne transakcije. Zapiši stvarne komande, izlazne
     kodove, DatasetVersion, verziju kataloga/pravila i nalaz o pokrivenosti.
   - U Feature 002 quickstartu označi build-features kao implementiran.
     Dodaj provjerenu komandu, potrebne ulaze i očekivani rezultat.
     Kasnije komande ostavi prema stvarnom statusu.
   - Uskladi tasks.md, next_work.md i relevantne dijelove ugovora.
     Sačuvaj istorijske hashove i odluke. Razlikuj završenu fazu 4 od
     kasnijeg modelskog dijela SC-003, evaluacije i v2 integracije.
     Provjeri linkove i da je T026 prvi sljedeći zadatak.

4. Pokreni ciljane testove, puni backend suite, Ruff i git diff --check.
   Provjeri i da se u planirani commit ne bi uključili CSV, SQLite baze,
   logovi ili drugi generisani fajlovi. Vrati kratku tabelu T017–T025 s
   dokazom, spisak ispravki i jasan zaključak da li je faza 4 spremna za
   push. Ako nešto ostane otvoreno, navedi tačan kriterijum i dokaz koji fali.

Stani prije T026, commita i pusha.
