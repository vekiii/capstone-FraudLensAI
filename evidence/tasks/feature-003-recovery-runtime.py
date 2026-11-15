"""Isolated TEST-only process harness; never reads the real .env or opens a network provider."""
import asyncio
import json
import os
import sys
from pathlib import Path

from fraudlens.investigation import environment

work = Path(sys.argv[1]).resolve()
assert work.is_relative_to(Path.cwd() / '.cache')
environment.ENV_FILE = work / 'absent.env'
assert not environment.ENV_FILE.exists()
os.environ.setdefault('INVESTIGATION_ENABLED', 'true')
os.environ.update(INVESTIGATION_PROVIDER='test',
                  INVESTIGATION_STORE=str(work / 'smoke.sqlite'), APP_MODE='fixture')
os.environ.pop('OPENAI_API_KEY', None)
os.environ.pop('OPENAI_MODEL', None)

from fraudlens.investigation.context import CaseContextReader  # noqa: E402
from fraudlens.investigation.provider import ScriptedProvider  # noqa: E402
from fraudlens.investigation.workflow import InvestigationService  # noqa: E402

role = sys.argv[2]
metadata = work / 'metadata.json'
original_reader = CaseContextReader.__init__


def isolated_reader(self, fixture_path=None, metadata_path=None):
    original_reader(self, fixture_path, metadata if metadata.exists() else metadata_path)


CaseContextReader.__init__ = isolated_reader
if role == 'api':
    import uvicorn
    uvicorn.run('fraudlens.main:app', host='127.0.0.1', port=8000, log_level='warning')
else:
    from fraudlens.investigation.cli import main
    if role in ('fault-worker', 'late-worker'):
        boundary = sys.argv[3]
        original_result = InvestigationService._dispatch_result
        original_complete = InvestigationService._complete

        def block():
            (work / 'fault-marker.json').write_text(json.dumps(dict(pid=os.getpid(), boundary=boundary)))
            # The parent kills this process after the durable marker.
            import time
            time.sleep(45)
            raise RuntimeError('Fault harness was not killed')

        class Paused(ScriptedProvider):
            async def next_turn(self, *args):
                if boundary == 'intent' or (boundary == 'evidence' and self.position == 1):
                    (work / 'fault-marker.json').write_text(json.dumps(dict(pid=os.getpid(), boundary=boundary)))
                    if role == 'late-worker':
                        for _ in range(200):
                            if (work / 'release-response').exists():
                                break
                            await asyncio.sleep(.05)
                        else:
                            raise RuntimeError('Late-response harness not released')
                    else:
                        await asyncio.sleep(45)
                        raise RuntimeError('Fault harness was not killed')
                return await super().next_turn(*args)

        def after_result(self, *args, **kwargs):
            original_result(self, *args, **kwargs)
            if boundary == 'result':
                block()

        def before_complete(self, *args, **kwargs):
            if boundary == 'drafting':
                block()
            return original_complete(self, *args, **kwargs)

        InvestigationService._provider = lambda self, binding: Paused()
        InvestigationService._dispatch_result = after_result
        InvestigationService._complete = before_complete
    elif role != 'worker':
        raise ValueError('Unknown isolated role')
    raise SystemExit(main(['worker', '--store', str(work / 'smoke.sqlite'), '--once']))
