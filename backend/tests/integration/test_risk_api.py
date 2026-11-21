"""T231 RED: model API behavior independent of real labels/artifacts."""
from fastapi.testclient import TestClient

from fraudlens.contracts import PredictionResult
from fraudlens.main import create_app
from fraudlens.scoring.model_scorer import FeatureTransaction
from fraudlens.settings import Settings

ID = 'ibm-hi-small:' + 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040' + ':row:12'


class Store:
    def __init__(self, record):
        self.record = record

    def get(self, _identity):
        return self.record


class Scorer:
    def __init__(self, result):
        self.result = result

    def score(self, _record):
        return self.result


def result(identity=ID, score=0.4):
    return PredictionResult(transaction_id=identity, risk_score=score,
                            review_status='review_recommended', source='model',
                            model_version='lightgbm-test', feature_version='hi-small-temporal-v1',
                            synthetic_data=True, scored_at='2022-09-06T00:00:00Z',
                            explanation='Observed facts; analyst review required.')


def app(record, scored):
    return create_app(settings=Settings(mode='model'), feature_store=Store(record),
                      model_scorer=Scorer(scored))


def test_fixture_mode_remains_artifact_free_and_model_route_unavailable():
    with TestClient(create_app(settings=Settings())) as client:
        assert client.get('/api/health').status_code == 200
        assert client.get('/api/cases').status_code == 200
        response = client.get(f'/api/transactions/{ID}/risk')
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'model_unavailable'


def test_model_success_is_read_only_and_keeps_foundation_cases():
    record = FeatureTransaction(ID, '2022-09-06T00:00:00+00:00', {})
    with TestClient(app(record, result())) as client:
        response = client.get(f'/api/transactions/{ID}/risk')
        assert client.get('/api/cases').status_code == 200
        assert client.get('/api/health').json()['mode'] == 'model'
    assert response.status_code == 200
    assert response.json()['transaction_id'] == ID
    assert 'label' not in response.json()


def test_model_route_controlled_negative_cases():
    eligible = FeatureTransaction(ID, '2022-09-06T00:00:00+00:00', {})
    cases = [(None, result(), 404, 'transaction_not_found'),
             (FeatureTransaction(ID, eligible.occurred_at_utc, {}, False), result(),
              409, 'transaction_ineligible'),
             (FeatureTransaction(ID + '3', eligible.occurred_at_utc, {}), result(),
              503, 'model_unavailable'),
             (eligible, result(ID + '3'), 503, 'model_unavailable'),
             (eligible, {'risk_score': float('nan')}, 503, 'model_unavailable')]
    for record, scored, status, code in cases:
        with TestClient(app(record, scored)) as client:
            response = client.get(f'/api/transactions/{ID}/risk')
        assert response.status_code == status
        assert response.json()['error']['code'] == code


def test_model_mode_missing_artifact_never_falls_back_to_fixture():
    with TestClient(create_app(settings=Settings(mode='model',
                                                model_artifact_root='/missing/artifacts',
                                                model_feature_root='/missing/features'))) as client:
        response = client.get(f'/api/transactions/{ID}/risk')
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'model_unavailable'


def test_invalid_canonical_id_is_rejected_before_lookup():
    with TestClient(app(None, result())) as client:
        response = client.get('/api/transactions/TX-001/risk')
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'invalid_request'
