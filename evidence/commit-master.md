# Master commit and branch record

Updated: 2026-11-22. Snapshot taken from current local and fetched remote refs after audit commit `ab692c69ae06bd89a83bf92d95893ccfddf380dc` and before the commit that publishes this ledger update. The Feature 002 ledger was brought from `feature/002-clean-start` because the integration base did not contain it.

Times are Git committer timestamps in ISO 8601 with their recorded UTC offset. The committer is shown as the person who recorded the commit; the author is listed separately because Git distinguishes authorship from committing. These names and timestamps are repository metadata and do not independently verify work effort or identity.

## Feature 002 - start here

This section retains previously selected Feature 002 commits and adds newly reachable commits whose subjects identify Feature 002, T200-series work or LightGBM. The complete history below is authoritative for all reachable commits in this snapshot.

| Committed at (ISO 8601) | Committer | Author | Commit | Description |
|---|---|---|---|---|
| 2026-11-12T21:39:12+01:00 | Veki | Veki | `f63bffe490358a4fba06d27b896d42c5e81bf882` | feature 02 created |
| 2026-11-12T23:51:05+01:00 | Isidora Popovic | Isidora Popovic | `5eb0d10cc7c2da724902e27329832455f58ed4fd` | docs(feature-002): strengthen risk-scoring specification after review |
| 2026-11-12T23:52:15+01:00 | Isidora Popovic | Isidora Popovic | `7957844bf328c2d164bcbb09ec5c1ed821564809` | docs(feature-002): add technical plan and Codex work prompts |
| 2026-11-13T04:03:56+01:00 | milangavric2003 | milangavric2003 | `3568c7dc9b5c4fe55286dd8b8c583650f41c265c` | docs(feature-002): generate implementation tasks (Prompt 0) |
| 2026-11-13T05:30:41+01:00 | milangavric2003 | milangavric2003 | `63d33843bc6483d66362e10133ec21c261c76df1` | feat(feature-002): implement source inspection (Prompt 1, T001–T005) |
| 2026-11-13T06:34:14+01:00 | milangavric2003 | milangavric2003 | `182d0b290c8819e602fc5d77e8df8e904228b032` | feat(feature-002): resolve source and contract issues (Prompt 1); T006 complete; T007/T008 await producer/consumer review. |
| 2026-11-13T09:42:24+01:00 | Isidora Popovic | Isidora Popovic | `dab61f36e36fa07f3b72c6d41b8ea7d94116d043` | docs(feature-002): record collective T007/T008 approval |
| 2026-11-13T09:45:55+01:00 | Isidora Popovic | Isidora Popovic | `6952f1d90b72cac00983449b1e96079b42a7eb72` | docs(evidence): finalize approval publication ledger |
| 2026-11-13T10:41:00+01:00 | Elena Kalajdžić | Elena Kalajdžić | `b5f75211c9a6aa5befa602f04308918df98ac106` | feat(feature-002): complete and verify local dataset import |
| 2026-11-13T11:20:52+01:00 | Elena Kalajdžić | Elena Kalajdžić | `55306089b506458fcaec9b621f49c00dd971d46e` | fix(feature-002): finalize phase 3 import verification and docs |
| 2026-11-13T14:23:37+01:00 | Elena Kalajdžić | Elena Kalajdžić | `0f5ad9ac0b04cc406e3c19b0f1934da4cc29d10d` | feat(feature-002): complete feature replay and rules baseline |
| 2026-11-13T14:35:38+01:00 | Elena Kalajdžić | Elena Kalajdžić | `27ac7d49e3d638717c752dce225216d291bf9e87` | fix(feature-002): protect concurrent feature snapshot builds |
| 2026-11-13T19:21:00+01:00 | Isidora Popovic | Isidora Popovic | `c872375e3457bf16a148541c407063a02615553a` | docs(ml): switch pretrained candidate to IBM AML LightGBM |
| 2026-11-14T14:44:17+01:00 | Elena Kalajdžić | Elena Kalajdžić | `c88c684f3b9be96b50124b067ff4848f518da4d9` | feat(feature-002): publish history-v1 scoring and exploratory evaluation |
| 2026-11-14T21:04:15+01:00 | Elena Kalajdžić | Elena Kalajdžić | `2099c7e50beb28e69c2e815154ab4233cd975487` | feat(feature-002): add boosted scorer and document full-run validation |
| 2026-11-15T10:07:54+01:00 | Isidora Popovic | Isidora Popovic | `cbc25b0742b83b4c8acf036a7ae81c1b0559c9de` | docs(feature-002): record access approval |
| 2026-11-15T13:50:07+01:00 | Isidora Popovic | Isidora Popovic | `496025e15ef4293e904870bd9e6fed714e8fa8c5` | fix(feature-002): preserve frozen protocol bytes on Windows |
| 2026-11-15T15:30:59+01:00 | Isidora Popovic | Isidora Popovic | `c4aaf419ac6b8bf13b64b9dabdee62867cd9a601` | test(feature-002): harden validation boundaries |
| 2026-11-15T15:32:47+01:00 | Isidora Popovic | Isidora Popovic | `d9bd8a2e3629a2d3939fc5507583f310428c53ac` | docs(evidence): record feature-002 publication ledger |
| 2026-11-16T11:43:44+01:00 | Isidora Popovic | Isidora Popovic | `57ce87f2d40b42c163e3c2b7efa6e4ab586363ca` | docs(feature-002): save protocol audit working artifacts |
| 2026-11-16T21:49:06+01:00 | Elena Kalajdžić | Elena Kalajdžić | `93d387e573d5c288f41ab6c38d30aa837b69987c` | feat(feature-002): publish isolated boosted daily cap and team handoff |
| 2026-11-18T19:14:33+01:00 | git stash | git stash | `04da6cd96554b588f39703f7d3f9af205e9170b5` | index on feature/002-model-development: 6b05dc4 docs(model2): record synthetic contribution ledger |
| 2026-11-18T19:14:33+01:00 | git stash | git stash | `81962309387d3749dde8b3cee7ffc336c85dec60` | On feature/002-model-development: preserve Feature 002 work before clean restart |
| 2026-11-18T19:14:33+01:00 | git stash | git stash | `b16aaf187a6da741381d9be1742b69e1ed53382d` | untracked files on feature/002-model-development: 6b05dc4 docs(model2): record synthetic contribution ledger |
| 2026-11-18T20:34:49+01:00 | Isidora Popovic | Isidora Popovic | `df4dabf36b9f4ff7b3a66d9de011ce29fbcbbed1` | docs(feature-002): specify dataset risk scoring and EDA |
| 2026-11-18T20:35:54+01:00 | Isidora Popovic | Isidora Popovic | `80d05971fd3b376125d184ec9fab310edcd564f4` | docs(evidence): record Feature 002 specification commit |
| 2026-11-18T22:27:19+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `3d2991edd017285464b913f5e48a1d09bbb990de` | feat(data): add resumable Feature 002 preparation |
| 2026-11-18T22:29:11+01:00 | Isidora Popovic | Isidora Popovic | `1fb0e8a5789e11c791ed955bbc5a9a2747b4efba` | docs(evidence): record Feature 002 publication |
| 2026-11-19T13:07:38+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `27902a1e5716b9feb0be88108bd8ac246a8347d6` | feat(data): benchmark and prepare local HI-Small snapshot |
| 2026-11-19T13:08:54+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `b1326138944e706ce9b938abddd5b5e8b7f22810` | docs(evidence): refresh Feature 002 handoff and index |
| 2026-11-19T14:30:28+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `c6da2b60d3c7cc9876912c7af4afbb4810309f97` | test(data): add T211 temporal feature RED contracts |
| 2026-11-19T14:39:02+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `70f3019665a3d7b972c90b4d15c87986efa80178` | docs(data): freeze T212 temporal feature protocol |
| 2026-11-19T14:45:19+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `84e538a3f63181e97865147d4e46bc0cf6544268` | feat(data): implement T213 temporal feature kernel |
| 2026-11-19T14:49:25+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `10aed303e9330e1be655eb04e4a2323174dd2657` | test(data): add T214 partition RED contracts |
| 2026-11-19T14:58:33+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `7edc19fc13595e9aa0c910375d6d25f64df3f1ce` | feat(data): implement T215 chronological partition planner |
| 2026-11-19T15:01:08+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `5284c2a97b571b8f00ce6973a73c8e7daaacb632` | test(data): add T216 label-audit RED contracts |
| 2026-11-19T15:08:15+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `a4dca5e041377572a42673936b47e5790398b6d7` | feat(data): implement T217 restricted aggregate label audit |
| 2026-11-19T15:14:22+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `292e9d0aac5d495cd6bd3246167fc51e3fb5d832` | data: freeze T218 count-only UTC partition boundaries |
| 2026-11-19T22:56:15+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `eb10bab91ecb2df23f6f8d6e016677421b291e7d` | data: record T218 aggregate audit and FR-018 stop |
| 2026-11-19T23:01:53+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `41c8acfbf9b9d128ebb36ff77e2a556af3de0109` | feat(data): add fail-closed T219 protocol gate and record partial freeze |
| 2026-11-19T23:11:30+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `937beecaa3ab1c4b8da95933e311ce4a840ccada` | data: freeze T219 partition ID hashes and retain FR-018 stop |
| 2026-11-19T23:31:43+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `2273937913f4bff7ce405bed77d12be0b0be8687` | feat(data): bind T218 exception and artifact hashes in T219 gate |
| 2026-11-20T00:03:22+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `9901bc77ce22ab9d414a30144a437420f9cc1fa0` | docs(training): record T221 protocol proposal |
| 2026-11-20T00:04:18+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `42adea7542718cb6ecb634ab8dd138f9b7b5d4c8` | docs(evidence): record T221 publication |
| 2026-11-20T08:53:29+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `9292c1febcc5045e3a8f183ceaf8e93f3db5f3c4` | test(training): add T220 RED boundary contracts |
| 2026-11-20T09:08:36+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `a460ae108d24a7d994beb1a6f335ca3352127e3b` | docs(training): freeze T221 combined model choices |
| 2026-11-20T09:29:44+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `9b4f26f55078dfd283bc17d91f5a1463399cc966` | Implement T223 train-only baselines |
| 2026-11-20T09:40:56+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `bf20f1c9760ec4ec342dc3caf89a6e43ed2cc66d` | Implement T224 candidate grids without training |
| 2026-11-20T09:49:03+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `838b967294f8c13350c4a2a627c0bf50f28e6e8d` | Add T225 RED evaluation contracts |
| 2026-11-20T09:55:47+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `03c69c296f22132c0ac7208401322aa27ad035ca` | Implement T226 validation evaluation |
| 2026-11-20T10:02:12+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `6dd2cc6923f7945f723b2c45be18c4f37d91e5ff` | Implement trusted LightGBM artifact integrity boundary (T227) |
| 2026-11-20T10:08:10+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `d91be2eee4ffc1defb5576bfa6e9b39ee98819cf` | Record T228 training blockers and local runbook |
| 2026-11-20T15:32:31+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `14fede41d3abaffc0c6f831953a15f59484b3c2f` | Implement IBM day split and local LightGBM pipeline |
| 2026-11-21T14:00:54+01:00 | Elena Kalajdžić | Elena Kalajdžić | `4a28e26b94707b08795840694576602c9f8b79a4` | docs(T219): record macOS resource review candidate |
| 2026-11-21T14:01:35+01:00 | Elena Kalajdžić | Elena Kalajdžić | `29b514233d8e4a6903fdb29dad395c719c097835` | feat(T219,T228): guard Mac fits and verify preflight schema |
| 2026-11-21T14:02:06+01:00 | Elena Kalajdžić | Elena Kalajdžić | `cddc8bb1ec1697722bcb51b2f61ae39329e7b814` | feat(T228): add bounded five-arm numeric diagnostic |
| 2026-11-21T14:02:37+01:00 | Elena Kalajdžić | Elena Kalajdžić | `705b6580c189afe9115d97cdff601b0bdff1d40b` | feat(T224): add guarded cross-family validation comparison |
| 2026-11-21T14:03:01+01:00 | Elena Kalajdžić | Elena Kalajdžić | `ebebdfb32cdca46a039df76a0d3ee48d075858f5` | feat(T229): freeze unweighted model and sealed test predictions |
| 2026-11-21T14:03:19+01:00 | Elena Kalajdžić | Elena Kalajdžić | `c408b6f950a6609917ff9ee51f2cd752e87a7951` | docs(T230): record authorized frozen-model test evaluation |
| 2026-11-21T14:03:57+01:00 | Elena Kalajdžić | Elena Kalajdžić | `2cec92702bc9f0ad8a9b53eae3a177ef392e7c1f` | test(T231): add risk API contract RED cases |
| 2026-11-21T14:05:34+01:00 | Elena Kalajdžić | Elena Kalajdžić | `cd4d92cc68b805b1668b418deec9cada6c117e5a` | feat(T232-T236): integrate trusted opt-in LightGBM risk API |
| 2026-11-21T14:05:48+01:00 | Elena Kalajdžić | Elena Kalajdžić | `25bbe72765ec10c25ff1986a9a7474aa01716952` | test(T237): add Feature 002 decoder RED cases |
| 2026-11-21T14:07:17+01:00 | Elena Kalajdžić | Elena Kalajdžić | `cea1f4746e5e06e2306a80ac5a70a0d256f5c842` | feat(T238-T242): add typed risk UI and aggregate presentation |
| 2026-11-21T14:07:36+01:00 | Elena Kalajdžić | Elena Kalajdžić | `9881239b69cfc2f7addde6fa78559ea1c043143f` | test(T250): add results authorization RED cases |
| 2026-11-21T14:08:56+01:00 | Elena Kalajdžić | Elena Kalajdžić | `d51573d57e7917cd7b53093ce45707b7c12a475a` | feat(T250,T251,T240): gate frozen aggregate results and wire UI |
| 2026-11-21T14:09:26+01:00 | Elena Kalajdžić | Elena Kalajdžić | `8a5c00e09cf5394ddfe0db8af6206dfdeaab7149` | docs(T243): propose bounded read-only EDA page |
| 2026-11-21T14:09:40+01:00 | Elena Kalajdžić | Elena Kalajdžić | `b18594ebacfeddd656a79c0d92102382d4fd4f40` | docs(T252,T253): prepare human review and showcase contract |
| 2026-11-21T14:09:54+01:00 | Elena Kalajdžić | Elena Kalajdžić | `2e4fc4866f34d87afeb77ad6ecf6c1e1cf0a1473` | test(T244): add label-free EDA aggregate RED cases |
| 2026-11-21T14:10:18+01:00 | Elena Kalajdžić | Elena Kalajdžić | `155131dd028ccbee4c7ce2dd9e915243ea7adfd4` | feat(T245): add label-free bounded EDA aggregates |
| 2026-11-21T14:11:00+01:00 | Elena Kalajdžić | Elena Kalajdžić | `599a00f71b10d77fc2048ee76c5c3cb832542bbf` | feat(T246): publish and serve hash-pinned label-free EDA summary |
| 2026-11-21T14:11:15+01:00 | Elena Kalajdžić | Elena Kalajdžić | `b74a244e27b5572b408d2d0f1c92ae8afb1d38d1` | docs(T243): record team approval for dedicated EDA page |
| 2026-11-21T14:11:29+01:00 | Elena Kalajdžić | Elena Kalajdžić | `5ab4ce59f4cd301ab0c99d718a4cbcde91ec9e58` | test(T248): add EDA decoder and UI state RED cases |
| 2026-11-21T14:11:54+01:00 | Elena Kalajdžić | Elena Kalajdžić | `7dc88ca0abba1b15955dee0fdba83f5756d91f49` | feat(T247,T248): add accessible hash-pinned EDA page |
| 2026-11-21T14:12:11+01:00 | Elena Kalajdžić | Elena Kalajdžić | `f848e4a1b706e0381f8d8a0bed74a0452c87134c` | docs(T219,T224,T229,T230): reconcile frozen protocol lineage |
| 2026-11-21T14:13:09+01:00 | Elena Kalajdžić | Elena Kalajdžić | `a844b724888323df1d27d212eb9767b4d088eb21` | test(T249): record full Feature 002 and Foundation regression |
| 2026-11-22T12:31:25+01:00 | milangavric2003 | milangavric2003 | `88cb4541ff6b09e1e81130eef7fa54d4cd379146` | Merge origin/feature/002-clean-start@a844b72 into integration/capstone-mvp |
| 2026-11-22T12:46:11+01:00 | milangavric2003 | milangavric2003 | `361ff5502a19b2ead89d78928cb8f085aa75c700` | Complete offline fixture dependencies from origin/feature03@62f0991 in integration/capstone-mvp |
| 2026-11-22T16:45:28+01:00 | GitHub | Milan Gavrić | `d46699fbd11219ebc92c6ef002d4924a4c7d4b34` | Merge pull request #4 from vekiii/integration/model-rag-handoff |
| 2026-11-22T18:07:56+01:00 | Elena Kalajdžić | Elena Kalajdžić | `08375978b59f40c4623f8dee8100d7ba456c46f1` | docs: record scoped T252 manual review and open criteria |
| 2026-11-22T18:10:37+01:00 | Elena Kalajdžić | Elena Kalajdžić | `a47ce13a6f490de242974d96ccbb1639ce9875c4` | docs: hand off PR 3 review publication and remaining T252 |
| 2026-11-22T20:51:28+01:00 | Veki | Veki | `a6cc9e3bcbb479f275da050483684094c56c8c7f` | feat(T252): add technical findings and reproduction protocols for review |
| 2026-11-22T21:30:30+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `fd030b957b659bd54d768b17cb368ca8dfdaef56` | docs(T252): record user approval attestation and remaining evidence |
| 2026-11-22T21:55:54+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `399c13a6e5f200d1f621832317149a3ba8dd93d7` | docs(T252): record reviewer hash and renewed approval |
| 2026-11-22T22:00:00+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `6e7915713e4505429fc9a81bb2a0d8f7e37abe5e` | docs(T252): record Isidora reply and authorship question |
| 2026-11-22T22:04:20+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `a13a5c1445ccc938d5fa920d9afe80af706c9571` | docs(T252): record reviewer authorship and artifact blocker |
| 2026-11-22T22:14:35+01:00 | Codex | Codex | `76b9e08a7620fbb53feff00a7db872719b37dd1d` | docs: record T252 Windows frozen-input hash receipt |
| 2026-11-22T22:18:14+01:00 | Codex | Codex | `fc724e6d2f0bb9afa9071e47323e364063ecaf43` | docs: record T252 Windows parity input repair |
| 2026-11-22T22:26:08+01:00 | Codex | Codex | `7b5b56cbb4a2fe8d738a8b4e574ee63d051e068e` | docs: record reported Vedran T252 approval scope pending |
| 2026-11-22T22:35:50+01:00 | Codex | Codex | `b925ae5a9bd6a2ce06741366ef321b2dec297d33` | docs: reconcile T252 team approval and execution gates |
| 2026-11-22T22:45:47+01:00 | Codex | Codex | `6938da03d0b74a8f778ee0af80ff6985bf7d1187` | docs: record final team approval and T252 reproduction gap |
| 2026-11-22T22:53:39+01:00 | Codex | Codex | `a737e205f47b36eaa1436c4b294d2a702068bfee` | docs: record T230 snapshot transfer preparation |
| 2026-11-22T22:53:39+01:00 | Codex | Codex | `203e265e7323cc41519629d6c973618a78b5c57e` | docs: record final unweighted LightGBM configuration |

