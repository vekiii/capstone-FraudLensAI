"""Validate and tally local Capstone records without opening the offline rubric."""

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

IDS = tuple(f'EV-{number:02}' for number in range(1, 17))
MODES = dict(zip(IDS, ['live'] * 10 + ['deterministic'] * 6, strict=True))
STATUSES = ('pass', 'fail', 'blocked', 'not_run')
SCHEMA = json.loads(Path(__file__).with_name('execution.schema.json').read_text(encoding='utf-8'))


def _validate_metering(case_id, metering):
    confirmed = metering['confirmed_requests']
    if metering['reservations'] != (
        confirmed + metering['unknown_outcomes'] + metering['local_rejections']
        + metering['simulated_requests']
    ):
        raise ValueError(f'{case_id}: metering does not reconcile with reservations')
    if metering['usage'] is not None and metering['usage']['requests_with_usage'] > confirmed:
        raise ValueError(f'{case_id}: usage count exceeds confirmed requests')


def validate_phase(record):
    error = next(Draft202012Validator(SCHEMA).iter_errors(record), None)
    if error is not None:
        path = '.'.join(map(str, error.absolute_path)) or '<phase>'
        raise ValueError(f'{path}: failed schema rule {error.validator}')

    rows = {row['id']: row for row in record['rows']}
    if set(rows) != set(IDS):
        raise ValueError('Phase requires exactly one row per EV-01–EV-16')

    totals = dict.fromkeys(STATUSES, 0)
    for case_id, row in rows.items():
        if row['mode'] != MODES[case_id]:
            raise ValueError(f'{case_id}: unexpected execution mode')
        if row['metering'] is not None:
            _validate_metering(case_id, row['metering'])
        for retry in row['retries']:
            _validate_metering(case_id, retry['metering'])
        totals[row['status']] += 1

    reopen = rows['EV-06']
    if reopen['status'] == 'pass':
        saved = rows['EV-01']['binding']
        required = {'run_id', 'attempt_id', 'report_id', 'review_id', 'evidence_ids'}
        if not saved or not required.issubset(saved) or reopen['binding'] != saved:
            raise ValueError('EV-06: pass requires the saved EV-01 binding from this phase')
        if any(item['metering']['reservations'] for item in [reopen, *reopen['retries']]):
            raise ValueError('EV-06: reopening must not reserve a new provider request')
    return {'total': len(IDS), **totals}


def summarize(baseline, final):
    summary = {'baseline': validate_phase(baseline), 'final': validate_phase(final)}
    if baseline['phase'] != 'baseline' or final['phase'] != 'final':
        raise ValueError('Provide baseline first and final second')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('final', type=Path)
    args = parser.parse_args()
    try:
        baseline = json.loads(args.baseline.read_text(encoding='utf-8'))
        final = json.loads(args.final.read_text(encoding='utf-8'))
        summary = summarize(baseline, final)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
