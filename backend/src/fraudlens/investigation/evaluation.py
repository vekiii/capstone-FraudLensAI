"""Explicit offline evaluation; never imported by runtime generation."""
import copy
import json
import math
import re
import time
from pathlib import Path

from fraudlens.investigation.models import canonical, digest, validate

SPLITS = ('development', 'held_out')
LANGUAGES = ('en', 'sr-Latn', 'sr-Cyrl')


def _unique(rows):
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or row['id'] in result:
            raise ValueError('Invalid or duplicate evaluation identity')
        result[row['id']] = row
    return result


def retrieval_metrics(rows, references):
    predictions, refs = _unique(rows), _unique(references)
    if predictions.keys() != refs.keys():
        raise ValueError('Evaluation denominator mismatch')
    for row in rows:
        if row['split'] not in SPLITS or row['language'] not in LANGUAGES:
            raise ValueError('Unknown evaluation group')
    def group(selected):
        recall, rr, no_answer, correct = [], [], 0, 0
        for row in selected:
            ref = refs[row['id']]
            if 'input_sha256' in ref and row.get('input_sha256') != ref['input_sha256']:
                raise ValueError('Input hash mismatch')
            hits = row['hits']
            if not isinstance(hits, list) or len(hits) > 5 or len(set(hits)) != len(hits):
                raise ValueError('Invalid ranked results')
            relevant = set(ref['relevant_passage_ids'])
            if ref['answerability'] == 'no_answer':
                if relevant:
                    raise ValueError('Invalid no-answer reference')
                no_answer += 1
                correct += int(not hits and not row.get('error'))
            elif ref['answerability'] == 'answerable' and relevant:
                recall.append(len(relevant.intersection(hits)) / len(relevant))
                rr.append(next((1 / (i + 1) for i, hit in enumerate(hits) if hit in relevant), 0))
            else:
                raise ValueError('Invalid answerability')
        return dict(answerable_count=len(recall), no_answer_count=no_answer,
                    recall_at_5=sum(recall)/len(recall) if recall else None,
                    mrr_at_5=sum(rr)/len(rr) if rr else None,
                    correct_no_match=correct, false_answer=no_answer-correct)
    return {split: {language: group([r for r in rows if r['split'] == split
                                   and (language == 'overall' or r['language'] == language)])
                    for language in ('overall', *LANGUAGES)} for split in SPLITS}


def report_metrics(outcomes, reviews):
    by_id = _unique(outcomes)
    ratings, pairs = [], set()
    for review in reviews:
        required = {'id', 'reviewer', 'rated_at', 'report_sha256', 'factual', 'essential', 'procedural', 'critical'}
        if not isinstance(review, dict) or set(review) != required or review['id'] not in by_id:
            raise ValueError('Invalid review record')
        if not all(isinstance(review[k], str) and review[k].strip() for k in ('reviewer', 'rated_at')):
            raise ValueError('Actual reviewer/date required')
        validate('Digest', review['report_sha256'])
        pair = (review['id'], review['reviewer'])
        if pair in pairs or type(review['critical']) is not bool:
            raise ValueError('Duplicate rating or invalid critical flag')
        pairs.add(pair)
        for key, allowed in [('factual', {'supported','unsupported','uncertain'}),
                             ('essential', {'present','missing','uncertain'}),
                             ('procedural', {'applicable','unsupported','uncertain'})]:
            if not isinstance(review[key], list) or any(x not in allowed for x in review[key]):
                raise ValueError('Invalid human judgment')
        outcome = by_id[review['id']]
        if outcome.get('report_sha256', review['report_sha256']) != review['report_sha256']:
            raise ValueError('Rating/report hash mismatch')
        support = review['factual'].count('supported')/len(review['factual']) if review['factual'] else None
        coverage = review['essential'].count('present')/len(review['essential']) if review['essential'] else None
        passed = (outcome['status'] in ('validated','needs_information') and support is not None
                  and support >= .9 and coverage is not None and coverage >= .8
                  and not review['critical']
                  and (not outcome.get('no_guidance') or all(x == 'applicable' for x in review['procedural'])))
        ratings.append(dict(id=review['id'],reviewer=review['reviewer'],support=support,
                            coverage=coverage,passed=passed))
    disagreements = []
    for identity in by_id:
        originals = [copy.deepcopy(r) for r in reviews if r['id'] == identity]
        judgments = [{k:r[k] for k in ('factual','essential','procedural','critical')} for r in originals]
        if any(j != judgments[0] for j in judgments[1:]):
            disagreements.append(dict(id=identity,original_ratings=originals,resolution=None))
    return dict(report_count=len(outcomes), failures=sum(o['status'] not in ('validated','needs_information') for o in outcomes),
                ratings=ratings,disagreements=disagreements,
                unreviewed_count=sum(not any(r['id']==o['id'] for r in reviews) for o in outcomes))


