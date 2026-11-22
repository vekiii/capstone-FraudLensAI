"""Restricted, aggregate-only label audit for finite local inputs.

The service accepts an already frozen partition assignment. It never returns
record-level labels. Its in-memory input is suitable for synthetic contract
checks; a separately measured, verified snapshot pass is required for T218.
"""

import json
import os
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_PURPOSE = 'pretraining_class_audit'
_SHAPES = frozenset({'development_daily', 'partition_totals', 'showcase_total'})
_DEVELOPMENT = ('train', 'validation', 'test')
_PARTITIONS = frozenset((*_DEVELOPMENT, 'development_warmup', 'showcase'))


@dataclass(frozen=True, slots=True)
class _Record:
    identity: str
    instant: datetime
    scoreable: bool
    partition: str
    source: Mapping[str, object]


class LabelAuditService:
    """Serve only permitted aggregate queries with a durable append-only log."""

    def __init__(
        self,
        records: Iterable[Mapping[str, object]],
        *,
        partition_by_id: Mapping[str, str],
        audit_log_path: Path,
    ) -> None:
        self.audit_log_path = Path(audit_log_path)
        prepared = []
        seen = set()
        for source in records:
            if not isinstance(source, Mapping):
                raise ValueError('audit record must be a mapping')
            identity = source.get('transaction_id')
            instant = source.get('occurred_at_utc')
            scoreable = source.get('is_scoreable')
            if not isinstance(identity, str) or not identity or identity in seen:
                raise ValueError('audit transaction_id must be unique nonempty text')
            if not isinstance(instant, datetime) or instant.tzinfo is None:
                raise ValueError('audit instant must be timezone-aware')
            if not isinstance(scoreable, bool):
                raise ValueError('audit eligibility must be boolean')
            partition = partition_by_id.get(identity)
            if partition not in _PARTITIONS:
                raise ValueError('audit partition assignment is missing or invalid')
            if (partition == 'development_warmup') == scoreable:
                raise ValueError('audit eligibility disagrees with partition assignment')
            seen.add(identity)
            prepared.append(_Record(
                identity, instant.astimezone(timezone.utc), scoreable, partition, source,
            ))
        if set(partition_by_id) != seen:
            raise ValueError('audit partition assignment does not match source identities')
        self._records = tuple(prepared)

    def query(
        self,
        *,
        shape: str,
        purpose: str,
        partition: str | None = None,
        start_utc: datetime | None = None,
        end_utc: datetime | None = None,
        transaction_id: str | None = None,
    ) -> tuple[dict[str, object], ...] | dict[str, int]:
        """Authorize the fixed audit shapes; log before releasing any result."""
        query = {
            'shape': self._log_text(shape),
            'partition': self._log_text(partition),
            'start_utc': self._log_time(start_utc),
            'end_utc': self._log_time(end_utc),
            'transaction_id_present': transaction_id is not None,
        }
        permitted = (
            isinstance(shape, str)
            and shape in _SHAPES
            and purpose == _PURPOSE
            and partition is None
            and start_utc is None
            and end_utc is None
            and transaction_id is None
        )
        if not permitted:
            self._append(self._log_text(purpose), query, 'denied')
            raise PermissionError('label audit query is not permitted')
        if shape == 'showcase_total' and self._showcase_already_queried():
            self._append(purpose, query, 'denied')
            raise PermissionError('showcase-wide total has already been released')

        try:
            if shape == 'development_daily':
                result = self._development_daily()
            elif shape == 'partition_totals':
                result = self._partition_totals()
            else:
                result = self._showcase_total()
        except ValueError:
            self._append(purpose, query, 'error')
            raise
        self._append(purpose, query, 'allowed')
        return result

    @staticmethod
    def _log_text(value: object) -> str | None:
        if value is None:
            return None
        return value[:128] if isinstance(value, str) else f'<{type(value).__name__}>'

    @staticmethod
    def _log_time(value: object) -> str | None:
        if value is None:
            return None
        return value.isoformat() if isinstance(value, datetime) else f'<{type(value).__name__}>'

    def _append(self, purpose: str, query: dict[str, object], result: str) -> None:
        event = {
            'time': datetime.now(timezone.utc).isoformat(),
            'purpose': purpose,
            'query': query,
            'result': result,
        }
        encoded = (json.dumps(event, sort_keys=True, separators=(',', ':')) + '\n').encode()
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(
            self.audit_log_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600,
        )
        with os.fdopen(descriptor, 'ab') as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())

    def _showcase_already_queried(self) -> bool:
        if not self.audit_log_path.exists():
            return False
        with self.audit_log_path.open(encoding='utf-8') as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError
                    if event.get('result') == 'allowed' and not isinstance(
                        event.get('query'), dict,
                    ):
                        raise ValueError
                except (json.JSONDecodeError, ValueError):
                    raise ValueError('audit log is malformed; label access stopped') from None
                if event.get('result') == 'allowed' and event['query'].get('shape') == (
                    'showcase_total'
                ):
                    return True
        return False

    @staticmethod
    def _positive(record: _Record) -> int:
        value = record.source.get('is_laundering')
        if type(value) is int and value in (0, 1):
            return value
        if type(value) is str and value in ('0', '1'):
            return int(value)
        raise ValueError('audit label must be encoded as exact 0 or 1')

    def _development_daily(self) -> tuple[dict[str, object], ...]:
        by_day: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for record in self._records:
            if record.partition in _DEVELOPMENT and record.scoreable:
                counts = by_day[record.instant.date().isoformat()]
                counts[0] += 1
                counts[1] += self._positive(record)
        return tuple({
            'utc_day': day,
            'source_count': counts[0],
            'scoreable_count': counts[0],
            'positive_count': counts[1],
        } for day, counts in sorted(by_day.items()))

    def _partition_totals(self) -> tuple[dict[str, object], ...]:
        counts = {partition: [0, 0] for partition in _DEVELOPMENT}
        for record in self._records:
            if record.partition in counts and record.scoreable:
                counts[record.partition][0] += 1
                counts[record.partition][1] += self._positive(record)
        return tuple({
            'partition': partition,
            'scoreable_count': counts[partition][0],
            'positive_count': counts[partition][1],
        } for partition in _DEVELOPMENT)

    def _showcase_total(self) -> dict[str, int]:
        source_count = 0
        scoreable_count = 0
        positive_count = 0
        for record in self._records:
            if record.partition == 'showcase':
                source_count += 1
                if record.scoreable:
                    scoreable_count += 1
                    positive_count += self._positive(record)
        return {
            'source_count': source_count,
            'scoreable_count': scoreable_count,
            'positive_count': positive_count,
        }
