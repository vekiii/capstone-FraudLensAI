Implementiraj fazu 5 — US3: Reprodukcija i predaja, isključivo T020–T023, za `specs/006-capstone-evaluation`. Nemoj samo napisati plan ili novi prompt. Završi nezavisan rad, evidentiraj stvarne ljudske i tehničke blokade i stani pre T024.

FraudLens AI koristi FastAPI/Python i jednu React/TypeScript/Vite aplikaciju u `web/`. Ova faza uređuje proverljivo uputstvo, stvarnu reprodukciju drugog člana, potvrđene doprinose i CAP mapu dokaza. Ne popravlja rezultate prethodne evaluacije niti ponavlja plaćene pozive bez odgovarajućeg ovlašćenja.

Sve putanje su relativne u odnosu na koren projekta. Koristi aktuelni checkout, bez istorije prethodnih razgovora.

## 1. Početno čitanje i provera

Pročitaj primenljive `AGENTS.md`, zatim odmah root `next_work.md`, pre planiranja i rada. Ponovi pri nastavku sesije. Ovaj zahtev određuje opseg; handoff ga ne proširuje.

Pročitaj:
- `.specify/memory/constitution.md`
- `specs/006-capstone-evaluation/{tasks.md,spec.md,plan.md,quickstart.md}`
- relevantne delove `research.md`, `data-model.md` i `contracts/evaluation.md`
- `evidence/tasks/feature-006-release-candidate.md`
- `evidence/tasks/feature-006-before-after.md`
- `evidence/tasks/feature-006-final-live.md`
- `evidence/tasks/feature-006-final-negative.md`
- `evidence/tasks/feature-006-targeted-change.md`
- `evidence/tasks/feature-006-t098-inputs.md` i povezani postupak lokalnog indeksa
- relevantne setup/provider/binding/smoke evidence zapise
- `evals/capstone/README.md`, manifest i protocol prema potrebnom obimu
- postojeće evidence/prompt konvencije i eventualne već pripremljene T020–T023 zapise.

Ne učitavaj nezavisni Feature 03 holdout ili njegove referentne odgovore radi ove predaje.

Ako je dostupan, pročitaj i primeni `.agents/skills/speckit-implement/SKILL.md` samo za T020–T023. Eksplicitan opseg ima prednost nad opštom instrukcijom da se završi ceo tasks.md. Poštuj stvarne checklist/hook zahteve; ne menjaj oznake radi prolaska i ne traži ponovno odobrenje već odobrenih rutinskih koraka.

