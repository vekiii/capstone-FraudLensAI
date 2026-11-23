"""Targeted tests of an isolated proposal; production contracts stay unchanged."""

import json
from copy import deepcopy
from pathlib import Path

import pytest
from local_contribution_sidecar import build_sidecar, validate_sidecar

from fraudlens.bridge_reader import BridgeReader
from fraudlens.investigation.context import outbound_context, validate_outbound_dataset
from fraudlens.investigation.models import digest, validate
from fraudlens.investigation.provider import ProviderError, project_conversation
from fraudlens.scoring.local_contributions import compute_local_contributions
from fraudlens.scoring.model_scorer import FeatureStore, ModelScorer

ROOT = Path(__file__).resolve().parents[3]
BRIDGE_SHA = '16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004'
CANONICAL = ('ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:'
             'row:1500153')


@pytest.fixture(scope='module')
def proposal():
    root = ROOT / 'data/processed/model-case-bridge-v1'
    if not root.exists():
        pytest.skip('ignored bridge absent')
    bridge = BridgeReader(root, BRIDGE_SHA)
    binding = bridge.binding(CANONICAL)
    context = bridge.resolve(binding['case_id'], binding['snapshot_ref'])
    row = FeatureStore(ROOT / 'data/processed/t219-ibm-day-60-20-20-v1').get(CANONICAL)
    scorer = ModelScorer(ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts')
    calculation = compute_local_contributions(scorer, row)
    sidecar = build_sidecar(binding, context, calculation, scorer.manifest, row.features)
    return binding, context, row, calculation, scorer.manifest, sidecar


def test_sidecar_binds_to_unchanged_v2_context(proposal):
    binding, context, row, calculation, manifest, sidecar = proposal
    assert validate('InvestigationContext', context)['contract_version'] == 2
    assert context['source_payload']['risk_assessment']['explanation']['status'] == 'unavailable'
    assert sidecar['transaction_id'] == binding['transaction_id'] != row.transaction_id
    assert sidecar['feature_snapshot_digest'].startswith('sha256:')
    assert validate_sidecar(sidecar, binding, context, calculation, manifest, row.features) == sidecar
    projected = outbound_context(context, 'inv_' + 'a' * 32)
    assert 'contribution_summary' not in projected
    project_conversation([dict(type='context', data=projected)])


def test_isolated_json_example_matches_verified_browser_case(proposal):
    _, context, _, _, _, sidecar = proposal
    example = json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/'
                          'local-contribution-sidecar-v1.proposal.json').read_text())
    assert example['proposal_status'] == 'unapproved_isolated_example'
    assert example['existing_provider_context_v2'] == outbound_context(context, 'inv_' + 'a' * 32)
    reference = example['contribution_sidecar_v1']
    recomputed = deepcopy(sidecar)
    # Each digest must match its own exact content. Native float results can
    # differ in the last places across platforms, which changes the digest.
    for payload in (reference, recomputed):
        evidence_digest = payload.pop('evidence_digest')
        assert digest(payload) == evidence_digest

    roundoff = 1e-12
    for field in ('base_value', 'raw_score', 'remainder'):
        assert recomputed.pop(field) == pytest.approx(reference.pop(field), abs=roundoff, rel=0), field
    for actual, expected in zip(recomputed['items'], reference['items'], strict=True):
        assert actual.pop('contribution') == pytest.approx(
            expected.pop('contribution'), abs=roundoff, rel=0), expected['feature_key']

    # Check the score, identity, units, direction and item order exactly.
    assert recomputed == reference


@pytest.mark.parametrize('field,value', [
    ('transaction_id', 'D' + '0' * 32), ('assessment_run_id', 'run_bad'),
    ('context_revision', '0' * 64), ('model_sha256', '0' * 64),
    ('feature_snapshot_digest', 'sha256:' + '0' * 64),
    ('matrix_feature_order_sha256', '0' * 64),
    ('explained_scale', 'positive_class_estimate'),
    ('raw_score', 0.0), ('remainder', 0.0), ('score', float('nan')),
])
def test_sidecar_rejects_mismatch(proposal, field, value):
    binding, context, row, calculation, manifest, sidecar = proposal
    bad = deepcopy(sidecar)
    bad[field] = value
    with pytest.raises(ValueError):
        validate_sidecar(bad, binding, context, calculation, manifest, row.features)


def test_current_provider_rejects_unreviewed_context_extension(proposal):
    _, context, _, _, _, sidecar = proposal
    projected = outbound_context(context, 'inv_' + 'a' * 32)
    projected['contribution_summary'] = sidecar
    with pytest.raises(ProviderError, match='provider_input_invalid'):
        project_conversation([dict(type='context', data=projected)])


def test_current_v2_assessment_rejects_new_method(proposal):
    _, context, _, _, _, sidecar = proposal
    changed = deepcopy(context)
    changed['source_payload']['risk_assessment']['explanation'] = dict(
        status='available', method=sidecar['method'], explained_scale='log_odds',
        feature_snapshot_digest=sidecar['feature_snapshot_digest'], partial=True,
        base_value=sidecar['base_value'], remainder=sidecar['remainder'],
        items=[{**item, 'rule_condition': None} for item in sidecar['items']])
    with pytest.raises(ValueError, match='Invalid investigation contract'):
        validate('InvestigationContext', changed)
    projected = outbound_context(context, 'inv_' + 'a' * 32)
    projected['assessment']['explanation'] = changed['source_payload']['risk_assessment']['explanation']
    with pytest.raises(ValueError, match='Invalid dataset provider projection'):
        validate_outbound_dataset(projected)
