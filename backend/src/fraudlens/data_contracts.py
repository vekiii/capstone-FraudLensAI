"""Internal Feature 002 import objects; private labels never enter operational facts."""
import copy
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Literal, Protocol

DatasetStatus = Literal['staged', 'complete', 'failed']
LabelStatus = Literal['eligible_positive', 'eligible_negative', 'missing', 'invalid',
                      'unsupported']
EventStatus = Literal['event_valid', 'event_rejected']


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    transaction_id: str
    case_id: str
    full_digest: bytes
    case_full_digest: bytes
    framed_input: bytes


@dataclass(frozen=True)
class CanonicalTransaction:
    transaction_id: str
    case_id: str
    source_ordinal: int
    event_time_raw: str
    event_time_utc: datetime
    event_time_epoch_ns: int
    time_basis: str
    sender_bank: str
    sender_account: str
    receiver_bank: str
    receiver_account: str
    sender_join_key: bytes
    receiver_join_key: bytes
    paid_amount: str
    paid_currency: str
    received_amount: str
    received_currency: str
    payment_format: str | None
    event_fact_digest: bytes

    @property
    def predictor_fields(self) -> frozenset[str]:
        """Allowlist for later features; no IDs, labels, or row-order proxies."""
        return frozenset({'event_time_utc', 'paid_amount', 'paid_currency',
                          'received_amount', 'received_currency', 'payment_format'})


@dataclass(frozen=True, slots=True)
class PrivateEvaluationLabel:
    transaction_id: str
    source_ordinal: int
    status: LabelStatus
    value: int | None


@dataclass(frozen=True, slots=True)
class ImportRow:
    source_ordinal: int
    event_status: EventStatus
    rejection_reason: str | None
    private_label_status: LabelStatus | None


@dataclass(frozen=True, slots=True)
class ImportReport:
    source_records: int | None
    event_valid: int
    event_rejected: int
    label_eligible: int
    label_ineligible: int
    positives: int
    negatives: int
    complete_parse: bool
    errors: tuple[str, ...] = ()

    def reconciled(self) -> bool:
        return (self.complete_parse and self.source_records is not None
                and self.source_records == self.event_valid + self.event_rejected
                and self.event_valid == self.label_eligible + self.label_ineligible
                and self.label_eligible == self.positives + self.negatives)


@dataclass(frozen=True, slots=True)
class DatasetVersion:
    dataset_version: str
    source_sha256: str
    mapping_sha256: str
    time_policy_sha256: str
    status: DatasetStatus
    source_records: int | None = None


@dataclass(slots=True)
class ParseResult:
    status: Literal['complete', 'failed']
    report: ImportReport
    events: list[CanonicalTransaction] = field(default_factory=list)
    private_labels: list[PrivateEvaluationLabel] = field(default_factory=list)
    rows: list[ImportRow] = field(default_factory=list)


@dataclass(frozen=True)
class StoredOperationalEvent:
    transaction_id: str
    case_id: str
    facts: dict | None = None


@dataclass(frozen=True)
class StoredPrivateLabel:
    transaction_id: str
    value: int | None
    status: LabelStatus


@dataclass(frozen=True)
class ScoreRequestV2:
    canonical_transaction: CanonicalTransaction
    feature_snapshot: object
    dataset_version: str
    run_id: str
    scorer_version: str
    feature_version: str
    history_cutoff_exclusive_at: datetime


class ScorerV2(Protocol):
    requires_artifact: bool

    def score(self, request: ScoreRequestV2) -> object: ...


@dataclass(frozen=True)
class ExplanationV2:
    status: str
    feature_snapshot_digest: str
    reason_code: str | None = None
    method: str | None = None
    explained_scale: str | None = None
    partial: bool | None = None
    base_value: Decimal | None = None
    remainder: Decimal | None = None
    items: tuple[dict, ...] = ()


@dataclass(frozen=True)
class RiskAssessmentV2:
    transaction_id: str
    dataset_version: str
    run_id: str
    score: Decimal
    score_kind: str
    score_source: str
    scorer_version: str
    feature_version: str
    artifact_version: str
    event_time_utc: datetime
    history_cutoff_exclusive_at: datetime
    scored_at: datetime
    history_coverage: dict
    explanation: ExplanationV2


_VERSION_ID = re.compile(r'dv_[0-9a-f]{64}\Z')
_DIGEST_ID = re.compile(r'[0-9a-f]{64}\Z')


