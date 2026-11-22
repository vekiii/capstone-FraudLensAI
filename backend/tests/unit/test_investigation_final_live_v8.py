"""Final evaluation harness: notice omission, immutable continuation and separate roles."""
import copy
import importlib.util
from pathlib import Path

import pytest

from fraudlens.investigation.provider import Turn, scripted_draft
from fraudlens.investigation.report_policy import HUMAN_AUTHORITY_NOTICE, HUMAN_AUTHORITY_POLICY
from fraudlens.investigation.settings import InvestigationSettings

PATH = Path(__file__).resolve().parents[3] / 'evidence/tasks/feature-003-final-live-v8.py'
SPEC = importlib.util.spec_from_file_location('final_live_v8_test', PATH)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def conversation():
    return [dict(type='context', data=dict(case_id='CASE-783')),
        dict(type='tool_result', result=dict(evidence=[dict(evidence_id='ev_' + 'a' * 32,
            kind='case_fact', facts=[dict(path='transaction.amount', value='418.63'),
                                   dict(path='transaction.currency', value='GBP')])]))]


def test_fault_removes_only_notice_from_an_authored_candidate_without_changing_raw_turn():
    messages = conversation()
    draft = scripted_draft(messages, 'grounded')
    turn = Turn('draft', draft=draft, private_items=({'type': 'reasoning', 'encrypted_content': 'OPAQUE'},))
    original = copy.deepcopy((messages, turn))
    candidate = runner.invalid_candidate(messages, turn)
    assert HUMAN_AUTHORITY_NOTICE not in candidate['limitations']
    expected = copy.deepcopy(draft)
    expected['limitations'].remove(HUMAN_AUTHORITY_NOTICE)
    assert candidate == expected and candidate is not draft
    assert (messages, turn) == original


def test_ordinary_failures_remain_in_denominator_and_controlled_case_is_separate():
    packets = [dict(role='primary', scenario_id=identity, failed=True, units=[]) for identity in runner.IDS]
    result = runner.diagnostic_roles(packets)
    assert [p['scenario_id'] for p in result if p['role'] == 'primary'] == list(runner.IDS[:2])
    assert runner.core.aggregate(result, {})['failed_reports'] == 2


@pytest.mark.parametrize('case', ['CASE-781', 'CASE-782', 'CASE-763'])
def test_notice_fault_cannot_be_injected_into_an_ordinary_or_old_case(case):
    messages = conversation()
    messages[0]['data']['case_id'] = case
    with pytest.raises(ValueError, match='diagnostic scope'):
        runner.invalid_candidate(messages, Turn('draft', draft=scripted_draft(messages, 'grounded')))


@pytest.mark.parametrize('artifact_state', ['valid', 'changed', 'missing'])
def test_prepare_pins_actual_prompt_and_policy_without_opening_expectations(tmp_path, monkeypatch, artifact_state):
    original = runner.core.load
    artifact = tmp_path / 'authored-prior-audit.json'
    artifact.write_text('{"kind":"authored test artifact, not actual live evidence"}')
    expected_artifact_hash = runner.core.sha(artifact)
    if artifact_state == 'changed':
        artifact.write_text('{"kind":"changed authored test artifact"}')
    elif artifact_state == 'missing':
        artifact.unlink()

    def guarded(path):
        if path.name in ('reference.json', 'calibrations.json'):
            pytest.fail('Expected labels opened before generation')
        data = original(path)
        if path == runner.PACK / 'protocol.json':
            # Unit preparation must not depend on ignored historical live archives.
            # Keep actual code hashes/checks; use an independently hashed local fixture.
            data['preserved_artifacts'] = {str(artifact): expected_artifact_hash}
        return data

    monkeypatch.setattr(runner.core, 'load', guarded)
    monkeypatch.setattr(runner.core, 'load_settings', lambda: InvestigationSettings(
        provider='openai', model='gpt-6-luna', api_key='AUTHORED-NOT-REAL'))
    if artifact_state != 'valid':
        error = ValueError if artifact_state == 'changed' else FileNotFoundError
        with pytest.raises(error):
            runner.prepare(tmp_path / 'run')
        return
    _, _, _, _, _, freeze = runner.prepare(tmp_path / 'run')
    assert freeze['report_policy'] == HUMAN_AUTHORITY_POLICY
    assert freeze['prompt_sha256'] == runner.core.sha(runner.ROOT / 'prompts/application/investigation-v4.md')
    assert freeze['cap'] == 25 and freeze['settings']['max_input_bytes'] == 48000


def test_controlled_fault_is_one_shot_and_does_not_change_continuation(monkeypatch):
    saved = []
    monkeypatch.setattr(runner.core, 'frozen', lambda path, data: saved.append(data))
    provider = runner.FaultProvider.__new__(runner.FaultProvider)
    provider.history = [{'type': 'reasoning', 'encrypted_content': 'OPAQUE'}]
    messages = conversation()
    turn = Turn('draft', draft=scripted_draft(messages, 'grounded'), private_items=tuple(provider.history))
    before = copy.deepcopy((turn, provider.history))
    first = provider.application_candidate(messages, turn)
    assert HUMAN_AUTHORITY_NOTICE not in first.draft['limitations']
    assert first.private_items == turn.private_items
    assert saved[0]['expected_rejection'] == 'human_authority_notice_required'
    assert (turn, provider.history) == before
    assert provider.application_candidate(messages, turn) is turn and len(saved) == 1


def test_judge_packets_keep_controlled_case_separate_and_labels_out():
    records = [dict(id=identity, result=dict(report=None, failure=None), evidence=[]) for identity in runner.IDS]
    packets = runner.packets_after_generation(records, {identity: {} for identity in runner.IDS})
    assert len(packets) == 6 and sum(p['role'] == 'calibration' for p in packets) == 3
    assert sum(p['role'] == 'primary' for p in packets) == 2
    assert 'CAL8_EXPECTED_ONLY_CANARY' not in str(packets) and 'expectations' not in str(packets)
