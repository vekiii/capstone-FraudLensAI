"""Private, side-effect-free investigation configuration, separate from APP_MODE."""
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator

from fraudlens.investigation.environment import read_environment

ROOT = Path(__file__).resolve().parents[4]


class InvestigationSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid', hide_input_in_errors=True)
    enabled: bool = False
    semantic_retrieval: bool = False
    semantic_profile: Literal['v6', 'v7'] = 'v6'
    max_semantic_requests: int = Field(default=10, ge=1, le=30)
    provider: Literal['test', 'openai'] = 'test'
    test_scenario: Literal['grounded', 'needs_information', 'invalid_citation', 'refusal', 'incomplete'] = 'grounded'
    source: Literal['fixture', 'dataset'] = 'fixture'
    store: Path = ROOT / 'data/processed/investigations.sqlite'
    dataset_run_store: Path = ROOT / 'data/processed/scored-runs.sqlite'
    dataset_store: Path = ROOT / 'data/processed/dataset.sqlite'
    dataset_score_source: Literal['rules', 'model'] = 'rules'
    dataset_history_index: Path | None = None
    dataset_history_index_sha256: str | None = Field(default=None, pattern='^[0-9a-f]{64}$')
    analyst: str = Field(default='local-demo-analyst', min_length=1, max_length=80)
    api_key: SecretStr = Field(default_factory=lambda: SecretStr(''), repr=False, exclude=True)
    model: SecretStr = Field(default_factory=lambda: SecretStr(''), repr=False, exclude=True)
    max_provider_requests: int = Field(default=8, ge=1, le=8)
    max_tool_calls: int = Field(default=12, ge=1, le=12)
    total_timeout_seconds: int = Field(default=120, ge=1, le=120)
    request_timeout_seconds: int = Field(default=30, ge=1, le=45)
    max_input_bytes: int = Field(default=48000, ge=1, le=48000)
    max_output_tokens: int = Field(default=4096, ge=1, le=4096)
    max_response_bytes: int = Field(default=2097152, ge=1, le=2097152)

    @field_validator('store', 'dataset_run_store', 'dataset_store', 'dataset_history_index', mode='before')
    @classmethod
    def resolve_store(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            raise ValueError('Store path must not be empty')
        path = Path(value)
        return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()

    @field_validator('analyst')
    @classmethod
    def nonblank_analyst(cls, value):
        if not value.strip():
            raise ValueError('Analyst must not be blank')
        return value

    @model_validator(mode='after')
    def explicit_model(self):
        if self.request_timeout_seconds > 30 and (
                not self.semantic_retrieval or self.semantic_profile != 'v7' or self.provider != 'openai'):
            raise ValueError('Request limits above30 require the explicit OpenAI semantic v7 profile')
        if ((self.dataset_history_index is None) != (self.dataset_history_index_sha256 is None)
                or self.dataset_history_index is not None and self.source != 'dataset'):
            raise ValueError('History index requires dataset mode and an explicit digest')
        if self.provider == 'openai' and not self.model.get_secret_value().strip():
            raise ValueError('OpenAI provider requires an explicit model identifier')
        if self.semantic_retrieval and self.provider != 'openai':
            raise ValueError('Semantic retrieval requires explicit OpenAI configuration')
        return self


def load_settings() -> InvestigationSettings:
    """Read root .env plus process overrides; no database, SDK or network access.

    Values for key/model are private and excluded from repr and serialization.
    Errors intentionally omit supplied input, even for malformed unrelated fields.
    Presence of a model identifier is not evidence of provider access/capabilities.
    """
    environment = read_environment()
    values = {}
    for name in InvestigationSettings.model_fields:
        variable = {'api_key': 'OPENAI_API_KEY', 'model': 'OPENAI_MODEL'}.get(
            name, 'INVESTIGATION_' + name.upper())
        if variable in environment:
            raw = environment[variable]
            if name.startswith('max_') or name.endswith('_seconds'):
                # Integer-only environment spelling; no bool/float coercion.
                if not raw.isascii() or not raw.isdecimal():
                    raise ValueError('Invalid investigation limit configuration')
                raw = int(raw)
            elif name in ('enabled', 'semantic_retrieval'):
                if raw.lower() not in ('true', 'false'):
                    raise ValueError('INVESTIGATION_ENABLED must be true or false')
                raw = raw.lower() == 'true'
            values[name] = raw
    try:
        return InvestigationSettings.model_validate(values)
    except (ValueError, TypeError):
        raise ValueError('Invalid investigation configuration; check documented settings') from None
