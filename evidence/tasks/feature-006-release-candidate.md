# Feature 06 · T016 · Završna revizija za merenje

22. novembar 2026, Europe/Belgrade. Iz čistog stabla grane
`006-capstone-evaluation` kandidat je vezan na
`d8acc2a335d95e2402f586006925949f4d9f7739`.
Baseline je `5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`.
T016 validacija i odobrenje zabeleženi su pre prvog finalnog poziva.

| Pin | SHA-256 ili vrednost |
| --- | --- |
| Manifest `capstone-ev-v1` | `7bc9b5b0ca296c27f184cd7883f55b4a53c5b2a6e9eecaa0ba1020b5f16fda8f` |
| Javni ulazi | `7a52db065205cb3721596c6f6452d991948a6f42c5b28d23989b217c8162ba26` |
| Offline očekivanja | `57a84eb527a694eb33e2b312438f94a582741a225d42f30ea322d6950ed85953` |
| Finalni lokalni freeze | `d265e7dbae2dff23276c9fbc04591c5d5215b7c0bb8bb9f13b0b45df2594a5c3` |
| Model i profil | `gpt-6-luna`, semantic v8, report v6, grupisani alati, strict sections, reasoning `low` |
| Budžet | 21 zahteva preostao od 38 pošto je baseline potvrdio 17. Za final je vezan plafon od 19. |

`git diff --exit-code <baseline> <final> -- evals/capstone uv.lock web/package-lock.json`
vratio je exit 0. Ponovo su provereni digesti T098 i korpusa, seed i javni
digest svakog EV reda i identitet objavljenog EV-10 odlomka. Lokalni
`evals/results/capstone/final/freeze.json` sadrži ovaj SHA i hash-eve
fajlova koje izvršavanje koristi. Odobrenje je vezano za njegov digest.

Izmene između ta dva SHA-a su transportna deduplikacija istorijskih
događaja u adapteru, njena instrukcija u report promptu, ciljane regresione
provere i baseline evidence i task/handoff zapisi. Konačni report prompt
ima sopstveni digest u tragu. [T015](feature-006-targeted-change.md) ·
[Manifest](../../evals/capstone/manifest.json).
