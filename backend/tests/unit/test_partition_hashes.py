"""Synthetic label-free ID hash publication cases for T219."""

import hashlib

import pytest

from fraudlens.data.partition_hashes import hash_partition_ids

SOURCE = 'a' * 64
BOUNDARIES = {
    'source_sha256': SOURCE,
    'accepted_count': 7,
    'warmup_count': 1,
    'development_count': 5,
    'showcase_count': 2,
    'train_count': 2,
    'validation_count': 1,
    'test_count': 1,
    'warmup_end_exclusive_utc': '2022-09-02T00:00:00+00:00',
    'development_end_utc': '2022-09-02T03:00:00+00:00',
    'train_end_utc': '2022-09-02T01:00:00+00:00',
    'validation_end_utc': '2022-09-02T02:00:00+00:00',
}


def _rows():
    times = ['2022/09/01 00:00', '2022/09/02 01:00', '2022/09/02 01:00',
             '2022/09/02 02:00', '2022/09/02 03:00', '2022/09/02 04:00',
             '2022/09/02 04:00']
    for number in (7, 3, 1, 6, 4, 2, 5):
        yield times[number - 1], number, f'ibm-hi-small:{SOURCE}:row:{number}'


def _hash(*numbers):
    return hashlib.sha256(''.join(
        f'ibm-hi-small:{SOURCE}:row:{number}\n' for number in numbers
    ).encode()).hexdigest()


def test_external_merge_hashes_utc_then_source_row_and_reconciles(tmp_path):
    result = hash_partition_ids(_rows(), BOUNDARIES, tmp_path, chunk_size=2)
    assert result['partition_scoreable_id_sha256'] == {
        'development': _hash(2, 3, 4, 5), 'showcase': _hash(6, 7),
        'train': _hash(2, 3), 'validation': _hash(4), 'test': _hash(5),
    }
    assert result['partition_counts'] == {
        'development': 4, 'showcase': 2, 'train': 2, 'validation': 1, 'test': 1,
    }


def test_duplicate_identity_stops(tmp_path):
    rows = list(_rows())
    rows[-1] = rows[0]
    with pytest.raises(ValueError):
        hash_partition_ids(rows, BOUNDARIES, tmp_path, chunk_size=2)


def test_tampered_frozen_count_stops(tmp_path):
    boundary = {**BOUNDARIES, 'train_count': 3}
    with pytest.raises(ValueError):
        hash_partition_ids(_rows(), boundary, tmp_path, chunk_size=2)
