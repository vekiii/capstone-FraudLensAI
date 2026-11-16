"""Explicit isolated local HTTP/CLI journey; test provider only, never real .env."""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]


def main():
    work = ROOT / '.cache' / ('reliability-v2-smoke-' + uuid4().hex)
    work.mkdir(parents=True)
    store = work / 'investigations.sqlite'
    env = {**os.environ, 'PYTHONPATH': str(ROOT / 'backend/src'),
           'INVESTIGATION_ENABLED': 'true', 'INVESTIGATION_PROVIDER': 'test',
           'INVESTIGATION_TEST_SCENARIO': 'grounded', 'INVESTIGATION_SOURCE': 'fixture',
           'INVESTIGATION_STORE': str(store), 'INVESTIGATION_ANALYST': 'automated-local-smoke',
           'APP_MODE': 'fixture', 'OPENAI_API_KEY': '', 'OPENAI_MODEL': '',
           'PYTHONDONTWRITEBYTECODE': '1'}
    bootstrap = (
        'import runpy,sys; from pathlib import Path; '
        'from fraudlens.investigation import environment; '
        f'environment.ENV_FILE=Path({str(work / "absent.env")!r}); '
        'module=sys.argv.pop(1); runpy.run_module(module,run_name="__main__")'
    )
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

    def command(module, *args):
        return [sys.executable, '-c', bootstrap, module, *map(str, args)]

    def cli(*args):
        result = subprocess.run(command('fraudlens.investigation.cli', *args),
            cwd=ROOT, env=env, capture_output=True, timeout=15, creationflags=flags)
        if result.returncode:
            raise RuntimeError('Local CLI command failed')

    cli('prepare-knowledge', '--manifest',
        ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json',
        '--retrieval', ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json',
        '--store', store)
    with socket.socket() as available:
        available.bind(('127.0.0.1', 0))
        port = available.getsockname()[1]
    server = subprocess.Popen(command('uvicorn', 'fraudlens.main:app', '--host',
        '127.0.0.1', '--port', port, '--no-access-log'), cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
    opener = build_opener(ProxyHandler({}))

    def http(path, body=None):
        request = Request(f'http://127.0.0.1:{port}' + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={} if body is None else {'Content-Type': 'application/json',
                                             'Idempotency-Key': str(uuid4())})
        with opener.open(request, timeout=3) as response:
            return json.load(response), response.headers

    checks = {}
    started = time.monotonic()
    try:
        for _ in range(40):
            if server.poll() is not None:
                raise RuntimeError('Local backend exited')
            try:
                http('/api/health')
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError('Local backend startup timeout')
        cases, _ = http('/api/cases')
        checks['original_fixture_case_count'] = len(cases['items']) == 3
        latin, _ = http('/api/knowledge/search?' + urlencode({'q': 'nedostaje dokaz'}))
        cyrillic, _ = http('/api/knowledge/search?' + urlencode({'q': 'недостаје доказ'}))
        checks['script_equivalence'] = (latin['status'] == cyrillic['status'] == 'matched'
                                        and latin['hits'] == cyrillic['hits'])
        no_match, _ = http('/api/knowledge/search?q=nomatchxyz')
        checks['unknown_query_no_match'] = no_match['status'] == 'no_match'
        _, headers = http('/api/investigation/runs?case_id=CASE-001')
        created, _ = http('/api/investigation/runs', dict(case_id='CASE-001',
            source_mode='fixture', snapshot_ref=headers['X-Investigation-Snapshot']))
        checks['create_queued_without_dispatch'] = (created['state'] == 'created'
                                                   and created['budget']['provider_requests'] == 0)
        cli('worker', '--store', store, '--once')
        result, _ = http('/api/investigation/attempts/' + created['attempt_id'])
        checks['test_provider_report'] = (result['state'] == 'ready_for_review'
                                          and result['provider_mode'] == 'test'
                                          and result['report']['semantic_review'] == 'not_reviewed')
        checks['three_scoped_tools'] = [step['name'] for step in result['trace']] == [
            'get_case_facts', 'get_account_history', 'search_procedures']
        checks['bounded_request_count'] = result['budget']['provider_requests'] == 4
        checks['pinned_candidate_config'] = result['retrieval_version'] == latin['retrieval_version']
        summary = dict(kind='automated_local_test_provider_not_live_evaluation', checks=checks,
                       elapsed_seconds=round(time.monotonic() - started, 3), provider_api_calls=0)
        print(json.dumps(summary, indent=2))
        return 0 if all(checks.values()) else 1
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


if __name__ == '__main__':
    raise SystemExit(main())
