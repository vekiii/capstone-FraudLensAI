# Feature 06 · T024 · Završna regresija

22. novembar 2026, Europe/Belgrade. Glavni checkout je počeo čist na grani
`006-capstone-evaluation`, HEAD `82e931d2749feb612cbf3ad2fee98123cba4e63e`.
Komande su pokrenute iz zasebnog checkout-a
`.cache/006-t021/vedran-checkout`, detached HEAD
`d8acc2a335d95e2402f586006925949f4d9f7739` (D), uz prazan
`git status --short` pre i posle. [Originalni zahtev](../../prompts/development/006-capstone-phase-06.md) ·
[Quickstart](../../specs/006-capstone-evaluation/quickstart.md#završna-regresija).

Windows, CPython 3.14.3, uv 0.10.9, pytest 9.2.0, Ruff 0.17.4,
Node v24.20.0, npm 11.19.0, Vitest 5.1.0 i Vite 8.3.8. Ponovo su
korišćene zaključane instalacije iz [pripreme T021](feature-006-phase-05-handoff.md).

| Lockfile | SHA-256 lokalnih bajtova kandidata | SHA-256 Git/LF na D i B |
| --- | --- | --- |
| `uv.lock` | `caf9d0925d235ac17abf7112eb7b0b38af12f98aa9e00f3afffa0cb870946b85` | `4a6ad0c3106f35814782f2c3b24ca575466baf241a08ba10803be49d437896d3` |
| `web/package-lock.json` | `f385bd7caffd10d7d188d262d34191d2e3eb811dfaf63e957bac20e90bf0540a` | `ecdff23dbae2336b3bfe4bbe2fd183ea4bee2278fec1adcc06c4c29e3506fcd2` |

Root i web checkout nemaju `.env*`; odsutan je i
`infra/compose/.env.local` u testnom checkout-u. U procesu uklonjene su
nasleđene konfiguracije modela/providera, `APP_*`, `INVESTIGATION_*`,
`VITE_*`, `PYTEST_*`, `PYTHONPATH`, `UV_PROJECT_ENVIRONMENT` i opt-in
PostgreSQL promenljive. Postavljen je `SPECIFY_FEATURE_DIRECTORY=specs/006-capstone-evaluation`,
`UV_OFFLINE=1` i postojeći lokalni uv/npm keš iz glavnog checkout-a.
Pregled testova pre starta potvrdio je fixture i mock provider putanje,
bez pozivanja živog EV runner-a. T098 kopije (scored store, source,
transfer indeks i lokalno izgrađen indeks) bile su prisutne. Nedostajali
su Feature 02 istorijski store i oba zaključana model artifact paketa.
Oni nisu zamenjeni fixture-ima. Nema novih modelskih poziva ni rebuild-a.

## Obavezne komande i rezultati

`$tempRoot` je apsolutna putanja do izdvojenog lokalnog direktorijuma
`.cache/006-regression-52f9bf6194d64ff49feaffb69dfadded` pod D checkout-om.
Uz pytest je postavljen `PYTEST_ADDOPTS=-r a --junitxml="<tempRoot>/pytest.xml"`.
Svi logovi, JUnit XML i izlazni kodovi sačuvani su u tom direktorijumu.

| Komanda iz korena D checkout-a | Exit | Opaženi ishod |
| --- | ---: | --- |
| `uv run --locked python -m pytest backend/tests --basetemp "$tempRoot/tmp" -o "cache_dir=$tempRoot/cache"` | 1 | Prikupljeno **896**. Prošlo **796**, palo **72**, preskočeno **24**, greške pri postavci **4**, 44,63 s. Izlaz nema prikazan sažetak upozorenja. |
| `uv run --locked ruff check backend` | 0 | `All checks passed!` |
| `npm.cmd --prefix web run test -- --run` | 0 | **17/17** fajlova, **211/211** testova, 0 padova, grešaka ili preskoka, 5,30 s. Vitest prijavljuje trošak uspostavljanja 17 jsdom okruženja. |
| `npm.cmd --prefix web run build` | 0 | Ugrađeni `tsc --noEmit` i produkcijski Vite build prošli; 55 modula, 420 ms. Postojeće upozorenje za Three.js chunk **742,80 kB** iznad 500 kB. |
| `git diff --check` | 0 | Prazan izlaz na D checkout-u. |

Pregled svih 24 preskoka: 23 testa zahtevaju eksplicitno odobren
disposable PostgreSQL klaster, a jedan zahteva lokalni Feature 02
`history-v1` store i model artefakt. Puna komanda je izvršena bez
isključivanja testova. Poseban typecheck van build-a nije pokretan.

## Razvrstavanje i poređenje

[T001](feature-006-setup.md) je imao 84 ciljane backend i 47 React
provera. T001 sam po sebi ne objašnjava današnje ishode. Za 76 problematičnih
node ID-jeva napravljeno je ciljano poređenje sa prethodnim aplikacionim
baseline-om B (`5974f94f68c2a1fd1e42b9b2d01d438c30bd8dca`) u čistom
odvojenom checkout-u `.cache/006-t024-baseline-d43b3e3d0db64a4689d26869516d5b10`.
U B checkout-u je prošao `uv sync --locked --group dev --offline`, sa
istim CPython-om i lockfile-om. Poređenje koristi isti režim konfiguracije i
novu apsolutnu `$tempRoot`, `.cache/006-comparison` ispod B checkout-a.

```powershell
uv run --locked python -m pytest backend/tests/unit/test_pretrained_loader.py backend/tests/unit/test_pretrained_ibm_inference.py backend/tests/unit/test_boosted_integration.py backend/tests/unit/test_model_scoring.py backend/tests/unit/test_model_artifacts.py::test_escaped_path_upload_and_incompatible_manifest_reject backend/tests/integration/test_security_boundaries.py::test_case_listing_requires_an_authenticated_principal --basetemp "$tempRoot/tmp" -o "cache_dir=$tempRoot/cache"
```

Baseline poređenje, uz isti JUnit dodatak, ima **82 prikupljena, 6 prošlih,
72 pada, 4 greške, 0 preskoka, exit 1**. Upoređeni su parovi
`classname/name`, failure/error i kategorije poruka u dva JUnit XML-a.
Skupovi i kategorije svih 76 ishoda su jednaki. Puni baseline paket ovde
nije ponavljan.

| D nalaz | Broj | Klasifikacija i razlog |
| --- | ---: | --- |
| `test_pretrained_ibm_inference.py` i `test_pretrained_loader.py` | 36 + 30 padova | Potvrđeno postojeći RED. Izostaju `fraudlens.pretrained_inference` i `fraudlens.pretrained`. Ista grupa od 66 dokumentovana je i u [Feature 02](feature-002-regression.md). |
| `test_case_listing_requires_an_authenticated_principal` | 1 pad | Potvrđeno postojeći auth RED. Na oba SHA test očekuje 401/403 a dobija 200. Test označava planiranu granicu pristupa iz Feature 05 T028. |
| `test_boosted_integration.py` | 4 pada | Nedostupan lokalni preduslov u oba checkout-a. Nema `artifacts/feature-002-boosted-validation-20261114/manifest.json`. |
| `test_model_scoring.py` | 4 setup greške | Nedostupan lokalni preduslov u oba checkout-a. Fixture ne nalazi `artifacts/feature-002-history-v1-20261114/manifest.json`. |
| `test_escaped_path_upload_and_incompatible_manifest_reject` | 1 pad | Nedostupna Windows privilegija u oba checkout-a. Kreiranje testnog symlink-a staje sa WinError 1314 pre poslovne asercije. |

Među zabeleženim padovima nema potvrđene nove regresije ili nerazvrstanog
nalaza. Testovi sa nedostupnim preduslovom ne daju sud o poslovnom ponašanju
iza blokade. T024 je završen kao izvršena regresija sa padovima.

## Failing node ID-jevi

```text
ERROR backend/tests/unit/test_model_scoring.py::test_model_parity_identity_explanation_and_repeatability
ERROR backend/tests/unit/test_model_scoring.py::test_unseen_category_no_refit_and_correct_order
ERROR backend/tests/unit/test_model_scoring.py::test_bad_probability_fails_without_clipping_or_rules_fallback
ERROR backend/tests/unit/test_model_scoring.py::test_wrong_identity_label_or_artifact_rejected
FAILED backend/tests/integration/test_security_boundaries.py::test_case_listing_requires_an_authenticated_principal
FAILED backend/tests/unit/test_boosted_integration.py::test_trusted_boosted_reload_and_explanation
FAILED backend/tests/unit/test_boosted_integration.py::test_boosted_explanation_batches_counterfactual_predictions
FAILED backend/tests/unit/test_boosted_integration.py::test_boosted_assess_batch_matches_individual_scoring
FAILED backend/tests/unit/test_boosted_integration.py::test_wrong_boosted_version_rejected_before_deserialization
FAILED backend/tests/unit/test_model_artifacts.py::test_escaped_path_upload_and_incompatible_manifest_reject
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_ibm_source_fields_map_to_exact_ordered_22_feature_vector
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_pinned_categorical_codes_are_stable_and_ordered
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_exact_money_and_currency_meaning_are_preserved
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_paid_and_received_sides_are_not_swapped_or_currency_converted
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_synthetic_midnight_uses_recorded_minute_not_host_timezone
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_matching_currency_and_account_values_follow_upstream_semantics
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_malformed_or_missing_required_source_fields_fail_closed[change0]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_malformed_or_missing_required_source_fields_fail_closed[change1]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_malformed_or_missing_required_source_fields_fail_closed[change2]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_malformed_or_missing_required_source_fields_fail_closed[change3]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_malformed_or_missing_required_source_fields_fail_closed[change4]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_malformed_or_missing_required_source_fields_fail_closed[change5]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_private_label_or_unknown_source_fields_never_enter_model_input
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_ieee_fields_cannot_substitute_for_ibm_inputs
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_unknown_category_is_not_fabricated_or_refitted
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_graph_state_is_required_and_bound_to_source_and_model
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_missing_identity_or_cutoff_provenance_cannot_be_inferred_from_graph_maps
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_dataset_and_feature_lineage_must_match
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_bank_qualified_collision_cannot_use_unqualified_graph_lookup
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_training_period_graph_cannot_score_earlier_transaction
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_rejected_publisher_candidate_cannot_predict_even_with_matching_hashes
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_timestamp_source_and_canonical_time_must_agree
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_qualified_identity_must_match_graph_bank_index_before_prediction
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_missing_graph_aggregates_are_not_invented_zeroes
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_native_feature_order_and_category_metadata_must_match
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_synthetic_time_basis_must_match_documented_assumption
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_prediction_identity_provenance_and_uncalibrated_score
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_nonfinite_out_of_range_or_malformed_predictions_are_rejected[nan]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_nonfinite_out_of_range_or_malformed_predictions_are_rejected[inf]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_nonfinite_out_of_range_or_malformed_predictions_are_rejected[-0.1]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_nonfinite_out_of_range_or_malformed_predictions_are_rejected[1.1]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_nonfinite_out_of_range_or_malformed_predictions_are_rejected[result4]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_nonfinite_out_of_range_or_malformed_predictions_are_rejected[result5]
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_prediction_identity_must_not_be_reassigned
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_fake_inference_never_trains_or_uses_private_labels
FAILED backend/tests/unit/test_pretrained_ibm_inference.py::test_prediction_does_not_mutate_model_parameters
FAILED backend/tests/unit/test_pretrained_loader.py::test_valid_local_native_artifact_reaches_only_fake_booster
FAILED backend/tests/unit/test_pretrained_loader.py::test_missing_model_is_unavailable_without_zero_risk_fallback
FAILED backend/tests/unit/test_pretrained_loader.py::test_corrupt_truncated_or_modified_model_rejects_before_native_load[]
FAILED backend/tests/unit/test_pretrained_loader.py::test_corrupt_truncated_or_modified_model_rejects_before_native_load[content1]
FAILED backend/tests/unit/test_pretrained_loader.py::test_corrupt_truncated_or_modified_model_rejects_before_native_load[content2]
FAILED backend/tests/unit/test_pretrained_loader.py::test_substituted_wrong_domain_artifact_rejects_even_with_recomputed_hash
FAILED backend/tests/unit/test_pretrained_loader.py::test_wrong_model_revision_or_serialization_is_rejected[model_id-apexfi-ieee-cis]
FAILED backend/tests/unit/test_pretrained_loader.py::test_wrong_model_revision_or_serialization_is_rejected[domain-ieee_cis_isFraud]
FAILED backend/tests/unit/test_pretrained_loader.py::test_wrong_model_revision_or_serialization_is_rejected[upstream_revision-main]
FAILED backend/tests/unit/test_pretrained_loader.py::test_wrong_model_revision_or_serialization_is_rejected[upstream_revision-0000000000000000000000000000000000000000]
FAILED backend/tests/unit/test_pretrained_loader.py::test_wrong_model_revision_or_serialization_is_rejected[model_format-pickle]
FAILED backend/tests/unit/test_pretrained_loader.py::test_wrong_model_revision_or_serialization_is_rejected[model_format-joblib]
FAILED backend/tests/unit/test_pretrained_loader.py::test_wrong_model_revision_or_serialization_is_rejected[model_file-model.pkl]
FAILED backend/tests/unit/test_pretrained_loader.py::test_wrong_model_revision_or_serialization_is_rejected[preprocessing_source_file-preproc.pkl]
FAILED backend/tests/unit/test_pretrained_loader.py::test_expected_hash_mismatch_is_rejected[model_sha256-0000000000000000000000000000000000000000000000000000000000000000]
FAILED backend/tests/unit/test_pretrained_loader.py::test_expected_hash_mismatch_is_rejected[graph_sha256-0000000000000000000000000000000000000000000000000000000000000000]
FAILED backend/tests/unit/test_pretrained_loader.py::test_expected_hash_mismatch_is_rejected[preprocessing_source_sha256-0000000000000000000000000000000000000000000000000000000000000000]
FAILED backend/tests/unit/test_pretrained_loader.py::test_ieee_fields_cannot_replace_exact_ibm_schema
FAILED backend/tests/unit/test_pretrained_loader.py::test_feature_order_count_and_categorical_fields_are_verified
FAILED backend/tests/unit/test_pretrained_loader.py::test_native_booster_feature_metadata_must_agree_with_manifest
FAILED backend/tests/unit/test_pretrained_loader.py::test_native_categorical_metadata_must_agree_with_manifest
FAILED backend/tests/unit/test_pretrained_loader.py::test_unsupported_runtime_rejects_before_native_load[runtime0]
FAILED backend/tests/unit/test_pretrained_loader.py::test_unsupported_runtime_rejects_before_native_load[runtime1]
FAILED backend/tests/unit/test_pretrained_loader.py::test_missing_or_changed_graph_state_fails_before_native_load
FAILED backend/tests/unit/test_pretrained_loader.py::test_incompatible_identity_or_temporal_graph_metadata_is_rejected[account_identity_policy-bank_qualified_as_if_original]
FAILED backend/tests/unit/test_pretrained_loader.py::test_incompatible_identity_or_temporal_graph_metadata_is_rejected[coverage_complete-False]
FAILED backend/tests/unit/test_pretrained_loader.py::test_incompatible_identity_or_temporal_graph_metadata_is_rejected[training_end_exclusive-2026-01-06T00:00:00Z]
FAILED backend/tests/unit/test_pretrained_loader.py::test_untrusted_joblib_and_pickle_are_never_deserialized
FAILED backend/tests/unit/test_pretrained_loader.py::test_loader_never_trains_or_refits_and_never_contacts_network
FAILED backend/tests/unit/test_pretrained_loader.py::test_label_or_holdout_metadata_in_manifest_is_rejected
```
