"""Read-only local T098 inventory; never creates producer stores or dispatches work.

Run from root with PYTHONPATH=backend/src, passing a NEW ignored output path.
Only safe configuration fields and database metadata are recorded. Cached test
stores are inventoried, not promoted to actual published producer evidence.
"""

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

from fraudlens.investigation.dataset import DatasetReader
from fraudlens.investigation.environment import read_environment
from fraudlens.investigation.settings import InvestigationSettings

ROOT = Path(__file__).resolve().parents[2]
SAFE_FIELDS = (
    'enabled', 'provider', 'source', 'semantic_retrieval', 'store',
    'dataset_store', 'dataset_run_store', 'dataset_score_source',
)


def sha256(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def file_info(path):
    path = Path(path).resolve()
    return dict(path=str(path), exists=path.is_file(),
                bytes=path.stat().st_size if path.is_file() else None)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def main():
    output = Path(sys.argv[1]).resolve()
    if output.exists():
        raise FileExistsError('Use a new output path; preserve earlier results')
    environment = read_environment()
    defaults = InvestigationSettings()
    config = {}
    paths = {}
    for field in SAFE_FIELDS:
        name = 'INVESTIGATION_' + field.upper()
        value = environment.get(name, str(getattr(defaults, field)))
        config[name] = dict(value=value, explicit=name in environment)
        if field in ('store', 'dataset_store', 'dataset_run_store'):
            path = Path(value)
            paths[field] = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    config['APP_MODE'] = dict(value=environment.get('APP_MODE', 'fixture'),
                              explicit='APP_MODE' in environment)

    databases = []
    errors = []
    def scan_error(error):
        errors.append(dict(exception=type(error).__name__,
                           path=Path(error.filename).relative_to(ROOT).as_posix()))

    for current, directories, files in os.walk(ROOT, onerror=scan_error):
        directories[:] = [d for d in directories if d not in {
            '.git', '.venv', 'node_modules', '.vscode', '__pycache__',
        }]
        for name in files:
            if Path(name).suffix.lower() in ('.sqlite', '.sqlite3', '.db'):
                databases.append(Path(current) / name)
    relative = [p.relative_to(ROOT).as_posix() for p in databases]
    inventory = Counter('/'.join(p.split('/')[:2]) for p in relative)

    # This archive is explicitly authored in the existing smoke builder, not IBM
    # inference. Hash comparison identifies it without reading any data/labels.
    old = json.loads((ROOT / 'evidence/tasks/feature-003-dataset-producer-smoke-20261116.json').read_text(encoding='utf-8'))
    controlled = []
    for directory in sorted((ROOT / '.cache').glob('dataset-producer-smoke-*')):
        for name, expected in old['immutable_source_hashes'].items():
            path = directory / name
            if path.is_file():
                digest = sha256(path)
                controlled.append(dict(**file_info(path), sha256=digest,
                                       matches_recorded_authored_smoke=digest == expected))

    database_kinds = []
    for path in databases:
        if path.relative_to(ROOT).parts[0] == '.cache':
            continue
        with sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=1) as db:
            db.execute('PRAGMA query_only=ON')
            tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        database_kinds.append(dict(path=path.relative_to(ROOT).as_posix(), tables=tables,
                                   is_producer_dataset='operational_events' in tables and 'dataset_versions' in tables,
                                   is_producer_runs='scored_runs' in tables and 'scored_assessments' in tables))

    missing_probe = None
    if not paths['dataset_run_store'].exists():
        example = json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/context-dataset.json').read_text(encoding='utf-8'))
        reader = DatasetReader(paths['dataset_run_store'], paths['dataset_store'], 'rules')
        try:
            reader.resolve(example['case_id'], example['snapshot_ref'])
        except sqlite3.OperationalError as error:
            missing_probe = dict(outcome='unavailable', exception=type(error).__name__,
                                 source_file_created=paths['dataset_run_store'].exists(),
                                 fixture_fallback=False,
                                 scope='Missing-file negative probe with authored request IDs; NOT actual run validation')
        else:
            raise AssertionError('Missing producer store unexpectedly resolved')

    local_http = []
    opener = build_opener(ProxyHandler({}))
    for route in ('/api/health', '/api/cases'):
        try:
            with opener.open(Request('http://127.0.0.1:8000' + route), timeout=2) as response:
                data = json.loads(response.read(65536))
                local_http.append(dict(route=route, status=response.status,
                                       mode=data.get('mode'), contract_version=data.get('contract_version'),
                                       case_count=len(data['items']) if 'items' in data else None,
                                       has_dataset_identity='dataset_version' in data))
        except (URLError, OSError, ValueError) as error:
            local_http.append(dict(route=route, outcome='unavailable', exception=type(error).__name__))

    result = dict(
        observed_at_utc=datetime.now(timezone.utc).isoformat(),
        branch=git('branch', '--show-current'), head=git('rev-parse', 'HEAD'),
        worktrees=git('worktree', 'list', '--porcelain').splitlines(),
        configuration=config, configured_files={k: file_info(v) for k, v in paths.items()},
        database_inventory=dict(total=len(databases), groups=dict(sorted(inventory.items())),
                                outside_cache=[file_info(p) for p in databases if p.relative_to(ROOT).parts[0] != '.cache'],
                                scan_errors=errors),
        outside_cache_database_kinds=database_kinds,
        controlled_cache_hash_checks=controlled,
        raw_csv_metadata=file_info(ROOT / 'data/raw/HI-Small_Trans.csv'),
        artifact_files=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT / 'data/artifacts').rglob('*')) if p.is_file()],
        missing_store_adapter_probe=missing_probe, loopback_get_observations=local_http,
        task_status='T098 remains OPEN; actual producer identities/assembly not validated',
        actual_producer_api_worker_execution=False, provider_calls=0, label_reads=0,
        scope='Known workspace and configured paths only; no claim about unpublished stores elsewhere',
    )
    with output.open('x', encoding='utf-8') as target:
        json.dump(result, target, indent=2)
        target.write('\n')
    print(json.dumps(dict(output=str(output), task_status=result['task_status'],
                          configured_files=result['configured_files'],
                          database_count=len(databases), scan_error_count=len(errors),
                          outside_cache_database_kinds=database_kinds,
                          controlled_cache_hash_checks=controlled,
                          missing_store_adapter_probe=missing_probe,
                          loopback_get_observations=local_http), indent=2))


if __name__ == '__main__':
    main()
