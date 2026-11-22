"""Opt-in timeout follow-up, new data/ledger; reuses unchanged v2 runner functions."""
import argparse
import asyncio
import importlib.util
import json
import os
import re
from collections import Counter

from fraudlens.investigation.evaluation import verify_seal
from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.provider import safe_diagnostic

V2 = ROOT / 'evidence/tasks/feature-003-live-development-v2.py'
SPEC = importlib.util.spec_from_file_location('timeout_v3_core', V2)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)
PACK = ROOT / 'evals/investigation/development-v3'
OUT = ROOT / 'evals/results/feature-003/development-v3'
IDS = ('DEV3-721', 'DEV3-722', 'DEV3-723')
core.PACK, core.OUT, core.IDS = PACK, OUT, IDS
core.CANARY = b'DEV3_REFERENCE_ONLY_CANARY_20261116'


class DiagnosticMetered(core.Metered):
    async def handle_async_request(self, request):
        try:
            response = await super().handle_async_request(request)
            rates = {}
            for name in ('x-ratelimit-limit-requests', 'x-ratelimit-remaining-requests',
                         'x-ratelimit-limit-tokens', 'x-ratelimit-remaining-tokens'):
                value = response.headers.get(name, '')
                if re.fullmatch(r'[0-9]{1,18}', value):
                    rates[name] = int(value)
            if rates:
                self.latest['rate_headers'] = rates
                self.ledger.save()
            return response
        except asyncio.CancelledError:
            if self.latest is not None:
                self.latest['error_type'] = 'CancelledError'
                self.ledger.save()
            raise


core.Metered = DiagnosticMetered


def blocked_reason(record):
    if record['result']['state'] != 'failed':
        return None
    if record['result']['failure']['code'] == 'provider_access':
        return 'provider_access'
    for event in reversed(record['events']):
        reason = safe_diagnostic(event.get('diagnostic')).get('reason')
        if reason in ('quota_exhausted', 'rate_limit'):
            return reason
    return None


def audit():
    freeze = verify_seal(core.load(OUT / 'freeze.json'))
    protocol = core.load(PACK / 'protocol.json')
    assert core.sha(PACK / 'protocol.json') == freeze['protocol_sha256']
    assert core.sha(V2) == freeze['runner_sha256']
    for name, expected in {**freeze['code_sha256'], **protocol['files_sha256']}.items():
        assert core.sha(ROOT / name) == expected, name
    for name, expected in protocol['preserved_v2_artifacts'].items():
        assert core.sha(ROOT / name) == expected, name
    summary = verify_seal(core.load(OUT / 'summary.json'))
    ledger = core.load(OUT / 'transport-ledger.json')
    records = [verify_seal(core.load(OUT / (identity + '.json')))
               for identity in IDS if (OUT / (identity + '.json')).exists()]
    assert len(ledger['attempts']) <= 25
    assert all(sum(a['identity'] == identity for a in ledger['attempts']) <= 8 for identity in IDS)
    assert sum(a['phase'] == 'judge' for a in ledger['attempts']) <= 1
    inputs = {item['id']: item for item in core.load(PACK / 'inputs.json')}
    diagnostics = []
    for record in records:
        assert record['input_sha256'] == digest(inputs[record['id']])
        assert record['freeze_sha256'] == digest(freeze)
        assert record['result']['context_revision'] == inputs[record['id']]['context']['context_revision']
        assert record['result']['retrieval_version'] == freeze['retrieval_versions'][protocol['retrieval_mode'][record['id']]]
        for event in record['events']:
            diagnostic = safe_diagnostic(event.get('diagnostic'))
            if diagnostic:
                diagnostics.append(dict(id=record['id'], operation=event['operation'], diagnostic=diagnostic))
    if (OUT / 'judge-result.json').exists():
        packets = verify_seal(core.load(OUT / 'judge-packets.json'))
        judged = verify_seal(core.load(OUT / 'judge-result.json'))
        assert judged['packets_sha256'] == digest(packets)
        ratings = core.validate_batch(packets, judged['value'])
        aggregate = core.aggregate(packets, ratings)
        assert aggregate['reports'] == summary['judged_reports']
    result = dict(status='PASS', kind='development_v3_not_independent_release_evaluation',
        summary=summary, diagnostics=diagnostics,
        http_status_counts=dict(Counter(str(a.get('http_status', 'no_response')) for a in ledger['attempts'])),
        source_and_protocol_unchanged=True, v2_artifacts_preserved=True,
        human_validation=False, original_failed_release_targets_unchanged=True,
        artifact_sha256={p.name: core.sha(p) for p in OUT.glob('*.json') if p.name != 'audit.json'})
    core.frozen(OUT / 'audit.json', result)
    target = ROOT / 'evidence/tasks/feature-003-timeout-v3-results.json'
    if target.exists():
        assert core.load(target) == result
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--audit', action='store_true')
    args = parser.parse_args()
    if args.audit:
        return audit()
    inputs, protocol, settings, knowledge, versions, freeze = core.prepare(out=OUT)
    if not args.execute:
        print(json.dumps(dict(status='frozen_not_dispatched', cases=len(inputs), maximum_attempts=25)))
        return 0
    if (OUT / 'summary.json').exists():
        raise ValueError('Batch completed; use --audit, never replay')
    if not settings.api_key.get_secret_value():
        raise ValueError('Private key unavailable; no dispatch')
    lock = OUT / 'execution.lock'
    with lock.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        ledger = core.Ledger(OUT / 'transport-ledger.json')
        records, stopped = [], None
        for item in inputs:
            try:
                record = (await core.generate([item], protocol, settings, knowledge, versions,
                                              freeze, ledger, out=OUT))[0]
            except ValueError:
                path = OUT / (item['id'] + '.json')
                record = verify_seal(core.load(path)) if path.exists() else None
                if not record or blocked_reason(record) != 'provider_access':
                    raise
            records.append(record)
            stopped = blocked_reason(record)
            if stopped:
                break
        if len(records) == 3 and not stopped:
            packets, ratings, judge_meta = await core.judge(records, settings, ledger, freeze, out=OUT)
            summary = core.summarize(records, packets, ratings, judge_meta, ledger, freeze)
        else:
            known = {key: sum(a.get('usage', {}).get(key, 0) for a in ledger.value['attempts'] if a.get('usage'))
                     for key in ('input_tokens', 'output_tokens', 'total_tokens')}
            summary = dict(kind='development_v3_stopped_for_provider_limit',
                rows=[dict(id=r['id'], state=r['result']['state'], seconds=round(r['seconds'], 3),
                    failure=r['result']['failure']['code'] if r['result']['failure'] else None) for r in records],
                transport_attempts=len(ledger.value['attempts']), known_usage=known,
                unknown_usage_attempts=sum(not a.get('usage') for a in ledger.value['attempts']),
                judged_reports=None, passing_development_reports=None, spend=None, judge_status='not_run')
        summary.update(stopped_for=stopped, not_executed_ids=[identity for identity in IDS
            if identity not in {r['id'] for r in records}], freeze_sha256=digest(freeze))
        summary['transient_retries'] = {r['id']: r['result']['budget']['transient_retries'] for r in records}
        core.frozen(OUT / 'summary.json', summary)
        print(json.dumps(summary, indent=2), flush=True)
        return 0
    finally:
        lock.unlink()


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
