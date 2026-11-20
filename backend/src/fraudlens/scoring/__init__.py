"""Deterministic illustrative scoring, with no model or external service."""
from typing import Protocol

from fraudlens.contracts import RiskAssessment, Transaction

_DEMO_SCORES = (0.75, 0.40, 0.10)


class Scorer(Protocol):
    """Replaceable synchronous assessment boundary; delivery validates its result."""

    def score(self, transaction: Transaction) -> RiskAssessment: ...


class ScoringError(Exception):
    """Controlled failure, never a substitute score."""


def validate_transaction(transaction: Transaction) -> Transaction:
    """Revalidate a fresh snapshot, including mutated/constructed model instances."""
    if not isinstance(transaction, Transaction) or transaction.model_extra:
        raise ValueError('Invalid transaction input')
    # Validating an existing model directly would trust it by default. model_dump
    # can hide unvalidated extra keys; vars preserves them for closed validation.
    return Transaction.model_validate(vars(transaction), strict=True)


class FixtureScorer:
    """Rotate constants by (numeric TX suffix - 1) % 3, solely for demo variety.

    TX-001/002/003 yield 0.75/0.40/0.10. The same rule covers every valid TX ID;
    it is not an AML heuristic or an estimate of fraud probability. scored_at
    repeats occurred_at as a reproducible fixture timestamp, not wall-clock time.
    """

    def score(self, transaction: Transaction) -> RiskAssessment:
        try:
            validated = validate_transaction(transaction)
            index = (int(validated.transaction_id[3:]) - 1) % len(_DEMO_SCORES)
            return RiskAssessment(
                transaction_id=validated.transaction_id,
                score=_DEMO_SCORES[index], source='fixture', scorer_version='fixture-v1',
                scored_at=validated.occurred_at,
                explanation=(
                    'Illustrative synthetic fixture score selected by transaction ID; '
                    'no ML inference or verified fraud finding. '
                    'scored_at repeats transaction time for reproducibility.'
                ),
            )
        except (ValueError, TypeError):
            raise ScoringError('Unable to score synthetic transaction.') from None
