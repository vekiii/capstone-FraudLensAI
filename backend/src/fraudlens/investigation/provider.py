"""Replaceable provider boundary; no client/network work during import."""
import asyncio
import copy
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from fraudlens.investigation.models import SCHEMA, canonical, validate
from fraudlens.investigation.repair import REPAIR_HINTS
from fraudlens.investigation.report_policy import HUMAN_AUTHORITY_NOTICE

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = re.compile(r'label|laundering|isfraud|reference.answer|source.path|source.row|reviewer', re.I)
QUOTA_CODES = frozenset({'insufficient_quota', 'credit_balance_exhausted',
    'organization_usage_limit_exceeded', 'organization_spend_limit_exceeded',
    'project_spend_limit_exceeded', 'usage_limit_exceeded'})
PROVIDER_CODES = QUOTA_CODES | {'rate_limit_exceeded', 'slow_down', 'server_is_overloaded', 'server_overloaded'}
DIAGNOSTIC_REASONS = frozenset({'request_timeout', 'attempt_timeout', 'connection_error',
                               'rate_limit', 'quota_exhausted', 'http_error'})


def safe_diagnostic(value):
    """Only fixed codes and a numeric status may enter private audit events."""
    if not isinstance(value, dict):
        return {}
    result = {}
    reason, code, status = value.get('reason'), value.get('provider_code'), value.get('http_status')
    if isinstance(reason, str) and reason in DIAGNOSTIC_REASONS:
        result['reason'] = reason
    if type(status) is int and 100 <= status <= 599:
        result['http_status'] = status
    if isinstance(code, str) and code in PROVIDER_CODES:
        result['provider_code'] = code
    return result


def compile_report_schema(*, require_case_sections=False):
    """Compile the provider subset, sharing the repeated Claim definition.

    The provider enforces the closed shape. Original allOf/if/then conditions and
    uniqueItems constraints are enforced again by the unchanged local validator.
    Sharing a definition changes representation only; keep the entire private
    continuation and evidence available within the existing request-byte limit.
    """
    def compile_node(node):
        if isinstance(node, list):
            return [compile_node(item) for item in node]
        if not isinstance(node, dict):
            return node
        if '$ref' in node:
            prefix = '#/$defs/'
            if not node['$ref'].startswith(prefix):
                raise ProviderError('unsupported_capability')
            return compile_node(SCHEMA['$defs'][node['$ref'][len(prefix):]])
        compiled={key: compile_node(value) for key, value in node.items()
                  if key not in ('allOf','uniqueItems')}
        # Provider regex engines reject lookarounds. Keep exact-end validation
        # in the original local schema; outbound JSON uses a portable anchor.
        pattern=compiled.get('pattern')
        if isinstance(pattern,str) and pattern.endswith(r'(?![\s\S])'):
            compiled['pattern']=pattern[:-len(r'(?![\s\S])')]+'$'
        return compiled
    schema = compile_node(SCHEMA['$defs']['ReportDraft'])
    claim = schema['properties']['summary']['items']
    for field in schema['properties'].values():
        if field.get('items') == claim:
            field['items'] = {'$ref': '#/$defs/Claim'}
    if require_case_sections:
        for section in ('summary', 'observed_facts', 'citations'):
            schema['properties'][section]['minItems'] = 1
    schema['$defs'] = {'Claim': claim}
    return schema


