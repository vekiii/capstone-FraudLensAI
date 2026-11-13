# Feature 002 macOS verification and T007/T008 review handoff

- Date and timezone: 2026-11-13, Europe/Belgrade.
- Task and requirements: [T007/T008](../../specs/002-data-and-risk-scoring/tasks.md), FR-001–004, FR-023, FR-026; [Feature 002 quickstart](../../specs/002-data-and-risk-scoring/quickstart.md).
- Exact user prompts: [verification](../../prompts/development/002-macos-verification-request-2026-11-13.md) and [documentation continuation](../../prompts/development/002-macos-review-handoff-request-2026-11-13.md).
- Verification revision: branch `002-data-and-risk-scoring`, full HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; working tree clean before and after the verification. `origin/initialization` was `f37e67a554395b564feadbd8d39a2ea151993a94`; the comparison covered 44 changed files. This handoff is a later uncommitted documentation edit on that branch.
- Runtime: macOS/Darwin 27.0.0 arm64; project `.venv` CPython 3.14.7, system `python3` 3.9.6, uv 0.12.15, Node 24.21.0, npm 11.19.0. Resolved versions: FastAPI 0.162.4, Pydantic 2.14.3, Uvicorn 0.54.0, pytest 9.2.0, httpx 0.28.1, Ruff 0.17.4, jsonschema 4.26.0; Vitest 5.1.0, Vite 8.3.8. Existing `uv.lock` and `frontend/package-lock.json` used; no lockfile edit.
- Source: ignored `data/raw/HI-Small_Trans.csv`, 475,664,283 bytes, SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`, matching the [reference manifest](feature-002-technical-resolution.json). This was local verification of an existing file, not a download in this session. No raw records or row-level labels are reproduced here.
- Status: verification complete; T007/T008 technical material prepared, required human owner review pending. Mapping `pending_team_review`, `executable_mapping=false`, `import_allowed=false`; only read-only `inspect` is available.

## Commands and observed results

Unless a different directory is stated, commands ran from repository root. `UV_CACHE_DIR` was a writable session cache outside Git. Exit codes below are actual results, including failed first attempts.

| Actual command / setting | Exit | Observed result |
|---|---:|---|
| `git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --short --branch` | 0 | Branch and full HEAD above; clean worktree. |
| `git rev-parse origin/initialization && git diff --stat origin/initialization...HEAD` | 0 | Base above; 44 changed files. |
| `uv --version; python3 --version; node --version; npm --version; uname -srm; uv sync --locked --group dev` | 2 for final sync | Version/platform values above; initial sync failed: `Failed to initialize cache at /Users/ladylazarus/.cache/uv`, `Operation not permitted (os error 1)`. |
| `UV_CACHE_DIR=/private/tmp/fraudlens-uv-cache-20261113 uv sync --locked --group dev` | 0 | `Resolved 41 packages in 11ms`; `Checked 39 packages in 5ms`. |
| `cd frontend && npm ci --ignore-scripts` | 0 | `added 68 packages in 762ms`. |
| `shasum -a 256 data/raw/HI-Small_Trans.csv; stat -f '%z bytes' data/raw/HI-Small_Trans.csv` | 0 | Source hash and size above. |
| `UV_CACHE_DIR=/private/tmp/fraudlens-uv-cache-20261113 uv run --locked pytest backend/tests -q` | 0 | **375 passed**, 1 existing Starlette/httpx deprecation warning, 0.98 s. |
| `UV_CACHE_DIR=/private/tmp/fraudlens-uv-cache-20261113 uv run --locked ruff check backend` | 0 | `All checks passed!` |
| `cd frontend && npm test -- --run` | 0 | **151 passed** in 5 files; Vitest 5.1.0, 892 ms. |
| `cd frontend && npm run build` | 0 | `npm run typecheck` passed; Vite 8.3.8 transformed 8 modules and built in 158 ms. |
| `UV_CACHE_DIR=/private/tmp/fraudlens-uv-cache-20261113 uv run --locked python -` (first in-process fixture script) | 1 | `ModuleNotFoundError: No module named 'fraudlens'`; `PYTHONPATH` had not been set. No fixture assertions ran. |
| `PYTHONPATH=backend/src UV_CACHE_DIR=/private/tmp/fraudlens-uv-cache-20261113 uv run --locked python -` (same script) | 0 | In-process `TestClient` smoke: health 200 `ok/fixture`; case list 200 with 3 items; `CASE-001` 200; `CASE-999` 404 `case_not_found`; `CASE-1` 422 `invalid_request`. Five checks passed. |
| `git diff --check` | 0 | No worktree whitespace error at verification end. |

The smoke script, run through `python -` in the two commands above, was:

```python
from importlib.metadata import version
import sys
from fastapi.testclient import TestClient
from fraudlens.main import app
print('python', sys.version.split()[0])
for p in ('fastapi', 'pydantic', 'uvicorn', 'pytest', 'httpx', 'ruff', 'jsonschema'):
    print(p, version(p))
