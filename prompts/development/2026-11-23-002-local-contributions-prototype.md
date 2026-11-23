# Original development request — 2026-11-23

User request, retained in its original language and scope:

> Nastavljamo dodatak lokalnih doprinosa obilježja zamrznutog LightGBM-a. Pročitaj AGENTS.md, aktuelni next_work.md i evidence/tasks/002-model-contributions-preparation-2026-11-23.md. Sačuvaj postojeće lokalne izmjene.
>
> Cilj ove cjeline: Pripremiti provjeren računski prototip, prijedlog verzionisanog ugovora i prihvatne testove, bez aktiviranja doprinosa u aplikaciji. Pregledaj stvarni preprocessing, trusted manifest i redoslijed 32 model kolone; koristi postojeći pouzdani loader i isti zamrznuti model. Na malom determinističkom uzorku label-free redova i browser slučaju `ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:1500153` izračunaj score, raw score i `pred_contrib`. Provjeri oblik/konačnost, additive i sigmoid rekonstrukciju, isti preprocessing/broj stabala, grupisanje one-hot kolona uključujući neaktivne, i razlikovanje log1p iznosa od izvornog novca.
>
> Pregledaj Feature 003 schema/validatore/outbound/evidence/frontend. Predloži novu log-odds metodu sa model/feature/transaction/snapshot identitetom, base/raw/doprinosima, top-3/remainder, unavailable/mismatch i context/evidence digestom; očuvaj stare izvještaje i bridge. Pripremi JSON primjere i RED kriterijume za identitet, redoslijed, skalu, NaN/inf, rekonstrukciju, unknown kategoriju, grupisanje, remainder i postojeći score. Slijedi RED→GREEN za računski modul; namjerni budući contract RED evidentiraj odvojeno bez mijenjanja produkcijskih validatora. Izmjeri RAG sažetak prema limitu 48.000 bajtova; dodaj plan/taskove u 002/003, dokumentuj komande/rezultate/ograničenja i poruku vlasniku 003. Ispravi `frontend/` u aktuelnim uputama na `web/`, uz očuvanje istorijskih izvršavanja.
>
> Granice: bez promjene modela/manifesta/preprocessinga/praga; bez treninga, labela, T230, novih metrika, bridge prepisivanja, Feature 006, showcase replaya, live providera, API/RAG/UI aktivacije, commita/pusha/mergea. Na kraju vrati rekonstrukciju/score, primjer sa skalom, ugovor/uticaj, testove, poruku vlasniku i naredni korak.

This file is a compact transcription of the request for project evidence; the chat remains the exact source text.
