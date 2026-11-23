"""Read-only comparison; private outcomes joined only after label-free selection."""

from fractions import Fraction

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from fraudlens.simulation.models import CatalogResponse, Comparison, Recipe, instant
from fraudlens.simulation.replay import replay
from fraudlens.simulation.scenarios import Catalog

router = APIRouter(prefix="/api/simulation")


def error(status, code, message):
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


def get_catalog(request):
    configured = getattr(request.app.state, "simulation_catalog", None)
    return configured if configured is not None else Catalog()


@router.get("/scenarios", response_model=CatalogResponse)
def scenarios(request: Request):
    try:
        return CatalogResponse(contract_version=1, items=get_catalog(request).metadata())
    except Exception:
        return error(500, "internal_error", "Internal server error.")


@router.post("/comparisons", response_model=Comparison)
def comparisons(body: Recipe, request: Request):
    try:
        catalog = get_catalog(request)
        ref = body.scenario
        try:
            revision = catalog.resolve(ref.scenario_id, ref.scenario_version)
        except ValueError:
            return error(409, "simulation_version_unavailable", "Simulation version unavailable.")
        if ref.content_sha256 != revision.facts.content_sha256 or any(
            v != 1 for v in body.strategy_versions.model_dump().values()
        ):
            return error(409, "simulation_version_unavailable", "Simulation version unavailable.")
        facts = revision.facts
        results = replay(facts, body.score_threshold, body.budget_minutes_per_window)
        # Outcome access is deliberately after ALL three strategy selections.
        labels = {o.alert_id: o.outcome for o in revision.evaluation_outcomes().outcomes}
        admitted = sorted(
            [a for a in facts.alerts if Fraction(a.score) >= Fraction(body.score_threshold)],
            key=lambda a: (instant(a.available_at), a.alert_id),
        )
        admitted_ids = {a.alert_id for a in admitted}
        positives = {key for key, value in labels.items() if value == "positive"}
        for result in results:
            reviewed = {key for window in result["windows"] for key in window["reviewed_alert_ids"]}
            threshold_misses = len(positives - admitted_ids)
            backlog_misses = len(positives & set(result["pending_alert_ids"]))
            outcome_counts = dict(
                positives_found=len(positives & reviewed),
                positives_missed=threshold_misses + backlog_misses,
                positives_missed_threshold=threshold_misses,
                positives_missed_backlog=backlog_misses,
                reviewed_negatives=sum(labels.get(key) == "negative" for key in reviewed),
            )
            result["counts"] = dict(
                reviewed=len(reviewed),
                backlog=len(result["pending_alert_ids"]),
                unknown_in_horizon=sum(a.alert_id not in labels for a in facts.alerts),
                unknown_reviewed=sum(key not in labels for key in reviewed),
                outcomes=outcome_counts if labels or not facts.alerts else None,
            )
        threshold = body.score_threshold
        canonical = threshold.rstrip("0").rstrip(".") if "." in threshold else threshold
        recipe = body.model_copy(update={"score_threshold": canonical})
        return Comparison(
            contract_version=1,
            recipe=recipe,
            scenario=revision.metadata(),
            admitted_alerts=admitted,
            strategies=results,
        )
    except Exception:
        return error(500, "internal_error", "Internal server error.")
