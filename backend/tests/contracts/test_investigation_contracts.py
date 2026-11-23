"""Independent schema and semantic contract tests; no remote ref retrieval."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from fraudlens.investigation.models import validate

ROOT = Path(__file__).resolve().parents[3]
EX = ROOT / 'specs/003-ai-investigation/contracts/examples'
EXAMPLES = {
    'context-fixture': 'InvestigationContext', 'context-dataset': 'InvestigationContext',
    'create-request': 'CreateRequest', 'error-stale-snapshot': 'ErrorEnvelope',
    'evidence-fixture': 'Evidence', 'needs-information-draft': 'ReportDraft',
    'report-ready': 'Report', 'run-ready': 'RunView',
}


def example(name):
    return json.loads((EX / (name + '.json')).read_text())


@pytest.mark.parametrize('file,name', EXAMPLES.items())
def test_authored_examples(file, name):
    assert validate(name, example(file)) == example(file)


@pytest.mark.parametrize('file,name', EXAMPLES.items())
def test_closed_required_fields_recursively(file, name):
    original = example(file)
    def objects(value, path=()):
        if isinstance(value, dict):
            yield path, value
            for key, item in value.items():
                yield from objects(item, (*path, key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from objects(item, (*path, index))
    for path, obj in objects(original):
        for key in [*obj, 'isFraud', 'reference_answer', 'unknown']:
            payload = copy.deepcopy(original)
            target = payload
            for part in path:
                target = target[part]
            if key in obj:
                del target[key]
            else:
                target[key] = 'private'
            with pytest.raises(ValueError):
                validate(name, payload)


@pytest.mark.parametrize('kind', ['Digest', 'RunId', 'AttemptId', 'EvidenceId', 'ReviewId'])
def test_opaque_ids(kind):
    prefixes = {'Digest': '', 'RunId': 'inv_', 'AttemptId': 'att_',
                'EvidenceId': 'ev_', 'ReviewId': 'rev_'}
    good = prefixes[kind] + 'a' * (64 if kind == 'Digest' else 32)
    assert validate(kind, good) == good
    for bad in [good + '\n', '../path', 1, True, good.upper()]:
        with pytest.raises(ValueError):
            validate(kind, bad)


@pytest.mark.parametrize('value', ['2026-02-30T00:00:00Z', '2026-01-01T00:00:00',
                                  '2026-01-01T00:00:00+00:00', 1])
def test_invalid_instants(value):
    with pytest.raises(ValueError):
        validate('Instant', value)


@pytest.mark.parametrize('value', ['', ' ', 'x' * 501, 1, True])
def test_query_bounds(value):
    with pytest.raises(ValueError):
        validate('SearchArguments', {'query': value})


def test_trimmed_query():
    assert validate('SearchArguments', {'query': ' test '}) == {'query': 'test'}
    assert validate('SearchArguments', {'query': 'x' * 500})['query'] == 'x' * 500


@pytest.mark.parametrize('field', ['case_id', 'snapshot_ref', 'dataset_version', 'context_revision'])
@pytest.mark.parametrize('file', ['context-fixture', 'context-dataset'])
def test_context_binding(file, field):
    ctx = example(file)
    ctx[field] = 'changed'
    with pytest.raises(ValueError):
        validate('InvestigationContext', ctx)


@pytest.mark.parametrize('value', [float('nan'), float('inf'), float('-inf'), True, '0.7', -1, 2])
def test_score_strict(value):
    ctx = example('context-fixture')
    ctx['source_payload']['risk_assessment']['score'] = value
    with pytest.raises(ValueError):
        validate('InvestigationContext', ctx)


@pytest.mark.parametrize('field,value', [('contract_version', 2), ('contract_version', True),
                                        ('history', {}), ('dataset_version', 'dv_' + 'a' * 64)])
def test_fixture_metadata(field, value):
    ctx = example('context-fixture')
    ctx[field] = value
    with pytest.raises(ValueError):
        validate('InvestigationContext', ctx)


@pytest.mark.parametrize('field', ['summary', 'observed_facts', 'risk_indicators',
                                 'alternative_explanations', 'recommended_checks'])
def test_report_section_limit(field):
    draft = example('report-ready')['draft']
    draft[field] = [draft['summary'][0]] * 21
    with pytest.raises(ValueError):
        validate('ReportDraft', draft)


def test_provider_draft_has_no_authority():
    draft = example('needs-information-draft')
    for field in ['attempt_id', 'permissions', 'state', 'review']:
        with pytest.raises(ValueError):
            validate('ReportDraft', {**draft, field: 'invented'})


def test_producer_hash_normalized_lf():
    raw = (ROOT / 'specs/003-ai-investigation/contracts/producer-v2.snapshot.json').read_bytes()
    assert hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() == (
        'bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88')

@pytest.mark.parametrize('path', [
    ('case_id',), ('source_payload', 'risk_assessment', 'transaction_id'),
    ('source_payload', 'snapshot_ref'), ('source_payload', 'dataset_version'),
    ('source_payload', 'risk_assessment', 'run_id'),
])
def test_valid_shaped_identity_mismatch(path):
    from fraudlens.investigation.models import context_digest
    ctx = example('context-dataset')
    target = ctx
    for key in path[:-1]:
        target = target[key]
    value = target[path[-1]]
    target[path[-1]] = value[:-1] + ('b' if value[-1] != 'b' else 'a')
    ctx['context_revision'] = context_digest(ctx)
    with pytest.raises(ValueError):
        validate('InvestigationContext', ctx)


@pytest.mark.parametrize('field,value', [('actor', ''), ('actor', 'x' * 81),
                                      ('rationale', ' '), ('rationale', 'x' * 2001)])
def test_review_text_bounds(field, value):
    review = dict(review_id='rev_' + 'a' * 32, report_id='a' * 64, actor='analyst',
                  disposition='close', rationale='Checked', correction_note=None,
                  supersedes_review_id=None, created_at='2026-01-01T00:00:00Z')
    review[field] = value
    with pytest.raises(ValueError):
        validate('Review', review)


def test_models_revalidate_untrusted_constructed_or_mutated_instances():
    from fraudlens.investigation.models import InvestigationContext
    payload = example('context-fixture')
    model = InvestigationContext.model_validate(payload)
    assert model.model_dump(mode='json') == payload
    model.source_payload['transaction']['amount'] = 1.5
    with pytest.raises(ValueError):
        InvestigationContext.model_validate(model)
    forged = InvestigationContext.model_construct(**payload)
    forged.__dict__['unexpected'] = True
    with pytest.raises(ValueError):
        InvestigationContext.model_validate(forged)


def test_json_schema_format_checker_actually_checks_calendar():
    from jsonschema import Draft202012Validator, FormatChecker

    from fraudlens.investigation.models import REGISTRY, SCHEMA
    validator = Draft202012Validator({**SCHEMA, '$ref': '#/$defs/Instant'},
                                     registry=REGISTRY, format_checker=FormatChecker())
    assert not validator.is_valid('2026-02-30T00:00:00Z')
    assert validator.is_valid('2026-01-01T00:00:00Z')

@pytest.mark.parametrize('operation', ['remove_cutoff', 'coverage_unavailable'])
def test_available_history_cannot_hide_coverage(operation):
    from fraudlens.investigation.models import context_digest
    ctx = example('context-fixture')
    ctx['history'].update(availability='available', cutoff='2026-01-05T09:15:00Z',
                          coverage='full', start='2025-12-29T09:15:00Z')
    if operation == 'remove_cutoff':
        ctx['history']['cutoff'] = None
    else:
        ctx['history']['coverage'] = 'unavailable'
    ctx['context_revision'] = context_digest(ctx)
    with pytest.raises(ValueError):
        validate('InvestigationContext', ctx)
