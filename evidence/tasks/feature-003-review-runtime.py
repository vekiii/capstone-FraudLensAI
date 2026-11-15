"""Isolated review verification operator. All decisions are automated test actions."""
import json
import os
import sys
from pathlib import Path
from uuid import uuid4

from fraudlens.investigation import environment

work = Path(sys.argv[1]).resolve()
assert work.is_relative_to(Path.cwd() / '.cache')
environment.ENV_FILE = work / 'absent.env'
assert not environment.ENV_FILE.exists()
os.environ.update(INVESTIGATION_ENABLED='true', INVESTIGATION_PROVIDER='test',
                  INVESTIGATION_SOURCE='fixture', INVESTIGATION_TEST_SCENARIO='grounded',
                  INVESTIGATION_ANALYST='AUTOMATED TEST OPERATOR (not human approval)',
                  INVESTIGATION_STORE=str(work / 'smoke.sqlite'), APP_MODE='fixture')
os.environ.pop('OPENAI_API_KEY', None)
os.environ.pop('OPENAI_MODEL', None)

from fraudlens.investigation.knowledge import KnowledgeStore  # noqa: E402
from fraudlens.investigation.settings import load_settings  # noqa: E402
from fraudlens.investigation.workflow import InvestigationService  # noqa: E402

role = sys.argv[2]
if role == 'api':
    import uvicorn
    uvicorn.run('fraudlens.main:app', host='127.0.0.1', port=8000, log_level='warning')
elif role == 'worker':
    from fraudlens.investigation.cli import main
    raise SystemExit(main(['worker', '--store', str(work / 'smoke.sqlite'), '--once']))
else:
    settings = load_settings()
    knowledge = KnowledgeStore(settings.store, initialize=False)
    if role == 'needs':
        settings = settings.model_copy(update={'test_scenario': 'needs_information'})
        service = InvestigationService(knowledge.repository, knowledge, settings)
        context = service.context_reader.resolve('CASE-001', 'fixture', None)
        print(json.dumps(service.create({key: context[key] for key in ('case_id', 'source_mode', 'snapshot_ref')},
                                        settings.analyst, str(uuid4()))))
    elif role == 'audit':
        with knowledge.repository.connection() as db:
            result = {table: [json.loads(row[0]) for row in db.execute(f'SELECT content FROM {table} ORDER BY rowid')]
                      for table in ['reports', 'reviews', 'audit_events']}
            result['request_keys'] = [dict(actor=row[0], operation=row[1], request_key=row[2],
                response=json.loads(row[3])) for row in db.execute('SELECT actor,operation,request_key,response FROM request_keys ORDER BY rowid')]
        print(json.dumps(result))
    else:
        raise ValueError('Unknown isolated role')
