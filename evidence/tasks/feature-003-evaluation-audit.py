"""Metadata/hash-only lineage audit; never exposes questions or reference contents."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
                                     ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def main():
    protocol_path=ROOT/'evals/investigation/protocol.json'
    protocol=json.loads(protocol_path.read_text(encoding='utf-8'))
    approved=protocol['files_sha256']
    assert digest(approved)==protocol['sealed_inventory_sha256']
    content={k:v for k,v in approved.items() if not k.endswith('/reference/review-record.json')}
    assert digest(content)==protocol['bundle_sha256']
    changes={name:dict(t052_sha256=old,current_sha256=file_hash(ROOT/name))
             for name,old in approved.items() if file_hash(ROOT/name)!=old}
    assert set(changes) <= {'backend/src/fraudlens/investigation/retrieval.py'}, 'Unexpected sealed input/source change'
    runtime=[]
    for path in (ROOT/'backend/src/fraudlens/investigation').glob('*.py'):
        if path.name in ('evaluation.py','cli.py'):
            continue
        tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):
                assert not (node.module or '').endswith('.evaluation'), 'Runtime evaluator import'
            if isinstance(node,ast.Import):
                assert not any(x.name.endswith('.evaluation') for x in node.names)
        runtime.append(path.name)
    result=dict(version=2,date='2026-11-15',status='implementation_lineage_not_T055_freeze',
        t052_bundle_sha256=protocol['bundle_sha256'],original_protocol_sha256=file_hash(protocol_path),
        original_sealed_inventory_sha256=protocol['sealed_inventory_sha256'],
        original_approval_and_inputs_unchanged=True,implementation_changes=changes,
        runtime_modules_without_evaluator_import=sorted(runtime),
        new_artifact_sha256={name:file_hash(ROOT/name) for name in (
            'backend/src/fraudlens/investigation/evaluation.py',
            'backend/src/fraudlens/investigation/cli.py',
            'data/knowledge/fraudlens-aml-knowledge-v1/glossary.json')},
        held_out_exposure='No retrieval/investigation held-out questions or references printed/read into model context. Safety stimuli inspected; H08 input/reference not opened.',
        glossary_review='pending',t055='not_frozen',t056='not_run',live_provider='not_called')
    target=ROOT/'evals/investigation/implementation-lineage-v2.json'
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='PASS',files_hashed=len(approved),t052_bundle_sha256=protocol['bundle_sha256'],lineage_sha256=digest(result))))


if __name__=='__main__':
    main()