def _request_v2(request: ScoreRequestV2) -> None:
    from fraudlens.feature_history import (
        _CATALOG,
        _EVENT_FIELDS,
        FEATURE_VERSION,
        HistoricalFeatureSnapshot,
        _digest,
    )

    if not isinstance(request, ScoreRequestV2):
        raise TypeError('ScoreRequestV2 required')
    event, snapshot = request.canonical_transaction, request.feature_snapshot
    if (not isinstance(event, CanonicalTransaction)
            or set(vars(event)) != _EVENT_FIELDS
            or not isinstance(snapshot, HistoricalFeatureSnapshot)
            or set(vars(snapshot)) != set(HistoricalFeatureSnapshot.__dataclass_fields__)):
        raise ValueError('invalid event or snapshot schema')
    if (not isinstance(request.dataset_version, str)
            or not _VERSION_ID.fullmatch(request.dataset_version)
            or not isinstance(request.run_id, str) or not request.run_id
            or not isinstance(request.scorer_version, str) or not request.scorer_version
            or request.feature_version != FEATURE_VERSION
            or snapshot.feature_version != FEATURE_VERSION):
        raise ValueError('invalid score request versions')
    at = event.event_time_utc
    if (not isinstance(at, datetime) or at.tzinfo is None
            or not isinstance(request.history_cutoff_exclusive_at, datetime)
            or request.history_cutoff_exclusive_at != at
            or snapshot.event_time != at or snapshot.as_of != at
            or snapshot.transaction_id != event.transaction_id
            or snapshot.dataset_version != request.dataset_version):
        raise ValueError('score request identity or as-of mismatch')
    if (snapshot.coverage_state != 'full' or snapshot.scoreable is not True
            or not isinstance(snapshot.coverage_start, datetime)
            or snapshot.coverage_start.tzinfo is None
            or at < snapshot.coverage_start + timedelta(hours=24)):
        raise ValueError('score request lacks full, scoreable coverage')
    values = snapshot.feature_values
    if (not isinstance(values, dict) or set(values) != set(_CATALOG)
            or any(isinstance(value, (dict, list, tuple, set)) for value in values.values())
            or any(value is None for key, value in values.items()
                   if key != 'current_payment_format')):
        raise ValueError('feature schema mismatch')
    counts = [key for key in values if key.endswith('_count_24h')
              or key.startswith('sender_distinct_') or key.startswith('receiver_distinct_')]
    if any(type(values[key]) is not int or values[key] < 0 for key in counts):
        raise ValueError('feature count schema mismatch')
    amounts = ('sender_paid_sum_same_currency_24h',
               'receiver_received_sum_same_currency_24h', 'current_paid_amount')
    if any(not isinstance(values[key], Decimal) or not values[key].is_finite()
           or values[key] < 0 for key in amounts):
        raise ValueError('feature amount schema mismatch')
    if (values['current_paid_amount'] != Decimal(event.paid_amount)
            or values['current_paid_currency'] != event.paid_currency
            or values['current_payment_format'] != event.payment_format):
        raise ValueError('current feature mismatch')
    if (not isinstance(snapshot.feature_input_digest, str)
            or not _DIGEST_ID.fullmatch(snapshot.feature_input_digest)
            or snapshot.feature_input_digest != _digest(request.dataset_version, event,
                                                        values, snapshot.coverage_start,
                                                        snapshot.coverage_state)):
        raise ValueError('feature input digest mismatch')


def _finite_decimal(value: object) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, float, int)):
        raise ValueError('number must be numeric, never coerced from text or bool')
    try:
        score = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError('invalid score') from exc
    if not score.is_finite():
        raise ValueError('nonfinite number')
    return score


def _decimal_score(value: object) -> Decimal:
    score = _finite_decimal(value)
    if not Decimal(0) <= score <= Decimal(1):
        raise ValueError('score outside [0,1]')
    return score


def _explanation_v2(value: object, digest: str) -> ExplanationV2:
    from fraudlens.feature_history import feature_catalog

    if not isinstance(value, dict) or value.get('feature_snapshot_digest') != digest:
        raise ValueError('explanation snapshot digest mismatch')
    status = value.get('status')
    if status == 'unavailable':
        if set(value) != {'status', 'reason_code', 'feature_snapshot_digest'}:
            raise ValueError('unexpected unavailable explanation fields')
        if not isinstance(value['reason_code'], str) or not value['reason_code']:
            raise ValueError('unavailable explanation needs a reason')
        return ExplanationV2(**value)
    if status != 'available':
        raise ValueError('invalid explanation status')
    allowed = {'status', 'method', 'explained_scale', 'feature_snapshot_digest',
               'partial', 'base_value', 'remainder', 'items'}
    if set(value) != allowed or value['method'] not in {
            'rules', 'linear_log_odds', 'tree_path'}:
        raise ValueError('invalid available explanation schema')
    if value['explained_scale'] not in {
            'risk_score', 'log_odds', 'positive_class_estimate'}:
        raise ValueError('invalid explained scale')
    if type(value['partial']) is not bool or not isinstance(value['items'], (list, tuple)):
        raise ValueError('invalid explanation items')
    if len(value['items']) > 3 or any(not isinstance(item, dict) for item in value['items']):
        raise ValueError('invalid explanation items')
    item_fields = {'feature_key', 'observed_value', 'unit', 'direction',
                   'contribution', 'rule_condition'}
    catalog = feature_catalog()
    for item in value['items']:
        if (set(item) != item_fields
                or item['feature_key'] not in catalog
                or not all(isinstance(item[key], str) and item[key]
                           for key in ('feature_key', 'observed_value', 'unit'))
                or item['direction'] not in {'increases', 'decreases', 'neutral'}
                or (item['rule_condition'] is not None
                    and not isinstance(item['rule_condition'], str))):
            raise ValueError('unexpected explanation item fields')
        _finite_decimal(item['contribution'])
    for key in ('base_value', 'remainder'):
        if value[key] is not None:
            _finite_decimal(value[key])
    return ExplanationV2(**{**value, 'items': tuple(copy.deepcopy(value['items']))})


