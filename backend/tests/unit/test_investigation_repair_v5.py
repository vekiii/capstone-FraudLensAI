"""Authored SDK regressions: schema size, lossless continuation and strict repair."""
import asyncio
import copy
import json

import httpx2
import pytest
from jsonschema import Draft202012Validator
from test_investigation_openai import LIMITS, messages, response
from test_investigation_workflow import create
from test_investigation_workflow import runtime as workflow_runtime

from fraudlens.investigation.models import ROOT, canonical
from fraudlens.investigation.provider import (
    OpenAIProvider,
    ProviderError,
    compile_report_schema,
    scripted_draft,
)
from fraudlens.investigation.repair import REPAIR_HINTS
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.tools import definitions

runtime = workflow_runtime
LEGACY = json.loads((ROOT / 'backend/tests/fixtures/investigation/provider-report-inline-v1.json')
                    .read_text(encoding='utf-8'))
REPAIR = 'Repair the draft: output_invalid. Use only supplied evidence. ' + REPAIR_HINTS['exact_assertion_mismatch']


def expanded(schema):
    def visit(node):
        if isinstance(node, list):
            return [visit(item) for item in node]
        if not isinstance(node, dict):
            return node
        if '$ref' in node:
            assert len(node) == 1 and node['$ref'].startswith('#/$defs/')
            return visit(schema['$defs'][node['$ref'][len('#/$defs/'):]])
        return {key: visit(value) for key, value in node.items() if key != '$defs'}
    return visit(schema)


def draft_output(draft):
    return [dict(type='reasoning', id='rs_final', summary=[], encrypted_content=''),
            dict(type='message', id='msg_final', role='assistant', status='completed',
                 content=[dict(type='output_text', text=json.dumps(draft, ensure_ascii=False))])]


def sized_output(body, draft, target):
    """Fix an authored legacy repair at target bytes, independently of new compiler."""
    output = draft_output(draft)
    legacy = {**body, 'input': body['input'] + output + [dict(role='user', content=REPAIR)],
              'tool_choice': 'none', 'text': dict(format=dict(type='json_schema',
              name='investigation_report', strict=True, schema=LEGACY))}
    size = len(httpx2.Request('POST', 'https://example.invalid', json=legacy).content)
    assert target > size
    output[0]['encrypted_content'] = 'X' * (target - size)
    return output


def test_shared_schema_expands_to_the_frozen_previous_provider_contract():
    schema = compile_report_schema()
    Draft202012Validator.check_schema(schema)
    assert expanded(schema) == LEGACY
    assert len(canonical(LEGACY)) == 5801
    assert len(canonical(schema)) < 2500


@pytest.mark.parametrize('fault', ['unknown', 'required', 'enum', 'bounds', 'ref_kind'])
def test_shared_schema_keeps_negative_claim_constraints(fault):
    draft = scripted_draft([], 'needs_information')
    claim = dict(text='Authored claim', kind='observation', evidence_refs=['ev_' + 'a' * 32],
                 exact_assertions=[], quotes=[])
    draft['summary'] = [claim]
    if fault == 'unknown':
        claim['unapproved'] = True
    elif fault == 'required':
        del claim['quotes']
    elif fault == 'enum':
        claim['kind'] = 'decision'
    elif fault == 'bounds':
        claim['text'] = 'x' * 2001
    else:
        claim['evidence_refs'] = ['other-case']
    for schema in (LEGACY, compile_report_schema()):
        assert not Draft202012Validator(schema).is_valid(draft)


