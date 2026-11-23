"""Reviewed SQLite consumer integration, using controlled non-IBM records."""
import copy
import json
import sqlite3

import pytest

from fraudlens.investigation.context import CaseContextReader, HistoryReader, outbound_context
from fraudlens.investigation.models import ROOT, context_digest, validate


@pytest.fixture
def published(tmp_path):
    ctx = json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/context-dataset.json').read_text())
    payload = ctx['source_payload']
    runs, source = tmp_path / 'runs.sqlite', tmp_path / 'source.sqlite'
    with sqlite3.connect(runs) as db:
        db.executescript('''
          CREATE TABLE scored_runs(run_id TEXT,dataset_version TEXT,score_source TEXT,
            scorer_version TEXT,status TEXT);
          CREATE TABLE active_run(singleton INTEGER,run_id TEXT);
          CREATE TABLE scored_assessments(run_id TEXT,case_id TEXT,transaction_json TEXT,
            assessment_json TEXT,alert INTEGER);
        ''')
        db.execute('INSERT INTO scored_runs VALUES(?,?,?,?,?)',
                   (ctx['snapshot_ref'], ctx['dataset_version'], 'rules', 'rules-v1', 'completed'))
        db.execute('INSERT INTO active_run VALUES(1,?)', (ctx['snapshot_ref'],))
        db.execute('INSERT INTO scored_assessments VALUES(?,?,?,?,1)',
                   (ctx['snapshot_ref'], ctx['case_id'], json.dumps(payload['transaction']),
                    json.dumps(payload['risk_assessment'])))
    with sqlite3.connect(source) as db:
        db.executescript('''
          CREATE TABLE dataset_versions(id TEXT,status TEXT,rejected_records INTEGER);
          CREATE TABLE active_dataset(singleton INTEGER,version TEXT);
          CREATE TABLE operational_events(version TEXT,transaction_id TEXT,case_id TEXT,payload_json TEXT);
          CREATE TABLE private_evaluation_labels(secret TEXT);
          INSERT INTO private_evaluation_labels VALUES('PRIVATE_CANARY_DO_NOT_READ');
        ''')
        db.execute('INSERT INTO dataset_versions VALUES(?,?,0)', (ctx['dataset_version'], 'complete'))
        db.execute('INSERT INTO active_dataset VALUES(1,?)', (ctx['dataset_version'],))
    return ctx, runs, source


def adapter(published):
    from fraudlens.investigation.dataset import DatasetReader
    return DatasetReader(published[1], published[2], 'rules')


def add_event(published, number, at='2026-01-01T09:59:00+00:00', **changes):
    ctx, _, path = published
    fields = dict(event_time_utc=at, event_time_raw=at[:16],
                  time_basis='assumed_utc_for_synthetic_benchmark',
                  sender_bank='SYNTH-BANK-A', sender_account='001',
                  receiver_bank='SYNTH-BANK-B', receiver_account='002',
                  paid_amount='1.2300', paid_currency='Australian Dollar',
                  received_amount='0.00000001', received_currency='Bitcoin')
    fields.update(changes)
    with sqlite3.connect(path) as db:
        db.execute('INSERT INTO operational_events VALUES(?,?,?,?)',
                   (ctx['dataset_version'], 'D' + f'{number:032x}', 'C' + f'{number:032x}', json.dumps(fields)))


def test_real_reader_wiring_and_exact_projection(published):
    ctx, _, _ = published
    reader = adapter(published)
    result = CaseContextReader(dataset_reader=reader).resolve(ctx['case_id'], 'dataset', ctx['snapshot_ref'])
    assert result['contract_version'] == 2
    assert result['source_payload'] == ctx['source_payload']
    projection = outbound_context(result, 'inv_' + '1' * 32)
    assert projection['transaction']['paid']['amount'] == '1250.000'
    assert projection['transaction']['time_basis'] == 'assumed_utc_for_synthetic_benchmark'
    assert 'PRIVATE_CANARY' not in json.dumps(result)
    assert result['history']['coverage'] == 'unavailable'  # empty source != known empty account history


