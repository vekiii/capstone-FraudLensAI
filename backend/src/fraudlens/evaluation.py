"""Offline, label-separated chronological split state for Feature 002.

This module does not fit models or disclose holdout outcomes. Membership is
chosen from observable history-v1 snapshots before private labels are joined.
"""

import hashlib
import json
import math
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from itertools import groupby
from numbers import Integral
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from fraudlens.data_contracts import DatasetVersion, PrivateEvaluationLabel
from fraudlens.data_import import derive_dataset_version
from fraudlens.feature_history import HistoricalFeatureSnapshot, feature_catalog

_ROLES = ('train', 'validation', 'test')
_LABEL_ROLES = MappingProxyType({
    'train': 'supervised_fit_and_learned_transforms',
    'validation': 'selection_and_threshold_only',
    'test': 'final_metrics_after_frozen_predictions_only',
})
_LABEL_STATUSES = {'eligible_positive': 1, 'eligible_negative': 0,
                   'missing': None, 'invalid': None, 'unsupported': None}


@dataclass(frozen=True, slots=True)
class EvaluationProtocol:
    """Split policy and label roles; later T029 freezes the full experiment."""

    version: str
    feature_version: str
    feature_policy_hash: str
    train_percent: int
    validation_percent: int
    test_percent: int
    warmup_hours: int
    minimum_outer_positives: int
    label_roles: Mapping[str, str]
    holdout_disclosed: bool = False

    def __post_init__(self) -> None:
        if tuple(self.label_roles) != _ROLES or self.holdout_disclosed:
            raise ValueError('invalid split protocol roles or holdout state')
        object.__setattr__(self, 'label_roles', MappingProxyType(dict(self.label_roles)))


@dataclass(frozen=True, slots=True)
class Partition:
    role: str
    transaction_ids: tuple[str, ...]
    first_event_time: datetime | None
    last_event_time: datetime | None
    event_valid_count: int
    label_eligible_count: int
    label_ineligible_count: int
    positives: int
    negatives: int
    prevalence: float | None


@dataclass(frozen=True, slots=True)
class SplitManifest:
    """Immutable membership, exact counts and explicit eligibility result."""

    dataset_version: str
    source_sha256: str
    mapping_sha256: str
    time_policy_sha256: str
    protocol: EvaluationProtocol
    source_start: datetime
    warmup_cutoff: datetime
    partitions: Mapping[str, Partition]
    warmup_excluded_ids: tuple[str, ...]
    coverage_excluded_ids: tuple[str, ...]
    event_valid_count: int
    scoreable_count: int
    label_eligible_count: int
    label_ineligible_count: int
    membership_hash: str
    protocol_hash: str
    eligible: bool
    ineligibility_reasons: tuple[str, ...]
    frozen_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'partitions', MappingProxyType(dict(self.partitions)))
        if tuple(self.partitions) != _ROLES:
            raise ValueError('invalid split manifest partition roles')
        parts = tuple(self.partitions.values())
        if any(part.role != role or part.event_valid_count != len(part.transaction_ids)
               or part.label_eligible_count + part.label_ineligible_count
               != part.event_valid_count
               or part.positives + part.negatives != part.label_eligible_count
               for role, part in zip(_ROLES, parts, strict=True)):
            raise ValueError('invalid split manifest partition counts')
        all_ids = (*self.warmup_excluded_ids, *self.coverage_excluded_ids,
                   *(event_id for part in parts for event_id in part.transaction_ids))
        if (len(all_ids) != len(set(all_ids)) or len(all_ids) != self.event_valid_count
                or sum(part.event_valid_count for part in parts) != self.scoreable_count
                or self.warmup_cutoff != self.source_start + timedelta(hours=24)):
            raise ValueError('invalid split manifest membership')
        if (not self.ineligibility_reasons) != self.eligible:
            raise ValueError('invalid split manifest eligibility')
        for earlier, later in zip(parts, parts[1:]):
            if (earlier.transaction_ids and later.transaction_ids
                    and not earlier.last_event_time < later.first_event_time):
                raise ValueError('invalid split manifest chronology')
        if self.eligible and any(not part.transaction_ids for part in parts):
            raise ValueError('eligible split requires three nonempty partitions')
        membership_hash, protocol_hash = _manifest_digests(
            self.dataset_version, self.source_sha256, self.mapping_sha256,
            self.time_policy_sha256, self.protocol, self.source_start,
            self.warmup_cutoff, self.partitions, self.warmup_excluded_ids,
            self.coverage_excluded_ids, self.eligible, self.ineligibility_reasons)
        if self.membership_hash != membership_hash or self.protocol_hash != protocol_hash:
            raise ValueError('invalid split manifest digest')

    @property
    def fit_allowed(self) -> bool:
        return self.eligible

    @property
    def holdout_disclosed(self) -> bool:
        return self.protocol.holdout_disclosed


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=True).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def _manifest_digests(dataset_version: str, source_sha256: str,
                      mapping_sha256: str, time_policy_sha256: str,
                      policy: EvaluationProtocol, source_start: datetime,
                      cutoff: datetime, partitions: Mapping[str, Partition],
                      warmup: tuple[str, ...], coverage: tuple[str, ...],
                      eligible: bool, reasons: tuple[str, ...]) -> tuple[str, str]:
    base = {
        'dataset_version': dataset_version,
        'source_sha256': source_sha256,
        'mapping_sha256': mapping_sha256,
        'time_policy_sha256': time_policy_sha256,
        'feature_policy_hash': policy.feature_policy_hash,
        'policy': policy.version,
        'source_start': source_start.isoformat(),
        'warmup_cutoff': cutoff.isoformat(),
        'partitions': {role: {'ids': part.transaction_ids,
                             'first': part.first_event_time.isoformat()
                             if part.first_event_time else None,
                             'last': part.last_event_time.isoformat()
                             if part.last_event_time else None}
                       for role, part in partitions.items()},
        'warmup_excluded_ids': warmup,
        'coverage_excluded_ids': coverage,
    }
    membership_hash = _hash(base)
    summary = {role: {'eligible': part.label_eligible_count,
                      'ineligible': part.label_ineligible_count,
                      'positives': part.positives, 'negatives': part.negatives}
               for role, part in partitions.items()}
    return membership_hash, _hash({'membership': membership_hash, 'counts': summary,
                                   'eligible': eligible, 'reasons': reasons})


