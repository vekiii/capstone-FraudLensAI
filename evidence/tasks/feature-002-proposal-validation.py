"""Offline review probes; apply draft JSON Patch in memory, never to contracts."""
import copy
import hashlib
import json
import re
import textwrap
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
FEATURE = ROOT / 'specs/002-data-and-risk-scoring'


def apply_patch(document, operations):
    result = copy.deepcopy(document)
    for operation in operations:
        parts = [part.replace('~1', '/').replace('~0', '~')
                 for part in operation['path'].split('/')[1:]]
        parent = result
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        key = parts[-1]
        if operation['op'] == 'test':
            actual = parent[int(key)] if isinstance(parent, list) else parent[key]
            assert actual == operation['value'], operation['path']
        elif operation['op'] == 'add' and isinstance(parent, list) and key == '-':
            parent.append(copy.deepcopy(operation['value']))
        elif operation['op'] in {'add', 'replace'} and isinstance(parent, dict):
            if operation['op'] == 'replace':
                assert key in parent
            parent[key] = copy.deepcopy(operation['value'])
        else:
            raise ValueError('Unsupported proposal operation')
    return result


def main():
    proposal_path = FEATURE / 'proposals/v2-contract-changes.json'
    mapping_path = FEATURE / 'proposals/source-mapping.json'
    proposal = json.loads(proposal_path.read_text(encoding='utf-8'))
    mapping = json.loads(mapping_path.read_text(encoding='utf-8'))
    # Preserve proposal preconditions against exact historical input bytes after amendment.
    historical = json.loads((FEATURE / 'proposals/technical-amendment-baseline.json').read_text())
    inputs = {name: text.encode('utf-8') for name, text in historical['sources'].items()}
    for name, hash_key in [('schemas.json', 'base_schema_sha256'), ('api.md', 'base_api_sha256'),
                           ('data-and-scoring.md', 'base_offline_contract_sha256')]:
        assert hashlib.sha256(inputs[name]).hexdigest() == proposal[hash_key], name
    base = json.loads(inputs['schemas.json'])
    candidate = apply_patch(base, proposal['core_schema_patch_rfc6902'])
    optional = apply_patch(candidate,
                          proposal['optional_schema_patch_only_if_time_convention_approved_rfc6902'])
    for schema in [base, candidate, optional]:
        Draft202012Validator.check_schema(schema)

    def valid(schema, name, value):
        # Keep definitions for local references, but do not retain the root response oneOf.
        return Draft202012Validator({'$schema': schema['$schema'], '$defs': schema['$defs'],
                                     '$ref': '#/$defs/' + name},
                                    format_checker=FormatChecker()).is_valid(value)

    for currency in mapping['money_policy_proposed']['source_currency_allowlist']:
        assert valid(candidate, 'Money', {'amount': '0.000001', 'currency': currency})
    assert not valid(base, 'Money', {'amount': '0.000001', 'currency': 'Australian Dollar'})
    for currency in ['', 'x' * 18, None, 1]:
        assert not valid(candidate, 'Money', {'amount': '1.00', 'currency': currency})
    for name, value in [('TransactionId', 'D' + 'a' * 32), ('CaseId', 'C' + 'a' * 32),
                        ('RunId', 'run_example'), ('DatasetVersionId', 'dv_example')]:
        assert valid(base, name, value) and valid(candidate, name, value)
        assert valid(base, name, value + '\n')
        assert not valid(candidate, name, value + '\n')
    assert valid(base, 'Money', {'amount': '1.00\n', 'currency': 'Euro'})
    assert not valid(candidate, 'Money', {'amount': '1.00\n', 'currency': 'Euro'})
    assert valid(candidate, 'Instant', '2022-09-01T00:00:00.123456789Z')
    assert not valid(candidate, 'Instant', '2022-09-01T00:00:00Z\n')
    examples = []
    for block in re.findall(r'(?:^    .*\n?)+', inputs['api.md'].decode('utf-8'), re.M):
        content = textwrap.dedent(block)
        start = content.find('{')
        if start >= 0:
            try:
                examples.append(json.JSONDecoder().raw_decode(content[start:])[0])
            except ValueError:
                pass
    detail = next(example for example in examples if 'risk_assessment' in example)
    assert valid(base, 'CaseDetailV2', detail)
    assert not valid(candidate, 'CaseDetailV2', detail)  # New envelope field is required.
    detail = {**detail, 'dataset_version': detail['risk_assessment']['dataset_version']}
    assert valid(candidate, 'CaseDetailV2', detail)
    for value in [None, '', 'wrong_version', 1]:
        assert not valid(candidate, 'CaseDetailV2', {**detail, 'dataset_version': value})
    assert not valid(candidate, 'CaseDetailV2', {**detail, 'Is Laundering': 1})
    mismatch = {**detail, 'dataset_version': 'dv_different'}
    assert valid(candidate, 'CaseDetailV2', mismatch)  # Equality needs future semantic validators.
    assumed = copy.deepcopy(detail)
    assumed['transaction']['time_basis'] = 'assumed_utc_for_synthetic_benchmark'
    assert not valid(candidate, 'CaseDetailV2', assumed)
    assert valid(optional, 'CaseDetailV2', assumed)
    assert mapping['source']['verified_local_release'] is None
    assert mapping['source']['namespace'] is None
    assert mapping['time']['selected_policy'] is None
    assert mapping['identity_proposed']['approved_mapping_sha256'] is None
    for draft in [mapping, proposal]:
        assert all(value is None for value in draft['review'].values())
    assert [column['index'] for column in mapping['columns']] == list(range(11))
    assert [column['header'] for column in mapping['columns']] == mapping['csv']['expected_ordered_headers']
    assert mapping['columns'][2]['role'] == 'sender_account'
    assert mapping['columns'][4]['role'] == 'receiver_account'
    applied = json.loads((FEATURE / 'contracts/schemas.json').read_text())
    assert applied['$defs'] == optional['$defs']
    assert applied['oneOf'] == optional['oneOf']
    current_mapping = json.loads((ROOT / 'data/mappings/ibm_hi_small_v1.json').read_text())
    assert current_mapping['status'] == 'pending_team_review'
    assert current_mapping['execution_policy']['import_allowed'] is False
    assert current_mapping['source']['verified_local_release'] == 8
    assert current_mapping['time']['selected_policy']['approved_as_assumption'] is True
    for entry in current_mapping['required_reviews'].values():
        assert entry == {'status': 'pending', 'reviewer': None, 'date': None, 'decision': None}
    result = {
        'status': 'passed_applied_technical_contract_checks_not_runtime_acceptance',
        'technical_mapping_sha256': hashlib.sha256(
            (ROOT / 'data/mappings/ibm_hi_small_v1.json').read_bytes()).hexdigest(),
        'applied_schema_sha256': hashlib.sha256(
            (FEATURE / 'contracts/schemas.json').read_bytes()).hexdigest(),
        'mapping_proposal_sha256': hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
        'v2_proposal_sha256': hashlib.sha256(proposal_path.read_bytes()).hexdigest(),
        'candidate_core_schema_canonical_sha256': hashlib.sha256(
            json.dumps(candidate, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        'candidate_with_optional_time_schema_canonical_sha256': hashlib.sha256(
            json.dumps(optional, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        'checks': ['base hashes and patch preconditions', 'three schemas well formed',
                   '15 source currency tokens fit', 'currency boundary negatives',
                   'properly isolated definition probes; ID/money terminal-newline negatives',
                   'required detail version negatives', 'closed label-free envelope',
                   'explicit optional assumed-time basis', 'mapping positions and pending gates',
                   'applied schema equals approved proposal definitions; team/import gates pending'],
        'schema_only_version_mismatch_still_accepted': True,
        'runtime_backend_frontend_semantic_validators': 'not implemented; pending consumer review',
    }
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
