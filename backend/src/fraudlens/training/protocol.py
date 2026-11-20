"""Fail-closed FR-021 check at the boundary before any model fit."""

import json
from collections.abc import Mapping

from fraudlens.data.manifest import canonical_json_bytes, sha256_bytes


class ProtocolError(ValueError):
    """A frozen protocol cannot authorize model fitting."""


_FIELDS = (
    'dataset_sha256', 'boundary_sha256', 'partition_scoreable_id_sha256',
    'snapshot_manifest_sha256', 'accepted_snapshot_sha256',
    'partition_hash_report_sha256', 'audit_report_sha256',
    'timezone_policy', 'warmup_rule', 'feature_version', 'feature_order',
    'partition_boundaries', 'partition_counts', 'allowed_prevalence', 'seed',
    'tie_rules', 'preprocessing', 'imbalance_option', 'candidate_grid',
    'metrics', 'threshold_objective', 'resource_ceilings', 'label_rules',
    'showcase_role', 'audit_passed', 'provenance_complete',
)
_PARTITIONS = frozenset(('development', 'showcase', 'train', 'validation', 'test'))
_APPROVED_LOCAL_SOURCE = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'


def _hash(value: object) -> bool:
    return (isinstance(value, str) and len(value) == 64
            and all(character in '0123456789abcdef' for character in value))


def _count(value: object) -> bool:
    return type(value) is int and value >= 0


def verify_showcase_exception(
    protocol: Mapping[str, object], observed: Mapping[str, object],
) -> None:
    """Bind a post-audit exception to the original aggregate-only report."""
    decision = protocol.get('audit_decision')
    if not isinstance(decision, Mapping) or decision.get('kind') != (
        'showcase_ratio_diagnostic_after_human_review'
    ):
        raise ProtocolError('Human showcase exception is missing.')
    if (decision.get('source_sha256') != protocol['dataset_sha256']
            or decision.get('boundary_sha256') != protocol['boundary_sha256']
            or decision.get('showcase_role') != 'demo_only_record_labels_unread'):
        raise ProtocolError('Human showcase exception identity mismatch.')
    if (not _hash(decision.get('decision_record_sha256'))
            or decision['decision_record_sha256'] != observed.get('decision_record_sha256')):
        raise ProtocolError('Human decision record checksum mismatch.')
    raw_report = observed.get('audit_report_bytes')
    if (not isinstance(raw_report, bytes) or not _hash(decision.get('audit_report_sha256'))
            or sha256_bytes(raw_report) != decision['audit_report_sha256']
            or ('audit_report_sha256' in protocol
                and decision['audit_report_sha256'] != protocol['audit_report_sha256'])):
        raise ProtocolError('Original audit report checksum mismatch.')
    try:
        report = json.loads(raw_report)
    except (ValueError, UnicodeDecodeError):
        raise ProtocolError('Original audit report is malformed.') from None
    if (not isinstance(report, dict)
            or report.get('format') != 't218-restricted-aggregate-v1'
            or report.get('source_sha256') != protocol['dataset_sha256']
            or report.get('boundary_sha256') != protocol['boundary_sha256']):
        raise ProtocolError('Original audit report provenance mismatch.')
    rule = protocol['allowed_prevalence']
    if (not isinstance(rule, Mapping) or rule.get('minimum_ratio') != 0.75
            or rule.get('maximum_ratio') != 1.25):
        raise ProtocolError('Original audit tolerance rule mismatch.')
    try:
        results = report['results']
        tolerance = report['tolerance']
        dev_count = results['overall_development_scoreable_count']
        dev_positive = results['overall_development_positive_count']
        totals = results['partition_totals']
        showcase = results['showcase_total']
        statuses = tolerance['partitions']
        if (not _count(dev_count) or not _count(dev_positive)
                or dev_count == 0 or dev_positive == 0 or dev_positive > dev_count
                or not isinstance(totals, list) or len(totals) != 3
                or not isinstance(showcase, dict)
                or not isinstance(statuses, list) or len(statuses) != 4
                or tolerance['pass'] is not False):
            raise ValueError
        by_name = {item['partition']: item for item in totals}
        checks = {item['partition']: item for item in statuses}
        if (set(by_name) != {'train', 'validation', 'test'}
                or set(checks) != {'train', 'validation', 'test', 'showcase'}):
            raise ValueError
        if (sum(item['scoreable_count'] for item in totals) != dev_count
                or sum(item['positive_count'] for item in totals) != dev_positive):
            raise ValueError
        for name in ('train', 'validation', 'test', 'showcase'):
            item = showcase if name == 'showcase' else by_name[name]
            count, positive = item['scoreable_count'], item['positive_count']
            if (not _count(count) or not _count(positive)
                    or count == 0 or positive > count or positive < 20):
                raise ValueError
            in_range = (4 * positive * dev_count >= 3 * dev_positive * count
                        and 4 * positive * dev_count <= 5 * dev_positive * count)
            status = checks[name]
            if (status['minimum_20_positive_pass'] is not True
                    or status['prevalence_0_75_to_1_25_pass'] is not in_range
                    or status['pass'] is not in_range):
                raise ValueError
            if (name == 'showcase' and in_range) or (name != 'showcase' and not in_range):
                raise ValueError
        if showcase['source_count'] != showcase['scoreable_count']:
            raise ValueError
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ProtocolError('Original audit does not match showcase-only exception.') from None


