# Feature 002 inspection implementation request

Received 2026-11-13, Europe/Belgrade. Original user instruction:

> Implement only the Feature 002 task slice for source inspection, mapping decisions and contract review identified in tasks.md. Start by reading applicable AGENTS.md, then next_work.md; set the explicit Feature 002 directory. Read the spec, plan, research, data model, contracts, relevant tasks, current Foundation code and tests. Keep the current branch and unrelated working changes.
>
> Inspect only an authorized local IBM AML HI-Small source if present. Before generating artifacts, add and verify a Git ignore rule for the local artifact directory; raw and processed data are already ignored. Record exact source/release/license/hash, observed headers/encoding/ dialect, row and label counts, timestamp resolution/timezone evidence, amount/currency forms, file size and ambiguities. Do not infer a field from a paper or sample and call it observed. If the source is absent, implement only independent source-shaped inspection behavior/tests and leave the actual mapping and substantive evaluation pending.
>
> Propose/freeze the reviewed mapping and v2 contract only when supported by evidence. Compare with Foundation v1 backend schema, frontend strict decoder, case ordering and unconditional fixture banner. Record affected producer/consumer review under the Foundation shared-contract procedure; do not invent reviewers or approval. If review is pending, finish independent work but do not integrate a breaking contract. Add exact negative tests for duplicate and target-like headers, missing fields, invalid encoding and source mismatch. Record RED/GREEN and one next step. No commit/push.

Provenance clarification (original user reply):

```text
Acquisition source:
https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml

File: HI-Small_Trans.csv
Local path: data/raw/HI-Small_Trans.csv

Exact dataset release/version: unknown; pending verification.
Acquisition date: 13. November 2026.

License reference:
IBM's official AML-Data repository states that the dataset is
released under CDLA-Sharing-1.0:
https://github.com/IBM/AML-Data

Please verify that this license applies to the acquired Kaggle
release. Keep release verification and mapping approval pending
until supported by evidence.
```
