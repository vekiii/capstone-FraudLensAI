"""Replaceable provider boundary; no client/network work during import."""
import copy
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from fraudlens.investigation.models import canonical, validate

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = re.compile(r'label|laundering|isfraud|reference.answer|source.path|source.row|reviewer', re.I)


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
    def __init__(self, code, retryable=False, retry_after=0, outcome_unknown=False):
        super().__init__(code)
        self.code, self.retryable = code, retryable
        self.retry_after, self.outcome_unknown = retry_after, outcome_unknown


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
                _keys(data, keys, keys)
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
                _keys(item, ('type', 'code'), ('type', 'code'))
                if item['code'] != 'output_invalid':
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
        'Sinteticki fixture skor nije kalibrisana verovatnoca; semanticki pregled nije obavljen.'], citations=[])
    if scenario == 'needs_information' or case is None:
        draft['limitations'].append('Nema dovoljno dokaza za koristan zakljucak.')
        return validate('ReportDraft', draft)
    values = {fact['path']: fact['value'] for fact in case['facts']}
    required = ('transaction.amount', 'transaction.currency')
    if not all(key in values for key in required):
        return validate('ReportDraft', draft)
    ref = case['evidence_id']
    assertions = [dict(evidence_ref=ref, path=key, value=values[key]) for key in required]
    fact = _claim(ref, f"Zabelezena transakcija: {values[required[0]]} {values[required[1]]}.", assertions=assertions)
    draft.update(outcome='ready_for_review', summary=[copy.deepcopy(fact)], observed_facts=[fact], citations=[ref])
    procedure = next((item for item in items if item['kind'] == 'procedure'), None)
    if procedure:
        draft['recommended_checks'] = [_claim(procedure['evidence_id'],
            'Pregledati nedostajuce podatke prema citiranoj edukativnoj proceduri.', 'procedure')]
        draft['citations'].append(procedure['evidence_id'])
    else:
        draft['limitations'].append('Nema odgovarajuce proceduralne smernice; nema takve preporuke.')
    if any(item['kind'] == 'history' and item['eligible_count'] is None for item in items):
        draft['limitations'].append('Istorija nije dostupna; to ne znaci da nije bilo aktivnosti.')
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
        except (ValueError, KeyError, OSError, IndexError, TypeError):
            raise ProviderError('provider_failure') from None
