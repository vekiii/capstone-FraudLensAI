# T065 boosted sample: source and prior-history fact checks

**Checked:** 2026-11-15 by Codex on Isidora's local checkout. **Scope:** the five boosted full-run examples in [the T065 handoff](feature-002-explanation-review.md#boosted-full-run-sample--2026-11-14). This completes the requested preparation of source/history facts. It is not the independent full explanation review required to close T065.

## Provenance and procedure

- The local IBM v8 source `data/raw/HI-Small_Trans.csv` hashes to `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`; the mapping hashes to `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`. Both match the [pinned reproduction values](feature-002-peer-reproduction.md). The rebuilt dataset version is `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`; the import reports complete with 5,078,345 source and valid operational rows and zero rejected rows. Its stored time-policy hash is `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781`, matching the pinned value.
- Environment: Windows PowerShell, Python 3.14.10, Python SQLite 3.53.1. The database `data/processed/feature-002-ibm-v8-t065-work.sqlite` and output `data/processed/t065-db-check.json` are ignored local files. This is a newly imported local database, not Elena's original work store. No `history-v1` feature snapshot build or model scoring was performed.
- The transaction IDs were independently derived from the repository's source-identity rule and CSV ordinals. The five source ordinals were 578,886; 2,172,425; 3,635,831; 3,951,325; and 4,862,879, respectively in CSV order. A separate complete CSV pass and the read-only SQLite query agreed on the five records and history totals.
- Prior history uses the sender bank and account, event time in `[t-24h,t)`, and the current event's **paid currency**. Sums use `Decimal` on paid amounts. Same-time events and events in other currencies do not enter the same-currency sum. The checker reads `operational_events`; it does not read private labels.

Commands run from the repository root:

```powershell
Get-FileHash data/raw/HI-Small_Trans.csv -Algorithm SHA256
Get-FileHash data/mappings/ibm_hi_small_v1.json -Algorithm SHA256
$env:PYTHONPATH='backend/src'
.\.venv\Scripts\python.exe -m fraudlens.pipeline_cli import --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json --namespace kaggle:ealtman2019/ibm-transactions-for-anti-money-laundering-aml:v8 --expected-sha256 b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040 --store data/processed/feature-002-ibm-v8-t065-work.sqlite
.\.venv\Scripts\python.exe evidence/tasks/feature-002-t065-csv-cross-check.py
.\.venv\Scripts\python.exe evidence/tasks/feature-002-t065-fact-check.py --store data/processed/feature-002-ibm-v8-t065-work.sqlite > data/processed/t065-db-check.json
```

PowerShell wrote the redirected JSON as UTF-16; it was parsed as such for the comparison. The ignored output contains no private labels or account identifiers. Neither helper creates a score or an explanation.

## Findings in handoff order

| Transaction / case | Source ordinal; UTC event | Verified operational facts | Prior sender events, all currencies / same paid currency; same-currency paid sum | Match to handoff facts and history |
|---|---|---|---|---|
| `D90fbf75213cb7bb1bdc1f3f91ec23dd5` / `C737e48e2a489a7f10bf7a71716e3bc65` | 3,635,831; 2022-09-09 02:51 | ACH; 48,014.36 Yuan paid and received | 8 / 0; 0 Yuan | **PASS** for the stated source facts. The handoff did not state a history sum for this row; zero is an additional observed fact. |
| `D0adebff88899bbb3c98e9fb03b785df6` / `C0281c8396bb2a961e95f1b80ebeee0f7` | 578,886; 2022-09-05 07:40 | ACH; 51,805.35 Yuan paid and received | 7 / 0; 0 Yuan | **PASS** for the stated source facts and zero same-currency 24h sum. |
| `D6e00944c45c3f8307e5d65ef03edfd8d` / `C1b84af5218d0786128963eac213a69e9` | 2,172,425; 2022-09-06 19:44 | ACH; 89,709,263.78 Swiss Franc paid and received, with no unit conversion in the source or check | 11 / 0; 0 Swiss Franc | **PASS** for the stated source facts, original currency/amount and zero same-currency 24h sum. |
| `D9dc186ae55ba66066b6781023bac7170` / `C906476436b96bd9e4646d10a6d09dc70` | 3,951,325; 2022-09-09 13:15 | ACH; 51,424.51 Yuan paid and received | 5 / 0; 0 Yuan | **PASS** for the stated source facts and zero same-currency 24h sum. |
| `D26d712161d5bfa0d06da08cccaf5498b` / `C16b89849cf52390a3827f72899b40ca1` | 4,862,879; 2022-09-09 23:36 | ACH; 17,312.17 Euro paid and received | 22 / 0; 0 Euro | **PASS** for the stated source facts and zero same-currency 24h sum. |

All five source fact comparisons returned true in the SQLite checker; its history counts and sums matched the independent CSV pass. No source/history discrepancy with the handoff was found. **Zero same-currency prior sum does not mean zero sender activity:** all five senders had prior transactions in other currencies. Any explanation phrasing that suggests no prior activity would be misleading, but the rounded handoff itself states the narrower same-currency measure.

## Open verification boundary

The local check did not build or compare frozen `history-v1` snapshots and their digests. The original `evals/results/boosted-full-five-explanations.json` (pinned SHA-256 `7d50bec8aba0b4e36c58a1a696de27ae4869fe650ba653618f04f35a9227a54f`), Elena's saved boosted artifact, and the original run output are still absent. Therefore the displayed scores, model/run identity, explanation method and scale, full-precision contributions, negative remainder in row five, and 1e-8 reconstruction remain **UNVERIFIED**. The source/history PASS findings do not make the explanations PASS and do not close T065. Obtain the authorized original JSON and artifact, verify their hashes, then finish the independent five-explanation review. T066 was not attempted here.
