# FraudLens AI video demo

`FraudLensProductDemo` is a 1920×1080, 30 fps, 48-second Remotion composition. Seven scenes are connected with 18-frame spring transitions. Run `npm.cmd run dev` in this directory to preview in Studio; render with `npx.cmd remotion render FraudLensProductDemo out/FraudLensProductDemo.mp4`.

Scene copy, the illustrative $48.5K alert, its 4.1× amount, score, threshold, citations, and captions live in `src/data/transactions.json`. The amount and score are synthetic video values, not live customer data or live model inference. The LightGBM and RAG stages depict the intended workflow. Human review remains required. The source for the “more than 90%” statistic is linked in the JSON to McKinsey’s *The investigator-centered approach to financial crime: Doing what matters*.

The earlier three transaction fixtures and source excerpts remain in the JSON for provenance, but are not represented as the $48.5K showcase alert. Colors are imported from `web/src/theme.ts` through `src/theme.ts`; Inter is loaded with `@remotion/google-fonts/Inter`. Captions use the Remotion Basic Captions element and have no narration track.
