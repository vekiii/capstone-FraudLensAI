"""Authored protocol/recovery tests; no model calls or evaluation references."""
import asyncio
import copy
import json
from uuid import uuid4

import httpx2
import pytest
from test_investigation_openai import response
from test_investigation_workflow import create
from test_investigation_workflow import runtime as workflow_runtime

from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.provider import OpenAIProvider, Turn, scripted_draft
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.validation import validate_report

runtime = workflow_runtime
NOTICE = 'Konačnu odluku donosi ljudski analitičar; AI nacrt ne izvršava radnje.'
POLICY = 'human_authority_notice_v1'


class NoGuidance:
    def __init__(self, corrected=False, outcome='needs_information'):
        self.corrected, self.outcome, self.calls, self.drafts = corrected, outcome, 0, []

    async def next_turn(self, conversation, tools, schema, limits):
        self.calls += 1
        if self.calls <= 2:
            name, arguments = ('get_case_facts', {}) if self.calls == 1 else (
                'search_procedures', {'query': 'zzzzq-absent-guidance'})
            return Turn('tools', calls=(dict(call_id=f'call_{self.calls}', name=name, arguments=arguments),))
        draft = scripted_draft(conversation, 'grounded')
        draft['outcome'] = self.outcome
        draft['limitations'] = [text for text in draft['limitations'] if text != NOTICE]
        if self.calls > 3 and self.corrected:
            assert conversation[-1] == dict(type='repair', code='output_invalid', reason='human_authority_notice_required')
            assert limits['tool_choice'] == 'none'
            draft['limitations'].append(NOTICE)
        self.drafts.append(copy.deepcopy(draft))
        return Turn('draft', draft=draft, private_items=(dict(type='message', role='assistant',
                    content=[dict(type='output_text', text=json.dumps(draft, ensure_ascii=False))]),))


@pytest.mark.parametrize('corrected', [True, False])
@pytest.mark.parametrize('outcome', ['needs_information', 'ready_for_review'])
def test_missing_notice_gets_one_repair_then_validates_or_fails(runtime, corrected, outcome):
    _, request, make = runtime
    provider = NoGuidance(corrected, outcome)
    service = make(provider=provider)
    run = create(service, request)
    result = asyncio.run(service.work_once())
    assert provider.calls == 4 and result['budget']['repairs'] == 1
    assert result['budget']['provider_requests'] == 4 and result['budget']['tool_calls'] == 2
    assert NOTICE not in provider.drafts[0]['limitations']
    events = service.events(run['attempt_id'])
    assert [e['reason'] for e in events if e['operation'] == 'repair'] == ['human_authority_notice_required']
    raw = [e['private_items'][0]['content'][0]['text'] for e in events
           if e['operation'] == 'dispatch_result' and e['private_items']]
    assert [json.loads(text) for text in raw] == provider.drafts
    if corrected:
        assert result['state'] == outcome and result['report']['draft']['limitations'][-1] == NOTICE
        assert result['report']['semantic_review'] == 'not_reviewed'
    else:
        assert result['state'] == 'failed' and result['failure']['code'] == 'output_invalid'
        assert result['report'] is None


def test_new_binding_pins_notice_policy_and_prompt_v4(runtime):
    _, request, make = runtime
    service = make()
    run = create(service, request)
    binding = service.binding(run['attempt_id'])
    assert binding.get('report_policy') == POLICY
    assert binding['prompt'].startswith('# Investigation application prompt v4')
    assert NOTICE in binding['prompt']


def test_authored_test_provider_satisfies_the_new_policy_without_repair(runtime):
    _, request, make = runtime
    service = make('needs_information')
    create(service, request)
    result = asyncio.run(service.work_once())
    assert result['state'] == 'needs_information' and result['budget']['repairs'] == 0
    assert NOTICE in result['report']['draft']['limitations']


def create_older_binding(service, request, policy=None):
    """Construct a fixture binding before insertion; never modify immutable events."""
    original = service.repo.create

    def insert(*args, **kwargs):
        binding = copy.deepcopy(kwargs['binding'])
        binding.pop('report_policy', None)
        binding['prompt'] = (ROOT / 'prompts/application/investigation-v3.md').read_text(encoding='utf-8')
        binding['prompt_version'] = digest(binding['prompt'])
        if policy is not None:
            binding['report_policy'] = policy
        return original(*args, **{**kwargs, 'binding': binding})

    service.repo.create = insert
    try:
        return create(service, request)
    finally:
        service.repo.create = original


def test_legacy_missing_policy_stays_legacy_and_retry_inherits(runtime):
    _, request, make = runtime
    service = make(provider=NoGuidance())
    run = create_older_binding(service, request)
    original = service.binding(run['attempt_id'])
    result = asyncio.run(service.work_once())
    assert result['state'] == 'needs_information' and result['budget']['repairs'] == 0
    old_draft = copy.deepcopy(result['report'])
    child = service.retry(result['attempt_id'], result['revision'], False, 'local-analyst', str(uuid4()))
    assert 'report_policy' not in service.binding(child['attempt_id'])
    assert service.binding(child['attempt_id'])['prompt'] == original['prompt']
    assert service.read(run['attempt_id'])['report'] == old_draft


