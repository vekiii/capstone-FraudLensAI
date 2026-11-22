"""Publish only train/validation labels aligned to verified feature identities."""

import hashlib
import json
import sqlite3
import tempfile
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.data.training_input import _cutoffs, _partition, _without_label

_PARTITIONS = ('train', 'validation')


def _verified_feature_manifest(root: Path, boundary: dict, hashes: dict) -> dict:
    manifest_path = root / 'manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    if (manifest.get('format') != 'hi-small-training-features-v1'
            or manifest.get('source_sha256') != boundary['source_sha256']
            or manifest.get('partition_scoreable_id_sha256') != hashes
            or manifest.get('counts', {}).get('train') != boundary['train_count']
            or manifest.get('counts', {}).get('validation') != boundary['validation_count']):
        raise ValueError('feature manifest identity mismatch')
    for name in _PARTITIONS:
        if sha256_file(root / f'{name}.jsonl') != manifest['files'][name]:
            raise ValueError(f'{name} feature file checksum mismatch')
    return manifest


def publish_training_labels(
    source_lines: Iterable[bytes],
    feature_root: str | Path,
    boundary: dict[str, Any],
    expected_id_hashes: dict[str, str],
    destination: str | Path,
    *,
    resource_check: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Read only eligible train/validation label tokens, then align by feature ID.

    The caller must first verify the completed source snapshot and frozen inputs.
    Test, showcase and warm-up label tokens are discarded without parsing.
    """
    root = Path(feature_root)
    _verified_feature_manifest(root, boundary, expected_id_hashes)
    target = Path(destination)
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        raise ValueError('label destination must be new under an existing directory')
    cutoffs = _cutoffs(boundary)
    expected = {name: boundary[f'{name}_count'] for name in _PARTITIONS}
    with tempfile.TemporaryDirectory(prefix='.labels-', dir=target.parent) as stage_name:
        stage = Path(stage_name)
        connection = sqlite3.connect(stage / 'labels.sqlite')
        try:
            connection.execute(
                'CREATE TABLE labels (transaction_id TEXT PRIMARY KEY, '
                'partition TEXT NOT NULL, label INTEGER NOT NULL)'
            )
            source_count = 0
            counts = dict.fromkeys(_PARTITIONS, 0)
            for raw in source_lines:
                row = _without_label(raw)
                source_count += 1
                partition = _partition(row['timestamp'], cutoffs)
                if partition in _PARTITIONS:
                    _, remainder = raw.split(b',"is_laundering":', 1)
                    token = remainder.partition(b',')[0]
                    if token not in (b'"0"', b'"1"'):
                        raise ValueError('train/validation label must be binary')
                    try:
                        connection.execute(
                            'INSERT INTO labels VALUES (?, ?, ?)',
                            (row['transaction_id'], partition, int(token[1:2])),
                        )
                    except sqlite3.IntegrityError:
                        raise ValueError('duplicate train/validation identity') from None
                    counts[partition] += 1
                if source_count % 10_000 == 0:
                    connection.commit()
                    if resource_check is not None:
                        resource_check()
            if (source_count != boundary['accepted_count'] or counts != expected):
                raise ValueError('train/validation label counts differ from frozen boundary')
            connection.commit()
            file_hashes = {}
            for name in _PARTITIONS:
                digest = hashlib.sha256()
                count = 0
                with (root / f'{name}.jsonl').open('rb') as features:
                    with (stage / f'{name}.jsonl').open('wb') as output:
                        for raw in features:
                            identity = json.loads(raw)['transaction_id']
                            match = connection.execute(
                                'SELECT label FROM labels WHERE transaction_id = ? '
                                'AND partition = ?', (identity, name),
                            ).fetchone()
                            if match is None:
                                raise ValueError('feature row lacks matching train/validation label')
                            digest.update((identity + '\n').encode())
                            output.write(canonical_json_bytes({
                                'transaction_id': identity, 'label': match[0],
                            }) + b'\n')
                            count += 1
                            if count % 10_000 == 0 and resource_check is not None:
                                resource_check()
                if count != expected[name] or digest.hexdigest() != expected_id_hashes[name]:
                    raise ValueError('label output partition ID hash mismatch')
                file_hashes[name] = sha256_file(stage / f'{name}.jsonl')
        finally:
            connection.close()
        (stage / 'labels.sqlite').unlink()
        manifest = {
            'format': 'hi-small-restricted-training-labels-v1',
            'source_sha256': boundary['source_sha256'],
            'feature_manifest_sha256': sha256_file(root / 'manifest.json'),
            'counts': counts,
            'partition_scoreable_id_sha256': {
                name: expected_id_hashes[name] for name in _PARTITIONS
            },
            'files': file_hashes,
            'label_scope': 'train_and_validation_only',
        }
        if manifest['feature_manifest_sha256'] != sha256_file(root / 'manifest.json'):
            raise ValueError('feature manifest changed during label publication')
        (stage / 'manifest.json').write_bytes(canonical_json_bytes(manifest) + b'\n')
        if resource_check is not None:
            resource_check()
        stage.rename(target)
    return manifest
