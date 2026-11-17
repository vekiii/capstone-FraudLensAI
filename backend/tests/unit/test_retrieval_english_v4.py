"""Synthetic lexical controls, not independent retrieval quality evaluation."""
import pytest

from fraudlens.investigation.knowledge import KnowledgeStore, KnowledgeUnavailable
from fraudlens.investigation.retrieval import search


def configured(tmp_path, knowledge_factory, text, variant='english_coverage_v4'):
    store = KnowledgeStore(tmp_path / 'v4.sqlite')
    corpus = store.publish(knowledge_factory(text))
    version = store.save_configuration(dict(algorithm='bm25', k1=1.2, b=.75,
        maximum_results=5, adequacy_cutoff=0., variant=variant))
    return store, corpus, version


def test_function_words_cannot_make_an_answer(tmp_path, knowledge_factory):
    store, corpus, version = configured(tmp_path, knowledge_factory, 'the of and is evidence')
    assert search(store, 'what is the', corpus, version)['status'] == 'no_match'


def test_unmatched_specific_terms_count_against_coverage(tmp_path, knowledge_factory):
    store, corpus, version = configured(tmp_path, knowledge_factory, 'the transaction evidence')
    assert search(store, 'transaction administrator password location', corpus, version)['status'] == 'no_match'


def test_specific_terms_still_retrieve(tmp_path, knowledge_factory):
    store, corpus, version = configured(tmp_path, knowledge_factory, 'supporting documentation records')
    result = search(store, 'What is the supporting documentation?', corpus, version)
    assert result['status'] == 'matched'
    assert result['hits'][0]['passage']['section'] == 'Evidence'


def test_legacy_function_word_behavior_preserved(tmp_path, knowledge_factory):
    store, corpus, version = configured(tmp_path, knowledge_factory, 'the of and is evidence', 'baseline')
    assert search(store, 'what is the', corpus, version)['status'] == 'matched'


def test_unknown_variant_rejected(tmp_path, knowledge_factory):
    store, corpus, version = configured(tmp_path, knowledge_factory, 'supporting records', 'english_magic')
    with pytest.raises(KnowledgeUnavailable):
        search(store, 'records', corpus, version)


def test_v5_handles_plural_inflection_without_unknown_term_discount(tmp_path, knowledge_factory):
    store, corpus, version = configured(tmp_path, knowledge_factory,
        'payment transfers evidence', 'english_coverage_v5')
    assert search(store, 'payments transferred', corpus, version)['status'] == 'matched'
    assert search(store, 'payments administrator password location', corpus, version)['status'] == 'no_match'


def test_opt_in_v5_works_through_existing_http_and_preserves_passage(tmp_path, knowledge_factory, monkeypatch):
    from fastapi.testclient import TestClient

    from fraudlens.main import create_app
    store, corpus, version = configured(tmp_path, knowledge_factory, 'payment transfers evidence', 'english_coverage_v5')
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    app = create_app()
    app.state.knowledge_store = store
    with TestClient(app) as client:
        result = client.get('/api/knowledge/search', params=dict(q='payments transferred', corpus=corpus, retrieval=version))
        assert result.status_code == 200 and result.json()['status'] == 'matched'
        passage = result.json()['hits'][0]['passage']
        opened = client.get('/api/knowledge/passages/' + passage['passage_id'], params=dict(corpus=corpus))
        assert opened.status_code == 200 and opened.json() == passage
        negative = client.get('/api/knowledge/search', params=dict(q='payments administrator password location', corpus=corpus, retrieval=version))
        assert negative.status_code == 200 and negative.json()['status'] == 'no_match'
