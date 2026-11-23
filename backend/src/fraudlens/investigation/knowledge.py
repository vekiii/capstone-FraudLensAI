"""Offline reviewed-source ingestion and immutable corpus archive."""
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from fraudlens.investigation.models import ROOT, canonical, digest, validate
from fraudlens.investigation.store import InvestigationRepository

CHUNKER = {'version': 1, 'normalization': 'CRLF-to-LF; no trim; reject BOM/bare CR',
           'maximum_characters': 2400, 'maximum_passages': 200, 'section_boundaries': True}


class KnowledgeUnavailable(ValueError):
    pass


def normalized(raw):
    if raw.startswith(b'\xef\xbb\xbf'):
        raise ValueError('BOM rejected')
    raw = raw.replace(b'\r\n', b'\n')
    if b'\r' in raw:
        raise ValueError('Bare CR rejected')
    return raw.decode('utf-8')


def _forbidden(path):
    return (path.is_relative_to(ROOT / 'evals')
            or path.is_relative_to(ROOT / 'prompts/development'))


def stage(manifest_path):
    """Validate all documents before constructing an immutable complete corpus."""
    path = Path(manifest_path).resolve()
    if _forbidden(path):
        raise ValueError('Forbidden knowledge input')
    value = json.loads(normalized(path.read_bytes()))
    if (not isinstance(value, dict)
            or set(value) != {'manifest_version', 'corpus_id', 'status', 'documents'}
            or type(value['manifest_version']) is not int or value['manifest_version'] != 1
            or not isinstance(value['corpus_id'], str)
            or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,119}', value['corpus_id'])):
        raise ValueError('Invalid manifest')
    if value['status'] != 'reviewed' or not isinstance(value['documents'], list) or len(value['documents']) < 6:
        raise ValueError('Complete reviewed corpus required')
    document_root = (path.parent / 'documents').resolve()
    if not document_root.is_relative_to(path.parent) or _forbidden(document_root):
        raise ValueError('Forbidden document root')
    documents, fragments = [], []
    seen = set()
    for entry in value['documents']:
        if not isinstance(entry, dict) or set(entry) != {'path', 'metadata'} or not isinstance(entry['path'], str):
            raise ValueError('Invalid source entry')
        relative = Path(entry['path'])
        source = (document_root / relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not source.is_relative_to(document_root) or _forbidden(source):
            raise ValueError('Source outside document root')
        meta = validate('Document', entry['metadata'])
        if not meta['reviewed_by'].strip() or meta['doc_id'] in seen:
            raise ValueError('Missing reviewer or duplicate document')
        seen.add(meta['doc_id'])
        if meta['published_at'] is None and not meta['unknown_date_reason']:
            raise ValueError('Unknown date requires reason')
        if datetime.fromisoformat(meta['reviewed_at'].replace('Z', '+00:00')) < datetime.fromisoformat(meta['retrieved_at'].replace('Z', '+00:00')):
            raise ValueError('Review predates source retrieval')
        text = normalized(source.read_bytes())
        if hashlib.sha256(text.encode('utf-8')).hexdigest() != meta['content_sha256']:
            raise ValueError('Reviewed source hash changed')
        sections = {}
        section = None
        for line in text.splitlines(keepends=True):
            if line.startswith('## '):
                section = line[3:].strip()
                if section in sections:
                    raise ValueError('Duplicate section')
                sections[section] = ''
            elif section is not None:
                sections[section] += line
        if not meta['included_sections'] or len(set(meta['included_sections'])) != len(meta['included_sections']):
            raise ValueError('Missing or duplicate selected sections')
        for section in meta['included_sections']:
            if section not in sections or not sections[section].strip():
                raise ValueError('Missing source section')
            body = sections[section]
            for ordinal, start in enumerate(range(0, len(body), 2400)):
                fragments.append(dict(document=meta, section=section, ordinal=ordinal,
                                      text=body[start:start + 2400]))
                if len(fragments) > 200:
                    raise ValueError('Corpus passage limit exceeded')
        documents.append(meta)
    documents.sort(key=lambda d: d['doc_id'])
    corpus = 'corpus_' + digest({'corpus_id': value['corpus_id'], 'documents': documents, 'chunker': CHUNKER})
    passages = []
    for fragment in fragments:
        content_sha = hashlib.sha256(fragment['text'].encode()).hexdigest()
        passage = dict(passage_id=digest({'corpus': corpus, **fragment}), corpus_version=corpus,
                       **fragment, content_sha256=content_sha)
        passages.append(validate('Passage', passage))
    passages.sort(key=lambda p: p['passage_id'])
    return dict(corpus_version=corpus, documents=documents, passages=passages, chunker=CHUNKER)


class KnowledgeStore:
    def __init__(self, path, initialize=True):
        if not initialize:
            self.repository = object.__new__(InvestigationRepository)
            self.repository.path = Path(path)
            return
        self.repository = InvestigationRepository(path)
        with self.repository.transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS corpus_versions(corpus_version TEXT PRIMARY KEY,content TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS documents(corpus_version TEXT REFERENCES corpus_versions,doc_id TEXT,content TEXT NOT NULL,PRIMARY KEY(corpus_version,doc_id))')
            db.execute('CREATE TABLE IF NOT EXISTS passages(passage_id TEXT PRIMARY KEY,corpus_version TEXT REFERENCES corpus_versions,content TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS retrieval_configs(retrieval_version TEXT PRIMARY KEY,content TEXT NOT NULL)')
            for table in ('corpus_versions', 'documents', 'passages', 'retrieval_configs'):
                for action in ('UPDATE', 'DELETE'):
                    db.execute(f'CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} BEFORE {action} ON {table} '
                               "BEGIN SELECT RAISE(ABORT, 'Immutable knowledge'); END")

    def publish(self, manifest_path):
        corpus = stage(manifest_path)
        version = corpus['corpus_version']
        with self.repository.transaction() as db:
            existing = db.execute('SELECT content FROM corpus_versions WHERE corpus_version=?', (version,)).fetchone()
            if existing:
                if existing[0] != canonical(corpus).decode():
                    raise ValueError('Corpus identity conflict')
                return version
            db.execute('INSERT INTO corpus_versions VALUES (?,?)', (version, canonical(corpus).decode()))
            for document in corpus['documents']:
                db.execute('INSERT INTO documents VALUES (?,?,?)',
                           (version, document['doc_id'], canonical(document).decode()))
            for passage in corpus['passages']:
                db.execute('INSERT INTO passages VALUES (?,?,?)',
                           (passage['passage_id'], version, canonical(passage).decode()))
        return version

    def corpus(self, version):
        if not isinstance(version, str) or not version.startswith('corpus_'):
            raise ValueError('Invalid corpus identity')
        validate('Digest', version[7:])
        with self.repository.connection() as db:
            row = db.execute('SELECT content FROM corpus_versions WHERE corpus_version=?', (version,)).fetchone()
        if row is None:
            raise KnowledgeUnavailable('knowledge_unavailable')
        return json.loads(row[0])

    def passages(self, version):
        return self.corpus(version)['passages']

    def passage(self, version, passage_id):
        validate('Digest', passage_id)
        for passage in self.passages(version):
            if passage['passage_id'] == passage_id:
                return passage
        raise KeyError('evidence_not_found')

    def save_configuration(self, configuration):
        version = digest(configuration)
        with self.repository.transaction() as db:
            old = db.execute('SELECT content FROM retrieval_configs WHERE retrieval_version=?', (version,)).fetchone()
            if old is None:
                db.execute('INSERT INTO retrieval_configs VALUES (?,?)', (version, canonical(configuration).decode()))
        return version

    def configuration(self, version):
        validate('Digest', version)
        with self.repository.connection() as db:
            row = db.execute('SELECT content FROM retrieval_configs WHERE retrieval_version=?', (version,)).fetchone()
        if row is None:
            raise KnowledgeUnavailable('Retrieval configuration unavailable')
        return json.loads(row[0])


    def latest(self, kind):
        if kind not in ('corpus', 'retrieval'):
            raise ValueError('Unknown knowledge identity')
        table, column = ('corpus_versions', 'corpus_version') if kind == 'corpus' else ('retrieval_configs', 'retrieval_version')
        with self.repository.connection() as db:
            row = db.execute(f'SELECT {column} FROM {table} ORDER BY rowid DESC LIMIT 1').fetchone()
        if row is None:
            raise KnowledgeUnavailable('Knowledge not prepared')
        return row[0]
