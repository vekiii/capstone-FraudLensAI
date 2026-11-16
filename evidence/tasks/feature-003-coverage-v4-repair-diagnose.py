"""Offline reconstruction of rejected repair payload size; never sends a request."""
import json
import sqlite3

import httpx2

from fraudlens.investigation.context import outbound_context
from fraudlens.investigation.evaluation import verify_seal
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT, canonical
from fraudlens.investigation.provider import compile_report_schema
from fraudlens.investigation.repair import REPAIR_HINTS
from fraudlens.investigation.retrieval import search
from fraudlens.investigation.tools import definitions, provider_evidence


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    out = ROOT / 'evals/results/feature-003/development-v4'
    saved = verify_seal(load(out / 'DEV4-742.json'))
    item = next(i for i in load(ROOT / 'evals/investigation/development-v4/inputs.json') if i['id'] == saved['id'])
    binding = next(e for e in saved['events'] if e['operation'] == 'binding')
    repair = next(e for e in saved['events'] if e['operation'] == 'repair')
    sources = {e['evidence_id']: e for e in saved['evidence']}
    store = KnowledgeStore(out / 'runs.sqlite', initialize=False)
    uri = 'file:' + (out / 'runs.sqlite').as_posix() + '?mode=ro'
    with sqlite3.connect(uri, uri=True) as db:
        rows = db.execute('SELECT content FROM tool_steps WHERE attempt_id=? ORDER BY sequence',
                          (saved['result']['attempt_id'],)).fetchall()
    steps = {step['call_id']: step for step in (json.loads(row[0]) for row in rows)}

    def tool_result(call_id):
        step = steps[call_id]
        items = [sources[ref] for ref in step['evidence_refs']]
        if step['name'] == 'search_procedures':
            found = search(store, step['arguments']['query'], binding['corpus_version'], binding['retrieval_version'])
            eligible = None if found.truncated else len(found['hits'])
            truncated = found.truncated or len(items) < len(found['hits'])
            status = 'completed' if found['hits'] else 'no_match'
            returned = len(items)
        else:
            returned, eligible, truncated = (items[0][key] for key in ('returned_count', 'eligible_count', 'truncated'))
            status = 'completed'
        return dict(status=status, evidence=[provider_evidence(e) for e in items],
                    returned_count=returned, eligible_count=eligible, truncated=truncated)

    context = outbound_context(item['context'], saved['result']['run_id'])
    history = [dict(role='user', content=canonical(context).decode())]
    turns = [e for e in saved['events'] if e['operation'] == 'dispatch_result' and e['outcome'] == 'completed']
    previous = []
    for turn in turns:
        for call in previous:
            if call.get('type') == 'function_call':
                history.append(dict(type='function_call_output', call_id=call['call_id'],
                                    output=canonical(tool_result(call['call_id'])).decode()))
        history.extend(turn['private_items'])
        previous = turn['private_items']
    history.append(dict(role='user', content='Repair the draft: output_invalid. Use only supplied evidence. '
                        + REPAIR_HINTS[repair['reason']]))
    instructions = (binding['prompt'] + '\nSynthetic development instruction: ' + item['instruction']
                    + '\nProcedure query hints: ' + json.dumps(item['procedure_queries'], ensure_ascii=False))
    payload = dict(model='gpt-6-luna', instructions=instructions, input=history, tools=definitions(),
        parallel_tool_calls=False, store=False, include=['reasoning.encrypted_content'],
        max_output_tokens=binding['limits']['max_output_tokens'], tool_choice='none',
        text=dict(format=dict(type='json_schema', name='investigation_report', strict=True,
                             schema=compile_report_schema())))
    # Constructing a request measures encoding; no client/transport is invoked.
    request = httpx2.Request('POST', 'https://example.invalid', json=payload)
    size = len(canonical(payload))
    result = dict(id=saved['id'], kind='offline_repair_payload_reconstruction',
        repair_reason=repair['reason'], completed_turns=len(turns),
        canonical_utf8_bytes=size, httpx_json_bytes=len(request.content),
        configured_input_limit=binding['limits']['max_input_bytes'],
        exceeds_input_limit=size > binding['limits']['max_input_bytes'],
        expected_preserved_private_items=True, actual_api_calls=0)
    target = ROOT / 'evidence/tasks/feature-003-coverage-v4-repair-diagnosis.json'
    if target.exists():
        assert load(target) == result
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if result['exceeds_input_limit'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
