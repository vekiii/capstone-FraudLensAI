"""Author deterministic NEW synthetic development inputs, never old holdout data."""
import copy
import json

from fraudlens.investigation.context import CaseContextReader
from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.models import ROOT, context_digest, digest, validate


def main():
    folder = ROOT / 'evals/investigation/development-v2'
    folder.mkdir(parents=True, exist_ok=True)
    if any((folder / name).exists() for name in ('inputs.json', 'reference.json', 'protocol.json')):
        raise ValueError('Authored files already exist; no replacement permitted')
    base = CaseContextReader().resolve('CASE-001', 'fixture', None)
    inputs, references = [], []
    for index, amount, currency, score in [(701, '4210.35', 'EUR', .64),
                                         (702, '67.89', 'GBP', .23), (703, '812.06', 'USD', .51)]:
        identity = f'DEV2-{index}'
        context = copy.deepcopy(base)
        context.update(case_id=f'CASE-{index}', observed_at='2026-11-15T00:00:00Z')
        payload = context['source_payload']
        payload['case_id'] = context['case_id']
        tx = payload['transaction']
        tx.update(transaction_id=f'TX-{index}', occurred_at='2026-11-10T10:30:45Z',
            amount=amount, currency=currency, sender_account=f'AUTHORED-A:DEV-SENDER-{index}',
            receiver_account=f'AUTHORED-B:DEV-RECEIVER-{index}')
        payload['risk_assessment'].update(transaction_id=tx['transaction_id'], score=score,
            scored_at='2026-11-10T10:31:00Z',
            explanation='Authored fixture illustration; not ML inference or calibrated probability.')
        context['snapshot_ref'] = 'fixture_' + digest(dict(id=identity, payload=payload))
        events, accounts = [], {}
        if index == 701:
            context['history'] = dict(availability='available', coverage='incomplete',
                cutoff=tx['occurred_at'], start='2026-11-03T10:30:45Z', lookback_days=7,
                view_scope='authored_fixture', reason='Authored incomplete sender history; receiver not supplied.')
            accounts = {context['case_id']: dict(sender=dict(bank='DEV-BANK-A', account='DEV-701'))}
            entries = [('TX-711', '2026-11-08T09:00:00Z', '320.10', 'EUR'),
                       ('TX-712', '2026-11-09T12:00:00Z', '75.20', 'USD'),
                       ('TX-713', '2026-11-10T10:30:05Z', '999.99', 'EUR'),
                       ('TX-714', '2026-11-11T09:00:00Z', '888.88', 'USD'),
                       ('TX-701', '2026-11-10T10:30:45Z', '4210.35', 'EUR')]
            events = [dict(transaction_id=t, occurred_at=at, amount=a, currency=c,
                           bank='DEV-BANK-A', account='DEV-701') for t, at, a, c in entries]
        context['context_revision'] = context_digest(context)
        validate('InvestigationContext', context)
        item = dict(id=identity, language='sr-Cyrl' if index == 702 else 'sr-Latn',
            instruction='Napiši kratak izveštaj na srpskom koristeći samo dostupne činjenice i dozvoljene alate. Proveri istoriju obe strane i primenljive procedure. Ne donosi odluku umesto analitičara.',
            context=context, history_fixture=dict(accounts=accounts, events=events),
            procedure_queries=['nedostaje dokaz', 'pregled dokumentacija'])
        inputs.append(input_only(item))
        facts = [f'Focal transfer {tx["transaction_id"]} is exactly {amount} {currency}; not bank loss.',
            'Recorded focal time is 2026-11-10T10:30:45Z; no independently verified fixture time-basis provenance.',
            f'Score {score} is an authored fixture illustration, not ML inference, guilt or calibrated probability.',
            'Occupation, device and source of funds are unavailable; no invented customer identity or explanation.']
        gaps = ['occupation', 'device', 'source of funds', 'independently verified fixture time provenance']
        if index == 701:
            facts += ['Sender history is available but INCOMPLETE: two eligible events before the focal minute in the seven-day window.',
                'Separate sender-history totals are EUR 320.10 and USD 75.20; currencies cannot be combined.',
                'Receiver history is unavailable; that is not proof of no receiver activity.']
            gaps += ['full history coverage', 'receiver history']
            history = 'Sender incomplete, receiver unavailable. Same-minute/future/focal events are not eligible evidence.'
        else:
            facts += ['Account history is unavailable, not an observed empty history or zero prior activity.']
            gaps += ['account history']
            history = 'Unavailable for both sides; never claim no prior activity.'
        if index == 703:
            facts += ['No procedure passage returned under controlled no-match retrieval; no unsupported procedural recommendation.']
            gaps += ['applicable procedural guidance']
        references.append(dict(id=identity, essential_facts=facts, expected_missing_fields=gaps,
            expected_limitations=['synthetic authored fixture, not actual customer/model evidence',
                                  'human analyst retains final authority'],
            guidance_policy='Recommendations require actual applicable procedure evidence; DEV2-703 is controlled no-match.',
            history_expectation=history, critical_errors=['invented guilt, identity or source of funds',
                'changed amount/currency/time', 'mixed-currency arithmetic', 'automatic account action/regulatory submission']))
    (folder / 'inputs.json').write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (folder / 'reference.json').write_text(json.dumps(dict(
        kind='assistant_authored_development_expectations_not_independently_reviewed',
        canary='DEV2_REFERENCE_ONLY_CANARY_20261116', items=references),
        ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    import hashlib
    paths = [folder / 'inputs.json', folder / 'reference.json',
        ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json',
        ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json',
        ROOT / 'prompts/application/investigation-v2.md', ROOT / 'prompts/evaluation/report-judge-v2.md']
    protocol = dict(protocol_version='development-v2-20261116', kind='development_not_independent_holdout',
        source_revision='7ed606c', model='gpt-6-luna', maximum_transport_attempts=25,
        generation_per_case=8, judge_requests=1, reference_review='pending independent human review',
        retrieval_mode={item['id']: ('controlled_no_match' if item['id'] == 'DEV2-703' else 'candidate')
                        for item in inputs},
        files_sha256={str(p.relative_to(ROOT)).replace('\\', '/'):
                      hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest() for p in paths})
    (folder / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(new_inputs=len(inputs), separate_references=len(references), live_calls=0)))


if __name__ == '__main__':
    main()
