"""Fresh45s shared8/5 successor; no reuse of exposed RUN2 outcomes as acceptance."""

import hashlib
import importlib.util
import json
from pathlib import Path

from fraudlens.investigation.models import ROOT, digest


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def main():
    target = ROOT / "evals/investigation/acceptance-v3-20261118"
    if target.exists():
        raise ValueError("Never overwrite prospective input sources")
    helper = ROOT / "evidence/tasks/feature-003-t101-t102-prepare-20261118.py"
    spec = importlib.util.spec_from_file_location("source_only_authoring_v3", helper)
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    definitions = [
        ("available", "3478.26", "EUR", 0.59),
        ("unavailable", "96.57", "USD", 0.35),
        ("mixed", "1037.84", "GBP", 0.67),
        ("unavailable", "174.62", "EUR", 0.41),
        ("available", "14628.39", "USD", 0.92),
        ("available", "31.78", "GBP", 0.23),
        ("unavailable", "5126.93", "EUR", 0.78),
        ("mixed", "7839.54", "USD", 0.85),
    ]
    inputs, refs = [], []
    for index, (history, amount, currency, score) in enumerate(definitions, 1):
        item, ref = author.authored(
            f"RUN3-{index:02}",
            960 + index,
            amount,
            currency,
            score,
            history,
            author.NO_GUIDANCE if index == 4 else author.QUESTION,
        )
        inputs.append(item)
        refs.append(ref)
    roles = dict(
        quality_order=[v["id"] for v in inputs],
        timing_order=[v["id"] for v in inputs[:5]],
        secondary_order=[inputs[i - 1]["id"] for i in (2, 3, 4, 6, 8)],
        sample_overlap="FIRST five of quality eight, fixed BEFORE outputs; correlated samples",
    )
    save(target / "inputs/cohort.json", inputs)
    save(
        target / "reference/source-obligations.json",
        dict(
            provenance="Source-only obligations fixed before generation; no outcome labels in runtime",
            custodian="Codex offline automation; not independent-human review",
            items=refs,
        ),
    )
    save(target / "reference/roles.json", roles)
    queries = [
        "How is a missing customer fact documented in an investigation?",
        "Can an automated draft make the final analyst decision?",
        "What binds a citation to its historical source version?",
        "What should a report disclose about authored fixture data?",
        "Can a risk indicator be interpreted as evidence of guilt?",
        "How should undocumented funds origin affect the report?",
        "Does unavailable transaction history establish inactivity?",
        "How should a report distinguish an explanation from an established fact?",
        "What limits apply to sharing customer investigation details?",
        "How should missing evidence appear in the final draft?",
        "Which metadata identifies the origin of a procedure?",
        "Is a synthetic transfer amount evidence of financial loss?",
        "Does simulated guidance establish current local law?",
        "Who authorizes account intervention and case escalation?",
        "How can conflicting source statements be disclosed?",
        "What limits an investigation based on partial evidence?",
        "How should the absence of an applicable procedure be reported?",
        "What supports totals involving different currencies?",
        "Which current Portuguese statutory reporting date applies here?",
        "How much is the exact official Portugal case submission charge?",
    ]
    save(
        target / "inputs/search.json",
        [dict(id=f"SEARCH3-{i:02}", language="en", query=q) for i, q in enumerate(queries, 1)],
    )
    save(
        target / "protocol.json",
        dict(
            version=3,
            semantic_profile="v7",
            request_timeout_seconds=45,
            semantic_timeout_seconds=30,
            total_timeout_seconds=120,
            useful_target_seconds=90,
            **roles,
            source_mode="authored_synthetic_fixture_not_ML_evaluation",
            prior_actual_requests=68,
            user_request45_decision="Da, novi profil sa 45s",
            overall_cap=155,
            prospective_caps=dict(
                shared_five_generation=40, quality_tail_generation=24, primary_secondary=13
            ),
            conservative_full_maximum=145,
            operational_retry_reserve=10,
            calibration="Reviewed controls-v2 exact6/6; judge payload/model/rubric unchanged by generator45s",
            historical_results="All prior controls and failed2/5 and RUN2-01 retained; no prior-slot replacement",
            source_input_sha256={v["id"]: digest(v) for v in inputs},
            authoring_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        ),
    )
    print(
        json.dumps(
            dict(fresh_cases=8, shared_timing=5, fresh_local_queries=20, new_provider_calls=0)
        )
    )


if __name__ == "__main__":
    main()