@pytest.mark.parametrize('ceiling,target,succeeds', [
    (48000, 49925, True), (45000, 49925, False),
    (48000, 53000, False), (60000, 53000, False),
])
def test_sdk_repair_fits_without_losing_a_single_continuation_item(ceiling, target, succeeds):
    captured, outputs = [], []
    draft = scripted_draft([], 'needs_information')
    tool_output = [dict(type='reasoning', id='rs_tool', summary=[], encrypted_content='AUTHORED-OPAQUE'),
                   dict(type='function_call', id='fc_tool', call_id='call_original',
                        name='get_case_facts', arguments='{}')]

    def handler(request):
        body = json.loads(request.content)
        captured.append(body)
        assert len(request.content) <= min(48000, ceiling)
        if len(captured) == 1:
            output = tool_output
        elif len(captured) == 2:
            output = sized_output(body, draft, target)
        else:
            assert body['input'] == captured[1]['input'] + outputs[1] + [dict(role='user', content=REPAIR)]
            assert body['text'] == captured[0]['text'] == captured[1]['text']
            assert body['tools'] == definitions() and body['tool_choice'] == 'none'
            assert body['store'] is False
            assert outputs[0] == tool_output
            output = draft_output(draft)
        outputs.append(copy.deepcopy(output))
        return httpx2.Response(200, json=response(output))

    async def exercise():
        provider = OpenAIProvider('AUTHORED-NOT-REAL', 'authored-model',
                                  transport=httpx2.MockTransport(handler))
        conversation = messages()
        limits = {**LIMITS, 'max_input_bytes': ceiling}
        try:
            first = await provider.next_turn(conversation, definitions(), {}, limits)
            conversation.extend([dict(type='tool_call', **first.calls[0]),
                dict(type='tool_result', call_id='call_original', result=dict(status='completed',
                evidence=[], returned_count=0, eligible_count=0, truncated=False))])
            await provider.next_turn(conversation, definitions(), {}, limits)
            conversation.append(dict(type='repair', code='output_invalid', reason='exact_assertion_mismatch'))
            if succeeds:
                result = await provider.next_turn(conversation, definitions(), {}, {**limits, 'tool_choice': 'none'})
                assert result.draft == draft
            else:
                before = copy.deepcopy(provider.history)
                with pytest.raises(ProviderError, match='budget_exhausted'):
                    await provider.next_turn(conversation, definitions(), {}, {**limits, 'tool_choice': 'none'})
                assert provider.history == before
        finally:
            await provider.aclose()

    asyncio.run(exercise())
    assert len(captured) == (3 if succeeds else 2)


@pytest.mark.parametrize('corrected', [True, False])
def test_large_sdk_repair_is_still_validated_once_and_accounted(runtime, corrected):
    captured, original = [], []
    calls = [('get_case_facts', {}), ('get_account_history', {'account_side': 'sender'}),
             ('search_procedures', {'query': 'missing evidence'})]

    def handler(request):
        body = json.loads(request.content)
        captured.append(body)
        assert len(request.content) <= 48000
        count = len(captured)
        if count <= 3:
            name, arguments = calls[count - 1]
            output = [dict(type='reasoning', id=f'rs_{count}', summary=[], encrypted_content='OPAQUE'),
                      dict(type='function_call', id=f'fc_{count}', call_id=f'call_{count}',
                           name=name, arguments=json.dumps(arguments))]
        else:
            conversation = [dict(type='tool_result', result=json.loads(item['output']))
                            for item in body['input'] if item.get('type') == 'function_call_output']
            draft = scripted_draft(conversation, 'grounded')
            if count == 4 or not corrected:
                draft['observed_facts'][0]['exact_assertions'][0]['value'] = '999999.00'
            if count == 4:
                output = sized_output(body, draft, 49925)
                original.extend(copy.deepcopy(output))
            else:
                assert count == 5 and body['tool_choice'] == 'none'
                assert body['input'] == captured[3]['input'] + original + [dict(role='user', content=REPAIR)]
                output = draft_output(draft)
        return httpx2.Response(200, json=response(output, usage=dict(total_tokens=10)))

    _, request, make = runtime
    service = make()
    service.settings = InvestigationSettings(max_provider_requests=5)
    service.provider_factory = lambda binding: OpenAIProvider('AUTHORED', 'authored-model',
        prompt=binding['prompt'], transport=httpx2.MockTransport(handler))
    run = create(service, request)
    result = asyncio.run(service.work_once())
    assert len(captured) == 5
    assert result['budget']['provider_requests'] == 5
    assert result['budget']['repairs'] == 1 and result['budget']['tool_calls'] == 3
    events = service.events(run['attempt_id'])
    assert sum(e['operation'] == 'repair' for e in events) == 1
    assert sum(e['operation'] == 'dispatch_result' and e['outcome'] == 'completed' for e in events) == 5
    assert original in [e['private_items'] for e in events if e['operation'] == 'dispatch_result']
    assert result['state'] == ('ready_for_review' if corrected else 'failed')
    if not corrected:
        assert result['report'] is None and result['failure']['code'] == 'output_invalid'
