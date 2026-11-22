# T005/T006 contracts
Date 2026-11-14 Europe/Belgrade (work began 2026-11-13). Branch feature03; baseline 6db94af3471a9007a8a0d88cba8c7ece32886483; initial tree clean.
Prompt: ../../prompts/development/003-investigation-phase-02.md. Human review pending.

Actual RED: uv run --locked pytest backend/tests/contracts/test_investigation_contracts.py
--basetemp <root>/.cache/phase2-red-<unique UUID> -o cache_dir=<root>/.cache/phase2-cache-<same UUID> --tb=no -q
Exit 1: 56 failed at importable NotImplementedError boundary, 1 existing snapshot
hash check passed. GREEN same module after models: exit 0, 57 passed.
Local registry resolves source/producer refs without network; pinned producer hash
normalizes checkout CRLF to LF, no JSON reformatting. Canonical context checks exclude
context_revision; semantic identity/fixture provenance checks beyond schema.
Pydantic public/domain models have strict fields and source-schema validation;
source_payload is deliberately retained as unchanged source dict, no producer import.
No semantic faithfulness/quote validation or provider-schema compilation claimed.

## Additional semantic tests / final GREEN
Added valid-shaped ID/run/dataset mutations with recomputed context hashes,
Pydantic mutated/constructed instance checks, review text bounds and explicit offline
format-checker test. Coverage tests then exposed available-history missing cutoff/
coverage: 2 actual assertion failures (DID NOT RAISE ValueError); recursive semantic
History validation fixed them. Dataset explanation scale is checked against its
actual producer method (rules=risk_score, linear=log_odds, tree=positive_class_estimate),
not indiscriminately converted to risk_score. No producer object/schema changed.

Command: `uv run --locked pytest backend/tests/contracts/test_investigation_contracts.py --basetemp D:\AIBootcamp\capstone\.cache\003-p2-0717086054b845d581e92694c32ea365 -o cache_dir=D:\AIBootcamp\capstone\.cache\003-p2-cache-0717086054b845d581e92694c32ea365 --tb=short -q`

Exit 0.

```text
......................................................................   [100%]
70 passed in 1.19s
```
