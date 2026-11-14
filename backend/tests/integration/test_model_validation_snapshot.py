"""Read-only first validation prediction probe; never query private labels."""

import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from fraudlens.data_contracts import CanonicalTransaction, ScoreRequestV2
from fraudlens.feature_history import HistoricalFeatureSnapshot
from fraudlens.model_scoring import ModelScorer, load_trusted_artifact

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'data/processed/feature-002-ibm-v8-rules-work.sqlite'
ARTIFACT = ROOT / 'artifacts/feature-002-history-v1-20261114'
PROTOCOL = ROOT / 'evals/protocols/feature_002_v1.json'
MANIFEST_SHA = '2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e'


@pytest.mark.skipif(not STORE.exists() or not ARTIFACT.exists(),
                    reason='local ignored history-v1 evidence unavailable')
def test_frozen_first_validation_prediction_and_explanation():
    protocol = json.loads(PROTOCOL.read_text())
    metadata = json.loads((ARTIFACT / 'metadata.json').read_text())
    loaded = load_trusted_artifact(
        ARTIFACT, expected_manifest_sha256=MANIFEST_SHA,
        expected_dataset_version=protocol['dataset_version'],
        expected_protocol_sha256=metadata['protocol_sha256'])
    connection = sqlite3.connect(f'{STORE.resolve().as_uri()}?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    try:
        assert connection.execute(
            'SELECT status FROM dataset_versions WHERE id=?',
            (protocol['dataset_version'],)).fetchone() == ('complete',)
        assert connection.execute(
            'SELECT status FROM feature_builds WHERE version=? AND feature_version=?',
            (protocol['dataset_version'], 'history-v1')).fetchone() == ('complete',)
        row = connection.execute('''
            SELECT s.transaction_id,e.case_id,e.payload_json,s.event_time,s.as_of,
                   s.coverage_start,s.coverage_state,s.scoreable,
                   s.feature_input_digest,s.created_at,s.payload_json
            FROM feature_snapshots AS s
            JOIN operational_events AS e
              ON e.version=s.version AND e.transaction_id=s.transaction_id
            WHERE s.version=? AND s.feature_version='history-v1' AND s.scoreable=1
              AND s.event_time>? AND s.event_time<=?
            ORDER BY s.event_time,s.transaction_id LIMIT 1
        ''', (protocol['dataset_version'], protocol['split']['train_end_inclusive'],
              protocol['split']['validation_end_inclusive'])).fetchone()
        assert row is not None
    finally:
        connection.close()
    (transaction_id, case_id, event_json, event_time, as_of, coverage_start,
     coverage_state, scoreable, digest, created_at, feature_json) = row
    facts = json.loads(event_json)
    event = CanonicalTransaction(
        transaction_id=transaction_id, case_id=case_id,
        source_ordinal=facts['source_ordinal'],
        event_time_raw=facts['event_time_raw'],
        event_time_utc=datetime.fromisoformat(facts['event_time_utc']),
        event_time_epoch_ns=facts['event_time_epoch_ns'],
        time_basis=facts['time_basis'], sender_bank=facts['sender_bank'],
        sender_account=facts['sender_account'], receiver_bank=facts['receiver_bank'],
        receiver_account=facts['receiver_account'],
        sender_join_key=bytes.fromhex(facts['sender_join_key']),
        receiver_join_key=bytes.fromhex(facts['receiver_join_key']),
        paid_amount=facts['paid_amount'], paid_currency=facts['paid_currency'],
        received_amount=facts['received_amount'],
        received_currency=facts['received_currency'],
        payment_format=facts['payment_format'],
        event_fact_digest=bytes.fromhex(facts['event_fact_digest']))
    values = json.loads(feature_json)
    for key in ('sender_paid_sum_same_currency_24h',
                'receiver_received_sum_same_currency_24h', 'current_paid_amount'):
        values[key] = Decimal(values[key])
    snapshot = HistoricalFeatureSnapshot(
        transaction_id, protocol['dataset_version'], 'history-v1',
        datetime.fromisoformat(event_time), datetime.fromisoformat(as_of),
        datetime.fromisoformat(coverage_start), coverage_state, bool(scoreable),
        values, digest, datetime.fromisoformat(created_at))
    request = ScoreRequestV2(event, snapshot, protocol['dataset_version'],
                             'validation_probe_phase6', 'model-history-v1',
                             'history-v1', event.event_time_utc)
    result = ModelScorer(loaded).assess(request)
    expected = metadata['reload_probe_predictions'][0]
    tolerance = protocol['reproduction_tolerances']['probability_absolute']
    assert abs(float(result.score) - expected) <= tolerance
    explanation = result.explanation
    assert explanation.feature_snapshot_digest == digest
    assert explanation.method == 'tree_path'
    assert explanation.explained_scale == 'positive_class_estimate'
    assert result.transaction_id == transaction_id
    assert result.run_id == request.run_id
    reconstructed = explanation.base_value + explanation.remainder + sum(
        (item['contribution'] for item in explanation.items), Decimal(0))
    assert abs(reconstructed - result.score) <= Decimal(str(
        protocol['reproduction_tolerances']['explanation_reconstruction_absolute']))
    print(json.dumps({'transaction_id': transaction_id, 'run_id': result.run_id,
                      'snapshot_digest': digest, 'prediction': str(result.score),
                      'saved_prediction': expected, 'base': str(explanation.base_value),
                      'remainder': str(explanation.remainder),
                      'items': [{**item, 'contribution': str(item['contribution'])}
                                for item in explanation.items]}))
