"""Capture SDK output before strict parsing without mutating provider/client state."""
from types import SimpleNamespace

from fraudlens.investigation.models import canonical
from fraudlens.investigation.retrieval_semantic_v6 import select_with_provider


async def audited_selection(provider, query, passages, capture, *, profile='v6'):
    async def create(**payload):
        response = await provider.client.responses.create(**payload)
        raw = response.model_dump(mode='json')
        if len(canonical(raw)) > 2097152:
            raise ValueError('Semantic response exceeds audit cap')
        capture(raw)  # exact response retained even when citation/schema check fails
        return response
    proxy = SimpleNamespace(model=provider.model, client=SimpleNamespace(
        responses=SimpleNamespace(create=create)))
    return await select_with_provider(proxy, query, passages, **({'profile': profile} if profile != 'v6' else {}))
