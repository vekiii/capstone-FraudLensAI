# Feature 002 protocol SHA-256 mismatch investigation

**Date:** 2026-11-15 (Europe/Budapest)
**Branch at start:** `model-implementations`, HEAD `123f9cc5fa2e72d4d582ffd064fab3dce4e3d736`
**Scope:** T066 pinned-protocol prerequisite only. No model or evaluation run.

## Finding

The expected SHA-256 `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068` is **correct for the committed protocol bytes**. The previously observed `e8073b9c664f241418566eb87b4a3797e9798aeb2d306d035bbd2c8676e38074` came from Git's CRLF conversion in this Windows working tree. The files have the same normalized content; only line-ending bytes differ. The local untracked draft is a separate document with another structure and another hash. It is not the pinned protocol.

| File/source checked | Byte count and line endings | SHA-256 | Meaning |
|---|---|---|---|
| `c88c684f3b9be96b50124b067ff4848f518da4d9:evals/protocols/feature_002_v1.json` and current `HEAD` Git blob | 5,919 bytes; 187 LF, zero CRLF | `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068` | Author-committed, tracked final protocol. `git log --all -- evals/protocols/feature_002_v1.json` found its introduction in Elena's `c88c684` and no later content commit. |
| Working-tree `evals/protocols/feature_002_v1.json` before repair | 6,106 bytes; 187 CRLF | `e8073b9c664f241418566eb87b4a3797e9798aeb2d306d035bbd2c8676e38074` | Same Git-normalized JSON but wrong raw-byte identity for the trusted loader and T066. Replacing CRLF with LF produces the expected `01fff67d...` exactly. |
| Untracked `evals/protocols/feature_002_v1.local-draft-2026-11-14.json` | 11,423 bytes; 247 LF | `439de30ddf91e29fb1b00857e64d2abf84e893afb70de3dfd950c8f1a525402a` | Separate, nested proposal (`protocol_version`, `dataset`, `feature_snapshot`); tracked final file instead has `version`, `dataset_version`, `split` and `amendment`. Preserved unchanged and not substituted. |

The local Git configuration reports `core.autocrlf=true` from `C:/Program Files/Git/etc/gitconfig`. Before repair, `git check-attr text eol -- evals/protocols/feature_002_v1.json` reported both attributes unspecified. The existing `.gitattributes` pinned LF only for `data/mappings/ibm_hi_small_v1.json`. This explains why the mapping retained its expected raw hash while the protocol did not. The code reads raw bytes and hashes them (`backend/src/fraudlens/pipeline_cli.py` and `model_scoring.py`), so the checkout difference matters for artifact identity and reproduction; it is not merely a display issue.

## Repair and boundaries

Added `evals/protocols/feature_002_v1.json text eol=lf` to `.gitattributes`, then converted **only that working-tree file** from CRLF to LF after checking the normalized bytes against the expected SHA-256. The protocol JSON values, Git blob and published expected hash were not changed. After repair, `Get-FileHash` reports `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`; `git check-attr` reports `text: set`, `eol: lf`. The local draft and four pre-existing untracked drafts were left untouched. No artifact was deserialized, no database was opened, and no score or metric was produced.

This resolves the **protocol-byte mismatch in this checkout**. It does not complete T066: the original source/history SQLite database, boosted artifact/manifest/metadata, original frozen-tree artifact, explanation sample and frozen outputs are still absent. Exact reproduction remains **BLOCKED** until those inputs are available and verified. T065 likewise remains blocked by its missing source/explanation evidence.

## Commands and validation

Run from repository root in PowerShell; the Python blocks were read-only except for the explicitly guarded LF conversion:

```powershell
git log --all --format="%H %aI %an %s" -- evals/protocols/feature_002_v1.json
Get-FileHash -Algorithm SHA256 -LiteralPath evals/protocols/feature_002_v1.json,evals/protocols/feature_002_v1.local-draft-2026-11-14.json
git config --show-origin --get core.autocrlf
git check-attr text eol -- evals/protocols/feature_002_v1.json
git ls-tree HEAD evals/protocols/feature_002_v1.json
```

Python `hashlib.sha256` over `Path.read_bytes()` and binary `git show HEAD:evals/protocols/feature_002_v1.json` / `git show c88c684:evals/protocols/feature_002_v1.json` gave the exact byte counts, line-ending counts and hashes in the table. A guarded Python conversion required the CRLF-to-LF result to equal the pinned hash before writing the protocol file. A JSON top-level-key comparison confirmed that the local draft is structurally distinct. `git diff --cached --check` passed. The staged inventory contains `.gitattributes`, this evidence record, the T066 addendum, `next_work.md` and the original request; the protocol JSON itself has **no staged content change**. A separate new-document whitespace/link check passed (zero links, zero errors). No application tests were run for this byte-preserving checkout fix.