@pytest.mark.parametrize('mutation', ['run', 'dataset', 'transaction', 'time', 'scale', 'kind', 'sum', 'private'])
def test_published_semantic_corruption_fails_closed(published, mutation):
    ctx, runs, _ = published
    payload = copy.deepcopy(ctx['source_payload'])
    risk = payload['risk_assessment']
    if mutation == 'run':
        risk['run_id'] = 'run_other'
    elif mutation == 'dataset':
        risk['dataset_version'] = 'dv_' + 'b' * 64
    elif mutation == 'transaction':
        risk['transaction_id'] = 'D' + 'b' * 32
    elif mutation == 'time':
        risk['event_time_utc'] = '2026-01-01T09:00:00Z'
    elif mutation == 'scale':
        risk['explanation']['explained_scale'] = 'log_odds'
    elif mutation == 'kind':
        risk['score_kind'] = 'positive_class_estimate'
    elif mutation == 'sum':
        risk['explanation']['base_value'] = 0.2
    else:
        payload['transaction']['is_laundering'] = 1
    with sqlite3.connect(runs) as db:
        db.execute('UPDATE scored_assessments SET transaction_json=?,assessment_json=?',
                   (json.dumps(payload['transaction']), json.dumps(risk)))
    with pytest.raises(ValueError):
        adapter(published).resolve(ctx['case_id'], ctx['snapshot_ref'])


def test_history_scope_direction_limits_exact_totals_and_missing(published):
    ctx, _, source = published
    add_event(published, 90, '2025-12-25T09:59:00+00:00')  # proves window coverage
    add_event(published, 91, '2026-01-01T10:00:00+00:00')
    add_event(published, 92, sender_bank='OTHER')
    for i in range(1, 53):
        add_event(published, i)
    reader = adapter(published)
    context = reader.resolve(ctx['case_id'], ctx['snapshot_ref'])
    before = source.read_bytes()
    result = HistoryReader(dataset_reader=reader).read(context, 'sender')
    assert result['eligible_count'] == 52 and result['returned_count'] == 50 and result['truncated']
    assert result['totals'] == {'outgoing': {'Australian Dollar': '63.9600'}}
    assert result['events'][0]['amount'] == '1.2300'
    assert result['events'][0]['direction'] == 'outgoing'
    incoming = reader.read(context, 'receiver', 1)
    assert incoming['totals'] == {'incoming': {'Bitcoin': '0.00000053'}}
    assert source.read_bytes() == before
    assert context['history']['coverage'] == 'full'
    assert 'PRIVATE_CANARY' not in json.dumps([context, result, incoming])
    reader.dataset_store = source.with_name('absent.sqlite')
    missing = reader.read(context, 'sender')
    assert missing['availability'] == 'unavailable' and missing['eligible_count'] is None
    assert not reader.dataset_store.exists()


def test_source_switch_rejected_and_old_version_still_strict(published):
    ctx, runs, source = published
    reader = adapter(published)
    context = reader.resolve(ctx['case_id'], ctx['snapshot_ref'])
    with sqlite3.connect(runs) as db:
        db.execute("UPDATE active_run SET run_id='run_other'")
    with pytest.raises(ValueError, match='stale_snapshot'):
        reader.read(context, 'sender')
    validate('InvestigationContext', context)  # archived context remains readable
    risk = ctx['source_payload']['risk_assessment']
    risk['explanation'].update(method='boosted_sequential_probability', explained_scale='positive_class_estimate')
    ctx['context_revision'] = context_digest(ctx)
    with pytest.raises(ValueError):
        validate('InvestigationContext', ctx)


