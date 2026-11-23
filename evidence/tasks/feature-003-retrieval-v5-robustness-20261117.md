# V5 robustness audit - NOT READY FOR ACCEPTANCE

User requested checking whether new retrieval solutions overfit. Read current
handoff and implementation; no runtime/config/threshold modifications, merge,
provider calls or proposed acceptance-pack use. Runtime SHA and raw rows:
feature-003-retrieval-v5-robustness-20261117.json.

Predeclared24 challenge queries before execution:12 answerable paraphrases across
the six documents,12 corpus-unanswerable questions about exact customer facts,
legal quantities and specific filing events. Agent-authored proposed document
references, NOT independent human gold review. Input-only search calls, predictions
materialized before reference join. Separate ignored store, same corpus/configs;
runtime source hash before/after equal. No retuning after seeing failures.

| Configuration | Recall@5 (12 answerable) | MRR@5 | No-match on12 no-answer |
|---|---:|---:|---:|
| Demo BM25 cutoff.5 |.9167|.8194|0/12|
| V3 selected baseline cutoff8.863342357405378 |0|0|12/12|
| V5 coverage/inflection cutoff.5 |.5833|.5417|2/12|

V5 misses5/12 relevant answers and retrieves hits for10/12 unanswerable queries.
The returned hit is not itself an LLM-generated false assertion: narrative
abstention/factuality was not measured. Under the declared retrieval no-match
criterion these are false-match failures. Historical and development outcomes
remain untouched; earlier1/1 on4 answerable+2 no-answer does not generalize.

Concrete v5 false matches include exact customer source-of-funds and exact
supporting-document retention-period requests. Related vocabulary retrieves
general procedures which cannot supply these exact facts. Coverage checks lexical
overlap, not whether requested information exists. V3's high cutoff abstains on
every query, including every answerable query; its earlier success is also fragile.

Code audit: no question IDs, answer-table lookups or hardcoded document routing.
However v5 was selected after inspecting exposed development failures; a four-row
positive denominator and heuristic suffix/coverage rules create selection-overfit
risk. Stemming is incomplete (filing->fil versus file, sharing->shar versus share),
and semantic paraphrases without shared vocabulary remain difficult. Unit/regression
success does not establish retrieval generalization. Small corpus and query-family
overlap limit the audit; no formal proof of statistical overfitting or independent
held-out acceptance is claimed.

Conclusion: meaningful generalization failure observed; do NOT promote v5 or close
T095 on earlier perfect development score. These challenge queries are now exposed
diagnostics, not an untouched final test. Review negative-query semantics/reference
completeness, define a separately versioned next design and maintain genuinely
separate reviewed acceptance data. No code fix in this review-only request.
