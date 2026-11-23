"""Read-only, label-free frozen-bridge contribution probe; no evaluation labels."""

import hashlib
import json
import math
import sqlite3
from pathlib import Path

from fraudlens.bridge import validate_crosswalk
from fraudlens.bridge_reader import BridgeReader
from fraudlens.scoring.local_contributions import compute_local_contributions, stable_binary_score
from fraudlens.scoring.model_scorer import FeatureStore, FeatureTransaction, ModelScorer

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / 'data/processed/model-case-bridge-v1'
FEATURES = ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'
ARTIFACTS = ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts'
BRIDGE_SHA = '16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004'


def main():
    bridge = BridgeReader(BRIDGE, BRIDGE_SHA)
    manifest = bridge._check()
    with sqlite3.connect((BRIDGE / 'runs.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as db:
        bindings = [json.loads(row[0]) for row in db.execute(
            'SELECT binding_json FROM bridge_crosswalk ORDER BY canonical_id')]
    validate_crosswalk(bindings)
    assert len(bindings) == manifest['alert_count'] == 65
    selected = {row['canonical_transaction_id']: row for row in bindings}
    store = FeatureStore(FEATURES)
    rows = {}
    for path in store.paths:
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for line in stream:
                digest.update(line)
                if b'ibm-hi-small:' not in line:
                    continue
                item = json.loads(line)
                if item['transaction_id'] in selected:
                    assert item['transaction_id'] not in rows
                    rows[item['transaction_id']] = item
        assert digest.hexdigest() == store.expected_files[path.stem]
    assert set(rows) == set(selected)
    scorer = ModelScorer(ARTIFACTS)
    max_raw_error = max_group_error = max_score_error = 0.0
    statuses = set()
    for canonical, binding in selected.items():
        row = rows[canonical]
        tx = FeatureTransaction(canonical, row['occurred_at_utc'], row['features'])
        before = scorer.score(tx)
        result = compute_local_contributions(scorer, tx)
        after = scorer.score(tx)
        assert before.risk_score == after.risk_score == result['score'] == binding['risk_score']
        assert before.review_status == after.review_status == binding['review_status']
        statuses.add(before.review_status)
        assert result['num_iteration'] == 140 and result['objective'] == 'binary sigmoid:1'
        assert len(result['matrix_contributions']) == 32 and len(result['groups']) == 11
        max_raw_error = max(max_raw_error, abs(math.fsum((result['base_value'],
            *result['matrix_contributions'])) - result['raw_score']))
        max_group_error = max(max_group_error, abs(math.fsum(result['groups'].values()) -
            math.fsum(result['matrix_contributions'])))
        max_score_error = max(max_score_error, abs(stable_binary_score(
            result['raw_score'], 1.0) - result['score']))
    print(json.dumps(dict(count=len(selected), statuses=sorted(statuses),
        max_raw_error=max_raw_error, max_group_error=max_group_error,
        max_score_error=max_score_error, all_scores_exact=True,
        all_statuses_exact=True, label_values_read=False), sort_keys=True))


if __name__ == '__main__':
    main()
