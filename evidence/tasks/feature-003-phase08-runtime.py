"""Isolated local regression server; no contributor .env or usable provider key."""
import os
import sys
from pathlib import Path

from fraudlens.investigation import environment

work = Path(sys.argv[1]).resolve()
assert work.is_relative_to(Path.cwd() / '.cache')
environment.ENV_FILE = work / 'absent.env'
assert not environment.ENV_FILE.exists()
os.environ['OPENAI_API_KEY'] = ''
os.environ.setdefault('OPENAI_MODEL', '')
os.environ.setdefault('INVESTIGATION_PROVIDER', 'test')
os.environ.setdefault('INVESTIGATION_ENABLED', 'true')
os.environ['INVESTIGATION_SOURCE'] = 'fixture'
os.environ['APP_MODE'] = 'fixture'

import uvicorn  # noqa: E402

uvicorn.run('fraudlens.main:app', host='127.0.0.1', port=8000, log_level='warning')
