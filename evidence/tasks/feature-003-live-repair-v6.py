"""Fresh two-primary/one-diagnostic live check; opt-in and bounded by existing ledger."""
import asyncio
import copy
import importlib.util
import json
import sys
from dataclasses import replace

from fraudlens.investigation.evaluation import verify_seal
from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.provider import OpenAIProvider, ProviderError, scripted_draft
from fraudlens.investigation.validation import validate_report

PATH = ROOT / 'evidence/tasks/feature-003-coverage-v4.py'
SPEC = importlib.util.spec_from_file_location('live_repair_v6_base', PATH)
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)
core, adapter = base.core, base.adapter
PACK = ROOT / 'evals/investigation/development-v6'
OUT = ROOT / 'evals/results/feature-003/development-v6'
IDS = ('DEV6-761', 'DEV6-762', 'DEV6-763')
CONTROLLED = IDS[-1]
for module in (base, adapter, core):
    module.PACK, module.OUT, module.IDS = PACK, OUT, IDS
core.CANARY = b'DEV6_REFERENCE_ONLY_CANARY_20261116'
BASE_METERED = core.Metered


def invalid_candidate(conversation, turn):
    if conversation[0]['data']['case_id'] != 'CASE-763' or turn.kind != 'draft':
        raise ValueError('Wrong diagnostic scope')
    candidate = scripted_draft(conversation, 'grounded')
    if not candidate['observed_facts']:
        raise ValueError('No supplied case facts for diagnostic')
    candidate['observed_facts'][0]['exact_assertions'][0]['value'] = 'AUTHORED-INVALID-EXACT-VALUE'
    return candidate


def diagnostic_roles(packets):
    result = copy.deepcopy(packets)
    for packet in result:
        if packet['scenario_id'] == CONTROLLED:
            packet['role'] = 'diagnostic'
    return result


class FaultProvider(OpenAIProvider):
    attempted = False

    def application_candidate(self, conversation, turn):
        if self.attempted or turn.kind != 'draft' or conversation[0]['data']['case_id'] != 'CASE-763':
            return turn
        self.attempted = True
        original = copy.deepcopy((turn, self.history))
        fault = dict(kind='authored_application_candidate_fault_not_natural_model_error',
            id=CONTROLLED, original_draft_sha256=digest(turn.draft),
            original_private_items_sha256=digest(list(turn.private_items)))
        try:
            candidate = invalid_candidate(conversation, turn)
            fault.update(injected=True, expected_rejection='exact_assertion_mismatch',
                         candidate=candidate, candidate_sha256=digest(candidate))
            result = replace(turn, draft=candidate)
        except ValueError:
            fault.update(injected=False, unexercised_reason='supplied_case_facts_unavailable')
            result = turn
        assert (turn, self.history) == original
        core.frozen(OUT / 'controlled-fault.json', fault)
        return result

    async def next_turn(self, conversation, *args, **kwargs):
        turn = await super().next_turn(conversation, *args, **kwargs)
        return self.application_candidate(conversation, turn)


class Metered(BASE_METERED):
    async def handle_async_request(self, request):
        if self.phase == 'generation' and b'CAL6_EXPECTED_ONLY_CANARY' in request.content:
            raise ProviderError('provider_input_invalid')
        body = json.loads(request.content)
        last = body['input'][-1] if isinstance(body.get('input'), list) and body['input'] else {}
        repair = last.get('role') == 'user' and last.get('content', '').startswith('Repair the draft: output_invalid.')
        try:
            return await super().handle_async_request(request)
        finally:
            if self.latest is not None:
                self.latest.update(input_bytes=len(request.content), repair_request=repair,
                    tool_choice=body.get('tool_choice'), report_schema_sha256=digest(body['text']['format']['schema']))
                self.ledger.save()


def packets_after_generation(records, reference):
    return diagnostic_roles(base.packets_after_generation(records, reference))


def controlled_result(records, ledger):
    record = next((r for r in records if r['id'] == CONTROLLED), None)
    path = OUT / 'controlled-fault.json'
    fault = verify_seal(core.load(path)) if path.exists() else {}
    transports = [a for a in ledger.value['attempts'] if a['phase'] == 'generation' and a['identity'] == CONTROLLED]
    repairs = [a for a in transports if a.get('repair_request')]
    rejected = bool(record and any(e['operation'] == 'repair' and e.get('reason') == 'exact_assertion_mismatch'
                                  for e in record['events']))
    valid = bool(record and record['result']['report'])
    return dict(id=CONTROLLED, excluded_from_primary_quality=True,
        injection_kind='application_candidate_fault', injected=bool(fault.get('injected')),
        intended_rejection_observed=rejected, repair_transport_attempts=len(repairs),
        repair_request_bytes=[a['input_bytes'] for a in repairs],
        subsequent_real_llm_report_valid=valid,
        mechanism_pass=bool(fault.get('injected') and rejected and repairs and valid
            and record['result']['budget']['repairs'] == 1 and record['seconds'] <= 120),
        natural_model_error_claimed=False)


