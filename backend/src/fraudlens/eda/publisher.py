"""Prepare a trusted EDA summary from a verified snapshot without parsing labels.

This module performs no work at import time. The caller explicitly invokes the
offline publisher; the API only reads the resulting hash-pinned aggregate.
"""

import hashlib
import os
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from fraudlens.contracts import EdaSummary
from fraudlens.data.features import normalize_timestamp_utc
from fraudlens.data.manifest import (
    ManifestError,
    canonical_json_bytes,
    verify_completed_snapshot,
)
from fraudlens.data.training_input import _without_label
from fraudlens.eda import aggregate_eda


@dataclass(frozen=True, slots=True)
class SnapshotExpectations:
    source_sha256: str
    manifest_sha256: str
    accepted_sha256: str
    accepted_size_bytes: int
    source_count: int
    warmup_count: int
    coverage_start_utc: str
    coverage_end_utc: str
    warmup_end_exclusive_utc: str
    dataset_version: str


T210_EXPECTED = SnapshotExpectations(
    source_sha256='b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040',
    manifest_sha256='38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88',
    accepted_sha256='8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba',
    accepted_size_bytes=3_015_200_326,
    source_count=5_078_345,
    warmup_count=1_114_921,
    coverage_start_utc='2022-09-01T00:00:00Z',
    coverage_end_utc='2022-09-18T16:18:00Z',
    warmup_end_exclusive_utc='2022-09-02T00:00:00Z',
    dataset_version='ibm-hi-small-b19d39f5',
)


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _verified_manifest(root: Path, expected: SnapshotExpectations) -> dict:
    try:
        manifest_bytes = (root / 'manifest.json').read_bytes()
    except OSError:
        raise ValueError('snapshot manifest is unavailable') from None
    if _digest(manifest_bytes) != expected.manifest_sha256:
        raise ValueError('snapshot manifest identity mismatch')
    try:
        manifest = verify_completed_snapshot(root)
    except ManifestError:
        raise ValueError('completed snapshot verification failed') from None
    files = manifest.get('processed_files', [])
    accepted = next((item for item in files if item.get('name') == 'accepted.jsonl'), None)
    if (manifest.get('source_sha256') != expected.source_sha256
            or manifest.get('source_count') != expected.source_count
            or manifest.get('accepted_count') != expected.source_count
            or manifest.get('rejected_count') != 0
            or not isinstance(accepted, dict)
            or accepted.get('sha256') != expected.accepted_sha256
            or accepted.get('size_bytes') != expected.accepted_size_bytes):
        raise ValueError('snapshot source, count or accepted hash mismatch')
    return manifest


def prepare_eda_summary(
    snapshot_root: str | Path, expected: SnapshotExpectations = T210_EXPECTED,
    *, on_progress: Callable[[int], None] | None = None,
    progress_interval: int = 100_000,
) -> EdaSummary:
    """Verify exact snapshot bytes, then aggregate only decoded non-label facts."""
    if type(progress_interval) is not int or progress_interval < 1:
        raise ValueError('EDA progress interval must be positive')
    root = Path(snapshot_root)
    manifest = _verified_manifest(root, expected)
    warmup_end = normalize_timestamp_utc(expected.warmup_end_exclusive_utc)
    seen = 0
    observed_warmup = 0

    def facts():
        nonlocal seen, observed_warmup
        with (root / 'accepted.jsonl').open('rb') as stream:
            for raw in stream:
                # _without_label removes the token from bytes before json.loads.
                # Do not deserialize the whole accepted row or inspect the token.
                row = _without_label(raw)
                seen += 1
                if (row['source_row_number'] != seen
                        or row['source_sha256'] != expected.source_sha256
                        or row['transaction_id'] != (
                            f'ibm-hi-small:{expected.source_sha256}:row:{seen}')):
                    raise ValueError('accepted row identity or order mismatch')
                if normalize_timestamp_utc(row['timestamp']) < warmup_end:
                    observed_warmup += 1
                if on_progress is not None and seen % progress_interval == 0:
                    on_progress(seen)
                yield row

    summary = aggregate_eda(
        facts(), dataset_version=expected.dataset_version,
        source_sha256=expected.source_sha256,
        source_count=expected.source_count, rejected_count=0,
        warmup_count=expected.warmup_count,
        quality_counts=manifest.get('rejection_counts', {}),
    )
    if seen != expected.source_count or observed_warmup != expected.warmup_count:
        raise ValueError('accepted or warm-up aggregate count mismatch')
    if (summary.coverage_start_utc != expected.coverage_start_utc
            or summary.coverage_end_utc != expected.coverage_end_utc):
        raise ValueError('EDA UTC coverage mismatch')
    if on_progress is not None and seen % progress_interval:
        on_progress(seen)
    return summary


def publish_eda_summary(
    snapshot_root: str | Path, expected: SnapshotExpectations,
    destination: str | Path, *, on_progress: Callable[[int], None] | None = None,
    progress_interval: int = 100_000,
) -> str:
    """Publish only a completed bounded summary; never replace an existing one."""
    target = Path(destination)
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        raise ValueError('EDA destination exists or parent is unavailable')
    summary = prepare_eda_summary(
        snapshot_root, expected, on_progress=on_progress,
        progress_interval=progress_interval,
    )
    raw = canonical_json_bytes(summary.model_dump(mode='json')) + b'\n'
    if len(raw) > 1_048_576:
        raise ValueError('EDA summary exceeds API size limit')
    descriptor, temporary = tempfile.mkstemp(prefix='.eda-summary-', dir=target.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            raise ValueError('EDA destination exists') from None
    finally:
        Path(temporary).unlink(missing_ok=True)
    return _digest(raw)
