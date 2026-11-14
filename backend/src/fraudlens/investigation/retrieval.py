"""Offline BM25 baseline; scores are not relevance probabilities."""
import math
import re
import unicodedata
from collections import Counter

from fraudlens.investigation.knowledge import KnowledgeUnavailable
from fraudlens.investigation.models import validate


def tokens(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    return re.findall(r'[^\W_]+', text, flags=re.UNICODE)


class SearchResult(dict):
    """Closed public payload plus internal truncation information for HTTP headers."""
    truncated = False


def search(store, query, corpus, retrieval):
    query = validate('SearchArguments', {'query': query})['query']
    config = store.configuration(retrieval)
    cutoff = config.get('adequacy_cutoff')
    if (isinstance(cutoff, bool) or not isinstance(cutoff, (int, float))
            or not math.isfinite(cutoff) or cutoff < 0
            or config.get('algorithm') != 'bm25' or config.get('k1') != 1.2
            or config.get('b') != .75 or config.get('maximum_results') != 5):
        raise KnowledgeUnavailable('Retrieval configuration unavailable')
    passages = store.passages(corpus)
    counts = [Counter(tokens(p['text'])) for p in passages]
    average = sum(sum(count.values()) for count in counts) / len(counts) if counts else 0
    if average == 0:
        raise KnowledgeUnavailable('Empty corpus')
    # Float addition must have the same order across randomized Python hash seeds.
    terms = sorted(set(tokens(query)))
    n = len(passages)
    frequencies = {term: sum(term in count for count in counts) for term in terms}
    ranked = []
    for passage, count in zip(passages, counts):
        length = sum(count.values())
        score = 0.0
        for term in terms:
            tf = count[term]
            if tf:
                idf = math.log(1 + (n - frequencies[term] + .5) / (frequencies[term] + .5))
                score += idf * tf * 2.2 / (tf + 1.2 * (.25 + .75 * length / average))
        if score > 0 and score >= cutoff:
            ranked.append((score, passage))
    ranked.sort(key=lambda item: (-item[0], item[1]['passage_id']))
    result = SearchResult(validate('SearchResult', dict(
        contract_version=1, corpus_version=corpus, retrieval_version=retrieval,
        query=query, status='matched' if ranked else 'no_match',
        hits=[dict(rank=i + 1, score=score, passage=passage)
              for i, (score, passage) in enumerate(ranked[:5])])))
    result.truncated = len(ranked) > 5
    return result
