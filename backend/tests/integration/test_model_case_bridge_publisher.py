"""Exercise the publisher itself on a small authored operational snapshot."""

import json
import sqlite3
from contextlib import closing
from types import SimpleNamespace

import pytest

from fraudlens import bridge, bridge_publish
from fraudlens.data.manifest import atomic_write_json, canonical_json_bytes, sha256_file
from fraudlens.data.source import stable_transaction_id


@pytest.fixture
def publisher_inputs(tmp_path, monkeypatch):
    source, features = tmp_path / 'source', tmp_path / 'features'
    source.mkdir()
    features.mkdir()
    canonical = stable_transaction_id(bridge_publish.SOURCE_SHA256, 1)
    instant = '2022-09-06T12:00:00Z'
    accepted = source / 'accepted.jsonl'
    accepted.write_bytes(canonical_json_bytes({
        'amount_paid': '1.2300', 'amount_received': '0.000001',
        'is_laundering': 'SYNTHETIC_LABEL_CANARY', 'payment_currency': 'Australian Dollar',
        'payment_format': 'ACH', 'receiving_currency': 'Bitcoin',
        'receiver_account': '002', 'receiver_bank': 'SYNTH-B', 'receiver_key': 'SYNTH-B/002',
        'sender_account': '001', 'sender_bank': 'SYNTH-A', 'sender_key': 'SYNTH-A/001',
        'source_row_number': 1, 'source_sha256': bridge_publish.SOURCE_SHA256,
        'timestamp': '2022/09/06 12:00', 'transaction_id': canonical,
    }) + b'\n')
    source_manifest = source / 'manifest.json'
    atomic_write_json(source_manifest, {
        'complete': True, 'source_sha256': bridge_publish.SOURCE_SHA256,
        'source_count': 1, 'accepted_count': 1, 'rejected_count': 0,
        'processed_files': [{
            'name': accepted.name, 'size_bytes': accepted.stat().st_size, 'sha256': sha256_file(accepted),
        }],
    })
    (source / 'COMPLETE').write_text(sha256_file(source_manifest) + '\n', encoding='ascii')
    (features / 'train.jsonl').write_bytes(b'')
    (features / 'validation.jsonl').write_bytes(b'')
    (features / 'test.jsonl').write_bytes(canonical_json_bytes({
        'transaction_id': canonical, 'occurred_at_utc': instant, 'features': {},
    }) + b'\n')
    feature_manifest = features / 'manifest.json'
    atomic_write_json(feature_manifest, {
        'source_sha256': bridge_publish.SOURCE_SHA256, 'counts': {'test': 1},
        'files': {split: sha256_file(features / f'{split}.jsonl') for split in ('train', 'validation', 'test')},
    })
    predictions = tmp_path / 'predictions.csv'
    predictions.write_text(f'transaction_id,occurred_at_utc,score\n{canonical},{instant},0.5\n', encoding='ascii')
    monkeypatch.setattr(bridge_publish, 'FEATURE_MANIFEST_SHA256', sha256_file(feature_manifest))
    monkeypatch.setattr(bridge, 'FEATURE_MANIFEST_SHA256', sha256_file(feature_manifest))
    monkeypatch.setattr(bridge_publish, 'PREDICTION_SHA256', sha256_file(predictions))
    score = SimpleNamespace(risk_score=0.5, review_status='review_recommended')
    monkeypatch.setattr(bridge_publish, 'ModelScorer', lambda _: SimpleNamespace(score=lambda _: score))
    return source, features, tmp_path / 'unused-model', predictions, tmp_path / 'publication'


def test_publish_seals_and_activates_label_free_databases(publisher_inputs):
    destination = publisher_inputs[-1]
    manifest = bridge_publish.publish(*publisher_inputs)

    assert manifest['alert_count'] == manifest['operational_event_count'] == 1
    assert not destination.with_name(destination.name + '.partial').exists()
    assert (destination / 'COMPLETE').read_text(encoding='ascii').strip() == sha256_file(destination / 'manifest.json')
    assert manifest == json.loads((destination / 'manifest.json').read_bytes())
    for database in ('dataset', 'runs'):
        assert manifest[f'{database}_sha256'] == sha256_file(destination / f'{database}.sqlite')
    with closing(sqlite3.connect(destination / 'dataset.sqlite')) as db:
        event, = db.execute('SELECT payload_json FROM operational_events').fetchone()
    assert 'SYNTHETIC_LABEL_CANARY' not in event
    assert 'is_laundering' not in event
    assert json.loads(event)['paid_amount'] == '1.2300'
    with closing(sqlite3.connect(destination / 'runs.sqlite')) as db:
        binding, = db.execute('SELECT binding_json FROM bridge_crosswalk').fetchone()
    assert json.loads(binding)['risk_score'] == 0.5
    with pytest.raises(ValueError, match='Publication destination exists'):
        bridge_publish.publish(*publisher_inputs)


def test_publish_refuses_changed_feature_file_before_staging(publisher_inputs):
    features, destination = publisher_inputs[1], publisher_inputs[-1]
    (features / 'test.jsonl').write_bytes(b'')
    with pytest.raises(ValueError, match='Feature partition hash mismatch'):
        bridge_publish.publish(*publisher_inputs)
    assert not destination.exists()
    assert not destination.with_name(destination.name + '.partial').exists()
