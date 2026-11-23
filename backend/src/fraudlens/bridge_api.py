"""Read-only model alert publication routes, separate from fixture cases."""

import os
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from fraudlens.bridge_reader import BridgeNotFound, BridgeReader, BridgeUnavailable
from fraudlens.investigation.contribution_sidecar import (
    SidecarInvalid,
    SidecarMissing,
    SidecarReader,
)
from fraudlens.investigation.environment import read_environment
from fraudlens.scoring.model_scorer import valid_canonical_id

router = APIRouter(prefix='/api/model/cases')


def _error(status, code):
    return JSONResponse(status_code=status, content={'error': {'code': code, 'message': {
        'invalid_request': 'Invalid model case request.',
        'case_not_found': 'Published model case not found.',
        'stale_snapshot': 'Published model run changed.',
        'run_unavailable': 'Published model cases unavailable.',
    }[code]}})


def _reader(request):
    if request.app.state.settings.mode != 'model':
        raise BridgeUnavailable('Model mode disabled')
    root = os.environ.get('MODEL_CASE_BRIDGE_ROOT')
    if not root:
        raise BridgeUnavailable('Bridge path not configured')
    return BridgeReader(Path(root), os.environ.get('MODEL_CASE_BRIDGE_MANIFEST_SHA256'))


def _response(request, operation, value=None):
    try:
        if operation == 'list' and request.query_params:
            return _error(422, 'invalid_request')
        if operation == 'binding' and (request.query_params or not valid_canonical_id(value)):
            return _error(422, 'invalid_request')
        if operation == 'detail' and (set(request.query_params) - {'snapshot'}
                or len(request.query_params.getlist('snapshot')) > 1):
            return _error(422, 'invalid_request')
        reader = _reader(request)
        if operation == 'binding':
            return reader.binding(value)
        if operation == 'list':
            return reader.list_cases()
        return reader.detail(value, request.query_params.get('snapshot'))
    except BridgeNotFound:
        return _error(404, 'case_not_found')
    except BridgeUnavailable:
        return _error(503, 'run_unavailable')
    except ValueError as exc:
        if str(exc) == 'stale_snapshot':
            return _error(409, 'stale_snapshot')
        return _error(503, 'run_unavailable')
    except (OSError, KeyError, TypeError):
        return _error(503, 'run_unavailable')


@router.get('/by-transaction/{transaction_id}')
def binding(request: Request, transaction_id: str):
    return _response(request, 'binding', transaction_id)


@router.get('')
def listing(request: Request):
    return _response(request, 'list')


@router.get('/{case_id}')
def detail(request: Request, case_id: str):
    return _response(request, 'detail', case_id)


@router.get('/{case_id}/local-contributions')
def local_contributions(request: Request, case_id: str):
    """Separate experimental sidecar; never changes the v2 case response."""
    if request.query_params:
        return _error(422, 'invalid_request')
    try:
        reader = _reader(request)
        context = reader.resolve(case_id, None)
        binding = reader._binding(case_id=case_id)
    except BridgeNotFound:
        return _error(404, 'case_not_found')
    except (BridgeUnavailable, ValueError, OSError, KeyError):
        return _error(503, 'run_unavailable')
    config = read_environment()
    path, pin = config.get('INVESTIGATION_LOCAL_CONTRIBUTION_PATH'), config.get('INVESTIGATION_LOCAL_CONTRIBUTION_SHA256')
    if not path and not pin:
        return {'contract_version': 1, 'status': 'unavailable', 'reason_code': 'not_configured'}
    if not path or not pin:
        return {'contract_version': 1, 'status': 'invalid', 'reason_code': 'verification_failed'}
    try:
        source = Path(path)
        if not source.is_absolute():
            source = Path(__file__).resolve().parents[3] / source
        return SidecarReader(source, pin).read(binding, context)
    except SidecarMissing:
        return {'contract_version': 1, 'status': 'unavailable', 'reason_code': 'missing_artifact'}
    except SidecarInvalid:
        return {'contract_version': 1, 'status': 'invalid', 'reason_code': 'verification_failed'}
