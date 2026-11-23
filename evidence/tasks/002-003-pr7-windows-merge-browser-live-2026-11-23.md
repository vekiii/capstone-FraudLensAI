# PR #7 Windows integration and live rehearsal

23 November 2026, Europe/Belgrade. [Milan's request](../../prompts/development/2026-11-23-pr7-windows-merge-browser-live.md) authorized a local merge, browser review and one new real-provider attempt for `row:2959955`. The tested merge commit is `cc1c3d7`, with parents `c5944a3` and `cff04a0`.

## Local integration

- `git fetch origin refs/heads/main:refs/remotes/origin/main refs/heads/feature/002-model-contributions:refs/remotes/origin/feature/002-model-contributions` succeeded. The clean feature branch matched its remote tracking ref and current `origin/main` was `cff04a0`.
- `git merge --no-ff --no-commit origin/main` conflicted in `next_work.md` and `evidence/README.md`. Both PR #7 and CAP-06 entries were retained. `git diff --cached --check` passed before committing. The merge brings in PR #8 verification documentation and regression tests. The change from `c5944a3` contains no production source paths.
- Local HEAD contains `origin/main`. GitHub publication and PR state changes remain subject to the team's decision.

## Saved reports on Windows

The regular Windows demo environment uses Python 3.14.10 and LightGBM 4.7.0. The received 94,480-byte ZIP matched SHA-256 `c645a516a1c9f5e99bc0a8c1096d0166da6b2551e9bf61de0e3258b7c496dc1b`. The two imported files matched their independent pins: sidecar `8edb466a84a186f6115b725d10796c409d1aa5fa065ddfddf0e2e3e1beb12429` and saved investigation store `8675fed623cc062fbb2a1631225e72c5813c82122b5c28fe2c99a1d7eeea40dc`. The local bridge matched manifest `16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004`.

Chrome 158.0.8127.36 rendered the contribution panels and reopened the archived cases through loopback Vite and FastAPI. `row:2959955` retained score `0.26731622570809`, outcome `needs_information` and six clicked citations. `row:1500153` retained score `0.9267620061893889`, outcome `ready_for_review` and five clicked citations. Both exact-value panels and contribution citations were checked. Refresh and reopen returned the same reports and preserved the SQLite hash. The initial sandboxed Chrome process failed to start a usable GPU process. The permitted browser rerun passed. Screenshots and the browser harness remain local under ignored `.cache/pr7-windows-20261123/`.

For the human review, compare the transaction and score, the positive and negative log-odds terms, the `log1p` feature versus the actual currency amount, and the report's contribution citation. The browser showed the title **Posebni lokalni doprinosi modela**, the **Pune vrijednosti i identiteti** details and the **Sačuvani dokaz** evidence panel. The offline servers were restarted with `Start-Process -WindowStyle Hidden` after Milan reported visible command windows. The original launcher PIDs were verified before stopping them. Both browser URLs responded via loopback after the restart.

## One new live attempt

The offline preflight checked the exact model-case score `0.26731622570809`, `review_recommended`, the v1 sidecar and the new store. It prepared the six-document corpus `corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3` and retrieval version `071f1a593fa17471295860bb5abc3a0064261a7e159bdf3d530494881001bccb`. The Windows review runner used the normal create-attempt API and the production `InvestigationService.work_once()` in an isolated database. The HTTP instrumentation measured serialized body length without modifying the payload or logging credentials. One attempt ran with `gpt-6-luna`, semantic v8, report v6, grouped tools, strict sections, low reasoning, 60 seconds per request, 120 seconds total, 8,192 output tokens, eight requests, 12 tool calls and the 48,000-byte input guard.

| Observation | Result |
|---|---|
| Attempt / report | `att_4e16f866f5cb436eb650c35e57097ba3` / `047248e05253350d088711d052c52ec53ba93363277222adb4af696d5afae334` |
| Outcome / elapsed | `ready_for_review` / 34.125 s |
| Provider / tools | 4 HTTP 200 OpenAI responses, 4 tools, 0 repairs, 0 transient retries |
| Actual request bodies | 12,891 B, 19,613 B, 8,453 B, 31,183 B. Minimum reserve 16,817 B. |
| Returned token usage | 17,544 input + 2,962 output = 20,506 tokens |
| Reopen | 5/5 cited items via API and Chrome, including the bound local contribution item. Reopen preserved the saved report and database. |

The draft correctly describes model inference over a synthetic input, the exact `6815.55 US Dollar` transaction and unchanged score, three positive log-odds contributions, incomplete sender and receiver history, simulated guidance and human authority. The saved draft's contribution citation matches the exact sidecar digest. There is no analyst decision in this rehearsal. This single attempt supports the compact demo case under the current budget. General case coverage remains unmeasured.

## Regression results and decision

- `npm.cmd --prefix web test -- --run` passed **297 tests**. `npm.cmd --prefix web run build` passed frontend typechecking and build. Vite emitted its large-chunk advisory.
- The Windows targeted backend suite ran `test_capstone_negative.py`, `test_risk_api.py`, `test_local_contribution_flow.py`, `test_contribution_sidecar_reader.py`, `test_local_contribution_sidecar.py` and `test_investigation_repair_v5.py`. Before the pinned sidecar was imported it produced 55 passed, 4 skipped and 3 failed. After import it produced **61 passed and 1 failed**, with no skips. All sidecar flow, CAP-06 and byte-boundary checks in that run passed.
- The remaining failure is `test_isolated_json_example_matches_verified_browser_case`. The pinned JSON digest validates. Native Windows recomputation has differences of approximately `8.88e-16` in one contribution and `4.44e-16` in the remainder, which generate a different canonical digest. The bridge score matches exactly. The test currently compares entire regenerated JSON byte semantics across environments. Keep exact delivered artifact verification and compare recomputed numeric values within the contract tolerance in a targeted follow-up.
- Recommendation: retain the limit for the compact demo case. Leave PR #7 in Draft until the Windows assertion and Feature 003 owner implementation review are resolved and the tested integration is published. The local verification made one new investigation attempt and no demo decision, with no second live attempt.

## Follow-up — Windows comparison and Feature 003 owner decision

On 23 November 2026 Milan personally confirmed that both archived cases looked correct in the browser. As Feature 003 owner, he authorized recording his approval of the reviewed opt-in pinned sidecar v1 implementation in Draft PR #7 after the test correction. The decision covers the local contribution display and its use as case evidence under the existing v2 assessment and 48,000-byte provider cap. The team review and merge remain separate from his approval. [User confirmation and publication request](../../prompts/development/2026-11-23-pr7-windows-merge-browser-live.md#follow-up-after-milans-browser-review).

- RED on `cc1c3d7`: isolated `test_isolated_json_example_matches_verified_browser_case` failed at exact dictionary equality with different native float results and resulting digests. The initial test invocation hit a Windows permission error in pytest's default temporary directory. The fresh `--basetemp` run reproduced the intended assertion failure.
- GREEN: the updated test recomputes the canonical digest of each payload separately and requires an exact match. It compares only the floating-point base, raw score, remainder and item contributions at absolute tolerance `1e-12`, with relative tolerance zero. The published score, all identities, methods, units, directions, and item order still compare exactly. The delivered `sidecars.json` matched SHA-256 `8edb466a84a186f6115b725d10796c409d1aa5fa065ddfddf0e2e3e1beb12429`. Integration tests exercise that same pin and wrong-pin rejection.
- An in-memory mutation check rejected a different identity, reordered items, a contribution changed by `1e-8` and a bad digest. The first three mutations carried valid recomputed digests.
- Python 3.14.10 on Windows: **62 targeted backend tests passed**, including the same six files listed above. `npm.cmd --prefix web test -- --run` passed **297 tests**. `npm.cmd --prefix web run build` passed typecheck and build with the existing chunk advisory. Ruff passed on the changed test. The production scorer, sidecar reader, application prompts, and serving code are identical to `cc1c3d7`. This turn made no provider requests.
- The first full backend run had 1,460 passed, 1 skipped and 1 failed. The unchanged prompt-wording test used the default Windows CP1252 decoder for a UTF-8 Markdown file. An initial UTF-8 command used a nested pytest temp path with an absent parent. With a fresh standalone `--basetemp` path and `python -X utf8`, both tests in `test_investigation_synthetic_model_wording.py` passed.
- Final Windows full suite with `python -X utf8 -B -m pytest -p no:cacheprovider --basetemp <fresh-temp-dir> -q -rs --tb=short --disable-warnings backend/tests`: **1,461 passed, 1 skipped, 7 warnings** in 143.01 s. The sole skip was the symlink test in `test_artifacts.py` because symlink creation was unavailable. The post-run sidecar and archived SQLite hashes matched their original pins. Review remains at the Draft-to-Ready handoff.
