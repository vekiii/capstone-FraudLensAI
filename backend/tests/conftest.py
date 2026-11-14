"""Synthetic reviewed metadata is test-only, never real corpus approval."""
import hashlib
import json

import pytest


@pytest.fixture
def knowledge_factory(tmp_path):
    def factory(text='money transfer evidence', reviewed=True):
        root = tmp_path / 'authored-corpus'
        docs = root / 'documents'
        docs.mkdir(parents=True, exist_ok=True)
        entries = []
        for i in range(6):
            source = f'# Authored test\n## Evidence\n{text}\n## Limits\nTest only, not law.\n'
            path = docs / f'doc{i}.md'
            path.write_bytes(source.encode('utf-8'))
            meta = dict(doc_id=f'doc{i}', title='Authored test', origin_kind='simulated',
                        source_uri='local:test', published_at='2026-01-01', unknown_date_reason=None,
                        retrieved_at='2026-01-02T00:00:00Z', jurisdiction='SIMULATED test only',
                        version='test-v1', reviewed_by='SYNTHETIC TEST REVIEWER' if reviewed else None,
                        reviewed_at='2026-01-03T00:00:00Z' if reviewed else None,
                        reuse_terms='Authored test content only',
                        content_sha256=hashlib.sha256(source.encode()).hexdigest(),
                        included_sections=['Evidence', 'Limits'], applicability_notes='Test only')
            entries.append({'path':path.name,'metadata':meta})
        manifest = root / 'manifest.json'
        manifest.write_text(json.dumps(dict(manifest_version=1,corpus_id='test-corpus',
                                           status='reviewed' if reviewed else 'staged', documents=entries)))
        return manifest
    return factory
