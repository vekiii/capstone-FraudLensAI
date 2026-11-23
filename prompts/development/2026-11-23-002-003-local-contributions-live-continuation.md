# Original user request — local LIVE contribution demo continuation

Popunila sam privatni .env. Nastavi ranije odobreni lokalni LIVE demo doprinosa obilježja sa stvarnim providerom.

Pročitaj AGENTS.md, next_work.md i prethodnu live preflight evidenciju. Sačuvaj postojeće lokalne izmjene.

1. Provjeri da je .env Git-ignored i da nije staged. Učitaj konfiguraciju stvarnim projektnim mehanizmom u API i worker. Ne ispisuj sadržaj .env, API ključ, authorization headere ili druge tajne u izlaz, logove i evidence.
2. Provjeri da su ključ i eksplicitni model ID podešeni. Koristi tačno konfigurisan model, bez tihog fallbacka. Ako autentifikacija ili pristup modelu ne prođu, zaustavi se; ne pokušavaj druge modele automatski.
3. Ponovi potreban preflight modela, bridge-a, sidecara i konfiguracije. Koristi novo izolovano knowledge/investigation skladište. Ne mijenjaj postojeće zamrznute artefakte ili stare izvještaje.
4. Izvrši najviše DVA nova investigation pokušaja: prvo row:2959955; zatim row:1500153, ako prvi ne otkrije materijalni problem sa identitetima, dokazima ili tumačenjem doprinosa. Izvorni kanonski prefiks: `ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:`. Prethodni preflight nije napravio provider pozive. Bez dodatnih novih pokušaja nakon neuspjeha. Postojeći retry/repair može raditi samo unutar istog pokušaja i postojećih ukupnih budžeta.
5. Zadrži postojeći provider profil i sve granice, uključujući 48.000 ulaznih bajtova. Ne povećavaj limite i ne odsijecaj činjenice ili dokaze tiho radi prolaza.
6. Provjeri cijeli tok: score → objavljeni slučaj → doprinosi → stvarna LLM istraga → izvještaj → citirani dokazi. Koristi browser ako je dostupan. Ako nije, uradi HTTP provjere i jasno navedi da vizuelna browser provjera nije izvršena.
7. Pregledaj izvještaje prema stvarnim dokazima: isti score, identiteti, iznosi i valute; tačan smjer doprinosa i log-odds skala; bez pretvaranja doprinosa u procente rizika; bez tvrdnji o uzročnosti, krivici ili dokazu pranja novca; jasno ograničenje istorije i sintetičkog izvora; citati upućuju na dokaze dostupne tom pokušaju. Ne pravi dodatne LLM judge pozive.
8. Ako izvještaj prođe provjere, u izolovanom skladištu sačuvaj demo request_more_information odluku pod testnim identitetom. Ponovo otvori izvještaj i odluku bez novih provider poziva. Ne predstavljaj automatizovanu demo odluku kao ljudsko prihvatanje.
9. Zapiši attempt ID-jeve, requested/returned model ID, broj poziva, trajanje, usage ako je dostupan, provjere veličine ulaza, citate, nalaze i ograničenja. Bez tajni i bez neprovjerenih procjena cijene.

Ako pronađeš problem, dokumentuj ga bez promjene koda ili prompta između ova dva pokušaja. Ispravke i novo izvršavanje planiramo nakon pregleda rezultata.

Bez treninga, labela, T230, showcase replaya ili Feature 006. Bez commita, pusha, PR-a ili mergea.

Na kraju vrati tabelu: prošao / nije prošao / nije pokrenut za oba slučaja; da li je stvarni LLM koristio doprinose i da li ih je vjerno tumačio; konkretne nepodržane tvrdnje, ako postoje; stvarni broj provider poziva, trajanje i usage; browser/HTTP rezultate; preporuku: doraditi lokalno ili pripremiti Draft PR.
