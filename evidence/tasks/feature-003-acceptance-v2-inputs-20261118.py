"""Author a prospective shared quality/timing cohort; no provider or old ratings."""

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
    target = ROOT / "evals/investigation/acceptance-v2-20261118"
    accepted = ROOT / "evals/investigation/report-quality-v4-controls-v2"
    if target.exists() or accepted.exists():
        raise ValueError("New prospective pack paths required")
    helper = ROOT / "evidence/tasks/feature-003-t101-t102-prepare-20261118.py"
    spec = importlib.util.spec_from_file_location("source_only_authoring_v1", helper)
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    definitions = [
        ("available", "3259.61", "EUR", 0.58),
        ("unavailable", "87.32", "USD", 0.33),
        ("mixed", "926.74", "GBP", 0.64),
        ("unavailable", "168.95", "EUR", 0.37),
        ("available", "13247.86", "USD", 0.88),
        ("available", "24.69", "GBP", 0.21),
        ("unavailable", "4837.52", "EUR", 0.76),
        ("mixed", "7294.13", "USD", 0.83),
    ]
    inputs, references = [], []
    for position, (history, amount, currency, score) in enumerate(definitions, 1):
        item, reference = author.authored(
            f"RUN2-{position:02}",
            940 + position,
            amount,
            currency,
            score,
            history,
            author.NO_GUIDANCE if position == 4 else author.QUESTION,
        )
        inputs.append(item)
        references.append(reference)
    order = [i["id"] for i in inputs]
    save(target / "inputs/cohort.json", inputs)
    save(
        target / "reference/source-obligations.json",
        dict(
            provenance="Pre-generation source-derived obligations; no prediction/report/grade inputs",
            custodian="Codex offline automation, source script/version pinned before generation",
            items=references,
        ),
    )
    queries = [
        "What should an analyst record when customer records are absent?",
        "Who may approve a final case disposition?",
        "How can the original evidence version be traced?",
        "Which limitations apply to simulated transaction examples?",
        "Does an elevated score establish wrongdoing?",
        "What can be concluded if funds origin is undocumented?",
        "Can missing account records be reported as no activity?",
        "How should plausible alternative explanations be qualified?",
        "What customer information should be excluded from a public report?",
        "How should an unresolved source gap affect a conclusion?",
        "What provenance identifies a cited procedure?",
        "Does an alert amount represent a bank loss?",
        "Can an older procedure establish today's legal requirement?",
        "What authorization is needed for escalation?",
        "What should the report preserve when sources conflict?",
        "How can an analyst express uncertainty without inventing facts?",
        "What should happen when the library lacks applicable guidance?",
        "Should balances in different currencies be added together?",
        "What exact current Portuguese deadline applies to this case?",
        "Which official Portuguese filing fee applies today?",
    ]
    save(
        target / "inputs/search.json",
        [dict(id=f"SEARCH2-{n:02}", language="en", query=q) for n, q in enumerate(queries, 1)],
    )
    roles = dict(
        quality_order=order,
        timing_order=order[:5],
        secondary_order=[order[i - 1] for i in (2, 3, 4, 6, 8)],
        sample_overlap="Timing five are prospectively the FIRST five of quality eight; "
        "same saved reports, no selection after outputs; correlated samples disclosed.",
        timing_genres=[
            "available_history",
            "unavailable_history",
            "mixed_currency",
            "no_adequate_procedure",
            "elevated_missing_customer_facts",
        ],
    )
    save(target / "reference/roles.json", roles)
    save(
        target / "protocol.json",
        dict(
            version=2,
            status="source_authoring_before_execution",
            semantic_profile="v7",
            source_mode="authored_synthetic_fixture_not_ML_evaluation",
            **roles,
            prior_actual_requests=56,
            maximum_total_requests=155,
            prospective_caps=dict(
                calibration=6,
                first_five_shared_generation=40,
                last_three_quality_generation=24,
                primary_secondary=13,
            ),
            conservative_full_maximum=139,
            remaining_retry_reserve=16,
            criteria="Unchanged v4 exact6/6, 7/8 quality, .90/.80, zero critical; "
            "timing4/5<=90, all5<=120, local20 rank19p95<=2",
            original_8_quality_slots="Never generated; retained unexecuted after original calibration failure",
            historical_results="All original failed/unknown outcomes retained, no regrading",
            source_authoring_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            source_input_sha256={i["id"]: digest(i) for i in inputs},
        ),
    )
    proposed = ROOT / "evals/investigation/report-quality-v4-controls-v2-proposed"
    for name in ("inputs/controls.json", "reference/expectations.json"):
        destination = accepted / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write((proposed / name).read_bytes())
    save(
        accepted / "acceptance.json",
        dict(
            user_decision="Prihvatam doradu unutar T101/T102",
            version=2,
            controls_source="Exact reviewed corrective draft; no expected-label edits",
            actual_calls_before_use=0,
            old_calibration_result="2/6 preserved unchanged",
        ),
    )
    print(
        json.dumps(
            dict(
                new_quality_cases=8,
                shared_timing_cases=5,
                local_queries=20,
                accepted_controls=6,
                actual_provider_calls=0,
                max_future_total=139,
            )
        )
    )


if __name__ == "__main__":
    main()
