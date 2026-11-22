# Human-authority notice correction — 2026-11-16

First committed/pushed completed v6 evaluation as **af8fe4b**, confirmed matching
remote feature03-reliability-v2. Then handled user-authorized T088–T090 locally.
Original request: [prompt](../../prompts/development/003-human-authority-v7-2026-11-16.md).
Design: [human-authority-v7.md](../../specs/003-ai-investigation/human-authority-v7.md).

## Behavior and ownership

New attempts pin application prompt v4 and private
`report_policy=human_authority_notice_v1`. Every draft outcome must include this
exact separate limitations item:

> Konačnu odluku donosi ljudski analitičar; AI nacrt ne izvršava radnje.

The existing local report validator first preserves all schema/fact/evidence/
quotation/citation/limited-source checks, then checks this whole protocol item.
Missing item produces fixed `human_authority_notice_required` repair guidance.
The application allows its existing single repair with tool_choice=none and then
fails output_invalid if still missing. Lower request ceilings still apply. Unknown
policy fails unsupported_capability before any provider dispatch.

No appended boilerplate or rewritten response: the model supplies its own final
draft; original private SDK items are recorded unchanged. Report digests reflect
exact validated drafts. The authored test provider now emits the notice as part
of its authored template. Existing raw reports/ratings stay immutable.

Old bindings with no policy retain old behavior. Retry copies its parent's policy
and exact prompt, rather than silently adopting the latest. Public JSON schemas,
states, review authority and numerical limits remain unchanged; private binding
and prompt protocol are explicitly documented in tools-and-provider.md.

This is an exact protocol check, **not semantic interpretation**. A paraphrase,
quote, negated prefix or text placed only in another section does not satisfy the
new literal requirement and can consume the single repair. The approved constant
does not prove that other claims are safe or noncontradictory. Semantic status
stays `not_reviewed`; original mandatory disclosures and quality criteria remain.

## Verification actually executed

Feature003 selected explicitly; scoped speckit-implement, requirements checklist
16/16 PASS; no extension hooks. Existing locked environment, no installs.

```powershell
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_human_authority_v7.py -q --tb=short
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_human_authority_v7.py backend/tests/unit/test_investigation_reliability_v2.py backend/tests/unit/test_investigation_coverage_v4.py backend/tests/unit/test_investigation_repair_v5.py backend/tests/unit/test_investigation_live_development_v2.py -q --tb=short
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short
.venv/Scripts/ruff.exe check backend evidence/tasks/feature-003-human-authority-v7-check.py
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-human-authority-v7-check.py
git diff --check
```

- Test-authoring initially encountered the immutable-audit trigger; corrected
  fixture setup to construct legacy/unknown bindings before insertion. No trigger
  disabled and no immutable record updated. This authoring error is not RED evidence.
- **RED9 failed/1 passed** before runtime changes: missing notices accepted with
  no repair, no policy/prompt binding, no unknown-policy rejection, budget case
  incorrectly accepted. Legacy behavior already passed and remains compatible.
- **GREEN18 new**, **82 related** checks PASS. One SDK assertion initially assumed
  the notice had to be the last limitation; corrected to the specified whole-item
  membership at any position. Production rules were not weakened.
- First full suite:910 PASS/1 FAIL because an old mocked generator returned a
  draft without the new mandatory item. Updated that authored positive fixture
  to include the notice, keeping its one-request and reference-isolation checks.
- Final full backend: **911 passed in70.09s**. Ruff/diff PASS.
- Both needs_information/ready_for_review: one missing notice repaired or failed;
  raw drafts unchanged, no second repair, final report only after validation.
  Exact-item negatives, unknown policy0 requests, lower3-request budget, legacy/
  new retry pinning and old report immutability pass. Existing semantic/fact and
  recovery/security regressions pass under the new default.
- Real OpenAI SDK with **mock HTTP only**: missing original draft and opaque
  reasoning retained in the next input, fixed canonical hint serialized, one
  repair accepted. **Zero actual API calls** in this maintenance unit.

## Preservation and practical limits

Before edits, copied/verified19 frozen v6 runtime files under ignored
`.cache/evidence-snapshots/live-repair-v6/`. New policy module is separate; source
hashes intentionally differ from the historical batch.
[Offline results](feature-003-human-authority-v7-results.json): PASS. All32 prior
artifact hashes plus10 original v6 raw/metadata hashes and original v6 audit
remain intact. All13 cited IDs resolve; old reports have unchanged report IDs
under their original policy. The saved DEV6-762 omission is rejected under the
new policy without editing or regrading its output. Its original **1/2 ordinary
quality** remains failed, and the controlled repair remains separately reported.

Use old live runners/audits at their original commit (v6 source at af8fe4b) or
verified snapshot. Their old source-hash checks should not be run against changed
runtime. Latest offline preservation helper above uses the correct source snapshot.
Local milan guide remains ignored and below200 lines; historical checks that could
rewrite old evidence were removed from its current command list.

No .env/dependency/frontend/public schema edits, no fresh live batch or post hooks.
Correction was initially local; user subsequently requested its commit/push on
feature03-reliability-v2. Pre-publication HEAD af8fe4b; resulting tip is in Git.
Next step: freeze new prompt-v4/policy-aware development inputs and bounded live
protocol to assess complete reports and omission recovery without replaying762
or weakening judge criteria. Actual quality of the new prompt is **unverified**.
Producer/human/reproduction/Converge and original failed release gates stay open.
