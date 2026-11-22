"""Label-free chronological feature publication from a verified accepted snapshot.

The default row ceiling makes this a synthetic-scale boundary. A separately
reviewed full-source runner must pass its measured ceiling explicitly.
"""

import hashlib
import json
import re
import sqlite3
import tempfile
from collections.abc import Callable
from contextlib import ExitStack
from decimal import Decimal
from pathlib import Path
from typing import Any

from fraudlens.data.features import (
    FEATURE_ORDER,
    FEATURE_VERSION,
    iter_temporal_features_ordered,
    normalize_timestamp_utc,
)
from fraudlens.data.manifest import canonical_json_bytes, sha256_file

_LABEL_MARKER = b',"is_laundering":'
_SOURCE_KEYS = frozenset({
    'amount_paid', 'amount_received', 'payment_currency', 'payment_format',
    'receiver_account', 'receiver_bank', 'receiver_key', 'receiving_currency',
    'sender_account', 'sender_bank', 'sender_key', 'source_row_number',
    'source_sha256', 'timestamp', 'transaction_id',
})
_PARTITIONS = ('train', 'validation', 'test', 'showcase')
_HASHES = (*_PARTITIONS, 'development')
_HEX = re.compile(r'[0-9a-f]{64}\Z')
_TIMESTAMP = re.compile(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}\Z')


def _without_label(raw: bytes) -> dict[str, Any]:
    """Discard the canonical label token before JSON parsing any row fields."""
    if not isinstance(raw, bytes) or raw.count(_LABEL_MARKER) != 1:
        raise ValueError('accepted row must contain one canonical label field')
    head, remainder = raw.split(_LABEL_MARKER, 1)
    _, comma, tail = remainder.partition(b',')
    if not comma:
        raise ValueError('canonical label field must be followed by source fields')
    try:
        row = json.loads(head + b',' + tail)
    except (ValueError, UnicodeDecodeError):
        raise ValueError('accepted non-label fields are malformed') from None
    if not isinstance(row, dict) or set(row) != _SOURCE_KEYS:
        raise ValueError('accepted non-label schema mismatch')
    return row


def _cutoffs(boundary: dict[str, Any]) -> tuple[str, str, str, str]:
    if not isinstance(boundary, dict):
        raise ValueError('frozen boundary is required')
    values = []
    for field in ('warmup_end_exclusive_utc', 'train_end_utc',
                  'validation_end_utc', 'development_end_utc'):
        value = boundary.get(field)
        if not isinstance(value, str):
            raise ValueError(f'{field} is missing')
        try:
            instant = normalize_timestamp_utc(value)
        except ValueError:
            raise ValueError(f'{field} is malformed') from None
        values.append(instant.strftime('%Y/%m/%d %H:%M'))
    if not values[0] <= values[1] < values[2] < values[3]:
        raise ValueError('frozen boundary ordering is invalid')
    return tuple(values)  # type: ignore[return-value]


def _partition(timestamp: str, cutoffs: tuple[str, str, str, str]) -> str | None:
    warmup, train, validation, development = cutoffs
    if timestamp < warmup:
        return None
    if timestamp <= train:
        return 'train'
    if timestamp <= validation:
        return 'validation'
    if timestamp <= development:
        return 'test'
    return 'showcase'


def _ordered_rows(connection: sqlite3.Connection):
    cursor = connection.execute(
        'SELECT nonlabel_json FROM rows ORDER BY timestamp, source_row_number',
    )
    for (raw,) in cursor:
        yield json.loads(raw)


