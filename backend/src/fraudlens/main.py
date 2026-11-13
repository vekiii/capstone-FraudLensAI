"""Local fixture API with service-backed cases and closed public errors."""
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from fraudlens.cases import CaseNotFoundError, CaseScoringError, CaseService, FixtureLoadError
from fraudlens.contracts import CaseDetail, CaseId, CaseList, Error, ErrorBody, Health
from fraudlens.scoring import FixtureScorer, Scorer
from fraudlens.settings import Settings, load_settings

logger = logging.getLogger(__name__)


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

    @app.get('/api/health', response_model=Health, responses={500: {'model': Error}})
    def health(config: Annotated[Settings, Depends(get_settings)]) -> Health:
        return Health(status='ok', mode=config.mode)

    @app.get('/api/cases', response_model=CaseList, responses={500: {'model': Error}})
    def case_list(service: Annotated[CaseService, Depends(get_case_service)]) -> CaseList:
        return service.list_cases()

    @app.get('/api/cases/{case_id}', response_model=CaseDetail,
             responses={404: {'model': Error}, 422: {'model': Error}, 500: {'model': Error}})
    def case_detail(case_id: CaseId,
                    service: Annotated[CaseService, Depends(get_case_service)]) -> CaseDetail:
        return service.get_case(case_id)

    return app


app = create_app()
