"""Evaluate frozen test scores after explicit one-time human authorization."""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from fraudlens.data.manifest import sha256_file, verify_completed_snapshot
from fraudlens.data.training_input import _without_label
from fraudlens.training.evaluation import evaluate_validation

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / 'data/processed/t210-hi-small-b19d39f5'
FEATURES = ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'
EXPECTED_SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
EXPECTED_SNAPSHOT_SHA = '38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88'


def evaluate_once(predictions_path: Path, prediction_sha: str, output: Path) -> dict:
    if sha256_file(predictions_path) != prediction_sha:
        raise ValueError('frozen test prediction checksum mismatch')
    experiment_path = predictions_path.parent / 'experiment.json'
    experiment = json.loads(experiment_path.read_bytes())
    if experiment.get('prediction_sha256', {}).get('test') != prediction_sha:
        raise ValueError('experiment does not bind the test prediction checksum')
    snapshot = verify_completed_snapshot(SNAPSHOT)
    if (snapshot['source_sha256'] != EXPECTED_SOURCE_SHA
            or sha256_file(SNAPSHOT / 'manifest.json') != EXPECTED_SNAPSHOT_SHA):
        raise ValueError('verified source snapshot identity mismatch')
    feature_manifest = json.loads((FEATURES / 'manifest.json').read_bytes())
    if (sha256_file(FEATURES / 'manifest.json') != experiment['feature_manifest_sha256']
            or feature_manifest['source_sha256'] != EXPECTED_SOURCE_SHA
            or sha256_file(FEATURES / 'test.jsonl') != feature_manifest['files']['test']):
        raise ValueError('test feature identity mismatch')

    predictions = []
    with predictions_path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['transaction_id', 'occurred_at_utc', 'score']:
            raise ValueError('sealed test prediction schema mismatch')
        for row in reader:
            predictions.append((row['transaction_id'], datetime.fromisoformat(
                row['occurred_at_utc']), float(row['score'])))
    expected_ids = []
    with (FEATURES / 'test.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            expected_ids.append(json.loads(line)['transaction_id'])
    if len(predictions) != len(expected_ids) or any(
            result[0] != identity for result, identity in zip(predictions, expected_ids,
                                                              strict=True)):
        raise ValueError('test predictions are not aligned to the frozen test IDs')

    labels = {}
    wanted = set(expected_ids)
    with (SNAPSHOT / 'accepted.jsonl').open('rb') as stream:
        for raw in stream:
            row = _without_label(raw)
            identity = row['transaction_id']
            if identity in wanted:
                _, remainder = raw.split(b',"is_laundering":', 1)
                token = remainder.partition(b',')[0]
                if token not in (b'"0"', b'"1"'):
                    raise ValueError('test label token is not binary')
                labels[identity] = int(token[1:2])
    if len(labels) != len(expected_ids):
        raise ValueError('frozen test labels do not cover the frozen prediction IDs')
    threshold = experiment['validation_metrics']['threshold']
    metrics = evaluate_validation(
        [labels[identity] for identity in expected_ids],
        [row[2] for row in predictions],
        expected_ids,
        [row[1] for row in predictions],
        fixed_threshold=threshold,
    )
    result = {
        'partition': 'research_test',
        'explicit_authorization': True,
        'authorization_flag': '--authorize-test-evaluation I_AUTHORIZE',
        'prediction_sha256': prediction_sha,
        'experiment_json_sha256': sha256_file(experiment_path),
        'protocol_sha256': experiment['protocol_sha256'],
        'threshold_source': 'frozen_validation_positive_class_f1',
        'metrics': metrics.__dict__,
        'record_level_test_labels_written': False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n',
                      encoding='utf-8')
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--prediction-sha256', required=True)
    parser.add_argument('--authorize-test-evaluation', choices=('I_AUTHORIZE',), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(evaluate_once(args.predictions, args.prediction_sha256, args.output),
                     sort_keys=True))


if __name__ == '__main__':
    main()
