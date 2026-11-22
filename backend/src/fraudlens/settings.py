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
    eda_summary_path: Path | None = None
    eda_summary_sha256: str | None = None


def load_settings() -> Settings:
    """APP_MODE=model is the sole opt-in; fixture remains the default."""
    eda_path = os.environ.get('EDA_SUMMARY_PATH')
    eda_sha = os.environ.get('EDA_SUMMARY_SHA256')
    return Settings(
        mode=os.environ.get('APP_MODE', 'fixture'),
        eda_summary_path=Path(eda_path) if eda_path else None,
        eda_summary_sha256=eda_sha,
    )
