"""Private, side-effect-free investigation configuration, separate from APP_MODE."""
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator

ROOT = Path(__file__).resolve().parents[4]


class InvestigationSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid', hide_input_in_errors=True)
    enabled: bool = False
    provider: Literal['test', 'openai'] = 'test'
    source: Literal['fixture', 'dataset'] = 'fixture'
    store: Path = ROOT / 'data/processed/investigations.sqlite'
    analyst: str = Field(default='local-demo-analyst', min_length=1)
    api_key: SecretStr = Field(default_factory=lambda: SecretStr(''), repr=False, exclude=True)
    model: SecretStr = Field(default_factory=lambda: SecretStr(''), repr=False, exclude=True)
    max_provider_requests: int = Field(default=8, ge=1, le=8)
    max_tool_calls: int = Field(default=12, ge=1, le=12)
    total_timeout_seconds: int = Field(default=120, ge=1, le=120)
    request_timeout_seconds: int = Field(default=30, ge=1, le=30)
    max_input_bytes: int = Field(default=48000, ge=1, le=48000)
    max_output_tokens: int = Field(default=4096, ge=1, le=4096)
    max_response_bytes: int = Field(default=2097152, ge=1, le=2097152)

    @field_validator('store', mode='before')
    @classmethod
    def resolve_store(cls, value):
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
        if self.provider == 'openai' and not self.model.get_secret_value().strip():
            raise ValueError('OpenAI provider requires an explicit model identifier')
        return self


def load_settings() -> InvestigationSettings:
    """Read explicit environment only; no .env, database, SDK or network access.

    Values for key/model are private and excluded from repr and serialization.
    Errors intentionally omit supplied input, even for malformed unrelated fields.
    Presence of a model identifier is not evidence of provider access/capabilities.
    """
    values = {}
    for name in InvestigationSettings.model_fields:
        variable = {'api_key': 'OPENAI_API_KEY', 'model': 'OPENAI_MODEL'}.get(
            name, 'INVESTIGATION_' + name.upper())
        if variable in os.environ:
            raw = os.environ[variable]
            if name.startswith('max_') or name.endswith('_seconds'):
                # Integer-only environment spelling; no bool/float coercion.
                if not raw.isascii() or not raw.isdecimal():
                    raise ValueError('Invalid investigation limit configuration')
                raw = int(raw)
            elif name == 'enabled':
                if raw.lower() not in ('true', 'false'):
                    raise ValueError('INVESTIGATION_ENABLED must be true or false')
                raw = raw.lower() == 'true'
            values[name] = raw
    try:
        return InvestigationSettings.model_validate(values)
    except (ValueError, TypeError):
        raise ValueError('Invalid investigation configuration; check documented settings') from None
