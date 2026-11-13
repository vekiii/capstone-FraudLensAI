"""T010 RED: identity vectors use reviewed byte framing and synthetic content."""
import hashlib

from fraudlens import data_import

MAPPING = 'a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57'
POLICY = '67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781'


def identity(namespace, member, ordinal):
    derive = getattr(data_import, 'derive_source_identity', None)
    assert callable(derive), 'T013 missing: domain-separated D/C source identity'
    return derive(namespace, member, ordinal)


def version(raw):
    derive = getattr(data_import, 'derive_dataset_version', None)
    assert callable(derive), 'T013 missing: version from full source/mapping/policy digests'
    return derive(hashlib.sha256(raw).digest(), bytes.fromhex(MAPPING), bytes.fromhex(POLICY))


def test_prefilter_ordinal_and_distinct_equal_rows():
    first = identity('ibm-v8-test', 'HI-Small_Trans.csv', 1)
    second = identity('ibm-v8-test', 'HI-Small_Trans.csv', 2)
    third = identity('ibm-v8-test', 'HI-Small_Trans.csv', 3)
    assert len({first.transaction_id, second.transaction_id, third.transaction_id}) == 3
    assert first.transaction_id.startswith('D')
    assert first.case_id.startswith('C')
    assert identity('ibm-v8-test', 'HI-Small_Trans.csv', 3) == third


def test_reviewed_synthetic_dc_vector():
    row = identity('synthetic:fraudlens-review:v1', 'review-7.csv', 7)
    assert row.transaction_id == 'D425884d07ae8e842624343aa411210de'
    assert row.case_id == 'C1cb19a78e9497dd29eee2de9e7527c60'


def test_namespace_and_member_are_separate_identity_inputs():
    baseline = identity('ibm-v8-test', 'HI-Small_Trans.csv', 3)
    assert identity('another-bank-source', 'HI-Small_Trans.csv', 3) != baseline
    assert identity('ibm-v8-test', 'other.csv', 3) != baseline
    import pytest
    with pytest.raises(ValueError, match='nonempty'):
        identity('ibm-v8-test/HI-Small_Trans.csv', '', 3)


def test_label_only_edit_keeps_dc_but_changes_dataset_version():
    blank = b'2026/01/01 10:00,BANK_A,0007,BANK_B,0007,0.000001,Euro,10.20,Euro,Wire,\n'
    labeled = blank[:-1] + b'1\n'
    assert identity('ibm-v8-test', 'HI-Small_Trans.csv', 1) == identity(
        'ibm-v8-test', 'HI-Small_Trans.csv', 1)
    assert version(blank) != version(labeled)


def test_label_only_change_has_distinct_dataset_version_in_isolation():
    blank = b'event-facts,\n'
    labeled = b'event-facts,1\n'
    assert version(blank) != version(labeled)


def test_modified_source_fails_pinned_sha256_even_if_dc_is_unchanged():
    verify = getattr(data_import, 'verify_source_digest', None)
    assert callable(verify), 'T013 missing: pinned source SHA-256 verification'
    original = b'row,0\n'
    changed_label = b'row,1\n'
    assert verify(original, hashlib.sha256(original).hexdigest())
    assert not verify(changed_label, hashlib.sha256(original).hexdigest())


def test_rejected_row_does_not_renumber_later_equal_valued_rows():
    # CSV ordinal 1 is rejected on facts; equal valid rows at 2 and 3 stay distinct.
    after_rejection = identity('ibm-v8-test', 'HI-Small_Trans.csv', 2)
    following_equal = identity('ibm-v8-test', 'HI-Small_Trans.csv', 3)
    assert after_rejection.transaction_id != following_equal.transaction_id
    assert after_rejection.case_id != following_equal.case_id
    assert after_rejection == identity('ibm-v8-test', 'HI-Small_Trans.csv', 2)


def test_quoted_multiline_record_consumes_one_ordinal():
    first = b'"wire\ntransfer",0\n'
    assert first.count(b'\n') == 2  # physical lines do not set the source ordinal
    next_row = identity('ibm-v8-test', 'HI-Small_Trans.csv', 2)
    assert next_row != identity('ibm-v8-test', 'HI-Small_Trans.csv', 3)


