# Integracija frontend dorada za završni demo

24. novembar 2026, Windows. Testirani aplikacioni SHA `5d31af490fe41e4844db8f1d238fd39c80afa37d`, na osnovi `main` commita `71ba4b7`. Sa grane `feature/frontend` na `8582a5b` preuzet je diff za `web/`, uključujući Data, EDA prikaz, RAG i testove. Izvorne dorade su u `1ac73c1`, `ecf8458` i `c50fc41`. Merge kandidat obuhvata postojeći model, kroz PR #7 povezane doprinose modela, demo istragu i CAP-06 provere. [Nalog](../../prompts/development/2026-11-24-final-frontend-demo.md).

Posle prenosa sam reprodukovao pad novog testa za redosled na RAG dijagramu. Prikaz sada vodi kroz nacrt, validaciju i odluku analitičara kao uzastopne korake. Neuspeh evaluacije kvaliteta ima neutralne brojke i tekstualni status. Napomena o korpusu opisuje stvarni uslov za pokretanje lokalne pretrage. Test je zatim prošao u punom web paketu.

| Provera | Opaženo na `5d31af4` |
| --- | --- |
| `npm.cmd --prefix web ci --no-audit --no-fund` | Zaključana instalacija završena. |
| `npm.cmd --prefix web test -- --run` | 300 prolaza u 21 fajlu. |
| `npm.cmd --prefix web run build` | TypeScript i Vite build prošli, uz postojeće upozorenje za Three.js paket. |
| CAP-06, risk API i investigation API | 22 prolaza, uključujući svih sedam CAP-06 provera. |
| Chrome, `/data`, `/eda`, `/rag` | Širine 1280, 375 i 320 px, bez horizontalnog prelivanja ili neobrađenih JS grešaka. EDA se popunio iz verifikovanog agregata sa 5.078.345 prihvaćenih redova. Lokalni knowledge API je vratio `matched`, a agregatni model results API HTTP 200. |
| Chrome, skor i sačuvana živa istraga | Skor `0.26731622570809`, otvoren povezani slučaj i prikazani LightGBM doprinosi. Otvoren sačuvani dokaz sa iznosom, zatim posle stvarnog reload-a ista odluka, citat i stanje `reviewed`. Upoređeni identični API odgovori pre i posle. |
| Izolacija probe | Podešeni lokalni API i web na portovima 8011 i 5185. API dozvoljava samo GET tokom probe. Nema workera ni novih OpenAI zahteva. Postojeći brojač ostao je 4. SHA-256 proverne SQLite kopije ostao je isti. |

Backend komanda iz checkout-a kandidata, sa Pythonom 3.14.10 i zaključanim zavisnostima iz postojećeg demo okruženja sa istim `uv.lock`:

```powershell
$python = (Resolve-Path '../capstone-demo-77ed64c/.venv/Scripts/python.exe').Path
New-Item -ItemType Directory -Force .cache | Out-Null
$env:PYTHONUTF8 = '1'
& $python -m pytest -q -p no:cacheprovider backend/tests/integration/test_capstone_negative.py backend/tests/integration/test_risk_api.py backend/tests/integration/test_investigation_api.py --basetemp .cache/final-integration-tests --junitxml=.cache/final-integration-tests.xml
```

Za browser proveru kopirano je i ponovo hashirano 17 Windows artefakata i sidecar. Iz aktivne demo baze je SQLite backup metodom napravljena proverna kopija sa jednim pregledanim pokušajem i četiri završena zahteva. Chrome je pokrenut lokalnim `.cache/frontend-demo-browser.mjs` kroz `.cache/frontend-demo-run.ps1`. Prvi prolaz skripte proverio je doprinose pre završetka asinhronog učitavanja. Ponavljanje nakon uvođenja čekanja prošlo je na istom aplikacionom SHA-u.

Živi OpenAI nacrt nastao je na `77ed64c`. Ovaj kandidat je potvrđen ponovnim otvaranjem tog nacrta i odluke, uz 7/7 novih offline CAP-06 kontrola. Sveža živa generacija na integrisanom kandidatu i puna backend regresija ostaju neizvršene. Remotion projekat i istorijske grane nisu deo ove integracije.
