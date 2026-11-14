"""Label-free, controlled public shapes for Phase 7 contract tests."""

from datetime import UTC, datetime, timedelta

VERSION = 'dv_' + 'a' * 64


def entry(index=1, *, run='run_test_1', source='rules', score=0.65,
          at=None, amount='1250.000', paid_currency='Australian Dollar',
          received_currency='US Dollar'):
    at = at or datetime(2022, 9, 10, 10, tzinfo=UTC) + timedelta(minutes=index)
    stamp = at.strftime('%Y-%m-%dT%H:%M:%SZ')
    event_id = f'D{index:032x}'
    case_id = f'C{index:032x}'
    kind = ('ordinal_rule_score' if source == 'rules'
            else 'uncalibrated_probability_estimate')
    method = 'rules' if source == 'rules' else 'tree_path'
    scale = 'risk_score' if source == 'rules' else 'positive_class_estimate'
    scorer = 'rules-v1' if source == 'rules' else 'model-history-v1'
    transaction = {
        'transaction_id': event_id, 'event_time_utc': stamp,
        'event_time_raw': at.strftime('%Y/%m/%d %H:%M'),
        'time_basis': 'assumed_utc_for_synthetic_benchmark',
        'sender': {'bank': 'Bank A', 'account': '001'},
        'receiver': {'bank': 'Bank B', 'account': '002'},
        'paid': {'amount': amount, 'currency': paid_currency},
        'received': {'amount': amount, 'currency': received_currency},
        'payment_format': 'ACH',
    }
    explanation = {
        'status': 'available', 'method': method, 'explained_scale': scale,
        'feature_snapshot_digest': 'b' * 64, 'partial': False,
        'base_value': score, 'remainder': 0.0, 'items': [],
    }
    assessment = {
        'transaction_id': event_id, 'run_id': run, 'dataset_version': VERSION,
        'score': score, 'score_kind': kind, 'score_source': source,
        'scorer_version': scorer, 'feature_version': 'history-v1',
        'event_time_utc': stamp, 'history_cutoff_exclusive_at': stamp,
        'scored_at': '2026-11-14T13:00:00Z',
        'history_coverage': {'state': 'full', 'start': '2022-09-01T00:00:00Z'},
        'explanation': explanation,
    }
    return case_id, transaction, assessment
