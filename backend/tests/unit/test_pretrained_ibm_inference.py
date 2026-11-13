"""RED contract for the isolated IBM HI-Small pretrained inference adapter.

These examples use authored facts, graph maps and a fake predictor. They never
deserialize the publisher's preprocessing file or load IBM source records.
"""

import importlib
import json
import math
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from fraudlens.data_contracts import CanonicalTransaction

REVISION = '4fc397afa0e22396d26153d69e46e46304411ca0'
VERSION = 'dv_' + 'a' * 64
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
MODEL_SHA = '5c20d22e5e395d3b7e1f2741583f350bdac10d43afcc697ccbcd5373efcfd798'
GRAPH_SHA = 'c' * 64  # synthetic test state, not a published checksum
AT = datetime(2026, 1, 5, 13, 45, tzinfo=UTC)  # Monday
NAMES = (
    'hour', 'dow', 'log_paid', 'log_recv', 'amt_diff', 'ccy_mismatch',
    'self_loop', 'is_round', 'same_bank', 'snd_out_deg', 'snd_in_deg',
    'snd_out_cnt', 'snd_in_cnt', 'snd_out_amt_mean', 'rcv_out_deg',
    'rcv_in_deg', 'rcv_in_cnt', 'gather_scatter', 'amt_to_snd_mean',
    'Receiving Currency', 'Payment Currency', 'Payment Format',
)
CATEGORIES = ('Receiving Currency', 'Payment Currency', 'Payment Format')
NATIVE_NAMES = NAMES[:-3] + (
    'Receiving_Currency', 'Payment_Currency', 'Payment_Format',
)
CURRENCIES = (
    'Australian Dollar', 'Bitcoin', 'Brazil Real', 'Canadian Dollar', 'Euro',
    'Mexican Peso', 'Ruble', 'Rupee', 'Saudi Riyal', 'Shekel', 'Swiss Franc',
    'UK Pound', 'US Dollar', 'Yen', 'Yuan',
)
FORMATS = (
    'ACH', 'Bitcoin', 'Cash', 'Cheque', 'Credit Card', 'Reinvestment', 'Wire',
)
DEFAULT = object()


def api():
    # A missing module is an assertion inside collected tests, not a collection error.
    try:
        module = importlib.import_module('fraudlens.pretrained_inference')
    except ModuleNotFoundError as exc:
        if exc.name != 'fraudlens.pretrained_inference':
            raise
        pytest.fail('RED: fraudlens.pretrained_inference adapter is not implemented')
    assert callable(getattr(module, 'build_ibm_feature_vector', None)), (
        'RED: build_ibm_feature_vector is not implemented'
    )
    assert callable(getattr(module, 'score_ibm_transaction', None)), (
        'RED: score_ibm_transaction is not implemented'
    )
    return module


def event(**changes):
    base = CanonicalTransaction(
        transaction_id='tx-synthetic-7', case_id='case-synthetic-7', source_ordinal=7,
        event_time_raw='2026/01/05 13:45', event_time_utc=AT,
        event_time_epoch_ns=int(AT.timestamp()) * 1_000_000_000,
        time_basis='assumed_utc_for_synthetic_benchmark',
        sender_bank='Bank A', sender_account='sender-1',
        receiver_bank='Bank A', receiver_account='receiver-2',
        sender_join_key=b'synthetic-sender-qualified',
        receiver_join_key=b'synthetic-receiver-qualified',
        paid_amount='100.00', paid_currency='Euro',
        received_amount='90.00', received_currency='US Dollar',
        payment_format='Wire', event_fact_digest=b'synthetic-fact-digest',
    )
    return replace(base, **changes)


