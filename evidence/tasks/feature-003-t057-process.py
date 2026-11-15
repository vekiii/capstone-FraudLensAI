"""Actual killed CLI processes, reopened store, child retries and two-connection races."""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from fraudlens.investigation import environment
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.store import InvestigationRepository
from fraudlens.investigation.workflow import InvestigationService

root = Path.cwd()
work = root / '.cache' / ('003-recovery-' + uuid4().hex)
work.mkdir(parents=True)
environment.ENV_FILE = work / 'absent.env'
env = {**os.environ, 'PYTHONPATH': str(root / 'backend/src')}
env.pop('OPENAI_API_KEY', None)
env.pop('OPENAI_MODEL', None)
helper = root / 'evidence/tasks/feature-003-recovery-runtime.py'
subprocess.run([sys.executable, str(root / 'evidence/tasks/feature-003-knowledge-smoke-prepare.py'), str(work)], env=env, check=True, capture_output=True)
store = KnowledgeStore(work / 'smoke.sqlite', initialize=False)
settings = InvestigationSettings(enabled=True, provider='test', store=store.repository.path)


def service():
    return InvestigationService(InvestigationRepository(store.repository.path), store, settings)


runtime = service()
context = runtime.context_reader.resolve('CASE-001', 'fixture', None)
body = {key: context[key] for key in ('case_id', 'source_mode', 'snapshot_ref')}
results = dict(mode='Actual local CLI fault processes; authored fixture/test provider; no LLM quality or billing evidence',
               work=str(work), checks=[])
for boundary in ('intent', 'result', 'evidence', 'drafting'):
    parent = runtime.create(body, settings.analyst, str(uuid4()))
    marker = work / 'fault-marker.json'
    marker.unlink(missing_ok=True)
    child_process = subprocess.Popen([sys.executable, str(helper), str(work), 'fault-worker', boundary],
                                    env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    try:
        for _ in range(160):
            if marker.exists():
                break
            if child_process.poll() is not None:
                raise RuntimeError(child_process.communicate()[1].decode())
            time.sleep(.05)
        assert marker.exists(), 'Fault marker missing'
        before = runtime.read(parent['attempt_id'])
        child_process.kill()
        child_process.communicate(timeout=5)
    finally:
        if child_process.poll() is None:
            child_process.kill()
            child_process.communicate(timeout=5)
    # Reopening and reading proves dead-owner recovery without a replay or waiting 120s.
    reopened = service()
    ended = reopened.read(parent['attempt_id'])
    assert ended['state'] == 'failed' and ended['failure']['code'] == 'interrupted'
    assert ended['failure']['outcome_unknown'] is (boundary in ('intent', 'evidence'))
    assert ended['budget']['provider_requests'] == before['budget']['provider_requests']
    assert reopened.read(parent['attempt_id']) == ended
    key = str(uuid4())
    def retry(_):
        return service().retry(ended['attempt_id'], ended['revision'], True, settings.analyst, key)
    with ThreadPoolExecutor(2) as pool:
        one, two = pool.map(retry, range(2))
    assert one == two and one['parent_attempt_id'] == ended['attempt_id']
    copied = reopened.evidence(one['attempt_id'])
    output = subprocess.run([sys.executable, str(helper), str(work), 'worker'], env=env, check=True, capture_output=True, text=True)
    assert json.loads(output.stdout)['state'] == 'ready_for_review'
    done = reopened.read(one['attempt_id'])
    assert done['budget']['provider_requests'] == 4
    assert all(item['attempt_id'] == done['attempt_id'] and item['context_revision'] == ended['context_revision'] for item in copied)
    if copied:
        assert set(done['trace'][0]['evidence_refs']).issubset(item['evidence_id'] for item in copied)
    with store.repository.connection() as db:
        outcomes = db.execute('SELECT sequence,outcome FROM provider_dispatches WHERE attempt_id=? ORDER BY sequence', (ended['attempt_id'],)).fetchall()
    results['checks'].append(dict(boundary=boundary, parent_attempt_id=ended['attempt_id'], child_attempt_id=one['attempt_id'],
        parent_state=ended['state'], outcome_unknown=ended['failure']['outcome_unknown'],
        parent_requests=ended['budget']['provider_requests'], child_requests=done['budget']['provider_requests'],
        parent_outcomes=outcomes, copied_evidence=len(copied), child_report_id=done['report']['report_id'], status='PASS'))

# Cancel from two connections while a real CLI awaits an authored response.
pending = runtime.create(body, settings.analyst, str(uuid4()))
marker = work / 'fault-marker.json'
marker.unlink(missing_ok=True)
late = subprocess.Popen([sys.executable, str(helper), str(work), 'late-worker', 'intent'],
                        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
try:
    for _ in range(160):
        if marker.exists():
            break
        time.sleep(.05)
    assert marker.exists()
    active = runtime.read(pending['attempt_id'])
    key = str(uuid4())
    def cancel(_):
        return service().cancel(active['attempt_id'], active['revision'], settings.analyst, key)
    with ThreadPoolExecutor(2) as pool:
        first, second = pool.map(cancel, range(2))
    assert first == second and first['state'] == 'cancelled'
    (work / 'release-response').write_text('release authored response')
    output, errors = late.communicate(timeout=10)
    assert late.returncode == 0, errors.decode()
    assert json.loads(output)['state'] == 'cancelled'
    ended = runtime.read(active['attempt_id'])
    assert ended == first and ended['failure']['outcome_unknown'] is True and ended['report'] is None
    with store.repository.connection() as db:
        assert db.execute('SELECT outcome FROM provider_dispatches WHERE attempt_id=?', (ended['attempt_id'],)).fetchall() == [('unknown',)]
    results['checks'].append(dict(name='actual late CLI response after two-connection idempotent cancel', attempt_id=ended['attempt_id'],
        requests=ended['budget']['provider_requests'], outcome_unknown=True, report=None, state=ended['state'], status='PASS'))
finally:
    if late.poll() is None:
        late.kill()
        late.communicate(timeout=5)

# Independent keys race on the same saved revision; one child only.
queued = runtime.create(body, settings.analyst, str(uuid4()))
ended = runtime.cancel(queued['attempt_id'], queued['revision'], settings.analyst, str(uuid4()))
def competing(_):
    try:
        return service().retry(ended['attempt_id'], ended['revision'], False, settings.analyst, str(uuid4()))['attempt_id']
    except ValueError as exc:
        return str(exc)
with ThreadPoolExecutor(2) as pool:
    raced = list(pool.map(competing, range(2)))
assert sum(value.startswith('att_') for value in raced) == 1 and 'revision_conflict' in raced
for value in raced:
    if value.startswith('att_'):
        view = runtime.read(value)
        runtime.cancel(value, view['revision'], settings.analyst, str(uuid4()))
results['checks'].append(dict(name='two-connection distinct-key CAS', results=raced, status='PASS'))
results['status'] = 'PASS'
(root / 'evidence/tasks/feature-003-t057-process-results.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