def _bounded_transport(inner):
    import httpx2
    class Transport(httpx2.AsyncBaseTransport):
        limit = 2097152
        exceeded = False
        input_limit = 48000
        input_exceeded = False

        async def handle_async_request(self, request):
            if len(request.content) > self.input_limit:
                self.input_exceeded = True
                raise ProviderError('budget_exhausted')
            response = await inner.handle_async_request(request)
            parent = self
            class Stream(httpx2.AsyncByteStream):
                async def __aiter__(self):
                    total = 0
                    async for chunk in response.stream:
                        total += len(chunk)
                        if total > parent.limit:
                            parent.exceeded = True
                            raise ProviderError('provider_incomplete')
                        yield chunk

                async def aclose(self):
                    await response.aclose()
            if response.headers.get('content-encoding', 'identity') != 'identity':
                await response.aclose()
                self.exceeded = True
                raise ProviderError('provider_incomplete')
            return httpx2.Response(response.status_code, headers=response.headers,
                stream=Stream(), request=request, extensions=response.extensions)

        async def aclose(self):
            await inner.aclose()
    return Transport()


class OpenAIProvider:
    def __init__(self, api_key, model, prompt='', transport=None, *, request_timeout_cap=30, output_token_cap=4096,
                 reasoning_effort=None, parallel_tools=False, strict_case_sections=False):
        import httpx2
        from openai import AsyncOpenAI
        if type(request_timeout_cap) is not int or request_timeout_cap not in (30, 45, 60):
            raise ProviderError('unsupported_capability')
        if type(output_token_cap) is not int or output_token_cap not in (4096, 8192):
            raise ProviderError('unsupported_capability')
        if reasoning_effort not in (None, 'low'):
            raise ProviderError('unsupported_capability')
        if type(parallel_tools) is not bool:
            raise ProviderError('unsupported_capability')
        self.parallel_tools = parallel_tools
        self.strict_case_sections = strict_case_sections
        self.reasoning_effort = reasoning_effort
        self.output_token_cap = output_token_cap
        self.request_timeout_cap = request_timeout_cap
        if not isinstance(model, str) or not model.strip() or len(model) > 200:
            raise ProviderError('unsupported_capability')
        if not api_key:
            raise ProviderError('provider_access')
        self.model, self.prompt = model, prompt
        self.transport = _bounded_transport(transport or httpx2.AsyncHTTPTransport())
        self.client = AsyncOpenAI(
            api_key=api_key, max_retries=0, timeout=30,
            base_url='https://api.openai.com/v1',
            default_headers={'Accept-Encoding': 'identity'},
            http_client=httpx2.AsyncClient(transport=self.transport, trust_env=False,
                                          follow_redirects=False, timeout=30))
        self.history, self.seen = [], 0

    async def next_turn(self, conversation, tools, report_schema, remaining_limits):
        from openai import APIConnectionError, APIStatusError, APITimeoutError

        from fraudlens.investigation.tools import definitions
        messages = project_conversation(conversation)
        if tools != definitions() or len(messages) < self.seen:
            raise ProviderError('provider_input_invalid')
        compact_history = self.parallel_tools and any(
            item['type'] == 'context' and item['data']['source_mode'] == 'dataset' for item in messages
        )
        pending = copy.deepcopy(self.history)
        for item in messages[self.seen:]:
            if item['type'] == 'context':
                pending.append(dict(role='user', content=canonical(item['data']).decode()))
            elif item['type'] == 'tool_result':
                if compact_history:
                    _deduplicate_history_facts(item['result'])
                pending.append(dict(type='function_call_output', call_id=item['call_id'],
                                    output=canonical(item['result']).decode()))
            elif item['type'] == 'repair':
                instruction = 'Repair the draft: output_invalid. Use only supplied evidence.'
                if 'reason' in item:
                    instruction += ' ' + REPAIR_HINTS[item['reason']]
                pending.append(dict(role='user', content=instruction))
        require_case_sections = self.strict_case_sections and any(
            evidence['kind'] == 'case_fact'
            for item in messages if item['type'] == 'tool_result'
            for evidence in item['result']['evidence']
        )
        payload = dict(model=self.model, instructions=self.prompt, input=pending,
            tools=tools, parallel_tool_calls=self.parallel_tools, store=False,
            include=['reasoning.encrypted_content'],
            max_output_tokens=remaining_limits['max_output_tokens'],
            text=dict(format=dict(type='json_schema', name='investigation_report',
                                  strict=True, schema=compile_report_schema(require_case_sections=require_case_sections))))
        if self.reasoning_effort is not None:
            payload['reasoning'] = {'effort': self.reasoning_effort}
        if 'tool_choice' in remaining_limits:
            payload['tool_choice'] = remaining_limits['tool_choice']
        timeout = min(self.request_timeout_cap, remaining_limits['request_timeout'])
        if (timeout <= 0 or not 1 <= payload['max_output_tokens'] <= self.output_token_cap
                or len(canonical(payload)) > min(48000, remaining_limits['max_input_bytes'])):
            raise ProviderError('budget_exhausted')
        self.transport.limit = min(2097152, remaining_limits['max_response_bytes'])
        self.transport.exceeded = False
        self.transport.input_limit = min(48000, remaining_limits['max_input_bytes'])
        self.transport.input_exceeded = False
        try:
            async with asyncio.timeout(timeout):
                async with self.client.responses.with_streaming_response.create(**payload, timeout=timeout) as raw:
                    body = bytearray()
                    async for chunk in raw.iter_bytes():
                        body.extend(chunk)
                        if len(body) > self.transport.limit:
                            raise ProviderError('provider_incomplete')
                    response = json.loads(body)
                    request_id = raw.headers.get('x-request-id')
        except ProviderError:
            raise
        except APIStatusError as exc:
            if self.transport.exceeded:
                raise ProviderError('provider_incomplete') from None
            code = ('provider_access' if exc.status_code in (401, 403) else
                    'unsupported_capability' if exc.status_code in (400, 404, 422) else 'provider_failure')
            provider_code = getattr(exc, 'code', None)
            quota = (isinstance(provider_code, str) and provider_code in QUOTA_CODES
                     or getattr(exc, 'type', None) == 'insufficient_quota')
            retryable = (exc.status_code == 429 or exc.status_code >= 500) and not quota
            try:
                delay = float(exc.response.headers.get('retry-after', '0'))
            except ValueError:
                delay = 3  # Fail rather than ignore an unbounded/unparseable delay.
            reason = 'quota_exhausted' if quota else 'rate_limit' if exc.status_code == 429 else 'http_error'
            raise ProviderError(code, retryable=retryable, retry_after=delay,
                diagnostic=dict(reason=reason, http_status=exc.status_code, provider_code=provider_code)) from None
        except (APIConnectionError, APITimeoutError) as exc:
            if self.transport.input_exceeded:
                raise ProviderError('budget_exhausted') from None
            if self.transport.exceeded:
                raise ProviderError('provider_incomplete') from None
            reason = 'request_timeout' if isinstance(exc, APITimeoutError) else 'connection_error'
            raise ProviderError('provider_failure', retryable=True, outcome_unknown=True,
                                diagnostic=dict(reason=reason)) from None
        except TimeoutError:
            raise ProviderError('provider_failure', retryable=True, outcome_unknown=True,
                                diagnostic=dict(reason='request_timeout')) from None
        except (ValueError, TypeError):
            raise ProviderError('provider_incomplete') from None
        if not isinstance(response, dict) or not isinstance(response.get('output'), list):
            raise ProviderError('provider_incomplete')
        returned_model = response.get('model')
        if returned_model is not None and (not isinstance(returned_model, str) or not 1 <= len(returned_model) <= 200):
            raise ProviderError('provider_incomplete')
        if response.get('usage') is not None and not isinstance(response['usage'], dict):
            raise ProviderError('provider_incomplete')
        output = response['output']
        for item in output:
            if not isinstance(item, dict) or item.get('type') not in ('reasoning', 'message', 'function_call'):
                raise ProviderError('unsupported_capability')
            if item['type'] == 'message' and item.get('role') != 'assistant':
                raise ProviderError('unsupported_capability')
            if item['type'] == 'message':
                content = item.get('content')
                if not isinstance(content, list) or any(not isinstance(part, dict) for part in content):
                    raise ProviderError('provider_incomplete')
                if any(part.get('type') == 'output_text' and not isinstance(part.get('text'), str) for part in content):
                    raise ProviderError('provider_incomplete')
        self.history, self.seen = pending + copy.deepcopy(output), len(messages)
        meta = dict(private_items=tuple(output), returned_model=response.get('model'),
                    request_id=request_id or response.get('id'), usage=response.get('usage'))
        if response.get('status') == 'incomplete':
            return Turn('incomplete', **meta)
        if response.get('status') != 'completed':
            raise ProviderError('provider_failure')
        calls, texts = [], []
        for item in output:
            if item['type'] == 'function_call':
                try:
                    arguments = json.loads(item['arguments'])
                    if not isinstance(arguments, dict):
                        raise ValueError()
                    calls.append(dict(call_id=item['call_id'], name=item['name'], arguments=arguments))
                except (ValueError, KeyError, TypeError):
                    raise ProviderError('output_invalid') from None
            elif item['type'] == 'message':
                for content in item.get('content', []):
                    if content.get('type') == 'refusal':
                        return Turn('refusal', **meta)
                    if content.get('type') == 'output_text':
                        texts.append(content['text'])
        if calls:
            return Turn('tools', calls=tuple(calls), **meta)
        try:
            draft = json.loads(''.join(texts))
        except (ValueError, TypeError):
            draft = {}  # Local validator rejects; one application-owned repair may follow.
        return Turn('draft', draft=draft, **meta)

    async def aclose(self):
        await self.client.close()


