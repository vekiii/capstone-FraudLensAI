"""Verify the approved local T098 index using the existing read-only readers."""

import json
import subprocess
from contextlib import closing
from pathlib import Path

from fraudlens.data_contracts import CaseDetailV2
from fraudlens.data_store import RunStore
from fraudlens.investigation.dataset import DatasetReader
from fraudlens.investigation.history_index import file_digest

root = Path("data/processed/feature-003-t098-20261118").resolve()
manifest = json.loads(subprocess.check_output([
    "git", "show",
    "62f099134c57a3129d28f333545a1398f6e812e4:evidence/tasks/feature-003-t098-transfer-20261118.json",
]))
originals = {}
for name in ("source.sqlite", "model-bounded.sqlite", "history-index.sqlite"):
    expected = next(item for item in manifest["files"] if item["name"] == name)
    digest = file_digest(root / name)
    assert digest == expected["sha256"] == expected["expected"], name
    originals[name] = digest

index = root / "history-index-feature006-local.sqlite"
source = root / "source.sqlite"
model = root / "model-bounded.sqlite"
result = dict(transferred_digests=originals, local_index_sha256=file_digest(index), cases=[])
reader = DatasetReader(model, source, "model", history_index=index,
                       history_index_sha256=result["local_index_sha256"])
with closing(RunStore(model, read_only=True)) as store:
    active = store.active_metadata("model")
    assert active["run_id"] == "run_boosted_candidate_smoke"
    run = active["run_id"]
    for case in ("C6c481448f7d25af15beea1309f44ee58", "C4af2f03a9d1bca5fc14d76e05af12140"):
        detail = CaseDetailV2.model_validate(store.detail_active("model", run, case)).model_dump(mode="json")
        context = reader.resolve(case, run)
        assert context["source_payload"] == detail
        assert context["history"]["availability"] == "available"
        assert context["dataset_version"] == active["dataset_version"]
        history = reader.read(context, "sender", limit=1)
        assert history["availability"] == "available"
        assert len(history["events"]) == history["returned_count"] <= 1
        risk = detail["risk_assessment"]
        assert risk["scorer_version"] == active["scorer_version"] and risk["score_source"] == "model"
        result["cases"].append(dict(
            case_id=case, transaction_id=detail["transaction"]["transaction_id"],
            snapshot_ref=run, dataset_version=context["dataset_version"],
            context_revision=context["context_revision"], score=risk["score"],
            score_source=risk["score_source"], score_kind=risk["score_kind"],
            scorer_version=risk["scorer_version"],
            history={key: context["history"][key] for key in ("availability", "coverage")},
            sender_history_returned=history["returned_count"],
        ))
metadata = reader._index().metadata
assert metadata["source_sha256"] == originals["source.sqlite"]
assert metadata["dataset_version"] == active["dataset_version"]
assert metadata["status"] == "complete" and metadata["row_count"] == 5078345
result["index_rows"] = metadata["row_count"]
result["status"] = "PASS"
print(json.dumps(result, indent=2))
