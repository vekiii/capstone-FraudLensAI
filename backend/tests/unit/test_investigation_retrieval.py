import copy
import math
import os
import subprocess
import sys

import pytest

from fraudlens.investigation.knowledge import KnowledgeStore, KnowledgeUnavailable
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.retrieval import search

CONFIG = dict(configuration_version=1, algorithm='bm25', k1=1.2, b=0.75,
              adequacy_cutoff=0.0, maximum_results=5, normalization=['NFKC', 'casefold'])


def test_scores_are_identical_across_process_hash_seeds(knowledge_factory, tmp_path):
    store_path = tmp_path / 'deterministic.sqlite'
    store = KnowledgeStore(store_path)
    terms = ['term' + str(i) for i in range(20)]
    body = ' '.join(term for i, term in enumerate(terms) for _ in range(i + 1))
    corpus = store.publish(knowledge_factory(body))
    retrieval = store.save_configuration(CONFIG)
    script = (
        'import json,sys; from fraudlens.investigation.knowledge import KnowledgeStore; '
        'from fraudlens.investigation.retrieval import search; '
        'print(json.dumps(search(KnowledgeStore(sys.argv[1], initialize=False), '
        'sys.argv[4], sys.argv[2], sys.argv[3]), sort_keys=True))'
    )
    outputs = [subprocess.check_output(
        [sys.executable, '-c', script, str(store_path), corpus, retrieval, ' '.join(terms)],
        env={**os.environ, 'PYTHONHASHSEED': str(seed), 'PYTHONPATH': str(ROOT / 'backend/src')},
        text=True,
    ) for seed in range(1, 5)]
    assert len(set(outputs)) == 1


def test_formula_dedup_normalization_topfive_and_ties(knowledge_factory, tmp_path):
    store = KnowledgeStore(tmp_path / 'inv.sqlite')
    corpus = store.publish(knowledge_factory('MONEY transfer money'))
    version = store.save_configuration(CONFIG)
    result = search(store, '  ＭＯＮＥＹ MONEY  ', corpus, version)
    assert result['query'] == 'ＭＯＮＥＹ MONEY'
    assert len(result['hits']) == 5
    ids = [hit['passage']['passage_id'] for hit in result['hits']]
    assert ids == sorted(ids)
    passages = store.passages(corpus)
    # Six money sections (3 body tokens) and six Limits sections (4 tokens).
    idf = math.log(1 + (12 - 6 + .5) / (6 + .5))
    lengths = [len(p['text'].split()) for p in passages]
    avg = sum(lengths) / len(lengths)
    expected = idf * (2 * 2.2) / (2 + 1.2 * (.25 + .75 * 3 / avg))
    assert result['hits'][0]['score'] == pytest.approx(expected)
    assert search(store, 'money', corpus, version)['hits'] == result['hits']


def test_no_match_and_explicit_cutoff(knowledge_factory, tmp_path):
    store = KnowledgeStore(tmp_path / 'inv.sqlite')
    corpus = store.publish(knowledge_factory())
    version = store.save_configuration(CONFIG)
    assert search(store, 'notfoundxyz', corpus, version)['status'] == 'no_match'
    high = store.save_configuration({**CONFIG, 'adequacy_cutoff': 100})
    assert search(store, 'money', corpus, high)['status'] == 'no_match'
    assert store.configuration(version) == CONFIG
    assert search(store, 'money', corpus, version)['status'] == 'matched'


@pytest.mark.parametrize('query', ['', ' ', 'x' * 501, None, 1, ['money']])
def test_invalid_queries(knowledge_factory, tmp_path, query):
    store = KnowledgeStore(tmp_path / 'inv.sqlite')
    corpus = store.publish(knowledge_factory())
    with pytest.raises(ValueError):
        search(store, query, corpus, store.save_configuration(CONFIG))


def test_unavailable_config_empty_token_corpus(knowledge_factory, tmp_path):
    store = KnowledgeStore(tmp_path / 'inv.sqlite')
    corpus = store.publish(knowledge_factory('!!!'))
    with pytest.raises(KnowledgeUnavailable):
        search(store, 'money', corpus, store.save_configuration({**CONFIG, 'adequacy_cutoff': None}))
    # Existing sections contain Limits tokens, but a test double can expose avgdl=0.
    class EmptyStore:
        def configuration(self, version): return copy.deepcopy(CONFIG)
        def passages(self, corpus): return []
    with pytest.raises(KnowledgeUnavailable):
        search(EmptyStore(), 'money', corpus, 'a' * 64)
