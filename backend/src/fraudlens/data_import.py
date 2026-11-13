"""Read-only inspection and reviewed-policy streaming canonical parsing."""
import csv
import hashlib
import io
import json
import re
import struct
from collections import Counter, defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from fraudlens.data_contracts import (
    CanonicalTransaction,
    ImportReport,
    ImportRow,
    ParseResult,
    PrivateEvaluationLabel,
    SourceIdentity,
)

REQUIRED_ROLES = frozenset({
    'timestamp', 'sender_bank', 'sender_account', 'receiver_bank', 'receiver_account',
    'paid_amount', 'paid_currency', 'received_amount', 'received_currency', 'label',
})
ALLOWED_ROLES = REQUIRED_ROLES | {'payment_format'}
HI_SMALL_HEADERS = ['Timestamp', 'From Bank', 'Account', 'To Bank', 'Account',
                    'Amount Received', 'Receiving Currency', 'Amount Paid',
                    'Payment Currency', 'Payment Format', 'Is Laundering']
_MAPPING_ROLES = ['event_time_raw', 'sender_bank', 'sender_account', 'receiver_bank',
                  'receiver_account', 'received_amount', 'received_currency', 'paid_amount',
                  'paid_currency', 'payment_format', 'private_evaluation_label']
_PLAIN = re.compile(r'[+-]?[0-9]+(?:\.[0-9]+)?\Z')
_TIME = re.compile(
    r'[0-9]{4}[-/][0-9]{2}[-/][0-9]{2}[ T][0-9]{2}:[0-9]{2}'
    r'(?::[0-9]{2}(?:\.[0-9]{1,9})?)?(?:Z|[+-][0-9]{2}:[0-9]{2})?\Z')


class _InvalidSource(Exception):
    def __init__(self, code):
        self.code = code


def _normalize(header):
    return header.strip().lstrip('\ufeff').strip().casefold()


