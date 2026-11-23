"""Frozen model bridge contract: identity and fail-closed negative cases."""
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from fraudlens.bridge import identity, validate_binding

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/model-case-binding-v1.json').read_text())
SCHEMA = json.loads((ROOT / 'specs/003-ai-investigation/contracts/model-case-bridge-v1.json').read_text())


def test_example_and_deterministic_distinct_ids():
    Draft202012Validator({**SCHEMA, '$ref': '#/$defs/Binding'}, format_checker=FormatChecker()).validate(EXAMPLE)
    assert identity(EXAMPLE['canonical_transaction_id'], 'case') == (EXAMPLE['case_id'], EXAMPLE['case_digest'])
    assert identity(EXAMPLE['canonical_transaction_id'], 'tx') == (EXAMPLE['transaction_id'], EXAMPLE['transaction_digest'])
    assert EXAMPLE['case_id'] != EXAMPLE['transaction_id']
    validate_binding(EXAMPLE)


@pytest.mark.parametrize('field,value', [
    ('case_id', 'C' + '0' * 32), ('transaction_id', 'D' + '0' * 32),
    ('case_digest', '0' * 64), ('source_sha256', '0' * 64),
    ('model_sha256', '0' * 64), ('feature_manifest_sha256', '0' * 64),
    ('feature_version', 'wrong-v1'), ('threshold', 0.9),
    ('risk_score', 0.1), ('snapshot_ref', 'run_other'),
    ('event_time_utc', '2022-09-07T12:00:00Z'),
])
def test_reject_identity_provenance_or_alert_mismatch(field, value):
    changed = copy.deepcopy(EXAMPLE)
    changed[field] = value
    with pytest.raises(ValueError):
        validate_binding(changed, expected_run=EXAMPLE['snapshot_ref'],
                         expected_score=EXAMPLE['risk_score'],
                         expected_event_time=EXAMPLE['event_time_utc'])


def test_reject_label_or_fixture_fields():
    for key in ('is_laundering', 'fixture_case_id'):
        changed = copy.deepcopy(EXAMPLE)
        changed[key] = 1
        with pytest.raises(ValueError):
            validate_binding(changed)


def test_reject_below_threshold():
    changed = copy.deepcopy(EXAMPLE)
    changed['risk_score'] = 0.1
    with pytest.raises(ValueError):
        validate_binding(changed)