def verify_local_copy_fitting_decision(
    protocol: Mapping[str, object], observed: Mapping[str, object],
) -> None:
    """Bind the reported team approval to this exact local copy and snapshot."""
    decision = protocol.get('provenance_decision')
    if (not isinstance(decision, Mapping)
            or decision.get('kind') != 'exact_local_copy_fitting_after_team_approval'
            or protocol['dataset_sha256'] != _APPROVED_LOCAL_SOURCE
            or decision.get('source_sha256') != _APPROVED_LOCAL_SOURCE
            or decision.get('snapshot_manifest_sha256') != protocol['snapshot_manifest_sha256']):
        raise ProtocolError('Exact local-copy provenance decision identity mismatch.')
    raw_decision = observed.get('fitting_decision_record_bytes')
    if (not isinstance(raw_decision, bytes)
            or not _hash(decision.get('decision_record_sha256'))
            or sha256_bytes(raw_decision) != decision['decision_record_sha256']):
        raise ProtocolError('Exact local-copy fitting decision record mismatch.')


def verify_prefit_protocol(
    protocol: Mapping[str, object], approved_protocol_sha256: str,
    observed: Mapping[str, object],
) -> None:
    """Require the approved protocol hash and independently observed identities.

    The caller must supply hashes measured from the source, frozen boundaries,
    ordered scoreable IDs, and the human-approved canonical protocol digest.
    A digest recomputed from a changed protocol is not approval; callers must
    pass the approved digest unchanged. A copied data hash is not evidence.
    """
    if not isinstance(protocol, Mapping) or not isinstance(observed, Mapping):
        raise ProtocolError('Protocol and observed identities must be mappings.')
    if any(field not in protocol or protocol[field] is None or protocol[field] == ''
           or (isinstance(protocol[field], (Mapping, list, tuple))
               and not protocol[field])
           for field in _FIELDS):
        raise ProtocolError('Frozen protocol has missing fields.')
    try:
        actual_digest = sha256_bytes(canonical_json_bytes(dict(protocol)))
    except (TypeError, ValueError, OverflowError):
        raise ProtocolError('Frozen protocol cannot be hashed canonically.') from None
    if not _hash(approved_protocol_sha256) or actual_digest != approved_protocol_sha256:
        raise ProtocolError('Frozen protocol checksum mismatch.')
    for field in ('dataset_sha256', 'boundary_sha256', 'snapshot_manifest_sha256',
                  'accepted_snapshot_sha256', 'partition_hash_report_sha256',
                  'audit_report_sha256'):
        if not _hash(protocol[field]) or protocol[field] != observed.get(field):
            raise ProtocolError(f'{field} provenance mismatch.')
    expected_ids = protocol['partition_scoreable_id_sha256']
    actual_ids = observed.get('partition_scoreable_id_sha256')
    if (not isinstance(expected_ids, Mapping) or not isinstance(actual_ids, Mapping)
            or set(expected_ids) != _PARTITIONS or set(actual_ids) != _PARTITIONS):
        raise ProtocolError('Partition scoreable-ID hash set mismatch.')
    if any(not _hash(expected_ids[name]) or expected_ids[name] != actual_ids[name]
           for name in _PARTITIONS):
        raise ProtocolError('Partition scoreable-ID checksum mismatch.')
    if protocol['seed'] != 42 or isinstance(protocol['seed'], bool):
        raise ProtocolError('Protocol seed mismatch.')
    if protocol['showcase_role'] != 'demo_only_record_labels_unread':
        raise ProtocolError('Showcase role mismatch.')
    if protocol['audit_passed'] is False:
        verify_showcase_exception(protocol, observed)
    elif protocol['audit_passed'] is not True:
        raise ProtocolError('Aggregate class audit status is invalid.')
    if protocol['provenance_complete'] is False:
        verify_local_copy_fitting_decision(protocol, observed)
    elif protocol['provenance_complete'] is not True:
        raise ProtocolError('Dataset provenance status is invalid.')