with TestClient(app) as c:
    checks = [('/api/health', 200), ('/api/cases', 200),
              ('/api/cases/CASE-001', 200), ('/api/cases/CASE-999', 404),
              ('/api/cases/CASE-1', 422)]
    for path, status in checks:
        r = c.get(path)
        assert r.status_code == status, (path, r.status_code, r.text)
        b = r.json()
        print(path, r.status_code,
              'status/mode=' + str((b.get('status'), b.get('mode'))) if path.endswith('health')
              else 'items=' + str(len(b.get('items', []))) if path == '/api/cases'
              else 'error=' + str(b.get('error', {}).get('code')) if status >= 400
              else 'case_id=' + str(b.get('case_id')))
    assert len(c.get('/api/cases').json()['items']) == 3
print('smoke_checks=5 passed; fixture_cases=3')
```

It was **in-process**; no live server or browser check occurred. The first smoke attempt used the same script without `PYTHONPATH`. This fixture check is neither IBM import/evaluation nor a second-person reproduction. The existing Starlette warning reads: `Using httpx with starlette.testclient is deprecated; install httpx2 instead.` No browser finding was supplied by the user, so none is recorded.

### Read-only mapped source scan

The existing CSV hash matched before the scan. The macOS adaptation of the current quickstart command was:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.pipeline_cli inspect --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json
```

It ran inside a Python `subprocess.run(..., capture_output=True, text=True)` wrapper so the large JSON report was summarized without saving it. The **CLI child exit code was 2** (the reporting wrapper itself exited 0). Elapsed scan time: **25.76 s**. Stderr: `Inspection blocked; pending_team_review`. JSON: `status=blocked`, `complete_parse=true`, `row_count=5078345`, `error_codes=["pending_team_review"]`, `import_allowed=false`. This is a controlled team-review gate after a complete parse; no import or activation happened.

## Review hash audit and Git whitespace findings

The [original technical manifest](feature-002-technical-resolution.json) is preserved unchanged as the record of its initial byte check. The audit read every path with `git show HEAD:<path>`, hashed those **raw Git blob bytes**, then separately hashed a copy with LF converted to CRLF. It also hashed the working files. On this macOS checkout all 15 Git blobs and working files have LF endings and zero CRLF; working-file hashes equal raw Git hashes. **5/15 manifest entries match raw Git bytes; 10/15 match only after LF→CRLF conversion.** This is an ending difference, not evidence of a changed semantic contract or team approval. Reviews against this commit should use the raw Git hash column below for precise byte identity.

Team review anchor: commit **`182d0b290c8819e602fc5d77e8df8e904228b032`**.

| Review input at that commit | SHA-256 of raw Git blob | SHA-256 in original manifest | Manifest match |
|---|---|---|---|
| `data/mappings/ibm_hi_small_v1.json` | `0b0b85db9cc18cf959bbef80e5899707a3895cef147b6c1c0ae696b96645cc0b` | `4a8200f72c3fcd8f1d0c1ce99dd054a37d0972e4159c23c803174cdefaf207bf` | after LF→CRLF |
| `specs/002-data-and-risk-scoring/contracts/api.md` | `8836ec9cf15f610d840384ca78247e549ed55ddafbaa971bcbdd008b27e3a1ed` | `a77e93675055a322056eda2f17900ece33370bb21edac4cb61c1d1a29c736cc8` | after LF→CRLF |
| `specs/002-data-and-risk-scoring/contracts/data-and-scoring.md` | `e31ce98be5cf77c0b4b836dad0d083db71ff7e18ccf9846b6fa96845bb9346a0` | `abe99c6199263cd0ae9990d3cdc2507510d0750263ec572612c7e9991569c871` | after LF→CRLF |
| `specs/002-data-and-risk-scoring/contracts/schemas.json` | `9e93f40da78381d280da52a2a6ea421837e14c7d46420ccc85a41f1b404c0fc7` | `9e93f40da78381d280da52a2a6ea421837e14c7d46420ccc85a41f1b404c0fc7` | raw |