def summarize(records, packets, ratings, judge_meta, ledger, freeze):
    result = base.summarize(records, packets, ratings, judge_meta, ledger, freeze)
    diagnostic = next((p for p in packets if p['scenario_id'] == CONTROLLED), None)
    diagnostic_rating = (ratings or {}).get(('diagnostic', CONTROLLED))
    semantic = None
    if diagnostic and diagnostic_rating:
        packet = {**diagnostic, 'role': 'primary'}
        semantic = core.aggregate([packet], {('primary', CONTROLLED): diagnostic_rating})['reports'][0]
    result.update(kind='two_ordinary_reports_plus_separate_controlled_repair', ordinary_case_count=2,
        controlled_repair=controlled_result(records, ledger),
        controlled_report_raw_rating=semantic,
        controlled_report_quality_pass=semantic['passed'] if semantic and result['quality_assessment_valid'] else None,
        ordinary_successful_within_90=sum(r['id'] != CONTROLLED and r['result']['report'] is not None
                                         and r['seconds'] <= 90 for r in records))
    return result


core.OpenAIProvider, core.Metered = FaultProvider, Metered
core.packets_after_generation, core.summarize = packets_after_generation, summarize


def audit():
    freeze = verify_seal(core.load(OUT / 'freeze.json'))
    protocol = core.load(PACK / 'protocol.json')
    assert core.sha(PACK / 'protocol.json') == freeze['protocol_sha256']
    for name, expected in {**freeze['code_sha256'], **protocol['files_sha256'],
                           **protocol['preserved_artifacts']}.items():
        assert core.sha(ROOT / name) == expected, name
    summary = verify_seal(core.load(OUT / 'summary.json'))
    ledger = core.Ledger(OUT / 'transport-ledger.json')
    attempts = ledger.value['attempts']
    assert len(attempts) <= 25 and sum(a['phase'] == 'judge' for a in attempts) <= 1
    assert all(sum(a['identity'] == identity for a in attempts) <= 8 for identity in IDS)
    generation = [a for a in attempts if a['phase'] == 'generation']
    assert all(a['input_bytes'] <= 48000 for a in generation)
    assert len({a['report_schema_sha256'] for a in generation}) <= 1
    assert all(a['tool_choice'] == 'none' for a in generation if a.get('repair_request'))
    records, citations = [], 0
    inputs = {i['id']: i for i in core.load(PACK / 'inputs.json')}
    for identity in IDS:
        path = OUT / (identity + '.json')
        if not path.exists():
            continue
        saved = verify_seal(core.load(path))
        assert saved['input_sha256'] == digest(inputs[identity]) and saved['freeze_sha256'] == digest(freeze)
        value = saved['result']
        assert value['context_revision'] == inputs[identity]['context']['context_revision']
        assert value['retrieval_version'] == freeze['retrieval_versions'][protocol['retrieval_mode'][identity]]
        assert value['budget']['provider_requests'] <= 8 and value['budget']['repairs'] <= 1
        assert value['budget']['tool_calls'] <= 12 and value['budget']['transient_retries'] <= 1
        if value['report']:
            checked = validate_report(value['report']['draft'], saved['evidence'], value['attempt_id'],
                value['context_revision'], inputs[identity]['context'], value['corpus_version'])
            assert checked['report_id'] == value['report']['report_id']
            citations += len(value['report']['draft']['citations'])
        records.append(saved)
    fault_path = OUT / 'controlled-fault.json'
    if fault_path.exists():
        fault = verify_seal(core.load(fault_path))
        saved = next(r for r in records if r['id'] == CONTROLLED)
        assert any(digest(e['private_items']) == fault['original_private_items_sha256']
                   for e in saved['events'] if e['operation'] == 'dispatch_result')
        if fault.get('injected'):
            assert digest(fault['candidate']) == fault['candidate_sha256']
            try:
                validate_report(fault['candidate'], saved['evidence'], saved['result']['attempt_id'],
                    saved['result']['context_revision'], inputs[CONTROLLED]['context'], saved['result']['corpus_version'])
            except ValueError as error:
                assert str(error) == 'exact_assertion_mismatch'
            else:
                raise AssertionError('Injected invalid candidate was accepted')
    if (OUT / 'judge-packets.json').exists():
        packets = verify_seal(core.load(OUT / 'judge-packets.json'))
        assert [p['scenario_id'] for p in packets if p['role'] == 'primary'] == list(IDS[:2])
        ratings, meta = None, dict(status='unavailable_not_passed')
        if (OUT / 'judge-result.json').exists():
            meta = verify_seal(core.load(OUT / 'judge-result.json'))
            assert meta['packets_sha256'] == digest(packets)
            ratings = base.validate_batch(packets, meta['value'])
        actual = summarize(records, packets, ratings, meta, ledger, freeze)
        for key in ('controlled_repair', 'controlled_report_quality_pass', 'quality_assessment_valid',
                    'passing_development_reports', 'judged_reports', 'calibration'):
            assert summary[key] == actual[key], key
        assert summary['judged_reports'] is None or len(summary['judged_reports']) == 2
    result = dict(status='PASS', kind='development_v6_audit_not_release_acceptance', summary=summary,
        cited_ids_resolved=citations, prior_artifacts_preserved=True, runtime_unchanged=True,
        http_status_counts={str(status): sum(a.get('http_status') == status for a in attempts)
                            for status in {a.get('http_status') for a in attempts}},
        artifact_sha256={p.name: core.sha(p) for p in OUT.glob('*.json') if p.name != 'audit.json'})
    core.frozen(OUT / 'audit.json', result)
    target = ROOT / 'evidence/tasks/feature-003-live-repair-v6-results.json'
    if target.exists():
        assert core.load(target) == result
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    if '--audit' in sys.argv:
        raise SystemExit(audit())
    raise SystemExit(asyncio.run(adapter.main()))
