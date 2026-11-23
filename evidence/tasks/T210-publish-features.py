"""Verify the pinned local snapshot, then publish label-free temporal partitions.

Run from the repository root with PYTHONPATH=backend/src. No labels are parsed.
Generated output stays under ignored data/processed/.
"""

import ctypes
import json
import shutil
import sys
import time
from pathlib import Path

from fraudlens.data.manifest import sha256_file, verify_completed_snapshot
from fraudlens.data.training_input import publish_training_features

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'data/raw/HI-Small_Trans.csv'
SNAPSHOT = ROOT / 'data/processed/t210-hi-small-b19d39f5'
BOUNDARIES = ROOT / 'data/processed/t218-hi-small-b19d39f5/boundaries.json'
ID_REPORT = ROOT / 'data/processed/t219-hi-small-b19d39f5/partition-id-hashes.json'
OUTPUT = ROOT / 'data/processed/t210-hi-small-temporal-v1'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
SNAPSHOT_SHA = '38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88'
BOUNDARY_SHA = 'b1300cad3b94bb9c2325a221c2352ca327dc2c6cf0cd1268d0bdb39a0928a728'
ID_REPORT_SHA = 'e283752549b1f8f6b0bc6b21ce9569854cf6c4cdb593636ab3dc7381466dbf60'
START_FREE = 20 * 1024**3
MIN_FREE = 10 * 1024**3
MEMORY_LIMIT = 8 * 1024**3
TIME_LIMIT = 45 * 60


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


def main() -> None:
    if OUTPUT.exists():
        raise ValueError('feature output already exists; refusing overwrite')
    initial_free = shutil.disk_usage(OUTPUT.parent).free
    if initial_free < START_FREE:
        raise ValueError('less than 20 GiB free before feature publication')
    if SOURCE.stat().st_size != 475_664_283 or sha256_file(SOURCE) != SOURCE_SHA:
        raise ValueError('raw source size or SHA-256 mismatch')
    snapshot = verify_completed_snapshot(SNAPSHOT)
    if (sha256_file(SNAPSHOT / 'manifest.json') != SNAPSHOT_SHA
            or snapshot['source_sha256'] != SOURCE_SHA
            or snapshot['accepted_count'] != 5_078_345):
        raise ValueError('completed snapshot identity mismatch')
    if sha256_file(BOUNDARIES) != BOUNDARY_SHA:
        raise ValueError('frozen boundary SHA-256 mismatch')
    if sha256_file(ID_REPORT) != ID_REPORT_SHA:
        raise ValueError('frozen partition-ID report SHA-256 mismatch')
    boundary = json.loads(BOUNDARIES.read_bytes())
    report = json.loads(ID_REPORT.read_bytes())
    if (boundary['source_sha256'] != SOURCE_SHA
            or boundary['snapshot_manifest_sha256'] != SNAPSHOT_SHA
            or report['source_sha256'] != SOURCE_SHA
            or report['boundary_sha256'] != BOUNDARY_SHA
            or report['snapshot_manifest_sha256'] != SNAPSHOT_SHA):
        raise ValueError('frozen boundary or ID-report provenance mismatch')
    start = time.monotonic()

    def check_resources() -> None:
        if time.monotonic() - start > TIME_LIMIT:
            raise RuntimeError('45-minute feature-publication time ceiling exceeded')
        if peak_working_set() > MEMORY_LIMIT:
            raise RuntimeError('8 GiB feature-publication memory ceiling exceeded')
        if shutil.disk_usage(OUTPUT.parent).free < MIN_FREE:
            raise RuntimeError('10 GiB disk reserve breached')

    check_resources()
    with (SNAPSHOT / 'accepted.jsonl').open('rb') as source:
        manifest = publish_training_features(
            source, boundary, report['partition_scoreable_id_sha256'], OUTPUT,
            max_rows=5_078_345, resource_check=check_resources,
        )
    check_resources()
    print(json.dumps({
        'output': str(OUTPUT.relative_to(ROOT)),
        'manifest_sha256': sha256_file(OUTPUT / 'manifest.json'),
        'counts': manifest['counts'],
        'elapsed_seconds': round(time.monotonic() - start, 3),
        'peak_working_set_bytes': peak_working_set(),
        'initial_free_bytes': initial_free,
        'end_free_bytes': shutil.disk_usage(OUTPUT.parent).free,
    }, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print(f'feature publication stopped: {error}', file=sys.stderr)
        sys.exit(1)