class Provider(Protocol):
    async def next_turn(self, conversation, tools, report_schema, remaining_limits): ...


@dataclass(frozen=True)
class Turn:
    kind: str
    calls: tuple = ()
    draft: dict | None = None
    private_items: tuple = ()
    returned_model: str | None = None
    request_id: str | None = None
    usage: dict | None = None


class ProviderError(ValueError):
    def __init__(self, code, retryable=False, retry_after=0, outcome_unknown=False, diagnostic=None):
        super().__init__(code)
        self.code, self.retryable = code, retryable
        self.retry_after, self.outcome_unknown = retry_after, outcome_unknown
        self.diagnostic = safe_diagnostic(diagnostic)


def _keys(value, allowed, required=None):
    if not isinstance(value, dict) or not set(value) <= set(allowed):
        raise ProviderError('provider_input_invalid')
    if required is not None and not set(required) <= value.keys():
        raise ProviderError('provider_input_invalid')


def _provider_result(result):
    fields = ('status', 'evidence', 'returned_count', 'eligible_count', 'truncated')
    _keys(result, fields, fields)
    if len(canonical(result)) > 16000 or not isinstance(result['evidence'], list):
        raise ProviderError('provider_input_invalid')
    for item in result['evidence']:
        keys = ('evidence_id', 'kind', 'text', 'facts', 'returned_count', 'eligible_count', 'truncated')
        _keys(item, (*keys, 'provenance'), keys)
        validate('EvidenceId', item['evidence_id'])
        if item['kind'] not in ('case_fact', 'history', 'procedure') or not isinstance(item['text'], str):
            raise ProviderError('provider_input_invalid')
        for fact in item['facts']:
            validate('Fact', fact)
            if PRIVATE.search(fact['path']):
                raise ProviderError('provider_input_invalid')
        if 'provenance' in item:
            _keys(item['provenance'], ('doc_id', 'title', 'origin_kind', 'source_uri', 'published_at',
                'unknown_date_reason', 'retrieved_at', 'jurisdiction', 'version', 'content_sha256',
                'applicability_notes', 'reuse_terms', 'passage_id', 'section', 'corpus_version'))


