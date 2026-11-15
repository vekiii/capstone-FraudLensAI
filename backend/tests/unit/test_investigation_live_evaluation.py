"""Materialized dataset projection; authored public contract examples only."""
import asyncio
import json
from uuid import uuid4

import pytest

from fraudlens.investigation.context import outbound_context
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.provider import project_conversation


def test_dataset_projection_preserves_exact_directional_values_and_excludes_bank():
    ctx=json.loads((ROOT/'specs/003-ai-investigation/contracts/examples/context-dataset.json').read_text(encoding='utf-8'))
    projected=outbound_context(ctx,'inv_'+'a'*32)
    assert projected['source_mode']=='dataset'
    assert projected['transaction']['paid']==ctx['source_payload']['transaction']['paid']
    assert projected['transaction']['received']==ctx['source_payload']['transaction']['received']
    assert projected['transaction']['event_time_raw']==ctx['source_payload']['transaction']['event_time_raw']
    assert 'SYNTH-BANK-A' not in json.dumps(projected)
    assert project_conversation([dict(type='context',data=projected)])
    projected['transaction']['private_label']='PRIVATE'
    with pytest.raises(ValueError):
        project_conversation([dict(type='context',data=projected)])


def test_authored_dataset_materialized_workflow_without_network(tmp_path,knowledge_factory):
    from fraudlens.investigation.context import HistoryReader
    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.settings import InvestigationSettings
    from fraudlens.investigation.workflow import InvestigationService
    ctx=json.loads((ROOT/'specs/003-ai-investigation/contracts/examples/context-dataset.json').read_text(encoding='utf-8'))
    knowledge=KnowledgeStore(tmp_path/'test.sqlite')
    knowledge.publish(knowledge_factory())
    knowledge.save_configuration(dict(algorithm='bm25',k1=1.2,b=.75,maximum_results=5,adequacy_cutoff=0))
    class Reader:
        def resolve(self,*args):
            return ctx
    service=InvestigationService(knowledge.repository,knowledge,InvestigationSettings(),history_reader=HistoryReader(events=[],accounts={}))
    service.context_reader=Reader()
    run=service.create({k:ctx[k] for k in ('case_id','source_mode','snapshot_ref')},'TEST',str(uuid4()))
    result=asyncio.run(service.work_once())
    assert result['state']=='needs_information'
    assert result['attempt_id']==run['attempt_id']
    assert service.evidence(run['attempt_id'])[0]['facts']
