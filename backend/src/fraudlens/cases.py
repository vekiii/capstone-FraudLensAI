"""Load synthetic cases and validate assessments before case delivery."""
import json
from pathlib import Path

from pydantic import TypeAdapter

from fraudlens.contracts import (
    CaseDetail,
    CaseId,
    CaseList,
    CaseSummary,
    Contract,
    RiskAssessment,
    Transaction,
)
from fraudlens.scoring import Scorer, validate_transaction
from fraudlens.settings import Settings


class FixtureCase(Contract):
    """Closed storage projection using only existing case/transaction fields."""

    case_id: CaseId
    transaction: Transaction


class FixtureLoadError(Exception):
    """Generic repository failure; HTTP translation belongs to case delivery."""


class CaseScoringError(Exception):
    """Invalid input, scorer failure or invalid assessment; never a fallback result."""


class CaseNotFoundError(Exception):
    """A valid case identifier is absent from the fixture collection."""


_FIXTURE_CASES = TypeAdapter(list[FixtureCase])


def _unique_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous JSON objects instead of accepting the last duplicate key."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON member')
        result[key] = value
    return result


def load_cases(path: Path | None = None) -> list[FixtureCase]:
    """Return fresh validated records ordered by case_id, without scoring or writes.

    The shipped file has three cases; an injected empty collection is valid.
    Import/startup does not read fixtures, and no mutable records are cached.
    """
    try:
        fixture_path = Settings().fixture_path if path is None else Path(path)
        payload = json.loads(fixture_path.read_text(encoding='utf-8'),
                             object_pairs_hook=_unique_members)
        cases = _FIXTURE_CASES.validate_python(payload, strict=True)
        case_ids = [case.case_id for case in cases]
        transaction_ids = [case.transaction.transaction_id for case in cases]
        if len(case_ids) != len(set(case_ids)) or len(transaction_ids) != len(set(transaction_ids)):
            raise ValueError('Duplicate fixture identity')
    except (OSError, ValueError):
        # Includes decoding, JSON and Pydantic validation failures. Do not expose
        # paths, rejected input values or a chained internal exception to callers.
        raise FixtureLoadError('Unable to load synthetic cases.') from None
    return sorted(cases, key=lambda case: case.case_id)


def score_case(case: FixtureCase, scorer: Scorer) -> CaseDetail:
    """Score a validated case snapshot and enforce identity before delivery.

    No HTTP behavior here. Both list and detail delivery use this
    boundary, with a scorer supplied by their caller.
    """
    try:
        if not isinstance(case, FixtureCase) or case.model_extra:
            raise ValueError('Invalid case input')
        transaction = validate_transaction(vars(case).get('transaction'))
        validated_case = FixtureCase.model_validate(
            {**vars(case), 'transaction': transaction}, strict=True)
    except (ValueError, TypeError):
        raise CaseScoringError('Unable to score case.') from None

    scoring_input = transaction.model_copy(deep=True)
    try:
        # Only this adapter call translates arbitrary third-party exceptions.
        # Unexpected bugs in our service code remain visible to the server.
        result = scorer.score(scoring_input)
    except Exception:
        raise CaseScoringError('Unable to score case.') from None

    try:
        if validate_transaction(scoring_input) != transaction:
            raise ValueError('Scorer altered its transaction input')
        if not isinstance(result, RiskAssessment) or result.model_extra:
            raise ValueError('Invalid assessment type or fields')
        assessment = RiskAssessment.model_validate(vars(result), strict=True)
        if assessment.transaction_id != transaction.transaction_id:
            raise ValueError('Assessment transaction identity mismatch')
        return CaseDetail(case_id=validated_case.case_id, transaction=transaction,
                          risk_assessment=assessment)
    except (ValueError, TypeError):
        raise CaseScoringError('Unable to score case.') from None


class CaseService:
    """Lazy fixture access and shared scoring for list/detail delivery."""

    def __init__(self, fixture_path: Path, scorer: Scorer):
        self.fixture_path = fixture_path
        self.scorer = scorer

    def list_cases(self) -> CaseList:
        details = [score_case(case, self.scorer) for case in load_cases(self.fixture_path)]
        return CaseList(items=[
            CaseSummary(case_id=detail.case_id,
                        transaction_id=detail.transaction.transaction_id,
                        score=detail.risk_assessment.score,
                        score_source=detail.risk_assessment.source)
            for detail in details
        ])

    def get_case(self, case_id: CaseId) -> CaseDetail:
        for case in load_cases(self.fixture_path):
            if case.case_id == case_id:
                return score_case(case, self.scorer)
        raise CaseNotFoundError('Case not found.')