U PowerShell sesiji:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
```
Ovo ne menja Git granu.

Read-only pregled pri generisanju prompta pokazao je granu `006-capstone-evaluation`, prazan `git status --short`, T001–T019 označene završenim i T020–T023 neoznačene. Ponovo proveri granu, HEAD, status i dokaz za svaki preduslov.

Sačuvaj postojeće izmene. Bez automatskog pull-a, merge-a, promene grane, reset/clean/stash ili objavljivanja.

## 2. Referentna revizija i poznata ograničenja

Prethodni evidence vezuje:
- baseline: `5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`
- testirani final: `d8acc2a335d95e2402f586006925949f4d9f7739`

Zabeleženi zbir:
- baseline: 11 pass, 4 fail, 1 blocked, od 16;
- final: 13 pass, 3 fail, od 16;
- sve šest finalnih negativnih kontrola prolaze;
- 36 potvrđenih provider zahteva, 121.405 ulaznih i 18.891 izlazni token;
- novčani iznos nije očitan.

Finalni otvoreni EV nalazi:
- EV-01: validiran nacrt i obnovljiva odluka postoje, ali nema zahtevanog proceduralnog odlomka;
- EV-04: `citation_set_mismatch`;
- EV-07: generički pogoci bez potrebne neizvesnosti.

T019 evidence navodi dokaz za SC-001 i SC-003, dok SC-002 ostaje otvoren zbog blokiranog baseline EV-06. Nezavisna reprodukcija i puna završna regresija ostaju neizvršene.

To su istorijski rezultati koje moraš proveriti prema evidence-u, ne sveže izvršene provere ove sesije. Ne pretvaraj „task izvršen” u „svi kriterijumi prošli”.

Razlikuj testirani aplikacioni SHA od kasnijeg dokumentacionog HEAD-a. Posebno sačuvaj zapis da je posle oba merenja ispravljena samo execution schema evidencije (`run_` → `inv_`), sa zasebnim digestom. Ne predstavljaj tu ispravku kao deo ranije testiranog SHA-a ili novu promenu rezultata.

## 3. T020 — stvarni quickstart za kandidata

Zavisnosti: T016 i T019.

Ažuriraj:
`specs/006-capstone-evaluation/quickstart.md`

Uputstvo mora sadržati stvarne, proverljive korake za:
- identifikaciju testirane revizije i čistog checkout-a;
- Python 3.14 / Node 24 i locked instalacije;
- autorizovani prenos lokalnih artefakata koji nisu u Git-u;
- proveru transfer digest-a, source/run identiteta i kompatibilnosti;
- pripremu history indeksa za konkretni checkout;
- odvojene API i worker terminale sa istom dataset konfiguracijom;
- React u `web/`, postojeći Vite proxy i proveru porekla;
- pripremu korpusa i izbor tačne retrieval/prompt/provider konfiguracije;
- svež lokalni investigation store, bez korišćenja autorovog radnog store-a kao zamene za reprodukciju;
- test-provider pripremu i jasno odvojene uslove za stvarni model;
- zaustavljanje sopstvenih procesa i čuvanje evidence-a.

Važno: postojeći lokalni history indeks vezan je za putanju/potpis izvornog store-a. Ne predstavljaj digest indeksa iz `D:\AIBootcamp\capstone` kao prenosiv na drugi checkout. Navedi postojeću `prepare-history-index` komandu i proveru novog lokalnog indeksa prema T002 evidence-u. Izvorne T098 fajlove sačuvaj nepromenjenim.

Osnovne komande, iz korena:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix web ci
```

Tačne komande za indeks, korpus, server i worker preuzmi iz postojećeg CLI-ja i stvarno izvršenih zapisa; ne izmišljaj opcije. Ukloni mašinski specifične pretpostavke i ne dodaj stvarne ključeve u dokumentaciju.

Poveži tri scenarija za odbranu sa stvarnim dokazima:
1. validiran nacrt, sadržajno proverena citirana činjenica i obnovljiva odluka iz final EV-01/EV-06, uz jasno ograničenje da zamrznuti EV-01 nije prošao proceduralni kriterijum;
2. final EV-08 `needs_information`, sa stvarno nedostupnom istorijom;
3. konkretna kontrolisana greška iz final EV-11–EV-16.

Nemoj označiti neuspešan EV red kao uspešan samo zato što pokazuje deo korisnog toka.

Za dokumentacione izmene nema veštačkog RED-a. Proveri CLI opcije, lokalne linkove, putanje i primenljivost komandi. Jasno razlikuj komande koje si sada proverio od onih koje imaju samo postojeći izvršeni dokaz.

## 4. T021 — stvarni drugi član, čist checkout

Zavisi od T020.

Pripremi i održavaj:
`evidence/tasks/feature-006-peer-reproduction.md`

Najpre pripremi konkretan pregledljiv quickstart i postupak reprodukcije. Zatim zatraži stvarni nalaz drugog člana kroz ovaj razgovor ako već nije dostupan.

Zabeleži samo stvarno potvrđene podatke:
- član i datum;
- čist checkout i tačan testirani SHA;
- operativno okruženje i verzije;
- poreklo/digeste lokalnih artefakata i lokalno pripremljenog indeksa;
- izvršene komande i stvarne ishode;
- provereni Cases/investigation binding, citat i obnovljivu odluku prema dogovorenom obimu;
- probleme, odstupanja i neizvršene korake.

