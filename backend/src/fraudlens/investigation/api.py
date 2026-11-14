"""Read-only knowledge API, separate from foundation error handlers."""
import sqlite3

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from fraudlens.investigation.knowledge import KnowledgeStore, KnowledgeUnavailable
from fraudlens.investigation.models import validate
from fraudlens.investigation.retrieval import search
from fraudlens.investigation.settings import load_settings

router = APIRouter(prefix='/api/knowledge')


def error(status, code):
    messages = {'invalid_request': 'Invalid knowledge request.',
                'knowledge_unavailable': 'Knowledge search is not prepared.',
                'evidence_not_found': 'Knowledge evidence not found.',
                'internal_error': 'Knowledge service unavailable.'}
    return JSONResponse(status_code=status, content=validate('ErrorEnvelope', dict(
        contract_version=1, error=dict(code=code, message=messages[code], retryable=status >= 500))))


def respond(request, operation, passage_id=None):
    try:
        allowed = {'corpus', 'retrieval', 'q'} if operation == 'search' else {'corpus'}
        if set(request.query_params) - allowed or any(len(request.query_params.getlist(k)) != 1 for k in request.query_params):
            raise ValueError('Invalid query keys')
        query = validate('SearchArguments', {'query': request.query_params.get('q', '')})['query'] if operation == 'search' else None
        corpus = request.query_params.get('corpus')
        retrieval = request.query_params.get('retrieval')
        if corpus is not None:
            if not corpus.startswith('corpus_'):
                raise ValueError('Invalid corpus identity')
            validate('Digest', corpus[7:])
        if retrieval is not None:
            validate('Digest', retrieval)
        if passage_id is not None:
            validate('Digest', passage_id)
    except ValueError:
        return error(422, 'invalid_request')
    try:
        settings = load_settings()
        if not settings.enabled:
            raise KnowledgeUnavailable('Disabled')
        store = getattr(request.app.state, 'knowledge_store', None)
        if store is None:
            if not settings.store.is_file():
                raise KnowledgeUnavailable('Missing store')
            store = KnowledgeStore(settings.store, initialize=False)
        corpus = corpus or store.latest('corpus')
        if operation == 'documents':
            payload = validate('DocumentList', dict(contract_version=1, corpus_version=corpus,
                                                    documents=store.corpus(corpus)['documents']))
        elif operation == 'passage':
            payload = store.passage(corpus, passage_id)
        else:
            payload = search(store, query, corpus, retrieval or store.latest('retrieval'))
            return JSONResponse(payload, headers={'X-Results-Truncated': str(payload.truncated).lower()})
        return JSONResponse(payload)
    except KeyError:
        return error(404, 'evidence_not_found')
    except (KnowledgeUnavailable, ValueError, OSError, sqlite3.Error):
        return error(503, 'knowledge_unavailable')


@router.get('/documents')
def documents(request: Request):
    return respond(request, 'documents')


@router.get('/search')
def search_route(request: Request):
    return respond(request, 'search')


@router.get('/passages/{passage_id}')
def passage(request: Request, passage_id: str):
    return respond(request, 'passage', passage_id)


@router.get('/{unknown:path}')
def unknown(request: Request, unknown: str):
    return error(404, 'evidence_not_found')
