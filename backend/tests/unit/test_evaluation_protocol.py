"""T026 RED: offline chronological protocol on authored, label-separated facts."""

import importlib
import importlib.util
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import MappingProxyType

import pytest

from fraudlens.data_contracts import CanonicalTransaction, DatasetVersion, PrivateEvaluationLabel
from fraudlens.data_import import derive_dataset_version
from fraudlens.feature_history import build_feature_snapshots

START = datetime(2026, 1, 1, tzinfo=UTC)
SOURCE_HASH = 'b' * 64
MAPPING_HASH = 'c' * 64
TIME_HASH = 'd' * 64
VERSION = derive_dataset_version(*(bytes.fromhex(value) for value in
                                   (SOURCE_HASH, MAPPING_HASH, TIME_HASH)))


def _event(name: str, at: datetime, ordinal: int) -> CanonicalTransaction:
    return CanonicalTransaction(
        transaction_id=name, case_id='case-' + name, source_ordinal=ordinal,
        event_time_raw=at.isoformat(), event_time_utc=at,
        event_time_epoch_ns=int(at.timestamp()) * 1_000_000_000,
        time_basis='assumed_utc', sender_bank='A', sender_account='1',
        receiver_bank='R', receiver_account='1', sender_join_key=b'A:1',
        receiver_join_key=b'R:1', paid_amount='10', paid_currency='Euro',
        received_amount='10', received_currency='Euro', payment_format='Wire',
        event_fact_digest=name.encode(),
    )


def _events():
    """160 scoreable rows: 110/26/24 after a four-row boundary tie group."""
    warmup = [_event('warm-start', START, 1),
              _event('warm-mid', START + timedelta(hours=12), 2)]
    base = START + timedelta(hours=24)
    rows = []
    for i in range(160):
        minute = 110 if 110 <= i <= 113 else i - 3 if i >= 114 else i
        rows.append(_event(f'event-{i:03}', base + timedelta(minutes=minute), i + 3))
    return warmup + rows


def _population():
    events = _events()
    warmup = events[:2]
    snapshots = build_feature_snapshots(events, dataset_version=VERSION,
                                        coverage_start=START)
    positive = set(range(3)) | set(range(114, 134)) | set(range(136, 156))
    labels = tuple(
        PrivateEvaluationLabel(
            event.transaction_id, event.source_ordinal,
            'missing' if event in warmup else
            'eligible_positive' if i - 2 in positive else 'eligible_negative',
            None if event in warmup else int(i - 2 in positive),
        )
        for i, event in enumerate(events)
    )
    dataset = DatasetVersion(VERSION, SOURCE_HASH, MAPPING_HASH, TIME_HASH, 'complete',
                             len(events))
    return dataset, tuple(snapshots.values()), labels


def _protocol(dataset, snapshots, labels, **overrides):
    # The planned evaluator does not exist yet. Fail in the test body, with
    # collection and fixture construction intact, before asserting its contract.
    if importlib.util.find_spec('fraudlens.evaluation') is None:
        pytest.fail('T027 missing behavior: fraudlens.evaluation.build_split_manifest')
    module = importlib.import_module('fraudlens.evaluation')
    build = getattr(module, 'build_split_manifest', None)
    assert callable(build), 'T027 missing behavior: build_split_manifest'
    options = dict(dataset_version=dataset, snapshots=snapshots, labels=labels,
                   source_start=START, expected_source_sha256=SOURCE_HASH)
    options.update(overrides)
    return build(**options)


def _parts(manifest):
    return manifest.partitions['train'], manifest.partitions['validation'], \
        manifest.partitions['test']


def test_synthetic_replay_is_label_free_and_past_only():
    dataset, snapshots, labels = _population()
    by_id = {s.transaction_id: s for s in snapshots}
    assert dataset.status == 'complete'
    assert len(labels) == len(snapshots) == 162
    assert not by_id['warm-mid'].scoreable
    assert by_id['event-000'].scoreable
    assert by_id['event-110'].feature_values == by_id['event-111'].feature_values
    assert all('label' not in key and 'target' not in key
               for s in snapshots for key in s.feature_values)
    assert all(s.as_of == s.event_time for s in snapshots)


def test_whole_timestamp_nearest_boundaries_and_exact_membership():
    dataset, snapshots, labels = _population()
    manifest = _protocol(dataset, snapshots, labels)
    train, validation, test = _parts(manifest)
    assert train.transaction_ids == tuple(f'event-{i:03}' for i in range(110))
    assert validation.transaction_ids == tuple(f'event-{i:03}' for i in range(110, 136))
    assert test.transaction_ids == tuple(f'event-{i:03}' for i in range(136, 160))
    assert {f'event-{i:03}' for i in range(110, 114)} <= set(validation.transaction_ids)
    assert manifest.warmup_excluded_ids == ('warm-start', 'warm-mid')
    assert train.last_event_time < validation.first_event_time < test.first_event_time


