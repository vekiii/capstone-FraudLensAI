"""Strict foundation payloads; delivery identity checks belong to case services."""
import re
from typing import Annotated, Literal

from jsonschema import FormatChecker
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints


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


class ErrorBody(Contract):
    code: Literal['invalid_request', 'case_not_found', 'internal_error']
    message: Annotated[str, StringConstraints(min_length=1, max_length=200)]


class Error(Contract):
    error: ErrorBody
