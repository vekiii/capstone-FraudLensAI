# T252 — tehnička Windows reprodukcija

- Datum: 22. novembar 2026, Europe/Belgrade.
- Izvršilac: Codex. Izolovani checkout `.cache/capstone-t252-windows` na `d46699f`.
- Zahtev: proveriti i rasporediti Windows paket iz `new_folders/` i reprodukovati tok sa testnim providerom.

Svih 19 fajlova iz `SHA256SUMS.txt` je hashirano i poklapa se sa manifestom.
Kopirano je 17 fajlova iz `data/` u ignorisane putanje checkouta. Hash svakog
odredišnog fajla se poklapa. Digest bridge manifesta poklapa se i sa
zabeleženim pinom iz Windows quickstarta. Originalni ZIP nije pronađen u
`new_folders/`. Radno stablo izolovanog checkouta je bilo čisto nakon kopiranja.

Zvanični Windows Python ZIP je proveren SHA-256 vrednošću iz
[CPython manifesta](https://www.python.org/ftp/python/3.14.10/windows-3.14.10.json).
`uv sync --locked --python <lokalni Python 3.14.10> --group dev --group ml --group investigation`
je završio sa kodom 0. `.venv/Scripts/python.exe evidence/tasks/T233-parity.py`
uz `PYTHONPATH=backend/src` potvrdio je 8/8 tačnih skorova i 1/1 HTTP paritet.

Automatizovana ASGI provera koristila je `APP_MODE=model`, isti pin za API i
worker, svež lokalni store i `INVESTIGATION_PROVIDER=test`. Izvršeni su
`prepare-knowledge`, HTTP čitanja skora i bindinga, kreiranje pokušaja,
`worker --once`, čitanje citata, snimanje odluke i čitanje iz nove ASGI instance.
Skor `0.9267620061893889` se poklopio u risk, binding i case odgovorima za
`C0674a2484035b8a21df34cbd69f3a38b`. Pokušaj
`att_17c759e497f44322a20d57266d06395d` je stigao u `ready_for_review`.
Čitanja citiranih dokaza vrste `case_fact` i `procedure` su prošla. Odluka
`rev_3ffc8622aa6e4b9b8554c1b47a7eeb6b` je sačuvana i obnovljena.

Ovo je automatizovana tehnička evidencija. Browser i ljudski pregled T252
nisu izvršeni u ovoj sesiji. Nije bilo treninga, T230 ponavljanja, pristupa
label fajlovima ni plaćenih poziva.

## Prvi nalaz za Feature 06

[Pre/posle evidencija](feature-006-before-after.md) pokazuje da je baseline
EV-06 blokiran jer EV-01 nije proizveo nacrt, odluku i citat. Završni EV-06
je prošao uz ledger 19 → 19. Istorijski redovi ostaju zamrznuti. Za dopunski
dokaz definisati da li tim prihvata postojeći završni dokaz kao odvojenu
reprodukciju ili traži novi uporedivi par. Novo živo izvršavanje koristi
odobreni obim prema `evals/capstone/protocol.md`.
