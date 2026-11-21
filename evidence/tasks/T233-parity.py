"""Deterministic ID-only offline/app parity probe; never opens label files."""

import csv
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from fraudlens.main import create_app
from fraudlens.scoring.model_scorer import FeatureTransaction, ModelScorer
from fraudlens.settings import Settings

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001'
FEATURES = ROOT / 'data/processed/t219-ibm-day-60-20-20-v1/test.jsonl'
PREDICTION_SHA256 = '99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7'


def main() -> None:
    predictions = FREEZE / 'test-predictions-sealed.csv'
    with predictions.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == PREDICTION_SHA256
    with predictions.open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 233_070
    # The selection key depends solely on the ID, never scores or labels.
    chosen = sorted(rows, key=lambda row: hashlib.sha256(
        row['transaction_id'].encode('utf-8')).digest())[:8]
    wanted = {row['transaction_id']: row for row in chosen}
    features = {}
    with FEATURES.open(encoding='utf-8') as stream:
        for line in stream:
            item = json.loads(line)
            if item['transaction_id'] in wanted:
                features[item['transaction_id']] = item
    assert len(features) == len(chosen)
    scorer = ModelScorer(FREEZE / 'artifacts')
    for row in chosen:
        identity = row['transaction_id']
        actual = scorer.score(FeatureTransaction(**features[identity])).risk_score
        assert actual == float(row['score']), identity
    with TestClient(create_app(settings=Settings(mode='model'))) as client:
        first = chosen[0]
        response = client.get(f"/api/transactions/{first['transaction_id']}/risk")
        assert response.status_code == 200, response.status_code
        assert response.json()['risk_score'] == float(first['score'])
        assert client.get('/api/cases').status_code == 200
    print('8/8 exact float parity by ID-only deterministic sample; 1/1 HTTP parity')
    print('selected source rows:', ', '.join(
        row['transaction_id'].rsplit(':', 1)[1] for row in chosen))


if __name__ == '__main__':
    main()
