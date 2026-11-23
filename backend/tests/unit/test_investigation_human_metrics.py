"""Authored review completeness/disagreement tests; never reads real ratings."""
import importlib.util

from fraudlens.investigation.models import ROOT


def helper():
    spec=importlib.util.spec_from_file_location('authored_human_metrics',ROOT/'evidence/tasks/feature-003-finalize-reviews.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_claim_ratings_cannot_complete_review_and_disagreements_survive():
    module=helper()
    outcomes=[dict(id=str(i),status='validated',report_sha256='a'*64,report_id='a'*64) for i in range(8)]
    def rating(identity,role,reviewer,judgment):
        return dict(scenario_id=identity,role=role,reviewer_identity=reviewer,reviewed_at='2026-11-15',
                    report_sha256='a'*64,report_id='a'*64,reason='Authored independent judgment',critical_error=False,
                    essential_fact_id=None,claim_kind='observation',claim_id='claim1',report_location='/summary/0',judgment=judgment)
    rows=[rating(str(i),'primary','TEST A','supported') for i in range(8)]
    rows.extend(rating(str(i),'secondary','TEST B','unsupported') for i in range(4))
    outcomes[0]['required_review_units']=[('primary','/observed_facts/0','claim2',None)]
    result=module.finalize(outcomes,rows,[],['0','1','2','3'])
    assert result['review_complete'] is False
    assert len(result['disagreements'])==4
    assert result['original_records']==rows


def test_one_critical_error_fails_pack_even_when_seven_reports_pass():
    module=helper()
    outcomes=[dict(id=str(i),status='validated',report_sha256='a'*64,report_id='a'*64) for i in range(8)]
    rows=[]
    for i in range(8):
        for role,reviewer in [('primary','TEST A')]+([('secondary','TEST B')] if i<4 else []):
            base=dict(scenario_id=str(i),role=role,reviewer_identity=reviewer,reviewed_at='2026-11-15',
                report_sha256='a'*64,report_id='a'*64,reason='Authored test',critical_error=i==0,
                essential_fact_id=None,claim_kind='observation',claim_id='c',report_location='/summary/0',judgment='supported')
            rows.append(base)
            rows.append({**base,'essential_fact_id':'f','claim_kind':'essential_fact','claim_id':None,
                         'report_location':'essential_facts','judgment':'present'})
    result=module.finalize(outcomes,rows,[],['0','1','2','3'])
    assert result['review_complete'] is True
    assert sum(r['passed'] for r in result['ratings'])==7
    assert result['quality_acceptance'] is False
