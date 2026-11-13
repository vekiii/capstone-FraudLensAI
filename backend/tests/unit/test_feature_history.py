"""T018 RED: hand-computed, label-free history-v1 replay examples."""

import importlib
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from fraudlens.data_contracts import CanonicalTransaction
from fraudlens.data_import import parse_canonical_source

START = datetime(2026, 1, 1, tzinfo=UTC)
T = START + timedelta(hours=36)
VERSION = 'dv_' + '0' * 64
HISTORY_KEYS = (
    'sender_out_count_24h', 'sender_distinct_receivers_24h',
    'sender_paid_count_same_currency_24h', 'sender_paid_sum_same_currency_24h',
    'receiver_in_count_24h', 'receiver_distinct_senders_24h',
    'receiver_received_count_same_currency_24h',
    'receiver_received_sum_same_currency_24h',
)


def event(name, at, *, sender=('A', '1'), receiver=('R', '1'),
          paid='10', paid_currency='Euro', received='7',
          received_currency='US Dollar', payment_format='Wire'):
    """A canonical operational fact; source ordinal and ID are lineage only."""
    return CanonicalTransaction(
        transaction_id=name, case_id='case-' + name, source_ordinal=1,
        event_time_raw=at.strftime('%Y/%m/%d %H:%M'), event_time_utc=at,
        event_time_epoch_ns=int(at.timestamp()) * 1_000_000_000,
        time_basis='assumed_utc', sender_bank=sender[0], sender_account=sender[1],
        receiver_bank=receiver[0], receiver_account=receiver[1],
        sender_join_key=repr(sender).encode(), receiver_join_key=repr(receiver).encode(),
        paid_amount=paid, paid_currency=paid_currency,
        received_amount=received, received_currency=received_currency,
        payment_format=payment_format, event_fact_digest=name.encode(),
    )


def replay(events, **kwargs):
    module = importlib.import_module('fraudlens.feature_history')
    build = getattr(module, 'build_feature_snapshots', None)
    assert callable(build), 'T020 missing: build_feature_snapshots label-free replay'
    return build(events, dataset_version=VERSION, coverage_start=START, **kwargs)


def values(result, name):
    return result[name].feature_values


def test_all_eleven_catalog_values_and_directional_decimal_sums():
    facts = [
        event('s1', T - timedelta(minutes=60), receiver=('B', '7'), paid='10', received='1'),
        event('s2', T - timedelta(minutes=50), receiver=('C', '7'), paid='20', received='2'),
        event('s3', T - timedelta(minutes=40), receiver=('D', '8'), paid='30', received='3'),
        event('r1', T - timedelta(minutes=30), sender=('U', '1'), received='7'),
        event('r2', T - timedelta(minutes=20), sender=('V', '1'), received='9'),
        event('r3', T - timedelta(minutes=10), sender=('W', '2'), received='11'),
        event('target', T, paid='40', received='19', payment_format='Wire'),
    ]
    got = values(replay(facts), 'target')
    assert got == {
        'sender_out_count_24h': 3,
        'sender_distinct_receivers_24h': 3,
        'sender_paid_count_same_currency_24h': 3,
        'sender_paid_sum_same_currency_24h': Decimal('60'),
        'receiver_in_count_24h': 3,
        'receiver_distinct_senders_24h': 3,
        'receiver_received_count_same_currency_24h': 3,
        'receiver_received_sum_same_currency_24h': Decimal('27'),
        'current_paid_amount': Decimal('40'),
        'current_paid_currency': 'Euro',
        'current_payment_format': 'Wire',
    }


def test_window_includes_exact_lower_bound_excludes_upper_peer():
    facts = [event('too-early', T - timedelta(hours=24, minutes=1)),
             event('lower', T - timedelta(hours=24)),
             event('last', T - timedelta(minutes=1)),
             event('target', T), event('peer', T)]
    result = replay(facts)
    assert values(result, 'target')['sender_out_count_24h'] == 2
    assert values(result, 'peer')['sender_out_count_24h'] == 2


def test_input_permutation_does_not_change_snapshots():
    facts = [event('one', T - timedelta(minutes=3)),
             event('two', T - timedelta(minutes=2)), event('target', T)]
    assert values(replay(facts), 'target') == values(replay(list(reversed(facts))), 'target')


def test_tied_peers_share_prior_history_then_both_update_later_history():
    facts = [event('prior', T - timedelta(minutes=1)), event('peer-a', T),
             event('peer-b', T), event('later', T + timedelta(minutes=1))]
    result = replay(facts)
    assert values(result, 'peer-a')['sender_out_count_24h'] == 1
    assert values(result, 'peer-b')['sender_out_count_24h'] == 1
    assert values(result, 'later')['sender_out_count_24h'] == 3


def test_future_append_does_not_change_prior_snapshot():
    base = [event('prior', T - timedelta(minutes=1)), event('target', T)]
    assert values(replay(base), 'target') == values(
        replay(base + [event('future', T + timedelta(minutes=1))]), 'target')


