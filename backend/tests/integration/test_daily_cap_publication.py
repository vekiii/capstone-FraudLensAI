"""Daily top-20 publication derives a new run from immutable model scores."""

import sqlite3
from datetime import UTC, datetime, timedelta

import pytest
from backend.tests.phase7_samples import VERSION, entry
from fastapi.testclient import TestClient

from fraudlens.data_store import RunStore
from fraudlens.main import create_app
from fraudlens.settings import Settings

MANIFEST = 'a' * 64
SOURCE_RUN = 'run_boosted_source'
TARGET_RUN = 'run_boosted_daily20_test'
THRESHOLD = '0.9936687168275105'


def make_source(path):
    store = RunStore(path)
    store.begin_run(SOURCE_RUN, VERSION, 'model',
                    'model-history-v1-boosted-candidate', MANIFEST,
                    THRESHOLD, 46)
    start = datetime(2022, 9, 2, tzinfo=UTC)
    for index in range(1, 47):
        if index <= 22:
            at = start + timedelta(minutes=index)
            score = 0.999 if index <= 21 else 0.994
        elif index <= 42:
            at = start + timedelta(days=1, minutes=index)
            score = 0.998
        elif index == 43:
            at = start + timedelta(days=2)
            score = 0.1
        else:
            at = start + timedelta(days=3, minutes=index)
            score = 0.99
        case, transaction, assessment = entry(index, run=SOURCE_RUN,
                                                source='model', score=score, at=at)
        assessment['scorer_version'] = 'model-history-v1-boosted-candidate'
        assessment['explanation']['method'] = 'boosted_sequential_probability'
        store.append(SOURCE_RUN, case, transaction, assessment)
    store.complete(SOURCE_RUN)
    store.close()


def test_derived_policy_run_keeps_scores_and_binds_list_detail(tmp_path):
    from fraudlens.daily_capacity_publication import derive_daily_cap_run

    source = tmp_path / 'source.sqlite'
    target = tmp_path / 'target.sqlite'
    make_source(source)
    result = derive_daily_cap_run(source, SOURCE_RUN, target, TARGET_RUN,
                                  manifest_sha=MANIFEST, threshold=THRESHOLD)
    assert result['scored_count'] == 46
    assert result['threshold_eligible_count'] == 42
    assert result['total_alerts'] == 40
    assert result['capacity_excluded_count'] == 2
    original = RunStore(source, read_only=True)
    derived = RunStore(target)
    assert original.connection.execute(
        'SELECT total_alerts FROM scored_runs WHERE run_id=?', (SOURCE_RUN,)
    ).fetchone() == (42,)
    assert derived.connection.execute(
        'SELECT status FROM scored_runs WHERE run_id=?', (TARGET_RUN,)
    ).fetchone() == ('completed',)
    assert derived.connection.execute('''
        SELECT transaction_id FROM scored_assessments
        WHERE run_id=? AND alert=0 AND score>=0.9936687168275105
        ORDER BY transaction_id''',
        (TARGET_RUN,)).fetchall() == [('D' + f'{i:032x}',) for i in (21, 22)]
    derived.activate(TARGET_RUN, 'model', MANIFEST)
    listing = derived.list_active('model')
    assert listing['total_alerts'] == listing['displayed_count'] == 40
    assert listing['alert_policy_id'] == 'boosted_utc_daily_top20_v1'
    assert listing['threshold_eligible_count'] == 42
    assert listing['capacity_excluded_count'] == 2
    with pytest.raises(sqlite3.DatabaseError, match='immutable'):
        derived.connection.execute('''
            UPDATE run_policies SET capacity_excluded_count=0 WHERE run_id=?''',
            (TARGET_RUN,))
    with TestClient(create_app(Settings(mode='dataset', scorer='model',
                                      run_store_path=target))) as api:
        body = api.get('/api/cases').json()
        assert body['total_alerts'] == len(body['items']) == 40
        assert body['alert_policy_id'] == 'boosted_utc_daily_top20_v1'
        for item in body['items']:
            detail = api.get(f'/api/cases/{item["case_id"]}?snapshot={TARGET_RUN}')
            assert detail.status_code == 200
            assert detail.json()['risk_assessment']['score'] == item['score']
            assert detail.json()['risk_assessment']['run_id'] == TARGET_RUN
        excluded = 'C' + f'{21:032x}'
        assert api.get(f'/api/cases/{excluded}?snapshot={TARGET_RUN}').status_code == 404
    original.close()
    derived.close()


def test_derived_policy_rejects_wrong_manifest_or_incomplete_source(tmp_path):
    from fraudlens.daily_capacity_publication import derive_daily_cap_run

    source = tmp_path / 'source.sqlite'
    make_source(source)
    with pytest.raises(ValueError, match='manifest'):
        derive_daily_cap_run(source, SOURCE_RUN, tmp_path / 'bad.sqlite', TARGET_RUN,
                             manifest_sha='b' * 64, threshold=THRESHOLD)
    assert not (tmp_path / 'bad.sqlite').exists()
    with pytest.raises(ValueError, match='hash'):
        derive_daily_cap_run(source, SOURCE_RUN, tmp_path / 'bad-hash.sqlite',
                             TARGET_RUN, manifest_sha=MANIFEST, threshold=THRESHOLD,
                             expected_source_sha256='0' * 64)
    assert not (tmp_path / 'bad-hash.sqlite').exists()
