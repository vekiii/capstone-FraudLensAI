"""Publish IBM-style whole-day 60/20/20 scoreable features, without labels."""

import ctypes
import hashlib
import json
import shutil
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.data.research_split import plan_ibm_day_split

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'data/raw/HI-Small_Trans.csv'
OLD_FEATURES = ROOT / 'data/processed/t210-hi-small-temporal-v1'
OUTPUT = ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
OLD_FEATURE_MANIFEST_SHA = '5ca1660eb582b68b27f58241b115eea5d69d3feb77f78f9fe46c12611b4f517a'
MEMORY_LIMIT = 8 * 1024**3
MIN_START_FREE = 20 * 1024**3
MIN_END_FREE = 10 * 1024**3
TIME_LIMIT = 60 * 60


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
        raise ValueError('versioned split output already exists; refusing overwrite')
    initial_free = shutil.disk_usage(OUTPUT.parent).free
    if initial_free < MIN_START_FREE:
        raise RuntimeError('less than 20 GiB free before publication')
    if (sha256_file(SOURCE) != SOURCE_SHA
            or sha256_file(OLD_FEATURES / 'manifest.json') != OLD_FEATURE_MANIFEST_SHA):
        raise ValueError('source or prior feature manifest identity mismatch')
    old_manifest = json.loads((OLD_FEATURES / 'manifest.json').read_bytes())
    frozen_boundary_path = ROOT / 'data/processed/t218-hi-small-b19d39f5/boundaries.json'
    frozen_boundary = json.loads(frozen_boundary_path.read_bytes())
    if (old_manifest.get('counts', {}).get('train', 0)
            + old_manifest.get('counts', {}).get('validation', 0)
            + old_manifest.get('counts', {}).get('test', 0)
            != (frozen_boundary['train_count'] + frozen_boundary['validation_count']
                + frozen_boundary['test_count'])):
        raise ValueError('parent feature counts differ from frozen scoreable development')
    for name, digest in old_manifest['files'].items():
        if sha256_file(OLD_FEATURES / f'{name}.jsonl') != digest:
            raise ValueError(f'{name} feature file checksum mismatch')

    def feature_rows():
        for name in ('train', 'validation', 'test'):
            with (OLD_FEATURES / f'{name}.jsonl').open('rb') as stream:
                for line in stream:
                    item = json.loads(line)
                    yield {
                        'transaction_id': item['transaction_id'],
                        'occurred_at_utc': datetime.fromisoformat(item['occurred_at_utc']),
                    }

    started = time.monotonic()
    planned = plan_ibm_day_split(feature_rows())
    train_cut = planned.train_end_utc
    validation_cut = planned.validation_end_utc
    stage_context = tempfile.TemporaryDirectory(prefix='.t219-ibm-split-', dir=OUTPUT.parent)
    stage_root = Path(stage_context.name)
    targets = {'train': stage_root / 'train.jsonl',
               'validation': stage_root / 'validation.jsonl',
               'test': stage_root / 'test.jsonl'}
    counts = dict.fromkeys(targets, 0)
    identities = {name: hashlib.sha256() for name in targets}
    with (targets['train'].open('wb') as train_out,
          targets['validation'].open('wb') as validation_out,
          targets['test'].open('wb') as test_out):
        outputs = {'train': train_out, 'validation': validation_out, 'test': test_out}
        for name in ('train', 'validation', 'test'):
            with (OLD_FEATURES / f'{name}.jsonl').open('rb') as stream:
                for line in stream:
                    item = json.loads(line)
                    day = datetime.fromisoformat(item['occurred_at_utc']).date()
                    partition = 'train' if day <= train_cut else (
                        'validation' if day <= validation_cut else 'test'
                    )
                    outputs[partition].write(line)
                    counts[partition] += 1
                    identities[partition].update(
                        (item['transaction_id'] + '\n').encode('utf-8'),
                    )
                    if counts[partition] % 100_000 == 0:
                        if peak_working_set() > MEMORY_LIMIT:
                            raise RuntimeError('8 GiB working-set ceiling exceeded')
                        if time.monotonic() - started > TIME_LIMIT:
                            raise RuntimeError('60-minute runtime ceiling exceeded')
                        if shutil.disk_usage(OUTPUT.parent).free < MIN_END_FREE:
                            raise RuntimeError('10 GiB disk reserve breached')
    expected = planned.counts
    if counts != expected or sum(counts.values()) != (
        frozen_boundary['train_count'] + frozen_boundary['validation_count']
        + frozen_boundary['test_count']
    ):
        raise ValueError('published partition counts do not reconcile')
    id_hashes = {name: digest.hexdigest() for name, digest in identities.items()}
    manifest = {
        'format': 'hi-small-ibm-day-60-20-20-features-v1',
        'source_sha256': SOURCE_SHA,
        'parent_feature_manifest_sha256': OLD_FEATURE_MANIFEST_SHA,
        'method': 'whole_utc_day_boundaries_minimize_max_relative_target_share_error',
        'target_shares': {'train': 0.6, 'validation': 0.2, 'test': 0.2},
        'warmup_rows_excluded_from_partitions': 1_114_921,
        'showcase_rows_excluded_from_experiment': old_manifest['counts']['showcase'],
        'chronological': True,
        'cutoffs_inclusive_utc_day': {
            'train_end': train_cut.isoformat(),
            'validation_end': validation_cut.isoformat(),
            'test_end': frozen_boundary['development_end_utc'],
        },
        'counts': counts,
        'daily_counts': [{'utc_day': day.isoformat(), 'count': count}
                         for day, count in planned.daily_counts],
        'partition_scoreable_id_sha256': id_hashes,
        'label_values_read': False,
        'files': {name: sha256_file(path) for name, path in targets.items()},
        'resource_ceilings': {
            'initial_free_disk_bytes_min': MIN_START_FREE,
            'ending_free_disk_bytes_min': MIN_END_FREE,
            'peak_working_set_bytes_max': MEMORY_LIMIT,
            'elapsed_seconds_max': TIME_LIMIT,
        },
    }
    (stage_root / 'manifest.json').write_bytes(canonical_json_bytes(manifest) + b'\n')
    if peak_working_set() > MEMORY_LIMIT or shutil.disk_usage(OUTPUT.parent).free < MIN_END_FREE:
        raise RuntimeError('resource ceiling failed before publication completion')
    stage_root.rename(OUTPUT)
    stage_context.cleanup()
    print(json.dumps({
        'output': str(OUTPUT.relative_to(ROOT)),
        'manifest_sha256': sha256_file(OUTPUT / 'manifest.json'),
        'counts': counts,
        'cutoffs': manifest['cutoffs_inclusive_utc_day'],
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'peak_working_set_bytes': peak_working_set(),
        'initial_free_bytes': initial_free,
        'end_free_bytes': shutil.disk_usage(OUTPUT.parent).free,
    }, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print(f'IBM-style split publication stopped: {error}', file=sys.stderr)
        sys.exit(1)
