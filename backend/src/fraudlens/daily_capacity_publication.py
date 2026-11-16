"""Derive a capped, immutable run from a completed boosted score archive."""

import hashlib
import json
import re
from pathlib import Path

from fraudlens.daily_capacity_diagnostic import select_daily_threshold_alerts
from fraudlens.data_store import RunStore

POLICY_ID = 'boosted_utc_daily_top20_v1'
FROZEN_THRESHOLD = '0.9936687168275105'
BOOSTED_SCORER = 'model-history-v1-boosted-candidate'


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def derive_daily_cap_run(source_path: Path, source_run_id: str,
                         target_path: Path, target_run_id: str, *,
                         manifest_sha: str, threshold: str,
                         expected_source_sha256: str | None = None) -> dict:
    """Copy scores verbatim in value, rebind run ID, and publish daily top 20.

    The source is opened read-only and checked before a new target is created.
    All scored rows remain in the derived run; only their alert flags change.
    """
    source_path, target_path = Path(source_path), Path(target_path)
    if (not source_path.is_file() or target_path.exists()
            or source_path.resolve() == target_path.resolve()):
        raise ValueError('source missing or target already exists')
    if (source_run_id == target_run_id or threshold != FROZEN_THRESHOLD
            or re.fullmatch(r'[0-9a-f]{64}', manifest_sha) is None):
        raise ValueError('daily policy identity, manifest or threshold mismatch')
    digest = file_sha256(source_path)
    if expected_source_sha256 is not None and digest != expected_source_sha256:
        raise ValueError('source run-store hash mismatch')

    source = RunStore(source_path, read_only=True)
    try:
        meta = source.connection.execute('''
            SELECT dataset_version,score_source,scorer_version,artifact_sha256,
                   threshold,expected_count,scored_count,total_alerts,status
            FROM scored_runs WHERE run_id=?''', (source_run_id,)).fetchone()
        if meta is not None and meta[3] != manifest_sha:
            raise ValueError('source manifest mismatch')
        if (meta is None or meta[1:5] != ('model', BOOSTED_SCORER,
                                          manifest_sha, threshold)
                or meta[5] != meta[6] or meta[8] != 'completed'):
            raise ValueError('completed boosted source run mismatch')
        if (source.connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='run_policies'").fetchone()
                and source.connection.execute(
                    'SELECT 1 FROM run_policies WHERE run_id=?',
                    (source_run_id,)).fetchone()):
            raise ValueError('source run already has an alert policy')
        alerts = []
        for transaction_id, event_time, score, assessment_json in source.connection.execute('''
            SELECT transaction_id,event_time,score,assessment_json
            FROM scored_assessments WHERE run_id=? AND alert=1''',
            (source_run_id,)):
            assessment = json.loads(assessment_json)
            if (assessment['run_id'] != source_run_id
                    or assessment['transaction_id'] != transaction_id
                    or assessment['score'] != score):
                raise ValueError('source alert assessment mismatch')
            alerts.append({'transaction_id': transaction_id,
                           'event_time': event_time, 'score': score})
        if len(alerts) != meta[7]:
            raise ValueError('source alert count mismatch')
        kept, dropped = select_daily_threshold_alerts(alerts, threshold)
        if len(kept) + len(dropped) != len(alerts):
            raise ValueError('source threshold/alert mismatch')
    finally:
        source.close()

    selection_sha = hashlib.sha256(
        '\n'.join(row['transaction_id'] for row in kept).encode()).hexdigest()
    target = RunStore(target_path)
    try:
        target.begin_run(target_run_id, meta[0], 'model', BOOSTED_SCORER,
                         manifest_sha, threshold, meta[5])
        connection = target.connection
        connection.execute('ATTACH DATABASE ? AS source_scores',
                           (source_path.resolve().as_uri() + '?mode=ro',))
        try:
            connection.execute('CREATE TEMP TABLE selected_ids (transaction_id TEXT PRIMARY KEY)')
            connection.executemany('INSERT INTO selected_ids VALUES(?)',
                                   ((row['transaction_id'],) for row in kept))
            connection.execute('BEGIN IMMEDIATE')
            try:
                connection.execute('''
                    INSERT INTO scored_assessments(
                        run_id,transaction_id,case_id,event_time,score,
                        score_kind,score_source,alert,transaction_json,assessment_json)
                    SELECT ?,s.transaction_id,s.case_id,s.event_time,s.score,
                           s.score_kind,s.score_source,
                           CASE WHEN s.alert=1 AND EXISTS (
                               SELECT 1 FROM selected_ids AS chosen
                               WHERE chosen.transaction_id=s.transaction_id)
                           THEN 1 ELSE 0 END,
                           s.transaction_json,json_set(s.assessment_json,'$.run_id',?)
                    FROM source_scores.scored_assessments AS s
                    WHERE s.run_id=?''',
                    (target_run_id, target_run_id, source_run_id))
                connection.execute('''
                    UPDATE scored_runs SET scored_count=?,total_alerts=?
                    WHERE run_id=?''', (meta[5], len(kept), target_run_id))
                connection.execute('''
                    INSERT INTO run_policies VALUES(?,?,?,?,?,?,?)''',
                    (target_run_id, POLICY_ID, source_run_id, digest,
                     selection_sha, len(alerts), len(dropped)))
                connection.execute('COMMIT')
            except Exception:
                connection.execute('ROLLBACK')
                raise
        finally:
            connection.execute('DETACH DATABASE source_scores')
        target.complete(target_run_id)
        return {'status': 'completed', 'run_id': target_run_id,
                'source_run_id': source_run_id, 'source_store_sha256': digest,
                'policy_id': POLICY_ID, 'selection_sha256': selection_sha,
                'scored_count': meta[5], 'threshold_eligible_count': len(alerts),
                'capacity_excluded_count': len(dropped),
                'total_alerts': len(kept)}
    finally:
        target.close()
