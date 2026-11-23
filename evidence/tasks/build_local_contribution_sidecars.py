"""One-time local, label-free build; writes only ignored sidecar files."""
import hashlib
import json
import sqlite3
from pathlib import Path

from fraudlens.bridge import validate_crosswalk
from fraudlens.bridge_reader import BridgeReader
from fraudlens.investigation.contribution_sidecar import build_sidecar
from fraudlens.investigation.models import canonical
from fraudlens.scoring.local_contributions import compute_local_contributions
from fraudlens.scoring.model_scorer import FeatureStore, FeatureTransaction, ModelScorer

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / 'data/processed/model-case-bridge-v1'
FEATURES = ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'
ARTIFACTS = ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts'
DESTINATION = ROOT / 'data/processed/local-contributions-v1/sidecars.json'
BRIDGE_SHA = '16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004'


def main():
    bridge = BridgeReader(BRIDGE, BRIDGE_SHA)
    manifest = bridge._check()
    with sqlite3.connect((BRIDGE / 'runs.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as db:
        bindings = [json.loads(row[0]) for row in db.execute(
            'SELECT binding_json FROM bridge_crosswalk ORDER BY canonical_id')]
    validate_crosswalk(bindings)
    assert len(bindings) == manifest['alert_count'] == 65
    selected = {binding['canonical_transaction_id']: binding for binding in bindings}
    store = FeatureStore(FEATURES)
    rows = {}
    for path in store.paths:
        digest = hashlib.sha256()
        with path.open('rb') as source:
            for line in source:
                digest.update(line)
                if b'ibm-hi-small:' not in line:
                    continue
                row = json.loads(line)
                if row['transaction_id'] in selected:
                    assert row['transaction_id'] not in rows
                    rows[row['transaction_id']] = row
        assert digest.hexdigest() == store.expected_files[path.stem]
    assert set(rows) == set(selected)
    scorer = ModelScorer(ARTIFACTS)
    items, originals = {}, {}
    for canonical_id, binding in selected.items():
        raw = rows[canonical_id]
        transaction = FeatureTransaction(canonical_id, raw['occurred_at_utc'], raw['features'])
        before = scorer.score(transaction)
        calculation = compute_local_contributions(scorer, transaction)
        after = scorer.score(transaction)
        assert (before.risk_score == after.risk_score == calculation['score'] == binding['risk_score']
                and before.review_status == after.review_status == binding['review_status'])
        context = bridge.resolve(binding['case_id'], binding['snapshot_ref'])
        items[binding['case_id']] = build_sidecar(binding, context, calculation, raw['features'])
        originals[binding['case_id']] = calculation
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    if DESTINATION.exists():
        raise FileExistsError('Immutable local sidecar already exists')
    content = canonical(dict(contract_version=1, items=items))
    with DESTINATION.open('xb') as stream:
        stream.write(content)
    full = DESTINATION.parent / 'full-calculations.json'
    with full.open('xb') as stream:
        stream.write(canonical(dict(contract_version=1, calculations=originals)))
    print(json.dumps(dict(count=len(items), path=str(DESTINATION),
        sha256=hashlib.sha256(content).hexdigest(), bytes=len(content),
        full_calculations_sha256=hashlib.sha256(full.read_bytes()).hexdigest()), sort_keys=True))


if __name__ == '__main__':
    main()
