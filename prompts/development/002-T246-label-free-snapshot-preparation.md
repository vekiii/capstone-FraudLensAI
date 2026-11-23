# Development request: T246 label-free snapshot preparation

Nastavi nezavisni rad na prepreci T246.

Pročitaj AGENTS.md, next_work.md i postojeću implementaciju
label-free čitanja korišćenu tokom pripreme podataka.

Utvrdi može li se iz provjerenog lokalnog T210 snapshot-a dobiti
EDA sažetak cijelog izvora tako da se is_laundering vrijednosti
ne parsiraju, ne koriste i ne prikazuju.

Prvo pregledaj postojeći mehanizam uklanjanja label polja prije
parsiranja i projektna pravila. Ne koristi json.loads cijelog
transakcionog reda pa naknadno brisanje labele.

Ako postoji podržana putanja koja poštuje pravila, pripremi konkretan
postupak, sintetičke testove i provjeru porijekla/agregata.
Ako ne postoji, navedi tačno koji label-free ulaz treba pribaviti.

U ovoj fazi ne pokreći prolaz nad punim izvorom i ne implementiraj
EDA UI. Vrati nalaz i najmanji naredni korak.

T243 ostaje pending dok ne prenesem stvarnu timsku odluku.
T252 ne označavaj završenim bez recenzenta.
Bez showcase replaya, treninga, ponavljanja T230, commita ili pusha.
