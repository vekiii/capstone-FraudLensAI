"""T051: dataset API reads one completed scorer-matched run without scoring."""

import pytest
from backend.tests.phase7_samples import VERSION, entry
from fastapi.testclient import TestClient
from pydantic import ValidationError

from fraudlens.data_store import RunStore
from fraudlens.main import create_app
from fraudlens.settings import Settings


def test_dataset_mode_requires_explicit_scorer(tmp_path):
    with pytest.raises(ValidationError):
        Settings(mode='dataset', run_store_path=tmp_path / 'runs.sqlite')


def prepared(tmp_path):
    path = tmp_path / 'runs.sqlite'
    store = RunStore(path)
    store.begin_run('run_one', VERSION, 'rules', 'rules-v1', None, '0.5', 1)
    store.append('run_one', *entry(run='run_one'))
    store.complete('run_one')
    store.activate('run_one', 'rules')
    store.close()
    return path


def client(path, scorer='rules'):
    return TestClient(create_app(Settings(mode='dataset', scorer=scorer,
                                          run_store_path=path)))


def test_list_detail_health_and_stale_switch(tmp_path):
    path = prepared(tmp_path)
    with client(path) as api:
        health = api.get('/api/health')
        assert health.status_code == 200
        assert health.json()['contract_version'] == 2
        assert health.json()['score_source'] == 'rules'
        listing = api.get('/api/cases')
        assert listing.status_code == 200
        body = listing.json()
        assert body['snapshot_ref'] == 'run_one'
        assert body['total_alerts'] == body['displayed_count'] == 1
        case = body['items'][0]['case_id']
        detail = api.get(f'/api/cases/{case}?snapshot=run_one')
        assert detail.status_code == 200
        assert detail.json()['risk_assessment']['run_id'] == 'run_one'
        assert detail.json()['transaction']['paid']['amount'] == '1250.000'
        assert detail.json()['transaction']['received']['currency'] == 'US Dollar'
        assert 'label' not in str(body).lower()
        assert 'label' not in str(detail.json()).lower()
        store = RunStore(path)
        store.begin_run('run_two', VERSION, 'rules', 'rules-v1', None, 'no_alert', 0)
        store.complete('run_two')
        store.activate('run_two', 'rules')
        store.close()
        stale = api.get(f'/api/cases/{case}?snapshot=run_one')
        assert stale.status_code == 409
        assert stale.json()['error']['code'] == 'stale_snapshot'
        empty = api.get('/api/cases')
        assert empty.status_code == 200
        assert empty.json()['items'] == []
        assert empty.json()['selected_time_range'] == {'from': None, 'to': None}


def test_unavailable_invalid_and_no_public_mutation_routes(tmp_path):
    path = tmp_path / 'missing.sqlite'
    with client(path) as api:
        assert api.get('/api/health').json()['status'] == 'unavailable'
        unavailable = api.get('/api/cases')
        assert unavailable.status_code == 503
        assert unavailable.json()['error']['code'] == 'run_unavailable'
        case = 'C' + '1' * 32
        assert api.get(f'/api/cases/{case}').status_code == 422
        assert api.get(f'/api/cases/{case}?snapshot=bad').status_code == 422
        for path_part in ('import', 'train', 'evaluate', 'activate-run'):
            assert api.post(f'/api/{path_part}').status_code in {404, 405}
    path = prepared(tmp_path)
    with client(path, scorer='model') as api:
        assert api.get('/api/cases').status_code == 503