def graph(**changes):
    base = {
        'source_sha256': SOURCE_SHA, 'dataset_version': VERSION,
        'model_revision': REVISION, 'state_sha256': GRAPH_SHA,
        'training_end_exclusive': AT - timedelta(days=1),
        'coverage_complete': True,
        'identity_policy': 'unqualified_account_collision_checked',
        'account_bank_index': {'sender-1': 'Bank A', 'receiver-2': 'Bank A'},
        'out_deg': {'sender-1': 6, 'receiver-2': 2},
        'in_deg': {'sender-1': 5, 'receiver-2': 3},
        'out_cnt': {'sender-1': 8},
        'in_cnt': {'sender-1': 7, 'receiver-2': 4},
        'out_amt_mean': {'sender-1': 50.0},
    }
    return {**base, **changes}


def manifest(**changes):
    base = {
        'domain': 'ibm_hi_small_is_laundering', 'source_sha256': SOURCE_SHA,
        'dataset_version': VERSION, 'revision': REVISION,
        'model_sha256': MODEL_SHA, 'graph_state_sha256': GRAPH_SHA,
        'feature_policy': 'fraudsentinel-ibm-aml-v1',
        'feature_names': NAMES, 'native_feature_names': NATIVE_NAMES,
        'categorical_columns': CATEGORIES,
        # Exact category order from the pinned native LightGBM footer.
        'categorical_vocabulary': {
            'Receiving Currency': CURRENCIES,
            'Payment Currency': CURRENCIES,
            'Payment Format': FORMATS,
        },
        'score_kind': 'uncalibrated_model_score',
    }
    return {**base, **changes}


def vector(tx=None, state=DEFAULT, spec=None):
    return api().build_ibm_feature_vector(
        event() if tx is None else tx,
        dataset_version=VERSION,
        graph_state=graph() if state is DEFAULT else state,
        model_manifest=manifest() if spec is None else spec,
    )


class FakePredictor:
    def __init__(self, result=0.25):
        self.result = result
        self.calls = []

    def predict(self, feature_values):
        self.calls.append(feature_values)
        return [self.result]

    def fit(self, *_args, **_kwargs):
        pytest.fail('Inference must not fit a model')

    def train(self, *_args, **_kwargs):
        pytest.fail('Inference must not train a model')

    def partial_fit(self, *_args, **_kwargs):
        pytest.fail('Inference must not refit a model')


def score(tx=None, state=None, spec=None, predictor=None):
    return api().score_ibm_transaction(
        event() if tx is None else tx,
        dataset_version=VERSION,
        graph_state=graph() if state is None else state,
        model_manifest=manifest() if spec is None else spec,
        predictor=FakePredictor() if predictor is None else predictor,
    )


def assert_rejected(call, reason):
    module = api()
    with pytest.raises(module.PretrainedInferenceError) as caught:
        call()
    assert caught.value.reason_code == reason


def test_ibm_source_fields_map_to_exact_ordered_22_feature_vector():
    got = vector()
    values = tuple(got.values)
    assert got.transaction_id == 'tx-synthetic-7'
    assert tuple(got.feature_names) == NAMES
    assert len(values) == 22
    assert values[:2] == (13, 0)
    assert values[2] == pytest.approx(math.log1p(100))
    assert values[3] == pytest.approx(math.log1p(90))
    assert values[4:9] == (10.0, 1, 0, 1, 1)
    assert values[9:18] == (6, 5, 8, 7, 50.0, 2, 3, 4, 1)
    assert values[18] == pytest.approx(100 / (50 + 1e-6))
    assert values[19:] == ('US Dollar', 'Euro', 'Wire')


def test_recorded_source_positions_and_native_schema_are_exact():
    mapping_path = (
        Path(__file__).resolve().parents[3] / 'data' / 'mappings'
        / 'ibm_hi_small_v1.json'
    )
    mapping = json.loads(mapping_path.read_text(encoding='utf-8'))
    assert tuple(mapping['csv']['expected_ordered_headers']) == (
        'Timestamp', 'From Bank', 'Account', 'To Bank', 'Account',
        'Amount Received', 'Receiving Currency', 'Amount Paid',
        'Payment Currency', 'Payment Format', 'Is Laundering',
    )
    assert tuple(col['role'] for col in mapping['columns']) == (
        'event_time_raw', 'sender_bank', 'sender_account', 'receiver_bank',
        'receiver_account', 'received_amount', 'received_currency',
        'paid_amount', 'paid_currency', 'payment_format',
        'private_evaluation_label',
    )
    assert len(NAMES) == len(NATIVE_NAMES) == 22
    assert NATIVE_NAMES[-3:] == (
        'Receiving_Currency', 'Payment_Currency', 'Payment_Format',
    )


