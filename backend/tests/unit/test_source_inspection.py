"""Authored source-shaped inputs, never observations of an IBM release (T004)."""
import csv
import hashlib
import importlib
import importlib.util
import io
import json
from pathlib import Path

import pytest

ROLES = ('timestamp', 'sender_bank', 'sender_account', 'receiver_bank', 'receiver_account',
         'paid_amount', 'paid_currency', 'received_amount', 'received_currency', 'label')
HEADERS = list(ROLES)
ROW = ['2026/01/01 10:00', 'bank-a', 'PRIVATE_ACCOUNT_A', 'bank-b', 'PRIVATE_ACCOUNT_B',
       '0.000', 'Test Coin', '123.4500', 'EUR', '1']
COLUMNS = dict(zip(ROLES, range(len(ROLES))))


def inspector():
    # Missing behavior must fail here, in a collected test body, during RED.
    assert importlib.util.find_spec('fraudlens.data_import') is not None, \
        'Missing read-only source inspection (T005)'
    module = importlib.import_module('fraudlens.data_import')
    assert callable(getattr(module, 'inspect_source', None)), 'Missing inspect_source'
    return module.inspect_source


def write_csv(path, headers=HEADERS, rows=None):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(headers)
    writer.writerows([ROW] if rows is None else rows)
    path.write_bytes(stream.getvalue().encode('utf-8'))
    return path


def inspect(path, **changes):
    options = dict(source=path, source_name='authored-test-only', release='fixture-v1',
                   license_ref='authored-test-only', columns=COLUMNS)
    return inspector()(**(options | changes))


@pytest.fixture
def source(tmp_path):
    return write_csv(tmp_path / 'source.csv')


@pytest.fixture(autouse=True)
def no_writes_or_activation(tmp_path):
    marker = tmp_path / 'active.json'
    marker.write_text('{"active":"old-complete-run"}', encoding='utf-8')
    yield
    assert marker.read_text(encoding='utf-8') == '{"active":"old-complete-run"}'
    assert sorted(p.name for p in tmp_path.iterdir()) in [
        ['active.json'], ['active.json', 'source.csv']]


def test_complete_read_only_report_preserves_exact_forms_and_private_boundary(source):
    before = source.read_bytes()
    report = inspect(source, expected_sha256=hashlib.sha256(before).hexdigest())
    assert report['status'] == 'inspected'
    assert report['error_codes'] == []
    assert report['sha256'] == hashlib.sha256(before).hexdigest()
    assert report['size_bytes'] == len(before)
    assert report['headers'] == HEADERS
    assert report['encoding'] == 'utf-8'
    assert report['dialect']['delimiter'] == ','
    assert report['row_count'] == 1
    assert report['complete_parse'] is True
    assert report['columns'][5]['amount']['minimum'] == '0.000'
    assert report['columns'][7]['amount']['maximum'] == '123.4500'
    assert report['columns'][6]['value_counts'] == {'Test Coin': 1}
    assert report['columns'][9]['label_counts'] == {'0': 0, '1': 1, 'missing': 0, 'other': 0}
    assert report['columns'][0]['timestamp']['resolution_counts'] == {'minute': 1}
    assert report['columns'][0]['timestamp']['timezone_counts'] == {'absent': 1}
    assert report['columns'][0]['timestamp']['lexical_form_counts'] == {'9999/99/99 99:99': 1}
    assert report['columns'][5]['amount']['sign_counts'] == {'none': 1}
    assert report['columns'][5]['amount']['leading_zero_count'] == 0
    assert report['ambiguities'] == ['mapping_unreviewed', 'timezone_absent',
                                      'label_meaning_unreviewed']
    assert report['mapping_status'] == 'unreviewed_inspection_only'
    assert 'PRIVATE_ACCOUNT' not in json.dumps(report)
    assert source.read_bytes() == before


@pytest.mark.parametrize('pair', [
    ('sender_account', 'sender_account'), ('sender_account', ' Sender_Account '),
    ('sender_account', '\ufeffsender_account'), ('sender_account', 'SENDER_ACCOUNT'),
])
def test_duplicate_headers_are_exact_controlled_failures(source, pair):
    headers = HEADERS.copy()
    headers[2], headers[4] = pair
    write_csv(source, headers)
    before = source.read_bytes()
    result = inspect(source)
    assert result['status'] == 'blocked'
    assert result['error_codes'] == ['duplicate_headers']
    assert result['duplicate_header_groups'] == [[2, 4]]
    assert result['row_count'] == 1  # Preserve ordinal observations, never a dict overwrite.
    assert source.read_bytes() == before


