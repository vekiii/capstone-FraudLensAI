"""Fixture loading/validation without scoring or HTTP delivery (T014)."""
import copy
import importlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = ROOT / 'data/fixtures/cases.json'
SCHEMA = json.loads(
    (ROOT / 'specs/001-project-foundation/contracts/schemas.json').read_text(encoding='utf-8'))
RECORDS = [
    {
        'case_id': f'CASE-{number:03}',
        'transaction': {
            'transaction_id': f'TX-{number:03}', 'occurred_at': '2026-01-01T10:00:00Z',
            'sender_account': f'DEMO-BANK-A:SYN-ACCOUNT-{number:03}',
            'receiver_account': f'DEMO-BANK-B:SYN-ACCOUNT-{number + 3:03}',
            'amount': '1250.00', 'currency': 'EUR',
        },
    }
    for number in [1, 2, 3]
]


def case_module():
    spec = importlib.util.find_spec('fraudlens.cases')
    assert spec is not None, 'Missing fixture loading/validation behavior (T014)'
    module = importlib.import_module('fraudlens.cases')
    assert callable(getattr(module, 'load_cases', None)), 'Missing load_cases boundary'
    return module


def write_cases(tmp_path, payload):
    path = tmp_path / 'cases.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    return path


def assert_rejected(module, path):
    with pytest.raises(module.FixtureLoadError) as caught:
        module.load_cases(path)
    assert str(caught.value) == 'Unable to load synthetic cases.'
    assert str(path) not in str(caught.value)
    assert 'PRIVATE_' not in repr(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__ is True


def test_shipped_three_records_follow_canonical_fields_and_synthetic_policy():
    module = case_module()
    raw = json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))
    # The storage projection uses existing case_id/transaction fields; scoring
    # is absent. Reuse the independent canonical ID/transaction schema pieces.
    storage_schema = {
        **SCHEMA, 'type': 'array', 'minItems': 3, 'maxItems': 3,
        'items': {
            'type': 'object', 'additionalProperties': False,
            'properties': {
                'case_id': SCHEMA['$defs']['CaseSummary']['properties']['case_id'],
                'transaction': {'$ref': '#/$defs/Transaction'},
            },
            'required': ['case_id', 'transaction'],
        },
    }
    Draft202012Validator(storage_schema, format_checker=FormatChecker()).validate(raw)
    assert [item['case_id'] for item in raw] == ['CASE-001', 'CASE-002', 'CASE-003']
    assert len({item['transaction']['transaction_id'] for item in raw}) == 3
    for item in raw:
        for field in ['sender_account', 'receiver_account']:
            assert item['transaction'][field].startswith('DEMO-BANK-')
            assert ':SYN-ACCOUNT-' in item['transaction'][field]
        assert item['transaction']['currency'] == 'EUR'
    assert [item.model_dump(mode='json') for item in module.load_cases()] == raw


def test_loader_uses_repository_default_path_even_from_another_directory(monkeypatch, tmp_path):
    module = case_module()
    monkeypatch.chdir(tmp_path)
    assert [case.case_id for case in module.load_cases()] == ['CASE-001', 'CASE-002', 'CASE-003']


def test_unsorted_input_is_returned_in_case_order_without_rewriting_file(tmp_path):
    module = case_module()
    path = write_cases(tmp_path, [RECORDS[2], RECORDS[0], RECORDS[1]])
    before = path.read_bytes()
    first = [case.model_dump(mode='json') for case in module.load_cases(path)]
    second = [case.model_dump(mode='json') for case in module.load_cases(path)]
    assert first == second == RECORDS
    assert path.read_bytes() == before


def test_repeated_reads_do_not_share_mutable_records(tmp_path):
    module = case_module()
    path = write_cases(tmp_path, RECORDS)
    first = module.load_cases(path)
    first[0].transaction.amount = '0.00'
    first.pop()
    assert [case.model_dump(mode='json') for case in module.load_cases(path)] == RECORDS


def test_empty_collection_is_valid_for_the_empty_state_contract(tmp_path):
    module = case_module()
    assert module.load_cases(write_cases(tmp_path, [])) == []


@pytest.mark.parametrize('identity', ['case_id', 'transaction_id'])
def test_duplicate_identifiers_are_rejected(tmp_path, identity):
    module = case_module()
    records = copy.deepcopy(RECORDS)
    if identity == 'case_id':
        records[2]['case_id'] = records[0]['case_id']
    else:
        records[2]['transaction']['transaction_id'] = records[0]['transaction']['transaction_id']
    assert_rejected(module, write_cases(tmp_path, records))


