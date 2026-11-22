"""No-fit tests for the restricted research train/validation label publisher."""

import hashlib
import json

from fraudlens.data.features import FEATURE_ORDER
from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.data.research_labels import publish_research_labels


def _row(identity, number, label):
    source_sha = 'a' * 64
    values = {
        'amount_paid': '1', 'amount_received': '1', 'payment_currency': 'USD',
        'payment_format': 'ACH', 'receiver_account': 'ra', 'receiver_bank': 'rb',
        'receiver_key': 'rk', 'receiving_currency': 'USD', 'sender_account': 'sa',
        'sender_bank': 'sb', 'sender_key': 'sk', 'source_row_number': number,
        'source_sha256': source_sha, 'timestamp': f'2022/09/0{number} 01:00',
        'transaction_id': identity,
    }
    before = {key: values[key] for key in ('transaction_id', 'timestamp')}
    after = {key: value for key, value in values.items()
             if key not in ('transaction_id', 'timestamp')}
    # The project parser requires the is_laundering key between sorted source fields.
    ordered = {**before, 'is_laundering': str(label), **after}
    return json.dumps(ordered, separators=(',', ':')).encode()


def test_publisher_reads_only_research_train_and_validation_labels(tmp_path):
    features = tmp_path / 'features'
    features.mkdir()
    ids = {'train': ['train-1'], 'validation': ['validation-1'], 'test': ['test-1']}
    feature_files = {}
    id_hashes = {}
    for part, identities in ids.items():
        rows = []
        for identity in identities:
            feature = {name: ('USD' if name == 'current_payment_currency' else
                              'ACH' if name == 'current_payment_format' else 0)
                       for name in FEATURE_ORDER}
            rows.append(canonical_json_bytes({
                'transaction_id': identity, 'occurred_at_utc': '2022-09-02T01:00:00+00:00',
                'features': feature,
            }) + b'\n')
        path = features / f'{part}.jsonl'
        path.write_bytes(b''.join(rows))
        feature_files[part] = sha256_file(path)
        id_hashes[part] = hashlib.sha256(''.join(f'{item}\n' for item in identities).encode()
                                        ).hexdigest()
    manifest = {
        'format': 'hi-small-ibm-day-60-20-20-features-v1',
        'source_sha256': 'a' * 64,
        'files': feature_files,
        'partition_scoreable_id_sha256': id_hashes,
    }
    (features / 'manifest.json').write_bytes(canonical_json_bytes(manifest) + b'\n')
    source = [_row('train-1', 2, 1), _row('validation-1', 3, 0), _row('test-1', 4, 1)]

    result = publish_research_labels(source, features, tmp_path / 'labels')

    assert result['counts'] == {
        'train': {'rows': 1, 'positive': 1, 'negative': 0},
        'validation': {'rows': 1, 'positive': 0, 'negative': 1},
    }
    assert result['label_values_read'] == {
        'train': True, 'validation': True, 'test': False,
        'showcase': False, 'warmup': False,
    }
    assert not (tmp_path / 'labels' / 'test.jsonl').exists()
    assert json.loads((tmp_path / 'labels' / 'train.jsonl').read_text())['label'] == 1
