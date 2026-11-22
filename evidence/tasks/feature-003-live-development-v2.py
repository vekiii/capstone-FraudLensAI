"""Opt-in new development evaluation, never replays the original held-out batch."""
import argparse
import asyncio
import copy
import hashlib
import json
import os
import time
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

import httpx2

from fraudlens.investigation.context import HistoryReader
from fraudlens.investigation.evaluation import input_only, verify_seal, write_frozen
from fraudlens.investigation.judging import RATING_SCHEMA, aggregate, validate_rating
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.provider import OpenAIProvider, ProviderError, _bounded_transport
from fraudlens.investigation.settings import load_settings
from fraudlens.investigation.workflow import InvestigationService

PACK = ROOT / 'evals/investigation/development-v2'
OUT = ROOT / 'evals/results/feature-003/development-v2'
IDS = ('DEV2-701', 'DEV2-702', 'DEV2-703')
CANARY = b'DEV2_REFERENCE_ONLY_CANARY_20261116'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def frozen(path, value):
    if Path(path).exists():
        if verify_seal(load(path)) != value:
            raise ValueError('Frozen artifact differs; no overwrite permitted')
    else:
        write_frozen(path, value)


def judge_prompt():
    return (ROOT / 'prompts/evaluation/report-judge-v2.md').read_text(encoding='utf-8-sig') + (
        '\nThis is one batch of new development packets, not a release holdout. '
        'Return one ratings entry per supplied scenario_id; rate each unit only '
        'against its own packet. No assumptions from other packets. All claims, '
        'including hypothesis/procedural prose, must be considered in whole-report flags.')


BATCH_SCHEMA = dict(type='object', additionalProperties=False, required=['ratings'],
    properties=dict(ratings=dict(type='array', maxItems=3, items=dict(
        type='object', additionalProperties=False, required=['scenario_id', 'rating'],
        properties=dict(scenario_id=dict(type='string'), rating=RATING_SCHEMA)))))


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.value = json.loads(self.path.read_text()) if self.path.exists() else dict(cap=25, attempts=[])

    def reserve(self, phase, identity):
        if phase not in ('generation', 'judge') or (
            phase == 'generation' and identity not in IDS or phase == 'judge' and identity != 'batch'
        ):
            raise ValueError('Unknown transport scope')
        # Reload so a second instance cannot silently reset an existing budget.
        if self.path.exists():
            self.value = load(self.path)
        attempts = self.value['attempts']
        if self.value.get('cap') != 25 or len(attempts) >= 25:
            raise ValueError('Global transport cap exhausted')
        count = sum(a['phase'] == phase and a['identity'] == identity for a in attempts)
        if count >= (8 if phase == 'generation' else 1):
            raise ValueError('Scoped transport cap exhausted')
        item = dict(sequence=len(attempts) + 1, phase=phase, identity=identity,
                    reserved_at=datetime.now(UTC).isoformat(), outcome='unknown')
        attempts.append(item)
        self.save()
        return item

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.value, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, self.path)

    def prior(self, phase, identity):
        return any(a['phase'] == phase and a['identity'] == identity for a in self.value['attempts'])


class Metered(httpx2.AsyncBaseTransport):
    def __init__(self, ledger, phase, identity, inner=None):
        self.ledger, self.phase, self.identity = ledger, phase, identity
        self.inner = inner if inner is not None else httpx2.AsyncHTTPTransport(retries=0)
        self.latest = None

    async def handle_async_request(self, request):
        if self.phase == 'generation' and CANARY in request.content:
            raise ProviderError('provider_input_invalid')
        self.latest = self.ledger.reserve(self.phase, self.identity)
        started = time.monotonic()
        try:
            response = await self.inner.handle_async_request(request)
            self.latest.update(http_status=response.status_code,
                               request_id=response.headers.get('x-request-id'))
            return response
        except Exception as exc:
            self.latest['error_type'] = type(exc).__name__
            raise
        finally:
            self.latest['headers_seconds'] = round(time.monotonic() - started, 3)
            self.ledger.save()

    async def aclose(self):
        await self.inner.aclose()


