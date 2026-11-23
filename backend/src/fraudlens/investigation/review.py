"""Explicit analyst review boundary; never called by provider/tool orchestration."""
from uuid import UUID

from fraudlens.investigation.models import validate


class AnalystReviewService:
    def __init__(self, investigation):
        self.investigation = investigation

    def submit(self, attempt_id, revision, request, actor, key):
        validate('AttemptId', attempt_id)
        request = validate('ReviewRequest', request)
        UUID(key)
        if not isinstance(actor, str) or not 1 <= len(actor.strip()) <= 80:
            raise ValueError('Invalid review actor')
        actor = actor.strip()
        service = self.investigation
        payload = dict(attempt_id=attempt_id, revision=revision, request=request)
        # No provider, source refresh, evidence regeneration or external I/O here.
        with service.repo.transaction() as db:
            replay = service.repo.replay(db, actor, 'review', key, payload)
            if replay:
                return replay
            service.repo.append_review(db, attempt_id, revision, actor, request)
            result = service._transaction_view(db, attempt_id)
            service.repo.remember(db, actor, 'review', key, payload, result)
            return result
