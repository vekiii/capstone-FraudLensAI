"""Synthetic RED contracts for restartable dataset preparation (T207).

The runner contract exercised here is ``run_pipeline(rows, *, staging_dir,
output_dir, source_sha256, config_hash, chunk_size, min_free_bytes, resume)``.
Only fabricated rows and temporary directories are used.
"""

import importlib
import json
import shutil

import pytest

from fraudlens.data.manifest import ManifestError, verify_completed_snapshot
from fraudlens.data.source import stable_transaction_id

SOURCE_SHA256 = 'b' * 64
CONFIG_HASH = 'c' * 64


def pipeline_module():
    """Load the pipeline boundary to be implemented by T208."""
    try:
        module = importlib.import_module('fraudlens.data.pipeline')
    except ModuleNotFoundError as error:
        if error.name != 'fraudlens.data.pipeline':
            raise
        pytest.fail('Missing Feature 002 resumable pipeline (T208)', pytrace=False)
    assert callable(getattr(module, 'run_pipeline', None)), 'Missing run_pipeline boundary'
    return module


def synthetic_rows(count=4):
    """Create valid fabricated records with stable source-row identities."""
    return [
        {
            'source_sha256': SOURCE_SHA256,
            'source_row_number': number,
            'transaction_id': stable_transaction_id(SOURCE_SHA256, number),
            'timestamp': f'2022/09/01 00:{number:02d}',
            'sender_bank': '0007',
            'sender_account': f'0000{number:05d}',
            'receiver_bank': '0012',
            'receiver_account': f'0000{number + 10:05d}',
            'amount_received': '10.00',
            'receiving_currency': 'EUR',
            'amount_paid': '10.00',
            'payment_currency': 'EUR',
            'payment_format': 'Wire',
            'is_laundering': '0',
        }
        for number in range(1, count + 1)
    ]


def run(rows, tmp_path, *, resume=False, min_free_bytes=0):
    return pipeline_module().run_pipeline(
        rows,
        staging_dir=tmp_path / 'staging',
        output_dir=tmp_path / 'snapshot',
        source_sha256=SOURCE_SHA256,
        config_hash=CONFIG_HASH,
        chunk_size=2,
        min_free_bytes=min_free_bytes,
        resume=resume,
    )


def interrupted_rows(rows, stop_before_index=2):
    """Yield one chunk, then simulate process interruption mid-source."""
    yield from rows[:stop_before_index]
    raise KeyboardInterrupt


def test_interruption_keeps_checkpoint_but_never_publishes_partial_snapshot(tmp_path):
    with pytest.raises(KeyboardInterrupt):
        run(interrupted_rows(synthetic_rows()), tmp_path)

    staging_dir = tmp_path / 'staging'
    output_dir = tmp_path / 'snapshot'
    assert staging_dir.exists()
    assert any(staging_dir.rglob('*')), 'Expected a committed checkpoint for the completed chunk'
    assert not (output_dir / 'manifest.json').exists()
    assert not (output_dir / 'COMPLETE').exists()


def test_resume_revalidates_staged_chunk_and_rejects_checkpoint_mismatch(tmp_path):
    with pytest.raises(KeyboardInterrupt):
        run(interrupted_rows(synthetic_rows()), tmp_path)

    staged_files = [
        path for path in (tmp_path / 'staging').rglob('*')
        if path.is_file() and path.name != 'checkpoint.json'
    ]
    assert staged_files, 'Interrupted run should leave at least one staged chunk'
    staged_files[0].write_bytes(b'corrupted synthetic checkpoint')

    with pytest.raises(pipeline_module().CheckpointMismatchError):
        run(synthetic_rows(), tmp_path, resume=True)
    assert not (tmp_path / 'snapshot' / 'COMPLETE').exists()


def test_disk_exhaustion_stops_before_publishing_or_consuming_rows(tmp_path, monkeypatch):
    module = pipeline_module()
    usage_type = type(shutil.disk_usage(tmp_path))
    monkeypatch.setattr(
        module.shutil,
        'disk_usage',
        lambda _path: usage_type(total=100, used=95, free=5),
    )

    consumed = []

    def tracked_rows():
        for row in synthetic_rows():
            consumed.append(row['source_row_number'])
            yield row

    with pytest.raises(module.DiskSpaceError):
        module.run_pipeline(
            tracked_rows(),
            staging_dir=tmp_path / 'staging',
            output_dir=tmp_path / 'snapshot',
            source_sha256=SOURCE_SHA256,
            config_hash=CONFIG_HASH,
            chunk_size=2,
            min_free_bytes=10,
            resume=False,
        )

    assert consumed == []
    assert not (tmp_path / 'snapshot' / 'COMPLETE').exists()


def test_resume_matches_uninterrupted_result_without_duplicate_rows(tmp_path):
    rows = synthetic_rows()
    with pytest.raises(KeyboardInterrupt):
        run(interrupted_rows(rows), tmp_path)

    resumed = run(rows, tmp_path, resume=True)
    accepted_path = resumed.output_dir / 'accepted.jsonl'
    accepted = [
        json.loads(line)
        for line in accepted_path.read_text(encoding='utf-8').splitlines()
    ]
    row_numbers = [row['source_row_number'] for row in accepted]

    assert resumed.source_count == 4
    assert resumed.accepted_count == 4
    assert resumed.rejected_count == 0
    assert row_numbers == [1, 2, 3, 4]
    assert len(row_numbers) == len(set(row_numbers))

    manifest = json.loads((tmp_path / 'snapshot' / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['source_sha256'] == SOURCE_SHA256
    assert manifest['config_hash'] == CONFIG_HASH
    assert manifest['source_count'] == manifest['accepted_count'] + manifest['rejected_count']
    assert manifest['complete'] is True
    assert (tmp_path / 'snapshot' / 'COMPLETE').is_file()
    assert verify_completed_snapshot(resumed.output_dir)['complete'] is True

    uninterrupted_root = tmp_path / 'uninterrupted'
    uninterrupted_root.mkdir()
    uninterrupted = run(rows, uninterrupted_root)
    for name in ('accepted.jsonl', 'rejections.jsonl', 'manifest.json', 'COMPLETE'):
        assert (resumed.output_dir / name).read_bytes() == (uninterrupted.output_dir / name).read_bytes()

    accepted_path.write_bytes(accepted_path.read_bytes() + b'corruption\n')
    with pytest.raises(ManifestError, match='checksum'):
        verify_completed_snapshot(resumed.output_dir)
