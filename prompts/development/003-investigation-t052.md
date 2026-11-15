# Original development request — 2026-11-15

Nastavi Feature 003 na aktuelnoj grani: T052 prema specs/003-ai-investigation/tasks.md. Napravi konkretne artefakte, ne samo plan.

Prvo pročitaj AGENTS.md, aktuelni next_work.md i relevantne specifikacije, evaluation.md, plan, ugovore i evidence. Proveri preduslove i sačuvaj postojeće izmene.

Pripremi evaluacioni paket: 30 retrieval pitanja (10 development, 20 held-out), 12 investigation scenarija (4 development, 8 held-out), reference, split-ove, rubriku, safety scenarije i protocol prema T052. Reference izvedi iz izvora i konteksta, ne iz generisanih izveštaja. Odvoji privatne odgovore od runtime ulaza i proveri strukturu, brojeve, identitete i hash veze.

Ne izmišljaj autorstvo, nezavisni ljudski pregled ili odobrenje. Ako pregled nedostaje, ostavi paket kao predložen i T052 nezavršen, uz jasan checklist za stvarnog recenzenta.

Ne čitaj stvarni .env, ne pozivaj OpenAI i ne pokreći T033. Ne menjaj retrieval niti pokreći tuning/held-out evaluaciju. T051 ostaje otvoren bez stvarne potvrde.

Sačuvaj prompt, stvarne provere i ograničenja; ažuriraj tasks.md i next_work.md. Stani posle pripreme T052, bez T053+, commit-a ili push-a.

Transport-only backslash line separators were rendered as paragraph breaks.
