"""T011 RED: staged SQLite import invariants on authored versions only."""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

from fraudlens.data_import import HI_SMALL_HEADERS

_ROOT = Path(__file__).resolve().parents[3]
_MAPPING = _ROOT / 'data/mappings/ibm_hi_small_v1.json'


def _cli_source(tmp_path):
    source = tmp_path / 'HI-Small_Trans.csv'
    with source.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(HI_SMALL_HEADERS)
        writer.writerow(['2026/01/01 10:00', 'BANK_A', '0007', 'BANK_B', '0007',
                         '0.000001', 'Euro', '10.20', 'Euro', 'Wire', '1'])
        writer.writerow(['2026/01/01 10:01', 'BANK_A', '0008', 'BANK_B', '0009',
                         'bad', 'Euro', '10.20', 'Euro', 'Wire', '0'])
    return source, hashlib.sha256(source.read_bytes()).hexdigest()


def _cli_args(source, digest, store):
    return ['import', '--source', str(source), '--mapping', str(_MAPPING),
            '--namespace', 'synthetic:t015-cli-test', '--expected-sha256', digest,
            '--store', str(store)]


def _synthetic_binding(monkeypatch, digest, source):
    from fraudlens import pipeline_cli

    original = pipeline_cli._load_authorization
    reviewed = original(_MAPPING)
    assert reviewed['mapping_sha256'] == hashlib.sha256(_MAPPING.read_bytes()).hexdigest()
    monkeypatch.setattr(pipeline_cli, '_load_authorization', lambda _: {
        **reviewed, 'source_sha256': digest, 'source_size': source.stat().st_size,
        'namespace': 'synthetic:t015-cli-test'})
    return pipeline_cli


def test_cli_import_counts_replay_and_private_output(tmp_path, monkeypatch, capsys):
    source, digest = _cli_source(tmp_path)
    cli = _synthetic_binding(monkeypatch, digest, source)
    store_path = tmp_path / 'imports.sqlite'
    args = _cli_args(source, digest, store_path)
    assert cli.main(args) == 0
    output = capsys.readouterr()
    first = json.loads(output.out)
    assert {key: first[key] for key in ('source_records', 'event_valid', 'event_rejected',
                                       'label_eligible', 'label_ineligible', 'positives',
                                       'negatives')} == {
        'source_records': 2, 'event_valid': 1, 'event_rejected': 1,
        'label_eligible': 1, 'label_ineligible': 0, 'positives': 1, 'negatives': 0}
    assert first['repeated'] is False
    assert '0007' not in output.out + output.err
    assert 'HI-Small_Trans.csv' not in output.out + output.err
    assert cli.main(args) == 0
    second = json.loads(capsys.readouterr().out)
    assert second == {**first, 'repeated': True}
    store = store_type()(store_path)
    assert store.active_version() == first['dataset_version']
    assert store.event_count(first['dataset_version']) == 1
    assert store.case_count(first['dataset_version']) == 1
    store.close()


def test_cli_rejects_wrong_source_and_mapping_hash(tmp_path, monkeypatch, capsys):
    from fraudlens import pipeline_cli

    source, digest = _cli_source(tmp_path)
    cli = _synthetic_binding(monkeypatch, digest, source)
    args = _cli_args(source, digest, tmp_path / 'imports.sqlite')
    source.write_bytes(source.read_bytes() + b'\n')
    assert cli.main(args) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['source_mismatch']
    assert not (tmp_path / 'imports.sqlite').exists()
    monkeypatch.undo()
    changed = tmp_path / 'mapping.json'
    changed.write_bytes(_MAPPING.read_bytes() + b' ')
    with pytest.raises(ValueError, match='mapping_approval_mismatch'):
        pipeline_cli._load_authorization(changed)
    changed_args = _cli_args(source, digest, tmp_path / 'imports.sqlite')
    changed_args[changed_args.index('--mapping') + 1] = str(changed)
    assert pipeline_cli.main(changed_args) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == [
        'mapping_approval_mismatch']


