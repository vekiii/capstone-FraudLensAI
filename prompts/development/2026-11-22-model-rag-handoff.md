Preuzimam nastavak Milanovog integracionog rada na FraudLensAI.

Repo:
https://github.com/vekiii/capstone-FraudLensAI

Draft PR:
https://github.com/vekiii/capstone-FraudLensAI/pull/3

Integraciona grana:
integration/capstone-mvp

Posljednji nama poznati PR HEAD:
dd0bf61280b74b5029651a622c6c075b85f14461

Moj postojeći ML checkout:
 <STAGEC_CHECKOUT>

Cilj ovog zadatka:
Pripremiti izdvojeno integraciono radno okruženje, provjeriti da
postojeći zamrznuti model radi ispravno na Milanovom PR-u i utvrditi
tačan preostali posao za povezivanje Feature 002 sa Feature 003
investigation/RAG tokom.

1. Pročitaj primjenjive AGENTS.md i aktuelni next_work.md prije rada.
   Zatim pročitaj integracionu evidenciju PR-a i relevantne Feature 002
   i Feature 003 specifikacije, planove, taskove i ugovore.

2. Provjeri lokalni Git status, remote i aktuelni HEAD PR-a #3.
   Ako je HEAD napredovao od navedenog commita, evidentiraj razliku
   i koristi aktuelni PR HEAD kao osnovu. Ne spajaj promjene u postojeći
   ML checkout i sačuvaj sve postojeće lokalne izmjene.

3. Napravi zaseban Git worktree:
   <INTEGRATION_WORKTREE>

   Napravi novu radnu granu:
   integration/model-rag-handoff

   Osnova mora biti provjereni HEAD grane integration/capstone-mvp.
   Ako folder ili grana već postoje, provjeri njihovo stanje i nastavi
   bez brisanja ili prepisivanja postojećeg rada.

4. U novom worktree-u postavi zaključano okruženje prema aktuelnom
   integracionom lockfile-u i uputama. Provjeri kompatibilnost sa
   zamrznutim artefaktom, uključujući Python 3.14.10.
   Ne mijenjaj lockfile ili zahtjeve kompatibilnosti samo da instalacija prođe.
   Sačuvaj okruženje originalnog ML checkout-a.

5. Pronađi potrebne postojeće lokalne artefakte u ML checkout-u.
   U novi worktree kopiraj samo neophodne fajlove, uz provjeru
   očekivanih hash-eva i Git ignore pravila prije i poslije kopiranja:

   - data/eval/ibm-day-lightgbm-unweighted-freeze-001/
   - label-free feature snapshot:
     data/processed/t219-ibm-day-60-20-20-v1/
   - postojeći agregatni T230 izvještaj:
     data/eval/t230-unweighted-test-evaluation-001.json
   - postojeći EDA sažetak:
     data/processed/t246-hi-small-eda-summary-v1.json

   Provjeri stvarne zavisnosti loadera i results servisa; prenesi
   dodatni postojeći fajl samo ako je potreban i objasni zašto.
   Ne kopiraj T210 accepted.jsonl ni direktorijume labela za ovaj zadatak.
   Ne prepisuj postojeći fajl s drugačijim hash-em.

   Očekivani model SHA-256:
   3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c

   Manifest SHA-256:
   c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45

   Zamrznute test predikcije SHA-256:
   99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7

   T230 agregatni izvještaj SHA-256:
   5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb

   EDA sažetak SHA-256:
   b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820

   Zamrznuti prag:
   0.2489517623052024

6. Pregledaj i izvrši postojeći evidence/tasks/T233-parity.py
   na integracionom checkout-u. Potvrdi paritet offline skorova i
   risk HTTP odgovora. Ovo je inference provjera bez labela,
   nije ponavljanje test evaluacije.

   Ako provjera ne prođe, dijagnostikuj uzrok i zabilježi ga.
   Ne mijenjaj model, preprocessing, prag ili očekivane skorove
   da bi provjera prošla.

7. Pokreni integrisani backend i postojeću React aplikaciju prema
   aktuelnim uputama. Provjeri:
   - stvarni model risk odgovor i njegov prikaz;
   - postojeće validation/test agregate;
   - EDA sažetak;
   - očuvan fixture investigation tok.

   Ne pokreći live LLM/provider pozive u ovom zadatku.
   Razlikuj automatizovane, HTTP i stvarno obavljene browser provjere.

8. Pregledaj granicu između sadašnjeg modelskog risk odgovora i
   Feature 003 dataset investigation konteksta, uključujući:
   specs/003-ai-investigation/dataset-adapter-agreement-v2.md

   Pripremi minimalan prijedlog integracionog dogovora i taskova za:
   - mapiranje transaction_id i case_id;
   - dataset/run/snapshot identitete;
   - score, threshold, model i feature verzije;
   - podatke o transakciji i dostupnu istoriju;
   - objašnjenja zasnovana na dostupnim činjenicama;
   - unavailable, stale i mismatch ponašanje;
   - tok model upozorenje → slučaj → istraga/RAG → izvještaj
     → ljudska odluka.

   Razdvoji već podržano, potrebnu implementaciju i odluke koje
   moraju usaglasiti vlasnici Feature 002 i Feature 003.
   Ne izmišljaj istoriju, feature doprinose ili timska odobrenja.
   Sačuvaj istorijske ugovore.
   U ovoj cjelini još ne implementiraj novi adapter.

9. Zapiši originalni prompt i novu integracionu evidence prema
   konvencijama repozitorijuma. Ažuriraj next_work.md u novom
   worktree-u sa stvarnim rezultatima i jednim konkretnim narednim
   korakom. Ne označavaj T252 završenim bez stvarnog ljudskog pregleda.

Ograničenja:
- Bez novog treninga na projektnim podacima.
- Bez ponavljanja T230 i pristupa test/showcase labelama.
- Bez promjene zamrznutog modela, praga ili metrika.
- Koristi postojeću integrisanu React aplikaciju.
- Bez showcase replaya.
- Bez commita, pusha ili mergea u ovom zadatku.

Na kraju navedi:
- koji folder otvaram za naredni Codex chat;
- radnu granu i tačan testirani commit;
- rezultat pariteta i provjera aplikacije;
- eventualne prepreke;
- minimalne naredne taskove za model–RAG adapter.