def test_membership_is_deterministic_and_fixed_before_label_join():
    dataset, snapshots, labels = _population()
    first = _protocol(dataset, snapshots, labels)
    changed = tuple(replace(label, status='missing', value=None)
                    if label.transaction_id in {'event-110', 'event-136'} else label
                    for label in labels)
    second = _protocol(dataset, tuple(reversed(snapshots)), tuple(reversed(changed)))
    for old, new in zip(_parts(first), _parts(second), strict=True):
        assert old.transaction_ids == new.transaction_ids
    assert second.partitions['validation'].label_ineligible_count == 1
    assert second.partitions['test'].label_ineligible_count == 1


def test_exact_counts_class_distribution_and_natural_prevalence():
    dataset, snapshots, labels = _population()
    manifest = _protocol(dataset, snapshots, labels)
    expected = ((110, 3, 107), (26, 20, 6), (24, 20, 4))
    for partition, (rows, positives, negatives) in zip(_parts(manifest), expected,
                                                       strict=True):
        assert partition.event_valid_count == rows
        assert partition.label_eligible_count == rows
        assert partition.label_ineligible_count == 0
        assert (partition.positives, partition.negatives) == (positives, negatives)
        assert partition.prevalence == pytest.approx(positives / rows)
    assert manifest.event_valid_count == 162
    assert manifest.scoreable_count == 160
    assert manifest.eligible is True


@pytest.mark.parametrize('partition_name', ['train', 'validation', 'test'])
def test_missing_class_or_outer_positive_minimum_is_explicitly_ineligible(partition_name):
    dataset, snapshots, labels = _population()
    ranges = {'train': range(0, 3), 'validation': range(114, 134),
              'test': range(136, 156)}
    removed = {f'event-{i:03}' for i in ranges[partition_name]}
    changed = tuple(replace(label, status='missing', value=None)
                    if label.transaction_id in removed else label for label in labels)
    manifest = _protocol(dataset, snapshots, changed)
    assert manifest.eligible is False
    assert manifest.fit_allowed is False
    assert manifest.ineligibility_reasons
    assert manifest.partitions[partition_name].positives == 0
    assert manifest.partitions[partition_name].label_ineligible_count == len(removed)
    assert _parts(manifest)[0].transaction_ids == tuple(f'event-{i:03}' for i in range(110))


@pytest.mark.parametrize('partition_name,changed_id', [('validation', 'event-114'),
                                                       ('test', 'event-136')])
def test_nineteen_outer_positives_stops_fit_without_window_search(partition_name,
                                                                  changed_id):
    dataset, snapshots, labels = _population()
    changed = tuple(replace(label, status='eligible_negative', value=0)
                    if label.transaction_id == changed_id else label for label in labels)
    manifest = _protocol(dataset, snapshots, changed)
    assert manifest.partitions[partition_name].positives == 19
    assert manifest.partitions[partition_name].negatives == (
        7 if partition_name == 'validation' else 5)
    assert manifest.eligible is False
    assert manifest.fit_allowed is False
    first = 110 if partition_name == 'validation' else 136
    last = 136 if partition_name == 'validation' else 160
    assert manifest.partitions[partition_name].transaction_ids == tuple(
        f'event-{i:03}' for i in range(first, last))


@pytest.mark.parametrize('partition_name', ['train', 'validation', 'test'])
def test_missing_negative_class_is_ineligible(partition_name):
    dataset, snapshots, labels = _population()
    ranges = {'train': range(110), 'validation': range(110, 136),
              'test': range(136, 160)}
    selected = {f'event-{i:03}' for i in ranges[partition_name]}
    changed = tuple(replace(label, status='eligible_positive', value=1)
                    if label.transaction_id in selected else label for label in labels)
    manifest = _protocol(dataset, snapshots, changed)
    assert manifest.partitions[partition_name].negatives == 0
    assert manifest.eligible is False
    assert manifest.fit_allowed is False
    assert manifest.ineligibility_reasons


@pytest.mark.parametrize('change', ['wrong_version', 'wrong_source_hash',
                                    'wrong_mapping_hash',
                                    'bad_as_of', 'unsupported_coverage',
                                    'staged_dataset'])