def _feature_policy_hash(keys: frozenset[str]) -> str:
    catalog = feature_catalog()
    return _hash({name: asdict(catalog[name]) for name in sorted(keys)})


def _validate_dataset(dataset: DatasetVersion, expected_sha: str, source_start: datetime):
    if not isinstance(dataset, DatasetVersion) or dataset.status != 'complete':
        raise ValueError('complete dataset version required')
    if not dataset.dataset_version or not all((dataset.source_sha256,
                                               dataset.mapping_sha256,
                                               dataset.time_policy_sha256)):
        raise ValueError('dataset provenance missing')
    if dataset.source_sha256 != expected_sha:
        raise ValueError('source identity mismatch')
    try:
        derived = derive_dataset_version(*(bytes.fromhex(value) for value in (
            dataset.source_sha256, dataset.mapping_sha256,
            dataset.time_policy_sha256)))
    except (TypeError, ValueError) as exc:
        raise ValueError('invalid dataset provenance digest') from exc
    if derived != dataset.dataset_version:
        raise ValueError('dataset version and provenance mismatch')
    if not isinstance(source_start, datetime) or source_start.tzinfo is None:
        raise ValueError('source start must be timezone-aware')


def _validate_snapshots(snapshots, dataset: DatasetVersion, source_start: datetime,
                        cutoff: datetime) -> tuple[list[HistoricalFeatureSnapshot],
                                                     frozenset[str]]:
    catalog_keys = frozenset(feature_catalog())
    required_keys = catalog_keys - {'current_payment_format'}
    seen: set[str] = set()
    ordered = []
    feature_keys = None
    for snapshot in snapshots:
        if not isinstance(snapshot, HistoricalFeatureSnapshot):
            raise ValueError('snapshot provenance type mismatch')
        if not snapshot.transaction_id or snapshot.transaction_id in seen:
            raise ValueError('duplicate or missing event identity')
        seen.add(snapshot.transaction_id)
        if snapshot.dataset_version != dataset.dataset_version:
            raise ValueError('snapshot dataset version mismatch')
        if snapshot.feature_version != 'history-v1':
            raise ValueError('unsupported feature version')
        if (snapshot.event_time.tzinfo is None or snapshot.as_of != snapshot.event_time
                or snapshot.coverage_start != source_start
                or snapshot.event_time < source_start):
            raise ValueError('snapshot as-of or coverage provenance mismatch')
        if snapshot.coverage_state not in {'full', 'incomplete', 'unavailable'}:
            raise ValueError('unsupported coverage state')
        if not isinstance(snapshot.feature_values, dict):
            raise ValueError('unsupported feature schema or label in feature values')
        current_keys = frozenset(snapshot.feature_values)
        if (not required_keys <= current_keys <= catalog_keys
                or feature_keys is not None and current_keys != feature_keys):
            raise ValueError('unsupported feature schema or label in feature values')
        feature_keys = current_keys
        if (not isinstance(snapshot.feature_input_digest, str)
                or len(snapshot.feature_input_digest) != 64
                or any(character not in '0123456789abcdef'
                       for character in snapshot.feature_input_digest)):
            raise ValueError('snapshot feature provenance missing')
        if snapshot.event_time < cutoff:
            if snapshot.scoreable or snapshot.coverage_state == 'full':
                raise ValueError('warmup coverage state inconsistent')
        elif snapshot.scoreable != (snapshot.coverage_state == 'full'):
            raise ValueError('scoreable coverage state inconsistent')
        ordered.append(snapshot)
    if dataset.source_records is not None and len(ordered) > dataset.source_records:
        raise ValueError('snapshot count exceeds source provenance')
    ordered.sort(key=lambda item: (item.event_time, item.transaction_id))
    if ordered and ordered[0].event_time != source_start:
        raise ValueError('source start and snapshot provenance mismatch')
    return ordered, feature_keys or catalog_keys


