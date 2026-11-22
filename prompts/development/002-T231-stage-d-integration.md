# Original user instruction — Feature 002 Stage D (2026-11-21)

> Nastavljamo Feature 002, Stage D: T231–T236.
>
> Prihvatam zamrznuti neponderisani LightGBM artefakt za lokalnu
> capstone integraciju i eksplicitni opt-in model režim, uz dokumentovana
> ograničenja iz validation i T230 izvještaja.
>
> Model SHA-256: 3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c
>
> Pouzdani manifest SHA-256: c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45
>
> Prag ostaje: 0.2489517623052024
>
> Ovo odobrenje ne obuhvata produkcijsku upotrebu, novi trening,
> novu test evaluaciju ili showcase replay.
>
> Radi iz: /Users/ladylazarus/Desktop/FraudLensAI-StageC
>
> 1. Pročitaj AGENTS.md, next_work.md i aktuelne Feature 002
> spec/plan/tasks/ugovore. Zabilježi moju odluku i njen opseg.
> 2. Implementiraj T231–T236 redom prema njihovim stvarnim zahtjevima.
> Počni T231 sintetičkim RED testovima i potvrdi da padaju zbog
> očekivanog nedostajućeg ponašanja.
> 3. Implementiraj verzionisane ugovore, pouzdani loader i Scorer
> adapter, eksplicitni opt-in, kontrolisane greške i read-only
> endpoint za podobnu transakciju. Očuvaj postojeći fixture režim
> i /api/cases ugovore; kanonske transakcione ID-jeve i feature
> identitet; isti train-only vokabular i redoslijed 32 model kolone;
> zamrznuti model i prag; provjere pouzdanog manifesta/model hash-a
> prije parsiranja; odbijanje nekompatibilnih ili neispravnih ulaza
> i artefakata. Ne uči preprocessing ponovo. Ne koristi labele za
> scoring. Model režim ne uključuj podrazumijevano i ne prikrivaj
> greške tihim prelaskom na fixture rezultate.
> 4. Skor predstavi kao risk score, uz verzije, sintetičko porijeklo
> i status koji zahtijeva ljudsku procjenu, prema specifikaciji.
> Objašnjenja zasnuj na dostupnim činjenicama i feature vrijednostima.
> Ne izmišljaj doprinose pojedinih features ili SHAP vrijednosti.
> 5. Poštuj FR-026: bez dnevnog capa, bez potiskivanja upozorenja
> i bez promjene praga. Ne implementiraj frontend, EDA stranicu,
> results API ili showcase replay u ovoj cjelini.
> 6. Provjeri paritet aplikacijskog scoring-a s postojećim offline
> skorovima na istim feature redovima i ID-jevima, bez labela.
> Uzorak unaprijed odredi po ID-ju, bez biranja prema test labelama.
> Ako otkriješ neslaganje, istraži uzrok; ne mijenjaj zamrznuti
> model ili offline rezultate da bi provjera prošla.
> 7. Pokreni relevantne negativne, ugovorne i backend regresione
> testove za T236, Ruff i git diff --check. Mali sintetički fit
> testovi su dozvoljeni ako ih postojeća regresija koristi;
> trening na projektnim podacima nije.
> 8. Sačuvaj prompt, izmjene, komande, rezultate, ograničenja i
> evidence za svaki task. Ažuriraj tasks.md, next_work.md i indeks
> samo prema stvarno ispunjenim kriterijumima.
>
> Vrati: status svakog taska T231–T236; šta je implementirano i gdje;
> rezultate testova i provjere pariteta; konkretne komande za fixture
> i opt-in model režim; preostale prepreke i naredni task.
>
> Ne ponavljaj T230, ne pristupaj test/showcase labelama,
> ne pokreći showcase replay, commit ili push.