## Branches: current refs and recorded merges

Branch refs below are the local and fetched `origin` refs present on 2026-11-22. A branch being absent from this list does not prove it was deleted. The available reflogs contain no branch-deletion events, so deleted branch names cannot be reliably enumerated from this checkout.

### Current local and remote branch refs

| Ref | Tip commit | Tip committed at (ISO 8601) | Committer | Author | Tip description |
|---|---|---|---|---|---|
| `002-data-and-risk-scoring` | `27ac7d4` | 2026-11-13T14:35:38+01:00 | Elena Kalajdžić | Elena Kalajdžić | fix(feature-002): protect concurrent feature snapshot builds |
| `codex/pr3-final-review` | `6938da0` | 2026-11-22T22:45:47+01:00 | Codex | Codex | docs: record final team approval and T252 reproduction gap |
| `feature/002-clean-start` | `28a938a` | 2026-11-22T22:54:43+01:00 | Codex | Codex | docs: refresh master commit and branch evidence |
| `feature/002-model-development` | `6b05dc4` | 2026-11-18T12:34:48+01:00 | Isidora Popovic | Isidora Popovic | docs(model2): record synthetic contribution ledger |
| `feature/005-real-time-fraud-detection-mlops-spec` | `1401889` | 2026-11-17T16:30:22+01:00 | Isidora Popovic | Isidora Popovic | style(web): refine overview hero typography |
| `feature/006-security-edge-case-audit` | `ab692c6` | 2026-11-22T23:52:31+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | test(security): audit integrated MVP boundaries |
| `initialization` | `f37e67a` | 2026-11-12T23:53:43+01:00 | Isidora Popovic | Isidora Popovic | docs(evidence): record session publication ledger |
| `ls` | `f37e67a` | 2026-11-12T23:53:43+01:00 | Isidora Popovic | Isidora Popovic | docs(evidence): record session publication ledger |
| `main` | `b03e8e3` | 2026-11-11T16:19:45+01:00 | Veki | Veki | initial idea |
| `model-implementations` | `9f72895` | 2026-11-16T08:37:16+01:00 | Isidora Popovic | Isidora Popovic | docs: update next work agreement handoff |
| `model2` | `6b05dc4` | 2026-11-18T12:34:48+01:00 | Isidora Popovic | Isidora Popovic | docs(model2): record synthetic contribution ledger |
| `origin` | `0fbe313` | 2026-11-13T14:34:36+01:00 | Veki | Veki | last update |
| `origin/002-data-and-risk-scoring` | `27ac7d4` | 2026-11-13T14:35:38+01:00 | Elena Kalajdžić | Elena Kalajdžić | fix(feature-002): protect concurrent feature snapshot builds |
| `origin/004-simulation-and-prioritization` | `45a375f` | 2026-11-19T05:36:50+01:00 | milangavric2003 | milangavric2003 | T020-T021; feature 04 finished |
| `origin/006-capstone-evaluation` | `3eee1d6` | 2026-11-22T21:35:14+01:00 | Veki | Veki | feat(feature-006): update evidence map and release candidate documentation for clarity and accuracy |
| `origin/codex/pr3-final-review` | `6938da0` | 2026-11-22T22:45:47+01:00 | Codex | Codex | docs: record final team approval and T252 reproduction gap |
| `origin/feature/002-clean-start` | `a844b72` | 2026-11-21T14:13:09+01:00 | Elena Kalajdžić | Elena Kalajdžić | test(T249): record full Feature 002 and Foundation regression |
| `origin/feature/005-real-time-fraud-detection-mlops-spec` | `1401889` | 2026-11-17T16:30:22+01:00 | Isidora Popovic | Isidora Popovic | style(web): refine overview hero typography |
| `origin/feature03` | `62f0991` | 2026-11-18T16:34:25+01:00 | Veki | Veki | T101 finished |
| `origin/feature03-reliability-v2` | `9202964` | 2026-11-16T08:38:08+01:00 | milangavric2003 | milangavric2003 | Record final recovery results and prepare joint merge review |
| `origin/feature03-retrieval-v3` | `8ca4ba8` | 2026-11-17T13:41:57+01:00 | Veki | Veki | T096 finished |
| `origin/feature03-retrieval-v4` | `5431299` | 2026-11-18T06:19:33+01:00 | milangavric2003 | milangavric2003 | T098 finished; producer integration and history index verified |
| `origin/initialization` | `f37e67a` | 2026-11-12T23:53:43+01:00 | Isidora Popovic | Isidora Popovic | docs(evidence): record session publication ledger |
| `origin/integration/003-investigation-web` | `71f34dd` | 2026-11-19T12:17:53+01:00 | Veki | Veki | feature03 integration into front |
| `origin/integration/004-simulation-web` | `8d964bf` | 2026-11-19T10:28:17+01:00 | Veki | Veki | simulation lab integration into front |
| `origin/integration/capstone-mvp` | `d46699f` | 2026-11-22T16:45:28+01:00 | GitHub | Milan Gavrić | Merge pull request #4 from vekiii/integration/model-rag-handoff |
| `origin/integration/model-rag-handoff` | `40ce7e3` | 2026-11-22T16:39:05+01:00 | milangavric2003 | milangavric2003 | Record PR 4 Windows review and verification |
| `origin/main` | `0fbe313` | 2026-11-13T14:34:36+01:00 | Veki | Veki | last update |
| `origin/model-implementations` | `93d387e` | 2026-11-16T21:49:06+01:00 | Elena Kalajdžić | Elena Kalajdžić | feat(feature-002): publish isolated boosted daily cap and team handoff |
| `origin/model2` | `b09e422` | 2026-11-18T11:47:02+01:00 | Isidora Popovic | Isidora Popovic | docs(evidence): record model2 push receipt |
| `origin/pr/3` | `d46699f` | 2026-11-22T16:45:28+01:00 | GitHub | Milan Gavrić | Merge pull request #4 from vekiii/integration/model-rag-handoff |

