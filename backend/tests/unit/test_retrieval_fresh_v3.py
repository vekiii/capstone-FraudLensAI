"""Synthetic v3 workflow/control tests; never the real fresh/legacy evaluation pack."""

import hashlib
import json
from pathlib import Path

import pytest

from fraudlens.investigation import retrieval_fresh_v3 as v3
from fraudlens.investigation.evaluation import verify_seal
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import digest


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def file_hash(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


@pytest.fixture
def pack(tmp_path, knowledge_factory):
    root = tmp_path/'fresh-pack'
    manifest = knowledge_factory('money transfer evidence')
    store = KnowledgeStore(tmp_path/'fixture.sqlite')
    corpus = store.publish(manifest)
    relevant = min(p['passage_id'] for p in store.passages(corpus) if 'money' in p['text'])
    partitions = {}
    for split, languages, answers in (
        ('development', [6, 6, 6], [4, 4, 4]),
        ('held_out', [8, 6, 6], [6, 5, 5]),
    ):
        inputs, refs = [], []
        for lang, count, positive in zip(('en', 'sr-Latn', 'sr-Cyrl'), languages, answers):
            for i in range(count):
                item = dict(id=f'{split}-{lang}-{i}', language=lang,
                            family_id=f'{split}-family-{i}',
                            query=('money' if split == 'development' else 'money money')
                            if i < positive else 'nevermatchxyz')
                inputs.append(item)
                refs.append(dict(id=item['id'], input_sha256=digest(item),
                                 answerability='answerable' if i < positive else 'no_answer',
                                 relevant_passage_ids=[relevant] if i < positive else [],
                                 rationale='Authored synthetic arithmetic/control reference'))
        filename = 'development' if split == 'development' else 'held-out'
        write(root/f'inputs/{filename}.json', inputs)
        write(root/f'reference/{filename}.json', refs)
        partitions[split] = [{k: row[k] for k in ('id', 'language', 'family_id')} for row in inputs]
    write(root/'splits.json', partitions)
    write(root/'protocol.json', dict(version=3, corpus_manifest=str(manifest), corpus_version=corpus,
                                    question_author='SYNTHETIC AUTHOR',
                                    glossary=dict(status='reviewed', reviewed_by='SYNTHETIC REVIEWER',
                                                  reviewed_at='2026-11-17', terms={})))
    reviews = dict(plan=dict(decision='approved', actor='SYNTHETIC PLAN REVIEWER',
                             date='2026-11-17'))
    for split, filename in (('development', 'development'), ('held_out', 'held-out')):
        reviews[split] = dict(
            decision='approved', actor='SYNTHETIC REFERENCE REVIEWER', date='2026-11-17',
            exposure='no_prior_holdout_exposure', novelty_confirmed=True,
            author='SYNTHETIC AUTHOR',
            artifacts={p: file_hash(root/p) for p in
                       (f'inputs/{filename}.json', f'reference/{filename}.json')},
        )
    write(root/'review.json', reviews)
    return root


def prepared(pack, tmp_path):
    development = tmp_path/'development'
    result = v3.develop(pack, development)
    assert result['status'] == 'eligible'
    frozen = tmp_path/'freeze.json'
    v3.freeze(pack, development/'selection.json', frozen)
    return frozen


def authorization(tmp_path, frozen):
    path = tmp_path/'authorization.json'
    write(path, dict(decision='approved', actor='SYNTHETIC USER', date='2026-11-17',
                     freeze_sha256=digest(read(frozen)), maximum_searches=40,
                     provider_calls=0))
    return path


@pytest.mark.parametrize('gate', ['plan', 'development'])
def test_unreviewed_development_never_creates_output(pack, tmp_path, gate):
    reviews = read(pack/'review.json')
    reviews[gate]['decision'] = 'pending'
    write(pack/'review.json', reviews)
    with pytest.raises(ValueError, match='review'):
        v3.develop(pack, tmp_path/'not-created')
    assert not (tmp_path/'not-created').exists()


def test_development_never_opens_heldout_files(pack, tmp_path, monkeypatch):
    original = Path.open
    def guarded(path, *args, **kwargs):
        assert path.name != 'held-out.json', 'Development must not open fresh holdout'
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded)
    result = v3.develop(pack, tmp_path/'dev')
    assert result['status'] == 'eligible' and result['deployment'] == 'baseline'
    assert len(result['rows']['baseline']) == 18
    assert result['choices']['baseline']['metrics']['answerable_count'] == 12
    assert result['choices']['baseline']['metrics']['correct_no_match'] == 6


@pytest.mark.parametrize('problem', ['id', 'family'])
def test_overlapping_split_metadata_is_rejected_before_search(pack, tmp_path, problem):
    splits = read(pack/'splits.json')
    key = 'id' if problem == 'id' else 'family_id'
    splits['held_out'][0][key] = splits['development'][0][key]
    write(pack/'splits.json', splits)
    with pytest.raises(ValueError, match='split|family'):
        v3.develop(pack, tmp_path/'blocked')


