# Executed integrated v6 + blind judge bundle - DO NOT REPLAY

User approved44 new model calls, all reserved/consumed with zero retries. Four
calibration calls and20 blind gold annotations PRECEDED20 candidate requests.
Original execution stopped at the10th candidate503. Explicit continuation ran
only10 undispatched IDs with the SAME freeze; failed020 retained as zero.
Partial report was not overwritten. Outputs19 success/1failed, denominator16+4.

Blind judge is a separate stateless context using the same configured model,
NOT independent human/model gold. No candidate result/author labels sent to judge.
Reference differences and all source/quote checks are retained. Do not tune on
these now-exposed questions or treat them as future untouched evaluation data.

manifest.json covers exact executed artifacts with LF hashes. executed-runtime/
holds code snapshots BEFORE later HTTP-audit redaction, raw-failure retention and
worker language-addendum changes. Current semantic core/prompt unchanged; current
infra has offline regressions, not a second live run. Details in evidence/tasks/
feature-003-v6-integration-judge-20261117.md and post-evaluation-lineage JSON.

Offline reproduction, no credentials/network:

    $env:PYTHONPATH = Join-Path $PWD 'backend/src'
    .venv/Scripts/python.exe -m fraudlens.investigation.verify_semantic_evaluation

Both live scripts are EXHAUSTED and their exclusive markers prevent replay.
Any new model experiment requires a new concrete budget/protocol. No merge or
T095 checkbox was performed by recording a passing numeric gate.
