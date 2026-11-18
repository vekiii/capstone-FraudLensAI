# Current handoff - Feature 004 US1 complete, 2026-11-18

T001-T011 checked in their actual scopes. T008-T011 now implemented: exact
label-free replay; closed read-only simulation API; outcome join after selection;
strict client/decoder/default-results view with normal navigation. Cases default
preserved. No remaining intentional RED (replay9/API26/frontend simulation8 GREEN).
Final full backend401 PASS, frontend159 PASS, Ruff/typecheck/build/diff PASS.
Existing Starlette/httpx deprecation warning. Normal local FastAPI/Vite/automated
Chrome walkthrough7 grouped checks PASS; A/B/C,E and exact hand-counted results,
Cases detail/back and404/422. Isolated browser/owned processes cleaned up.

No fixture/outcome/hash/catalog/lock/shared/Cases contract/scorer changes; no
provider/ML/Feature02 adapter/Feature05/agents or Git publication. Human review
and actual teammate reproduction remain pending, not inferred from automation.
Evidence: [US1](evidence/tasks/feature-004-us1.md),
[handoff](evidence/tasks/feature-004-phase-03-handoff.md),
[browser](evidence/tasks/feature-004-us1-browser-results.json).

Next: separately scope Phase4 T012-T014 (capacity/threshold controls and
stale-result extensions). Do not start automatically. Recipe export/reopen and
producer adapter remain later work. Detailed prior RED/history retained in evidence.
