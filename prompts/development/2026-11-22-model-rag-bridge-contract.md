# Original development request — model–RAG bridge contract, 2026-11-22

> Nastavljamo nakon uspješne integracione provjere na commitu dd0bf61280b74b5029651a622c6c075b85f14461.
>
> Cilj: pripremiti konkretan minimalni ugovor i implementacione taskove za povezivanje postojećeg Feature 002 modela sa Feature 003 investigation/RAG tokom.
>
> Pročitaj AGENTS.md, aktuelni next_work.md i evidence/tasks/model-rag-handoff-2026-11-22.md. Sačuvaj postojeće necommitovane izmjene. Pregledaj postojeće specifikacije, ugovore, modele i dataset adapter Feature 002/003. Iskoristi prethodni prijedlog ako već postoji; nemoj praviti paralelne dokumente za isti dogovor.
>
> Pripremi prijedlog koji precizno definiše: (1) kanonski transaction_id → case_id bez tihih kolizija; (2) model/feature/dataset/snapshot/run/prag/vremena; (3) tačne činjenice i istoriju, lokalni inventar bez labela i postupak pripreme ako izvor nedostaje; (4) 24h modelsku naspram investigation istorije; (5) score i činjenice bez kalibracione ili lažne feature-contribution tvrdnje; (6) unavailable/stale/mismatch/unknown/incomplete bez fixture zamjene; (7) React upozorenje → slučaj → istraga → dokazni izvještaj → ljudska odluka.
>
> Za svako polje navedi postojeći izvor, transformaciju/validaciju i ciljno polje. Razdvoji već određene tehničke odluke od odluka vlasnika 002/003. Predloži najmanje kompatibilno rješenje, verzionisanje i uticaj novih ugovora bez prepisivanja historijskih. Dodaj integracione taskove: ugovorni/negativni RED → adapter → React → paritet/cijeli tok → regresija, svaki sa kriterijumom i dokazom.
>
> Samo dokumentacija i taskovi, bez adaptera. Ažuriraj evidence, indeks i next_work.md stvarnim stanjem. Prijedlog nije prihvaćena timska odluka. Feature 006 isključen; bez treninga, T230 ponavljanja, labela, showcase replaya, live LLM-a, commita, pusha ili mergea. Na kraju vrati rješenje, precizne promjene ugovora, izvore, timske odluke sa preporukom/posljedicom i redoslijed taskova.

This file preserves the request; the proposed agreement and actual documentation work are in [the existing integration handoff](../../evidence/tasks/model-rag-handoff-2026-11-22.md).
