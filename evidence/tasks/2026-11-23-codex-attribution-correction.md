# Codex-labelled Git commit attribution correction — 2026-11-23

The user stated that the nine commits recorded with `Codex <codex@openai.com>` should be attributed to her and selected the exact replacement identity `Isidora Popovic <popovicisidora17@gmail.com>`. Both Git author and committer fields were corrected. This records the user's attribution instruction; Git metadata alone does not establish individual intellectual contribution to every line.

| Branch | Superseded commit | Replacement commit |
|---|---|---|
| `codex/pr3-final-review` | `76b9e08a7620fbb53feff00a7db872719b37dd1d` | `3c7092bfb86d7c13238960e0fad28b85ebca01d5` |
| `codex/pr3-final-review` | `fc724e6d2f0bb9afa9071e47323e364063ecaf43` | `33f73574c4499814e727914b693964eb1634feff` |
| `codex/pr3-final-review` | `c84197c4560e1a24ec2f84ce293fb344e225be39` | `41be73595a9bafc3a949608c2c51471d33de73e1` |
| `codex/pr3-final-review` | `7b5b56cbb4a2fe8d738a8b4e574ee63d051e068e` | `faee7f6d5b1cf3e269ca3338309453a1514ec3ae` |
| `codex/pr3-final-review` | `b925ae5a9bd6a2ce06741366ef321b2dec297d33` | `0600c36961c94d662edcfafd9673ee3b9cf052da` |
| `codex/pr3-final-review` | `6938da03d0b74a8f778ee0af80ff6985bf7d1187` | `f25345f6f1ca2d3688705efd583d6451e9b57bcf` |
| `feature/002-clean-start` | `a737e205f47b36eaa1436c4b294d2a702068bfee` | `990ba1f405629367e9d18147dfac7fa9ff41ebba` |
| `feature/002-clean-start` | `203e265e7323cc41519629d6c973618a78b5c57e` | `5676ef4c5047721951ea4f15eeb0a1e6a18dd956` |
| `feature/002-clean-start` | `28a938ab68824c6eb7e896882adfd65984e336cc` | `ab9f0bf936459ea2fa0af7bd849b941893b9abae` |

The old tip trees match the replacement tip trees exactly (`git diff --exit-code` passed for both). Every replacement commit preserves the corresponding old tree, message, author date and committer date. Parent links were remapped only within each chain. The six and three replacement commits have no `Codex` author in their reachable histories. No model, protocol, data, labels, source code, test result or application behavior was changed by the rewrite.

Before publishing, `git ls-remote --heads` matched both expected old tips. `git push --force-with-lease` updated only the two named remote branches: `codex/pr3-final-review` from `6938da0` to `f25345f`, and `feature/002-clean-start` from `28a938a` to `ab9f0bf`. A subsequent `git ls-remote --heads` returned the exact replacement tip hashes. Local branch refs were aligned with those remote tips. `git log --all --author=Codex` returned no reachable commits after alignment; the old object IDs may remain available in caches or remote retention and are listed here only as superseded history.

`origin/integration/capstone-mvp` and the security audit branch were not rewritten. The ignored local T230 archives were untouched. The master ledgers were refreshed to use the corrected identities and hashes. Each ledger identifies its pre-publication snapshot at the top of the file.
