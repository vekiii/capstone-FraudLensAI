"""Bounded label-free chronological scoreable-ID hashing for frozen boundaries."""

import hashlib
import heapq
import re
import tempfile
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path

_TIMESTAMP = re.compile(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}\Z')
_NAMES = ('development', 'showcase', 'train', 'validation', 'test')


def _cutoff(boundary: Mapping[str, object], name: str) -> str:
    value = boundary.get(name)
    if not isinstance(value, str):
        raise ValueError(f'{name} is missing')
    try:
        instant = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f'{name} is malformed') from None
    if instant.utcoffset() != timezone.utc.utcoffset(None):
        raise ValueError(f'{name} must be UTC')
    return instant.strftime('%Y/%m/%d %H:%M')


def _run_lines(path: Path):
    with path.open('rb') as stream:
        yield from stream


def hash_partition_ids(
    rows: Iterable[tuple[str, int, str]],
    boundary: Mapping[str, object],
    workdir: str | Path,
    *,
    chunk_size: int = 100_000,
) -> dict[str, object]:
    """Sort UTC-minute/source-row keys in bounded runs, then hash IDs in order.

    Input must be a verified, fully accepted snapshot. The row iterator must
    extract only timestamp, source row number and transaction ID, never labels.
    Temporary sort runs are removed on success or failure.
    """
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size < 1:
        raise ValueError('chunk_size must be positive')
    source_sha = boundary.get('source_sha256')
    accepted = boundary.get('accepted_count')
    if (not isinstance(source_sha, str) or re.fullmatch(r'[0-9a-f]{64}', source_sha) is None
            or not isinstance(accepted, int) or isinstance(accepted, bool) or accepted < 1):
        raise ValueError('frozen source identity/count is invalid')
    counts_expected = {
        'warmup': boundary.get('warmup_count'),
        'development_source': boundary.get('development_count'),
        'showcase': boundary.get('showcase_count'),
        'train': boundary.get('train_count'),
        'validation': boundary.get('validation_count'),
        'test': boundary.get('test_count'),
    }
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0
           for value in counts_expected.values()):
        raise ValueError('frozen partition counts are invalid')
    if counts_expected['development_source'] + counts_expected['showcase'] != accepted:
        raise ValueError('frozen source partition counts do not reconcile')
    if (sum(counts_expected[name] for name in ('train', 'validation', 'test'))
            != counts_expected['development_source'] - counts_expected['warmup']):
        raise ValueError('frozen scoreable development counts do not reconcile')
    warmup_end = _cutoff(boundary, 'warmup_end_exclusive_utc')
    train_end = _cutoff(boundary, 'train_end_utc')
    validation_end = _cutoff(boundary, 'validation_end_utc')
    development_end = _cutoff(boundary, 'development_end_utc')
    if not warmup_end <= train_end < validation_end < development_end:
        raise ValueError('frozen timestamp boundaries are out of order')

    digests = {name: hashlib.sha256() for name in _NAMES}
    counts = {name: 0 for name in _NAMES}
    seen = bytearray(accepted + 1)
    scanned = 0
    with tempfile.TemporaryDirectory(prefix='t219-ids-', dir=workdir) as temporary:
        root = Path(temporary)
        run_paths: list[Path] = []
        chunk: list[bytes] = []

        def flush() -> None:
            if not chunk:
                return
            path = root / f'run-{len(run_paths):05d}.txt'
            with path.open('wb') as stream:
                stream.writelines(sorted(chunk))
            run_paths.append(path)
            chunk.clear()

        valid_times: set[str] = set()
        for timestamp, number, identity in rows:
            if not isinstance(timestamp, str) or _TIMESTAMP.fullmatch(timestamp) is None:
                raise ValueError('timestamp is malformed')
            if timestamp not in valid_times:
                try:
                    datetime.strptime(timestamp, '%Y/%m/%d %H:%M')
                except ValueError:
                    raise ValueError('timestamp is invalid') from None
                valid_times.add(timestamp)
            if (not isinstance(number, int) or isinstance(number, bool)
                    or number < 1 or number > accepted or seen[number]):
                raise ValueError('source row is missing, duplicated or out of range')
            if identity != f'ibm-hi-small:{source_sha}:row:{number}':
                raise ValueError('transaction identity differs from frozen source')
            seen[number] = 1
            scanned += 1
            chunk.append(f'{timestamp}\t{number:010d}\n'.encode('ascii'))
            if len(chunk) == chunk_size:
                flush()
        flush()
        if scanned != accepted or 0 in seen[1:]:
            raise ValueError('source-row identity coverage does not reconcile')

        warmup = 0
        development_source = 0
        ordered = heapq.merge(*(_run_lines(path) for path in run_paths))
        for line in ordered:
            timestamp = line[:16].decode('ascii')
            number = int(line[17:-1])
            if timestamp <= development_end:
                development_source += 1
            if timestamp < warmup_end:
                warmup += 1
                continue
            if timestamp <= train_end:
                partition = 'train'
            elif timestamp <= validation_end:
                partition = 'validation'
            elif timestamp <= development_end:
                partition = 'test'
            else:
                partition = 'showcase'
            encoded = f'ibm-hi-small:{source_sha}:row:{number}\n'.encode('ascii')
            digests[partition].update(encoded)
            counts[partition] += 1
            if partition != 'showcase':
                digests['development'].update(encoded)
                counts['development'] += 1

    if warmup != counts_expected['warmup'] or development_source != (
        counts_expected['development_source']
    ) or any(counts[name] != counts_expected[name] for name in (
        'train', 'validation', 'test', 'showcase'
    )):
        raise ValueError('ordered IDs disagree with frozen partition counts')
    return {
        'partition_scoreable_id_sha256': {name: digest.hexdigest()
                                          for name, digest in digests.items()},
        'partition_counts': counts,
        'warmup_count': warmup,
        'development_source_count': development_source,
        'accepted_count': scanned,
    }
