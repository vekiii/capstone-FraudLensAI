"""Explicit exposed-development comparison; no holdout or provider access."""
import json
import tempfile
from pathlib import Path

from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.retrieval import search


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def main():
    target = ROOT / 'evidence/tasks/feature-003-retrieval-v5-development-20261117.json'
    if target.exists():
        raise ValueError('Diagnostic report already exists; preserve previous result')
    work = Path(tempfile.mkdtemp(dir=ROOT / '.cache', prefix='retrieval-v4-development-'))
    store = KnowledgeStore(work / 'diagnostic.sqlite')
    corpus = store.publish(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')
    prefix = 'data/knowledge/fraudlens-aml-knowledge-v1/'
    base = read(prefix + 'retrieval.json')
    configs = dict(demo_baseline=base,
                   v3_selected_baseline={**base, 'adequacy_cutoff': 8.863342357405378},
                   v4=read(prefix + 'retrieval-development-v4.json'))
    configs['v5'] = {**configs['v4'], 'configuration_version': 5, 'variant': 'english_coverage_v5'}
    pack = 'evals/investigation/retrieval-fresh-v3/'
    inputs = [q for q in read(pack + 'inputs/development.json') if q['language'] == 'en']
    rows = []
    for name, config in configs.items():
        version = store.save_configuration(config)
        for q in inputs:
            result = search(store, q['query'], corpus, version)
            rows.append(dict(configuration=name, id=q['id'], input_sha256=digest(q),
                             status=result['status'], hits=[h['passage']['passage_id'] for h in result['hits']]))
    # Prediction file is materialized before the separate offline reference join.
    (work / 'predictions.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    refs = {q['id']: q for q in read(pack + 'reference/development.json')}
    metrics = {}
    for name in configs:
        recalls, reciprocal, no_answer, no_count = [], [], 0, 0
        for row in rows:
            if row['configuration'] != name:
                continue
            ref, ids = refs[row['id']], row['hits']
            if ref['answerability'] == 'no_answer':
                no_count += 1
                no_answer += not ids
                continue
            relevant = set(ref['relevant_passage_ids'])
            recalls.append(len(relevant.intersection(ids)) / len(relevant))
            reciprocal.append(next((1 / (i + 1) for i, item in enumerate(ids) if item in relevant), 0))
        metrics[name] = dict(recall_at5=sum(recalls) / len(recalls), mrr_at5=sum(reciprocal) / len(reciprocal),
                             answerable=len(recalls), no_answer_correct=no_answer, no_answer_count=no_count)
    report = dict(scope='Exposed English development ONLY, not fresh acceptance or full RAG quality',
                  corpus=corpus, configurations=configs, rows=rows, metrics=metrics, provider_calls=0)
    target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
