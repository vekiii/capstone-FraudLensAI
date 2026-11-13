"""Strict Pydantic boundaries validated against the pinned local wire schemas."""
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import urljoin

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import BaseModel, ConfigDict, model_validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / 'specs/003-ai-investigation/contracts/schemas.json'
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
PRODUCER = json.loads(SCHEMA_PATH.with_name('producer-v2.snapshot.json').read_text())
FOUNDATION = json.loads((ROOT / 'specs/001-project-foundation/contracts/schemas.json').read_text())
REGISTRY = Registry().with_resources([
    (SCHEMA['$id'], Resource.from_contents(SCHEMA)),
    (urljoin(SCHEMA['$id'], 'producer-v2.snapshot.json'), Resource.from_contents(PRODUCER)),
    (urljoin(SCHEMA['$id'], '../../001-project-foundation/contracts/schemas.json'),
     Resource.from_contents(FOUNDATION)),
])


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def context_digest(value):
    return digest({k: v for k, v in value.items() if k != 'context_revision'})


def _finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Nonfinite number')
    if isinstance(value, dict):
        for k, v in value.items():
            if k == 'contract_version' and type(v) is not int:
                raise ValueError('Version must be integer')
            _finite(v)
    elif isinstance(value, list):
        for v in value:
            _finite(v)


def validate(name, value):
    """Revalidate snapshots, including models created without validation."""
    if isinstance(value, BaseModel):
        value = vars(value)
    value = copy.deepcopy(value)
    if isinstance(value, dict):
        for key in ('query', 'rationale', 'actor'):
            if isinstance(value.get(key), str):
                value[key] = value[key].strip()
    _finite(value)
    schema = {**SCHEMA, '$ref': '#/$defs/' + name}
    try:
        Draft202012Validator(schema, registry=REGISTRY,
                             format_checker=FormatChecker()).validate(value)
    except Exception as exc:
        # Never include rejected private input in public exception messages.
        raise ValueError('Invalid investigation contract') from exc
    if name == 'InvestigationContext':
        payload, history = value['source_payload'], value['history']
        validate('History', history)
        assessment, transaction = payload['risk_assessment'], payload['transaction']
        if value['case_id'] != payload['case_id']:
            raise ValueError('Case identity mismatch')
        if transaction['transaction_id'] != assessment['transaction_id']:
            raise ValueError('Transaction identity mismatch')
        if value['source_mode'] == 'dataset':
            if not (value['snapshot_ref'] == payload['snapshot_ref'] == assessment['run_id']):
                raise ValueError('Run identity mismatch')
            if not (value['dataset_version'] == payload['dataset_version'] == assessment['dataset_version']):
                raise ValueError('Dataset identity mismatch')
            if history['cutoff'] != assessment['history_cutoff_exclusive_at']:
                raise ValueError('Cutoff mismatch')
            explanation = assessment['explanation']
            if explanation['status'] == 'available' and explanation['explained_scale'] != {
                'rules': 'risk_score', 'linear_log_odds': 'log_odds',
                'tree_path': 'positive_class_estimate'}[explanation['method']]:
                raise ValueError('Explanation scale mismatch')
        elif assessment['source'] != 'fixture' or assessment['scorer_version'] != 'fixture-v1':
            raise ValueError('Fixture provenance changed')
        if value['context_revision'] != context_digest(value):
            raise ValueError('Context digest mismatch')
    if name == 'History':
        if value['availability'] == 'available' and (
            value['cutoff'] is None or value['coverage'] == 'unavailable' or value['start'] is None
        ):
            raise ValueError('Available history requires coverage')
    return value


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, revalidate_instances='always')
    definition: ClassVar[str]

    @model_validator(mode='before')
    @classmethod
    def check_contract(cls, value):
        return validate(cls.definition, value)


class History(Contract):
    definition = 'History'
    availability: str
    cutoff: Any
    coverage: str
    start: Any
    lookback_days: Any
    view_scope: str
    reason: Any


class InvestigationContext(Contract):
    definition = 'InvestigationContext'
    contract_version: Any
    context_revision: Any
    source_mode: str
    case_id: Any
    snapshot_ref: str
    dataset_version: Any
    observed_at: Any
    source_payload: dict[str, Any]
    history: Any


class Fact(Contract):
    definition = 'Fact'
    path: str
    value: str


class Assertion(Contract):
    definition = 'Assertion'
    evidence_ref: Any
    path: str
    value: str


