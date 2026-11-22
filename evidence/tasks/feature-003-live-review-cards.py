"""Explicit offline reference join AFTER all eight primary outputs are sealed."""
import html
import json
from pathlib import Path

from fraudlens.investigation.evaluation import verify_seal, write_frozen
from fraudlens.investigation.models import ROOT, digest

OUT=ROOT/'evals/results/feature-003/live-v1'


def main():
    splits=json.loads((ROOT/'evals/investigation/splits.json').read_text(encoding='utf-8'))
    ids=splits['investigation']['held_out']
    paths=[OUT/('primary-'+i+'.json') for i in ids]
    if not all(p.exists() for p in paths):
        raise SystemExit('All eight primary outputs must be sealed before offline review join.')
    outputs=[verify_seal(json.loads(p.read_text(encoding='utf-8'))) for p in paths]
    refs={x['id']:x for x in json.loads((ROOT/'evals/investigation/reference/investigation.json').read_text(encoding='utf-8')) if x['id'] in ids}
    cards=OUT/'review-cards'
    cards.mkdir(exist_ok=True)
    templates={'primary':[],'secondary':[]}
    outcomes=[]
    for item in outputs:
        identity=item['id'];result=item['result'];report=result['report']
        state=result['state'];ref=refs[identity]
        outcomes.append(dict(id=identity,status='validated' if report else state,
            attempt_id=result['attempt_id'],report_sha256=digest(report) if report else None,
            report_id=report['report_id'] if report else None,context_revision=result['context_revision']))
        lines=[f'# {identity}: {state}',f'Attempt: {result["attempt_id"]}',
               f'Duration: {item["duration_seconds"]:.3f} s',
               'Primary: Vedran Mitic. Secondary: Milan only for the preselected subset.',
               'Actual reviewer/date/judgments must be filled by humans. Templates are NOT ratings.']
        if report:
            base=dict(scenario_id=identity,attempt_id=result['attempt_id'],report_id=report['report_id'],
                report_sha256=digest(report),context_revision=result['context_revision'],
                reviewer_identity=None,reviewed_at=None,role=None,claim_id=None,report_location=None,
                claim_text=None,claim_kind=None,evidence_ids=[],judgment=None,reason=None,
                critical_error=None,essential_fact_id=None)
            for section,claims in report['draft'].items():
                if not isinstance(claims,list):
                    lines.append(f'{section}: '+html.escape(str(claims)))
                    continue
                lines.append('## '+section)
                for i,claim in enumerate(claims):
                    lines.append(f'{i+1}. '+html.escape(json.dumps(claim,ensure_ascii=False)))
                    if isinstance(claim,dict) and claim.get('kind') in ('observation','procedure'):
                        row={**base,'claim_id':f'{section}/{i}','report_location':f'/{section}/{i}',
                             'claim_text':claim['text'],'claim_kind':claim['kind'],'evidence_ids':claim['evidence_refs']}
                        for role in templates:
                            if role=='primary' or identity in splits['second_review_subset']:
                                templates[role].append({**row,'role':role})
            for fact in ref['essential_facts']:
                fact_id=fact.get('id',fact.get('fact_id'))
                row={**base,'claim_id':None,'report_location':'essential_facts','claim_text':json.dumps(fact,ensure_ascii=False),
                     'claim_kind':'essential_fact','essential_fact_id':fact_id}
                for role in templates:
                    if role=='primary' or identity in splits['second_review_subset']:
                        templates[role].append({**row,'role':role})
        else:
            lines.append('No report produced. Failure remains in denominator; do not invent claim ratings.')
            lines.append(html.escape(json.dumps(result.get('failure'),ensure_ascii=False)))
        lines.extend(['## Independent frozen expectations',html.escape(json.dumps(ref,ensure_ascii=False,indent=2)),
                      '## Exact evidence supplied',html.escape(json.dumps(item['evidence'],ensure_ascii=False,indent=2))])
        (cards/(identity+'.md')).write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
    for role,rows in templates.items():
        (cards/(role+'-ratings.template.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write_frozen(OUT/'outcomes.json',dict(mode='openai',outcomes=outcomes))
    print(json.dumps(dict(cards=len(outputs),actual_ratings=0,primary_template_rows=len(templates['primary']),secondary_template_rows=len(templates['secondary']))))


if __name__=='__main__':
    main()
