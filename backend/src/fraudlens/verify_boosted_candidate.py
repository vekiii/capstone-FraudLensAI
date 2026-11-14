"""Label-free isolated publication smoke check for the boosted research candidate."""

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

from fraudlens.data_contracts import ScoreRequestV2
from fraudlens.data_store import RunStore
from fraudlens.main import create_app
from fraudlens.model_scoring import BOOSTED_SCORER_VERSION, ModelScorer, load_trusted_artifact
from fraudlens.pipeline_cli import _public_assessment, _public_transaction, _source_row
from fraudlens.settings import Settings


def verify(source_path: Path, protocol_path: Path, artifact_dir: Path,
           manifest_sha: str, run_store_path: Path) -> dict:
    """Publish only a controlled score-selected validation subset to a new store."""
    if run_store_path.exists() or source_path.resolve() == run_store_path.resolve():
        raise ValueError('isolated run store must be new and distinct')
    protocol_raw = protocol_path.read_bytes()
    protocol = json.loads(protocol_raw)
    artifact = load_trusted_artifact(
        artifact_dir, expected_manifest_sha256=manifest_sha,
        expected_dataset_version=protocol['dataset_version'],
        expected_protocol_sha256=hashlib.sha256(protocol_raw).hexdigest(),
        expected_scorer_version=BOOSTED_SCORER_VERSION)
    scorer = ModelScorer(artifact)
    metadata = json.loads((artifact_dir / 'metadata.json').read_text())
    scores_path = artifact_dir / 'validation_scores.npy'
    if hashlib.sha256(scores_path.read_bytes()).hexdigest() != metadata['validation_scores_sha256']:
        raise ValueError('saved validation scores hash mismatch')
    scores = np.load(scores_path, allow_pickle=False)
    expected_count = protocol['split']['partitions']['validation']['count']
    if scores.shape != (expected_count,) or not np.isfinite(scores).all():
        raise ValueError('saved validation scores incompatible')
    threshold = artifact.manifest['validation_threshold']['threshold']
    positions = set(np.flatnonzero(scores >= threshold).tolist())
    if len(positions) != 20:
        raise ValueError('candidate alert count changed')
    source = sqlite3.connect(f'{source_path.resolve().as_uri()}?mode=ro', uri=True)
    source.execute('PRAGMA query_only=ON')
    source.execute('PRAGMA temp_store=FILE')
    selected = []
    membership = hashlib.sha256()
    try:
        cursor = source.execute('''
            SELECT s.transaction_id,e.case_id,e.payload_json,s.event_time,s.as_of,
                   s.coverage_start,s.coverage_state,s.scoreable,
                   s.feature_input_digest,s.created_at,s.payload_json
            FROM feature_snapshots AS s JOIN operational_events AS e
              ON e.version=s.version AND e.transaction_id=s.transaction_id
            WHERE s.version=? AND s.feature_version='history-v1' AND s.scoreable=1
              AND s.event_time>? AND s.event_time<=?
            ORDER BY s.event_time,s.transaction_id''',
            (protocol['dataset_version'], protocol['split']['train_end_inclusive'],
             protocol['split']['validation_end_inclusive']))
        count = 0
        for index, row in enumerate(cursor):
            count += 1
            membership.update(row[0].encode('ascii') + b'\n')
            if index in positions:
                selected.append((index, row))
        if (count != expected_count
                or membership.hexdigest() != protocol['split']['partitions']
                ['validation']['ids_sha256']):
            raise ValueError('validation membership mismatch')
    finally:
        source.close()
    run_id = 'run_boosted_candidate_smoke'
    store = RunStore(run_store_path)
    try:
        store.begin_run(run_id, protocol['dataset_version'], 'model',
                        BOOSTED_SCORER_VERSION, manifest_sha, str(threshold), len(selected))
        differences = []
        for index, row in selected:
            event, snapshot = _source_row(row, protocol['dataset_version'])
            request = ScoreRequestV2(event, snapshot, protocol['dataset_version'],
                                     run_id, BOOSTED_SCORER_VERSION, 'history-v1',
                                     event.event_time_utc)
            assessment = scorer.assess(request)
            differences.append(abs(float(assessment.score) - float(scores[index])))
            store.append(run_id, event.case_id, _public_transaction(event),
                         _public_assessment(assessment))
        store.complete(run_id)
        # This is an isolated throwaway store; the shared active pointer is untouched.
        store.activate(run_id, 'model', manifest_sha)
    finally:
        store.close()
    with TestClient(create_app(Settings(mode='dataset', scorer='model',
                                        run_store_path=run_store_path))) as client:
        health = client.get('/api/health')
        listing = client.get('/api/cases')
        if health.status_code != 200 or listing.status_code != 200:
            raise ValueError('candidate API unavailable')
        body = listing.json()
        if (body['snapshot_ref'] != run_id or body['total_alerts'] != 20
                or body['displayed_count'] != 20
                or body['scorer_version'] != BOOSTED_SCORER_VERSION):
            raise ValueError('candidate API list mismatch')
        details = []
        for item in body['items']:
            response = client.get(
                f"/api/cases/{item['case_id']}?snapshot={body['snapshot_ref']}")
            if response.status_code != 200:
                raise ValueError('candidate API detail unavailable')
            detail = response.json()
            assessment = detail['risk_assessment']
            if (assessment['explanation']['method'] != 'boosted_sequential_probability'
                    or assessment['scorer_version'] != BOOSTED_SCORER_VERSION):
                raise ValueError('candidate API explanation mismatch')
            details.append(detail)
    return {'status': 'isolated_validation_smoke', 'run_id': run_id,
            'validation_rows': expected_count, 'score_selected': len(selected),
            'api_alerts': body['total_alerts'], 'api_displayed': body['displayed_count'],
            'api_details_checked': len(details),
            'explanation_method': 'boosted_sequential_probability',
            'max_abs_score_diff': max(differences),
            'source_read_only': True, 'labels_read': False,
            'shared_active_pointer_changed': False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--artifact-dir', type=Path, required=True)
    parser.add_argument('--manifest-sha', required=True)
    parser.add_argument('--run-store', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.source, args.protocol, args.artifact_dir,
                            args.manifest_sha, args.run_store), sort_keys=True))


if __name__ == '__main__':
    main()
