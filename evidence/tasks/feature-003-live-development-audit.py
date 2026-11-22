"""Offline integrity/count audit of the new development run; no provider access."""
import importlib.util
import json
from collections import Counter

from fraudlens.investigation.evaluation import verify_seal, write_frozen
from fraudlens.investigation.judging import aggregate
from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.validation import validate_report

PATH = ROOT / 'evidence/tasks/feature-003-live-development-v2.py'
SPEC = importlib.util.spec_from_file_location('development_v2_frozen_runner', PATH)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def main():
    out = runner.OUT
    freeze = verify_seal(runner.load(out / 'freeze.json'))
    assert runner.sha(PATH) == freeze['runner_sha256']
    assert runner.sha(runner.PACK / 'protocol.json') == freeze['protocol_sha256']
    protocol = runner.load(runner.PACK / 'protocol.json')
    for name, expected in {**freeze['code_sha256'], **protocol['files_sha256']}.items():
        assert runner.sha(ROOT / name) == expected, name
    inputs = {item['id']: item for item in runner.load(runner.PACK / 'inputs.json')}
    records = [verify_seal(runner.load(out / (identity + '.json'))) for identity in runner.IDS]
    ledger = runner.load(out / 'transport-ledger.json')
    assert len(ledger['attempts']) <= 25
    assert sum(a['phase'] == 'judge' for a in ledger['attempts']) <= 1
    for identity in runner.IDS:
        assert sum(a['phase'] == 'generation' and a['identity'] == identity for a in ledger['attempts']) <= 8
    citation_count = 0
    for saved in records:
        value, item = saved['result'], inputs[saved['id']]
        assert saved['input_sha256'] == digest(item)
        assert saved['freeze_sha256'] == digest(freeze)
        assert value['context_revision'] == item['context']['context_revision']
        assert value['corpus_version'] == freeze['corpus_version']
        assert value['retrieval_version'] == freeze['retrieval_versions'][protocol['retrieval_mode'][saved['id']]]
        assert value['provider_mode'] == 'openai' and value['requested_model'] == 'gpt-6-luna'
        assert value['budget']['provider_requests'] <= 8 and value['budget']['tool_calls'] <= 12
        assert value['budget']['repairs'] <= 1
        assert value['report'] is None or value['report']['semantic_review'] == 'not_reviewed'
        if value['report']:
            validated = validate_report(value['report']['draft'], saved['evidence'], value['attempt_id'],
                value['context_revision'], item['context'], value['corpus_version'])
            assert validated['report_id'] == value['report']['report_id']
            citation_count += len(value['report']['draft']['citations'])
    packets = verify_seal(runner.load(out / 'judge-packets.json'))
    judge = verify_seal(runner.load(out / 'judge-result.json'))
    assert judge['packets_sha256'] == digest(packets) and judge['freeze_sha256'] == digest(freeze)
    ratings = runner.validate_batch(packets, judge['value'])
    semantic = aggregate(packets, ratings)
    summary = verify_seal(runner.load(out / 'summary.json'))
    assert summary['judged_reports'] == semantic['reports']
    assert summary['passing_development_reports'] == semantic['passing_reports']
    assert summary['transport_attempts'] == len(ledger['attempts'])
    assert {a['returned_model'] for a in ledger['attempts'] if a.get('returned_model')} == {'gpt-6-luna'}
    known = dict(input_tokens=0, output_tokens=0, total_tokens=0)
    for attempt in ledger['attempts']:
        if isinstance(attempt.get('usage'), dict):
            for key in known:
                known[key] += attempt['usage'].get(key, 0)
    assert known == summary['known_usage']
    report_counts = []
    for packet in packets:
        identity = packet['scenario_id']
        if packet['failed']:
            report_counts.append(dict(id=identity, failed_generation=True, passed=False))
            continue
        rating = ratings[('primary', identity)]
        units = {u['unit_id']: u for u in packet['units']}
        counts = Counter((units[u['unit_id']]['claim_kind'], u['judgment']) for u in rating['units'])
        denominator = Counter(u['claim_kind'] for u in packet['units'])
        report_counts.append(dict(id=identity, failed_generation=False,
            supported_factual=counts[('observation', 'supported')], factual_count=denominator['observation'],
            essential_present=counts[('essential_fact', 'present')], essential_count=denominator['essential_fact'],
            applicable_procedural=counts[('procedure', 'applicable')], procedural_count=denominator['procedure'],
            missingness_correct=rating['missingness_correct'], critical_error=rating['critical_error'],
            additional_issue_count=len(rating['additional_issues']),
            passed=next(r['passed'] for r in semantic['reports'] if r['id'] == identity)))
    names = ['freeze.json', 'summary.json', 'transport-ledger.json', 'judge-packets.json',
             'judge-response.json', 'judge-result.json', *(identity + '.json' for identity in runner.IDS)]
    audit = dict(status='PASS', kind='automated_development_check_not_release_or_human_validation',
        runtime_commit='7ed606c91c0bdc8b44c7318d1ad1d87e8d1bc31e', setup_commit='103c3c0',
        source_and_protocol_unchanged_during_batch=True,
        freeze_sha256=digest(freeze), artifact_sha256={name: runner.sha(out / name) for name in names},
        model='gpt-6-luna', rows=summary['rows'], machine_quality=report_counts,
        passing_development_reports=summary['passing_development_reports'],
        successful_within_90=summary['successful_within_90'],
        all_terminal_within_120=summary['all_terminal_within_120'],
        transport_attempts=len(ledger['attempts']), generation_attempts=sum(a['phase'] == 'generation' for a in ledger['attempts']),
        judge_attempts=sum(a['phase'] == 'judge' for a in ledger['attempts']),
        http_status_counts=dict(Counter(str(a.get('http_status', 'no_response')) for a in ledger['attempts'])),
        known_usage=known, unknown_usage_attempts=summary['unknown_usage_attempts'], spend=None,
        cited_ids_resolved=citation_count, unknown_citation_ids=0,
        unknown_attempts=[{key: a.get(key) for key in ('sequence', 'identity', 'phase', 'outcome', 'headers_seconds')}
                          for a in ledger['attempts'] if not isinstance(a.get('usage'), dict)],
        independent_reference_review='pending', secondary_judge=False, human_validation=False,
        original_release_targets_unchanged=True, additional_provider_calls_by_this_audit=0)
    if (out / 'audit.json').exists():
        assert verify_seal(runner.load(out / 'audit.json')) == audit
    else:
        write_frozen(out / 'audit.json', audit)
    target = ROOT / 'evidence/tasks/feature-003-live-development-v2-results.json'
    if target.exists():
        assert runner.load(target) == audit
    else:
        target.write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