def test_changed_review_binding_blocks_selection(pack, tmp_path):
    rows = read(pack/'inputs/development.json')
    rows[0]['query'] = 'altered after review'
    write(pack/'inputs/development.json', rows)
    with pytest.raises(ValueError, match='review'):
        v3.develop(pack, tmp_path/'blocked')


def test_no_feasible_development_cutoff_is_ineligible(pack, tmp_path, monkeypatch):
    import fraudlens.investigation.retrieval as retrieval
    monkeypatch.setattr(retrieval, 'search', lambda *args: dict(hits=[], status='no_match'))
    result = v3.develop(pack, tmp_path/'dev')
    assert result['status'] == 'ineligible' and result['deployment'] is None
    with pytest.raises(ValueError, match='eligible'):
        v3.freeze(pack, tmp_path/'dev/selection.json', tmp_path/'blocked.json')


def test_freeze_requires_new_reference_review_and_never_overwrites(pack, tmp_path):
    v3.develop(pack, tmp_path/'dev')
    reviews = read(pack/'review.json')
    reviews['held_out']['decision'] = 'pending'
    write(pack/'review.json', reviews)
    with pytest.raises(ValueError, match='review'):
        v3.freeze(pack, tmp_path/'dev/selection.json', tmp_path/'blocked.json')
    reviews['held_out']['decision'] = 'approved'
    write(pack/'review.json', reviews)
    v3.freeze(pack, tmp_path/'dev/selection.json', tmp_path/'freeze.json')
    with pytest.raises((ValueError, FileExistsError)):
        v3.freeze(pack, tmp_path/'dev/selection.json', tmp_path/'freeze.json')


@pytest.mark.parametrize('problem', ['missing', 'wrong_freeze', 'budget'])
def test_acceptance_requires_exact_authorization_before_search(pack, tmp_path, problem):
    frozen = prepared(pack, tmp_path)
    auth = authorization(tmp_path, frozen)
    data = read(auth)
    if problem == 'missing':
        data['decision'] = 'pending'
    elif problem == 'wrong_freeze':
        data['freeze_sha256'] = '0'*64
    else:
        data['maximum_searches'] = 41
    write(auth, data)
    with pytest.raises(ValueError, match='authorization'):
        v3.execute(pack, frozen, auth, tmp_path/'blocked')
    assert not (tmp_path/'blocked').exists()


def test_prediction_never_opens_references_and_refuses_replay(pack, tmp_path, monkeypatch):
    frozen = prepared(pack, tmp_path)
    auth = authorization(tmp_path, frozen)
    original = Path.open
    def guarded(path, *args, **kwargs):
        assert 'reference' not in path.parts, 'Prediction must not access private answers'
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded)
    result = v3.execute(pack, frozen, auth, tmp_path/'run')
    assert len(result['rows']['baseline']) == 20
    assert len(result['rows']['improved']) == 20
    with pytest.raises((ValueError, FileExistsError)):
        v3.execute(pack, frozen, auth, tmp_path/'second-location')
    assert not (tmp_path/'second-location').exists()


def test_changed_frozen_input_blocks_execution(pack, tmp_path):
    frozen = prepared(pack, tmp_path)
    auth = authorization(tmp_path, frozen)
    rows = read(pack/'inputs/held-out.json')
    rows[0]['query'] = 'changed'
    write(pack/'inputs/held-out.json', rows)
    with pytest.raises(ValueError, match='hash'):
        v3.execute(pack, frozen, auth, tmp_path/'blocked')


def test_changed_rank_source_blocks_execution(pack, tmp_path, monkeypatch):
    frozen = prepared(pack, tmp_path)
    auth = authorization(tmp_path, frozen)
    monkeypatch.setattr(v3, '_source_hashes', lambda: {})
    with pytest.raises(ValueError, match='source'):
        v3.execute(pack, frozen, auth, tmp_path/'blocked')


def test_changed_archived_text_with_same_passage_ids_is_rejected(pack, tmp_path, monkeypatch):
    import copy
    frozen = prepared(pack, tmp_path)
    auth = authorization(tmp_path, frozen)
    original = KnowledgeStore.corpus
    def changed(store, version):
        value = copy.deepcopy(original(store, version))
        value['passages'][0]['text'] += ' changed content without a changed ID'
        return value
    monkeypatch.setattr(KnowledgeStore, 'corpus', changed)
    with pytest.raises(ValueError, match='corpus'):
        v3.execute(pack, frozen, auth, tmp_path/'blocked')
    assert not (tmp_path/'blocked').exists()


def test_changed_original_corpus_file_blocks_freeze(pack, tmp_path):
    v3.develop(pack, tmp_path/'dev')
    manifest = Path(read(pack/'protocol.json')['corpus_manifest'])
    document = manifest.parent/'documents/doc0.md'
    document.write_text(document.read_text() + '\nChanged after selection\n')
    with pytest.raises(ValueError, match='corpus'):
        v3.freeze(pack, tmp_path/'dev/selection.json', tmp_path/'blocked.json')


