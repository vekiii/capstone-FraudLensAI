"""Bounded, resumable staging for deterministic canonical dataset chunks.

The runner accepts an iterable so synthetic interruption and recovery can be
tested without opening the real source. Callers should supply source rows from
the verified source reader and a configuration hash for all processing options.
"""

import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fraudlens.data.manifest import (
    MANIFEST_VERSION,
    ManifestError,
    atomic_write_bytes,
    atomic_write_json,
    build_manifest,
    canonical_json_bytes,
    read_json,
    sha256_bytes,
    sha256_file,
    validate_checkpoint,
)
from fraudlens.data.validation import validate_rows

_CHECKPOINT_NAME = 'checkpoint.json'
_CHUNK_PATTERN = 'chunk-{index:08d}.json'


class PipelineError(RuntimeError):
    """Controlled failure while staging, verifying, or publishing a snapshot."""


class CheckpointMismatchError(PipelineError):
    """A staged checkpoint is corrupt or incompatible with this run/source."""


class DiskSpaceError(PipelineError):
    """The configured free-space reserve is unavailable."""


class SnapshotExistsError(PipelineError):
    """Refuse to overwrite an already published snapshot."""


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Count-only result; transaction and rejection records live in the snapshot."""

    source_count: int
    accepted_count: int
    rejected_count: int
    output_dir: Path


def _row_bytes(row: Mapping[str, object]) -> bytes:
    try:
        return canonical_json_bytes(dict(row))
    except (TypeError, ValueError):
        raise PipelineError('Source row cannot be encoded as deterministic JSON.') from None


def _input_chunk_hash(rows: list[Mapping[str, object]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(_row_bytes(row))
        digest.update(b'\n')
    return digest.hexdigest()


def _write_chunk(staging_dir: Path, index: int, rows: list[Mapping[str, object]]) -> dict[str, Any]:
    report = validate_rows(rows)
    payload = {
        'chunk_index': index,
        'source_count': report.source_count,
        'accepted_count': report.accepted_count,
        'rejected_count': report.rejected_count,
        'accepted_rows': list(report.accepted_rows),
        'rejections': [
            {'source_row_number': item.source_row_number, 'reason_code': item.reason_code}
            for item in report.rejections
        ],
    }
    reason_counts = Counter(item.reason_code for item in report.rejections)
    payload['rejection_counts'] = dict(sorted(reason_counts.items()))
    chunk_bytes = canonical_json_bytes(payload) + b'\n'
    destination = staging_dir / _CHUNK_PATTERN.format(index=index)
    atomic_write_bytes(destination, chunk_bytes)
    return {
        'chunk_index': index,
        'file_name': destination.name,
        'source_count': report.source_count,
        'accepted_count': report.accepted_count,
        'rejected_count': report.rejected_count,
        'rejection_counts': dict(sorted(reason_counts.items())),
        'input_sha256': _input_chunk_hash(rows),
        'output_sha256': sha256_bytes(chunk_bytes),
    }


def _read_verified_chunk(staging_dir: Path, metadata: Mapping[str, Any]) -> dict[str, Any]:
    name = metadata.get('file_name')
    if not isinstance(name, str) or Path(name).name != name:
        raise CheckpointMismatchError('Checkpoint chunk path is invalid.')
    path = staging_dir / name
    try:
        payload = path.read_bytes()
    except OSError:
        raise CheckpointMismatchError('Checkpoint chunk is missing or unreadable.') from None
    if sha256_bytes(payload) != metadata.get('output_sha256'):
        raise CheckpointMismatchError('Checkpoint chunk checksum does not match.')
    try:
        chunk = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise CheckpointMismatchError('Checkpoint chunk JSON is malformed.') from None
    if not isinstance(chunk, dict):
        raise CheckpointMismatchError('Checkpoint chunk must be a JSON object.')
    if chunk.get('chunk_index') != metadata.get('chunk_index'):
        raise CheckpointMismatchError('Checkpoint chunk index does not match.')
    for field in ('source_count', 'accepted_count', 'rejected_count'):
        if chunk.get(field) != metadata.get(field):
            raise CheckpointMismatchError('Checkpoint chunk counts do not match.')
    if chunk['accepted_count'] + chunk['rejected_count'] != chunk['source_count']:
        raise CheckpointMismatchError('Checkpoint chunk row counts do not reconcile.')
    if len(chunk.get('accepted_rows', [])) != chunk['accepted_count']:
        raise CheckpointMismatchError('Checkpoint accepted rows do not match their count.')
    if len(chunk.get('rejections', [])) != chunk['rejected_count']:
        raise CheckpointMismatchError('Checkpoint rejection rows do not match their count.')
    counts = Counter(
        item.get('reason_code') for item in chunk['rejections'] if isinstance(item, dict)
    )
    if dict(sorted(counts.items())) != metadata.get('rejection_counts'):
        raise CheckpointMismatchError('Checkpoint rejection reasons do not match.')
    if chunk.get('rejection_counts') != metadata.get('rejection_counts'):
        raise CheckpointMismatchError('Checkpoint rejection counts do not match.')
    return chunk


def _load_checkpoint(staging_dir: Path, source_sha256: str, config_hash: str) -> dict[str, Any]:
    try:
        checkpoint = read_json(staging_dir / _CHECKPOINT_NAME)
        checkpoint = validate_checkpoint(
            checkpoint,
            source_sha256=source_sha256,
            config_hash=config_hash,
        )
        for expected_index, metadata in enumerate(checkpoint['chunks']):
            if not isinstance(metadata, dict) or metadata.get('chunk_index') != expected_index:
                raise ManifestError('Checkpoint chunk order is malformed.')
            _read_verified_chunk(staging_dir, metadata)
        return checkpoint
    except ManifestError as error:
        raise CheckpointMismatchError(str(error)) from None


def _check_free_space(path: Path, minimum: int) -> None:
    if shutil.disk_usage(path).free < minimum:
        raise DiskSpaceError('Available disk space is below the configured reserve.')


def _append_chunk_outputs(
    staging_dir: Path,
    chunks: list[dict[str, Any]],
    accepted_stream: Any,
    rejection_stream: Any,
) -> None:
    for metadata in chunks:
        chunk = _read_verified_chunk(staging_dir, metadata)
        for row in chunk['accepted_rows']:
            accepted_stream.write(canonical_json_bytes(row) + b'\n')
        for rejection in chunk['rejections']:
            rejection_stream.write(canonical_json_bytes(rejection) + b'\n')


def _atomic_publish(
    *,
    staging_dir: Path,
    output_dir: Path,
    checkpoint: dict[str, Any],
) -> None:
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary_dir = Path(tempfile.mkdtemp(prefix=f'.{output_dir.name}.partial-', dir=output_dir.parent))
    try:
        accepted_path = temporary_dir / 'accepted.jsonl'
        rejection_path = temporary_dir / 'rejections.jsonl'
        with accepted_path.open('wb') as accepted_stream, rejection_path.open('wb') as rejection_stream:
            _append_chunk_outputs(staging_dir, checkpoint['chunks'], accepted_stream, rejection_stream)
            accepted_stream.flush()
            os.fsync(accepted_stream.fileno())
            rejection_stream.flush()
            os.fsync(rejection_stream.fileno())

        output_files = []
        for path in (accepted_path, rejection_path):
            output_files.append({
                'name': path.name,
                'size_bytes': path.stat().st_size,
                'sha256': sha256_file(path),
            })
        manifest = build_manifest(
            source_sha256=checkpoint['source_sha256'],
            config_hash=checkpoint['config_hash'],
            source_count=checkpoint['source_count'],
            accepted_count=checkpoint['accepted_count'],
            rejected_count=checkpoint['rejected_count'],
            rejection_counts=checkpoint['rejection_counts'],
            checkpoints=checkpoint['chunks'],
            processed_files=output_files,
        )
        manifest_bytes = canonical_json_bytes(manifest) + b'\n'
        atomic_write_bytes(temporary_dir / 'manifest.json', manifest_bytes)
        atomic_write_bytes(
            temporary_dir / 'COMPLETE',
            (sha256_bytes(manifest_bytes) + '\n').encode('ascii'),
        )
        if output_dir.exists():
            raise SnapshotExistsError('Output snapshot path already exists; refusing overwrite.')
        os.replace(temporary_dir, output_dir)
    finally:
        if temporary_dir.exists():
            shutil.rmtree(temporary_dir)


def run_pipeline(
    rows: Iterable[Mapping[str, object]],
    *,
    staging_dir: str | Path,
    output_dir: str | Path,
    source_sha256: str,
    config_hash: str,
    chunk_size: int,
    min_free_bytes: int,
    resume: bool,
) -> PipelineResult:
    """Validate and stage rows in bounded chunks, then atomically publish a snapshot.

    Resume replays the source iterable from its beginning, verifies each staged
    input chunk against its original row hash, and validates every staged output
    checksum before appending new work. Checkpoints are committed only after a
    complete chunk has been atomically written. An interrupted iterable leaves
    committed chunks available for recovery but never publishes a snapshot.
    """
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError('Chunk size must be a positive integer.')
    if isinstance(min_free_bytes, bool) or not isinstance(min_free_bytes, int) or min_free_bytes < 0:
        raise ValueError('Minimum free space must be a nonnegative integer.')
    if (
        not isinstance(source_sha256, str)
        or len(source_sha256) != 64
        or any(character not in '0123456789abcdef' for character in source_sha256)
    ):
        raise ValueError('Source identity must be a lowercase SHA-256 digest.')
    if (
        not isinstance(config_hash, str)
        or len(config_hash) != 64
        or any(character not in '0123456789abcdef' for character in config_hash)
    ):
        raise ValueError('Configuration identity must be a lowercase SHA-256 digest.')
    if not isinstance(resume, bool):
        raise ValueError('Resume flag must be boolean.')

    stage = Path(staging_dir)
    output = Path(output_dir)
    if output.exists():
        raise SnapshotExistsError('Output snapshot path already exists; refusing overwrite.')
    stage.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    _check_free_space(stage.parent, min_free_bytes)
    _check_free_space(output.parent, min_free_bytes)

    if stage.exists():
        if not resume:
            raise CheckpointMismatchError('Staging directory exists; resume must be explicit.')
        checkpoint = _load_checkpoint(stage, source_sha256, config_hash)
    else:
        if resume:
            raise CheckpointMismatchError('Resume requested but no staging checkpoint exists.')
        stage.mkdir(parents=True)
        checkpoint = {
            'manifest_version': MANIFEST_VERSION,
            'source_sha256': source_sha256,
            'config_hash': config_hash,
            'source_count': 0,
            'accepted_count': 0,
            'rejected_count': 0,
            'rejection_counts': {},
            'chunks': [],
        }
        atomic_write_json(stage / _CHECKPOINT_NAME, checkpoint)

    staged_chunks = checkpoint['chunks']
    existing_chunk_count = len(staged_chunks)
    input_iterator = iter(rows)
    current_chunk: list[Mapping[str, object]] = []

    for chunk_index in range(existing_chunk_count):
        expected_metadata = staged_chunks[chunk_index]
        expected_rows = expected_metadata['source_count']
        replay_rows: list[Mapping[str, object]] = []
        for _ in range(expected_rows):
            try:
                row = next(input_iterator)
            except StopIteration:
                raise CheckpointMismatchError('Source ended before the checkpoint boundary.') from None
            if not isinstance(row, Mapping):
                raise CheckpointMismatchError('Source row shape changed before the checkpoint boundary.')
            replay_rows.append(row)
        if _input_chunk_hash(replay_rows) != expected_metadata.get('input_sha256'):
            raise CheckpointMismatchError('Source rows do not match the staged checkpoint.')

    current_chunk_index = existing_chunk_count
    for row in input_iterator:
        if not isinstance(row, Mapping):
            # The validator can ledger malformed rows, but checkpoint input
            # fingerprints require deterministic mapping-shaped source rows.
            row = {'_invalid_source_row': ''}
        current_chunk.append(row)
        if len(current_chunk) == chunk_size:
            _check_free_space(stage.parent, min_free_bytes)
            metadata = _write_chunk(stage, current_chunk_index, current_chunk)
            staged_chunks.append(metadata)
            checkpoint['source_count'] += metadata['source_count']
            checkpoint['accepted_count'] += metadata['accepted_count']
            checkpoint['rejected_count'] += metadata['rejected_count']
            chunk_rejections = Counter(checkpoint['rejection_counts'])
            chunk_rejections.update(metadata['rejection_counts'])
            checkpoint['rejection_counts'] = dict(sorted(chunk_rejections.items()))
            atomic_write_json(stage / _CHECKPOINT_NAME, checkpoint)
            current_chunk_index += 1
            current_chunk = []

    if current_chunk:
        _check_free_space(stage.parent, min_free_bytes)
        metadata = _write_chunk(stage, current_chunk_index, current_chunk)
        staged_chunks.append(metadata)
        checkpoint['source_count'] += metadata['source_count']
        checkpoint['accepted_count'] += metadata['accepted_count']
        checkpoint['rejected_count'] += metadata['rejected_count']
        chunk_rejections = Counter(checkpoint['rejection_counts'])
        chunk_rejections.update(metadata['rejection_counts'])
        checkpoint['rejection_counts'] = dict(sorted(chunk_rejections.items()))
        atomic_write_json(stage / _CHECKPOINT_NAME, checkpoint)

    if checkpoint['accepted_count'] + checkpoint['rejected_count'] != checkpoint['source_count']:
        raise PipelineError('Final checkpoint counts do not reconcile.')
    checkpoint = _load_checkpoint(stage, source_sha256, config_hash)
    _check_free_space(output.parent, min_free_bytes)
    _atomic_publish(staging_dir=stage, output_dir=output, checkpoint=checkpoint)

    # The returned report is count-only; output rows remain in the completed
    # snapshot and are streamed rather than accumulated in memory.
    return PipelineResult(
        source_count=checkpoint['source_count'],
        accepted_count=checkpoint['accepted_count'],
        rejected_count=checkpoint['rejected_count'],
        output_dir=output,
    )
