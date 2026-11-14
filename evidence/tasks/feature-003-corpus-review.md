# T013 staged source review - 2026-11-14
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
