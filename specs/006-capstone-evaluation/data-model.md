# Model podataka — Feature 06

| Entitet | Polja i pravila |
| --- | --- |
| Dataset binding | `case_id`, `transaction_id`, `source_mode`, `snapshot_ref`, dataset i verzija skoringa, vrsta skora, `context_revision` iz servera. Dataset binding koristi istu objavljenu reviziju u Cases i investigation čitanju. |
| Zamrznuti paket | ID/verzija paketa, spisak tačno 16 EV ID-jeva, verzija i digest svakog ulaza, početnog stanja i očekivanja, kriterijumi ocene, pravilo za ponavljanje i verzije relevantnih izvora. |
| Izvršni slučaj | EV ID, dozvoljeni režim, javni koraci i parametri, ulazne reference, seed početnog stanja i kontrolisana greška gde je predviđena. Podaci za ocenu su odvojeno skladišteni. |
| Očekivanje | EV ID, verifikabilne činjenice, prihvatljivi ishodi, obavezni kontrolni signali, postupak ocene i dokazi za neuspeh. Pristupa mu offline ocenjivač posle snimanja rezultata. |
| Zapis izvršavanja | EV ID, faza `baseline` ili `final`, commit, verzija paketa i digest ulaza, režim, stvarni ishod, status, trag, binding, verzije korpusa/modela/konfiguracije, broj zahteva i eventualna nepoznata potrošnja. |
| Ciljana izmena | Početni trag i EV ID, hipoteza o uzroku, tačna promena, commit ili diff, očekivani uticaj i rezultat ponovljene provere. |
| Predaja | Završni commit/tag, uputstvo i stvarni zapis reprodukcije drugog člana, tri scenarija za demo, osam CAP stavki i četiri potvrđena zapisa doprinosa. |

Dozvoljeni statusi rezultata su `pass`, `fail`, `blocked` i `not_run`.
Jedna ispravka ili ponavljanje unutar dozvoljenog workflow-a ostaje deo jednog
primarnog ishoda. Svaki dodatni pokušaj ima svoj trag i razlog. Pri agregiranju
svaka faza ima 16 mesta. Blokiran ili neizvršen red ima razlog i ne ispunjava
uslov stvarno izvršenog merenja.

Čuvati sirove rezultate, lokalne store-ove i druge generisane artefakte u
ignorisanim putanjama. U predaju uključiti pročišćene sažetke, bezbedne tragove i
identitete artefakata koji omogućavaju proveru rezultata. Tajni ključevi,
train/test labele i offline očekivanja se ne šalju u izvršni kontekst.
