"""Isolated prospective sidecar contract. Not imported by application code."""

import hashlib
import math

from fraudlens.investigation.models import canonical
from fraudlens.scoring.model_scorer import MANIFEST_SHA256, MODEL_SHA256


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def build_sidecar(binding, context, calculation, manifest, features):
    groups = calculation['groups']
    ordered = sorted(groups, key=lambda key: (-abs(groups[key]), key))
    items = []
    for key in ordered[:3]:
        value = features[key]
        items.append(dict(feature_key=key, observed_value=str(value),
            unit=('log1p_source_amount' if key == 'current_amount_paid_log1p' else
                  'category' if key in ('current_payment_currency', 'current_payment_format')
                  else 'count' if 'sum_' not in key else 'same_currency_amount'),
            direction='increases' if groups[key] > 0 else 'decreases' if groups[key] < 0 else 'neutral',
            contribution=groups[key]))
    sidecar = dict(contract_version=1, status='available',
        method='lightgbm_pred_contrib_log_odds_v1', explained_scale='log_odds',
        objective=calculation['objective'], num_iteration=calculation['num_iteration'],
        canonical_transaction_id=binding['canonical_transaction_id'],
        transaction_id=binding['transaction_id'], case_id=binding['case_id'],
        assessment_run_id=binding['snapshot_ref'], dataset_version=binding['dataset_version'],
        context_revision=context['context_revision'],
        model_sha256=MODEL_SHA256, manifest_sha256=MANIFEST_SHA256,
        feature_version=binding['feature_version'],
        matrix_feature_order_sha256=digest(manifest['matrix_feature_order']),
        feature_snapshot_digest=context['source_payload']['risk_assessment']['explanation']['feature_snapshot_digest'],
        score=calculation['score'], raw_score=calculation['raw_score'],
        base_value=calculation['base_value'], partial=True, items=items,
        remainder=calculation['remainder'])
    sidecar['evidence_digest'] = digest(sidecar)
    return sidecar


def validate_sidecar(sidecar, binding, context, calculation, manifest, features):
    expected = build_sidecar(binding, context, calculation, manifest, features)
    if set(sidecar) != set(expected) or sidecar != expected:
        raise ValueError('sidecar identity, ordering or evidence mismatch')
    values = [sidecar['base_value'], sidecar['remainder'], sidecar['raw_score'],
              sidecar['score'], *(item['contribution'] for item in sidecar['items'])]
    if any(type(value) not in (int, float) or not math.isfinite(value) for value in values):
        raise ValueError('nonfinite sidecar value')
    if abs(math.fsum((sidecar['base_value'], sidecar['remainder'],
                      *(item['contribution'] for item in sidecar['items']))) -
           sidecar['raw_score']) > 1e-8:
        raise ValueError('sidecar reconstruction mismatch')
    return sidecar
