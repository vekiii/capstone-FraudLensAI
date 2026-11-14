"""Create disposable label-free Phase 7 browser runs; never touch IBM SQLite."""

import hashlib
import json
import sys
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

from backend.tests.unit.test_rule_scoring import history

from fraudlens.data_contracts import ScoreRequestV2, score_v2
from fraudlens.data_store import RunStore
from fraudlens.feature_history import _digest
from fraudlens.model_scoring import ModelScorer, load_trusted_artifact
from fraudlens.pipeline_cli import _public_assessment, _public_transaction
from fraudlens.rule_scoring import RuleScorer

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / 'artifacts/feature-002-history-v1-20261114'
PROTOCOL = ROOT / 'evals/protocols/feature_002_v1.json'
VERSION = 'dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802'
MANIFEST_SHA = '2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e'


def request(index, run_id, scorer_version):
    event, snapshot = history()
    at = event.event_time_utc + timedelta(minutes=index)
    event = replace(event, transaction_id=f'D{index:032x}', case_id=f'C{index:032x}',
                    event_time_utc=at, event_time_epoch_ns=int(at.timestamp()) * 10**9,
                    event_time_raw=at.strftime('%Y/%m/%d %H:%M'))
    snapshot = replace(snapshot, transaction_id=event.transaction_id,
                       dataset_version=VERSION, event_time=at, as_of=at,
                       feature_input_digest=_digest(VERSION, event,
                                                    snapshot.feature_values,
                                                    snapshot.coverage_start,
                                                    snapshot.coverage_state))
    return ScoreRequestV2(event, snapshot, VERSION, run_id, scorer_version,
                          'history-v1', at)


def create(path: Path):
    if path.exists():
        raise ValueError('controlled run store already exists')
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    model = ModelScorer(load_trusted_artifact(
        ARTIFACT, expected_manifest_sha256=MANIFEST_SHA,
        expected_dataset_version=VERSION, expected_protocol_sha256=protocol_sha))
    store = RunStore(path)
    try:
        store.begin_run('run_rules_102', VERSION, 'rules', 'rules-v1', None, '0.5', 102)
        for index in range(1, 103):
            scored = request(index, 'run_rules_102', 'rules-v1')
            result = score_v2(scored, RuleScorer())
            store.append('run_rules_102', scored.canonical_transaction.case_id,
                         _public_transaction(scored.canonical_transaction),
                         _public_assessment(result))
        store.complete('run_rules_102')
        store.begin_run('run_model_control', VERSION, 'model', 'model-history-v1',
                        MANIFEST_SHA, '0', 1)
        scored = request(1001, 'run_model_control', 'model-history-v1')
        result = model.assess(scored)
        store.append('run_model_control', scored.canonical_transaction.case_id,
                     _public_transaction(scored.canonical_transaction),
                     _public_assessment(result))
        store.complete('run_model_control')
        store.begin_run('run_empty_control', VERSION, 'rules', 'rules-v1',
                        None, 'no_alert', 0)
        store.complete('run_empty_control')
        store.activate('run_rules_102', 'rules')
        print(json.dumps({'rules_alerts': store.list_active('rules')['total_alerts'],
                          'rules_displayed': store.list_active('rules')['displayed_count'],
                          'model_score': str(result.score),
                          'model_digest': scored.feature_snapshot.feature_input_digest,
                          'model_manifest_sha256': MANIFEST_SHA,
                          'run_store': str(path)}))
    finally:
        store.close()


if __name__ == '__main__':
    create(Path(sys.argv[1]))
