"""Minimal dedicated SQLite primitives; no workflow, provider or route execution."""
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID, uuid4

from fraudlens.investigation.models import canonical, digest, validate

TRANSITIONS = {
    'created': {'gathering_evidence', 'failed', 'cancelled'},
    'gathering_evidence': {'drafting', 'needs_information', 'failed', 'cancelled'},
    'drafting': {'ready_for_review', 'needs_information', 'failed', 'cancelled'},
    'ready_for_review': {'reviewed'}, 'needs_information': {'reviewed'},
}
DDL = '''
CREATE TABLE schema_meta(version INTEGER NOT NULL);
INSERT INTO schema_meta VALUES (1);
CREATE TABLE contexts(revision TEXT PRIMARY KEY,content TEXT NOT NULL);
CREATE TABLE investigation_runs(run_id TEXT PRIMARY KEY,context_revision TEXT NOT NULL REFERENCES contexts(revision));
CREATE TABLE attempts(attempt_id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES investigation_runs,
context_revision TEXT NOT NULL REFERENCES contexts(revision),state TEXT NOT NULL,revision INTEGER NOT NULL CHECK(revision>=1),
provider_requests INTEGER NOT NULL DEFAULT 0 CHECK(provider_requests BETWEEN 0 AND 8),created_at REAL NOT NULL);
CREATE TABLE request_keys(actor TEXT,operation TEXT,request_key TEXT,payload_digest TEXT NOT NULL,response TEXT NOT NULL,
attempt_id TEXT NOT NULL REFERENCES attempts,PRIMARY KEY(actor,operation,request_key));
CREATE TABLE evidence_items(evidence_id TEXT PRIMARY KEY,attempt_id TEXT NOT NULL REFERENCES attempts,content TEXT NOT NULL);
CREATE TABLE provider_dispatches(attempt_id TEXT NOT NULL REFERENCES attempts,sequence INTEGER NOT NULL,
outcome TEXT NOT NULL,reserved_at REAL NOT NULL,PRIMARY KEY(attempt_id,sequence));
CREATE TABLE tool_steps(attempt_id TEXT NOT NULL REFERENCES attempts,sequence INTEGER NOT NULL,content TEXT NOT NULL,PRIMARY KEY(attempt_id,sequence));
CREATE TABLE reports(report_id TEXT PRIMARY KEY,attempt_id TEXT NOT NULL REFERENCES attempts,content TEXT NOT NULL);
CREATE TABLE reviews(review_id TEXT PRIMARY KEY,attempt_id TEXT NOT NULL REFERENCES attempts,report_id TEXT NOT NULL REFERENCES reports,content TEXT NOT NULL);
CREATE TABLE audit_events(id INTEGER PRIMARY KEY,attempt_id TEXT NOT NULL REFERENCES attempts,content TEXT NOT NULL);
CREATE TABLE worker_lease(singleton INTEGER PRIMARY KEY CHECK(singleton=1),attempt_id TEXT REFERENCES attempts,owner TEXT,expires REAL);
INSERT INTO worker_lease VALUES (1,NULL,NULL,NULL);
'''