def _deduplicate_history_facts(result):
    """Keep the exact history JSON and omit its redundant per-event fact entries."""
    from fraudlens.investigation.tools import facts

    for item in result['evidence']:
        if item['kind'] != 'history':
            continue
        try:
            history = json.loads(item['text'])
            if not isinstance(history, dict) or not isinstance(history.get('events'), list):
                continue
            source_facts = {(fact['path'], fact['value']) for fact in facts(history['events'], 'events')}
        except ValueError:
            continue
        event_facts = {(fact['path'], fact['value']) for fact in item['facts'] if fact['path'].startswith('events.')}
        if event_facts == source_facts:
            item['facts'] = [fact for fact in item['facts'] if not fact['path'].startswith('events.')]


def project_conversation(conversation):
    """Validate every turn, not merely initial context; private SDK items stay separate."""
    try:
        if not isinstance(conversation, list) or len(canonical(conversation)) > 48000:
            raise ProviderError('provider_input_invalid')
        result = copy.deepcopy(conversation)
        for item in result:
            if not isinstance(item, dict):
                raise ProviderError('provider_input_invalid')
            kind = item.get('type')
            if kind == 'context':
                _keys(item, ('type', 'data'), ('type', 'data'))
                data = item['data']
                keys = ('source_mode', 'notice', 'context_revision', 'case_id', 'transaction', 'assessment')
                if data.get('source_mode') == 'dataset' and 'context_contract_version' in data:
                    keys += ('context_contract_version',)
                _keys(data, keys, keys)
                if data['source_mode']=='dataset':
                    from fraudlens.investigation.context import validate_outbound_dataset
                    validate_outbound_dataset(data)
                    continue
                if data['source_mode'] != 'fixture':
                    raise ProviderError('context_unavailable')
                validate('Digest', data['context_revision'])
                validate('CaseId', data['case_id'])
                tx_keys = ('transaction_id', 'occurred_at', 'amount', 'currency', 'sender_alias', 'receiver_alias')
                _keys(data['transaction'], tx_keys, tx_keys)
                for side in ('sender', 'receiver'):
                    if not re.fullmatch(r'account_[0-9a-f]{24}', data['transaction'][side + '_alias']):
                        raise ProviderError('provider_input_invalid')
                risk_keys = ('score', 'source', 'scorer_version', 'scored_at', 'explanation')
                _keys(data['assessment'], risk_keys, risk_keys)
                if not math.isfinite(data['assessment']['score']):
                    raise ProviderError('provider_input_invalid')
            elif kind == 'tool_call':
                _keys(item, ('type', 'call_id', 'name', 'arguments'), ('call_id', 'name', 'arguments'))
                if not isinstance(item['arguments'], dict):
                    raise ProviderError('provider_input_invalid')
                for key in item['arguments']:
                    if key not in ('account_side', 'query'):
                        raise ProviderError('provider_input_invalid')
            elif kind == 'tool_result':
                _keys(item, ('type', 'call_id', 'result'), ('call_id', 'result'))
                _provider_result(item['result'])
            elif kind == 'repair':
                _keys(item, ('type', 'code', 'reason'), ('type', 'code'))
                if item['code'] != 'output_invalid':
                    raise ProviderError('provider_input_invalid')
                if 'reason' in item and (not isinstance(item['reason'], str)
                                        or item['reason'] not in REPAIR_HINTS):
                    raise ProviderError('provider_input_invalid')
            else:
                raise ProviderError('provider_input_invalid')
        return result
    except (ValueError, TypeError, KeyError, OverflowError):
        raise ProviderError('provider_input_invalid') from None


