"""Post-execution integrity/usage audit; no calls, tuning or generated ratings."""
import ast
import hashlib
import json
from pathlib import Path

from fraudlens.investigation.evaluation import verify_seal, write_frozen
from fraudlens.investigation.models import ROOT, digest

OUT=ROOT/'evals/results/feature-003/live-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def main():
    freeze=verify_seal(json.loads((OUT/'freeze.json').read_text(encoding='utf-8')))
    for name,expected in freeze['code_sha256'].items():
        assert sha(ROOT/name)==expected,name
    assert hashlib.sha256((ROOT/'evidence/tasks/feature-003-live-run.py').read_bytes()).hexdigest()==freeze['runner_sha256']
    retrieval=verify_seal(json.loads((ROOT/'evals/investigation/freezes/retrieval-v1.json').read_text(encoding='utf-8')))
    for name,expected in retrieval['artifacts'].items():
        assert sha(ROOT/name)==expected,name
    protocol=json.loads((ROOT/'evals/investigation/protocol.json').read_text(encoding='utf-8'))
    for name,expected in protocol['files_sha256'].items():
        if name.startswith('evals/investigation/'):
            assert sha(ROOT/name)==expected,name
    inputs={x['id']:x for x in json.loads((ROOT/'evals/investigation/inputs/investigation.json').read_text(encoding='utf-8'))}
    ledger=json.loads((OUT/'transport-ledger.json').read_text(encoding='utf-8'))
    assert len(ledger['attempts'])<=104
    known=dict(input_tokens=0,output_tokens=0,total_tokens=0)
    count_known=0; count_dispatched=0; hashes={}
    for path in sorted([*OUT.glob('primary-*.json'),*OUT.glob('demo-*.json')]):
        value=verify_seal(json.loads(path.read_text(encoding='utf-8')))
        assert value['input_sha256']==digest(inputs[value['id']])
        assert value['freeze_sha256']==digest(freeze)
        result=value['result']
        assert result['context_revision']==inputs[value['id']]['context']['context_revision']
        assert result['corpus_version']==freeze['corpus_version']
        assert result['retrieval_version']==freeze['retrieval_sha256']
        count_dispatched+=result['budget']['provider_requests']
        for item in value['evidence']:
            assert item['attempt_id']==result['attempt_id'] and item['context_revision']==result['context_revision']
        for event in value['events']:
            if event['operation']=='dispatch_result' and event.get('usage'):
                count_known+=1
                for key in known:
                    known[key]+=event['usage'].get(key,0)
        hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    assert len(hashes)==13
    imports=[]
    for path in (ROOT/'backend/src/fraudlens/investigation').glob('*.py'):
        if path.name in ('evaluation.py','cli.py'):
            continue
        tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):
                assert not (node.module or '').endswith('.evaluation')
                assert not ((node.module or '')=='fraudlens.investigation' and any(a.name=='evaluation' for a in node.names))
        imports.append(path.name)
    audit=dict(date='2026-11-15',status='PASS_available_audit_T061_partial_pending_T059_T060',
        input_corpus_context_evidence_bindings='PASS',frozen_generation_code='PASS',
        retrieval_config_and_reference_hashes='PASS',outputs=hashes,transport_attempts=len(ledger['attempts']),
        reserved_provider_requests=count_dispatched,requests_with_reported_usage=count_known,
        requests_without_reported_usage=count_dispatched-count_known,known_usage=known,spend=None,
        runtime_modules_without_reference_loader_import=imports,human_quality_metrics='pending',
        t056_quality_rerun=False,post_generation_tuning=False)
    write_frozen(OUT/'audit.json',audit)
    (ROOT/'evidence/tasks/feature-003-live-audit-results.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    summary=json.loads((ROOT/'evidence/tasks/feature-003-live-results.json').read_text(encoding='utf-8'))
    summary['known_usage']=known
    summary['requests_with_reported_usage']=count_known
    summary['requests_without_reported_usage']=count_dispatched-count_known
    summary['usage_note']='Reported subset only; unknown dispatches/local rejections not assumed free. No spend estimate.'
    write_frozen(OUT/'execution-summary-v2.json',summary)
    (ROOT/'evidence/tasks/feature-003-live-results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:audit[k] for k in ('status','transport_attempts','reserved_provider_requests','requests_with_reported_usage','requests_without_reported_usage','known_usage')}))


if __name__=='__main__':
    main()
