"""Optional, independently pinned local contributions for frozen model alerts.

The v2 assessment and context remain authoritative for the score. This file is
never used by the scoring path. A sidecar is accepted only against a trusted
file pin and the exact bridge/context identities.
"""

import hashlib
import json
import math
import re
from pathlib import Path

from fraudlens.data.features import FEATURE_ORDER
from fraudlens.investigation.models import canonical
from fraudlens.scoring.model_scorer import MANIFEST_SHA256, MODEL_SHA256

METHOD = 'lightgbm_pred_contrib_log_odds_v1'
MATRIX_ORDER_SHA256 = '783b54d4289abedbba1b678bc44c4ec000347353e250c6471a5f589563af2b82'


def _stable_score(raw):
    if raw >= 0:
        return 1.0 / (1.0 + math.exp(-raw))
    value = math.exp(raw)
    return value / (1.0 + value)


def build_sidecar(binding, context, calculation, features):
    """Create a bounded summary from all 11 verified local groups."""
    groups = calculation['groups']
    matrix = calculation['matrix_contributions']
    if (set(groups) != set(FEATURE_ORDER) or len(matrix) != 32
            or any(type(value) not in (int, float) or not math.isfinite(value)
                   for value in [*groups.values(), *matrix])
            or abs(math.fsum(groups.values()) - math.fsum(matrix)) > 1e-8):
        raise SidecarInvalid('Invalid source grouping')
    ordered = sorted(groups, key=lambda key: (-abs(groups[key]), key))
    if abs(math.fsum(groups[key] for key in ordered[3:]) - calculation['remainder']) > 1e-8:
        raise SidecarInvalid('Invalid omitted remainder')
    items = []
    for key in ordered[:3]:
        value = features[key]
        unit = ('log1p_source_amount' if key == 'current_amount_paid_log1p' else
                'category' if key in ('current_payment_currency', 'current_payment_format') else
                'same_currency_amount' if 'sum_' in key else 'count')
        items.append(dict(feature_key=key, observed_value=str(value), unit=unit,
                          direction='increases' if groups[key] > 0 else
                                    'decreases' if groups[key] < 0 else 'neutral',
                          contribution=groups[key]))
    sidecar = dict(contract_version=1, status='available', method=METHOD,
        explained_scale='log_odds', objective=calculation['objective'],
        num_iteration=calculation['num_iteration'],
        canonical_transaction_id=binding['canonical_transaction_id'],
        transaction_id=binding['transaction_id'], case_id=binding['case_id'],
        assessment_run_id=binding['snapshot_ref'], dataset_version=binding['dataset_version'],
        context_revision=context['context_revision'], model_sha256=MODEL_SHA256,
        manifest_sha256=MANIFEST_SHA256, feature_version=binding['feature_version'],
        matrix_feature_order_sha256=MATRIX_ORDER_SHA256,
        feature_snapshot_digest=context['source_payload']['risk_assessment']['explanation']['feature_snapshot_digest'],
        score=calculation['score'], raw_score=calculation['raw_score'],
        base_value=calculation['base_value'], partial=True, items=items,
        remainder=calculation['remainder'])
    sidecar['evidence_digest'] = hashlib.sha256(canonical(sidecar)).hexdigest()
    return _check(sidecar, binding, context)


class SidecarInvalid(ValueError):
    pass


class SidecarMissing(ValueError):
    pass


