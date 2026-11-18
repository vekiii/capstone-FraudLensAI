"""Pure label-free deterministic replay with exact rational priorities."""

from fractions import Fraction

from pydantic import TypeAdapter

from fraudlens.simulation.models import Nonnegative, Scenario, Score, instant


def replay(scenario, score_threshold, budget_minutes_per_window):
    facts = Scenario.model_validate(scenario)
    threshold = TypeAdapter(Score).validate_python(score_threshold, strict=True)
    budget = TypeAdapter(Nonnegative).validate_python(budget_minutes_per_window, strict=True)
    admitted = [a for a in facts.alerts if Fraction(a.score) >= Fraction(threshold)]
    def arrival(a):
        return instant(a.available_at), a.alert_id
    strategies = []
    for strategy in ("fifo", "highest_score", "weighted_score_per_minute"):
        reviewed, windows = set(), []
        for start in facts.window_starts:
            candidates = [
                a
                for a in admitted
                if a.alert_id not in reviewed and instant(a.available_at) <= instant(start)
            ]
            if strategy == "fifo":
                candidates.sort(key=arrival)
            else:

                def key(a):
                    priority = Fraction(a.score)
                    if strategy == "weighted_score_per_minute":
                        priority *= Fraction(a.weight) / a.estimated_review_minutes
                    return (-priority, *arrival(a))

                candidates.sort(key=key)
            selected, used = [], 0
            for alert in candidates:
                if used + alert.estimated_review_minutes <= budget:
                    selected.append(alert.alert_id)
                    reviewed.add(alert.alert_id)
                    used += alert.estimated_review_minutes
            windows.append(
                dict(
                    starts_at=start,
                    ranked_alert_ids=[a.alert_id for a in candidates],
                    reviewed_alert_ids=selected,
                    used_minutes=used,
                )
            )
        strategies.append(
            dict(
                strategy_id=strategy,
                windows=windows,
                pending_alert_ids=[
                    a.alert_id for a in sorted(admitted, key=arrival) if a.alert_id not in reviewed
                ],
            )
        )
    return strategies
