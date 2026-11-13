"""Local inspection only. Import, training and activation remain gated."""
import argparse
import json
import sys
from pathlib import Path

from fraudlens.data_import import inspect_source


class _Arguments(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default message can echo local paths or rejected values.
        raise ValueError('invalid_arguments')


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
    try:
        args = parser.parse_args(argv)
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
    except ValueError:
        report = dict(status='failed', error_codes=['invalid_arguments'])
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    print(f"Inspection {report['status']}; "
          f"{','.join(report['error_codes']) or 'complete read-only scan; mapping unreviewed'}",
          file=sys.stderr)
    return 0 if report['status'] == 'inspected' else 2


if __name__ == '__main__':
    raise SystemExit(main())
