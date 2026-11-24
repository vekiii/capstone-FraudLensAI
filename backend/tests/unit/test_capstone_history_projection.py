"""Grouped dataset history keeps one exact copy of each transport fact."""

import asyncio
import copy
import json

import httpx2
import pytest

from fraudlens.investigation.models import SCHEMA, canonical
from fraudlens.investigation.provider import OpenAIProvider
from fraudlens.investigation.tools import definitions, facts


@pytest.mark.parametrize('parallel, consistent', [(True, True), (True, False), (False, True)])
def test_transport_only_compacts_exact_duplicate_event_facts(monkeypatch, parallel, consistent):
    history = {'events': [{'amount': '100.00', 'currency': 'US Dollar'}], 'returned_count': 1}
    evidence = dict(kind='history', text=canonical(history).decode(), facts=facts(history))
    if not consistent:
        evidence['facts'][0]['value'] = 'different'
    messages = [dict(type='context', data={'source_mode': 'dataset'}), dict(
        type='tool_result', call_id='local-call', result={'evidence': [evidence]})]
    original = copy.deepcopy(messages)
    monkeypatch.setattr('fraudlens.investigation.provider.project_conversation', copy.deepcopy)
    captured = []

    def respond(request):
        captured.append(json.loads(request.content))
        return httpx2.Response(200, json={'status': 'completed', 'model': 'test-model', 'output': []})

    async def send():
        adapter = OpenAIProvider('synthetic-key', 'test-model', parallel_tools=parallel,
                                 transport=httpx2.MockTransport(respond))
        try:
            await adapter.next_turn(messages, definitions(), SCHEMA['$defs']['ReportDraft'],
                dict(max_input_bytes=48000, max_output_tokens=4096,
                     max_response_bytes=2097152, request_timeout=10))
        finally:
            await adapter.aclose()

    asyncio.run(send())
    assert messages == original
    returned, = json.loads(captured[0]['input'][1]['output'])['evidence']
    assert returned['text'] == evidence['text']
    assert returned['facts'] == [fact for fact in evidence['facts']
                                if not (parallel and consistent and fact['path'].startswith('events.'))]
