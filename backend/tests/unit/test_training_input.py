"""Synthetic RED checks for a label-free chronological training-input publisher."""

import hashlib
import json

import pytest

from fraudlens.data.training_input import publish_training_features

SOURCE = 'a' * 64
TIMES = (
    '2022/09/01 00:00', '2022/09/02 00:00', '2022/09/02 01:00',
    '2022/09/02 02:00', '2022/09/02 03:00',
)


def row(number, timestamp, label):
    return (json.dumps({
        'amount_paid': '10.00', 'amount_received': '10.00',
        'is_laundering': label, 'payment_currency': 'USD',
        'payment_format': 'Wire', 'receiver_account': 'R1',
        'receiver_bank': 'B1', 'receiver_key': 'B1:R1',
        'receiving_currency': 'USD', 'sender_account': 'S1',
        'sender_bank': 'B1', 'sender_key': 'B1:S1',
        'source_row_number': number, 'source_sha256': SOURCE,
        'timestamp': timestamp, 'transaction_id': f'ibm-hi-small:{SOURCE}:row:{number}',
    }, sort_keys=True, separators=(',', ':')).encode() + b'\n')


def boundary():
    return {
        'source_sha256': SOURCE, 'accepted_count': 5,
        'warmup_count': 1, 'development_count': 4, 'showcase_count': 1,
        'train_count': 1, 'validation_count': 1, 'test_count': 1,
        'warmup_end_exclusive_utc': '2022-09-02T00:00:00+00:00',
        'train_end_utc': '2022-09-02T00:00:00+00:00',
        'validation_end_utc': '2022-09-02T01:00:00+00:00',
        'development_end_utc': '2022-09-02T02:00:00+00:00',
    }


def hashes():
    ids = {name: [f'ibm-hi-small:{SOURCE}:row:{index}'] for name, index in (
        ('train', 2), ('validation', 3), ('test', 4), ('showcase', 5),
    )}
    ids['development'] = [ids[name][0] for name in ('train', 'validation', 'test')]
    return {name: hashlib.sha256(('\n'.join(values) + '\n').encode()).hexdigest()
            for name, values in ids.items()}


def test_publishes_only_verified_scoreable_features_without_labels(tmp_path):
    lines = [row(i, TIMES[i - 1], i % 2) for i in (5, 3, 1, 4, 2)]
    destination = tmp_path / 'features'
    manifest = publish_training_features(lines, boundary(), hashes(), destination)
    assert manifest['counts'] == {'warmup': 1, 'train': 1, 'validation': 1,
                                  'test': 1, 'showcase': 1}
    assert manifest['partition_scoreable_id_sha256'] == hashes()
    for name in ('train', 'validation', 'test', 'showcase'):
        raw = (destination / f'{name}.jsonl').read_bytes()
        assert b'is_laundering' not in raw
        record = json.loads(raw)
        assert set(record['features']) == set(manifest['feature_order'])
    train = json.loads((destination / 'train.jsonl').read_bytes())
    assert train['features']['sender_out_count_24h'] == 1


def test_label_changes_do_not_change_feature_publication(tmp_path):
    first = [row(i, TIMES[i - 1], i % 2) for i in range(1, 6)]
    second = [row(i, TIMES[i - 1], (i + 1) % 2) for i in range(1, 6)]
    publish_training_features(first, boundary(), hashes(), tmp_path / 'first')
    publish_training_features(second, boundary(), hashes(), tmp_path / 'second')
    for name in ('train', 'validation', 'test', 'showcase'):
        assert (tmp_path / 'first' / f'{name}.jsonl').read_bytes() == (
            tmp_path / 'second' / f'{name}.jsonl').read_bytes()


def test_full_source_requires_explicit_higher_row_ceiling(tmp_path):
    frozen = boundary()
    frozen['accepted_count'] = 5_078_345
    with pytest.raises(ValueError, match='ceiling'):
        publish_training_features([], frozen, hashes(), tmp_path / 'features')


def test_missing_canonical_label_field_fails_before_publication(tmp_path):
    lines = [row(i, TIMES[i - 1], 0) for i in range(1, 6)]
    lines[0] = lines[0].replace(b',"is_laundering":0', b'')
    with pytest.raises(ValueError, match='label field'):
        publish_training_features(lines, boundary(), hashes(), tmp_path / 'features')
    assert not (tmp_path / 'features').exists()


@pytest.mark.parametrize('damage', [
    'wrong_source', 'duplicate_row', 'wrong_hash', 'missing_row', 'overwrite',
])
def test_mismatch_refuses_publication(tmp_path, damage):
    lines = [row(i, TIMES[i - 1], 0) for i in range(1, 6)]
    frozen = hashes()
    target = tmp_path / 'features'
    if damage == 'wrong_source':
        changed = json.loads(lines[0])
        changed['source_sha256'] = 'b' * 64
        lines[0] = json.dumps(changed).encode() + b'\n'
    elif damage == 'duplicate_row':
        lines[-1] = lines[0]
    elif damage == 'wrong_hash':
        frozen['test'] = 'b' * 64
    elif damage == 'missing_row':
        lines.pop()
    else:
        target.mkdir()
    with pytest.raises(ValueError):
        publish_training_features(lines, boundary(), frozen, target)
    if damage != 'overwrite':
        assert not target.exists()
