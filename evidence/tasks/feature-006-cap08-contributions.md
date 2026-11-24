# Feature 06 · T022 · CAP-08 doprinosi

**Status: završeno prema izmenjenom US3.** Kandidat
`d8acc2a335d95e2402f586006925949f4d9f7739`. Vedran Mitic je
22. novembra 2026. pregledao i potvrdio sva četiri zapisa u ovom
razgovoru. Zbog angažovanja ostalih članova na drugim zadacima predaja
koristi jednu objedinjenu potvrdu. Pregledalac je Vedran. Postojeći zasebni
pregledi navedeni su u tabeli u svom stvarnom opsegu.
[Dopuna zahteva i potvrda](../../prompts/development/006-capstone-phase-05.md).

| Član | Tehnički doprinos i veza sa tokom | Odluka i stvarna tehnička provera | Dostupan raniji pregled rada kolege |
| --- | --- | --- | --- |
| Vedran Mitic (Git `Veki`, povezivanje prema [istorijskom zapisu](project-evidence-plan-2026-11-12.md)) | Priprema i provera kompatibilnog T098 izvora za isti skor u Cases i investigation-u. `b61916a13add61e703f055440dae0027bc6059f0` je predak kandidata. | Izgraditi lokalni indeks iz hash-vezanog source-a. Proverena jednakost celog payload-a za oba slučaja i 5.078.345 redova indeksa. [T002](feature-006-t098-inputs.md). | Za ovu predaju pregledao i potvrdio sva četiri zapisa. |
| Milan (Git `milangavric2003`) | Ciljana izmena OpenAI transporta grupisane dataset istrage u samom kandidatu. | Izostaviti duple stavke istorije kad iste vrednosti postoje u punom JSON tekstu. Ciljane RED/GREEN provere i 66 regresionih prolaza; EV-01 finalni zahtev 40.006 bajtova. [T015](feature-006-targeted-change.md). | [T012](feature-006-phase-04-freeze.md) beleži njegov pregled tačnog EV-10 reda. Autor pregledanog rada u tom zapisu nije naveden. |
| Isidora Popovic | Konsolidacija Cases i dashboard-a u postojećem React/TypeScript `web/` i dodavanje same-origin Vite proxy-ja. `3da25106b86c69210c0ac44c134cd78ed56e488e` je predak kandidata. | Zadržati jednu aplikaciju sa premeštenim typed dekoderima; izvršeno 163 web testova, typecheck, build i 60 fokusiranih backend testova. Kandidat koristi ovaj React Cases ulaz. [Migracija](https://github.com/vekiii/capstone-FraudLensAI/blob/3eee1d6/evidence/tasks/typescript-first-web-app-migration-2026-11-17.md). | Dokumentovala je proveru preduslova Eleninog boosted scorer-a. CSV, mapiranje i lockfile su odgovarali, a nedostajući artefakti i digest protokola blokirali su stvarnu reprodukciju modela. [Zapis provere](https://github.com/vekiii/capstone-FraudLensAI/blob/3eee1d6/evidence/tasks/feature-002-peer-reproduction.md#peer-reproduction-attempt--blocked-by-unavailable-pinned-inputs--2026-11-15). |
| Elena Kalajdžić | Boosted scorer i dataset score provenance koju koristi Cases pre investigation-a. `2099c7e50beb28e69c2e815154ab4233cd975487` je predak kandidata. | Kandidat sa 11 zamrznutih ulaza i objašnjenjem `boosted_sequential_probability`; raniji izolovani API/browser nalaz potvrdio objavljeni skor i poreklo. [Model](https://github.com/vekiii/capstone-FraudLensAI/blob/3eee1d6/evidence/tasks/feature-002-boosted-validation.md) · [T098 skor u predaji](feature-006-t098-inputs.md). | Zaseban primer nije evidentiran za predaju. |
