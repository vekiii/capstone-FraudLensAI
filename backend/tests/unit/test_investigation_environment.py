"""Local configuration privacy/precedence; authored keys only, no network."""
import os

import pytest

from fraudlens.investigation import environment
from fraudlens.investigation.settings import load_settings


def test_local_file_reaches_backend_without_enabling_provider(monkeypatch, tmp_path):
    for name in ('OPENAI_API_KEY', 'OPENAI_MODEL', 'INVESTIGATION_ENABLED', 'INVESTIGATION_PROVIDER'):
        monkeypatch.delenv(name, raising=False)
    environment.ENV_FILE.write_text(
        '# Local only\nexport OPENAI_API_KEY="AUTHORED-SECRET" # private\n'
        "OPENAI_MODEL='authored-model'\n", encoding='utf-8')
    monkeypatch.chdir(tmp_path.parent)
    cfg = load_settings()
    assert cfg.api_key.get_secret_value() == 'AUTHORED-SECRET'
    assert cfg.model.get_secret_value() == 'authored-model'
    assert not cfg.enabled and cfg.provider == 'test'
    assert 'OPENAI_API_KEY' not in os.environ
    assert 'AUTHORED-SECRET' not in repr(cfg) + cfg.model_dump_json()


def test_process_values_win_including_explicit_empty(monkeypatch):
    environment.ENV_FILE.write_text(
        'OPENAI_API_KEY=AUTHORED-SECRET\nOPENAI_MODEL=file-model\n', encoding='utf-8')
    monkeypatch.setenv('OPENAI_API_KEY', '')
    monkeypatch.setenv('OPENAI_MODEL', 'process-model')
    cfg = load_settings()
    assert cfg.api_key.get_secret_value() == ''
    assert cfg.model.get_secret_value() == 'process-model'


def test_missing_local_file_uses_only_process(monkeypatch):
    monkeypatch.setenv('OPENAI_MODEL', 'process-model')
    assert environment.read_environment()['OPENAI_MODEL'] == 'process-model'


def test_values_are_literal_and_preserve_hashes_and_windows_paths(monkeypatch):
    environment.ENV_FILE.write_text(
        'AUTHORED_PATH=C:\\local\\store.sqlite\n'
        'AUTHORED_HASH=abc#def # comment\n'
        'AUTHORED_LITERAL="$(never-execute) ${NEVER_EXPAND} # literal"\n', encoding='utf-8')
    monkeypatch.setenv('NEVER_EXPAND', 'must-not-appear')
    values = environment.read_environment()
    assert values['AUTHORED_PATH'] == r'C:\local\store.sqlite'
    assert values['AUTHORED_HASH'] == 'abc#def'
    assert values['AUTHORED_LITERAL'] == '$(never-execute) ${NEVER_EXPAND} # literal'


@pytest.mark.parametrize('line', [
    'OPENAI_API_KEY="AUTHORED-SECRET',
    'OPENAI_API_KEY="AUTHORED-SECRET" unexpected',
    'AUTHORED-SECRET',
])
def test_malformed_file_fails_without_secret_or_line_disclosure(line, capsys, caplog):
    environment.ENV_FILE.write_text(line, encoding='utf-8')
    with pytest.raises(ValueError) as exc:
        environment.read_environment()
    assert 'AUTHORED-SECRET' not in str(exc.value) + caplog.text + capsys.readouterr().out
