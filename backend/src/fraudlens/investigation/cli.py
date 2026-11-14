"""Explicit trusted-operator ingestion, worker and synthetic-only probe."""
import argparse
import asyncio
import json
import sqlite3
from pathlib import Path

from fraudlens.investigation.knowledge import KnowledgeStore, stage
from fraudlens.investigation.provider import ProviderError


def main(argv=None):
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare-knowledge')
    prepare.add_argument('--manifest', required=True)
    prepare.add_argument('--store', required=True)
    prepare.add_argument('--stage-only', action='store_true')
    prepare.add_argument('--retrieval')
    probe = commands.add_parser('probe-provider')
    probe.add_argument('--synthetic-only', action='store_true')
    worker = commands.add_parser('worker')
    worker.add_argument('--store', required=True)
    mode = worker.add_mutually_exclusive_group(required=True)
    mode.add_argument('--once', action='store_true')
    mode.add_argument('--poll', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'worker':
            from fraudlens.investigation.settings import load_settings
            from fraudlens.investigation.workflow import InvestigationService
            settings = load_settings()
            if not settings.enabled or not Path(args.store).is_file():
                print('Worker unavailable: enable investigation and prepare its store.')
                return 2
            knowledge = KnowledgeStore(args.store, initialize=False)
            service = InvestigationService(knowledge.repository, knowledge, settings)
            async def work():
                while True:
                    result = await service.work_once()
                    print(json.dumps({'state': result['state'], 'attempt_id': result['attempt_id']}
                                     if result else {'state': 'idle'}), flush=True)
                    if args.once:
                        return
                    await asyncio.sleep(1)
            asyncio.run(work())
            return 0
        if args.command == 'probe-provider':
            from fraudlens.investigation.provider import probe_provider
            from fraudlens.investigation.settings import load_settings
            if not args.synthetic_only:
                print('Explicit --synthetic-only required.')
                return 2
            settings = load_settings()
            if not settings.model.get_secret_value() or not settings.api_key.get_secret_value():
                print('Provider model/key configuration unavailable.')
                return 2
            print(json.dumps(asyncio.run(probe_provider(settings))))
            return 0
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
    except ProviderError as exc:
        print(json.dumps(dict(status='provider_operation_failed', code=exc.code,
                              outcome_unknown=exc.outcome_unknown)))
        return 2
    except (ValueError, OSError, KeyError, sqlite3.Error):
        print('Investigation operation unavailable: check configuration and prepared sources.')
        return 2
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