Separately, `git diff --check origin/initialization...HEAD` exited **2** and reported exactly three pre-existing `new blank line at EOF` findings in the branch comparison:

1. `evidence/tasks/feature-002-task-generation.md:82`
2. `evidence/tasks/feature-002-task-plan-validation.ps1:164`
3. `specs/002-data-and-risk-scoring/tasks.md:291`

They were not introduced or repaired by this documentation handoff.

## Questions for actual owners

Use the full commit and raw Git blob hashes above when recording a review. These questions prepare a review; they do not answer for a human owner.

### Data/scoring producer — T007, then T008

- Does the [mapping's source/csv/columns section](../../data/mappings/ibm_hi_small_v1.json) correctly bind Kaggle v8, exact ordered headers and the two `Account` occurrences at positions 2/4 to sender and receiver?
- Are the [mapping's time, money, labels and identity policies](../../data/mappings/ibm_hi_small_v1.json) acceptable, including UTC+00 as an analysis assumption, scales 0–6, zero support, source currency names, private labels and pre-filter ordinal identity? Which points need a revised decision or evidence?
- Does the [offline source mapping and import contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#reviewed-source-mapping-contract) match the intended producer behavior before an importer is designed?

### Frontend/API owner — T008

- Do the [API mode/compatibility and endpoint sections](../../specs/002-data-and-risk-scoring/contracts/api.md#mode-and-compatibility) preserve Foundation v1 while defining unambiguous v2 dispatch and 404/409/422/503 behavior?
- Can the [CaseListV2/CaseDetailV2 sections](../../specs/002-data-and-risk-scoring/contracts/api.md#caselistv2) and [JSON Schema](../../specs/002-data-and-risk-scoring/contracts/schemas.json) be implemented with exact currency/Decimal values, dataset/run/snapshot equality, ordering and a strict frontend decoder? Record remaining runtime validators/migrations.

### Investigation owner — affected consumer of T008

- Are the [TransactionV2 and assessment fields](../../specs/002-data-and-risk-scoring/contracts/api.md#casedetailv2) sufficient for a case review with source/time-basis disclosure, without exposing private labels or eligibility indicators?
- Does the [label-free ScoreRequestV2 and ScorerV2 boundary](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#scorerequestv2-and-scorerv2) supply the facts and explanation provenance investigation needs, or is a reviewed contract migration required?

### Priority/simulation owner — affected consumer of T008

- Do [CaseListV2 ordering, alert counts and snapshot rules](../../specs/002-data-and-risk-scoring/contracts/api.md#caselistv2) provide stable versioned inputs for ranking/replay without depending on fixture ordering?
- Do the [dataset/run and operational label boundaries](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md) keep holdout labels outside priority inputs while identifying the scorer and time assumption required for simulation? Record missing fields or migrations.

### Human review record — fill only after each owner's actual review

| Owner stream | Actual name | Date/time and timezone | Reviewed commit and raw blob hashes | Findings | Decision (approve / request changes / defer) | Remaining migration or evidence |
|---|---|---|---|---|---|---|
| Data/scoring | pending | pending | pending | pending | pending | pending |
| Frontend/API | pending | pending | pending | pending | pending | pending |
| Investigation | pending | pending | pending | pending | pending | pending |
| Priority/simulation | pending | pending | pending | pending | pending | pending |

Record each actual decision in the required [source audit](feature-002-source-audit.md) or [contract review](feature-002-contract-review.md) after the owner acts. The table here is only a capture format; no reviewer, date, finding or approval is inferred.

## T009–T011 technical findings and proposed tests — not executed

These are source-shaped test proposals derived from the current [mapping](../../data/mappings/ibm_hi_small_v1.json), [data model](../../specs/002-data-and-risk-scoring/data-model.md) and [offline contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md). They are **not RED tests, executed results, IBM import evidence or owner approvals**. T009–T011 implementation is [dependent on T008](../../specs/002-data-and-risk-scoring/tasks.md).

| Proposed test | Expected assertion | Exact repository rule |
|---|---|---|
| T009: two source-shaped rows use account `000123456` at different banks, with the same sender/receiver side held fixed | Bank-qualified join keys differ; retain exact bank and account strings and direction. Transaction IDs also differ because the rows have different ordinals, not because the banks enter the ID digest. | [Mapping `party_policy`](../../data/mappings/ibm_hi_small_v1.json), [CanonicalTransaction parties and identity](../../specs/002-data-and-risk-scoring/data-model.md#canonicaltransaction) |
| T009: paid `100.00` `Euro`, received `99.123456` `Bitcoin` | Valid separate exact Decimal texts and source currencies; preserve scales 2 and 6, with no rounding or FX. A paired negative case using `EUR` instead of `Euro` is rejected as an unapproved currency token, without implicit ISO conversion. | [Mapping `money_policy.source_currency_allowlist` and `new_currency_policy`](../../data/mappings/ibm_hi_small_v1.json), [CanonicalTransaction money](../../specs/002-data-and-risk-scoring/data-model.md#canonicaltransaction) |
| T009: valid event facts with an empty `Is Laundering` field | Event remains `event_valid` and operational; private label status is `missing`/supervised-ineligible. It contributes observable facts to history but no training/evaluation label. | [Mapping `labels.missing_or_other_token`](../../data/mappings/ibm_hi_small_v1.json), [ImportReport accounting and PrivateEvaluationLabel](../../specs/002-data-and-risk-scoring/data-model.md#importreport-and-row-accounting), [offline mapping contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#reviewed-source-mapping-contract) |
| T009/T010: rejected row 1 precedes two equal-valued valid rows 2 and 3 | Ordinals are assigned before validation: 1 rejected, 2 and 3 retained with distinct D/C IDs despite equal event values. Counts reconcile `source_records=3`, `event_valid=2`, `event_rejected=1`; no accepted-row renumbering. | [Mapping `csv.source_row_ordinal`](../../data/mappings/ibm_hi_small_v1.json), [identity and row accounting](../../specs/002-data-and-risk-scoring/data-model.md#identity-and-version-rules) |
| T011: interrupt import of a **new** dataset version after some SQLite batches while an older complete version exists | New attempt remains staged or becomes failed, never selectable or active; no partial complete report. The older complete version survives restart, and a retry can complete without overwriting it. | [DatasetVersion states](../../specs/002-data-and-risk-scoring/data-model.md#datasetversion), [T011/T014 transactional requirements](../../specs/002-data-and-risk-scoring/tasks.md), [offline import failure contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#local-command-interface) |
| T010/T011: reimport the **same already complete** source/mapping/time-policy version | Same `dv_` and D/C identities; no duplicate events/cases, no overwrite or partial replacement of the existing complete version. This idempotency case is separate from the interrupted new-version attempt. | [Identity/version and immutable complete-version rules](../../specs/002-data-and-risk-scoring/data-model.md#identity-and-version-rules), [T010/T011 and T016](../../specs/002-data-and-risk-scoring/tasks.md) |
| T010 isolated identity test: change only a private label in synthetic input while keeping namespace, member, ordinal, mapping and observable facts fixed | D/C IDs and event-fact digest/history inputs remain unchanged; raw-content SHA-256 and thus `dv_` change. Test the identity/version function boundary with synthetic values, without claiming that the edited file is accepted as IBM v8. | [Data-model identity/version inputs](../../specs/002-data-and-risk-scoring/data-model.md#identity-and-version-rules), [mapping `identity.label_only_changes`](../../data/mappings/ibm_hi_small_v1.json) |
| T010 negative source-binding test: try an otherwise identical **edited IBM v8 CSV** with only one label changed under the pinned v8 mapping | At the isolated source-binding validation boundary, assert the specific SHA-256 mismatch against `source.expected_sha256` and refusal before import. A future CLI may refuse earlier on `pending_team_review`; that generic gate result alone would not prove hash validation. The edited file cannot inherit the verified v8 source identity. | [Mapping `source.expected_sha256` and `execution_policy.import_allowed=false`](../../data/mappings/ibm_hi_small_v1.json), [offline source-bound duplicate/mapping contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#reviewed-source-mapping-contract) |

The identity/version distinction and v8 hash refusal are already specified, so the isolated T010 assertion needs no new policy decision. A full import of an edited file as a **different declared source** would require a separately reviewed source binding/namespace and mapping decision; the current pinned v8 mapping does not authorize it. All proposed import tests await T008 and the actual mapping/consumer gates. No test fixture, SQLite database, RED test or implementation was created for this note.

## T007 reproducible identity and hash proposal — 2026-11-13, not approved

Historical state at commit `182d0b290c8819e602fc5d77e8df8e904228b032`. The user's later [joint team technical decision](feature-002-t007-t008-team-review-2026-11-13.md) adopts this recipe. That record contains the changed mapping hash and new `dv_` vectors; final owner review of the resulting working diff remains pending. The proposal text and original vectors below are preserved as the earlier calculation.

[Exact user request](../../prompts/development/002-identity-hash-proposal-request-2026-11-13.md). Reference commit `182d0b290c8819e602fc5d77e8df8e904228b032`. This section proposes the missing byte-level recipe identified in the independent T007/T008 review. It retains the [data-model identity inputs](../../specs/002-data-and-risk-scoring/data-model.md#identity-and-version-rules): source namespace, member and pre-filter one-based CSV record ordinal for D/C; raw source SHA-256, mapping SHA-256 and time-policy SHA-256 for `DatasetVersion`. It adds no label, account, business fact, accepted-row position or raw source hash to D/C. The full digest and framed inputs must be retained locally for collision checks. **No mapping, contract, importer or test was changed by this proposal.**

### Exact proposed byte recipe

1. Encode the reviewed source namespace and exact member name as UTF-8, without Unicode normalization or case folding. For each, prepend its byte length as one unsigned four-byte big-endian integer (`U32BE`), permitting lengths 0–`2^32−1` at the encoding layer; the mapping/contract still requires nonempty valid values. Append the pre-filter one-based CSV record ordinal as one unsigned eight-byte big-endian integer (`U64BE`), valid from 1 through `2^64−1`. Thus `I = U32BE(len(namespace_utf8)) || namespace_utf8 || U32BE(len(member_utf8)) || member_utf8 || U64BE(ordinal)`. The source member is included separately even if the namespace text mentions it.
2. `D = "D" || lowercase_hex(SHA256(ASCII("FraudLensAI/tx/v1") || 0x00 || I)[0:16])`. `C = "C" || lowercase_hex(SHA256(ASCII("FraudLensAI/case/v1") || 0x00 || I)[0:16])`. The domains differ; each public suffix is exactly 16 digest bytes / 32 lowercase hex characters. The digest is SHA-256 over bytes, not a formatted string. This preserves distinct identities for equal-valued rows with different ordinals and stable identities under label-only edits.
3. Source hash `S = SHA256(exact original CSV bytes)`; never normalize source line endings or labels. Mapping hash `M = SHA256(N(exact reviewed mapping-file bytes))`, where `N` first requires strict UTF-8 with no BOM, rejects any bare `0x0d`, then replaces every CRLF (`0x0d 0x0a`) with LF (`0x0a`). It does **not** reserialize JSON, trim whitespace, change a final newline or exclude any mapping-file byte. All mapping keys/values, including current null/pending review and execution fields, participate. JSON structure/duplicate-key validity is a separate prerequisite. A content change other than CRLF↔LF changes `M` and invalidates prior approval.
4. Time-policy hash `T` keeps the already recorded rule: SHA-256 of UTF-8 JSON for `time.selected_policy`, sorted keys, compact `,`/`:` separators, with the current Python JSON ASCII escaping behavior (`ensure_ascii=True`). It is distinct from `M`; on the reference mapping it is `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781`. The time-policy hash is included both as a field inside the mapping bytes and as its own DatasetVersion input, intentionally preserving the current model's three inputs.
5. `DatasetVersion = "dv_" || lowercase_hex(SHA256(ASCII("FraudLensAI/dataset-version/v1") || 0x00 || S || M || T))`. `S`, `M` and `T` are each the **32 raw digest bytes**, obtained from their 64-character lowercase hex representation if necessary, in that exact order. They are fixed width, so no extra length prefixes or delimiters are used. The `dv_` suffix is the full 32-byte SHA-256 / 64 lowercase hex characters. A label-only source edit changes `S` and `dv_`, while `I`, D and C stay the same for the same namespace/member/ordinal and unchanged observable facts. This is an algorithm vector only; a changed IBM v8 file still fails the pinned source-hash check and is not importable as v8.

### Separate approval record and three different hashes

Propose a separate tracked review record containing the exact reviewed commit/path, `M`, the source SHA-256, `T`, actual reviewer names, dates, findings/decisions and any migration notes. That record's bytes and metadata are **not** inputs to `M` or `dv_`; do not put `M` inside its own hashed mapping file. The existing mapping's `identity.approved_mapping_sha256` remains `null` in this proposal and is not silently treated as signoff. Before import, a future reviewed implementation must verify the complete mapping's recomputed `M` against the separate approved record and all required gates. If mapping content, review flags or import policy changes after approval, recompute `M`, refuse the old approval and obtain review of the final bytes; no old complete dataset is overwritten. The team must decide whether to retain the embedded null field in the final frozen mapping or remove it in a reviewed revision, and how to represent actual approvals/import enablement outside the hashed mapping. **Current `import_allowed=false` remains effective.**

For the reference commit, the **raw Git blob SHA-256** of the LF mapping bytes is `0b0b85db9cc18cf959bbef80e5899707a3895cef147b6c1c0ae696b96645cc0b`. This happens to equal proposed `M` because the committed file has LF. The historical review manifest's `4a8200f72c3fcd8f1d0c1ce99dd054a37d0972e4159c23c803174cdefaf207bf` is the SHA-256 of CRLF bytes, **not** proposed `M`. `T` above hashes only the selected time-policy object under its existing canonical JSON rule. Neither the historical manifest nor this proposal records an actual owner approval.

### Executed in-memory vector check

Actual command from repository root, system `python3` 3.9.6, exit **0**: `python3 - <<'PY'` with the following body. It read the pinned mapping through `git show`; it wrote no source, mapping, database or evidence file. The synthetic seven-record CSV uses the exact eleven headers and LF endings. Its first six records have timestamp `2022/09/01 12:01` through `12:06`, sender `BANKA`/accounts `000000001` through `000000006`, receiver `BANKB`/accounts `000000101` through `000000106`, both amounts `1.00 Euro`, `Wire`, label `0`. Record 7 is the imagined row from the review: `2022/09/01 12:34,BANKA,000123456,BANKB,000123456,99.123456,Bitcoin,100.00,Euro,Wire,`. The second variant changes only that last empty label to `1`. Namespace `synthetic:fraudlens-review:v1` and member `review-7.csv` are test-vector values, **not** a reviewed IBM namespace/member; the current v8 mapping would reject these synthetic CSV hashes.

```python
import csv, hashlib, io, json, struct, subprocess
raw_map = subprocess.check_output(['git', 'show',
    '182d0b290c8819e602fc5d77e8df8e904228b032:data/mappings/ibm_hi_small_v1.json'])
def mapping_hash(raw):
    raw.decode('utf-8', 'strict')
    assert not raw.startswith(b'\xef\xbb\xbf')
    assert b'\r' not in raw.replace(b'\r\n', b'')
    return hashlib.sha256(raw.replace(b'\r\n', b'\n')).digest()
M = mapping_hash(raw_map)
assert M == mapping_hash(raw_map.replace(b'\n', b'\r\n'))
mapping = json.loads(raw_map)
T = hashlib.sha256(json.dumps(mapping['time']['selected_policy'],
    sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')).digest()
def framed(value):
    b = value.encode('utf-8')
    return struct.pack('>I', len(b)) + b
I = framed('synthetic:fraudlens-review:v1') + framed('review-7.csv') + struct.pack('>Q', 7)
D = 'D' + hashlib.sha256(b'FraudLensAI/tx/v1\x00' + I).digest()[:16].hex()
C = 'C' + hashlib.sha256(b'FraudLensAI/case/v1\x00' + I).digest()[:16].hex()
header = mapping['csv']['expected_ordered_headers']
rows = [[f'2022/09/01 12:0{i}', 'BANKA', f'{i:09d}', 'BANKB',
         f'{i+100:09d}', '1.00', 'Euro', '1.00', 'Euro', 'Wire', '0']
        for i in range(1, 7)]
rows.append(['2022/09/01 12:34', 'BANKA', '000123456', 'BANKB',
             '000123456', '99.123456', 'Bitcoin', '100.00', 'Euro', 'Wire', ''])
def source_bytes(records):
    out = io.StringIO(newline='')
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(header)
    writer.writerows(records)
    return out.getvalue().encode('utf-8')
blank = source_bytes(rows)
rows[6][10] = '1'
label1 = source_bytes(rows)
def version(source):
    S = hashlib.sha256(source).digest()
    return 'dv_' + hashlib.sha256(b'FraudLensAI/dataset-version/v1\x00' + S + M + T).hexdigest()
print('M_LF', M.hex(), 'M_CRLF', mapping_hash(raw_map.replace(b'\n', b'\r\n')).hex())
print('T', T.hex(), 'I', I.hex())
print('S_blank', hashlib.sha256(blank).hexdigest(), 'S_label1', hashlib.sha256(label1).hexdigest())
print('D', D, 'C', C, 'dv_blank', version(blank), 'dv_label1', version(label1))
```

Observed values from the executed check:

| Item | Value |
|---|---|
| `I` framed identity bytes, hex | `0000001d73796e7468657469633a66726175646c656e732d7265766965773a76310000000c7265766965772d372e6373760000000000000007` |
| Proposed `M` from LF | `0b0b85db9cc18cf959bbef80e5899707a3895cef147b6c1c0ae696b96645cc0b` |
| Proposed `M` from CRLF after normalization | `0b0b85db9cc18cf959bbef80e5899707a3895cef147b6c1c0ae696b96645cc0b` |
| Existing `T` | `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781` |
| Synthetic blank-label CSV, 678 bytes, `S` | `a77db4d5f32043d538e1dd1a799119161912689bcdfb277bc75ba8670e78a588` |
| Synthetic label-`1` CSV, 679 bytes, `S` | `76984a07b7a7e8cf3ebeeb1732ce3852fa08383966c8e1bf3ed5ac3a1532afa9` |
| Both variants: D | `D425884d07ae8e842624343aa411210de` |
| Both variants: C | `C1cb19a78e9497dd29eee2de9e7527c60` |
| Blank label: `dv_` | `dv_83ce36822c035a5c2ca8e8a8a6c3371e7e3e1371b86df086b83a1c2dbb2b6aa6` |
| Label `1`: `dv_` | `dv_dfa703ee0abc65eee9a19791b23f5c8e3ed0e5d94c3f121b139086259aca984c` |

These are checks of a **proposed algorithm**, not results of T009–T011, actual IBM import or review approval. The exact team decision still needed is whether to adopt this framing/domain/output recipe and normalized mapping hash with a separate approval record, including how the future final mapping represents review state and import enablement. T007/T008 remain open until the real owners review and decide.

## RED/GREEN applicability, limits and continuation

This session verified existing behavior and documented the result; it did not implement critical business behavior, so no new RED/GREEN cycle applies. Backend/frontend tests, Ruff and build passed as recorded above. Browser verification, live-server/proxy smoke, IBM canonical import, model evaluation, v2 runtime/decoder integration and independent teammate reproduction were **not run** in this session. Synthetic fixture smoke is not model evaluation. Phase 2 assignment compliance is not claimed.

Next concrete step: actual data/scoring, frontend/API, investigation and priority/simulation owners review the pinned mapping/contracts, enter their real decisions and migration findings, then determine whether T007/T008 gates can close. Until then keep both unchecked and `import_allowed=false`; do not start Prompt 2 from this handoff.