def test_cli_interrupted_stage_retries_without_replacing_complete(tmp_path, monkeypatch, capsys):
    source, digest = _cli_source(tmp_path)
    cli = _synthetic_binding(monkeypatch, digest, source)
    args = _cli_args(source, digest, tmp_path / 'imports.sqlite')
    assert cli.main(args) == 0
    old = json.loads(capsys.readouterr().out)['dataset_version']
    changed = source.read_bytes().replace(b'Wire,1', b'Wire,')
    source.write_bytes(changed)
    new_digest = hashlib.sha256(changed).hexdigest()
    cli = _synthetic_binding(monkeypatch, new_digest, source)
    new_args = _cli_args(source, new_digest, tmp_path / 'imports.sqlite')
    original_rows = cli.iter_canonical_rows

    def interrupted(*a, **kw):
        yield next(original_rows(*a, **kw))
        raise ValueError('injected_stream_interruption')

    monkeypatch.setattr(cli, 'iter_canonical_rows', interrupted)
    assert cli.main(new_args) == 2
    assert json.loads(capsys.readouterr().out)['status'] == 'failed'
    store = store_type()(tmp_path / 'imports.sqlite')
    assert store.active_version() == old
    store.close()
    monkeypatch.setattr(cli, 'iter_canonical_rows', original_rows)
    assert cli.main(new_args) == 0
    new = json.loads(capsys.readouterr().out)['dataset_version']
    assert new != old
    store = store_type()(tmp_path / 'imports.sqlite')
    assert store.version_status(old) == 'complete'
    assert store.active_version() == new
    store.close()


@pytest.mark.parametrize('change_mode', ['in_place', 'replace', 'size_change'])
def test_cli_changed_source_between_hash_and_parse_cannot_complete(
        tmp_path, monkeypatch, capsys, change_mode):
    source, original_digest = _cli_source(tmp_path)
    cli = _synthetic_binding(monkeypatch, original_digest, source)
    store_path = tmp_path / 'imports.sqlite'
    assert cli.main(_cli_args(source, original_digest, store_path)) == 0
    old_version = json.loads(capsys.readouterr().out)['dataset_version']

    source.write_bytes(source.read_bytes().replace(b'Wire,1', b'Wire,0'))
    new_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    cli = _synthetic_binding(monkeypatch, new_digest, source)
    original_hash = cli._file_sha256

    def hash_then_change(path):
        result = original_hash(path)
        replacement_label = b'Wire,10' if change_mode == 'size_change' else b'Wire,1'
        changed = source.read_bytes().replace(b'Wire,0', replacement_label)
        if change_mode != 'replace':
            source.write_bytes(changed)
        else:
            replacement = tmp_path / 'replacement.csv'
            replacement.write_bytes(changed)
            os.replace(replacement, source)
        return result

    monkeypatch.setattr(cli, '_file_sha256', hash_then_change)
    assert cli.main(_cli_args(source, new_digest, store_path)) == 2
    failure = json.loads(capsys.readouterr().out)
    assert failure == {'status': 'failed', 'error_codes': ['source_mismatch']}
    store = store_type()(store_path)
    assert store.active_version() == old_version
    assert store.version_status(old_version) == 'complete'
    new_version = cli.derive_dataset_version(
        bytes.fromhex(new_digest), bytes.fromhex(cli._MAPPING_M),
        bytes.fromhex(cli._load_authorization(_MAPPING)['time_policy_sha256']))
    assert store.version_status(new_version) == 'failed'
    store.close()


def store_type():
    assert importlib.util.find_spec('fraudlens.data_store') is not None, (
        'T014 missing: versioned SQLite import repository')
    from fraudlens.data_store import DatasetStore
    return DatasetStore


def add_event(store, version, transaction_id):
    return store.add_event(version, transaction_id, case_id='C' + transaction_id[1:])


def test_interrupted_new_version_never_replaces_complete_version(tmp_path):
    store = store_type()(tmp_path / 'imports.sqlite')
    store.stage('dv_' + 'a' * 64, source_records=1)
    add_event(store, 'dv_' + 'a' * 64, 'D' + '1' * 32)
    store.complete('dv_' + 'a' * 64)
    store.activate('dv_' + 'a' * 64)
    store.stage('dv_' + 'b' * 64, source_records=2)
    add_event(store, 'dv_' + 'b' * 64, 'D' + '2' * 32)
    store.close()  # interruption before reconciliation and complete
    reopened = store_type()(tmp_path / 'imports.sqlite')
    assert reopened.active_version() == 'dv_' + 'a' * 64
    assert reopened.version_status('dv_' + 'b' * 64) != 'complete'