@pytest.mark.parametrize('payload', [None, {}, {'items': RECORDS}, 'PRIVATE_BAD_ROOT', 1, True])
def test_collection_must_be_a_json_array(tmp_path, payload):
    module = case_module()
    assert_rejected(module, write_cases(tmp_path, payload))


@pytest.mark.parametrize('record', [None, [], 'PRIVATE_BAD_RECORD', 1])
def test_each_record_must_be_an_object(tmp_path, record):
    module = case_module()
    assert_rejected(module, write_cases(tmp_path, [record]))


MISSING = [('case_id',), ('transaction',)] + [
    ('transaction', field) for field in RECORDS[0]['transaction']
]


@pytest.mark.parametrize('path', MISSING)
def test_missing_required_attributes_are_rejected(tmp_path, path):
    module = case_module()
    records = copy.deepcopy(RECORDS)
    record = records[-1]
    if len(path) == 1:
        del record[path[0]]
    else:
        del record[path[0]][path[1]]
    assert_rejected(module, write_cases(tmp_path, records))


INVALID = [
    (('case_id',), 'CASE-1'), (('case_id',), 'CASE-001\n'), (('case_id',), 1),
    (('transaction',), None), (('transaction', 'transaction_id'), 'TX-01'),
    (('transaction', 'transaction_id'), 'TX-001\n'),
    (('transaction', 'sender_account'), ''),
    (('transaction', 'receiver_account'), 'a' * 121),
    (('transaction', 'amount'), 1250.0), (('transaction', 'amount'), '-1.00'),
    (('transaction', 'amount'), '01.00'), (('transaction', 'amount'), '1.0'),
    (('transaction', 'currency'), 'eur'), (('transaction', 'currency'), 'EUR\n'),
    (('transaction', 'occurred_at'), '2026-02-30T10:00:00Z'),
    (('transaction', 'occurred_at'), '2026-01-01T10:00:00+00:00'),
]


@pytest.mark.parametrize('path,value', INVALID)
def test_malformed_attributes_are_rejected(tmp_path, path, value):
    module = case_module()
    records = copy.deepcopy(RECORDS)
    if len(path) == 1:
        records[-1][path[0]] = value
    else:
        records[-1][path[0]][path[1]] = value
    assert_rejected(module, write_cases(tmp_path, records))


@pytest.mark.parametrize('level', ['case', 'transaction'])
@pytest.mark.parametrize('field', [
    'unexpected', 'is_fraud', 'fraud_label', 'confirmed_fraud', 'risk_assessment',
    'score', 'model_accuracy', 'training_claim', 'evaluation_metrics',
])
def test_closed_records_exclude_labels_scoring_and_ml_claim_fields(tmp_path, level, field):
    module = case_module()
    records = copy.deepcopy(RECORDS)
    target = records[-1] if level == 'case' else records[-1]['transaction']
    target[field] = 'PRIVATE_REJECTED_VALUE'
    assert_rejected(module, write_cases(tmp_path, records))


@pytest.mark.parametrize('raw', ['', '{broken', '[NaN]', '[{"case_id":"CASE-001"'])
def test_malformed_json_is_a_controlled_load_error(tmp_path, raw):
    module = case_module()
    path = tmp_path / 'PRIVATE_INVALID_JSON.json'
    path.write_text(raw, encoding='utf-8')
    assert_rejected(module, path)


def test_duplicate_json_member_names_are_not_silently_overwritten(tmp_path):
    module = case_module()
    raw = json.dumps([RECORDS[0]]).replace(
        '"case_id": "CASE-001"', '"case_id": "CASE-999", "case_id": "CASE-001"')
    path = tmp_path / 'duplicate-members.json'
    path.write_text(raw, encoding='utf-8')
    assert_rejected(module, path)


@pytest.mark.parametrize('failure', ['missing', 'directory', 'invalid_utf8', 'permission'])
def test_file_failures_never_disclose_paths_or_internal_messages(tmp_path, monkeypatch, failure):
    module = case_module()
    path = tmp_path / 'PRIVATE_FIXTURE.json'
    if failure == 'directory':
        path.mkdir()
    elif failure == 'invalid_utf8':
        path.write_bytes(b'\xff\xfe\xfa')
    elif failure == 'permission':
        def forbidden(*args, **kwargs):
            raise PermissionError('PRIVATE_PERMISSION_DETAIL: C:\\private\\fixtures.json')
        monkeypatch.setattr(Path, 'read_text', forbidden)
    assert_rejected(module, path)
