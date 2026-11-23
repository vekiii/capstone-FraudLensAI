Odobravam ograničen lokalni LIVE demo doprinosa obilježja sa stvarnim
LLM providerom. Cilj je provjeriti da stvarni investigation/RAG tok
koristi nove doprinose pravilno, bez promjene modelskog skora.

Ovo je lokalni eksperiment, ne timsko prihvatanje novog ugovora.

Pročitaj AGENTS.md, next_work.md, postojeću evidence implementacije
i evidence/tasks/pr3-live-demo-2026-11-23.md.

Sačuvaj sve postojeće lokalne izmjene i artefakte.
Radi samo u FraudLensAI-Contributions na trenutnoj feature grani.

1. PREFLIGHT

Provjeri model, manifest, bridge i sidecar pinove, kompatibilni runtime
i postojeći score/status paritet.

Koristi postojeći odobreni live provider profil i stvarni model ID
iz važeće lokalne konfiguracije/projektnih uputa.
Bez tihog mijenjanja providera, modela, prompt profila ili budžeta.

Kredencijale koristi isključivo iz privatne server konfiguracije.
Ne ispisuj ih, ne šalji ih frontendu i ne dodaj ih u evidence/Git.
Ako nisu dostupni, stani prije mrežnih poziva i navedi šta nedostaje.
Ne koristi test provider kao zamjenu za live rezultat.

2. IZOLOVANO LIVE SKLADIŠTE

Pripremi novo izolovano knowledge/investigation skladište za ovaj demo.
Ne prepisuj postojeće pokušaje, odluke ili ranije demo baze.

Uključi lokalni opt-in doprinosa i provjerenu bounded provider projekciju.
Potvrdi da dostupne doprinose nije moguće pomiješati sa drugim slučajem,
runom ili kontekstom.

3. ODOBRENI OBIM POZIVA

Odobrena su najviše DVA nova investigation pokušaja:
- prvo row:2959955;
- zatim row:1500153, ako prvi ne otkrije problem sa identitetima,
  dokazima ili tumačenjem doprinosa.

Oba su iz izvora:
ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040

Jedan pokušaj po slučaju, bez automatskog novog pokušaja nakon neuspjeha.
Postojeći ugovoreni retry/repair mehanizmi smiju raditi samo unutar
istog pokušaja i postojećih ukupnih granica.

Ne povećavaj limite provider zahtjeva, alata, vremena, tokena ili
48.000 ulaznih bajtova. Ne pravi dodatne LLM judge pozive.

4. LIVE TOK

Pokreni backend, React i odgovarajući live worker sa istom konfiguracijom.

Za svaki odobreni slučaj provjeri:
- risk score i objavljeni slučaj;
- panel doprinosa i log-odds skalu;
- novu istragu sa stvarnim providerom;
- stvarni izlaz alata i contribution dokaz;
- završen izvještaj ili kontrolisani neuspjeh.

Ako je browser alat dostupan, prođi stvarni React tok i otvori sve
citirane dokaze. Ako nije, uradi HTTP provjeru i jasno označi da
vizuelni browser dio nije izvršen.

Ne uklanjaj limit i ne odsijecaj sadržaj tiho ako zahtjev ne stane.
Zabilježi stvarnu veličinu odbijenog zahtjeva i razlog.
Ne bilježi privatni provider sadržaj ili tajne u javnu evidenciju.

5. PROVJERA IZVJEŠTAJA

Uporedi konkretne tvrdnje sa dostupnim činjenicama, doprinosima i
citiranim dokazima. Provjeri da izvještaj:
- ne mijenja score, ID-jeve, iznose ili valute;
- razlikuje modelske doprinose od transakcionih činjenica;
- pravilno navodi smjer doprinosa;
- ne pretvara log-odds doprinose u procente rizika;
- ne naziva doprinose uzrocima, dokazom krivice ili pranja novca;
- jasno označava nepotpunu istoriju i sintetičko porijeklo;
- ne tvrdi da ima dostupno objašnjenje druge vrste;
- koristi samo dokaze stvarno dostupne tom pokušaju.

Sadržaj proceduralnih dokumenata ne smije služiti kao dokaz
da se konkretna aktivnost zaista dogodila.

Sačuvaj tačne tvrdnje i nalaze za provjeru, ali ovu Codex kontrolu
ne nazivaj nezavisnim ljudskim pregledom ili punom quality evaluacijom.

6. ČUVANJE I PONOVNO OTVARANJE

Ako izvještaj prođe provjere, u izolovanom skladištu provjeri snimanje
demo odluke request_more_information pod jasno označenim demo identitetom.

Ponovo otvori izvještaj i odluku bez pokretanja workera ili dodatnih
provider poziva. Potvrdi da dokaz i izvještaj ostaju isti i da broj
provider zahtjeva ne raste.

Ako izvještaj ima materijalnu grešku, ne predstavljaj ga kao uspjeh
i ne bilježi demo odluku kao prihvatanje kvaliteta.

7. EVIDENCIJA

Za svaki pokušaj zapiši:
- osnovni Git commit i digest inventara relevantnih lokalnih izmjena;
- model/sidecar/context identitete i konfiguraciju;
- attempt ID, requested i returned model ID ako je dostupan;
- stvarne provider pozive, alate, trajanje i usage ako je vraćen;
- provjeru veličine ulaza i budžeta;
- citate i rezultate provjere tvrdnji;
- neuspjehe, upozorenja i neizvršene provjere.

Ne izmišljaj cijenu poziva iz tokena bez provjerene cijene.
Ne predstavljaj offline veličine kao stvarno poslane live zahtjeve.

Ažuriraj evidence, indeks i next_work.md.
Bez commita, pusha, PR-a ili mergea.

Granice:
Bez treninga, labela, T230, novih test metrika, showcase replaya,
Feature 006 ili izmjene zamrznutih artefakata.
Ako pronađeš problem, dokumentuj ga. Bez dodatnih live pokušaja
ili promjene kodnih/prompt rješenja između ova dva mjerenja;
ispravke i ponavljanje planiramo poslije pregleda rezultata.

Na kraju vrati:
- tabelu oba pokušaja: prošao / nije prošao / nije pokrenut;
- da li je stvarni LLM koristio doprinose i koliko vjerno;
- konkretne pogrešne ili nepodržane tvrdnje, ako postoje;
- broj poziva, trajanje i usage;
- browser/HTTP dokaz;
- preporuku: ostaviti lokalno, doraditi ili pripremiti Draft PR.