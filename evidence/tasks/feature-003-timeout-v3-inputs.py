"""New instances of development templates; no old reference/output content read."""
import copy
import hashlib
import json
from datetime import datetime, timedelta

from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.models import ROOT, context_digest, digest


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def main():
    folder = ROOT / 'evals/investigation/development-v3'
    folder.mkdir(parents=True, exist_ok=True)
    if any((folder / name).exists() for name in ('inputs.json', 'reference.json', 'protocol.json')):
        raise ValueError('Development-v3 files already exist; never overwrite')
    templates = json.loads((ROOT / 'evals/investigation/development-v2/inputs.json').read_text(encoding='utf-8'))
    inputs, refs = [], []

    def later(value):
        return (datetime.fromisoformat(value.replace('Z', '+00:00')) + timedelta(days=2)).isoformat().replace('+00:00', 'Z')

    for template, number, amount, score in zip(templates, (721, 722, 723),
            ('7050.80', '158.42', '940.17'), (.58, .27, .49), strict=True):
        item = copy.deepcopy(template)
        old = item['context']['case_id']
        item['id'], item['language'] = f'DEV3-{number}', 'sr-Latn'
        context = item['context']
        context['case_id'] = context['source_payload']['case_id'] = f'CASE-{number}'
        payload, history = context['source_payload'], context['history']
        tx, risk = payload['transaction'], payload['risk_assessment']
        tx.update(transaction_id=f'TX-{number}', amount=amount, occurred_at=later(tx['occurred_at']),
                  sender_account=f'AUTHORED-A:DEV3-SENDER-{number}', receiver_account=f'AUTHORED-B:DEV3-RECEIVER-{number}')
        risk.update(transaction_id=tx['transaction_id'], score=score, scored_at=later(risk['scored_at']))
        for name in ('cutoff', 'start'):
            if history[name]:
                history[name] = later(history[name])
        accounts = item['history_fixture']['accounts']
        if old in accounts:
            accounts[context['case_id']] = accounts.pop(old)
            accounts[context['case_id']]['sender']['account'] = f'DEV3-{number}'
        for index, event in enumerate(item['history_fixture']['events']):
            event['transaction_id'] = f'TX-{int(event["transaction_id"][3:]) + 20}'
            event.update(occurred_at=later(event['occurred_at']), account=f'DEV3-{number}')
            if index < 2:
                event['amount'] = ('210.20', '31.05')[index]
            if event['transaction_id'] == tx['transaction_id']:
                event['amount'] = amount
        context['snapshot_ref'] = 'fixture_' + digest(dict(id=item['id'], payload=payload, history=history))
        context['context_revision'] = context_digest(context)
        inputs.append(input_only(item))
        facts = [f'Focal transfer {tx["transaction_id"]} is exactly {amount} {tx["currency"]}; not bank loss.',
            f'Recorded focal time {tx["occurred_at"]}; independently verified fixture time-basis provenance is unavailable.',
            f'Score {score} is an authored fixture illustration, not ML inference, guilt or calibrated probability.',
            'Occupation, device and source of funds are unavailable; no invented customer identity or explanation.']
        gaps = ['occupation', 'device', 'source of funds', 'independently verified fixture time provenance']
        if number == 721:
            facts += ['Sender history is available but INCOMPLETE: two eligible events before the focal minute in the seven-day window.',
                      'Separate history totals EUR 210.20 and USD 31.05; never combine currencies.',
                      'Receiver history unavailable is not evidence of no prior activity.']
            gaps += ['full history coverage', 'receiver history']
        else:
            facts += ['Account history is unavailable, not observed empty history or zero prior activity.']
            gaps += ['account history']
        if number == 723:
            facts += ['Controlled retrieval returns no procedure passage; no unsupported procedural recommendation.']
            gaps += ['applicable procedural guidance']
        refs.append(dict(id=item['id'], essential_facts=facts, expected_missing_fields=gaps,
            expected_limitations=['authored synthetic fixture, not actual customer/model evidence', 'human analyst final authority'],
            guidance_policy='Only actual applicable procedure evidence supports procedural recommendations; 723 controlled no-match.',
            history_expectation='Incomplete sender/unavailable receiver on721; unavailable both sides otherwise.',
            critical_errors=['invented guilt/identity/funds', 'changed exact money/time', 'mixed-currency arithmetic', 'automatic intervention']))
    (folder / 'inputs.json').write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (folder / 'reference.json').write_text(json.dumps(dict(kind='authored_template_development_not_independent_holdout',
        canary='DEV3_REFERENCE_ONLY_CANARY_20261116', items=refs), indent=2) + '\n', encoding='utf-8')
    paths = [folder / 'inputs.json', folder / 'reference.json',
        ROOT / 'evidence/tasks/feature-003-timeout-v3.py', ROOT / 'evidence/tasks/feature-003-timeout-v3-inputs.py',
        ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json',
        ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json',
        ROOT / 'prompts/application/investigation-v2.md', ROOT / 'prompts/evaluation/report-judge-v2.md']
    old_artifacts = list((ROOT / 'evals/results/feature-003/development-v2').glob('*.json'))
    protocol = dict(protocol_version='development-v3-20261116', kind='development_template_instances_not_independent_holdout',
        baseline_commit='46a15ed', runtime_revision='46a15ed+uncommitted-timeout-v3', model='gpt-6-luna',
        maximum_transport_attempts=25, reference_review='independent human review pending',
        retrieval_mode={item['id']: 'controlled_no_match' if item['id'] == 'DEV3-723' else 'candidate' for item in inputs},
        files_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in paths},
        preserved_v2_artifacts={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in old_artifacts})
    (folder / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(new_template_instances=len(inputs), preserved_v2_files=len(old_artifacts), live_calls=0)))


if __name__ == '__main__':
    main()
