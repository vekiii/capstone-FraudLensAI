"""Authored diagnostics and durable cap only; no real env/ledger/HTTP."""
import asyncio
import importlib.util
import json
from pathlib import Path

import httpx2
import pytest


@pytest.fixture
def diagnostic(tmp_path,monkeypatch):
    source=Path(__file__).resolve().parents[3]/'evidence/tasks/feature-003-t033-resume.py'
    monkeypatch.chdir(tmp_path)
    spec=importlib.util.spec_from_file_location('probe_diagnostics_test',source)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_error_metadata_never_retains_arbitrary_provider_message(diagnostic):
    private='PRIVATE_TEST_CANARY'
    error={'error':{'code':private,'type':private,'param':private,
                    'message':'SECRET '+private}}
    result=diagnostic.diagnostic(json.dumps(error).encode())
    assert private not in json.dumps(result)
    assert result['code']=='other' and 'message' not in result


def test_schema_context_and_keyword_are_safe(diagnostic):
    raw={'error':{'code':'invalid_json_schema','type':'invalid_request_error',
                 'param':'text.format.schema','message':"Invalid schema: In context=('properties', 'summary'), 'oneOf' is not permitted."}}
    result=diagnostic.diagnostic(json.dumps(raw).encode())
    assert result['schema_error'] and result['mentioned_keywords']==['oneOf']
    assert result['param']=='text.format.schema'
    assert result['schema_context']=="('properties', 'summary')"


def test_transport_cap_persists_failures_before_network(diagnostic):
    from fraudlens.investigation.provider import ProviderError
    class Failed(httpx2.AsyncBaseTransport):
        calls=0
        async def handle_async_request(self,request):
            self.calls+=1
            raise httpx2.ConnectError('Authored failure',request=request)
        async def aclose(self):
            pass
    async def run():
        metered=diagnostic.Metered()
        await metered.inner.aclose()
        metered.inner=Failed()
        for _ in range(4):
            with pytest.raises(httpx2.ConnectError):
                await metered.handle_async_request(httpx2.Request('POST','https://example.invalid'))
        with pytest.raises(ProviderError,match='budget_exhausted'):
            await metered.handle_async_request(httpx2.Request('POST','https://example.invalid'))
        assert metered.inner.calls==4
        saved=json.loads(diagnostic.PATH.read_text(encoding='utf-8'))
        assert len(saved['attempts'])==4
        await metered.aclose()
    asyncio.run(run())