def publish_training_features(
    source_lines,
    boundary: dict[str, Any],
    expected_id_hashes: dict[str, str],
    destination: str | Path,
    *,
    max_rows: int = 10_000,
    resource_check: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Sort non-label fields, compute strict-prior features, and verify partitions.

    ``source_lines`` must come from a separately verified accepted snapshot.
    This function never parses or publishes ``is_laundering``. The caller must
    retain labels in an independently controlled training-only boundary.
    """
    if (not isinstance(boundary, dict)
            or type(max_rows) is not int or max_rows < 1
            or type(boundary.get('accepted_count')) is not int
            or boundary['accepted_count'] < 1
            or boundary['accepted_count'] > max_rows):
        raise ValueError('accepted row count exceeds explicit publication ceiling')
    accepted = boundary['accepted_count']
    source_sha = boundary.get('source_sha256')
    if not isinstance(source_sha, str) or _HEX.fullmatch(source_sha) is None:
        raise ValueError('frozen source hash is invalid')
    if (not isinstance(expected_id_hashes, dict)
            or set(expected_id_hashes) != set(_HASHES)
            or any(not isinstance(value, str) or _HEX.fullmatch(value) is None
                   for value in expected_id_hashes.values())):
        raise ValueError('independent partition ID hashes are required')
    expected_counts = {
        name: boundary.get(f'{name}_count') for name in _PARTITIONS
    }
    expected_counts['warmup'] = boundary.get('warmup_count')
    if (any(type(value) is not int or value < 0 for value in expected_counts.values())
            or sum(expected_counts.values()) != accepted
            or type(boundary.get('development_count')) is not int
            or sum(expected_counts[name] for name in ('warmup', 'train',
                                                      'validation', 'test'))
            != boundary.get('development_count')):
        raise ValueError('frozen partition counts do not reconcile')
    cutoffs = _cutoffs(boundary)
    target = Path(destination)
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        raise ValueError('feature destination must be new under an existing directory')

    with tempfile.TemporaryDirectory(prefix='.features-', dir=target.parent) as stage_name:
        stage = Path(stage_name)
        database = stage / 'sort.sqlite'
        connection = sqlite3.connect(database)
        try:
            connection.execute('CREATE TABLE rows ('
                               'source_row_number INTEGER PRIMARY KEY, '
                               'timestamp TEXT NOT NULL, nonlabel_json BLOB NOT NULL)')
            count = 0
            for raw in source_lines:
                row = _without_label(raw)
                number = row['source_row_number']
                timestamp = row['timestamp']
                if (type(number) is not int or not 1 <= number <= accepted
                        or not isinstance(timestamp, str)
                        or _TIMESTAMP.fullmatch(timestamp) is None
                        or row['source_sha256'] != source_sha
                        or row['transaction_id'] != (
                            f'ibm-hi-small:{source_sha}:row:{number}')):
                    raise ValueError('accepted row identity or timestamp mismatch')
                normalize_timestamp_utc(timestamp)
                try:
                    connection.execute('INSERT INTO rows VALUES (?, ?, ?)',
                                       (number, timestamp, canonical_json_bytes(row)))
                except sqlite3.IntegrityError:
                    raise ValueError('duplicate source row number') from None
                count += 1
                if count > accepted:
                    raise ValueError('accepted row count exceeds frozen count')
                if count % 10_000 == 0:
                    connection.commit()
                    if resource_check is not None:
                        resource_check()
            if count != accepted:
                raise ValueError('accepted row count differs from frozen count')
            connection.commit()

            counts = dict.fromkeys(expected_counts, 0)
            digests = {name: hashlib.sha256() for name in _HASHES}
            with ExitStack() as stack:
                streams = {name: stack.enter_context((stage / f'{name}.jsonl').open('wb'))
                           for name in _PARTITIONS}
                processed = 0
                for result in iter_temporal_features_ordered(_ordered_rows(connection)):
                    processed += 1
                    if processed % 10_000 == 0 and resource_check is not None:
                        resource_check()
                    partition = _partition(result['timestamp'], cutoffs)
                    if (partition is None) != (not result['is_scoreable']):
                        raise ValueError('feature warm-up eligibility differs from boundary')
                    if partition is None:
                        counts['warmup'] += 1
                        continue
                    counts[partition] += 1
                    identity = result['transaction_id']
                    encoded_id = (identity + '\n').encode('utf-8')
                    digests[partition].update(encoded_id)
                    if partition != 'showcase':
                        digests['development'].update(encoded_id)
                    features = {name: (str(value) if isinstance(value, Decimal) else value)
                                for name, value in result['features'].items()}
                    streams[partition].write(canonical_json_bytes({
                        'transaction_id': identity,
                        'occurred_at_utc': result['occurred_at_utc'].isoformat(),
                        'features': features,
                    }) + b'\n')
            if counts != expected_counts:
                raise ValueError('published partition counts differ from frozen counts')
            actual_hashes = {name: digest.hexdigest() for name, digest in digests.items()}
            if actual_hashes != expected_id_hashes:
                raise ValueError('published partition ID hashes differ from frozen hashes')
        finally:
            connection.close()
        database.unlink()
        manifest = {
            'format': 'hi-small-training-features-v1',
            'source_sha256': source_sha,
            'feature_version': FEATURE_VERSION,
            'feature_order': list(FEATURE_ORDER),
            'counts': counts,
            'partition_scoreable_id_sha256': actual_hashes,
            'files': {name: sha256_file(stage / f'{name}.jsonl') for name in _PARTITIONS},
        }
        (stage / 'manifest.json').write_bytes(canonical_json_bytes(manifest) + b'\n')
        if resource_check is not None:
            resource_check()
        stage.rename(target)
    return manifest
