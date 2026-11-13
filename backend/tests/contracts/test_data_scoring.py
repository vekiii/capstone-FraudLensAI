"""T021 RED: synthetic v2 scorer boundary, separate from Foundation v1."""

import importlib
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from fraudlens.data_contracts import CanonicalTransaction
from fraudlens.feature_history import build_feature_snapshots

START = datetime(2026, 1, 1, tzinfo=UTC)
EVENT_TIME = START + timedelta(hours=36)
SCORED_AT = EVENT_TIME + timedelta(minutes=7)
VERSION = 'dv_' + 'a' * 64
RUN = 'run_synthetic_1'


def _event():
    return CanonicalTransaction(
        transaction_id='D' + '1' * 32, case_id='C' + '1' * 32,
        source_ordinal=1, event_time_raw='2026/01/02 12:00',
        event_time_utc=EVENT_TIME,
        event_time_epoch_ns=int(EVENT_TIME.timestamp()) * 1_000_000_000,
        time_basis='assumed_utc', sender_bank='A', sender_account='1',
        receiver_bank='R', receiver_account='2', sender_join_key=b'A:1',
        receiver_join_key=b'R:2', paid_amount='40.000001', paid_currency='Euro',
        received_amount='39.999999', received_currency='US Dollar',
        payment_format='Wire', event_fact_digest=b'\x01' * 32,
    )


def _snapshot(event=None):
    event = event or _event()
    return build_feature_snapshots([event], dataset_version=VERSION,
                                   coverage_start=START)[event.transaction_id]


def _fields(event=None, snapshot=None):
    event = event or _event()
    snapshot = snapshot or _snapshot(event)
    return dict(canonical_transaction=event, feature_snapshot=snapshot,
                dataset_version=VERSION, run_id=RUN, scorer_version='rules-v1',
                feature_version='history-v1',
                history_cutoff_exclusive_at=EVENT_TIME)


def _boundary():
    module = importlib.import_module('fraudlens.data_contracts')
    request_type = getattr(module, 'ScoreRequestV2', None)
    score = getattr(module, 'score_v2', None)
    assert request_type is not None, 'T022 missing: ScoreRequestV2'
    assert callable(score), 'T022 missing: score_v2 validation boundary'
    return request_type, score


class ControlledScorer:
    """Returns one authored response; no real rules, model, or fallback."""

    requires_artifact = False

    def __init__(self, *, changes=None, mutate=False, requires_artifact=False):
        self.changes = changes or {}
        self.mutate = mutate
        self.requires_artifact = requires_artifact
        self.calls = 0

    def score(self, request):
        self.calls += 1
        snapshot = request.feature_snapshot
        if self.mutate:
            snapshot.feature_values['sender_out_count_24h'] = 999
        result = dict(
            transaction_id=request.canonical_transaction.transaction_id,
            dataset_version=request.dataset_version, run_id=request.run_id,
            score=Decimal('0.35'), score_kind='ordinal_rule_score',
            score_source='rules', scorer_version=request.scorer_version,
            feature_version=request.feature_version,
            artifact_version='rules-v1',
            event_time_utc=request.canonical_transaction.event_time_utc,
            history_cutoff_exclusive_at=request.history_cutoff_exclusive_at,
            scored_at=SCORED_AT,
            history_coverage={'state': snapshot.coverage_state,
                              'start': snapshot.coverage_start},
            explanation={'status': 'unavailable', 'reason_code': 'synthetic_test',
                         'feature_snapshot_digest': snapshot.feature_input_digest},
        )
        result.update(self.changes)
        return result


def _score(*, fields=None, scorer=None, artifact=None):
    fields = fields or _fields()
    request_type, score = _boundary()
    request = request_type(**fields)
    scorer = scorer or ControlledScorer()
    return score(request, scorer, artifact=artifact), request, scorer


