"""RED: isolated contribution sidecar must fail closed without affecting v2."""
import json
from copy import deepcopy
from pathlib import Path

import pytest

from fraudlens.bridge_reader import BridgeReader
from fraudlens.investigation.contribution_sidecar import SidecarInvalid, SidecarReader
from fraudlens.investigation.models import canonical

ROOT = Path(__file__).resolve().parents[3]
BRIDGE = BridgeReader(ROOT / 'data/processed/model-case-bridge-v1',
    '16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004')
CASE = 'ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:1500153'


@pytest.fixture
def linked(tmp_path):
    if not BRIDGE.root.exists():
        pytest.skip('ignored bridge absent')
    binding = BRIDGE.binding(CASE)
    context = BRIDGE.resolve(binding['case_id'], binding['snapshot_ref'])
    source = json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/'
        'local-contribution-sidecar-v1.proposal.json').read_text())['contribution_sidecar_v1']
    payload = {'contract_version': 1, 'items': {binding['case_id']: source}}
    raw = canonical(payload)
    path = tmp_path / 'sidecars.json'
    path.write_bytes(raw)
    import hashlib
    return path, hashlib.sha256(raw).hexdigest(), binding, context, source


def test_pin_and_binding(linked):
    path, pin, binding, context, source = linked
    assert SidecarReader(path, pin).read(binding, context) == source
    with pytest.raises(SidecarInvalid):
        SidecarReader(path, '0' * 64).read(binding, context)


@pytest.mark.parametrize('field,value', [
    ('canonical_transaction_id', 'wrong'), ('transaction_id', 'wrong'),
    ('case_id', 'wrong'), ('assessment_run_id', 'wrong'),
    ('context_revision', '0' * 64), ('model_sha256', '0' * 64),
    ('feature_version', 'wrong'), ('raw_score', 0), ('score', float('nan')),
    ('explained_scale', 'risk_score'), ('remainder', float('inf')),
])
def test_corrupt_sidecar_rejected(linked, field, value):
    path, _, binding, context, source = linked
    changed = deepcopy(source)
    changed[field] = value
    payload = {'contract_version': 1, 'items': {binding['case_id']: changed}}
    raw = canonical(payload) if field not in ('score', 'remainder') else json.dumps(payload).encode()
    path.write_bytes(raw)
    import hashlib
    with pytest.raises(SidecarInvalid):
        SidecarReader(path, hashlib.sha256(raw).hexdigest()).read(binding, context)
