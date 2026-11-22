"""Synthetic source-header mapping contracts for Feature 002 (T202)."""

import hashlib
import importlib

import pytest

EXPECTED_HEADER = [
    'Timestamp',
    'From Bank',
    'Account',
    'To Bank',
    'Account',
    'Amount Received',
    'Receiving Currency',
    'Amount Paid',
    'Payment Currency',
    'Payment Format',
    'Is Laundering',
]

SYNTHETIC_ROW = [
    '2022-09-01 00:00:00',
    '0007',
    '000012345',
    '0012',
    '000000007',
    '10.00',
    'EUR',
    '10.00',
    'EUR',
    'Wire',
    '0',
]


def source_module():
    """Load the Feature 002 mapper when implemented by T204."""
    try:
        module = importlib.import_module('fraudlens.data.source')
    except ModuleNotFoundError as error:
        if error.name not in {'fraudlens.data', 'fraudlens.data.source'}:
            raise
        pytest.fail('Missing Feature 002 source schema mapper (T204)', pytrace=False)
    assert callable(getattr(module, 'map_ibm_header', None)), 'Missing verified header mapper'
    assert callable(getattr(module, 'map_transaction_row', None)), 'Missing exact-text row mapper'
    return module


def test_duplicate_account_headers_map_sender_and_receiver_by_position():
    module = source_module()

    columns = module.map_ibm_header(EXPECTED_HEADER)
    mapped = module.map_transaction_row(columns, SYNTHETIC_ROW)

    assert columns == {
        'timestamp': 0,
        'sender_bank': 1,
        'sender_account': 2,
        'receiver_bank': 3,
        'receiver_account': 4,
        'amount_received': 5,
        'receiving_currency': 6,
        'amount_paid': 7,
        'payment_currency': 8,
        'payment_format': 9,
        'is_laundering': 10,
    }
    assert mapped['sender_bank'] == '0007'
    assert mapped['sender_account'] == '000012345'
    assert mapped['receiver_bank'] == '0012'
    assert mapped['receiver_account'] == '000000007'
    assert mapped['sender_account'] != mapped['receiver_account']


@pytest.mark.parametrize(
    'header',
    [
        # A bank column moved while duplicate Account names remain present.
        [
            'Timestamp', 'To Bank', 'Account', 'From Bank', 'Account',
            'Amount Received', 'Receiving Currency', 'Amount Paid',
            'Payment Currency', 'Payment Format', 'Is Laundering',
        ],
        # Missing duplicate field, renamed field, or unrecognized extra field.
        EXPECTED_HEADER[:4] + EXPECTED_HEADER[5:],
        EXPECTED_HEADER[:5] + ['Amount Received (renamed)', *EXPECTED_HEADER[6:]],
        [*EXPECTED_HEADER, 'Unexpected Field'],
    ],
    ids=['changed-order', 'missing-account', 'renamed-field', 'extra-field'],
)
def test_changed_or_malformed_header_is_rejected(header):
    module = source_module()

    with pytest.raises(ValueError):
        module.map_ibm_header(header)


def test_header_with_only_one_account_occurrence_is_rejected():
    module = source_module()

    with pytest.raises(ValueError):
        module.map_ibm_header(['Timestamp', 'From Bank', 'Account', 'To Bank'])


def test_source_hash_and_row_identity_are_stable_for_exact_source_bytes(tmp_path):
    module = source_module()
    source_bytes = (','.join(EXPECTED_HEADER) + '\n' + ','.join(SYNTHETIC_ROW) + '\n').encode()
    path = tmp_path / 'synthetic.csv'
    path.write_bytes(source_bytes)

    expected_hash = hashlib.sha256(source_bytes).hexdigest()
    assert module.sha256_file(path) == expected_hash
    assert module.stable_transaction_id(expected_hash, 1) == (
        f'ibm-hi-small:{expected_hash}:row:1'
    )
    assert module.stable_transaction_id(expected_hash, 1) != (
        module.stable_transaction_id(expected_hash, 2)
    )


def test_source_row_parser_keeps_text_and_source_order_without_label_coercion(tmp_path):
    module = source_module()
    source_bytes = (','.join(EXPECTED_HEADER) + '\n' + ','.join(SYNTHETIC_ROW) + '\n').encode()
    path = tmp_path / 'synthetic.csv'
    path.write_bytes(source_bytes)

    rows = list(module.iter_source_rows(path))

    assert len(rows) == 1
    assert rows[0]['source_row_number'] == 1
    assert rows[0]['transaction_id'] == module.stable_transaction_id(
        hashlib.sha256(source_bytes).hexdigest(), 1
    )
    assert rows[0]['timestamp'] == '2022-09-01 00:00:00'
    assert rows[0]['sender_bank'] == '0007'
    assert rows[0]['sender_account'] == '000012345'
    assert rows[0]['receiver_bank'] == '0012'
    assert rows[0]['receiver_account'] == '000000007'
    assert rows[0]['amount_received'] == '10.00'
    assert rows[0]['amount_paid'] == '10.00'
    assert rows[0]['is_laundering'] == '0'


def test_source_row_parser_rejects_wrong_column_count(tmp_path):
    module = source_module()
    path = tmp_path / 'malformed.csv'
    path.write_text(','.join(EXPECTED_HEADER) + '\nTimestamp,bank\n', encoding='utf-8')

    with pytest.raises(ValueError, match='column count'):
        list(module.iter_source_rows(path))
