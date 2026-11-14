"""Deterministic local reasons on the actual scorer output scale."""

import math
from decimal import Decimal

from fraudlens.data_contracts import _finite_decimal, _request_v2
from fraudlens.feature_history import feature_catalog


def _item(request, key, contribution, condition=None):
    catalog = feature_catalog()
    if key not in catalog:
        raise ValueError('explanation feature outside frozen catalog')
    value = request.feature_snapshot.feature_values[key]
    if value is None:
        observed = 'missing'
    else:
        observed = str(value)
    unit = catalog[key].unit
    if key in {'current_paid_amount', 'sender_paid_sum_same_currency_24h'}:
        unit = request.feature_snapshot.feature_values['current_paid_currency']
    if key == 'receiver_received_sum_same_currency_24h':
        unit = request.canonical_transaction.received_currency
    if not isinstance(unit, str) or not unit:
        raise ValueError('missing explanation unit')
    amount = _finite_decimal(contribution)
    return {'feature_key': key, 'observed_value': observed, 'unit': unit,
            'direction': 'increases' if amount > 0 else
                         'decreases' if amount < 0 else 'neutral',
            'contribution': amount, 'rule_condition': condition}


def additive_explanation(request, contributions, *, base, scale, method,
                         expected, tolerance):
    """Keep all omitted local terms in remainder and verify declared scale."""
    _request_v2(request)
    valid = {'rules': 'risk_score', 'linear_log_odds': 'log_odds',
             'tree_path': 'positive_class_estimate'}
    if method not in valid or valid[method] != scale:
        raise ValueError('explanation method/scale mismatch')
    baseline = _finite_decimal(base)
    target = _finite_decimal(expected)
    tol = _finite_decimal(tolerance)
    if tol < 0 or not Decimal(0) <= target <= Decimal(1):
        raise ValueError('invalid explanation target/tolerance')
    if not isinstance(contributions, (tuple, list)):
        raise ValueError('invalid explanation contributions')
    candidates = []
    for index, entry in enumerate(contributions):
        if not isinstance(entry, (tuple, list)) or len(entry) not in {2, 3}:
            raise ValueError('invalid explanation contribution')
        key, amount = entry[:2]
        condition = entry[2] if len(entry) == 3 else None
        if method != 'rules' and condition is not None:
            raise ValueError('model explanation cannot assert rule condition')
        if method == 'rules' and not isinstance(condition, str):
            raise ValueError('rule explanation needs actual condition')
        candidates.append((index, _item(request, key, amount, condition)))
    ordered = sorted(candidates, key=lambda pair: (-abs(pair[1]['contribution']),
                                                    pair[0]))
    shown = ordered[:3]
    omitted = ordered[3:]
    remainder = sum((item['contribution'] for _, item in omitted), Decimal(0))
    reconstructed = baseline + remainder + sum(
        (item['contribution'] for _, item in shown), Decimal(0))
    if method == 'linear_log_odds':
        estimate = Decimal(str(1 / (1 + math.exp(-float(reconstructed)))))
    else:
        estimate = reconstructed
    if abs(estimate - target) > tol:
        raise ValueError('explanation reconstruction mismatch')
    return {'status': 'available', 'method': method, 'explained_scale': scale,
            'feature_snapshot_digest': request.feature_snapshot.feature_input_digest,
            'partial': bool(omitted), 'base_value': baseline,
            'remainder': remainder, 'items': [item for _, item in shown]}


def unavailable_explanation(request, reason_code):
    _request_v2(request)
    if not isinstance(reason_code, str) or not reason_code:
        raise ValueError('unavailable explanation requires reason')
    return {'status': 'unavailable', 'reason_code': reason_code,
            'feature_snapshot_digest': request.feature_snapshot.feature_input_digest}


def rule_explanation(request, evaluation):
    _request_v2(request)
    keys = {'R1': 'sender_out_count_24h', 'R2': 'receiver_in_count_24h',
            'R3': 'current_paid_amount'}
    if (evaluation.policy_version != request.scorer_version
            or tuple(reason.rule_id for reason in evaluation.reasons) != tuple(keys)):
        raise ValueError('rule explanation identity mismatch')
    return additive_explanation(
        request, [(keys[reason.rule_id], reason.contribution,
                   f'{reason.state}: {reason.comparison}')
                  for reason in evaluation.reasons], base=Decimal(0),
        scale='risk_score', method='rules', expected=evaluation.score,
        tolerance=Decimal(0))


def _transformed_keys(pipeline, ordered_features):
    prepare = pipeline.named_steps['prepare']
    if len(ordered_features) != prepare.n_features_in_:
        raise ValueError('transformed feature order mismatch')
    keys = []
    for name, transformer, columns in prepare.transformers_:
        if name == 'remainder':
            if columns:
                raise ValueError('unexpected remainder columns')
            continue
        for column in columns:
            if type(column) is not int or ordered_features[column] not in feature_catalog():
                raise ValueError('unknown transformed feature')
            count = (len(transformer.categories_[list(columns).index(column)])
                     if name == 'category' else 1)
            keys.extend([ordered_features[column]] * count)
    if len(keys) != len(prepare.get_feature_names_out()):
        raise ValueError('transformed feature count mismatch')
    return keys


def model_explanation(request, pipeline, row, score, ordered_features,
                      *, tolerance=Decimal('1e-8')):
    """Explain the fitted tree path or linear log odds, with no refit."""
    _request_v2(request)
    if request.scorer_version != 'model-history-v1':
        raise ValueError('explanation scorer mismatch')
    keys = _transformed_keys(pipeline, ordered_features)
    transformed = pipeline.named_steps['prepare'].transform(row)
    if hasattr(transformed, 'toarray'):
        transformed = transformed.toarray()
    if transformed.shape != (1, len(keys)):
        raise ValueError('transformed row shape mismatch')
    values = transformed[0]
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError('nonfinite transformed feature')
    model = pipeline.named_steps['model']
    if not hasattr(model, 'classes_') or list(model.classes_) != [0, 1]:
        raise ValueError('positive class unavailable')
    if hasattr(model, 'tree_'):
        tree = model.tree_

        def positive(node):
            counts = tree.value[node][0]
            total = float(sum(counts))
            if total <= 0:
                raise ValueError('empty tree node')
            return Decimal(str(float(counts[1]) / total))

        node = 0
        base = positive(node)
        parts = []
        while tree.children_left[node] != tree.children_right[node]:
            feature = int(tree.feature[node])
            if feature < 0 or feature >= len(keys):
                raise ValueError('tree feature outside transformed input')
            next_node = (int(tree.children_left[node])
                         if float(values[feature]) <= float(tree.threshold[node])
                         else int(tree.children_right[node]))
            parts.append((keys[feature], positive(next_node) - positive(node)))
            node = next_node
        if int(model.apply(transformed)[0]) != node:
            raise ValueError('tree path differs from fitted prediction')
        return additive_explanation(request, parts, base=base,
                                    scale='positive_class_estimate',
                                    method='tree_path', expected=score,
                                    tolerance=tolerance)
    if hasattr(model, 'coef_') and hasattr(model, 'intercept_'):
        if model.coef_.shape != (1, len(keys)):
            raise ValueError('linear coefficient order mismatch')
        parts = [(key, Decimal(str(float(coef) * float(value))))
                 for key, coef, value in zip(keys, model.coef_[0], values)]
        return additive_explanation(request, parts,
                                    base=Decimal(str(float(model.intercept_[0]))),
                                    scale='log_odds', method='linear_log_odds',
                                    expected=score, tolerance=tolerance)
    raise ValueError('unsupported local explanation method')
