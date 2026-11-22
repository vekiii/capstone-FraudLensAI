"""Local case API and opt-in read-only model assessment."""
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from fraudlens.cases import CaseNotFoundError, CaseScoringError, CaseService, FixtureLoadError
from fraudlens.contracts import (
    CaseDetail,
    CaseId,
    CaseList,
    EdaError,
    EdaErrorBody,
    EdaSummary,
    Error,
    ErrorBody,
    Health,
    ModelHealth,
    ModelResults,
    PredictionResult,
    ResultsError,
    ResultsErrorBody,
    RiskError,
    RiskErrorBody,
)
from fraudlens.eda.service import EdaService, EdaUnavailable
from fraudlens.investigation.api import error as investigation_error
from fraudlens.investigation.api import investigation_router
from fraudlens.investigation.api import router as knowledge_router
from fraudlens.scoring import FixtureScorer, Scorer
from fraudlens.scoring.model_scorer import (
    FeatureStore,
    ModelScorer,
    ModelUnavailable,
    valid_canonical_id,
)
from fraudlens.settings import Settings, load_settings
from fraudlens.training.results import ResultsNotAuthorized, ResultsService, ResultsUnavailable

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


def _risk_error(status: int, code: str, message: str) -> JSONResponse:
    body = RiskError(error=RiskErrorBody(code=code, message=message))
    return JSONResponse(status_code=status, content=body.model_dump(mode='json'))


def _results_error(status: int, code: str, message: str) -> JSONResponse:
    body = ResultsError(error=ResultsErrorBody(code=code, message=message))
    return JSONResponse(status_code=status, content=body.model_dump(mode='json'))


def _eda_error(status: int, code: str, message: str) -> JSONResponse:
    body = EdaError(error=EdaErrorBody(code=code, message=message))
    return JSONResponse(status_code=status,
                        content=body.model_dump(mode='json'))


def create_app(settings: Settings | None = None, scorer: Scorer | None = None,
               model_scorer: ModelScorer | None = None,
               feature_store: FeatureStore | None = None,
               results_service: ResultsService | None = None,
               eda_service: EdaService | None = None) -> FastAPI:
    app = FastAPI(title='FraudLens AI')
    app.include_router(knowledge_router)
    app.include_router(investigation_router)
    app.state.settings = settings if settings is not None else load_settings()
    app.state.scorer = scorer if scorer is not None else FixtureScorer()
    app.state.model_scorer = model_scorer
    app.state.feature_store = feature_store
    app.state.results_service = results_service if results_service is not None else ResultsService()
    app.state.eda_service = eda_service if eda_service is not None else EdaService(
        app.state.settings.eda_summary_path, app.state.settings.eda_summary_sha256,
    )
    if app.state.settings.mode == 'model':
        try:
            if app.state.model_scorer is None:
                app.state.model_scorer = ModelScorer(app.state.settings.model_artifact_root)
            if app.state.feature_store is None:
                app.state.feature_store = FeatureStore(app.state.settings.model_feature_root)
        except ModelUnavailable:
            logger.error('Opt-in model inputs are unavailable or incompatible')
            app.state.model_scorer = None
            app.state.feature_store = None

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
    async def server_error(request: Request, exc: Exception) -> JSONResponse:
        # Starlette's ServerErrorMiddleware still re-raises after sending this
        # response. Programming errors remain observable; no fallback is used.
        logger.error('Unhandled application failure (%s)', type(exc).__name__)
        if request.url.path.startswith(('/api/investigation/', '/api/knowledge/')):
            return investigation_error(500, 'internal_error')
        return _error_response(500)

    @app.get('/api/health', response_model=Health | ModelHealth,
             responses={500: {'model': Error}})
    def health(config: Annotated[Settings, Depends(get_settings)]) -> Health | ModelHealth:
        if config.mode == 'model':
            return ModelHealth(status='ok', mode='model')
        return Health(status='ok', mode='fixture')

    @app.get('/api/cases', response_model=CaseList, responses={500: {'model': Error}})
    def case_list(service: Annotated[CaseService, Depends(get_case_service)]) -> CaseList:
        return service.list_cases()

    @app.get('/api/cases/{case_id}', response_model=CaseDetail,
             responses={404: {'model': Error}, 422: {'model': Error}, 500: {'model': Error}})
    def case_detail(case_id: CaseId,
                    service: Annotated[CaseService, Depends(get_case_service)]) -> CaseDetail:
        return service.get_case(case_id)

    @app.get('/api/transactions/{transaction_id}/risk', response_model=PredictionResult,
             responses={404: {'model': RiskError}, 409: {'model': RiskError},
                        422: {'model': RiskError}, 503: {'model': RiskError}})
    def transaction_risk(transaction_id: str):
        if len(transaction_id) > 160 or not valid_canonical_id(transaction_id):
            return _risk_error(422, 'invalid_request', 'Invalid transaction identifier.')
        if app.state.settings.mode != 'model' or app.state.model_scorer is None or app.state.feature_store is None:
            return _risk_error(503, 'model_unavailable', 'Model assessment is unavailable.')
        try:
            record = app.state.feature_store.get(transaction_id)
            if record is None:
                return _risk_error(404, 'transaction_not_found', 'Transaction not found.')
            if not record.is_scoreable:
                return _risk_error(409, 'transaction_ineligible', 'Transaction is not scoreable.')
            if record.transaction_id != transaction_id:
                raise ModelUnavailable('transaction identity mismatch')
            result = app.state.model_scorer.score(record)
            if (not isinstance(result, PredictionResult)
                    or result.transaction_id != transaction_id):
                raise ModelUnavailable('model output identity mismatch')
            return PredictionResult.model_validate(vars(result), strict=True)
        except ModelUnavailable:
            logger.error('Opt-in model assessment failed')
            return _risk_error(503, 'model_unavailable', 'Model assessment is unavailable.')

    @app.get('/api/model/results', response_model=ModelResults,
             responses={404: {'model': ResultsError}, 409: {'model': ResultsError},
                        422: {'model': ResultsError}, 500: {'model': ResultsError}})
    def model_results(request: Request):
        if request.query_params:
            return _results_error(422, 'invalid_request', 'Results query is not permitted.')
        if app.state.settings.mode != 'model':
            return _results_error(409, 'evaluation_not_authorized',
                                  'Model results require local model mode.')
        try:
            return app.state.results_service.load()
        except ResultsNotAuthorized:
            return _results_error(409, 'evaluation_not_authorized',
                                  'Test evaluation is not authorized.')
        except ResultsUnavailable:
            logger.error('Frozen aggregate results unavailable or incompatible')
            return _results_error(404, 'results_unavailable', 'Model results are unavailable.')

    @app.get('/api/eda/summary', response_model=EdaSummary,
             responses={404: {'model': EdaError}, 422: {'model': EdaError},
                        500: {'model': EdaError}})
    def eda_summary(request: Request):
        if request.query_params:
            return _eda_error(422, 'invalid_request', 'EDA query is not permitted.')
        try:
            return app.state.eda_service.load()
        except EdaUnavailable:
            logger.error('Trusted EDA aggregate is unavailable or incompatible')
            return _eda_error(404, 'dataset_unavailable', 'EDA summary is unavailable.')

    return app


app = create_app()