def test_valid_request_and_response_preserve_all_references_and_digest():
    assessment, request, scorer = _score()
    assert scorer.calls == 1
    assert assessment.transaction_id == request.canonical_transaction.transaction_id
    assert assessment.dataset_version == VERSION
    assert assessment.run_id == RUN
    assert assessment.feature_version == 'history-v1'
    assert assessment.scorer_version == 'rules-v1'
    assert assessment.history_cutoff_exclusive_at == request.feature_snapshot.as_of
    assert assessment.history_coverage == {'state': 'full', 'start': START}
    assert assessment.explanation.feature_snapshot_digest == (
        request.feature_snapshot.feature_input_digest)
    assert assessment.score == Decimal('0.35')


@pytest.mark.parametrize('field,value', [
    ('dataset_version', 'dv_' + 'b' * 64),
    ('feature_version', 'history-v2'),
    ('history_cutoff_exclusive_at', EVENT_TIME + timedelta(minutes=1)),
])
def test_request_rejects_mismatched_version_or_as_of(field, value):
    with pytest.raises((ValueError, TypeError)):
        _score(fields={**_fields(), field: value})


@pytest.mark.parametrize('field,value', [
    ('transaction_id', 'D' + '2' * 32),
    ('dataset_version', 'dv_' + 'b' * 64),
    ('run_id', 'run_other'),
    ('feature_version', 'history-v2'),
    ('scorer_version', 'rules-v2'),
    ('history_cutoff_exclusive_at', EVENT_TIME + timedelta(minutes=1)),
])
def test_response_rejects_changed_identity_or_version(field, value):
    with pytest.raises((ValueError, TypeError)):
        _score(scorer=ControlledScorer(changes={field: value}))


def test_request_rejects_changed_snapshot_transaction_identity():
    fields = _fields()
    fields['feature_snapshot'] = replace(fields['feature_snapshot'],
                                         transaction_id='D' + '2' * 32)
    with pytest.raises((ValueError, TypeError)):
        _score(fields=fields)


@pytest.mark.parametrize('change', [
    {'feature_version': 'history-v2'},
    {'coverage_state': 'incomplete'},
    {'scoreable': False},
    {'feature_values': {'unknown_predictor': 1}},
    {'feature_input_digest': '0' * 64},
])
def test_request_rejects_bad_snapshot_schema_or_coverage(change):
    fields = _fields()
    fields['feature_snapshot'] = replace(fields['feature_snapshot'], **change)
    with pytest.raises((ValueError, TypeError)):
        _score(fields=fields)


def test_response_rejects_wrong_explanation_digest():
    bad = {'status': 'unavailable', 'reason_code': 'synthetic_test',
           'feature_snapshot_digest': '0' * 64}
    with pytest.raises((ValueError, TypeError)):
        _score(scorer=ControlledScorer(changes={'explanation': bad}))


@pytest.mark.parametrize('change', [
    {'history_coverage': {'state': 'incomplete', 'start': START}},
    {'history_coverage': {'state': 'full', 'start': EVENT_TIME}},
    {'unexpected_private': {'label': 1}},
    {'explanation': {'status': 'unavailable', 'reason_code': 'synthetic_test',
                     'feature_snapshot_digest': '0' * 64,
                     'nested': {'label': 1}}},
])
def test_response_rejects_bad_coverage_or_extra_private_data(change):
    with pytest.raises((ValueError, TypeError)):
        _score(scorer=ControlledScorer(changes=change))


def test_available_explanation_cannot_launder_private_label_as_feature():
    snapshot = _snapshot()
    explanation = {
        'status': 'available', 'method': 'rules', 'explained_scale': 'risk_score',
        'feature_snapshot_digest': snapshot.feature_input_digest,
        'partial': False, 'base_value': Decimal(0), 'remainder': Decimal(0),
        'items': [{'feature_key': 'private_label', 'observed_value': '1',
                   'unit': 'label', 'direction': 'increases',
                   'contribution': Decimal('0.35'), 'rule_condition': 'hidden target'}],
    }
    with pytest.raises((ValueError, TypeError)):
        _score(fields=_fields(snapshot=snapshot),
               scorer=ControlledScorer(changes={'explanation': explanation}))


