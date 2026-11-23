# User-approved automated retrieval review method, 2026-11-17

User explicitly authorized API/worker integration and "nezavisnu evaluaciju kao
LLM as judge". This replaces the pending HUMAN reference-review requirement for
this T095 retrieval experiment with a separate blind automated annotator. It
does not create a human signature, independent-model claim, report-quality pass,
T066 reproduction, T094 resolution or approval for automatic merge/task closure.

Configured model gpt-6-luna used in separate stateless contexts, no candidate
selection supplied to judge. Four known-label judge calibrations predeclared and
all required to pass. Judge20 reference sets frozen BEFORE candidate20 requests.
Inputs from the previously proposed, unexecuted English held-out partition;
16answerable+4no-answer preserved. Candidate core/prompt/parameters not tuned on
results. Same-model/corpus/topic correlation remains a limitation; wording novelty
does not prove semantic independence from all earlier development families.

Max44 new calls (4calibration+20judge+20candidate), retries0. Initial execution
stopped after candidate10 failed; its failure was retained. Explicit continuation
ran ONLY10 previously undispatched inputs under same freeze, no retry or extra
budget. Both initial failed partial report and complete aggregate preserved.
All failures count in denominators, thresholds unchanged .80Recall/.70MRR/all4
no-answer. Monetary cost unknown; known62777tokens plus one unknown usage outcome.

After completion a privacy-only public HTTP audit projection was corrected through
RED/GREEN. Original executed runtime archived; semantic core/prompt unchanged.
Scores refer to the executed version, not a secretly rerun or relabeled new
experiment. Current post-correction runtime has offline regression evidence.
