"""Re-execute isolated browser verifiers with separate Phase 8 result files.

Generated verifier copies live only in .cache; old scripts/results stay intact.
No producer/model integration or real human review is simulated as acceptance.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / '.cache' / ('phase08-browser-' + uuid4().hex)
EVIDENCE = ROOT / 'evidence/tasks'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result-prefix', default='feature-003-phase08',
                        help='Distinct evidence filename prefix for a teammate reproduction')
    options = parser.parse_args()
    if re.fullmatch(r'feature-003-[a-z0-9-]{1,80}', options.result_prefix) is None:
        parser.error('Use a feature-003- lowercase alphanumeric/hyphen filename prefix')
    WORK.mkdir(parents=True)
    env = {**os.environ, 'PYTHONPATH': str(ROOT / 'backend/src'),
           'OPENAI_API_KEY': '', 'OPENAI_MODEL': ''}
    entries = [
        ('feature-003-knowledge-smoke.mjs', 'knowledge', ['--reviewed']),
        ('feature-003-t057-review-browser.mjs', 'review', []),
        ('feature-003-t057-recovery-browser.mjs', 'recovery', []),
        ('feature-003-t057-process.py', 'process', []),
    ]
    results = []
    for original, label, args in entries:
        source = (EVIDENCE / original).read_text(encoding='utf-8')
        output = f'{options.result_prefix}-{label}-results.json'
        if label == 'knowledge':
            source = source.replace('feature-003-reviewed-knowledge-smoke-results.json', output)
            source = source.replace('feature-003-knowledge-smoke-results.json', output)
            old = "['-m', 'uvicorn', 'fraudlens.main:app', '--app-dir', 'backend/src', '--host', '127.0.0.1', '--port', '8000']"
            assert old in source
            source = source.replace(old, "['evidence/tasks/feature-003-phase08-runtime.py', work]")
            cleanup = "  if (report.cleanup_error) { report.status = 'FAIL'; process.exitCode = 1; }"
            assert cleanup in source
            source = source.replace(cleanup, """
  try { await pause(500); for (const port of [8000, 5173, 9228]) await free(port); report.owned_process_cleanup = 'PASS'; }
  catch (error) { report.cleanup_error = String(error); }
""" + cleanup)
        else:
            old = f'feature-003-t057-{label}' + ('-browser' if label != 'process' else '') + '-results.json'
            assert old in source
            source = source.replace(old, output)
        if label == 'recovery':
            marker = "  assert.equal(report.errors.length, 0); note('No uncaught browser exceptions'); report.status = 'PASS';"
            assert marker in source
            source = source.replace(marker, """
  // Fresh isolated server: actual missing-key and missing-model API/proxy/browser checks.
  stop(backend); await pause(250); env.INVESTIGATION_ENABLED = 'true';
  env.INVESTIGATION_PROVIDER = 'openai'; env.OPENAI_MODEL = 'TEST-NOT-A-REAL-MODEL';
  const startConfigBackend = () => start(join(root, '.venv/Scripts/python.exe'), ['evidence/tasks/feature-003-phase08-runtime.py', work]);
  backend = startConfigBackend(); await ready('http://127.0.0.1:8000/api/health');
  for (const base of ['http://127.0.0.1:8000', 'http://127.0.0.1:5173']) {
    const list = await fetch(base + '/api/investigation/runs?case_id=CASE-001'); assert.equal(list.status, 200);
    const response = await fetch(base + '/api/investigation/runs', { method: 'POST', headers: {
      'content-type': 'application/json', 'idempotency-key': randomUUID(), origin: base
    }, body: JSON.stringify({ case_id: 'CASE-001', source_mode: 'fixture', snapshot_ref: list.headers.get('x-investigation-snapshot') }) });
    assert.equal(response.status, 503); assert.equal((await response.json()).error.code, 'provider_unavailable');
  }
  await tab.send('Page.navigate', { url: 'http://127.0.0.1:5173/' }); await wait("document.querySelectorAll('.case-choice').length===3");
  await openCase('CASE-001'); await click('[data-start]'); await wait("document.querySelectorAll('[role=alert]').length>0");
  assert.equal(await evaluate("document.querySelectorAll('[data-run-state=created]').length"), 0);
  note('Missing-key actual API/proxy 503 and browser controlled creation error; zero dispatch');
  stop(backend); await pause(250); env.OPENAI_MODEL = ''; backend = startConfigBackend(); await ready('http://127.0.0.1:8000/api/health');
  for (const base of ['http://127.0.0.1:8000', 'http://127.0.0.1:5173']) {
    assert.equal((await fetch(base + '/api/cases')).status, 200);
    const response = await fetch(base + '/api/investigation/runs?case_id=CASE-001');
    assert.equal(response.status, 503); assert.equal((await response.json()).error.code, 'context_unavailable');
  }
  await tab.send('Page.navigate', { url: 'http://127.0.0.1:5173/' }); await wait("document.querySelectorAll('.case-choice').length===3");
  await click('[aria-label="Otvori CASE-001"]'); await wait("!!document.querySelector('[data-investigation-open]')");
  await click('[data-investigation-open]'); await wait("document.querySelectorAll('[role=alert]').length>0");
  note('Missing-model actual API/proxy 503 and browser controlled unavailable; foundation still 200');
""" + marker)
        target = WORK / original
        target.write_text(source, encoding='utf-8')
        executable = sys.executable if target.suffix == '.py' else 'node'
        command = [executable, str(target), *args]
        run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        (WORK / (label + '.log')).write_bytes(run.stdout + run.stderr)
        result_path = EVIDENCE / output
        detail = json.loads(result_path.read_text(encoding='utf-8')) if result_path.exists() else {}
        entry = dict(source=original, source_sha256=hashlib.sha256((EVIDENCE / original).read_bytes()).hexdigest(),
                     generated_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                     command=command, exit_code=run.returncode, result=output,
                     status=detail.get('status', 'NO_RESULT'), checks=len(detail.get('checks', [])),
                     log=str(WORK / (label + '.log')))
        results.append(entry)
        print(json.dumps(entry), flush=True)
        if run.returncode or detail.get('status') != 'PASS':
            break
    passed = len(results) == len(entries) and all(r['exit_code'] == 0 and r['status'] == 'PASS' for r in results)
    (EVIDENCE / (options.result_prefix + '-browser-results.json')).write_text(json.dumps(dict(
        mode='Automated local browser/process regression, no human review or real provider calls',
        status='PASS' if passed else 'FAIL', real_provider_calls=0, results=results), indent=2) + '\n', encoding='utf-8')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
