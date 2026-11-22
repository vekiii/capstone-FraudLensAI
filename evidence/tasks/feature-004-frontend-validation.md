# T019 — Feature 004 frontend validation

- **Status** Complete on 2026-11-19 (Europe/Belgrade).
- **Revision** `a0dfa5e6a8ccc117afe432e9c056549d41b6aec9` on `004-simulation-and-prioritization`.
- **Environment** Windows, Node 24.20.0, npm 11.19.0, Vitest 5.1.0, TypeScript 7.0.2, Vite 8.3.8 and jsdom 31.0.0. The existing install matched all 67 installed package versions in `frontend/package-lock.json`. There were 51 absent optional entries. Lock SHA-256 is `81f2b73c47a723aeb4ab0a272c367fa388808311d0f5b64ef4b0c8e91c03709c`.
- **References** [Quickstart](../../specs/004-simulation-and-prioritization/quickstart.md#test-first-validation) · [Request](../../prompts/development/004-simulation-phase-06.md)

## Commands and results

Commands ran from the repository root. `$testDir` was a fresh directory under `.cache/` for the Vitest JSON report.

| Command | Observed result | Exit |
| --- | --- | ---: |
| `npm.cmd --prefix frontend run test -- --run --reporter=default --reporter=json "--outputFile=$testDir/vitest.json"` | 193 passed in six files | 0 |
| `npm.cmd --prefix frontend run typecheck` | `tsc --noEmit` passed | 0 |
| `npm.cmd --prefix frontend run build` | TypeScript and Vite build passed, nine modules transformed | 0 |

The Vitest report recorded 82 API tests, 14 API lifecycle tests, 32 contract tests, 19 view tests, four UI lifecycle tests and 42 simulation tests. Cases coverage includes getting back to the list, focus restoration, and preventing obsolete detail successes or failures from updating the UI. Simulation coverage includes late responses after edits, scenario changes, resubmission and navigation, a late recipe read after a new comparison, strict recipe handling, and inspection of ranked and reviewed alerts.

This phase reran existing regression tests. Independent use of the browser walkthrough is recorded under T020. [Browser acceptance record](feature-004-browser-acceptance.md)
