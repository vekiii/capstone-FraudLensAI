# Feature 06 · T022 · CAP-08 doprinosi

**Status: delimičan.** Kandidat `d8acc2a335d95e2402f586006925949f4d9f7739`.
Ispod su predlozi izvedeni iz Git istorije i postojećih provera. Nema
pojedinačnih CAP-08 potvrda za ovu predaju. Raniji kolektivni pregled iz
[evidencije osnove](human-review.md) i Milanov pregled EV-10 iz
[T012](feature-006-phase-04-freeze.md) pokrivaju svoje tadašnje opsege.
Vedran je 22. novembra 2026. naveo da će potvrde biti dostavljene kasnije.

| Član | Tehnički doprinos i veza sa tokom | Odluka i stvarna tehnička provera | Pregled rada kolege i potvrda |
| --- | --- | --- | --- |
| Vedran Mitic (Git `Veki`, povezivanje prema [istorijskom zapisu](project-evidence-plan-2026-11-12.md)) | Priprema i provera kompatibilnog T098 izvora za isti skor u Cases i investigation-u. `b61916a13add61e703f055440dae0027bc6059f0` je predak kandidata. | Izgraditi lokalni indeks iz hash-vezanog source-a. Proverena jednakost celog payload-a za oba slučaja i 5.078.345 redova indeksa. [T002](feature-006-t098-inputs.md). | Konkretan primer i pojedinačna potvrda čekaju. |
| Milan (Git `milangavric2003`) | Ciljana izmena OpenAI transporta grupisane dataset istrage u samom kandidatu. | Izostaviti duple stavke istorije kad iste vrednosti postoje u punom JSON tekstu. Ciljane RED/GREEN provere i 66 regresionih prolaza; EV-01 finalni zahtev 40.006 bajtova. [T015](feature-006-targeted-change.md). | [T012](feature-006-phase-04-freeze.md) beleži njegov stvarni pregled tačnog EV-10 reda. Autor pregledanog rada i potvrda da je to relevantan primer pregleda kolege čekaju. |
| Isidora Popovic | Konsolidacija Cases i dashboard-a u postojećem React/TypeScript `web/` i dodavanje same-origin Vite proxy-ja. `3da25106b86c69210c0ac44c134cd78ed56e488e` je predak kandidata. | Zadržati jednu aplikaciju sa premeštenim typed dekoderima; izvršeno 163 web testova, typecheck, build i 60 fokusiranih backend testova. Kandidat koristi ovaj React Cases ulaz. [Migracija](typescript-first-web-app-migration-2026-11-17.md). | Konkretan primer i pojedinačna potvrda čekaju. |
| Elena Kalajdžić | Boosted scorer i dataset score provenance koju koristi Cases pre investigation-a. `2099c7e50beb28e69c2e815154ab4233cd975487` je predak kandidata. | Kandidat sa 11 zamrznutih ulaza i objašnjenjem `boosted_sequential_probability`; raniji izolovani API/browser nalaz potvrdio objavljeni skor i poreklo. [Model](feature-002-boosted-validation.md) · [T098 skor u predaji](feature-006-t098-inputs.md). | Konkretan primer i pojedinačna potvrda čekaju. |

## Šta nedostaje od svakog člana

Potvrditi ili ispraviti sopstveni red u tabeli. Uz potvrdu navesti ime ili
alias, datum i jedan konkretan pregled rada kolege. Za primer su dovoljni
ime ili alias kolege, fajl/commit/evidence i šta je zaista provereno ili
koja je primedba data. Ako navedeni tehnički doprinos, odluka ili provera
odstupaju od stvarnog rada, dostaviti ispravku i odgovarajuću referencu.
