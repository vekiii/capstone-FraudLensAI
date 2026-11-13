# Original development request — IBM pretrained candidate correction

Date: 2026-11-13. Branch: `model-implementations`.

The user instructed the team to keep IBM HI-Small unchanged, replace the incompatible ApexFi IEEE-CIS candidate with `naazimsnh02/fraudsentinel-tier1-scorers` for review, and inspect only its AML LightGBM model, preprocessing, metrics and two reference scripts. The request calls for verifying source revision, artifact availability, IBM target and 22-feature schema; investigating graph-state, bank-qualified identity, point-in-time history, test-label threshold selection, training-row overlap and joblib security; retaining Kluey XGBoost only as an alternative; recording any training-to-inference scope change as pending actual team approval; updating evidence, handoff and source-decision documentation; committing documentation only; and reporting Prompt 04C as the next action. It forbids training, IBM data modification, inference, `joblib.load`, fixture/rules changes, false completion of T026–T036, and pushing.

The user's full prompt in this conversation is authoritative; this is a faithful summary, not a new approval or expanded scope.