def test_new_retry_keeps_notice_policy(runtime):
    _, request, make = runtime
    service = make('needs_information')
    run = create(service, request)
    parent = asyncio.run(service.work_once())
    child = service.retry(parent['attempt_id'], parent['revision'], False, 'local-analyst', str(uuid4()))
    assert service.binding(child['attempt_id']).get('report_policy') == POLICY
    assert service.binding(child['attempt_id'])['prompt'] == service.binding(run['attempt_id'])['prompt']


def test_unknown_policy_fails_before_provider_dispatch(runtime):
    _, request, make = runtime
    service = make()
    create_older_binding(service, request, 'AUTHORED-UNKNOWN-POLICY')
    result = asyncio.run(service.work_once())
    assert result['state'] == 'failed' and result['failure']['code'] == 'unsupported_capability'
    assert result['budget']['provider_requests'] == 0 and result['report'] is None


def test_notice_repair_cannot_exceed_lower_request_budget(runtime):
    _, request, make = runtime
    provider = NoGuidance(corrected=True)
    service = make(provider=provider, settings=InvestigationSettings(max_provider_requests=3))
    create(service, request)
    result = asyncio.run(service.work_once())
    assert provider.calls == 3 and result['budget']['provider_requests'] == 3
    assert result['state'] == 'failed' and result['failure']['code'] == 'budget_exhausted'


@pytest.mark.parametrize('limitation', [
    '', 'Human analyst decides.', 'NE: ' + NOTICE, '"' + NOTICE + '"',
    NOTICE.lower(), NOTICE + ' This is only a quote.',
])
def test_exact_protocol_item_cannot_be_replaced_by_keywords_or_quoted_text(limitation):
    draft = scripted_draft([], 'needs_information')
    draft['limitations'] = [limitation] if limitation else ['Other truthful limitation.']
    draft['missing_information'].append(NOTICE)  # Wrong location cannot satisfy the protocol.
    before = copy.deepcopy(draft)
    with pytest.raises(ValueError, match='human_authority_notice_required'):
        validate_report(draft, [], 'att_' + 'a' * 32, '0' * 64, report_policy=POLICY)
    assert draft == before


def test_literal_policy_is_not_semantic_approval_and_legacy_still_accepts_old_form():
    draft = scripted_draft([], 'needs_information')
    before = copy.deepcopy(draft)
    report = validate_report(draft, [], 'att_' + 'a' * 32, '0' * 64, report_policy=POLICY)
    assert report['draft'] == before and draft == before
    assert report['semantic_review'] == 'not_reviewed'
    draft['limitations'].remove(NOTICE)
    assert validate_report(draft, [], 'att_' + 'a' * 32, '0' * 64)['draft'] == draft


def test_real_sdk_notice_repair_serializes_fixed_hint_and_preserves_invalid_output(runtime):
    seen, outputs = [], []

    def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        assert len(request.content) <= 48000 and body['store'] is False
        count = len(seen)
        if count <= 2:
            name, arguments = ('get_case_facts', {}) if count == 1 else (
                'search_procedures', {'query': 'zzzzq-absent-guidance'})
            output = [dict(type='reasoning', id=f'rs_{count}', summary=[], encrypted_content='AUTHORED-OPAQUE'),
                dict(type='function_call', id=f'fc_{count}', call_id=f'call_{count}',
                     name=name, arguments=json.dumps(arguments))]
        else:
            conversation = [dict(type='tool_result', result=json.loads(item['output']))
                            for item in body['input'] if item.get('type') == 'function_call_output']
            draft = scripted_draft(conversation, 'grounded')
            draft['outcome'] = 'needs_information'
            if count == 3:
                draft['limitations'].remove(NOTICE)
            else:
                assert count == 4 and body['tool_choice'] == 'none'
                assert body['input'][:-1] == seen[2]['input'] + outputs[2]
                assert NOTICE in body['input'][-1]['content']
                assert json.loads(outputs[2][-1]['content'][0]['text'])['limitations'] == [
                    text for text in draft['limitations'] if text != NOTICE]
            output = [dict(type='reasoning', id=f'rs_{count}', summary=[], encrypted_content='AUTHORED-DRAFT-OPAQUE'),
                dict(type='message', role='assistant', content=[dict(type='output_text', text=json.dumps(draft))])]
        outputs.append(copy.deepcopy(output))
        return httpx2.Response(200, json=response(output))

    _, request, make = runtime
    service = make()
    service.provider_factory = lambda binding: OpenAIProvider('AUTHORED-NOT-REAL', 'authored-model',
        prompt=binding['prompt'], transport=httpx2.MockTransport(handler))
    run = create(service, request)
    result = asyncio.run(service.work_once())
    assert len(seen) == 4 and result['state'] == 'needs_information'
    assert result['budget']['repairs'] == 1 and result['budget']['transient_retries'] == 0
    assert NOTICE in result['report']['draft']['limitations']
    assert outputs[2] in [e['private_items'] for e in service.events(run['attempt_id'])
                          if e['operation'] == 'dispatch_result']
