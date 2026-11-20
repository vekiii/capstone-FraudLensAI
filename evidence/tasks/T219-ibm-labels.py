"""Prepare only train/validation labels for the versioned IBM-style split."""

import ctypes
import json
import shutil
import time
from pathlib import Path

from fraudlens.data.manifest import sha256_file, verify_completed_snapshot
from fraudlens.data.research_labels import publish_research_labels

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / 'data/processed/t210-hi-small-b19d39f5'
FEATURES = ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'
OUTPUT = ROOT / 'data/processed/t219-ibm-day-60-20-20-labels-v1'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
SNAPSHOT_SHA = '38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88'
START_FREE = 20 * 1024**3
MIN_FREE = 10 * 1024**3
MEMORY_LIMIT = 8 * 1024**3
TIME_LIMIT = 30 * 60


class MemoryCounters(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong),
        ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t), ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t), ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
        ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t),
        ('PrivateUsage', ctypes.c_size_t),
    ]


def peak_working_set() -> int:
    counters = MemoryCounters()
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
        raise ValueError('research labels already exist; refusing overwrite')
    free_at_start = shutil.disk_usage(OUTPUT.parent).free
    if free_at_start < START_FREE:
        raise RuntimeError('less than 20 GiB free before restricted label pass')
    snapshot = verify_completed_snapshot(SNAPSHOT)
    if (snapshot['source_sha256'] != SOURCE_SHA
            or sha256_file(SNAPSHOT / 'manifest.json') != SNAPSHOT_SHA):
        raise ValueError('verified snapshot identity mismatch')
    started = time.monotonic()

    def resource_check() -> None:
        if peak_working_set() > MEMORY_LIMIT:
            raise RuntimeError('8 GiB process working-set ceiling exceeded')
        if time.monotonic() - started > TIME_LIMIT:
            raise RuntimeError('30-minute restricted label-pass ceiling exceeded')
        if shutil.disk_usage(OUTPUT.parent).free < MIN_FREE:
            raise RuntimeError('10 GiB disk reserve breached')

    with (SNAPSHOT / 'accepted.jsonl').open('rb') as source:
        result = publish_research_labels(source, FEATURES, OUTPUT, resource_check=resource_check)
    print(json.dumps({
        'output': str(OUTPUT.relative_to(ROOT)),
        'feature_manifest_sha256': result['feature_manifest_sha256'],
        'label_manifest_sha256': sha256_file(OUTPUT / 'manifest.json'),
        'counts': result['counts'],
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'free_at_start_bytes': free_at_start,
        'free_at_end_bytes': shutil.disk_usage(OUTPUT.parent).free,
        'peak_working_set_bytes': peak_working_set(),
        'label_values_read': result['label_values_read'],
    }, sort_keys=True))


if __name__ == '__main__':
    main()
