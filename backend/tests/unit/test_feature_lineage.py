"""T019 RED: history-v1 catalog and fail-closed predictor lineage."""

import importlib

import pytest

KEYS = frozenset({
    'sender_out_count_24h', 'sender_distinct_receivers_24h',
    'sender_paid_count_same_currency_24h', 'sender_paid_sum_same_currency_24h',
    'receiver_in_count_24h', 'receiver_distinct_senders_24h',
    'receiver_received_count_same_currency_24h',
    'receiver_received_sum_same_currency_24h', 'current_paid_amount',
    'current_paid_currency', 'current_payment_format',
})


def feature_module():
    module = importlib.import_module('fraudlens.feature_history')
    assert callable(getattr(module, 'feature_catalog', None)), (
        'T020 missing: versioned history-v1 catalog and lineage metadata')
    assert callable(getattr(module, 'validate_feature_projection', None)), (
        'T020 missing: fail-closed feature projection validator')
    return module


def projection(predictors=None, **extras):
    return {
        'feature_version': 'history-v1',
        'predictors': predictors or {'sender_out_count_24h': 3},
        'join_keys': {'sender_bank': 'A', 'sender_account': '1'},
        **extras,
    }


def test_catalog_exact_allowlist_and_source_lineage():
    catalog = feature_module().feature_catalog()
    assert set(catalog) == KEYS
    assert catalog['sender_paid_sum_same_currency_24h'].source_fields == (
        'sender_bank', 'sender_account', 'paid_amount', 'paid_currency',
        'event_time_utc')
    assert catalog['receiver_received_sum_same_currency_24h'].source_fields == (
        'receiver_bank', 'receiver_account', 'received_amount',
        'received_currency', 'event_time_utc')
    assert catalog['current_payment_format'].source_fields == ('payment_format',)
    assert catalog['sender_paid_sum_same_currency_24h'].direction == 'outgoing_paid'
    assert catalog['sender_paid_sum_same_currency_24h'].unit == (
        'decimal_in_current_paid_currency')
    assert catalog['receiver_received_sum_same_currency_24h'].direction == (
        'incoming_received')
    assert catalog['sender_out_count_24h'].lookback == '[t-24h,t)'
    assert catalog['current_paid_amount'].availability == 'at_event_observation'
    assert all('private_label' not in item.source_fields for item in catalog.values())


def test_bank_account_join_metadata_is_not_returned_as_predictor():
    validated = feature_module().validate_feature_projection(projection())
    assert set(validated) == {'sender_out_count_24h'}
    assert 'sender_bank' not in validated and 'sender_account' not in validated


@pytest.mark.parametrize('forbidden', [
    'transaction_id', 'case_id', 'source_ordinal', 'sender_account',
    'receiver_account', 'sender_join_key', 'raw_account_id',
    'encoded_sender_account', 'hashed_sender_account',
    'encoded_transaction_id', 'hashed_transaction_id',
    'encoded_case_id', 'hashed_case_id',
    'encoded_source_ordinal', 'hashed_source_ordinal',
    'target_label', 'is_laundering', 'label_eligible',
    'private_label_status', 'csv_row_number', 'file_position',
    'future_out_count', 'whole_file_total_paid',
])
def test_forbidden_predictor_or_proxy_is_rejected(forbidden):
    candidate = projection({'sender_out_count_24h': 3, forbidden: 99})
    with pytest.raises(ValueError, match='allowlist|forbidden|lineage'):
        feature_module().validate_feature_projection(candidate)


@pytest.mark.parametrize('source', [
    'transaction_id', 'case_id', 'source_ordinal', 'private_label',
    'label_eligible', 'future_events', 'whole_file_count',
])
def test_catalog_candidate_cannot_launder_forbidden_source(source):
    candidate = projection(lineage={
        'sender_out_count_24h': {'source_fields': [source], 'as_of': 't'},
    })
    with pytest.raises(ValueError, match='allowlist|forbidden|lineage'):
        feature_module().validate_feature_projection(candidate)


def test_nested_extra_field_cannot_hide_private_label():
    candidate = projection(extras={'diagnostics': {'nested': [
        {'label_eligible': True, 'private_label': 1}]}})
    with pytest.raises(ValueError, match='allowlist|forbidden|lineage'):
        feature_module().validate_feature_projection(candidate)


def test_nested_extra_field_cannot_hide_hashed_identifier():
    candidate = projection(extras={'model_inputs': {'sender_account_sha256': 'a' * 64}})
    with pytest.raises(ValueError, match='allowlist|forbidden|lineage'):
        feature_module().validate_feature_projection(candidate)


def test_unknown_category_semantics_are_frozen_without_refit():
    catalog = feature_module().feature_catalog()
    assert catalog['current_paid_currency'].unknown_policy == 'frozen_unknown_encoding'
    assert catalog['current_payment_format'].unknown_policy == 'frozen_unknown_encoding'
    assert catalog['current_payment_format'].missing_policy == 'explicit_null'
    assert catalog['current_payment_format'].unsupported_source_policy == (
        'reject_pending_mapping_revision')
    assert feature_module().validate_feature_projection(
        projection({'current_paid_currency': 'Euro', 'current_payment_format': 'Wire'})) == {
            'current_paid_currency': 'Euro', 'current_payment_format': 'Wire'}


def test_unknown_feature_or_unversioned_projection_is_rejected():
    module = feature_module()
    with pytest.raises(ValueError, match='allowlist|version|unknown'):
        module.validate_feature_projection(projection({'new_future_count': 4}))
    with pytest.raises(ValueError, match='version'):
        module.validate_feature_projection({'predictors': {'sender_out_count_24h': 1}})
