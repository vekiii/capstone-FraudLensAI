"""Synthetic validation contracts for Feature 002 (T205); no source rows used."""

import importlib

import pytest

from fraudlens.data.source import stable_transaction_id

SOURCE_SHA256 = 'a' * 64
BASE_ROW = {
    'source_sha256': SOURCE_SHA256,
    'source_row_number': 1,
    'transaction_id': stable_transaction_id(SOURCE_SHA256, 1),
    'timestamp': '2022/09/01 00:00',
    'sender_bank': '0007',
    'sender_account': '000012345',
    'receiver_bank': '0012',
    'receiver_account': '000000007',
    'amount_received': '10.00',
    'receiving_currency': 'EUR',
    'amount_paid': '10.00',
    'payment_currency': 'EUR',
    'payment_format': 'Wire',
    'is_laundering': '0',
}

EXPECTED_REASON_CODES = {
    'INVALID_TIMESTAMP',
    'MISSING_SENDER_BANK',
    'MISSING_SENDER_ACCOUNT',
    'MISSING_RECEIVER_BANK',
    'MISSING_RECEIVER_ACCOUNT',
    'INVALID_AMOUNT_RECEIVED',
    'INVALID_AMOUNT_PAID',
    'MISSING_RECEIVING_CURRENCY',
    'MISSING_PAYMENT_CURRENCY',
    'MISSING_PAYMENT_FORMAT',
    'INVALID_LABEL',
    'MISSING_REQUIRED_FIELD',
}


def validation_module():
    """Load the batch validator that T206 will implement."""
    try:
        module = importlib.import_module('fraudlens.data.validation')
    except ModuleNotFoundError as error:
        if error.name not in {'fraudlens.data.validation'}:
            raise
        pytest.fail('Missing Feature 002 canonical validator (T206)', pytrace=False)
    assert callable(getattr(module, 'validate_rows', None)), 'Missing validate_rows boundary'
    return module


def row_with(**changes):
    row = {**BASE_ROW, **changes}
    row['transaction_id'] = stable_transaction_id(
        row['source_sha256'], row['source_row_number'],
    )
    return row


@pytest.mark.parametrize(
    ('field', 'value', 'reason_code'),
    [
        ('timestamp', '2022/02/30 12:00', 'INVALID_TIMESTAMP'),
        ('timestamp', '', 'INVALID_TIMESTAMP'),
        ('sender_bank', '', 'MISSING_SENDER_BANK'),
        ('sender_account', '', 'MISSING_SENDER_ACCOUNT'),
        ('receiver_bank', '', 'MISSING_RECEIVER_BANK'),
        ('receiver_account', '', 'MISSING_RECEIVER_ACCOUNT'),
        ('amount_received', '-1.00', 'INVALID_AMOUNT_RECEIVED'),
        ('amount_received', 'NaN', 'INVALID_AMOUNT_RECEIVED'),
        ('amount_received', '', 'INVALID_AMOUNT_RECEIVED'),
        ('amount_paid', '1,00', 'INVALID_AMOUNT_PAID'),
        ('amount_paid', 'Infinity', 'INVALID_AMOUNT_PAID'),
        ('amount_paid', '', 'INVALID_AMOUNT_PAID'),
        ('receiving_currency', '', 'MISSING_RECEIVING_CURRENCY'),
        ('payment_currency', '', 'MISSING_PAYMENT_CURRENCY'),
        ('payment_format', '', 'MISSING_PAYMENT_FORMAT'),
    ],
)
def test_malformed_or_missing_values_get_bounded_reason_codes(field, value, reason_code):
    report = validation_module().validate_rows([row_with(**{field: value})])

    assert report.source_count == 1
    assert report.accepted_count == 0
    assert report.rejected_count == 1
    rejection = report.rejections[0]
    assert rejection.source_row_number == 1
    assert rejection.reason_code == reason_code
    assert rejection.reason_code in EXPECTED_REASON_CODES
    assert len(rejection.reason_code) <= 32
    assert not value or value not in repr(rejection)


@pytest.mark.parametrize('label', ['2', '-1', 'true', '01', ''])
def test_unsupported_or_malformed_label_encoding_is_rejected_without_echo(label):
    report = validation_module().validate_rows([row_with(is_laundering=label)])

    assert report.rejected_count == 1
    rejection = report.rejections[0]
    assert rejection.reason_code == 'INVALID_LABEL'
    assert rejection.source_row_number == 1
    assert not label or label not in repr(rejection)


@pytest.mark.parametrize('field', ['timestamp', 'sender_account', 'amount_paid', 'is_laundering'])
def test_missing_required_field_is_rejected_with_source_row_reference(field):
    row = row_with()
    row.pop(field)

    report = validation_module().validate_rows([row])

    assert report.rejected_count == 1
    rejection = report.rejections[0]
    assert rejection.source_row_number == 1
    assert rejection.reason_code == 'MISSING_REQUIRED_FIELD'
    assert len(rejection.reason_code) <= 32


def test_valid_amount_keeps_decimal_text_without_float_rounding():
    exact_amount = '9007199254740993.01'

    report = validation_module().validate_rows([row_with(amount_paid=exact_amount)])

    assert report.accepted_count == 1
    assert report.rejected_count == 0
    assert report.accepted_rows[0]['amount_paid'] == exact_amount


def test_source_accepted_and_rejected_counts_reconcile_for_a_mixed_batch():
    rows = [
        row_with(source_row_number=1),
        row_with(source_row_number=2, amount_paid='-0.01'),
        row_with(source_row_number=3, is_laundering='yes'),
        row_with(source_row_number=4, receiver_account=''),
    ]

    report = validation_module().validate_rows(rows)

    assert report.source_count == len(rows) == 4
    assert report.accepted_count == len(report.accepted_rows) == 1
    assert report.rejected_count == len(report.rejections) == 3
    assert report.accepted_count + report.rejected_count == report.source_count
    assert {item.source_row_number for item in report.accepted_rows}.isdisjoint(
        item.source_row_number for item in report.rejections
    )
    assert all(item.reason_code in EXPECTED_REASON_CODES for item in report.rejections)
    assert all(len(item.reason_code) <= 32 for item in report.rejections)