def test_available_empty_history_is_not_unavailable(published):
    ctx, _, _ = published
    add_event(published, 99, '2025-12-24T10:00:00+00:00', sender_account='OTHER', receiver_account='OTHER')
    reader = adapter(published)
    context = reader.resolve(ctx['case_id'], ctx['snapshot_ref'])
    result = reader.read(context, 'sender')
    assert result['availability'] == 'available' and result['eligible_count'] == 0
    assert result['coverage'] == 'full' and result['events'] == []


def test_new_boosted_version_is_explicit_and_provider_projection_accepts_it(published):
    from fraudlens.investigation.dataset import DatasetReader
    from fraudlens.investigation.provider import project_conversation
    ctx, runs, source = published
    risk = ctx['source_payload']['risk_assessment']
    risk.update(score_source='model', score_kind='uncalibrated_probability_estimate',
                scorer_version='model-history-v1-boosted-candidate')
    risk['explanation'].update(method='boosted_sequential_probability', explained_scale='positive_class_estimate')
    with sqlite3.connect(runs) as db:
        db.execute("UPDATE scored_runs SET score_source='model',scorer_version=?", (risk['scorer_version'],))
        db.execute('UPDATE scored_assessments SET assessment_json=?', (json.dumps(risk),))
    reader = DatasetReader(runs, source, 'model')
    context = reader.resolve(ctx['case_id'], ctx['snapshot_ref'])
    projected = outbound_context(context, 'inv_' + 'a' * 32)
    assert projected['context_contract_version'] == 2
    assert 'order/baseline dependent' in projected['notice']
    assert project_conversation([{'type': 'context', 'data': projected}])[0]['data'] == projected
    projected.pop('context_contract_version')
    with pytest.raises(ValueError):
        project_conversation([{'type': 'context', 'data': projected}])


def test_inclusive_start_focal_future_and_directional_self_transfer(published):
    ctx, _, source = published
    add_event(published, 1, '2025-12-25T10:00:00+00:00')
    add_event(published, 2, '2026-01-01T10:00:00+00:00')
    add_event(published, 3, '2026-01-02T10:00:00+00:00')
    add_event(published, 4, receiver_bank='SYNTH-BANK-A', receiver_account='001')
    add_event(published, 5)  # focal exclusion must work even inside eligible time
    with sqlite3.connect(source) as db:
        db.execute('UPDATE operational_events SET transaction_id=? WHERE transaction_id=?',
                   (ctx['source_payload']['transaction']['transaction_id'], 'D' + f'{5:032x}'))
    reader = adapter(published)
    context = reader.resolve(ctx['case_id'], ctx['snapshot_ref'])
    result = reader.read(context, 'sender')
    assert result['eligible_count'] == 3
    assert result['totals'] == {'outgoing': {'Australian Dollar': '2.4600'}, 'incoming': {'Bitcoin': '0.00000001'}}
    with reader.connection(source) as db:
        with pytest.raises(sqlite3.DatabaseError):
            db.execute('SELECT secret FROM private_evaluation_labels').fetchall()
        with pytest.raises(sqlite3.OperationalError):
            db.execute('DELETE FROM operational_events')