def test_member_boundaries_and_release_namespace_do_not_alias():
    a = identity('n', 'member-one.csv', 7)
    b = identity('n', 'member-two.csv', 7)
    c = identity('nmember-', 'one.csv', 7)
    d = identity('n:v9', 'member-one.csv', 7)
    assert len({a.transaction_id, b.transaction_id, c.transaction_id,
                d.transaction_id}) == 4
    assert len({a.case_id, b.case_id, c.case_id, d.case_id}) == 4


def test_source_mapping_and_time_policy_each_change_dataset_version():
    derive = getattr(data_import, 'derive_dataset_version', None)
    assert callable(derive), 'T013 missing: version from full source/mapping/policy digests'
    source = hashlib.sha256(b'row,0\n').digest()
    mapping = bytes.fromhex(MAPPING)
    policy = bytes.fromhex(POLICY)
    baseline = derive(source, mapping, policy)
    assert derive(hashlib.sha256(b'row,1\n').digest(), mapping, policy) != baseline
    assert derive(source, hashlib.sha256(b'edited mapping').digest(), policy) != baseline
    assert derive(source, mapping, hashlib.sha256(b'edited policy').digest()) != baseline


def test_truncated_id_collision_with_distinct_full_digest_fails():
    registry_type = getattr(data_import, 'IdentityRegistry', None)
    assert registry_type is not None, 'T013 missing: full-digest identity collision registry'
    registry = registry_type()
    registry.register('D' + 'a' * 32, b'\x01' * 32, b'input-one', b'fact-one')
    import pytest
    with pytest.raises(ValueError, match='collision'):
        registry.register('D' + 'a' * 32, b'\x02' * 32, b'input-two', b'fact-two')


def test_same_identity_with_changed_label_free_facts_fails():
    registry_type = getattr(data_import, 'IdentityRegistry', None)
    assert registry_type is not None, 'T013 missing: fact-digest collision registry'
    registry = registry_type()
    registry.register('D' + 'a' * 32, b'\x01' * 32, b'same-input', b'old-fact')
    import pytest
    with pytest.raises(ValueError, match='collision|changed fact'):
        registry.register('D' + 'a' * 32, b'\x01' * 32, b'same-input', b'new-fact')


def test_same_identity_and_facts_can_be_replayed_without_duplication():
    registry_type = getattr(data_import, 'IdentityRegistry', None)
    assert registry_type is not None, 'T013 missing: idempotent identity registry'
    registry = registry_type()
    registry.register('D' + 'a' * 32, b'\x01' * 32, b'same-input', b'same-fact')
    registry.register('D' + 'a' * 32, b'\x01' * 32, b'same-input', b'same-fact')
    assert len(registry) == 1


def test_parser_keeps_prefilter_ordinals_after_rejected_then_equal_rows():
    import csv
    import io

    from fraudlens import data_import as module
    parser = getattr(module, 'parse_canonical_source', None)
    assert callable(parser), 'T013 missing: parser assigning identity before rejection'
    headers = ['Timestamp', 'From Bank', 'Account', 'To Bank', 'Account',
               'Amount Received', 'Receiving Currency', 'Amount Paid',
               'Payment Currency', 'Payment Format', 'Is Laundering']
    valid = ['2026/01/01 10:00', 'BANK_A', '0007', 'BANK_B', '0007',
             '0.000001', 'Euro', '10.20', 'Euro', 'Wire', '']
    rejected = valid.copy()
    rejected[7] = '-1.00'
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(headers)
    writer.writerows([rejected, valid, valid])
    result = parser(stream.getvalue().encode(), namespace='ibm-v8-test',
                    member='HI-Small_Trans.csv')
    assert [event.source_ordinal for event in result.events] == [2, 3]
    assert result.events[0].transaction_id == identity('ibm-v8-test', 'HI-Small_Trans.csv', 2).transaction_id
    assert result.events[1].transaction_id == identity('ibm-v8-test', 'HI-Small_Trans.csv', 3).transaction_id
    assert result.events[0].transaction_id != result.events[1].transaction_id


