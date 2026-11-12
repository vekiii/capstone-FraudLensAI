"""Local fixture configuration; no credentials or data loading at startup."""
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    mode: Literal['fixture'] = 'fixture'
    fixture_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[3] / 'data/fixtures/cases.json'
    )


def load_settings() -> Settings:
    """Read APP_MODE on each factory invocation; reject unsupported values."""
    return Settings(mode=os.environ.get('APP_MODE', 'fixture'))
