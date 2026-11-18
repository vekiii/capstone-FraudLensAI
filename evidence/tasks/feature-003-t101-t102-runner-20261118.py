"""Opt-in fresh generation/timing harness. Never executes on import.

prepare is offline. api/worker/observe/slot require a separately recorded approval
for live batches. TEST batches bypass only that spend gate, never qualify as live
quality/performance evidence. No old script, reference or score file is loaded.
"""

import argparse
import asyncio
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from fraudlens.investigation.acceptance_harness import (
    DispatchLedger,
    build_service,
    require_authorization,
)
from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT, validate
from fraudlens.investigation.report_policy import HUMAN_AUTHORITY_POLICY
from fraudlens.investigation.settings import load_settings
from fraudlens.investigation.timing_observer import observe
from fraudlens.investigation.validation import validate_report

PACK = ROOT / "evals/investigation/acceptance-v1-20261118"
CAPS = dict(development=32, quality=64, timing=40)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(args):
    args.batch.mkdir(parents=True, exist_ok=False)
    inputs = [input_only(row) for row in load(PACK / "inputs" / (args.stage + ".json"))]
    save(args.batch / "inputs.json", inputs)
    knowledge = KnowledgeStore(args.batch / "runs.sqlite")
    corpus = knowledge.publish(ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/manifest.json")
    retrieval = knowledge.save_configuration(
        load(ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json")
    )
    settings = load_settings()
    model = settings.model.get_secret_value() if args.provider == "openai" else "TEST-only"
    if args.provider == "openai" and (not model or not settings.api_key.get_secret_value()):
        raise ValueError("Configured model/key required; no capability probe performed")
    cap = CAPS[args.stage] if args.provider == "openai" else 0
    if cap:
        DispatchLedger(args.batch / "dispatch.sqlite", cap, model)
    paths = list((ROOT / "backend/src/fraudlens").rglob("*.py"))
    paths += list((ROOT / "data/knowledge/fraudlens-aml-knowledge-v1").rglob("*"))
    paths += list((ROOT / "specs/003-ai-investigation/contracts").glob("*.json"))
    paths += list((ROOT / "prompts/application").glob("*.md"))
    paths += [
        Path(__file__).resolve(),
        args.batch / "inputs.json",
        PACK / "protocol.json",
        ROOT / "uv.lock",
        ROOT / "frontend/package-lock.json",
    ]
    freeze = dict(
        batch_directory=str(args.batch.resolve()),
        stage=args.stage,
        provider=args.provider,
        model=model,
        maximum_requests=cap,
        corpus_version=corpus,
        local_retrieval_version=retrieval,
        semantic_retrieval=args.provider == "openai",
        source_mode="fixture",
        input_order=[i["id"] for i in inputs],
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        dirty_status=subprocess.check_output(["git", "status", "--porcelain"], text=True),
        machine=dict(os=platform.platform(), cpu=platform.processor(), python=sys.version),
        files_sha256={str(p.resolve()): sha(p) for p in paths if p.is_file()},
        observer="separate HTTP process; perf_counter; 250ms; parent per-slot125s watchdog",
        acceptance_eligible=args.provider == "openai",
    )
    save(args.batch / "freeze.json", freeze)
    print(
        json.dumps(
            dict(
                prepared=True,
                provider=args.provider,
                cap=cap,
                freeze_sha256=sha(args.batch / "freeze.json"),
                new_provider_calls=0,
            )
        )
    )


def setup(args):
    freeze_path = args.batch / "freeze.json"
    freeze = load(freeze_path)
    if freeze["provider"] == "openai":
        if args.approval is None:
            raise ValueError("Separate reviewed hash-bound approval required")
        freeze = require_authorization(args.approval, freeze_path)
    else:
        for name, expected in freeze["files_sha256"].items():
            if sha(Path(name)) != expected:
                raise ValueError("Frozen TEST execution source changed")
    os.environ.update(
        INVESTIGATION_ENABLED="true",
        INVESTIGATION_SOURCE="fixture",
        INVESTIGATION_PROVIDER=freeze["provider"],
        INVESTIGATION_STORE=str(args.batch / "runs.sqlite"),
        INVESTIGATION_SEMANTIC_RETRIEVAL=str(freeze["semantic_retrieval"]).lower(),
        INVESTIGATION_SEMANTIC_PROFILE=freeze.get("semantic_profile", "v6"),
        INVESTIGATION_REPORT_PROMPT=freeze.get("report_prompt", "v4"),
        INVESTIGATION_REQUEST_TIMEOUT_SECONDS=str(freeze.get("request_timeout_seconds", 30)),
        INVESTIGATION_MAX_OUTPUT_TOKENS=str(freeze.get("max_output_tokens", 4096)),
    )
    # A local T098 dataset index setting must not contaminate authored fixture mode.
    from fraudlens.investigation.settings import InvestigationSettings

    private = load_settings()
    settings = InvestigationSettings(
        enabled=True,
        source="fixture",
        provider=freeze["provider"],
        semantic_retrieval=freeze["semantic_retrieval"],
        semantic_profile=freeze.get("semantic_profile", "v6"),
        report_prompt=freeze.get("report_prompt", "v4"),
        report_reasoning_effort=freeze.get("report_reasoning_effort"),
        report_parallel_tools=freeze.get("report_parallel_tools", False),
        report_strict_sections=freeze.get("report_strict_sections", False),
        request_timeout_seconds=freeze.get("request_timeout_seconds", 30),
        max_output_tokens=freeze.get("max_output_tokens", 4096),
        store=args.batch / "runs.sqlite",
        api_key=private.api_key,
        model=freeze["model"] if freeze["provider"] == "openai" else "",
        analyst="acceptance-v1-operator",
    )
    if freeze["provider"] == "openai" and private.model.get_secret_value() != freeze["model"]:
        raise ValueError("Configured model changed")
    knowledge = KnowledgeStore(args.batch / "runs.sqlite", initialize=False)
    if (
        knowledge.latest("corpus") != freeze["corpus_version"]
        or knowledge.latest("retrieval") != freeze["local_retrieval_version"]
    ):
        raise ValueError("Frozen corpus/configuration changed")
    ledger = (
        DispatchLedger(args.batch / "dispatch.sqlite", freeze["maximum_requests"], freeze["model"])
        if freeze["provider"] == "openai"
        else None
    )
    service = build_service(knowledge, load(args.batch / "inputs.json"), settings, ledger=ledger)
    return freeze, knowledge, service


def validate_view(service, expected, view):
    validate("RunView", view)
    context = expected["context"]
    if any(
        view[key] != context[key]
        for key in ("case_id", "source_mode", "snapshot_ref", "context_revision")
    ):
        raise ValueError("Foreign observed source")
    report = view["report"]
    if report is None:
        return False
    evidence = service.evidence(view["attempt_id"])
    checked = validate_report(
        report["draft"],
        evidence,
        view["attempt_id"],
        context["context_revision"],
        context,
        view["corpus_version"],
        report_policy=HUMAN_AUTHORITY_POLICY,
    )
    return checked["report_id"] == report["report_id"]


async def slot(args, service):
    import httpx

    item = next(i for i in load(args.batch / "inputs.json") if i["id"] == args.identity)
    context = item["context"]
    request = {key: context[key] for key in ("case_id", "source_mode", "snapshot_ref")}
    async with httpx.AsyncClient(
        base_url=f"http://127.0.0.1:{args.port}", trust_env=False, follow_redirects=False, timeout=2
    ) as client:
        result = await observe(
            client,
            request,
            args.batch / (item["id"] + "-intent.json"),
            lambda view: validate_view(service, item, view),
        )
    # Save full server view/context/evidence/audit AFTER immutable observations.
    if result["attempt_id"]:
        aid = result["attempt_id"]
        save(
            args.batch / (item["id"] + "-archive.json"),
            dict(
                view=service.read(aid),
                context=service.context(aid),
                evidence=service.evidence(aid),
                events=service.events(aid),
            ),
        )


def observe_batch(args, freeze, service):
    save(
        args.batch / "batch-intent.json",
        dict(
            freeze_sha256=sha(args.batch / "freeze.json"),
            order=freeze["input_order"],
            provider=freeze["provider"],
        ),
    )
    # Queue must be idle before first dispatch. A previous marker blocks replay.
    with service.repo.connection() as db:
        if db.execute("SELECT count(*) FROM attempts").fetchone()[0]:
            raise ValueError("Fresh empty queue required")
    observations = []
    for identity in freeze["input_order"]:
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "slot",
            "--batch",
            str(args.batch),
            "--identity",
            identity,
            "--port",
            str(args.port),
        ]
        if args.approval:
            command += ["--approval", str(args.approval)]
        started = time.perf_counter()
        try:
            with (args.batch / (identity + "-observer.log")).open("x", encoding="utf-8") as log:
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=125,
                    creationflags=0x08000000 if os.name == "nt" else 0,
                )
            if result.returncode:
                raise RuntimeError("Observer process failed")
        except (subprocess.TimeoutExpired, RuntimeError) as exc:
            save(
                args.batch / (identity + "-watchdog.json"),
                dict(
                    error=type(exc).__name__,
                    parent_elapsed_seconds=time.perf_counter() - started,
                    terminal_state="unknown",
                    worker_may_continue=True,
                    acceptance_pass=False,
                ),
            )
            break
        observed = load(args.batch / (identity + "-intent-result.json"))
        observations.append(dict(id=identity, **observed))
        if observed["stop_batch"]:
            break
        if freeze["provider"] == "openai":
            with sqlite_connection(args.batch / "dispatch.sqlite") as db:
                outcomes = db.execute("SELECT result FROM dispatches").fetchall()
            if any(r[0] is None or json.loads(r[0]).get("stop_batch") for r in outcomes):
                break
    save(
        args.batch / "observations.json",
        dict(
            provider=freeze["provider"],
            acceptance_eligible=freeze["acceptance_eligible"],
            scenario_order=freeze["input_order"],
            observations=observations,
        ),
    )


