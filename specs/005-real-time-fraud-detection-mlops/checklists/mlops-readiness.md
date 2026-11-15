# MLOps reproducibility and promotion gate

- [ ] Freeze exact training dataset/source/label-cutoff/feature-policy/split hashes and reproduce row membership; T033–T035.
- [ ] Compare online versus offline features and quantify any drift; T034.
- [ ] Run predeclared validation and delayed confirmed-label evaluation, report denominators, capacity, uncertainty and prior exposure; T038/T039.
- [ ] Verify MLflow run, registry version and local manifest SHA-256 round-trip without bypassing `load_trusted_artifact`; T036/T037.
- [ ] Reject unapproved, mismatched, wrong dependency or wrong signature artifact before any live prediction; T019/T037.
- [ ] Record named reviewer, decision, exact digest and alert policy before promotion; test atomic activation and rollback; T040.
- [ ] Distinguish synthetic transport fixture success from real model quality and Feature 002 T065/T066 signoff; final review T046.
