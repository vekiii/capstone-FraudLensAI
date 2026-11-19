"""Fail-closed FR-021 check at the boundary before any model fit."""

from collections.abc import Mapping

from fraudlens.data.manifest import canonical_json_bytes, sha256_bytes


class ProtocolError(ValueError):
    """A frozen protocol cannot authorize model fitting."""


_FIELDS = (
    'dataset_sha256', 'boundary_sha256', 'partition_scoreable_id_sha256',
    'timezone_policy', 'warmup_rule', 'feature_version', 'feature_order',
    'partition_boundaries', 'partition_counts', 'allowed_prevalence', 'seed',
    'tie_rules', 'preprocessing', 'imbalance_option', 'candidate_grid',
    'metrics', 'threshold_objective', 'resource_ceilings', 'label_rules',
    'showcase_role', 'audit_passed', 'provenance_complete',
)
_PARTITIONS = frozenset(('development', 'showcase', 'train', 'validation', 'test'))


def _hash(value: object) -> bool:
    return (isinstance(value, str) and len(value) == 64
            and all(character in '0123456789abcdef' for character in value))


def verify_prefit_protocol(
    protocol: Mapping[str, object], protocol_sha256: str,
    observed: Mapping[str, object],
) -> None:
    """Require exact protocol bytes/fields and independently observed identities.

    The caller must supply hashes measured from the source, frozen boundaries,
    and ordered scoreable IDs. A copied value from the protocol is not evidence.
    """
    if not isinstance(protocol, Mapping) or not isinstance(observed, Mapping):
        raise ProtocolError('Protocol and observed identities must be mappings.')
    if any(field not in protocol or protocol[field] is None or protocol[field] == ''
           for field in _FIELDS):
        raise ProtocolError('Frozen protocol has missing fields.')
    try:
        actual_digest = sha256_bytes(canonical_json_bytes(dict(protocol)))
    except (TypeError, ValueError, OverflowError):
        raise ProtocolError('Frozen protocol cannot be hashed canonically.') from None
    if not _hash(protocol_sha256) or actual_digest != protocol_sha256:
        raise ProtocolError('Frozen protocol checksum mismatch.')
    for field in ('dataset_sha256', 'boundary_sha256'):
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
    if protocol['audit_passed'] is not True:
        raise ProtocolError('Aggregate class audit did not pass.')
    if protocol['provenance_complete'] is not True:
        raise ProtocolError('Dataset provenance is incomplete.')
