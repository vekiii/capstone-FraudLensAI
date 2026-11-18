# Report v6 development review, 2026-11-18

The user authorized one new staged cycle with up to 153 new requests and a total
ceiling of 303, starting at 150. The development cap was 32. Four fresh authored
fixtures and source obligations were saved before dispatch. The frozen settings
selected report v6, semantic v8, 8192 generator output tokens, 45-second drafting,
30-second selection and 120-second overall deadline. Source and approval hashes
verified after execution. Existing API, worker and HTTP observer were used.

| Case | Outcome | Seconds | Codex review |
|---|---|---:|---|
| DEV6B-01 | ready_for_review | 35.665 | Source facts and guidance supported. Both timelines reproduce the exclusive 09:38:00Z boundary. |
| DEV6B-02 | needs_information | 31.002 | Both histories correctly described as unknown, with no inferred period or totals. Human authority retained. |
| DEV6B-03 | failed | 59.908 | Draft request timed out and remained unknown. The worker tried a retry, which the ledger blocked before another send. |
| DEV6B-04 | not_run | | The observer stopped the batch on the unknown dispatch. |

Codex reviewed both available drafts against the evidence and all seven source
obligations per case. Both were locally valid, with qualitative source review
recorded per row. No numeric semantic scores were assigned. Development failed
the required four valid reports. Retrieval and final evaluation were gated on
that result and did not start. T101 and T102 remain open.

18 new dispatch intents, 17 HTTP 200 and one unknown, counted as 168 of 303 total.
Known usage was 64,428 tokens plus the unknown request. 15 recorded generator
requests used the 8192 ceiling and three selectors used 2048. Completed responses
showed no output-token-limit truncation. Unknown response contents remain unknown.
No changes to defaults, old observations or prior results. Raw artifacts are in
ignored `evals/results/feature-003/report-v6-cycle-20261118/development/`.
[Machine record](feature-003-report-v6-development-20261118-results.json).
