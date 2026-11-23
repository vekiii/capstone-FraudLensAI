"""Offline SDK replay of retained development trace; never uses a real transport/key."""
import asyncio
import copy
import hashlib
import json
import sqlite3

import httpx2

from fraudlens.investigation.context import outbound_context
from fraudlens.investigation.evaluation import verify_seal
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT, canonical
from fraudlens.investigation.provider import OpenAIProvider, compile_report_schema
from fraudlens.investigation.repair import REPAIR_HINTS
from fraudlens.investigation.retrieval import search
from fraudlens.investigation.tools import definitions, provider_evidence
from fraudlens.investigation.validation import validate_report


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def expanded(schema):
    def visit(node):
        if isinstance(node, list):
            return [visit(item) for item in node]
        if not isinstance(node, dict):
            return node
        if '$ref' in node:
            assert node == {'$ref': '#/$defs/Claim'}
            return visit(schema['$defs']['Claim'])
        return {key: visit(value) for key, value in node.items() if key != '$defs'}
    return visit(schema)


async def check():
    out = ROOT / 'evals/results/feature-003/development-v4'
    freeze = verify_seal(load(out / 'freeze.json'))
    protocol = load(ROOT / 'evals/investigation/development-v4/protocol.json')
    assert sha(ROOT / 'evals/investigation/development-v4/protocol.json') == freeze['protocol_sha256']
    for name, expected in {**protocol['files_sha256'], **protocol['preserved_v2_artifacts'],
                           **protocol['preserved_v3_source']}.items():
        assert sha(ROOT / name) == expected, name
    snapshot = ROOT / '.cache/evidence-snapshots/coverage-v4'
    for name, expected in freeze['code_sha256'].items():
        assert sha(snapshot / name) == expected, name
    # Original exported artifact hashes must still match their completed audit.
    audit = load(ROOT / 'evidence/tasks/feature-003-coverage-v4-results.json')
    for name, expected in audit['artifact_sha256'].items():
        assert sha(out / name) == expected, name
    before = {str(p.relative_to(ROOT)): sha(p) for folder in ('development-v2', 'development-v3', 'development-v4')
              for p in (out.parent / folder).glob('*.json')}
    saved = verify_seal(load(out / 'DEV4-742.json'))
    source = next(i for i in load(ROOT / 'evals/investigation/development-v4/inputs.json') if i['id'] == saved['id'])
    binding = next(e for e in saved['events'] if e['operation'] == 'binding')
    repair = next(e for e in saved['events'] if e['operation'] == 'repair')
    evidence = {e['evidence_id']: e for e in saved['evidence']}
    store = KnowledgeStore(out / 'runs.sqlite', initialize=False)
    uri = 'file:' + (out / 'runs.sqlite').as_posix() + '?mode=ro'
    with sqlite3.connect(uri, uri=True) as db:
        rows = db.execute('SELECT content FROM tool_steps WHERE attempt_id=? ORDER BY sequence',
                          (saved['result']['attempt_id'],)).fetchall()
    steps = {step['call_id']: step for step in (json.loads(row[0]) for row in rows)}

    def tool_result(call_id):
        step = steps[call_id]
        items = [evidence[ref] for ref in step['evidence_refs']]
        if step['name'] == 'search_procedures':
            found = search(store, step['arguments']['query'], binding['corpus_version'], binding['retrieval_version'])
            eligible = None if found.truncated else len(found['hits'])
            truncated = found.truncated or len(items) < len(found['hits'])
            status, returned = ('completed' if found['hits'] else 'no_match'), len(items)
        else:
            returned, eligible, truncated = (items[0][key] for key in ('returned_count', 'eligible_count', 'truncated'))
            status = 'completed'
        return dict(status=status, evidence=[provider_evidence(e) for e in items],
                    returned_count=returned, eligible_count=eligible, truncated=truncated)

    completed = [e for e in saved['events'] if e['operation'] == 'dispatch_result' and e['outcome'] == 'completed']
    requests, sizes = [], []

    def handler(request):
        requests.append(json.loads(request.content))
        sizes.append(len(request.content))
        index = len(requests) - 1
        if index < len(completed):
            return httpx2.Response(200, json=dict(status='completed', output=completed[index]['private_items']))
        # A diagnostic stub proves serialization only. No invented corrected LLM report.
        return httpx2.Response(200, json=dict(status='incomplete', output=[]))

    instructions = (binding['prompt'] + '\nSynthetic development instruction: ' + source['instruction']
                    + '\nProcedure query hints: ' + json.dumps(source['procedure_queries'], ensure_ascii=False))
    provider = OpenAIProvider('OFFLINE-MOCK-NO-CREDENTIAL', 'gpt-6-luna', prompt=instructions,
                              transport=httpx2.MockTransport(handler))
    limits = dict(request_timeout=1, max_input_bytes=binding['limits']['max_input_bytes'],
                  max_output_tokens=binding['limits']['max_output_tokens'],
                  max_response_bytes=binding['limits']['max_response_bytes'])
    conversation = [dict(type='context', data=outbound_context(source['context'], saved['result']['run_id']))]
    try:
        for event in completed:
            turn = await provider.next_turn(conversation, definitions(), {}, limits)
            assert turn.private_items == tuple(event['private_items'])
            if turn.kind == 'tools':
                for call in turn.calls:
                    conversation.extend([dict(type='tool_call', **call), dict(type='tool_result',
                                         call_id=call['call_id'], result=tool_result(call['call_id']))])
        assert turn.kind == 'draft'
        try:
            validate_report(turn.draft, saved['evidence'], saved['result']['attempt_id'],
                            source['context']['context_revision'], source['context'], binding['corpus_version'])
        except ValueError as error:
            assert str(error) == repair['reason'] == 'exact_assertion_mismatch'
        else:
            raise AssertionError('Original invalid draft must remain rejected')
        history = copy.deepcopy(provider.history)
        conversation.append(dict(type='repair', code='output_invalid', reason=repair['reason']))
        turn = await provider.next_turn(conversation, definitions(), {}, {**limits, 'tool_choice': 'none'})
        assert turn.kind == 'incomplete' and len(requests) == 6
        instruction = 'Repair the draft: output_invalid. Use only supplied evidence. ' + REPAIR_HINTS[repair['reason']]
        assert requests[-1]['input'] == history + [dict(role='user', content=instruction)]
        assert all(r['text'] == requests[0]['text'] and r['tools'] == definitions() and not r['store'] for r in requests)
    finally:
        await provider.aclose()
    legacy = load(ROOT / 'backend/tests/fixtures/investigation/provider-report-inline-v1.json')
    schema = compile_report_schema()
    assert expanded(schema) == legacy
    old_payload = copy.deepcopy(requests[-1])
    old_payload['text']['format']['schema'] = legacy
    old_size = len(httpx2.Request('POST', 'https://example.invalid', json=old_payload).content)
    assert old_size == load(ROOT / 'evidence/tasks/feature-003-coverage-v4-repair-diagnosis.json')['httpx_json_bytes']
    assert max(sizes) <= limits['max_input_bytes'] == 48000
    assert before == {name: sha(ROOT / name) for name in before}
    result = dict(status='PASS', kind='offline_sdk_repair_serialization_not_model_evaluation',
        original_failure='exact_assertion_mismatch', original_draft_still_rejected=True,
        old_repair_bytes=old_size, new_repair_bytes=sizes[-1], limit=48000,
        remaining_bytes=48000 - sizes[-1], old_schema_bytes=len(canonical(legacy)),
        new_schema_bytes=len(canonical(schema)), expanded_schemas_equal=True,
        entire_ordered_continuation_preserved=True, mocked_sdk_requests=len(requests),
        actual_api_calls=0, corrected_live_report=False, prior_json_files_preserved=len(before),
        pre_change_source_snapshot_verified=True, prior_protocol_and_artifact_hashes_verified=True,
        provider_source_sha256=sha(ROOT / 'backend/src/fraudlens/investigation/provider.py'))
    target = ROOT / 'evidence/tasks/feature-003-repair-v5-results.json'
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    asyncio.run(check())