def test_invalid_provenance_or_partition_state_fails_closed(change):
    dataset, snapshots, labels = _population()
    if change == 'wrong_version':
        snapshots = (replace(snapshots[0], dataset_version='dv_' + 'e' * 64),
                     *snapshots[1:])
    elif change == 'wrong_source_hash':
        dataset = replace(dataset, source_sha256='f' * 64)
    elif change == 'wrong_mapping_hash':
        dataset = replace(dataset, mapping_sha256='f' * 64)
    elif change == 'bad_as_of':
        snapshots = (replace(snapshots[2], as_of=snapshots[2].event_time +
                             timedelta(minutes=1)), *snapshots[:2], *snapshots[3:])
    elif change == 'staged_dataset':
        dataset = replace(dataset, status='staged')
    else:
        snapshots = (replace(snapshots[2], coverage_state='unknown'),
                     *snapshots[:2], *snapshots[3:])
    with pytest.raises(ValueError, match='version|source|as.of|coverage|provenance|complete'):
        _protocol(dataset, snapshots, labels)


def test_manifest_is_immutable_deterministic_and_bound_to_feature_policy():
    dataset, snapshots, labels = _population()
    first = _protocol(dataset, snapshots, labels)
    second = _protocol(dataset, tuple(reversed(snapshots)), tuple(reversed(labels)))
    assert first == second
    assert first.membership_hash == second.membership_hash
    assert first.protocol_hash == second.protocol_hash
    assert first.protocol.feature_version == 'history-v1'
    assert len(first.protocol.feature_policy_hash) == 64
    assert first.holdout_disclosed is False
    with pytest.raises((AttributeError, TypeError)):
        first.partitions['train'] = first.partitions['test']
    with pytest.raises((AttributeError, TypeError)):
        first.partitions['train'].positives = 999


def test_manifest_rejects_overlap_and_inconsistent_counts():
    dataset, snapshots, labels = _population()
    manifest = _protocol(dataset, snapshots, labels)
    bad_count = replace(manifest.partitions['validation'], positives=21)
    with pytest.raises(ValueError, match='split manifest partition counts'):
        replace(manifest, partitions=MappingProxyType({
            **manifest.partitions, 'validation': bad_count}))
    duplicate = replace(manifest.partitions['validation'],
                        transaction_ids=manifest.partitions['train'].transaction_ids)
    with pytest.raises(ValueError, match='split manifest'):
        replace(manifest, partitions=MappingProxyType({
            **manifest.partitions, 'validation': duplicate}))
    with pytest.raises(ValueError, match='split manifest digest'):
        replace(manifest, membership_hash='0' * 64)


@pytest.mark.parametrize('change', ['unknown_label_id', 'duplicate_snapshot_id'])
def test_mismatched_event_identity_is_rejected(change):
    dataset, snapshots, labels = _population()
    if change == 'unknown_label_id':
        labels = (replace(labels[0], transaction_id='other-event'), *labels[1:])
    else:
        snapshots = (replace(snapshots[1], transaction_id=snapshots[0].transaction_id),
                     *snapshots[:1], *snapshots[2:])
    with pytest.raises(ValueError, match='identity|identities'):
        _protocol(dataset, snapshots, labels)


def test_incomplete_coverage_is_excluded_without_discarding_observable_facts():
    dataset, snapshots, labels = _population()
    target = next(s for s in snapshots if s.transaction_id == 'event-120')
    changed = tuple(replace(s, coverage_state='incomplete', scoreable=False)
                    if s.transaction_id == target.transaction_id else s for s in snapshots)
    manifest = _protocol(dataset, changed, labels)
    assert target.transaction_id in manifest.coverage_excluded_ids
    assert target.transaction_id not in set().union(
        *(set(part.transaction_ids) for part in _parts(manifest)))
    assert manifest.event_valid_count == 162
    assert manifest.scoreable_count == 159


def test_no_scoreable_rows_reports_insufficient_data_without_fit():
    dataset, snapshots, labels = _population()
    manifest = _protocol(dataset, snapshots[:2], labels[:2])
    assert manifest.eligible is False
    assert manifest.fit_allowed is False
    assert manifest.ineligibility_reasons
    assert manifest.scoreable_count == 0


def test_label_edits_and_future_append_do_not_change_prior_scoring_features():
    dataset, snapshots, labels = _population()
    original = next(s for s in snapshots if s.transaction_id == 'event-050')
    changed_labels = tuple(replace(label, status='missing', value=None)
                           if label.transaction_id == original.transaction_id else label
                           for label in labels)
    future = _event('future', START + timedelta(days=3), 163)
    replay = build_feature_snapshots(_events() + [future], dataset_version=VERSION,
                                     coverage_start=START)
    assert replay[original.transaction_id].feature_values == original.feature_values
    assert replay[original.transaction_id].feature_input_digest == original.feature_input_digest
    assert all('label' not in key and 'target' not in key
               for key in replay[original.transaction_id].feature_values)
    _protocol(dataset, snapshots, changed_labels)
    assert all('label' not in key for key in original.feature_values)
