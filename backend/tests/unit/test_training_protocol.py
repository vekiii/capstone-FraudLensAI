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
        'snapshot_manifest_sha256': hashlib.sha256(b'synthetic manifest').hexdigest(),
        'accepted_snapshot_sha256': hashlib.sha256(b'synthetic accepted').hexdigest(),
        'partition_hash_report_sha256': hashlib.sha256(b'synthetic ID report').hexdigest(),
        'feature_manifest_sha256': hashlib.sha256(b'synthetic feature manifest').hexdigest(),
        'training_labels_manifest_sha256': hashlib.sha256(b'synthetic labels manifest').hexdigest(),
        'audit_report_sha256': hashlib.sha256(b'synthetic audit').hexdigest(),
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
        'snapshot_manifest_sha256': protocol['snapshot_manifest_sha256'],
        'accepted_snapshot_sha256': protocol['accepted_snapshot_sha256'],
        'partition_hash_report_sha256': protocol['partition_hash_report_sha256'],
        'feature_manifest_sha256': protocol['feature_manifest_sha256'],
        'training_labels_manifest_sha256': protocol['training_labels_manifest_sha256'],
        'audit_report_sha256': protocol['audit_report_sha256'],
        'partition_scoreable_id_sha256': {key: hashlib.sha256(value).hexdigest()
                                         for key, value in ids.items()},
    }
    return protocol, observed


def test_matching_complete_synthetic_protocol_is_admitted():
    protocol, observed = _fixture()
    verify_prefit_protocol(protocol, _digest(protocol), observed)


