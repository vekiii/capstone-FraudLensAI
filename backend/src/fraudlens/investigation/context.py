"""Fixture contexts and explicitly authored history; no producer imports."""
import copy
import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from fraudlens.cases import CaseService
from fraudlens.investigation.models import context_digest, digest, validate
from fraudlens.scoring import FixtureScorer
from fraudlens.settings import Settings

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / 'data/fixtures/investigation'


def instant(value):
    validate('Instant', value)
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


class CaseContextReader:
    def __init__(self, fixture_path=None, metadata_path=None):
        self.fixture_path = Path(fixture_path or Settings().fixture_path)
        self.metadata_path = Path(metadata_path or FIXTURES / 'contexts.json')

    def resolve(self, case_id, source_mode, snapshot_ref):
        if source_mode != 'fixture':
            raise ValueError('Dataset context unavailable; no fixture fallback')
        metadata = json.loads(self.metadata_path.read_text(encoding='utf-8'))
        snapshot = 'fixture_' + digest({
            'cases': json.loads(self.fixture_path.read_text(encoding='utf-8')),
            'scorer_version': 'fixture-v1', 'metadata': metadata,
        })
        if snapshot_ref is not None and snapshot_ref != snapshot:
            raise ValueError('stale_snapshot')
        payload = CaseService(self.fixture_path, FixtureScorer()).get_case(case_id)
        result = dict(contract_version=1, source_mode='fixture', case_id=case_id,
                      snapshot_ref=snapshot, dataset_version=None,
                      observed_at=metadata['observed_at'], source_payload=payload.model_dump(mode='json'),
                      history=dict(availability='unavailable', cutoff=None, coverage='unavailable',
                                   start=None, lookback_days=7, view_scope='authored_fixture',
                                   reason='No history coverage supplied by the fixture context.'))
        result['context_revision'] = context_digest(result)
        return validate('InvestigationContext', result)


class HistoryReader:
    def __init__(self, events=None, accounts=None):
        self.events = copy.deepcopy(events) if events is not None else json.loads(
            (FIXTURES / 'history.json').read_text())['events']
        self.accounts = copy.deepcopy(accounts) if accounts is not None else json.loads(
            (FIXTURES / 'contexts.json').read_text())['accounts']

    def read(self, context, account_side, limit=50):
        context = validate('InvestigationContext', context)
        if account_side not in ('sender', 'receiver') or type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError('Invalid history arguments')
        history = context['history']
        identity = self.accounts.get(context['case_id'], {}).get(account_side)
        if history['availability'] == 'unavailable' or identity is None:
            return dict(availability='unavailable', coverage='unavailable', events=[],
                        returned_count=0, eligible_count=None, truncated=False, totals={})
        cutoff = instant(history['cutoff'])
        cutoff_minute = cutoff.replace(second=0, microsecond=0)
        start = cutoff - timedelta(days=7)
        focal = context['source_payload']['transaction']['transaction_id']
        eligible = []
        for event in self.events:
            if event['bank'] != identity['bank'] or event['account'] != identity['account']:
                continue
            time = instant(event['occurred_at'])
            if start <= time < cutoff_minute and event['transaction_id'] != focal:
                eligible.append(event)
        eligible.sort(key=lambda event: (instant(event['occurred_at']), event['transaction_id']))
        totals = {}
        for event in eligible:
            value = Decimal(event['amount'])
            if not value.is_finite() or value < 0:
                raise ValueError('Invalid history money')
            currency = event['currency']
            totals[currency] = totals.get(currency, Decimal(0)) + value
        events = [{key: event[key] for key in
                   ('transaction_id', 'occurred_at', 'bank', 'account', 'amount', 'currency')}
                  for event in eligible[:limit]]
        return dict(availability='available', coverage=history['coverage'], cutoff=history['cutoff'],
                    start=start.isoformat().replace('+00:00', 'Z'), lookback_days=7,
                    events=events, returned_count=len(events), eligible_count=len(eligible),
                    truncated=len(eligible) > limit, totals={k: str(v) for k, v in totals.items()})


def outbound_context(context, run_id):
    """Explicit fixture projection; no private/source rows or arbitrary extra fields."""
    context = validate('InvestigationContext', context)
    validate('RunId', run_id)
    if context['source_mode'] != 'fixture':
        raise ValueError('Dataset projection unavailable')
    tx, risk = context['source_payload']['transaction'], context['source_payload']['risk_assessment']
    def alias(side):
        return 'account_' + digest([run_id, context['context_revision'], side, tx[side + '_account']])[:24]
    return dict(source_mode='fixture', notice='Authored synthetic data; no ML inference',
                context_revision=context['context_revision'], case_id=context['case_id'],
                transaction=dict(transaction_id=tx['transaction_id'], occurred_at=tx['occurred_at'],
                                 amount=tx['amount'], currency=tx['currency'],
                                 sender_alias=alias('sender'), receiver_alias=alias('receiver')),
                assessment={key: risk[key] for key in
                            ('score', 'source', 'scorer_version', 'scored_at', 'explanation')})