### Merge commits

| Committed at (ISO 8601) | Committer | Author | Commit | Description |
|---|---|---|---|---|
| 2026-11-13T14:05:04+01:00 | Veki | Veki | `b9650a1ccfbfe84c8f73e7da46caf351fddbccff` | Merge verified initialization foundation into main |
| 2026-11-18T19:14:33+01:00 | git stash | git stash | `81962309387d3749dde8b3cee7ffc336c85dec60` | On feature/002-model-development: preserve Feature 002 work before clean restart |
| 2026-11-22T12:31:25+01:00 | milangavric2003 | milangavric2003 | `88cb4541ff6b09e1e81130eef7fa54d4cd379146` | Merge origin/feature/002-clean-start@a844b72 into integration/capstone-mvp |
| 2026-11-22T16:45:28+01:00 | GitHub | Milan Gavrić | `d46699fbd11219ebc92c6ef002d4924a4c7d4b34` | Merge pull request #4 from vekiii/integration/model-rag-handoff |

Merge commits identify the receiving-side event recorded in Git. The `git stash` row is a stash object with multiple parents, not a branch integration. For a branch not represented by a merge commit, the current graph may still include its work via fast-forward or squash; the available local metadata cannot establish deleted-branch history.

## Complete commit history

All commits reachable from any local or fetched remote ref in this checkout, oldest first (305 commits at update time). The branch refs above identify current branch tips; commit presence does not mean a commit is unique to one branch.

