"""Prepare label-free frozen-test explanation examples for a human teammate."""

import argparse
import hashlib
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from fraudlens.data_contracts import ScoreRequestV2, score_v2
from fraudlens.model_scoring import ModelScorer, load_trusted_artifact
from fraudlens.pipeline_cli import _source_row
from fraudlens.rule_scoring import RuleScorer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--artifact-dir', type=Path, required=True)
    parser.add_argument('--manifest-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    protocol_raw = args.protocol.read_bytes()
    protocol = json.loads(protocol_raw)
    bundle = json.loads(args.predictions.read_text())
    if bundle['protocol_sha256'] != hashlib.sha256(protocol_raw).hexdigest():
        raise ValueError('frozen protocol mismatch')
    ids = [row[0] for row in bundle['predictions']['model']]
    if (ids != [row[0] for row in bundle['predictions']['rules']]
            or len(ids) != protocol['split']['partitions']['test']['count']):
        raise ValueError('frozen score population mismatch')
    selected = sorted(ids, key=lambda value: hashlib.sha256(
        value.encode('ascii')).digest())[:5]
    artifact = load_trusted_artifact(
        args.artifact_dir, expected_manifest_sha256=args.manifest_sha,
        expected_dataset_version=protocol['dataset_version'],
        expected_protocol_sha256=bundle['protocol_sha256'])
    model = ModelScorer(artifact)
    rules = RuleScorer()
    connection = sqlite3.connect(f'{args.source.resolve().as_uri()}?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    try:
        rows = connection.execute(f'''
            SELECT s.transaction_id,e.case_id,e.payload_json,s.event_time,s.as_of,
                   s.coverage_start,s.coverage_state,s.scoreable,
                   s.feature_input_digest,s.created_at,s.payload_json
            FROM feature_snapshots AS s JOIN operational_events AS e
              ON e.version=s.version AND e.transaction_id=s.transaction_id
            WHERE s.version=? AND s.feature_version='history-v1'
              AND s.transaction_id IN ({','.join('?' for _ in selected)})''',
            (protocol['dataset_version'], *selected)).fetchall()
    finally:
        connection.close()
    if len(rows) != 5:
        raise ValueError('review sample rows missing')
    by_id = {row[0]: row for row in rows}
    examples = []
    for event_id in selected:
        event, snapshot = _source_row(by_id[event_id], protocol['dataset_version'])
        if not snapshot.scoreable or snapshot.event_time <= __import__(
                'datetime').datetime.fromisoformat(
                    protocol['split']['validation_end_inclusive']):
            raise ValueError('review sample outside frozen test')
        for source, scorer, version in (
                ('model', model, 'model-history-v1'),
                ('rules', rules, 'rules-v1')):
            request = ScoreRequestV2(event, snapshot, protocol['dataset_version'],
                                     'run_phase8_review', version, 'history-v1',
                                     event.event_time_utc)
            assessment = (scorer.assess(request) if source == 'model'
                          else score_v2(request, scorer))
            explanation = asdict(assessment.explanation)
            examples.append({'transaction_id': event_id, 'score_source': source,
                             'case_id': event.case_id,
                             'feature_input_digest': snapshot.feature_input_digest,
                             'event_time_utc': event.event_time_utc.isoformat(),
                             'history_as_of': snapshot.as_of.isoformat(),
                             'feature_values': snapshot.feature_values,
                             'score': float(assessment.score),
                             'score_kind': assessment.score_kind,
                             'scorer_version': assessment.scorer_version,
                             'run_id': assessment.run_id,
                             'explanation': explanation})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as target:
        json.dump({'rule': protocol['review_sample'], 'selected_ids': selected,
                   'examples': examples}, target, default=str, indent=2)
        target.write('\n')
    print(json.dumps({'status': 'prepared_for_teammate_review',
                      'selected_ids': selected, 'examples': len(examples)}))


if __name__ == '__main__':
    main()