def test_pinned_categorical_codes_are_stable_and_ordered():
    assert CURRENCIES.index('US Dollar') == 12
    assert CURRENCIES.index('Euro') == 4
    assert FORMATS.index('Wire') == 6
    got = vector()
    assert tuple(got.values)[19:] == ('US Dollar', 'Euro', 'Wire')
    assert tuple(got.categorical_codes) == (12, 4, 6)


def test_exact_money_and_currency_meaning_are_preserved():
    tx = event(paid_amount='100.125000', received_amount='90.250000')
    got = vector(tx)
    assert (tx.paid_amount, tx.received_amount) == ('100.125000', '90.250000')
    values = tuple(got.values)
    assert values[2] == pytest.approx(math.log1p(100.125))
    assert values[3] == pytest.approx(math.log1p(90.25))
    assert values[4] == pytest.approx(9.875)
    assert values[19:] == ('US Dollar', 'Euro', 'Wire')


def test_paid_and_received_sides_are_not_swapped_or_currency_converted():
    tx = event(
        paid_amount='90.00', paid_currency='US Dollar',
        received_amount='100.00', received_currency='Euro',
    )
    values = tuple(vector(tx).values)
    assert values[2:5] == pytest.approx(
        (math.log1p(90), math.log1p(100), 10.0)
    )
    assert values[19:] == ('Euro', 'US Dollar', 'Wire')


def test_synthetic_midnight_uses_recorded_minute_not_host_timezone():
    at = datetime(2026, 1, 6, 0, 0, tzinfo=UTC)  # Tuesday
    tx = event(
        event_time_raw='2026/01/06 00:00', event_time_utc=at,
        event_time_epoch_ns=int(at.timestamp()) * 1_000_000_000,
    )
    assert tuple(vector(tx).values)[:2] == (0, 1)


def test_matching_currency_and_account_values_follow_upstream_semantics():
    tx = event(receiver_account='sender-1', received_currency='Euro')
    state = graph(account_bank_index={'sender-1': 'Bank A'})
    got = vector(tx, state)
    assert tuple(got.values)[5:7] == (0, 1)
    assert tuple(got.values)[19:21] == ('Euro', 'Euro')


@pytest.mark.parametrize('change', [
    {'event_time_raw': 'invalid'}, {'paid_amount': '-1'},
    {'received_amount': 'NaN'}, {'paid_currency': ''},
    {'sender_account': ''}, {'receiver_bank': ''},
])
def test_malformed_or_missing_required_source_fields_fail_closed(change):
    assert_rejected(lambda: vector(event(**change)), 'invalid_source_event')


def test_private_label_or_unknown_source_fields_never_enter_model_input():
    tx = {**vars(event()), 'Is Laundering': 1}
    assert_rejected(lambda: score(tx), 'forbidden_input_field')


def test_ieee_fields_cannot_substitute_for_ibm_inputs():
    tx = {**vars(event()), 'card1': 'invented', 'TransactionDT': 123}
    assert_rejected(lambda: vector(tx), 'forbidden_input_field')


def test_unknown_category_is_not_fabricated_or_refitted():
    assert_rejected(
        lambda: vector(event(payment_format='Unsupported format')),
        'unsupported_category',
    )


def test_graph_state_is_required_and_bound_to_source_and_model():
    for state in (None, graph(source_sha256='d' * 64),
                  graph(model_revision='wrong'), graph(state_sha256='e' * 64)):
        assert_rejected(lambda state=state: vector(event(), state), 'incompatible_graph_state')


def test_missing_identity_or_cutoff_provenance_cannot_be_inferred_from_graph_maps():
    for state in (
        graph(account_bank_index=None),
        graph(identity_policy=None),
        graph(training_end_exclusive=None),
    ):
        assert_rejected(lambda state=state: vector(event(), state),
                        'incompatible_graph_state')


