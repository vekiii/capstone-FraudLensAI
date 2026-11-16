"""Real SDK over mocked HTTP only: budgets, privacy, strict schema and continuation."""
import asyncio
import copy
import json

import httpx2
import pytest

from fraudlens.investigation.context import CaseContextReader, outbound_context
from fraudlens.investigation.models import SCHEMA
from fraudlens.investigation.provider import OpenAIProvider, ProviderError, compile_report_schema
from fraudlens.investigation.tools import definitions

LIMITS = dict(request_timeout=1, max_input_bytes=48000,
              max_output_tokens=4096, max_response_bytes=2097152)


def messages():
    return [dict(type='context', data=outbound_context(
        CaseContextReader().resolve('CASE-001', 'fixture', None), 'inv_' + 'a' * 32))]


def response(output=None, status='completed', usage=None):
    return dict(id='resp_mock', model='returned-model', status=status,
                output=output or [], usage=usage)


def run(handler, conversation=None, limits=None):
    async def main():
        provider = OpenAIProvider('TEST-KEY-NOT-REAL', 'explicit-test-model',
                                  transport=httpx2.MockTransport(handler))
        try:
            return await provider.next_turn(conversation or messages(), definitions(),
                                           SCHEMA['$defs']['ReportDraft'], limits or LIMITS)
        finally:
            await provider.aclose()
    return asyncio.run(main())


def test_strict_request_model_budget_and_no_hidden_retry():
    seen = []
    def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        assert body['model'] == 'explicit-test-model'
        assert body['parallel_tool_calls'] is False and body['store'] is False
        assert body['max_output_tokens'] == 4096
        assert body['text']['format']['strict'] is True
        assert len(request.content) <= 48000
        assert all(t['strict'] for t in body['tools'])
        return httpx2.Response(429, json={'error': {'message': 'PRIVATE-CANARY'}},
                               headers={'retry-after': '1'})
    with pytest.raises(ProviderError) as error:
        run(handler)
    assert error.value.retryable and error.value.retry_after == 1
    assert len(seen) == 1 and 'PRIVATE-CANARY' not in str(error.value)


def test_provider_projection_omits_unique_items_without_relaxing_local_schema():
    from jsonschema import Draft202012Validator, ValidationError

    from fraudlens.investigation.models import validate
    compiled=compile_report_schema()
    def check(node):
        if isinstance(node,dict):
            assert 'uniqueItems' not in node
            for value in node.values():
                check(value)
        elif isinstance(node,list):
            for value in node:
                check(value)
    check(compiled)
    local=SCHEMA['$defs']['ReportDraft']['properties']['citations']
    assert local['uniqueItems'] is True
    # Use the actual compiled item shape; local uniqueness remains mandatory.
    citation_schema={**compiled['properties']['citations'],'uniqueItems':local['uniqueItems']}
    with pytest.raises(ValidationError):
        Draft202012Validator(citation_schema).validate(['ev_'+'a'*32]*2)
    draft=dict(outcome='needs_information',summary=[],observed_facts=[],risk_indicators=[],
               alternative_explanations=[],missing_information=['Synthetic'],
               recommended_checks=[],limitations=['Synthetic probe'],citations=[])
    validate('ReportDraft',draft)


def test_provider_pattern_uses_supported_anchor_and_local_rejects_terminal_newline():
    from fraudlens.investigation.models import validate
    projected=compile_report_schema()['properties']['citations']['items']['pattern']
    assert '(?!' not in projected
    assert projected=='^ev_[0-9a-f]{32}$'
    validate('EvidenceId','ev_'+'a'*32)
    with pytest.raises(ValueError):
        validate('EvidenceId','ev_'+'a'*32+'\n')


@pytest.mark.parametrize('status,code', [(401,'provider_access'),(403,'provider_access'),
    (400,'unsupported_capability'),(404,'unsupported_capability'),(500,'provider_failure')])
def test_safe_access_capability_and_transient_errors(status, code):
    with pytest.raises(ProviderError) as error:
        run(lambda request: httpx2.Response(status, json={'error': {'message': 'SECRET'}}))
    assert error.value.code == code and 'SECRET' not in str(error.value)
    assert error.value.retryable == (status == 500)


@pytest.mark.parametrize('outcome', ['refusal','incomplete'])
def test_refusal_and_incomplete_do_not_become_reports(outcome):
    output = [dict(type='message', role='assistant', content=[dict(type='refusal', refusal='No')])]
    result = run(lambda request: httpx2.Response(200, json=response(
        output, 'incomplete' if outcome == 'incomplete' else 'completed')))
    assert result.kind == outcome and result.draft is None


