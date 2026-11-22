"""Synthetic checks for T218 count freeze and FR-018 exact tolerance."""

import importlib.util
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from fraudlens.data.partitions import plan_partitions


def runner():
    path = Path(__file__).resolve().parents[3] / 'evidence/tasks/T218-audit.py'
    spec = importlib.util.spec_from_file_location('t218_audit_runner', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_count_only_boundaries_match_synthetic_partition_contract(monkeypatch):
    module = runner()
    monkeypatch.setattr(module, 'TARGET', 22)
    t0 = datetime(2022, 9, 1, tzinfo=timezone.utc)
    minute_groups = [(0, 1), *((1440 + minute, 1) for minute in range(20)),
                     (1460, 2), (1461, 1)]
    rows = []
    counts = Counter()
    for minute, size in minute_groups:
        stamp = (t0 + timedelta(minutes=minute)).strftime('%Y/%m/%d %H:%M')
        counts[stamp] = size
        for _ in range(size):
            number = len(rows) + 1
            rows.append({'source_row_number': number,
                         'transaction_id': f'synthetic-{number}', 'timestamp': stamp})
    plan = plan_partitions(rows, development_target=22)
    frozen = module._boundaries(counts, {'accepted_count': len(rows)}, 'synthetic-manifest')

    for partition in ('warmup', 'scoreable', 'development', 'showcase',
                      'train', 'validation', 'test'):
        assert frozen[f'{partition}_count'] == getattr(plan, f'{partition}_count')
    assert frozen['development_end_utc'] == plan.development_end_utc.isoformat()
    assert frozen['train_end_utc'] == plan.train_end_utc.isoformat()
    assert frozen['validation_end_utc'] == plan.validation_end_utc.isoformat()


@pytest.mark.parametrize(('positives', 'expected'), [(15, True), (25, True),
                                                   (14, False), (26, False)])
def test_prevalence_tolerance_has_inclusive_exact_edges(positives, expected):
    module = runner()
    result = module._tolerance({
        'overall_development_scoreable_count': 100,
        'overall_development_positive_count': 20,
        'partition_totals': [
            {'partition': 'train', 'scoreable_count': 100,
             'positive_count': positives},
            {'partition': 'validation', 'scoreable_count': 100,
             'positive_count': 20},
            {'partition': 'test', 'scoreable_count': 100,
             'positive_count': 20},
        ],
        'showcase_total': {'source_count': 100, 'scoreable_count': 100,
                           'positive_count': 20},
    })
    assert result['partitions'][0]['prevalence_0_75_to_1_25_pass'] is expected
    assert result['pass'] is (expected and positives >= 20)