def test_configured_service_archives_dataset_and_tools_preserve_direction(published, knowledge_factory, tmp_path, monkeypatch):
    from uuid import uuid4

    from fastapi.testclient import TestClient

    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.settings import InvestigationSettings
    from fraudlens.investigation.tools import ToolExecutor
    from fraudlens.investigation.workflow import InvestigationService
    from fraudlens.main import create_app
    ctx, runs, source = published
    add_event(published, 1)
    knowledge = KnowledgeStore(tmp_path / 'investigations.sqlite')
    knowledge.publish(knowledge_factory())
    config = json.loads((ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text())
    knowledge.save_configuration(config)
    service = InvestigationService(knowledge.repository, knowledge,
        InvestigationSettings(source='dataset', dataset_run_store=runs, dataset_store=source))
    created = service.create(dict(case_id=ctx['case_id'], source_mode='dataset', snapshot_ref=ctx['snapshot_ref']),
                             'test-analyst', str(uuid4()))
    attempt = created['attempt_id']
    archived = service.context(attempt)
    binding = service.binding(attempt)
    executor = ToolExecutor(knowledge.repository, attempt, 'unused', archived, knowledge,
                            binding['corpus_version'], binding['retrieval_version'], service.history_reader)
    items, _ = executor._history('sender')
    body = json.loads(items[0]['text'])
    assert body['events'][0]['direction'] == 'outgoing'
    assert body['totals']['outgoing']['Australian Dollar'] == '1.2300'
    assert 'SYNTH-BANK-A' not in items[0]['text']
    assert service.read(attempt)['budget']['provider_requests'] == 0
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    monkeypatch.setenv('INVESTIGATION_STORE', str(knowledge.repository.path))
    app = create_app()
    app.state.investigation_service = service
    with TestClient(app) as client:
        response = client.post('/api/investigation/runs',
                               json={k: ctx[k] for k in ('case_id', 'source_mode', 'snapshot_ref')},
                               headers={'Idempotency-Key': str(uuid4())})
        assert response.status_code == 202
        assert response.json()['source_mode'] == 'dataset'
        assert client.get('/api/investigation/attempts/' + attempt).status_code == 200
        missing = client.post('/api/investigation/runs',
                              json=dict(case_id='C' + 'f' * 32, source_mode='dataset', snapshot_ref=ctx['snapshot_ref']),
                              headers={'Idempotency-Key': str(uuid4())})
        assert missing.status_code == 404
        assert missing.json()['error']['code'] == 'case_not_found'
    with sqlite3.connect(runs) as db:
        db.execute("UPDATE active_run SET run_id='run_other'")
    assert service.context(attempt) == archived
    assert service.read(attempt)['budget']['provider_requests'] == 0


@pytest.mark.parametrize('change', ['dataset', 'incomplete', 'wrong_source'])
def test_changed_producer_binding_does_not_fall_back(published, change):
    ctx, runs, source = published
    reader = adapter(published)
    with sqlite3.connect(source if change == 'dataset' else runs) as db:
        if change == 'dataset':
            db.execute("UPDATE active_dataset SET version=?", ('dv_' + 'b' * 64,))
        elif change == 'incomplete':
            db.execute("UPDATE scored_runs SET status='staging'")
        else:
            db.execute("UPDATE scored_runs SET score_source='model'")
    with pytest.raises(ValueError, match='stale_snapshot'):
        reader.resolve(ctx['case_id'], ctx['snapshot_ref'])


def indexed_reader(published, tmp_path):
    from fraudlens.investigation.dataset import DatasetReader
    from fraudlens.investigation.history_index import prepare_history_index
    path = tmp_path / 'history-index.sqlite'
    result = prepare_history_index(published[2], path)
    return DatasetReader(published[1], published[2], 'rules',
                         history_index=path, history_index_sha256=result['index_sha256']), result, path


def test_indexed_history_exact_parity_privacy_and_source_immutable(published, tmp_path):
    ctx, _, source = published
    add_event(published, 99, '2025-12-24T10:00:00+00:00')
    add_event(published, 98, '2026-01-01T10:00:00+00:00')
    add_event(published, 97, sender_bank='OTHER', receiver_bank='OTHER')
    for number in range(1, 53):
        add_event(published, number, hidden_label='PRIVATE_CANARY_DO_NOT_COPY')
    add_event(published, 96, receiver_bank='SYNTH-BANK-A', receiver_account='001')
    before = source.read_bytes()
    legacy = adapter(published)
    context = legacy.resolve(ctx['case_id'], ctx['snapshot_ref'])
    reader, result, index = indexed_reader(published, tmp_path)
    assert reader.resolve(ctx['case_id'], ctx['snapshot_ref']) == context
    for side in ('sender', 'receiver'):
        for limit in (1, 50):
            assert reader.read(context, side, limit) == legacy.read(context, side, limit)
    assert result['row_count'] == 56
    assert source.read_bytes() == before
    assert b'PRIVATE_CANARY' not in index.read_bytes()


def test_indexed_available_empty_and_missing_source_are_distinct(published, tmp_path):
    ctx, _, source = published
    add_event(published, 99, '2025-12-24T10:00:00+00:00', sender_account='OTHER', receiver_account='OTHER')
    reader, _, _ = indexed_reader(published, tmp_path)
    context = reader.resolve(ctx['case_id'], ctx['snapshot_ref'])
    history = reader.read(context, 'sender')
    assert history['availability'] == 'available' and history['eligible_count'] == 0
    reader.dataset_store = source.with_name('absent.sqlite')
    history = reader.read(context, 'sender')
    assert history['availability'] == 'unavailable' and history['eligible_count'] is None
    assert not reader.dataset_store.exists()


@pytest.mark.parametrize('change', ['source', 'index', 'index_hash'])
def test_index_changed_binding_fails_closed(published, tmp_path, change):
    from fraudlens.investigation.dataset import DatasetReader
    ctx, runs, source = published
    add_event(published, 1)
    reader, result, index = indexed_reader(published, tmp_path)
    context = reader.resolve(ctx['case_id'], ctx['snapshot_ref'])
    if change == 'source':
        add_event(published, 2)
    elif change == 'index':
        with index.open('ab') as out:
            out.write(b'changed')
    else:
        with pytest.raises(ValueError):
            bad = DatasetReader(runs, source, 'rules', history_index=index,
                                history_index_sha256='f' * 64)
            bad.resolve(ctx['case_id'], ctx['snapshot_ref'])
        return
    with pytest.raises(ValueError, match='stale_snapshot'):
        reader.read(context, 'sender')
    validate('InvestigationContext', context)


def test_index_preparation_refuses_existing_output_and_incomplete_source(published, tmp_path):
    from fraudlens.investigation.history_index import prepare_history_index
    target = tmp_path / 'index.sqlite'
    target.write_bytes(b'preserve existing')
    with pytest.raises((ValueError, FileExistsError)):
        prepare_history_index(published[2], target)
    assert target.read_bytes() == b'preserve existing'
    with sqlite3.connect(published[2]) as db:
        db.execute("UPDATE dataset_versions SET status='staged'")
    with pytest.raises(ValueError):
        prepare_history_index(published[2], tmp_path / 'not-published.sqlite')


@pytest.mark.parametrize('kwargs', [
    {'dataset_history_index': 'index.sqlite'},
    {'dataset_history_index_sha256': 'a' * 64},
    {'dataset_history_index': 'index.sqlite', 'dataset_history_index_sha256': 'bad'},
])
def test_history_index_private_settings_require_pair(kwargs):
    from fraudlens.investigation.settings import InvestigationSettings
    with pytest.raises(ValueError):
        InvestigationSettings(source='dataset', **kwargs)


def test_history_index_private_settings_pair_is_supported(tmp_path):
    from fraudlens.investigation.settings import InvestigationSettings
    cfg = InvestigationSettings(source='dataset', dataset_history_index=tmp_path / 'index.sqlite',
                                dataset_history_index_sha256='a' * 64)
    assert cfg.dataset_history_index.is_absolute()


def test_indexed_runtime_never_scans_operational_json(published, tmp_path, monkeypatch):
    from contextlib import contextmanager
    ctx, _, _ = published
    add_event(published, 1)
    reader, _, _ = indexed_reader(published, tmp_path)
    original = reader.connection

    @contextmanager
    def no_operational_scan(path):
        with original(path) as db:
            db.set_authorizer(lambda action, table, *args:
                              sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_READ
                              and table == 'operational_events' else sqlite3.SQLITE_OK)
            yield db

    monkeypatch.setattr(reader, 'connection', no_operational_scan)
    context = reader.resolve(ctx['case_id'], ctx['snapshot_ref'])
    assert reader.read(context, 'sender')['eligible_count'] == 1


def test_index_is_read_only_and_wrong_dataset_pin_rejected(published, tmp_path):
    from contextlib import closing

    from fraudlens.investigation.dataset import DatasetReader
    from fraudlens.investigation.history_index import file_digest, read_connection
    ctx, runs, source = published
    add_event(published, 1)
    _, _, index = indexed_reader(published, tmp_path)
    with read_connection(index, {'history_events'}) as db:
        with pytest.raises(sqlite3.OperationalError):
            db.execute('DELETE FROM history_events')
    with closing(sqlite3.connect(index)) as db:
        metadata = json.loads(db.execute('SELECT content FROM history_source').fetchone()[0])
        metadata['dataset_version'] = 'dv_' + 'b' * 64
        db.execute('UPDATE history_source SET content=?', (json.dumps(metadata),))
        db.commit()
    reader = DatasetReader(runs, source, 'rules', history_index=index,
                           history_index_sha256=file_digest(index))
    with pytest.raises(ValueError, match='stale_snapshot'):
        reader.resolve(ctx['case_id'], ctx['snapshot_ref'])


def test_history_index_cli_and_service_wiring(published, tmp_path):
    from fraudlens.investigation.cli import main
    from fraudlens.investigation.history_index import file_digest
    from fraudlens.investigation.settings import InvestigationSettings
    from fraudlens.investigation.workflow import InvestigationService
    ctx, runs, source = published
    add_event(published, 1)
    index = tmp_path / 'cli-index.sqlite'
    assert main(['prepare-history-index', '--source-store', str(source), '--output', str(index)]) == 0
    settings = InvestigationSettings(source='dataset', dataset_run_store=runs,
                                     dataset_store=source, dataset_history_index=index,
                                     dataset_history_index_sha256=file_digest(index))
    service = InvestigationService(None, None, settings)
    context = service.context_reader.resolve(ctx['case_id'], 'dataset', ctx['snapshot_ref'])
    assert service.history_reader.read(context, 'sender')['eligible_count'] == 1
    before = index.read_bytes()
    assert main(['prepare-history-index', '--source-store', str(source), '--output', str(index)]) == 2
    assert index.read_bytes() == before


def test_archived_attempt_read_does_not_require_source_or_index(published, tmp_path, knowledge_factory):
    from uuid import uuid4

    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.settings import InvestigationSettings
    from fraudlens.investigation.workflow import InvestigationService
    ctx, runs, source = published
    add_event(published, 1)
    _, result, index = indexed_reader(published, tmp_path)
    knowledge = KnowledgeStore(tmp_path / 'investigations.sqlite')
    knowledge.publish(knowledge_factory())
    knowledge.save_configuration(json.loads(
        (ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
    settings = InvestigationSettings(source='dataset', dataset_run_store=runs, dataset_store=source,
                                     dataset_history_index=index,
                                     dataset_history_index_sha256=result['index_sha256'])
    service = InvestigationService(knowledge.repository, knowledge, settings)
    created = service.create({key: ctx[key] for key in ('case_id', 'source_mode', 'snapshot_ref')},
                             'test-analyst', str(uuid4()))
    archived = service.context(created['attempt_id'])
    missing = InvestigationSettings(source='dataset', dataset_run_store=tmp_path / 'absent-run.sqlite',
                                    dataset_store=tmp_path / 'absent-source.sqlite',
                                    dataset_history_index=tmp_path / 'absent-index.sqlite',
                                    dataset_history_index_sha256=result['index_sha256'])
    reopened = InvestigationService(knowledge.repository, knowledge, missing)
    assert reopened.read(created['attempt_id']) == created
    assert reopened.context(created['attempt_id']) == archived
    assert not missing.dataset_store.exists() and not missing.dataset_history_index.exists()
