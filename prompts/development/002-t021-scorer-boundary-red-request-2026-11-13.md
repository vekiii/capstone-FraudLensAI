# Original T021 request — 2026-11-13

Nastavi fazu 4 projekta FraudLens AI na grani 002-data-and-risk-scoring.
Završi samo T021 kao RED zadatak. Pročitaj AGENTS.md, next_work.md,
T021/T022 u tasks.md, data-model.md, offline ugovor i postojeću
evidenciju faze 4. Sačuvaj lokalne T017–T020 izmjene i ovaj prompt
u prompts/development/.

U backend/tests/contracts/test_data_scoring.py napiši ugovorne testove
za ScoreRequestV2 i validaciju odgovora scorera. Koristi sintetičke
zahtjeve i kontrolisani testni scorer. Pokrij sve kriterijume T021:

- Valjan zahtjev i odgovor s usklađenim identitetom transakcije,
  dataseta, runa i feature verzije, odgovarajućim as-of vremenom,
  pokrivenošću i digestom ulaza za objašnjenje.
- Odbijanje pogrešnih identiteta, verzija i digesta, neispravne sheme
  ili pokrivenosti i nedostajućeg artefakta kad ga scorer zahtijeva.
- Razliku između vremena događaja, vremena do kojeg se računa istorija
  i stvarnog vremena bodovanja. Za ponovljeno bodovanje uporedi
  semantički rezultat uz kontrolu vremenskih i run metapodataka.
- Zaštitu originalnog zahtjeva od mutacije koju pokuša scorer,
  kao i odbijanje neočekivanih privatnih oznaka i ugniježđenih dodataka.
- Odbijanje bool, string, NaN, beskonačnih i vanopsežnih skorova,
  bez konverzije, ograničavanja na [0,1], zamjene nulom ili prelaska
  na drugi scorer.

Dodaj barem jedan valjan primjer uz negativne slučajeve kako T022
ne bi mogao proći pukim odbijanjem svih zahtjeva. Pokreni kolekciju
i izvršavanje T021 testova. Kolekcija treba da prođe. Zabilježi tačan
razlog očekivanih padova i jasno navedi koje tvrdnje još čekaju GREEN.
Pokreni Ruff i git diff --check.

U evidence/tasks/feature-002-feature-rules.md upiši vezu između
kriterijuma i testova, komande, izlazne kodove i stvarne rezultate.
Ažuriraj tasks.md i next_work.md prema dokazima.

Stani prije T022. Bez izmjena produkcijskog scorera, IBM replaya,
izmjene postojeće SQLite baze, commita ili pusha. Vrati broj
prikupljenih testova, stvarne razloge padova i status T021.
