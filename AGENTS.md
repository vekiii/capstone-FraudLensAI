# FraudLens AI contributor instructions

## Mandatory start of every task
Before planning, generating prompts, reviewing or implementing any project work,
MUST read the current root [next_work.md](next_work.md), after applicable AGENTS.md
instructions. Repeat this at the start of each new task or resumed session; do not
rely only on previous chat context. Read-only requests must read it too, without
updating it. If it is missing or unreadable, report that fact and use the requested
feature's tasks/evidence to establish context; do not invent the missing handoff.
The user's current request determines scope; next_work.md does not authorize
unrequested implementation. Verify its progress claims against relevant evidence.

## Scope and authority
Use [.specify/memory/constitution.md](.specify/memory/constitution.md) as the shared
governance source and [original_idea.md](original_idea.md) for the approved product
context. Implement the selected feature's specification, plan and tasks within the
agreed MVP and Bootcamp modules 1–9.

Out-of-course additions require explicit team approval before implementation;
record the proposal, benefit, schedule impact and actual decision in the relevant
feature or decision record. Routine decisions within approved work need no renewed
approval. Do not silently widen contracts or weaken requirements to pass checks.

The foundation uses FastAPI and vanilla TypeScript/Vite with local synthetic data.
ML training, RAG, LLM integration, real datasets and later product features belong
to subsequent specifications. GNNs, transformer training, multi-agent product
orchestration, open-web investigation and graph databases need team scope approval.
Human analysts retain final decisions; no automatic account interventions or
regulatory submissions are included in the MVP.

## Development and verification
Follow Specify → Plan → Tasks → Implement → Converge, with clarification and review
as needed. Read the selected feature artifacts before implementing behavior.
For Spec-kit commands explicitly select the feature in the PowerShell session:
`$env:SPECIFY_FEATURE_DIRECTORY = 'specs/001-project-foundation'`.
This selects feature files, without changing the Git branch.

Use RED → GREEN → REFACTOR for critical business behavior, including negative,
contract and relevant regression checks. RED must fail for the intended missing
behavior. Mechanical setup needs no artificial failing tests. Run actual checks
before claiming completion; distinguish no tests, not run, failure and success.
Do not change checklist markers to bypass review gates.

Preserve existing work and shared .agents/.specify content. Use generated lockfiles
and locked installs after initial resolution. Keep secrets, sensitive data and
machine-local/generated files out of Git. Record original development prompts,
versions, commands, observed results, limitations and pending human review using
the prompts/ and evidence/ conventions. Synthetic fixture checks are not model
evaluation, and one contributor's setup is not second-person reproduction.

After each implementation unit or partial-work handoff, update next_work.md with
actual progress, evidence links, blockers/unrun checks and one concrete next step.
Keep detailed execution history in evidence/. Prompt-generation-only requests remain
read-only and do not update progress files. Git commit/push is not automatic.

Keep deterministic calculations and validation in code; LLMs must not invent facts
or permissions. Keep evaluation labels and holdout answers outside prediction and
retrieval inputs. Use explicit contracts and replaceable boundaries so fixture
work can proceed without a trained model or provider access.
