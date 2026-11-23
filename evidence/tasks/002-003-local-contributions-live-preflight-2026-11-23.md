# Local contribution LIVE demo — preflight stopped before provider calls

Date: 2026-11-23 Europe/Belgrade. [Exact authorization](../../prompts/development/2026-11-23-002-003-local-contributions-live-demo.md). Branch `feature/002-model-contributions`, HEAD/base `156e25b524f035522c228d64ce824065c3890939`. This remains a local experiment, not Feature 003 contract acceptance.

## Result

The private root `.env` is absent and neither `OPENAI_API_KEY` nor `OPENAI_MODEL` is set in this process. `fraudlens.investigation.environment.read_environment()` independently reported both values unconfigured; only Boolean presence was printed, never a credential. The [existing approved live-demo instructions](../../specs/003-ai-investigation/quickstart.md#pr-3-demo-with-the-real-openai-provider-on-windows) and [prior PR #3 evidence](pr3-live-demo-2026-11-23.md) name `gpt-6-luna` with semantic v8/report v6, grouped tools, strict sections, low reasoning, 48,000 input bytes, 8,192 output tokens, eight provider requests and 120 seconds total. Those historical values do not establish an active local model/key configuration. The requested rule says to stop before network calls if credentials are unavailable. Therefore no new knowledge store, live server/worker, attempt or provider request was created; the existing test-provider demo store and processes were not used as a substitute. No browser or HTTP LIVE flow was executed.

| Approved case | LIVE status | Attempt ID | Provider requests / tools / usage / duration | Report, citations, decision |
|---|---|---|---|---|
| `row:2959955` | **Not started** — missing private key and model configuration | None | 0 / 0 / unavailable / unavailable | None |
| `row:1500153` | **Not started** — first case did not reach the prerequisite check | None | 0 / 0 / unavailable / unavailable | None |

No requested or returned live model ID, live serialized input byte count, report claims, citations, saved decision or reopen result exists. Earlier **offline** builder sizes (28,660 and 45,417 bytes) are not live sent-request measurements. No price was inferred.

## Local checks completed without provider calls

- `shasum -a 256` verified frozen model text `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`, trusted model manifest `c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45`, bridge manifest `16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004` and independent sidecar bundle `8edb466a84a186f6115b725d10796c409d1aa5fa065ddfddf0e2e3e1beb12429`. Model files reside under `data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts/selected-unweighted-lightgbm/`; an initial check used a wrong `data/artifacts` path, failed for those two files, and the corrected-path check passed.
- `PYTHONPATH=backend/src .venv/bin/python evidence/tasks/probe_65_local_contributions.py`: exit 0, 65/65 exact score and status parity; no label values read; maximum raw reconstruction error `1.199040866595169e-13`, group error `1.7763568394002505e-15`, score error `1.1102230246251565e-16`.
- Compatible read-only Integration runtime: Python 3.14.10, LightGBM 4.7.0, OpenAI SDK 3.51.0. This establishes installed software, not provider access.
- `git diff --name-only origin/main -- data/eval data/processed backend/src/fraudlens/scoring/model_scorer.py backend/src/fraudlens/scoring/preprocessor.py backend/src/fraudlens/bridge_reader.py`: empty; no tracked frozen artifact, model scorer, preprocessing or bridge reader edits. Existing local work is preserved.
- Relevant current app/source inventory: sorted `path SHA-256` lines for ten files (`bridge_api.py`, sidecar/scoring modules, provider/settings/tools/workflow, and the three React contribution files) hash to SHA-256 `c8df72261c2c14312b2e61f6dbcb429104c97ac5c5382c736014939ddde50241`. This identifies the local candidate for a future run; no code was changed during this preflight.

## Handoff

Place a valid `OPENAI_API_KEY` and explicit `OPENAI_MODEL` in this checkout's private, ignored root `.env` or the private server process configuration, using the already approved live provider profile. Do not put either in Git or evidence. Then repeat the preflight, prepare a **new** isolated ignored knowledge/investigation store, and run at most one attempt per approved case in the stated order. Preserve the existing test/demo stores. If any LIVE report has material identity, evidence or contribution-interpretation errors, stop before the second attempt and do not record a demo decision as quality acceptance. No source fix or extra attempt is authorized between the two measurements.

No training, label access, T230, showcase replay, Feature 006, live provider call, commit, push, PR or merge occurred.
