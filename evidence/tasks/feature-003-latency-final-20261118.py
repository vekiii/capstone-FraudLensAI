"""Authorized fresh report v6 final generation stage. Prepare offline; run explicit live only.

Maximum42 actual requests, part of135 remaining/303 total approved2026-11-18. No old replay.
Uses existing tested API/worker/observer and durable stage ledger unchanged.
"""

import argparse
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

from fraudlens.investigation.models import ROOT

PACK = ROOT / "evals/investigation/report-v6-final-20261118"
BATCH = ROOT / "evals/results/feature-003/report-v6-latency-cycle-20261118/final"
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
    cal_result = BATCH.parent / "calibration-clarified/calibration-result.json"
    cal = json.loads(cal_result.read_text(encoding="utf-8"))
    if not retrieval["threshold_pass"] or not cal["passed"]:
        raise ValueError("Final generation requires passing retrieval and report calibration")
    if PACK.exists() or BATCH.exists():
        raise ValueError("Final pack already prepared")
    author = module(
        ROOT / "evidence/tasks/feature-003-t101-t102-prepare-20261118.py", "final_author"
    )
    rows = [
        ("available", "987.64", "EUR", 0.53),
        ("unavailable", "244.12", "GBP", 0.24),
        ("mixed", "7894.13", "USD", 0.73),
        ("unavailable", "89.60", "EUR", 0.32),
        ("available", "18641.79", "GBP", 0.94),
        ("available", "45.92", "USD", 0.18),
        ("unavailable", "6608.49", "EUR", 0.78),
        ("mixed", "2731.04", "GBP", 0.61),
    ]
    inputs, refs = [], []
    for i, (kind, amount, unit, score) in enumerate(rows, 1):
        question = (
            "What is the exact current statutory filing deadline in Uruguay?"
            if i == 4
            else "Review this transfer using the available case facts, time window, and applicable procedure."
        )
        item, ref = author.authored(
            f"LAT-FINAL-{i:02}", 660 + i, amount, unit, score, kind, question
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
    searches = [dict(id=f"LAT-SEARCH-{i:02}", query=q) for i, q in enumerate(questions, 1)]
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
            approved_ceiling=303,
            generation_cap=42,
            judging_cap=13,
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
        cal_result,
        PACK / "inputs/searches.json",
        PACK / "reference/source-obligations.json",
    ):
        freeze["files_sha256"][str(pinned)] = runner.sha(pinned)
    path.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    save(
        BATCH / "approval.json",
        dict(
            approved=True,
            stage="quality",
            maximum_requests=42,
            freeze_sha256=runner.sha(path),
            model=freeze["model"],
            user_authorization="2026-11-18 user requested final evaluation after corrective cycle, ceiling 303",
        ),
    )


def run(batch=None, *, total_cap=303):
    import httpx

    from fraudlens.investigation.acceptance_harness import require_authorization

    batch = BATCH if batch is None else batch
    frozen = require_authorization(batch / "approval.json", batch / "freeze.json")
    save(
        batch / "supervisor-intent.json",
        dict(cap=frozen["maximum_requests"], reserved_judging=13, total_cap=total_cap),
    )
    env = dict(os.environ, PYTHONPATH=str(ROOT / "backend/src"), PYTHONIOENCODING="utf-8")
    common = ["--batch", str(batch), "--approval", str(batch / "approval.json"), "--port", "8879"]
    children, logs = [], []
    try:
        # Occupied port must fail before any attempt creation/provider spending.
        import socket

        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 8879))
        for kind in ("api", "worker"):
            log = (batch / (kind + ".log")).open("x", encoding="utf-8")
            logs.append(log)
            children.append(
                subprocess.Popen(
                    [sys.executable, str(RUNNER), kind, *common],
                    cwd=ROOT,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    creationflags=0x08000000 if os.name == "nt" else 0,
                )
            )
            if kind == "api":
                for _ in range(50):
                    if children[-1].poll() is not None:
                        raise ValueError("API startup failed")
                    try:
                        with httpx.Client(trust_env=False, timeout=0.5) as client:
                            response = client.get("http://127.0.0.1:8879/openapi.json")
                            if response.status_code == 200:
                                break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.1)
                else:
                    raise ValueError("API startup deadline")
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "observe", *common],
            cwd=ROOT,
            env=env,
            timeout=1025,
            creationflags=0x08000000 if os.name == "nt" else 0,
        )
        if completed.returncode:
            raise ValueError("Observer failure; preserve all unknown outcomes")
    finally:
        for child in reversed(children):
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
        for log in logs:
            log.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "run"))
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    else:
        run()
