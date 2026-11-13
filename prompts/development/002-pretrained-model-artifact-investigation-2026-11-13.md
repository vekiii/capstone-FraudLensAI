# Original development request: pretrained artifact investigation

Received 2026-11-13. Original request:

> Work ONLY on the `model-implementations` branch.
>
> OBJECTIVE:\
> Find an existing, downloadable, already-trained fraud-detection model suitable for an inference-only FraudLens AI implementation.
>
> Investigate these sources in order:
>
> PRIMARY REFERENCE:\
> https://github.com/shejz/IEEE-CIS-Fraud-Detection
>
> PRETRAINED ARTIFACT CANDIDATE:\
> https://huggingface.co/karthifde/apexfi-fraud-detection
>
> ALTERNATIVE:\
> https://github.com/manasscodes/IEEE-CIS-Fraud-Detection
>
> TASKS:
>
> 1. Check the original shejz repository, including its releases, for actual pretrained model weights. A notebook, leaderboard score, or training script is NOT a pretrained artifact.
> 2. Inspect the ApexFi IEEE-CIS LightGBM model, its native weights, preprocessing dependencies, inference example, license and required feature schema.
> 3. Inspect the alternative GitHub repository's trained LightGBM model and fitted preprocessing files.
> 4. Verify that actual model bytes are downloadable, not merely referenced in documentation.
> 5. Inspect source revision, immutable artifact version, checksums, size, model type, library requirements, license and provenance.
> 6. Evaluate security risks. Python pickle/joblib files can execute code during deserialization; do not load untrusted artifacts merely to inspect them. Prefer native non-executable model formats when practical.
> 7. Compare the model's exact required feature names, feature order, dtypes, categorical encodings and preprocessing against:
>    - IBM HI-Small source fields
>    - `history-v1` features
>    - Existing FraudLens v2 transaction and scoring contracts
> 8. Build a field-by-field compatibility matrix identifying exact matches, legitimate deterministic transformations and unavailable features.
> 9. Do not invent card/device/address/identity features or replace missing mandatory IEEE features with arbitrary constants.
> 10. Determine whether an authentic IBM transaction can be scored without losing required model semantics.
> 11. If none of the candidates is compatible, clearly distinguish an IEEE-CIS-only isolated demonstration from IBM-backed FraudLens inference.
>
> NO MODEL TRAINING OR INFERENCE YET.
>
> Create:\
> `evidence/tasks/feature-002-pretrained-model.md`
>
> Include model-source comparison, exact artifacts, evidence, security review, license status, compatibility matrix and recommended implementation path.
>
> If direct IBM scoring is impossible, do not authorize it silently. Record the required team decision and stop IBM integration.
>
> Update `next_work.md`.
>
> After documentation checks and review, commit:
>
> docs(ml): assess pretrained model artifacts and input compatibility
>
> Do not push.
>
> Report the selected candidate, verified download location, feature compatibility, blockers and next permitted step.
