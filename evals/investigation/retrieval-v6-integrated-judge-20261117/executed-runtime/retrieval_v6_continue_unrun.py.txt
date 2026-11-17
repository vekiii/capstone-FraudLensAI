"""Explicit continuation of UNDISPATCHED inputs, never retry failed/completed IDs.

Original frozen script/runtime/prompt/44 cap unchanged. Preserve first failed
partial report, append remaining outputs and a separately named aggregate report.
"""
import asyncio
import importlib.util
import json
from unittest.mock import patch
from uuid import NAMESPACE_URL, uuid5

import httpx

from fraudlens.investigation.models import ROOT

path = ROOT / 'backend/tests/support/retrieval_v6_integrated_judge.py'
spec = importlib.util.spec_from_file_location('original_frozen_runner', path)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


async def run():
    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.semantic_runtime import SemanticSearchService
    from fraudlens.main import create_app
    freeze = original.read(original.WORK / 'freeze.json')
    if original.runtime_revision() != freeze['runtime_revision'] or original.hashes() != freeze['files']:
        raise ValueError('Original source/prompt freeze changed; continuation forbidden')
    old_ledger = [json.loads(line) for line in (original.WORK / 'dispatch.jsonl').read_text().splitlines()]
    dispatched = {r['id'] for r in old_ledger if r['role'] == 'candidate_integrated_api'}
    inputs = [q for q in original.read(original.WORK / 'inputs.json') if q['id'] not in dispatched]
    if len(inputs) != 10 or len(old_ledger) != 34:
        raise ValueError('Expected exactly10 undispatched rows and34 prior intents')
    original.write(original.WORK / 'continuation-started.json', dict(
        reason='User authorized completing44-call evaluation; preserve failed020, run only021-030',
        previous_dispatches=34, remaining_cap=10, same_frozen_runtime=True))
    settings = original.load_settings()
    if settings.model.get_secret_value() != freeze['model']:
        raise ValueError('Explicit model changed')
    config = settings.model_copy(update=dict(enabled=True, semantic_retrieval=True, provider='openai',
        max_semantic_requests=20, store=original.WORK / 'runtime.sqlite'))
    service = SemanticSearchService(KnowledgeStore(config.store, initialize=False), config)
    app = create_app()
    app.state.semantic_search_service = service
    rows = []
    with patch('fraudlens.investigation.semantic_api.load_settings', return_value=config):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://testserver') as client:
            for q in inputs:
                original.reserve('candidate_integrated_api', q['id'])
                key = str(uuid5(NAMESPACE_URL, 'fraudlens-sem-v6-evaluation-' + q['id']))
                response = await client.post('/api/knowledge/semantic-search', json=dict(query=q['query']),
                                             headers={'Idempotency-Key': key})
                row = dict(id=q['id'], http_status=response.status_code, job=response.json())
                original.write(original.WORK / ('candidate-' + q['id'] + '.json'), row)
                rows.append(row)
                print(f"Undispatched continuation {len(rows)}/10: HTTP{response.status_code}", flush=True)
                if response.status_code != 200:
                    break
    original.write(original.WORK / 'candidate-outputs-continuation.json', rows)
    aggregate = original.read(original.WORK / 'candidate-outputs.json') + rows
    original.write(original.WORK / 'candidate-outputs-complete.json', aggregate)
    # Reuse the TESTED aggregator, only redirect its two input/output file paths.
    read, write = original.read, original.write
    def combined_read(p):
        if p.name == 'candidate-outputs.json':
            return aggregate
        return read(p)
    def combined_write(p, value):
        if p.name == 'feature-003-v6-integrated-judge-20261117.json':
            value['continuation'] = 'Only10 undispatched inputs; failed020 retained; zero retries; same freeze'
            p = p.with_name('feature-003-v6-integrated-judge-complete-20261117.json')
        return write(p, value)
    original.read, original.write = combined_read, combined_write
    original.summarize()


if __name__ == '__main__':
    asyncio.run(run())
