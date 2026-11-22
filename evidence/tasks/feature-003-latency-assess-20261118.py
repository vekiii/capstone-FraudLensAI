"""Offline timing, exact report packet materialization, and final aggregation."""

import argparse
import importlib.util
import time
from pathlib import Path

from fraudlens.investigation.acceptance_harness import require_authorization
from fraudlens.investigation.judging_v4 import aggregate, ratings_map
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.retrieval import search
from fraudlens.investigation.timing_evaluation import assess_demo, assess_searches

BATCH = ROOT / "evals/results/feature-003/report-v6-latency-cycle-20261118"
PACK = ROOT / "evals/investigation/report-v6-final-20261118"


def helper(filename, name):
    path = ROOT / "evidence/tasks" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(batch=BATCH, pack=PACK, *, runtime_facts=False, quality_only=False):
    driver = helper("feature-003-latency-judge-20261118.py", "driver")
    materializer = helper("feature-003-materialize-quality-v2-20261118.py", "materializer")
    final = batch / "final"
    freeze = require_authorization(final / "approval.json", final / "freeze.json")
    protocol = driver.load(pack / "protocol.json")
    order = protocol["quality_order"]
    assert order == freeze["input_order"]
    observations = driver.load(final / "observations.json")["observations"]
    if not quality_only:
        timing_ids = protocol["timing_order"]
        timed = [
            {k: o[k] for k in ("id", "seconds", "state", "report_validated")}
            for o in observations
            if o["id"] in timing_ids
        ]
        queries = driver.load(pack / "inputs/searches.json")
        store = KnowledgeStore(final / "runs.sqlite", initialize=False)
        corpus, retrieval = freeze["corpus_version"], freeze["local_retrieval_version"]
        store.passages(corpus)
        local = []
        for row in queries:
            before = time.perf_counter()
            failed = False
            try:
                search(store, row["query"], corpus, retrieval)
            except OSError, ValueError, LookupError:
                failed = True
            local.append(dict(id=row["id"], seconds=time.perf_counter() - before, error=failed))
        demo = assess_demo(timing_ids, timed)
        searches = assess_searches([q["id"] for q in queries], local)
        driver.save(
            batch / "timing-results.json",
            dict(
                demo=demo,
                local_search=searches,
                performance_pass=demo["passed"] and searches["passed"],
            ),
        )
    refs = {r["id"]: r for r in driver.load(pack / "reference/source-obligations.json")}
    inputs = driver.load(final / "inputs.json")
    inventory, packets = [], []
    for item in inputs:
        identity = item["id"]
        archive_path = final / (identity + "-archive.json")
        archives = (
            driver.load(archive_path)
            if archive_path.is_file()
            else dict(context=item["context"], evidence=[], view=dict(run_id="inv_" + "0" * 32))
        )
        roles = ["primary", "secondary"] if identity in protocol["secondary_order"] else ["primary"]
        for role in roles:
            material = materializer.materialize(
                archives, item, refs[identity]["essential_facts"], role, runtime_facts=runtime_facts
            )
            inventory.append(material)
            packets.append(material["packet"])
    driver.save(batch / "report-inventory.json", inventory)
    driver.save(batch / "report-packets.json", packets)
    print(f"Prepared {len(packets)} packets for source review. No judging dispatched.")


def assess(batch=BATCH, pack=PACK, calibration_root=None):
    driver = helper("feature-003-latency-judge-20261118.py", "driver")
    calibration_root = calibration_root or batch / "calibration-clarified"
    judging = batch / "judging"
    cal_freeze = require_authorization(
        calibration_root / "approval.json", calibration_root / "freeze.json"
    )
    ref = Path(cal_freeze["private_control_expectations_path"])
    if driver.sha(ref) != cal_freeze["private_control_expectations_sha256"]:
        raise ValueError("Calibration reference changed")
    require_authorization(judging / "approval.json", judging / "freeze.json")
    calibration = dict(
        packets=driver.load(calibration_root / "packets.json"),
        ratings=ratings_map(driver.load(calibration_root / "ratings.json")),
        expectations=driver.load(ref),
    )
    result = aggregate(
        driver.load(judging / "packets.json"),
        ratings_map(driver.load(judging / "ratings.json")),
        driver.load(pack / "protocol.json")["quality_order"],
        calibration,
    )
    driver.save(batch / "quality-results.json", result)
    print(
        f"Passing reports {result['passing_reports']} / 8. Quality pass {result['quality_pass']}."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "assess"))
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--runtime-facts", action="store_true")
    parser.add_argument("--quality-only", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(
            args.batch, args.pack, runtime_facts=args.runtime_facts, quality_only=args.quality_only
        )
    else:
        assess(args.batch, args.pack, args.calibration)
