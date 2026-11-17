"""Prove favorable raw metrics cannot bypass calibration or missing-case counts."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


@pytest.mark.parametrize('mode', ['bad_calibration', 'missing_outputs'])
def test_judge_aggregation_keeps_failure_denominators(tmp_path, monkeypatch, mode):
    path = Path('backend/tests/support/retrieval_v6_integrated_judge.py').resolve()
    spec = importlib.util.spec_from_file_location('local_judge_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    monkeypatch.setattr(module, 'WORK', tmp_path / 'run')
    monkeypatch.setattr(module, 'runtime_revision', lambda: 'revision')
    monkeypatch.setattr(module, 'hashes', lambda: {})
    module.WORK.mkdir()
    (tmp_path / 'evidence/tasks').mkdir(parents=True)
    def save(name, value):
        (module.WORK / name).write_text(json.dumps(value), encoding='utf-8')
    inputs = [dict(id=str(i)) for i in range(20)]
    proposed = [dict(id=str(i), answerability='answerable' if i < 16 else 'no_answer') for i in range(20)]
    refs = [dict(id=str(i), status='completed', selection=dict(verdict='supported' if i < 16 else 'insufficient',
              selected=[dict(passage_id='p' + str(i))] if i < 16 else [])) for i in range(20)]
    outputs = [dict(id=str(i), http_status=200, job=dict(status='completed', result=dict(
        status='matched' if i < 16 else 'no_match', hits=[dict(passage=dict(passage_id='p' + str(i)))] if i < 16 else []))) for i in range(20)]
    if mode == 'missing_outputs':
        outputs = [r for r in outputs if r['id'] not in ('0', '19')]
    save('inputs.json', inputs)
    save('proposed-references.json', proposed)
    save('calibration-results.json', [dict(passed=not (mode == 'bad_calibration' and i == 0)) for i in range(4)])
    save('blind-gold.json', refs)
    save('gold-freeze.json', dict(sha256=hashlib.sha256((module.WORK / 'blind-gold.json').read_bytes()).hexdigest()))
    save('candidate-outputs.json', outputs)
    save('freeze.json', dict(runtime_revision='revision', files={}))
    (module.WORK / 'dispatch.jsonl').write_text('{}\n' * 44)
    module.summarize()
    report = json.loads((tmp_path / 'evidence/tasks/feature-003-v6-integrated-judge-20261117.json').read_text())
    assert report['threshold_pass'] is False
    assert report['metrics']['answerable'] == 16 and report['metrics']['no_answer_total'] == 4
    if mode == 'bad_calibration':
        assert report['judge_quality_valid'] is False and report['metrics']['recall_at5'] == 1
    else:
        assert report['metrics']['recall_at5'] == 15 / 16
        assert report['metrics']['no_answer_correct'] == 3
        assert report['metrics']['failed_or_unrun_ids'] == ['0', '19']
