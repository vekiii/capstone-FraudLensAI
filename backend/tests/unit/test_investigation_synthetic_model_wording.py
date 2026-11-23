"""Guard the distinction between synthetic input and a real model inference."""

from pathlib import Path

from test_investigation_context import context

from fraudlens.investigation.context import outbound_context

ROOT = Path(__file__).resolve().parents[3]


def test_active_prompt_distinguishes_model_inference_from_synthetic_input():
    prompt = (ROOT / 'prompts/application/investigation-v6.md').read_text()
    assert 'sintetički fixture nije stvaran klijent niti ML predikcija' not in prompt
    assert 'score_source=model' in prompt
    assert 'stvarna modelska predikcija nad sintetičkim ulaznim podacima' in prompt
    assert 'LLM izveštaj opisuje dobijenu predikciju' in prompt


def test_fixture_projection_still_identifies_absence_of_model_inference():
    projected = outbound_context(context(), 'inv_' + 'a' * 32)
    assert projected['source_mode'] == 'fixture'
    assert projected['assessment']['source'] == 'fixture'
    assert 'no ML inference' in projected['notice']