Tvoje ponavljanje instalacije, drugi terminal, worktree ili drugi agent nisu drugi član tima. Ako osoba nije dostupna, sačuvaj `pending` zapis i preciznu listu potrebnih nalaza, ostavi T021 neoznačen i nastavi T022/T023 koliko je moguće.

Ako pripremaš izolovani checkout za proveru postupka, ne menjaj postojeću granu ili tuđe izmene. Sopstvenu probu označi kao agentsku pripremu, ne kao peer reproduction.

Novi provider pozivi nisu automatski odobreni prethodnim baseline/final budžetom. Pre svakog novog plaćenog izvršavanja proveri eksplicitno ovlašćenje i raspoloživ budžet za baš taj obim. Ako ih nema, dovrši offline pripremu i zabeleži blokirani live deo; ne pokreći probe ili worker sa stvarnim providerom.

Ne šalji poruke članovima preko spoljnih servisa bez posebnog ovlašćenja.

## 5. T022 — potvrde sva četiri člana

Može napredovati paralelno sa dokumentacijom i reprodukcijom, nakon identifikovanja kandidata.

Pripremi:
`evidence/tasks/feature-006-cap08-contributions.md`

Za svakog od četiri člana prikupi i poveži:
- suštinski tehnički doprinos;
- odluku i stvarnu proveru te odluke;
- vezu doprinosa sa glavnim tokom;
- konkretan primer pregleda rada kolege;
- relevantne fajlove, commit/evidence reference i vezu sa predatom revizijom;
- stvarnu potvrdu člana, sa datumom kada je poznat.

Git autorstvo, istorijski izveštaj ili pretpostavljena timska uloga mogu biti izvori za pripremu, ali nisu zamena za traženu potvrdu. Ne izmišljaj imena, doprinose, sate, review ili potpise.

Pripremi postojeće dokazive stavke i jasno izdvoji nepotvrđeno. Kroz ovaj razgovor traži samo nedostajuće podatke/potvrde, grupisano i konkretno. Ne zahtevaj ponovo već postojeću važeću potvrdu.

Bez potvrda sva četiri člana T022 ostaje delimičan. Nezavisni rad na CAP mapi ipak nastavi.

## 6. T023 — CAP-01–CAP-08 mapa dokaza

Zavisi od T019–T022.

Sastavi:
`evidence/tasks/feature-006-capstone-evidence-map.md`

Za svih osam stavki navedi:
- konkretan zahtev;
- testirani SHA;
- dokaz i način provere;
- stvarni status;
- ograničenja i preostali korak.

Obuhvati:
- CAP-01: specifikacija, plan, ugovor i glavni tok;
- CAP-02: dataset score provenance i stvarni model;
- CAP-03: sadržaj citata, njegova potpora i nedovoljni dokazi;
- CAP-04: deterministički alat, stanja i sačuvana odluka;
- CAP-05: svih 16 baseline/final redova, ciljana izmena i imenilac 16;
- CAP-06: svih šest finalnih negativnih kontrola;
- CAP-07: tačna revizija, quickstart, artefakti i stvarna peer reprodukcija;
- CAP-08: potvrđeni doprinosi i pregledi sva četiri člana.

Proveri da final live, final negative i final EV rezultati referenciraju isti testirani SHA. Baseline zadržava sopstveni SHA. Ako postoji neslaganje, prijavi ga; ne menjaj istorijske reference da bi izgledale usklađeno.

Poveži tri scenarija za odbranu iz T020 i njihove stvarne granice. Sačuvaj 13/16 final rezultat, tri neuspeha i otvoreni SC-002. Ne popravljaj aplikaciju ili ponavljaj evaluaciju u ovom opsegu.