@pytest.mark.parametrize('extra', ['isFraud', 'target_copy', 'LaBeL_encoded',
                                  'Is Laundering', 'reference_decision'])
def test_extra_target_like_headers_cannot_become_inputs(source, extra):
    write_csv(source, HEADERS + [extra], [ROW + ['PRIVATE_TARGET']])
    result = inspect(source)
    assert result['status'] == 'blocked'
    assert result['error_codes'] == ['target_like_columns', 'unknown_columns']
    assert result['target_like_columns'] == [10]
    assert 'PRIVATE_TARGET' not in json.dumps(result)


def test_unknown_column_requires_review(source):
    write_csv(source, HEADERS + ['unreviewed'], [ROW + ['PRIVATE_UNKNOWN']])
    result = inspect(source)
    assert result['error_codes'] == ['unknown_columns']
    assert result['unknown_columns'] == [10]
    assert 'PRIVATE_UNKNOWN' not in json.dumps(result)


def test_missing_required_role_is_not_inferred(source):
    result = inspect(source, columns={k: v for k, v in COLUMNS.items() if k != 'paid_currency'})
    assert result['error_codes'] == ['missing_roles', 'unknown_columns']
    assert result['missing_roles'] == ['paid_currency']


def test_missing_header_alias_is_controlled(source):
    aliases = {role: [role] for role in ROLES}
    aliases['paid_currency'] = ['absent header']
    result = inspect(source, columns=None, aliases=aliases)
    assert result['error_codes'] == ['missing_roles', 'unknown_columns']
    assert result['missing_roles'] == ['paid_currency']


def test_ambiguous_aliases_do_not_pick_a_winner(source):
    aliases = {role: [role] for role in ROLES}
    aliases['sender_account'] = ['sender_account', 'receiver_account']
    result = inspect(source, columns=None, aliases=aliases)
    assert result['error_codes'] == ['ambiguous_aliases', 'missing_roles', 'unknown_columns']


@pytest.mark.parametrize('body,encoding,code', [
    (b'bad\xffbytes', 'utf-8', 'invalid_encoding'),
    ('x,y\n1,2'.encode('utf-16'), 'utf-16', 'unsupported_encoding'),
    (b'x\x00,y\n1,2', 'utf-8', 'invalid_encoding'),
    (b'', 'utf-8', 'empty_source'),
    (b'x,y\n', 'utf-8', 'header_only'),
    (b'x,y\n"unfinished', 'utf-8', 'malformed_csv'),
    (b'x,y\n1,2\n"unfinished', 'utf-8', 'malformed_csv'),
    (b'x,y\n1,2,3\n', 'utf-8', 'record_width_mismatch'),
])
def test_structural_failures_never_publish_partial_totals(source, body, encoding, code):
    source.write_bytes(body)
    result = inspect(source, columns=None, encoding=encoding)
    assert result['status'] == 'failed'
    assert result['error_codes'] == [code]
    assert result['row_count'] is None
    assert result['complete_parse'] is False
    assert result['columns'] == []
    assert source.read_bytes() == body


def test_missing_or_directory_source_is_controlled(tmp_path):
    for path in [tmp_path / 'source.csv', tmp_path]:
        result = inspect(path)
        assert result['error_codes'] == ['source_unavailable']
        assert str(tmp_path) not in json.dumps(result)


def test_unreadable_source_is_controlled(source, monkeypatch):
    def denied(*args, **kwargs):
        raise PermissionError('PRIVATE_PATH')
    monkeypatch.setattr(Path, 'open', denied)
    assert inspect(source)['error_codes'] == ['source_unavailable']


def test_source_hash_mismatch_fails_before_reporting_observations(source):
    result = inspect(source, expected_sha256='0' * 64)
    assert result['error_codes'] == ['source_mismatch']
    assert result['row_count'] is None
    assert result['columns'] == []


def test_changed_source_during_scan_is_a_mismatch(source, monkeypatch):
    module = importlib.import_module(inspector().__module__)
    real_summary = module._summarize

    def changed(*args, **kwargs):
        result = real_summary(*args, **kwargs)
        source.write_bytes(source.read_bytes().replace(b'123.4500', b'223.4500'))
        return result

    monkeypatch.setattr(module, '_summarize', changed)
    result = inspect(source)
    assert result['error_codes'] == ['source_mismatch']
    assert result['row_count'] is None


