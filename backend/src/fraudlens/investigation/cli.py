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
    freeze = commands.add_parser('freeze-retrieval')
    freeze.add_argument('--protocol',required=True)
    freeze.add_argument('--store',required=True)
    freeze.add_argument('--output',required=True)
    evaluate = commands.add_parser('evaluate-retrieval')
    evaluate.add_argument('--protocol', required=True)
    evaluate.add_argument('--configuration', choices=['baseline','improved'], required=True)
    evaluate.add_argument('--split', choices=['development','held_out'], required=True)
    evaluate.add_argument('--store', required=True)
    evaluate.add_argument('--output', required=True)
    evaluate.add_argument('--freeze')
    join = commands.add_parser('join-retrieval')
    join.add_argument('--protocol', required=True)
    join.add_argument('--predictions', required=True)
    join.add_argument('--output', required=True)
    reports = commands.add_parser('evaluate-reports')
    reports.add_argument('--protocol', required=True)
    reports.add_argument('--provider', choices=['test','openai'], required=True)
    reports.add_argument('--split', choices=['development','held_out'], required=True)
    reports.add_argument('--output', required=True)
    reports.add_argument('--store', required=True)
    reviews = commands.add_parser('summarize-reviews')
    reviews.add_argument('--protocol', required=True)
    reviews.add_argument('--reviews', required=True)
    reviews.add_argument('--outcomes', required=True)
    reviews.add_argument('--output', required=True)
    prepare = commands.add_parser('prepare-knowledge')
    prepare.add_argument('--manifest', required=True)
    prepare.add_argument('--store', required=True)
    prepare.add_argument('--stage-only', action='store_true')
    prepare.add_argument('--retrieval')
    history = commands.add_parser('prepare-history-index')
    history.add_argument('--source-store', required=True)
    history.add_argument('--output', required=True)
    probe = commands.add_parser('probe-provider')
    probe.add_argument('--synthetic-only', action='store_true')
    worker = commands.add_parser('worker')
    worker.add_argument('--store', required=True)
    mode = worker.add_mutually_exclusive_group(required=True)
    mode.add_argument('--once', action='store_true')
    mode.add_argument('--poll', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'prepare-history-index':
            from fraudlens.investigation.history_index import prepare_history_index
            print(json.dumps(prepare_history_index(args.source_store, args.output)))
            return 0
        if args.command in ('freeze-retrieval','evaluate-retrieval','join-retrieval','evaluate-reports','summarize-reviews'):
            from fraudlens.investigation import evaluation
            protocol = evaluation.verify_pack_inputs(args.protocol)
            if args.command == 'freeze-retrieval':
                result=evaluation.freeze_development(args.protocol,args.store,args.output)
                print(json.dumps(result))
                return 0 if result['status']=='retrieval_frozen' else 2
            if args.command == 'evaluate-reports':
                if args.provider == 'openai' or args.split != 'development':
                    # Fail closed before settings/environment/provider initialization.
                    print('Live/held-out report evaluation blocked: T033/T055 prerequisites required; no provider invoked.')
                    return 2
                inputs = evaluation.selected_inputs(Path(args.protocol).parent,'investigation',args.split)
                knowledge = KnowledgeStore(args.store,initialize=False)
                output = Path(args.output)
                work = output.parent/(output.stem+'-test-stores')
                work.mkdir(parents=True,exist_ok=True)
                rows = evaluation.generate_reports(inputs,lambda item: evaluation.test_report(
                    item,knowledge,work/(item['id']+'.sqlite')))
                evaluation.write_frozen(output,dict(kind='reports',mode='test',split=args.split,rows=rows))
                print(json.dumps({'status':'test_provider_only','count':len(rows)}))
                return 0
            if args.command == 'evaluate-retrieval':
                result = evaluation.evaluate_retrieval(args.protocol,args.store,args.configuration,
                            args.split,args.output,args.freeze)
            elif args.command == 'join-retrieval':
                frozen = json.loads(Path(args.predictions).read_text(encoding='utf-8'))
                result = evaluation.offline_retrieval_join(Path(args.protocol).parent,frozen)
                evaluation.write_frozen(args.output,result)
            else:
                records = json.loads(Path(args.reviews).read_text(encoding='utf-8'))
                outcomes = evaluation.verify_seal(json.loads(Path(args.outcomes).read_text(encoding='utf-8')))['outcomes']
                splits = json.loads((Path(args.protocol).parent/'splits.json').read_text(encoding='utf-8'))
                result = evaluation.import_reviews(records,outcomes,splits['second_review_subset'])
                evaluation.write_frozen(args.output,result)
            print(json.dumps({'status':'completed','result_sha256':evaluation.digest(result),
                              't052_bundle_sha256':protocol['bundle_sha256']}))
            return 0
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
