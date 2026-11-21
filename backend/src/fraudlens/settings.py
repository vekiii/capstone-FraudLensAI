"""Local fixture default with explicit model-mode opt-in."""
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    mode: Literal['fixture', 'model'] = 'fixture'
    fixture_path: Path = Field(
        default_factory=lambda: _ROOT / 'data/fixtures/cases.json'
    )
    model_artifact_root: Path = _ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts'
    model_feature_root: Path = _ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'


def load_settings() -> Settings:
    """APP_MODE=model is the sole opt-in; fixture remains the default."""
    return Settings(mode=os.environ.get('APP_MODE', 'fixture'))
