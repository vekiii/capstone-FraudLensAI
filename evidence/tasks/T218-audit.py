"""T218 local count-only freeze and restricted aggregate audit.

Run ``count`` first. Run ``audit`` only with the printed boundary SHA-256.
Outputs stay in ignored data/processed; never print or persist record labels.
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from bisect import bisect_left
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fraudlens.data.manifest import atomic_write_json, sha256_file, verify_completed_snapshot

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / 'data/processed/t210-hi-small-b19d39f5'
OUTPUT = ROOT / 'data/processed/t218-hi-small-b19d39f5'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
TARGET = 3_000_000
MIN_FREE_BYTES = 10 * 1024**3
TIMESTAMP = re.compile(rb'"timestamp":"(\d{4}/\d{2}/\d{2} \d{2}:\d{2})"')
PARTITIONS = ('train', 'validation', 'test', 'showcase')


def _preflight() -> dict:
    if shutil.disk_usage(OUTPUT.parent).free < MIN_FREE_BYTES:
        raise RuntimeError('T218 disk reserve below 10 GiB')
    manifest = verify_completed_snapshot(SNAPSHOT)
    if manifest['source_sha256'] != SOURCE_SHA or manifest['accepted_count'] != 5_078_345:
        raise RuntimeError('T218 verified source identity/count mismatch')
    return manifest


def _boundaries(groups: Counter[str], manifest: dict, manifest_sha256: str) -> dict:
    ordered = sorted(groups.items())
    if len(ordered) < 5:
        raise RuntimeError('too few whole timestamp groups')
    times = [datetime.strptime(text, '%Y/%m/%d %H:%M').replace(tzinfo=timezone.utc)
             for text, _ in ordered]
    counts = [count for _, count in ordered]
    cumulative = []
    current = 0
    for count in counts:
        current += count
        cumulative.append(current)
    development_count = min(
        cumulative[:-1], key=lambda count: (abs(count - TARGET), count),
    )
    development_index = cumulative.index(development_count)
    t0 = times[0]
    warmup_end = t0 + timedelta(hours=24)
    warmup_count = sum(count for instant, count in zip(times, counts)
                       if instant < warmup_end)
    if warmup_count >= development_count:
        raise RuntimeError('no scoreable development rows')
    scoreable_count = current - warmup_count
    scoreable_dev_count = development_count - warmup_count
    first_scoreable = next(index for index, instant in enumerate(times)
                           if instant >= warmup_end)
    scoreable_prefix = []
    scoreable_so_far = 0
    for count in counts[first_scoreable:development_index + 1]:
        scoreable_so_far += count
        scoreable_prefix.append(scoreable_so_far)
    if len(scoreable_prefix) < 3:
        raise RuntimeError('nonempty train/validation/test split impossible')
    candidates = scoreable_prefix[:-1]
    scaled = [20 * value for value in candidates]
    pairs = []
    for index, train in enumerate(candidates[:-1]):
        first_validation = index + 1
        insertion = bisect_left(scaled, 17 * scoreable_dev_count, lo=first_validation)
        for candidate in (insertion - 1, insertion):
            if first_validation <= candidate < len(candidates):
                pairs.append((train, candidates[candidate]))
    train_count, validation_end = min(
        pairs,
        key=lambda pair: (
            abs(10 * pair[0] - 7 * scoreable_dev_count),
            abs(20 * pair[1] - 17 * scoreable_dev_count),
            pair[0], pair[1],
        ),
    )
    train_index = first_scoreable + scoreable_prefix.index(train_count)
    validation_index = first_scoreable + scoreable_prefix.index(validation_end)
    return {
        'format': 't218-count-only-v1',
        'source_sha256': SOURCE_SHA,
        'snapshot_manifest_sha256': manifest_sha256,
        'accepted_count': manifest['accepted_count'],
        't0_utc': t0.isoformat(),
        'max_utc': times[-1].isoformat(),
        'warmup_end_exclusive_utc': warmup_end.isoformat(),
        'warmup_count': warmup_count,
        'scoreable_count': scoreable_count,
        'development_count': development_count,
        'showcase_count': current - development_count,
        'development_end_utc': times[development_index].isoformat(),
        'train_end_utc': times[train_index].isoformat(),
        'validation_end_utc': times[validation_index].isoformat(),
        'train_count': train_count,
        'validation_count': validation_end - train_count,
        'test_count': scoreable_dev_count - validation_end,
        'timestamp_group_count': len(ordered),
        'target_source_count': TARGET,
    }


def count_only() -> None:
    started = time.monotonic()
    manifest = _preflight()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    boundary_path = OUTPUT / 'boundaries.json'
    if boundary_path.exists():
        raise RuntimeError('count-only boundaries already exist; refusing overwrite')
    groups: Counter[str] = Counter()
    scanned = 0
    with (SNAPSHOT / 'accepted.jsonl').open('rb') as stream:
        for line in stream:
            match = TIMESTAMP.search(line)
            if match is None or TIMESTAMP.search(line, match.end()) is not None:
                raise RuntimeError('timestamp field missing or duplicated')
            groups[match.group(1).decode('ascii')] += 1
            scanned += 1
    if scanned != manifest['accepted_count']:
        raise RuntimeError('count-only scan did not reconcile with verified snapshot')
    result = _boundaries(groups, manifest, sha256_file(SNAPSHOT / 'manifest.json'))
    atomic_write_json(boundary_path, result)
    print(json.dumps({
        'phase': 'count', 'rows': scanned, 'timestamp_groups': len(groups),
        'boundary_sha256': sha256_file(boundary_path),
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'free_bytes': shutil.disk_usage(OUTPUT).free,
        'boundaries': result,
    }, sort_keys=True))


def _log(path: Path, *, shape: str, result: str, boundary_sha256: str) -> None:
    event = {
        'time': datetime.now(timezone.utc).isoformat(),
        'purpose': 'pretraining_class_audit',
        'query': {'shape': shape, 'boundary_sha256': boundary_sha256},
        'result': result,
    }
    encoded = (json.dumps(event, sort_keys=True, separators=(',', ':')) + '\n').encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, 'ab') as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _classify(timestamp: str, cutoffs: tuple[str, str, str, str]) -> str:
    warmup_end, development_end, train_end, validation_end = cutoffs
    if timestamp < warmup_end:
        return 'development_warmup'
    if timestamp > development_end:
        return 'showcase'
    if timestamp <= train_end:
        return 'train'
    if timestamp <= validation_end:
        return 'validation'
    return 'test'


def _audit_results(path: Path, boundary: dict) -> dict:
    daily: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    totals = {partition: [0, 0] for partition in PARTITIONS}
    showcase_source = 0
    warmup_count = 0
    rows = 0
    cutoffs = tuple(
        datetime.fromisoformat(boundary[name]).strftime('%Y/%m/%d %H:%M')
        for name in ('warmup_end_exclusive_utc', 'development_end_utc',
                     'train_end_utc', 'validation_end_utc')
    )
    with path.open('r', encoding='utf-8') as stream:
        for line in stream:
            record = json.loads(line)
            timestamp = record['timestamp']
            if (not isinstance(timestamp, str) or len(timestamp) != 16
                    or timestamp[4] != '/' or timestamp[7] != '/'
                    or timestamp[10] != ' ' or timestamp[13] != ':'):
                raise RuntimeError('audit timestamp differs from validated source form')
            partition = _classify(timestamp, cutoffs)
            if partition == 'development_warmup':
                warmup_count += 1
            else:
                label = record['is_laundering']
                if label not in ('0', '1'):
                    raise RuntimeError('invalid canonical label')
                totals[partition][0] += 1
                totals[partition][1] += int(label)
                if partition == 'showcase':
                    showcase_source += 1
                else:
                    day = timestamp[:10].replace('/', '-')
                    daily[day][0] += 1
                    daily[day][1] += int(label)
            rows += 1
    if rows != boundary['accepted_count'] or warmup_count != boundary['warmup_count']:
        raise RuntimeError('audit row/warm-up counts disagree with frozen boundaries')
    if any(totals[p][0] != boundary[f'{p}_count'] for p in PARTITIONS):
        raise RuntimeError('audit partition counts disagree with frozen boundaries')
    if sum(value[0] for value in daily.values()) != (
        boundary['development_count'] - boundary['warmup_count']
    ):
        raise RuntimeError('audit development daily counts disagree with boundaries')
    return {
        'development_daily': [
            {'utc_day': day, 'scoreable_count': count, 'positive_count': positives}
            for day, (count, positives) in sorted(daily.items())
        ],
        'partition_totals': [
            {'partition': partition, 'scoreable_count': totals[partition][0],
             'positive_count': totals[partition][1]}
            for partition in ('train', 'validation', 'test')
        ],
        'showcase_total': {
            'source_count': showcase_source,
            'scoreable_count': totals['showcase'][0],
            'positive_count': totals['showcase'][1],
        },
        'overall_development_scoreable_count': sum(totals[p][0] for p in PARTITIONS[:3]),
        'overall_development_positive_count': sum(totals[p][1] for p in PARTITIONS[:3]),
    }


def _tolerance(results: dict) -> dict:
    dev_count = results['overall_development_scoreable_count']
    dev_positive = results['overall_development_positive_count']
    partitions = [*results['partition_totals'],
                  {'partition': 'showcase', **results['showcase_total']}]
    checked = []
    for item in partitions:
        count = item['scoreable_count']
        positive = item['positive_count']
        minimum_positive = positive >= 20
        prevalence_in_range = (
            dev_count > 0 and dev_positive > 0 and count > 0
            and 4 * positive * dev_count >= 3 * dev_positive * count
            and 4 * positive * dev_count <= 5 * dev_positive * count
        )
        checked.append({
            'partition': item['partition'],
            'minimum_20_positive_pass': minimum_positive,
            'prevalence_0_75_to_1_25_pass': prevalence_in_range,
            'pass': minimum_positive and prevalence_in_range,
        })
    return {'rule': 'FR-018 inclusive exact-integer comparisons',
            'partitions': checked, 'pass': all(item['pass'] for item in checked)}


def audit(expected_sha256: str) -> None:
    started = time.monotonic()
    manifest = _preflight()
    boundary_path = OUTPUT / 'boundaries.json'
    actual_sha256 = sha256_file(boundary_path)
    if actual_sha256 != expected_sha256:
        raise RuntimeError('count-only boundary hash mismatch; audit stopped')
    boundary = json.loads(boundary_path.read_text(encoding='utf-8'))
    if (boundary['source_sha256'] != SOURCE_SHA
            or boundary['snapshot_manifest_sha256'] != sha256_file(SNAPSHOT / 'manifest.json')
            or boundary['accepted_count'] != manifest['accepted_count']):
        raise RuntimeError('frozen boundary provenance mismatch; audit stopped')
    log_path = OUTPUT / 'label-access.jsonl'
    result_path = OUTPUT / 'aggregate-audit.json'
    if log_path.exists() or result_path.exists():
        raise RuntimeError('aggregate audit already attempted; refusing a second showcase total')
    _log(log_path, shape='development_daily', result='started',
         boundary_sha256=actual_sha256)
    try:
        results = _audit_results(SNAPSHOT / 'accepted.jsonl', boundary)
        decision = _tolerance(results)
        report = {
            'format': 't218-restricted-aggregate-v1',
            'boundary_sha256': actual_sha256,
            'source_sha256': SOURCE_SHA,
            'results': results,
            'tolerance': decision,
        }
        atomic_write_json(result_path, report)
        for shape in ('development_daily', 'partition_totals', 'showcase_total'):
            _log(log_path, shape=shape, result='allowed',
                 boundary_sha256=actual_sha256)
    except BaseException:
        _log(log_path, shape='aggregate_audit', result='error',
             boundary_sha256=actual_sha256)
        raise
    print(json.dumps({
        'phase': 'audit', 'report_sha256': sha256_file(result_path),
        'boundary_sha256': actual_sha256,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'free_bytes': shutil.disk_usage(OUTPUT).free,
        'partition_totals': results['partition_totals'],
        'showcase_total': results['showcase_total'],
        'overall_development_scoreable_count': results['overall_development_scoreable_count'],
        'overall_development_positive_count': results['overall_development_positive_count'],
        'tolerance': decision,
    }, sort_keys=True))
    if not decision['pass']:
        raise RuntimeError('FR-018 aggregate audit tolerance failed; downstream training stopped')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('count', 'audit'))
    parser.add_argument('--boundary-sha256')
    arguments = parser.parse_args()
    if arguments.phase == 'count':
        if arguments.boundary_sha256 is not None:
            parser.error('count phase does not accept a boundary hash')
        count_only()
    else:
        if not arguments.boundary_sha256 or len(arguments.boundary_sha256) != 64:
            parser.error('audit phase requires --boundary-sha256')
        audit(arguments.boundary_sha256)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(f'T218 stopped: {error}', file=sys.stderr)
        sys.exit(1)
