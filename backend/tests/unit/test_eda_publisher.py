"""Synthetic T246 preflight: strip the label token before parsing EDA facts."""

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from fraudlens.data.manifest import canonical_json_bytes

SOURCE = 'a' * 64


def _row(number: int, timestamp: str, label_token: bytes) -> bytes:
    row = {
        'amount_paid': '10.00', 'amount_received': '9.00',
        'is_laundering': 'PLACEHOLDER', 'payment_currency': 'USD',
        'payment_format': 'Wire', 'receiver_account': 'R1',
        'receiver_bank': 'B1', 'receiver_key': 'B1:R1',
        'receiving_currency': 'EUR', 'sender_account': 'S1',
        'sender_bank': 'B2', 'sender_key': 'B2:S1',
        'source_row_number': number, 'source_sha256': SOURCE,
        'timestamp': timestamp,
        'transaction_id': f'ibm-hi-small:{SOURCE}:row:{number}',
    }
    return (canonical_json_bytes(row).replace(b'"PLACEHOLDER"', label_token) + b'\n')


def _snapshot(root: Path, labels: tuple[bytes, bytes] = (b'not_json', b'also_not_json')):
    root.mkdir()
    accepted = (
        _row(1, '2022/09/01 00:00', labels[0])
        + _row(2, '2022/09/02 00:00', labels[1])
    )
    (root / 'accepted.jsonl').write_bytes(accepted)
    (root / 'rejections.jsonl').write_bytes(b'')
    manifest = {
        'complete': True, 'source_sha256': SOURCE, 'source_count': 2,
        'accepted_count': 2, 'rejected_count': 0, 'rejection_counts': {},
        'processed_files': [
            {'name': 'accepted.jsonl', 'size_bytes': len(accepted),
             'sha256': hashlib.sha256(accepted).hexdigest()},
            {'name': 'rejections.jsonl', 'size_bytes': 0,
             'sha256': hashlib.sha256(b'').hexdigest()},
        ],
    }
    manifest_bytes = canonical_json_bytes(manifest) + b'\n'
    (root / 'manifest.json').write_bytes(manifest_bytes)
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    (root / 'COMPLETE').write_text(manifest_sha + '\n')
    from fraudlens.eda.publisher import SnapshotExpectations

    return SnapshotExpectations(
        source_sha256=SOURCE, manifest_sha256=manifest_sha,
        accepted_sha256=hashlib.sha256(accepted).hexdigest(),
        accepted_size_bytes=len(accepted), source_count=2, warmup_count=1,
        coverage_start_utc='2022-09-01T00:00:00Z',
        coverage_end_utc='2022-09-02T00:00:00Z',
        warmup_end_exclusive_utc='2022-09-02T00:00:00Z',
        dataset_version='synthetic-v1',
    )


def test_invalid_json_label_tokens_are_never_parsed_or_exposed(tmp_path):
    from fraudlens.eda.publisher import prepare_eda_summary

    first = tmp_path / 'first'
    second = tmp_path / 'second'
    identity_a = _snapshot(first, (b'not_json', b'not_json_either'))
    identity_b = _snapshot(second, (b'0', b'1'))
    result_a = prepare_eda_summary(first, identity_a)
    result_b = prepare_eda_summary(second, identity_b)
    assert result_a == result_b
    encoded = result_a.model_dump_json()
    assert 'is_laundering' not in encoded
    assert 'not_json' not in encoded
    assert result_a.source_count == 2
    assert result_a.warmup_count == 1
    assert result_a.scoreable_count == 1


def test_manifest_and_accepted_hash_mismatch_stop_before_publication(tmp_path):
    from fraudlens.eda.publisher import prepare_eda_summary, publish_eda_summary

    root = tmp_path / 'snapshot'
    identity = _snapshot(root)
    target = tmp_path / 'eda.json'
    with pytest.raises(ValueError, match='manifest'):
        publish_eda_summary(root, replace(identity, manifest_sha256='b' * 64), target)
    assert not target.exists()
    (root / 'accepted.jsonl').write_bytes((root / 'accepted.jsonl').read_bytes() + b'\n')
    with pytest.raises(ValueError, match='snapshot|checksum|hash'):
        prepare_eda_summary(root, identity)
    assert not target.exists()


def test_identity_warmup_and_coverage_mismatches_stop(tmp_path):
    from fraudlens.eda.publisher import prepare_eda_summary

    root = tmp_path / 'snapshot'
    identity = _snapshot(root)
    with pytest.raises(ValueError, match='warm-up'):
        prepare_eda_summary(root, replace(identity, warmup_count=0))
    with pytest.raises(ValueError, match='coverage'):
        prepare_eda_summary(root, replace(identity,
                                          coverage_end_utc='2022-09-03T00:00:00Z'))


def test_published_summary_has_digest_and_is_readable_by_eda_service(tmp_path):
    from fraudlens.eda.publisher import publish_eda_summary
    from fraudlens.eda.service import EdaService

    root = tmp_path / 'snapshot'
    identity = _snapshot(root)
    target = tmp_path / 'eda.json'
    digest = publish_eda_summary(root, identity, target)
    assert digest == hashlib.sha256(target.read_bytes()).hexdigest()
    assert EdaService(target, digest, expected_source_sha256=SOURCE).load().source_count == 2
    assert 'is_laundering' not in target.read_text()
    with pytest.raises(ValueError, match='exists'):
        publish_eda_summary(root, identity, target)


def test_progress_callback_failure_does_not_publish(tmp_path):
    from fraudlens.eda.publisher import publish_eda_summary

    root = tmp_path / 'snapshot'
    identity = _snapshot(root)
    target = tmp_path / 'eda.json'

    def stop(_seen: int) -> None:
        raise MemoryError('synthetic limit')

    with pytest.raises(MemoryError, match='synthetic limit'):
        publish_eda_summary(root, identity, target, on_progress=stop,
                            progress_interval=1)
    assert not target.exists()
