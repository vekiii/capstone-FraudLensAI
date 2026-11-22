"""Offline BM25 baseline; scores are not relevance probabilities."""
import math
import re
import unicodedata
from collections import Counter

from fraudlens.investigation.knowledge import KnowledgeUnavailable
from fraudlens.investigation.models import validate

ENGLISH_FUNCTION_WORDS = frozenset('''a an the and or but of in on at to from for
with without by as is are was were be been being do does did can could may might
must should would will shall what which who whom whose when where why how this
that these those it its they their them we our you your i me my not no than then
about into through within each any all both only also have has had'''.split())

SERBIAN_LATIN = str.maketrans(dict(zip(
    'абвгдђежзијклљмнњопрстћуфхцчџш',
    ('a', 'b', 'v', 'g', 'd', 'đ', 'e', 'ž', 'z', 'i', 'j', 'k', 'l', 'lj',
     'm', 'n', 'nj', 'o', 'p', 'r', 's', 't', 'ć', 'u', 'f', 'h', 'c', 'č', 'dž', 'š'),
    strict=True,
)))


def tokens(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    return re.findall(r'[^\W_]+', text, flags=re.UNICODE)


def english_light_stem(term):
    """Versioned lexical heuristic, not a complete morphological analyzer."""
    if len(term) > 5 and term.endswith('ly'):
        term = term[:-2]
    if len(term) > 5 and term.endswith(('ing', 'ed')):
        term = term[:-3] if term.endswith('ing') else term[:-2]
        if len(term) > 3 and term[-1] == term[-2] and term[-1] not in 'aeiou':
            term = term[:-1]
    if len(term) > 4 and term.endswith('s') and not term.endswith(('ss', 'us', 'is')):
        term = term[:-1]
    return term


class SearchResult(dict):
    """Closed public payload plus internal truncation information for HTTP headers."""
    truncated = False


def search(store, query, corpus, retrieval):
    query = validate('SearchArguments', {'query': query})['query']
    config = store.configuration(retrieval)
    policy = config.get('query_normalization', 'legacy')
    if not isinstance(policy, str) or policy not in ('legacy', 'sr_cyrillic_to_latin_v1'):
        raise KnowledgeUnavailable('Unknown query normalization policy')
    cutoff = config.get('adequacy_cutoff')
    if (isinstance(cutoff, bool) or not isinstance(cutoff, (int, float))
            or not math.isfinite(cutoff) or cutoff < 0
            or config.get('algorithm') != 'bm25' or config.get('k1') != 1.2
            or config.get('b') != .75 or config.get('maximum_results') != 5):
        raise KnowledgeUnavailable('Retrieval configuration unavailable')
    passages = store.passages(corpus)
    variant = config.get('variant','baseline')
    coverage_variant = variant in ('english_coverage_v4', 'english_coverage_v5')
    if variant not in ('baseline','title_glossary', 'english_coverage_v4', 'english_coverage_v5'):
        raise KnowledgeUnavailable('Unknown retrieval variant')
    def tokenize(text):
        terms = tokens(text)
        if coverage_variant:
            terms = [term for term in terms if term not in ENGLISH_FUNCTION_WORDS]
        if variant == 'english_coverage_v5':
            terms = [english_light_stem(term) for term in terms if len(term) > 1]
        return terms
    counts = [Counter(tokenize(p['text'])) for p in passages]
    average = sum(sum(count.values()) for count in counts) / len(counts) if counts else 0
    if average == 0:
        raise KnowledgeUnavailable('Empty corpus')
    weights = {term:1.0 for term in tokenize(query)}
    if policy == 'sr_cyrillic_to_latin_v1':
        # Only script conversion for lookup, no new concepts or inferred synonyms.
        # Without this explicit configuration old hashes/scores keep old semantics.
        weights = {term.translate(SERBIAN_LATIN): weight for term, weight in weights.items()}
    titles = [Counter(tokens(p['document']['title']+' '+p['section'])) for p in passages]
    if variant == 'title_glossary':
        glossary = config.get('glossary',{})
        if (glossary.get('status') != 'reviewed' or not glossary.get('reviewed_by')
                or not glossary.get('reviewed_at') or not isinstance(glossary.get('terms'),dict)):
            raise KnowledgeUnavailable('Reviewed glossary required')
        for term in list(weights):
            for synonym in glossary['terms'].get(term,[]):
                if not isinstance(synonym,str) or tokens(synonym) != [synonym]:
                    raise KnowledgeUnavailable('Invalid glossary token')
                weights[synonym] = max(weights.get(synonym,0),.5)
    # Float addition must have the same order across randomized Python hash seeds.
    terms = sorted(weights)
    n = len(passages)
    frequencies = {term: sum(term in count or (variant == 'title_glossary' and term in title)
                            for count,title in zip(counts,titles)) for term in terms}
    ranked = []
    for passage, count, title in zip(passages, counts, titles):
        if coverage_variant and (
            not terms or sum(term in count for term in terms) / len(terms) < .5
        ):
            continue
        length = sum(count.values())
        score = 0.0
        for term in terms:
            tf = count[term] + (2*title[term] if variant == 'title_glossary' else 0)
            if tf:
                idf = math.log(1 + (n - frequencies[term] + .5) / (frequencies[term] + .5))
                score += weights[term] * idf * tf * 2.2 / (tf + 1.2 * (.25 + .75 * length / average))
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
