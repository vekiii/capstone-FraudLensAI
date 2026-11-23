"""Opt-in four-attempt synthetic probe; durable cap, allowlisted diagnostics only."""
import asyncio
import hashlib
import json
import re
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx2

from fraudlens.investigation import provider
from fraudlens.investigation.settings import load_settings

PATH = Path('.cache/t033-resume-20261115.json')
record = json.loads(PATH.read_text(encoding='utf-8')) if PATH.exists() else dict(
    budget=4,attempts=[],runs=[])


def save():
    PATH.parent.mkdir(parents=True,exist_ok=True)
    PATH.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')


def diagnostic(raw):
    try:
        error=json.loads(raw)['error']
        value={}
        allowed={'type':{'invalid_request_error','server_error','authentication_error','permission_error'},
                 'code':{'invalid_json_schema','invalid_function_parameters','unsupported_parameter',
                         'model_not_found','invalid_api_key','insufficient_quota','rate_limit_exceeded',
                         'invalid_value','unsupported_value'}}
        for key,choices in allowed.items():
            item=error.get(key)
            value[key]=item if item is None or item in choices else 'other'
        parameter=error.get('param')
        if isinstance(parameter,str) and re.fullmatch(r'(?:model|tool_choice|max_output_tokens|include|input|tools|text)(?:[.\[\]A-Za-z0-9_-]{0,150})',parameter):
            value['param']=parameter
        message=error.get('message','')
        value['message_sha256']=hashlib.sha256(message.encode()).hexdigest()
        value['schema_error']='schema' in message.lower()
        value['mentioned_keywords']=[word for word in ('oneOf','allOf','anyOf','uniqueItems','pattern','minLength','maxLength','required','additionalProperties','tool_choice','model') if word in message]
        # Only the schema validator's field-path tuple, never arbitrary message text.
        context=re.search(r'In context=(\([^\n]{0,600}?\))',message)
        if context and re.fullmatch(r"[A-Za-z0-9_(), '\[\]]+",context[1]):
            value['schema_context']=context[1]
        return value
    except (ValueError,KeyError,TypeError,AttributeError):
        return dict(status='bounded_diagnostic_unavailable')


class Metered(httpx2.AsyncBaseTransport):
    def __init__(self):
        self.inner=httpx2.AsyncHTTPTransport()

    async def handle_async_request(self, request):
        if len(record['attempts'])>=4:
            raise provider.ProviderError('budget_exhausted')
        item=dict(sequence=len(record['attempts'])+1,started_at=datetime.now(UTC).isoformat())
        record['attempts'].append(item)
        save()  # Count failures/crashes before any transport I/O.
        start=time.monotonic()
        try:
            response=await self.inner.handle_async_request(request)
            item.update(http_status=response.status_code,request_id=response.headers.get('x-request-id'))
            if response.status_code>=400:
                original=response.stream
                class Observed(httpx2.AsyncByteStream):
                    async def __aiter__(self):
                        prefix=bytearray()
                        try:
                            async for chunk in original:
                                prefix.extend(chunk[:max(0,65536-len(prefix))])
                                yield chunk
                        finally:
                            item['diagnostic']=diagnostic(prefix)
                            save()
                    async def aclose(self):
                        await original.aclose()
                response=httpx2.Response(response.status_code,headers=response.headers,
                    stream=Observed(),request=request,extensions=response.extensions)
            return response
        except Exception as exc:
            item['transport_error_type']=type(exc).__name__
            raise
        finally:
            item['headers_elapsed_seconds']=round(time.monotonic()-start,3)
            save()

    async def aclose(self):
        await self.inner.aclose()


async def main():
    settings=load_settings()  # Authorized private root .env, never printed.
    if not settings.api_key.get_secret_value() or not settings.model.get_secret_value():
        raise SystemExit('Model/key configuration unavailable; no attempt.')
    run=dict(started_at=datetime.now(UTC).isoformat(),requested_model=settings.model.get_secret_value(),turns=[])
    record['runs'].append(run)
    save()
    original=provider.OpenAIProvider.next_turn
    async def observed(self,*args,**kwargs):
        result=await original(self,*args,**kwargs)
        run['turns'].append(dict(kind=result.kind,request_id=result.request_id,
            returned_model=result.returned_model,usage=result.usage))
        save()
        return result
    provider.OpenAIProvider.next_turn=observed
    started=time.monotonic()
    try:
        run['result']=await provider.probe_provider(settings,Metered())
        code=0
    except provider.ProviderError as exc:
        run.update(status='probe_failed',code=exc.code,outcome_unknown=exc.outcome_unknown)
        code=2
    except Exception as exc:
        run.update(status='probe_failed',unexpected_type=type(exc).__name__)
        code=1
    finally:
        run['elapsed_seconds']=round(time.monotonic()-started,3)
        save()
    safe=json.dumps(record,indent=2)
    if settings.api_key.get_secret_value() in safe:
        raise SystemExit('Sensitive metadata refused.')
    print(safe)
    return code


if __name__=='__main__':
    raise SystemExit(asyncio.run(main()))