def _validate_labels(labels, snapshot_ids: set[str]) -> dict[str, PrivateEvaluationLabel]:
    indexed = {}
    ordinals = set()
    for label in labels:
        if not isinstance(label, PrivateEvaluationLabel):
            raise ValueError('private label type mismatch')
        if (not label.transaction_id or label.transaction_id in indexed
                or label.source_ordinal < 1 or label.source_ordinal in ordinals):
            raise ValueError('duplicate or invalid private label identity')
        if label.status not in _LABEL_STATUSES or label.value != _LABEL_STATUSES[label.status]:
            raise ValueError('private label status and value mismatch')
        indexed[label.transaction_id] = label
        ordinals.add(label.source_ordinal)
    if set(indexed) != snapshot_ids:
        raise ValueError('private label event identities do not match snapshots')
    return indexed


def _boundary(groups: list[tuple[HistoricalFeatureSnapshot, ...]], target_numerator: int,
              target_denominator: int, total: int, lower: int, upper: int) -> int | None:
    if lower >= upper:
        return None
    counts = []
    cumulative = 0
    for group in groups:
        cumulative += len(group)
        counts.append(cumulative)
    choices = counts[lower:upper]
    if not choices:
        return None
    return min(choices, key=lambda count: (abs(count * target_denominator
                                                 - target_numerator * total), count))


def _partition(role: str, rows: tuple[HistoricalFeatureSnapshot, ...],
               labels: Mapping[str, PrivateEvaluationLabel]) -> Partition:
    positives = sum(labels[row.transaction_id].status == 'eligible_positive' for row in rows)
    negatives = sum(labels[row.transaction_id].status == 'eligible_negative' for row in rows)
    eligible = positives + negatives
    return Partition(role, tuple(row.transaction_id for row in rows),
                     rows[0].event_time if rows else None,
                     rows[-1].event_time if rows else None, len(rows), eligible,
                     len(rows) - eligible, positives, negatives,
                     positives / eligible if eligible else None)


