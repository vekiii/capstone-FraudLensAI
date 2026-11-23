"""One-off local HI-Small canonical preparation and non-label quality summary."""

import argparse
import json
import shutil
import sys
import time
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fraudlens.data.manifest import canonical_json_bytes, sha256_bytes, verify_completed_snapshot
from fraudlens.data.pipeline import run_pipeline
from fraudlens.data.source import EXPECTED_HEADER, iter_source_rows, sha256_file

SOURCE = Path('data/raw/HI-Small_Trans.csv')
ROOT = Path('data/processed')
EXPECTED_SHA256 = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
EXPECTED_SIZE = 475_664_283
CHUNK_SIZE = 10_000
RESERVE = 10 * 1024**3
INITIAL_FREE = 20 * 1024**3
RUN_ID = 't210-hi-small-b19d39f5'
STAGE = ROOT / f'.{RUN_ID}.stage'
OUTPUT = ROOT / RUN_ID
REPORT = ROOT / f'{RUN_ID}-quality.json'
FIELDS = (
    'timestamp', 'sender_bank', 'sender_account', 'receiver_bank',
    'receiver_account', 'amount_received', 'receiving_currency',
    'amount_paid', 'payment_currency', 'payment_format',
)
CATEGORIES = ('receiving_currency', 'payment_currency', 'payment_format')
AMOUNTS = ('amount_received', 'amount_paid')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_SIZE:
        raise SystemExit('Source file missing or size mismatch; no ingestion started.')
    actual_hash = sha256_file(SOURCE)
    if actual_hash != EXPECTED_SHA256:
        raise SystemExit('Source hash mismatch; no ingestion started.')
    if OUTPUT.exists() or REPORT.exists():
        raise SystemExit('Output already exists; refusing overwrite.')
    free = shutil.disk_usage(ROOT).free
    if free < INITIAL_FREE:
        raise SystemExit(f'Insufficient initial free space: {free} bytes.')
    config = {
        'source_sha256': EXPECTED_SHA256,
        'source_size_bytes': EXPECTED_SIZE,
        'expected_header': EXPECTED_HEADER,
        'schema': 'fraudlens-source-v1',
        'validator': 'fraudlens-validation-v1',
        'chunk_size': CHUNK_SIZE,
        'checkpoint_cadence_rows': CHUNK_SIZE,
        'min_free_bytes': RESERVE,
        'timestamp_policy': 'preserve source text; conditional UTC later',
    }
    config_hash = sha256_bytes(canonical_json_bytes(config))
    missing = Counter()
    categories = {name: Counter() for name in CATEGORIES}
    category_overflow = Counter()
    minimum = {}
    maximum = {}
    source_rows = 0

    def rows():
        nonlocal source_rows
        for row in iter_source_rows(SOURCE):
            source_rows += 1
            for field in FIELDS:
                value = row[field]
                if not value.strip():
                    missing[field] += 1
            timestamp = row['timestamp']
            if timestamp:
                minimum['timestamp'] = min(minimum.get('timestamp', timestamp), timestamp)
                maximum['timestamp'] = max(maximum.get('timestamp', timestamp), timestamp)
            for field in AMOUNTS:
                try:
                    value = Decimal(row[field])
                except InvalidOperation:
                    continue
                if not value.is_finite():
                    continue
                minimum[field] = min(minimum.get(field, value), value)
                maximum[field] = max(maximum.get(field, value), value)
            for field in CATEGORIES:
                value = row[field]
                if value in categories[field] or len(categories[field]) < 1000:
                    categories[field][value] += 1
                else:
                    category_overflow[field] += 1
            yield row

    started = time.perf_counter()
    print(json.dumps({'event': 'start', 'source_sha256': actual_hash,
                      'source_size_bytes': EXPECTED_SIZE, 'config_hash': config_hash,
                      'initial_free_bytes': free, 'resume': args.resume}), flush=True)
    result = run_pipeline(
        rows(), staging_dir=STAGE, output_dir=OUTPUT,
        source_sha256=actual_hash, config_hash=config_hash,
        chunk_size=CHUNK_SIZE, min_free_bytes=RESERVE, resume=args.resume,
    )
    manifest = verify_completed_snapshot(OUTPUT)
    if result.source_count != source_rows or source_rows != 5_078_345:
        raise SystemExit('Source counts do not match expected observations.')
    report = {
        'report_version': 1,
        'source_sha256': actual_hash,
        'source_size_bytes': EXPECTED_SIZE,
        'source_rows': source_rows,
        'accepted_rows': result.accepted_count,
        'rejected_rows': result.rejected_count,
        'rejection_counts': manifest['rejection_counts'],
        'missing_nonlabel_counts': dict(sorted(missing.items())),
        'source_text_min': {k: str(v) for k, v in sorted(minimum.items())},
        'source_text_max': {k: str(v) for k, v in sorted(maximum.items())},
        'category_counts': {k: dict(sorted(v.items())) for k, v in categories.items()},
        'category_overflow_counts': dict(sorted(category_overflow.items())),
        'label_audit': 'deferred until frozen partitions and authorized restricted audit',
        'warmup_count': None,
        'scoreable_count': None,
        'config': config,
        'config_hash': config_hash,
        'manifest_sha256': sha256_file(OUTPUT / 'manifest.json'),
        'elapsed_seconds_including_verification': round(time.perf_counter() - started, 3),
        'python_version': sys.version.split()[0],
        'remaining_free_bytes': shutil.disk_usage(ROOT).free,
    }
    payload = canonical_json_bytes(report) + b'\n'
    with REPORT.open('xb') as stream:
        stream.write(payload)
    print(json.dumps({'event': 'complete', 'report_sha256': sha256_bytes(payload),
                      'report': report}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
