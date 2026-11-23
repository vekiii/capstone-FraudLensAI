# Current human source review - 2026-11-14

Later implementation update: actual corpus publication and runtime recheck now
PASS; see [Phase 3 completion](feature-003-phase-03-completion.md).
The review-time no-publication statements below remain historical; reviewer
identities, decisions, timestamps and approved source hashes are unchanged.

Branch: feature03. All six texts approved without changes by Milan Gavrić.
T013 complete. Manifest status reviewed; no actual corpus publish/ingest performed.

| Document | Reviewer | Decision | Approval recorded at (UTC) | Approved content SHA-256 |
|---|---|---|---|---|
| sim-review.md | Milan Gavrić | Approved without changes | 2026-11-14T10:13:38Z | 4a18944611dc634b6f4a099ebdcaf649b405a1243917443086d2f8853e3b07ae |
| sim-citation.md | Milan Gavrić | Approved without changes | 2026-11-14T10:15:33Z | 7285d239e0a34b3868559035e5e64479af1d83ae505f0886528117d48a1f9044 |
| sim-missing.md | Milan Gavrić | Approved without changes | 2026-11-14T10:20:01Z | 6e5ee8f44a5a9653dac71b431b4c7cec704a30e99d1f09db38598fff33e138b4 |
| ibm-guide.md | Milan Gavrić | Approved without changes | 2026-11-14T10:20:01Z | f9c01b0d842287cc3b797e01ac3a23085b699edcceec46d432295132ac7f2ff4 |
| us-records.md | Milan Gavrić | Approved without changes | 2026-11-14T10:20:01Z | 971fb8be66ebd2795982b46bca9173713ceb9578a06307be3dcd41fff1ef2f6b |
| us-confidentiality.md | Milan Gavrić | Approved without changes | 2026-11-14T10:20:01Z | f0787d7c21d1df278081a5c70dd996a60f3d86d12a601e6e9d46e30874d9e866 |

## Actual decisions and scope

1. Milan approved sim-review.md after the original was linked and its full Serbian
   translation and review questions were presented: "odobravam. Ime i prezime
   recenzenta sam ja Milan Gavrić." Recorded at 2026-11-14T10:13:38Z.
2. Milan approved sim-citation.md after the original was linked and its full
   Serbian translation and citation-faithfulness explanation were presented:
   "odobravam". Recorded at 2026-11-14T10:15:33Z.
3. All four remaining original texts were linked and full Serbian translations,
   source comparisons, historical/jurisdiction/educational limitations and reuse
   basis were presented. Milan responded "odobravam sve." No changes requested.
   Remaining approvals recorded at 2026-11-14T10:20:01Z (11:20:01 Europe/Belgrade).

Timestamps use the observed session clock when recording each response, not a
user-supplied exact approval instant. First/second timestamps are preserved.
Review covers all six texts and documented provenance/reuse/applicability.
Only Milan is recorded as reviewer; no other teammate's review is asserted.
One identified human reviewer suffices for FR-005/T013; four-person sign-off is
not required. Later FR-025/FR-027 and T066 have independent-review/reproduction
requirements. This approval is not a website-wide license, present-law assessment
or authorization to implement later phases or publish the corpus.

## Post-approval verification

Production `knowledge.stage` validation PASS: six documents, six passages;
review metadata, selected sections, schemas, source hashes and passage limits
validated. No source text/hash changed. Review/applicability metadata updated
truthfully; no source-wide reuse permission invented.
Corpus identity:
`corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3`.
Command: project .venv Python with PYTHONPATH=backend/src, calling
`stage('data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')`; exit 0.
Final consistency check initially lacked PYTHONPATH in a fresh shell and failed
with ModuleNotFoundError (environment setup, not source validation). Rerun with
PYTHONPATH=backend/src PASS: six approvals, T013 complete, downstream tasks still
unchecked, identical corpus identity. Git diff whitespace check PASS.
Validation only: no database opened, no corpus published, no runtime smoke repeated.
T015/T017/T019/T021/T022 remain partial pending actual-source publish/recheck.
Next: agree continuation with Milan, starting with T015 and remaining Phase 3
checks through T022. T023+ untouched; no commit/push.

The preparation record below is historical. Its all-null, manifest-only and
pending-review statements are superseded by the completed review above.

# T013 staged source preparation - 2026-11-14
Branch feature03 baseline 83b587b. Existing phase-02 handoff/next_work edits preserved.
Six documents and manifest prepared before asking for review. All reviewed_by/at
are null; manifest status staged. Retrieval date is 2026-11-14, represented at
00:00 UTC as a date-only convention, not a measured fetch timestamp.

Primary sources actually inspected with web tools:
- IBM AML-Data README: https://github.com/IBM/AML-Data/blob/main/README.md
  Synthetic generation, repository vs data licenses verified. No data downloaded,
  IBM text copied or real field-source audit claimed; field-policy details come
  from this project's pinned producer contract and are labeled authored guidance.
- FinCEN FIN-2007-G003 (2007-06-13), section (2): source URI in manifest.
  Exact 15-word excerpt plus authored summary, original source not paraphrase-as-quote.
- FinCEN FIN-2010-G006 (2010-11-23), scope paragraph/confidentiality discussion:
  exact short scope excerpt plus authored summary. Historical US applicability only.
No full third-party document copied, no unsupported permission or review invented.
Attempts at FinCEN website-policy/disclaimer/legacy PDF URLs were inaccessible;
therefore no website-wide license claim is made. Candidates use minimal attributed
excerpts and independently authored summaries; actual human reuse review required.

## Required actual reviewer action
User clarification received 2026-11-14: "Proverio sam samo manifest".
This records manifest inspection only. No document/source/reuse approval, actual
review timestamp, or permission has been inferred. All six normalized content
hashes were independently checked and match; reviewed_by/reviewed_at remain null.

Inspect all six documents and the manifest: source fidelity, thematic completeness,
reuse basis, included sections, dates/jurisdiction, simulated labels, limitations
and content hashes. Return actual reviewer name, date, decision and any corrections.
T013/FR-005 require this human review; agent preparation is not approval.
No corpus published/ingested. T013 partial until actual review; dependent tasks
must retain that limitation. User requested demo cutoff; config version 2 uses
unvalidated heuristic 0.5, no threshold tuning or quality acceptance claimed.

Review these actual texts alongside their manifest entries:
- [Simulated review](../../data/knowledge/fraudlens-aml-knowledge-v1/documents/sim-review.md)
- [Simulated citation](../../data/knowledge/fraudlens-aml-knowledge-v1/documents/sim-citation.md)
- [Simulated missing facts](../../data/knowledge/fraudlens-aml-knowledge-v1/documents/sim-missing.md)
- [IBM limitations guide](../../data/knowledge/fraudlens-aml-knowledge-v1/documents/ibm-guide.md)
- [Historical US supporting records](../../data/knowledge/fraudlens-aml-knowledge-v1/documents/us-records.md)
- [Historical US confidentiality](../../data/knowledge/fraudlens-aml-knowledge-v1/documents/us-confidentiality.md)

For each, confirm that the retained section/short excerpt or authored summary is
faithful, reuse basis is acceptable, and simulation/jurisdiction/date/limitations
are clear. Record actual reviewer name, date, decision and corrections. Until
that happens, keep staged status and do not run a real corpus publish.
