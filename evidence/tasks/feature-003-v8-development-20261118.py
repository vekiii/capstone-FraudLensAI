"""Authorized fresh v8 development stage. Prepare offline; run explicit live only.

Maximum32 actual requests, part of153new/279total approved2026-11-18. No old replay.
Uses existing tested API/worker/observer and durable stage ledger unchanged.
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from types import SimpleNamespace

from fraudlens.investigation.models import ROOT

PACK = ROOT / "evals/investigation/v8-development-20261118"
BATCH = ROOT / "evals/results/feature-003/v8-cycle-20261118/development"
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
        ("available", "4582.73", "EUR", 0.54),
        ("unavailable", "113.86", "USD", 0.32),
        ("mixed", "1294.68", "GBP", 0.71),
        ("unavailable", "219.43", "EUR", 0.39),
    ]
    inputs, refs = [], []
    for i, (history, amount, currency, score) in enumerate(rows, 1):
        item, ref = author.authored(
            f"DEV8N-{i:02}",
            600 + i,
            amount,
            currency,
            score,
            history,
            author.NO_GUIDANCE if i == 4 else author.QUESTION,
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
            report="v5",
            cap=32,
            order=[r["id"] for r in inputs],
            historical_actual=126,
            total_cap=279,
            decision="User Potvrdjujem; explicit candidate153new approved2026-11-18",
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
        report_prompt="v5",
        request_timeout_seconds=45,
        semantic_timeout_seconds=30,
    )
    # Complete the new freeze BEFORE authorization/dispatch, never edit a live freeze.
    path.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    approval = dict(
        approved=True,
        stage="development",
        maximum_requests=32,
        freeze_sha256=runner.sha(path),
        model=freeze["model"],
        user_authorization="2026-11-18 user Potvrdjujem to v8/reportv5,153new/279total; development32",
    )
    save(BATCH / "approval.json", approval)
    print(json.dumps(dict(prepared=True, calls=0, stage_cap=32)))


def run():
    import httpx

    from fraudlens.investigation.acceptance_harness import require_authorization

    require_authorization(BATCH / "approval.json", BATCH / "freeze.json")
    save(BATCH / "supervisor-intent.json", dict(cap=32, historical_actual=126, total_cap=279))
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
