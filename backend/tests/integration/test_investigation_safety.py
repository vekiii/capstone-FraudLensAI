"""Frozen safety stimuli plus existing authored negative/recovery controls; no holdout."""
import asyncio
import copy
import importlib.util
import json
from pathlib import Path
from uuid import uuid4

import pytest
from test_investigation_api import runtime as api_runtime

from fraudlens.investigation.context import CaseContextReader
from fraudlens.investigation.models import ROOT, context_digest

runtime = api_runtime


def unit(name):
    path = Path(__file__).parents[1]/'unit'/f'test_investigation_{name}.py'
    spec = importlib.util.spec_from_file_location('safety_'+name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tools = unit('tools')
validation = unit('validation')
transport = unit('openai')
context = unit('context')
workflow = unit('workflow')
harness = tools.harness
pack = validation.pack
workflow_runtime = workflow.runtime


def stimulus(identity):
    # Only the independent safety file; never investigation held-out contexts/answers.
    rows = json.loads((ROOT/'evals/investigation/inputs/safety.json').read_text(encoding='utf-8'))
    return next(x['stimulus'] for x in rows if x['id']==identity)


@pytest.mark.parametrize('identity',['SAFE-01','SAFE-02'])
def test_frozen_injection_cannot_authorize_actions(runtime,knowledge_factory,identity):
    _,service,body,store = runtime
    text = next(iter(stimulus(identity).values()))
    if identity == 'SAFE-01':
        store.publish(knowledge_factory('missing evidence '+text))
    else:
        ctx = CaseContextReader().resolve('CASE-001','fixture',None)
        ctx['source_payload']['risk_assessment']['explanation']=text
        ctx['context_revision']=context_digest(ctx)
        class Reader:
            def resolve(self,*args):
                return ctx
        service.context_reader=Reader()
    run=service.create(body,service.settings.analyst,str(uuid4()))
    result=asyncio.run(service.work_once())
    assert result['attempt_id']==run['attempt_id']
    assert {x['name'] for x in result['trace']} <= {'get_case_facts','get_account_history','search_procedures'}
    assert result['review'] is None
    with store.repository.connection() as db:
        assert db.execute('SELECT count(*) FROM reviews').fetchone()[0]==0


def test_SAFE03_exact_unknown_tool_requests_never_execute(harness):
    repo,attempt,_,_,make=harness
    for i,call in enumerate(stimulus('SAFE-03')['calls']):
        with pytest.raises(ValueError):
            make().execute(str(i),call['name'],call['arguments'])
    assert tools.evidence_rows(repo,attempt)==[]
    assert tools.step_rows(repo,attempt)==[]


def test_SAFE03_history_scope_arguments_are_server_owned(harness):
    for field in ('bank','account','cutoff','limit'):
        with pytest.raises(ValueError):
            harness[-1]().execute('scope-'+field,'get_account_history',{'account_side':'sender',field:'forged'})
    assert tools.evidence_rows(harness[0],harness[1])==[]


def test_SAFE04_foreign_binding(pack):
    validation.test_unknown_or_mismatched_evidence_is_rejected(pack,'other-attempt')


@pytest.mark.parametrize('change',['other-context','wrong-corpus','changed-passage','changed-hash'])
def test_SAFE04_full_bindings(pack,change):
    validation.test_unknown_or_mismatched_evidence_is_rejected(pack,change)


def test_SAFE04_retry_reuse_and_stale_binding(runtime):
    from test_investigation_recovery import (
        test_child_retry_rebinds_valid_evidence_and_preserves_parent,
    )
    test_child_retry_rebinds_valid_evidence_and_preserves_parent(runtime)


def test_SAFE05_bank_and_account():
    context.test_history_cutoff_window_identity_and_focal()


def test_SAFE05_exact_frozen_bank_pair():
    from fraudlens.investigation.context import HistoryReader
    source=stimulus('SAFE-05')
    ctx=context.available()
    events=[dict(x,transaction_id=f'TX-{i+2:03d}',occurred_at='2026-01-04T09:15:00Z') for i,x in enumerate(source['events'])]
    reader=HistoryReader(events=events,accounts={ctx['case_id']:{'sender':dict(bank=source['allowed_bank'],account=source['account'])}})
    found=reader.read(ctx,'sender')
    assert found['eligible_count']==1 and found['totals']=={'EUR':'1.00'}
    assert all(e['bank']==source['allowed_bank'] for e in found['events'])


def test_SAFE06_authored_boundaries_not_heldout():
    context.test_history_empty_unavailable_and_truncated()
    context.test_history_currencies_separate()


@pytest.mark.parametrize('identity',['INV-H07','INV-H08'])
def test_SAFE06_exact_frozen_history(identity):
    from fraudlens.investigation.context import HistoryReader
    root=ROOT/'evals/investigation'
    item=next(x for x in json.loads((root/'inputs/investigation.json').read_text(encoding='utf-8')) if x['id']==identity)
    reference=next(x for x in json.loads((root/'reference/investigation.json').read_text(encoding='utf-8')) if x['id']==identity)['history_expectation']
    result=HistoryReader(**item['history_fixture']).read(item['context'],'sender')
    for key in ('eligible_count','returned_count','truncated','totals','coverage'):
        assert result[key]==reference[key], key
    returned=[e['transaction_id'] for e in result['events']]
    assert returned==reference['eligible_event_ids'][:50]
    assert not set(returned).intersection(reference.get('excluded_event_ids',[]))


def test_SAFE06_oversize_individual_item(harness):
    tools.test_oversized_individual_value_fails_without_clipping(harness)


def test_SAFE07_all_outbound_turns_and_continuations():
    # Actual captured SDK requests over controlled MockTransport; no network.
    limits = transport.LIMITS.copy()
    try:
        # Contract maximum remains 30s; cold SDK/schema imports on Windows can exceed 1s.
        transport.LIMITS['request_timeout']=30
        transport.test_required_private_output_items_and_call_ids_survive_next_turn()
        transport.test_private_late_input_never_reaches_http()
    finally:
        transport.LIMITS.update(limits)
    context.test_history_projection_excludes_private_and_unknown_fields()


def test_SAFE07_actual_canaries_all_sdk_requests_and_index(harness,tmp_path):
    import httpx2

    from fraudlens.investigation.knowledge import stage
    from fraudlens.investigation.provider import OpenAIProvider, ProviderError
    from fraudlens.investigation.tools import definitions
    values=json.loads((ROOT/'evals/investigation/reference/private-canaries.json').read_text(encoding='utf-8'))
    canaries=[v for k,v in values.items() if k.endswith('_canary')]
    assert len(canaries)==3
    # Seed ONLY private history columns and a neighboring reference sidecar.
    _,_,_,reader,make=harness
    reader=copy.deepcopy(reader)
    reader.events=reader.events[:1]
    reader.events[0].update(private_label=canaries[0],reference_answer=canaries[1],reviewer_notes=canaries[2])
    (tmp_path/'private-reference.json').write_text(json.dumps(values),encoding='utf-8')
    executor=make(history_reader=reader)
    history=executor.execute('history','get_account_history',{'account_side':'sender'})
    procedure=executor.execute('procedure','search_procedures',{'query':'money'})
    corpus=stage(tmp_path/'authored-corpus/manifest.json')
    assert all(c not in json.dumps(corpus) for c in canaries)
    prompt=(ROOT/'prompts/application/investigation-v1.md').read_text(encoding='utf-8')
    seen=[]
    def handler(request):
        body=json.loads(request.content)
        seen.append(body)
        assert all(c not in request.content.decode() for c in canaries)
        output=[dict(type='reasoning',id='rs_'+str(len(seen)),summary=[],encrypted_content='OPAQUE'),
                dict(type='function_call',id='fc_'+str(len(seen)),call_id='call_'+str(len(seen)),name='get_case_facts',arguments='{}')]
        return httpx2.Response(200,json=transport.response(output))
    async def run():
        provider=OpenAIProvider('TEST','test-model',prompt=prompt,transport=httpx2.MockTransport(handler))
        messages=transport.messages()
        limits={**transport.LIMITS,'request_timeout':30}
        try:
            await provider.next_turn(messages,definitions(),{},limits)
            for i,result in enumerate((history,procedure),1):
                messages.extend([dict(type='tool_result',call_id='call_'+str(i),result=result)])
                await provider.next_turn(messages,definitions(),{},limits)
            messages.append(dict(type='tool_result',call_id='bad',result={'reference_answer':canaries[1]}))
            with pytest.raises(ProviderError):
                await provider.next_turn(messages,definitions(),{},limits)
            assert len(seen)==3  # Rejected late field never reached transport.
            assert any(x.get('type')=='reasoning' for x in seen[-1]['input'])
            assert any(x.get('type')=='function_call_output' for x in seen[-1]['input'])
        finally:
            await provider.aclose()
    asyncio.run(run())


def test_SAFE08_unknown_citation(pack):
    validation.test_unknown_or_mismatched_evidence_is_rejected(pack,'unknown')


def test_SAFE08_unarchived_passage(pack):
    pack[2][1]['passage']['passage_id']='f'*64
    # Evidence digest binds exact provenance, including original passage identity.
    with pytest.raises(ValueError):
        validation.checked(pack)


def test_SAFE08_actual_missing_archive_lookup(runtime):
    client,_,_,store=runtime
    response=client.get('/api/knowledge/passages/'+'f'*64,params={'corpus':store.latest('corpus')})
    assert response.status_code==404 and response.json()['error']['code']=='evidence_not_found'


def test_SAFE09_exact_assertion(pack):
    validation.test_changed_structured_assertions_and_quotes_are_rejected(pack,'amount')


@pytest.mark.parametrize('change',['path','quote','assertion-owner','quote-owner'])
def test_SAFE09_assertion_subcases(pack,change):
    validation.test_changed_structured_assertions_and_quotes_are_rejected(pack,change)


def test_SAFE09_false_interpretation_separate_from_citation(pack):
    validation.test_valid_reference_can_still_have_a_false_natural_language_interpretation(pack)
    from fraudlens.investigation.evaluation import report_metrics
    rating=dict(id='test',reviewer='SYNTHETIC RATER',rated_at='2026-11-15',report_sha256='a'*64,
                factual=['unsupported'],essential=['missing'],procedural=[],critical=True)
    assert not report_metrics([dict(id='test',status='validated')],[rating])['ratings'][0]['passed']


@pytest.mark.parametrize('field,original,changed',[
    ('transaction.amount','1250.000','1250.00'),
    ('transaction.currency','Australian Dollar','USD')])
def test_SAFE09_frozen_precision_and_currency_mutations(pack,field,original,changed):
    from fraudlens.investigation.tools import content_digest
    evidence=pack[2][0]
    evidence['facts']=[dict(path=field,value=original)]
    evidence['content_sha256']=content_digest(evidence)
    for claim in (pack[3]['summary'][0],pack[3]['observed_facts'][0]):
        claim['exact_assertions']=[dict(evidence_ref=evidence['evidence_id'],path=field,value=changed)]
        claim['quotes']=[]
    with pytest.raises(ValueError):
        validation.checked(pack)


def test_SAFE10_sdk_budget():
    transport.test_strict_request_model_budget_and_no_hidden_retry()
    transport.test_input_limit_includes_prompt_schema_and_private_continuation()
    transport.test_bounded_stream_even_when_content_length_is_absent_or_wrong(200)


def test_SAFE10_workflow_limits(workflow_runtime):
    workflow.test_eight_request_budget_and_twelve_tool_budget(workflow_runtime)


def test_SAFE10_retry_deadline(workflow_runtime):
    workflow.test_one_transient_retry_and_no_access_retry(workflow_runtime)
    workflow.test_deadline_is_hard_and_counts_wait_time(workflow_runtime)


@pytest.mark.parametrize('scenario,state,code',[
    ('invalid_citation','failed','output_invalid'),('refusal','failed','provider_refusal'),
    ('incomplete','failed','provider_incomplete')])
def test_SAFE10_single_repair_outcomes(workflow_runtime,scenario,state,code):
    workflow.test_explicit_outcomes_and_single_repair(workflow_runtime,scenario,state,code)


@pytest.mark.parametrize('status,code',[(401,'provider_access'),(403,'provider_access'),
    (400,'unsupported_capability'),(429,'provider_failure'),(500,'provider_failure')])
def test_SAFE10_transport_failures(status,code):
    if status==429:
        import httpx2

        from fraudlens.investigation.provider import ProviderError
        with pytest.raises(ProviderError) as error:
            transport.run(lambda request:httpx2.Response(429,json={'error':{'message':'TEST'}}))
        assert error.value.code==code and error.value.retryable is True
    else:
        transport.test_safe_access_capability_and_transient_errors(status,code)


def test_SAFE10_connection_failure_no_hidden_retry():
    import httpx2

    from fraudlens.investigation.provider import ProviderError
    seen=[]
    def handler(request):
        seen.append(request)
        raise httpx2.ConnectError('Authored connection failure',request=request)
    with pytest.raises(ProviderError) as error:
        transport.run(handler)
    assert len(seen)==1
    assert error.value.retryable and error.value.outcome_unknown
    transport.test_deadline_cancels_transport()


def test_SAFE11_unknown_restart(runtime):
    from test_investigation_recovery import (
        test_reopen_expired_work_never_replays_and_preserves_known_outcomes,
    )
    test_reopen_expired_work_never_replays_and_preserves_known_outcomes(runtime,'intent')


@pytest.mark.parametrize('boundary',['claim','result','drafting'])
def test_SAFE11_other_restart_boundaries(runtime,boundary):
    from test_investigation_recovery import (
        test_reopen_expired_work_never_replays_and_preserves_known_outcomes,
    )
    test_reopen_expired_work_never_replays_and_preserves_known_outcomes(runtime,boundary)


def test_SAFE11_replay_and_request_conflict(runtime):
    _,service,body,_=runtime
    key=str(uuid4())
    original=service.create(body,service.settings.analyst,key)
    asyncio.run(service.work_once())
    assert service.create(body,service.settings.analyst,key)==original
    with pytest.raises(ValueError,match='request_conflict'):
        service.create({**body,'case_id':'CASE-002'},service.settings.analyst,key)


def test_SAFE11_created_get_is_zero_spend(workflow_runtime):
    workflow.test_creation_and_get_never_dispatch_provider(workflow_runtime)


def test_SAFE12_late_cancellation(runtime):
    from test_investigation_recovery import (
        test_cancel_pending_reply_cannot_record_result_or_publish,
    )
    test_cancel_pending_reply_cannot_record_result_or_publish(runtime)


def test_SAFE12_review_conflict_correction_and_inputs(runtime):
    from test_investigation_review_api import test_review_amendment_etag_replay_and_immutable_draft
    test_review_amendment_etag_replay_and_immutable_draft(runtime)


@pytest.mark.parametrize('changes',[{'rationale':''},{'actor':'forged'}])
def test_SAFE12_empty_rationale_and_forged_actor(runtime,changes):
    from test_investigation_review_api import test_closed_input_and_safe_errors
    test_closed_input_and_safe_errors(runtime,changes)


def test_SAFE12_needs_information_only_request_more(runtime):
    from test_investigation_review_api import action, body

    from fraudlens.investigation.provider import ScriptedProvider
    client,service,request,_=runtime
    service.provider_factory=lambda binding:ScriptedProvider('needs_information')
    service.create(request,service.settings.analyst,str(uuid4()))
    run=asyncio.run(service.work_once())
    assert run['state']=='needs_information'
    for disposition in ('close','escalate'):
        assert action(client,run,'reviews',body(run,disposition=disposition)).status_code==409
    saved=action(client,run,'reviews',body(run,disposition='request_more_information'))
    assert saved.status_code==201
