"""Read-only, label-free source/history check for the five boosted T065 cases.

Run against a complete, locally rebuilt IBM v8 work store. The output omits
account identifiers and private labels. It does not verify model assessments.
"""

import argparse
import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

DATASET = 'dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802'
CASES = (
    ('D90fbf75213cb7bb1bdc1f3f91ec23dd5', 'C737e48e2a489a7f10bf7a71716e3bc65',
     '2022-09-09T02:51:00+00:00', '48014.36', 'Yuan'),
    ('D0adebff88899bbb3c98e9fb03b785df6', 'C0281c8396bb2a961e95f1b80ebeee0f7',
     '2022-09-05T07:40:00+00:00', '51805.35', 'Yuan'),
    ('D6e00944c45c3f8307e5d65ef03edfd8d', 'C1b84af5218d0786128963eac213a69e9',
     '2022-09-06T19:44:00+00:00', '89709263.78', 'Swiss Franc'),
    ('D9dc186ae55ba66066b6781023bac7170', 'C906476436b96bd9e4646d10a6d09dc70',
     '2022-09-09T13:15:00+00:00', '51424.51', 'Yuan'),
    ('D26d712161d5bfa0d06da08cccaf5498b', 'C16b89849cf52390a3827f72899b40ca1',
     '2022-09-09T23:36:00+00:00', '17312.17', 'Euro'),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', required=True, type=Path)
    args = parser.parse_args()
    with sqlite3.connect(f'file:{args.store.resolve().as_posix()}?mode=ro', uri=True) as db:
        version = db.execute(
            'SELECT status,source_records,source_sha256,mapping_sha256,time_policy_sha256 '
            'FROM dataset_versions WHERE id=?', (DATASET,)
        ).fetchone()
        if version is None or version[0] != 'complete':
            raise ValueError('Expected complete dataset version is unavailable')
        targets = []
        for transaction_id, case_id, expected_time, expected_amount, expected_currency in CASES:
            row = db.execute(
                'SELECT case_id,payload_json FROM operational_events '
                'WHERE version=? AND transaction_id=?', (DATASET, transaction_id)
            ).fetchone()
            if row is None:
                raise ValueError(f'Missing transaction {transaction_id}')
            facts = json.loads(row[1])
            targets.append({
                'transaction_id': transaction_id, 'case_id': row[0], 'facts': facts,
                'expected': (case_id, expected_time, expected_amount, expected_currency),
            })

        # One scan of operational facts; no private label table is opened.
        low = min(item['facts']['event_time_epoch_ns'] for item in targets) - 24 * 3600 * 10**9
        high = max(item['facts']['event_time_epoch_ns'] for item in targets)
        sender_filter = ' OR '.join(
            "(json_extract(payload_json,'$.sender_bank')=? "
            "AND json_extract(payload_json,'$.sender_account')=?)" for _ in targets
        )
        params = [DATASET, low, high]
        for item in targets:
            params.extend((item['facts']['sender_bank'], item['facts']['sender_account']))
        rows = db.execute(
            'SELECT payload_json FROM operational_events WHERE version=? '
            "AND CAST(json_extract(payload_json,'$.event_time_epoch_ns') AS INTEGER)>=? "
            "AND CAST(json_extract(payload_json,'$.event_time_epoch_ns') AS INTEGER)<? "
            f'AND ({sender_filter})', params,
        )
        candidate_history = [json.loads(row[0]) for row in rows]
        has_snapshots = db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='feature_snapshots'"
        ).fetchone() is not None
        output = {
            'database': str(args.store), 'dataset_version': DATASET,
            'dataset_status': version[0], 'source_records': version[1],
            'source_sha256': version[2], 'mapping_sha256': version[3],
            'time_policy_sha256': version[4], 'cases': [],
        }
        for item in targets:
            facts = item['facts']
            t = facts['event_time_epoch_ns']
            history = [event for event in candidate_history
                       if event['sender_bank'] == facts['sender_bank']
                       and event['sender_account'] == facts['sender_account']
                       and t - 24 * 3600 * 10**9 <= event['event_time_epoch_ns'] < t]
            same_currency = [event for event in history
                             if event['paid_currency'] == facts['paid_currency']]
            paid_sum = sum((Decimal(event['paid_amount']) for event in same_currency),
                           Decimal(0))
            expected_case, expected_time, expected_amount, expected_currency = item['expected']
            snapshot = None
            if has_snapshots:
                row = db.execute(
                    'SELECT coverage_state,scoreable,feature_input_digest,payload_json '
                    'FROM feature_snapshots WHERE version=? AND feature_version=? '
                    'AND transaction_id=?', (DATASET, 'history-v1', item['transaction_id'])
                ).fetchone()
                if row:
                    payload = json.loads(row[3])
                    snapshot = {'coverage_state': row[0], 'scoreable': bool(row[1]),
                                'feature_input_digest': row[2],
                                'current_paid_amount': payload.get('current_paid_amount'),
                                'current_paid_currency': payload.get('current_paid_currency'),
                                'current_payment_format': payload.get('current_payment_format'),
                                'sender_paid_count_same_currency_24h': payload.get(
                                    'sender_paid_count_same_currency_24h'),
                                'sender_paid_sum_same_currency_24h': payload.get(
                                    'sender_paid_sum_same_currency_24h')}
            output['cases'].append({
                'transaction_id': item['transaction_id'], 'case_id': item['case_id'],
                'source_ordinal': facts['source_ordinal'],
                'event_time_utc': facts['event_time_utc'],
                'payment_format': facts['payment_format'],
                'paid_amount': facts['paid_amount'], 'paid_currency': facts['paid_currency'],
                'received_amount': facts['received_amount'],
                'received_currency': facts['received_currency'],
                'event_fact_digest': facts['event_fact_digest'],
                'sender_prior_24h_all_currency_count': len(history),
                'sender_prior_24h_same_currency_count': len(same_currency),
                'sender_prior_24h_same_currency_paid_sum': str(paid_sum),
                'handoff_source_fact_match': (
                    item['case_id'] == expected_case
                    and datetime.fromisoformat(facts['event_time_utc'])
                    == datetime.fromisoformat(expected_time)
                    and facts['payment_format'] == 'ACH'
                    and Decimal(facts['paid_amount']) == Decimal(expected_amount)
                    and Decimal(facts['received_amount']) == Decimal(expected_amount)
                    and facts['paid_currency'] == expected_currency
                    and facts['received_currency'] == expected_currency
                ),
                'snapshot': snapshot,
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
