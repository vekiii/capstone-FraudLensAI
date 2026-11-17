"""Explicit offline v3 evaluation; no legacy pack, settings or provider imports.

Reviews/authorizations are trusted local human records, not authentication.
Development, immutable freeze, input-only prediction and private join are separate
operations. This module is never imported by application generation.
"""

import argparse
import copy
import hashlib
import json
import math
import sqlite3
from collections import Counter
from pathlib import Path

from fraudlens.investigation.evaluation import (
    LANGUAGES,
    seal,
    select_development_cutoff,
    verify_seal,
)
from fraudlens.investigation.knowledge import KnowledgeStore, stage
from fraudlens.investigation.models import ROOT, digest

FILES = {
    'development': ('inputs/development.json', 'reference/development.json'),
    'held_out': ('inputs/held-out.json', 'reference/held-out.json'),
}
COUNTS = {'development': [6, 6, 6], 'held_out': [8, 6, 6]}
ANSWERS = {'development': [4, 4, 4], 'held_out': [6, 5, 5]}


def _read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def _write(path, payload):
    # Parent must already exist: no implicit mutation before precondition checks.
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(seal(payload), stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def _source_hashes():
    paths = sorted((ROOT/'backend/src/fraudlens/investigation').glob('*.py'))
    paths += sorted((ROOT/'specs/003-ai-investigation/contracts').glob('*.json'))
    paths += [ROOT/'specs/001-project-foundation/contracts/schemas.json']
    return {str(p.relative_to(ROOT)).replace('\\', '/'): _hash(p) for p in paths}


def _metadata(pack, complete=False):
    protocol, splits, reviews = (_read(pack/p) for p in
                                 ('protocol.json', 'splits.json', 'review.json'))
    if protocol.get('version') != 3 or set(splits) != set(FILES):
        raise ValueError('Unknown v3 protocol/split')
    ids, families = {}, {}
    for split in FILES:
        rows = splits[split]
        if (not isinstance(rows, list)
                or any(set(row) != {'id', 'language', 'family_id'} for row in rows)):
            raise ValueError('Invalid split metadata')
        if any(not isinstance(v, str) or not v.strip() for row in rows for v in row.values()):
            raise ValueError('Invalid split identity/family')
        ids[split], families[split] = {r['id'] for r in rows}, {r['family_id'] for r in rows}
        if len(ids[split]) != len(rows):
            raise ValueError('Duplicate split identity')
        if split == 'development' or complete:
            expected = dict(zip(LANGUAGES, COUNTS[split]))
            if Counter(r['language'] for r in rows) != expected:
                raise ValueError('Invalid split language counts')
    if ids['development'] & ids['held_out'] or families['development'] & families['held_out']:
        raise ValueError('Overlapping split identity/family')
    plan = reviews.get('plan', {})
    if (plan.get('decision') != 'approved' or not plan.get('actor') or not plan.get('date')):
        raise ValueError('Plan review required')
    return protocol, splits, reviews


def _review(pack, reviews, split, protocol):
    review = reviews.get(split, {})
    author = protocol.get('question_authors', {}).get(split, protocol.get('question_author'))
    if (review.get('decision') != 'approved' or not review.get('actor')
            or not review.get('date') or not author or review.get('author') != author
            or review['actor'] == review['author']
            or review.get('novelty_confirmed') is not True
            or review.get('exposure') != 'no_prior_holdout_exposure'):
        raise ValueError('Actual independent reference/novelty review required')
    expected = {p: _hash(pack/p) for p in FILES[split]}
    if review.get('artifacts') != expected:
        raise ValueError('Reference review hash binding changed')


def _inputs(pack, splits, split):
    rows = _read(pack/FILES[split][0])
    if (not isinstance(rows, list) or any(
            set(r) != {'id', 'family_id', 'language', 'query'}
            or not isinstance(r['query'], str) or not 1 <= len(r['query'].strip()) <= 500
            for r in rows)):
        raise ValueError('Invalid input-only question')
    projected = [{k: r[k] for k in ('id', 'language', 'family_id')} for r in rows]
    if projected != splits[split]:
        raise ValueError('Input/split identity mismatch')
    return rows


def _references(pack, split, inputs, passages):
    rows = _read(pack/FILES[split][1])
    by_id = {r['id']: r for r in rows}
    if len(by_id) != len(rows) or set(by_id) != {r['id'] for r in inputs}:
        raise ValueError('Reference denominator mismatch')
    positive = Counter()
    for item in inputs:
        ref = by_id[item['id']]
        relevant = ref.get('relevant_passage_ids')
        if (set(ref) != {'id', 'input_sha256', 'answerability', 'relevant_passage_ids', 'rationale'}
                or ref['input_sha256'] != digest(item) or not ref['rationale'].strip()
                or not isinstance(relevant, list) or len(set(relevant)) != len(relevant)
                or not set(relevant) <= passages):
            raise ValueError('Invalid reference binding/passages')
        if ref['answerability'] == 'answerable' and relevant:
            positive[item['language']] += 1
        elif ref['answerability'] != 'no_answer' or relevant:
            raise ValueError('Invalid reference answerability')
    if positive != dict(zip(LANGUAGES, ANSWERS[split])):
        raise ValueError('Reference answerability counts changed')
    return by_id


def _predict(store, corpus, configurations, inputs, split):
    from fraudlens.investigation.retrieval import search
    rows = {}
    for name, config in configurations.items():
        version = digest(config)
        group = rows[name] = []
        for item in inputs:
            row = dict(id=item['id'], language=item['language'], split=split,
                       input_sha256=digest(item), hits=[], scores=[], error=None)
            try:
                result = search(store, item['query'], corpus, version)
                row.update(hits=[h['passage']['passage_id'] for h in result['hits']],
                           scores=[h['score'] for h in result['hits']])
            except (ValueError, OSError, sqlite3.Error):
                row['error'] = 'search_error'
            group.append(row)
    return rows


def develop(pack, output):
    """Run only reviewed development questions; never open held-out files."""
    pack, output = Path(pack).resolve(), Path(output).resolve()
    protocol, splits, reviews = _metadata(pack)
    _review(pack, reviews, 'development', protocol)
    inputs = _inputs(pack, splits, 'development')
    prepared = stage(protocol['corpus_manifest'])
    if prepared['corpus_version'] != protocol['corpus_version']:
        raise ValueError('Corpus hash mismatch')
    refs = _references(pack, 'development', inputs,
                       {p['passage_id'] for p in prepared['passages']})
    configs = {}
    for name, variant in (('baseline', 'baseline'), ('improved', 'title_glossary')):
        configs[name] = dict(configuration_version=5, algorithm='bm25', k1=1.2, b=.75,
                             maximum_results=5, adequacy_cutoff=0, variant=variant,
                             query_normalization='legacy' if name == 'baseline'
                             else 'sr_cyrillic_to_latin_v1')
    configs['improved']['glossary'] = copy.deepcopy(protocol['glossary'])
    # All real pack searches occur only after its reference review.
    output.mkdir(parents=True, exist_ok=False)
    store_path = output/'knowledge.sqlite'
    store = KnowledgeStore(store_path)
    corpus = store.publish(protocol['corpus_manifest'])
    for config in configs.values():
        store.save_configuration(config)
    rows = _predict(store, corpus, configs, inputs, 'development')
    choices = {name: None if any(r['error'] for r in group)
               else select_development_cutoff(group, list(refs.values()))
               for name, group in rows.items()}
    eligible = all(choices.values())
    if eligible:
        for name in configs:
            configs[name]['adequacy_cutoff'] = choices[name]['cutoff']
            store.save_configuration(configs[name])
    deployment = max(configs, key=lambda name: (
        choices[name]['metrics']['recall_at_5'], choices[name]['metrics']['mrr_at_5'],
        name == 'baseline')) if eligible else None
    result = dict(kind='retrieval_fresh_v3_development', status='eligible' if eligible
                  else 'ineligible', rows=rows, choices=choices, configurations=configs,
                  deployment=deployment, corpus_version=corpus, store=str(store_path),
                  source_hashes=_source_hashes(),
                  artifacts={p: _hash(pack/p) for p in (*FILES['development'], 'protocol.json')},
                  development_metadata=splits['development'], development_review=reviews['development'],
                  plan_review=reviews['plan'], corpus_sha256=digest(store.corpus(corpus)),
                  corpus_artifacts={str(p.resolve()): _hash(p) for p in (
                      Path(protocol['corpus_manifest']),
                      *(Path(protocol['corpus_manifest']).parent/'documents'/d['path']
                        for d in _read(protocol['corpus_manifest'])['documents']))})
    _write(output/'selection.json', result)
    return result


def freeze(pack, development, output):
    """Hash reviewed held-out files without parsing question/answer contents."""
    pack, development = Path(pack).resolve(), Path(development).resolve()
    protocol, splits, reviews = _metadata(pack, complete=True)
    selected = verify_seal(_read(development))
    if selected.get('kind') != 'retrieval_fresh_v3_development' or selected['status'] != 'eligible':
        raise ValueError('Both development configurations must be eligible')
    if selected['source_hashes'] != _source_hashes():
        raise ValueError('Development source changed')
    for path, expected in selected['corpus_artifacts'].items():
        if _hash(path) != expected:
            raise ValueError('Development corpus artifact hash mismatch')
    if (selected['development_metadata'] != splits['development']
            or selected['development_review'] != reviews['development']
            or selected['plan_review'] != reviews['plan']):
        raise ValueError('Development review/split changed')
    for p, expected in selected['artifacts'].items():
        if _hash(pack/p) != expected:
            raise ValueError('Development artifact hash mismatch')
    for split in FILES:
        _review(pack, reviews, split, protocol)
    paths = [*FILES['development'], *FILES['held_out'],
             'protocol.json', 'splits.json', 'review.json']
    result = dict(kind='retrieval_fresh_v3_freeze', configurations=selected['configurations'],
                  deployment=selected['deployment'], corpus_version=selected['corpus_version'],
                  store=selected['store'], source_hashes=selected['source_hashes'],
                  corpus_sha256=selected['corpus_sha256'],
                  corpus_artifacts=selected['corpus_artifacts'],
                  pack_hashes={p: _hash(pack/p) for p in paths},
                  selection_sha256=_hash(development), selection_path=str(development),
                  execution_claim=str(development.parent/'execution-claim.json'),
                  passage_ids=[p['passage_id'] for p in KnowledgeStore(
                      selected['store'], initialize=False).passages(selected['corpus_version'])])
    _write(output, result)
    return result


def _frozen(pack, path, include_references=False):
    result = verify_seal(_read(path))
    if result.get('kind') != 'retrieval_fresh_v3_freeze':
        raise ValueError('Unknown freeze')
    if result['source_hashes'] != _source_hashes():
        raise ValueError('Frozen source hash mismatch')
    if _hash(result['selection_path']) != result['selection_sha256']:
        raise ValueError('Frozen selection hash mismatch')
    for path, expected in result['corpus_artifacts'].items():
        if _hash(path) != expected:
            raise ValueError('Frozen corpus artifact hash mismatch')
    for p, expected in result['pack_hashes'].items():
        if not include_references and p.startswith('reference/'):
            continue
        if _hash(pack/p) != expected:
            raise ValueError('Frozen artifact hash mismatch')
    return result


def execute(pack, frozen, authorization, output):
    """One authorized 40-search prediction run. No private reference access."""
    pack, output = Path(pack).resolve(), Path(output).resolve()
    state = _frozen(pack, frozen)
    auth = _read(authorization)
    freeze_hash = digest(_read(frozen))
    if (auth.get('decision') != 'approved' or not auth.get('actor') or not auth.get('date')
            or auth.get('freeze_sha256') != freeze_hash or auth.get('maximum_searches') != 40
            or auth.get('provider_calls') != 0):
        raise ValueError('Explicit freeze-bound 40-search authorization required')
    _, splits, _ = _metadata(pack, complete=True)
    inputs = _inputs(pack, splits, 'held_out')
    store = KnowledgeStore(state['store'], initialize=False)
    for config in state['configurations'].values():
        if store.configuration(digest(config)) != config:
            raise ValueError('Archived configuration hash mismatch')
    if digest(store.corpus(state['corpus_version'])) != state['corpus_sha256']:
        raise ValueError('Archived corpus hash mismatch')
    if output.exists():
        raise FileExistsError('Prediction output already exists')
    # Claim is anchored to the selection, so copying a freeze cannot reset it.
    _write(state['execution_claim'], dict(freeze_sha256=freeze_hash, output=str(output),
                                         authorization_sha256=_hash(authorization)))
    output.mkdir(parents=True, exist_ok=False)
    result = dict(kind='retrieval_fresh_v3_predictions', freeze_sha256=freeze_hash,
                  deployment=state['deployment'], rows=_predict(
                      store, state['corpus_version'], state['configurations'], inputs, 'held_out'))
    _write(output/'predictions.json', result)
    return result


def _prediction_rows(payload, state, inputs):
    if set(payload.get('rows', {})) != {'baseline', 'improved'}:
        raise ValueError('Both prediction configurations required')
    expected = {r['id']: r for r in inputs}
    for name, rows in payload['rows'].items():
        if (len(rows) != len(expected) or len({r['id'] for r in rows}) != len(rows)
                or {r['id'] for r in rows} != set(expected)):
            raise ValueError('Prediction denominator mismatch')
        for row in rows:
            hits, scores = row['hits'], row['scores']
            if (row['input_sha256'] != digest(expected[row['id']])
                    or row['language'] != expected[row['id']]['language']
                    or row['split'] != 'held_out' or len(hits) != len(scores)
                    or len(hits) > 5 or len(set(hits)) != len(hits)
                    or not set(hits) <= set(state['passage_ids'])
                    or row['error'] not in (None, 'search_error') or (row['error'] and hits)
                    or any(type(s) not in (float, int) or not math.isfinite(s)
                           or s <= 0 or s < state['configurations'][name]['adequacy_cutoff']
                           for s in scores)
                    or list(zip(scores, hits)) != sorted(zip(scores, hits),
                                                         key=lambda pair: (-pair[0], pair[1]))):
                raise ValueError('Invalid bound prediction row')


def _metrics(rows, refs):
    def group(selected):
        recall, ranks = [], []
        missing = correct = false = no_errors = errors = 0
        for row in selected:
            ref = refs[row['id']]
            errors += bool(row['error'])
            if ref['answerability'] == 'answerable':
                relevant = set(ref['relevant_passage_ids'])
                recall.append(len(relevant.intersection(row['hits']))/len(relevant))
                ranks.append(next((1/(i+1) for i, hit in enumerate(row['hits'])
                                   if hit in relevant), 0))
            else:
                missing += 1
                no_errors += bool(row['error'])
                correct += not row['hits'] and not row['error']
                false += bool(row['hits'])
        return dict(answerable_count=len(recall), no_answer_count=missing,
                    recall_at_5=sum(recall)/len(recall) if recall else None,
                    mrr_at_5=sum(ranks)/len(ranks) if ranks else None,
                    correct_no_match=correct, false_answer=false,
                    no_answer_errors=no_errors, execution_errors=errors)
    return {lang: group([r for r in rows if lang == 'overall' or r['language'] == lang])
            for lang in ('overall', *LANGUAGES)}


def join(pack, frozen, predictions, output):
    """Validate complete sealed predictions before opening any private answers."""
    pack = Path(pack).resolve()
    state = _frozen(pack, frozen)
    payload = verify_seal(_read(predictions))
    if (payload.get('kind') != 'retrieval_fresh_v3_predictions'
            or payload.get('freeze_sha256') != digest(_read(frozen))
            or payload.get('deployment') != state['deployment']):
        raise ValueError('Prediction/freeze binding mismatch')
    _, splits, _ = _metadata(pack, complete=True)
    inputs = _inputs(pack, splits, 'held_out')
    _prediction_rows(payload, state, inputs)
    _frozen(pack, frozen, include_references=True)
    refs = _references(pack, 'held_out', inputs, set(state['passage_ids']))
    metrics = {name: _metrics(rows, refs) for name, rows in payload['rows'].items()}
    passed = {name: (group['overall']['recall_at_5'] >= .8
                     and group['overall']['mrr_at_5'] >= .7
                     and group['overall']['correct_no_match'] == 4)
              for name, group in metrics.items()}
    by_id = {name: {r['id']: r for r in rows} for name, rows in payload['rows'].items()}
    comparisons = []
    for item in inputs:
        scores = {name: _metrics([by_id[name][item['id']]], refs)['overall']
                  for name in by_id}
        def quality(name):
            score = scores[name]
            return ((score['recall_at_5'], score['mrr_at_5']) if score['answerable_count']
                    else (score['correct_no_match'], -score['execution_errors']))
        before, after = quality('baseline'), quality('improved')
        lower = any(a < b for a, b in zip(after, before))
        higher = any(a > b for a, b in zip(after, before))
        change = ('mixed' if lower and higher else 'regressed' if lower
                  else 'improved' if higher else 'unchanged')
        comparisons.append(dict(id=item['id'], configurations=scores, change=change))
    result = dict(kind='retrieval_fresh_v3_metrics', configurations=metrics,
                  configuration_pass=passed, sc002_met=any(passed.values()),
                  deployment=state['deployment'], comparisons=comparisons,
                  freeze_sha256=digest(_read(frozen)), predictions_sha256=_hash(predictions))
    _write(output, result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('develop', 'freeze', 'execute', 'join'):
        command = commands.add_parser(name)
        command.add_argument('--pack', required=True, type=Path)
        command.add_argument('--output', required=True, type=Path)
        if name == 'freeze':
            command.add_argument('--development', required=True, type=Path)
        if name in ('execute', 'join'):
            command.add_argument('--freeze', required=True, type=Path)
        if name == 'execute':
            command.add_argument('--authorization', required=True, type=Path)
        if name == 'join':
            command.add_argument('--predictions', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        operation = globals()[args.command]
        values = dict(vars(args))
        values.pop('command')
        if 'freeze' in values:
            values['frozen'] = values.pop('freeze')
        result = operation(**values)
        print(json.dumps(dict(kind=result['kind'], status=result.get('status', 'completed'))))
        return 0
    except (ValueError, OSError, KeyError, TypeError):
        print('Fresh retrieval operation blocked; inspect protocol, reviews and frozen artifacts.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