| Committed at (ISO 8601) | Committer | Author | Commit | Description |
|---|---|---|---|---|
| 2026-11-11T16:19:45+01:00 | Veki | Veki | `b03e8e3b9b5a4234beb2fcc15fecf3b1507df737` | initial idea |
| 2026-11-11T16:55:15+01:00 | Veki | Veki | `f86aff0f1e7a2d6344ca07f9c437188286418015` | feature 1 implementation: constitution; specification; technical plan; API and JSON; Tasks; Quickstart |
| 2026-11-11T17:08:59+01:00 | Veki | Veki | `e62c4fe108b9cf9ee1052c8ed130c44c386855ff` | tasks prompt generator |
| 2026-11-11T17:31:42+01:00 | Veki | Veki | `0aa7328827a7b3006ca8bef26aa3985f008b2e6a` | T001-T005 |
| 2026-11-11T17:53:54+01:00 | Veki | Veki | `25cbd17a7a8b455a5439442009f44de972f5d1d8` | add next_work.md |
| 2026-11-12T10:52:56+01:00 | Veki | Veki | `5d602521e9b430ae3da3e408c55fadaf9ecfa06e` | T006-T007 |
| 2026-11-12T11:11:43+01:00 | Veki | Veki | `56aaa1060e1671f2c281a8d384f5ec7ac235d343` | T008-T011 |
| 2026-11-12T15:52:45+01:00 | Isidora Popovic | Isidora Popovic | `fe187a66431f32d9fed65baf9f3c5f8e30774beb` | test(backend): define US2 case API and fixture scorer expectations |
| 2026-11-12T15:52:46+01:00 | Isidora Popovic | Isidora Popovic | `2ff3d84e8540cbb5d990d4340096ada24b78d43d` | feat(frontend): validate case API responses and request lifecycle |
| 2026-11-12T15:52:46+01:00 | Isidora Popovic | Isidora Popovic | `8e99ee0cefe8bc5d516a4b937ec19712734470bf` | test(frontend): define US2 fetch and case inspection behaviors |
| 2026-11-12T15:52:46+01:00 | Isidora Popovic | Isidora Popovic | `ff4406e2f896b2432089567e1951e4c7133c329b` | feat(backend): serve validated synthetic cases with deterministic scoring |
| 2026-11-12T15:52:47+01:00 | Isidora Popovic | Isidora Popovic | `d7c3bb72a65708889ae137181dda17e8640dcb84` | feat(frontend): add synthetic case inspection UI |
| 2026-11-12T15:53:35+01:00 | Isidora Popovic | Isidora Popovic | `549f304a44157caeb7f18e7996e41c0bc966d978` | docs(us2): record integrated verification and current acceptance limits |
| 2026-11-12T15:54:18+01:00 | Isidora Popovic | Isidora Popovic | `3c786fbd16c9fd3909dc1e54c4858cd830e541bf` | docs: record successful US2 publication |
| 2026-11-12T16:52:13+01:00 | Veki | Veki | `f17ff8ff3a29ac00679bae089cdefd62ab2f846c` | did T019 |
| 2026-11-12T18:54:46+01:00 | milangavric2003 | milangavric2003 | `6a99ef6dd6b0851b472d58021cd96d887b14a286` | phase-05 |
| 2026-11-12T20:48:54+01:00 | Veki | Veki | `733bff2746a7db4f0bd8be65cd3fd6ee717ba19b` | T024-T027; without T025 |
| 2026-11-12T21:14:26+01:00 | Veki | Veki | `33bcf628ec4325d386117f72378e79835194e772` | T025 and T028 finish |
| 2026-11-12T21:39:12+01:00 | Veki | Veki | `f63bffe490358a4fba06d27b896d42c5e81bf882` | feature 02 created |
| 2026-11-12T23:50:15+01:00 | Isidora Popovic | Isidora Popovic | `6b69ae2e38053a3727647eb868655ed1f77164b0` | docs(evidence): document historical contributions and time estimate |
| 2026-11-12T23:51:05+01:00 | Isidora Popovic | Isidora Popovic | `5eb0d10cc7c2da724902e27329832455f58ed4fd` | docs(feature-002): strengthen risk-scoring specification after review |
| 2026-11-12T23:52:15+01:00 | Isidora Popovic | Isidora Popovic | `7957844bf328c2d164bcbb09ec5c1ed821564809` | docs(feature-002): add technical plan and Codex work prompts |
| 2026-11-12T23:53:43+01:00 | Isidora Popovic | Isidora Popovic | `f37e67a554395b564feadbd8d39a2ea151993a94` | docs(evidence): record session publication ledger |
| 2026-11-13T04:03:56+01:00 | milangavric2003 | milangavric2003 | `3568c7dc9b5c4fe55286dd8b8c583650f41c265c` | docs(feature-002): generate implementation tasks (Prompt 0) |
| 2026-11-13T05:30:41+01:00 | milangavric2003 | milangavric2003 | `63d33843bc6483d66362e10133ec21c261c76df1` | feat(feature-002): implement source inspection (Prompt 1, T001–T005) |
| 2026-11-13T06:34:14+01:00 | milangavric2003 | milangavric2003 | `182d0b290c8819e602fc5d77e8df8e904228b032` | feat(feature-002): resolve source and contract issues (Prompt 1); T006 complete; T007/T008 await producer/consumer review. |
| 2026-11-13T09:42:24+01:00 | Isidora Popovic | Isidora Popovic | `dab61f36e36fa07f3b72c6d41b8ea7d94116d043` | docs(feature-002): record collective T007/T008 approval |
| 2026-11-13T09:43:36+01:00 | Isidora Popovic | Isidora Popovic | `ae98c63262b0b231f17a55a9b8ee399f62747270` | docs(evidence): attribute collective approval and effort |
| 2026-11-13T09:45:55+01:00 | Isidora Popovic | Isidora Popovic | `6952f1d90b72cac00983449b1e96079b42a7eb72` | docs(evidence): finalize approval publication ledger |
| 2026-11-13T10:41:00+01:00 | Elena Kalajdžić | Elena Kalajdžić | `b5f75211c9a6aa5befa602f04308918df98ac106` | feat(feature-002): complete and verify local dataset import |
| 2026-11-13T11:20:52+01:00 | Elena Kalajdžić | Elena Kalajdžić | `55306089b506458fcaec9b621f49c00dd971d46e` | fix(feature-002): finalize phase 3 import verification and docs |
| 2026-11-13T14:05:04+01:00 | Veki | Veki | `b9650a1ccfbfe84c8f73e7da46caf351fddbccff` | Merge verified initialization foundation into main |
| 2026-11-13T14:23:37+01:00 | Elena Kalajdžić | Elena Kalajdžić | `0f5ad9ac0b04cc406e3c19b0f1934da4cc29d10d` | feat(feature-002): complete feature replay and rules baseline |
| 2026-11-13T14:34:36+01:00 | Veki | Veki | `0fbe31315052542575b22515c83b0a062efeaa31` | last update |
| 2026-11-13T14:35:38+01:00 | Elena Kalajdžić | Elena Kalajdžić | `27ac7d49e3d638717c752dce225216d291bf9e87` | fix(feature-002): protect concurrent feature snapshot builds |
| 2026-11-13T16:05:55+01:00 | Isidora Popovic | Isidora Popovic | `fe310c1a7213655b47cc2ffb22554fc39b4e2acf` | test(ml): add RED chronological evaluation protocol tests |
| 2026-11-13T16:15:00+01:00 | Isidora Popovic | Isidora Popovic | `a2857cdfce02b9d60b2b8c3c276a2500081cbad5` | feat(ml): implement immutable temporal evaluation protocol |
| 2026-11-13T17:27:44+01:00 | Isidora Popovic | Isidora Popovic | `d606fb7137be1c4f43cce6b89c8c89d350054862` | chore(ml): record locked dependencies and resource pilot |
| 2026-11-13T18:22:05+01:00 | Isidora Popovic | Isidora Popovic | `b8643a42b7a1bed8f5b9199ddb31826c34d3591e` | docs(ml): prepare pretrained model integration branch |
| 2026-11-13T18:34:27+01:00 | Isidora Popovic | Isidora Popovic | `87b69806d02e1f51902b00172a485490fcc645ba` | docs(ml): assess pretrained model artifacts and input compatibility |
| 2026-11-13T18:38:36+01:00 | Isidora Popovic | Isidora Popovic | `13472f9058079687cf4ae4ce159db9286fdcb039` | docs(ml): define gated pretrained inference architecture |
| 2026-11-13T19:21:00+01:00 | Isidora Popovic | Isidora Popovic | `c872375e3457bf16a148541c407063a02615553a` | docs(ml): switch pretrained candidate to IBM AML LightGBM |
| 2026-11-13T20:21:47+01:00 | Isidora Popovic | Isidora Popovic | `81b3b9a46c99ca7dceee4e7517b441ea97f42c1f` | test(ml): add RED IBM pretrained inference tests |
| 2026-11-13T21:02:46+01:00 | Isidora Popovic | Isidora Popovic | `79987df7723e892fc6797acb1ee2981c383a0a8b` | test(ml): align pretrained loader RED tests with IBM model |
| 2026-11-13T21:14:13+01:00 | Isidora Popovic | Isidora Popovic | `f426cec2e759a325a64e4058537ca95d94c8e2c4` | test(ml): add RED IBM pretrained inference tests |
| 2026-11-13T21:16:56+01:00 | Isidora Popovic | Isidora Popovic | `92bdd79dbbfd11a2d43567296d114a51a5725dd6` | docs(ml): record blocked IBM pretrained inference gate |
| 2026-11-13T21:20:13+01:00 | Isidora Popovic | Isidora Popovic | `429d6ec8c9b15a4a2e5cc223aa0005ab42a97c2d` | docs(ml): record pretrained inference verification gate |
| 2026-11-13T21:24:13+01:00 | Isidora Popovic | Isidora Popovic | `07cce92cc5924cb6c3bd66888c14b165f618e3af` | fix(data): preserve approved mapping bytes on Windows |
| 2026-11-13T21:28:14+01:00 | Isidora Popovic | Isidora Popovic | `570b34491afc3da723864a6e1d6279386ce6cc63` | docs(ml): finalize IBM pretrained inference handoff |
| 2026-11-13T22:01:41+01:00 | Isidora Popovic | Isidora Popovic | `ddf5ceb1894843bde07c9e36b4816702f04e0a5e` | docs(ml): reconcile pretrained model gate evidence |
| 2026-11-13T22:01:54+01:00 | Isidora Popovic | Isidora Popovic | `24a44c209552415219c5137465267fb9f953ea47` | docs: record phase 5 contribution handoff |
| 2026-11-13T22:03:05+01:00 | Isidora Popovic | Isidora Popovic | `a031b16978fe1b80dbc20cd95cd03d87bb673d00` | docs(evidence): record phase 5 contribution ledger |
| 2026-11-13T22:11:15+01:00 | Isidora Popovic | Isidora Popovic | `2dd815d85bfc9c2fc70a28baef9c142d551e57e0` | docs(ml): verify IBM source mapping gate |
| 2026-11-13T22:18:56+01:00 | Isidora Popovic | Isidora Popovic | `86d4fbbbfdfa4cae2590c6e304cb4566af3ab1aa` | docs(ml): verify pretrained graph compatibility |
| 2026-11-13T22:22:15+01:00 | Isidora Popovic | Isidora Popovic | `60d575d480284fec32f53e72dc1565880f924048` | docs(ml): record blocked pretrained loader gate |
| 2026-11-13T22:25:33+01:00 | Isidora Popovic | Isidora Popovic | `1a770a592f91cdcf26e57cdb3babc29af9b51c80` | test(ml): add RED IBM pretrained inference tests |
| 2026-11-13T22:27:01+01:00 | Isidora Popovic | Isidora Popovic | `c9edcefc061956536666fdc9b5ba2169f10ab1fd` | docs(ml): record blocked IBM inference smoke |
| 2026-11-13T22:29:50+01:00 | Isidora Popovic | Isidora Popovic | `59acd2004fe6b42fd59dc2d64d05af39e5dd7fdd` | docs(ml): audit pretrained evaluation independence |
| 2026-11-13T22:32:46+01:00 | Isidora Popovic | Isidora Popovic | `8ac9bccdd08a8d5a2018b3e9413e75e9e72e8138` | docs(ml): reconcile pretrained Phase 5 handoff |
| 2026-11-13T22:44:01+01:00 | Isidora Popovic | Isidora Popovic | `c8a8dd61b3485ae7cb9b99a1da1825f791ad527e` | docs(ml): audit replacement pretrained models |
| 2026-11-13T22:48:00+01:00 | Isidora Popovic | Isidora Popovic | `49712efd4437ba4e601c6e989952cb4fbf3d9175` | docs(ml): propose inference-only Phase 5 scope |
| 2026-11-13T22:51:12+01:00 | Isidora Popovic | Isidora Popovic | `c30a6aca3d6dbbb74ab92d102427a43f48584b8f` | docs(ml): record pretrained artifact freeze blocker |
| 2026-11-13T23:01:19+01:00 | Veki | Veki | `224bde1837ce5e8eaefad71a6f43c56b8a516b4c` | feature03 initialized |
| 2026-11-13T23:20:27+01:00 | Veki | Veki | `fd6d724b83a3a35cee9bf821651e56ffc269b2f9` | feature03 plan and tasks |
| 2026-11-13T23:50:01+01:00 | Veki | Veki | `6db94af3471a9007a8a0d88cba8c7ece32886483` | T001-T004 |
| 2026-11-14T00:13:12+01:00 | Veki | Veki | `83b587bcc17f8ad703ea67ca593b3785d7fc4391` | T005-T012 |
| 2026-11-14T01:01:10+01:00 | Veki | Veki | `47c1a96e36777cd89a17299e06871df7b983346b` | T013 - T022; not all finished |
| 2026-11-14T11:23:17+01:00 | Isidora Popovic | Isidora Popovic | `cab42fd047c336054da88f28f011e3615094fceb` | docs(ml): preserve IBM tree notebook and reproduction request |
| 2026-11-14T11:23:27+01:00 | Isidora Popovic | Isidora Popovic | `6f7bcb70af2642fc20943e66a6f6f2c7ff4dcc5d` | feat(ml): reproduce IBM tree experiment with offline scoring |
| 2026-11-14T11:24:15+01:00 | Isidora Popovic | Isidora Popovic | `fb32b8c8467bb5cffe6b4cbc57730b484af1b1db` | docs(ml): record tree experiment results and commit handoff |
| 2026-11-14T11:25:55+01:00 | milangavric2003 | milangavric2003 | `27ecc387256fa9fdd7b49525fbe29fec3d164e1b` | T013 finished; all six knowledge documents reviewed and approved |
| 2026-11-14T11:40:26+01:00 | milangavric2003 | milangavric2003 | `1a99c340d3e7ef96e73cb51191a34302cd58a728` | T015-T022 finished; feature03 phase 3 complete |
| 2026-11-14T14:04:45+01:00 | milangavric2003 | milangavric2003 | `fece114e03f95445161c25033625b6bb536585c1` | T023-T030 offline implementation; phase 4 incomplete, SDK installation blocked |
| 2026-11-14T14:44:17+01:00 | Elena Kalajdžić | Elena Kalajdžić | `c88c684f3b9be96b50124b067ff4848f518da4d9` | feat(feature-002): publish history-v1 scoring and exploratory evaluation |
| 2026-11-14T21:04:15+01:00 | Elena Kalajdžić | Elena Kalajdžić | `2099c7e50beb28e69c2e815154ab4233cd975487` | feat(feature-002): add boosted scorer and document full-run validation |
| 2026-11-15T00:11:47+01:00 | milangavric2003 | milangavric2003 | `8334b8900da8cc415126229f92fe17f84828e8a3` | T031-T038 offline implementation; phase 4 offline complete, T033 pending |
| 2026-11-15T06:19:20+01:00 | milangavric2003 | milangavric2003 | `093739fc058afe7a2f2363244dcf36093a662626` | feat(investigation): load local env and record T033 probe rejection |
| 2026-11-15T06:48:16+01:00 | milangavric2003 | milangavric2003 | `fcdf5283a485c67532b2d0564025b238ce4c6d13` | T039-T044 finished; feature03 phase 5 offline complete, T033 capability gate pending |
| 2026-11-15T07:12:47+01:00 | milangavric2003 | milangavric2003 | `db02fa526c9ccf51db9aedd0c5eb9cf2bc3e47f2` | T045-T050 finished; feature03 phase 6 offline implemented, T051 human confirmation and T033 pending |
| 2026-11-15T08:03:40+01:00 | milangavric2003 | milangavric2003 | `c8590b9ad59d84d1954f42f9401baa450a374ca1` | T052 evaluation pack prepared; independent human review and freeze pending, T051 and T033 remain open |
| 2026-11-15T09:55:06+01:00 | Isidora Popovic | Isidora Popovic | `8bd9ce52d6eb98abe772a5a4fbc06416cf108917` | docs(t065): review five model explanations |
| 2026-11-15T10:00:03+01:00 | Isidora Popovic | Isidora Popovic | `04b7a14b697773c4e8bdd06230b17c95fea47490` | test(t066): reproduce model evaluation run |
| 2026-11-15T10:07:54+01:00 | Isidora Popovic | Isidora Popovic | `cbc25b0742b83b4c8acf036a7ae81c1b0559c9de` | docs(feature-002): record access approval |
| 2026-11-15T10:47:53+01:00 | Isidora Popovic | Isidora Popovic | `154ecad932853ce35980a1467b5cafa4c18104d0` | chore(env): configure reproducible Python and SQLite environment |
| 2026-11-15T11:06:30+01:00 | Isidora Popovic | Isidora Popovic | `bc5382b2a31b3be7ddb63688d86a18141069999c` | docs(model): document training, evaluation, and application integration |
| 2026-11-15T11:07:35+01:00 | Isidora Popovic | Isidora Popovic | `123f9cc5fa2e72d4d582ffd064fab3dce4e3d736` | docs(evidence): attribute model and verification commits |
| 2026-11-15T12:07:40+01:00 | Isidora Popovic | Isidora Popovic | `e93540f89907e71ea6fa2c90e551ede48c76667a` | docs(feature-005): specify streaming fraud detection and MLOps |
| 2026-11-15T12:09:20+01:00 | Isidora Popovic | Isidora Popovic | `054cf4451245dbea0036b316f43a7339a6280bc6` | docs(evidence): record feature-005 specification publication |
| 2026-11-15T12:38:59+01:00 | Veki | Veki | `0dd452468cded16c317567460d1dc808daecfc6b` | T051 update and review |
| 2026-11-15T13:21:53+01:00 | Veki | Veki | `382e0609f73077cb6c53288f2e607c9194e04d51` | T052 finish |
| 2026-11-15T13:38:04+01:00 | Isidora Popovic | Isidora Popovic | `d39962c91dbcee3602dc00d06a47411dbfdbdcb4` | docs(feature-005): record pending T001 scope decision |
| 2026-11-15T13:39:25+01:00 | Isidora Popovic | Isidora Popovic | `04f612403e5989cd446dedc0e39308db5ffb3790` | docs(evidence): update feature-005 T001 contribution ledger |
| 2026-11-15T13:50:07+01:00 | Isidora Popovic | Isidora Popovic | `496025e15ef4293e904870bd9e6fed714e8fa8c5` | fix(feature-002): preserve frozen protocol bytes on Windows |
| 2026-11-15T13:59:31+01:00 | Veki | Veki | `875f9a2922982fd2529ffe3a763ec52eb1c4bc1d` | T053 finish; T054, T057, T060 and T061 partialy |
| 2026-11-15T14:16:23+01:00 | Veki | Veki | `1c76674ea21fc5229972d033b1b35b2a9437fdcf` | T054-T056 finished |
| 2026-11-15T14:32:52+01:00 | Veki | Veki | `cf218b0359cededfb2e201fd251b5361cb4c5d03` | T057 finished |
| 2026-11-15T14:53:51+01:00 | Veki | Veki | `9796902f3b1b4c8670a1f7e15213b9e34678bf26` | T033 fnished |
| 2026-11-15T15:30:30+01:00 | Isidora Popovic | Isidora Popovic | `c1c5a5dbfd4ac9b895ae349e7dffc991cea33673` | docs(t065): verify five source and history fact checks |
| 2026-11-15T15:30:59+01:00 | Isidora Popovic | Isidora Popovic | `c4aaf419ac6b8bf13b64b9dabdee62867cd9a601` | test(feature-002): harden validation boundaries |
| 2026-11-15T15:32:47+01:00 | Isidora Popovic | Isidora Popovic | `d9bd8a2e3629a2d3939fc5507583f310428c53ac` | docs(evidence): record feature-002 publication ledger |
| 2026-11-15T16:29:31+01:00 | Isidora Popovic | Isidora Popovic | `57d3bce90ac562eafe64084bd14bfdf34a322071` | feat(overview): add read-only dataset aggregates |
| 2026-11-15T16:29:42+01:00 | Isidora Popovic | Isidora Popovic | `8b84323b7271db55195c50726f352272315e49ff` | feat(frontend): add responsive dataset and model overview |
| 2026-11-15T16:29:53+01:00 | Isidora Popovic | Isidora Popovic | `a0b3a69e4c31574b64b89e9a3b12270f9f379167` | docs(overview): record verification and screenshots |
| 2026-11-15T16:30:15+01:00 | Isidora Popovic | Isidora Popovic | `010e669c009acc9fa14b724c1383fff96fadcdd8` | docs(overview): record verification and screenshots |
| 2026-11-15T16:30:15+01:00 | Isidora Popovic | Isidora Popovic | `63b89add15a2833d718889f4c320f640d3fc6d81` | feat(frontend): add responsive dataset and model overview |
| 2026-11-15T16:30:15+01:00 | Isidora Popovic | Isidora Popovic | `9a6a2b89845f4ea430fcd61dda49c6a912d99db7` | feat(overview): add read-only dataset aggregates |
| 2026-11-15T16:33:29+01:00 | Isidora Popovic | Isidora Popovic | `b16d23583abfefe30ba2f2beee9f1f4873d7f39b` | docs(evidence): record dashboard branch attribution |
| 2026-11-15T17:21:01+01:00 | Isidora Popovic | Isidora Popovic | `61b4daa1d6bfe78290fc28d765bf362f12aaf543` | fix(overview): validate UTC timestamps in chart aggregation |
| 2026-11-15T17:21:10+01:00 | Isidora Popovic | Isidora Popovic | `0ed42334ef161074f2a34571cc8a0183dc233c26` | docs(overview): record real-data verification evidence |
| 2026-11-15T17:21:19+01:00 | Isidora Popovic | Isidora Popovic | `9454bfc42bc6d954e916c777c30cac499df1a94d` | docs(overview): update real-data verification handoff |
| 2026-11-15T17:21:35+01:00 | Isidora Popovic | Isidora Popovic | `55f02b0a33fb9df27b17868330f0333a940651ad` | fix(overview): validate UTC timestamps in chart aggregation |
| 2026-11-15T17:21:35+01:00 | Isidora Popovic | Isidora Popovic | `799ebe8c08b2119dbbde02b48544d6d5a1196bc5` | docs(overview): record real-data verification evidence |
| 2026-11-15T17:24:07+01:00 | Isidora Popovic | Isidora Popovic | `ccb62809e6117bf6869df5a9fa6d87bbca4862a2` | docs(evidence): record real-data verification provenance |
| 2026-11-15T17:24:31+01:00 | Veki | Veki | `0829296f2824764c3773f6c8e90eb94d39843455` | T058 finished |
| 2026-11-15T17:25:34+01:00 | Isidora Popovic | Isidora Popovic | `2a5b769c8939223ac7ed80dd256e4f40a1695b08` | docs(evidence): record feature branch push receipt |
| 2026-11-15T17:59:50+01:00 | Veki | Veki | `aaabd8dec787d83e1b50bc2972e8182162ca6225` | T065 finished; others half finished |
| 2026-11-15T23:18:59+01:00 | Veki | Veki | `cd98ea021a38b362b5766c4e23a1e55ec0ad0dcd` | T059-T061 finished |
| 2026-11-16T02:19:47+01:00 | milangavric2003 | milangavric2003 | `7ed606c91c0bdc8b44c7318d1ad1d87e8d1bc31e` | Improve investigation reliability and add development checks |
| 2026-11-16T02:29:09+01:00 | milangavric2003 | milangavric2003 | `103c3c04cb7fed4935e4449626dd7bcda01d5c6f` | Freeze bounded live development evaluation protocol |
| 2026-11-16T02:35:21+01:00 | milangavric2003 | milangavric2003 | `46a15edf4de4a05df625891b978bc03c9fed0a90` | Record actual LLM development outcomes and audit |
| 2026-11-16T07:24:57+01:00 | milangavric2003 | milangavric2003 | `eedbe72f5f6b814a5a7bbf1b8d0e7deb006e2262` | Improve bounded timeout recovery and calibrate development report judging |
| 2026-11-16T07:43:33+01:00 | milangavric2003 | milangavric2003 | `4262193b8e279c129386804ad6288f8c98b0becc` | Fit investigation repair within input limit by sharing claim schema |
| 2026-11-16T08:01:29+01:00 | milangavric2003 | milangavric2003 | `af8fe4b1d5bbe9d367981fa046bb57c3274a5be4` | Record calibrated live report and controlled repair evaluation |
| 2026-11-16T08:16:39+01:00 | milangavric2003 | milangavric2003 | `1936d233f13b81ff44e4972a8b9db1c5a3729ac9` | Require versioned human authority notice with bounded draft repair |
| 2026-11-16T08:32:23+01:00 | milangavric2003 | milangavric2003 | `dd140af841febd49e4df8a9cab17d6d5fb9be9a8` | Freeze final bounded reliability verification before joint merge review |
| 2026-11-16T08:37:16+01:00 | Isidora Popovic | Isidora Popovic | `9f728957b68528864421745a46842339ef94c897` | docs: update next work agreement handoff |
| 2026-11-16T08:38:08+01:00 | milangavric2003 | milangavric2003 | `920296436643e2c25ca27fc19441ecedf7e078c6` | Record final recovery results and prepare joint merge review |
| 2026-11-16T08:45:22+01:00 | milangavric2003 | milangavric2003 | `1f3a09d229a20966df36342bd92dec4b3110f9bf` | Record reliability merge and resume feature03 handoff |
| 2026-11-16T09:22:46+01:00 | Isidora Popovic | Isidora Popovic | `024956d8579a9eeb9cbba290c54d9ea273842381` | docs(feature-005): add RAG and showcase phase |
| 2026-11-16T09:24:42+01:00 | Isidora Popovic | Isidora Popovic | `4c4ff94a133c5c166c54978f7635f60c3c08a75e` | docs(evidence): record Phase 7 publication |
| 2026-11-16T11:42:55+01:00 | Isidora Popovic | Isidora Popovic | `c09e9646a030ebd58aa98895cade477f1ec9d38c` | docs(feature-005): record scope and team decisions |
| 2026-11-16T11:43:19+01:00 | Isidora Popovic | Isidora Popovic | `ec43eccc02e55e0412f95dc88bb2f85db1c04b60` | feat(feature-005): add immutable live transaction store |
| 2026-11-16T11:43:31+01:00 | Isidora Popovic | Isidora Popovic | `a4553f164d5c30e407f127179383d77a3438595d` | feat(web): build Feature 005 showcase foundation |
| 2026-11-16T11:43:44+01:00 | Isidora Popovic | Isidora Popovic | `57ce87f2d40b42c163e3c2b7efa6e4ab586363ca` | docs(feature-002): save protocol audit working artifacts |
| 2026-11-16T11:44:18+01:00 | Isidora Popovic | Isidora Popovic | `2e2963b209b2a839a22a1c06140690e9f6106cd7` | docs: update handoff with phase 4 dependency gate |
| 2026-11-16T11:45:43+01:00 | Isidora Popovic | Isidora Popovic | `487c427ea50e169f5e36898420d659f05ead2c60` | docs: record branch publication in project ledger |
| 2026-11-16T12:08:19+01:00 | Isidora Popovic | Isidora Popovic | `52d91597d2d77c6bbd72062366bec7cbb44973ea` | test(security): audit Feature 005 security and edge cases |
| 2026-11-16T13:28:11+01:00 | Veki | Veki | `987b64cf8717a18eafc95c2dbcbc3655c9d6898c` | T062-T064 finished |
| 2026-11-16T15:56:51+01:00 | Veki | Veki | `2469aec0b146c5c26cb5c0eea70cb96bb9c559e3` | Update T066 handoff details and clarify user self-review process |
| 2026-11-16T16:25:43+01:00 | Isidora Popovic | Isidora Popovic | `827779db3c1ef049acd1ddf401a4aafbc1615848` | test(security): harden local API and PostgreSQL fixtures |
| 2026-11-16T16:25:53+01:00 | Isidora Popovic | Isidora Popovic | `5ea0c4c01ef717b6f7b99b98f11c19a202b62d2e` | fix(security): add API protections and browser CSP checks |
| 2026-11-16T16:27:22+01:00 | Isidora Popovic | Isidora Popovic | `4b41608eba2fea573fd94d8aed32ccd995312aad` | docs(security): record verification and commit attribution |
| 2026-11-16T16:28:05+01:00 | Isidora Popovic | Isidora Popovic | `e7ae0ece89ff00c6103880b4cd59b80a20e3bc8c` | docs: record security branch publication receipt |
| 2026-11-16T16:28:49+01:00 | Isidora Popovic | Isidora Popovic | `9d62b10d31b8250f77eb4edc4c6d935cf3da5972` | docs: reconcile security publication handoff |
| 2026-11-16T21:49:06+01:00 | Elena Kalajdžić | Elena Kalajdžić | `93d387e573d5c288f41ab6c38d30aa837b69987c` | feat(feature-002): publish isolated boosted daily cap and team handoff |
| 2026-11-17T02:48:17+01:00 | milangavric2003 | milangavric2003 | `dab0fb424041aa1d4a4bbd6a89044ea8a418a981` | T066-T067 finished; remaining Feature 003 work documented |
| 2026-11-17T02:48:54+01:00 | milangavric2003 | milangavric2003 | `95b5eebe5e3a50583ffcf33b081d2c7e53755681` | Record Feature 003 review publication and next steps |
| 2026-11-17T04:39:32+01:00 | milangavric2003 | milangavric2003 | `c255fa8e8a93d95d5c6c7f97890e90c5ace6059c` | T099-T100 finished; history labels and current API contract documented |
| 2026-11-17T04:40:47+01:00 | milangavric2003 | milangavric2003 | `249a50baae8fa4d3b2b560777da6dae8efd2acd7` | Record T099-T100 verification and publication blocker |
| 2026-11-17T04:56:19+01:00 | milangavric2003 | milangavric2003 | `18e930ab4ad86e75f6f908b4a40a0a87def20e5b` | Record T095 development design and pending evaluation review |
| 2026-11-17T05:44:28+01:00 | milangavric2003 | milangavric2003 | `cc712513d3a30286c23a9f1059aaffaa5dbae79e` | Implement T095 fresh retrieval evaluator and development review packet |
| 2026-11-17T06:04:35+01:00 | milangavric2003 | milangavric2003 | `a2b35caaab5ccd46293945315c4d1dfee8d08b14` | Record T095 development results and fix protocol pinning |
| 2026-11-17T07:16:58+01:00 | milangavric2003 | milangavric2003 | `68aa0272e185abf36fd796d80072bed30d107fd7` | Record English-only retrieval scope for initial MVP |
| 2026-11-17T12:05:35+01:00 | Isidora Popovic | Isidora Popovic | `3da25106b86c69210c0ac44c134cd78ed56e488e` | feat(web): consolidate app in React TypeScript |
| 2026-11-17T12:25:35+01:00 | Isidora Popovic | Isidora Popovic | `0802adb517bccb0fd9089dc7c5ed51e7a47a94b1` | perf(web): lazy load routes and motion dependencies |
| 2026-11-17T12:44:52+01:00 | Isidora Popovic | Isidora Popovic | `a2d2101b93ce08e2a4596aa765ce8845dc5730e0` | docs(feature-005): reconcile T002 infrastructure readiness |
| 2026-11-17T12:57:22+01:00 | Isidora Popovic | Isidora Popovic | `b480146977aa33d344c79c8ddd98d4502986cb8d` | fix(web): restore styles under development CSP |
| 2026-11-17T12:58:32+01:00 | Isidora Popovic | Isidora Popovic | `2d8b43f6983ea699c73495603073a6085a1bfd9b` | docs(evidence): record web style fix publication |
| 2026-11-17T13:04:00+01:00 | Veki | Veki | `6bf6675c8474262b6e5e6aa60f39b065a50bb233` | RAG updated T095 finished |
| 2026-11-17T13:41:57+01:00 | Veki | Veki | `8ca4ba8f0bb80af08e9902084974ebccb4b875ee` | T096 finished |
| 2026-11-17T16:21:37+01:00 | Veki | Veki | `038f728cddab31b0bc08dbeb74d89560f59c348d` | T097 finished |
| 2026-11-17T16:30:22+01:00 | Isidora Popovic | Isidora Popovic | `14018899b264f31e9db78020c50ef2e6714577c4` | style(web): refine overview hero typography |
| 2026-11-18T06:19:33+01:00 | milangavric2003 | milangavric2003 | `5431299053660f982e93c4d5fc8909131281ec2a` | T098 finished; producer integration and history index verified |
| 2026-11-18T10:53:11+01:00 | milangavric2003 | milangavric2003 | `0786f8307e827d147ec8af67d5364bd47f23aa2a` | T101/T102 updated; versioned evaluation and bounded request profiles |
| 2026-11-18T11:03:00+01:00 | Isidora Popovic | Isidora Popovic | `4eec23fe14c7593b6edbf5591802bfae7f6fda41` | docs(model2): record split audit prerequisite blocker |
| 2026-11-18T11:04:24+01:00 | Isidora Popovic | Isidora Popovic | `929988d390e2198bee72effcd0b995f780b594ff` | docs(model2): record publication receipt |
| 2026-11-18T11:39:10+01:00 | milangavric2003 | milangavric2003 | `bb46ba4434fe9c82091d382da4d190f80810a706` | T101/T102 updated; source-bound selection and live evaluation evidence |
| 2026-11-18T11:45:51+01:00 | Isidora Popovic | Isidora Popovic | `91b2c19a28dc2149d478d13be4e8d7aea28f5bc0` | feat(model2): add synthetic partition loader scaffold |
| 2026-11-18T11:46:02+01:00 | Isidora Popovic | Isidora Popovic | `a416df2671cde8e45f78c6f7e22bcb5227c614a4` | feat(model2): add synthetic metrics and baselines |
| 2026-11-18T11:46:32+01:00 | Isidora Popovic | Isidora Popovic | `af39c697099563fdbbabb481fd186c4a0cfde3fa` | docs(model2): record synthetic implementation evidence |
| 2026-11-18T11:47:02+01:00 | Isidora Popovic | Isidora Popovic | `b09e422e7b2be20bd1c4643bfc98b4010bdd0658` | docs(evidence): record model2 push receipt |
| 2026-11-18T12:33:20+01:00 | Isidora Popovic | Isidora Popovic | `32a9af74a1126c90d7f4249bb9a64252214ac419` | fix(model2): sort loader test imports |
| 2026-11-18T12:33:32+01:00 | Isidora Popovic | Isidora Popovic | `37544ee55f204665b974d72fd691de77e4b913c4` | chore(model2): record partial logistic warning cleanup |
| 2026-11-18T12:33:46+01:00 | Isidora Popovic | Isidora Popovic | `c1b7f0bbfa8771ab95615a5451a17b5ad2f235e0` | feat(model2): add synthetic chronological split auditor |
| 2026-11-18T12:33:58+01:00 | Isidora Popovic | Isidora Popovic | `9a30d8fb9ddb79d60710a5e0224c893c6f606e3d` | feat(model2): add synthetic imbalance training harness |
| 2026-11-18T12:34:12+01:00 | Isidora Popovic | Isidora Popovic | `b107f367836924c3ae5f6adc86d5a9f126d79273` | feat(model2): add synthetic validation alert policies |
| 2026-11-18T12:34:48+01:00 | Isidora Popovic | Isidora Popovic | `6b05dc46a4f00597e2869a6073244d075bde3d84` | docs(model2): record synthetic contribution ledger |
| 2026-11-18T15:31:55+01:00 | Veki | Veki | `dabcb6472403d47bb72c8ec4c5a9d965f364c693` | T102 finished |
| 2026-11-18T16:34:25+01:00 | Veki | Veki | `62f099134c57a3129d28f333545a1398f6e812e4` | T101 finished |
| 2026-11-18T16:58:05+01:00 | Veki | Veki | `95fe9667f199d3a0ab9725062ad821640a6531de` | feature04 creation |
| 2026-11-18T17:11:35+01:00 | Veki | Veki | `ff389744e2529e248371b69a998375b32784d2ae` | Add Feature 004 task generation and technical plan documentation |
| 2026-11-18T17:20:51+01:00 | Veki | Veki | `734c433cbd9aff487d81752514a9f08237320889` | T001 |
| 2026-11-18T17:29:26+01:00 | Veki | Veki | `9ebcea82fc7f2010a7287ea14cded42b99ad74f7` | T002-T004 |
| 2026-11-18T17:44:16+01:00 | Veki | Veki | `c53a164b20dcaaf413bab93ad3dd01acad0c4673` | T005-T007 |
| 2026-11-18T18:06:34+01:00 | Veki | Veki | `e710d49e148b65433811f16414e82afb3f2e2723` | T008-T011 |
| 2026-11-18T19:14:33+01:00 | git stash | git stash | `04da6cd96554b588f39703f7d3f9af205e9170b5` | index on feature/002-model-development: 6b05dc4 docs(model2): record synthetic contribution ledger |
| 2026-11-18T19:14:33+01:00 | git stash | git stash | `81962309387d3749dde8b3cee7ffc336c85dec60` | On feature/002-model-development: preserve Feature 002 work before clean restart |
| 2026-11-18T19:14:33+01:00 | git stash | git stash | `b16aaf187a6da741381d9be1742b69e1ed53382d` | untracked files on feature/002-model-development: 6b05dc4 docs(model2): record synthetic contribution ledger |
| 2026-11-18T20:34:49+01:00 | Isidora Popovic | Isidora Popovic | `df4dabf36b9f4ff7b3a66d9de011ce29fbcbbed1` | docs(feature-002): specify dataset risk scoring and EDA |
| 2026-11-18T20:35:54+01:00 | Isidora Popovic | Isidora Popovic | `80d05971fd3b376125d184ec9fab310edcd564f4` | docs(evidence): record Feature 002 specification commit |
| 2026-11-18T22:27:19+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `3d2991edd017285464b913f5e48a1d09bbb990de` | feat(data): add resumable Feature 002 preparation |
| 2026-11-18T22:29:11+01:00 | Isidora Popovic | Isidora Popovic | `1fb0e8a5789e11c791ed955bbc5a9a2747b4efba` | docs(evidence): record Feature 002 publication |
| 2026-11-19T04:06:15+01:00 | milangavric2003 | milangavric2003 | `e15ee1f5fd0750f017b55f672d1fbc515d08f750` | T012-T014 |
| 2026-11-19T04:21:38+01:00 | milangavric2003 | milangavric2003 | `a0dfa5e6a8ccc117afe432e9c056549d41b6aec9` | T015–T017 |
| 2026-11-19T04:30:39+01:00 | milangavric2003 | milangavric2003 | `3c9b3446d799eadce412d4b77a4560adcaf836ef` | T018-T019 |
| 2026-11-19T05:36:50+01:00 | milangavric2003 | milangavric2003 | `45a375fe631238314173749f2a9d4d3265bbd687` | T020-T021; feature 04 finished |
| 2026-11-19T10:28:17+01:00 | Veki | Veki | `8d964bf3441faa528f29c46750752fe68a2a224f` | simulation lab integration into front |
| 2026-11-19T12:17:53+01:00 | Veki | Veki | `71f34dde1cf9470b4015069c4e54febd205e4cfa` | feature03 integration into front |
| 2026-11-19T13:07:38+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `27902a1e5716b9feb0be88108bd8ac246a8347d6` | feat(data): benchmark and prepare local HI-Small snapshot |
| 2026-11-19T13:08:54+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `b1326138944e706ce9b938abddd5b5e8b7f22810` | docs(evidence): refresh Feature 002 handoff and index |
| 2026-11-19T14:30:28+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `c6da2b60d3c7cc9876912c7af4afbb4810309f97` | test(data): add T211 temporal feature RED contracts |
| 2026-11-19T14:39:02+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `70f3019665a3d7b972c90b4d15c87986efa80178` | docs(data): freeze T212 temporal feature protocol |
| 2026-11-19T14:45:19+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `84e538a3f63181e97865147d4e46bc0cf6544268` | feat(data): implement T213 temporal feature kernel |
| 2026-11-19T14:49:25+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `10aed303e9330e1be655eb04e4a2323174dd2657` | test(data): add T214 partition RED contracts |
| 2026-11-19T14:58:33+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `7edc19fc13595e9aa0c910375d6d25f64df3f1ce` | feat(data): implement T215 chronological partition planner |
| 2026-11-19T15:01:08+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `5284c2a97b571b8f00ce6973a73c8e7daaacb632` | test(data): add T216 label-audit RED contracts |
| 2026-11-19T15:08:15+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `a4dca5e041377572a42673936b47e5790398b6d7` | feat(data): implement T217 restricted aggregate label audit |
| 2026-11-19T15:14:22+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `292e9d0aac5d495cd6bd3246167fc51e3fb5d832` | data: freeze T218 count-only UTC partition boundaries |
| 2026-11-19T22:56:15+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `eb10bab91ecb2df23f6f8d6e016677421b291e7d` | data: record T218 aggregate audit and FR-018 stop |
| 2026-11-19T23:01:53+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `41c8acfbf9b9d128ebb36ff77e2a556af3de0109` | feat(data): add fail-closed T219 protocol gate and record partial freeze |
| 2026-11-19T23:11:30+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `937beecaa3ab1c4b8da95933e311ce4a840ccada` | data: freeze T219 partition ID hashes and retain FR-018 stop |
| 2026-11-19T23:20:09+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `88c5a26e9270d6cd3e143d22ba41289642caf21e` | docs(data): record showcase prevalence exception and retain audit failure |
| 2026-11-19T23:31:43+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `2273937913f4bff7ce405bed77d12be0b0be8687` | feat(data): bind T218 exception and artifact hashes in T219 gate |
| 2026-11-19T23:43:12+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `d8b8373d3656515fe9428fc9e03b8535d8d3ae3d` | Add pinned references for model implementation (Multi-GNN, TabGT, AMLworld papers) |
| 2026-11-20T00:03:22+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `9901bc77ce22ab9d414a30144a437420f9cc1fa0` | docs(training): record T221 protocol proposal |
| 2026-11-20T00:04:18+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `42adea7542718cb6ecb634ab8dd138f9b7b5d4c8` | docs(evidence): record T221 publication |
| 2026-11-20T08:53:29+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `9292c1febcc5045e3a8f183ceaf8e93f3db5f3c4` | test(training): add T220 RED boundary contracts |
| 2026-11-20T09:08:36+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `a460ae108d24a7d994beb1a6f335ca3352127e3b` | docs(training): freeze T221 combined model choices |
| 2026-11-20T09:19:49+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `3f751061a0e753eac092601d2509180a447d984f` | build(training): lock ML compatibility and artifact format |
| 2026-11-20T09:29:44+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `9b4f26f55078dfd283bc17d91f5a1463399cc966` | Implement T223 train-only baselines |
| 2026-11-20T09:40:56+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `bf20f1c9760ec4ec342dc3caf89a6e43ed2cc66d` | Implement T224 candidate grids without training |
| 2026-11-20T09:49:03+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `838b967294f8c13350c4a2a627c0bf50f28e6e8d` | Add T225 RED evaluation contracts |
| 2026-11-20T09:55:47+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `03c69c296f22132c0ac7208401322aa27ad035ca` | Implement T226 validation evaluation |
| 2026-11-20T10:02:12+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `6dd2cc6923f7945f723b2c45be18c4f37d91e5ff` | Implement trusted LightGBM artifact integrity boundary (T227) |
| 2026-11-20T10:08:10+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `d91be2eee4ffc1defb5576bfa6e9b39ee98819cf` | Record T228 training blockers and local runbook |
| 2026-11-20T10:12:30+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `d09888df6ce2e5ead53bee0380c74944919b3cc2` | Document team handoff for gated model training |
| 2026-11-20T10:39:24+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `8f2e3f380589766ed1eda4b0d18efe7b6def165f` | Record exact-copy fit approval and add label-free input publisher |
| 2026-11-20T15:32:31+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `14fede41d3abaffc0c6f831953a15f59484b3c2f` | Implement IBM day split and local LightGBM pipeline |
| 2026-11-20T17:13:03+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `b7693f605e09d7a8ad1eefad5c4bac986629eb2d` | Document colleague training transfer and ignore local bundle |
| 2026-11-20T17:13:49+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `aa1accac0ff90f2eb370618be15f145b3cc6bf2b` | Record colleague bundle publication evidence |
| 2026-11-21T11:58:30+01:00 | Veki | Veki | `9187e69ca7887d529618ade87d016fa0a9aca2d2` | feature06 creation |
| 2026-11-21T12:18:19+01:00 | Veki | Veki | `60ebf0f4916d1cc5c48fdc751d44462add9618d3` | created speckit plan |
| 2026-11-21T12:25:03+01:00 | Veki | Veki | `cbfa969ca34f9d19c72b39a662f3e125e4f373d4` | taksts for feature06 creation |
| 2026-11-21T12:42:30+01:00 | Veki | Veki | `055fc06561f8b3d45d1a96e4db15a5ba682deefe` | T001 |
| 2026-11-21T12:51:36+01:00 | Veki | Veki | `002989f671ccae25f0ec5a5f09f0d7b8551fdd3e` | T003 finished, T002 not done yet |
| 2026-11-21T13:28:21+01:00 | Veki | Veki | `b61916a13add61e703f055440dae0027bc6059f0` | T002 |
| 2026-11-21T14:00:54+01:00 | Elena Kalajdžić | Elena Kalajdžić | `4a28e26b94707b08795840694576602c9f8b79a4` | docs(T219): record macOS resource review candidate |
| 2026-11-21T14:01:35+01:00 | Elena Kalajdžić | Elena Kalajdžić | `29b514233d8e4a6903fdb29dad395c719c097835` | feat(T219,T228): guard Mac fits and verify preflight schema |
| 2026-11-21T14:02:06+01:00 | Elena Kalajdžić | Elena Kalajdžić | `cddc8bb1ec1697722bcb51b2f61ae39329e7b814` | feat(T228): add bounded five-arm numeric diagnostic |
| 2026-11-21T14:02:37+01:00 | Elena Kalajdžić | Elena Kalajdžić | `705b6580c189afe9115d97cdff601b0bdff1d40b` | feat(T224): add guarded cross-family validation comparison |
| 2026-11-21T14:03:01+01:00 | Elena Kalajdžić | Elena Kalajdžić | `ebebdfb32cdca46a039df76a0d3ee48d075858f5` | feat(T229): freeze unweighted model and sealed test predictions |
| 2026-11-21T14:03:19+01:00 | Elena Kalajdžić | Elena Kalajdžić | `c408b6f950a6609917ff9ee51f2cd752e87a7951` | docs(T230): record authorized frozen-model test evaluation |
| 2026-11-21T14:03:57+01:00 | Elena Kalajdžić | Elena Kalajdžić | `2cec92702bc9f0ad8a9b53eae3a177ef392e7c1f` | test(T231): add risk API contract RED cases |
| 2026-11-21T14:05:34+01:00 | Elena Kalajdžić | Elena Kalajdžić | `cd4d92cc68b805b1668b418deec9cada6c117e5a` | feat(T232-T236): integrate trusted opt-in LightGBM risk API |
| 2026-11-21T14:05:48+01:00 | Elena Kalajdžić | Elena Kalajdžić | `25bbe72765ec10c25ff1986a9a7474aa01716952` | test(T237): add Feature 002 decoder RED cases |
| 2026-11-21T14:07:17+01:00 | Elena Kalajdžić | Elena Kalajdžić | `cea1f4746e5e06e2306a80ac5a70a0d256f5c842` | feat(T238-T242): add typed risk UI and aggregate presentation |
| 2026-11-21T14:07:36+01:00 | Elena Kalajdžić | Elena Kalajdžić | `9881239b69cfc2f7addde6fa78559ea1c043143f` | test(T250): add results authorization RED cases |
| 2026-11-21T14:08:56+01:00 | Elena Kalajdžić | Elena Kalajdžić | `d51573d57e7917cd7b53093ce45707b7c12a475a` | feat(T250,T251,T240): gate frozen aggregate results and wire UI |
| 2026-11-21T14:09:26+01:00 | Elena Kalajdžić | Elena Kalajdžić | `8a5c00e09cf5394ddfe0db8af6206dfdeaab7149` | docs(T243): propose bounded read-only EDA page |
| 2026-11-21T14:09:40+01:00 | Elena Kalajdžić | Elena Kalajdžić | `b18594ebacfeddd656a79c0d92102382d4fd4f40` | docs(T252,T253): prepare human review and showcase contract |
| 2026-11-21T14:09:54+01:00 | Elena Kalajdžić | Elena Kalajdžić | `2e4fc4866f34d87afeb77ad6ecf6c1e1cf0a1473` | test(T244): add label-free EDA aggregate RED cases |
| 2026-11-21T14:10:18+01:00 | Elena Kalajdžić | Elena Kalajdžić | `155131dd028ccbee4c7ce2dd9e915243ea7adfd4` | feat(T245): add label-free bounded EDA aggregates |
| 2026-11-21T14:11:00+01:00 | Elena Kalajdžić | Elena Kalajdžić | `599a00f71b10d77fc2048ee76c5c3cb832542bbf` | feat(T246): publish and serve hash-pinned label-free EDA summary |
| 2026-11-21T14:11:15+01:00 | Elena Kalajdžić | Elena Kalajdžić | `b74a244e27b5572b408d2d0f1c92ae8afb1d38d1` | docs(T243): record team approval for dedicated EDA page |
| 2026-11-21T14:11:29+01:00 | Elena Kalajdžić | Elena Kalajdžić | `5ab4ce59f4cd301ab0c99d718a4cbcde91ec9e58` | test(T248): add EDA decoder and UI state RED cases |
| 2026-11-21T14:11:54+01:00 | Elena Kalajdžić | Elena Kalajdžić | `7dc88ca0abba1b15955dee0fdba83f5756d91f49` | feat(T247,T248): add accessible hash-pinned EDA page |
| 2026-11-21T14:12:11+01:00 | Elena Kalajdžić | Elena Kalajdžić | `f848e4a1b706e0381f8d8a0bed74a0452c87134c` | docs(T219,T224,T229,T230): reconcile frozen protocol lineage |
| 2026-11-21T14:13:09+01:00 | Elena Kalajdžić | Elena Kalajdžić | `a844b724888323df1d27d212eb9767b4d088eb21` | test(T249): record full Feature 002 and Foundation regression |
| 2026-11-22T05:21:24+01:00 | milangavric2003 | milangavric2003 | `8bae72147f79a353e457bdb8495638c427c7efae` | T004-T007 |
| 2026-11-22T05:28:09+01:00 | milangavric2003 | milangavric2003 | `df8a79945844414c7f903d0149bc75358b7e21f4` | T008 |
| 2026-11-22T05:48:14+01:00 | milangavric2003 | milangavric2003 | `d78febd26dbf2348bbc98c98f94f51e744dcfa3c` | T009-T011 |
| 2026-11-22T06:00:17+01:00 | milangavric2003 | milangavric2003 | `5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca` | Freeze Capstone phase four evaluation package |
| 2026-11-22T06:10:12+01:00 | milangavric2003 | milangavric2003 | `d8acc2a335d95e2402f586006925949f4d9f7739` | Fit grouped dataset history within investigation input budget |
| 2026-11-22T06:18:45+01:00 | milangavric2003 | milangavric2003 | `02ab4061d2e7bae459ebf0d7c2be8885a05f6450` | Record Capstone phase four comparison and verified evidence |
| 2026-11-22T11:39:35+01:00 | Veki | Veki | `56f216714081eddaa57c09be06e5b9de56f47c1d` | T020 |
| 2026-11-22T12:26:23+01:00 | Veki | Veki | `82e931d2749feb612cbf3ad2fee98123cba4e63e` | T021-T023 |
| 2026-11-22T12:31:25+01:00 | milangavric2003 | milangavric2003 | `88cb4541ff6b09e1e81130eef7fa54d4cd379146` | Merge origin/feature/002-clean-start@a844b72 into integration/capstone-mvp |
| 2026-11-22T12:35:44+01:00 | milangavric2003 | milangavric2003 | `1737ef9929b9f3dc33b3b6e16d0573c1151836d3` | Port React from origin/feature/005-real-time-fraud-detection-mlops-spec@1401889 into integration/capstone-mvp |
| 2026-11-22T12:39:07+01:00 | milangavric2003 | milangavric2003 | `35a7df74857e953175ffe291cd3848d70686c9e4` | Port origin/integration/003-investigation-web@71f34dd into integration/capstone-mvp |
| 2026-11-22T12:40:50+01:00 | milangavric2003 | milangavric2003 | `eab1d2abb1ebfa6933ddf54b24fb4ef43a8e6db6` | Port origin/integration/004-simulation-web@8d964bf into integration/capstone-mvp |
| 2026-11-22T12:46:11+01:00 | milangavric2003 | milangavric2003 | `361ff5502a19b2ead89d78928cb8f085aa75c700` | Complete offline fixture dependencies from origin/feature03@62f0991 in integration/capstone-mvp |
| 2026-11-22T12:49:34+01:00 | milangavric2003 | milangavric2003 | `dd0bf61280b74b5029651a622c6c075b85f14461` | Record integration/capstone-mvp verification at 361ff55 |
| 2026-11-22T13:08:43+01:00 | Veki | Veki | `f330d43386f40de7e4aa528600a592b571ce60d8` | T024-T025 |
| 2026-11-22T13:31:27+01:00 | milangavric2003 | milangavric2003 | `b92430ba76953bbc8232b2d26f68a007089dea83` | docs(feature-006): record local Cases access decision |
| 2026-11-22T13:38:09+01:00 | milangavric2003 | milangavric2003 | `8b91432eb7954c414a9912fb54006a8356144baa` | test(feature-006): verify Cases access in the local demo |
| 2026-11-22T14:38:26+01:00 | Elena Kalajdžić | Elena Kalajdžić | `2429673dfd733c6d784e86490c57be44a9dc3eda` | Define approved model case bridge contract |
| 2026-11-22T14:38:40+01:00 | Elena Kalajdžić | Elena Kalajdžić | `53f59908f103594e95fcdd6ec24e01158f44ccea` | Publish frozen model alerts from label-free facts |
| 2026-11-22T14:38:53+01:00 | Elena Kalajdžić | Elena Kalajdžić | `8669919992fc47e200cf4e3f10878e7de24053bb` | Resolve published model cases in investigation API |
| 2026-11-22T14:39:09+01:00 | Elena Kalajdžić | Elena Kalajdžić | `ed974647ec57b23561548f84911e90a7fff209fa` | Connect React model alerts to investigation flow |
| 2026-11-22T14:40:13+01:00 | Elena Kalajdžić | Elena Kalajdžić | `5fc29680fa544546de5b5d6beac8e9b7edef8701` | Record bridge regression tests and integration evidence |
| 2026-11-22T14:41:21+01:00 | Elena Kalajdžić | Elena Kalajdžić | `c0d59f20fbc5616b84fe6ccb341de4cf83fa49ba` | Record model case bridge branch publication |
| 2026-11-22T16:38:35+01:00 | milangavric2003 | milangavric2003 | `f68d2cd9cd0264770a94feda0f93634f621145a8` | Fix Windows bridge publication and pin the trusted manifest |
| 2026-11-22T16:39:05+01:00 | milangavric2003 | milangavric2003 | `40ce7e393248db68fc9bf24c2663766deb93f1e5` | Record PR 4 Windows review and verification |
| 2026-11-22T16:45:28+01:00 | GitHub | Milan Gavrić | `d46699fbd11219ebc92c6ef002d4924a4c7d4b34` | Merge pull request #4 from vekiii/integration/model-rag-handoff |
| 2026-11-22T18:07:40+01:00 | Elena Kalajdžić | Elena Kalajdžić | `2779b9137cda323eaea79299e158893b92ff962f` | docs: record final Codex review of PR 3 candidate |
| 2026-11-22T18:07:56+01:00 | Elena Kalajdžić | Elena Kalajdžić | `08375978b59f40c4623f8dee8100d7ba456c46f1` | docs: record scoped T252 manual review and open criteria |
| 2026-11-22T18:10:37+01:00 | Elena Kalajdžić | Elena Kalajdžić | `a47ce13a6f490de242974d96ccbb1639ce9875c4` | docs: hand off PR 3 review publication and remaining T252 |
| 2026-11-22T20:51:28+01:00 | Veki | Veki | `a6cc9e3bcbb479f275da050483684094c56c8c7f` | feat(T252): add technical findings and reproduction protocols for review |
| 2026-11-22T21:09:25+01:00 | Veki | Veki | `d1bad7139a1d7133846274b9f2ef4298acbcadf8` | feat(feature-006): add supplemental evidence and execution details for EV-06 |
| 2026-11-22T21:30:30+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `fd030b957b659bd54d768b17cb368ca8dfdaef56` | docs(T252): record user approval attestation and remaining evidence |
| 2026-11-22T21:32:08+01:00 | Veki | Veki | `f9fd78ba8fad3829aa78fc8cf583e2ac9b8c2d2f` | feat(feature-006): add supplemental evidence and live comparison details for SC-002 and CAP-05 |
| 2026-11-22T21:35:14+01:00 | Veki | Veki | `3eee1d62b9d7e4d9f440f8f1931415159e75aa18` | feat(feature-006): update evidence map and release candidate documentation for clarity and accuracy |
| 2026-11-22T21:55:54+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `399c13a6e5f200d1f621832317149a3ba8dd93d7` | docs(T252): record reviewer hash and renewed approval |
| 2026-11-22T22:00:00+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `6e7915713e4505429fc9a81bb2a0d8f7e37abe5e` | docs(T252): record Isidora reply and authorship question |
| 2026-11-22T22:04:20+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `a13a5c1445ccc938d5fa920d9afe80af706c9571` | docs(T252): record reviewer authorship and artifact blocker |
| 2026-11-22T22:14:35+01:00 | Codex | Codex | `76b9e08a7620fbb53feff00a7db872719b37dd1d` | docs: record T252 Windows frozen-input hash receipt |
| 2026-11-22T22:18:14+01:00 | Codex | Codex | `fc724e6d2f0bb9afa9071e47323e364063ecaf43` | docs: record T252 Windows parity input repair |
| 2026-11-22T22:21:37+01:00 | Codex | Codex | `c84197c4560e1a24ec2f84ce293fb344e225be39` | docs: record reviewer Windows parity result |
| 2026-11-22T22:26:08+01:00 | Codex | Codex | `7b5b56cbb4a2fe8d738a8b4e574ee63d051e068e` | docs: record reported Vedran T252 approval scope pending |
| 2026-11-22T22:35:50+01:00 | Codex | Codex | `b925ae5a9bd6a2ce06741366ef321b2dec297d33` | docs: reconcile T252 team approval and execution gates |
| 2026-11-22T22:45:47+01:00 | Codex | Codex | `6938da03d0b74a8f778ee0af80ff6985bf7d1187` | docs: record final team approval and T252 reproduction gap |
| 2026-11-22T22:53:39+01:00 | Codex | Codex | `a737e205f47b36eaa1436c4b294d2a702068bfee` | docs: record T230 snapshot transfer preparation |
| 2026-11-22T22:53:39+01:00 | Codex | Codex | `203e265e7323cc41519629d6c973618a78b5c57e` | docs: record final unweighted LightGBM configuration |
| 2026-11-22T22:54:43+01:00 | Codex | Codex | `28a938ab68824c6eb7e896882adfd65984e336cc` | docs: refresh master commit and branch evidence |
| 2026-11-22T23:52:31+01:00 | Isidora Popovic LUKOWA | Isidora Popovic LUKOWA | `ab692c69ae06bd89a83bf92d95893ccfddf380dc` | test(security): audit integrated MVP boundaries |