def score_v2(request: ScoreRequestV2, scorer: ScorerV2, *, artifact: object = None
             ) -> RiskAssessmentV2:
    """Validate both sides of an injected scorer; never fall back or repair output."""
    _request_v2(request)
    if not callable(getattr(scorer, 'score', None)):
        raise TypeError('ScorerV2.score required')
    if getattr(scorer, 'requires_artifact', False) and artifact is None:
        raise ValueError('required scorer artifact missing')
    if artifact is not None:
        if (not isinstance(artifact, dict)
                or artifact.get('scorer_version') != request.scorer_version
                or not isinstance(artifact.get('sha256'), str)
                or not _DIGEST_ID.fullmatch(artifact['sha256'])):
            raise ValueError('incompatible scorer artifact')
    result = scorer.score(copy.deepcopy(request))
    if not isinstance(result, dict):
        raise ValueError('scorer response schema mismatch')
    required = {name for name in RiskAssessmentV2.__dataclass_fields__}
    if set(result) != required:
        raise ValueError('unexpected or missing assessment fields')
    expected = {'transaction_id': request.canonical_transaction.transaction_id,
                'dataset_version': request.dataset_version, 'run_id': request.run_id,
                'scorer_version': request.scorer_version,
                'feature_version': request.feature_version,
                'event_time_utc': request.canonical_transaction.event_time_utc,
                'history_cutoff_exclusive_at': request.history_cutoff_exclusive_at}
    if any(result[key] != value for key, value in expected.items()):
        raise ValueError('scorer response identity mismatch')
    coverage = {'state': request.feature_snapshot.coverage_state,
                'start': request.feature_snapshot.coverage_start}
    if result['history_coverage'] != coverage:
        raise ValueError('scorer response coverage mismatch')
    if (result['score_source'] not in {'rules', 'model'}
            or result['score_kind'] not in {
                'ordinal_rule_score', 'uncalibrated_probability_estimate',
                'calibrated_probability'}
            or (result['score_source'] == 'rules'
                and result['score_kind'] != 'ordinal_rule_score')
            or (result['score_source'] == 'model'
                and (artifact is None or result['score_kind'] == 'ordinal_rule_score'))
            or (result['score_kind'] == 'calibrated_probability'
                and (artifact is None or artifact.get('calibrated') is not True))
            or not isinstance(result['artifact_version'], str)
            or result['artifact_version'] != request.scorer_version
            or (artifact is not None
                and artifact.get('artifact_version') != result['artifact_version'])):
        raise ValueError('scorer source, kind or artifact mismatch')
    scored_at = result['scored_at']
    if (not isinstance(scored_at, datetime) or scored_at.tzinfo is None
            or scored_at.astimezone(UTC) < request.history_cutoff_exclusive_at):
        raise ValueError('actual scored time invalid')
    score = _decimal_score(result['score'])
    explanation = _explanation_v2(result['explanation'],
                                  request.feature_snapshot.feature_input_digest)
    if result['score_source'] == 'rules' and explanation.status == 'available':
        if (explanation.method != 'rules' or explanation.explained_scale != 'risk_score'
                or explanation.partial is not False
                or explanation.base_value is None or explanation.remainder is None
                or (_finite_decimal(explanation.base_value)
                    + sum((_finite_decimal(item['contribution'])
                           for item in explanation.items), Decimal(0))
                    + _finite_decimal(explanation.remainder)) != score):
            raise ValueError('rule explanation source, scale or reconstruction mismatch')
    return RiskAssessmentV2(**{**result, 'score': score, 'explanation': explanation,
                               'history_coverage': copy.deepcopy(coverage)})
