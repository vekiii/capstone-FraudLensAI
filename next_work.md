# Current handoff — Feature 004 Phase 4 complete, 2026-11-19

T001–T014 are checked in their actual scopes. Phase 4 added the risk score threshold
and whole-minute budget per review window to Simulation & Evaluation. Editing a
setting immediately clears results. Obsolete successes and failures are ignored
after edits, scenario changes, resubmission and navigation. Each strategy shows
threshold and backlog misses and the counts of unknown outcomes.

T012 API regressions passed before implementation. T013 produced 21 expected RED
failures and all 30 focused frontend tests passed after T014. Final verification
passed 405 backend tests, 181 frontend tests, Ruff, typecheck, production build
and `git diff --check`. The local Chrome retry passed 11 grouped checks, including
budget 2→4, threshold editing, zero budget, invalid minutes and Cases navigation.
[US2 evidence](evidence/tasks/feature-004-us2.md) ·
[Chrome results](evidence/tasks/feature-004-us2-browser-results.json) ·
[Prior US1 evidence](evidence/tasks/feature-004-us1.md)

Human review and teammate reproduction are pending. The next separately scoped
step is T015, API regressions for the exact recipe round trip and a label-only
scenario variant. The walkthrough with recipe reopen is pending that phase.