Ako T021/T022 nedostaju, napravi kompletnu mapu raspoloživih dokaza sa eksplicitnim pending poljima. T023 ostaje delimičan dok njegove zavisnosti nisu stvarno ispunjene.

## 7. Provere i granice

Ova faza je prvenstveno dokumentacija, provera porekla i stvarni ljudski postupak. Ne izmišljaj RED za tekst ili već ispravno ponašanje.

Proveri:
- lokalne linkove i navedene CLI opcije;
- postojanje i dostupnost referenciranih commit-a;
- konzistentnost SHA/digest/status referenci;
- da zbir obe faze zadržava svih 16 redova;
- da privatni lokalni fajlovi nisu predstavljeni kao automatski dostupni iz Git-a;
- da deljeni evidence nema ključeve, `.env` sadržaj ili nezaštićene podatke.

Ne pokreći velike arhive ili evaluacione runner-e samo radi čitanja rezultata. Ako koristiš postojeći checker, prvo proveri da nema provider poziva, mutacija izvornog stanja ili drugih neželjenih efekata.

Puna završna regresija T024 i završna pokrivenost T025 ostaju van opsega. Za neophodnu stvarnu produktnu ispravku dokumentuj nalaz i traži odluku o proširenju; ne menjaj testirani kandidat prećutno.

Sačuvaj jednu React/TypeScript aplikaciju, backend ugovore, zamrznuti EV paket, originalne rezultate, lokalne baze i lockfile-ove. Nema novog treninga, holdout tuninga ili druge frontend aplikacije.

## 8. Prompt, evidence i predaja

Pre izmena sačuvaj tačan primljeni prompt u:
`prompts/development/006-capstone-phase-05.md`

Postojeći original ne prepisuj; nastavke dodaj kao datirane dopune.

Održavaj:
- quickstart;
- tri propisana T021/T022/T023 evidence fajla;
- `evidence/tasks/feature-006-phase-05-handoff.md`;
- status T020–T023 u `specs/006-capstone-evaluation/tasks.md`;
- kratak aktuelni `next_work.md`.

Zabeleži početnu granu/HEAD, testirani kandidat, postojeće izmene, stvarne provere, ljudske potvrde, blokade i jedan konkretan naredni korak. Osvežavaj predaju nakon koherentne celine, ne samo na kraju.

Čekiraj samo potpuno izvršene i proverene taskove. Pending zapis ili pripremljen šablon ne završava ljudsku reprodukciju ili individualne potvrde. Ne proglašavaj feature prihvaćenim dok kriterijumi ostaju otvoreni.

Pregledaj diff i nove fajlove, pa izvrši:
```powershell
git diff --check
```

Bez subagenata osim ako ih primenljive instrukcije zahtevaju. Bez commit-a, tagovanja, push-a, merge-a ili deploy-a bez zasebnog zahteva.

Završni odgovor: status T020–T023, šta je pripremljeno i stvarno potvrđeno, izvršene provere, nedostajuće ljudske/live stavke, otvoreni EV/SC nalazi i handoff putanja. Sledeći korak je prvi stvarno nedovršen uslov ove faze; tek nakon njenog završetka zasebno pokrenuti T024–T025.

Ne započinji T024.

## Dopuna — 22. novembar 2026.

Na sledeći korak „Sledeći korak je da drugi član izvrši odeljke 1–3 quickstart-a sa testnim providerom i dostavi nalaz za T021.” korisnik je odgovorio:

> Hajde da promenimo, to cu odraditi isto ja jer on radi sada na drugoj stvari a moramo da nastavimo sa radom.

> Odradi fazu 5 dok je ne zavrsis.

Na zahtev za četiri potvrde T022 korisnik je odgovorio:

> Nece biti pregleda rada drugih kolega jer oni sada rade druge stvari i moramo da menajamo plan jer nemaju vremena za pereglede. Ja sam pregeldao i potvrdjujem.
