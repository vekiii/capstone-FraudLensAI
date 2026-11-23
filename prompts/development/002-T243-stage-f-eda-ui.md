# Stage F EDA page — original development request

Date: 2026-11-21. User request, retained verbatim:

> Potvrđujem da je tim odobrio dodatnu EDA stranicu iz prijedloga T243,
> uz opisani obim i evidentirani uticaj na rok. Nastavi Stage F.
>
> Radi iz:
> /Users/ladylazarus/Desktop/FraudLensAI-StageC
>
> Pročitaj AGENTS.md, next_work.md, odluku feature-002-eda.md
> i tačne zahtjeve T243–T249.
>
> 1. Zabilježi ovu potvrdu odluke u T243 evidenciji, bez izmišljanja
>    imena recenzenata ili pojedinačnih potvrda.
>
> 2. Implementiraj preostale T247/T248 zahtjeve i T249 regresiju.
>    Poštuj njihove zavisnosti i RED/GREEN postupak.
>
> 3. Koristi postojeći /api/eda/summary i provjereni sažetak SHA-256:
>    b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820
>
>    Ne ponavljaj agregaciju i ne čitaj izvorni snapshot kroz frontend
>    ili na API zahtjev.
>
> 4. Dodaj pristupačnu EDA navigaciju/rutu i prikaze prema odobrenom
>    prijedlogu: izvor, vremenski obuhvat, kvalitet, brojevi redova,
>    kategorije i iznosi odvojeni po valuti.
>
>    Grafikoni moraju imati jasne jedinice i denominatore.
>    Ne sabiraj različite valute u jedan novčani zbir.
>    Ne prikazuj pojedinačne transakcije, račune ili labele.
>
> 5. Pokrij decoder i loading/empty/unavailable/malformed/retry stanja.
>    Očuvaj postojeće fixture, model i results tokove.
>    Ne prikazuj izmišljene ili hardkodovane zamjenske podatke.
>
> 6. Izvrši punu regresiju koju zahtijeva T249, frontend typecheck/build,
>    Ruff i git diff --check. Provjeri stvarnu EDA stranicu u browseru,
>    uključujući normalan prikaz i relevantna negativna stanja.
>
> 7. Sačuvaj evidence i ažuriraj tasks.md, next_work.md i indeks
>    prema stvarno ispunjenim kriterijumima.
>
> Vrati status T243–T249, rezultate provjera i način lokalnog pregleda.
>
> T252 ostaje otvoren do stvarnog ljudskog pregleda.
> Bez treninga, ponavljanja T230, pristupa labelama,
> showcase replaya, commita ili pusha.
