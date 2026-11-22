"""Archive Capstone observations through the existing API and worker boundaries."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from fraudlens.investigation import cli, provider
from fraudlens.investigation.acceptance_harness import (
    DispatchLedger,
    metered_transport,
    require_authorization,
)
from fraudlens.investigation.history_index import file_digest
from fraudlens.investigation.knowledge import KnowledgeStore, normalized, stage
from fraudlens.investigation.models import digest
from fraudlens.investigation.settings import load_settings
from fraudlens.investigation.workflow import InvestigationService

PACK = Path(__file__).resolve().parent
ROOT = PACK.parents[1]
RESULTS = PACK.parent / 'results/capstone'
PUBLIC = PACK / 'inputs/cases.json'
MANIFEST = PACK / 'manifest.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def variant(knowledge, case, review):
    """Recreate the reviewed synthetic source in a dedicated ignored workspace."""
    from hashlib import sha256

    original = ROOT / knowledge['manifest']
    destination = ROOT / review['manifest']
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(original.parent / 'documents', destination.parent / 'documents', dirs_exist_ok=True)
    document = destination.parent / 'documents' / case['document']
    text = normalized(document.read_bytes())
    section = '## ' + case['section'] + '\n'
    before, found, body = text.partition(section)
    if not found or '\n## ' in body or not body.endswith('\n'):
        raise ValueError('Unexpected source layout')
    updated = before + found + body + case['append_text'] + '\n'
    content_sha256 = sha256(updated.encode()).hexdigest()
    if content_sha256 != review['content_sha256']:
        raise ValueError('Synthetic source differs from the reviewed text')
    document.write_bytes(updated.encode())
    manifest = read(original)
    manifest.update(corpus_id=case['corpus_id'], status='reviewed')
    metadata = next(item['metadata'] for item in manifest['documents'] if item['path'] == case['document'])
    metadata.update(
        version=case['document_version'], content_sha256=content_sha256,
        reviewed_by=review['reviewed_by'], reviewed_at=review['reviewed_at'],
    )
    write(destination, manifest)
    return stage(destination)


def case_settings(manifest, row, directory):
    settings = manifest['live_environment'].copy()
    seed = row['seed']
    dataset = manifest['dataset']
    settings.update(
        APP_RUN_STORE=str(ROOT / dataset['run_store']),
        INVESTIGATION_STORE=str(directory / 'investigation.sqlite'),
        INVESTIGATION_DATASET_RUN_STORE=str(ROOT / dataset['run_store']),
        INVESTIGATION_DATASET_STORE=str(ROOT / dataset['source_store']),
        INVESTIGATION_DATASET_HISTORY_INDEX=str(ROOT / dataset['history_index']),
        INVESTIGATION_DATASET_HISTORY_INDEX_SHA256=manifest['artifacts'][dataset['history_index']],
    )
    if seed['history'] == 'unavailable':
        missing = directory / seed['absent_history_name']
        if missing.exists():
            raise ValueError('Isolated history source must be absent')
        settings['INVESTIGATION_DATASET_STORE'] = str(missing)
        # Settings merge root .env, so a blank path would be invalid. Verify
        # independently below that neither history index setting was inherited.
        del settings['INVESTIGATION_DATASET_HISTORY_INDEX']
        del settings['INVESTIGATION_DATASET_HISTORY_INDEX_SHA256']
    with patch.dict(os.environ, settings):
        if seed['history'] == 'unavailable':
            os.environ.pop('INVESTIGATION_DATASET_HISTORY_INDEX', None)
            os.environ.pop('INVESTIGATION_DATASET_HISTORY_INDEX_SHA256', None)
        loaded = load_settings()
        if seed['history'] == 'unavailable' and loaded.dataset_history_index is not None:
            raise ValueError('Unexpected history index configured in .env')
        if not loaded.api_key.get_secret_value():
            raise ValueError('Approved live provider key is unavailable')
    return settings


def prepare_store(path, manifest, row):
    seed = row['seed']
    store = KnowledgeStore(path)
    corpus = store.publish(ROOT / seed['knowledge_manifest'])
    if corpus != seed['corpus']:
        raise ValueError('Frozen source version changed')
    store.save_configuration(read(ROOT / manifest['knowledge']['retrieval']))
    return store


def local_binding(settings):
    return dict(
        configuration_sha256=digest(settings),
        requested_model=settings['OPENAI_MODEL'],
    )


@contextmanager
def use_metered_provider(ledger) -> Iterator[None]:
    original = provider.OpenAIProvider

    def create(*args, **kwargs):
        if 'transport' in kwargs:
            raise ValueError('Unexpected transport override')
        return original(*args, **kwargs, transport=metered_transport(ledger))

    with patch.object(provider, 'OpenAIProvider', create):
        yield


def ledger_for(directory):
    frozen = require_authorization(directory / 'approval.json', directory / 'freeze.json')
    if frozen['commit'] != git('rev-parse', 'HEAD'):
        raise ValueError('Execution revision differs from phase freeze')
    return DispatchLedger(directory / 'dispatches.sqlite', frozen['maximum_requests'], frozen['model'])


def dispatches(ledger, after=0):
    with ledger.connection() as db:
        rows = db.execute('SELECT * FROM dispatches WHERE sequence > ? ORDER BY sequence', (after,)).fetchall()
    return [dict(sequence=sequence, request=json.loads(request), bytes=len(request), sha256=sha,
                 response=json.loads(result) if result is not None else None)
            for sequence, request, sha, result in rows]


def envelope(response):
    return dict(status=response.status_code, body=response.json())


def search(client, queries, corpus):
    output = []
    for query in queries:
        headers = {'Idempotency-Key': str(uuid4())}
        sent = client.post('/api/knowledge/semantic-search', headers=headers,
                           json={'query': query, 'corpus': corpus})
        saved = client.get('/api/knowledge/semantic-search/status', headers=headers)
        hits = saved.json().get('result', {}).get('hits', [])
        sources = [envelope(client.get('/api/knowledge/passages/' + hit['passage']['passage_id'],
                                      params={'corpus': corpus})) for hit in hits]
        output.append(dict(query=query, key=headers['Idempotency-Key'], sent=envelope(sent),
                           saved=envelope(saved), sources=sources))
    return dict(queries=output)


def investigation(client, case_id, transaction_id, snapshot, directory):
    detail = client.get('/api/cases/' + case_id, params={'snapshot': snapshot}).raise_for_status().json()
    assert detail['transaction']['transaction_id'] == transaction_id
    context = client.get('/api/investigation/runs', params={'case_id': case_id}).raise_for_status()
    created = client.post('/api/investigation/runs', headers={'Idempotency-Key': str(uuid4())},
                          json=dict(case_id=case_id, source_mode='dataset', snapshot_ref=snapshot))
    output = dict(detail=detail, created=envelope(created), context_header=context.headers['x-investigation-context'])
    if created.status_code == 202:
        worker(directory)
        base = '/api/investigation/attempts/' + created.json()['attempt_id']
        attempt = client.get(base).raise_for_status().json()
        output['attempt'] = attempt
        if attempt['report']:
            output['citations'] = [envelope(client.get(base + '/evidence/' + key))
                                   for key in attempt['report']['draft']['citations']]
    return output


def worker(directory):
    settings = load_settings()
    original = provider.canonical
    with (settings.store.parent / 'payload-sizes.jsonl').open('a', encoding='utf-8') as sizes:
        def measure(value):
            body = original(value)
            if isinstance(value, dict) and {'model', 'input', 'instructions', 'tools', 'text'} <= value.keys():
                sizes.write(json.dumps(dict(bytes=len(body), input_items=len(value['input']))) + '\n')
                sizes.flush()
            return body

        with use_metered_provider(ledger_for(directory)), patch.object(provider, 'canonical', measure):
            return cli.main(['worker', '--store', str(settings.store), '--once'])


def store_trace(knowledge, attempt):
    service = InvestigationService(knowledge.repository, knowledge, load_settings())
    attempt_id = attempt['attempt_id']
    return dict(context=service.context(attempt_id), events=service.events(attempt_id))


def browser(directory, phase_directory, data, *, reopen=False):
    root = directory / ('browser-reopen' if reopen else 'browser-creation')
    root.mkdir()
    settings = dict(data, reopen=reopen, directory=str(root),
                    python=sys.executable, script=str(Path(__file__).resolve()),
                    phase_directory=str(phase_directory))
    inputs = root / 'parameters.json'
    write(inputs, settings)
    result = subprocess.run(['node', str(PACK / 'browser.ts'), str(inputs)], cwd=ROOT,
                            capture_output=True, text=True, encoding='utf-8', timeout=230)
    (root / 'runner.log').write_text(result.stdout + result.stderr, encoding='utf-8')
    output = read(root / 'result.json')
    output.update(exit_code=result.returncode, artifact=str(root.relative_to(ROOT)))
    return output


def observe(directory, ledger, public, row, manifest):
    case_id, model_input = public['id'], public['input']
    reopen = case_id == 'EV-06'
    state = directory / ('EV-01' if reopen else case_id)
    state.mkdir(exist_ok=reopen)
    env = case_settings(manifest, row, state)
    start = len(dispatches(ledger))
    output = dict(id=case_id, configuration=local_binding(manifest['live_environment']))
    seed = row['seed']
    with patch.dict(os.environ, env):
        if seed['history'] == 'unavailable':
            os.environ.pop('INVESTIGATION_DATASET_HISTORY_INDEX', None)
            os.environ.pop('INVESTIGATION_DATASET_HISTORY_INDEX_SHA256', None)
        settings = load_settings()
        if reopen:
            prior = read(directory / 'EV-01.json')
            old = prior.get('observation') or {}
            if not (old.get('review_reopened') and old.get('opened_citations') and old.get('attempt')):
                output['blocked'] = 'EV-01 iste faze nema potvrđen sačuvani nacrt, odluku i otvoren citat.'
                return output
            knowledge = KnowledgeStore(settings.store, initialize=False)
        else:
            knowledge = prepare_store(settings.store, manifest, row)
        output['corpus'] = knowledge.latest('corpus')
        output['retrieval'] = knowledge.latest('retrieval')
        data = None
        try:
            if case_id == 'EV-01' or reopen:
                browser_input = old['browser_input'] if reopen else model_input
                parameters = dict(browser_input, snapshot=manifest['dataset']['snapshot_ref'])
                if reopen:
                    parameters.update(restore=old['attempt'], citations=old['opened_citations'])
                data = browser(state, directory, parameters, reopen=reopen)
                data['browser_input'] = browser_input
            else:
                from fraudlens.main import app

                with TestClient(app) as client:
                    if 'queries' in model_input:
                        with use_metered_provider(ledger):
                            data = search(client, model_input['queries'], seed['corpus'])
                    else:
                        data = investigation(client, model_input['case_id'], model_input['transaction_id'],
                                             manifest['dataset']['snapshot_ref'], directory)
            if data.get('attempt'):
                data.update(store_trace(knowledge, data['attempt']))
            sizes = state / 'payload-sizes.jsonl'
            if sizes.exists() and not reopen:
                data['payload_sizes'] = [json.loads(line) for line in sizes.read_text().splitlines()]
        except Exception as exc:
            output['execution_error'] = type(exc).__name__
            (state / f'{case_id}-error.log').write_text(str(exc), encoding='utf-8')
        output['observation'] = data
        output['dispatches_before'] = start
        output['dispatches_after'] = len(dispatches(ledger))
        output['dispatches'] = dispatches(ledger, after=start)
    return output


def run(phase, revision, *, prepare_only):
    if revision != git('rev-parse', 'HEAD') or git('status', '--porcelain'):
        raise ValueError('Select the exact committed revision with a clean worktree')
    public = read(PUBLIC)
    manifest = read(MANIFEST)
    if file_digest(PUBLIC) != manifest['input_sha256']:
        raise ValueError('Frozen public file changed')
    for name, sha in manifest['artifacts'].items():
        if file_digest(ROOT / name) != sha:
            raise ValueError('Frozen artifact changed: ' + name)
    for case, pin in zip(public['cases'], manifest['cases'], strict=True):
        if (case['id'], digest(case), digest(pin['seed'])) != (
                pin['id'], pin['input_sha256'], pin['seed_sha256']):
            raise ValueError('Public scenario or seed changed')
    checked = variant(manifest['knowledge'], public['cases'][9]['input'], manifest['ev10_review'])
    if checked['corpus_version'] != manifest['ev10_review']['corpus']:
        raise ValueError('Reviewed variant identity changed')
    directory = RESULTS / phase
    model = manifest['live_environment']['OPENAI_MODEL']
    freeze = directory / 'freeze.json'
    frozen_paths = (MANIFEST, PUBLIC, PACK / 'protocol.md', PACK / 'browser.ts', Path(__file__))
    # The offline rubric is pinned separately in the public manifest. This
    # process verifies the executable package only and never opens that rubric.
    if prepare_only:
        directory.mkdir(parents=True)
        write(freeze, dict(stage=phase, commit=revision, batch_directory=str(directory), model=model,
                           maximum_requests=manifest['budget']['requests_per_phase'],
                           files_sha256={str(path): file_digest(path) for path in frozen_paths}))
        return
    ledger = ledger_for(directory)
    if dispatches(ledger) or any(directory.glob('EV-*')):
        raise ValueError('Phase already started; preserve observations before any recovery')
    rows = []
    for case, pin in zip(public['cases'][:10], manifest['cases'][:10], strict=True):
        state = observe(directory, ledger, case, pin, manifest)
        write(directory / (case['id'] + '.json'), state)
        rows.append(state)
        print(case['id'], state.get('blocked') or state.get('execution_error') or 'archived', flush=True)
    write(RESULTS / f'{phase}-live.json', dict(phase=phase, commit=revision, rows=rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('baseline', 'final', 'browser-api', 'worker'))
    parser.add_argument('revision_or_directory')
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    if args.phase == 'browser-api':
        import uvicorn

        with use_metered_provider(ledger_for(Path(args.revision_or_directory))):
            uvicorn.run('fraudlens.main:app', host='127.0.0.1', port=8000, access_log=False)
        return 0
    if args.phase == 'worker':
        return worker(Path(args.revision_or_directory))
    run(args.phase, args.revision_or_directory, prepare_only=args.prepare)
    return 0


if __name__ == '__main__':
    sys.exit(main())
