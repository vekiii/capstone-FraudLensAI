"""Closed, aggregate-only contract for the Dataset & Model Overview page."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _OverviewModel(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class OverviewDataset(_OverviewModel):
    data_source: Literal['ibm_aml_hi_small']
    dataset_version: str
    run_id: str
    scored_transactions: int = Field(ge=0)
    unknown_timestamp_transactions: int = Field(ge=0)
    confirmed_fraud: None
    legitimate: None
    fraud_rate: None
    label_unavailable_reason: str


class OverviewPredictions(_OverviewModel):
    flagged: int = Field(ge=0)
    not_flagged: int = Field(ge=0)
    flag_rate: float | None = Field(ge=0, le=1)


class OverviewPoint(_OverviewModel):
    period: str
    transactions: int = Field(ge=0)
    flagged: int = Field(ge=0)
    not_flagged: int = Field(ge=0)


class OverviewModel(_OverviewModel):
    name: str
    source: Literal['rules', 'model']
    scorer_version: str
    threshold: str
    evaluation_dataset: None
    evaluation_split: None
    precision: None
    recall: None
    f1: None
    metric_source: str


class OverviewResponse(_OverviewModel):
    contract_version: Literal[1] = 1
    dataset: OverviewDataset
    predictions: OverviewPredictions
    series: list[OverviewPoint]
    aggregation: Literal['day', 'week']
    model: OverviewModel
