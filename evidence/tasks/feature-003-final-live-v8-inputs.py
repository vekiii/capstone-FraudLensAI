"""Freeze fresh authored instances and separate reference/calibration material."""
import copy
import json
from datetime import datetime, timedelta

from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.models import ROOT, context_digest, digest, validate


def main():
    folder = ROOT / 'evals/investigation/development-v8'
    folder.mkdir(parents=True, exist_ok=True)
    if any(folder.iterdir()):
        raise ValueError('V8 inputs already exist; never overwrite')
    old = ROOT / 'evals/investigation/development-v4'
    templates = {i['id']: i for i in json.loads((old / 'inputs.json').read_text(encoding='utf-8'))}
    references = {i['id']: i for i in json.loads((old / 'reference.json').read_text(encoding='utf-8'))['items']}
    inputs, refs = [], []

    def later(value):
        return (datetime.fromisoformat(value.replace('Z', '+00:00')) + timedelta(days=1)).isoformat().replace('+00:00', 'Z')

    for old_number, number, amount, score in [(741, 781, '7428.16', .54),
                                             (743, 782, '63.28', .32),
                                             (742, 783, '418.63', .24)]:
        template = templates[f'DEV4-{old_number}']
        item = copy.deepcopy(template)
        item['id'] = f'DEV8-{number}'
        context = item['context']
        context['case_id'] = context['source_payload']['case_id'] = f'CASE-{number}'
        context['observed_at'] = '2026-11-16T00:00:00Z'
        payload, history = context['source_payload'], context['history']
        tx, risk = payload['transaction'], payload['risk_assessment']
        tx.update(transaction_id=f'TX-{number}', amount=amount, occurred_at=later(tx['occurred_at']),
                  sender_account=f'AUTHORED-A:DEV8-SENDER-{number}', receiver_account=f'AUTHORED-B:DEV8-RECEIVER-{number}')
        risk.update(transaction_id=tx['transaction_id'], score=score, scored_at=later(risk['scored_at']))
        for key in ('cutoff', 'start'):
            if history[key]:
                history[key] = later(history[key])
        accounts = item['history_fixture']['accounts']
        if template['context']['case_id'] in accounts:
            accounts[context['case_id']] = accounts.pop(template['context']['case_id'])
            accounts[context['case_id']]['sender']['account'] = f'DEV8-{number}'
        for index, event in enumerate(item['history_fixture']['events']):
            original_id = event['transaction_id']
            event.update(transaction_id=f'TX-{int(original_id[3:]) + 100}',
                         occurred_at=later(event['occurred_at']), account=f'DEV8-{number}')
            if index < 2:
                event['amount'] = ('162.80', '57.35')[index]
            if original_id == template['context']['source_payload']['transaction']['transaction_id']:
                event.update(transaction_id=tx['transaction_id'], amount=amount)
        context['snapshot_ref'] = 'fixture_' + digest(dict(id=item['id'], payload=payload, history=history))
        context['context_revision'] = context_digest(context)
        validate('InvestigationContext', context)
        inputs.append(input_only(item))
        ref = copy.deepcopy(references[template['id']])
        ref['id'] = item['id']
        old_tx = template['context']['source_payload']['transaction']
        old_score = template['context']['source_payload']['risk_assessment']['score']
        ref['essential_facts'] = [fact.replace(old_tx['transaction_id'], tx['transaction_id'])
            .replace(old_tx['amount'], amount).replace(str(old_score), str(score))
            .replace(old_tx['occurred_at'], tx['occurred_at'])
            .replace('145.60', '162.80').replace('42.15', '57.35') for fact in ref['essential_facts']]
        ref['history_expectation'] = ('Incomplete sender with EUR162.80/USD57.35; receiver unavailable.'
                                      if number == 781 else 'History unavailable for both sides.')
        refs.append(ref)
    calibrations = json.loads((old / 'calibrations.json').read_text(encoding='utf-8'))
    calibrations = json.loads(json.dumps(calibrations).replace('CAL4-', 'CAL8-').replace('cal_a_', 'cal6_a_')
                              .replace('cal_b_', 'cal6_b_').replace('cal_c_', 'cal6_c_')
                              .replace('CAL4_EXPECTED_ONLY_CANARY', 'CAL8_EXPECTED_ONLY_CANARY'))
    values = {'inputs.json': inputs,
        'reference.json': dict(kind='authored_template_development_not_independent_review',
                              canary='DEV8_REFERENCE_ONLY_CANARY_20261116', items=refs),
        'calibrations.json': calibrations}
    for name, value in values.items():
        (folder / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    import hashlib

    def sha(path):
        return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()

    paths = [folder / name for name in values] + [ROOT / name for name in (
        'evidence/tasks/feature-003-final-live-v8.py', 'evidence/tasks/feature-003-final-live-v8-inputs.py',
        'evidence/tasks/feature-003-coverage-v4.py', 'evidence/tasks/feature-003-timeout-v3.py',
        'evidence/tasks/feature-003-live-development-v2.py', 'prompts/application/investigation-v4.md',
        'prompts/evaluation/report-judge-v3.md',
        'data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json')]
    prior = [p for version in ('development-v2', 'development-v3', 'development-v4', 'development-v6')
             for p in (ROOT / 'evals/results/feature-003' / version).glob('*.json')]
    prior += [ROOT / name for name in ('evidence/tasks/feature-003-repair-v5-results.json',
                                      'evidence/tasks/feature-003-repair-v5-probe-results.json',
                                      'evidence/tasks/feature-003-human-authority-v7-results.json')]
    protocol = dict(protocol_version='final-live-v8-20261116', baseline_commit='1936d23',
        kind='two_ordinary_plus_controlled_candidate_fault', maximum_transport_attempts=25,
        ordinary_ids=['DEV8-781', 'DEV8-782'], diagnostic_id='DEV8-783',
        model='gpt-6-luna', reference_review='independent human review pending',
        retrieval_mode={i['id']: 'controlled_no_match' if i['id'] == 'DEV8-782' else 'candidate' for i in inputs},
        files_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in paths},
        preserved_artifacts={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in prior})
    (folder / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(new_cases=3, ordinary=2, controlled=1, calibrations=3,
                         preserved_artifacts=len(prior), actual_api_calls=0)))


if __name__ == '__main__':
    main()