def build_split_manifest(*, dataset_version: DatasetVersion,
                         snapshots: tuple[HistoricalFeatureSnapshot, ...],
                         labels: tuple[PrivateEvaluationLabel, ...],
                         source_start: datetime,
                         expected_source_sha256: str) -> SplitManifest:
    """Freeze observable membership, then join private labels offline for counts.

    No label, eligibility flag or class count participates in boundary choice.
    Known deficient coverage remains an event-valid fact but is not scoreable.
    """
    _validate_dataset(dataset_version, expected_source_sha256, source_start)
    cutoff = source_start + timedelta(hours=24)
    ordered, feature_keys = _validate_snapshots(snapshots, dataset_version,
                                                source_start, cutoff)
    warmup = tuple(row.transaction_id for row in ordered if row.event_time < cutoff)
    coverage = tuple(row.transaction_id for row in ordered
                     if row.event_time >= cutoff and row.coverage_state != 'full')
    scoreable = tuple(row for row in ordered
                      if row.event_time >= cutoff and row.coverage_state == 'full')
    groups = [tuple(group) for _, group in groupby(scoreable, key=lambda row: row.event_time)]
    total = len(scoreable)
    if len(groups) >= 3:
        train_end = _boundary(groups, 7, 10, total, 0, len(groups) - 2)
        train_group_index = next(i for i, group in enumerate(groups)
                                 if group[-1].transaction_id == scoreable[train_end - 1]
                                 .transaction_id)
        validation_end = _boundary(groups, 17, 20, total, train_group_index + 1,
                                   len(groups) - 1)
    else:
        train_end = validation_end = None
    if train_end is None or validation_end is None:
        rows_by_role = ((), (), ())
    else:
        rows_by_role = (scoreable[:train_end], scoreable[train_end:validation_end],
                        scoreable[validation_end:])

    # This is the first point where private evaluation labels are read.
    private_labels = _validate_labels(labels, {row.transaction_id for row in ordered})
    partitions = MappingProxyType({
        role: _partition(role, rows, private_labels)
        for role, rows in zip(_ROLES, rows_by_role, strict=True)
    })
    reasons = []
    if train_end is None or validation_end is None:
        reasons.append('insufficient_distinct_timestamps_for_three_partitions')
    for role, partition in partitions.items():
        if partition.positives == 0 or partition.negatives == 0:
            reasons.append(f'{role}_requires_both_classes')
        if role in {'validation', 'test'} and partition.positives < 20:
            reasons.append(f'{role}_requires_20_positives')

    policy = EvaluationProtocol('feature-002-split-v1', 'history-v1',
                                _feature_policy_hash(feature_keys), 70, 15, 15, 24, 20,
                                _LABEL_ROLES)
    membership_hash, protocol_hash = _manifest_digests(
        dataset_version.dataset_version, dataset_version.source_sha256,
        dataset_version.mapping_sha256, dataset_version.time_policy_sha256,
        policy, source_start, cutoff, partitions, warmup, coverage,
        not reasons, tuple(reasons))
    return SplitManifest(
        dataset_version.dataset_version, dataset_version.source_sha256,
        dataset_version.mapping_sha256, dataset_version.time_policy_sha256,
        policy, source_start, cutoff, partitions, warmup, coverage, len(ordered), total,
        sum(part.label_eligible_count for part in partitions.values()),
        sum(part.label_ineligible_count for part in partitions.values()),
        membership_hash, protocol_hash,
        not reasons, tuple(reasons),
    )


def _validate_binary(labels):
    values = tuple(labels)
    if any(not isinstance(value, Integral) or value not in (0, 1)
           for value in values):
        raise ValueError('binary labels required')
    return tuple(int(value) for value in values)


def precision_at_k(scores, labels, ids, k=20):
    """Stable-ID score ties; the capacity boundary uses exactly min(K,n) rows."""
    if not (len(scores) == len(labels) == len(ids)) or len(set(ids)) != len(ids):
        raise ValueError('ranking identities mismatch')
    if not all(math.isfinite(float(score)) for score in scores):
        raise ValueError('nonfinite score')
    truth = _validate_binary(labels)
    ordered = sorted(range(len(scores)), key=lambda i: (-float(scores[i]), ids[i]))
    top = ordered[:min(k, len(ordered))]
    return sum(truth[i] for i in top) / len(top) if top else None


def select_candidate(results, *, ap_tolerance=1e-6):
    """AP, then P@K, then prospective grid order for residual ties."""
    if not results or len(results) > 6:
        raise ValueError('candidate count outside frozen grid')
    viable = [(i, row) for i, row in enumerate(results)
              if row.get('status', 'complete') == 'complete']
    if not viable:
        raise ValueError('no completed candidate')
    for _, row in viable:
        if not all(math.isfinite(float(row[key])) for key in ('ap', 'precision_at_k')):
            raise ValueError('nonfinite candidate metric')
    best_ap = max(row['ap'] for _, row in viable)
    tied = [i for i, row in viable
            if best_ap - row['ap'] <= ap_tolerance]
    best_p = max(results[i]['precision_at_k'] for i in tied)
    return next(i for i in tied if results[i]['precision_at_k'] == best_p)


