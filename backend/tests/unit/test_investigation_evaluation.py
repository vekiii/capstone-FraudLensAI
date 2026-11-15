"""Independent authored arithmetic and privacy fixtures; no real evaluation pack."""
import copy
import json

import pytest

from fraudlens.investigation import evaluation as ev
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import digest
from fraudlens.investigation.retrieval import search


def rows():
    return [dict(id='A', split='development', language='en', hits=['x','z']),
            dict(id='B', split='development', language='sr-Latn', hits=['z','y']),
            dict(id='C', split='development', language='sr-Cyrl', hits=[])]


def refs():
    return [dict(id='A', answerability='answerable', relevant_passage_ids=['x','y']),
            dict(id='B', answerability='answerable', relevant_passage_ids=['y']),
            dict(id='C', answerability='no_answer', relevant_passage_ids=[])]


def test_recall_mrr_denominators_languages_and_split():
    result = ev.retrieval_metrics(rows(), refs())['development']
    assert result['overall']['recall_at_5'] == .75
    assert result['overall']['mrr_at_5'] == .75
    assert result['overall']['answerable_count'] == 2
    assert result['overall']['no_answer_count'] == 1
    assert result['overall']['correct_no_match'] == 1
    assert result['overall']['false_answer'] == 0
    assert result['sr-Cyrl']['recall_at_5'] is None
    assert result['en']['recall_at_5'] == .5
    assert ev.retrieval_metrics([], [])['held_out']['overall']['recall_at_5'] is None


def test_missing_or_duplicate_predictions_cannot_disappear():
    for predictions in (rows()[:-1], rows()+[rows()[0]]):
        with pytest.raises(ValueError):
            ev.retrieval_metrics(predictions, refs())


def test_no_match_zero_recall_and_false_answer_counts():
    predictions = rows()
    predictions[0]['hits'] = []
    predictions[2]['hits'] = ['wrong']
    result = ev.retrieval_metrics(predictions, refs())['development']['overall']
    assert result['recall_at_5'] == .5 and result['mrr_at_5'] == .25
    assert result['false_answer'] == 1 and result['correct_no_match'] == 0


def test_seal_detects_hash_and_version_mismatch():
    frozen = ev.seal({'rows': rows()})
    assert ev.verify_seal(frozen) == {'rows': rows()}
    for key, value in [('version', 2), ('sha256', '0'*64), ('payload', {})]:
        bad = {**frozen, key: value}
        with pytest.raises(ValueError):
            ev.verify_seal(bad)


def test_split_projection_never_returns_reference_or_other_split(tmp_path):
    (tmp_path/'inputs').mkdir()
    (tmp_path/'reference').mkdir()
    (tmp_path/'inputs/retrieval.json').write_text(json.dumps([
        dict(id='D',language='en',query='authored question'),
        dict(id='H',language='en',query='HELDOUT-CANARY')]))
    (tmp_path/'reference/retrieval.json').write_text('REFERENCE-CANARY')
    (tmp_path/'splits.json').write_text(json.dumps(dict(retrieval=dict(development=['D'],held_out=['H']))))
    assert ev.selected_inputs(tmp_path,'retrieval','development') == [dict(id='D',language='en',query='authored question')]
    with pytest.raises(ValueError):
        ev.selected_inputs(tmp_path,'retrieval',None)


def test_input_only_generation_rejects_extra_reference_fields():
    item = dict(id='T',language='en',query='authored')
    seen = []
    assert ev.generate_reports([item], lambda x: seen.append(x) or {})[0]['input_sha256'] == digest(item)
    assert seen == [item]
    for key in ('reference_answer','label','reviewer_notes'):
        with pytest.raises(ValueError):
            ev.generate_reports([{**item,key:'PRIVATE-CANARY'}], lambda x: pytest.fail('Must reject before callback'))


def test_zero_claim_uncertain_failure_and_disagreements():
    outcomes = [dict(id='A',status='validated'), dict(id='B',status='provider_failure'),
                dict(id='C',status='validation_failure')]
    rating = dict(id='A',reviewer='author-one',rated_at='2026-11-15',report_sha256='a'*64,
                  factual=['uncertain'],essential=['present'],procedural=[],critical=False)
    other = {**rating,'reviewer':'author-two','factual':['supported']}
    original = copy.deepcopy([rating,other])
    result = ev.report_metrics(outcomes,[rating,other])
    assert result['report_count'] == 3 and result['failures'] == 2
    assert result['ratings'][0]['support'] == 0
    assert len(result['disagreements']) == 1
    assert [rating,other] == original
    zero = {**rating,'factual':[]}
    result = ev.report_metrics(outcomes,[zero])
    assert result['ratings'][0]['support'] is None
    assert result['ratings'][0]['passed'] is False


