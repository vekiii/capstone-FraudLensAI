"""Prepare only an isolated test corpus; not the staged six-source corpus."""
import importlib.util
import json
import sys
from pathlib import Path

from fraudlens.investigation.knowledge import KnowledgeStore

root = Path.cwd()
work = Path(sys.argv[1]).resolve()
assert work.is_relative_to(root / '.cache')
work.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('test_helpers', root / 'backend/tests/conftest.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
factory = module.knowledge_factory.__wrapped__(work)
manifest = factory('money transfer evidence OLD')
store_path = work / 'smoke.sqlite'
store = KnowledgeStore(store_path)
old = store.publish(manifest)
config = json.loads((root / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text())
retrieval = store.save_configuration(config)
factory('money transfer evidence NEW')
(work / 'setup.json').write_text(json.dumps(dict(store=str(store_path), old=old,
    retrieval=retrieval, manifest=str(manifest))))
print('Prepared synthetic test-only archive')
