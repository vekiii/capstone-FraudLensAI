# Feature branch pull recovery - 2026-11-13

User reported pulling initialization and then 002-data-and-risk-scoring while
on main, causing a next_work.md conflict. Observed HEAD and ORIG_HEAD were both
`b9650a1ccfbfe84c8f73e7da46caf351fddbccff`; MERGE_HEAD and remote feature tip were
`0f5ad9ac0b04cc406e3c19b0f1934da4cc29d10d`.
Only next_work.md was unmerged. The other staged changes were incoming feature
002 files, not a completed merge. The new commit adds T017-T025 feature replay
and rules work; it does not modify the previously failing test_data_store helper.

Before aborting, ran `.venv/Scripts/python.exe -m pytest backend/tests -q`
with fresh absolute --basetemp and cache_dir paths under root .cache.
Result: **566 passed, 6 failed**, exit 1, one existing Starlette/httpx warning.
The same six integration cases fail at test_data_store.py:40 comparing raw CRLF
mapping bytes to the reviewed LF-normalized digest. See the prior
[merge review](main-merge-review-2026-11-13.md) for hashes and affected cases.
The reported 572-pass branch evidence was not reproduced on this Windows checkout.
No production code, tests or mapping policy were modified to hide these failures.
No new frontend, browser, IBM import or model evaluation was performed.

Ran `git merge --abort`, exit 0. Verified main remains at b9650a1, status clean
immediately after abort, ahead of origin/main by 23 commits. Remote feature tip
remains 0f5ad9a; no commits were deleted/reset and no push occurred.
These recovery evidence/handoff edits were subsequently added as uncommitted
documentation only. No merge is pending.

Next: fix and verify the cross-platform mapping-hash test expectation on the
feature branch before another merge review. To inspect colleagues' updates
without merging them into the current branch, use `git fetch origin` followed
by `git log main..origin/002-data-and-risk-scoring --oneline`.
