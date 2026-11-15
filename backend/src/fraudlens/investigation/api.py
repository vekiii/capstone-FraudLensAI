"""Read-only knowledge API, separate from foundation error handlers."""
import json
import re
import sqlite3
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from fraudlens.cases import CaseNotFoundError
from fraudlens.investigation.knowledge import KnowledgeStore, KnowledgeUnavailable
from fraudlens.investigation.models import validate
from fraudlens.investigation.retrieval import search
from fraudlens.investigation.settings import load_settings

router = APIRouter(prefix='/api/knowledge')
investigation_router = APIRouter(prefix='/api/investigation')


def error(status, code):
    messages = {'invalid_request': 'Invalid knowledge request.',
                'knowledge_unavailable': 'Knowledge search is not prepared.',
                'evidence_not_found': 'Knowledge evidence not found.',
                'internal_error': 'Investigation service unavailable.',
                'forbidden_scope': 'Request outside the local application scope.',
                'case_not_found': 'Case not found.',
                'investigation_not_found': 'Investigation not found.',
                'stale_snapshot': 'The source snapshot has changed. Refresh the case.',
                'request_conflict': 'Request identity already used for different input.',
                'revision_conflict': 'Saved revision changed. Refresh before another action.',
                'invalid_transition': 'Action is not allowed for this attempt state.',
                'context_unavailable': 'Selected source context unavailable.',
                'provider_unavailable': 'Provider configuration unavailable.',
                'store_busy': 'Investigation store is busy.'}
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


