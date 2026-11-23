"""Offline T059/T060 import; actual human files required, no ratings generated."""
import json
from pathlib import Path

from fraudlens.investigation.evaluation import report_metrics, verify_seal, write_frozen
from fraudlens.investigation.models import ROOT

OUT=ROOT/'evals/results/feature-003/live-v1'


def finalize(outcomes,records,failed_confirmations,second_subset):
    by_id={x['id']:x for x in outcomes}
    if len(by_id)!=8:
        raise ValueError('Eight primary outcomes required')
    grouped={};originals=[];units={}
    for row in records:
        if row['scenario_id'] not in by_id or row['role'] not in ('primary','secondary'):
            raise ValueError('Wrong rating identity/role')
        if not row['reviewer_identity'] or not row['reviewed_at'] or not row['reason'] or type(row['critical_error']) is not bool:
            raise ValueError('Actual reviewer/date/reason/judgment required')
        outcome=by_id[row['scenario_id']]
        if row['report_sha256']!=outcome['report_sha256'] or row['report_id']!=outcome['report_id']:
            raise ValueError('Report binding mismatch')
        key=(row['scenario_id'],row['role'],row['reviewer_identity'])
        unit=(row['scenario_id'],row['role'],row['report_location'],row['claim_id'],row['essential_fact_id'])
        if unit in units:
            raise ValueError('Duplicate rating unit')
        units[unit]=row.copy()
        group=grouped.setdefault(key,dict(id=key[0],reviewer=key[2],rated_at=row['reviewed_at'],
            report_sha256=row['report_sha256'],factual=[],essential=[],procedural=[],critical=False))
        allowed=({'present','missing','uncertain'} if row['essential_fact_id'] is not None else
                 {'applicable','unsupported','uncertain'} if row['claim_kind']=='procedure' else
                 {'supported','unsupported','uncertain'})
        if row['judgment'] not in allowed:
            raise ValueError('Actual supported judgment required')
        if row['essential_fact_id'] is not None:
            group['essential'].append(row['judgment'])
        elif row['claim_kind']=='observation':
            group['factual'].append(row['judgment'])
        elif row['claim_kind']=='procedure':
            group['procedural'].append(row['judgment'])
        elif row['claim_kind']!='hypothesis':
            raise ValueError('Unknown rating unit')
        group['critical']=group['critical'] or row['critical_error']
        originals.append(row.copy())
    primary=[r for key,r in grouped.items() if key[1]=='primary']
    metric=report_metrics(outcomes,primary)
    primary_by_id={key[0]:key[2] for key in grouped if key[1]=='primary'}
    secondary_by_id={key[0]:key[2] for key in grouped if key[1]=='secondary'}
    for confirmation in failed_confirmations:
        identity=confirmation['id']
        if by_id[identity]['report_id'] is not None or confirmation['judgment']!='failure_confirmed':
            raise ValueError('Failure confirmation mismatch')
        if not confirmation['reviewer'] or not confirmation['date'] or not confirmation['reason']:
            raise ValueError('Actual failure confirmation required')
        if confirmation['role'] not in ('primary','secondary'):
            raise ValueError('Invalid confirmation role')
        target=primary_by_id if confirmation['role']=='primary' else secondary_by_id
        if identity in target:
            raise ValueError('Duplicate failure confirmation')
        target[identity]=confirmation['reviewer']
    disagreements=[]
    for unit,row in units.items():
        if unit[1]!='primary':
            continue
        other=units.get((unit[0],'secondary',*unit[2:]))
        if other and (row['judgment'],row['critical_error'])!=(other['judgment'],other['critical_error']):
            disagreements.append(dict(unit=unit,primary=row.copy(),secondary=other.copy(),resolution=None))
    required={(o['id'],*unit) for o in outcomes for unit in o.get('required_review_units',[])}
    complete_units=required <= set(units)
    complete=(set(primary_by_id)==set(by_id) and len(set(primary_by_id.values()))==1
              and complete_units and not disagreements
              and all(identity in secondary_by_id and secondary_by_id[identity]!=primary_by_id[identity] for identity in second_subset))
    metric.update(review_complete=complete,original_records=originals,failed_confirmations=failed_confirmations,
                  disagreements=disagreements,
                  quality_acceptance=None if not complete else (
                      sum(r['passed'] for r in metric['ratings'])>=7
                      and not any(r['critical_error'] for r in records)))
    return metric


def main():
    # File is supplied by actual people, never created by this importer.
    review_path=ROOT/'evals/results/feature-003/reviews.json'
    if not review_path.is_file():
        raise SystemExit('Actual primary/secondary ratings pending; nothing synthesized.')
    submitted=json.loads(review_path.read_text(encoding='utf-8'))
    outcomes=verify_seal(json.loads((OUT/'outcomes.json').read_text(encoding='utf-8')))['outcomes']
    templates=[]
    for role in ('primary','secondary'):
        templates.extend(json.loads((OUT/'review-cards'/(role+'-ratings.template.json')).read_text(encoding='utf-8')))
    for outcome in outcomes:
        outcome['required_review_units']=[(r['role'],r['report_location'],r['claim_id'],r['essential_fact_id'])
                                           for r in templates if r['scenario_id']==outcome['id']]
    references={r['id']:r for r in json.loads((ROOT/'evals/investigation/reference/investigation.json').read_text(encoding='utf-8'))}
    for outcome in outcomes:
        outcome['no_guidance']=not references[outcome['id']]['applicable_guidance_passage_ids']
    split=json.loads((ROOT/'evals/investigation/splits.json').read_text(encoding='utf-8'))
    result=finalize(outcomes,submitted['ratings'],submitted['failed_case_confirmations'],split['second_review_subset'])
    write_frozen(OUT/'human-metrics.json',result)
    print(json.dumps(dict(review_complete=result['review_complete'],report_count=result['report_count'],
                          failures=result['failures'],quality_acceptance=result['quality_acceptance'])))


if __name__=='__main__':
    main()
