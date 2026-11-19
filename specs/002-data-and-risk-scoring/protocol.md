# Feature 002 protocol

Status: preparation resource settings frozen by T209 on 2026-11-19. A conditional UTC assumption for naive source timestamps is recorded below. The user authorized a content-addressed local-copy exception for T203/T210 on 2026-11-19; its limits are below. Temporal processing, partitions, feature schema, and model decisions remain open.

## T203 local-copy decision and T210 scope

The user confirmed a local download of `HI-Small_Trans.csv`, could not provide its Kaggle version or receipt, and explicitly directed us to close T203 and execute T210. For this local educational preparation, identify the exact selected source revision by its measured SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` and 475,664,283-byte size. The publisher's Kaggle revision, acquisition date and method beyond the user-reported local download remain unknown. IBM's AML-Data README is the source for CDLA-Sharing-1.0 data terms; the Kaggle listing's own terms field was unavailable. These are explicit reproducibility and licensing limitations, not verified facts. No data redistribution is authorized by this decision.

This decision permits a **local canonical preparation and quality report** only for the exact matching bytes, with exact-header/schema validation and the T209 resource ceilings. It does not permit substituting a different source, treating the unknown upstream release as known, fitting models, inspecting record-level labels outside the restricted pipeline, or claiming temporal partitions complete. Contrary source or license evidence is a stop condition. T203 closes under this documented exception; T210 must report any missing manifest/data-card fields honestly.

## T209 preparation resource contract

The following settings apply only to the T208 canonical validation and snapshot runner. They do not establish capacity for temporal sorting, feature generation, model fitting, or API serving. The measurements and exact commands are in [T209 evidence](../../evidence/tasks/T209.md).

| Control | Frozen setting | Operational response |
|---|---:|---|
| Source batch / chunk size | 10,000 records | Do not increase without a new synthetic benchmark. |
| Checkpoint cadence | Every complete 10,000-record chunk; final partial chunk also committed | Resume only after source, configuration, input-prefix and staged-output verification. |
| Process peak working-set ceiling | 512 MiB | Stop the run if monitored peak exceeds the ceiling; investigate before retry. This is an operational ceiling, not yet an in-process limiter. |
| Minimum free-space reserve | 10 GiB on staging and output volumes | Pass `min_free_bytes=10737418240` to `run_pipeline`; a low-space check stops the run. |
| Start-of-run free space | At least 20 GiB on each relevant volume | Check before invoking the runner; the 10 GiB reserve alone is not a capacity forecast. |
| Maximum canonical preparation runtime | 15 minutes for approximately 5.1 million records on the measured workstation | Stop and review a slower run. This is an operational ceiling, not yet an in-process timeout. |
| Published snapshot | One immutable directory with verified `COMPLETE` marker | Never treat staged or partial output as complete. |

These values must be reconsidered if source size, record width, machine, volume, code, or output format changes. A real-source run also requires the T203 local-copy decision above, verified input SHA-256, and a processing configuration hash. Any ceiling breach is a stop condition; it is not permission to drop records or relax validation.

The full-size synthetic run processed 5,078,345 rows in 331.236 seconds with an 83,034,112-byte process peak working set. Stage plus published snapshot occupied 6,120,299,645 bytes before cleanup. The 20 GiB initial free-space rule allows over 4 GiB beyond that observed footprint while preserving the 10 GiB reserve; it is a preflight threshold for this format, not a promise that every source will fit. The runner checks disk reserve automatically; an operator must monitor the memory and runtime ceilings until a bounded watchdog is added.

### T210 real-source runtime review, 2026-11-19

The first exact-source T210 run combined source hashing, CSV parsing, canonical validation, a bounded non-label quality scan, snapshot publication and full output verification. It completed in 903.834 seconds, exceeding the T209 **canonical synthetic** 900-second operational ceiling by 3.834 seconds. This breach was observed and reviewed after completion, not hidden or relabeled as a pass. The snapshot's `COMPLETE` marker, manifest counts and processed-file hashes verified; 5,078,345 source rows reconciled with 5,078,345 accepted and zero rejected. Highest sampled process peak working set was 84,594,688 bytes, with 67,546,107,904 bytes free afterward. No memory or disk threshold was approached.

For a **repeat of this exact-source integrated T210 preparation plus quality-scan configuration on this workstation**, set a reviewed 20-minute operational runtime ceiling. This gives about 1.33× headroom over the measured run; the original 15-minute T209 ceiling remains the synthetic canonical-run comparison and its breach remains recorded. The verified T210 snapshot can be retained for later permitted local preparation steps without rerunning the entire CSV solely for a 3.834-second overrun. A different source, code/configuration, volume or machine requires a new review, and downstream feature/partition/model work still has separate gates. Runtime and peak working set remain operator-monitored until enforced by code.

## HI-Small source interpretation for preparation

The selected input is **`HI-Small_Trans.csv` only**. The publisher's Kaggle description lists it separately from `HI-Small_Patterns.txt` and the other independent HI/LI variants. Its published approximate counts and date span are context, not measured facts for the local CSV. The description warns that some transactions occur after the primary Sep 1–10, 2022 period and reports that these late transactions are laundering. This label-related statement is a publisher caveat; it does not authorize record-level label inspection or changing the frozen chronological split from the feature spec.

The checked Kaggle description excerpt, IBM README and accessible paper do not assign a timezone to `HI-Small_Trans.csv`. The local timestamp field has minute precision and no offset. **Project assumption for later temporal processing:** interpret a valid naive source timestamp as UTC at minute precision, without changing its displayed text during initial canonical preparation. This is an explicit modeling convention, not a publisher claim. If source documentation for the selected bytes states another timezone, stop and revise the policy before temporal processing.

## Later protocol decisions

- Upstream Kaggle release and exact acquisition date: unknown under the explicit T203 local-copy exception; selected bytes are pinned by SHA-256.
- Naive timestamp interpretation: UTC-at-minute-precision project assumption recorded above; implementation and verification of canonical UTC normalization remain pending T211–T213.
- Feature order, precision, missing/category policy and version: pending T212.
- Development/showcase and train/validation/test boundaries and hashes: pending T214–T219.
- Candidate grid, class strategy, threshold objective and artifact format: pending T221/T222.
- Label access and separately authorized evaluation: pending T216–T230.
