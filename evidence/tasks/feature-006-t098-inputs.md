# T002 — T098 integritet i kompatibilnost, 21. novembar 2026.

**T002 ostaje otvoren.** Paket je identičan manifestu, ali predati indeks
postojeći reader odbija na ovom checkout-u.

Grana `006-capstone-evaluation`, početni HEAD
`055fc06561f8b3d45d1a96e4db15a5ba682deefe`, početno radno stablo čisto.
Radni direktorijum `D:\AIBootcamp\capstone`, vremenska zona Europe/Belgrade.
[Originalni zahtev](../../prompts/development/006-capstone-phase-02.md).

Autoritativni manifest pročitan je komandom
`git show feature03:evidence/tasks/feature-003-t098-transfer-20261118.json`,
iz lokalnog `feature03` na `62f099134c57a3129d28f333545a1398f6e812e4`.
Sva tri fajla su pod `data/processed/feature-003-t098-20261118`.

| Fajl | Bajtova | SHA-256 pre i posle čitanja, odgovara manifestu |
|---|---:|---|
| model-bounded.sqlite | 131072 | `13cde42167cac02f257748633034a9461aa00648f6737ade813779845882d384` |
| source.sqlite | 12443103232 | `125895e52cd7ce72fc1c4328ea758d3af23014dc8eb5df9d6a190e275e55ac47` |
| history-index.sqlite | 1622720512 | `8745ec13848f5ce0f76417fd0c2f7c731a2189cb634034aea5eeaa3a205c5a9f` |

Početni digest izračunat je pomoću `hashlib.file_digest`, a završni pomoću
`Get-FileHash` nad sva tri fajla. Python provere izvršene su iz korena kroz
`.venv/Scripts/python.exe -` uz `PYTHONPATH=backend/src`, exit 0. Direktne
SQLite provere koristile su URI `mode=ro&immutable=1` za aktivnu dataset
reviziju i red `history_source`. Postojeći Cases i investigation reader-i
otvarali su store-ove u read-only režimu. Privatne labele i EV reference
nisu čitane.

- `RunStore(read_only=True).active_metadata('model')`, koji bira samo aktivan
  kompletan run, vratio je `run_boosted_candidate_smoke` sa 20 alert-a.
  Aktivni source dataset je kompletan i ima isti ID
  `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`.
- `RunStore.detail_active('model', run, case)` i `CaseDetailV2.model_validate`
  potvrdili su oba propisana slučaja. Zabeleženi provenansi su `model`,
  `uncalibrated_probability_estimate` i `model-history-v1-boosted-candidate`.

| Case | Transaction | Sačuvan skor |
|---|---|---:|
| C6c481448f7d25af15beea1309f44ee58 | D4e050598f0f526f6fe690bb4874e2ee5 | 0.9944662676905943 |
| C4af2f03a9d1bca5fc14d76e05af12140 | Dcc88ddb85039576f141172f225b63a35 | 0.9949877910390978 |

Indeks ima verziju 1, status `complete`, 5.078.345 redova, isti dataset ID i
isti source digest. Ipak, `HistoryIndex` zahteva i istu apsolutnu putanju i
potpis `[size, mtime_ns]`. Sačuvana putanja pripada izvornom checkout-u.
Sačuvani mtime je 1794976711684811600, lokalni 1794976711000000000.
`DatasetReader(..., history_index=idx, history_index_sha256=...)` uz poziv
`resolve(case, run)` vraća `stale_snapshot` za oba slučaja.

Za dijagnozu je i postojeći `DatasetReader` bez opcionalnog indeksa pročitao
iste pinned slučajeve. Njegov `source_payload` jednak je celom Cases payload-u
za oba, uključujući case/transaction/run/dataset identitete i skor.
Istorija je u toj probi bila `unavailable`. Ovo je dijagnoza kompatibilnosti
skora, a predati indeks i dalje mora proći redovnu proveru. Nalaz ne potvrđuje
EV-08. Sledeći preduslov je kompatibilan indeks od vlasnika artefakta za ovaj
source i checkout ili zasebno odobrena izmena ugovora o prenosivosti indeksa.
