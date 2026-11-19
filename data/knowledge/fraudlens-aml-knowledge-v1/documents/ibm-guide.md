# IBM synthetic data field limitations

## Field limitations
Authored guide, not copied IBM documentation. IBM AML-Data describes generated transactions and identifies the actual data license as CDLA-Sharing-1.0, distinct from the repository Apache-2.0 license. Synthetic labels are training/evaluation targets, not legal findings; exclude them from runtime context. Field handling in this project follows the pinned producer contract: retain directional amount/currency strings, raw time and explicit time-basis assumptions. Do not infer occupation, timezone, real bank loss or calibrated probability from fixture fields. No raw data or IBM source text is redistributed here.
