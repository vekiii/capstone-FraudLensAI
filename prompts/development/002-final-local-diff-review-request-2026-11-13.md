Uradi tehnički review konačnog lokalnog diffa za FraudLens AI Feature 002
na grani `002-data-and-risk-scoring`. Želim da ti provjeriš usklađenost
s projektom i vratiš zaključak koji mogu razumjeti bez čitanja diffa.

Pročitaj AGENTS.md, next_work.md, original_idea.md, Feature 002 spec,
plan, tasks.md i relevantne ugovore. Pregledaj stvarni lokalni diff u
odnosu na 182d0b2, uključujući nove evidence fajlove. Kao osnovu koristi
stvarne zahtjeve projekta i kriterijume prihvatanja.

1. Provjeri T007. Da li mapping vjerno čuva smjer transakcije, novac,
   vrijeme i privatne oznake? Da li recept za D/C i DatasetVersion daje
   stabilne rezultate? Ponovi ogledne vektore i provjeri da se hash
   mappinga poklapa s konačnim diffom na LF i CRLF ulazima.
2. Provjeri T008. Da li izmjene čuvaju Foundation v1 i postojeći v2
   format? Da li v2 ugovori daju scoringu, frontend/API-ju, investigationu
   i priority/simulationu potrebne podatke za predviđeni MVP? Za svaku
   komponentu navedi konkretan nalaz i ugovor ili zahtjev na koji se
   oslanjaš. Razlikuj sadašnji problem od planirane kasnije implementacije.
3. Pokreni ciljane provjere. Za svaki problem navedi zahtjev, fajl i
   liniju, primjer, posljedicu i najmanju potrebnu ispravku. Ako postoji
   tehnički blokator za T009–T011, reci tačno koji. Ako ga nema, reci
   eksplicitno da je rješenje tehnički spremno za početak importa.
4. Sačuvaj ovaj prompt u prompts/development/ i dodaj nalaze, pregledanu
   reviziju ili hashove, komande i stvarne rezultate u postojeći
   evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md.
   Ažuriraj next_work.md prema ishodu. Zajedničku tehničku odluku koju
   sam već prenijela zadrži u evidenciji. Zaključke ovog pregleda
   evidentiraj kao Codexov tehnički pregled, bez dodjele ljudi ulogama
   ili upisivanja pojedinačnih odobrenja.

U ovoj sesiji pregledaj i evidentiraj nalaze. Na kraju vrati kratak
zaključak o usklađenosti s projektom, konkretne tehničke blokatore ako
postoje i status T007/T008 prema postojećim kriterijumima. Bez commit/push.
