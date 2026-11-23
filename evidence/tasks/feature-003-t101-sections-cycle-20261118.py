"""Source-only fixture authoring and bounded generation for the T101 recovery."""

import argparse
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

from fraudlens.investigation.models import ROOT

BASE = ROOT / "evals/results/feature-003/report-v6-sections-20261118"
PACK = ROOT / "evals/investigation/report-v6-sections-20261118"
PREVIOUS = ROOT / "evals/results/feature-003/report-v6-successor-20261118"
SCRIPTS = ROOT / "evidence/tasks"
CEILING = 433
CAPS = {"development": 20, "calibration": 6, "final": 42, "judging": 13}


def helper(name):
    spec = importlib.util.spec_from_file_location("t101_" + name, SCRIPTS / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def count(batch):
    import sqlite3

    ledger = batch / "dispatch.sqlite"
    if not ledger.exists():
        return 0
    with sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True) as db:
        return db.execute("SELECT count(*) FROM dispatches").fetchone()[0]


def actual():
    return (
        300
        + sum(count(PREVIOUS / k) for k in ("calibration", "final", "judging"))
        + sum(count(BASE / k) for k in CAPS)
    )


def prepare(stage):
    driver = helper("feature-003-t101-t102-runner-20261118.py")
    author = helper("feature-003-t101-t102-prepare-20261118.py")
    batch = BASE / stage
    split = "development" if stage == "development" else "quality"
    pack = PACK / stage
    settings = (
        [
            ("available", "617.45", "EUR", 0.42),
            ("unavailable", "129.07", "GBP", 0.28),
            ("mixed", "4218.31", "USD", 0.68),
            ("unavailable", "570.11", "EUR", 0.35),
            ("available", "19701.26", "GBP", 0.92),
            ("mixed", "731.61", "USD", 0.51),
            ("unavailable", "872.52", "EUR", 0.46),
            ("mixed", "2793.90", "GBP", 0.62),
        ]
        if stage == "development"
        else [
            ("available", "6149.33", "GBP", 0.62),
            ("unavailable", "95.47", "EUR", 0.19),
            ("mixed", "3176.83", "USD", 0.76),
            ("unavailable", "450.91", "GBP", 0.39),
            ("available", "21332.85", "EUR", 0.95),
            ("available", "76.54", "USD", 0.25),
            ("unavailable", "5821.46", "GBP", 0.73),
            ("mixed", "4348.11", "EUR", 0.67),
        ]
    )
    if stage == "development":
        assert actual() == 352
        settings = settings[:4]
    elif (
        not driver.load(BASE / "development/review.json")["passed"]
        or not driver.load(BASE / "calibration/calibration-result.json")["passed"]
    ):
        raise ValueError("Fresh development and calibration must pass first")
    inputs, refs = [], []
    for i, (history, amount, currency, score) in enumerate(settings, 1):
        location = "Malta" if stage == "development" else "Luxembourg"
        question = (
            f"What precise current statutory reporting deadline applies in {location}?"
            if i == 4
            else "Examine the recorded transfer, score limitations, history scope and available review procedure."
        )
        identity = f"SEC-{stage.upper()}-{i:02}"
        row, ref = author.authored(
            identity,
            (700 if stage == "development" else 720) + i,
            amount,
            currency,
            score,
            history,
            question,
        )
        ref["provenance"] = (
            "Reviewed from source literals before generation. No prior draft or rating used."
        )
        inputs.append(row)
        refs.append(ref)
    (pack / "inputs").mkdir(parents=True, exist_ok=False)
    (pack / "reference").mkdir()
    driver.save(pack / f"inputs/{split}.json", inputs)
    driver.save(pack / "reference/source-obligations.json", refs)
    ids = [row["id"] for row in inputs]
    protocol = dict(
        quality_order=ids,
        timing_order=ids[:5],
        secondary_order=[ids[i] for i in (1, 2, 3, 5, 7)] if stage == "final" else [],
        stage_caps=CAPS,
        total_ceiling=CEILING,
        source="authored synthetic fixtures, reviewed source obligations",
    )
    driver.save(pack / "protocol.json", protocol)
    driver.PACK = pack
    driver.CAPS = dict(driver.CAPS, **{split: CAPS[stage]})
    driver.prepare(SimpleNamespace(batch=batch, stage=split, provider="openai"))
    freeze_path = batch / "freeze.json"
    freeze = driver.load(freeze_path)
    freeze.update(
        semantic_profile="v8",
        report_prompt="v6",
        max_output_tokens=8192,
        request_timeout_seconds=60,
        report_parallel_tools=True,
        report_reasoning_effort="low",
        report_strict_sections=True,
    )
    for path in (Path(__file__).resolve(), pack / "reference/source-obligations.json"):
        freeze["files_sha256"][str(path)] = driver.sha(path)
    freeze_path.write_text(json.dumps(freeze, indent=2) + "\n", encoding="utf-8")
    authorize(stage)


def authorize(stage):
    driver = helper("feature-003-t101-judge-live-20261118.py")
    batch = BASE / stage
    path = batch / "freeze.json"
    freeze = driver.load(path)
    if freeze["maximum_requests"] != CAPS[stage] or actual() + CAPS[stage] > CEILING:
        raise ValueError("Approved request budget would be exceeded")
    driver.save(
        batch / "approval.json",
        dict(
            approved=True,
            stage=freeze["stage"],
            maximum_requests=CAPS[stage],
            model=freeze["model"],
            freeze_sha256=driver.sha(path),
            actual_before=actual(),
            total_ceiling=CEILING,
            user_authorization="User approved more if necessary and ordered completion of T101 on 2026-11-18.",
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "authorize"))
    parser.add_argument("stage", choices=tuple(CAPS))
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.stage)
    elif args.command == "authorize":
        authorize(args.stage)
    else:
        helper("feature-003-latency-final-20261118.py").run(BASE / args.stage, total_cap=CEILING)
