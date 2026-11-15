"""Pinned authored boundary checks, NOT reviewed/live producer adapter evidence.

T062 human review and the actual producer/history port remain pending. These
tests verify existing safeguards without pretending a synthetic reader is that
adapter, or weakening the frozen schema to accept newer producer methods.
"""
import copy
import json

import pytest

from fraudlens.investigation.context import CaseContextReader, HistoryReader, outbound_context
from fraudlens.investigation.models import ROOT, context_digest, validate


def authored_context():
    return json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/context-dataset.json')
                      .read_text(encoding='utf-8'))


@pytest.mark.parametrize('path', [
    ('case_id',), ('source_payload', 'case_id'),
    ('snapshot_ref',), ('source_payload', 'snapshot_ref'),
    ('source_payload', 'risk_assessment', 'run_id'),
    ('dataset_version',), ('source_payload', 'dataset_version'),
    ('source_payload', 'risk_assessment', 'dataset_version'),
    ('source_payload', 'transaction', 'transaction_id'),
    ('source_payload', 'risk_assessment', 'transaction_id'),
])
def test_well_shaped_cross_object_identity_change_rejected(path):
    ctx = authored_context()
    target = ctx
    for key in path[:-1]:
        target = target[key]
    old = target[path[-1]]
    target[path[-1]] = old[:-1] + ('b' if old[-1] != 'b' else 'c')
    ctx['context_revision'] = context_digest(ctx)
    with pytest.raises(ValueError):
        validate('InvestigationContext', ctx)


def test_directional_precision_time_and_rules_scale_survive_outbound_projection():
    ctx = authored_context()
    tx = ctx['source_payload']['transaction']
    tx['received'] = {'amount': '0.00012500', 'currency': 'Bitcoin'}
    ctx['context_revision'] = context_digest(ctx)
    before = copy.deepcopy(ctx)
    projected = outbound_context(ctx, 'inv_' + 'a' * 32)
    for key in ('transaction_id', 'paid', 'received', 'event_time_raw',
                'event_time_utc', 'time_basis'):
        assert projected['transaction'][key] == tx[key]
    assert projected['assessment'] == ctx['source_payload']['risk_assessment']
    assert projected['assessment']['score_kind'] == 'ordinal_rule_score'
    assert projected['assessment']['explanation']['explained_scale'] == 'risk_score'
    assert ctx == before
    assert tx['sender']['bank'] not in json.dumps(projected)


@pytest.mark.parametrize('mutation', ['scale', 'cutoff', 'new_method', 'private_label'])
def test_semantic_or_unreviewed_payload_rejected(mutation):
    ctx = authored_context()
    risk = ctx['source_payload']['risk_assessment']
    if mutation == 'scale':
        risk['explanation']['explained_scale'] = 'log_odds'
    elif mutation == 'cutoff':
        ctx['history']['cutoff'] = '2026-01-01T10:01:00Z'
    elif mutation == 'new_method':
        risk['explanation']['method'] = 'boosted_sequential_probability'
    else:
        ctx['source_payload']['transaction']['is_laundering'] = True
    ctx['context_revision'] = context_digest(ctx)
    with pytest.raises(ValueError):
        outbound_context(ctx, 'inv_' + 'a' * 32)


def test_dataset_is_unavailable_without_actual_reviewed_producer_no_fixture_fallback():
    ctx = authored_context()
    with pytest.raises(ValueError, match='Dataset context unavailable'):
        CaseContextReader().resolve(ctx['case_id'], 'dataset', ctx['snapshot_ref'])
    with pytest.raises(ValueError, match='stale_snapshot'):
        CaseContextReader().resolve('CASE-001', 'fixture', ctx['snapshot_ref'])


def test_authored_dataset_history_distinguishes_missing_empty_and_strict_scope():
    ctx = authored_context()
    identity = ctx['source_payload']['transaction']['sender']
    accounts = {ctx['case_id']: {'sender': identity}}
    assert HistoryReader(events=[], accounts=accounts).read(ctx, 'sender')['eligible_count'] is None
    ctx['history'].update(availability='available', coverage='full',
                          start='2025-12-25T10:00:00Z', reason='Authored test only')
    ctx['context_revision'] = context_digest(ctx)
    empty = HistoryReader(events=[], accounts=accounts).read(ctx, 'sender')
    assert empty['availability'] == 'available' and empty['eligible_count'] == 0
    base = dict(bank=identity['bank'], account=identity['account'], amount='1.2300',
                currency='Australian Dollar', occurred_at='2026-01-01T09:59:00Z')
    focal = ctx['source_payload']['transaction']['transaction_id']
    rows = [{**base, 'transaction_id': 'D' + '1' * 32, 'private_label': 'PRIVATE'},
            {**base, 'transaction_id': 'D' + '2' * 32, 'bank': 'OTHER'},
            {**base, 'transaction_id': 'D' + '3' * 32, 'account': 'OTHER'},
            {**base, 'transaction_id': 'D' + '4' * 32, 'occurred_at': '2026-01-01T10:00:00Z'},
            {**base, 'transaction_id': 'D' + '5' * 32, 'occurred_at': '2025-12-25T09:59:00Z'},
            {**base, 'transaction_id': focal}]
    result = HistoryReader(events=rows, accounts=accounts).read(ctx, 'sender')
    assert [row['transaction_id'] for row in result['events']] == ['D' + '1' * 32]
    assert result['totals'] == {'Australian Dollar': '1.2300'}
    assert 'PRIVATE' not in json.dumps(result)
