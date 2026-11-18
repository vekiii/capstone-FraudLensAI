"""Durable explicit semantic-search jobs; read/status/replay never redispatch."""
import asyncio
import hashlib
import json
import time

from fraudlens.investigation.models import ROOT, digest, validate
from fraudlens.investigation.retrieval_semantic_v6 import (
    policy_identity,
    project_selection,
    request_payload,
)


def runtime_revision():
    files = ('retrieval_semantic_v6.py', 'semantic_runtime.py', 'semantic_api.py',
             'retrieval_semantic_adapter_v6.py', 'semantic_response_audit.py', 'settings.py', 'workflow.py', 'tools.py')
    return digest({name: hashlib.sha256((ROOT / 'backend/src/fraudlens/investigation' / name)
                  .read_bytes().replace(b'\r\n', b'\n')).hexdigest() for name in files})


class SemanticSearchService:
    def __init__(self, knowledge, settings, provider_factory=None, selector=None):
        self.knowledge, self.repo, self.settings = knowledge, knowledge.repository, settings
        self.selector = selector
        self.provider_factory = provider_factory or self._provider
        with self.repo.transaction() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS semantic_search_jobs(
                key TEXT PRIMARY KEY, request_digest TEXT NOT NULL, state TEXT NOT NULL,
                started REAL NOT NULL, content TEXT NOT NULL)''')
            db.execute('''CREATE TABLE IF NOT EXISTS semantic_search_dispatch_audit(
                job_key TEXT PRIMARY KEY, response_json TEXT NOT NULL)''')

    def _provider(self):
        from fraudlens.investigation.provider import OpenAIProvider
        return OpenAIProvider(self.settings.api_key.get_secret_value(), self.settings.model.get_secret_value())

    def _key(self, request_key):
        if not isinstance(request_key, str) or not 1 <= len(request_key) <= 200:
            raise ValueError('invalid_request')
        return digest([self.settings.analyst, request_key])

    def status(self, request_key):
        key = self._key(request_key)
        with self.repo.transaction() as db:
            row = db.execute('SELECT state,started,content FROM semantic_search_jobs WHERE key=?', (key,)).fetchone()
            if row is None:
                raise ValueError('search_not_found')
            result = json.loads(row[2])
            if row[0] == 'pending' and row[1] + min(30, self.settings.request_timeout_seconds) <= time.time():
                result.update(status='failed', error='timeout', outcome_unknown=True)
                db.execute('UPDATE semantic_search_jobs SET state=?,content=? WHERE key=?',
                           ('failed', json.dumps(result), key))
            return result

    def cancel(self, request_key):
        key = self._key(request_key)
        with self.repo.transaction() as db:
            row = db.execute('SELECT content FROM semantic_search_jobs WHERE key=?', (key,)).fetchone()
            if row is None:
                raise ValueError('search_not_found')
            result = json.loads(row[0])
            if result['status'] == 'pending':
                result.update(status='cancelled', outcome_unknown=True)
                db.execute('UPDATE semantic_search_jobs SET state=?,content=? WHERE key=? AND state=?',
                           ('cancelled', json.dumps(result), key, 'pending'))
            return result

    async def search(self, query, request_key, corpus=None):
        if not self.settings.enabled or not self.settings.semantic_retrieval or self.settings.provider != 'openai':
            raise ValueError('semantic_unavailable')
        query = validate('SearchArguments', dict(query=query))['query']
        corpus = corpus or self.knowledge.latest('corpus')
        if corpus != self.knowledge.latest('corpus'):
            raise ValueError('stale_snapshot')
        passages = self.knowledge.passages(corpus)
        model = self.settings.model.get_secret_value()
        profile_args = {'profile': self.settings.semantic_profile} if self.settings.semantic_profile != 'v6' else {}
        payload = request_payload(query, passages, model, **profile_args)
        if (len(json.dumps(payload, ensure_ascii=False).encode()) > self.settings.max_input_bytes
                or self.settings.max_output_tokens < 2048):
            raise ValueError('semantic_budget_exhausted')
        policy = policy_identity(model, passages, **profile_args)
        revision = runtime_revision()
        key, request_hash = self._key(request_key), digest([query, corpus, policy, revision])
        now = time.time()
        with self.repo.transaction() as db:
            old = db.execute('SELECT request_digest FROM semantic_search_jobs WHERE key=?', (key,)).fetchone()
            if old and old[0] != request_hash:
                raise ValueError('request_conflict')
            if not old:
                if db.execute('SELECT COUNT(*) FROM semantic_search_jobs').fetchone()[0] >= self.settings.max_semantic_requests:
                    raise ValueError('semantic_budget_exhausted')
                result = dict(contract_version=1, job_id='sem_' + key[:32], status='pending', provider_requests=1,
                              corpus_version=corpus, retrieval_version=policy, result=None,
                              runtime_revision=revision, error=None, outcome_unknown=False)
                db.execute('INSERT INTO semantic_search_jobs VALUES(?,?,?,?,?)',
                           (key, request_hash, 'pending', now, json.dumps(result)))
        if old:
            return self.status(request_key)
        provider = None
        try:
            provider = self.provider_factory()
            if hasattr(provider, 'transport'):
                provider.transport.limit = self.settings.max_response_bytes
                provider.transport.input_limit = self.settings.max_input_bytes
            async with asyncio.timeout(min(30, self.settings.request_timeout_seconds)):
                if self.selector is not None:
                    selection, audit = await self.selector(provider, query, passages)
                else:
                    from fraudlens.investigation.semantic_response_audit import audited_selection
                    def capture(raw):
                        with self.repo.transaction() as db:
                            db.execute('INSERT INTO semantic_search_dispatch_audit VALUES(?,?)',
                                       (key, json.dumps(raw)))
                    selection, audit = await audited_selection(provider, query, passages, capture, **profile_args)
            projected = project_selection(query, passages, selection, corpus, policy)
            # Revalidate the active source before publishing; saved reads stay pinned.
            if (self.knowledge.latest('corpus') != corpus
                    or policy_identity(model, self.knowledge.passages(corpus), **profile_args) != policy
                    or runtime_revision() != revision):
                raise ValueError('stale_snapshot')
            result.update(status='completed', result=projected, audit=audit)
        except asyncio.CancelledError:
            result.update(status='failed', error='interrupted', outcome_unknown=True)
            self._finish(key, result)
            raise
        except Exception as exc:
            result.update(status='failed', error='stale_snapshot' if str(exc) == 'stale_snapshot' else 'provider_failure',
                          outcome_unknown=True, diagnostic=dict(error_type=type(exc).__name__))
        finally:
            if provider is not None:
                try:
                    async with asyncio.timeout(1):
                        if hasattr(provider, 'aclose'):
                            await provider.aclose()
                        else:
                            await provider.client.close()
                except Exception:
                    pass
        self._finish(key, result)
        return self.status(request_key)

    def _finish(self, key, result):
        with self.repo.transaction() as db:
            db.execute('UPDATE semantic_search_jobs SET state=?,content=? '
                       'WHERE key=? AND state=? AND started>?',
                       (result['status'], json.dumps(result), key, 'pending',
                        time.time() - min(30, self.settings.request_timeout_seconds)))
