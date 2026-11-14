"""Local fixture API with service-backed cases and closed public errors."""
import logging
import re
import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from fraudlens.cases import CaseNotFoundError, CaseScoringError, CaseService, FixtureLoadError
from fraudlens.contracts import CaseDetail, CaseList, Error, ErrorBody, Health
from fraudlens.data_contracts import CaseDetailV2, CaseListV2, HealthV2
from fraudlens.data_store import PublishedCaseNotFound, RunStore, RunUnavailable, StaleSnapshot
from fraudlens.scoring import FixtureScorer, Scorer
from fraudlens.settings import Settings, load_settings

logger = logging.getLogger(__name__)

_DATASET_ERRORS = {
    404: ('case_not_found', 'Case not found.'),
    409: ('stale_snapshot', 'Selected snapshot is no longer active.'),
    422: ('invalid_request', 'Invalid request.'),
    503: ('run_unavailable', 'Selected run is unavailable.'),
    500: ('internal_error', 'Internal server error.'),
}


def _dataset_error(status: int) -> JSONResponse:
    code, message = _DATASET_ERRORS[status]
    return JSONResponse(status_code=status,
                        content={'error': {'code': code, 'message': message}})


def _dataset_store(config: Settings) -> RunStore:
    if not config.run_store_path.is_file():
        raise RunUnavailable('no run store')
    return RunStore(config.run_store_path, read_only=True)


def _error_response(status_code: int, headers: dict[str, str] | None = None) -> JSONResponse:
    if status_code == 404:
        body = ErrorBody(code='case_not_found', message='Case not found.')
    elif status_code < 500:
        body = ErrorBody(code='invalid_request', message='Invalid request.')
    else:
        body = ErrorBody(code='internal_error', message='Internal server error.')
    return JSONResponse(status_code=status_code, headers=headers,
                        content=Error(error=body).model_dump(mode='json'))


def get_settings(request: Request) -> Settings:
    """Dependency override point scoped to this application instance."""
    return request.app.state.settings


def get_scorer(request: Request) -> Scorer:
    return request.app.state.scorer


def get_case_service(config: Annotated[Settings, Depends(get_settings)],
                     scorer: Annotated[Scorer, Depends(get_scorer)]) -> CaseService:
    return CaseService(config.fixture_path, scorer)


def create_app(settings: Settings | None = None, scorer: Scorer | None = None) -> FastAPI:
    app = FastAPI(title='FraudLens AI')
    app.state.settings = settings if settings is not None else load_settings()
    app.state.scorer = scorer if scorer is not None else FixtureScorer()

    @app.exception_handler(CaseNotFoundError)
    async def case_not_found(_request: Request, _exc: CaseNotFoundError) -> JSONResponse:
        return _error_response(404)

    @app.exception_handler(FixtureLoadError)
    @app.exception_handler(CaseScoringError)
    async def service_failure(_request: Request, exc: Exception) -> JSONResponse:
        logger.error('Case service failed (%s)', type(exc).__name__)
        return _error_response(500)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return _error_response(422)

    @app.exception_handler(ResponseValidationError)
    async def invalid_response(_request: Request, _exc: ResponseValidationError) -> JSONResponse:
        logger.error('Response contract validation failed')
        return _error_response(500)

    @app.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error('HTTP server error (%s)', exc.status_code)
        # Retain the framework's method-negotiation behavior, not debug headers.
        headers = None
        if exc.status_code == 405 and exc.headers and 'Allow' in exc.headers:
            headers = {'Allow': exc.headers['Allow']}
        return _error_response(exc.status_code, headers=headers)

    @app.exception_handler(Exception)
    async def server_error(_request: Request, exc: Exception) -> JSONResponse:
        # Starlette's ServerErrorMiddleware still re-raises after sending this
        # response. Programming errors remain observable; no fallback is used.
        logger.error('Unhandled application failure (%s)', type(exc).__name__)
        return _error_response(500)

    @app.get('/api/health', response_model=Health | HealthV2,
             responses={500: {'model': Error}})
    def health(config: Annotated[Settings, Depends(get_settings)]):
        if config.mode == 'fixture':
            return Health(status='ok', mode='fixture')
        try:
            store = _dataset_store(config)
            try:
                active = store.active_metadata(config.scorer)
            finally:
                store.close()
        except RunUnavailable:
            active = None
        except sqlite3.Error:
            return _dataset_error(500)
        return HealthV2.model_validate({
            'contract_version': 2, 'status': 'ok' if active else 'unavailable',
            'mode': 'dataset', 'data_source': 'ibm_aml_hi_small',
            'score_source': config.scorer,
            'dataset_version': active['dataset_version'] if active else None,
            'active_run_id': active['run_id'] if active else None})

    @app.get('/api/cases', response_model=CaseList | CaseListV2,
             responses={500: {'model': Error}})
    def case_list(config: Annotated[Settings, Depends(get_settings)],
                  service: Annotated[CaseService, Depends(get_case_service)]):
        if config.mode == 'fixture':
            return service.list_cases()
        try:
            store = _dataset_store(config)
            try:
                return CaseListV2.model_validate(store.list_active(config.scorer))
            finally:
                store.close()
        except RunUnavailable:
            return _dataset_error(503)
        except sqlite3.Error:
            return _dataset_error(500)

    @app.get('/api/cases/{case_id}', response_model=CaseDetail | CaseDetailV2,
             responses={404: {'model': Error}, 422: {'model': Error}, 500: {'model': Error}})
    def case_detail(case_id: str,
                    config: Annotated[Settings, Depends(get_settings)],
                    service: Annotated[CaseService, Depends(get_case_service)],
                    snapshot: str | None = None):
        if config.mode == 'fixture':
            if re.fullmatch(r'CASE-[0-9]{3}', case_id) is None:
                return _error_response(422)
            return service.get_case(case_id)
        if (re.fullmatch(r'C[0-9a-f]{32}', case_id) is None
                or snapshot is None
                or re.fullmatch(r'run_[A-Za-z0-9_-]{1,64}', snapshot) is None):
            return _dataset_error(422)
        try:
            store = _dataset_store(config)
            try:
                return CaseDetailV2.model_validate(
                    store.detail_active(config.scorer, snapshot, case_id))
            finally:
                store.close()
        except RunUnavailable:
            return _dataset_error(503)
        except StaleSnapshot:
            return _dataset_error(409)
        except PublishedCaseNotFound:
            return _dataset_error(404)
        except sqlite3.Error:
            return _dataset_error(500)

    return app


app = create_app()
