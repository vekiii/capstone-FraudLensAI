"""Explicit synthetic CLI gate; mocked capability exchange, never a live API call."""
import asyncio
import json

import httpx2

from fraudlens.investigation.cli import main
from fraudlens.investigation.provider import ProviderError, probe_provider
from fraudlens.investigation.settings import InvestigationSettings


def test_probe_command_requires_explicit_synthetic_flag(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    monkeypatch.delenv('OPENAI_MODEL',raising=False)
    assert main(['probe-provider']) == 2


def test_probe_missing_model_key_is_safe(capsys,monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    monkeypatch.delenv('OPENAI_MODEL',raising=False)
    assert main(['probe-provider','--synthetic-only']) == 2
    assert 'Traceback' not in capsys.readouterr().out


def test_probe_failure_preserves_safe_capability_outcome(monkeypatch, capsys):
    monkeypatch.setenv('OPENAI_API_KEY', 'DUMMY-NOT-A-REAL-KEY')
    monkeypatch.setenv('OPENAI_MODEL', 'dummy-explicit-model')
    async def unavailable(settings):
        raise ProviderError('unsupported_capability')
    monkeypatch.setattr('fraudlens.investigation.provider.probe_provider', unavailable)
    assert main(['probe-provider', '--synthetic-only']) == 2
    output = capsys.readouterr().out
    assert 'unsupported_capability' in output
    assert 'DUMMY' not in output and 'Traceback' not in output


def test_probe_uses_only_authored_diagnostic_context_and_strict_two_turns():
    seen=[]
    draft=dict(outcome='needs_information',summary=[],observed_facts=[],risk_indicators=[],
        alternative_explanations=[],missing_information=['No actual case.'],recommended_checks=[],
        limitations=['Synthetic probe only.'],citations=[])
    def handler(request):
        body=json.loads(request.content)
        seen.append(body)
        assert 'CASE-001' not in json.dumps(body)
        if len(seen)==1:
            assert body['tool_choice']['name']=='get_case_facts'
            output=[dict(type='function_call',id='fc',call_id='probe_call',name='get_case_facts',arguments='{}')]
        else:
            assert body['tool_choice']=='none'
            output=[dict(type='message',role='assistant',content=[dict(type='output_text',text=json.dumps(draft))])]
        return httpx2.Response(200,json=dict(id='resp',model='actual-model',status='completed',output=output,usage=None))
    settings=InvestigationSettings(provider='openai',api_key='TEST',model='explicit-model')
    result=asyncio.run(probe_provider(settings,httpx2.MockTransport(handler)))
    assert result['status']=='capability_probe_passed' and len(seen)==2
    assert all(item['usage'] is None for item in result['requests'])