def select_threshold(scores, labels, *, max_alerts=20):
    """Inclusive distinct-score F0.5 policy with symbolic no-alert."""
    if len(scores) != len(labels) or max_alerts < 1:
        raise ValueError('threshold inputs mismatch')
    truth = _validate_binary(labels)
    if not all(math.isfinite(float(score)) for score in scores):
        raise ValueError('nonfinite score')
    positives = sum(truth)
    best = {'threshold': 'no_alert', 'alerts': 0, 'f0_5': 0.0}
    ordered = sorted(range(len(scores)), key=lambda i: -float(scores[i]))
    alerts = tp = 0
    for threshold, group in groupby(ordered, key=lambda i: float(scores[i])):
        indices = tuple(group)
        alerts += len(indices)
        if alerts > max_alerts:
            break
        tp += sum(truth[i] for i in indices)
        fp = alerts - tp
        fn = positives - tp
        metric = 1.25 * tp / (1.25 * tp + 0.25 * fn + fp) if tp else 0.0
        if (metric > best['f0_5']
                or metric == best['f0_5'] and alerts < best['alerts']):
            best = {'threshold': threshold, 'alerts': alerts, 'f0_5': metric}
    return best


def fit_candidate_grid(train_x, train_y, validation_x, validation_y,
                       validation_ids, *, numeric_columns, categorical_columns,
                       candidates):
    """Fit each declared candidate and all learned transforms on train only."""
    import numpy as np
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import average_precision_score
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.tree import DecisionTreeClassifier

    if not candidates or len(candidates) > 6:
        raise ValueError('candidate count outside frozen grid')
    train_y = np.asarray(_validate_binary(train_y))
    validation_y = np.asarray(_validate_binary(validation_y))
    if (len(train_x) != len(train_y) or len(validation_x) != len(validation_y)
            or len(set(train_y)) < 2 or len(set(validation_y)) < 2):
        raise ValueError('ineligible fit population')
    results = []
    for kind, *parameters in candidates:
        numeric = Pipeline([('imputer', SimpleImputer(strategy='median')),
                            ('scale', StandardScaler())])
        prepare = ColumnTransformer([
            ('numeric', numeric, list(numeric_columns)),
            ('category', OneHotEncoder(handle_unknown='ignore'),
             list(categorical_columns)),
        ])
        if kind == 'logistic_l2' and len(parameters) == 1:
            model = LogisticRegression(C=parameters[0], class_weight='balanced',
                                       max_iter=200, random_state=42, solver='liblinear')
        elif kind == 'decision_tree' and len(parameters) == 2:
            model = DecisionTreeClassifier(max_depth=parameters[0],
                                           min_samples_leaf=parameters[1],
                                           class_weight='balanced', random_state=42)
        else:
            raise ValueError('candidate outside frozen grid')
        pipeline = Pipeline([('prepare', prepare), ('model', model)])
        try:
            pipeline.fit(train_x, train_y)
            scores = pipeline.predict_proba(validation_x)[:, 1]
            ap = float(average_precision_score(validation_y, scores))
            at_k = precision_at_k(scores, validation_y, validation_ids)
        except (ValueError, RuntimeError, MemoryError) as exc:
            results.append({'kind': kind, 'parameters': parameters, 'status': 'failed',
                            'failure_type': type(exc).__name__})
            continue
        results.append({'kind': kind, 'parameters': parameters, 'status': 'complete',
                        'pipeline': pipeline, 'validation_scores': scores, 'ap': ap,
                        'precision_at_k': at_k})
    return results