def test_earlier_heldout_facts_contribute_without_labels():
    # The two prior events conceptually belong to validation and test partitions.
    facts = [event('validation-fact', T - timedelta(minutes=2)),
             event('test-fact', T - timedelta(minutes=1)), event('target', T)]
    got = values(replay(facts, purpose='training'), 'target')
    assert got['sender_out_count_24h'] == 2
    assert got['sender_paid_sum_same_currency_24h'] == Decimal('20')


def test_bank_qualified_accounts_and_counterparties_do_not_alias():
    facts = [event('a', T - timedelta(minutes=3), receiver=('B', '7')),
             event('b', T - timedelta(minutes=2), receiver=('C', '7')),
             event('different-bank', T - timedelta(minutes=1), sender=('X', '1')),
             event('target', T)]
    got = values(replay(facts), 'target')
    assert got['sender_out_count_24h'] == 2
    assert got['sender_distinct_receivers_24h'] == 2


def test_paid_and_received_currency_are_grouped_independently():
    facts = [event('euro-usd', T - timedelta(minutes=3), paid='1.000001', received='2.000002'),
             event('other-paid', T - timedelta(minutes=2), paid='9', paid_currency='US Dollar',
                   received='3.000003'),
             event('other-received', T - timedelta(minutes=1), paid='4.000004',
                   received='5', received_currency='Euro'),
             event('target', T, paid='0.1', received='0.2')]
    got = values(replay(facts), 'target')
    assert got['sender_out_count_24h'] == got['receiver_in_count_24h'] == 3
    assert got['sender_paid_count_same_currency_24h'] == 2
    assert got['sender_paid_sum_same_currency_24h'] == Decimal('5.000005')
    assert got['receiver_received_count_same_currency_24h'] == 2
    assert got['receiver_received_sum_same_currency_24h'] == Decimal('5.000005')
    assert got['current_paid_amount'] == Decimal('0.1')


def test_first_24_hours_are_context_only_and_boundary_is_scoreable():
    warm = event('warm', START + timedelta(hours=23, minutes=59))
    boundary = event('boundary', START + timedelta(hours=24))
    result = replay([event('start', START), warm, boundary])
    assert result['warm'].coverage_state == 'incomplete'
    assert result['warm'].scoreable is False
    assert result['boundary'].coverage_state == 'full'
    assert result['boundary'].scoreable is True
    assert values(result, 'boundary')['sender_out_count_24h'] == 2


def test_full_coverage_cold_account_has_measured_zero():
    target = event('new', T, sender=('NEW', '1'), receiver=('NEW', '2'))
    result = replay([event('source-start', START), target])['new']
    assert result.coverage_state == 'full' and result.scoreable is True
    assert all(result.feature_values[key] == 0 for key in HISTORY_KEYS)
    assert type(result.feature_values['sender_paid_sum_same_currency_24h']) is Decimal
    assert type(result.feature_values['receiver_received_sum_same_currency_24h']) is Decimal


@pytest.mark.parametrize('coverage_kwargs,state', [
    ({'missing_intervals': ((T - timedelta(hours=2), T - timedelta(hours=1)),)},
     'incomplete'),
    ({'coverage_available': False}, 'unavailable'),
])
def test_deficient_coverage_is_null_not_measured_zero(coverage_kwargs, state):
    snapshot = replay([event('target', T)], **coverage_kwargs)['target']
    assert snapshot.coverage_state == state and snapshot.scoreable is False
    assert all(snapshot.feature_values[key] is None for key in HISTORY_KEYS)


def test_blank_invalid_or_removed_private_label_never_changes_replay():
    header = ('Timestamp,From Bank,Account,To Bank,Account,Amount Received,'
              'Receiving Currency,Amount Paid,Payment Currency,Payment Format,'
              'Is Laundering\n')
    start = '2026/01/01 00:00,A,1,R,1,7,US Dollar,10,Euro,Wire,0\n'
    target = '2026/01/02 12:00,A,1,R,1,7,US Dollar,10,Euro,Wire,0\n'
    snapshots = []
    identities = []
    statuses = []
    for private_label in ('1', '', 'invalid'):
        prior = ('2026/01/02 11:59,A,1,R,1,7,US Dollar,10,Euro,Wire,'
                 + private_label + '\n')
        parsed = parse_canonical_source((header + start + prior + target).encode(),
                                        namespace='ibm-v8-test', member='authored.csv')
        assert parsed.report.event_valid == 3
        identities.append(parsed.events[1].transaction_id)
        statuses.append(parsed.private_labels[1].status)
        snapshots.append(values(replay(parsed.events), parsed.events[2].transaction_id))
    assert len(set(identities)) == 1
    assert statuses == ['eligible_positive', 'missing', 'invalid']
    assert snapshots[0] == snapshots[1] == snapshots[2]
    assert snapshots[0]['sender_out_count_24h'] == 1
    object.__setattr__(parsed.events[1], 'private_label', 1)
    with pytest.raises(ValueError, match='private label'):
        replay(parsed.events)


def test_training_and_scoring_replay_have_identical_feature_values():
    facts = [event('prior', T - timedelta(minutes=1)), event('target', T)]
    assert values(replay(facts, purpose='training'), 'target') == values(
        replay(facts, purpose='scoring'), 'target')
