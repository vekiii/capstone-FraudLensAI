"""Offline bridge and test-provider flow with a separate pinned sidecar."""
import asyncio
import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from fraudlens.bridge_reader import BridgeReader
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.review import AnalystReviewService
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.tools import COMPACT_TEXT, content_digest, provider_evidence
from fraudlens.investigation.workflow import InvestigationService
from fraudlens.main import create_app
from fraudlens.scoring.model_scorer import FeatureStore, ModelScorer
from fraudlens.settings import Settings

ROOT = Path(__file__).resolve().parents[3]
BRIDGE_ROOT = ROOT / 'data/processed/model-case-bridge-v1'
BRIDGE_SHA = '16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004'
SIDE_ROOT = ROOT / 'data/processed/local-contributions-v1/sidecars.json'
SIDE_SHA = '8edb466a84a186f6115b725d10796c409d1aa5fa065ddfddf0e2e3e1beb12429'
IDS = [
    'ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:1500153',
    'ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:2959955',
]


@pytest.fixture(scope='module')
def model_inputs():
    return (ModelScorer(ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts'),
            FeatureStore(ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'))


@pytest.mark.parametrize('canonical', IDS)
@pytest.mark.parametrize('enabled', [False, True])
def test_new_attempt_and_saved_report(canonical, enabled, tmp_path, knowledge_factory, monkeypatch,
                                      model_inputs):
    if not SIDE_ROOT.exists():
        pytest.skip('ignored verified sidecar absent')
    bridge = BridgeReader(BRIDGE_ROOT, BRIDGE_SHA)
    binding = bridge.binding(canonical)
    context = bridge.resolve(binding['case_id'], binding['snapshot_ref'])
    store = KnowledgeStore(tmp_path / 'isolated-investigation.sqlite')
    store.publish(knowledge_factory())
    store.save_configuration(json.loads((ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
    kwargs = dict(enabled=True, source='dataset', dataset_score_source='model', provider='test',
        model_case_bridge_root=BRIDGE_ROOT, model_case_bridge_manifest_sha256=BRIDGE_SHA,
        store=store.repository.path)
    if enabled:
        kwargs.update(local_contribution_path=SIDE_ROOT, local_contribution_sha256=SIDE_SHA)
        monkeypatch.setenv('INVESTIGATION_LOCAL_CONTRIBUTION_PATH', str(SIDE_ROOT))
        monkeypatch.setenv('INVESTIGATION_LOCAL_CONTRIBUTION_SHA256', SIDE_SHA)
    monkeypatch.setenv('MODEL_CASE_BRIDGE_ROOT', str(BRIDGE_ROOT))
    monkeypatch.setenv('MODEL_CASE_BRIDGE_MANIFEST_SHA256', BRIDGE_SHA)
    service = InvestigationService(store.repository, store, InvestigationSettings(**kwargs))
    created = service.create({k: context[k] for k in ('case_id', 'source_mode', 'snapshot_ref')},
                             'test-analyst', str(uuid4()))
    attempt = created['attempt_id']
    assert service.binding(attempt).get('local_contribution_status') == ('available' if enabled else None)
    app = create_app(settings=Settings(mode='model'), model_scorer=model_inputs[0], feature_store=model_inputs[1])
    with TestClient(app) as client:
        risk = client.get(f'/api/transactions/{canonical}/risk')
        assert risk.status_code == 200
        assert risk.json()['risk_score'] == binding['risk_score']
        assert risk.json()['review_status'] == binding['review_status']
        response = client.get(f'/api/model/cases/{binding["case_id"]}/local-contributions')
        assert response.status_code == 200
        assert response.json()['status'] == ('available' if enabled else 'unavailable')
        assert client.get(f'/api/model/cases/{binding["case_id"]}').json() == context['source_payload']
    done = asyncio.run(service.work_once())
    assert done['state'] == 'ready_for_review'
    limitations = ' '.join(done['report']['draft']['limitations'])
    assert ('lokalni doprinosi su na log-odds' in limitations) == enabled
    assert ('doprinosi modelskih obelezja nisu dostupni' in limitations) == (not enabled)
    evidence = service.evidence(attempt)
    contributions = [item for item in evidence if any(fact['path'].startswith('local_contribution_v1.')
                     for fact in item['facts'])]
    assert len(contributions) == int(enabled)
    if enabled:
        assert contributions[0]['attempt_id'] == attempt
        assert contributions[0]['context_revision'] == context['context_revision']
        assert contributions[0]['content_sha256'] == content_digest(contributions[0])
        assert contributions[0]['text'].startswith(COMPACT_TEXT + '\n')
        assert provider_evidence(contributions[0])['text'] == COMPACT_TEXT
        assert provider_evidence(contributions[0])['facts'] == contributions[0]['facts']
        assert json.loads(contributions[0]['text'].split('\n', 1)[1])['method'] == (
            'lightgbm_pred_contrib_log_odds_v1')
    review = AnalystReviewService(service).submit(attempt, done['revision'],
        dict(disposition='request_more_information', rationale='Test-only analyst decision.', correction_note=None,
             supersedes_review_id=None,
             report_id=done['report']['report_id']), 'test-analyst', str(uuid4()))
    reopened = InvestigationService(store.repository, store, InvestigationSettings(**kwargs))
    assert reopened.read(attempt) == review
    assert reopened.evidence(attempt) == evidence
    if enabled:
        # Replacing the local pin after completion never rewrites an archived attempt.
        changed = {**kwargs, 'local_contribution_sha256': '0' * 64}
        corrupt_reader = InvestigationService(store.repository, store, InvestigationSettings(**changed))
        assert corrupt_reader.read(attempt) == review
        assert corrupt_reader.evidence(attempt) == evidence


def test_wrong_pin_is_invalid_but_keeps_score_and_investigation(tmp_path, knowledge_factory, monkeypatch):
    bridge = BridgeReader(BRIDGE_ROOT, BRIDGE_SHA)
    binding = bridge.binding(IDS[0])
    context = bridge.resolve(binding['case_id'], binding['snapshot_ref'])
    monkeypatch.setenv('MODEL_CASE_BRIDGE_ROOT', str(BRIDGE_ROOT))
    monkeypatch.setenv('MODEL_CASE_BRIDGE_MANIFEST_SHA256', BRIDGE_SHA)
    monkeypatch.setenv('INVESTIGATION_LOCAL_CONTRIBUTION_PATH', str(SIDE_ROOT))
    monkeypatch.setenv('INVESTIGATION_LOCAL_CONTRIBUTION_SHA256', '0' * 64)
    app = create_app(settings=Settings(mode='model'), model_scorer=object(), feature_store=object())
    with TestClient(app) as client:
        assert client.get(f'/api/model/cases/{binding["case_id"]}/local-contributions').json()['status'] == 'invalid'
        detail = client.get(f'/api/model/cases/{binding["case_id"]}').json()
        assert detail['risk_assessment']['score'] == binding['risk_score']
    store = KnowledgeStore(tmp_path / 'invalid-pin-investigation.sqlite')
    store.publish(knowledge_factory())
    store.save_configuration(json.loads((ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
    settings = InvestigationSettings(enabled=True, source='dataset', dataset_score_source='model',
        model_case_bridge_root=BRIDGE_ROOT, model_case_bridge_manifest_sha256=BRIDGE_SHA,
        local_contribution_path=SIDE_ROOT, local_contribution_sha256='0' * 64,
        store=store.repository.path)
    service = InvestigationService(store.repository, store, settings)
    created = service.create({k: context[k] for k in ('case_id', 'source_mode', 'snapshot_ref')},
                             'test-analyst', str(uuid4()))
    assert service.binding(created['attempt_id'])['local_contribution_status'] == 'invalid'
    assert asyncio.run(service.work_once())['state'] == 'ready_for_review'
    assert not any(fact['path'].startswith('local_contribution_v1.')
        for item in service.evidence(created['attempt_id']) for fact in item['facts'])


def test_retry_reuses_only_same_verified_sidecar(tmp_path, knowledge_factory):
    bridge = BridgeReader(BRIDGE_ROOT, BRIDGE_SHA)
    binding = bridge.binding(IDS[0])
    context = bridge.resolve(binding['case_id'], binding['snapshot_ref'])
    store = KnowledgeStore(tmp_path / 'retry-investigation.sqlite')
    store.publish(knowledge_factory())
    store.save_configuration(json.loads((ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
    settings = InvestigationSettings(enabled=True, source='dataset', dataset_score_source='model',
        test_scenario='needs_information', model_case_bridge_root=BRIDGE_ROOT,
        model_case_bridge_manifest_sha256=BRIDGE_SHA, local_contribution_path=SIDE_ROOT,
        local_contribution_sha256=SIDE_SHA, store=store.repository.path)
    service = InvestigationService(store.repository, store, settings)
    created = service.create({k: context[k] for k in ('case_id', 'source_mode', 'snapshot_ref')},
                             'test-analyst', str(uuid4()))
    parent = asyncio.run(service.work_once())
    assert parent['attempt_id'] == created['attempt_id']
    assert parent['state'] == 'needs_information'
    original = service.evidence(parent['attempt_id'])
    child = service.retry(parent['attempt_id'], parent['revision'], True, 'test-analyst', str(uuid4()))
    assert child['parent_attempt_id'] == parent['attempt_id']
    assert service.evidence(parent['attempt_id']) == original
    assert len(service.evidence(child['attempt_id'])) == len(original)
    changed = InvestigationService(store.repository, store, settings.model_copy(
        update={'local_contribution_sha256': '0' * 64}))
    with pytest.raises(ValueError, match='stale_snapshot'):
        changed.retry(parent['attempt_id'], service.read(parent['attempt_id'])['revision'],
                      True, 'test-analyst', str(uuid4()))
    assert changed.evidence(parent['attempt_id']) == original
