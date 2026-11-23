"""Publish restricted train/validation labels from the pinned snapshot only."""

import ctypes
import json
import shutil
import sys
import time
from pathlib import Path

from fraudlens.data.manifest import sha256_file, verify_completed_snapshot
from fraudlens.training.label_input import publish_training_labels

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / 'data/processed/t210-hi-small-b19d39f5'
BOUNDARIES = ROOT / 'data/processed/t218-hi-small-b19d39f5/boundaries.json'
ID_REPORT = ROOT / 'data/processed/t219-hi-small-b19d39f5/partition-id-hashes.json'
FEATURES = ROOT / 'data/processed/t210-hi-small-temporal-v1'
OUTPUT = ROOT / 'data/processed/t210-hi-small-train-validation-labels-v1'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
SNAPSHOT_SHA = '38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88'
BOUNDARY_SHA = 'b1300cad3b94bb9c2325a221c2352ca327dc2c6cf0cd1268d0bdb39a0928a728'
ID_REPORT_SHA = 'e283752549b1f8f6b0bc6b21ce9569854cf6c4cdb593636ab3dc7381466dbf60'
START_FREE = 20 * 1024**3
MIN_FREE = 10 * 1024**3
MEMORY_LIMIT = 8 * 1024**3
TIME_LIMIT = 30 * 60


class ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong),
        ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t), ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
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
        raise ValueError('label output already exists; refusing overwrite')
    initial_free = shutil.disk_usage(OUTPUT.parent).free
    if initial_free < START_FREE:
        raise ValueError('less than 20 GiB free before label publication')
    snapshot = verify_completed_snapshot(SNAPSHOT)
    if (sha256_file(SNAPSHOT / 'manifest.json') != SNAPSHOT_SHA
            or snapshot['source_sha256'] != SOURCE_SHA
            or snapshot['accepted_count'] != 5_078_345
            or sha256_file(BOUNDARIES) != BOUNDARY_SHA
            or sha256_file(ID_REPORT) != ID_REPORT_SHA):
        raise ValueError('snapshot, boundary or ID-report checksum mismatch')
    boundary = json.loads(BOUNDARIES.read_bytes())
    report = json.loads(ID_REPORT.read_bytes())
    if (boundary['source_sha256'] != SOURCE_SHA
            or boundary['snapshot_manifest_sha256'] != SNAPSHOT_SHA
            or report['source_sha256'] != SOURCE_SHA
            or report['boundary_sha256'] != BOUNDARY_SHA):
        raise ValueError('boundary or ID-report provenance mismatch')
    start = time.monotonic()

    def check_resources() -> None:
        if time.monotonic() - start > TIME_LIMIT:
            raise RuntimeError('30-minute label-publication time ceiling exceeded')
        if peak_working_set() > MEMORY_LIMIT:
            raise RuntimeError('8 GiB label-publication memory ceiling exceeded')
        if shutil.disk_usage(OUTPUT.parent).free < MIN_FREE:
            raise RuntimeError('10 GiB disk reserve breached')

    check_resources()
    with (SNAPSHOT / 'accepted.jsonl').open('rb') as source:
        manifest = publish_training_labels(
            source, FEATURES, boundary, report['partition_scoreable_id_sha256'],
            OUTPUT, resource_check=check_resources,
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
        print(f'label publication stopped: {error}', file=sys.stderr)
        sys.exit(1)
