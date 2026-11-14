"""Test-provider mechanics, privacy projection and explicit non-live outcomes."""
import asyncio
import copy
import json
import socket

import pytest

from fraudlens.investigation.context import CaseContextReader, outbound_context
from fraudlens.investigation.models import SCHEMA, validate
from fraudlens.investigation.provider import ProviderError, ScriptedProvider, project_conversation
from fraudlens.investigation.tools import definitions


def conversation():
    return [dict(type='context', data=outbound_context(
        CaseContextReader().resolve('CASE-001', 'fixture', None), 'inv_' + 'a' * 32))]


def turn(provider, messages=None):
    return asyncio.run(provider.next_turn(messages if messages is not None else conversation(), definitions(),
                              SCHEMA['$defs']['ReportDraft'],
                              dict(request_timeout=30, max_input_bytes=48000,
                                   max_output_tokens=4096, max_response_bytes=2097152)))


def test_no_initialization_or_import_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Provider initialization must not call network')
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    result = turn(ScriptedProvider())
    assert result.kind == 'tools'
    assert result.returned_model == 'authored-test-provider-v1'
    assert result.usage is None


def test_scripted_sequence_preserves_call_ids_and_requests_only_three_tools():
    provider = ScriptedProvider()
    calls = [turn(provider).calls[0] for _ in range(3)]
    assert [c['name'] for c in calls] == [
        'get_case_facts', 'get_account_history', 'search_procedures']
    assert len({c['call_id'] for c in calls}) == 3
    assert all(set(c) == {'call_id', 'name', 'arguments'} for c in calls)


@pytest.mark.parametrize('scenario,kind', [('refusal', 'refusal'), ('incomplete', 'incomplete')])
def test_explicit_non_draft_outcomes(scenario, kind):
    result = turn(ScriptedProvider(scenario))
    assert result.kind == kind and result.draft is None and result.calls == ()


def test_no_fact_evidence_produces_limitation_draft():
    provider = ScriptedProvider('needs_information')
    for _ in range(3):
        turn(provider)
    result = turn(provider)
    validate('ReportDraft', result.draft)
    assert result.draft['outcome'] == 'needs_information'
    assert result.draft['observed_facts'] == [] and result.draft['limitations']


def test_scripted_grounded_draft_uses_only_actual_tool_result_refs_and_values():
    provider = ScriptedProvider()
    messages = conversation()
    for _ in range(3):
        turn(provider, messages)
    ref = 'ev_' + 'b' * 32
    result = dict(status='completed', returned_count=1, eligible_count=1, truncated=False,
                  evidence=[dict(evidence_id=ref, kind='case_fact', text='Authored 1250.00 EUR',
                                 facts=[dict(path='transaction.amount', value='1250.00'),
                                        dict(path='transaction.currency', value='EUR')],
                                 returned_count=1, eligible_count=1, truncated=False)])
    messages.append(dict(type='tool_result', call_id='test_call_1', result=result))
    output = turn(provider, messages)
    validate('ReportDraft', output.draft)
    assert output.kind == 'draft' and output.draft['outcome'] == 'ready_for_review'
    assert output.draft['citations'] == [ref]
    assert output.draft['observed_facts'][0]['exact_assertions'][0]['value'] == '1250.00'
    assert output.private_items == ()


@pytest.mark.parametrize('placement', ['root', 'context', 'transaction', 'assessment', 'late-result'])
def test_every_turn_rejects_non_allowlisted_private_fields(placement):
    messages = conversation()
    if placement == 'root':
        messages[0]['source_path'] = 'PRIVATE-CANARY'
    elif placement == 'context':
        messages[0]['data']['reference_answer'] = 'PRIVATE-CANARY'
    elif placement == 'transaction':
        messages[0]['data']['transaction']['Is Laundering'] = 'PRIVATE-CANARY'
    elif placement == 'assessment':
        messages[0]['data']['assessment']['reviewer_notes'] = 'PRIVATE-CANARY'
    else:
        messages.append(dict(type='tool_result', call_id='test',
                             result={'raw_source_row': 'PRIVATE-CANARY'}))
    with pytest.raises(ProviderError) as error:
        turn(ScriptedProvider(), messages)
    assert 'PRIVATE-CANARY' not in str(error.value)


def test_projection_is_copy_and_never_accepts_arbitrary_provider_items():
    messages = conversation()
    projected = project_conversation(messages)
    assert projected == messages and projected is not messages
    projected[0]['data']['case_id'] = 'CASE-999'
    assert messages[0]['data']['case_id'] == 'CASE-001'
    with pytest.raises(ProviderError):
        project_conversation(messages + [{'type': 'provider_item', 'source_path': 'private'}])


def test_input_and_output_are_bounded(tmp_path):
    messages = conversation()
    messages[0]['data']['notice'] = 'x' * 48001
    with pytest.raises(ProviderError):
        turn(ScriptedProvider(), messages)
    script = tmp_path / 'oversize.json'
    script.write_text(json.dumps({'version': 1, 'scenarios': {
        'large': [{'draft': {**SCHEMA['$defs']['ReportDraft'], 'padding': 'x' * 2097153}}]}}))
    with pytest.raises(ProviderError):
        turn(ScriptedProvider('large', script))


def test_unknown_script_is_explicit_no_fallback():
    with pytest.raises(ProviderError):
        turn(ScriptedProvider('not-a-scenario'))


def test_injected_tool_text_has_no_executable_or_permission_authority():
    original = conversation()
    text = json.dumps(original)
    projected = project_conversation(copy.deepcopy(original))
    assert json.dumps(projected) == text
    assert 'sender_account' not in text and 'DEMO-BANK' not in text
