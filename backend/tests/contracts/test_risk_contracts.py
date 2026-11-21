"""T231 RED: closed Feature 002 prediction contract."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from fraudlens.contracts import ModelResults, PredictionResult


def test_prediction_contract_rejects_labels_and_invalid_scores():
    valid = dict(transaction_id='ibm-hi-small:' + 'a' * 64 + ':row:1', risk_score=0.4,
                 review_status='below_threshold', source='model',
                 model_version='lightgbm-3b4e4019', feature_version='hi-small-temporal-v1',
                 synthetic_data=True, scored_at='2022-09-06T00:00:00Z',
                 explanation='Observed transaction features only.')
    PredictionResult.model_validate(valid)
    schema = json.loads((Path(__file__).resolve().parents[3] /
                         'specs/002-data-and-risk-scoring/contracts/schemas.json').read_text())
    validator = Draft202012Validator({**schema, '$ref': '#/$defs/PredictionResult'},
                                     format_checker=FormatChecker())
    assert validator.is_valid(valid)
    for extra in ({'label': 1}, {'is_laundering': 1}, {'risk_score': float('nan')},
                  {'risk_score': 1.1}):
        if not (isinstance(extra.get('risk_score'), float) and
                extra['risk_score'] != extra['risk_score']):
            assert not validator.is_valid({**valid, **extra})
        with pytest.raises(ValidationError):
            PredictionResult.model_validate({**valid, **extra})


def test_model_results_contract_is_closed_and_aggregate_only():
    body = {
        'model_version': 'lightgbm-test', 'feature_version': 'hi-small-temporal-v1',
        'dataset_version': 'ibm-hi-small-sha256:test', 'threshold': 0.2489517623052024,
        'calibration_status': 'not_assessed',
        'partitions': [{
            'partition': 'validation', 'state': 'available', 'synthetic_data': True,
            'coverage_utc': '2022-09-05 UTC', 'row_count': 2, 'positive_count': 1,
            'negative_count': 1,
            'metrics': [{'name': 'Precision', 'value': 0.5, 'denominator': 2,
                         'unit': 'ratio'}],
        }], 'limitations': ['Synthetic local result.'],
    }
    schema = json.loads((Path(__file__).resolve().parents[3] /
                         'specs/002-data-and-risk-scoring/contracts/schemas.json').read_text())
    validator = Draft202012Validator({**schema, '$ref': '#/$defs/ModelResults'},
                                     format_checker=FormatChecker())
    assert validator.is_valid(body)
    ModelResults.model_validate(body)
    for invalid in ({**body, 'is_laundering': 1},
                    {**body, 'partitions': [{**body['partitions'][0], 'transaction_id': 'x'}]},
                    {**body, 'partitions': [{**body['partitions'][0], 'metrics': [
                        {'name': 'Precision', 'value': float('inf'), 'denominator': 2,
                         'unit': 'ratio'}]}]}):
        with pytest.raises(ValidationError):
            ModelResults.model_validate(invalid)
