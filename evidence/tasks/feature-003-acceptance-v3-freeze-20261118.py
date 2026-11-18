"""Offline freeze of the prospectively shared8/5 cohort. No network calls."""

import argparse
import hashlib
import json
import subprocess
from importlib.metadata import version
from pathlib import Path

from fraudlens.investigation.acceptance_harness import DispatchLedger, require_authorization
from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.retrieval_semantic_v6 import policy_identity
from fraudlens.investigation.settings import load_settings


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=("first-five", "last-three"), required=True)
    args = parser.parse_args()
    session = ROOT / "evals/results/feature-003/acceptance-live-20261118"
    pack = ROOT / "evals/investigation/acceptance-v3-20261118"
    calibration = session / "controls-v2-calibration"
    if not load(calibration / "calibration-result.json")["passed"]:
        raise ValueError("Successful exact6/6 required before held-out dispatch")
    batch = session / "cohort-v3" / args.part
    batch.mkdir(parents=True, exist_ok=False)
    all_inputs = [input_only(v) for v in load(pack / "inputs/cohort.json")]
    first = args.part == "first-five"
    inputs = all_inputs[:5] if first else all_inputs[5:]
    cap = 40 if first else 24
    save(batch / "inputs.json", inputs)
    save(batch / "searches.json", load(pack / "inputs/search.json"))
    roles = load(pack / "reference/roles.json")
    knowledge = KnowledgeStore(batch / "runs.sqlite")
    corpus = knowledge.publish(ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/manifest.json")
    retrieval = knowledge.save_configuration(
        load(ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json")
    )
    private = load_settings()
    model = private.model.get_secret_value()
    if model != "gpt-6-luna" or not private.api_key.get_secret_value():
        raise ValueError("Reviewed configured model/key required")
    DispatchLedger(batch / "dispatch.sqlite", cap, model)
    machine = load(session / "timing/machine-observer.json")
    for name, previous in machine["sdk_versions"].items():
        if version(name) != previous:
            raise ValueError("SDK changed")
    save(batch / "machine-observer.json", machine)
    policy = policy_identity(model, knowledge.passages(corpus), profile="v7")
    source = dict(
        corpus_version=corpus,
        local_retrieval_version=retrieval,
        semantic_policy=policy,
        semantic_profile="v7",
        source_mode="authored_synthetic_fixture_not_ML_evaluation",
        stage_order=[v["id"] for v in inputs],
        full_quality_order=roles["quality_order"],
        timing_order=roles["timing_order"],
        secondary_order=roles["secondary_order"],
        sample_overlap=roles["sample_overlap"],
        limits=dict(
            provider_requests=8,
            tool_calls=12,
            request_seconds=45,
            semantic_request_seconds=30,
            attempt_seconds=120,
            output_tokens=4096,
            input_bytes=48000,
        ),
        expected_search_versions={
            v["id"]: dict(corpus=corpus, local_retrieval=retrieval)
            for v in load(batch / "searches.json")
        },
    )
    save(batch / "source-observer-freeze.json", source)
    paths = list((ROOT / "backend/src/fraudlens").rglob("*.py"))
    paths += list((ROOT / "data/knowledge/fraudlens-aml-knowledge-v1").rglob("*"))
    paths += list((ROOT / "specs/003-ai-investigation/contracts").glob("*.json"))
    paths += list((ROOT / "prompts/application").glob("*.md"))
    paths += [
        Path(__file__).resolve(),
        ROOT / "evidence/tasks/feature-003-t101-t102-runner-20261118.py",
        ROOT / "uv.lock",
        ROOT / "frontend/package-lock.json",
        pack / "protocol.json",
        batch / "inputs.json",
        batch / "searches.json",
        batch / "machine-observer.json",
        batch / "source-observer-freeze.json",
    ]
    freeze = dict(
        batch_directory=str(batch),
        stage="shared-timing-quality" if first else "quality-tail",
        provider="openai",
        model=model,
        maximum_requests=cap,
        source_mode="fixture",
        corpus_version=corpus,
        local_retrieval_version=retrieval,
        semantic_retrieval=True,
        semantic_profile="v7",
        request_timeout_seconds=45,
        semantic_policy=policy,
        input_order=[v["id"] for v in inputs],
        search_order=[v["id"] for v in load(batch / "searches.json")],
        full_quality_order=roles["quality_order"],
        timing_order=roles["timing_order"],
        secondary_order=roles["secondary_order"],
        acceptance_eligible=True,
        prior_actual_before_cohort=68,
        overall_cap=155,
        prospective_full_maximum=145,
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        dirty_status=subprocess.check_output(["git", "status", "--porcelain"], text=True),
        private_source_obligations_sha256=sha(pack / "reference/source-obligations.json"),
        private_roles_sha256=sha(pack / "reference/roles.json"),
        files_sha256={str(p.resolve()): sha(p) for p in paths if p.is_file()},
    )
    save(batch / "freeze.json", freeze)
    save(
        batch / "approval.json",
        dict(
            approved=True,
            freeze_sha256=sha(batch / "freeze.json"),
            stage=freeze["stage"],
            maximum_requests=cap,
            model=model,
            user_authorization="Prihvatam doradu unutar T101/T102; Da, novi profil sa 45s",
            scope="Prospective shared8/5 cohort, v7 explicit formatting clarification; approved45/120/8; semantic30 "
            "limits; same original155 cap, original results retained, operational retries authorized",
        ),
    )
    require_authorization(batch / "approval.json", batch / "freeze.json")
    print(
        json.dumps(
            dict(
                prepared=args.part,
                cases=len(inputs),
                cap=cap,
                semantic_profile="v7",
                freeze_sha256=sha(batch / "freeze.json"),
                actual_calls=0,
            )
        )
    )


if __name__ == "__main__":
    main()
