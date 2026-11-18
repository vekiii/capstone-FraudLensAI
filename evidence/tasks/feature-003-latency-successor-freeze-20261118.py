"""Offline freeze for fresh final evaluation with complete source evidence.

This prepares inputs and provenance. The user must authorize the stated paid ceiling
before an operator can create a separate hash-bound dispatch approval.
"""

import importlib.util
import json
import platform
import sys
from pathlib import Path
from types import SimpleNamespace

from fraudlens.investigation.models import ROOT

PACK = ROOT / "evals/investigation/report-v6-successor-20261118"
BATCH = ROOT / "evals/results/feature-003/report-v6-successor-20261118/final"
RUNNER = ROOT / "evidence/tasks/feature-003-t101-t102-runner-20261118.py"


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def prepare():
    retrieval_result = ROOT / "evidence/tasks/feature-003-latency-retrieval-20261118-results.json"
    retrieval = json.loads(retrieval_result.read_text(encoding="utf-8"))
    cal_freeze = BATCH.parent / "calibration/freeze.json"
    if not retrieval["threshold_pass"] or not cal_freeze.is_file():
        raise ValueError("Prepare retrieval evidence and fresh calibration before final inputs")
    if PACK.exists() or BATCH.exists():
        raise ValueError("Final pack already prepared")
    author = module(
        ROOT / "evidence/tasks/feature-003-t101-t102-prepare-20261118.py", "final_author"
    )
    rows = [
        ("available", "1402.24", "EUR", 0.53),
        ("unavailable", "807.38", "GBP", 0.24),
        ("mixed", "6115.92", "USD", 0.73),
        ("unavailable", "162.47", "EUR", 0.32),
        ("available", "14833.94", "GBP", 0.94),
        ("available", "62.39", "USD", 0.18),
        ("unavailable", "4752.65", "EUR", 0.78),
        ("mixed", "3056.31", "GBP", 0.61),
    ]
    inputs, refs = [], []
    for i, (kind, amount, unit, score) in enumerate(rows, 1):
        question = (
            "What is the exact current statutory filing deadline in Costa Rica?"
            if i == 4
            else "Review this transfer using the available case facts, time window, and applicable procedure."
        )
        item, ref = author.authored(
            f"NEXT-FINAL-{i:02}", 680 + i, amount, unit, score, kind, question
        )
        ref["provenance"] = (
            "Codex source review before dispatch. No prior generated reports or outcome labels."
        )
        inputs.append(item)
        refs.append(ref)
    ids = [r["id"] for r in inputs]
    # Separate, new local timing queries. No labels or search outputs in these rows.
    questions = [
        "Escalate a case with incomplete information",
        "Confirm the exact transaction fields",
        "What does the score prove",
        "Explain unknown employment",
        "Describe what a citation establishes",
        "Missing device evidence",
        "Keep amounts in their original currency",
        "What is a simulated procedure",
        "Document the choice to close",
        "Time basis of a benchmark transfer",
        "Record limits of partial history",
        "Keep contradictory sources separate",
        "Identify a passage by its version",
        "Summarize records versus narrative",
        "Scope of US affiliate sharing",
        "Evidence for a suggested check",
        "Preserve the original time",
        "Unknown account history",
        "Current tax rate in Peru",
        "Weather forecast for Friday",
    ]
    searches = [dict(id=f"NEXT-SEARCH-{i:02}", query=q) for i, q in enumerate(questions, 1)]
    save(PACK / "inputs/quality.json", inputs)
    save(PACK / "inputs/searches.json", searches)
    save(PACK / "reference/source-obligations.json", refs)
    save(
        PACK / "protocol.json",
        dict(
            quality_order=ids,
            timing_order=ids[:5],
            secondary_order=[ids[i] for i in (1, 2, 3, 5, 7)],
            source="authored synthetic fixtures",
            machine=platform.platform(),
            python=sys.version,
            clock="perf_counter; separate HTTP observer; 250ms polling",
            requested_ceiling=361,
            current_ceiling=303,
            runtime_facts=True,
            typed_judge_units=True,
            generation_cap=42,
            judging_cap=13,
            calibration_cap=6,
            overlap="first five of eight",
        ),
    )
    runner = module(RUNNER, "final_runner")
    runner.PACK = PACK
    runner.CAPS = dict(runner.CAPS, quality=42)
    runner.prepare(SimpleNamespace(batch=BATCH, stage="quality", provider="openai"))
    path = BATCH / "freeze.json"
    freeze = runner.load(path)
    freeze.update(
        semantic_profile="v8",
        report_prompt="v6",
        max_output_tokens=8192,
        request_timeout_seconds=60,
        report_reasoning_effort="low",
        report_parallel_tools=True,
        semantic_timeout_seconds=30,
    )
    for pinned in (
        Path(__file__).resolve(),
        retrieval_result,
        cal_freeze,
        PACK / "inputs/searches.json",
        PACK / "reference/source-obligations.json",
    ):
        freeze["files_sha256"][str(pinned)] = runner.sha(pinned)
    path.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    save(
        BATCH / "pending-decision.json",
        dict(
            stage="quality",
            approved=False,
            generation_cap=42,
            judging_cap=13,
            calibration_cap=6,
            requested_total_ceiling=361,
            freeze_sha256=runner.sha(path),
            status="awaiting explicit budget increase and passing fresh judge calibration",
        ),
    )


if __name__ == "__main__":
    prepare()