def _claim(ref, text, kind='observation', assertions=None):
    return dict(text=text, kind=kind, evidence_refs=[ref],
                exact_assertions=assertions or [], quotes=[])


def scripted_draft(conversation, scenario):
    items = [e for item in conversation if item['type'] == 'tool_result'
             for e in item['result']['evidence']]
    case = next((item for item in items if item['kind'] == 'case_fact'), None)
    draft = dict(outcome='needs_information', summary=[], observed_facts=[], risk_indicators=[],
        alternative_explanations=[], missing_information=['Zanimanje, uredjaj i poreklo sredstava nisu dostupni.'],
        recommended_checks=[], limitations=['TEST provider: autorski scenario, nije stvaran AI izvestaj.',
        'Sinteticki fixture skor nije kalibrisana verovatnoca; semanticki pregled nije obavljen.',
        HUMAN_AUTHORITY_NOTICE], citations=[])
    if scenario == 'needs_information' or case is None:
        draft['limitations'].append('Nema dovoljno dokaza za koristan zakljucak.')
        return validate('ReportDraft', draft)
    values = {fact['path']: fact['value'] for fact in case['facts']}
    dataset_case = (values.get('assessment.score_source') == 'model'
                    and 'transaction.paid.amount' in values)
    required = ('transaction.paid.amount', 'transaction.paid.currency') if dataset_case else (
        'transaction.amount', 'transaction.currency')
    if not all(key in values for key in required):
        return validate('ReportDraft', draft)
    ref = case['evidence_id']
    assertions = [dict(evidence_ref=ref, path=key, value=values[key]) for key in required]
    fact = _claim(ref, f"Zabelezena transakcija: {values[required[0]]} {values[required[1]]}.", assertions=assertions)
    draft.update(outcome='ready_for_review', summary=[copy.deepcopy(fact)], observed_facts=[fact], citations=[ref])
    if dataset_case:
        local_available = any(item['kind'] == 'case_fact' and any(
            fact['path'] == 'local_contribution_v1.method' and
            fact['value'] == 'lightgbm_pred_contrib_log_odds_v1' for fact in item['facts'])
            for item in items)
        draft['limitations'][1] = (
            'Sinteticki modelski risk score nije kalibrisana verovatnoca; '
            'lokalni doprinosi su na log-odds skali i nisu uzrocni nalaz.'
            if local_available else
            'Sinteticki modelski risk score nije kalibrisana verovatnoca; '
            'doprinosi modelskih obelezja nisu dostupni.')
    procedure = next((item for item in items if item['kind'] == 'procedure'), None)
    if procedure:
        draft['recommended_checks'] = [_claim(procedure['evidence_id'],
            'Pregledati nedostajuce podatke prema citiranoj edukativnoj proceduri.', 'procedure')]
        draft['citations'].append(procedure['evidence_id'])
    else:
        draft['limitations'].append('Nema odgovarajuce proceduralne smernice; nema takve preporuke.')
    if any(item['kind'] == 'history' and item['eligible_count'] is None for item in items):
        draft['limitations'].append('Istorija nije dostupna; to ne znaci da nije bilo aktivnosti.')
    if any(item['kind'] == 'history' and any(fact['path'] == 'coverage' and fact['value'] == 'incomplete'
           for fact in item['facts']) for item in items):
        draft['limitations'].append('Sedmodnevna istorija je nepotpuna u dostupnom sintetickom izvoru.')
    if scenario == 'invalid_citation':
        draft['summary'][0]['evidence_refs'] = ['ev_' + 'f' * 32]
    return validate('ReportDraft', draft)


