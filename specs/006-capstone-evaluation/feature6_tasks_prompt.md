# Feature 06 — šablon za prompt po fazi

U Codex razgovoru sa pristupom repozitorijumu pošalji:

> Iskoristi specs/006-capstone-evaluation/feature6_tasks_prompt.md i generiši mi prompt za poseban Codex razgovor za implementaciju faze 1, odnosno T001.

Dobijeni prompt kopiraj u novi razgovor sa pristupom istom checkoutu. Za prekinuti rad možeš tražiti prompt za nastavak određene faze iz aktuelnog handoffa.

| Faza | Zadaci | Cilj |
| --- | --- | --- |
| 1 | T001 | Zaključani setup i početne aplikacione provere |
| 2 | T002–T003 | T098 snapshot, integritet artefakata i runtime zavisnosti |
| 3 | T004–T008 | Dataset binding, testni prolaz i živi preflight |
| 4 | T009–T019 | Fiksni EV ulazi, početni rezultat, ciljana izmena i završno merenje |
| 5 | T020–T023 | Reprodukcija iz čistog checkouta i mapa dokaza |
| 6 | T024–T025 | Završne regresije i predaja rada |

## Instrukcije generatoru

1. Radi samo čitanje. Odmah posle važećih `AGENTS.md` instrukcija pročitaj korenski `next_work.md`, pa [tasks.md](tasks.md), [specifikaciju](spec.md) i [plan](plan.md). Pročitaj relevantne delove [quickstarta](quickstart.md), [EV matrice](contracts/ev-cases.md), [ugovora](contracts/evaluation.md), modela podataka i evidencije. Ako handoff nedostaje, navedi to i utvrdi stanje iz dostupnih izvora.
2. Proveri broj faze, ID-jeve, stvarne zavisnosti i trenutno stanje grane. Pri nastavku uporedi checkboxove sa kodom i dokazima. Ako faza i ID-jevi nisu usklađeni, postavi jedno kratko pitanje. Dozvoli i uži, jasno naveden opseg, posebno u fazi 4.
3. Vrati **samo jedan Markdown code block** sa gotovim promptom na srpskom. Navedi konkretne taskove, preduslove, putanje, komande i očekivane provere. Generator ne menja fajlove, Git stanje ili oznake zadataka i ne pokreće testove, aplikaciju ili provider.

## Sadržaj generisanog prompta

- Zatraži **implementaciju tačno izabranog opsega** na grani `006-capstone-evaluation`. Traži da izvršilac pročita `AGENTS.md` i korenski `next_work.md` pre rada, eksplicitno podesi `$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'` i koristi `speckit-implement` za taj opseg ako je dostupan. Sačuvaj postojeće izmene. Commit, push i merge zahtevaju zaseban zahtev.
- Za kritično ponašanje zahtevaj RED → GREEN → REFACTOR i stvarni razlog početnog pada. T001 koristi zaključanu instalaciju i postojeće ciljane provere. Za već ispravno ponašanje beleži regresionu proveru. Kad preduslov blokira deo posla, završi dostupne nezavisne zadatke i zabeleži blokadu.
- Za dataset proveri isti slučaj i snapshot kroz Cases i istragu, sa poreklom skora. Jasno razlikuj lokalnu probu sa testnim providerom od preflighta sa stvarnim modelom. Pre plaćenog poziva proveri da postoje ovlašćenje i raspoloživ budžet za taj obim. Čuvaj tajne i lokalne artefakte van Git-a.
- Za EV fazu zamrzni svih 16 ulaza i kriterijume pre početnog merenja. Očekivanja i evaluacione oznake drži van modelskog konteksta i pretrage. EV-01–EV-10 koriste konfiguraciju stvarnog modela uz dokumentovana opravdana zaustavljanja, a EV-11–EV-16 determinističke provere ili simulirane kvarove. Ciljana izmena sledi posle stvarnog početnog traga. Zadržati iste ulaze za završno merenje i sve statuse u imenitelju 16.
- Za predaju veži završne nalaze za isti testirani SHA. Stvarnu reprodukciju drugog člana i individualne doprinose evidentiraj po potvrdi. Otvorene ili neizvršene stavke zabeleži kao takve.
- Sačuvaj primljeni prompt pod `prompts/development/006-capstone-phase-NN.md` i datiraj dopune pri nastavku. Koristi evidence putanje iz taskova. Osveži `next_work.md` posle svake završene celine i čekiraj samo izvršene i proverene zadatke. Izveštaj treba da navede stvarne provere, preostale blokade i prvi naredni korak. Stani na granici traženog opsega.
