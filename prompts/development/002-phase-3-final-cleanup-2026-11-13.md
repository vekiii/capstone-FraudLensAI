Završi finalni cleanup faze 3 za FraudLens AI na grani
002-data-and-risk-scoring. Ispravi potvrđeni problem u importeru,
uskladi dokumentaciju, ponovi T016 i nakon uspješnih provjera napravi
commit i push. Stani prije T017.

Referenca pregleda je objavljeni commit
b5f75211c9a6aa5befa602f04308918df98ac106.

Prvo pročitaj AGENTS.md, next_work.md, zadatke T015/T016, offline ugovor
i evidence/tasks/feature-002-import-identity.md. Provjeri stvarnu granu,
HEAD, radno stablo i stanje remote grane. Sačuvaj zatečene izmjene.
Prije izmjena sačuvaj ovaj originalni prompt u prompts/development/.

1. Ispravi vezu između SHA-256 i stvarno obrađenog CSV-a

   pipeline_cli._import trenutno hashira CSV, pa ga ponovo otvara za
   parsiranje. U sintetičkoj provjeri izmjena `Wire,1` u `Wire,0` između
   ta dva koraka završila je kao `complete` pod hashom originalnog
   sadržaja.

   Dodaj RED regresiju koja reprodukuje problem. Provjeri da promjena
   izvora ne može objaviti kompletnu verziju pod pogrešnim hashom i da
   prethodna kompletna verzija ostaje dostupna. Test treba uredno da se
   učita i padne zbog potvrđenog ponašanja.

   Implementiraj minimalnu streaming ispravku. Provjeri SHA-256 i
   veličinu upravo onih bajtova koje parser obradi prije `complete`
   i `activate`. Pokrij zamjenu fajla i izmjenu na mjestu prema načinu
   na koji je implementiran tok čitanja. Pri nepoklapanju vrati
   kontrolisani neuspjeh i primijeni postojeća pravila za neuspjeli
   staged import.

   Sačuvaj provjeru odobrenog izvora, mappinga i namespacea, postojeći
   format CLI-ja, `inspect`, Foundation v1 i brzo ponavljanje iste
   kompletne verzije bez izmjene baze. Zadrži odobreni mapping i
   formulu za DatasetVersion.

2. Uskladi dokumentaciju s izvršivim stanjem faze 3

   - U specs/002-data-and-risk-scoring/quickstart.md zamijeni planirani
     primjer importa tačnom pokretljivom komandom. Navedi pripremu
     okruženja iz korijena repozitorijuma za macOS i PowerShell,
     putanju CSV-a, kreiranje data/processed/ i sve obavezne argumente:
     --source, --mapping, --namespace, --expected-sha256 i --store.
     Koristi stvarni IBM v8 namespace i odobreni SHA-256. Opiši prvi
     rezultat, ponavljanje iste komande i read-only provjeru baze.
     Zabilježi da je izmjerena baza bila oko 7,56 GB. Buduće CLI
     komande zadrži označene kao planirane.
   - U README.md i data/README.md dodaj kratku uputu i link na
     quickstart. Objasni da lokalni CLI import koristi zasebno
     odobrenje vezano za tačan mapping i izvor, uz očuvano ponašanje
     `inspect` komande. Navedi da kolega može napraviti svoju bazu
     iz istog CSV-a, a CSV i baza ostaju lokalno.
   - U offline ugovoru i tasks.md uskladi opise trenutnog stanja.
     Istorijske nalaze i ranije odobrene hashove sačuvaj kao istoriju.
     Ako mijenjaš dokument koji je obuhvaćen T007/T008 evidencijom,
     zasebno zabilježi dokumentacioni diff i novi hash. Provjeri da
     izmjene dokumentacije nisu promijenile pravila ili pokvarile
     provjeru odobrenog mappinga u CLI-ju.
   - U import evidenciju dodaj konačni SHA prethodne objave `b5f7521`
     i prethodno potvrđeni push. T060, nezavisnu reprodukciju kod
     kolege i kasnije faze zadrži prema stvarnom statusu.

3. Provjeri ispravku i ponovi T016

   Pokreni RED i GREEN regresiju, ciljane CLI/import testove, cijeli
   backend suite, Ruff i git diff --check. Provjeri da izmijenjeni
   dokumentacioni linkovi rade.

   Sačuvaj prethodnu SQLite bazu. Provjeri slobodan prostor i koristi
   novu ignorisanu putanju za bazu. Pokreni puni IBM v8 import preko
   ispravljenog CLI-ja, pa ponovi istu komandu nad istom novom bazom.
   Izvrši read-only provjeru. Potvrdi:

   - oba pokretanja završavaju uspješno i vraćaju isti DatasetVersion
     kao prethodni T016
   - obrađeno je 5.078.345 redova, svi su valjani i svih 5.078.345
     privatnih oznaka je podobno, uz 5.177 pozitivnih i 5.073.168
     negativnih
   - sve tri jednačine za računanje redova i oznaka se poklapaju
   - baza ima po 5.078.345 jedinstvenih D i C ID-jeva, očekivanu
     verziju SQLite šeme i quick_check=ok
   - hash CSV-a prije i poslije ostaje
     b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040,
     a odobreni normalizovani hash mappinga ostaje isti
   - hash nove baze poslije prvog importa i poslije ponavljanja je
     identičan. Za ovu provjeru poredi samo taj par pokretanja.

   U evidence/tasks/feature-002-import-identity.md upiši link na
   originalni prompt, pregledanu reviziju, stvarne komande, izlazne
   kodove, RED/GREEN rezultate, hashove, zbirne brojeve, trajanja,
   veličinu baze i rezultate read-only provjere. Ažuriraj tasks.md
   samo gdje treba uskladiti opis s dokazima. U next_work.md zapiši
   stvarni ishod i T017 kao sljedeći korak ako je cleanup završen.

4. Commituj i pushuj završni cleanup

   Kad prođu regresije i puni T016 import s ponavljanjem, provjeri da
   quickstart sadrži komandu koja je stvarno korištena. Pregledaj
   staged spisak i pokreni git diff --cached --check.

   U commit uključi samo ispravku faze 3, regresione testove,
   dokumentaciju, prompt i pripadajuću evidenciju. CSV, obje SQLite
   baze, journal/WAL fajlovi, generisani artefakti i nepovezane lokalne
   izmjene ostaju van commita.

   Commit poruka:
   fix(feature-002): finalize phase 3 import verification and docs

   Pushuj na origin/002-data-and-risk-scoring. Ako je remote grana
   napredovala, sačuvaj commitove kolega, razriješi preklapanja i
   ponovi provjere pogođene usklađivanjem prije pusha. Bez force
   pusha i bez mergea u main. Provjeri da remote pokazuje na isti
   puni SHA kao lokalni commit.

   Ako neka provjera ne prođe, dijagnostikuj problem, ispravi ga i
   ponovi pogođene provjere. Ako je puni T016 i dalje blokiran,
   evidentiraj konkretan razlog i prijavi stvarno stanje prije pusha.

Na kraju vrati sažetak ispravki, rezultate testova i oba importa,
status faze 3, link na ažurirani quickstart, puni commit SHA, GitHub
link, potvrdu pusha i git status. Stani prije T017.