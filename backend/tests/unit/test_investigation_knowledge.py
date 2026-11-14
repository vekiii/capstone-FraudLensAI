import hashlib
import json
from pathlib import Path

import pytest

from fraudlens.investigation.knowledge import KnowledgeStore, stage
from fraudlens.investigation.models import ROOT


def update_manifest(path, mutate):
    value = json.loads(path.read_text())
    mutate(value)
    path.write_text(json.dumps(value))


def test_publish_and_archive_exact_sections(knowledge_factory, tmp_path):
    manifest = knowledge_factory('Evidence text with trailing spaces  ')
    store = KnowledgeStore(tmp_path / 'inv.sqlite')
    first = store.publish(manifest)
    passages = store.passages(first)
    assert len(passages) == 12
    assert passages[0]['text'].endswith('  \n') or passages[0]['section'] == 'Limits'
    assert all(len(p['text']) <= 2400 for p in passages)
    assert all(not ('Evidence text' in p['text'] and 'Test only' in p['text']) for p in passages)
    assert store.publish(manifest) == first
    changed = knowledge_factory('Different evidence')
    second = store.publish(changed)
    assert second != first
    assert store.passages(first) == passages


def test_normalization_without_trim_and_reject_bom_cr(knowledge_factory):
    manifest = knowledge_factory('money  ')
    source = manifest.parent / 'documents/doc0.md'
    baseline = stage(manifest)
    source.write_bytes(source.read_bytes().replace(b'\n', b'\r\n'))
    assert stage(manifest) == baseline
    for bad in [b'\xef\xbb\xbfhello', b'hello\rworld']:
        source.write_bytes(bad)
        with pytest.raises(ValueError):
            stage(manifest)


@pytest.mark.parametrize('kind', ['hash', 'date', 'reviewer', 'reviewdate', 'unknown', 'path'])
def test_invalid_manifest(knowledge_factory, kind):
    manifest = knowledge_factory()
    def mutate(value):
        doc = value['documents'][0]
        if kind == 'hash':
            doc['metadata']['content_sha256'] = '0' * 64
        if kind == 'date':
            doc['metadata']['published_at'] = '2026-02-30'
        if kind == 'reviewer':
            doc['metadata']['reviewed_by'] = None
        if kind == 'reviewdate':
            doc['metadata']['reviewed_at'] = None
        if kind == 'unknown':
            doc['unexpected'] = True
        if kind == 'path':
            doc['path'] = '../manifest.json'
    update_manifest(manifest, mutate)
    with pytest.raises(ValueError):
        stage(manifest)


def test_unreviewed_not_published(knowledge_factory, tmp_path):
    manifest = knowledge_factory(reviewed=False)
    with pytest.raises(ValueError):
        KnowledgeStore(tmp_path / 'inv.sqlite').publish(manifest)


@pytest.mark.parametrize('kind', ['root', 'boolean_version', 'corpus_id', 'entry'])
def test_manifest_structure_is_validated_before_reading_documents(knowledge_factory, kind):
    manifest = knowledge_factory()
    value = json.loads(manifest.read_text())
    if kind == 'root':
        value = None
    elif kind == 'boolean_version':
        value['manifest_version'] = True
    elif kind == 'corpus_id':
        value['corpus_id'] = '../private'
    else:
        value['documents'][0] = None
    manifest.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        stage(manifest)


def test_stable_subpassages_and_ceiling(knowledge_factory):
    manifest = knowledge_factory('x' * 5000)
    data = stage(manifest)
    assert len(data['passages']) == 24
    assert all(len(p['text']) <= 2400 for p in data['passages'])
    assert stage(manifest) == data
    source = manifest.parent / 'documents/doc0.md'
    source.write_text('# Test\n## Evidence\n' + 'x' * 480001 + '\n## Limits\nEnd\n')
    update_manifest(manifest, lambda v: v['documents'][0]['metadata'].update(
        content_sha256=hashlib.sha256(source.read_bytes().replace(b'\r\n', b'\n')).hexdigest()))
    with pytest.raises(ValueError):
        stage(manifest)


def test_resolved_root_and_reference_boundary(knowledge_factory, tmp_path):
    manifest = knowledge_factory()
    for forbidden in ('evals/investigation/inputs', 'evals/investigation/reference', 'prompts/development'):
        with pytest.raises(ValueError):
            stage(ROOT / forbidden / 'manifest.json')
    outside = tmp_path / 'reference'
    outside.mkdir()
    target = outside / 'secret.md'
    target.write_text('PRIVATE answer')
    link = manifest.parent / 'documents/link.md'
    try:
        link.symlink_to(target)
    except OSError:
        # Directory-resolution guard and ../ traversal have separate tests.
        return
    update_manifest(manifest, lambda v: v['documents'][0].update(path='link.md'))
    with pytest.raises(ValueError):
        stage(manifest)


def test_document_root_cannot_escape_manifest_through_resolution(knowledge_factory, tmp_path, monkeypatch):
    manifest = knowledge_factory()
    root = manifest.parent / 'documents'
    outside = tmp_path / 'outside'
    __import__('shutil').copytree(root, outside)
    original = Path.resolve
    def resolved(self, *args, **kwargs):
        if self == root:
            return outside
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, 'resolve', resolved)
    with pytest.raises(ValueError):
        stage(manifest)


def test_prepare_knowledge_rejects_review_before_creating_store(knowledge_factory, tmp_path):
    from fraudlens.investigation.cli import main
    manifest = knowledge_factory(reviewed=False)
    target = tmp_path / 'not-created.sqlite'
    assert main(['prepare-knowledge', '--manifest', str(manifest), '--store', str(target)]) == 2
    assert not target.exists()
