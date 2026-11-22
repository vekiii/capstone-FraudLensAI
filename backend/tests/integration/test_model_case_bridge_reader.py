"""Read-only bridge rejects stale, corrupt, unauthorized and partial sources."""

import json
import sqlite3
from pathlib import Path

import pytest

from fraudlens.bridge_reader import BridgeNotFound, BridgeReader, BridgeUnavailable
from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.investigation.context import CaseContextReader

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def published(tmp_path):
    contract = ROOT / 'specs/003-ai-investigation/contracts/examples'
    binding = json.loads((contract / 'model-case-binding-v1.json').read_text())
    context = json.loads((contract / 'model-context-v2.json').read_text())
    runs, source = tmp_path / 'runs.sqlite', tmp_path / 'dataset.sqlite'
    with sqlite3.connect(runs) as db:
        db.executescript('''CREATE TABLE scored_runs(run_id TEXT,dataset_version TEXT,score_source TEXT,scorer_version TEXT,status TEXT);
          CREATE TABLE active_run(singleton INTEGER,run_id TEXT);
          CREATE TABLE scored_assessments(run_id TEXT,case_id TEXT,transaction_json TEXT,assessment_json TEXT,alert INTEGER);
          CREATE TABLE bridge_crosswalk(canonical_id TEXT PRIMARY KEY,case_id TEXT UNIQUE,transaction_id TEXT UNIQUE,binding_json TEXT);''')
        db.execute('INSERT INTO scored_runs VALUES(?,?,?,?,?)', (binding['snapshot_ref'], binding['dataset_version'], 'model',
            'lightgbm-'+binding['model_sha256'][:12], 'completed'))
        db.execute('INSERT INTO active_run VALUES(1,?)', (binding['snapshot_ref'],))
        db.execute('INSERT INTO scored_assessments VALUES(?,?,?,?,1)', (binding['snapshot_ref'], binding['case_id'],
            json.dumps(context['source_payload']['transaction']), json.dumps(context['source_payload']['risk_assessment'])))
        db.execute('INSERT INTO bridge_crosswalk VALUES(?,?,?,?)', (binding['canonical_transaction_id'], binding['case_id'],
            binding['transaction_id'], json.dumps(binding)))
    with sqlite3.connect(source) as db:
        db.executescript('''CREATE TABLE dataset_versions(id TEXT,status TEXT,rejected_records INTEGER);
          CREATE TABLE active_dataset(singleton INTEGER,version TEXT);
          CREATE TABLE operational_events(version TEXT,transaction_id TEXT,case_id TEXT,payload_json TEXT);
          CREATE TABLE private_evaluation_labels(secret TEXT);
          INSERT INTO private_evaluation_labels VALUES('LABEL_CANARY');''')
        db.execute('INSERT INTO dataset_versions VALUES(?,?,1)', (binding['dataset_version'], 'complete'))
        db.execute('INSERT INTO active_dataset VALUES(1,?)', (binding['dataset_version'],))
        base = dict(event_time_utc='2022-09-06T11:59:00+00:00', event_time_raw='2022/09/06 11:59',
            time_basis='assumed_utc_for_synthetic_benchmark', sender_bank='SYNTH-BANK-A', sender_account='001',
            receiver_bank='SYNTH-BANK-B', receiver_account='002', paid_amount='1.2300', paid_currency='Australian Dollar',
            received_amount='0.000001', received_currency='Bitcoin')
        for n, when in enumerate(('2022-09-06T11:59:00+00:00','2022-09-06T12:00:00+00:00','2022-08-30T11:59:00+00:00')):
            event = {**base, 'event_time_utc': when}
            db.execute('INSERT INTO operational_events VALUES(?,?,?,?)', (binding['dataset_version'],
                'D'+f'{n+1:032x}', None, json.dumps(event)))
    manifest = dict(bridge_version=1,status='complete',source_sha256=binding['source_sha256'],
        accepted_sha256='8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba',
        predictions_sha256='99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7',
        model_sha256=binding['model_sha256'],model_manifest_sha256='c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45',
        feature_manifest_sha256=binding['feature_manifest_sha256'],threshold=binding['threshold'],
        run_id=binding['snapshot_ref'],dataset_version=binding['dataset_version'],alert_count=1,
        runs_sha256=sha256_file(runs),dataset_sha256=sha256_file(source))
    (tmp_path/'manifest.json').write_bytes(canonical_json_bytes(manifest)+b'\n')
    (tmp_path/'COMPLETE').write_text(sha256_file(tmp_path/'manifest.json')+'\n')
    return tmp_path,binding


def test_context_history_strict_cutoff_incomplete_and_no_labels(published):
    root,binding = published
    reader=BridgeReader(root)
    ctx=CaseContextReader(dataset_reader=reader).resolve(binding['case_id'],'dataset',binding['snapshot_ref'])
    assert ctx['history']['coverage']=='incomplete'
    history=reader.read(ctx,'sender')
    assert history['availability']=='available' and history['coverage']=='incomplete'
    assert history['eligible_count']==1 and history['events'][0]['amount']=='1.2300'
    assert 'LABEL_CANARY' not in json.dumps(ctx)+json.dumps(history)


def test_unknown_stale_and_missing_never_fall_back_to_fixture(published):
    root,binding=published
    reader=BridgeReader(root)
    with pytest.raises(BridgeNotFound):
        reader.binding(binding['canonical_transaction_id'][:-1]+'9')
    with pytest.raises(ValueError,match='stale_snapshot'):
        CaseContextReader(dataset_reader=reader).resolve(binding['case_id'],'dataset','run_other')
    (root/'COMPLETE').unlink()
    with pytest.raises(BridgeUnavailable):
        reader.resolve(binding['case_id'],None)


