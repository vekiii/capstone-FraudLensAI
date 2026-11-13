"""T023 RED: hand-computed rules-v1 arithmetic and label-free replay."""

import importlib
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from fraudlens.data_contracts import CanonicalTransaction, ScoreRequestV2, score_v2
from fraudlens.feature_history import build_feature_snapshots

START = datetime(2026, 1, 1, tzinfo=UTC)
T = START + timedelta(hours=36)
VERSION = 'dv_' + 'a' * 64


def event(name, at, *, sender=('A', '1'), receiver=('R', '1'),
          paid='10', paid_currency='Euro', received='7',
          received_currency='US Dollar'):
    return CanonicalTransaction(
        transaction_id=name, case_id='case-' + name, source_ordinal=1,
        event_time_raw=at.strftime('%Y/%m/%d %H:%M'), event_time_utc=at,
        event_time_epoch_ns=int(at.timestamp()) * 1_000_000_000,
        time_basis='assumed_utc', sender_bank=sender[0], sender_account=sender[1],
        receiver_bank=receiver[0], receiver_account=receiver[1],
        sender_join_key=repr(sender).encode(), receiver_join_key=repr(receiver).encode(),
        paid_amount=paid, paid_currency=paid_currency,
        received_amount=received, received_currency=received_currency,
        payment_format='Wire', event_fact_digest=name.encode(),
    )


def history(*, current_paid='40', current_currency='Euro', prior_count=3,
            coverage_start=START, missing_intervals=(), extra=()):
    amounts = ('10', '20', '30')
    facts = [event(f'p{i}', T - timedelta(minutes=60-i*10), paid=amounts[i],
                   received=('7', '9', '11')[i]) for i in range(prior_count)]
    target = event('target', T, paid=current_paid, paid_currency=current_currency)
    facts.extend([target, *extra])
    snapshots = build_feature_snapshots(facts, dataset_version=VERSION,
                                        coverage_start=coverage_start,
                                        missing_intervals=missing_intervals)
    return target, snapshots['target']


def request(event_fact, snapshot):
    return ScoreRequestV2(event_fact, snapshot, VERSION, 'run_authored',
                          'rules-v1', 'history-v1', event_fact.event_time_utc)


def evaluate(event_fact, snapshot):
    module = importlib.import_module('fraudlens.rule_scoring')
    fn = getattr(module, 'evaluate_rules', None)
    assert callable(fn), 'T024 missing: evaluate_rules frozen rules-v1'
    return fn(request(event_fact, snapshot))


def reasons(result):
    return {reason.rule_id: reason for reason in result.reasons}


def test_exact_all_thresholds_and_r3_equality():
    fact, snapshot = history()
    result = evaluate(fact, snapshot)
    assert result.score == Decimal('1.00')
    assert result.policy_version == 'rules-v1'
    assert result.policy_sha256 == (
        'a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce')
    assert {key: item.contribution for key, item in reasons(result).items()} == {
        'R1': Decimal('0.35'), 'R2': Decimal('0.30'), 'R3': Decimal('0.35')}
    assert all(item.state == 'fired' for item in result.reasons)
    assert reasons(result)['R3'].comparison == '40*3 >= 2*60'
    assert reasons(result)['R3'].observed_amount == Decimal('40')
    assert reasons(result)['R3'].currency == 'Euro'


def test_just_below_exact_r3_threshold_keeps_r1_r2():
    fact, snapshot = history(current_paid='39.999999')
    result = evaluate(fact, snapshot)
    assert result.score == Decimal('0.65')
    assert reasons(result)['R1'].state == 'fired'
    assert reasons(result)['R2'].state == 'fired'
    assert reasons(result)['R3'].state == 'not_fired'
    assert reasons(result)['R3'].contribution == Decimal('0')
    assert reasons(result)['R3'].comparison == '39.999999*3 >= 2*60'


def test_two_prior_rows_make_r3_comparison_unavailable():
    fact, snapshot = history(prior_count=2)
    result = evaluate(fact, snapshot)
    assert result.score == Decimal('0.00')
    assert reasons(result)['R1'].observed_count == 2
    assert reasons(result)['R2'].observed_count == 2
    assert reasons(result)['R3'].observed_count == 2
    assert reasons(result)['R3'].state == 'comparison_unavailable'
    assert reasons(result)['R3'].contribution == Decimal('0')