def test_parser_multiline_record_does_not_shift_following_identity():
    import csv
    import io

    from fraudlens import data_import as module
    parser = getattr(module, 'parse_canonical_source', None)
    assert callable(parser), 'T013 missing: CSV record ordinal independent of physical lines'
    headers = ['Timestamp', 'From Bank', 'Account', 'To Bank', 'Account',
               'Amount Received', 'Receiving Currency', 'Amount Paid',
               'Payment Currency', 'Payment Format', 'Is Laundering']
    first = ['2026/01/01 10:00', 'BANK_A', '0007', 'BANK_B', '0007',
             '0.000001', 'Euro', '10.20', 'Euro', 'Wire', '']
    first[2] = '0007\nALT'
    second = first.copy()
    second[9] = 'Wire'
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(headers)
    writer.writerows([first, second])
    result = parser(stream.getvalue().encode(), namespace='ibm-v8-test',
                    member='HI-Small_Trans.csv')
    assert result.report.source_records == 2
    assert result.events[-1].source_ordinal == 2
    assert result.events[-1].transaction_id == identity('ibm-v8-test', 'HI-Small_Trans.csv', 2).transaction_id


def test_reordered_source_changes_version_without_promising_new_row_keys():
    before = b'header\nA,0\nB,0\n'
    reordered = b'header\nB,0\nA,0\n'
    assert version(before) != version(reordered)
    assert identity('ibm-v8-test', 'HI-Small_Trans.csv', 1) == identity(
        'ibm-v8-test', 'HI-Small_Trans.csv', 1)
    # The same row key can now name different facts; registry must reject a silent update.
    registry_type = getattr(data_import, 'IdentityRegistry', None)
    assert registry_type is not None, 'T013 missing: reordered-row fact collision guard'
    registry = registry_type()
    row = identity('ibm-v8-test', 'HI-Small_Trans.csv', 1)
    registry.register(row.transaction_id, row.full_digest, row.framed_input, b'A')
    import pytest
    with pytest.raises(ValueError, match='collision|changed fact'):
        registry.register(row.transaction_id, row.full_digest, row.framed_input, b'B')


def test_same_account_number_in_different_banks_has_distinct_join_key():
    import csv
    import io

    parser = getattr(data_import, 'parse_canonical_source', None)
    assert callable(parser), 'T013 missing: bank-qualified operational accounts'
    headers = ['Timestamp', 'From Bank', 'Account', 'To Bank', 'Account',
               'Amount Received', 'Receiving Currency', 'Amount Paid',
               'Payment Currency', 'Payment Format', 'Is Laundering']
    row = ['2026/01/01 10:00', 'BANK_A', '0007', 'BANK_C', '0007',
           '1.00', 'Euro', '1.00', 'Euro', 'Wire', '']
    other_bank = row.copy()
    other_bank[1] = 'BANK_B'
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(headers)
    writer.writerows([row, other_bank])
    result = parser(stream.getvalue().encode(), namespace='ibm-v8-test',
                    member='HI-Small_Trans.csv')
    assert [event.sender_account for event in result.events] == ['0007', '0007']
    assert result.events[0].sender_join_key != result.events[1].sender_join_key


def test_case_id_prefix_collision_with_distinct_full_digest_fails():
    registry_type = getattr(data_import, 'IdentityRegistry', None)
    assert registry_type is not None, 'T013 missing: C full-digest collision registry'
    registry = registry_type()
    registry.register('C' + 'b' * 32, b'\x03' * 32, b'first-case-input', b'fact')
    import pytest
    with pytest.raises(ValueError, match='collision'):
        registry.register('C' + 'b' * 32, b'\x04' * 32, b'second-case-input', b'fact')


def test_member_case_and_unicode_bytes_are_not_normalized():
    base = identity('namespace', 'file.csv', 1)
    assert identity('namespace', 'FILE.csv', 1) != base
    assert identity('namespace', 'caf\u00e9.csv', 1) != identity(
        'namespace', 'cafe\u0301.csv', 1)
