"""T041: fitted transform parity and strict v2 model boundary."""

from dataclasses import replace
from decimal import Decimal

import numpy as np
import pytest
from test_rule_scoring import history

from fraudlens.data_contracts import ScoreRequestV2, score_v2
from fraudlens.model_scoring import load_trusted_artifact

ARTIFACT_DIR = 'artifacts/feature-002-history-v1-20261114'
MANIFEST_SHA = '2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e'
PROTOCOL_SHA = '01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068'
DATASET_VERSION = 'dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802'


@pytest.fixture(scope='module')
def artifact():
    return load_trusted_artifact(
        ARTIFACT_DIR, expected_manifest_sha256=MANIFEST_SHA,
        expected_dataset_version=DATASET_VERSION,
        expected_protocol_sha256=PROTOCOL_SHA)


def model_request(*, currency='Euro'):
    fact, snapshot = history(current_currency=currency)
    # Build a valid digest for the model's dataset version.
    from fraudlens.feature_history import _digest

    snapshot = replace(snapshot, dataset_version=DATASET_VERSION,
                       feature_input_digest=_digest(DATASET_VERSION, fact,
                                                    snapshot.feature_values,
                                                    snapshot.coverage_start,
                                                    snapshot.coverage_state))
    return ScoreRequestV2(fact, snapshot, DATASET_VERSION, 'model_run_1',
                          'model-history-v1', 'history-v1', fact.event_time_utc)


def test_model_parity_identity_explanation_and_repeatability(artifact):
    from fraudlens.model_scoring import ModelScorer

    scorer = ModelScorer(artifact)
    req = model_request()
    before = req.feature_snapshot.feature_values.copy()
    first = score_v2(req, scorer, artifact=scorer.artifact_reference)
    second = score_v2(req, scorer, artifact=scorer.artifact_reference)
    row = scorer.input_row(req)
    expected = artifact.pipeline.predict_proba(row)[0, 1]
    assert abs(float(first.score) - expected) <= 1e-12
    assert first.score == second.score
    assert first.score_source == 'model'
    assert first.score_kind == 'uncalibrated_probability_estimate'
    assert first.run_id == req.run_id
    assert first.scored_at >= req.canonical_transaction.event_time_utc
    assert first.explanation.method == 'tree_path'
    assert first.explanation.explained_scale == 'positive_class_estimate'
    assert first.explanation.feature_snapshot_digest == req.feature_snapshot.feature_input_digest
    assert req.feature_snapshot.feature_values == before


def test_unseen_category_no_refit_and_correct_order(artifact, monkeypatch):
    from fraudlens.model_scoring import ModelScorer

    scorer = ModelScorer(artifact)
    req = model_request(currency='Unknown currency')
    prepare = artifact.pipeline.named_steps['prepare']
    monkeypatch.setattr(prepare, 'fit', lambda *args, **kwargs: pytest.fail('refit'))
    monkeypatch.setattr(prepare, 'fit_transform', lambda *args, **kwargs: pytest.fail('refit'))
    row = scorer.input_row(req)
    assert row.shape == (1, 11)
    assert row[0, 9] == 'Unknown currency'
    assert row[0, 10] == 'Wire'
    result = score_v2(req, scorer, artifact=scorer.artifact_reference)
    assert Decimal(0) <= result.score <= Decimal(1)


def test_bad_probability_fails_without_clipping_or_rules_fallback(artifact, monkeypatch):
    from fraudlens.model_scoring import ModelScorer

    scorer = ModelScorer(artifact)
    req = model_request()
    for bad in (np.array([[0.0, np.nan]]), np.array([[0.0, 1.2]])):
        monkeypatch.setattr(artifact.pipeline, 'predict_proba', lambda row, b=bad: b)
        with pytest.raises(ValueError):
            score_v2(req, scorer, artifact=scorer.artifact_reference)


def test_wrong_identity_label_or_artifact_rejected(artifact):
    from fraudlens.model_scoring import ModelScorer

    scorer = ModelScorer(artifact)
    req = model_request()
    with pytest.raises(ValueError):
        score_v2(replace(req, run_id=''), scorer, artifact=scorer.artifact_reference)
    with pytest.raises(TypeError):
        ScoreRequestV2(*tuple(vars(req).values()), label=1)
    with pytest.raises(ValueError):
        score_v2(req, scorer, artifact={'sha256': '0' * 64,
                                       'scorer_version': 'wrong',
                                       'artifact_version': 'wrong'})
