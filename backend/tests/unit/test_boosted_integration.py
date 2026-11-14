"""Controlled boosted candidate trust, explanation and publication boundaries."""

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from test_rule_scoring import history

from fraudlens.explanations import additive_explanation

ARTIFACT = Path('artifacts/feature-002-boosted-validation-20261114')
MANIFEST_SHA = '013c7ebe5ab5a5270a7b66af200060d3499c31eb2598c06a038ca887fd9320a6'
PROTOCOL_SHA = '01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068'
VERSION = 'dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802'


def test_boosted_probability_explanation_reconstructs_score():
    fact, snapshot = history()
    from fraudlens.data_contracts import ScoreRequestV2

    request = ScoreRequestV2(fact, snapshot, snapshot.dataset_version,
                             'run_boost_test', 'model-history-v1-boosted-candidate',
                             'history-v1', fact.event_time_utc)
    explanation = additive_explanation(
        request, [('sender_out_count_24h', Decimal('0.2'))],
        base=Decimal('0.3'), scale='positive_class_estimate',
        method='boosted_sequential_probability', expected=Decimal('0.5'),
        tolerance=Decimal('1e-8'))
    assert explanation['method'] == 'boosted_sequential_probability'
    assert explanation['base_value'] + explanation['items'][0]['contribution'] == Decimal('0.5')


def test_wrong_boosted_method_scale_rejected():
    fact, snapshot = history()
    from fraudlens.data_contracts import ScoreRequestV2

    request = ScoreRequestV2(fact, snapshot, snapshot.dataset_version,
                             'run_boost_test', 'model-history-v1-boosted-candidate',
                             'history-v1', fact.event_time_utc)
    with pytest.raises(ValueError):
        additive_explanation(request, [], base=Decimal('0'), scale='log_odds',
                             method='boosted_sequential_probability',
                             expected=Decimal('0'), tolerance=Decimal('1e-8'))


def test_trusted_boosted_reload_and_explanation():
    from fraudlens.data_contracts import ScoreRequestV2
    from fraudlens.feature_history import _digest
    from fraudlens.model_scoring import BOOSTED_SCORER_VERSION, ModelScorer, load_trusted_artifact

    artifact = load_trusted_artifact(
        ARTIFACT, expected_manifest_sha256=MANIFEST_SHA,
        expected_dataset_version=VERSION, expected_protocol_sha256=PROTOCOL_SHA,
        expected_scorer_version=BOOSTED_SCORER_VERSION)
    scorer = ModelScorer(artifact)
    fact, snapshot = history()
    snapshot = replace(snapshot, dataset_version=VERSION,
                       feature_input_digest=_digest(
                           VERSION, fact, snapshot.feature_values,
                           snapshot.coverage_start, snapshot.coverage_state))
    request = ScoreRequestV2(fact, snapshot, VERSION, 'run_boost_test',
                             BOOSTED_SCORER_VERSION, 'history-v1', fact.event_time_utc)
    first = scorer.assess(request)
    second = scorer.assess(request)
    assert first.score == second.score
    assert first.explanation.method == 'boosted_sequential_probability'
    assert first.explanation.feature_snapshot_digest == snapshot.feature_input_digest
    assert first.score_source == 'model'
    assert first.score_kind == 'uncalibrated_probability_estimate'
    assert first.scorer_version == BOOSTED_SCORER_VERSION


def test_boosted_explanation_batches_counterfactual_predictions(monkeypatch):
    from fraudlens.data_contracts import ScoreRequestV2
    from fraudlens.feature_history import _digest
    from fraudlens.model_scoring import BOOSTED_SCORER_VERSION, ModelScorer, load_trusted_artifact

    artifact = load_trusted_artifact(
        ARTIFACT, expected_manifest_sha256=MANIFEST_SHA,
        expected_dataset_version=VERSION, expected_protocol_sha256=PROTOCOL_SHA,
        expected_scorer_version=BOOSTED_SCORER_VERSION)
    scorer = ModelScorer(artifact)
    fact, snapshot = history()
    snapshot = replace(snapshot, dataset_version=VERSION,
                       feature_input_digest=_digest(
                           VERSION, fact, snapshot.feature_values,
                           snapshot.coverage_start, snapshot.coverage_state))
    request = ScoreRequestV2(fact, snapshot, VERSION, 'run_boost_batch',
                             BOOSTED_SCORER_VERSION, 'history-v1', fact.event_time_utc)
    calls = []
    predict = artifact.pipeline.predict_proba

    def tracked(values):
        calls.append(values.shape)
        return predict(values)

    monkeypatch.setattr(artifact.pipeline, 'predict_proba', tracked)
    assessment = scorer.assess(request)
    assert calls == [(1, 11), (12, 11)]
    explanation = assessment.explanation
    reconstructed = explanation.base_value + explanation.remainder + sum(
        (item['contribution'] for item in explanation.items), Decimal(0))
    assert abs(reconstructed - assessment.score) <= Decimal('1e-8')


def test_boosted_assess_batch_matches_individual_scoring(monkeypatch):
    from fraudlens.data_contracts import ScoreRequestV2
    from fraudlens.feature_history import _digest
    from fraudlens.model_scoring import BOOSTED_SCORER_VERSION, ModelScorer, load_trusted_artifact

    artifact = load_trusted_artifact(
        ARTIFACT, expected_manifest_sha256=MANIFEST_SHA,
        expected_dataset_version=VERSION, expected_protocol_sha256=PROTOCOL_SHA,
        expected_scorer_version=BOOSTED_SCORER_VERSION)
    scorer = ModelScorer(artifact)
    fact, snapshot = history()
    snapshot = replace(snapshot, dataset_version=VERSION,
                       feature_input_digest=_digest(
                           VERSION, fact, snapshot.feature_values,
                           snapshot.coverage_start, snapshot.coverage_state))
    request = ScoreRequestV2(fact, snapshot, VERSION, 'run_boost_batch',
                             BOOSTED_SCORER_VERSION, 'history-v1', fact.event_time_utc)
    individual = scorer.assess(request)
    second = replace(request, run_id='run_boost_batch_2')
    calls = []
    predict = artifact.pipeline.predict_proba

    def tracked(values):
        calls.append(values.shape)
        return predict(values)

    monkeypatch.setattr(artifact.pipeline, 'predict_proba', tracked)
    batched = scorer.assess_batch([request, second])
    assert calls == [(24, 11)]
    assert [item.score for item in batched] == [individual.score] * 2
    assert [item.explanation for item in batched] == [individual.explanation] * 2
    assert [item.run_id for item in batched] == ['run_boost_batch', 'run_boost_batch_2']


def test_wrong_boosted_version_rejected_before_deserialization(monkeypatch):
    import fraudlens.model_scoring as module
    from fraudlens.model_scoring import load_trusted_artifact

    monkeypatch.setattr(module.joblib, 'load', lambda *_: pytest.fail('deserialized'))
    with pytest.raises(ValueError, match='origin or version'):
        load_trusted_artifact(
            ARTIFACT, expected_manifest_sha256=MANIFEST_SHA,
            expected_dataset_version=VERSION, expected_protocol_sha256=PROTOCOL_SHA)
