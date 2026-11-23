"""Read-only live ledgers/outputs -> compact public evidence; never dispatches."""

import hashlib
import json
import sqlite3

from fraudlens.investigation.models import ROOT

SESSION = ROOT / "evals/results/feature-003/acceptance-live-20261118"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def collect():
    ledgers = sorted(SESSION.rglob("dispatch.sqlite")) + [
        ROOT
        / "evals/results/feature-003/acceptance-preparation-20261118/development-proposal/dispatch.sqlite"
    ]
    stages, totals = (
        [],
        dict(actual_requests=0, http200=0, http400=0, http429=0, unknown=0, known_tokens=0),
    )
    for path in ledgers:
        if "frozen-runtime" in str(path):
            continue
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
            rows = db.execute("SELECT result FROM dispatches ORDER BY sequence").fetchall()
        if not rows:
            continue
        counts = dict(
            actual_requests=len(rows), http200=0, http400=0, http429=0, unknown=0, known_tokens=0
        )
        for (raw,) in rows:
            result = json.loads(raw) if raw else {}
            status = result.get("status")
            counts["unknown" if status is None else f"http{status}"] += 1
            counts["known_tokens"] += (result.get("usage") or {}).get("total_tokens", 0)
        stages.append(dict(path=path.relative_to(ROOT).as_posix(), **counts))
        for key in totals:
            totals[key] += counts[key]
    quality = load(SESSION / "cohort-v3/judging/quality-assessment.json")
    timing = load(SESSION / "cohort-v3/first-five/timing-assessment.json")
    outcomes = []
    for stage in ("first-five", "last-three"):
        for path in sorted((SESSION / "cohort-v3" / stage).glob("RUN3-*-intent-result.json")):
            raw = load(path)
            outcomes.append(
                dict(
                    id=path.name.split("-intent")[0],
                    **{
                        key: raw[key]
                        for key in ("state", "seconds", "report_validated", "attempt_id")
                    },
                )
            )
    # The immutable raw files stay ignored; hashes bind the actual evidence used here.
    files = {}
    for path in SESSION.rglob("*"):
        if path.is_file() and (
            path.name
            in (
                "dispatch.sqlite",
                "freeze.json",
                "source-observer-freeze.json",
                "quality-assessment.json",
                "quality-envelope.json",
                "timing-assessment.json",
                "timing-envelope.json",
                "packets-reviewed.json",
                "custodian-review.json",
            )
            or path.name.endswith("-intent-result.json")
        ):
            files[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(
        kind="Actual RUN3/v7/request45; failed acceptance retained",
        total_budget=155,
        totals=totals,
        remaining_requests=155 - totals["actual_requests"],
        unknown_usage_is_not_zero=True,
        spend="unknown",
        stages=stages,
        generation=dict(
            profile="v7",
            report_prompt="v4",
            request_seconds=45,
            semantic_seconds=30,
            useful_seconds=90,
            total_seconds=120,
            outcomes=outcomes,
        ),
        quality={
            key: quality[key]
            for key in (
                "quality_assessment_valid",
                "quality_pass",
                "passing_reports",
                "report_count",
                "failed_reports",
                "reports",
                "calibration",
                "human_validation",
            )
        },
        paired_disagreements=[
            {key: value for key, value in row.items() if key not in ("primary", "secondary")}
            for row in quality["disagreements"]
        ],
        timing=dict(
            useful_within_90=timing["demo"]["successful_within_90"],
            denominator=5,
            all_terminal_within_120=timing["demo"]["all_terminal_within_120"],
            local_search=timing["local_search"],
            performance_pass=timing["performance_pass"],
        ),
        limitation="Authored synthetic source fixtures plus real provider; not ML/population evaluation or independent human/model review. Zero critical flags only in five evaluable reports; three absent reports fail.",
        source_files_sha256=files,
    )


if __name__ == "__main__":
    target = ROOT / "evidence/tasks/feature-003-t101-t102-run3-20261118-results.json"
    with target.open("x", encoding="utf-8") as stream:
        json.dump(collect(), stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(target.relative_to(ROOT).as_posix())
