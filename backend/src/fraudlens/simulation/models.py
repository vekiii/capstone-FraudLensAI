"""Closed frozen-scenario facts and separately validated evaluation outcomes."""

import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

SAFE = 2**53 - 1
Id = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]{1,80}$")]
Positive = Annotated[int, Field(ge=1, le=SAFE)]
Nonnegative = Annotated[int, Field(ge=0, le=SAFE)]
Text = Annotated[str, StringConstraints(min_length=1)]


def utc(value):
    if not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z", value
    ):
        raise ValueError("Invalid UTC instant")
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def decimal_text(value):
    if len(value) > 128 or not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value):
        raise ValueError("Invalid decimal string")
    return value


def score(value):
    decimal_text(value)
    if not Decimal(0) <= Decimal(value) <= Decimal(1):
        raise ValueError("Score outside range")
    return value


def weight(value):
    decimal_text(value)
    if Decimal(value) <= 0:
        raise ValueError("Nonpositive weight")
    return value


Instant = Annotated[str, AfterValidator(utc)]
Score = Annotated[str, AfterValidator(score)]
Weight = Annotated[str, AfterValidator(weight)]


class Closed(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, frozen=True, revalidate_instances="always"
    )


class Source(Closed):
    kind: Literal["bundled_synthetic"]
    data_version: Text
    time_basis: Text


class Provenance(Closed):
    source: Literal["fixture"]
    score_kind: Literal["illustrative_score"]
    scorer_version: Text


class Assumption(Closed):
    id: Id
    description: Text


class Horizon(Closed):
    starts_at: Instant
    ends_at: Instant


class Defaults(Closed):
    score_threshold: Score
    budget_minutes_per_window: Nonnegative


class Alert(Closed):
    alert_id: Id
    available_at: Instant
    score: Score
    weight: Weight
    estimated_review_minutes: Positive
    weight_assumption_id: Id
    duration_assumption_id: Id


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def unique(values):
    if len(values) != len(set(values)):
        raise ValueError("Duplicate identifier")


class Scenario(Closed):
    scenario_id: Id
    scenario_version: Positive
    content_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    title: Text
    source: Source
    score_provenance: Provenance
    assumptions: list[Assumption]
    horizon: Horizon
    window_starts: Annotated[list[Instant], Field(min_length=1, max_length=12)]
    defaults: Defaults
    generation_seed: Nonnegative | None = None
    alerts: Annotated[list[Alert], Field(max_length=250)]

    @model_validator(mode="after")
    def boundaries(self):
        start, end = instant(self.horizon.starts_at), instant(self.horizon.ends_at)
        windows = [instant(v) for v in self.window_starts]
        if start >= end or windows[0] != start or any(not start <= t < end for t in windows):
            raise ValueError("Invalid horizon/windows")
        if any(a >= b for a, b in zip(windows, windows[1:])):
            raise ValueError("Unordered windows")
        ids = [a.id for a in self.assumptions]
        unique(ids)
        unique([a.alert_id for a in self.alerts])
        for a in self.alerts:
            if not start <= instant(a.available_at) < end:
                raise ValueError("Alert outside horizon")
            if a.weight_assumption_id not in ids or a.duration_assumption_id not in ids:
                raise ValueError("Unknown assumption")
        return self


class Outcome(Closed):
    alert_id: Id
    outcome: Literal["positive", "negative"]


class OutcomeSet(Closed):
    scenario_id: Id
    scenario_version: Positive
    outcomes: list[Outcome]


def validate_pair(scenario, outcomes):
    s = Scenario.model_validate(scenario)
    o = OutcomeSet.model_validate(outcomes)
    if (s.scenario_id, s.scenario_version) != (o.scenario_id, o.scenario_version):
        raise ValueError("Scenario identity mismatch")
    unique([v.alert_id for v in o.outcomes])
    if any(v.alert_id not in {a.alert_id for a in s.alerts} for v in o.outcomes):
        raise ValueError("Foreign outcome")
    return s, o


def canonical_value(value, key=""):
    if isinstance(value, dict):
        return {k: canonical_value(v, k) for k, v in value.items()}
    if isinstance(value, list):
        result = [canonical_value(v, "instant" if key == "window_starts" else "") for v in value]
        if key in ("alerts", "outcomes", "assumptions"):
            result.sort(key=lambda v: v["id" if key == "assumptions" else "alert_id"])
        return result
    if key in ("score", "weight", "score_threshold"):
        # Text-only removal preserves all 128 allowed digits, independent of Decimal context.
        return value.rstrip("0").rstrip(".") if "." in value else value
    if key in ("available_at", "starts_at", "ends_at", "instant"):
        return instant(value).isoformat(timespec="microseconds").replace("+00:00", "Z")
    return value


def fingerprint(scenario, outcomes):
    s, o = validate_pair(scenario, outcomes)
    facts = s.model_dump()
    facts.pop("content_sha256")
    payload = canonical_value(dict(scenario=facts, outcomes=o.model_dump()))
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