@contextmanager
def sqlite_connection(path):
    import sqlite3

    db = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        yield db
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "api", "worker", "observe", "slot"))
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--stage", choices=tuple(CAPS), default="development")
    parser.add_argument("--provider", choices=("test", "openai"), default="test")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--identity")
    parser.add_argument("--port", type=int, default=8768)
    args = parser.parse_args()
    args.batch = args.batch.resolve()
    if args.approval:
        args.approval = args.approval.resolve()
    if args.command == "prepare":
        prepare(args)
        return
    freeze, knowledge, service = setup(args)
    if args.command == "api":
        import uvicorn

        from fraudlens.main import create_app

        app = create_app()
        app.state.knowledge_store = knowledge
        app.state.investigation_service = service
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    elif args.command == "worker":

        async def work():
            for _ in range(1800):
                result = await service.work_once()
                if result:
                    print(
                        json.dumps(dict(attempt_id=result["attempt_id"], state=result["state"])),
                        flush=True,
                    )
                await asyncio.sleep(0.05)

        asyncio.run(work())
    elif args.command == "slot":
        asyncio.run(slot(args, service))
    else:
        observe_batch(args, freeze, service)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Exception messages/SDK repr may contain sensitive environment values.
        print(json.dumps(dict(failed=True, error_type=type(error).__name__)))
        raise SystemExit(2) from None