def test_changed_private_answers_are_detected_at_join(pack, tmp_path):
    frozen = prepared(pack, tmp_path)
    auth = authorization(tmp_path, frozen)
    write(pack/'reference/held-out.json', [])
    v3.execute(pack, frozen, auth, tmp_path/'run')
    with pytest.raises(ValueError, match='hash'):
        v3.join(pack, frozen, tmp_path/'run/predictions.json', tmp_path/'blocked.json')


def test_reference_author_cannot_approve_own_answers(pack, tmp_path):
    reviews = read(pack/'review.json')
    reviews['development']['actor'] = 'SYNTHETIC AUTHOR'
    write(pack/'review.json', reviews)
    with pytest.raises(ValueError, match='review'):
        v3.develop(pack, tmp_path/'blocked')


@pytest.mark.parametrize('extra', ['reference_answer', 'relevant_passage_ids', 'label'])
def test_private_input_fields_are_rejected_even_with_matching_review(pack, tmp_path, extra):
    inputs = read(pack/'inputs/development.json')
    inputs[0][extra] = 'PRIVATE CANARY'
    write(pack/'inputs/development.json', inputs)
    reviews = read(pack/'review.json')
    reviews['development']['artifacts']['inputs/development.json'] = file_hash(
        pack/'inputs/development.json')
    write(pack/'review.json', reviews)
    with pytest.raises(ValueError, match='input'):
        v3.develop(pack, tmp_path/'blocked')


@pytest.mark.parametrize('problem', ['unsealed', 'missing', 'duplicate'])
def test_join_rejects_invalid_predictions_before_reading_references(pack, tmp_path,
                                                                  monkeypatch, problem):
    from fraudlens.investigation.evaluation import seal
    frozen = prepared(pack, tmp_path)
    auth = authorization(tmp_path, frozen)
    v3.execute(pack, frozen, auth, tmp_path/'run')
    predictions = tmp_path/'run/predictions.json'
    value = read(predictions)
    if problem == 'unsealed':
        value['sha256'] = '0'*64
    else:
        payload = verify_seal(value)
        rows = payload['rows']['baseline']
        rows.pop() if problem == 'missing' else rows.append(rows[0])
        value = seal(payload)
    write(predictions, value)
    original = Path.open
    def guarded(path, *args, **kwargs):
        assert 'reference' not in path.parts
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded)
    with pytest.raises(ValueError):
        v3.join(pack, frozen, predictions, tmp_path/'blocked.json')


def test_error_outcomes_keep_denominators_and_cannot_pass_no_answer(pack, tmp_path, monkeypatch):
    import fraudlens.investigation.retrieval as retrieval
    frozen = prepared(pack, tmp_path)
    auth = authorization(tmp_path, frozen)
    def fail(*args):
        raise ValueError('PRIVATE EXCEPTION MUST NOT LEAK')
    monkeypatch.setattr(retrieval, 'search', fail)
    result = v3.execute(pack, frozen, auth, tmp_path/'run')
    assert all(row['error'] == 'search_error' for row in result['rows']['baseline'])
    metrics = v3.join(pack, frozen, tmp_path/'run/predictions.json', tmp_path/'metrics.json')
    overall = metrics['configurations']['baseline']['overall']
    assert overall['answerable_count'] == 16 and overall['no_answer_count'] == 4
    assert overall['recall_at_5'] == 0 and overall['correct_no_match'] == 0
    assert overall['no_answer_errors'] == 4 and overall['false_answer'] == 0
    assert not metrics['sc002_met']
    assert 'PRIVATE EXCEPTION' not in (tmp_path/'run/predictions.json').read_text()


def test_complete_synthetic_experiment_has_both_metrics_and_immutable_results(pack, tmp_path):
    frozen = prepared(pack, tmp_path)
    v3.execute(pack, frozen, authorization(tmp_path, frozen), tmp_path/'run')
    result = v3.join(pack, frozen, tmp_path/'run/predictions.json', tmp_path/'metrics.json')
    assert set(result['configurations']) == {'baseline', 'improved'}
    assert result['configurations']['baseline']['overall']['recall_at_5'] == 1
    assert result['configurations']['baseline']['overall']['correct_no_match'] == 4
    assert result['deployment'] == 'baseline' and result['sc002_met']
    assert len(result['comparisons']) == 20
    assert all(row['change'] == 'unchanged' for row in result['comparisons'])
    with pytest.raises((ValueError, FileExistsError)):
        v3.join(pack, frozen, tmp_path/'run/predictions.json', tmp_path/'metrics.json')


def test_sqlite_search_errors_preserve_all_rows(pack, tmp_path, monkeypatch):
    import sqlite3

    import fraudlens.investigation.retrieval as retrieval
    frozen = prepared(pack, tmp_path)
    def fail(*args):
        raise sqlite3.OperationalError('PRIVATE DATABASE ERROR')
    monkeypatch.setattr(retrieval, 'search', fail)
    result = v3.execute(pack, frozen, authorization(tmp_path, frozen), tmp_path/'run')
    assert all(len(rows) == 20 for rows in result['rows'].values())
    assert all(r['error'] == 'search_error' for rows in result['rows'].values() for r in rows)
