# T033 actual provider access: PENDING

2026-11-15 Europe/Belgrade. No live probe authorized or executed in this continuation.
No model/project access, live request ID, usage, supported capability or quality
result is claimed. SDK 3.51.0 availability is a local dependency fact only.

`probe-provider --synthetic-only` exists and has mocked HTTP tests. A later,
explicitly agreed live probe needs backend-process OPENAI_API_KEY and the actual
accessible OPENAI_MODEL identifier; no credential should be pasted into chat.
No .env loader is provided. The command sends only an authored CASE-000 diagnostic,
not a stored case/corpus/reference. It makes at most two SDK calls, disables SDK
retries, applies configured hard limits and emits safe model/request/usage metadata
or a controlled failure. It does not evaluate report quality.

T033 does not block offline T034-T038; leave its task unchecked.
