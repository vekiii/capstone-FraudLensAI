"""Identity and no-prevalence-gate checks for FR-021 research v2."""

import hashlib

import pytest

from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
from fraudlens.data.manifest import canonical_json_bytes
from fraudlens.training.protocol import ProtocolError, verify_research_protocol

_SOURCE = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
_FEATURE = 'a' * 64
_LABELS = 'b' * 64
_PARENT = 'c' * 64
_IDS = {name: hashlib.sha256(name.encode()).hexdigest()
        for name in ('train', 'validation', 'test')}


def protocol_fixture():
    counts = {'train': 5, 'validation': 4, 'test': 3}
    class_distribution = {
        'train': {'rows': 5, 'positive': 1, 'negative': 4, 'prevalence': 0.2},
        'validation': {'rows': 4, 'positive': 3, 'negative': 1, 'prevalence': 0.75},
        'test': {'rows': 3, 'positive': 0, 'negative': 3, 'prevalence': 0.0},
    }
    protocol = {
        'format': 'fraudlens-fr021-training-protocol-v2',
        'dataset_sha256': _SOURCE,
        'feature_version': FEATURE_VERSION,
        'feature_order': list(FEATURE_ORDER),
        'split_method': {
            'label_values_used_for_boundaries': False,
            'targets': {'train': 0.6, 'validation': 0.2, 'test': 0.2},
        },
        'research_feature_manifest_sha256': _FEATURE,
        'feature_manifest_sha256': _PARENT,
        'research_label_manifest_sha256': _LABELS,
        'research_partition_scoreable_id_sha256': _IDS,
        'research_partition_counts': counts,
        'partition_boundaries': {
            'research_train_end_utc_day_inclusive': '2022-09-04',
            'research_validation_end_utc_day_inclusive': '2022-09-05',
            'research_test_end_utc': '2022-09-06T11:12:00+00:00',
        },
        'class_distribution': class_distribution,
        'fr018': {'minimum_positive_gate': False, 'prevalence_ratio_gate': False},
    }
    features = {
        'source_sha256': _SOURCE,
        'parent_feature_manifest_sha256': _PARENT,
        'feature_version': FEATURE_VERSION,
        'feature_order': list(FEATURE_ORDER),
        'partition_scoreable_id_sha256': _IDS,
        'counts': counts,
        'cutoffs_inclusive_utc_day': {
            'train_end': '2022-09-04', 'validation_end': '2022-09-05',
            'test_end': '2022-09-06T11:12:00+00:00',
        },
    }
    labels = {
        'source_sha256': _SOURCE,
        'feature_manifest_sha256': _FEATURE,
        'scope': 'train_and_validation_only',
        'counts': {
            'train': {'rows': 5, 'positive': 1, 'negative': 4},
            'validation': {'rows': 4, 'positive': 3, 'negative': 1},
        },
    }
    return protocol, features, labels


def verify(protocol, features, labels):
    digest = hashlib.sha256(canonical_json_bytes(protocol)).hexdigest()
    verify_research_protocol(protocol, digest, features, labels, _FEATURE, _LABELS)


def test_class_imbalance_is_diagnostic_without_minimum_or_ratio_gates():
    protocol, features, labels = protocol_fixture()

    verify(protocol, features, labels)


def test_research_protocol_rejects_digest_or_partition_identity_mismatch():
    protocol, features, labels = protocol_fixture()
    digest = hashlib.sha256(canonical_json_bytes(protocol)).hexdigest()
    features['counts'] = {**features['counts'], 'test': 4}
    with pytest.raises(ProtocolError, match='partition IDs or counts'):
        verify_research_protocol(protocol, digest, features, labels, _FEATURE, _LABELS)


def test_research_protocol_rejects_reintroduced_fr018_gates():
    protocol, features, labels = protocol_fixture()
    protocol['fr018']['prevalence_ratio_gate'] = True
    with pytest.raises(ProtocolError, match='Retired FR-018 gates'):
        verify(protocol, features, labels)