def _check(sidecar, binding, context):
    try:
        expected = {
            'contract_version': 1, 'status': 'available', 'method': METHOD,
            'explained_scale': 'log_odds', 'objective': 'binary sigmoid:1',
            'num_iteration': 140, 'canonical_transaction_id': binding['canonical_transaction_id'],
            'transaction_id': binding['transaction_id'], 'case_id': binding['case_id'],
            'assessment_run_id': binding['snapshot_ref'],
            'dataset_version': binding['dataset_version'],
            'context_revision': context['context_revision'],
            'model_sha256': MODEL_SHA256, 'manifest_sha256': MANIFEST_SHA256,
            'feature_version': binding['feature_version'],
            'feature_snapshot_digest': context['source_payload']['risk_assessment']['explanation']['feature_snapshot_digest'],
            'partial': True,
        }
        for key, value in expected.items():
            if type(sidecar.get(key)) is not type(value) or sidecar[key] != value:
                raise SidecarInvalid('Sidecar identity or method mismatch')
        if set(sidecar) != set(expected) | {'matrix_feature_order_sha256', 'score', 'raw_score',
                'base_value', 'items', 'remainder', 'evidence_digest'}:
            raise SidecarInvalid('Unexpected sidecar field')
        order = sidecar['matrix_feature_order_sha256']
        if not isinstance(order, str) or not re.fullmatch(r'[0-9a-f]{64}', order):
            raise SidecarInvalid('Invalid matrix identity')
        # This digest identifies the trusted manifest's ordered columns, not
        # generic names supplied by LightGBM.
        # Fixed digest of the ordered columns in the trusted frozen manifest.
        if order != MATRIX_ORDER_SHA256:
            raise SidecarInvalid('Matrix feature order mismatch')
        numbers = [sidecar[key] for key in ('score', 'raw_score', 'base_value', 'remainder')]
        items = sidecar['items']
        if not isinstance(items, list) or len(items) != 3:
            raise SidecarInvalid('Invalid top three')
        names = []
        for item in items:
            if set(item) != {'feature_key', 'observed_value', 'unit', 'direction', 'contribution'}:
                raise SidecarInvalid('Invalid contribution item')
            name, value = item['feature_key'], item['contribution']
            if (not isinstance(name, str) or name not in FEATURE_ORDER or name in names
                    or not isinstance(item['observed_value'], str) or type(value) not in (int, float)):
                raise SidecarInvalid('Invalid contribution item')
            names.append(name)
            unit = ('log1p_source_amount' if name == 'current_amount_paid_log1p' else
                    'category' if name in ('current_payment_currency', 'current_payment_format') else
                    'same_currency_amount' if 'sum_' in name else 'count')
            if item['unit'] != unit:
                raise SidecarInvalid('Contribution unit mismatch')
            if item['direction'] != ('increases' if value > 0 else 'decreases' if value < 0 else 'neutral'):
                raise SidecarInvalid('Invalid contribution direction')
            numbers.append(value)
        if names != sorted(names, key=lambda name: (-abs(next(item['contribution'] for item in items
                                                            if item['feature_key'] == name)), name)):
            raise SidecarInvalid('Top three order mismatch')
        if any(type(value) not in (int, float) or not math.isfinite(value) for value in numbers):
            raise SidecarInvalid('Nonfinite contribution')
        if not 0 <= sidecar['score'] <= 1 or abs(sidecar['score'] - binding['risk_score']) > 1e-12:
            raise SidecarInvalid('Score mismatch')
        if abs(math.fsum([sidecar['base_value'], sidecar['remainder'],
                          *(item['contribution'] for item in items)]) - sidecar['raw_score']) > 1e-8:
            raise SidecarInvalid('Raw reconstruction mismatch')
        if abs(_stable_score(sidecar['raw_score']) - sidecar['score']) > 1e-12:
            raise SidecarInvalid('Score reconstruction mismatch')
        digest = sidecar['evidence_digest']
        if digest != hashlib.sha256(canonical({k: v for k, v in sidecar.items()
                                                if k != 'evidence_digest'})).hexdigest():
            raise SidecarInvalid('Evidence digest mismatch')
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise SidecarInvalid('Invalid sidecar') from exc
    return sidecar


class SidecarReader:
    def __init__(self, path: Path, pin: str):
        self.path, self.pin = Path(path), pin

    def read(self, binding, context):
        if not isinstance(self.pin, str) or re.fullmatch(r'[0-9a-f]{64}', self.pin) is None:
            raise SidecarInvalid('Missing trusted pin')
        try:
            if self.path.stat().st_size > 2_000_000:
                raise SidecarInvalid('Sidecar bundle too large')
            raw = self.path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != self.pin:
                raise SidecarInvalid('Trusted pin mismatch')
            def unique_pairs(pairs):
                value = {}
                for key, item in pairs:
                    if key in value:
                        raise SidecarInvalid('Duplicate JSON key')
                    value[key] = item
                return value

            data = json.loads(raw, object_pairs_hook=unique_pairs,
                parse_constant=lambda _: (_ for _ in ()).throw(SidecarInvalid('Nonfinite JSON')))
            if type(data) is not dict or set(data) != {'contract_version', 'items'} or data['contract_version'] != 1:
                raise SidecarInvalid('Invalid bundle')
            item = data['items'].get(binding['case_id'])
            if item is None:
                raise SidecarMissing('No sidecar for case')
            return _check(item, binding, context)
        except FileNotFoundError as exc:
            raise SidecarMissing('Sidecar bundle absent') from exc
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, AttributeError) as exc:
            raise SidecarInvalid('Invalid sidecar bundle') from exc
