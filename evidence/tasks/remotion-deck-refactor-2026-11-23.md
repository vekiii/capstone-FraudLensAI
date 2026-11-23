# Remotion deck refactor — 2026-11-23

## Scope

The [original request](../../prompts/development/2026-11-23-remotion-deck-refactor.md) is preserved.

Refactored the existing `fraud-demo/src/Composition.tsx` and retained its composition ID and Basic Captions component. The seven-scene video uses the palette in `web/src/theme.ts`, Inter from `@remotion/google-fonts/Inter`, and `TransitionSeries` with 18-frame `springTiming` overlaps alternating fade, slide from right, and wipe. Scene lengths are centralized in `SCENES`, totaling 1,440 frames at 30 fps. The persistent layer contains a pipeline rail, grid, and drifting lime glow.

The previous fixture transactions and synthetic excerpts remain in `fraud-demo/src/data/transactions.json`. The $48.5K case, 4.1× ratio, 0.82 score, brief, and citations are expressly illustrative showcase values in that file. The video does not run LightGBM, retrieval, or an LLM. The visible badge says it is not live customer data; the model node and evidence flow say they are conceptual. The 0.60 threshold is illustrative. A human reviews any next step.

McKinsey’s [*The investigator-centered approach to financial crime: Doing what matters*](https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/the-investigator-centered-approach-to-financial-crime-doing-what-matters) states that, for most banks, more than 90% of transaction-monitoring alerts turn out to be false positives. The video’s “90%+” is attributed to that article.

## Verification

| Check | Observed result |
| --- | --- |
| `npm.cmd install @remotion/transitions@4.0.546 @remotion/google-fonts@4.0.546 --save-exact` | Sandbox network attempt failed with EACCES; elevated retry added four packages and reported zero vulnerabilities. |
| `npm.cmd run lint` | ESLint and TypeScript passed after the final source edits. |
| `npm.cmd run build` | Remotion bundle passed before the final copy-only JSON/code substitutions. |
| `npx.cmd remotion render FraudLensProductDemo out/FraudLensProductDemo.mp4` | Default browser download failed with EACCES, so the installed Chrome executable was used for the render. |
| Final render with installed Chrome, `--concurrency=4 --log=error` | Passed; MP4 is 16,574,828 bytes. |
| Bundled `ffprobe.exe` on final MP4 | 1920×1080, 30/1 fps, 1,440 frames, 48.000000 seconds. |
| Seven frame captures with bundled `ffmpeg.exe` | Frames at seconds 1, 6, 12, 19, 28, 37 and 45 were extracted. Initial visual inspection found captions obscuring cards; caption styling and placement were corrected and the final render rechecked. Final frames at 12, 28, 37 and 45 seconds show readable content without overlap. |
| Studio HTTP check | `http://127.0.0.1:3000/FraudLensProductDemo` returned 200 after the refactor. |

The existing `fraud-demo/fraud-demo/` nested scaffold and unrelated repository work were preserved. Generated `out/` remains ignored by `fraud-demo/.gitignore`.

## Local publication

At the user's request, the frontend design audit was committed as `180d3a4` and the Remotion source, lockfile, theme and scoped ignore rule as `36fea55`. Both use the existing repository identity `Isidora Popovic <popovicisidora17@gmail.com>`. The exported MP4 stays local under the ignored `fraud-demo/out/` directory. No push or merge was requested or performed. The documentation and handoff are recorded in a separate local commit.
