# PR #3 Windows real-provider demo verification — 2026-11-23

[User request](../../prompts/development/2026-11-23-pr3-live-demo.md) ·
[Windows startup and demo steps](../../specs/003-ai-investigation/quickstart.md#pr-3-demo-with-the-real-openai-provider-on-windows)

## Candidate and setup

- [PR #3](https://github.com/vekiii/capstone-FraudLensAI/pull/3) was open and Draft from `integration/capstone-mvp` at `747ff975d21cf9dde6958d40f706650415743d1e` to `main` at `0fbe31315052542575b22515c83b0a062efeaa31` when checked. Git diff confirmed the same runtime, application prompts and locks as the tested `d46699f`.
- Restored the 17 ignored files listed in the prior verified Windows transfer inventory to the app's expected paths. Source and destination SHA-256 matched for all 17. Python 3.14.10, OpenAI SDK 3.51.0, LightGBM 4.7.0, Node 24.20.0, npm 11.19.0, Vite 8.3.8 and Chrome 158.0.8127.36 were observed. The configured OpenAI model is `gpt-6-luna`. Credentials stayed in the private local configuration.
- Prepared the committed knowledge corpus and retrieval configuration in a fresh ignored SQLite store. The OpenAI profile was semantic v8 with report v6, grouped tools, strict sections and low report reasoning. Limits were 48,000 input bytes, 8,192 maximum output tokens, eight provider requests, 12 tools and 120 seconds total. The app used the existing 30-second semantic selector limit and an explicit 60-second report request cap.

## First live attempt

Ran `node .cache/pr3-live-demo-20261123/verify.mjs` from the repository root. It started FastAPI and React on loopback, opened Chrome, submitted the canonical ID ending in `row:1500153` and clicked through from the exact score `0.9267620061893889` to case `C0674a2484035b8a21df34cbd69f3a38b`. The publication listed 65 alerts. Model results, EDA and fixture cases each returned HTTP 200. An unpublished ID returned 404 and a stale snapshot returned 409.

Chrome queued one OpenAI attempt `att_6599ca48fee54a4aa5fd2b07df0503db`. The worker ran once and the ledger recorded three returned OpenAI responses with usage, plus a fourth reserved request rejected locally. Case facts, both account history tools and semantic procedure search completed. The final state was `failed` with `budget_exhausted` in 12.611 seconds of worker invocation. The browser harness exited 1 at the report assertion. A report, clicked report citations and a saved decision were unavailable for this attempt. The ignored proof is under `.cache/pr3-live-demo-20261123/` and the database is `data/processed/pr3-live-verification-20261123.sqlite`.

## Offline diagnosis

Ran `.cache/pr3-live-demo-20261123/check-input.py` in the locked Python environment with `PYTHONPATH=backend/src`. A read-only reconstruction used the two saved generator turns, actual projected case and history tool outputs, and the saved procedure selection. The serialized drafting request was **49,935 bytes** against the **48,000-byte** guard. The production provider implementation returned `budget_exhausted` before the mock transport was entered. This confirms why the fourth reservation produced no provider response.

Case `C62fa694c59836209294725e25e4414ab` (canonical suffix `row:2959955`) has a score of `0.26731622570809` and two sender and four receiver history events. Simulating the same sequence and procedure passages gave **33,279 bytes**, which reached the mock transport without changing the guard. This is a candidate for the recovery demo.

## Successful compact-case run

The user explicitly approved the additional attempt. Ran `node .cache/pr3-live-demo-20261123/compact/verify.mjs` with the same app, provider profile and limits. Chrome followed the live score `0.26731622570809` to its published case, queued `att_b466609f7e1b4a3ea2ce2d26d14430d6` and the single worker reached `ready_for_review` in 27.725 seconds. All **4/4 OpenAI responses** recorded provider request IDs, returned model `gpt-6-luna` and usage totaling 20,692 tokens. Four tools completed and the attempt recorded zero repairs and zero transient retries.

Chrome displayed the validated report and opened all five distinct cited evidence links. The API returned 200 for each. The two procedure passages were the *Review* section of *Simulated review and escalation* and the *Missingness* section of *Simulated missing and conflicting facts*. Their content supports the report's recommendation to review the transaction and score limitations, record missing evidence, and leave disposition to the analyst. A local digest check matched the cited evidence contents. This was a scoped check of the report's sources for one synthetic case.

The automated demo operator chose `request_more_information` and saved decision `rev_3ed20097ad594a3db95e321809dbdf8f`. The API returned 201 and Chrome displayed the decision. The initial browser harness then exited 1 while clicking during reload. Ran `node .cache/pr3-live-demo-20261123/compact/reopen.mjs` with an empty process key and no worker. It restarted the API and React, waited for the new browser document after reload and verified the same decision in Chrome and through HTTP. The attempt was `reviewed`, the disposition matched, and the provider count stayed at four. The reopen check exited 0.

The verified store is `data/processed/pr3-live-compact-verification-20261123.sqlite`. Its browser observations and reopen logs are local under `.cache/pr3-live-demo-20261123/compact/`. The user can launch the same app with that store to show the result or prepare a fresh demo store and queue a new attempt. App code, model, provider limits, PR status and Git history were preserved. The input cap remains a known limitation for larger cases. The development-test evaluation, training, showcase replay and full test suites were outside this verification.
