# Original development prompt — Feature 002 publication

> Pripremi i objavi moj dosadašnji rad na FraudLens AI Feature 002
> na zajedničkoj grani `model-implementations`. Odobravam commit i push
> na `origin/model-implementations`. Radi do potvrđenog pusha, osim ako
> naiđeš na konkretan problem koji ne možeš riješiti u ovom opsegu.
>
> 1. Provjeri i uskladi granu
>    - Pročitaj AGENTS.md, next_work.md i Feature 002 tasks.md.
>    - Provjeri trenutnu granu, lokalni HEAD, zatečene izmjene i stanje
>      nakon `git fetch origin`. Sačuvaj moj i koleginičin postojeći rad.
>    - Pregledaj i nekomitovani diff i lokalne commitove koji još nisu
>      na GitHubu. Ako je remote napredovao, uključi nove commitove
>      bez prepisivanja tuđe istorije. Ponovi pogođene provjere nakon
>      usklađivanja. Bez force pusha i mergea u main.
>    - Sačuvaj ovaj originalni prompt u prompts/development/.
>
> 2. Uskladi dokumentaciju za predaju
>    - Provjeri da tasks.md, next_work.md, quickstart i evidencija
>      pokrivaju stvarno završene T029–T064. T065–T067 ostaju otvoreni
>      prema postojećim dokazima. U next_work.md navedi gdje Isidora
>      nalazi pet primjera za pregled i uputstvo za reprodukciju.
>    - Provjeri da quickstart vodi od čistog checkouta i lokalnog IBM
>      CSV-a do modela i benchmark izvještaja. Objasni kako kolega
>      može ponovo napraviti ili pribaviti provjereni lokalni artefakt.
>      Uputstvo ne smije pretpostaviti putanju s mog Maca ili model
>      koji nije dostupan u checkoutu. Ako neki korak još nije potvrđen
>      na drugom računaru, jasno ga označi.
>    - U sažetku navedi istraživački status benchmarka zbog prethodne
>      izloženosti testnog perioda, AP modela i pravila, 0 pozitivnih
>      u top 20 kod oba i 0 objavljenih upozorenja uz `no_alert`.
>      Dodatnu validacionu dijagnostiku i eksperiment s omjerom
>      prikaži odvojeno od zamrznutog benchmarka. Zabilježi da je
>      direktna browser provjera iz faze 7, a faza 8 ima live API/proxy
>      provjere. Ne mijenjaj model, prag ili protokol radi predaje.
>
> 3. Pokreni završne provjere i napravi commit
>    - Pokreni ciljane testove za trening, artefakte, API i reproduce,
>      backend regresije, frontend testove, typecheck/build, Ruff
>      i `git diff --check`. Evidentiraj stvarne rezultate. Ranije
>      poznate pretrained RED padove prijavi odvojeno od novih
>      regresija. Ne skrivaj ih izmjenom testova.
>    - Uključi kod, testove, protokol, dokumentaciju, promptove i
>      sažetu evidenciju za predaju. SQLite baze, CSV, joblib/pickle,
>      velike izlaze benchmarka, pojedinačne oznake, tajne, lokalne
>      logove i nepovezane izmjene ostavi van commita.
>    - Pregledaj staged spisak i pokreni `git diff --cached --check`.
>      Provjeri i cijeli raspon commitova koji ide na remote, kako
>      lokalni artefakti ne bi otišli kroz neki raniji commit.
>    - Commituj preostali rad. Ako već postoje odgovarajući lokalni
>      commitovi, zadrži ih i commituj samo preostale izmjene.
>
> 4. Pushuj i potvrdi predaju
>    - Pushuj na `origin/model-implementations` i provjeri da udaljeni
>      HEAD pokazuje na isti puni SHA kao lokalni.
>    - Vrati puni SHA, GitHub link do commita, `git status --short --branch`,
>      rezultate provjera i šta tačno Isidora treba da uradi za T065 i T066.
>      Navedi svaki kriterijum koji još čeka stvarni timski pregled.
