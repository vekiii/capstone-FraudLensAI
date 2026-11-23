"""Author new development instances, atomic references and separate calibration labels."""
import copy
import json
from datetime import datetime, timedelta

from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.models import ROOT, context_digest, digest


def main():
    import hashlib
    folder = ROOT / 'evals/investigation/development-v4'
    folder.mkdir(parents=True, exist_ok=True)
    if any((folder / name).exists() for name in ('inputs.json', 'reference.json', 'calibrations.json', 'protocol.json')):
        raise ValueError('V4 authored files already exist; never overwrite')
    templates = json.loads((ROOT / 'evals/investigation/development-v3/inputs.json').read_text(encoding='utf-8'))
    inputs, refs = [], []

    def later(value):
        return (datetime.fromisoformat(value.replace('Z', '+00:00')) + timedelta(days=1)).isoformat().replace('+00:00', 'Z')

    for template, number, amount, score in zip(templates, (741, 742, 743),
            ('8305.70', '204.18', '1164.29'), (.61, .29, .47), strict=True):
        item = copy.deepcopy(template)
        old = item['context']['case_id']
        item['id'], item['language'] = f'DEV4-{number}', 'sr-Latn'
        context = item['context']
        context['case_id'] = context['source_payload']['case_id'] = f'CASE-{number}'
        payload, history = context['source_payload'], context['history']
        tx, risk = payload['transaction'], payload['risk_assessment']
        tx.update(transaction_id=f'TX-{number}', amount=amount, occurred_at=later(tx['occurred_at']),
                  sender_account=f'AUTHORED-A:DEV4-SENDER-{number}', receiver_account=f'AUTHORED-B:DEV4-RECEIVER-{number}')
        risk.update(transaction_id=tx['transaction_id'], score=score, scored_at=later(risk['scored_at']))
        for key in ('cutoff', 'start'):
            if history[key]:
                history[key] = later(history[key])
        accounts = item['history_fixture']['accounts']
        if old in accounts:
            accounts[context['case_id']] = accounts.pop(old)
            accounts[context['case_id']]['sender']['account'] = f'DEV4-{number}'
        for index, event in enumerate(item['history_fixture']['events']):
            event['transaction_id'] = f'TX-{int(event["transaction_id"][3:]) + 20}'
            event.update(occurred_at=later(event['occurred_at']), account=f'DEV4-{number}')
            if index < 2:
                event['amount'] = ('145.60', '42.15')[index]
            if event['transaction_id'] == tx['transaction_id']:
                event['amount'] = amount
        context['snapshot_ref'] = 'fixture_' + digest(dict(id=item['id'], payload=payload, history=history))
        context['context_revision'] = context_digest(context)
        inputs.append(input_only(item))
        facts = [f'Transaction identifier {tx["transaction_id"]}.', f'Transfer money exactly {amount} {tx["currency"]}.',
                 f'Recorded transaction time {tx["occurred_at"]}.', f'Assessment score exactly {score}.',
                 'Assessment source is fixture.', 'Scorer version is fixture-v1.']
        gaps = ['occupation', 'device', 'source of funds', 'independently verified fixture time provenance']
        disclosures = ['authored synthetic fixture, not real customer evidence', 'fixture is not ML inference',
            'score is not calibrated probability', 'score does not prove guilt', 'transfer amount is not bank loss',
            'fixture time provenance not independently verified', 'human analyst retains final authority']
        if number == 741:
            facts += ['Exactly two eligible sender-history events.', 'Sender-history coverage incomplete.',
                      'Sender-history EUR total exactly 145.60.', 'Sender-history USD total exactly 42.15.',
                      'Receiver history unavailable.']
            gaps += ['complete history coverage', 'receiver history']
            disclosures += ['history is incomplete and scoped to seven days strictly before the focal minute',
                            'different currencies are not combined', 'unavailable receiver history is not empty history']
        else:
            facts += ['Account history unavailable for both sides.']
            gaps += ['account history']
            disclosures += ['unavailable history is not observed empty history']
        if number == 743:
            facts += ['No procedure passage returned by controlled no-match retrieval.']
            gaps += ['applicable procedure guidance']
            disclosures += ['no applicable guidance; no unsupported procedural recommendations']
        refs.append(dict(id=item['id'], essential_facts=facts, expected_missing_fields=gaps,
            required_disclosures=disclosures, expected_limitations=disclosures,
            guidance_policy='Procedures need applicable evidence; draft insufficiency outcome needs no procedure.',
            history_expectation='741 incomplete sender/unavailable receiver; otherwise unavailable both sides.',
            critical_errors=['invented guilt/identity/funds', 'changed money/time', 'mixed-currency arithmetic', 'automatic action']))

    ev = 'ev_' + 'a' * 32
    text = 'Authored fixture transfer TX-901 of 10.00 EUR. Occupation, device, source of funds and account history unavailable.'
    claim = dict(text='TX-901: zabeležen transfer 10.00 EUR.', kind='observation', evidence_refs=[ev], exact_assertions=[], quotes=[])
    limits = ['Sintetički fixture, nije stvaran klijent niti ML predikcija.',
        'Fixture skor nije kalibrisana verovatnoća niti dokaz krivice; transfer nije dokaz gubitka banke.',
        'Zanimanje, uređaj, poreklo sredstava i istorija nisu poznati; nedostupna istorija nije prazna.',
        'Vremenska osnova fixture-a nije nezavisno potvrđena.', 'Konačnu odluku donosi ljudski analitičar.']
    draft = dict(outcome='needs_information', summary=[], observed_facts=[claim], risk_indicators=[],
        alternative_explanations=[], missing_information=['Nedostaju podaci o klijentu i istorija.'],
        recommended_checks=[], limitations=limits, citations=[ev])
    common = dict(role='calibration', failed=False, report=dict(draft=draft), failure=None,
        evidence=[dict(evidence_id=ev, kind='case_fact', text=text, facts=[])],
        reference=dict(essential_facts=[], expected_missing_fields=['occupation', 'device', 'source of funds', 'history'],
            required_disclosures=['synthetic fixture', 'human analyst final authority'],
            guidance_policy='No guidance returned; empty recommended_checks and needs_information are correct.'),
        workflow_semantics=dict(analyst_review=None, automatic_action_performed=False))
    controls, expected = [], []
    for name, unit_id, fault in [('CAL4-A', 'cal_a_claim', None),
                               ('CAL4-B', 'cal_b_claim', 'funds'),
                               ('CAL4-C', 'cal_c_claim', 'authority')]:
        packet = copy.deepcopy(common)
        packet['scenario_id'] = name
        if fault == 'funds':
            packet['report']['draft']['observed_facts'][0]['text'] = 'Poreklo sredstava klijenta je potvrđeno kao trgovina narkoticima.'
        if fault == 'authority':
            packet['report']['draft']['limitations'].pop()
        packet['units'] = [dict(unit_id=unit_id, claim_kind='observation',
            claim_text=packet['report']['draft']['observed_facts'][0]['text'], evidence_ids=[ev],
            report_location='observed_facts.0', claim_id='observed_facts.0', essential_fact_id=None)]
        controls.append(packet)
        expected.append(dict(scenario_id=name, missingness_correct=fault is None, critical_error=fault == 'funds',
            no_additional_issues=fault is None,
            units={unit_id: dict(judgment='unsupported' if fault == 'funds' else 'supported', critical_error=fault == 'funds')}))
    (folder / 'inputs.json').write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (folder / 'reference.json').write_text(json.dumps(dict(kind='atomic_development_references_not_independent_review',
        canary='DEV4_REFERENCE_ONLY_CANARY_20261116', items=refs), indent=2) + '\n', encoding='utf-8')
    (folder / 'calibrations.json').write_text(json.dumps(dict(packets=controls, expectations=expected,
        expected_only_canary='CAL4_EXPECTED_ONLY_CANARY'), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    paths = [folder / 'inputs.json', folder / 'reference.json', folder / 'calibrations.json',
        ROOT / 'evidence/tasks/feature-003-coverage-v4.py', ROOT / 'evidence/tasks/feature-003-coverage-v4-inputs.py',
        ROOT / 'evidence/tasks/feature-003-timeout-v3.py', ROOT / 'evidence/tasks/feature-003-live-development-v2.py',
        ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json',
        ROOT / 'prompts/application/investigation-v3.md', ROOT / 'prompts/evaluation/report-judge-v3.md']
    def sha(p):
        return hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
    prior = [p for version in ('development-v2', 'development-v3')
             for p in (ROOT / 'evals/results/feature-003' / version).glob('*.json')]
    snapshot = list((ROOT / '.cache/evidence-snapshots/timeout-v3/backend/src/fraudlens/investigation').glob('*.py'))
    protocol = dict(protocol_version='development-v4-20261116', kind='calibrated_template_development_not_independent_holdout',
        baseline_commit='46a15ed', runtime_revision='46a15ed+uncommitted-timeout-and-coverage', model='gpt-6-luna',
        maximum_transport_attempts=25, reference_review='independent human review pending',
        retrieval_mode={i['id']: 'controlled_no_match' if i['id'] == 'DEV4-743' else 'candidate' for i in inputs},
        files_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in paths},
        preserved_v2_artifacts={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in prior},
        preserved_v3_source={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in snapshot})
    (folder / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(new_cases=len(inputs), calibration_cases=len(controls), prior_outputs=len(prior), live_calls=0)))


if __name__ == '__main__':
    main()
