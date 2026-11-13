# Foundation development instruction index

Created: 2026-11-12 for T023 (FR-008/010). This index links development instructions
and their records. Originals and author-requested editorial revisions are identified
explicitly; edited text must not be presented as a verbatim original.
The instruction authorizes work; evidence records what actually happened.
Historical prompts may describe then-pending work; current task status is in
[`tasks.md`](../../specs/001-project-foundation/tasks.md) and
[`next_work.md`](../../next_work.md).

## Development instructions and continuation

| Work | Development instruction / record | Execution / handoff |
|---|---|---|
| Phase 1, T001–T005 | [phase 01](001-foundation-phase-01.md) | [phase 01 handoff](../../evidence/tasks/phase-01-handoff.md) |
| Phase 2, T006–T007 | [phase 02](001-foundation-phase-02.md) | [contract evidence](../../evidence/tasks/T006.md), [phase 02 handoff](../../evidence/tasks/phase-02-handoff.md) |
| Phase 3, T008–T011 | [phase 03](001-foundation-phase-03.md) | [startup evidence](../../evidence/tasks/T008.md), [setup checks](../../evidence/tasks/T011.md), [phase 03 handoff](../../evidence/tasks/phase-03-handoff.md) |
| Phase 4, T012 | [backend RED request](001-foundation-T012.md) | [T012 evidence](../../evidence/tasks/T012.md) |
| Phase 4, T013 | [frontend RED request](001-foundation-T013.md) | [T013 evidence](../../evidence/tasks/T013.md) |
| Phase 4, T014 | [fixture request](001-foundation-T014.md) | [T014 evidence](../../evidence/tasks/T014.md) |
| Phase 4, T015 | [scorer request](001-foundation-T015.md) | [T015 evidence](../../evidence/tasks/T015.md) |
| Phase 4, T016 | [API request](001-foundation-T016.md) | [T016 evidence](../../evidence/tasks/T016.md) |
| Phase 4, T017 | [frontend API request](001-foundation-T017.md) | [T017 evidence](../../evidence/tasks/T017.md) |
| Phase 4, T018 | [UI request](001-foundation-T018.md) | [T018 evidence](../../evidence/tasks/T018.md) |
| Phase 4, T019 | [integrated verification request](001-foundation-T019.md) | [T019 history and final browser continuation](../../evidence/tasks/T019.md) |
| T019 continuation | [original browser continuation request](001-foundation-T019-browser-continuation.md) | [final browser results](../../evidence/tasks/T019-browser-results.json) |
| Phase 5, T020–T023 | [phase 05 instruction — author-edited record](001-foundation-phase-05.md) | [T020/T021 boundary evidence](../../evidence/tasks/T020.md), [phase 05 handoff](../../evidence/tasks/phase-05-handoff.md) |

Phase 4 originals are preserved per task; no phase-wide original is invented.
The phase 5 request was initially recorded before implementation. On 2026-11-12,
the author requested that its conversational wording be replaced with structured
instructions in the format of earlier phases. That file is now explicitly marked
as an edited record; its task scope and the user's ownership of commit/push remain
unchanged. It is not a verbatim transcript or a newly issued implementation request.

## Amendments and evidence policy

Keep each original intact. Record later user changes as clearly dated amendments
in its source record or a separately linked continuation, preserving Git history.
This index links changes; it must not replace earlier wording with a retrospective
summary claimed to be original. No original records predating T023 were edited
when creating this index, and no secret redactions were needed for phase 5.

The existing [prompt conventions](../README.md) and
[evidence conventions](../../evidence/README.md) were reviewed for T023:

- Development instructions live here in prompts/development/.
- Versioned runtime prompts belong in prompts/app/ when an application actually
  uses them. Foundation has no runtime LLM prompt; no empty directory is needed.
- Commands, versions, real outcomes, missing checks and review status belong in
  evidence/, not in a development instruction presented as proof of execution.
- Fixture tests verify deterministic application contracts/behavior; model
  evaluations additionally need data/split/model versions and leakage controls.
- Human review and second-person reproduction stay pending until actually done.
  Agent execution does not establish peer review or SC-001 by itself.

The evidence policy already states these distinctions and required no amendment
for T023. Task-level RED/GREEN or already-correct outcomes remain in their own
evidence files. Phase 6/T024–T027 instructions and evidence are not invented here.

## Phase 6 (2026-11-12)
Original instruction: [001-foundation-phase-06.md](001-foundation-phase-06.md).
User confirmed no peer result and requested reproduction steps.
