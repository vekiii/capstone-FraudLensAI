"""Strict foundation payloads; delivery identity checks belong to case services."""
import re
from typing import Annotated, Literal

from jsonschema import FormatChecker
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


def utc_timestamp(value: str) -> str:
    if not value.endswith('Z') or not FormatChecker().conforms(value, 'date-time'):
        raise ValueError('Expected a valid UTC date-time ending in Z')
    return value


def amount_string(value: str) -> str:
    if re.fullmatch(r'(0|[1-9][0-9]*)\.[0-9]{2}', value) is None:
        raise ValueError('Expected a nonnegative decimal string with two fractional digits')
    return value


def tx_id(value: str) -> str:
    if re.fullmatch(r'TX-[0-9]{3}', value) is None:
        raise ValueError('Invalid transaction identifier')
    return value


def case_id(value: str) -> str:
    if re.fullmatch(r'CASE-[0-9]{3}', value) is None:
        raise ValueError('Invalid case identifier')
    return value


TransactionId = Annotated[str, AfterValidator(tx_id)]
CaseId = Annotated[str, AfterValidator(case_id)]
Timestamp = Annotated[str, AfterValidator(utc_timestamp)]
Account = Annotated[str, StringConstraints(min_length=1, max_length=120)]
Score = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
Source = Literal['fixture', 'rules', 'model']


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class Transaction(Contract):
    transaction_id: TransactionId
    occurred_at: Timestamp
    sender_account: Account
    receiver_account: Account
    amount: Annotated[str, AfterValidator(amount_string)]
    currency: Annotated[str, StringConstraints(min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')]


class RiskAssessment(Contract):
    transaction_id: TransactionId
    score: Score
    source: Source
    scorer_version: Annotated[str, StringConstraints(min_length=1, max_length=80)]
    scored_at: Timestamp
    explanation: Annotated[str, StringConstraints(min_length=1, max_length=500)]


class CaseSummary(Contract):
    case_id: CaseId
    transaction_id: TransactionId
    score: Score
    score_source: Source


class CaseDetail(Contract):
    case_id: CaseId
    transaction: Transaction
    risk_assessment: RiskAssessment


class CaseList(Contract):
    items: list[CaseSummary]


class Health(Contract):
    status: Literal['ok']
    mode: Literal['fixture']


class ModelHealth(Contract):
    status: Literal['ok']
    mode: Literal['model']


class ErrorBody(Contract):
    code: Literal['invalid_request', 'case_not_found', 'internal_error']
    message: Annotated[str, StringConstraints(min_length=1, max_length=200)]


class Error(Contract):
    error: ErrorBody


class PredictionResult(Contract):
    """Feature 002 v1 assessment; no target or ground truth fields."""

    transaction_id: Annotated[str, StringConstraints(
        min_length=1, max_length=160,
        pattern=r'^ibm-hi-small:[0-9a-f]{64}:row:[1-9][0-9]*$')]
    risk_score: Score
    review_status: Literal['review_recommended', 'below_threshold']
    source: Literal['model']
    model_version: Annotated[str, StringConstraints(min_length=1, max_length=80)]
    feature_version: Annotated[str, StringConstraints(min_length=1, max_length=80)]
    synthetic_data: Literal[True]
    scored_at: Timestamp
    explanation: Annotated[str, StringConstraints(min_length=1, max_length=1000)]


class RiskErrorBody(Contract):
    code: Literal['invalid_request', 'transaction_not_found', 'transaction_ineligible',
                  'model_unavailable', 'internal_error']
    message: Annotated[str, StringConstraints(min_length=1, max_length=200)]


class RiskError(Contract):
    error: RiskErrorBody


class Metric(Contract):
    name: Annotated[str, StringConstraints(min_length=1, max_length=80)]
    value: Annotated[float, Field(allow_inf_nan=False)] | None
    denominator: Annotated[int, Field(ge=0)]
    unit: Annotated[str, StringConstraints(min_length=1, max_length=40)]


class PartitionResults(Contract):
    partition: Literal['train', 'validation', 'test']
    state: Literal['available', 'not_authorized', 'unavailable']
    synthetic_data: Literal[True]
    coverage_utc: Annotated[str, StringConstraints(min_length=1, max_length=120)]
    row_count: Annotated[int, Field(ge=0)]
    positive_count: Annotated[int, Field(ge=0)]
    negative_count: Annotated[int, Field(ge=0)]
    metrics: Annotated[list[Metric], Field(max_length=40)]


class ModelResults(Contract):
    model_version: Annotated[str, StringConstraints(min_length=1, max_length=80)]
    feature_version: Annotated[str, StringConstraints(min_length=1, max_length=80)]
    dataset_version: Annotated[str, StringConstraints(min_length=1, max_length=120)]
    threshold: Score | None
    calibration_status: Literal['not_assessed', 'assessed']
    partitions: Annotated[list[PartitionResults], Field(max_length=3)]
    limitations: Annotated[list[Annotated[str, StringConstraints(max_length=300)]],
                           Field(max_length=20)]


class ResultsErrorBody(Contract):
    code: Literal['invalid_request', 'results_unavailable',
                  'evaluation_not_authorized', 'internal_error']
    message: Annotated[str, StringConstraints(min_length=1, max_length=200)]


class ResultsError(Contract):
    error: ResultsErrorBody


class EdaSeries(Contract):
    series_id: Annotated[str, StringConstraints(min_length=1, max_length=80)]
    label: Annotated[str, StringConstraints(min_length=1, max_length=120)]
    unit: Literal['transactions', 'amount']
    bucket_labels: Annotated[list[Annotated[str, StringConstraints(max_length=120)]],
                             Field(max_length=366)]
    values: Annotated[list[Annotated[float, Field(ge=0, allow_inf_nan=False)]],
                      Field(max_length=366)]
    denominator: Annotated[int, Field(ge=0)]
    currency: Annotated[str, StringConstraints(min_length=1, max_length=40)] | None = None
    side: Literal['paid', 'received'] | None = None
    timezone: Literal['UTC'] | None = None

    @model_validator(mode='after')
    def check_series(self) -> 'EdaSeries':
        if len(self.bucket_labels) != len(self.values):
            raise ValueError('EDA bucket/value lengths differ')
        if self.unit == 'amount' and (self.currency is None or self.side is None):
            raise ValueError('amount series requires a side and one currency')
        if self.unit == 'transactions' and (self.currency is not None or self.side is not None):
            raise ValueError('count series cannot have a currency or amount side')
        return self


class EdaSummary(Contract):
    dataset_version: Annotated[str, StringConstraints(min_length=1, max_length=120)]
    source_sha256: Annotated[str, StringConstraints(pattern=r'^[0-9a-f]{64}$')]
    synthetic_data: Literal[True]
    coverage_start_utc: Timestamp | None
    coverage_end_utc: Timestamp | None
    source_count: Annotated[int, Field(ge=0)]
    accepted_count: Annotated[int, Field(ge=0)]
    rejected_count: Annotated[int, Field(ge=0)]
    warmup_count: Annotated[int, Field(ge=0)]
    scoreable_count: Annotated[int, Field(ge=0)]
    quality_counts: Annotated[dict[str, Annotated[int, Field(ge=0)]], Field(max_length=20)]
    omitted_amount_currencies: dict[Literal['paid', 'received'], Annotated[int, Field(ge=0)]]
    series: Annotated[list[EdaSeries], Field(max_length=30)]

    @model_validator(mode='after')
    def check_counts(self) -> 'EdaSummary':
        if self.source_count != self.accepted_count + self.rejected_count:
            raise ValueError('source/accepted/rejected EDA counts do not reconcile')
        if self.accepted_count != self.warmup_count + self.scoreable_count:
            raise ValueError('warm-up/scoreable EDA counts do not reconcile')
        if (self.coverage_start_utc is None) != (self.coverage_end_utc is None):
            raise ValueError('EDA coverage must be complete or empty')
        if self.accepted_count == 0 and self.coverage_start_utc is not None:
            raise ValueError('empty EDA coverage must be null')
        if self.accepted_count > 0 and self.coverage_start_utc is None:
            raise ValueError('nonempty EDA coverage is required')
        forbidden = ('label', 'launder', 'target', 'positive', 'negative', 'fraud')
        if any(any(part in key.lower() for part in forbidden) for key in self.quality_counts):
            raise ValueError('label-derived EDA quality key is forbidden')
        allowed_counts = {
            'sender_bank_count', 'receiver_bank_count', 'payment_currency_count',
            'receiving_currency_count', 'payment_format_count', 'utc_transaction_count',
        }
        for item in self.series:
            if item.unit == 'transactions' and item.series_id not in allowed_counts:
                raise ValueError('unknown EDA count series')
            if item.unit == 'amount' and item.series_id != (
                f'{item.side}_amount_{item.currency}'
            ):
                raise ValueError('unknown EDA amount series')
        return self


class EdaErrorBody(Contract):
    code: Literal['invalid_request', 'dataset_unavailable', 'internal_error']
    message: Annotated[str, StringConstraints(min_length=1, max_length=200)]


class EdaError(Contract):
    error: EdaErrorBody
