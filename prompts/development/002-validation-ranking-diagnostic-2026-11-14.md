# Original development prompt — validation ranking diagnostic

Na grani model-implementations uradi dijagnostiku VALIDACIONOG rangiranja
za FraudLens Feature 002. Cilj je da saznamo zašto zamrznuti model daje
no_alert i da li neki od već istreniranih kandidata bolje rangira prvih
20 transakcija.

Pročitaj AGENTS.md, next_work.md, zamrznuti T029 protokol i evidenciju
feature-002-model-metrics.md. Zabilježi HEAD i sačuvaj zatečeni rad.
Sačuvaj ovaj prompt u prompts/development/.

1. Pronađi postojeće validacione predikcije i sačuvane artefakte kandidata
   iz T031–T032. Koristi tačno članstvo zamrznute validation particije i
   iste podobne transakcije za sve kandidate i R1–R3. Ako predikcije
   nedostaju, možeš ih ponovo izračunati iz postojećeg pouzdanog lokalnog
   artefakta, sa sačuvanom pripremom ulaza i bazom otvorenom read-only.
   Ako nedostaju i predikcije i artefakt, označi kandidata kao nedostupnog.
   Ne treniraj i ne pristupaj testnim oznakama ni predikcijama.

2. Za zamrznuto stablo, ostale dostupne kandidate i pravila R1–R3
   izračunaj AP i broj pozitivnih u top 20, 50 i 100. Kod izjednačenih
   skorova koristi postojeće determinističko pravilo iz protokola.
   Navedi ukupan broj podobnih validacionih redova, broj pozitivnih
   i njihovo učešće. Vrati tabelu:

   scorer | AP | pozitivnih u top 20 | top 50 | top 100 |
   najviši skor | broj transakcija na najvišem skoru

3. Za svaki scorer prikaži grupu istog skora koja obuhvata 20. mjesto:
   koliko je redova iznad nje, koliko ih je u grupi, koliko je pozitivnih
   u grupi i koliko ih postojeći redoslijed bira u top 20. Ako grupa
   prelazi granicu 20, jasno označi izjednačenje. Oznake koristi samo
   za mjerenje, bez promjene redoslijeda unutar grupe.

4. Za zamrznuti model i R1–R3 provjeri konkretan razlog za no_alert
   prema implementiranoj T032 politici. Izbroj koliko bi upozorenja
   dao najviši inkluzivni prag i provjeri postoji li prag s 1–20
   upozorenja. Ako postoji, zabilježi najbolji ostvareni F0.5 i objasni
   zašto je izabran no_alert. Odvoji top-20 rangiranje od broja stvarnih
   upozorenja prema zamrznutoj politici.

5. Zapiši komande, izvore predikcija, identitet protokola, brojeve i
   ograničenja u evidence/tasks/feature-002-model-metrics.md kao
   dodatnu validacionu dijagnostiku. Vrati tabelu i preporuči jedan
   naredni eksperiment na osnovu nalaza: politiku upozorenja ako je
   problem prvenstveno veliki broj izjednačenih skorova ili rad na
   kandidatima/karakteristikama ako vrh liste slabo izdvaja pozitivne.
   Ako podaci ne razjašnjavaju uzrok, navedi šta tačno nedostaje.

Zadrži zamrznuti model, prag, protokol i objavljeni benchmark.
Bez novog treninga, biranja novog pobjednika, izmjene baze, commita
ili pusha. Rezultat prikaži kao dijagnostiku na validaciji.

The user message repeated this same prompt a second time verbatim.