def test_full_coverage_measured_cold_start_is_zero_not_missing():
    target = event('target', T, sender=('NEW', '1'), receiver=('NEW', '2'))
    snapshot = build_feature_snapshots([target], dataset_version=VERSION,
                                       coverage_start=START)['target']
    result = evaluate(target, snapshot)
    assert result.score == Decimal('0.00')
    assert [item.observed_count for item in result.reasons] == [0, 0, 0]
    assert reasons(result)['R3'].state == 'comparison_unavailable'


@pytest.mark.parametrize('state', ['incomplete', 'unavailable'])
def test_deficient_coverage_never_emits_ordinal_score(state):
    fact, snapshot = history()
    snapshot = replace(snapshot, coverage_state=state, scoreable=False)
    with pytest.raises(ValueError):
        evaluate(fact, snapshot)


def test_r1_r2_thresholds_are_independent():
    priors = [event(f's{i}', T - timedelta(minutes=20-i),
                    receiver=('OTHER', str(i))) for i in range(3)]
    target = event('target', T, receiver=('R', '1'))
    snapshot = build_feature_snapshots([*priors, target], dataset_version=VERSION,
                                       coverage_start=START)['target']
    result = evaluate(target, snapshot)
    assert result.score == Decimal('0.35')
    assert reasons(result)['R1'].state == 'fired'
    assert reasons(result)['R2'].state == 'not_fired'


def test_paid_currency_changes_r3_group_without_fx():
    fact, snapshot = history(current_currency='US Dollar')
    result = evaluate(fact, snapshot)
    assert result.score == Decimal('0.65')
    assert reasons(result)['R3'].observed_count == 0
    assert reasons(result)['R3'].currency == 'US Dollar'
    assert reasons(result)['R3'].state == 'comparison_unavailable'


def test_future_event_and_private_label_do_not_change_prior_rule_score():
    fact, snapshot = history()
    later = event('later', T + timedelta(minutes=1), paid='99999')
    fact2, snapshot2 = history(extra=(later,))
    # Private evaluation labels live outside CanonicalTransaction and replay.
    private_labels = {'p0': 1, 'p1': None, 'p2': 'invalid'}
    first = evaluate(fact, snapshot)
    private_labels['p0'] = None
    second = evaluate(fact2, snapshot2)
    assert private_labels['p0'] is None
    assert first == second


def test_opaque_transaction_and_case_ids_do_not_affect_rule_conditions():
    fact, snapshot = history()
    changed = replace(fact, transaction_id='opaque-new', case_id='opaque-case')
    changed_snapshot = replace(snapshot, transaction_id='opaque-new')
    first = evaluate(fact, snapshot)
    second = evaluate(changed, changed_snapshot)
    assert first == second


def test_rules_adapter_uses_v2_boundary_without_model_artifact():
    from fraudlens.rule_scoring import RuleScorer

    fact, snapshot = history()
    assessment = score_v2(request(fact, snapshot), RuleScorer())
    assert assessment.score == Decimal('1.00')
    assert assessment.score_kind == 'ordinal_rule_score'
    assert assessment.score_source == 'rules'
    assert assessment.explanation.method == 'rules'
    assert assessment.explanation.feature_snapshot_digest == snapshot.feature_input_digest
    assert [item['contribution'] for item in assessment.explanation.items] == [
        Decimal('0.35'), Decimal('0.30'), Decimal('0.35')]


def test_rules_repeat_has_same_semantics_across_run_and_wall_clock():
    from fraudlens.rule_scoring import RuleScorer

    fact, snapshot = history(current_paid='39.999999')
    first_request = request(fact, snapshot)
    first = score_v2(first_request, RuleScorer())
    second = score_v2(replace(first_request, run_id='run_authored_2'), RuleScorer())
    assert first.run_id != second.run_id
    for key in ('transaction_id', 'dataset_version', 'score', 'score_kind',
                'score_source', 'scorer_version', 'feature_version',
                'artifact_version', 'event_time_utc',
                'history_cutoff_exclusive_at', 'history_coverage', 'explanation'):
        assert getattr(first, key) == getattr(second, key)
    assert first.score == Decimal('0.65')


def test_zero_score_explains_nonfires_and_unavailable_r3():
    from fraudlens.rule_scoring import RuleScorer

    fact, snapshot = history(prior_count=2)
    assessment = score_v2(request(fact, snapshot), RuleScorer())
    assert assessment.score == Decimal('0.00')
    assert [item['contribution'] for item in assessment.explanation.items] == [
        Decimal(0), Decimal(0), Decimal(0)]
    assert assessment.explanation.items[2]['rule_condition'].startswith(
        'comparison_unavailable:')
