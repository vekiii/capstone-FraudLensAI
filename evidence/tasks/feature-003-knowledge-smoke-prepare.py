"""Prepare an isolated archive; optionally start with the human-reviewed corpus."""
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
store_path = work / 'smoke.sqlite'
store = KnowledgeStore(store_path)
reviewed = len(sys.argv) == 3 and sys.argv[2] == '--reviewed'
manifest = (root / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json'
            if reviewed else factory('money transfer evidence OLD'))
old = store.publish(manifest)
config = json.loads((root / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text())
retrieval = store.save_configuration(config)
replacement = factory('money transfer evidence NEW')
(work / 'setup.json').write_text(json.dumps(dict(store=str(store_path), old=old,
    retrieval=retrieval, manifest=str(replacement), reviewed=reviewed,
    query='supporting documentation' if reviewed else 'money')))
print('Prepared isolated reviewed-source archive' if reviewed else 'Prepared synthetic test-only archive')
