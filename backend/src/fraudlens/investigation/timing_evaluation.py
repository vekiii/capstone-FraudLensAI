"""Offline SC-006 measurement assessment. No provider/runtime calls or generation.

Trusted observers record end-to-end visible-terminal latency; this module checks
arithmetic and sample identity, not whether an observer measured honestly.
"""

import argparse
import copy
import json
import math
from pathlib import Path

SUCCESS = frozenset({"ready_for_review", "needs_information"})
TERMINAL = SUCCESS | {"failed", "cancelled"}
STATES = TERMINAL | {"created", "gathering_evidence", "drafting", "unknown", "not_run"}


def _index(ids, rows, count):
    if (
        len(ids) != count
        or any(not isinstance(i, str) or not i.strip() for i in ids)
        or len(set(ids)) != count
    ):
        raise ValueError(f"Exactly {count} unique frozen IDs required")
    result = {}
    for row in rows:
        identity = row["id"]
        if identity not in ids or identity in result:
            raise ValueError("Duplicate or foreign measurement")
        result[identity] = copy.deepcopy(row)
    return result


def _seconds(value):
    if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
        raise ValueError("Finite nonnegative measured seconds required")
    return value


def assess_demo(scenario_order, observations):
    indexed = _index(scenario_order, observations, 5)
    rows = []
    for identity in scenario_order:
        row = indexed.get(identity)
        if row is None:
            rows.append(
                dict(
                    id=identity,
                    observed=False,
                    successful_within_90=False,
                    terminal_within_120=False,
                    observation=None,
                )
            )
            continue
        seconds = _seconds(row["seconds"])
        if row["state"] not in STATES or type(row["report_validated"]) is not bool:
            raise ValueError("Invalid observation state/validation")
        success = row["state"] in SUCCESS and row["report_validated"] and seconds <= 90
        terminal = row["state"] in TERMINAL and seconds <= 120
        rows.append(
            dict(
                id=identity,
                observed=True,
                successful_within_90=success,
                terminal_within_120=terminal,
                observation=row,
            )
        )
    successful = sum(r["successful_within_90"] for r in rows)
    all_terminal = all(r["terminal_within_120"] for r in rows)
    return dict(
        denominator=5,
        successful_within_90=successful,
        all_terminal_within_120=all_terminal,
        passed=successful >= 4 and all_terminal,
        rows=rows,
    )


def assess_searches(search_order, observations):
    indexed = _index(search_order, observations, 20)
    durations = []
    for row in indexed.values():
        if type(row["error"]) is not bool:
            raise ValueError("Search error must be Boolean")
        seconds = _seconds(row["seconds"])
        if not row["error"]:
            durations.append(seconds)
    complete = len(durations) == 20
    # Nearest rank ceil(.95*20)=19, NOT maximum/mean/interpolation.
    p95 = sorted(durations)[18] if complete else None
    return dict(
        denominator=20,
        observed=len(indexed),
        successful_searches=len(durations),
        p95_seconds=p95,
        passed=complete and p95 <= 2,
        rows=[indexed.get(i, dict(id=i, missing=True)) for i in search_order],
    )


def main():
    parser = argparse.ArgumentParser(description="Offline timing arithmetic; no network")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    demo = assess_demo(data["scenario_order"], data["observations"])
    search = assess_searches(data["search_order"], data["searches"])
    result = dict(
        protocol_version=1,
        demo=demo,
        local_search=search,
        performance_pass=demo["passed"] and search["passed"],
        limitation="Arithmetic only; observer provenance and frozen run identity require audit.",
    )
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(performance_pass=result["performance_pass"])))


if __name__ == "__main__":
    main()
