"""Read-only development diagnostic for a proposed UTC daily top-20 policy.

The script fixes a score-only selection before querying train/validation labels.
It never reads test labels or changes the scored run or shared active pointer.
"""

import argparse
import hashlib
import json
import sqlite3
from collections import defaultdict
from contextlib import closing
from pathlib import Path

from fraudlens.daily_capacity_diagnostic import select_daily_threshold_alerts


def read_only(path):
    if not path.is_file():
        raise ValueError(f'required local input missing: {path.name}')
    connection = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    return connection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-store', required=True, type=Path)
    parser.add_argument('--source-store', required=True, type=Path)
    parser.add_argument('--protocol', required=True, type=Path)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--manifest-sha', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('diagnostic output already exists')
    protocol = json.loads(args.protocol.read_text())
    with closing(read_only(args.run_store)) as runs:
        meta = runs.execute('''
            SELECT dataset_version,score_source,scorer_version,artifact_sha256,
                   threshold,expected_count,scored_count,total_alerts,status
            FROM scored_runs WHERE run_id=?''', (args.run_id,)).fetchone()
        if (meta is None or meta[0] != protocol['dataset_version']
                or meta[1:4] != ('model', 'model-history-v1-boosted-candidate',
                                 args.manifest_sha)
                or meta[5] != meta[6] or meta[8] != 'completed'):
            raise ValueError('completed boosted run/manifest mismatch')
        rows = []
        for transaction_id, event_time, assessment in runs.execute('''
            SELECT transaction_id,event_time,assessment_json
            FROM scored_assessments INDEXED BY alert_listing
            WHERE run_id=? AND alert=1''', (args.run_id,)):
            rows.append({'transaction_id': transaction_id, 'event_time': event_time,
                         'score': json.loads(assessment)['score']})
        if len(rows) != meta[7]:
            raise ValueError('stored alert count mismatch')

    kept, removed = select_daily_threshold_alerts(rows, meta[4])
    kept_ids = {item['transaction_id'] for item in kept}
    selected_ids = '\n'.join(item['transaction_id'] for item in kept).encode()
    per_day = defaultdict(lambda: {'threshold_alerts': 0, 'retained': 0,
                                   'removed': 0, 'development_alerts': 0,
                                   'development_hits_before': 0,
                                   'development_hits_after': 0})
    for item in rows:
        per_day[item['event_time'][:10]]['threshold_alerts'] += 1
    for item in kept:
        per_day[item['event_time'][:10]]['retained'] += 1
    for item in removed:
        per_day[item['event_time'][:10]]['removed'] += 1

    # All selections and their digest are fixed before opening private labels.
    cutoff = protocol['split']['validation_end_inclusive'].replace('+00:00', 'Z')
    version = protocol['dataset_version']
    with closing(read_only(args.source_store)) as source:
        dataset = source.execute('''
            SELECT status,source_sha256,mapping_sha256,time_policy_sha256
            FROM dataset_versions WHERE id=?''', (version,)).fetchone()
        build = source.execute('''
            SELECT status,snapshot_count FROM feature_builds
            WHERE version=? AND feature_version='history-v1' ''', (version,)).fetchone()
        if (dataset != ('complete', protocol['source_sha256'],
                        protocol['mapping_sha256'], protocol['time_policy_sha256'])
                or build != ('complete', protocol['split']['scoreable_count']
                             + protocol['split']['warmup_excluded_count'])):
            raise ValueError('development source/protocol mismatch')
        for item in rows:
            if item['event_time'] > cutoff:
                continue
            label = source.execute('''
                SELECT status,value FROM private_evaluation_labels
                WHERE version=? AND transaction_id=?''',
                (version, item['transaction_id'])).fetchone()
            if (label is None or label[0] not in {
                    'eligible_positive', 'eligible_negative'}
                    or label[1] not in (0, 1)):
                raise ValueError('development label ineligible')
            day = per_day[item['event_time'][:10]]
            day['development_alerts'] += 1
            day['development_hits_before'] += label[1]
            if item['transaction_id'] in kept_ids:
                day['development_hits_after'] += label[1]

    daily = [{'utc_day': day, **counts} for day, counts in sorted(per_day.items())]
    totals = {key: sum(day[key] for day in daily)
              for key in ('threshold_alerts', 'retained', 'removed',
                          'development_alerts', 'development_hits_before',
                          'development_hits_after')}
    result = {'status': 'development_only', 'run_id': args.run_id,
              'manifest_sha256': args.manifest_sha, 'threshold': meta[4],
              'policy': 'UTC_date_score_desc_transaction_id_asc_top_20',
              'selection_sha256': hashlib.sha256(selected_ids).hexdigest(),
              'development_end_inclusive': cutoff, 'totals': totals,
              'days': daily, 'test_labels_read': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'totals': totals,
                      'selection_sha256': result['selection_sha256']}, sort_keys=True))


if __name__ == '__main__':
    main()
