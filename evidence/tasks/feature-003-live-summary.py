"""Summarize actual executions; never invent human support/coverage/spend."""
import hashlib
import json
from pathlib import Path

from fraudlens.investigation.evaluation import verify_seal, write_frozen
from fraudlens.investigation.models import ROOT

OUT=ROOT/'evals/results/feature-003/live-v1'


def main():
    split=json.loads((ROOT/'evals/investigation/splits.json').read_text(encoding='utf-8'))
    roles={'primary':split['investigation']['held_out'],'demo':split['ordinary_live_demo_cases']}
    summary=dict(date='2026-11-15',mode='actual OpenAI frozen synthetic inputs',model='gpt-6-luna',
        provider_budget=104,human_ratings='pending',support=None,essential_coverage=None,
        critical_unsupported_claims=None,spend=None,quality_acceptance='pending_T059',roles={})
    hashes={}
    for role,ids in roles.items():
        rows=[]
        for identity in ids:
            path=OUT/(role+'-'+identity+'.json')
            if not path.exists():
                raise SystemExit('Batch incomplete; no final aggregate written.')
            value=verify_seal(json.loads(path.read_text(encoding='utf-8')))
            hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            result=value['result']
            rows.append(dict(id=identity,attempt_id=result['attempt_id'],state=result['state'],
                report_id=result['report']['report_id'] if result['report'] else None,
                seconds=value['duration_seconds'],failure=result['failure'],budget=result['budget']))
        summary['roles'][role]=dict(count=len(rows),rows=rows,
            validated_or_needs_information=sum(x['state'] in ('ready_for_review','needs_information') for x in rows),
            failures=sum(x['state']=='failed' for x in rows),
            successful_within_90=sum(x['state'] in ('ready_for_review','needs_information') and x['seconds']<=90 for x in rows),
            all_terminal_within_120=all(x['seconds']<=120 for x in rows))
    ledger=json.loads((OUT/'transport-ledger.json').read_text(encoding='utf-8'))
    summary['transport_attempts']=len(ledger['attempts'])
    summary['artifact_sha256']=hashes
    write_frozen(OUT/'execution-summary.json',summary)
    (ROOT/'evidence/tasks/feature-003-live-results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('roles','artifact_sha256')}))


if __name__=='__main__':
    main()
