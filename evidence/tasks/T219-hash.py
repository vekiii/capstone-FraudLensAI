"""Benchmark or hash frozen T218 scoreable IDs without accessing labels."""

import argparse
import ctypes
import json
import re
import shutil
import sys
import time
from pathlib import Path

from fraudlens.data.manifest import atomic_write_json, sha256_file, verify_completed_snapshot
from fraudlens.data.partition_hashes import hash_partition_ids

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'data/raw/HI-Small_Trans.csv'
SNAPSHOT = ROOT / 'data/processed/t210-hi-small-b19d39f5'
BOUNDARIES = ROOT / 'data/processed/t218-hi-small-b19d39f5/boundaries.json'
OUTPUT = ROOT / 'data/processed/t219-hi-small-b19d39f5'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
BOUNDARY_SHA = 'b1300cad3b94bb9c2325a221c2352ca327dc2c6cf0cd1268d0bdb39a0928a728'
MANIFEST_SHA = '38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88'
ROW = re.compile(rb'"source_row_number":([1-9][0-9]*)')
TIME = re.compile(rb'"timestamp":"(\d{4}/\d{2}/\d{2} \d{2}:\d{2})"')
ID = re.compile(rb'"transaction_id":"([^"]+)"')
CHUNK_SIZE = 100_000
MIN_FREE = 10 * 1024**3
START_FREE = 20 * 1024**3
MEMORY_CEILING = 512 * 1024**2
RUNTIME_CEILING = 900


class ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong),
        ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t), ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
        ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
        ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t),
        ('PrivateUsage', ctypes.c_size_t),
    ]


def peak_working_set() -> int:
    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    handle = ctypes.windll.kernel32.GetCurrentProcess
    handle.restype = ctypes.c_void_p
    get_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_info.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong)
    if not get_info(handle(), ctypes.byref(counters), counters.cb):
        raise OSError('GetProcessMemoryInfo failed')
    return counters.PeakWorkingSetSize


def _one(pattern: re.Pattern[bytes], line: bytes) -> bytes:
    match = pattern.search(line)
    if match is None or pattern.search(line, match.end()) is not None:
        raise ValueError('required non-label field missing or duplicated')
    return match.group(1)


def source_rows():
    with (SNAPSHOT / 'accepted.jsonl').open('rb') as stream:
        for line in stream:
            yield (
                _one(TIME, line).decode('ascii'),
                int(_one(ROW, line)),
                _one(ID, line).decode('ascii'),
            )


def synthetic_rows(boundary: dict):
    """Full-size, five-group skew with permuted source-order row numbers."""
    accepted = boundary['accepted_count']
    for ordinal in range(accepted):
        number = (ordinal * 7 + 1) % accepted + 1
        if number <= boundary['warmup_count']:
            timestamp = '2022/09/01 00:00'
        elif number <= boundary['warmup_count'] + boundary['train_count']:
            timestamp = '2022/09/02 01:00'
        elif number <= boundary['warmup_count'] + boundary['train_count'] + boundary['validation_count']:
            timestamp = '2022/09/02 02:00'
        elif number <= boundary['development_count']:
            timestamp = '2022/09/02 03:00'
        else:
            timestamp = '2022/09/02 04:00'
        yield timestamp, number, f'ibm-hi-small:{boundary["source_sha256"]}:row:{number}'


def synthetic_boundary() -> dict:
    return {
        'source_sha256': 'a' * 64,
        'accepted_count': 5_000_000,
        'warmup_count': 1_000_000,
        'development_count': 3_000_000,
        'showcase_count': 2_000_000,
        'train_count': 1_400_000,
        'validation_count': 300_000,
        'test_count': 300_000,
        'warmup_end_exclusive_utc': '2022-09-02T00:00:00+00:00',
        'train_end_utc': '2022-09-02T01:00:00+00:00',
        'validation_end_utc': '2022-09-02T02:00:00+00:00',
        'development_end_utc': '2022-09-02T03:00:00+00:00',
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('benchmark', 'actual'))
    arguments = parser.parse_args()
    start = time.monotonic()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    start_free = shutil.disk_usage(OUTPUT).free
    if start_free < START_FREE:
        raise RuntimeError('T219 start free space below 20 GiB')
    if arguments.phase == 'benchmark':
        boundary = synthetic_boundary()
        rows = synthetic_rows(boundary)
        output_path = OUTPUT / 'synthetic-benchmark.json'
    else:
        if sha256_file(SOURCE) != SOURCE_SHA:
            raise RuntimeError('T219 raw source checksum mismatch')
        manifest = verify_completed_snapshot(SNAPSHOT)
        if sha256_file(SNAPSHOT / 'manifest.json') != MANIFEST_SHA:
            raise RuntimeError('T219 snapshot manifest checksum mismatch')
        if manifest['source_sha256'] != SOURCE_SHA or manifest['accepted_count'] != 5_078_345:
            raise RuntimeError('T219 snapshot identity/count mismatch')
        if sha256_file(BOUNDARIES) != BOUNDARY_SHA:
            raise RuntimeError('T219 frozen boundary checksum mismatch')
        boundary = json.loads(BOUNDARIES.read_bytes())
        if (boundary['source_sha256'] != SOURCE_SHA
                or boundary['snapshot_manifest_sha256'] != MANIFEST_SHA):
            raise RuntimeError('T219 frozen boundary provenance mismatch')
        rows = source_rows()
        output_path = OUTPUT / 'partition-id-hashes.json'
    if output_path.exists():
        raise RuntimeError('T219 output already exists; refusing overwrite')
    result = hash_partition_ids(rows, boundary, OUTPUT, chunk_size=CHUNK_SIZE)
    elapsed = time.monotonic() - start
    peak = peak_working_set()
    end_free = shutil.disk_usage(OUTPUT).free
    if peak > MEMORY_CEILING or elapsed > RUNTIME_CEILING or end_free < MIN_FREE:
        raise RuntimeError('T219 memory, runtime or disk ceiling breached; refusing publication')
    report = {
        'format': 't219-scoreable-id-hashes-v1', 'phase': arguments.phase,
        'source_sha256': boundary['source_sha256'],
        'boundary_sha256': BOUNDARY_SHA if arguments.phase == 'actual' else None,
        'snapshot_manifest_sha256': MANIFEST_SHA if arguments.phase == 'actual' else None,
        'ordering': 'UTC-minute then source_row_number; UTF-8 transaction_id plus LF',
        'chunk_size': CHUNK_SIZE, 'start_free_bytes': start_free,
        'end_free_bytes': end_free, 'elapsed_seconds': round(elapsed, 3),
        'peak_working_set_bytes': peak, **result,
    }
    atomic_write_json(output_path, report)
    print(json.dumps({'phase': arguments.phase, 'output_sha256': sha256_file(output_path),
                      'elapsed_seconds': report['elapsed_seconds'],
                      'peak_working_set_bytes': peak, 'end_free_bytes': end_free,
                      'partition_counts': result['partition_counts']}, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(f'T219 stopped: {error}', file=sys.stderr)
        sys.exit(1)
