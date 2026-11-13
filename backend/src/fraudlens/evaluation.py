"""Offline, label-separated chronological split state for Feature 002.

This module does not fit models or disclose holdout outcomes. Membership is
chosen from observable history-v1 snapshots before private labels are joined.
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from itertools import groupby
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
