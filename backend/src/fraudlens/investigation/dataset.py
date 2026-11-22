"""Feature003 read-only consumer of the reviewed producer's published stores.

No producer imports, label reads, training or schema writes. SQL/paths are never
model arguments. Versioned contract and the reviewed layout are documented in
specs/003-ai-investigation/dataset-adapter-agreement-v2.md.
"""
import json
import math
import sqlite3
import time
from contextlib import ExitStack, contextmanager
from datetime import datetime, timedelta
from decimal import Decimal, localcontext
from functools import lru_cache
from pathlib import Path

from fraudlens.cases import CaseNotFoundError
from fraudlens.investigation.context import instant
from fraudlens.investigation.history_index import HistoryIndex, signature
from fraudlens.investigation.models import context_digest, validate


def timestamp(value):
    return value.isoformat().replace('+00:00', 'Z')


def source_instant(value):
    """Canonical producer SQLite uses +00:00; public wire uses Z."""
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.utcoffset() != timedelta(0):
        raise ValueError('Canonical source must use UTC')
    return result


def unavailable():
    return dict(availability='unavailable', coverage='unavailable', events=[],
                returned_count=0, eligible_count=None, truncated=False, totals={})


@lru_cache(maxsize=4)
def _validated_index(source, index, digest, _source_signature, _index_signature):
    # Readers in separate requests share the initial hash check. Every lookup
    # still guards the index and source against changed signatures or a live WAL.
    return HistoryIndex(source, index, digest)