def test_dataset_and_feature_lineage_must_match():
    for spec in (manifest(dataset_version='dv_' + '0' * 64),
                 manifest(feature_policy='history-v1'),
                 manifest(source_sha256='0' * 64)):
        assert_rejected(lambda spec=spec: vector(event(), graph(), spec),
                        'incompatible_lineage')


def test_bank_qualified_collision_cannot_use_unqualified_graph_lookup():
    state = graph(account_bank_index={'sender-1': ('Bank A', 'Bank B'),
                                      'receiver-2': 'Bank A'})
    assert_rejected(lambda: vector(event(), state), 'ambiguous_account_identity')
    cross_bank = event(receiver_account='sender-1', receiver_bank='Bank B')
    assert_rejected(lambda: vector(cross_bank, graph()), 'ambiguous_account_identity')


def test_training_period_graph_cannot_score_earlier_transaction():
    state = graph(training_end_exclusive=AT + timedelta(minutes=1))
    assert_rejected(lambda: vector(event(), state), 'future_graph_state')


def test_missing_graph_aggregates_are_not_invented_zeroes():
    state = graph(out_deg={}, coverage_complete=False)
    assert_rejected(lambda: vector(event(), state), 'incomplete_graph_coverage')
    state = graph(out_deg={})
    assert_rejected(lambda: vector(event(), state), 'incomplete_graph_coverage')


def test_native_feature_order_and_category_metadata_must_match():
    assert_rejected(lambda: vector(event(), graph(), manifest(feature_names=NAMES[::-1])),
                    'incompatible_feature_schema')
    assert_rejected(lambda: vector(event(), graph(), manifest(categorical_columns=())),
                    'incompatible_feature_schema')
    native = NATIVE_NAMES[:-1] + ('Payment Format',)
    assert_rejected(
        lambda: vector(event(), graph(), manifest(native_feature_names=native)),
        'incompatible_feature_schema',
    )
    bad_vocab = dict(manifest()['categorical_vocabulary'])
    bad_vocab['Payment Format'] = tuple(reversed(FORMATS))
    assert_rejected(
        lambda: vector(event(), graph(), manifest(categorical_vocabulary=bad_vocab)),
        'incompatible_feature_schema',
    )


def test_synthetic_time_basis_must_match_documented_assumption():
    assert_rejected(
        lambda: vector(event(time_basis='source_explicit_timezone')),
        'incompatible_lineage',
    )


def test_prediction_identity_provenance_and_uncalibrated_score():
    predictor = FakePredictor(0.25)
    got = score(predictor=predictor)
    assert len(predictor.calls) == 1
    assert got.transaction_id == 'tx-synthetic-7'
    assert got.score == pytest.approx(0.25)
    assert got.score_kind == 'uncalibrated_model_score'
    assert got.score_source == 'model'
    assert got.model_revision == REVISION
    assert got.artifact_sha256 == MODEL_SHA
    assert 'label' not in repr(predictor.calls[0]).lower()


@pytest.mark.parametrize('result', [float('nan'), float('inf'), -0.1, 1.1, [], [0.1, 0.2]])
def test_nonfinite_out_of_range_or_malformed_predictions_are_rejected(result):
    assert_rejected(lambda: score(predictor=FakePredictor(result)), 'invalid_prediction')


def test_prediction_identity_must_not_be_reassigned():
    class WrongIdentityPredictor(FakePredictor):
        def predict(self, feature_values):
            self.calls.append(feature_values)
            return {'transaction_id': 'other-transaction', 'score': 0.25}

    assert_rejected(lambda: score(predictor=WrongIdentityPredictor()),
                    'invalid_prediction_identity')


def test_fake_inference_never_trains_or_uses_private_labels():
    predictor = FakePredictor()
    score(predictor=predictor)
    assert len(predictor.calls) == 1
    assert 'Is Laundering' not in repr(predictor.calls[0])