class ScriptedProvider:
    def __init__(self, scenario='grounded', script_path=None):
        self.scenario, self.position = scenario, 0
        self.path = Path(script_path or ROOT / 'data/fixtures/investigation/provider-scripts.json')

    async def next_turn(self, conversation, tools, report_schema, remaining_limits):
        conversation = project_conversation(conversation)
        from fraudlens.investigation.tools import definitions
        if tools != definitions() or len(canonical(conversation)) > remaining_limits['max_input_bytes']:
            raise ProviderError('provider_input_invalid')
        try:
            if self.path.stat().st_size > remaining_limits['max_response_bytes']:
                raise ProviderError('provider_incomplete')
            scripts = json.loads(self.path.read_text(encoding='utf-8'))
            steps = scripts['scenarios'][self.scenario]
            step = steps[min(self.position, len(steps) - 1)]
            self.position += 1
            meta = dict(returned_model='authored-test-provider-v1',
                        request_id=f'test_request_{self.position}', usage=None)
            if 'tool' in step:
                call = dict(call_id=f'test_call_{self.position}', name=step['tool'], arguments=step['arguments'])
                return Turn('tools', calls=(call,), **meta)
            if 'outcome' in step:
                if step['outcome'] not in ('refusal', 'incomplete'):
                    raise ProviderError('provider_failure')
                return Turn(step['outcome'], **meta)
            draft = scripted_draft(conversation, step['draft'])
            if len(canonical(draft)) > remaining_limits['max_response_bytes']:
                raise ProviderError('provider_incomplete')
            return Turn('draft', draft=draft, **meta)
        except ProviderError:
            raise
        except (ValueError, KeyError, OSError, IndexError, TypeError):
            raise ProviderError('provider_failure') from None


