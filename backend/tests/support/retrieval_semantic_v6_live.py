"""Explicit one-shot public-data audit, total cap30, zero retries.

From root with PYTHONPATH=backend/src run this script --prepare, then --run.
Uses private local settings without printing secrets. Never load references into
the generation function; failures remain in metrics. No application-store writes.
"""
import asyncio
import hashlib
import json
import os
import sys

from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.retrieval_semantic_v6 import (
    policy_identity,
    request_payload,
    select_with_provider,
)
from fraudlens.investigation.settings import load_settings

WORK = ROOT / '.cache/retrieval-semantic-v6-20261117'
FILES = ['backend/src/fraudlens/investigation/retrieval_semantic_v6.py',
         'prompts/application/retrieval-answerability-v6.md']


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def hashes():
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES}


def prepare():
    WORK.mkdir(parents=True, exist_ok=False)
    store = KnowledgeStore(WORK / 'public-corpus.sqlite')
    corpus = store.publish(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')
    passages = store.passages(corpus)
    # Historical challenge is already exposed development, never fresh acceptance.
    cases = read(ROOT / 'evidence/tasks/feature-003-retrieval-v5-robustness-20261117.json')['cases']
    extra = [
        ('sim-review', 'Should a narrative claim wrongdoing merely because a score is high?'),
        ('sim-missing', 'If sources disagree, is their version information dispensable?'),
        ('sim-citation', 'Does a source identifier alone certify a correct interpretation?'),
        (None, 'In which country was this sender born?'),
        (None, 'What exact article of current EU law requires these records?'),
        (None, 'How many supporting documents were uploaded in this case?')]
    cases += [dict(id=i + 25, query=q, proposed_relevant_document=doc) for i, (doc, q) in enumerate(extra)]
    settings = load_settings()
    model = settings.model.get_secret_value()
    if not model or not settings.api_key.get_secret_value():
        raise ValueError('Explicit configured provider credentials required')
    for case in cases:
        request_payload(case['query'], passages, model)  # validate all before spending
    write(WORK / 'inputs.json', [dict(id=c['id'], query=c['query']) for c in cases])
    write(WORK / 'reference.json', cases)
    write(WORK / 'passages.json', passages)
    write(WORK / 'freeze.json', dict(status='FROZEN_DIAGNOSTIC_NOT_INDEPENDENT_ACCEPTANCE',
        model=model, corpus=corpus, policy=policy_identity(model, passages), files=hashes(),
        max_requests=30, sdk_retries=0, input_sha256=hashlib.sha256((WORK / 'inputs.json').read_bytes()).hexdigest(),
        passages_sha256=hashlib.sha256((WORK / 'passages.json').read_bytes()).hexdigest(),
        author='Codex AI; human semantic reference review absent'))
    print('Prepared30 public-data diagnostic queries; no provider calls.', flush=True)


async def generate():
    from fraudlens.investigation.provider import OpenAIProvider
    freeze = read(WORK / 'freeze.json')
    if hashes() != freeze['files']:
        raise ValueError('Frozen source changed')
    for name, key in [('inputs.json', 'input_sha256'), ('passages.json', 'passages_sha256')]:
        if hashlib.sha256((WORK / name).read_bytes()).hexdigest() != freeze[key]:
            raise ValueError('Frozen public input changed')
    inputs, passages = read(WORK / 'inputs.json'), read(WORK / 'passages.json')
    # Exclusive run marker disallows batch replay even after crash/unknown outcome.
    write(WORK / 'started.json', dict(max_requests=30, outcome='in_progress_or_unknown'))
    settings = load_settings()
    if settings.model.get_secret_value() != freeze['model']:
        raise ValueError('Explicit model changed')
    provider = OpenAIProvider(settings.api_key.get_secret_value(), freeze['model'])
    results = []
    ledger = WORK / 'dispatch.jsonl'
    try:
        for question in inputs:
            previous = ledger.read_text().splitlines() if ledger.exists() else []
            if len(previous) >= 30:
                raise ValueError('Hard request cap')
            # Persist intent BEFORE dispatch; unknown outcomes never regain budget.
            with ledger.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(dict(sequence=len(previous) + 1, id=question['id'])) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            try:
                selection, audit = await select_with_provider(provider, question['query'], passages)
                row = dict(id=question['id'], status='completed', selection=selection, audit=audit)
            except Exception as exc:
                row = dict(id=question['id'], status='failed', error_type=type(exc).__name__)
            write(WORK / f"result-{question['id']:02}.json", row)
            results.append(row)
            print(f"Request {len(results)}/30: {row['status']}", flush=True)
            if row['status'] == 'failed':
                break  # never repeatedly spend on capability/access/transport failure
    finally:
        await provider.client.close()
    write(WORK / 'outputs.json', results)


def join():
    outputs = read(WORK / 'outputs.json')
    refs = read(WORK / 'reference.json')  # only AFTER output archive exists
    passages = {p['passage_id']: p for p in read(WORK / 'passages.json')}
    results = {row['id']: row for row in outputs}
    recall, reciprocal, no_correct, no_count, failures = [], [], 0, 0, []
    for ref in refs:
        row = results.get(ref['id'])
        successful = row is not None and row['status'] == 'completed'
        if not successful:
            failures.append(ref['id'])
        expected = ref['proposed_relevant_document']
        if expected is None:
            no_count += 1
            no_correct += bool(successful and row['selection']['verdict'] == 'insufficient')
        else:
            ids = [passages[i['passage_id']]['document']['doc_id'] for i in row['selection']['selected']] if successful else []
            recall.append(int(expected in ids))
            reciprocal.append(1 / (ids.index(expected) + 1) if expected in ids else 0)
    usages = [r['audit']['usage'] for r in outputs if r['status'] == 'completed' and r['audit']['usage']]
    summary = dict(scope='AI-authored challenge diagnostics, NOT human-reviewed held-out acceptance',
        recall_at5=sum(recall) / len(recall), mrr_at5=sum(reciprocal) / len(reciprocal),
        answerable=len(recall), no_answer_correct=no_correct, no_answer_total=no_count,
        failures_or_unrun=failures, dispatched=len((WORK / 'dispatch.jsonl').read_text().splitlines()),
        token_usage=usages, freeze=read(WORK / 'freeze.json'), outputs=outputs)
    target = ROOT / 'evidence/tasks/feature-003-retrieval-v6-live-20261117.json'
    write(target, summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('outputs', 'freeze', 'token_usage')}, indent=2))


if __name__ == '__main__':
    if sys.argv[1:] == ['--prepare']:
        prepare()
    elif sys.argv[1:] == ['--run']:
        asyncio.run(generate())
        join()
    else:
        raise SystemExit('Explicit --prepare or --run required')
