# Proposed English v5 evaluation packet - NOT ACCEPTANCE EVIDENCE

30 AI-authored questions:10 development (8 answerable/2 no-answer),20 held-out
(16/4). Candidate hashes were recorded before authoring this packet. No query
from this packet has been run. Document references are proposals, not approved
gold labels; a reviewer must inspect relevance/completeness, resolve exact passage
IDs, and assess semantic overlap with exposed earlier question families. Reject
or replace overlapping questions rather than claiming novel independent coverage.
The six-document corpus limits semantic diversity; new wording alone is not new
independent evidence. Agent authorship does not establish independent human review.

Required next steps: actual reviewer identity/date/decision and source-bound
references; trusted input-only generator with separate offline reference join;
immutable reviewed freeze using the existing v3 safeguards adapted to English
counts; predeclare baseline/candidate configurations and development selection;
then an authorized one-shot acceptance run with retained errors/raw ranks. Do not
feed reference-proposed.json, split metadata or this review record to the runtime.
No lowering of Recall@5 .80/MRR@5 .70/all4 no-answer criteria.

Existing v3 runner assumes multilingual counts and MUST NOT run this packet as-is.
This packet is a review handoff, not an executable/frozen evaluation or a quality
pass. Old exposed-development diagnostics are stored separately in evidence/tasks.
