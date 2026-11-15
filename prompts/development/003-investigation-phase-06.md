# Original development request — 2026-11-15

Nastavi implementaciju Feature 003 na aktuelnoj grani: faza 6, T045–T051, prema specs/003-ai-investigation/tasks.md. Implementiraj taskove, ne samo plan.

Prvo pročitaj AGENTS.md, aktuelni next_work.md i relevantne specifikacije, plan, ugovore i evidence. Proveri kod i preduslove; sačuvaj postojeće izmene.

Obuhvati eksplicitne analyst odluke i obrazloženja, nepromenljiv AI nacrt, povezane korekcije, idempotentnost, revizije i odgovarajuće API/UI ponašanje. Koristi fixture/test provider. Ne čitaj stvarni .env, ne pozivaj OpenAI i ne pokreći T033; capability gate ostaje otvoren.

Primeni RED → GREEN → REFACTOR i izvrši relevantne testove i stvarne lokalne API/browser provere, uključujući sukob dve browser sesije. Ne izmišljaj ljudske potvrde i ne predstavljaj fixture rezultate kao LLM evaluaciju.

Sačuvaj prompt, zabeleži stvarne rezultate i ograničenja, ažuriraj task statuse i next_work.md. Stani posle T051, uz eksplicitno otvorene zahteve za stvarnu ljudsku potvrdu ako nedostaju. Bez sledeće faze, commit-a ili push-a.
