# Current status - T052 reviewed and frozen, 2026-11-15

Vedran explicitly approved the remaining 12 scenario cards. Full bound approval
and freeze are in reference/review-record.json and protocol.json. Structural
checker now validates both proposed and genuinely approved/frozen states.
T052 is complete; no live reports, safety execution or T053+ work is implied.
Earlier proposed/partial status below is historical.

# Proposed investigation evaluation pack — T052

Prepared 2026-11-15 by Codex (AI coding agent). **Proposed, partially reviewed
by Vedran, not frozen. T052 remains incomplete.** Vedran explicitly approves
retrieval expectations/no-answer, safety design, rubric/splits/protocol and
overall/per-language reporting. See reference/review-record.json partial_review.
The 12 investigation scenarios/history and whole-pack freeze remain pending;
[readable review cards](../../evidence/tasks/feature-003-t052-scenario-review.md)
replace reading repeated raw JSON wrappers. Earlier corpus review remains
distinct from review of evaluation expectations. Actual live-report reviewer
assignments may remain unassigned until people accept; no names are invented.

| Artifact | Contents | Consumer |
|---|---|---|
| [inputs/retrieval.json](inputs/retrieval.json) | 30 Serbian/English questions | Selected input only to future search harness |
| [inputs/investigation.json](inputs/investigation.json) | 12 materialized synthetic contexts, scoped history fixtures and queries | Selected input only to future generation harness |
| [inputs/safety.json](inputs/safety.json) | 12 adversarial scenario stimuli | Isolated safety harness only |
| [reference/](reference/) | Passage judgments, essential facts/missingness, rubric, canaries, origins and empty review record | Trusted offline reviewer/joiner only |
| [splits.json](splits.json) | 10/20 questions, 4/8 cases, five second ratings and five ordinary demos preselected | Trusted orchestrator, never provider input |
| [protocol.json](protocol.json) | Provisional hashes, selection rules, denominators, limits and open gates | Trusted offline verifier/orchestrator |

There are 2 development and 4 held-out no-answer questions. Held-out primary
reports precede the five ordinary demo attempts, some of which reuse scenario
inputs; demo attempts cannot replace primary outcomes. Rubric requires one human
to rate all eight and a different teammate to rate the five preselected cases.
Neither role has been assigned to an actual person.

References come from the retained, reviewed corpus text and supplied synthetic
fixture/producer-contract context, never generated reports or provider scripts.
Dataset-shaped scenarios are authored contract examples, **not actual producer
integration**. Current runtime resolves only its existing fixtures. A future T054
input harness must consume these exact materialized snapshots/history, not resolve
the repeated fixture case ID to a different snapshot. Dataset outbound projection
remains unavailable. This pack introduces no new HTTP/tool/runtime contract.

Private means evaluation-only: files remain visible to repository readers; no OS
access control or blind authoring is claimed. Codex saw all questions/answers while
authoring and checking. The next tuner must use development only and exclude
held-out expectations from its context. If held-out content influences tuning,
retire those cases and version fresh held-out data; never call that an independent
test. Only explicitly selected authorized input projections can later leave the
backend. Never pass entire protocol, split, reference or safety files to a provider.

The corpus loader accepts only manifest document paths under its reviewed document
root. No evaluation files are placed there. Reference joining must be a separate
offline stage after predictions/reports and their hashes are saved. The T054
generation/join implementation and T053 leakage/metric tests are not built here.
Static canary absence is not proof of all-turn runtime privacy.

To repeat **structural checks only** from the repository root:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
.venv/Scripts/python.exe evidence/tasks/feature-003-evaluation-pack-check.py
```

This validates counts, splits, references, source/passage/context identities and
hashes, exact essential facts, independent history arithmetic and private-canary
separation. It stages sources without publishing and checks an existing local
archive read-only. It has guards against environment-file reads, network and
subprocess calls; it imports no provider/settings and runs no search or evaluation.
Generated outputs later belong under ignored `evals/results/feature-003/`.

For the actual reviewer checklist, commands, observed failures and remaining gates,
see [T052 evidence](../../evidence/tasks/feature-003-evaluation-protocol.md).
No tuning, held-out execution, provider access, safety execution or human approval
is inferred from this package or a successful integrity check.