async def probe_provider(settings, transport=None):
    """Opt-in synthetic capability check; never opens case/context/evaluation files."""
    if settings.max_provider_requests < 2:
        raise ProviderError('budget_exhausted')
    provider = OpenAIProvider(settings.api_key.get_secret_value(), settings.model.get_secret_value(),
        prompt='Synthetic capability probe only. Call get_case_facts, then return a needs_information report with no claims and a limitation. No real case exists.',
        transport=transport)
    sample = dict(source_mode='fixture', notice='Synthetic diagnostic; no case data.',
        context_revision='0' * 64, case_id='CASE-000',
        transaction=dict(transaction_id='TX-000',occurred_at='2026-01-01T00:00:00Z',
                         amount='0.00',currency='EUR',sender_alias='account_'+'0'*24,
                         receiver_alias='account_'+'1'*24),
        assessment=dict(score=0,source='fixture',scorer_version='synthetic-probe',
                        scored_at='2026-01-01T00:00:00Z',explanation='No actual assessment.'))
    from fraudlens.investigation.tools import definitions
    conversation = [dict(type='context',data=sample)]
    limits = dict(request_timeout=min(30,settings.request_timeout_seconds),max_input_bytes=settings.max_input_bytes,
                  max_output_tokens=settings.max_output_tokens,max_response_bytes=settings.max_response_bytes)
    try:
        async with asyncio.timeout(min(120,settings.total_timeout_seconds)):
            first = await provider.next_turn(conversation,definitions(),{},
                {**limits,'tool_choice':{'type':'function','name':'get_case_facts'}})
            if (first.kind != 'tools' or len(first.calls) != 1
                    or first.calls[0]['name'] != 'get_case_facts' or first.calls[0]['arguments'] != {}):
                raise ProviderError('unsupported_capability')
            call = first.calls[0]
            conversation.extend([dict(type='tool_call',**call),dict(type='tool_result',
                call_id=call['call_id'],result=dict(status='completed',evidence=[],
                returned_count=0,eligible_count=0,truncated=False))])
            second = await provider.next_turn(conversation,definitions(),{}, {**limits,'tool_choice':'none'})
            if second.kind != 'draft':
                raise ProviderError('unsupported_capability')
            draft = validate('ReportDraft', second.draft)
            if draft['outcome'] != 'needs_information' or draft['observed_facts'] or draft['citations']:
                raise ProviderError('unsupported_capability')
            return dict(status='capability_probe_passed',requested_model=settings.model.get_secret_value(),
                requests=[dict(request_id=t.request_id,returned_model=t.returned_model,usage=t.usage)
                          for t in (first,second)])
    except TimeoutError:
        raise ProviderError('budget_exhausted',outcome_unknown=True) from None
    finally:
        await provider.aclose()
