"""Authored fixture context/history: no model or real customer access."""
import copy
import json
from pathlib import Path

import pytest

from fraudlens.cases import CaseService
from fraudlens.investigation.context import CaseContextReader, HistoryReader, outbound_context
from fraudlens.investigation.models import context_digest, validate
from fraudlens.scoring import FixtureScorer
from fraudlens.settings import Settings

ROOT = Path(__file__).resolve().parents[3]


def context():
    return CaseContextReader().resolve('CASE-001', 'fixture', None)


def available():
    value = copy.deepcopy(context())
    value['history'].update(availability='available', coverage='full',
                            cutoff='2026-01-05T09:15:00Z', start='2025-12-29T09:15:00Z',
                            reason='Explicitly authored synthetic history')
    value['context_revision'] = context_digest(value)
    return value


def event(i, time='2026-01-04T09:15:00Z', bank='AUTHORED-A', account='001', currency='EUR'):
    return dict(transaction_id=f'TX-{i:03d}', occurred_at=time, bank=bank,
                account=account, amount='1.00', currency=currency)


def test_snapshot_and_foundation_preservation():
    value = context()
    expected = CaseService(Settings().fixture_path, FixtureScorer()).get_case('CASE-001')
    assert value['source_payload'] == expected.model_dump(mode='json')
    assert value['dataset_version'] is None
    assert value['history']['availability'] == 'unavailable'
    assert value['snapshot_ref'].startswith('fixture_')
    validate('InvestigationContext', value)
    assert context() == value
    assert json.loads((ROOT / 'data/fixtures/cases.json').read_text())[0]['case_id'] == 'CASE-001'


def test_stale_and_wrong_source():
    for mode, snapshot in [('dataset', None), ('fixture', 'fixture_' + '0' * 64)]:
        with pytest.raises(ValueError):
            CaseContextReader().resolve('CASE-001', mode, snapshot)


def test_alias_allowlist_scope():
    ctx = context()
    first = outbound_context(ctx, 'inv_' + 'a' * 32)
    assert first == outbound_context(ctx, 'inv_' + 'a' * 32)
    assert first != outbound_context(ctx, 'inv_' + 'b' * 32)
    text = json.dumps(first)
    assert 'DEMO-BANK' not in text
    assert 'source_payload' not in first
    assert 'source_mode' in first
    assert first['transaction']['amount'] == ctx['source_payload']['transaction']['amount']


def test_history_cutoff_window_identity_and_focal():
    ctx = available()
    focal = ctx['source_payload']['transaction']['transaction_id']
    events = [event(2), event(3, '2026-01-05T09:15:00Z'),
              event(4, '2026-01-06T00:00:00Z'), event(5, '2025-12-28T00:00:00Z'),
              event(6, bank='OTHER'), event(7, account='OTHER'),
              {**event(8), 'transaction_id': focal}]
    result = HistoryReader(events=events, accounts={'CASE-001': {
        'sender': {'bank': 'AUTHORED-A', 'account': '001'}}}).read(ctx, 'sender', 50)
    assert [e['transaction_id'] for e in result['events']] == ['TX-002']
    assert result['availability'] == 'available'
    assert result['eligible_count'] == 1
    assert result['truncated'] is False


def test_history_empty_unavailable_and_truncated():
    reader = HistoryReader(events=[event(i) for i in range(2, 65)], accounts={
        'CASE-001': {'sender': {'bank': 'AUTHORED-A', 'account': '001'}}})
    assert reader.read(context(), 'sender', 50)['availability'] == 'unavailable'
    result = reader.read(available(), 'sender', 50)
    assert result['returned_count'] == 50
    assert result['eligible_count'] == 63
    assert result['truncated'] is True
    empty = HistoryReader(events=[], accounts=reader.accounts).read(available(), 'sender', 50)
    assert empty['availability'] == 'available' and empty['events'] == []
    for limit in [0, 51, True]:
        with pytest.raises(ValueError):
            reader.read(available(), 'sender', limit)


def test_history_currencies_separate():
    result = HistoryReader(events=[event(2), event(3, currency='USD')], accounts={
        'CASE-001': {'sender': {'bank': 'AUTHORED-A', 'account': '001'}}}).read(available(), 'sender', 50)
    assert result['totals'] == {'EUR': '1.00', 'USD': '1.00'}

def test_frozen_snapshot_changes_with_authored_metadata(tmp_path):
    from fraudlens.investigation.models import digest
    metadata = ROOT / 'data/fixtures/investigation/contexts.json'
    contents = json.loads(metadata.read_text())
    source = json.loads(Settings().fixture_path.read_text())
    frozen = 'fixture_' + digest({'cases': source, 'scorer_version': 'fixture-v1', 'metadata': contents})
    assert context()['snapshot_ref'] == frozen
    changed = tmp_path / 'contexts.json'
    contents['notice'] += ' version changed'
    changed.write_text(json.dumps(contents))
    assert CaseContextReader(metadata_path=changed).resolve('CASE-001', 'fixture', None)['snapshot_ref'] != frozen

def test_history_projection_excludes_private_and_unknown_fields():
    authored = {**event(2), 'isFraud': True, 'reference_answer': 'PRIVATE',
                'source_path': 'PRIVATE', 'reviewer_notes': 'PRIVATE'}
    result = HistoryReader(events=[authored], accounts={
        'CASE-001': {'sender': {'bank': 'AUTHORED-A', 'account': '001'}}}).read(available(), 'sender', 50)
    assert 'PRIVATE' not in json.dumps(result)
    assert 'isFraud' not in json.dumps(result)