def test_changed_binding_and_private_field_fail_closed(published):
    root,binding=published
    for changed in ({**binding,'case_id':'C'+'0'*32}, {**binding,'is_laundering':1}):
        with sqlite3.connect(root/'runs.sqlite') as db:
            db.execute('UPDATE bridge_crosswalk SET binding_json=?',(json.dumps(changed),))
        manifest=json.loads((root/'manifest.json').read_text())
        manifest['runs_sha256']=sha256_file(root/'runs.sqlite')
        (root/'manifest.json').write_bytes(canonical_json_bytes(manifest)+b'\n')
        (root/'COMPLETE').write_text(sha256_file(root/'manifest.json')+'\n')
        with pytest.raises(ValueError):
            BridgeReader(root).resolve(binding['case_id'],None)


def test_duplicate_case_identity_rejected_by_unique_index(published):
    root,binding=published
    with sqlite3.connect(root/'runs.sqlite') as db, pytest.raises(sqlite3.IntegrityError):
        db.execute('INSERT INTO bridge_crosswalk VALUES(?,?,?,?)',
            (binding['canonical_transaction_id']+':copy',binding['case_id'],'D'+'0'*32,json.dumps(binding)))


def test_wrong_history_cutoff_and_label_table_access_denied(published):
    root,binding=published
    with sqlite3.connect(root/'runs.sqlite') as db:
        row=db.execute('SELECT assessment_json FROM scored_assessments').fetchone()
        assessment=json.loads(row[0])
        assessment['history_cutoff_exclusive_at']='2022-09-06T11:59:00Z'
        db.execute('UPDATE scored_assessments SET assessment_json=?',(json.dumps(assessment),))
    manifest=json.loads((root/'manifest.json').read_text())
    manifest['runs_sha256']=sha256_file(root/'runs.sqlite')
    (root/'manifest.json').write_bytes(canonical_json_bytes(manifest)+b'\n')
    (root/'COMPLETE').write_text(sha256_file(root/'manifest.json')+'\n')
    with pytest.raises(ValueError):
        BridgeReader(root).resolve(binding['case_id'],None)
    reader=BridgeReader(root).reader
    with reader.connection(root/'dataset.sqlite') as db, pytest.raises(sqlite3.DatabaseError):
        db.execute('SELECT secret FROM private_evaluation_labels').fetchone()


@pytest.mark.parametrize('field', ['accepted_sha256', 'predictions_sha256', 'model_sha256',
                                  'feature_manifest_sha256'])
def test_rehashed_manifest_cannot_substitute_frozen_inputs(published, field):
    root, binding = published
    manifest = json.loads((root/'manifest.json').read_text())
    manifest[field] = '0' * 64
    (root/'manifest.json').write_bytes(canonical_json_bytes(manifest)+b'\n')
    (root/'COMPLETE').write_text(sha256_file(root/'manifest.json')+'\n')
    with pytest.raises(BridgeUnavailable):
        BridgeReader(root).resolve(binding['case_id'], None)


def _reseal(root, database):
    manifest = json.loads((root/'manifest.json').read_text())
    manifest['runs_sha256' if database == 'runs' else 'dataset_sha256'] = sha256_file(root/(database+'.sqlite'))
    (root/'manifest.json').write_bytes(canonical_json_bytes(manifest)+b'\n')
    (root/'COMPLETE').write_text(sha256_file(root/'manifest.json')+'\n')


def test_stale_active_run_and_score_mismatch_fail_closed(published):
    root, binding = published
    with sqlite3.connect(root/'runs.sqlite') as db:
        db.execute('UPDATE active_run SET run_id=?', ('run_other',))
    _reseal(root, 'runs')
    with pytest.raises(ValueError, match='stale_snapshot'):
        BridgeReader(root).resolve(binding['case_id'], None)
    with sqlite3.connect(root/'runs.sqlite') as db:
        db.execute('UPDATE active_run SET run_id=?', (binding['snapshot_ref'],))
        assessment = json.loads(db.execute('SELECT assessment_json FROM scored_assessments').fetchone()[0])
        assessment['score'] = 0.9
        db.execute('UPDATE scored_assessments SET assessment_json=?', (json.dumps(assessment),))
    _reseal(root, 'runs')
    with pytest.raises(ValueError, match='Binding/assessment mismatch'):
        BridgeReader(root).resolve(binding['case_id'], None)


def test_available_empty_history_is_distinct_from_missing_source(published):
    root, binding = published
    with sqlite3.connect(root/'dataset.sqlite') as db:
        db.execute("UPDATE operational_events SET payload_json=json_set(payload_json, '$.sender_bank', 'OTHER', '$.receiver_bank', 'OTHER')")
    _reseal(root, 'dataset')
    reader = BridgeReader(root)
    ctx = reader.resolve(binding['case_id'], binding['snapshot_ref'])
    history = reader.read(ctx, 'sender')
    assert history['availability'] == 'available' and history['eligible_count'] == 0
    assert history['events'] == [] and history['coverage'] == 'incomplete'
    (root/'dataset.sqlite').unlink()
    with pytest.raises(BridgeUnavailable):
        reader.resolve(binding['case_id'], binding['snapshot_ref'])
