"""Offline scoring aggregation and lineage audit; no provider/network access."""
import ast
import hashlib
import json

from fraudlens.investigation.evaluation import verify_seal, write_frozen
from fraudlens.investigation.judging import aggregate
from fraudlens.investigation.models import ROOT, digest

OUT = ROOT / 'evals/results/feature-003/judge-v2'
LIVE = ROOT / 'evals/results/feature-003/live-v1'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    amendment_path = ROOT / 'evals/investigation/amendments/report-judging-v2.json'
    amendment = load(amendment_path)
    for name, expected in amendment['frozen_outcomes_sha256'].items():
        assert sha(LIVE / name) == expected
    for name in ('base_protocol', 'rubric', 'splits'):
        bound = amendment[name]
        assert sha(ROOT / bound['path']) == bound['sha256']
    freeze = verify_seal(load(OUT / 'freeze.json'))
    assert freeze['amendment_sha256'] == sha(amendment_path)
    assert freeze['source_sha256'] == sha(ROOT / 'evidence/tasks/feature-003-judge-run.py')
    assert freeze['judging_sha256'] == sha(ROOT / 'backend/src/fraudlens/investigation/judging.py')
    assert freeze['prompt_sha256'] == sha(ROOT / 'prompts/evaluation/report-judge-v2.md')
    packets = verify_seal(load(OUT / 'packets.json'))
    assert digest(packets) == freeze['packets_sha256']
    ratings, uses, manifests = {}, [], []
    for packet in packets:
        source = verify_seal(load(LIVE / ('primary-' + packet['scenario_id'] + '.json')))
        assert packet['report_sha256'] == digest(source['result']['report'])
        assert packet['context_revision'] == source['result']['context_revision']
        assert packet['attempt_id'] == source['result']['attempt_id']
        if packet['failed']:
            assert source['result']['report'] is None
            continue
        path = OUT / (packet['role'] + '-' + packet['scenario_id'] + '.json')
        rated = verify_seal(load(path))
        assert rated['packet_sha256'] == digest(packet) and rated['freeze_sha256'] == digest(freeze)
        assert rated['evaluator_kind'] == 'llm' and rated['evaluator_identity'].startswith('openai/')
        ratings[(packet['role'], packet['scenario_id'])] = rated['rating']
        manifests.append(dict(file=path.name, sha256=sha(path), role=packet['role'],
                              scenario_id=packet['scenario_id'], model=rated['returned_model']))
    result = aggregate(packets, ratings)
    ledger = load(OUT / 'transport-ledger.json')
    assert len(ledger['attempts']) <= 6
    for path in OUT.glob('*-response-*.json'):
        raw = verify_seal(load(path))
        if raw.get('usage'):
            uses.append(raw['usage'])
    runtime = []
    for path in (ROOT / 'backend/src/fraudlens/investigation').glob('*.py'):
        if path.name in ('evaluation.py', 'cli.py', 'judging.py'):
            continue  # Explicit offline evaluator/CLI; never runtime reference ingress.
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or '').endswith(('.judging', '.evaluation'))
                assert not ((node.module or '') == 'fraudlens.investigation' and any(
                    a.name in ('judging', 'evaluation') for a in node.names))
        runtime.append(path.name)
    citations, resolved = 0, 0
    for packet in packets:
        if packet['role'] != 'primary' or packet['failed']:
            continue
        known = {e['evidence_id'] for e in packet['evidence']}
        refs = packet['report']['draft']['citations']
        citations += len(refs)
        resolved += sum(c in known for c in refs)
    retrieval = {}
    for name in ('baseline', 'improved'):
        path = ROOT / f'evals/results/feature-003/retrieval-v1/metrics-{name}.json'
        metrics = verify_seal(load(path))
        retrieval[name] = dict(held_out=metrics['held_out'], file_sha256=sha(path))
    original_live = load(ROOT / 'evidence/tasks/feature-003-live-results.json')
    result.update(protocol='report-judging-v2', post_hoc=True,
        judge_transport_attempts=len(ledger['attempts']), judged_outputs=manifests,
        known_judge_usage={k: sum(u.get(k, 0) for u in uses)
                           for k in ('input_tokens', 'output_tokens', 'total_tokens')},
        judge_dispatches_without_usage=len(ledger['attempts']) - len(uses), spend=None,
        citations=dict(resolved=resolved, count=citations,
                       rate=resolved / citations if citations else None,
                       meaning='Exact saved evidence identity; semantic support is separately graded'),
        retrieval=retrieval, live_generation_summary_sha256=sha(ROOT / 'evidence/tasks/feature-003-live-results.json'),
        live_generation_performance=original_live['roles']['demo'],
        preserved_live_outcomes=13, runtime_modules_without_evaluator_imports=runtime,
        human_validation=False, no_generation_rerun=True, no_holdout_tuning=True,
        status='completed_automated_post_hoc_quality_failed')
    write_frozen(OUT / 'audited-summary.json', result)
    safe = {k: v for k, v in result.items() if k not in ('original_ratings', 'runtime_modules_without_evaluator_imports')}
    (ROOT / 'evidence/tasks/feature-003-judge-results.json').write_text(
        json.dumps(safe, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'report_count', 'failed_reports', 'passing_reports',
                                           'quality_pass', 'judge_transport_attempts', 'known_judge_usage')}))


if __name__ == '__main__':
    main()