@pytest.mark.parametrize('field', ['dataset_sha256', 'boundary_sha256',
                                   'snapshot_manifest_sha256', 'accepted_snapshot_sha256',
                                   'partition_hash_report_sha256', 'audit_report_sha256',
                                   'feature_manifest_sha256', 'training_labels_manifest_sha256',
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


def test_missing_verified_feature_manifest_stops():
    protocol, observed = _fixture()
    del protocol['feature_manifest_sha256']
    with pytest.raises(ProtocolError):
        verify_prefit_protocol(protocol, _digest(protocol), observed)


def test_missing_verified_training_label_manifest_stops():
    protocol, observed = _fixture()
    del protocol['training_labels_manifest_sha256']
    with pytest.raises(ProtocolError):
        verify_prefit_protocol(protocol, _digest(protocol), observed)


@pytest.mark.parametrize('field', ['feature_order', 'partition_boundaries',
                                   'partition_counts', 'preprocessing', 'candidate_grid',
                                   'metrics', 'resource_ceilings'])
def test_empty_structured_protocol_field_stops(field):
    protocol, observed = _fixture()
    protocol[field] = [] if isinstance(protocol[field], list) else {}
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


def _exception_fixture():
    protocol, observed = _fixture()
    report = {
        'format': 't218-restricted-aggregate-v1',
        'source_sha256': protocol['dataset_sha256'],
        'boundary_sha256': protocol['boundary_sha256'],
        'results': {
            'overall_development_scoreable_count': 300,
            'overall_development_positive_count': 60,
            'partition_totals': [
                {'partition': name, 'scoreable_count': 100, 'positive_count': 20}
                for name in ('train', 'validation', 'test')
            ],
            'showcase_total': {'source_count': 100, 'scoreable_count': 100,
                               'positive_count': 30},
        },
        'tolerance': {
            'pass': False,
            'partitions': [
                {'partition': name, 'pass': True,
                 'minimum_20_positive_pass': True,
                 'prevalence_0_75_to_1_25_pass': True}
                for name in ('train', 'validation', 'test')
            ] + [{'partition': 'showcase', 'pass': False,
                  'minimum_20_positive_pass': True,
                  'prevalence_0_75_to_1_25_pass': False}],
        },
    }
    report_bytes = (json.dumps(report, sort_keys=True, separators=(',', ':')) + '\n').encode()
    decision_bytes = b'synthetic human decision'
    protocol['audit_passed'] = False
    protocol['audit_report_sha256'] = hashlib.sha256(report_bytes).hexdigest()
    observed['audit_report_sha256'] = protocol['audit_report_sha256']
    protocol['audit_decision'] = {
        'kind': 'showcase_ratio_diagnostic_after_human_review',
        'source_sha256': protocol['dataset_sha256'],
        'boundary_sha256': protocol['boundary_sha256'],
        'audit_report_sha256': hashlib.sha256(report_bytes).hexdigest(),
        'decision_record_sha256': hashlib.sha256(decision_bytes).hexdigest(),
        'showcase_role': 'demo_only_record_labels_unread',
    }
    observed['audit_report_bytes'] = report_bytes
    observed['decision_record_sha256'] = hashlib.sha256(decision_bytes).hexdigest()
    return protocol, observed


def test_checked_showcase_exception_admits_only_otherwise_complete_protocol():
    protocol, observed = _exception_fixture()
    verify_prefit_protocol(protocol, _digest(protocol), observed)


def test_showcase_exception_does_not_override_incomplete_provenance():
    protocol, observed = _exception_fixture()
    protocol['provenance_complete'] = False
    with pytest.raises(ProtocolError, match='provenance'):
        verify_prefit_protocol(protocol, _digest(protocol), observed)


def _local_copy_fitting_fixture():
    protocol, observed = _exception_fixture()
    source = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
    protocol['dataset_sha256'] = source
    observed['dataset_sha256'] = source
    report = json.loads(observed['audit_report_bytes'])
    report['source_sha256'] = source
    observed['audit_report_bytes'] = (
        json.dumps(report, sort_keys=True, separators=(',', ':')) + '\n'
    ).encode()
    protocol['audit_report_sha256'] = hashlib.sha256(observed['audit_report_bytes']).hexdigest()
    observed['audit_report_sha256'] = protocol['audit_report_sha256']
    protocol['audit_decision']['source_sha256'] = source
    protocol['audit_decision']['audit_report_sha256'] = protocol['audit_report_sha256']
    protocol['provenance_complete'] = False
    decision = b'exact local-copy fitting approved; upstream revision unknown'
    observed['fitting_decision_record_bytes'] = decision
    protocol['provenance_decision'] = {
        'kind': 'exact_local_copy_fitting_after_team_approval',
        'source_sha256': source,
        'snapshot_manifest_sha256': protocol['snapshot_manifest_sha256'],
        'decision_record_sha256': hashlib.sha256(decision).hexdigest(),
    }
    return protocol, observed


def test_checked_exact_local_copy_fitting_decision_admits_incomplete_provenance():
    protocol, observed = _local_copy_fitting_fixture()
    verify_prefit_protocol(protocol, _digest(protocol), observed)


@pytest.mark.parametrize('damage', [
    'missing_decision', 'changed_decision', 'wrong_source', 'wrong_snapshot',
    'wrong_kind', 'other_source',
])
def test_local_copy_fitting_exception_mismatch_stops(damage):
    protocol, observed = _local_copy_fitting_fixture()
    if damage == 'missing_decision':
        del protocol['provenance_decision']
    elif damage == 'changed_decision':
        observed['fitting_decision_record_bytes'] += b' changed'
    elif damage == 'wrong_source':
        protocol['provenance_decision']['source_sha256'] = '0' * 64
    elif damage == 'wrong_snapshot':
        protocol['provenance_decision']['snapshot_manifest_sha256'] = '0' * 64
    elif damage == 'wrong_kind':
        protocol['provenance_decision']['kind'] = 'unreviewed'
    else:
        protocol['dataset_sha256'] = '0' * 64
        observed['dataset_sha256'] = '0' * 64
        protocol['audit_decision']['source_sha256'] = '0' * 64
        report = json.loads(observed['audit_report_bytes'])
        report['source_sha256'] = '0' * 64
        observed['audit_report_bytes'] = (
            json.dumps(report, sort_keys=True, separators=(',', ':')) + '\n'
        ).encode()
        protocol['audit_report_sha256'] = hashlib.sha256(observed['audit_report_bytes']).hexdigest()
        observed['audit_report_sha256'] = protocol['audit_report_sha256']
        protocol['audit_decision']['audit_report_sha256'] = protocol['audit_report_sha256']
        protocol['provenance_decision']['source_sha256'] = '0' * 64
    with pytest.raises(ProtocolError):
        verify_prefit_protocol(protocol, _digest(protocol), observed)


@pytest.mark.parametrize('change', ['report', 'decision', 'source', 'boundary',
                                   'missing', 'development', 'showcase_minimum'])
def test_showcase_exception_mismatch_stops(change):
    protocol, observed = _exception_fixture()
    if change == 'report':
        observed['audit_report_bytes'] += b' '
    elif change == 'decision':
        observed['decision_record_sha256'] = '0' * 64
    elif change == 'source':
        protocol['audit_decision']['source_sha256'] = '0' * 64
    elif change == 'boundary':
        protocol['audit_decision']['boundary_sha256'] = '0' * 64
    elif change == 'missing':
        del protocol['audit_decision']
    else:
        report = json.loads(observed['audit_report_bytes'])
        if change == 'development':
            report['results']['partition_totals'][0]['positive_count'] = 1
        else:
            report['results']['showcase_total']['positive_count'] = 1
        observed['audit_report_bytes'] = (
            json.dumps(report, sort_keys=True, separators=(',', ':')) + '\n'
        ).encode()
        protocol['audit_decision']['audit_report_sha256'] = hashlib.sha256(
            observed['audit_report_bytes']
        ).hexdigest()
        protocol['audit_report_sha256'] = protocol['audit_decision']['audit_report_sha256']
        observed['audit_report_sha256'] = protocol['audit_report_sha256']
    with pytest.raises(ProtocolError):
        verify_prefit_protocol(protocol, _digest(protocol), observed)