def test_improved_title_synonym_weight_and_review_gate(knowledge_factory,tmp_path):
    store = KnowledgeStore(tmp_path/'inv.sqlite')
    corpus = store.publish(knowledge_factory('money money'))
    config = dict(algorithm='bm25',k1=1.2,b=.75,maximum_results=5,adequacy_cutoff=0,
                  variant='title_glossary',glossary=dict(status='reviewed',reviewed_by='TEST REVIEWER',
                    reviewed_at='2026-11-15',terms={'novac':['money']}))
    result = search(store,'novac',corpus,store.save_configuration(config))
    assert result['hits']
    direct = search(store,'money',corpus,store.save_configuration(config))
    assert result['hits'][0]['score'] == pytest.approx(direct['hits'][0]['score']*.5)
    title = search(store,'authored',corpus,store.save_configuration(config))
    assert title['hits']
    config['glossary']['status']='staged_unreviewed'
    with pytest.raises(ValueError):
        search(store,'novac',corpus,store.save_configuration(config))


def test_percentile_is_actual_nineteenth_of_twenty():
    assert ev.nearest_rank_p95(list(range(20,0,-1))) == 19
    with pytest.raises(ValueError):
        ev.nearest_rank_p95([])


def test_materialized_generation_uses_exact_context_and_no_reference(knowledge_factory,tmp_path):
    from fraudlens.investigation.context import CaseContextReader
    knowledge=KnowledgeStore(tmp_path/'knowledge.sqlite')
    knowledge.publish(knowledge_factory('money missing evidence'))
    knowledge.save_configuration(dict(algorithm='bm25',k1=1.2,b=.75,maximum_results=5,adequacy_cutoff=0))
    item=dict(id='TEST',language='en',instruction='Authored',
              context=CaseContextReader().resolve('CASE-001','fixture',None),
              history_fixture=dict(accounts={},events=[]),procedure_queries=['missing'])
    result=ev.test_report(item,knowledge,tmp_path/'test.sqlite')
    assert result['status']=='validated' and result['mode']=='test'
    assert result['report']['context_revision']==item['context']['context_revision']
    assert 'PRIVATE-CANARY' not in json.dumps(result['outbound_turns'])
    item['history_fixture']['events']=[dict(reference_answer='PRIVATE-CANARY')]
    with pytest.raises(ValueError):
        ev.test_report(item,knowledge,tmp_path/'never.sqlite')
    assert not (tmp_path/'never.sqlite').exists()


def test_cli_never_implicitly_runs_heldout_or_live(monkeypatch,tmp_path,capsys):
    from fraudlens.investigation.cli import main
    monkeypatch.setattr(ev,'verify_pack_inputs',lambda p:{'bundle_sha256':'test'})
    monkeypatch.setattr('fraudlens.investigation.settings.load_settings',lambda:pytest.fail('No real environment/provider'))
    assert main(['evaluate-reports','--protocol','unused','--provider','openai',
                 '--split','held_out','--store','unused','--output',str(tmp_path/'not-written')])==2
    assert not (tmp_path/'not-written').exists()
    assert 'blocked' in capsys.readouterr().out


def test_frozen_predictions_required_before_reference_open(tmp_path,monkeypatch):
    original=type(tmp_path).read_text
    def read(self,*args,**kwargs):
        if 'reference' in self.parts:
            pytest.fail('Must not open references before seal validation')
        return original(self,*args,**kwargs)
    monkeypatch.setattr(type(tmp_path),'read_text',read)
    with pytest.raises(ValueError):
        ev.offline_retrieval_join(tmp_path,{'version':2,'payload':{},'sha256':'a'*64})


def test_cutoff_primitive_is_development_only_and_prioritizes_no_false_answers():
    predictions=rows()
    predictions[0]['scores']=[2,1]
    predictions[1]['scores']=[2,1]
    predictions[2].update(hits=['wrong'],scores=[.2])
    choice=ev.select_development_cutoff(predictions,refs())
    assert choice['cutoff']==1
    assert choice['metrics']['false_answer']==0
    predictions[0]['split']='held_out'
    with pytest.raises(ValueError):
        ev.select_development_cutoff(predictions,refs())


def test_generation_ids_cannot_be_filesystem_paths():
    with pytest.raises(ValueError):
        ev.generate_reports([dict(id='../escape',language='en',query='test')],
                            lambda item: pytest.fail('Unsafe ID reached runner'))
