"""Explicit fixture/dataset selection; no data loading at startup."""
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    mode: Literal['fixture', 'dataset'] = 'fixture'
    scorer: Literal['rules', 'model'] | None = None
    run_store_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[3]
        / 'data/artifacts/feature-002-runs.sqlite')
    fixture_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[3] / 'data/fixtures/cases.json'
    )

    @model_validator(mode='after')
    def require_dataset_scorer(self):
        if self.mode == 'dataset' and self.scorer is None:
            raise ValueError('APP_SCORER=rules|model is required for dataset mode')
        return self


def load_settings() -> Settings:
    """Read APP_MODE on each factory invocation; reject unsupported values."""
    mode = os.environ.get('APP_MODE', 'fixture')
    return Settings(mode=mode, scorer=os.environ.get('APP_SCORER') if mode == 'dataset' else None,
                    run_store_path=Path(os.environ.get('APP_RUN_STORE',
                        str(Path(__file__).resolve().parents[3]
                            / 'data/artifacts/feature-002-runs.sqlite'))))
