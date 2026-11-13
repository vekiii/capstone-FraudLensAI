"""Inspection of a pending mapping only; all rows/hashes below are authored fixtures."""
import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from fraudlens.data_import import inspect_source

ROOT = Path(__file__).resolve().parents[3]
MAPPING = ROOT / 'data/mappings/ibm_hi_small_v1.json'


@pytest.fixture
def bound_source(tmp_path):
    mapping = json.loads(MAPPING.read_text(encoding='utf-8'))
    mapping['source']['source_name'] = 'authored-fixture-not-IBM-evidence'
    source = tmp_path / 'HI-Small_Trans.csv'
    row = ['2026/01/01 10:00', 'SYN-A', 'PRIVATE_SENDER', 'SYN-B', 'PRIVATE_RECEIVER',
           '0.000001', 'Australian Dollar', '1.00', 'Canadian Dollar', 'Wire', '1']
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(mapping['csv']['expected_ordered_headers'])
    writer.writerow(row)
    source.write_bytes(stream.getvalue().encode())
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    mapping['source'].update(expected_sha256=digest, reference_sha256=digest,
                             expected_size_bytes=source.stat().st_size)
    path = tmp_path / 'mapping.json'
    path.write_text(json.dumps(mapping), encoding='utf-8')
    return source, path, mapping


def inspect(bound_source, **overrides):
    source, path, _ = bound_source
    return inspect_source(source=source, source_name=None, release=None, license_ref=None,
                          mapping_path=path, **overrides)


def test_bound_exact_duplicate_is_inspectable_but_never_import_ready(bound_source):
    source, path, _ = bound_source
    before = {p.name: p.read_bytes() for p in source.parent.iterdir()}
    result = inspect(bound_source)
    assert result['status'] == 'blocked'
    assert result['error_codes'] == ['pending_team_review']
    assert result['duplicate_header_groups'] == [[2, 4]]
    assert result['approved_duplicate_observation'] == [2, 4]
    assert result['row_count'] == 1
    assert result['mapping_status'] == 'pending_team_review'
    assert result['import_allowed'] is False
    assert result['mapping_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert result['time_policy']['time_basis'] == 'assumed_utc_for_synthetic_benchmark'
    assert result['time_policy']['approved_as_assumption'] is True
    assert result['source_timezone'] is None
    assert result['columns'][0]['timestamp']['timezone_counts'] == {'absent': 1}
    assert result['label_semantics']['1'] == 'synthetic laundering transaction'
    assert 'label_meaning_unreviewed' not in result['ambiguities']
    assert 'PRIVATE_' not in json.dumps(result)
    assert {p.name: p.read_bytes() for p in source.parent.iterdir()} == before


@pytest.mark.parametrize('change', ['case', 'whitespace', 'extra_target', 'missing', 'reorder'])
def test_exact_mapping_does_not_allow_header_drift(bound_source, change):
    source, path, mapping = bound_source
    content = source.read_text(encoding='utf-8')
    headers, body = content.split('\n', 1)
    if change == 'case':
        headers = headers.replace('Account', 'ACCOUNT', 1)
    elif change == 'whitespace':
        headers = headers.replace('Account', ' Account ', 1)
    elif change == 'extra_target':
        headers += ',target_copy'
    elif change == 'missing':
        headers = headers.replace(',Amount Paid', '')
    else:
        headers = headers.replace('From Bank,Account', 'Account,From Bank', 1)
    source.write_text(headers + '\n' + body, encoding='utf-8')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    mapping['source'].update(expected_sha256=digest, reference_sha256=digest,
                             expected_size_bytes=source.stat().st_size)
    path.write_text(json.dumps(mapping), encoding='utf-8')
    assert inspect(bound_source)['error_codes'] == ['mapping_header_mismatch']


def test_mapping_source_mismatch_is_nonzero_without_prefix_counts(bound_source):
    source, _, _ = bound_source
    source.write_bytes(source.read_bytes().replace(b'1.00', b'2.00'))
    result = inspect(bound_source)
    assert result['error_codes'] == ['source_mismatch']
    assert result['row_count'] is None


@pytest.mark.parametrize('change', ['import_flag', 'status', 'reference_hash', 'clock_hash'])
def test_pending_configuration_cannot_self_enable_import_or_change_binding(bound_source, change):
    _, path, mapping = bound_source
    if change == 'import_flag':
        mapping['execution_policy']['import_allowed'] = True
    elif change == 'status':
        mapping['status'] = 'approved'
    elif change == 'reference_hash':
        mapping['source']['reference_sha256'] = '0' * 64
    else:
        mapping['time']['selected_policy']['offset_minutes'] = 60
    path.write_text(json.dumps(mapping), encoding='utf-8')
    assert inspect(bound_source)['error_codes'] == ['invalid_inspection_mapping']


def test_mapping_does_not_accept_caller_source_metadata_override(bound_source):
    source, path, _ = bound_source
    result = inspect_source(source=source, source_name=None, release='wrong-release',
                            license_ref=None, mapping_path=path)
    assert result['error_codes'] == ['mapping_source_mismatch']


@pytest.mark.parametrize('change', ['missing_member', 'invalid_size', 'missing_reviews',
                                  'forged_review', 'bad_encoding', 'duplicate_key'])
def test_malformed_mapping_is_controlled_without_private_details(bound_source, change):
    _, path, mapping = bound_source
    if change == 'missing_member':
        del mapping['source']['member']
    elif change == 'invalid_size':
        mapping['source']['expected_size_bytes'] = True
    elif change == 'missing_reviews':
        mapping['required_reviews'] = {}
    elif change == 'forged_review':
        mapping['required_reviews']['frontend_api']['reviewer'] = 'PRIVATE_FAKE_REVIEWER'
    elif change == 'bad_encoding':
        path.write_bytes(b'\xffPRIVATE_INVALID')
    else:
        path.write_text('{"status":1,"status":2}', encoding='utf-8')
    if change not in {'bad_encoding', 'duplicate_key'}:
        path.write_text(json.dumps(mapping), encoding='utf-8')
    result = inspect(bound_source)
    assert result['error_codes'] == ['invalid_inspection_mapping']
    assert 'PRIVATE_' not in json.dumps(result)
    assert result['row_count'] is None


def test_source_size_binding_is_checked(bound_source):
    _, path, mapping = bound_source
    mapping['source']['expected_size_bytes'] += 1
    path.write_text(json.dumps(mapping), encoding='utf-8')
    assert inspect(bound_source)['error_codes'] == ['source_mismatch']


def test_inspection_cli_accepts_pending_mapping_but_import_remains_absent(bound_source, capsys):
    from fraudlens.pipeline_cli import main
    source, path, _ = bound_source
    assert main(['inspect', '--source', str(source), '--mapping', str(path)]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result['error_codes'] == ['pending_team_review']
    assert result['import_allowed'] is False
    assert main(['import', '--source', str(source), '--mapping', str(path)]) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['invalid_arguments']
