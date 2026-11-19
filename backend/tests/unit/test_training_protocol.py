"""Synthetic FR-021 prefit gate cases; no real record labels are accessed."""

import hashlib
import json

import pytest

from fraudlens.training.protocol import ProtocolError, verify_prefit_protocol


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _fixture():
    source = b'synthetic source'
    boundaries = b'synthetic boundaries'
    ids = {'train': b'id-1\n', 'validation': b'id-2\n',
           'test': b'id-3\n', 'showcase': b'id-4\n',
           'development': b'id-1\nid-2\nid-3\n'}
    protocol = {
        'dataset_sha256': hashlib.sha256(source).hexdigest(),
        'boundary_sha256': hashlib.sha256(boundaries).hexdigest(),
        'partition_scoreable_id_sha256': {key: hashlib.sha256(value).hexdigest()
                                         for key, value in ids.items()},
        'timezone_policy': 'naive_source_as_UTC', 'warmup_rule': '[t0,t0+24h)',
        'feature_version': 'hi-small-temporal-v1', 'feature_order': ['synthetic_feature'],
        'partition_boundaries': {'train_end_utc': '2022-09-05T00:00:00+00:00'},
        'partition_counts': {'train': 1, 'validation': 1, 'test': 1, 'showcase': 1},
        'allowed_prevalence': {'minimum_ratio': 0.75, 'maximum_ratio': 1.25},
        'seed': 42, 'tie_rules': 'earlier_boundary',
        'preprocessing': {'fit_on': 'train_only'}, 'imbalance_option': 'none',
        'candidate_grid': ['constant'], 'metrics': ['average_precision', 'precision_at_20'],
        'threshold_objective': 'synthetic_fixed', 'resource_ceilings': {'memory_mib': 512},
        'label_rules': 'restricted', 'showcase_role': 'demo_only_record_labels_unread',
        'audit_passed': True, 'provenance_complete': True,
    }
    observed = {
        'dataset_sha256': hashlib.sha256(source).hexdigest(),
        'boundary_sha256': hashlib.sha256(boundaries).hexdigest(),
        'partition_scoreable_id_sha256': {key: hashlib.sha256(value).hexdigest()
                                         for key, value in ids.items()},
    }
    return protocol, observed


def test_matching_complete_synthetic_protocol_is_admitted():
    protocol, observed = _fixture()
    verify_prefit_protocol(protocol, _digest(protocol), observed)


@pytest.mark.parametrize('field', ['dataset_sha256', 'boundary_sha256',
                                   'partition_scoreable_id_sha256'])
def test_any_observed_hash_mismatch_stops(field):
    protocol, observed = _fixture()
    observed[field] = {} if field.endswith('id_sha256') else '0' * 64
    with pytest.raises(ProtocolError):
        verify_prefit_protocol(protocol, _digest(protocol), observed)


@pytest.mark.parametrize('field', ['timezone_policy', 'warmup_rule', 'feature_version',
                                   'feature_order', 'partition_boundaries', 'partition_counts',
                                   'allowed_prevalence', 'seed', 'tie_rules', 'preprocessing',
                                   'imbalance_option', 'candidate_grid', 'metrics',
                                   'threshold_objective', 'resource_ceilings', 'label_rules',
                                   'showcase_role', 'partition_scoreable_id_sha256'])
def test_missing_exact_protocol_field_stops(field):
    protocol, observed = _fixture()
    del protocol[field]
    with pytest.raises(ProtocolError):
        verify_prefit_protocol(protocol, _digest(protocol), observed)


@pytest.mark.parametrize('change', ['digest', 'audit', 'provenance', 'role', 'seed'])
def test_tamper_or_unresolved_gate_stops(change):
    protocol, observed = _fixture()
    digest = _digest(protocol)
    if change == 'digest':
        digest = '0' * 64
    elif change == 'audit':
        protocol['audit_passed'] = False
        digest = _digest(protocol)
    elif change == 'provenance':
        protocol['provenance_complete'] = False
        digest = _digest(protocol)
    elif change == 'role':
        protocol['showcase_role'] = 'evaluation'
        digest = _digest(protocol)
    else:
        protocol['seed'] = 7
        digest = _digest(protocol)
    with pytest.raises(ProtocolError):
        verify_prefit_protocol(protocol, digest, observed)


def test_nested_protocol_change_with_old_digest_stops():
    protocol, observed = _fixture()
    frozen_digest = _digest(protocol)
    protocol['partition_counts']['train'] += 1
    with pytest.raises(ProtocolError):
        verify_prefit_protocol(protocol, frozen_digest, observed)
