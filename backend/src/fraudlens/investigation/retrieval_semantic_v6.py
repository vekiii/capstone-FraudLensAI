"""Explicit bounded async semantic port; never hidden inside legacy search."""
import asyncio
import json

from jsonschema import Draft202012Validator

from fraudlens.investigation.models import ROOT, canonical, digest, validate
from fraudlens.investigation.retrieval import SearchResult

SCHEMA = dict(type='object', additionalProperties=False,
    required=['verdict', 'reason', 'selected'], properties=dict(
        verdict=dict(type='string', enum=['supported', 'insufficient']),
        reason=dict(type='string', minLength=1, maxLength=1000),
        selected=dict(type='array', maxItems=5, items=dict(type='object', additionalProperties=False,
            required=['passage_id', 'quote'], properties=dict(
                passage_id=dict(type='string', minLength=1, maxLength=100),
                quote=dict(type='string', minLength=1, maxLength=1200))))))


def validate_selection(value, passages):
    try:
        Draft202012Validator(SCHEMA).validate(value)
        selected = value['selected']
        if bool(selected) != (value['verdict'] == 'supported'):
            raise ValueError('Inconsistent semantic verdict')
        allowed = {p['passage_id']: p['text'] for p in passages}
        ids = []
        for item in selected:
            identity, quote = item['passage_id'], item['quote']
            if identity not in allowed or identity in ids or not quote.strip() or quote not in allowed[identity]:
                raise ValueError('Unauthorized citation or altered quote')
            ids.append(identity)
        return ids
    except Exception:
        raise ValueError('Invalid semantic selection') from None


def profile_prompt(profile='v6'):
    if profile not in ('v6', 'v7'):
        raise ValueError('Unknown semantic profile')
    return (ROOT / f'prompts/application/retrieval-answerability-{profile}.md').read_text(encoding='utf-8')


def request_payload(query, passages, model, *, profile='v6'):
    query = validate('SearchArguments', dict(query=query))['query']
    if not isinstance(model, str) or not model.strip() or len(model) > 200:
        raise ValueError('Explicit semantic model required')
    if not 1 <= len(passages) <= 20 or len({p['passage_id'] for p in passages}) != len(passages):
        raise ValueError('Semantic candidate pool unavailable/oversize')
    sources = [dict(passage_id=p['passage_id'], text=p['text'],
                    title=p['document']['title'], jurisdiction=p['document']['jurisdiction'],
                    version=p['document']['version'], published_at=p['document']['published_at']) for p in passages]
    prompt = profile_prompt(profile)
    payload = dict(model=model, store=False, max_output_tokens=2048,
                   instructions=prompt, input=canonical(dict(question=query, passages=sources)).decode(),
                   text=dict(format=dict(type='json_schema', name='answerability_v6', strict=True, schema=SCHEMA)))
    if len(canonical(payload)) > 48000:
        raise ValueError('Semantic input exceeds byte budget')
    return payload


async def select_with_provider(provider, query, passages, *, profile='v6'):
    """Caller MUST reserve dispatch in its ledger before invoking; zero retries."""
    payload = request_payload(query, passages, provider.model, profile=profile)
    async with asyncio.timeout(30):
        response = await provider.client.responses.create(**payload, timeout=30)
    raw = response.model_dump(mode='json')
    if len(canonical(raw)) > 2097152 or raw.get('status') != 'completed':
        raise ValueError('Semantic response incomplete/oversize')
    parts = [part for output in raw.get('output', []) if output.get('type') == 'message'
             for part in output.get('content', [])]
    if any(p.get('type') == 'refusal' for p in parts):
        raise ValueError('Semantic provider refusal')
    texts = [p['text'] for p in parts if p.get('type') == 'output_text']
    if len(texts) != 1:
        raise ValueError('Semantic response format unavailable')
    selection = json.loads(texts[0])
    validate_selection(selection, passages)
    return selection, dict(requested_model=provider.model, returned_model=raw.get('model'),
                            request_id=raw.get('id'), usage=raw.get('usage'), raw_response=raw)


def project_selection(query, passages, selection, corpus, policy_version):
    ids = validate_selection(selection, passages)
    by_id = {p['passage_id']: p for p in passages}
    result = SearchResult(validate('SearchResult', dict(contract_version=1, corpus_version=corpus,
        retrieval_version=policy_version, query=query, status='matched' if ids else 'no_match',
        hits=[dict(rank=i + 1, score=1 / (i + 1), passage=by_id[identity]) for i, identity in enumerate(ids)])))
    # Rank weights are ordering weights, NOT probabilities or model confidence.
    return result


def policy_identity(model, passages, *, profile='v6'):
    return digest(dict(version='semantic_answerability_' + profile, model=model, schema=SCHEMA,
        prompt=profile_prompt(profile),
        passages=digest(passages), max_requests_per_search=1, sdk_retries=0,
        timeout_seconds=30, input_bytes=48000, output_tokens=2048))