class Quote(Contract):
    definition = 'Quote'
    evidence_ref: Any
    text: str


class Claim(Contract):
    definition = 'Claim'
    text: str
    kind: str
    evidence_refs: list[Any]
    exact_assertions: list[Any]
    quotes: list[Any]


class ReportDraft(Contract):
    definition = 'ReportDraft'
    outcome: str
    summary: list[Any]
    observed_facts: list[Any]
    risk_indicators: list[Any]
    alternative_explanations: list[Any]
    missing_information: list[Any]
    recommended_checks: list[Any]
    limitations: list[Any]
    citations: list[Any]


class Report(Contract):
    definition = 'Report'
    report_id: Any
    attempt_id: Any
    context_revision: Any
    created_at: Any
    validation: str
    semantic_review: str
    draft: Any


class ReviewRequest(Contract):
    definition = 'ReviewRequest'
    report_id: Any
    disposition: str
    rationale: str
    correction_note: Any
    supersedes_review_id: Any


class Review(Contract):
    definition = 'Review'
    review_id: Any
    report_id: Any
    actor: str
    disposition: str
    rationale: str
    correction_note: Any
    supersedes_review_id: Any
    created_at: Any


class CreateRequest(Contract):
    definition = 'CreateRequest'
    case_id: Any
    source_mode: str
    snapshot_ref: str


class RetryRequest(Contract):
    definition = 'RetryRequest'
    reuse_evidence: bool


class CancelRequest(Contract):
    definition = 'CancelRequest'


class Document(Contract):
    definition = 'Document'
    doc_id: str
    title: str
    origin_kind: str
    source_uri: str
    published_at: Any
    unknown_date_reason: Any
    retrieved_at: Any
    jurisdiction: str
    version: str
    reviewed_by: str
    reviewed_at: Any
    reuse_terms: str
    content_sha256: Any
    included_sections: list[Any]
    applicability_notes: str


class Passage(Contract):
    definition = 'Passage'
    passage_id: Any
    corpus_version: str
    document: Any
    section: str
    ordinal: int
    text: str
    content_sha256: Any


class SearchHit(Contract):
    definition = 'SearchHit'
    rank: int
    score: float
    passage: Any


class SearchResult(Contract):
    definition = 'SearchResult'
    contract_version: Any
    corpus_version: str
    retrieval_version: Any
    query: str
    status: str
    hits: list[Any]


class DocumentList(Contract):
    definition = 'DocumentList'
    contract_version: Any
    corpus_version: str
    documents: list[Any]


class Evidence(Contract):
    definition = 'Evidence'
    contract_version: Any
    evidence_id: Any
    attempt_id: Any
    context_revision: Any
    kind: str
    text: str
    facts: list[Any]
    passage: Any
    history: Any
    returned_count: int
    eligible_count: Any
    truncated: bool
    content_sha256: Any
    created_at: Any


class ErrorEnvelope(Contract):
    definition = 'ErrorEnvelope'
    contract_version: Any
    error: dict[str, Any]


class Failure(Contract):
    definition = 'Failure'
    code: str
    message: str
    outcome_unknown: bool


class Budget(Contract):
    definition = 'Budget'
    provider_requests: int
    tool_calls: int
    repairs: int
    transient_retries: int
    deadline: Any


class ToolTrace(Contract):
    definition = 'ToolTrace'
    sequence: int
    name: str
    status: str
    elapsed_ms: int
    evidence_refs: list[Any]


class RunView(Contract):
    definition = 'RunView'
    contract_version: Any
    run_id: Any
    attempt_id: Any
    parent_attempt_id: Any
    case_id: Any
    context_revision: Any
    source_mode: str
    snapshot_ref: str
    corpus_version: str
    retrieval_version: Any
    provider_mode: str
    requested_model: Any
    returned_model: Any
    state: str
    revision: int
    created_at: Any
    updated_at: Any
    budget: Any
    trace: list[Any]
    report: Any
    review: Any
    failure: Any


class RunList(Contract):
    definition = 'RunList'
    contract_version: Any
    total_count: int
    truncated: bool
    items: list[Any]


class CaseFactsArguments(Contract):
    definition = 'CaseFactsArguments'


class HistoryArguments(Contract):
    definition = 'HistoryArguments'
    account_side: str


class SearchArguments(Contract):
    definition = 'SearchArguments'
    query: str
