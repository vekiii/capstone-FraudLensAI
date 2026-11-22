"""New opt-in bridge route; run RED before adding its router."""

from fastapi.testclient import TestClient

from fraudlens.main import create_app
from fraudlens.settings import Settings


def test_model_bridge_binding_route_is_explicit_and_has_no_fixture_fallback(monkeypatch):
    monkeypatch.setenv('MODEL_CASE_BRIDGE_ROOT', '/missing/bridge')
    app = create_app(settings=Settings(mode='model'), model_scorer=object(), feature_store=object())
    canonical = ('ibm-hi-small:' + 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
                 + ':row:1936564')
    with TestClient(app) as client:
        response = client.get('/api/model/cases/by-transaction/' + canonical)
        assert response.status_code == 503
        assert response.json()['error']['code'] == 'run_unavailable'
        assert client.get('/api/cases/CASE-001').status_code == 200
