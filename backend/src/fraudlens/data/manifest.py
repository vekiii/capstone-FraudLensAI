"""Deterministic manifest and atomic JSON helpers for dataset snapshots."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

MANIFEST_VERSION = 1


class ManifestError(ValueError):
    """A manifest is malformed or its recorded counts do not reconcile."""


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically and reject non-standard numeric values."""
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(',', ':'),
    ).encode('utf-8')


def sha256_bytes(value: bytes) -> str:
    """Return a lower-case SHA-256 digest for exact bytes."""
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Hash a file incrementally so output verification stays bounded-memory."""
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b''):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_bytes(path: str | Path, value: bytes) -> None:
    """Replace a file atomically after flushing its complete contents."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f'.{destination.name}.tmp')
    try:
        with temporary.open('wb') as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: str | Path, value: Any) -> None:
    """Write canonical JSON through a same-directory atomic replacement."""
    atomic_write_bytes(path, canonical_json_bytes(value) + b'\n')


def read_json(path: str | Path) -> Any:
    """Load UTF-8 JSON and turn parse/encoding failures into a controlled error."""
    try:
        with Path(path).open('r', encoding='utf-8') as stream:
            return json.load(stream)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise ManifestError('Manifest or checkpoint JSON is unreadable.') from None


def verify_completed_snapshot(snapshot_dir: str | Path) -> dict[str, Any]:
    """Verify completion marker, manifest counts, and every published file hash."""
    root = Path(snapshot_dir)
    try:
        manifest_bytes = (root / 'manifest.json').read_bytes()
        marker = (root / 'COMPLETE').read_text(encoding='ascii').strip()
    except (OSError, UnicodeDecodeError):
        raise ManifestError('Completed snapshot marker or manifest is missing.') from None
    if marker != sha256_bytes(manifest_bytes):
        raise ManifestError('Completed snapshot manifest checksum does not match.')
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ManifestError('Completed snapshot manifest is malformed.') from None
    if not isinstance(manifest, dict) or manifest.get('complete') is not True:
        raise ManifestError('Snapshot is not marked complete.')
    if (
        isinstance(manifest.get('source_count'), bool)
        or isinstance(manifest.get('accepted_count'), bool)
        or isinstance(manifest.get('rejected_count'), bool)
        or not all(isinstance(manifest.get(key), int) and manifest[key] >= 0
                   for key in ('source_count', 'accepted_count', 'rejected_count'))
        or manifest['accepted_count'] + manifest['rejected_count'] != manifest['source_count']
    ):
        raise ManifestError('Completed snapshot counts do not reconcile.')
    files = manifest.get('processed_files')
    if not isinstance(files, list):
        raise ManifestError('Completed snapshot file list is malformed.')
    for item in files:
        if not isinstance(item, dict):
            raise ManifestError('Completed snapshot file metadata is malformed.')
        name = item.get('name')
        if not isinstance(name, str) or Path(name).name != name:
            raise ManifestError('Completed snapshot file path is invalid.')
        path = root / name
        try:
            size = path.stat().st_size
            digest = sha256_file(path)
        except OSError:
            raise ManifestError('Completed snapshot output is missing or unreadable.') from None
        if size != item.get('size_bytes') or digest != item.get('sha256'):
            raise ManifestError('Completed snapshot output checksum does not match.')
    return manifest


def validate_checkpoint(checkpoint: Any, *, source_sha256: str, config_hash: str) -> dict[str, Any]:
    """Validate checkpoint identity, shape, and row reconciliation."""
    if not isinstance(checkpoint, dict):
        raise ManifestError('Checkpoint must be a JSON object.')
    if checkpoint.get('manifest_version') != MANIFEST_VERSION:
        raise ManifestError('Checkpoint version is unsupported.')
    if checkpoint.get('source_sha256') != source_sha256:
        raise ManifestError('Checkpoint source checksum does not match.')
    if checkpoint.get('config_hash') != config_hash:
        raise ManifestError('Checkpoint configuration does not match.')
    chunks = checkpoint.get('chunks')
    if not isinstance(chunks, list):
        raise ManifestError('Checkpoint chunk list is malformed.')
    counts = ('source_count', 'accepted_count', 'rejected_count')
    if any(isinstance(checkpoint.get(key), bool) or not isinstance(checkpoint.get(key), int)
           or checkpoint[key] < 0 for key in counts):
        raise ManifestError('Checkpoint counts are malformed.')
    if checkpoint['accepted_count'] + checkpoint['rejected_count'] != checkpoint['source_count']:
        raise ManifestError('Checkpoint row counts do not reconcile.')
    if any(not isinstance(chunk, dict) for chunk in chunks):
        raise ManifestError('Checkpoint chunk metadata is malformed.')
    for index, chunk in enumerate(chunks):
        if chunk.get('chunk_index') != index:
            raise ManifestError('Checkpoint chunk order is malformed.')
        if not isinstance(chunk.get('file_name'), str):
            raise ManifestError('Checkpoint chunk filename is malformed.')
        if (
            isinstance(chunk.get('source_count'), bool)
            or not isinstance(chunk.get('source_count'), int)
            or chunk['source_count'] < 1
        ):
            raise ManifestError('Checkpoint chunk source count is malformed.')
        chunk_counts = ('accepted_count', 'rejected_count')
        if any(
            isinstance(chunk.get(key), bool)
            or not isinstance(chunk.get(key), int)
            or chunk[key] < 0
            for key in chunk_counts
        ):
            raise ManifestError('Checkpoint chunk counts are malformed.')
        if chunk['accepted_count'] + chunk['rejected_count'] != chunk['source_count']:
            raise ManifestError('Checkpoint chunk counts do not reconcile.')
        for hash_name in ('input_sha256', 'output_sha256'):
            digest = chunk.get(hash_name)
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in '0123456789abcdef' for character in digest)
            ):
                raise ManifestError('Checkpoint chunk checksum is malformed.')
    chunk_count = sum(chunk['source_count'] for chunk in chunks)
    if chunk_count != checkpoint['source_count']:
        raise ManifestError('Checkpoint chunk counts do not reconcile.')
    rejection_counts = checkpoint.get('rejection_counts')
    if (
        not isinstance(rejection_counts, dict)
        or any(not isinstance(code, str) or not isinstance(count, int) or count < 0
               for code, count in rejection_counts.items())
        or sum(rejection_counts.values()) != checkpoint['rejected_count']
    ):
        raise ManifestError('Checkpoint rejection counts do not reconcile.')
    return checkpoint


def build_manifest(
    *,
    source_sha256: str,
    config_hash: str,
    source_count: int,
    accepted_count: int,
    rejected_count: int,
    rejection_counts: dict[str, int],
    checkpoints: list[dict[str, Any]],
    processed_files: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a completed snapshot manifest from verified output facts."""
    if accepted_count + rejected_count != source_count:
        raise ManifestError('Snapshot row counts do not reconcile.')
    return {
        'manifest_version': MANIFEST_VERSION,
        'source_sha256': source_sha256,
        'source_release': None,
        'source_url': None,
        'license_reference': None,
        'config_hash': config_hash,
        'source_count': source_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'rejection_counts': dict(sorted(rejection_counts.items())),
        'warmup_count': None,
        'scoreable_count': None,
        'parser_schema_version': None,
        'checkpoint_hashes': [chunk['output_sha256'] for chunk in checkpoints],
        'processed_files': processed_files,
        'complete': True,
        'provenance_complete': False,
        'temporal_partitioning_complete': False,
    }
