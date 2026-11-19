"""Reproducible, synthetic-only resource probe for the Feature 002 staging runner."""

import argparse
import ctypes
import hashlib
import json
import shutil
import tempfile
import time
from pathlib import Path

from fraudlens.data.manifest import verify_completed_snapshot
from fraudlens.data.pipeline import run_pipeline
from fraudlens.data.source import stable_transaction_id

SOURCE_HASH = 'a' * 64
CONFIG_HASH = hashlib.sha256(b'T209 synthetic resource probe v1').hexdigest()


class ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_ulong),
        ('PageFaultCount', ctypes.c_ulong),
        ('PeakWorkingSetSize', ctypes.c_size_t),
        ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
        ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
        ('PagefileUsage', ctypes.c_size_t),
        ('PeakPagefileUsage', ctypes.c_size_t),
        ('PrivateUsage', ctypes.c_size_t),
    ]


def peak_working_set() -> int:
    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    get_current_process.restype = ctypes.c_void_p
    get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_process_memory_info.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong)
    if not get_process_memory_info(
        get_current_process(), ctypes.byref(counters), counters.cb
    ):
        raise OSError('GetProcessMemoryInfo failed')
    return counters.PeakWorkingSetSize


def synthetic_rows(count: int, skew: str):
    for number in range(1, count + 1):
        account = number if skew == 'wide' else number % 8
        yield {
            'source_sha256': SOURCE_HASH,
            'source_row_number': number,
            'transaction_id': stable_transaction_id(SOURCE_HASH, number),
            'timestamp': f'2022/09/{1 + (number // 500000):02d} {number % 24:02d}:{number % 60:02d}',
            'sender_bank': f'{number % 128:04d}',
            'sender_account': f'{account:016d}',
            'receiver_bank': f'{(number + 17) % 128:04d}',
            'receiver_account': f'{account + 42:016d}',
            'amount_received': '1234.50',
            'receiving_currency': 'EUR',
            'amount_paid': '1234.50',
            'payment_currency': 'EUR',
            'payment_format': 'Wire',
            'is_laundering': '0',
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', type=int, required=True)
    parser.add_argument('--chunk-size', type=int, required=True)
    parser.add_argument('--skew', choices=('wide', 'hot'), required=True)
    args = parser.parse_args()
    if args.rows < 1 or args.chunk_size < 1:
        parser.error('rows and chunk-size must be positive')
    root = Path('data/processed')
    root.mkdir(parents=True, exist_ok=True)
    probe = Path(tempfile.mkdtemp(prefix='.t209-benchmark-', dir=root))
    free_before = shutil.disk_usage(root).free
    start = time.perf_counter()
    try:
        result = run_pipeline(
            synthetic_rows(args.rows, args.skew),
            staging_dir=probe / 'stage',
            output_dir=probe / 'snapshot',
            source_sha256=SOURCE_HASH,
            config_hash=CONFIG_HASH,
            chunk_size=args.chunk_size,
            min_free_bytes=1_073_741_824,
            resume=False,
        )
        elapsed = time.perf_counter() - start
        manifest = verify_completed_snapshot(result.output_dir)
        stage_bytes = sum(p.stat().st_size for p in (probe / 'stage').rglob('*') if p.is_file())
        output_bytes = sum(p.stat().st_size for p in result.output_dir.rglob('*') if p.is_file())
        print(json.dumps({
            'rows': args.rows,
            'skew': args.skew,
            'chunk_size': args.chunk_size,
            'elapsed_seconds_including_verification': round(elapsed, 3),
            'peak_working_set_bytes': peak_working_set(),
            'stage_bytes': stage_bytes,
            'snapshot_bytes': output_bytes,
            'free_before_bytes': free_before,
            'free_after_bytes': shutil.disk_usage(root).free,
            'source_count': manifest['source_count'],
            'accepted_count': manifest['accepted_count'],
            'rejected_count': manifest['rejected_count'],
        }, sort_keys=True))
    finally:
        shutil.rmtree(probe)


if __name__ == '__main__':
    main()