class DatasetReader:
    def __init__(self, run_store, dataset_store, score_source, *, history_index=None,
                 history_index_sha256=None):
        self.run_store, self.dataset_store = Path(run_store), Path(dataset_store)
        if score_source not in ('rules', 'model'):
            raise ValueError('Invalid dataset score source')
        self.score_source = score_source
        if (history_index is None) != (history_index_sha256 is None):
            raise ValueError('History index requires an explicit digest')
        self.history_index_path = Path(history_index) if history_index is not None else None
        self.history_index_sha256 = history_index_sha256

    def _index(self):
        source = self.dataset_store.resolve()
        index = self.history_index_path.resolve()
        return _validated_index(source, index, self.history_index_sha256,
                                tuple(signature(source)), tuple(signature(index)))

    @contextmanager
    def connection(self, path):
        db = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=1)
        deadline = time.monotonic() + 5
        db.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
        # Defense in depth: even fixed queries cannot accidentally read labels.
        db.set_authorizer(lambda action, table, column, database, trigger:
                          sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_READ and table not in {
                              'active_run', 'scored_runs', 'scored_assessments',
                              'active_dataset', 'dataset_versions', 'operational_events'
                          } else sqlite3.SQLITE_OK)
        try:
            db.execute('BEGIN')
            yield db
        finally:
            db.close()

    def _active(self, db, snapshot_ref):
        row = db.execute('''SELECT r.run_id,r.dataset_version,r.scorer_version
            FROM active_run a JOIN scored_runs r ON a.run_id=r.run_id
            WHERE a.singleton=1 AND r.status='completed' AND r.score_source=?''',
                         (self.score_source,)).fetchone()
        if row is None or (snapshot_ref is not None and snapshot_ref != row[0]):
            raise ValueError('stale_snapshot')
        return row

    def _history_metadata(self, context):
        cutoff = instant(context['source_payload']['risk_assessment']['history_cutoff_exclusive_at'])
        start = cutoff - timedelta(days=7)
        metadata = dict(availability='unavailable', coverage='unavailable',
                        cutoff=timestamp(cutoff), start=None, lookback_days=7,
                        view_scope='synthetic_shared_banks',
                        reason='Canonical history unavailable; not an empty history.')
        try:
            with self.connection(self.dataset_store) as db:
                row = db.execute('''SELECT d.id,d.rejected_records FROM active_dataset a
                    JOIN dataset_versions d ON d.id=a.version
                    WHERE a.singleton=1 AND d.status='complete' ''').fetchone()
                if row is None or row[0] != context['dataset_version']:
                    raise ValueError('stale_snapshot')
                if self.history_index_path is not None:
                    earliest = self._index().earliest(row[0])
                else:
                    earliest = db.execute("SELECT MIN(json_extract(payload_json,'$.event_time_utc')) "
                                          'FROM operational_events WHERE version=?', (row[0],)).fetchone()[0]
                if earliest is not None:
                    metadata.update(availability='available',
                                    coverage='full' if source_instant(earliest) <= start and row[1] == 0 else 'incomplete',
                                    start=timestamp(start),
                                    reason='Synthetic store coverage only, not complete customer activity.')
        except (OSError, sqlite3.Error):
            pass  # missing/busy/interrupted source is unavailable, never fixture/empty
        return metadata

    def resolve(self, case_id, snapshot_ref):
        validate('CaseId', case_id)
        with self.connection(self.run_store) as db:
            run, version, scorer = self._active(db, snapshot_ref)
            row = db.execute('''SELECT transaction_json,assessment_json,score FROM scored_assessments
                WHERE run_id=? AND case_id=? AND alert=1''', (run, case_id)).fetchone()
            if row is None:
                raise CaseNotFoundError('Published case not found')
            tx, risk = json.loads(row[0]), json.loads(row[1])
        context = dict(contract_version=2, source_mode='dataset', case_id=case_id,
                       snapshot_ref=run, dataset_version=version, observed_at=risk['scored_at'],
                       source_payload=dict(contract_version=2, case_id=case_id, snapshot_ref=run,
                                           dataset_version=version, transaction=tx, risk_assessment=risk),
                       history=dict(availability='unavailable', coverage='unavailable',
                                    cutoff=risk['history_cutoff_exclusive_at'], start=None,
                                    lookback_days=7, view_scope='synthetic_shared_banks', reason='Pending source check'))
        context['context_revision'] = context_digest(context)
        validate('InvestigationContext', context)
        if (tx['event_time_utc'] != risk['event_time_utc']
                or tx['event_time_utc'] != risk['history_cutoff_exclusive_at']
                or risk['score'] != row[2]
                or risk['score_source'] != self.score_source or risk['scorer_version'] != scorer
                or ((risk['score_source'] == 'rules') != (risk['score_kind'] == 'ordinal_rule_score'))):
            raise ValueError('Published assessment provenance mismatch')
        explanation = risk['explanation']
        if explanation['status'] == 'available':
            if (self.score_source == 'rules') != (explanation['method'] == 'rules'):
                raise ValueError('Explanation source mismatch')
            base, remainder = explanation['base_value'], explanation['remainder']
            if (base is None) != (remainder is None):
                raise ValueError('Incomplete additive explanation')
            if base is not None:
                value = Decimal(str(base)) + Decimal(str(remainder))
                value += sum((Decimal(str(i['contribution'])) for i in explanation['items']), Decimal(0))
                if explanation['method'] == 'linear_log_odds':
                    x = float(value)
                    value = Decimal(str(1 / (1 + math.exp(-x)) if x >= 0 else math.exp(x) / (1 + math.exp(x))))
                if abs(value - Decimal(str(risk['score']))) > Decimal('1e-8'):
                    raise ValueError('Explanation reconstruction mismatch')
        context['history'] = self._history_metadata(context)
        context['context_revision'] = context_digest(context)
        return validate('InvestigationContext', context)

    def read(self, context, account_side, limit=50):
        context = validate('InvestigationContext', context)
        if context['source_mode'] != 'dataset' or account_side not in ('sender', 'receiver') or type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError('Invalid dataset history scope')
        current = self.resolve(context['case_id'], context['snapshot_ref'])
        if current['history']['availability'] != 'available':
            return unavailable()
        if current['context_revision'] != context['context_revision']:
            raise ValueError('stale_snapshot')
        history = current['history']
        if history['availability'] != 'available':
            return unavailable()
        tx = context['source_payload']['transaction']
        identity = tx[account_side]
        cutoff = instant(history['cutoff']).replace(second=0, microsecond=0)
        start = instant(history['cutoff']) - timedelta(days=7)
        events, totals, count = [], {}, 0
        try:
            with self.connection(self.dataset_store) as db, localcontext() as decimal_context, ExitStack() as stack:
                decimal_context.prec = 200  # exact permitted decimal strings + population sums
                active = db.execute('SELECT version FROM active_dataset WHERE singleton=1').fetchone()
                if active is None or active[0] != context['dataset_version']:
                    raise ValueError('stale_snapshot')
                # Canonical source UTC strings are ISO; julianday compares offsets safely.
                # Explicit projection prevents private fields from entering Python/tool inputs.
                if self.history_index_path is not None:
                    cursor = stack.enter_context(self._index().rows(
                        context['dataset_version'], identity, timestamp(start), timestamp(cutoff),
                        tx['transaction_id']))
                else:
                    cursor = db.execute('''SELECT transaction_id,
                    json_extract(payload_json,'$.event_time_utc'),
                    json_extract(payload_json,'$.event_time_raw'),
                    json_extract(payload_json,'$.time_basis'),
                    json_extract(payload_json,'$.sender_bank'),json_extract(payload_json,'$.sender_account'),
                    json_extract(payload_json,'$.receiver_bank'),json_extract(payload_json,'$.receiver_account'),
                    json_extract(payload_json,'$.paid_amount'),json_extract(payload_json,'$.paid_currency'),
                    json_extract(payload_json,'$.received_amount'),json_extract(payload_json,'$.received_currency')
                    FROM operational_events WHERE version=? AND transaction_id<>?
                    AND julianday(json_extract(payload_json,'$.event_time_utc'))>=julianday(?)
                    AND julianday(json_extract(payload_json,'$.event_time_utc'))<julianday(?)
                    AND ((json_extract(payload_json,'$.sender_bank')=? AND json_extract(payload_json,'$.sender_account')=?)
                    OR (json_extract(payload_json,'$.receiver_bank')=? AND json_extract(payload_json,'$.receiver_account')=?))
                    ORDER BY julianday(json_extract(payload_json,'$.event_time_utc')),transaction_id''',
                        (context['dataset_version'], tx['transaction_id'], timestamp(start), timestamp(cutoff),
                         identity['bank'], identity['account'], identity['bank'], identity['account']))
                for row in cursor:
                    for direction, offset, money in [('outgoing', 4, 8), ('incoming', 6, 10)]:
                        if (row[offset], row[offset + 1]) != (identity['bank'], identity['account']):
                            continue
                        amount, currency = row[money:money + 2]
                        validate('Instant', timestamp(source_instant(row[1])))
                        if not isinstance(amount, str) or not isinstance(currency, str):
                            raise ValueError('Invalid history money')
                        value = Decimal(amount)
                        if not value.is_finite() or value < 0:
                            raise ValueError('Invalid history money')
                        bucket = totals.setdefault(direction, {})
                        bucket[currency] = bucket.get(currency, Decimal(0)) + value
                        count += 1
                        if len(events) < limit:
                            events.append(dict(transaction_id=row[0], occurred_at=timestamp(source_instant(row[1])),
                                               event_time_raw=row[2], time_basis=row[3], direction=direction,
                                               bank=identity['bank'], account=identity['account'], amount=amount, currency=currency))
        except (OSError, sqlite3.Error):
            return unavailable()
        return dict(availability='available', coverage=history['coverage'], cutoff=history['cutoff'],
                    start=history['start'], lookback_days=7, events=events, returned_count=len(events),
                    eligible_count=count, truncated=count > len(events),
                    totals={d: {c: format(v, 'f') for c, v in currencies.items()} for d, currencies in totals.items()})
