Odobravam lokalnu implementaciju i provjeru predloženog dodatka
doprinosa obilježja. Za sada bez commita, pusha ili PR-a.

Pročitaj AGENTS.md, next_work.md, postojeći sidecar prijedlog,
prototip i evidence/tasks/002-003-contribution-compatibility-2026-11-23.md.

Sačuvaj postojeće lokalne izmjene. Radi isključivo na
feature/002-model-contributions. Ne mijenjaj main, druge checkout-e
ili postojeće zamrznute artefakte.

Ovo je autorizacija za lokalni eksperiment s predloženim ugovorom,
ne tvrdnja da je vlasnik Feature 003 odobrio zajednički ugovor.

IMPLEMENTACIJA

1. Implementiraj verzionisani local-contribution-sidecar-v1 kao
   zaseban nepromjenjiv artefakt sa nezavisnim pouzdanim hash pinom.
   Postojeća bridge publikacija, v2 assessment/context ugovori
   i istorijski izvještaji ostaju nepromijenjeni.

2. Veži objašnjenje za:
   kanonski i javni transaction ID, case ID, assessment run,
   model/feature identitet i postojeći context digest.
   Provjeri rekonstrukciju, konačnost vrijednosti, metodu i skalu.

3. Dodaj eksplicitni lokalni opt-in za učitavanje doprinosa.
   Bez opt-ina postojeći tok mora ostati isti.

   Razlikuj:
   - nema konfigurisanog/dostupnog objašnjenja;
   - neispravan hash, identitet ili rekonstrukcija.

   Nepouzdane doprinose nikad ne šalji dalje.
   Postojeći provjereni score ostaje dostupan; odsustvo objašnjenja
   ne smije tiho postati razlog za nedostupnost modela.

4. Za nove investigation pokušaje dodaj provjeren doprinos kao
   zaseban verzionisan dokaz vezan za attempt, context i content digest.

   Zadrži postojeći v2 assessment explanation=unavailable kao istorijsku
   činjenicu, ali jasno razlikuj novo dodatno objašnjenje.
   Izbjegni kontradiktorne poruke u UI-ju i RAG-u.

   Promjena ili zamjena sidecara ne smije izmijeniti dokaz već sačuvanog
   pokušaja. Ponovno otvaranje starog izvještaja ne dodaje nove doprinose,
   ne mijenja izvještaj i ne poziva provider.

5. Koristi ograničeni sažetak doprinosa:
   metoda/skala, osnovna vrijednost, top-3 grupisana doprinosa,
   ostatak i potrebne provjerljive veze.

   Puni izračun zadrži lokalno za provjeru.
   Doprinosi nisu procenti rizika, uzroci ili dokaz pranja novca.

6. Implementiraj predloženu provider projekciju bez dupliciranog
   JSON teksta, uz očuvanje činjenica, identiteta dokaza,
   pokrivenosti istorije i proceduralnih odlomaka.
   Sačuvaj lokalni original dokaza i provjerljive citate.

   Primjenjuj postojeći limit od 48.000 bajtova na svaki zahtjev.
   Bez povećanja limita ili tihog odsijecanja sadržaja.

7. Dodaj zaseban tipiziran prikaz doprinosa u postojećem React toku.
   Prikaži dostupno/nedostupno/neispravno stanje, smjer doprinosa,
   skalu i ograničenja. Ne mijenjaj stare v2 dekodere tako da
   nekontrolisano prihvataju nova polja ili metode.

PROVJERE

8. Slijedi RED → GREEN za nova kritična ponašanja.
   Pokrij:
   - pogrešan pin, model, feature, ID, run ili context;
   - NaN/inf i neuspješnu rekonstrukciju;
   - top-3/remainder i determinističko grupisanje;
   - neispravan sidecar i očuvan osnovni scoring tok;
   - očuvanje starih izvještaja i dokaza;
   - provider projekciju, citate i input limit;
   - frontend dostupnost, greške i retry.

9. Ponovo potvrdi svih 65 score/status pariteta i postojeći T233.
   Bez labela i bez novih test metrika.

10. Provjeri cijeli lokalni tok sa doprinosima uključenim i isključenim:
    risk → slučaj → investigation → dokazi/izvještaj → testna odluka
    → ponovno otvaranje.

    Koristi novo izolovano investigation skladište i test provider.
    Provjeri oba poznata slučaja:
    row:1500153 i row:2959955 iz pinovanog IBM izvora.

    Test providerom provjeri tehnički prenos i prikaz.
    Ne predstavljaj ga kao potvrdu kvaliteta stvarnog LLM izvještaja.
    Ako browser nije dostupan, jasno razdvoji HTTP provjeru od
    neizvršenog vizuelnog pregleda.

11. Pokreni relevantnu i završnu backend/React regresiju,
    typecheck, build, Ruff i git diff --check.
    Ne ponavljaj već uspješne provjere bez razloga.

12. Napravi pregled promjena prema osnovi grane.
    Provjeri da model, prag, preprocessing, bridge i zamrznuti rezultati
    nisu promijenjeni i da nema labela, tajni ili artefakata za Git.

EVIDENCIJA I ZAVRŠETAK

Zapiši stvarne rezultate, komande, hash-eve, ograničenja i otvorene
odluke u evidence i next_work.md. Lokalni eksperimentalni ugovor
ne predstavljaj kao timski prihvaćen.

Ako pronađeš problem, ispravi ga unutar ovog obima i ponovi
odgovarajuće provjere. Ako ostane neriješen, dokumentuj ga i
ostavi dodatak isključen. Ne mijenjaj zajedničku granu.

Na kraju vrati:
- šta radi sa doprinosima, a šta bez njih;
- rezultate testova i pariteta;
- veličine stvarno izgrađenih offline zahtjeva;
- poznate rizike i neprovjerene stavke;
- preporuku: spremno za timski pregled ili ostaviti lokalno;
- lokalni URL i kratke korake za moj ručni pregled.

Bez treninga na projektnim podacima, labela, T230,
showcase replaya, Feature 006 ili live LLM poziva.
Bez commita, pusha, PR-a ili mergea.