def selected_inputs(pack, kind, split):
    if kind not in ('retrieval','investigation') or split not in SPLITS:
        raise ValueError('Explicit kind and split required')
    pack = Path(pack)
    partitions = json.loads((pack/'splits.json').read_text(encoding='utf-8'))[kind]
    ids = partitions[split]
    if set(partitions['development']) & set(partitions['held_out']):
        raise ValueError('Overlapping splits')
    # Trusted orchestrator reads combined storage; only selected inputs cross the boundary.
    all_inputs = _unique(json.loads((pack/'inputs'/f'{kind}.json').read_text(encoding='utf-8')))
    result = []
    for identity in ids:
        result.append(input_only(all_inputs[identity]))
    return result


def input_only(item):
    if (not isinstance(item,dict) or not isinstance(item.get('id'),str)
            or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',item['id'])):
        raise ValueError('Safe opaque evaluation ID required')
    fields = ({'id','language','query'} if 'query' in item else
              {'id','language','instruction','context','history_fixture','procedure_queries'})
    if set(item) != fields or item['language'] not in LANGUAGES:
        raise ValueError('Input-only boundary rejected')
    if 'context' in item:
        validate('InvestigationContext',item['context'])
        history = item['history_fixture']
        if not isinstance(history,dict) or set(history) != {'accounts','events'}:
            raise ValueError('Invalid materialized history')
        for event in history['events']:
            allowed = {'transaction_id','occurred_at','bank','account','amount','currency'}
            if not isinstance(event,dict) or not set(event) <= allowed:
                raise ValueError('Private or unsupported history field')
    else:
        validate('SearchArguments',{'query':item['query']})
    return copy.deepcopy(item)


def generate_reports(inputs, runner):
    _unique(inputs)
    clean = [input_only(item) for item in inputs]  # Validate entire batch before callbacks.
    results = []
    for item in clean:
        try:
            result = runner(copy.deepcopy(item))
        except Exception:
            result = {'status':'generation_failure'}
        results.append(dict(id=item['id'],input_sha256=digest(item),result=result))
    return results


def seal(value):
    return dict(version=1,payload=copy.deepcopy(value),sha256=digest(value))


def verify_seal(value):
    if (not isinstance(value,dict) or set(value) != {'version','payload','sha256'}
            or type(value['version']) is not int or value['version'] != 1
            or digest(value['payload']) != value['sha256']):
        raise ValueError('Evaluation seal/version mismatch')
    return copy.deepcopy(value['payload'])


def write_frozen(path, payload):
    """Exclusive immutable result file; never silently replace an earlier attempt."""
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:
        stream.write(canonical(seal(payload))+b'\n')


def offline_retrieval_join(pack, frozen):
    """Explicit reference opening AFTER prediction seal validation."""
    payload = verify_seal(frozen)
    if payload.get('kind') != 'retrieval' or payload.get('split') not in SPLITS:
        raise ValueError('Wrong prediction kind/split')
    rows = payload['rows']
    inputs = selected_inputs(pack,'retrieval',payload['split'])
    expected = {x['id']:digest(x) for x in inputs}
    if {r['id']:r['input_sha256'] for r in rows} != expected:
        raise ValueError('Prediction input binding mismatch')
    references = _unique(json.loads((Path(pack)/'reference/retrieval.json').read_text(encoding='utf-8')))
    return retrieval_metrics(rows,[references[x] for x in expected])


def nearest_rank_p95(milliseconds):
    if not milliseconds or any(not math.isfinite(x) or x < 0 for x in milliseconds):
        raise ValueError('Actual nonnegative measurements required')
    return sorted(milliseconds)[math.ceil(.95*len(milliseconds))-1]


def select_development_cutoff(scored_rows, references):
    """Development-only selection primitive; never accepts a held-out row."""
    if not scored_rows or any(r['split'] != 'development' for r in scored_rows):
        raise ValueError('Development-only selection required')
    scores = [x for row in scored_rows for x in row['scores']]
    if any(not math.isfinite(x) or x < 0 for x in scores):
        raise ValueError('Invalid retrieval score')
    candidates = sorted({0.0,*scores,*(math.nextafter(s,math.inf) for s in scores)})
    feasible=[]
    for cutoff in candidates:
        predictions=[]
        for row in scored_rows:
            if len(row['hits']) != len(row['scores']):
                raise ValueError('Score/rank mismatch')
            predictions.append({**row,'hits':[p for p,s in zip(row['hits'],row['scores']) if s>0 and s>=cutoff]})
        metrics=retrieval_metrics(predictions,references)['development']['overall']
        if metrics['false_answer']==0 and (metrics['recall_at_5'] or 0)>0:
            feasible.append(dict(cutoff=cutoff,metrics=metrics))
    return max(feasible,key=lambda x:(x['metrics']['recall_at_5'],x['cutoff'])) if feasible else None


def verify_pack_inputs(protocol_path):
    """Validate original T052 metadata and input hashes without opening references."""
    import hashlib
    protocol_path = Path(protocol_path)
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    if protocol['status'] != 'frozen' or not protocol['freeze_gate']['t052_complete']:
        raise ValueError('T052 freeze required')
    root = protocol_path.resolve().parents[2]
    for name, expected in protocol['files_sha256'].items():
        if '/inputs/' in name or name.endswith('/splits.json'):
            raw = (root/name).read_bytes().replace(b'\r\n',b'\n')
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError('Frozen input hash mismatch')
    return protocol


def evaluate_retrieval(protocol_path, store_path, configuration, split, output, freeze_path=None):
    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.retrieval import search
    protocol = verify_pack_inputs(protocol_path)
    if configuration not in ('baseline','improved') or split not in SPLITS:
        raise ValueError('Explicit configuration/split required')
    if not freeze_path:
        raise ValueError('Reviewed T055 configuration freeze required; no implicit demo configuration')
    freeze = verify_seal(json.loads(Path(freeze_path).read_text(encoding='utf-8')))
    if freeze.get('status') != 'retrieval_frozen' or freeze.get('t052_bundle_sha256') != protocol['bundle_sha256']:
        raise ValueError('T055 freeze binding mismatch')
    config = freeze['configurations'][configuration]
    store = KnowledgeStore(store_path,initialize=False)
    retrieval = digest(config)
    if store.configuration(retrieval) != config:
        raise ValueError('Archived configuration mismatch')
    inputs = selected_inputs(Path(protocol_path).parent,'retrieval',split)
    rows = []
    for item in inputs:
        start = time.perf_counter()
        try:
            found = search(store,item['query'],protocol['corpus_version'],retrieval)
            hits = [hit['passage']['passage_id'] for hit in found['hits']]
            scores = [hit['score'] for hit in found['hits']]
            error = None
        except (ValueError,OSError):
            hits,scores,error = [],[],'search_failure'
        rows.append(dict(id=item['id'],input_sha256=digest(item),language=item['language'],
                         split=split,hits=hits,scores=scores,error=error,
                         milliseconds=(time.perf_counter()-start)*1000))
    payload = dict(kind='retrieval',split=split,configuration=configuration,
                   corpus_version=protocol['corpus_version'],retrieval_version=retrieval,
                   freeze_sha256=digest(freeze),rows=rows)
    write_frozen(output,payload)
    return dict(count=len(rows),predictions_sha256=digest(payload),status='predictions_frozen')


def import_reviews(records, outcomes, second_subset):
    """Import frozen-rubric per-claim records, preserving every original judgment."""
    required = {'scenario_id','attempt_id','report_id','report_sha256','context_revision',
                'reviewer_identity','reviewed_at','role','claim_id','report_location','claim_text',
                'claim_kind','evidence_ids','judgment','reason','critical_error','essential_fact_id'}
    grouped = {}
    seen = set()
    for row in records:
        if set(row) != required or row['role'] not in ('primary','secondary'):
            raise ValueError('Invalid frozen-rubric rating')
        key = (row['scenario_id'],row['role'],row['reviewer_identity'])
        identity = (*key,row['report_location'],row['claim_id'],row['essential_fact_id'])
        if identity in seen or not row['reason'].strip():
            raise ValueError('Duplicate or unexplained rating')
        seen.add(identity)
        item = grouped.setdefault(key,dict(id=row['scenario_id'],reviewer=row['reviewer_identity'],
            rated_at=row['reviewed_at'],report_sha256=row['report_sha256'],
            factual=[],essential=[],procedural=[],critical=False))
        if item['report_sha256'] != row['report_sha256']:
            raise ValueError('Mixed report versions')
        if row['claim_kind'] == 'observation':
            item['factual'].append(row['judgment'])
        elif row['claim_kind'] == 'procedure':
            item['procedural'].append(row['judgment'])
        elif row['essential_fact_id'] is not None:
            item['essential'].append(row['judgment'])
        else:
            raise ValueError('Unsupported rating unit')
        item['critical'] = item['critical'] or row['critical_error']
    result = report_metrics(outcomes,list(grouped.values()))
    primary = {k[0]:k[2] for k in grouped if k[1]=='primary'}
    secondary = {k[0]:k[2] for k in grouped if k[1]=='secondary'}
    complete = (len(outcomes)==8 and set(primary)==set(_unique(outcomes))
                and all(x in secondary and secondary[x]!=primary.get(x) for x in second_subset))
    result.update(original_records=copy.deepcopy(records),review_complete=complete,
                  quality_acceptance=None)  # No automatic acceptance from an incomplete import.
    return result


def test_report(item, knowledge, database):
    """Materialized input-only test-provider harness, never live LLM quality evidence."""
    import asyncio
    from uuid import uuid4

    from fraudlens.investigation.context import HistoryReader, outbound_context
    from fraudlens.investigation.models import SCHEMA
    from fraudlens.investigation.provider import ScriptedProvider
    from fraudlens.investigation.store import InvestigationRepository
    from fraudlens.investigation.tools import ToolExecutor, definitions
    from fraudlens.investigation.validation import validate_report

    item = input_only(item)
    ctx = item['context']
    # Current outbound projection has no dataset adapter. Preserve failure, no fallback.
    if ctx['source_mode'] != 'fixture':
        return dict(status='context_unavailable',mode='test',usage=None)
    if Path(database).exists():
        raise ValueError('Fresh isolated test database required')
    repo = InvestigationRepository(database)
    attempt = repo.create(ctx,'evaluation-test','create',str(uuid4()),{})
    aid, owner = attempt['attempt_id'],'evaluation-test'
    repo.claim(aid,owner)
    corpus,retrieval = knowledge.latest('corpus'),knowledge.latest('retrieval')
    history = HistoryReader(**item['history_fixture'])
    tools = ToolExecutor(repo,aid,owner,ctx,knowledge,corpus,retrieval,history)
    provider = ScriptedProvider()
    messages = [dict(type='context',data=outbound_context(ctx,'inv_'+uuid4().hex))]
    async def run():
        async with asyncio.timeout(120):
            for _ in range(8):
                sequence = repo.reserve_dispatch(aid,owner)
                turn = await provider.next_turn(messages,definitions(),SCHEMA['$defs']['ReportDraft'],
                    dict(request_timeout=30,max_input_bytes=48000,max_output_tokens=4096,max_response_bytes=2097152))
                with repo.transaction() as db:
                    db.execute("UPDATE provider_dispatches SET outcome='completed' WHERE attempt_id=? AND sequence=?",(aid,sequence))
                if turn.kind=='tools':
                    for call in turn.calls:
                        result=tools.execute(call['call_id'],call['name'],call['arguments'])
                        messages.extend([dict(type='tool_call',**call),
                                         dict(type='tool_result',call_id=call['call_id'],result=result)])
                elif turn.kind=='draft':
                    with repo.connection() as db:
                        evidence=[json.loads(r[0]) for r in db.execute('SELECT content FROM evidence_items WHERE attempt_id=?',(aid,))]
                    report=validate_report(turn.draft,evidence,aid,ctx['context_revision'],ctx,corpus)
                    return dict(status='validated',mode='test',report=report,usage=None,
                                report_sha256=digest(report),outbound_turns=messages)
                else:
                    return dict(status='provider_failure',mode='test',usage=None)
        return dict(status='budget_exhausted',mode='test',usage=None)
    return asyncio.run(run())