class RouteFailure(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code


def local_guard(request, mutation=False):
    host = urlsplit('http://' + request.headers.get('host', '')).hostname
    # testserver is TestClient's in-process host; production demo is loopback only.
    if host not in ('localhost', '127.0.0.1', '::1', 'testserver'):
        raise RouteFailure(403, 'forbidden_scope')
    if mutation:
        origin = request.headers.get('origin')
        if origin is not None and origin != f'{request.url.scheme}://{request.headers.get("host", "")}':
            raise RouteFailure(403, 'forbidden_scope')
        if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
            raise RouteFailure(422, 'invalid_request')


def get_investigation_service(request, reading_attempt=False):
    from fraudlens.investigation.workflow import InvestigationService
    settings = load_settings()
    if not settings.enabled or not settings.store.is_file():
        raise RouteFailure(404 if reading_attempt else 503,
                           'investigation_not_found' if reading_attempt else 'context_unavailable')
    service = getattr(request.app.state, 'investigation_service', None)
    if service is not None:
        return service
    knowledge = KnowledgeStore(settings.store, initialize=False)
    return InvestigationService(knowledge.repository, knowledge, settings)


def feature_exception(exc):
    if isinstance(exc, RouteFailure):
        return error(exc.status, exc.code)
    if isinstance(exc, CaseNotFoundError):
        return error(404, 'case_not_found')
    if isinstance(exc, KnowledgeUnavailable):
        return error(503, 'knowledge_unavailable')
    if isinstance(exc, sqlite3.OperationalError) and ('locked' in str(exc) or 'busy' in str(exc)):
        return error(503, 'store_busy')
    if isinstance(exc, ValueError):
        code = str(exc)
        if code in ('stale_snapshot', 'request_conflict', 'revision_conflict', 'invalid_transition'):
            return error(409, code)
        if code == 'provider_unavailable':
            return error(503, code)
        if code == 'Investigation not found':
            return error(404, 'investigation_not_found')
        if code.startswith('Dataset context unavailable'):
            return error(503, 'context_unavailable')
    return error(503, 'context_unavailable')


def query_keys(request, allowed):
    if set(request.query_params) - set(allowed) or any(
            len(request.query_params.getlist(k)) != 1 for k in request.query_params):
        raise RouteFailure(422, 'invalid_request')


@investigation_router.post('/runs')
async def create_run(request: Request):
    try:
        local_guard(request, mutation=True)
        query_keys(request, ())
        try:
            key = request.headers.get('idempotency-key', '')
            UUID(key)
            # Bound the input while receiving it, before JSON parsing.
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 4096:
                    raise ValueError('Oversized request')
            payload = validate('CreateRequest', json.loads(body))
        except (ValueError, TypeError):
            raise RouteFailure(422, 'invalid_request') from None
        service = get_investigation_service(request)
        if payload['source_mode'] != service.settings.source:
            raise RouteFailure(503, 'context_unavailable')
        result = service.create(payload, service.settings.analyst, key)
        return JSONResponse(result, status_code=202, headers={'ETag': str(result['revision'])})
    except (RouteFailure, ValueError, KeyError, OSError, sqlite3.Error, KnowledgeUnavailable, CaseNotFoundError) as exc:
        return feature_exception(exc)


@investigation_router.get('/runs')
def list_runs(request: Request):
    try:
        local_guard(request)
        query_keys(request, ('case_id', 'context_revision'))
        try:
            case_id = validate('CaseId', request.query_params.get('case_id'))
            revision = request.query_params.get('context_revision')
            if revision is not None:
                validate('Digest', revision)
        except ValueError:
            raise RouteFailure(422, 'invalid_request') from None
        service = get_investigation_service(request)
        context = service.context_reader.resolve(case_id, service.settings.source, None)
        if revision is not None and revision != context['context_revision']:
            raise RouteFailure(409, 'stale_snapshot')
        with service.repo.connection() as db:
            count = db.execute('SELECT count(*) FROM investigation_runs WHERE context_revision=?', (context['context_revision'],)).fetchone()[0]
            rows = db.execute('''SELECT attempt_id FROM attempts a WHERE context_revision=?
                              AND NOT EXISTS (SELECT 1 FROM attempts newer WHERE newer.run_id=a.run_id
                                AND (newer.created_at>a.created_at OR (newer.created_at=a.created_at AND newer.rowid>a.rowid)))
                              ORDER BY created_at DESC,run_id LIMIT 20''',
                              (context['context_revision'],)).fetchall()
        result = validate('RunList', dict(contract_version=1, total_count=count,
            truncated=count > 20, items=[service.read(row[0]) for row in rows]))
        return JSONResponse(result, headers={'X-Investigation-Snapshot': context['snapshot_ref'],
                                            'X-Investigation-Context': context['context_revision']})
    except (RouteFailure, ValueError, KeyError, OSError, sqlite3.Error, KnowledgeUnavailable, CaseNotFoundError) as exc:
        return feature_exception(exc)


@investigation_router.get('/attempts/{attempt_id}')
def read_attempt(request: Request, attempt_id: str):
    try:
        local_guard(request)
        query_keys(request, ())
        try:
            validate('AttemptId', attempt_id)
        except ValueError:
            raise RouteFailure(422, 'invalid_request') from None
        result = get_investigation_service(request, True).read(attempt_id)
        return JSONResponse(result, headers={'ETag': str(result['revision'])})
    except (RouteFailure, ValueError, KeyError, OSError, sqlite3.Error, KnowledgeUnavailable) as exc:
        return feature_exception(exc)


@investigation_router.get('/attempts/{attempt_id}/evidence/{evidence_id}')
def read_evidence(request: Request, attempt_id: str, evidence_id: str):
    try:
        local_guard(request)
        query_keys(request, ())
        try:
            validate('AttemptId', attempt_id)
            validate('EvidenceId', evidence_id)
        except ValueError:
            raise RouteFailure(422, 'invalid_request') from None
        service = get_investigation_service(request, True)
        try:
            item = next(item for item in service.evidence(attempt_id) if item['evidence_id'] == evidence_id)
        except (StopIteration, ValueError):
            raise RouteFailure(404, 'evidence_not_found') from None
        return JSONResponse(item)
    except (RouteFailure, ValueError, KeyError, OSError, sqlite3.Error, KnowledgeUnavailable) as exc:
        return feature_exception(exc)


async def recovery_action(request, attempt_id, operation):
    try:
        local_guard(request, mutation=True)
        query_keys(request, ())
        try:
            validate('AttemptId', attempt_id)
            key = request.headers.get('idempotency-key', '')
            UUID(key)
            revision = request.headers.get('if-match', '')
            if not re.fullmatch(r'[1-9][0-9]{0,15}', revision):
                raise ValueError('Invalid revision')
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 4096:
                    raise ValueError('Oversized request')
            payload = json.loads(body)
            if operation == 'retry':
                payload = validate('RetryRequest', payload)
            elif payload != {}:
                raise ValueError('Invalid cancel body')
        except (ValueError, TypeError):
            raise RouteFailure(422, 'invalid_request') from None
        service = get_investigation_service(request, True)
        if operation == 'retry':
            result = service.retry(attempt_id, int(revision), payload['reuse_evidence'], service.settings.analyst, key)
        else:
            result = service.cancel(attempt_id, int(revision), service.settings.analyst, key)
        return JSONResponse(result, status_code=202 if operation == 'retry' else 200,
                            headers={'ETag': str(result['revision'])})
    except (RouteFailure, ValueError, KeyError, OSError, sqlite3.Error, KnowledgeUnavailable, CaseNotFoundError) as exc:
        return feature_exception(exc)


@investigation_router.post('/attempts/{attempt_id}/retry')
async def retry_attempt(request: Request, attempt_id: str):
    return await recovery_action(request, attempt_id, 'retry')


@investigation_router.post('/attempts/{attempt_id}/cancel')
async def cancel_attempt(request: Request, attempt_id: str):
    return await recovery_action(request, attempt_id, 'cancel')


@investigation_router.api_route('/{unknown:path}', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def unknown_investigation(request: Request, unknown: str):
    return error(404, 'investigation_not_found')
