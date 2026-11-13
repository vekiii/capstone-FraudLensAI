"""Internal Feature 002 import objects; private labels never enter operational facts."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

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
