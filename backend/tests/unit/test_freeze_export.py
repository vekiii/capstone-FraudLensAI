"""Synthetic checks for a label-free, frozen-model export."""

import csv
import hashlib
from datetime import datetime, timezone

import numpy as np
import pytest

from fraudlens.training.freeze_export import (
    verify_validation_reproduction,
    write_test_predictions,
)


class StaticBooster:
    def __init__(self, values):
        self.values = np.asarray(values, dtype=float)

    def predict(self, matrix, *, num_threads):
        assert num_threads == 4
        assert len(matrix) == len(self.values)
        return self.values


def test_validation_and_test_export_roundtrip(tmp_path):
    ids = ['a', 'b', 'c']
    times = [datetime(2022, 9, 5, tzinfo=timezone.utc)] * 3
    saved = tmp_path / 'validation.csv'
    saved.write_text('transaction_id,occurred_at_utc,score\n'
                     + ''.join(f'{identity},2022-09-05T00:00:00+00:00,{score}\n'
                               for identity, score in zip(ids, ('0.1', '0.5', '0.9'))))
    matrix = np.zeros((3, 2))
    verify_validation_reproduction(StaticBooster([0.1, 0.5, 0.9]), matrix,
                                    ids, times, saved)
    expected_id_hash = hashlib.sha256(b'a\nb\nc\n').hexdigest()
    output = tmp_path / 'test-predictions-sealed.csv'
    digest = write_test_predictions(StaticBooster([0.2, 0.6, 0.8]), matrix,
                                    ids, times, expected_id_hash, output)
    assert len(digest) == 64
    with output.open(newline='') as stream:
        assert [row['transaction_id'] for row in csv.DictReader(stream)] == ids


def test_mismatched_validation_and_nonfinite_test_fail(tmp_path):
    ids = ['a']
    times = [datetime(2022, 9, 5, tzinfo=timezone.utc)]
    saved = tmp_path / 'validation.csv'
    saved.write_text('transaction_id,occurred_at_utc,score\na,2022-09-05T00:00:00+00:00,0.2\n')
    with pytest.raises(ValueError, match='validation prediction mismatch'):
        verify_validation_reproduction(StaticBooster([0.3]), np.zeros((1, 2)),
                                        ids, times, saved)
    with pytest.raises(ValueError, match='test scores'):
        write_test_predictions(StaticBooster([np.nan]), np.zeros((1, 2)),
                                ids, times, hashlib.sha256(b'a\n').hexdigest(),
                                tmp_path / 'test.csv')
    with pytest.raises(ValueError, match='ID/order'):
        write_test_predictions(StaticBooster([0.5]), np.zeros((1, 2)),
                                ids, times, '0' * 64, tmp_path / 'wrong-order.csv')
    assert not (tmp_path / 'wrong-order.csv').exists()