class InvestigationRepository:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if tables:
                if 'schema_meta' not in tables or db.execute('SELECT version FROM schema_meta').fetchall() != [(1,)]:
                    raise ValueError('Unsupported investigation schema')
            else:
                db.executescript('BEGIN IMMEDIATE;\n' + DDL + '\nCOMMIT;')
                for table in ('contexts', 'evidence_items', 'reports', 'reviews', 'audit_events', 'request_keys'):
                    for action in ('UPDATE', 'DELETE'):
                        db.execute(f'CREATE TRIGGER immutable_{table}_{action} BEFORE {action} ON {table} '
                                   "BEGIN SELECT RAISE(ABORT, 'Immutable record'); END")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=0.5, isolation_level=None)
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA busy_timeout=500')
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise

    def get(self, attempt_id):
        with self.connection() as db:
            db.row_factory = sqlite3.Row
            row = db.execute('SELECT * FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            if row is None:
                raise ValueError('Investigation not found')
            return dict(row)

    def create(self, context, actor, operation, request_key, payload, binding=None):
        UUID(request_key)
        if not isinstance(actor, str) or not 1 <= len(actor.strip()) <= 80:
            raise ValueError('Invalid actor')
        context = validate('InvestigationContext', context)
        request_digest = digest({'context': context, 'payload': payload})
        with self.transaction() as db:
            old = db.execute('SELECT payload_digest,attempt_id,response FROM request_keys WHERE actor=? AND operation=? AND request_key=?',
                             (actor, operation, request_key)).fetchone()
            if old:
                if old[0] != request_digest:
                    raise ValueError('request_conflict')
                response = json.loads(old[2])
            else:
                revision = context['context_revision']
                content = canonical(context).decode()
                old_context = db.execute('SELECT content FROM contexts WHERE revision=?', (revision,)).fetchone()
                if old_context and old_context[0] != content:
                    raise ValueError('Context digest conflict')
                if not old_context:
                    db.execute('INSERT INTO contexts VALUES (?,?)', (revision, content))
                run_id, attempt_id = 'inv_' + uuid4().hex, 'att_' + uuid4().hex
                db.execute('INSERT INTO investigation_runs VALUES (?,?)', (run_id, revision))
                db.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?)',
                           (attempt_id, run_id, revision, 'created', 1, 0, time.time()))
                if binding is not None:
                    db.execute('INSERT INTO audit_events(attempt_id,content) VALUES (?,?)',
                               (attempt_id, canonical({'operation': 'binding', **binding}).decode()))
                cursor = db.execute('SELECT * FROM attempts WHERE attempt_id=?', (attempt_id,))
                response = dict(zip([field[0] for field in cursor.description], cursor.fetchone()))
                db.execute('INSERT INTO request_keys VALUES (?,?,?,?,?,?)',
                           (actor, operation, request_key, request_digest, canonical(response).decode(), attempt_id))
        return response

    def transition(self, attempt_id, expected_revision, state):
        if state == 'reviewed':
            raise ValueError('Use atomic review operation')
        with self.transaction() as db:
            self._transition(db, attempt_id, expected_revision, state)
        return self.get(attempt_id)

    def _transition(self, db, attempt_id, expected_revision, state):
        row = db.execute('SELECT state,revision FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
        if row is None or row[1] != expected_revision:
            raise ValueError('revision_conflict')
        if state not in TRANSITIONS.get(row[0], set()):
            raise ValueError('invalid_transition')
        if state in ('ready_for_review', 'needs_information') and not db.execute(
            'SELECT 1 FROM reports WHERE attempt_id=?', (attempt_id,)).fetchone():
            raise ValueError('Report required')
        if state in ('failed', 'cancelled', 'reviewed'):
            db.execute('UPDATE worker_lease SET attempt_id=NULL,owner=NULL,expires=NULL WHERE attempt_id=?', (attempt_id,))
        db.execute('UPDATE attempts SET state=?,revision=revision+1 WHERE attempt_id=? AND revision=?',
                   (state, attempt_id, expected_revision))

    def claim(self, attempt_id, owner):
        with self.transaction() as db:
            lease = db.execute('SELECT attempt_id FROM worker_lease WHERE singleton=1').fetchone()
            row = db.execute('SELECT state,revision FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            if lease[0] is not None or row is None or row[0] != 'created':
                raise ValueError('worker_claim_conflict')
            self._transition(db, attempt_id, row[1], 'gathering_evidence')
            db.execute('UPDATE worker_lease SET attempt_id=?,owner=?,expires=? WHERE singleton=1',
                       (attempt_id, owner, time.time() + 120))

    def reserve_dispatch(self, attempt_id, owner):
        with self.transaction() as db:
            lease = db.execute('SELECT attempt_id,owner,expires FROM worker_lease WHERE singleton=1').fetchone()
            row = db.execute('SELECT provider_requests,state FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            if lease[:2] != (attempt_id, owner) or lease[2] < time.time() or row is None or row[1] not in ('gathering_evidence', 'drafting') or row[0] >= 8:
                raise ValueError('budget_exhausted_or_claim_invalid')
            sequence = row[0] + 1
            db.execute('INSERT INTO provider_dispatches VALUES (?,?,?,?)',
                       (attempt_id, sequence, 'pending', time.time()))
            db.execute('UPDATE attempts SET provider_requests=? WHERE attempt_id=?', (sequence, attempt_id))
        return sequence

    def save_evidence(self, attempt_id, evidence):
        evidence = validate('Evidence', evidence)
        row = self.get(attempt_id)
        if evidence['attempt_id'] != attempt_id or evidence['context_revision'] != row['context_revision']:
            raise ValueError('Evidence scope mismatch')
        with self.transaction() as db:
            try:
                db.execute('INSERT INTO evidence_items VALUES (?,?,?)',
                           (evidence['evidence_id'], attempt_id, canonical(evidence).decode()))
            except sqlite3.IntegrityError:
                raise ValueError('Immutable evidence conflict') from None

    def save_report(self, attempt_id, draft):
        draft = validate('ReportDraft', draft)
        row = self.get(attempt_id)
        content = {'attempt_id': attempt_id, 'context_revision': row['context_revision'], 'draft': draft}
        report_id = digest(content)
        with self.transaction() as db:
            db.execute('INSERT INTO reports VALUES (?,?,?)', (report_id, attempt_id, canonical(content).decode()))
        return report_id

    def review(self, attempt_id, revision, actor, disposition, rationale, report_id):
        if not isinstance(actor, str) or not 1 <= len(actor.strip()) <= 80 or not isinstance(rationale, str) or not 1 <= len(rationale.strip()) <= 2000:
            raise ValueError('Invalid review text')
        if disposition not in ('close', 'escalate', 'request_more_information'):
            raise ValueError('Invalid disposition')
        with self.transaction() as db:
            row = db.execute('SELECT state FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            report = db.execute('SELECT content FROM reports WHERE report_id=? AND attempt_id=?', (report_id, attempt_id)).fetchone()
            if row is None or report is None or row[0] not in ('ready_for_review', 'needs_information'):
                raise ValueError('Invalid report review')
            if row[0] == 'needs_information' and disposition != 'request_more_information':
                raise ValueError('Invalid needs-information disposition')
            self._transition(db, attempt_id, revision, 'reviewed')
            review_id = 'rev_' + uuid4().hex
            content = canonical(dict(actor=actor, rationale=rationale.strip(), disposition=disposition,
                                     report_id=report_id, timestamp=time.time())).decode()
            db.execute('INSERT INTO reviews VALUES (?,?,?,?)', (review_id, attempt_id, report_id, content))
            db.execute('INSERT INTO audit_events(attempt_id,content) VALUES (?,?)', (attempt_id, content))

    def reserve_tool(self, attempt_id, owner, name, arguments, call_id=None):
        definitions = {'get_case_facts': 'CaseFactsArguments',
                       'get_account_history': 'HistoryArguments',
                       'search_procedures': 'SearchArguments'}
        if name not in definitions:
            raise ValueError('Unauthorized tool')
        arguments = validate(definitions[name], arguments)
        with self.transaction() as db:
            lease = db.execute('SELECT attempt_id,owner,expires FROM worker_lease WHERE singleton=1').fetchone()
            row = db.execute('SELECT state FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            if lease[:2] != (attempt_id, owner) or lease[2] < time.time() or row is None or row[0] != 'gathering_evidence':
                raise ValueError('Invalid worker scope')
            if call_id is not None and db.execute(
                "SELECT 1 FROM tool_steps WHERE attempt_id=? AND json_extract(content,'$.call_id')=?",
                (attempt_id, call_id),
            ).fetchone():
                raise ValueError('duplicate_tool_call')
            sequence = db.execute('SELECT count(*) FROM tool_steps WHERE attempt_id=?', (attempt_id,)).fetchone()[0] + 1
            if sequence > 12:
                raise ValueError('tool_budget_exhausted')
            db.execute('INSERT INTO tool_steps VALUES (?,?,?)',
                       (attempt_id, sequence, canonical({'name': name, 'arguments': arguments,
                                                        'status': 'reserved',
                                                        'call_id': call_id}).decode()))
        return sequence

    def reject_tool(self, attempt_id, name, code):
        """Audit rejections without retaining possibly secret arguments."""
        self.get(attempt_id)
        safe_name = name if name in {
            'get_case_facts', 'get_account_history', 'search_procedures'} else 'unknown'
        with self.transaction() as db:
            db.execute('INSERT INTO audit_events(attempt_id,content) VALUES (?,?)',
                       (attempt_id, canonical(dict(operation='tool', name=safe_name,
                                                   status='rejected', code=code)).decode()))

    def finish_tool(self, attempt_id, owner, sequence, evidence, status, elapsed_ms, code=None):
        """Commit evidence and outcome together, refusing expired/late workers."""
        items = [validate('Evidence', item) for item in evidence]
        with self.transaction() as db:
            lease = db.execute('SELECT attempt_id,owner,expires FROM worker_lease WHERE singleton=1').fetchone()
            attempt = db.execute('SELECT context_revision,state FROM attempts WHERE attempt_id=?',
                                 (attempt_id,)).fetchone()
            step = db.execute('SELECT content FROM tool_steps WHERE attempt_id=? AND sequence=?',
                              (attempt_id, sequence)).fetchone()
            if (lease[:2] != (attempt_id, owner) or lease[2] < time.time()
                    or attempt is None or attempt[1] != 'gathering_evidence' or step is None):
                raise ValueError('Invalid worker scope')
            record = json.loads(step[0])
            if record['status'] != 'reserved' or status not in ('completed', 'failed'):
                raise ValueError('Invalid tool outcome')
            for item in items:
                if item['attempt_id'] != attempt_id or item['context_revision'] != attempt[0]:
                    raise ValueError('Evidence scope mismatch')
                db.execute('INSERT INTO evidence_items VALUES (?,?,?)',
                           (item['evidence_id'], attempt_id, canonical(item).decode()))
            record.update(status=status, elapsed_ms=elapsed_ms, code=code,
                          evidence_refs=[item['evidence_id'] for item in items])
            db.execute('UPDATE tool_steps SET content=? WHERE attempt_id=? AND sequence=?',
                       (canonical(record).decode(), attempt_id, sequence))
