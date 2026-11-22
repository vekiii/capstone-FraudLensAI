# Original development request — Stage C numerical diagnosis

Date: 2026-11-20. Workspace: `/Users/ladylazarus/Desktop/FraudLensAI-StageC`.

> Validation audit je pokazao zasićenje skorova: izabrani model ima četiri stabla i 14.796 validation vjerovatnoća tačno 1.0. P@20 zavisi od transaction_id razrješenja te izjednačene grupe.
>
> Sada istraži numeričko ponašanje i pripremi prijedlog narednog kontrolisanog eksperimenta. Ne pokreći novi fit ni T230.
>
> Prvo pročitaj AGENTS.md, next_work.md, odobreni protokol, validation audit i relevantni trening kod.
>
> 1. Na postojećem izabranom artefaktu, bez fit-a, pregledaj stvarne LightGBM parametre, objective, boost_from_average, class weighting i eventualne dodatne sample weights; početnu predikciju i način inicijalizacije za neuravnotežene klase; raspon raw_score vrijednosti i izlaza/listova pojedinih stabala; u kojoj iteraciji dolazi do velikih pomaka raw skora; da li preprocessing i ulazi sadrže ekstremne ili neispravne vrijednosti relevantne za ovaj problem. Za tehnička objašnjenja provjeri instalirani LightGBM kod i odgovarajuću zvaničnu dokumentaciju. Razlikuj potvrđen uzrok, podržanu hipotezu i ono što ne možemo utvrditi bez novog fit-a.
>
> 2. Dijagnostički provjeri da li raw_score razlikuje transakcije čiji je predict_proba zaokružen na 1.0. Ako ih razlikuje, izračunaj zasebne validation AP i P@20 prema raw_score, uz isto determinističko pravilo za izjednačenja. Ovo je post-hoc dijagnostika, ne novi zvanični rezultat odobrenog eksperimenta. Ne mijenjaj izabrani prag, model, protokol, zamrznute test predikcije ili postojeće metrike.
>
> 3. Provjeri kako kombinacija class weighting-a i validation binary_logloss early stopping-a utiče na tumačenje izbora nakon samo 2–5 iteracija. Ne tvrdi da je kratko treniranje samo po sebi greška.
>
> 4. Predloži mali unaprijed definisan naredni eksperiment koji razdvaja moguće uzroke zasićenja. Za svaku predloženu promjenu navedi hipotezu, šta mijenjamo i šta držimo fiksnim. Ne predlaži široku pretragu parametara bez dijagnostičkog cilja. Uključi čuvanje za svakog kandidata: validation skorova i raw skorova; punih metrika i praga; best_iteration i istorije early stopping-a; parametara i modelskog artefakta; pokazatelja zasićenja i veličine izjednačenih grupa. Predlog mora koristiti samo postojeći train/validation. Zabilježi da je validation već korišćen za izbor i dijagnostiku; novi rezultati na njemu nisu nezavisna potvrda generalizacije.
>
> 5. Sačuvaj zaseban evidence zapis i ažuriraj next_work.md i indeks. Vrati nalaze i konkretan prijedlog za pregled.
>
> Ne mijenjaj trening kod ili postojeći protokol u ovoj fazi. Ne pokreći novi fit, ne pristupaj test/showcase labelama, ne pokreći T230, aktiviranje modela, commit ili push.

Result: [separate diagnosis and proposal](../../evidence/tasks/T228-stagec-numeric-diagnostic-2026-11-20.md). No fit or approval in this task.
