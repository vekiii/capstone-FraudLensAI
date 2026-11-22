"""Additive, label-free bridge for one frozen Feature 002 model publication."""

import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from fraudlens.data.features import FEATURE_VERSION
from fraudlens.scoring.model_scorer import (
    FEATURE_MANIFEST_SHA256,
    MODEL_SHA256,
    SOURCE_SHA256,
    THRESHOLD,
    valid_canonical_id,
)

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / 'specs/003-ai-investigation/contracts/model-case-bridge-v1.json').read_text())
VALIDATOR = Draft202012Validator({**SCHEMA, '$ref': '#/$defs/Binding'}, format_checker=FormatChecker())


def identity(canonical_id: str, kind: str) -> tuple[str, str]:
    """Return the public v2-shaped ID and full digest; never discard the latter."""
    if not valid_canonical_id(canonical_id) or kind not in ('case', 'tx'):
        raise ValueError('Invalid canonical identity')
    digest = hashlib.sha256(('fraudlens/bridge-v1/' + kind + '\0' + canonical_id).encode()).hexdigest()
    return ('C' if kind == 'case' else 'D') + digest[:32], digest


def validate_binding(value: dict, *, expected_run: str | None = None,
                     expected_score: float | None = None,
                     expected_event_time: str | None = None) -> dict:
    """Validate both JSON shape and cross-object/frozen semantic identity."""
    try:
        VALIDATOR.validate(value)
        canonical = value['canonical_transaction_id']
        case_id, case_digest = identity(canonical, 'case')
        tx_id, tx_digest = identity(canonical, 'tx')
        if (value['case_id'], value['case_digest'], value['transaction_id'],
                value['transaction_digest']) != (case_id, case_digest, tx_id, tx_digest):
            raise ValueError('Crosswalk mismatch')
        if (canonical.split(':')[1] != value['source_sha256']
                or value['source_sha256'] != SOURCE_SHA256
                or value['model_sha256'] != MODEL_SHA256
                or value['feature_manifest_sha256'] != FEATURE_MANIFEST_SHA256
                or value['feature_version'] != FEATURE_VERSION
                or value['threshold'] != THRESHOLD
                or value['risk_score'] < THRESHOLD
                or value['review_status'] != 'review_recommended'
                or not math.isfinite(value['risk_score'])
                or expected_run is not None and value['snapshot_ref'] != expected_run
                or expected_score is not None and value['risk_score'] != expected_score
                or expected_event_time is not None and value['event_time_utc'] != expected_event_time):
            raise ValueError('Frozen bridge mismatch')
    except Exception:
        raise ValueError('Invalid model case binding') from None
    return value


def validate_crosswalk(bindings: list[dict]) -> None:
    """Reject even engineered digest-prefix collisions before any publication."""
    by_canonical, by_case, by_tx = {}, {}, {}
    for binding in bindings:
        validate_binding(binding)
        canonical = binding['canonical_transaction_id']
        if canonical in by_canonical or binding['case_id'] in by_case or binding['transaction_id'] in by_tx:
            raise ValueError('Duplicate or colliding bridge identity')
        by_canonical[canonical] = binding
        by_case[binding['case_id']] = canonical
        by_tx[binding['transaction_id']] = canonical