def test_required_private_output_items_and_call_ids_survive_next_turn():
    seen = []
    private = [dict(type='reasoning', id='rs_mock', summary=[], encrypted_content='OPAQUE'),
               dict(type='function_call', id='fc_mock', call_id='call_exact',
                    name='get_case_facts', arguments='{}')]
    def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        if len(seen) == 1:
            return httpx2.Response(200, json=response(private))
        assert private[0] in body['input'] and private[1] in body['input']
        assert any(x.get('type') == 'function_call_output' and x['call_id'] == 'call_exact'
                   for x in body['input'])
        return httpx2.Response(200, json=response([], 'incomplete'))
    async def main():
        provider = OpenAIProvider('TEST', 'explicit', transport=httpx2.MockTransport(handler))
        conversation = messages()
        try:
            first = await provider.next_turn(conversation, definitions(), {}, LIMITS)
            assert first.calls[0]['call_id'] == 'call_exact'
            assert first.private_items == tuple(private)
            conversation.extend([dict(type='tool_call', **first.calls[0]),
                dict(type='tool_result',call_id='call_exact',result=dict(status='completed',
                    evidence=[], returned_count=0, eligible_count=0, truncated=False))])
            await provider.next_turn(conversation, definitions(), {}, LIMITS)
        finally:
            await provider.aclose()
    asyncio.run(main())


@pytest.mark.parametrize('status', [200,500])
def test_bounded_stream_even_when_content_length_is_absent_or_wrong(status):
    class Large(httpx2.AsyncByteStream):
        async def __aiter__(self):
            yield b'x' * 1048576
            yield b'x' * 1048577
    with pytest.raises(ProviderError) as error:
        run(lambda request: httpx2.Response(status, stream=Large()))
    assert error.value.code == 'provider_incomplete'
    assert not error.value.retryable


def test_deadline_cancels_transport():
    async def handler(request):
        await asyncio.sleep(2)
        pytest.fail('Timed-out transport must be cancelled')
    with pytest.raises(ProviderError):
        run(handler, limits={**LIMITS,'request_timeout':0.02})


def test_private_late_input_never_reaches_http():
    conversation = messages()
    conversation.append({'type':'tool_result','call_id':'bad','result':{'labels':'SECRET'}})
    def forbidden(request):
        pytest.fail('Invalid input must not reach HTTP')
    with pytest.raises(ProviderError):
        run(forbidden, conversation)


def test_input_limit_includes_prompt_schema_and_private_continuation():
    def forbidden(request):
        pytest.fail('Oversized input must not reach HTTP')
    with pytest.raises(ProviderError):
        run(forbidden, limits={**LIMITS,'max_input_bytes':50})


def test_compilation_keeps_closed_required_shape_without_changing_source_schema():
    original = copy.deepcopy(SCHEMA)
    schema = compile_report_schema()
    def check(value):
        if isinstance(value, dict):
            assert 'allOf' not in value
            if '$ref' in value:
                assert value == {'$ref': '#/$defs/Claim'}
                assert 'Claim' in schema['$defs']
            if value.get('type') == 'object':
                assert value['additionalProperties'] is False
                assert set(value['required']) == set(value['properties'])
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)
    check(schema)
    assert SCHEMA == original and 'citations' in schema['properties']


def test_draft_and_usage_are_returned_without_inferred_cost():
    draft = dict(outcome='needs_information', summary=[], observed_facts=[], risk_indicators=[],
        alternative_explanations=[], missing_information=['Missing'], recommended_checks=[],
        limitations=['Insufficient information'], citations=[])
    output = [dict(type='message',role='assistant',content=[dict(type='output_text',text=json.dumps(draft))])]
    result = run(lambda request: httpx2.Response(200,json=response(output,usage={'total_tokens':17})))
    assert result.draft == draft and result.usage == {'total_tokens':17}
    assert result.returned_model == 'returned-model'


@pytest.mark.parametrize('payload', [
    response([dict(type='message', role='assistant', content=[None])]),
    {**response(), 'model': {'untrusted': 'not a model ID'}},
])
def test_malformed_provider_envelopes_are_typed_failures(payload):
    with pytest.raises(ProviderError) as caught:
        run(lambda request: httpx2.Response(200, json=payload))
    assert caught.value.code == 'provider_incomplete'
