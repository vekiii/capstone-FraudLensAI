# Synthetic input versus model prediction: local correction

Date: 2026-11-23. Scope: local prompt correction and offline regression only. Original LIVE outcomes remain in [the LIVE record](002-003-local-contributions-live-demo-2026-11-23.md).

## Trace and cause

The first LIVE report for `row:2959955` said “nije stvarna ML predikcija.” Its saved attempt audit contains the active v6 prompt's blanket instruction `sintetički fixture nije stvaran klijent niti ML predikcija`; the saved context says `source_mode=dataset` and `assessment.score_source=model`. The same prompt later instructs the model to call a model-source score a model score. This internal contradiction is a direct plausible source of the report wording; the audit proves the bad instruction reached the attempt, while it cannot prove the LLM's internal causal path.

The dataset outbound context and case evidence identify a synthetic benchmark, preserve `assessment.score_source=model`, and do not deny ML inference. With the sidecar enabled, the case notice describes separately verified log-odds contributions. The initial fixture-only limitation in `tools.py` is replaced for dataset cases before evidence creation. Fixture outbound context correctly says `no ML inference`. The knowledge guide describes synthetic generated transactions and limits legal conclusions, without denying inference; the first attempt returned no applicable procedure passage. The provider projection retains the exact assessment fields and evidence facts. Therefore the smallest supported correction is to the active v6 prompt, leaving context, notices, procedure corpus and projection unchanged.

## Change and checks

`prompts/application/investigation-v6.md` now says synthetic inputs are not real clients; `assessment.score_source=model` is a real model prediction on those inputs; the LLM report describes that prediction and does not compute a new score. Fixture/rules scores remain explicitly distinct. It also uses the actual dataset `assessment.score_source` or fixture `assessment.source` field. Prompt SHA-256 after correction: `ddaf4c1128f2b50170f54de4d0f0532715cd412bd69ef2d9e2f854e2810afd1a`. New attempts will pin this changed prompt; old attempts retain their saved text/digest.

RED: `PYTHONPATH=backend/src .venv/bin/pytest -q backend/tests/unit/test_investigation_synthetic_model_wording.py` produced one intended failure for the blanket instruction and one test-design failure: the fixture test initially assumed `score_source`, then was corrected to the actual `source` field. GREEN: `PYTHONPATH=backend/src .venv/bin/pytest -q backend/tests/unit/test_investigation_synthetic_model_wording.py backend/tests/integration/test_investigation_dataset_adapter.py backend/tests/integration/test_local_contribution_flow.py` passed **40/40** (one Starlette deprecation warning). The integration assertion checks a model dataset's outbound assessment, synthetic notice, absence of the fixture-only no-inference phrase, and provider conversation projection. Fixture projection still says no inference. `git diff --check` passed.

`PYTHONPATH=backend/src .venv/bin/python evidence/tasks/probe_65_local_contributions.py` passed **65/65** exact published score/status parity, reading no labels: max raw reconstruction error `1.199040866595169e-13`, group-sum error `1.7763568394002505e-15`, probability reconstruction error `1.1102230246251565e-16`. No model, preprocessing, threshold, bridge, sidecar or identity code changed.

The ignored LIVE store SHA-256 before and after was `bbff7e4fdc80e0daadc696fbac0af05c18979ca51010cc69d6b14925325a60fd`. Read-only SQLite check: first attempt `att_f7200f39136640a2ac910567f3434514` remains `ready_for_review`, one report, four dispatches, zero reviews; second `att_6b027f6515ba4b68abf3ebdcb5c0427d` remains `reviewed`, one report, four dispatches, one test review. Both saved audits still contain the old instruction. Neither report was rewritten; the first is still **not passed**.

The report validator checks structure, exact assertions, citation integrity and required limitation presence; it expressly leaves semantic truth to human review. A phrase detector would miss paraphrases and risk rejecting true fixture statements, so no production semantic validator was added. The prompt/projection tests guard inputs, not LLM behavior. No provider calls or new attempts occurred.

## Next limited LIVE measurement plan (not executed)

After separate authorization, use a new ignored investigation store and the same pinned model/bridge/sidecar, provider profile and 48,000-byte cap. Pin the new prompt digest, run at most the newly authorized cases in specified order, capture exact serialized request bytes and returned model/usage, then review report wording and citations against evidence. Keep both original attempts immutable and report the new result separately. Feature 003 owner still needs to review the unapproved sidecar contract and report semantics before Draft PR.
