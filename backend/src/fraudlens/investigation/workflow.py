"""Durable bounded investigation boundary; no work in ordinary creation/GET."""
import asyncio
import json
import time
from datetime import UTC, datetime
from uuid import uuid4

from fraudlens.investigation.context import CaseContextReader, outbound_context
from fraudlens.investigation.models import SCHEMA, canonical, digest, validate
from fraudlens.investigation.provider import ProviderError, ScriptedProvider
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.tools import ToolExecutor, definitions
from fraudlens.investigation.validation import validate_report

ACTIVE = {'gathering_evidence', 'drafting'}


def instant(timestamp=None):
    return datetime.fromtimestamp(timestamp if timestamp is not None else time.time(), UTC).isoformat().replace('+00:00', 'Z')


def event(db, attempt, operation, **values):
    db.execute('INSERT INTO audit_events(attempt_id,content) VALUES (?,?)',
               (attempt, canonical(dict(operation=operation, timestamp=instant(), **values)).decode()))


class InvestigationService:
    def __init__(self, repository, knowledge, settings=None, provider_factory=None):
        self.repo, self.knowledge = repository, knowledge
        self.settings = settings or InvestigationSettings()
        self.provider_factory = provider_factory or self._provider
        self.context_reader = CaseContextReader()

    def _provider(self, binding):
        if binding['provider_mode'] == 'test':
            return ScriptedProvider(binding.get('test_scenario', 'grounded'))
        from fraudlens.investigation.provider import OpenAIProvider
        return OpenAIProvider(self.settings.api_key.get_secret_value(), binding['requested_model'],
                              prompt=binding['prompt'])

    def events(self, attempt_id):
        with self.repo.connection() as db:
            return [json.loads(row[0]) for row in db.execute(
                'SELECT content FROM audit_events WHERE attempt_id=? ORDER BY id', (attempt_id,))]

    def binding(self, attempt_id):
        return next(item for item in self.events(attempt_id) if item['operation'] == 'binding')

    def context(self, attempt_id):
        row = self.repo.get(attempt_id)
        with self.repo.connection() as db:
            data = db.execute('SELECT content FROM contexts WHERE revision=?', (row['context_revision'],)).fetchone()
        return validate('InvestigationContext', json.loads(data[0]))

    def create(self, request, actor, request_key):
        request = validate('CreateRequest', request)
        context = self.context_reader.resolve(request['case_id'], request['source_mode'], request['snapshot_ref'])
        corpus, retrieval = self.knowledge.latest('corpus'), self.knowledge.latest('retrieval')
        self.knowledge.corpus(corpus)
        self.knowledge.configuration(retrieval)
        if self.settings.provider == 'openai' and not self.settings.api_key.get_secret_value():
            raise ValueError('provider_unavailable')
        from fraudlens.investigation.models import ROOT
        prompt = (ROOT / 'prompts/application/investigation-v1.md').read_text(encoding='utf-8')
        limits = {key: getattr(self.settings, key) for key in (
            'max_provider_requests', 'max_tool_calls', 'total_timeout_seconds', 'request_timeout_seconds',
            'max_input_bytes', 'max_output_tokens', 'max_response_bytes')}
        binding = dict(corpus_version=corpus, retrieval_version=retrieval, prompt=prompt,
                       prompt_version=digest(prompt), limits=limits, timestamp=instant(),
                       provider_mode=self.settings.provider, requested_model=(
                           self.settings.model.get_secret_value() if self.settings.provider == 'openai' else None),
                       test_scenario=getattr(self.settings, 'test_scenario', 'grounded'))
        row = self.repo.create(context, actor, 'create', request_key, request, binding=binding)
        return self.read(row['attempt_id'])

    def _reconcile(self, attempt_id):
        with self.repo.transaction() as db:
            row = db.execute('SELECT state,revision FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            lease = db.execute('SELECT attempt_id,expires FROM worker_lease WHERE singleton=1').fetchone()
            if row and row[0] in ACTIVE and lease[0] == attempt_id and lease[1] < time.time():
                self._failure(db, attempt_id, row[1], 'budget_exhausted', True)

    def _failure(self, db, attempt_id, revision, code, unknown=False):
        allowed = SCHEMA['$defs']['Failure']['properties']['code']['enum']
        code = code if code in allowed else 'context_unavailable'
        event(db, attempt_id, 'failure', failure=validate('Failure', dict(code=code,
            message='Investigation ended with a controlled limitation or failure.', outcome_unknown=unknown)))
        db.execute("UPDATE provider_dispatches SET outcome='unknown' WHERE attempt_id=? AND outcome='pending'", (attempt_id,))
        self.repo._transition(db, attempt_id, revision, 'failed')

    def fail(self, attempt_id, code, unknown=False):
        with self.repo.transaction() as db:
            row = db.execute('SELECT state,revision FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            if row and row[0] in ACTIVE | {'created'}:
                self._failure(db, attempt_id, row[1], code, unknown)

    def read(self, attempt_id):
        validate('AttemptId', attempt_id)
        self._reconcile(attempt_id)
        row = self.repo.get(attempt_id)
        context, events = self.context(attempt_id), self.events(attempt_id)
        binding = next(item for item in events if item['operation'] == 'binding')
        latest = {item['operation']: item for item in events}
        with self.repo.connection() as db:
            steps = [json.loads(item[0]) for item in db.execute(
                'SELECT content FROM tool_steps WHERE attempt_id=? ORDER BY sequence', (attempt_id,))]
        trace = [dict(sequence=i + 1, name=item['name'],
                      status='failed' if item['status'] == 'reserved' else item['status'],
                      elapsed_ms=item.get('elapsed_ms', 0), evidence_refs=item.get('evidence_refs', []))
                 for i, item in enumerate(steps)]
        completed = [item for item in events if item['operation'] == 'dispatch_result']
        returned_model = next((item['returned_model'] for item in reversed(completed)
                               if item.get('returned_model')), None)
        return validate('RunView', dict(contract_version=1, run_id=row['run_id'], attempt_id=attempt_id,
            parent_attempt_id=None, case_id=context['case_id'], context_revision=row['context_revision'],
            source_mode=context['source_mode'], snapshot_ref=context['snapshot_ref'],
            corpus_version=binding['corpus_version'], retrieval_version=binding['retrieval_version'],
            provider_mode=binding['provider_mode'], requested_model=binding['requested_model'],
            returned_model=returned_model, state=row['state'], revision=row['revision'],
            created_at=instant(row['created_at']), updated_at=next(
                (item['timestamp'] for item in reversed(events) if 'timestamp' in item), instant(row['created_at'])),
            budget=dict(provider_requests=row['provider_requests'], tool_calls=len(steps),
                repairs=sum(item['operation'] == 'repair' for item in events),
                transient_retries=sum(item['operation'] == 'transient_retry' for item in events),
                deadline=latest.get('worker_started', {}).get('deadline')),
            trace=trace, report=latest.get('report', {}).get('report'), review=None,
            failure=latest.get('failure', {}).get('failure')))

    def evidence(self, attempt_id):
        self.repo.get(attempt_id)
        with self.repo.connection() as db:
            return [validate('Evidence', json.loads(row[0])) for row in db.execute(
                'SELECT content FROM evidence_items WHERE attempt_id=? ORDER BY rowid', (attempt_id,))]

    def _claim(self, attempt_id, owner, seconds):
        self.repo.claim(attempt_id, owner)
        deadline = time.time() + seconds
        with self.repo.transaction() as db:
            db.execute('UPDATE worker_lease SET expires=? WHERE singleton=1 AND attempt_id=? AND owner=?',
                       (deadline, attempt_id, owner))
            event(db, attempt_id, 'worker_started', deadline=instant(deadline))

    def _dispatch_result(self, attempt_id, sequence, outcome, turn=None):
        with self.repo.transaction() as db:
            db.execute('UPDATE provider_dispatches SET outcome=? WHERE attempt_id=? AND sequence=?',
                       (outcome, attempt_id, sequence))
            event(db, attempt_id, 'dispatch_result', sequence=sequence, outcome=outcome,
                  returned_model=turn.returned_model if turn else None,
                  request_id=turn.request_id if turn else None, usage=turn.usage if turn else None,
                  private_items=list(turn.private_items) if turn else [])

    def _complete(self, attempt_id, owner, report):
        with self.repo.transaction() as db:
            row = db.execute('SELECT state,revision FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            lease = db.execute('SELECT attempt_id,owner,expires FROM worker_lease WHERE singleton=1').fetchone()
            if row[0] != 'drafting' or lease[:2] != (attempt_id, owner) or lease[2] < time.time():
                raise ValueError('stale_worker')
            content = dict(attempt_id=attempt_id, context_revision=report['context_revision'], draft=report['draft'])
            db.execute('INSERT INTO reports VALUES (?,?,?)',
                       (report['report_id'], attempt_id, canonical(content).decode()))
            event(db, attempt_id, 'report', report=report)
            self.repo._transition(db, attempt_id, row[1], report['draft']['outcome'])
            db.execute('UPDATE worker_lease SET attempt_id=NULL,owner=NULL,expires=NULL WHERE singleton=1 AND owner=?', (owner,))

    async def work_once(self):
        with self.repo.connection() as db:
            active = [row[0] for row in db.execute("SELECT attempt_id FROM attempts WHERE state IN ('gathering_evidence','drafting')")]
        for attempt in active:
            self._reconcile(attempt)
        with self.repo.connection() as db:
            row = db.execute("SELECT attempt_id FROM attempts WHERE state='created' ORDER BY created_at,attempt_id LIMIT 1").fetchone()
        if row is None:
            return None
        attempt_id, owner = row[0], 'worker_' + uuid4().hex
        binding, context = self.binding(attempt_id), self.context(attempt_id)
        limits = binding['limits']
        try:
            self._claim(attempt_id, owner, limits['total_timeout_seconds'])
        except ValueError:
            return None
        deadline = time.monotonic() + limits['total_timeout_seconds']
        messages = [dict(type='context', data=outbound_context(context, self.repo.get(attempt_id)['run_id']))]
        retries, repairs = 0, 0
        try:
            self.context_reader.resolve(context['case_id'], context['source_mode'], context['snapshot_ref'])
            provider = self.provider_factory(binding)
            executor = ToolExecutor(self.repo, attempt_id, owner, context, self.knowledge,
                                    binding['corpus_version'], binding['retrieval_version'])
            while True:
                view = self.read(attempt_id)
                remaining = deadline - time.monotonic()
                if view['state'] not in ACTIVE or remaining <= 0:
                    raise ProviderError('budget_exhausted')
                if view['budget']['provider_requests'] >= limits['max_provider_requests']:
                    raise ProviderError('budget_exhausted')
                sequence = self.repo.reserve_dispatch(attempt_id, owner)
                request_limits = dict(request_timeout=min(30, limits['request_timeout_seconds'], remaining),
                    max_input_bytes=limits['max_input_bytes'], max_output_tokens=limits['max_output_tokens'],
                    max_response_bytes=limits['max_response_bytes'])
                try:
                    async with asyncio.timeout(request_limits['request_timeout']):
                        turn = await provider.next_turn(messages, definitions(), SCHEMA['$defs']['ReportDraft'], request_limits)
                except TimeoutError:
                    raise ProviderError('budget_exhausted', outcome_unknown=True) from None
                except ProviderError as exc:
                    self._dispatch_result(attempt_id, sequence, 'unknown' if exc.outcome_unknown else 'failed')
                    if exc.retryable and retries == 0 and 0 <= exc.retry_after <= 2 and exc.code != 'provider_access':
                        retries += 1
                        with self.repo.transaction() as db:
                            event(db, attempt_id, 'transient_retry')
                        async with asyncio.timeout(max(0, deadline - time.monotonic())):
                            await asyncio.sleep(exc.retry_after)
                        continue
                    raise
                self._dispatch_result(attempt_id, sequence, 'completed', turn)
                if time.monotonic() >= deadline:
                    raise ProviderError('budget_exhausted')
                if turn.kind in ('refusal', 'incomplete'):
                    raise ProviderError('provider_' + turn.kind)
                if turn.kind == 'tools' and turn.calls:
                    for call in turn.calls:
                        if self.read(attempt_id)['budget']['tool_calls'] >= limits['max_tool_calls']:
                            raise ProviderError('budget_exhausted')
                        if time.monotonic() >= deadline:
                            raise ProviderError('budget_exhausted')
                        try:
                            result = executor.execute(call['call_id'], call['name'], call['arguments'])
                        except ValueError as exc:
                            if 'budget' in str(exc):
                                raise ProviderError('budget_exhausted') from None
                            raise ProviderError('tool_result_too_large' if str(exc) == 'tool_result_too_large' else 'context_unavailable') from None
                        messages.extend([dict(type='tool_call', **call),
                                         dict(type='tool_result', call_id=call['call_id'], result=result)])
                    continue
                if turn.kind != 'draft' or turn.draft is None:
                    raise ProviderError('provider_incomplete')
                with self.repo.transaction() as db:
                    current = db.execute('SELECT state,revision FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
                    if current[0] == 'gathering_evidence':
                        self.repo._transition(db, attempt_id, current[1], 'drafting')
                        event(db, attempt_id, 'state', state='drafting')
                    elif current[0] != 'drafting':
                        raise ProviderError('interrupted')
                try:
                    report = validate_report(turn.draft, self.evidence(attempt_id), attempt_id,
                        context['context_revision'], context, binding['corpus_version'])
                except ValueError:
                    if repairs:
                        raise ProviderError('output_invalid') from None
                    repairs += 1
                    with self.repo.transaction() as db:
                        event(db, attempt_id, 'repair')
                    messages.append(dict(type='repair', code='output_invalid'))
                    continue
                self._complete(attempt_id, owner, report)
                break
        except ProviderError as exc:
            self.fail(attempt_id, exc.code, exc.outcome_unknown)
        except (ValueError, OSError, KeyError):
            self.fail(attempt_id, 'stale_snapshot')
        except asyncio.CancelledError:
            self.fail(attempt_id, 'interrupted', True)
            raise
        return self.read(attempt_id)
