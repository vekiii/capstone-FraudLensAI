"""Explicit opt-in application adapter; caller owns durable dispatch budgets."""
from fraudlens.investigation.models import validate
from fraudlens.investigation.retrieval_semantic_v6 import (
    policy_identity,
    project_selection,
    request_payload,
    select_with_provider,
)


async def semantic_search(store, query, corpus, provider, reserve_dispatch):
    """Budget-accounted opt-in port for application adapters.

    The owning API/worker must supply its durable reservation callback; an
    insufficient or failed reservation never dispatches. Legacy search cannot
    silently activate this paid path. Exceptions remain failures, not no-match.
    """
    query = validate('SearchArguments', dict(query=query))['query']
    passages = store.passages(corpus)
    request_payload(query, passages, provider.model)  # bounds before reservation
    policy = policy_identity(provider.model, passages)
    reservation = await reserve_dispatch(dict(policy_version=policy, requested_model=provider.model,
                                               requests=1, timeout_seconds=30, output_tokens=2048))
    if not isinstance(reservation, str) or not reservation.strip() or len(reservation) > 120:
        raise ValueError('Durable semantic dispatch reservation required')
    selection, audit = await select_with_provider(provider, query, passages)
    return project_selection(query, passages, selection, corpus, policy), dict(
        reservation=reservation, selection=selection, **audit)
