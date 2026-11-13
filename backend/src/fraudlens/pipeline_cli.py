"""Local source inspection and reviewed, source-bound dataset import."""
import argparse
import hashlib
import io
import json
import re
import sqlite3
import sys
from pathlib import Path

from fraudlens.data_import import derive_dataset_version, inspect_source, iter_canonical_rows
from fraudlens.data_store import DatasetStore

_ROOT = Path(__file__).resolve().parents[3]
_APPROVAL = _ROOT / 'evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md'
_APPROVAL_PROMPT = _ROOT / 'prompts/development/002-t007-t008-final-team-approval-2026-11-13.md'
_MAPPING_M = 'a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57'
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')


class _Arguments(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default message can echo local paths or rejected values.
        raise ValueError('invalid_arguments')


def _load_authorization(mapping_path: Path) -> dict:
    """Bind execution to the team's final-byte approval, never mapping status flags."""
    raw = mapping_path.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf') or b'\r' in raw.replace(b'\r\n', b''):
        raise ValueError('mapping_mismatch')
    digest = hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()
    review = _APPROVAL.read_text(encoding='utf-8')
    confirmation = _APPROVAL_PROMPT.read_text(encoding='utf-8')
    if (digest != _MAPPING_M
            or '## Collective final-byte approval conveyed by the user' not in review
            or f'| `data/mappings/ibm_hi_small_v1.json` (normalized M; current raw LF also equal) | `{digest}` |' not in review
            or 'Potvrđujem da je cijeli tim pregledao i odobrio konačne izmjene' not in confirmation):
        raise ValueError('mapping_approval_mismatch')
    mapping = json.loads(raw)
    source = mapping['source']
    return {'mapping_sha256': digest, 'source_sha256': source['expected_sha256'],
            'source_size': source['expected_size_bytes'], 'namespace': source['namespace'],
            'member': source['member'],
            'time_policy_sha256': mapping['time']['time_policy_sha256']}


def _file_sha256(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


class _MeasuredReader(io.RawIOBase):
    """Measure the exact binary stream supplied to the CSV decoder."""

    def __init__(self, stream):
        self._stream = stream
        self._digest = hashlib.sha256()
        self.size = 0

    def readable(self):
        return True

    def readinto(self, buffer):
        count = self._stream.readinto(buffer)
        if count:
            self._digest.update(memoryview(buffer)[:count])
            self.size += count
        return count

    def hexdigest(self):
        return self._digest.hexdigest()


def _import(args) -> dict:
    if _SHA256.fullmatch(args.expected_sha256) is None or not args.namespace:
        raise ValueError('invalid_arguments')
    binding = _load_authorization(args.mapping)
    if (args.namespace != binding['namespace'] or args.source.name != binding['member']
            or args.expected_sha256 != binding['source_sha256']):
        raise ValueError('source_binding_mismatch')
    source_hash, source_size = _file_sha256(args.source)
    if (source_hash != args.expected_sha256
            or (binding['source_size'] is not None and source_size != binding['source_size'])):
        raise ValueError('source_mismatch')
    version = derive_dataset_version(
        bytes.fromhex(source_hash), bytes.fromhex(binding['mapping_sha256']),
        bytes.fromhex(binding['time_policy_sha256']))
    store = DatasetStore(args.store)
    try:
        if store.version_status(version) == 'complete':
            counts = store.complete_report(version)
            return dict(status='complete', dataset_version=version, schema_version=1,
                        source_sha256=source_hash,
                        mapping_sha256=binding['mapping_sha256'],
                        repeated=True, **counts)
        store.stage(version, source_records=0, source_sha256=source_hash,
                    mapping_sha256=binding['mapping_sha256'],
                    time_policy_sha256=binding['time_policy_sha256'])
        try:
            with args.source.open('rb') as stream:
                measured = _MeasuredReader(stream)
                with io.BufferedReader(measured) as parser_stream:
                    counts = store.ingest_canonical_rows(version, iter_canonical_rows(
                        parser_stream, namespace=args.namespace, member=binding['member'],
                        compact_collision_index=True))
                if (measured.hexdigest() != source_hash or measured.size != source_size):
                    raise ValueError('source_mismatch')
            store.set_source_records(version, counts['source_records'])
            if not (counts['source_records'] == counts['event_valid'] + counts['event_rejected']
                    and counts['event_valid'] == counts['label_eligible'] + counts['label_ineligible']
                    and counts['label_eligible'] == counts['positives'] + counts['negatives']):
                raise ValueError('row_reconciliation_failed')
            store.complete(version)
            store.activate(version)
        except Exception:
            if store.version_status(version) == 'staged':
                store.fail(version, reason='import_failed')
            raise
        counts = store.complete_report(version)
        return dict(status='complete', dataset_version=version, schema_version=1,
                    source_sha256=source_hash,
                    mapping_sha256=binding['mapping_sha256'],
                    repeated=False, **counts)
    finally:
        store.close()


def main(argv=None):
    parser = _Arguments(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect')
    inspect.add_argument('--source', type=Path, required=True)
    inspect.add_argument('--source-name')
    inspect.add_argument('--release')
    inspect.add_argument('--license-ref')
    inspect.add_argument('--expected-sha256')
    inspect.add_argument('--mapping', type=Path,
                         help='Source-bound pending configuration for read-only inspection only')
    inspect.add_argument('--encoding', default='utf-8')
    inspect.add_argument('--delimiter', default=',')
    inspect.add_argument('--column', action='append', default=[], metavar='ROLE=INDEX',
                         help='Zero-based inspection-only role; never an approved mapping')
    import_command = commands.add_parser('import')
    import_command.add_argument('--source', type=Path, required=True)
    import_command.add_argument('--mapping', type=Path, required=True)
    import_command.add_argument('--namespace', required=True)
    import_command.add_argument('--expected-sha256', required=True)
    import_command.add_argument('--store', type=Path, required=True)
    args = None
    try:
        args = parser.parse_args(argv)
        if args.command == 'import':
            report = _import(args)
            print(json.dumps(report, ensure_ascii=True, sort_keys=True))
            print('Import complete', file=sys.stderr)
            return 0
        columns = {}
        for declaration in args.column:
            role, index = declaration.split('=')
            if role in columns:
                raise ValueError('invalid_arguments')
            columns[role] = int(index)
        report = inspect_source(source=args.source, source_name=args.source_name,
                                release=args.release, license_ref=args.license_ref,
                                expected_sha256=args.expected_sha256, encoding=args.encoding,
                                delimiter=args.delimiter, columns=columns or None,
                                mapping_path=args.mapping)
    except (ValueError, OSError, sqlite3.Error, KeyError, json.JSONDecodeError) as exc:
        if args is not None and args.command == 'import' and isinstance(exc, ValueError) and str(exc) in {
                'source_binding_mismatch', 'source_mismatch', 'mapping_mismatch',
                'mapping_approval_mismatch', 'row_reconciliation_failed'}:
            code = str(exc)
        else:
            code = 'invalid_arguments' if isinstance(exc, ValueError) else 'import_failed'
        report = dict(status='failed', error_codes=[code])
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    if args is not None and args.command == 'import':
        print(f"Import {report['status']}; {','.join(report['error_codes'])}", file=sys.stderr)
    else:
        print(f"Inspection {report['status']}; "
              f"{','.join(report['error_codes']) or 'complete read-only scan; mapping unreviewed'}",
              file=sys.stderr)
    return 0 if report['status'] == 'inspected' else 2


if __name__ == '__main__':
    raise SystemExit(main())