@pytest.mark.parametrize('change', [
    {'method': 'tree_path'},
    {'explained_scale': 'log_odds'},
    {'items': [{'feature_key': 'sender_out_count_24h', 'observed_value': '0',
                'unit': 'events', 'direction': 'neutral',
                'contribution': Decimal('0.30'), 'rule_condition': 'R1 false'}]},
])
def test_available_rule_explanation_matches_source_scale_and_score(change):
    snapshot = _snapshot()
    explanation = {
        'status': 'available', 'method': 'rules', 'explained_scale': 'risk_score',
        'feature_snapshot_digest': snapshot.feature_input_digest,
        'partial': False, 'base_value': Decimal(0), 'remainder': Decimal(0),
        'items': [{'feature_key': 'sender_out_count_24h', 'observed_value': '0',
                   'unit': 'events', 'direction': 'neutral',
                   'contribution': Decimal('0.35'), 'rule_condition': 'R1 false'}],
    }
    explanation.update(change)
    with pytest.raises(ValueError):
        _score(fields=_fields(snapshot=snapshot),
               scorer=ControlledScorer(changes={'explanation': explanation}))


def test_required_artifact_absent_fails_without_calling_scorer():
    scorer = ControlledScorer(requires_artifact=True)
    with pytest.raises((ValueError, TypeError)):
        _score(scorer=scorer)
    assert scorer.calls == 0


def test_event_as_of_and_actual_scoring_times_are_distinct():
    assessment, request, _ = _score()
    assert assessment.event_time_utc == EVENT_TIME
    assert assessment.history_cutoff_exclusive_at == EVENT_TIME
    assert assessment.scored_at == SCORED_AT
    assert assessment.scored_at > assessment.event_time_utc
    assert request.feature_snapshot.created_at != assessment.scored_at


def test_repeated_scoring_compares_semantics_separately_from_execution_metadata():
    first, _, _ = _score()
    second, _, _ = _score(scorer=ControlledScorer(
        changes={'scored_at': SCORED_AT + timedelta(seconds=1)}))
    for key in ('transaction_id', 'dataset_version', 'run_id', 'feature_version',
                'scorer_version', 'score', 'score_kind', 'score_source',
                'history_cutoff_exclusive_at', 'history_coverage'):
        assert getattr(first, key) == getattr(second, key)
    assert first.explanation.feature_snapshot_digest == (
        second.explanation.feature_snapshot_digest)
    assert first.scored_at != second.scored_at


def test_injected_scorer_cannot_mutate_original_request():
    fields = _fields()
    original = deepcopy(fields['feature_snapshot'].feature_values)
    _, request, _ = _score(fields=fields, scorer=ControlledScorer(mutate=True))
    assert fields['feature_snapshot'].feature_values == original
    assert request.feature_snapshot.feature_values == original


@pytest.mark.parametrize('private', [
    {'private_label': 1},
    {'feature_values': {'current_paid_amount': {'value': '40', 'target': 1}}},
])
def test_request_rejects_private_or_nested_unexpected_data(private):
    fields = _fields()
    if 'feature_values' in private:
        fields['feature_snapshot'] = replace(fields['feature_snapshot'], **private)
    else:
        fields.update(private)
    with pytest.raises((ValueError, TypeError)):
        _score(fields=fields)


@pytest.mark.parametrize('bad_score', [True, False, '0.35', float('nan'),
                                           float('inf'), -float('inf'),
                                           Decimal('-0.01'), Decimal('1.01')])
def test_invalid_score_fails_without_coercion_clamp_zero_or_fallback(bad_score):
    scorer = ControlledScorer(changes={'score': bad_score})
    with pytest.raises((ValueError, TypeError)):
        _score(scorer=scorer)
    assert scorer.calls == 1
