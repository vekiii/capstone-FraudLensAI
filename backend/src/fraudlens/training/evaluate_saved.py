"""Evaluate frozen score CSVs against a separately authorized label file."""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.training.evaluation import evaluate_validation


def evaluate_files(args: argparse.Namespace) -> dict:
    if args.partition == 'test' and not args.authorize_test_evaluation:
        raise ValueError('test label evaluation needs --authorize-test-evaluation')
    if args.partition == 'validation' and args.authorize_test_evaluation:
        raise ValueError('test authorization flag is valid only for test evaluation')
    predictions = []
    with args.scores.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['transaction_id', 'occurred_at_utc', 'score']:
            raise ValueError('prediction CSV schema mismatch')
        for row in reader:
            predictions.append((row['transaction_id'], datetime.fromisoformat(
                row['occurred_at_utc']), float(row['score'])))
    labels = []
    with args.labels.open(encoding='utf-8') as stream:
        for line in stream:
            labels.append(json.loads(line))
    if len(predictions) != len(labels) or not predictions:
        raise ValueError('prediction and label counts must match and be nonempty')
    if any(pred[0] != label.get('transaction_id') for pred, label in zip(
            predictions, labels, strict=True)):
        raise ValueError('prediction and label identities are not aligned')
    if any(type(item.get('label')) is not int or item['label'] not in (0, 1)
           for item in labels):
        raise ValueError('labels must be binary integers')
    metrics = evaluate_validation(
        [item['label'] for item in labels],
        [item[2] for item in predictions],
        [item[0] for item in predictions],
        [item[1] for item in predictions],
        fixed_threshold=args.threshold if args.partition == 'test' else None,
    )
    result = {
        'partition': args.partition,
        'prediction_sha256': sha256_file(args.scores),
        'label_file_sha256': sha256_file(args.labels),
        'threshold_source': ('frozen_validation_threshold' if args.partition == 'test'
                             else 'validation_positive_class_f1'),
        'metrics': metrics.__dict__,
    }
    args.output.write_bytes(canonical_json_bytes(result) + b'\n')
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scores', type=Path, required=True)
    parser.add_argument('--labels', type=Path, required=True)
    parser.add_argument('--partition', choices=('validation', 'test'), required=True)
    parser.add_argument('--threshold', type=float)
    parser.add_argument('--authorize-test-evaluation', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.partition == 'test' and args.threshold is None:
        parser.error('--threshold is required for test evaluation')
    print(json.dumps(evaluate_files(args), sort_keys=True))


if __name__ == '__main__':
    main()
