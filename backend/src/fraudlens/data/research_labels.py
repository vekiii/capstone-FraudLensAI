"""Publish labels for research train/validation identities only."""

import hashlib
import json
import sqlite3
import tempfile
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.data.training_input import _without_label


def publish_research_labels(
    source_lines: Iterable[bytes], feature_root: str | Path, destination: str | Path,
    *, resource_check: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Parse labels only for row IDs in the research train/validation files.

    Test, showcase, and warm-up records are scanned for non-label identity only;
    their label tokens are never interpreted or emitted.
    """
    feature_root = Path(feature_root)
    feature_manifest_path = feature_root / 'manifest.json'
    manifest = json.loads(feature_manifest_path.read_bytes())
    if manifest.get('format') != 'hi-small-ibm-day-60-20-20-features-v1':
        raise ValueError('unexpected research feature manifest')
    for name in ('train', 'validation', 'test'):
        path = feature_root / f'{name}.jsonl'
        if sha256_file(path) != manifest['files'][name]:
            raise ValueError(f'{name} feature checksum mismatch')
    target = Path(destination)
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        raise ValueError('research labels destination must be new')

    with tempfile.TemporaryDirectory(prefix='.research-labels-', dir=target.parent) as tmp:
        stage = Path(tmp)
        db = sqlite3.connect(stage / 'labels.sqlite')
        try:
            db.execute('CREATE TABLE requested (id TEXT PRIMARY KEY, part TEXT, label INTEGER)')
            expected_ids: dict[str, list[str]] = {'train': [], 'validation': []}
            for part in expected_ids:
                with (feature_root / f'{part}.jsonl').open('rb') as stream:
                    for raw in stream:
                        record = json.loads(raw)
                        identity = record['transaction_id']
                        expected_ids[part].append(identity)
                        db.execute('INSERT INTO requested (id, part) VALUES (?, ?)',
                                   (identity, part))
            for part, ids in expected_ids.items():
                digest = hashlib.sha256(''.join(f'{item}\n' for item in ids).encode()).hexdigest()
                if digest != manifest['partition_scoreable_id_sha256'][part]:
                    raise ValueError(f'{part} feature identity hash mismatch')
            db.commit()
            seen = 0
            parsed = 0
            for raw in source_lines:
                row = _without_label(raw)
                seen += 1
                found = db.execute('SELECT part FROM requested WHERE id = ?',
                                   (row['transaction_id'],)).fetchone()
                if found is not None:
                    _, remainder = raw.split(b',"is_laundering":', 1)
                    token = remainder.partition(b',')[0]
                    if token not in (b'"0"', b'"1"'):
                        raise ValueError('train/validation label token must be binary')
                    db.execute('UPDATE requested SET label = ? WHERE id = ?',
                               (int(token[1:2]), row['transaction_id']))
                    parsed += 1
                if seen % 10_000 == 0 and resource_check is not None:
                    db.commit()
                    resource_check()
            wanted = sum(map(len, expected_ids.values()))
            if parsed != wanted or db.execute('SELECT count(*) FROM requested WHERE label IS NULL')\
                    .fetchone()[0]:
                raise ValueError('source did not contain all train/validation feature IDs')
            db.commit()
            counts = {}
            files = {}
            id_hashes = {}
            for part in expected_ids:
                out = stage / f'{part}.jsonl'
                digest = hashlib.sha256()
                positives = 0
                rows = 0
                with out.open('wb') as stream:
                    for identity, label in db.execute(
                        'SELECT id, label FROM requested WHERE part = ? ORDER BY rowid', (part,),
                    ):
                        stream.write(canonical_json_bytes({
                            'transaction_id': identity, 'label': label,
                        }) + b'\n')
                        digest.update(f'{identity}\n'.encode())
                        positives += label
                        rows += 1
                if rows != len(expected_ids[part]) or digest.hexdigest() != manifest[
                        'partition_scoreable_id_sha256'][part]:
                    raise ValueError(f'{part} label alignment failed')
                counts[part] = {'rows': rows, 'positive': positives, 'negative': rows - positives}
                id_hashes[part] = digest.hexdigest()
                files[part] = sha256_file(out)
        finally:
            db.close()
        (stage / 'labels.sqlite').unlink()
        result = {
            'format': 'hi-small-ibm-day-60-20-20-training-labels-v1',
            'source_sha256': manifest['source_sha256'],
            'feature_manifest_sha256': sha256_file(feature_manifest_path),
            'scope': 'train_and_validation_only',
            'label_values_read': {'train': True, 'validation': True,
                                  'test': False, 'showcase': False, 'warmup': False},
            'counts': counts,
            'partition_scoreable_id_sha256': id_hashes,
            'files': files,
        }
        (stage / 'manifest.json').write_bytes(canonical_json_bytes(result) + b'\n')
        if resource_check is not None:
            resource_check()
        stage.rename(target)
    return result