def _digest(stream):
    stream.seek(0)
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def _inspection_mapping(path):
    """Read a source-bound pending config for inspection, never approval or import."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate mapping member')
            result[key] = value
        return result

    try:
        with Path(path).open('rb') as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError('Mapping too large')
        mapping = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
        source, policy = mapping['source'], mapping['time']['selected_policy']
        if (any(not isinstance(source[name], str) or not source[name].strip()
                for name in ('source_name', 'release', 'source_data_license', 'member'))
                or Path(source['member']).name != source['member']
                or type(source['expected_size_bytes']) is not int
                or source['expected_size_bytes'] < 1):
            raise ValueError('Invalid source declaration')
        if (mapping['schema_version'] != 1 or mapping['status'] != 'pending_team_review'
                or mapping['executable_mapping'] is not False
                or mapping['execution_policy'] != {'inspection_allowed': True,
                    'import_allowed': False, 'allowed_commands': ['inspect']}
                or mapping['technical_approval']['status'] != 'approved_by_user'
                or source['verified_local_release'] != 8
                or source['local_release_binding_verified'] is not True
                or re.fullmatch(r'[0-9a-f]{64}', source['expected_sha256']) is None
                or source['reference_sha256'] != source['expected_sha256']
                or mapping['csv']['expected_ordered_headers'] != HI_SMALL_HEADERS
                or [column['index'] for column in mapping['columns']] != list(range(11))
                or [column['header'] for column in mapping['columns']] != HI_SMALL_HEADERS
                or [column['role'] for column in mapping['columns']] != _MAPPING_ROLES
                or mapping['csv']['duplicate_exception']['exact_header'] != 'Account'
                or mapping['csv']['duplicate_exception']['zero_based_positions'] != [2, 4]
                or not isinstance(mapping['required_reviews'], dict)
                or set(mapping['required_reviews']) != {'data_scoring_producer', 'frontend_api',
                                                      'investigation', 'priority_simulation'}
                or mapping['time']['verified_source_timezone'] is not None
                or policy['time_basis'] != 'assumed_utc_for_synthetic_benchmark'
                or policy['offset_minutes'] != 0 or policy['approved_as_assumption'] is not True):
            raise ValueError('Invalid pending inspection configuration')
        canonical_policy = json.dumps(policy, sort_keys=True, separators=(',', ':')).encode()
        if hashlib.sha256(canonical_policy).hexdigest() != mapping['time']['time_policy_sha256']:
            raise ValueError('Changed time policy')
        if any(review['status'] != 'pending' or any(review[key] is not None
                for key in ('reviewer', 'date', 'decision'))
               for review in mapping['required_reviews'].values()):
            raise ValueError('This inspection configuration cannot claim team approval')
        return mapping, hashlib.sha256(raw).hexdigest()
    except (OSError, ValueError, KeyError, TypeError):
        raise _InvalidSource('invalid_inspection_mapping') from None


def _select(headers, columns, aliases):
    """Resolve inspection-only roles without allowing duplicate names to overwrite."""
    errors = []
    normalized = [_normalize(header) for header in headers]
    groups = defaultdict(list)
    for index, name in enumerate(normalized):
        groups[name].append(index)
    duplicates = [indices for indices in groups.values() if len(indices) > 1]
    if duplicates:
        errors.append('duplicate_headers')
    selected = dict(columns or {})
    if aliases is not None:
        if columns is not None:
            raise _InvalidSource('invalid_inspection_options')
        for role, names in aliases.items():
            matches = [i for i, header in enumerate(normalized)
                       if header in {_normalize(name) for name in names}]
            if len(matches) == 1:
                selected[role] = matches[0]
            elif len(matches) > 1:
                errors.append('ambiguous_aliases')
    if any(role not in ALLOWED_ROLES or type(index) is not int
           or index < 0 or index >= len(headers) for role, index in selected.items()):
        raise _InvalidSource('invalid_inspection_options')
    if len(set(selected.values())) != len(selected):
        errors.append('ambiguous_aliases')
    missing = sorted(REQUIRED_ROLES - selected.keys()) if columns is not None \
        or aliases is not None else []
    if missing:
        errors.append('missing_roles')
    targets = [i for i, name in enumerate(normalized)
               if i != selected.get('label') and any(
                   word in re.sub(r'[^a-z0-9]', '', name)
                   for word in ('target', 'label', 'fraud', 'launder', 'groundtruth',
                                'referencedecision', 'outcome'))]
    if targets:
        errors.append('target_like_columns')
    unknown = [i for i in range(len(headers)) if i not in selected.values()]
    if unknown:
        errors.append('unknown_columns')
    return selected, dict(normalized_headers=normalized, duplicate_header_groups=duplicates,
                         missing_roles=missing, target_like_columns=targets,
                         unknown_columns=unknown), list(dict.fromkeys(errors))


@lru_cache(maxsize=8192)
def _parse_time(value):
    if not _TIME.fullmatch(value):
        return None
    # datetime is used only for calendar validation. Never normalize/round source precision.
    try:
        datetime.fromisoformat(value.replace('/', '-'))
    except ValueError:
        return None
    offset = re.search(r'(Z|[+-][0-9]{2}:[0-9]{2})$', value)
    zone = offset[0] if offset else 'absent'
    wall = value[:offset.start()] if offset else value
    fraction = wall.partition('.')[2]
    resolution = f'fraction_{len(fraction)}' if fraction else (
        'second' if wall.count(':') == 2 else 'minute')
    return wall.replace('/', '-').replace(' ', 'T'), zone, resolution


def _amount(summary, value):
    stats = summary['amount']
    if not value:
        return
    if not _PLAIN.fullmatch(value):
        stats['non_plain_count'] += 1
        return
    number = Decimal(value)
    stats['plain_count'] += 1
    stats['negative_count'] += number < 0
    stats['zero_count'] += number == 0
    stats['sign_counts']['minus' if value.startswith('-') else (
        'plus' if value.startswith('+') else 'none')] += 1
    integer = value.lstrip('+-').split('.')[0]
    stats['leading_zero_count'] += len(integer) > 1 and integer.startswith('0')
    scale = len(value.partition('.')[2])
    stats['scale_counts'][str(scale)] += 1
    stats['max_integer_digits'] = max(stats['max_integer_digits'],
                                     len(integer))
    for key, compare in [('minimum', lambda a, b: a < b), ('maximum', lambda a, b: a > b)]:
        if stats[key] is None or compare(number, Decimal(stats[key])):
            stats[key] = value


def _summarize(reader, headers, selected):
    by_index = {index: role for role, index in selected.items()}
    summaries = []
    for i in range(len(headers)):
        role = by_index.get(i)
        item = dict(index=i, role=role, missing=0, min_length=None, max_length=0)
        if role in {'paid_amount', 'received_amount'}:
            item['amount'] = dict(plain_count=0, non_plain_count=0, negative_count=0,
                                  zero_count=0, minimum=None, maximum=None,
                                  scale_counts=Counter(), max_integer_digits=0,
                                  sign_counts=Counter(), leading_zero_count=0)
        elif role == 'timestamp':
            item['timestamp'] = dict(valid_count=0, invalid_count=0, resolution_counts=Counter(),
                                     timezone_counts=Counter(), wall_time_ranges={},
                                     lexical_form_counts=Counter())
        elif role == 'label':
            item['label_counts'] = {'0': 0, '1': 0, 'missing': 0, 'other': 0}
        elif role in {'paid_currency', 'received_currency', 'payment_format'}:
            item.update(value_counts={}, unlisted_values_count=0)
        summaries.append(item)
    count = 0
    for row in reader:
        if len(row) != len(headers):
            raise _InvalidSource('record_width_mismatch')
        if any('\x00' in value for value in row):
            raise _InvalidSource('invalid_encoding')
        count += 1
        for item, value in zip(summaries, row):
            length = len(value)
            item['missing'] += not value.strip()
            item['min_length'] = length if item['min_length'] is None else min(
                item['min_length'], length)
            item['max_length'] = max(item['max_length'], length)
            role = item['role']
            if 'amount' in item:
                _amount(item, value)
            elif role == 'timestamp':
                stats = item['timestamp']
                parsed = _parse_time(value)
                if parsed is None:
                    stats['invalid_count'] += 1
                else:
                    wall, zone, resolution = parsed
                    stats['valid_count'] += 1
                    stats['resolution_counts'][resolution] += 1
                    stats['timezone_counts'][zone] += 1
                    stats['lexical_form_counts'][re.sub(r'[0-9]', '9', value)] += 1
                    bounds = stats['wall_time_ranges'].setdefault(zone, [wall, wall])
                    bounds[:] = [min(bounds[0], wall), max(bounds[1], wall)]
            elif role == 'label':
                key = value if value in {'0', '1'} else ('missing' if not value else 'other')
                item['label_counts'][key] += 1
            elif 'value_counts' in item and value:
                counts = item['value_counts']
                if len(value) <= 120 and (value in counts or len(counts) < 64):
                    counts[value] = counts.get(value, 0) + 1
                else:
                    item['unlisted_values_count'] += 1
    if count == 0:
        raise _InvalidSource('header_only')
    return count, summaries


def inspect_source(*, source: Path, source_name: str | None, release: str | None,
                   license_ref: str | None, expected_sha256: str | None = None,
                   encoding: str = 'utf-8', delimiter: str = ',',
                   columns: dict[str, int] | None = None,
                   aliases: dict[str, list[str]] | None = None,
                   mapping_path: Path | None = None) -> dict:
    """Scan an explicit local file; declarations/ordinal roles are never review approval.

    UTF-8 (optional BOM), explicit delimiter, RFC-style double quotes, strict parsing.
    No encoding/dialect guessing. A complete blocked report can contain observations;
    any file-level failure discards prefix summaries and has no trustworthy row total.
    Only currency/format aggregates and 0/1 label counts expose categorical values.
    """
    report = dict(status='failed', error_codes=[], mapping_status='unreviewed_inspection_only',
                  provenance=dict(source_name=source_name, release=release, license_ref=license_ref),
                  sha256=None, size_bytes=None, encoding=encoding, bom=None,
                  dialect=dict(delimiter=delimiter, quotechar='"', doublequote=True,
                               escapechar=None, skipinitialspace=False, strict=True,
                               policy='explicit; successful parse is compatibility evidence'),
                  headers=[], columns=[], row_count=None, complete_parse=False,
                  ambiguities=['mapping_unreviewed'], import_allowed=False)
    mapping = None
    try:
        if mapping_path is not None:
            mapping, mapping_hash = _inspection_mapping(mapping_path)
            bound = mapping['source']
            if (columns is not None or aliases is not None
                    or encoding != mapping['csv']['encoding']
                    or delimiter != mapping['csv']['delimiter']):
                raise _InvalidSource('invalid_inspection_options')
            declarations = (source_name, release, license_ref, expected_sha256)
            expected = (bound['source_name'], bound['release'], bound['source_data_license'],
                        bound['expected_sha256'])
            if Path(source).name != bound['member'] or any(
                    value is not None and value != target
                    for value, target in zip(declarations, expected)):
                raise _InvalidSource('mapping_source_mismatch')
            source_name, release, license_ref, expected_sha256 = expected
            columns = {('timestamp' if role == 'event_time_raw' else
                        'label' if role == 'private_evaluation_label' else role): index
                       for index, role in enumerate(_MAPPING_ROLES)}
            report.update(mapping_status='pending_team_review', mapping_sha256=mapping_hash,
                          time_policy=mapping['time']['selected_policy'], source_timezone=None,
                          label_semantics={'1': mapping['labels']['positive_meaning'],
                                           '0': mapping['labels']['negative_meaning']},
                          provenance=dict(source_name=source_name, release=release,
                                          license_ref=license_ref), ambiguities=['pending_team_review'])
        if encoding not in {'utf-8', 'utf-8-sig'}:
            raise _InvalidSource('unsupported_encoding')
        if delimiter not in {',', ';', '\t', '|'} or (expected_sha256 is not None and
                re.fullmatch(r'[0-9a-f]{64}', expected_sha256) is None):
            raise _InvalidSource('invalid_inspection_options')
        with Path(source).open('rb') as binary:
            report['size_bytes'] = binary.seek(0, 2)
            report['sha256'] = _digest(binary)
            if expected_sha256 is not None and report['sha256'] != expected_sha256:
                raise _InvalidSource('source_mismatch')
            if mapping is not None and report['size_bytes'] != mapping['source']['expected_size_bytes']:
                raise _InvalidSource('source_mismatch')
            binary.seek(0)
            prefix = binary.read(4)
            if prefix.startswith((b'\xff\xfe', b'\xfe\xff', b'\x00\x00\xfe\xff')):
                raise _InvalidSource('unsupported_encoding')
            report['bom'] = prefix.startswith(b'\xef\xbb\xbf')
            report['encoding'] = 'utf-8-sig' if report['bom'] else 'utf-8'
            binary.seek(0)
            wrapper = io.TextIOWrapper(binary, encoding='utf-8-sig', errors='strict', newline='')
            try:
                reader = csv.reader(wrapper, delimiter=delimiter, strict=True)
                headers = next(reader, None)
                if not headers:
                    raise _InvalidSource('empty_source')
                if any('\x00' in header for header in headers):
                    raise _InvalidSource('invalid_encoding')
                if len(headers) > 128 or any(len(header) > 200 for header in headers):
                    raise _InvalidSource('schema_limits_exceeded')
                report['headers'] = headers
                if mapping is not None and (headers != HI_SMALL_HEADERS or report['bom']):
                    raise _InvalidSource('mapping_header_mismatch')
                selected, schema, errors = _select(headers, columns, aliases)
                if mapping is not None:
                    # The exact header, content digest and pending profile were checked above.
                    errors.remove('duplicate_headers')
                    report['approved_duplicate_observation'] = [2, 4]
                    errors.append('pending_team_review')
                report.update(schema)
                count, summaries = _summarize(reader, headers, selected)
            finally:
                wrapper.detach()
            if _digest(binary) != report['sha256']:
                raise _InvalidSource('source_mismatch')
        # Verify the named path still resolves to the scanned bytes, too.
        with Path(source).open('rb') as verification:
            if _digest(verification) != report['sha256']:
                raise _InvalidSource('source_mismatch')
        if not all(isinstance(value, str) and value.strip()
                   for value in (source_name, release, license_ref)):
            errors.append('provenance_incomplete')
        report['ambiguities'].extend(errors)
        for item in summaries:
            if item['role'] == 'timestamp' and item['timestamp']['timezone_counts'].get('absent'):
                report['ambiguities'].append('timezone_absent')
            if item['role'] == 'label' and mapping is None:
                report['ambiguities'].append('label_meaning_unreviewed')
        report['ambiguities'] = list(dict.fromkeys(report['ambiguities']))
        report.update(status='blocked' if errors else 'inspected', error_codes=errors,
                      row_count=count, complete_parse=True, columns=summaries)
    except (_InvalidSource, OSError, UnicodeError, csv.Error) as exc:
        if isinstance(exc, _InvalidSource):
            code = exc.code
        elif isinstance(exc, UnicodeError):
            code = 'invalid_encoding'
        elif isinstance(exc, csv.Error):
            code = 'malformed_csv'
        else:
            code = 'source_unavailable'
        report.update(status='failed', error_codes=[code], row_count=None,
                      complete_parse=False, columns=[])
    return report


# Canonical import boundary. The inspected mapping is pinned externally; this
# parser may be called with authored bytes while the real import CLI stays absent.
_APPROVED_MAPPING_M = 'a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57'
_CANONICAL_TIME = re.compile(r'[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}\Z')
_CANONICAL_MONEY = re.compile(r'(0|[1-9][0-9]*)(?:\.([0-9]{1,6}))?\Z')


def _reviewed_mapping():
    path = Path(__file__).resolve().parents[3] / 'data/mappings/ibm_hi_small_v1.json'
    raw = path.read_bytes()
    if hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() != _APPROVED_MAPPING_M:
        raise ValueError('Reviewed mapping bytes changed')
    return json.loads(raw)


def _frame(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError('Identity namespace/member must be nonempty')
    raw = value.encode('utf-8')
    if len(raw) >= 2**32:
        raise ValueError('Identity member is too long')
    return struct.pack('>I', len(raw)) + raw


def derive_source_identity(namespace: str, member: str, ordinal: int) -> SourceIdentity:
    """Domain-separated public 128-bit D/C IDs; retain full collision inputs."""
    if type(ordinal) is not int or not 1 <= ordinal < 2**64:
        raise ValueError('Invalid pre-filter CSV ordinal')
    framed = _frame(namespace) + _frame(member) + struct.pack('>Q', ordinal)
    tx = hashlib.sha256(b'FraudLensAI/tx/v1\x00' + framed).digest()
    case = hashlib.sha256(b'FraudLensAI/case/v1\x00' + framed).digest()
    return SourceIdentity('D' + tx[:16].hex(), 'C' + case[:16].hex(), tx, case, framed)


def derive_dataset_version(source_digest: bytes, mapping_digest: bytes,
                           policy_digest: bytes) -> str:
    if any(type(digest) is not bytes or len(digest) != 32
           for digest in (source_digest, mapping_digest, policy_digest)):
        raise ValueError('DatasetVersion requires three full SHA-256 digests')
    return 'dv_' + hashlib.sha256(b'FraudLensAI/dataset-version/v1\x00'
                                   + source_digest + mapping_digest + policy_digest).hexdigest()


def verify_source_digest(raw: bytes, expected_sha256: str) -> bool:
    return (isinstance(raw, bytes) and isinstance(expected_sha256, str)
            and re.fullmatch(r'[0-9a-f]{64}', expected_sha256) is not None
            and hashlib.sha256(raw).hexdigest() == expected_sha256)


class IdentityRegistry:
    """Detect public-ID, full-digest, input and observable-fact collisions."""

    def __init__(self):
        self._seen = {}

    def register(self, public_id: str, full_digest: bytes,
                 framed_input: bytes, fact_digest: bytes) -> None:
        if (not isinstance(public_id, str) or len(public_id) != 33
                or public_id[0] not in 'DC'
                or re.fullmatch(r'[0-9a-f]{32}', public_id[1:]) is None
                or len(full_digest) != 32):
            raise ValueError('Invalid identity registry entry')
        identity = (bytes(full_digest), bytes(framed_input), bytes(fact_digest))
        existing = self._seen.get(public_id)
        if existing is not None and existing != identity:
            raise ValueError('Identity collision or changed fact')
        self._seen[public_id] = identity

    def __len__(self):
        return len(self._seen)


def _join_key(bank: str, account: str) -> bytes:
    return _frame(bank) + _frame(account)


def _time_coordinate(raw: str):
    if _CANONICAL_TIME.fullmatch(raw) is None:
        raise ValueError('invalid_timestamp')
    try:
        wall = datetime.strptime(raw, '%Y/%m/%d %H:%M').replace(tzinfo=UTC)
    except ValueError:
        raise ValueError('invalid_timestamp') from None
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    delta = wall - epoch
    ns = ((delta.days * 86400 + delta.seconds) * 1_000_000_000)
    return wall, ns


def _canonical_amount(raw: str) -> str:
    match = _CANONICAL_MONEY.fullmatch(raw)
    if match is None or len(raw.split('.', 1)[0]) > 13:
        raise ValueError('invalid_amount')
    return raw


def _party(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip() or len(raw) > 120:
        raise ValueError('invalid_party')
    return raw


def _read_canonical_csv(source):
    """Yield source records from a binary stream; CSV ordinal counts records, not lines."""
    stream = io.BytesIO(source) if isinstance(source, bytes) else source
    text = io.TextIOWrapper(stream, encoding='utf-8', errors='strict', newline='')
    reader = csv.reader(text, delimiter=',', quotechar='"', doublequote=True,
                        skipinitialspace=False, strict=True)
    try:
        header = next(reader, None)
        if header is None:
            raise ValueError('empty_source')
        if '\x00' in ''.join(header) or header != HI_SMALL_HEADERS:
            raise ValueError('mapping_header_mismatch')
        ordinal = 0
        for row in reader:
            ordinal += 1
            if len(row) != 11 or '\x00' in ''.join(row):
                raise ValueError('record_width_or_encoding_mismatch')
            yield ordinal, row
        if ordinal == 0:
            raise ValueError('header_only')
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError('malformed_csv_or_encoding') from exc
    finally:
        if not isinstance(source, bytes):
            text.detach()


def _private_label(raw: str):
    if raw == '0':
        return 'eligible_negative', 0
    if raw == '1':
        return 'eligible_positive', 1
    if raw == '':
        return 'missing', None
    return 'invalid', None


def _canonical_event(row, identity, ordinal, mapping):
    time, epoch_ns = _time_coordinate(row[0])
    sender_bank, sender_account = _party(row[1]), _party(row[2])
    receiver_bank, receiver_account = _party(row[3]), _party(row[4])
    received_amount, paid_amount = _canonical_amount(row[5]), _canonical_amount(row[7])
    currencies = mapping['money_policy']['source_currency_allowlist']
    if row[6] not in currencies or row[8] not in currencies:
        raise ValueError('unsupported_currency')
    payment = row[9] or None
    if payment is not None and payment not in mapping['payment_format_policy']['allowed_source_values']:
        raise ValueError('unsupported_payment_format')
    facts = [row[0], sender_bank, sender_account, receiver_bank, receiver_account,
             received_amount, row[6], paid_amount, row[8], payment]
    fact_digest = hashlib.sha256(json.dumps(facts, ensure_ascii=True,
                             separators=(',', ':')).encode('utf-8')).digest()
    return CanonicalTransaction(
        transaction_id=identity.transaction_id, case_id=identity.case_id,
        source_ordinal=ordinal, event_time_raw=row[0], event_time_utc=time,
        event_time_epoch_ns=epoch_ns,
        time_basis='assumed_utc_for_synthetic_benchmark',
        sender_bank=sender_bank, sender_account=sender_account,
        receiver_bank=receiver_bank, receiver_account=receiver_account,
        sender_join_key=_join_key(sender_bank, sender_account),
        receiver_join_key=_join_key(receiver_bank, receiver_account),
        paid_amount=paid_amount, paid_currency=row[8],
        received_amount=received_amount, received_currency=row[6],
        payment_format=payment, event_fact_digest=fact_digest)


def iter_canonical_rows(source, *, namespace: str, member: str,
                        compact_collision_index: bool = False):
    """Stream one accounted record at a time for a transactional staged importer.

    A structural error can occur after earlier yielded records; callers must
    discard/mark failed the whole stage and must not publish a partial report.
    """
    mapping = _reviewed_mapping()
    _frame(namespace)
    _frame(member)
    registry = IdentityRegistry() if not compact_collision_index else None
    seen_ids = set() if compact_collision_index else None
    for ordinal, row in _read_canonical_csv(source):
        identity = derive_source_identity(namespace, member, ordinal)
        try:
            event = _canonical_event(row, identity, ordinal, mapping)
        except ValueError as exc:
            yield ImportRow(ordinal, 'event_rejected', str(exc), None), None, None
            continue
        if compact_collision_index:
            keys = (b'D' + identity.full_digest[:16],
                    b'C' + identity.case_full_digest[:16])
            if any(key in seen_ids for key in keys):
                raise ValueError('Identity collision')
            seen_ids.update(keys)
        else:
            registry.register(identity.transaction_id, identity.full_digest,
                              identity.framed_input, event.event_fact_digest)
            registry.register(identity.case_id, identity.case_full_digest,
                              identity.framed_input, event.event_fact_digest)
        status, value = _private_label(row[10])
        label = PrivateEvaluationLabel(identity.transaction_id, ordinal, status, value)
        yield ImportRow(ordinal, 'event_valid', None, status), event, label


def parse_canonical_source(source, *, namespace: str, member: str) -> ParseResult:
    """Aggregate a bounded authored fixture; large imports use iter_canonical_rows."""
    events, labels, rows = [], [], []
    try:
        for row_status, event, label in iter_canonical_rows(
                source, namespace=namespace, member=member):
            rows.append(row_status)
            if event is not None:
                events.append(event)
                labels.append(label)
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        report = ImportReport(None, 0, 0, 0, 0, 0, 0, False, (str(exc),))
        return ParseResult('failed', report)
    eligible = sum(label.value is not None for label in labels)
    positives = sum(label.value == 1 for label in labels)
    negatives = sum(label.value == 0 for label in labels)
    report = ImportReport(len(rows), len(events), len(rows) - len(events),
                          eligible, len(events) - eligible, positives, negatives, True)
    if not report.reconciled():
        raise AssertionError('Import row accounting invariant failed')
    return ParseResult('complete', report, events, labels, rows)
