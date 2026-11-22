"""Offline, bounded publication of frozen development alerts and label-free facts."""

import csv
import hashlib
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from fraudlens.bridge import identity, validate_binding, validate_crosswalk
from fraudlens.data.features import FEATURE_VERSION, normalize_timestamp_utc
from fraudlens.data.manifest import canonical_json_bytes, sha256_file, verify_completed_snapshot
from fraudlens.data.source import stable_transaction_id
from fraudlens.data.training_input import _without_label
from fraudlens.investigation.models import validate
from fraudlens.scoring.model_scorer import (
    FEATURE_MANIFEST_SHA256,
    MANIFEST_SHA256,
    MODEL_SHA256,
    SOURCE_SHA256,
    THRESHOLD,
    FeatureTransaction,
    ModelScorer,
)

PREDICTION_SHA256 = '99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7'


def utc(value):
    return normalize_timestamp_utc(value).isoformat().replace('+00:00', 'Z')


def _source_row(raw):
    row = _without_label(raw)
    if (row['source_sha256'] != SOURCE_SHA256
            or row['transaction_id'] != stable_transaction_id(SOURCE_SHA256, row['source_row_number'])):
        raise ValueError('Canonical source identity mismatch')
    return row


def _transaction(row):
    tx_id = identity(row['transaction_id'], 'tx')[0]
    return dict(transaction_id=tx_id, event_time_utc=utc(row['timestamp']),
                event_time_raw=row['timestamp'], time_basis='assumed_utc_for_synthetic_benchmark',
                sender=dict(bank=row['sender_bank'], account=row['sender_account']),
                receiver=dict(bank=row['receiver_bank'], account=row['receiver_account']),
                paid=dict(amount=row['amount_paid'], currency=row['payment_currency']),
                received=dict(amount=row['amount_received'], currency=row['receiving_currency']),
                payment_format=row['payment_format'])


