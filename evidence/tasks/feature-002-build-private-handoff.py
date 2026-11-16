"""Build an ignored, label-free T065/T066 transfer bundle from pinned files."""

import argparse
import json
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

from fraudlens.daily_capacity_publication import file_sha256

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802'
SOURCE = ROOT / 'data/processed/feature-002-ibm-v8-rules-work.sqlite'
V3 = ROOT / 'evals/results/boosted-full-20261114-v3.sqlite'


def read_only(path):
    if not path.is_file():
        raise ValueError(f'required local file missing: {path}')
    connection = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    return connection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to((ROOT / 'evals/results').resolve()):
        raise ValueError('output must be a new ignored evals/results directory')
    if (file_sha256(SOURCE)
            != '5397b637814cbed9cf31389613207335321597c9682ec67d31abacf28ebda4d9'
            or file_sha256(V3)
            != '732eefa75ad46c80404c34301ae6d72be87d4eb61f0d618457f7c760224dce06'):
        raise ValueError('pinned source/history or v3 store hash mismatch')
    sample = ROOT / 'evals/results/boosted-full-five-explanations.json'
    details = json.loads(sample.read_text())['details']
    if len(details) != 5 or len({d['transaction']['transaction_id'] for d in details}) != 5:
        raise ValueError('five-case sample identity mismatch')
    operational = []
    saved = []
    with closing(read_only(SOURCE)) as source, closing(read_only(V3)) as run:
        for detail in details:
            transaction_id = detail['transaction']['transaction_id']
            event = source.execute('''
                SELECT case_id,payload_json FROM operational_events
                WHERE version=? AND transaction_id=?''', (VERSION, transaction_id)).fetchone()
            snapshot = source.execute('''
                SELECT event_time,as_of,coverage_start,coverage_state,scoreable,
                       feature_input_digest,created_at,payload_json
                FROM feature_snapshots WHERE version=? AND feature_version='history-v1'
                  AND transaction_id=?''', (VERSION, transaction_id)).fetchone()
            assessment = run.execute('''
                SELECT case_id,transaction_json,assessment_json
                FROM scored_assessments WHERE run_id=? AND transaction_id=?''',
                ('run_boosted_full_20261114_v3', transaction_id)).fetchone()
            if (event is None or snapshot is None or assessment is None
                    or event[0] != detail['case_id'] or assessment[0] != event[0]
                    or snapshot[5] != detail['risk_assessment']['explanation'][
                        'feature_snapshot_digest']
                    or json.loads(assessment[1]) != detail['transaction']
                    or json.loads(assessment[2]) != detail['risk_assessment']):
                raise ValueError('source/snapshot/assessment identity mismatch')
            operational.append({
                'transaction_id': transaction_id, 'case_id': event[0],
                'event': json.loads(event[1]),
                'snapshot': dict(zip((
                    'event_time', 'as_of', 'coverage_start', 'coverage_state',
                    'scoreable', 'feature_input_digest', 'created_at', 'values'),
                    (*snapshot[:7], json.loads(snapshot[7])), strict=True)),
            })
            saved.append({'case_id': assessment[0],
                          'transaction': json.loads(assessment[1]),
                          'risk_assessment': json.loads(assessment[2])})

    files = {
        'boosted-artifact': ROOT / 'artifacts/feature-002-boosted-validation-20261114',
        'boosted-full-five-explanations.json': sample,
        'boosted-validation.json': ROOT / 'evals/results/boosted-validation.json',
        'handoff-instructions.md': ROOT / 'evidence/tasks/feature-002-team-handoff-2026-11-16.md',
        'benchmark/frozen-tree-artifact': ROOT / 'artifacts/feature-002-history-v1-20261114',
        'benchmark/test_predictions.json': ROOT / 'evals/results/phase8/test_predictions.json',
        'benchmark/test_report.json': ROOT / 'evals/results/phase8/test_report.json',
        'benchmark/holdout_ledger.json': ROOT / 'evals/results/phase8/holdout_ledger.json',
    }
    output.mkdir(parents=True)
    for relative, source in files.items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        elif source.is_file():
            shutil.copy2(source, destination)
        else:
            raise ValueError(f'required benchmark input missing: {source}')
    (output / 'five-operational-snapshots.json').write_text(
        json.dumps({'dataset_version': VERSION, 'cases': operational}, indent=2) + '\n')
    (output / 'five-saved-assessments.json').write_text(
        json.dumps({'run_id': 'run_boosted_full_20261114_v3', 'cases': saved}, indent=2)
        + '\n')
    hashes = {str(path.relative_to(output)): file_sha256(path)
              for path in sorted(output.rglob('*')) if path.is_file()}
    manifest = {'source_dataset_version': VERSION,
                'source_csv_sha256': 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040',
                'source_history_store': str(SOURCE),
                'source_history_store_sha256': '5397b637814cbed9cf31389613207335321597c9682ec67d31abacf28ebda4d9',
                'reference_v3_store': str(V3),
                'reference_v3_store_sha256': '732eefa75ad46c80404c34301ae6d72be87d4eb61f0d618457f7c760224dce06',
                'private_labels_included': False, 'files_sha256': hashes}
    (output / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'files': len(hashes),
                      'five_cases': len(operational), 'private_labels_included': False}))


if __name__ == '__main__':
    main()