def test_multiline_records_bom_and_explicit_semicolon_dialect(source):
    row = ROW.copy()
    row[2] = 'PRIVATE\nACCOUNT'
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=';')
    writer.writerow(HEADERS)
    writer.writerows([row, ROW])
    source.write_bytes(b'\xef\xbb\xbf' + stream.getvalue().encode())
    result = inspect(source, delimiter=';')
    assert result['status'] == 'inspected'
    assert result['bom'] is True
    assert result['row_count'] == 2
    assert result['dialect']['delimiter'] == ';'
    assert result['columns'][2]['min_length'] == len(row[2])
    assert result['columns'][2]['max_length'] == len(ROW[2])


def test_missing_provenance_does_not_claim_an_identified_release(source):
    result = inspect(source, release=None, license_ref=None)
    assert result['error_codes'] == ['provenance_incomplete']
    assert result['provenance']['release'] is None


def test_bounded_categories_and_invalid_labels_are_aggregate_only(source):
    rows = []
    for i in range(100):
        row = ROW.copy()
        row[6], row[9] = f'currency-{i}', 'PRIVATE_LABEL'
        rows.append(row)
    write_csv(source, rows=rows)
    result = inspect(source)
    assert result['columns'][9]['label_counts']['other'] == 100
    assert 'PRIVATE_LABEL' not in json.dumps(result)
    currency = result['columns'][6]
    assert len(currency['value_counts']) == 64
    assert currency['unlisted_values_count'] == 36


def test_summaries_keep_nanosecond_text_and_separate_timezone_evidence(source):
    first, second = ROW.copy(), ROW.copy()
    first[0] = '2026-01-01T10:00:00.123456789Z'
    second[0] = '2026-01-01T10:00:00+01:00'
    write_csv(source, rows=[first, second])
    stats = inspect(source)['columns'][0]['timestamp']
    assert stats['resolution_counts'] == {'fraction_9': 1, 'second': 1}
    assert stats['timezone_counts'] == {'Z': 1, '+01:00': 1}
    assert stats['wall_time_ranges']['Z'] == ['2026-01-01T10:00:00.123456789'] * 2


def test_invalid_forms_are_counted_without_canonical_coercion(source):
    rows = []
    for amount in ['-1.00', '1e3', 'NaN', '', '0.000000', '1234567890123.123456789']:
        row = ROW.copy()
        row[0], row[5], row[9] = '2026-02-30T10:00:00Z', amount, ''
        rows.append(row)
    write_csv(source, rows=rows)
    result = inspect(source)
    assert result['row_count'] == 6
    assert result['columns'][0]['timestamp']['invalid_count'] == 6
    assert result['columns'][5]['missing'] == 1
    assert result['columns'][5]['amount'] == {
        'plain_count': 3, 'non_plain_count': 2, 'negative_count': 1, 'zero_count': 1,
        'minimum': '-1.00', 'maximum': '1234567890123.123456789',
        'scale_counts': {'2': 1, '6': 1, '9': 1}, 'max_integer_digits': 13,
        'sign_counts': {'minus': 1, 'none': 2}, 'leading_zero_count': 0}
    assert result['columns'][9]['label_counts'] == {'0': 0, '1': 0, 'missing': 6, 'other': 0}


@pytest.mark.parametrize('changes', [
    {'columns': COLUMNS | {'paid_currency': 100}},
    {'columns': COLUMNS | {'unreviewed_role': 0}},
    {'expected_sha256': 'not-a-hash'}, {'delimiter': '::'},
])
def test_invalid_inspection_options_fail_closed(source, changes):
    assert inspect(source, **changes)['error_codes'] == ['invalid_inspection_options']


def test_only_inspect_cli_exists_and_errors_are_nonzero_sanitized(source, capsys):
    inspector()
    cli = importlib.import_module('fraudlens.pipeline_cli')
    args = ['inspect', '--source', str(source), '--source-name', 'authored-test-only',
            '--release', 'fixture-v1', '--license-ref', 'authored-test-only']
    for role, index in COLUMNS.items():
        args.extend(['--column', f'{role}={index}'])
    assert cli.main(args) == 0
    out = capsys.readouterr()
    assert json.loads(out.out)['row_count'] == 1
    assert 'inspected' in out.err
    assert cli.main(args + ['--expected-sha256', '0' * 64]) == 2
    out = capsys.readouterr()
    assert json.loads(out.out)['error_codes'] == ['source_mismatch']
    assert 'PRIVATE_' not in out.out + out.err
    assert str(source) not in out.out + out.err
    assert cli.main(['import', '--source', 'PRIVATE_PATH']) == 2
    out = capsys.readouterr()
    assert 'PRIVATE_PATH' not in out.out + out.err
