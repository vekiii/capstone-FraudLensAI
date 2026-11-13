"""Technical schema changes only; no API/decoder or v2 runtime integration."""
import json
import re
import textwrap
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]


def schema():
    return json.loads((ROOT / 'specs/002-data-and-risk-scoring/contracts/schemas.json').read_text())


def valid(name, payload):
    source = schema()
    return Draft202012Validator({'$schema': source['$schema'], '$defs': source['$defs'],
                                 '$ref': '#/$defs/' + name},
                                format_checker=FormatChecker()).is_valid(payload)


@pytest.mark.parametrize('currency', ['Australian Dollar', 'Canadian Dollar'])
def test_v2_preserves_observed_currency_name_lengths(currency):
    assert valid('Money', {'amount': '0.000001', 'currency': currency})
    assert not valid('Money', {'amount': '1.00', 'currency': 'x' * 18})


@pytest.mark.parametrize('name,value', [('TransactionId', 'D' + 'a' * 32),
                                      ('CaseId', 'C' + 'a' * 32), ('RunId', 'run_example'),
                                      ('DatasetVersionId', 'dv_example')])
def test_v2_identifiers_have_exact_terminal_matching(name, value):
    assert valid(name, value)
    assert not valid(name, value + '\n')


def test_v2_money_has_exact_terminal_matching():
    assert valid('Money', {'amount': '1.000001', 'currency': 'Euro'})
    assert not valid('Money', {'amount': '1.00\n', 'currency': 'Euro'})


def test_detail_version_is_required_and_assumed_clock_is_explicit():
    definitions = schema()['$defs']
    assert 'dataset_version' in definitions['CaseDetailV2']['required']
    assert definitions['CaseDetailV2']['properties']['dataset_version'] == {
        '$ref': '#/$defs/DatasetVersionId'}
    assert 'dataset_version' not in definitions['TransactionV2']['properties']
    assert 'assumed_utc_for_synthetic_benchmark' in definitions['TransactionV2'][
        'properties']['time_basis']['enum']


def test_published_examples_match_schema_and_agree_on_snapshot_versions():
    api = (ROOT / 'specs/002-data-and-risk-scoring/contracts/api.md').read_text(encoding='utf-8')
    examples = []
    for block in re.findall(r'(?:^    .*\n?)+', api, re.M):
        content = textwrap.dedent(block)
        start = content.find('{')
        if start >= 0:
            try:
                examples.append(json.JSONDecoder().raw_decode(content[start:])[0])
            except ValueError:
                pass
    listing = next(example for example in examples if 'items' in example)
    detail = next(example for example in examples if 'risk_assessment' in example)
    validator = Draft202012Validator(schema(), format_checker=FormatChecker())
    validator.validate(listing)
    validator.validate(detail)
    assert detail['dataset_version'] == listing['dataset_version'] == detail[
        'risk_assessment']['dataset_version']
    assert detail['snapshot_ref'] == listing['snapshot_ref'] == detail['risk_assessment']['run_id']
    assert detail['transaction']['time_basis'] == 'assumed_utc_for_synthetic_benchmark'
    missing = {k: v for k, v in detail.items() if k != 'dataset_version'}
    assert not validator.is_valid(missing)
    # Honest limitation: future backend/decoder semantic checks must enforce equality.
    assert validator.is_valid({**detail, 'dataset_version': 'dv_wrong'})
