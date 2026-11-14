"""Trusted-operator offline ingestion only; no provider command in this phase."""
import argparse
import json
from pathlib import Path

from fraudlens.investigation.knowledge import KnowledgeStore, stage


def main(argv=None):
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare-knowledge')
    prepare.add_argument('--manifest', required=True)
    prepare.add_argument('--store', required=True)
    prepare.add_argument('--stage-only', action='store_true')
    prepare.add_argument('--retrieval')
    args = parser.parse_args(argv)
    try:
        if args.stage_only:
            corpus = stage(args.manifest)
            print('Validated reviewed corpus:', corpus['corpus_version'], len(corpus['passages']))
        else:
            config_path = Path(args.retrieval) if args.retrieval else Path(args.manifest).parent / 'retrieval.json'
            config = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else None
            stage(args.manifest)  # Reject unreviewed/invalid sources before opening a store.
            store = KnowledgeStore(args.store)
            version = store.publish(args.manifest)
            if config is not None:
                print('Retrieval version:', store.save_configuration(config))
            print('Published corpus:', version)
        return 0
    except (ValueError, OSError, KeyError):
        print('Knowledge preparation unavailable: check reviewed manifest and source files.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