def calculate_metrics(ids, scores, labels, *, threshold, k=20, probability):
    """Non-interpolated AP and exact capacity/threshold metrics for label 1."""
    from sklearn.metrics import average_precision_score

    if (not ids or len(ids) != len(scores) or len(ids) != len(labels)
            or len(set(ids)) != len(ids) or k < 1):
        raise ValueError('ineligible metric population')
    truth = _validate_binary(labels)
    if len(set(truth)) < 2:
        raise ValueError('both classes required')
    if not all(math.isfinite(float(score)) and 0 <= float(score) <= 1
               for score in scores):
        raise ValueError('scores must be finite in [0,1]')
    if threshold != 'no_alert' and (not isinstance(threshold, (int, float))
                                    or not math.isfinite(threshold)
                                    or not 0 <= threshold <= 1):
        raise ValueError('invalid frozen threshold')
    order = sorted(range(len(ids)), key=lambda i: (-float(scores[i]), ids[i]))
    capacity = min(k, len(ids))
    selected = order[:capacity]
    positive_total = sum(truth)
    top_true = sum(truth[i] for i in selected)
    alerted = [i for i, score in enumerate(scores)
               if threshold != 'no_alert' and float(score) >= threshold]
    tp = sum(truth[i] for i in alerted)
    fp = len(alerted) - tp
    fn = positive_total - tp
    tn = len(ids) - positive_total - fp
    brier = (sum((float(score) - label) ** 2
                 for score, label in zip(scores, truth, strict=True)) / len(ids)
             if probability else None)
    reliability = None
    reliability_status = 'not_applicable_ordinal_rules' if not probability else \
        'not_estimable_insufficient_population'
    if probability and len(ids) >= 100 and positive_total >= 20:
        bins = []
        for index in range(10):
            rows = [(float(score), label) for score, label in
                    zip(scores, truth, strict=True)
                    if min(int(float(score) * 10), 9) == index]
            if rows:
                bins.append({'lower': index / 10, 'upper': (index + 1) / 10,
                             'count': len(rows), 'mean_probability':
                             sum(score for score, _ in rows) / len(rows),
                             'observed_rate': sum(label for _, label in rows) / len(rows)})
        reliability = bins
        reliability_status = 'descriptive_uncalibrated'
    return {'row_count': len(ids), 'positives': positive_total,
            'negatives': len(ids) - positive_total,
            'prevalence': positive_total / len(ids),
            'average_precision': float(average_precision_score(truth, scores)),
            'k': capacity, 'precision_at_k': top_true / capacity,
            'recall_at_k': top_true / positive_total,
            'k_crosses_score_tie': (capacity < len(ids) and
                                    scores[order[capacity - 1]] == scores[order[capacity]]),
            'confusion': {'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn},
            'threshold_precision': tp / len(alerted) if alerted else None,
            'threshold_recall': tp / positive_total,
            'alert_rate': len(alerted) / len(ids),
            'threshold': threshold, 'brier': brier,
            'reliability': reliability, 'reliability_status': reliability_status,
            'uncertainty_status': 'not_quantified',
            'uncertainty_reason': 'No interval method was predeclared for this benchmark.'}


def evaluate_frozen(predictions, labels, thresholds, *, account_seen=None):
    """Require identical row IDs before an offline private-label metric join."""
    if set(predictions) != {'model', 'rules'} or set(thresholds) != {'model', 'rules'}:
        raise ValueError('both scorers required')
    rows = {}
    for scorer, pairs in predictions.items():
        if len({event_id for event_id, _ in pairs}) != len(pairs):
            raise ValueError('duplicate prediction identity')
        rows[scorer] = dict(pairs)
    ids = sorted(rows['model'])
    if not ids or set(ids) != set(rows['rules']) or set(ids) != set(labels):
        raise ValueError('scorer or label identities mismatch')
    truth = [labels[event_id] for event_id in ids]
    metrics = {scorer: calculate_metrics(
        ids, [rows[scorer][event_id] for event_id in ids], truth,
        threshold=thresholds[scorer], probability=scorer == 'model')
        for scorer in ('model', 'rules')}
    if account_seen is None:
        coverage = {'status': 'not_supplied'}
    else:
        if set(account_seen) != set(ids) or any(type(value) is not bool
                                                for value in account_seen.values()):
            raise ValueError('account coverage identities mismatch')
        seen = sum(account_seen.values())
        coverage = {'status': 'measured', 'seen': seen, 'unseen': len(ids) - seen,
                    'seen_rate': seen / len(ids)}
    for result in metrics.values():
        result['account_coverage'] = coverage
    return metrics


def consume_holdout(path: Path, protocol_hash: str, predictions_hash: str):
    """Atomically record first label disclosure; repeats are exploratory."""
    path = Path(path)
    if not protocol_hash or not predictions_hash:
        raise ValueError('frozen hashes required')
    payload = {'protocol_hash': protocol_hash, 'predictions_hash': predictions_hash}
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        existing = json.loads(path.read_text())
        if existing != payload:
            raise ValueError('consumed holdout cannot make fresh confirmatory claim')
        return 'exploratory_reuse'
    with os.fdopen(descriptor, 'w') as stream:
        json.dump(payload, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    return 'first_disclosure'