def publish(source_root: Path, feature_root: Path, artifact_root: Path,
            predictions: Path, destination: Path) -> dict:
    """Verify frozen inputs, strip labels before parsing, stage and atomically activate."""
    if destination.exists() or destination.with_name(destination.name + '.partial').exists():
        raise ValueError('Publication destination exists')
    manifest = verify_completed_snapshot(source_root)
    accepted_sha = next(item['sha256'] for item in manifest['processed_files']
                        if item['name'] == 'accepted.jsonl')
    if (manifest['source_sha256'] != SOURCE_SHA256 or manifest['rejected_count'] != 0
            or sha256_file(feature_root / 'manifest.json') != FEATURE_MANIFEST_SHA256
            or sha256_file(predictions) != PREDICTION_SHA256):
        raise ValueError('Frozen input identity mismatch')
    feature_manifest = json.loads((feature_root / 'manifest.json').read_bytes())
    if (feature_manifest['source_sha256'] != SOURCE_SHA256
            or set(feature_manifest['files']) != {'train', 'validation', 'test'}):
        raise ValueError('Feature partition mismatch')
    for partition, digest in feature_manifest['files'].items():
        if sha256_file(feature_root / f'{partition}.jsonl') != digest:
            raise ValueError('Feature partition hash mismatch')
    with predictions.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['transaction_id', 'occurred_at_utc', 'score']:
            raise ValueError('Unexpected prediction columns')
        alerts = {}
        count = 0
        for row in reader:
            count += 1
            score = float(row['score'])
            if score >= THRESHOLD:
                if row['transaction_id'] in alerts:
                    raise ValueError('Duplicate frozen prediction')
                alerts[row['transaction_id']] = row
    if count != feature_manifest['counts']['test'] or not alerts:
        raise ValueError('Frozen prediction count mismatch')
    features = {}
    with (feature_root / 'test.jsonl').open(encoding='utf-8') as stream:
        for raw in stream:
            row = json.loads(raw)
            canonical = row['transaction_id']
            if canonical in alerts:
                if canonical in features or row['occurred_at_utc'] != alerts[canonical]['occurred_at_utc']:
                    raise ValueError('Feature identity/time mismatch')
                features[canonical] = row
    if set(features) != set(alerts):
        raise ValueError('Alert feature rows missing')
    scorer = ModelScorer(artifact_root)
    for canonical, row in features.items():
        prediction = scorer.score(FeatureTransaction(**row))
        if (prediction.risk_score != float(alerts[canonical]['score'])
                or prediction.review_status != 'review_recommended'):
            raise ValueError('Frozen score parity mismatch')
    # Pass 1 reads only matching focal rows; the label token is stripped before JSON parsing.
    focal = {}
    with (source_root / 'accepted.jsonl').open('rb') as stream:
        marker = b'"transaction_id":"'
        for raw in stream:
            position = raw.find(marker)
            if position < 0:
                raise ValueError('Malformed canonical source line')
            start = position + len(marker)
            end = raw.find(b'"', start)
            canonical = raw[start:end].decode('ascii')
            if canonical in alerts:
                if canonical in focal:
                    raise ValueError('Duplicate focal source row')
                focal[canonical] = _source_row(raw)
    if set(focal) != set(alerts):
        raise ValueError('Focal facts missing')
    accounts = {(row[side + '_bank'], row[side + '_account'])
                for row in focal.values() for side in ('sender', 'receiver')}
    dataset_version = 'dv_' + hashlib.sha256(
        canonical_json_bytes({'source': SOURCE_SHA256, 'accepted': accepted_sha,
                              'mapping': 'model-case-bridge-v1-label-free'})).hexdigest()
    run_id = 'run_bridge_' + hashlib.sha256(canonical_json_bytes(
        {'dataset': dataset_version, 'model': MODEL_SHA256, 'features': FEATURE_MANIFEST_SHA256,
         'predictions': PREDICTION_SHA256, 'threshold': THRESHOLD})).hexdigest()[:24]
    stage = destination.with_name(destination.name + '.partial')
    stage.mkdir(parents=True)
    try:
        dataset_path, runs_path = stage / 'dataset.sqlite', stage / 'runs.sqlite'
        with closing(sqlite3.connect(dataset_path)) as db, db:
            db.executescript('''CREATE TABLE dataset_versions(id TEXT PRIMARY KEY,status TEXT,rejected_records INTEGER);
                CREATE TABLE active_dataset(singleton INTEGER PRIMARY KEY,version TEXT);
                CREATE TABLE operational_events(version TEXT,transaction_id TEXT,case_id TEXT,payload_json TEXT);
                CREATE INDEX history_version ON operational_events(version,transaction_id);''')
            db.execute('INSERT INTO dataset_versions VALUES(?,?,0)', (dataset_version, 'complete'))
            db.execute('INSERT INTO active_dataset VALUES(1,?)', (dataset_version,))
            selected = 0
            seen_ids = set()
            with (source_root / 'accepted.jsonl').open('rb') as stream:
                for raw in stream:
                    row = _source_row(raw)
                    if (row['sender_bank'], row['sender_account']) not in accounts and (
                            row['receiver_bank'], row['receiver_account']) not in accounts:
                        continue
                    tx = _transaction(row)
                    if tx['transaction_id'] in seen_ids:
                        raise ValueError('History ID collision')
                    seen_ids.add(tx['transaction_id'])
                    event = dict(event_time_utc=tx['event_time_utc'].replace('Z', '+00:00'),
                                 event_time_raw=tx['event_time_raw'], time_basis=tx['time_basis'],
                                 sender_bank=tx['sender']['bank'], sender_account=tx['sender']['account'],
                                 receiver_bank=tx['receiver']['bank'], receiver_account=tx['receiver']['account'],
                                 paid_amount=tx['paid']['amount'], paid_currency=tx['paid']['currency'],
                                 received_amount=tx['received']['amount'], received_currency=tx['received']['currency'])
                    db.execute('INSERT INTO operational_events VALUES(?,?,?,?)',
                               (dataset_version, tx['transaction_id'], None, canonical_json_bytes(event).decode()))
                    selected += 1
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        start = '2022-09-01T00:00:00Z'  # verified T210 source start; conservative incomplete coverage below
        bindings = []
        with closing(sqlite3.connect(runs_path)) as db, db:
            db.executescript('''CREATE TABLE scored_runs(run_id TEXT PRIMARY KEY,dataset_version TEXT,score_source TEXT,scorer_version TEXT,status TEXT);
                CREATE TABLE active_run(singleton INTEGER PRIMARY KEY,run_id TEXT);
                CREATE TABLE scored_assessments(run_id TEXT,case_id TEXT,transaction_json TEXT,assessment_json TEXT,alert INTEGER,
                  PRIMARY KEY(run_id,case_id));
                CREATE TABLE bridge_crosswalk(canonical_id TEXT PRIMARY KEY,case_id TEXT UNIQUE,transaction_id TEXT UNIQUE,
                  binding_json TEXT NOT NULL);''')
            for canonical, row in sorted(focal.items()):
                feature = features[canonical]
                event_time = utc(row['timestamp'])
                if event_time != utc(alerts[canonical]['occurred_at_utc']):
                    raise ValueError('Focal time mismatch')
                case_id, case_digest = identity(canonical, 'case')
                tx_id, tx_digest = identity(canonical, 'tx')
                score = float(alerts[canonical]['score'])
                binding = dict(contract_version=1, canonical_transaction_id=canonical,
                    case_id=case_id, transaction_id=tx_id, case_digest=case_digest,
                    transaction_digest=tx_digest, snapshot_ref=run_id, dataset_version=dataset_version,
                    model_sha256=MODEL_SHA256, feature_version=FEATURE_VERSION,
                    feature_manifest_sha256=FEATURE_MANIFEST_SHA256, source_sha256=SOURCE_SHA256,
                    threshold=THRESHOLD, risk_score=score, review_status='review_recommended',
                    event_time_utc=event_time, assessed_at_utc=now)
                validate_binding(binding)
                bindings.append(binding)
                tx = _transaction(row)
                coverage = dict(state='incomplete', start=start)
                assessment = dict(transaction_id=tx_id, run_id=run_id, dataset_version=dataset_version,
                    score=score, score_kind='uncalibrated_probability_estimate', score_source='model',
                    scorer_version='lightgbm-'+MODEL_SHA256[:12], feature_version=FEATURE_VERSION,
                    event_time_utc=event_time, history_cutoff_exclusive_at=event_time,
                    scored_at=now, history_coverage=coverage,
                    explanation=dict(status='unavailable', reason_code='unsupported_method',
                                     feature_snapshot_digest='sha256:'+hashlib.sha256(canonical_json_bytes(feature['features'])).hexdigest()))
                validate('InvestigationContext', _context_example(case_id, run_id, dataset_version, tx, assessment))
                db.execute('INSERT INTO scored_assessments VALUES(?,?,?,?,1)',
                           (run_id, case_id, canonical_json_bytes(tx).decode(), canonical_json_bytes(assessment).decode()))
                db.execute('INSERT INTO bridge_crosswalk VALUES(?,?,?,?)',
                           (canonical, case_id, tx_id, canonical_json_bytes(binding).decode()))
            validate_crosswalk(bindings)
            db.execute('INSERT INTO scored_runs VALUES(?,?,?,?,?)',
                       (run_id, dataset_version, 'model', 'lightgbm-'+MODEL_SHA256[:12], 'completed'))
            db.execute('INSERT INTO active_run VALUES(1,?)', (run_id,))
        published = dict(bridge_version=1, status='complete', source_sha256=SOURCE_SHA256,
                         accepted_sha256=accepted_sha,
                         feature_manifest_sha256=FEATURE_MANIFEST_SHA256, model_sha256=MODEL_SHA256,
                         model_manifest_sha256=MANIFEST_SHA256, predictions_sha256=PREDICTION_SHA256,
                         threshold=THRESHOLD, dataset_version=dataset_version, run_id=run_id,
                         alert_count=len(bindings), operational_event_count=selected,
                         assessed_at_utc=now, runs_sha256=sha256_file(runs_path),
                         dataset_sha256=sha256_file(dataset_path))
        (stage / 'manifest.json').write_bytes(canonical_json_bytes(published)+b'\n')
        (stage / 'COMPLETE').write_text(sha256_file(stage / 'manifest.json')+'\n')
        os.replace(stage, destination)
        return published
    except Exception:
        # Leave the incomplete stage for forensics; it is never active.
        raise


def _context_example(case_id, run_id, dataset_version, tx, assessment):
    from fraudlens.investigation.models import context_digest
    context = dict(contract_version=2, source_mode='dataset', case_id=case_id,
                   snapshot_ref=run_id, dataset_version=dataset_version,
                   observed_at=assessment['scored_at'],
                   source_payload=dict(contract_version=2, case_id=case_id,
                                       snapshot_ref=run_id, dataset_version=dataset_version,
                                       transaction=tx, risk_assessment=assessment),
                   history=dict(availability='available', coverage='incomplete',
                                cutoff=assessment['history_cutoff_exclusive_at'],
                                start=assessment['history_coverage']['start'], lookback_days=7,
                                view_scope='synthetic_shared_banks', reason='Source begins after seven-day start.'))
    context['context_revision'] = context_digest(context)
    return context
