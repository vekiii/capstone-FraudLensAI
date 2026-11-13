# Feature 002 T007/T008 identity and hash proposal request

Received 2026-11-13 Europe/Belgrade. Exact original user instruction:

```text
Na osnovu upravo završenog T007/T008 pregleda pripremi konkretan prijedlog
za reproducibilne ID-jeve i hashove. Pročitaj AGENTS.md i next_work.md.
Koristi commit 182d0b2 kao referencu i sačuvaj zatečene lokalne izmjene.

1. Predloži tačan bajtni recept za D/C ID-jeve i DatasetVersion.
   Navedi redoslijed polja, kodiranje, zapis dužina i ordinala, oznake
   domena, način predstavljanja ulaznih hashova i dužinu izlaza.
   Zadrži postojeće ulaze i invarijante iz modela podataka.
2. Razradi prijedlog da odobreni SHA-256 stoji u zasebnom zapisu o reviewu
   i da se pri hashiranju mappinga CRLF normalizuje na LF. Preciziraj
   šta još ulazi u hash i šta se događa ako se mapping promijeni poslije
   odobrenja. Razlikuj hash mappinga, sirovi Git hash i postojeći hash
   vremenske politike.
3. Izračunaj ogledne D/C i dv_ vrijednosti za sintetički primjer iz
   pregleda. Pokaži da LF i CRLF daju isti predloženi hash mappinga
   i da promjena samo oznake mijenja dv_, uz iste D/C ID-jeve.
   Označi rezultate kao provjeru prijedloga, bez pokretanja T009–T011.
4. U postojećem macOS handoffu zapiši nalaz, prijedlog, stvarne komande
   i ogledne vrijednosti. Sačuvaj ovaj prompt u prompts/development/
   i u next_work.md poveži dokaz i navedi tačnu odluku koja čeka tim.
   Ostavi T007/T008 otvorene. Zadrži mapping, ugovore i importer kakvi
   jesu. Na kraju vrati izmijenjene fajlove i rezultat git diff --check.
```

This is a documentation and proposal request. It is not team approval or permission to import.
