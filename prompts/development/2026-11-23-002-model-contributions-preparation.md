# Original request — isolated model-contribution preparation

Date: 2026-11-23, Europe/Belgrade. Original user request:

> Pripremi izdvojeno radno okruženje za doprinose obilježja postojećeg
> zamrznutog LightGBM modela.
>
> Repo:
> https://github.com/vekiii/capstone-FraudLensAI
>
> Postojeći checkout:
>  /Users/ladylazarus/Desktop/FraudLensAI-Integration
>
> Novi radni folder:
>  /Users/ladylazarus/Desktop/FraudLensAI-Contributions
>
> Nova grana:
>  feature/002-model-contributions
>
> 1. Pročitaj AGENTS.md i aktuelni next_work.md.
>    Provjeri Git status, remote i postojeće worktree-e.
>    Sačuvaj sve lokalne izmjene i artefakte. Bez reset --hard,
>    clean, automatskog stasha ili prepisivanja rada.
>
> 2. Fetchuj origin i provjeri aktuelni origin/main.
>    Poznati merge commit je:
>    156e25b524f035522c228d64ce824065c3890939
>    Ako je main napredovao, evidentiraj nove promjene i stvarni HEAD.
>
> 3. Napravi novi worktree na grani feature/002-model-contributions
>    iz aktuelnog origin/main.
>    Ako grana ili folder već postoje, provjeri njihovo stanje
>    i nastavi bez brisanja ili prepisivanja.
>
> 4. U novom worktree-u pročitaj primjenjive upute i handoff.
>    Postavi izolovano okruženje prema lockfile-u i quickstart-u.
>    Model zahtijeva Python 3.14.10.
>    Ne kopiraj staru .venv i ne mijenjaj uv.lock ili verzijske
>    zaštite samo da instalacija prođe.
>
> 5. Pronađi postojeće provjerene artefakte u Integration i StageC
>    checkout-ima. U novi worktree kopiraj potrebni frozen direktorijum
>    i T219 label-free feature snapshot, uz provjeru hash-eva i Git ignore-a.
>    Za buduću end-to-end provjeru možeš prenijeti gotovu bridge
>    publikaciju uz nezavisni manifest pin prema aktuelnim uputama.
>
>    Ne kopiraj T210 accepted.jsonl, raw CSV ili direktorijume labela.
>    Ne regeneriši podatke i ne prepisuj postojeće različite fajlove.
>
>    Model SHA-256:
>    3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c
>
>    Trusted manifest SHA-256:
>    c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45
>
>    Prag:
>    0.2489517623052024
>
> 6. Provjeri da se model učitava kroz postojeći pouzdani loader.
>    Pregledaj postojeći preprocessing, mapiranje 32 model kolone,
>    ugovore objašnjenja i Feature 003 potrošače.
>
> 7. Pripremi kratak plan naredne cjeline:
>    - računski dokaz lokalnih doprinosa pomoću LightGBM pred_contrib;
>    - rekonstrukcija raw izlaza i postojećeg skora;
>    - mapiranje i grupisanje kolona;
>    - verzionisani ugovor za metodu i log-odds skalu;
>    - bounded top-3 sažetak sa ostatkom za RAG/UI;
>    - negativni testovi i očuvanje starih tokova.
>
>    U ovom prvom zadatku ne mijenjaj javne ugovore niti implementiraj
>    aplikacijsku podršku. Evidentiraj pripremu i stvarno izvršene
>    provjere prema projektnim konvencijama.
>
> Granice:
> - Isti zamrznuti model, preprocessing i prag.
> - Bez novog treninga, labela, T230 ili novih test metrika.
> - Bez showcase replaya, Feature 006 ili stare model-implementations grane.
> - Bez live LLM poziva, commita, pusha ili mergea.
>
> Na kraju vrati:
> - tačan folder koji otvaram za naredni Codex chat;
> - granu i osnovni commit;
> - runtime i provjerene artefakte;
> - eventualne prepreke;
> - jedan konkretan naredni korak.