def test_reimport_same_complete_version_is_idempotent(tmp_path):
    store = store_type()(tmp_path / 'imports.sqlite')
    version = 'dv_' + 'a' * 64
    store.stage(version, source_records=1)
    add_event(store, version, 'D' + '1' * 32)
    store.complete(version)
    store.stage(version, source_records=1)
    add_event(store, version, 'D' + '1' * 32)
    store.complete(version)
    assert store.event_count(version) == 1
    assert store.case_count(version) == 1
    assert store.version_status(version) == 'complete'


def test_incomplete_row_accounting_blocks_completion(tmp_path):
    store = store_type()(tmp_path / 'imports.sqlite')
    version = 'dv_' + 'b' * 64
    store.stage(version, source_records=2)
    add_event(store, version, 'D' + '2' * 32)
    try:
        store.complete(version)
    except ValueError:
        pass
    assert store.version_status(version) != 'complete'


def test_unsupported_sqlite_schema_version_fails_closed(tmp_path):
    import sqlite3
    path = tmp_path / 'imports.sqlite'
    with sqlite3.connect(path) as connection:
        connection.execute('PRAGMA user_version = 999')
    store_class = store_type()
    import pytest
    with pytest.raises(ValueError, match='schema'):
        store_class(path)
    with sqlite3.connect(path) as connection:
        assert connection.execute('PRAGMA user_version').fetchone()[0] == 999


def test_operational_projection_cannot_read_private_labels(tmp_path):
    store = store_type()(tmp_path / 'imports.sqlite')
    version = 'dv_' + 'a' * 64
    transaction = 'D' + '1' * 32
    store.stage(version, source_records=1)
    add_event(store, version, transaction)
    store.add_private_label(version, transaction, value=1, status='eligible_positive')
    store.complete(version)
    public = store.operational_events(version)
    assert len(public) == 1
    assert not {'label', 'label_status', 'eligibility', 'target'} & vars(public[0]).keys()
    import pytest
    with pytest.raises(PermissionError):
        store.private_labels(version, role='operational')
    assert store.private_labels(version, role='offline_evaluation')[0].value == 1


def test_failed_new_version_can_retry_after_restart_without_touching_old_complete(tmp_path):
    path = tmp_path / 'imports.sqlite'
    store = store_type()(path)
    old, new = 'dv_' + 'a' * 64, 'dv_' + 'b' * 64
    store.stage(old, source_records=1)
    add_event(store, old, 'D' + '1' * 32)
    store.complete(old)
    store.activate(old)
    store.stage(new, source_records=2)
    add_event(store, new, 'D' + '2' * 32)
    store.fail(new, reason='injected parser failure after a valid row')
    store.close()
    reopened = store_type()(path)
    assert reopened.active_version() == old
    assert reopened.version_status(new) == 'failed'
    reopened.stage(new, source_records=2)
    add_event(reopened, new, 'D' + '2' * 32)
    add_event(reopened, new, 'D' + '3' * 32)
    reopened.complete(new)
    assert reopened.event_count(new) == 2
    assert reopened.event_count(old) == 1
    assert reopened.active_version() == old  # completion does not auto-activate


def test_parser_exception_during_batch_does_not_publish_partial_version(tmp_path):
    store = store_type()(tmp_path / 'imports.sqlite')
    version = 'dv_' + 'b' * 64
    store.stage(version, source_records=3)

    def broken_rows():
        yield ('D' + '1' * 32, 'C' + '1' * 32)
        raise ValueError('injected malformed CSV after first event')

    import pytest
    with pytest.raises(ValueError, match='injected malformed CSV'):
        store.ingest(version, broken_rows())
    assert store.version_status(version) == 'failed'
    assert store.active_version() is None
    assert store.complete_report(version) is None