def prepare(out=OUT):
    protocol = load(PACK / 'protocol.json')
    # Hash references for binding only; parse no expectations during generation.
    for name, expected in protocol['files_sha256'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Protocol input/artifact hash mismatch')
    inputs = [input_only(item) for item in load(PACK / 'inputs.json')]
    if tuple(item['id'] for item in inputs) != IDS:
        raise ValueError('Unexpected generation identities')
    if CANARY in json.dumps(inputs, ensure_ascii=False).encode():
        raise ValueError('Reference marker in generation inputs')
    settings = load_settings()
    if settings.model.get_secret_value() != 'gpt-6-luna':
        raise ValueError('Expected explicit model configuration unavailable')
    settings = settings.model_copy(update=dict(enabled=True, provider='openai', source='fixture',
                                                store=out / 'runs.sqlite'))
    knowledge = KnowledgeStore(settings.store)
    corpus = knowledge.publish(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')
    candidate = load(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json')
    control = {**candidate, 'adequacy_cutoff': 1000000,
               'status': 'controlled_no_match_development_fixture'}
    versions = dict(candidate=knowledge.save_configuration(candidate),
                    controlled_no_match=knowledge.save_configuration(control))
    freeze = dict(protocol_sha256=sha(PACK / 'protocol.json'),
        settings=settings.model_dump(mode='json'), model='gpt-6-luna', sdk_version=version('openai'),
        prompt_sha256=sha(ROOT / 'prompts/application/investigation-v2.md'),
        judge_prompt_sha256=digest(judge_prompt()), judge_schema_sha256=digest(BATCH_SCHEMA),
        corpus_version=corpus, retrieval_versions=versions,
        code_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
                    for p in (ROOT / 'backend/src/fraudlens/investigation').glob('*.py')},
        runner_sha256=sha(Path(__file__)), cap=25, judge_timeout=60, judge_output_tokens=8192,
        input_sha256={item['id']: digest(item) for item in inputs})
    frozen(out / 'freeze.json', freeze)
    return inputs, protocol, settings, knowledge, versions, freeze


async def generate(inputs, protocol, settings, knowledge, versions, freeze, ledger, out=OUT):
    # This function has no reference-file read or judge input.
    records = []
    for item in inputs:
        path = out / (item['id'] + '.json')
        if path.exists():
            value = verify_seal(load(path))
            if value['input_sha256'] != digest(item) or value['freeze_sha256'] != digest(freeze):
                raise ValueError('Saved generation binding mismatch')
            records.append(value)
            continue
        if ledger.prior('generation', item['id']):
            raise ValueError('Prior ambiguous dispatch: no automatic case replay')
        retrieval = versions[protocol['retrieval_mode'][item['id']]]
        current = item

        class Reader:
            def resolve(self, case_id, source_mode, snapshot):
                expected = tuple(current['context'][k] for k in ('case_id', 'source_mode', 'snapshot_ref'))
                if (case_id, source_mode, snapshot) != expected:
                    raise ValueError('Materialized input scope mismatch')
                return copy.deepcopy(current['context'])

        class Observed(OpenAIProvider):
            async def next_turn(self, *args, **kwargs):
                turn = await super().next_turn(*args, **kwargs)
                metered.latest.update(outcome='completed', usage=turn.usage,
                    returned_model=turn.returned_model, turn_kind=turn.kind)
                ledger.save()
                return turn

        metered = Metered(ledger, 'generation', item['id'])

        class SelectedKnowledge:
            def latest(self, kind):
                return retrieval if kind == 'retrieval' else knowledge.latest(kind)

            def __getattr__(self, name):
                return getattr(knowledge, name)

        def factory(binding):
            instructions = (binding['prompt'] + '\nSynthetic development instruction: '
                + current['instruction'] + '\nProcedure query hints: '
                + json.dumps(current['procedure_queries'], ensure_ascii=False))
            return Observed(settings.api_key.get_secret_value(), settings.model.get_secret_value(),
                            prompt=instructions, transport=metered)

        service = InvestigationService(knowledge.repository, SelectedKnowledge(), settings, factory,
                                       HistoryReader(**item['history_fixture']))
        service.context_reader = Reader()
        request = {k: item['context'][k] for k in ('case_id', 'source_mode', 'snapshot_ref')}
        started = time.monotonic()
        run = service.create(request, 'automated-development-v2', str(uuid4()))
        # Explicit read-only selection is pinned at creation; no binding is mutated.
        if run['retrieval_version'] != retrieval:
            raise ValueError('Unexpected active retrieval configuration')
        result = await service.work_once()
        record = dict(id=item['id'], input_sha256=digest(item), freeze_sha256=digest(freeze),
            seconds=time.monotonic() - started, result=result,
            evidence=service.evidence(run['attempt_id']), events=service.events(run['attempt_id']))
        write_frozen(path, record)
        records.append(record)
        print(json.dumps(dict(id=item['id'], state=result['state'], seconds=round(record['seconds'], 3),
            provider_requests=result['budget']['provider_requests'],
            failure=result['failure']['code'] if result['failure'] else None)), flush=True)
        if result['failure'] and result['failure']['code'] == 'provider_access':
            raise ValueError('Provider access rejected; stop further dispatches')
    return records


def packets_after_generation(records, reference):
    packets = []
    for saved in records:
        report = saved['result']['report']
        units = []
        if report:
            for section in ('summary', 'observed_facts', 'risk_indicators',
                            'alternative_explanations', 'recommended_checks'):
                for index, claim in enumerate(report['draft'][section]):
                    if claim['kind'] not in ('observation', 'procedure'):
                        continue
                    units.append(dict(unit_id=digest([saved['id'], section, index, claim])[:24],
                        claim_id=f'{section}.{index}', report_location=f'{section}.{index}',
                        claim_kind=claim['kind'], claim_text=claim['text'],
                        evidence_ids=claim['evidence_refs'], essential_fact_id=None))
            for index, fact in enumerate(reference[saved['id']]['essential_facts']):
                units.append(dict(unit_id=digest([saved['id'], 'essential', index, fact])[:24],
                    claim_id=None, report_location=None, claim_kind='essential_fact', claim_text=fact,
                    evidence_ids=[], essential_fact_id=f'E{index + 1:02}'))
        packets.append(dict(role='primary', scenario_id=saved['id'], failed=report is None,
            units=units, report=report, evidence=saved['evidence'],
            reference=reference[saved['id']], failure=saved['result']['failure']))
    return packets


async def judge(records, settings, ledger, freeze, out=OUT):
    if len(records) != 3 or any(not (out / (identity + '.json')).exists() for identity in IDS):
        raise ValueError('All generation outcomes must be sealed before reference opening')
    references = load(PACK / 'reference.json')['items']
    packets = packets_after_generation(records, {r['id']: r for r in references})
    frozen(out / 'judge-packets.json', packets)
    active = [p for p in packets if not p['failed']]
    if not active:
        return packets, {}, dict(status='no_reports_to_rate')
    path = out / 'judge-result.json'
    if path.exists():
        saved = verify_seal(load(path))
        if saved['packets_sha256'] != digest(packets):
            raise ValueError('Judge packet binding mismatch')
        ratings = validate_batch(packets, saved['value'])
        return packets, ratings, saved
    if ledger.prior('judge', 'batch'):
        raise ValueError('Judge already dispatched; no automatic replay')
    from openai import AsyncOpenAI
    metered = Metered(ledger, 'judge', 'batch')
    transport = _bounded_transport(metered)
    transport.input_limit = 200000
    started = time.monotonic()
    try:
        async with asyncio.timeout(60), AsyncOpenAI(api_key=settings.api_key.get_secret_value(), max_retries=0,
                base_url='https://api.openai.com/v1', timeout=60,
                default_headers={'Accept-Encoding': 'identity'},
                http_client=httpx2.AsyncClient(transport=transport, trust_env=False,
                    follow_redirects=False, timeout=60)) as client:
            response = await client.responses.create(model='gpt-6-luna', store=False,
                instructions=judge_prompt(), input=json.dumps(dict(packets=active), ensure_ascii=False),
                max_output_tokens=8192, text=dict(format=dict(type='json_schema',
                    name='development_report_ratings', strict=True, schema=BATCH_SCHEMA)))
        write_frozen(out / 'judge-response.json', response.model_dump(mode='json'))
        metered.latest.update(outcome='completed', returned_model=response.model,
                              usage=response.model_dump(mode='json').get('usage'))
        ledger.save()
        if response.status != 'completed':
            raise ValueError('Judge response incomplete')
        value = json.loads(response.output_text)
        ratings = validate_batch(packets, value)
        saved = dict(value=value, packets_sha256=digest(packets), freeze_sha256=digest(freeze),
            evaluator_kind='automated_same_model_single_judge', human_validation=False,
            request_id=getattr(response, '_request_id', None), returned_model=response.model,
            seconds=time.monotonic() - started, usage=response.model_dump(mode='json').get('usage'))
        write_frozen(path, saved)
        return packets, ratings, saved
    except Exception as exc:
        write_frozen(out / 'judge-error.json', dict(error_type=type(exc).__name__,
            seconds=time.monotonic() - started, status='unavailable_not_passed'))
        return packets, None, dict(status='unavailable_not_passed', error_type=type(exc).__name__)


def validate_batch(packets, value):
    expected = {p['scenario_id']: p for p in packets if not p['failed']}
    if not isinstance(value, dict) or set(value) != {'ratings'} or not isinstance(value['ratings'], list):
        raise ValueError('Invalid judge batch shape')
    rows = value['ratings']
    if any(not isinstance(row, dict) or set(row) != {'scenario_id', 'rating'} for row in rows):
        raise ValueError('Invalid judge batch row')
    if len(rows) != len(expected) or {row['scenario_id'] for row in rows} != set(expected):
        raise ValueError('Missing, duplicate or foreign judge scenario')
    return {('primary', row['scenario_id']): validate_rating(expected[row['scenario_id']], row['rating'])
            for row in rows}


def summarize(records, packets, ratings, judge_meta, ledger, freeze):
    semantic = aggregate(packets, ratings) if ratings is not None else None
    known = dict(input_tokens=0, output_tokens=0, total_tokens=0)
    for item in ledger.value['attempts']:
        if isinstance(item.get('usage'), dict):
            for key in known:
                known[key] += item['usage'].get(key, 0)
    rows = [dict(id=r['id'], state=r['result']['state'], seconds=round(r['seconds'], 3),
        provider_requests=r['result']['budget']['provider_requests'],
        tool_calls=r['result']['budget']['tool_calls'], repairs=r['result']['budget']['repairs'],
        failure=r['result']['failure']['code'] if r['result']['failure'] else None) for r in records]
    return dict(kind='actual_llm_development_check_not_independent_holdout',
        model='gpt-6-luna', freeze_sha256=digest(freeze), human_validation=False,
        old_release_targets_unchanged=True, rows=rows,
        transport_attempts=len(ledger.value['attempts']), maximum_transport_attempts=25,
        known_usage=known, unknown_usage_attempts=sum(not isinstance(a.get('usage'), dict)
            for a in ledger.value['attempts']), spend=None,
        successful_within_90=sum(r['state'] in ('ready_for_review', 'needs_information')
                                 and r['seconds'] <= 90 for r in rows),
        all_terminal_within_120=all(r['seconds'] <= 120 for r in rows),
        judged_reports=semantic['reports'] if semantic else None,
        passing_development_reports=semantic['passing_reports'] if semantic else None,
        judge_status=judge_meta.get('status', 'completed'))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    inputs, protocol, settings, knowledge, versions, freeze = prepare()
    if not args.execute:
        print(json.dumps(dict(status='frozen_not_dispatched', cases=len(inputs), max_attempts=25)))
        return 0
    if not settings.api_key.get_secret_value():
        raise ValueError('Private key unavailable; no dispatch')
    lock = OUT / 'execution.lock'
    with lock.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        ledger = Ledger(OUT / 'transport-ledger.json')
        records = await generate(inputs, protocol, settings, knowledge, versions, freeze, ledger)
        packets, ratings, judge_meta = await judge(records, settings, ledger, freeze)
        summary = summarize(records, packets, ratings, judge_meta, ledger, freeze)
        frozen(OUT / 'summary.json', summary)
        print(json.dumps(summary, indent=2), flush=True)
        return 0
    finally:
        lock.unlink()


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
