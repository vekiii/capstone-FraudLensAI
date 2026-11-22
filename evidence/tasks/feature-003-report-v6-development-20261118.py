"""Authorized fresh report v6 development stage. Prepare offline; run explicit live only.

Maximum32 actual requests, part of153new/303total approved2026-11-18. No old replay.
Uses existing tested API/worker/observer and durable stage ledger unchanged.
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

from fraudlens.investigation.models import ROOT

PACK = ROOT / "evals/investigation/report-v6-development-20261118"
BATCH = ROOT / "evals/results/feature-003/report-v6-cycle-20261118/development"
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
    if PACK.exists() or BATCH.exists():
        raise ValueError("New materialized stage only; do not reset markers")
    author = module(ROOT / "evidence/tasks/feature-003-t101-t102-prepare-20261118.py", "v8_author")
    rows = [
        ("available", "2816.27", "EUR", 0.46),
        ("unavailable", "184.29", "USD", 0.29),
        ("mixed", "1736.94", "GBP", 0.74),
        ("unavailable", "326.81", "EUR", 0.37),
    ]
    inputs, refs = [], []
    for i, (history, amount, currency, score) in enumerate(rows, 1):
        item, ref = author.authored(
            f"DEV6B-{i:02}",
            620 + i,
            amount,
            currency,
            score,
            history,
            "What is the exact current statutory reporting deadline in Chile?"
            if i == 4
            else (
                "Review the transfer evidence, precisely bounded history, and limits on analyst guidance."
            ),
        )
        ref["provenance"] = (
            "Source-only automated review before dispatch; no output labels or human independence."
        )
        inputs.append(item)
        refs.append(ref)
    save(PACK / "inputs/development.json", inputs)
    save(PACK / "reference/development.json", refs)
    save(
        PACK / "protocol.json",
        dict(
            version=1,
            profile="v8",
            report="v6",
            cap=32,
            order=[r["id"] for r in inputs],
            historical_actual=150,
            total_cap=303,
            decision="User approved one report v6 cycle, 153 new requests, total ceiling303 on2026-11-18",
            gate="All4 valid; support>=.90/coverage>=.80; faithful limits; zero critical/unsupported guidance",
        ),
    )
    runner = module(RUNNER, "v8_runner")
    runner.PACK = PACK
    runner.prepare(SimpleNamespace(batch=BATCH, stage="development", provider="openai"))
    path = BATCH / "freeze.json"
    freeze = runner.load(path)
    freeze.update(
        semantic_profile="v8",
        report_prompt="v6",
        max_output_tokens=8192,
        request_timeout_seconds=45,
        semantic_timeout_seconds=30,
    )
    refs_path = PACK / "reference/development.json"
    freeze["private_review_sha256"] = runner.sha(refs_path)
    freeze["files_sha256"][str(Path(__file__).resolve())] = runner.sha(Path(__file__))
    # Complete the new freeze BEFORE authorization/dispatch, never edit a live freeze.
    path.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    approval = dict(
        approved=True,
        stage="development",
        maximum_requests=32,
        freeze_sha256=runner.sha(path),
        model=freeze["model"],
        user_authorization="2026-11-18 user requested execution and review for reportv6/8192,153new/303total, development32",
    )
    save(BATCH / "approval.json", approval)
    print(json.dumps(dict(prepared=True, calls=0, stage_cap=32)))


def run():
    import httpx

    from fraudlens.investigation.acceptance_harness import require_authorization

    require_authorization(BATCH / "approval.json", BATCH / "freeze.json")
    save(BATCH / "supervisor-intent.json", dict(cap=32, historical_actual=150, total_cap=303))
    env = dict(os.environ, PYTHONPATH=str(ROOT / "backend/src"), PYTHONIOENCODING="utf-8")
    common = ["--batch", str(BATCH), "--approval", str(BATCH / "approval.json"), "--port", "8879"]
    children, logs = [], []
    try:
        # Occupied port must fail before any attempt creation/provider spending.
        import socket

        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 8879))
        for kind in ("api", "worker"):
            log = (BATCH / (kind + ".log")).open("x", encoding="utf-8")
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
            timeout=520,
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
