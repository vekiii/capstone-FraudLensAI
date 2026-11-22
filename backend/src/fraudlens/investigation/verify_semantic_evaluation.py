"""Offline reproduction of archived metrics/code lineage; NEVER provider calls."""
import hashlib
import json

from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.retrieval_semantic_v6 import validate_selection


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify():
    folder = ROOT / 'evals/investigation/retrieval-v6-integrated-judge-20261117'
    manifest = read(folder / 'manifest.json')
    for name, expected in manifest['files_sha256_lf'].items():
        path = (folder / name).resolve()
        if not path.is_relative_to(folder.resolve()):
            raise ValueError('Archive path outside bundle')
        if hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest() != expected:
            raise ValueError('Archived file hash mismatch')
    freeze = read(folder / 'freeze.json')
    names = ('retrieval_semantic_v6.py', 'semantic_runtime.py', 'semantic_api.py',
             'retrieval_semantic_adapter_v6.py', 'settings.py', 'workflow.py', 'tools.py')
    revision = digest({n: hashlib.sha256((folder / 'executed-runtime' / (n + '.txt')).read_bytes()
                      .replace(b'\r\n', b'\n')).hexdigest() for n in names})
    if revision != freeze['runtime_revision']:
        raise ValueError('Executed runtime lineage mismatch')
    ledger = [json.loads(line) for line in (folder / 'dispatch.jsonl').read_text().splitlines()]
    if len(ledger) != 44 or len({(r['role'], r['id']) for r in ledger}) != 44:
        raise ValueError('Budget or replay violation')
    gold = {r['id']: r for r in read(folder / 'blind-gold.json')}
    outputs = {r['id']: r for r in read(folder / 'candidate-outputs-complete.json')}
    inputs = read(folder / 'inputs.json')
    passages = read(folder / 'passages.json')
    if len(inputs) != 20 or len(gold) != 20 or len(outputs) != 20:
        raise ValueError('Missing frozen rows')
    if not all(r['passed'] for r in read(folder / 'calibration-results.json')):
        raise ValueError('Judge calibration failed')
    recalls, reciprocal, no_correct, no_count, failures = [], [], 0, 0, []
    for q in inputs:
        ref, row = gold[q['id']], outputs[q['id']]
        relevant = set(validate_selection(ref['selection'], passages))
        success = row['http_status'] == 200 and row['job']['status'] == 'completed'
        if not success:
            failures.append(q['id'])
        ids = [h['passage']['passage_id'] for h in row['job']['result']['hits']] if success else []
        if ref['selection']['verdict'] == 'insufficient':
            no_count += 1
            no_correct += bool(success and row['job']['result']['status'] == 'no_match')
        else:
            recalls.append(len(relevant.intersection(ids)) / len(relevant))
            reciprocal.append(next((1 / (i + 1) for i, item in enumerate(ids) if item in relevant), 0))
    metrics = dict(recall_at5=sum(recalls) / len(recalls), mrr_at5=sum(reciprocal) / len(reciprocal),
                   answerable=len(recalls), no_answer_correct=no_correct, no_answer_total=no_count,
                   failed_or_unrun_ids=failures)
    actual = read(ROOT / 'evidence/tasks/feature-003-v6-integrated-judge-complete-20261117.json')
    if metrics != actual['metrics'] or not actual['judge_quality_valid']:
        raise ValueError('Metric or judge validity mismatch')
    passed = len(recalls) == 16 and no_count == no_correct == 4 and metrics['recall_at5'] >= .8 and metrics['mrr_at5'] >= .7
    return dict(status='PASS', threshold_pass=passed, metrics=metrics, reserved_requests=44,
                provider_calls=0, archived_runtime_verified=True,
                scope='Reproduction of archived automated judge evaluation, not new independent review')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
