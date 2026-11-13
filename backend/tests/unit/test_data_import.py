"""T009 RED: authored source-shaped records; no IBM import is performed."""
import csv
import io
from decimal import Decimal

import pytest

from fraudlens import data_import

HEADERS = ['Timestamp', 'From Bank', 'Account', 'To Bank', 'Account',
           'Amount Received', 'Receiving Currency', 'Amount Paid',
           'Payment Currency', 'Payment Format', 'Is Laundering']
BASE = ['2026/01/01 10:00', 'BANK_A', '0007', 'BANK_B', '0007',
        '0.000001', 'Euro', '10.20', 'Euro', 'Wire', '']


def source_bytes(*rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(HEADERS)
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def parse_authored(raw):
    parser = getattr(data_import, 'parse_canonical_source', None)
    assert callable(parser), 'T013 missing: streaming canonical parser and row accounting'
    return parser(raw, namespace='ibm-v8-test', member='HI-Small_Trans.csv')


def test_direction_exact_money_time_and_missing_private_label():
    result = parse_authored(source_bytes(BASE))
    assert result.report.source_records == 1
    assert result.report.event_valid == 1
    assert result.report.label_ineligible == 1
    event = result.events[0]
    assert (event.sender_bank, event.sender_account) == ('BANK_A', '0007')
    assert (event.receiver_bank, event.receiver_account) == ('BANK_B', '0007')
    assert (Decimal(event.paid_amount), event.paid_currency) == (Decimal('10.20'), 'Euro')
    assert (Decimal(event.received_amount), event.received_currency) == (Decimal('0.000001'), 'Euro')
    assert event.event_time_raw == '2026/01/01 10:00'
    assert event.event_time_utc.isoformat() == '2026-01-01T10:00:00+00:00'
    assert 'label' not in vars(event)


@pytest.mark.parametrize('column,value', [
    (6, 'EUR'), (5, '0.0000001'), (7, '-1.00'), (7, '1e999'),
    (7, '10000000000000.00'), (8, ''), (0, '2026/01/01 10:00+01:00'),
])
def test_unsupported_observable_fact_is_rejected_and_counted(column, value):
    row = BASE.copy()
    row[column] = value
    result = parse_authored(source_bytes(row))
    assert result.report.source_records == 1
    assert result.report.event_rejected == 1
    assert result.events == []


def test_invalid_label_keeps_valid_observable_event():
    row = BASE.copy()
    row[-1] = 'unknown'
    result = parse_authored(source_bytes(row))
    assert result.report.event_valid == 1
    assert result.report.label_ineligible == 1
    assert len(result.events) == 1


def test_quoted_multiline_is_one_record_and_rejected_row_is_accounted():
    malformed = BASE.copy()
    malformed[7] = '-1.00'
    multiline = BASE.copy()
    multiline[2] = '0007\nALT'
    result = parse_authored(source_bytes(malformed, multiline))
    assert result.report.source_records == 2
    assert result.report.event_rejected == 1
    assert result.report.event_valid == 1
    assert result.events[0].source_ordinal == 2


def test_truncated_utf8_cannot_publish_complete_report():
    result = parse_authored(source_bytes(BASE) + b'\xff')
    assert result.status == 'failed'
    assert result.report.complete_parse is False


@pytest.mark.parametrize('paid,received', [
    ('0', '0.000000'), ('1.2', '3.000001'),
    ('9999999999999.999999', '0.01'),
])
def test_supported_money_boundaries_preserve_lexical_scale(paid, received):
    row = BASE.copy()
    row[5], row[7] = received, paid
    result = parse_authored(source_bytes(row))
    assert result.report.event_valid == 1
    assert result.events[0].paid_amount == paid
    assert result.events[0].received_amount == received
    assert result.events[0].paid_currency == result.events[0].received_currency == 'Euro'


@pytest.mark.parametrize('field,value', [
    (5, 'NaN'), (7, 'Infinity'), (7, '+1.00'), (7, '01.00'),
    (5, ''), (6, ''), (7, '1.0000000'), (7, '10000000000000'),
    (0, ''), (0, '2026/02/30 10:00'), (0, '2026/01/01 10:00:01'),
    (1, '   '), (2, ''),
])
def test_invalid_amount_clock_or_party_rejects_event_without_rounding(field, value):
    row = BASE.copy()
    row[field] = value
    result = parse_authored(source_bytes(row))
    assert (result.report.source_records, result.report.event_rejected) == (1, 1)
    assert not result.events


@pytest.mark.parametrize('label,status,value', [
    ('0', 'eligible_negative', 0), ('1', 'eligible_positive', 1),
    ('', 'missing', None),
])
def test_private_label_status_is_separate_from_operational_event(label, status, value):
    row = BASE.copy()
    row[-1] = label
    result = parse_authored(source_bytes(row))
    assert result.report.source_records == result.report.event_valid == 1
    assert result.report.event_rejected == 0
    assert result.private_labels[0].status == status
    assert result.private_labels[0].value == value
    assert len(result.events) == 1
    assert not {'label', 'label_status', 'eligibility', 'target'} & vars(result.events[0]).keys()


@pytest.mark.parametrize('label', ['unknown', '2'])
def test_nonbinary_label_is_ineligible_but_event_facts_remain(label):
    row = BASE.copy()
    row[-1] = label
    result = parse_authored(source_bytes(row))
    assert result.report.event_valid == result.report.label_ineligible == 1
    assert result.private_labels[0].status in {'invalid', 'unsupported'}
    assert result.private_labels[0].value is None
    assert len(result.events) == 1


def test_accounting_reconciles_every_record_and_unknown_fields_never_become_predictors():
    valid = BASE.copy()
    positive = BASE.copy()
    positive[-1] = '1'
    invalid_label = BASE.copy()
    invalid_label[-1] = 'not-a-label'
    rejected = BASE.copy()
    rejected[7] = '-1.00'
    result = parse_authored(source_bytes(valid, positive, invalid_label, rejected))
    report = result.report
    assert report.source_records == report.event_valid + report.event_rejected == 4
    assert report.event_valid == report.label_eligible + report.label_ineligible == 3
    assert report.label_eligible == report.positives + report.negatives == 1
    assert len(result.events) == 3
    assert all('Is Laundering' not in vars(event) for event in result.events)
    assert all('source_ordinal' not in event.predictor_fields for event in result.events)


@pytest.mark.parametrize('raw', [
    b'',
    ','.join(HEADERS).encode() + b'\n',
    b'\xef\xbb\xbf' + source_bytes(BASE),
    source_bytes(BASE).replace(b'From Bank', b'from bank', 1),
    source_bytes(BASE).replace(b'From Bank', b'From Bank,From Bank', 1),
    source_bytes(BASE).replace(b'From Bank', b' From Bank ', 1),
    source_bytes(BASE).replace(b'From Bank', b'FROM BANK', 1),
    source_bytes(BASE).replace(b'Amount Paid', b'AmountPaid', 1),
    source_bytes(BASE).replace(b'Is Laundering', b'Is Laundering,target_copy', 1),
    source_bytes(BASE).replace(b'From Bank,Account', b'Account,From Bank', 1),
    source_bytes(BASE) + b'\xff',
    source_bytes(BASE) + b'\x00',
    source_bytes(BASE).decode().encode('utf-16'),
    source_bytes(BASE) + b'"unfinished',
    source_bytes(BASE) + b'extra,columns\n',
])
def test_structural_or_encoding_error_cannot_publish_partial_import(raw):
    result = parse_authored(raw)
    assert result.status == 'failed'
    assert result.report.complete_parse is False
    assert result.report.source_records is None
    assert not result.events


def test_malformed_quoted_record_after_valid_rows_invalidates_whole_attempt():
    raw = source_bytes(BASE, BASE, BASE) + b'"unterminated'
    result = parse_authored(raw)
    assert result.status == 'failed'
    assert result.report.complete_parse is False
    assert result.report.source_records is None
    assert not result.events


def test_wrong_width_after_valid_rows_invalidates_whole_attempt():
    raw = source_bytes(BASE, BASE) + b'one,two\n'
    result = parse_authored(raw)
    assert result.status == 'failed'
    assert result.report.complete_parse is False
    assert result.report.source_records is None
    assert not result.events


def test_each_row_has_prefilter_reference_and_one_event_status():
    valid = BASE.copy()
    rejected = BASE.copy()
    rejected[7] = '-1.00'
    missing_label = BASE.copy()
    missing_label[-1] = ''
    result = parse_authored(source_bytes(valid, rejected, missing_label))
    assert [(row.source_ordinal, row.event_status) for row in result.rows] == [
        (1, 'event_valid'), (2, 'event_rejected'), (3, 'event_valid')]
    assert result.rows[1].rejection_reason
    assert result.rows[0].private_label_status == 'missing'
    assert result.rows[1].private_label_status is None
    assert result.rows[2].private_label_status == 'missing'


def test_missing_payment_format_is_null_and_exact_long_currency_is_preserved():
    row = BASE.copy()
    row[6] = 'Australian Dollar'
    row[8] = 'Canadian Dollar'
    row[9] = ''
    result = parse_authored(source_bytes(row))
    assert result.report.event_valid == 1
    event = result.events[0]
    assert event.received_currency == 'Australian Dollar'
    assert event.paid_currency == 'Canadian Dollar'
    assert event.payment_format is None
    assert event.time_basis == 'assumed_utc_for_synthetic_benchmark'
    assert event.event_time_epoch_ns == 1767261600000000000


def test_unknown_payment_format_rejects_row_pending_mapping_revision():
    row = BASE.copy()
    row[9] = 'Unknown Format'
    result = parse_authored(source_bytes(row))
    assert result.report.event_rejected == 1
    assert not result.events
