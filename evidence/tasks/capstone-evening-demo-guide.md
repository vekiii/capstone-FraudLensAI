# Večernja proba i paket za predaju

Datum pripreme: 23. novembar 2026. Ovo je uputstvo za narednu probu. Rezultate drugih članova možete povezati sa predajom ako zapis sadrži izvršeni SHA, scenario i stvarni ishod.

## Windows pokretanje

1. Dogovorite konačni SHA ili tag predaje koji obuhvata CAP-06 popravku. U novom checkout-u zabeležite `git rev-parse HEAD` i `git status --short`. Ranije merenje od 15/16 vezano je za `d8acc2a`, a verifikacija iz PR-a #8 za `55444ce`.
2. Preuzmite od kolege postojeći verifikovani Windows demo paket preko timskog transfera. Raspakujte ga izvan repozitorijuma. Pratite `README-WINDOWS.md` i `INVENTORY.tsv`. Za svaki raspakovani fajl iz manifesta uporedite `Get-FileHash -Algorithm SHA256 -LiteralPath <fajl>` sa `SHA256SUMS.txt`. Rasporedite `data/` fajlove u putanje iz inventara i ponovo proverite digest kopija. Lokalni paket i ključ ostaju van Git-a. [Timski handoff](model-rag-handoff-2026-11-22.md#commit-and-transfer-review--2026-11-22).
3. Koristite Python 3.14.10 i Node 24. Iz korena checkout-a pokrenite `uv sync --locked --python 3.14.10 --group dev --group ml --group investigation` i `npm.cmd --prefix web ci`. U privatnom `.env` podesite model i ključ. U zajedničkom PowerShell bloku iz quickstart-a usmerite `$demoPython` na `.venv/Scripts/python.exe` iz ovog checkout-a. Dodelite nov lokalni SQLite fajl pod `data/processed/` i koristite isti put i podešavanja u API i worker terminalu. [Komande, pinovi i portovi](../../specs/003-ai-investigation/quickstart.md#pr-3-demo-with-the-real-openai-provider-on-windows).
4. Pripremite korpus i pokrenite API i Vite na loopback adresama iz quickstart-a. U Chrome-u otvorite `http://127.0.0.1:5173/cases`. U risk lookup-u koristite puni ID iz quickstart-a sa završetkom `row:2959955`. Otvorite povezani slučaj, pokrenite istragu jednom, pa izvršite `worker --once`. Otvorite proceduralni citat i proverite da podržava konkretnu preporuku. Sačuvajte demonstracionu odluku, ponovo učitajte slučaj i potvrdite isti pokušaj i odluku bez novog slanja.
5. Kontrolisani prekid proverite offline prema CAP-06 dokazu. Ako je tim dogovorio i živo ponavljanje dužeg slučaja, koristite `row:1500153` iz prethodnog živog zapisa i zabeležite stvarni ishod. Prethodni pokušaj dostigao je `budget_exhausted`. Ako se ishod razlikuje, zapišite ga. [Prethodni živi trag](pr3-live-demo-2026-11-23.md) · [CAP-06 provere](../security/cap06-submission-verification-2026-11-23.md).

**Zapis za popunjavanje posle probe**

- Konačni SHA/tag ______ · Izvršilac/datum ______ · Model i režim ______ · Paket i hash provera ______
- Kompaktan slučaj, stanje i potvrđeni pozivi ______ · Otvoren citat i tvrdnja ______ · Sačuvana i ponovo otvorena odluka ______
- Budžetski prekid, režim i ishod ______ · CAP-06 testovi ______ · Ograničenja ili preskočeni koraci ______

## Izvršena Vedranova proba

- SHA `77ed64c16f30ebaf7b7a2212c58b3b0b08c92709`, slučaj `row:2959955`, pokušaj `att_8d9855c128b541b7a2cffe7bb6ccc5a0`.
- Stvarni `gpt-6-luna` dao je nacrt u stanju `ready_for_review`. SQLite je potvrdio četiri završena zahteva. Otvoreni `case_fact` dokaz `ev_e5e1beaf4340418fa0bc33d79de77432` potvrdio je iznos 6.815,55 USD, vreme i skor `0.26731622570809` iz sažetka. Pretraga procedura vratila je `no_match`.
- Vedran je u Chrome-u sačuvao `request_more_information` zbog nedostajućeg porekla sredstava i nepotpune istorije. Ponovno otvaranje prikazalo je istu odluku i obrazloženje uz `reviewed` i 4/8 zahteva. SQLite je potvrdio odluku `rev_c1c76f3dd02548e7b68cfce8c9901ad3`, vezu za isti nacrt i četiri završena zahteva.
- Kontrolisani budžetski prekid nije ponovljen u ovoj probi. Zajednički SHA predaje još treba potvrditi sa timom.

## Mapa dokaza za predaju

| Stavka | Dokaz |
| --- | --- |
| CAP-01 | [Integracija MVP-a i tok](capstone-mvp-integration.md) |
| CAP-02–04 | [Živi prolaz na ranijem SHA-u](pr3-live-demo-2026-11-23.md). Dopuniti zapisom na SHA-u predaje. |
| CAP-05 | [Svih 16 uparenih ishoda](https://github.com/vekiii/capstone-FraudLensAI/blob/3eee1d6/evidence/tasks/feature-006-sc002-live-v2.md), uz zabeležene padove i regresije. |
| CAP-06 | [Negativne kontrole i prekid budžeta](../security/cap06-submission-verification-2026-11-23.md). |
| CAP-07 | Ovo uputstvo i potvrda člana koji je stvarno pokrenuo odabrani SHA iz čistog checkout-a. |
| CAP-08 | [Timski doprinosi](https://github.com/vekiii/capstone-FraudLensAI/blob/3eee1d6/evidence/tasks/feature-006-cap08-contributions.md) · [Vedranova beleška](cap08-vedran-mitic.md). |
