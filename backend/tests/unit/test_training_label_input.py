"""Restricted synthetic train/validation label publication checks."""

import json

import pytest
from test_training_input import TIMES, boundary, hashes, row

from fraudlens.data.training_input import publish_training_features
from fraudlens.training.label_input import publish_training_labels


def accepted_row(index):
    raw = row(index, TIMES[index - 1], index % 2)
    return raw.replace(
        b',"is_laundering":' + str(index % 2).encode(),
        b',"is_laundering":"' + str(index % 2).encode() + b'"',
    )


def test_only_train_and_validation_labels_are_published(tmp_path):
    lines = [accepted_row(i) for i in (5, 3, 1, 4, 2)]
    features = tmp_path / 'features'
    publish_training_features(lines, boundary(), hashes(), features)
    result = publish_training_labels(lines, features, boundary(), hashes(), tmp_path / 'labels')
    assert result['counts'] == {'train': 1, 'validation': 1}
    assert set(path.name for path in (tmp_path / 'labels').iterdir()) == {
        'train.jsonl', 'validation.jsonl', 'manifest.json',
    }
    assert json.loads((tmp_path / 'labels/train.jsonl').read_bytes())['label'] == 0
    assert json.loads((tmp_path / 'labels/validation.jsonl').read_bytes())['label'] == 1


def test_test_showcase_and_warmup_label_tokens_are_never_parsed(tmp_path):
    lines = [accepted_row(i) for i in range(1, 6)]
    features = tmp_path / 'features'
    publish_training_features(lines, boundary(), hashes(), features)
    for index in (0, 3, 4):
        lines[index] = lines[index].replace(
            b',"is_laundering":"' + str((index + 1) % 2).encode() + b'"',
            b',"is_laundering":unread_token',
        )
    publish_training_labels(lines, features, boundary(), hashes(), tmp_path / 'labels')
    assert b'unread_token' not in (tmp_path / 'labels/train.jsonl').read_bytes()


def test_wrong_train_label_stops_publication(tmp_path):
    lines = [accepted_row(i) for i in range(1, 6)]
    features = tmp_path / 'features'
    publish_training_features(lines, boundary(), hashes(), features)
    lines[1] = lines[1].replace(b',"is_laundering":"0"', b',"is_laundering":"2"')
    with pytest.raises(ValueError, match='train/validation label'):
        publish_training_labels(lines, features, boundary(), hashes(), tmp_path / 'labels')
    assert not (tmp_path / 'labels').exists()


def test_misaligned_features_stop_label_publication(tmp_path):
    lines = [accepted_row(i) for i in range(1, 6)]
    features = tmp_path / 'features'
    publish_training_features(lines, boundary(), hashes(), features)
    (features / 'train.jsonl').write_bytes(b'changed\n')
    with pytest.raises(ValueError, match='feature file'):
        publish_training_labels(lines, features, boundary(), hashes(), tmp_path / 'labels')
