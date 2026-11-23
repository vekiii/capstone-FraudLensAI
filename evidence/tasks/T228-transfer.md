# T228 colleague guide and transfer bundle

- Date/time and timezone: 2026-11-20, Europe/Budapest
- Request: [original development prompt](../../prompts/development/002-T228-colleague-transfer.md)
- Related evidence: [T219](T219.md), [T228](T228.md), [macOS guide](T228-colleague-macos-guide.md)
- Baseline revision: `14fede4` on `feature/002-clean-start`
- Status: documentation and local transfer bundle prepared; protocol approval and colleague reproduction pending

## Who did what

| Role | Recorded contribution | Evidence |
|---|---|---|
| User / project owner | Requested the colleague guide, data bundle, ignore rule, commit, push and evidence index update. Earlier approved fitting the exact local CSV copy, but asked to review the complete protocol before explicit approval. | [Development prompt](../../prompts/development/002-T228-colleague-transfer.md), [T219](T219.md) |
| Repository Git author, Isidora Popovic LUKOWA | Authored the existing branch tip `14fede4`, which implemented the IBM-day split and local LightGBM pipeline. Git authorship identifies the recorded commit author; it does not establish individual contribution to each line. | `git log -1 --format='%h %an <%ae> %s'`, [T219](T219.md), [T228](T228.md) |
| Codex in this session | Wrote the macOS guide and local transfer archive, verified the input manifests and archive CRC, added the ignore rule, checksum, evidence and handoff updates. No other teammate's work or review is claimed. | [Guide](T228-colleague-macos-guide.md), local `T228-colleague-transfer-2026-11-20.zip`, [checksum](../../T228-colleague-transfer-2026-11-20.zip.sha256), this record |
| Colleague | No Mac setup, independent reproduction or model training has been reported yet. | Pending |

## Commands and observed results

- `Get-FileHash` on both prepared T219 input manifests: feature SHA-256 `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`; restricted train/validation label SHA-256 `5aee2e1d5f4f2ca7329fcc7b5b1ca0c808c4e8e39e84559e76a0d3e1a6add12c`.
- `git ls-files -z` supplied the tracked repository files for the archive. The script added only `data/processed/t219-ibm-day-60-20-20-v1/` and `data/processed/t219-ibm-day-60-20-20-labels-v1/` from ignored data, plus the current guide and selected evidence. The first archive had duplicate documentation entries; the rebuilt archive had 273 unique entries.
- Python `zipfile.testzip()` returned `None` (all archive CRC checks passed); expected input manifests were present; no duplicate archive entries. A broad filename check matched a tracked historical showcase-decision prompt, not a showcase dataset. The actual data directory selection excluded raw CSV, test-label files, showcase data and evaluation output.
- Final archive size: 111,539,550 bytes. SHA-256: `a3f36444a829f44cf990a43dcdc2d70bfe906ee85327186449dfa31e32595687`. The archive was rebuilt after the guide gained exact extraction instructions; CRC, path uniqueness and permitted data-directory checks passed again.
- No model fit, test evaluation, macOS installation check or colleague reproduction was run. This was documentation and packaging; RED/GREEN testing is not applicable.
- `git check-ignore -v T228-colleague-transfer-2026-11-20.zip`: matched `.gitignore` line 44. `git diff --cached --check`: exit 0, with no whitespace findings. The archive was not staged.
- `git commit -m "Document colleague training transfer and ignore local bundle"`: exit 0, commit `b7693f6`; seven documentation/ignore/checksum files committed. Git reported the automatically configured committer identity `Isidora Popovic LUKOWA <i.popovic@lukowa.com>`.
- `git push origin feature/002-clean-start`: exit 0, remote advanced from `42adea7` to `b7693f6`, publishing that commit and the 12 earlier local commits on the feature branch. No push to `master` was requested or performed.

## Limits and review

The archive is local and ignored by Git because it contains prepared transaction features and training/validation labels. The committed checksum is useful only for a copy of that exact archive. Transfer must use the team's approved channel. The current FR-021 JSON is still a candidate with canonical SHA-256 `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f`; archive receipt does not approve it. Human review: pending. Second-person reproduction: pending.
