# Feature 002 T250/T251/T240 — original development request

User request, 2026-11-21:

> Nastavljamo Feature 002 nakon Stage E.
> T237, T238, T239, T241 i T242 su završeni; T240 čeka T251.
>
> Radi iz: `/Users/ladylazarus/Desktop/FraudLensAI-StageC`
>
> Pročitaj AGENTS.md, next_work.md, aktuelne spec/plan/tasks,
> API ugovore i relevantnu Stage C–E evidenciju.
>
> Implementiraj T250, zatim T251, pa dovrši T240 prema stvarnim
> zahtjevima i zavisnostima taskova.
>
> 1. T250: prvo napiši i pokreni zahtijevane negativne RED testove
> pristupa labelama i autorizacije rezultata. Potvrdi da padaju
> zbog očekivanog nedostajućeg ponašanja.
>
> 2. T251: implementiraj autorizovani read-only results API koji
> koristi već sačuvane, provjerene agregatne izvještaje.
> Ne pokreći evaluaciju na API zahtjev i ne čitaj accepted.jsonl,
> pojedinačne labele ili prediction CSV radi ponovnog obračuna.
> Za završni test izvještaj koristi postojeću T230 evidenciju
> i očekivani SHA-256:
> `5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb`
> Provjeri porijeklo i vezu izvještaja s tačnim zamrznutim modelom,
> prediction hash-em, pragom i odobrenjem.
> Nedostajuće, neodobrene ili neusklađene izvještaje odbij
> kontrolisano, bez izlaganja lokalnih putanja ili sadržaja fajlova.
> Primijeni autorizacioni ugovor iz specifikacije. Ne izmišljaj
> novi sistem naloga ili proširuj obim projekta.
>
> 3. T240: poveži postojeći frontend decoder i prikaz agregata
> sa stvarnim results API-jem.
> Jasno odvoji validation i test, uz:
> broj redova i pozitivnih/negativnih primjera;
> metrike i denominatore;
> zamrznuti prag i model identitet;
> vremenski obuhvat i sintetičko porijeklo;
> ograničenja rezultata.
> P@K cijele particije ne predstavljaj kao dnevni P@K.
> Ne prikazuj skor kao kalibrisanu vjerovatnoću.
> Obezbijedi loading, unavailable, unauthorized i error stanja,
> bez hardkodovane zamjene za API rezultat.
>
> 4. Pokreni relevantne backend i frontend regresije, Ruff,
> typecheck, build i git diff --check.
> Ako je browser dostupan, provjeri stvarni prikaz dozvoljenih
> rezultata i odgovarajuća negativna stanja.
> Odvoji browser nalaze od automatizovanih testova.
>
> 5. Sačuvaj prompt, RED/GREEN dokaze, komande, rezultate i ograničenja.
> Ažuriraj tasks.md, next_work.md i evidence indeks samo prema
> stvarno ispunjenim kriterijumima.
>
> Vrati status T250/T251/T240, implementirane ugovore i korisnički tok,
> rezultate provjera i tačan naredni task.
>
> Ne implementiraj Stage F EDA ili showcase replay u ovoj cjelini.
> Bez novog treninga, ponavljanja T230, pristupa pojedinačnim
> test/showcase labelama, promjene modela/praga, commita ili pusha.
