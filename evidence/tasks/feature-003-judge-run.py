"""Explicit offline judge preparation/execution; never regenerate reports."""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from fraudlens.investigation.evaluation import verify_seal, write_frozen
from fraudlens.investigation.judging import RATING_SCHEMA, aggregate, validate_rating
from fraudlens.investigation.models import ROOT, digest

OUT = ROOT / 'evals/results/feature-003/judge-v2'
LIVE = ROOT / 'evals/results/feature-003/live-v1'
AMENDMENT = ROOT / 'evals/investigation/amendments/report-judging-v2.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    amendment = load(AMENDMENT)
    for key in ('base_protocol', 'rubric', 'splits'):
        assert sha(ROOT / amendment[key]['path']) == amendment[key]['sha256']
    for name, expected in amendment['frozen_outcomes_sha256'].items():
        assert sha(LIVE / name) == expected
    refs = {v['id']: v for v in load(ROOT / 'evals/investigation/reference/investigation.json')}
    splits = load(ROOT / 'evals/investigation/splits.json')
    packets = []
    templates = {role: load(LIVE / f'review-cards/{role}-ratings.template.json')
                 for role in ('primary', 'secondary')}
    for role in ('primary', 'secondary'):
        for identity in (splits['investigation']['held_out'] if role == 'primary'
                         else amendment['roles']['secondary']['subset']):
            saved = verify_seal(load(LIVE / ('primary-' + identity + '.json')))
            report = saved['result']['report']
            rows = [u for u in templates[role] if u['scenario_id'] == identity]
            units = []
            for row in rows:
                binding = {k: row[k] for k in ('claim_id', 'report_location', 'claim_kind',
                                              'claim_text', 'evidence_ids', 'essential_fact_id')}
                units.append(dict(unit_id=digest(binding)[:24], **binding))
            reference = {k: refs[identity][k] for k in ('essential_facts', 'expected_missing_fields',
                'expected_limitations', 'guidance_policy', 'history_expectation', 'critical_errors')}
            packet = dict(role=role, scenario_id=identity, failed=report is None, units=units,
                attempt_id=saved['result']['attempt_id'], context_revision=saved['result']['context_revision'],
                report_sha256=digest(report), failure=saved['result']['failure'],
                report=report, evidence=saved['evidence'] if report else [], reference=reference)
            packets.append(packet)
    assert sum(not p['failed'] for p in packets) == 3
    return packets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--approved-cap', type=int, default=0)
    args = parser.parse_args()
    packets = prepare()
    OUT.mkdir(parents=True, exist_ok=True)
    prepared = OUT / 'packets.json'
    if not prepared.exists():
        write_frozen(prepared, packets)
    assert verify_seal(load(prepared)) == packets
    if not args.execute:
        print(json.dumps(dict(state='prepared_not_dispatched', packets=len(packets),
                              requests_planned=3, units=sum(len(p['units']) for p in packets))))
        return 0
    if args.approved_cap != 6:
        raise ValueError('Explicit separately approved six-attempt judge budget required')
    from fraudlens.investigation.environment import read_environment
    environment = read_environment()
    key = environment.get('OPENAI_API_KEY', '')
    if not key:
        raise ValueError('Private key unavailable; no dispatch')
    model = 'gpt-6-luna'
    prompt_path = ROOT / 'prompts/evaluation/report-judge-v2.md'
    prompt = prompt_path.read_text(encoding='utf-8')
    freeze = dict(amendment_sha256=sha(AMENDMENT), packets_sha256=digest(packets),
        prompt_sha256=sha(prompt_path), schema_sha256=digest(RATING_SCHEMA), model=model,
        source_sha256=sha(Path(__file__)), judging_sha256=sha(ROOT / 'backend/src/fraudlens/investigation/judging.py'),
        cap=6, max_retries=0, timeout_seconds=60, max_output_tokens=8192,
        isolation='Separate stateless Responses requests, store=false, no previous_response_id, no other judge outputs')
    freeze_path = OUT / 'freeze.json'
    if not freeze_path.exists():
        write_frozen(freeze_path, freeze)
    assert verify_seal(load(freeze_path)) == freeze
    ledger_path = OUT / 'transport-ledger.json'
    ledger = load(ledger_path) if ledger_path.exists() else dict(cap=6, attempts=[])
    import httpx2
    from openai import OpenAI

    class Transport(httpx2.BaseTransport):
        def __init__(self):
            self.inner = httpx2.HTTPTransport(retries=0)

        def handle_request(self, request):
            if len(ledger['attempts']) >= 6:
                raise ValueError('Judge transport budget exhausted')
            ledger['attempts'].append(dict(packet=current, reserved_at=datetime.now(UTC).isoformat(),
                                           outcome='unknown'))
            temporary = ledger_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
            os.replace(temporary, ledger_path)
            response = self.inner.handle_request(request)
            ledger['attempts'][-1].update(outcome='response_headers_received', status=response.status_code)
            temporary.write_text(json.dumps(ledger, indent=2), encoding='utf-8')
            os.replace(temporary, ledger_path)
            return response

        def close(self):
            self.inner.close()

    ratings = {}
    with OpenAI(api_key=key, max_retries=0, timeout=60,
                http_client=httpx2.Client(transport=Transport(), trust_env=False,
                                         follow_redirects=False, timeout=60)) as client:
        for packet in packets:
            if packet['failed']:
                continue  # Immutable failed outcome, no claims to ask a judge to invent.
            current = packet['role'] + '-' + packet['scenario_id']
            result_path = OUT / (current + '.json')
            if result_path.exists():
                saved = verify_seal(load(result_path))
                assert saved['packet_sha256'] == digest(packet)
                ratings[(packet['role'], packet['scenario_id'])] = validate_rating(packet, saved['rating'])
                continue
            # Do not silently resume an unknown dispatch after a restart.
            if any(a['packet'] == current for a in ledger['attempts']):
                raise ValueError('Packet has prior dispatch; inspect ledger before explicit recovery')
            for attempt in range(2):
                started = time.monotonic()
                try:
                    response = client.responses.create(model=model, store=False,
                        instructions=prompt, input=json.dumps(packet, ensure_ascii=False),
                        max_output_tokens=8192, text=dict(format=dict(type='json_schema',
                            name='report_judge_v2', strict=True, schema=RATING_SCHEMA)))
                    raw = response.model_dump(mode='json')
                    write_frozen(OUT / f'{current}-response-{attempt}.json', raw)
                    if response.status != 'completed':
                        raise ValueError('Judge did not complete')
                    rating = validate_rating(packet, json.loads(response.output_text))
                    saved = dict(packet_sha256=digest(packet), freeze_sha256=digest(freeze),
                        role=packet['role'], scenario_id=packet['scenario_id'],
                        evaluator_kind='llm', evaluator_identity='openai/' + response.model,
                        reviewed_at=datetime.now(UTC).isoformat(), returned_model=response.model,
                        duration_seconds=time.monotonic() - started,
                        request_id=getattr(response, '_request_id', None), rating=rating,
                        usage=raw.get('usage'))
                    write_frozen(result_path, saved)
                    ratings[(packet['role'], packet['scenario_id'])] = rating
                    print(json.dumps(dict(packet=current, state='rated', units=len(rating['units']))), flush=True)
                    break
                except Exception as exc:
                    # Never persist raw error messages: SDK errors may contain private data.
                    write_frozen(OUT / f'{current}-error-{attempt}.json',
                                 dict(error_type=type(exc).__name__, usage='unknown',
                                      duration_seconds=time.monotonic() - started))
                    if attempt or len(ledger['attempts']) >= 6 or getattr(exc, 'status_code', None) in (400, 401, 403, 404):
                        raise RuntimeError('Judge packet failed; safe error record saved') from None
    summary = aggregate(packets, ratings)
    summary.update(protocol_sha256=sha(AMENDMENT), freeze_sha256=digest(freeze),
                   transport_attempts=len(ledger['attempts']), failed_outcomes=[
                       dict(role=p['role'], id=p['scenario_id'], failure=p['failure'],
                            assessment='No report; failed outcome retained without claim ratings')
                       for p in packets if p['failed']])
    write_frozen(OUT / 'summary.json', summary)
    print(json.dumps({k: summary[k] for k in ('report_count', 'failed_reports', 'passing_reports', 'quality_pass')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
