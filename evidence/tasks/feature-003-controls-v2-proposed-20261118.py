"""Offline corrective control draft after v4 calibration; NOT new model evidence.

Keep original controls/gold/ratings unchanged. This candidate needs team review,
new version/freeze and prospective validation before use. No provider imports.
"""

import json

from fraudlens.investigation.judging_v4 import project_packet
from fraudlens.investigation.models import ROOT, digest


def main():
    source = ROOT / "evals/investigation/report-quality-v4"
    target = ROOT / "evals/investigation/report-quality-v4-controls-v2-proposed"
    if target.exists():
        raise ValueError("Never overwrite a proposed/frozen pack")
    original = json.loads((source / "inputs/controls.json").read_text(encoding="utf-8"))
    old_expected = json.loads((source / "reference/expectations.json").read_text(encoding="utf-8"))
    controls, expectations = [], []
    amount = "Amount: 2361.47 EUR."
    for old, gold in zip(original, old_expected, strict=True):
        identity = old["scenario_id"]
        report = dict(old["report"])
        report = {
            key: value.replace("1250.00", "2361.47").replace("Alice", "Nora")
            for key, value in report.items()
        }
        tested = report["summary"]
        # Isolate the intended unknown/disclosure predicate: known amount remains
        # explicit in every control, including intentional invention negatives.
        report["summary"] = tested if tested == amount else amount + " " + tested
        evidence_id = "ev_control_v2_" + identity.lower()
        text = old["evidence"][0]["text"].replace("1250.00", "2361.47")
        units, expected_units = [], {}

        def add(key, kind, value, location, judgment, critical=False):
            units.append(
                dict(
                    unit_id=key,
                    claim_kind=kind,
                    text=value,
                    location=location,
                    evidence_refs=[evidence_id],
                )
            )
            expected_units[key] = dict(judgment=judgment, critical_error=critical)

        add("o_amount", "observation", amount, "/summary", "supported")
        invented = identity in ("C3", "C4", "C6")
        if tested != amount:
            add(
                "o_tested",
                "observation",
                tested,
                "/summary",
                "unsupported" if invented else "supported",
                invented,
            )
        # Every repeated assertion is explicitly enumerated, including bad prose.
        add(
            "o_repeat",
            "observation",
            report["observations"],
            "/observations",
            "unsupported" if invented else "supported",
            invented,
        )
        for index, sentence in enumerate(report["missing_information"].split(". ")):
            sentence = sentence.strip()
            if sentence:
                add(
                    f"o_missing_{index}",
                    "observation",
                    sentence,
                    "/missing_information",
                    "supported",
                )
        for index, sentence in enumerate(report["limitations"].replace("; ", ". ").split(". ")):
            sentence = sentence.strip()
            if sentence:
                add(f"o_limit_{index}", "observation", sentence, "/limitations", "supported")
        add("e_amount", "essential_fact", amount, "", "present")
        obligation = old["units"][1]["text"].replace("1250.00", "2361.47")
        if obligation != amount:
            add("e_unknown", "essential_fact", obligation, "", gold["units"]["e1"]["judgment"])
        control = dict(
            scenario_id=identity,
            role="calibration",
            failed=False,
            report=report,
            evidence=[dict(evidence_id=evidence_id, text=text)],
            units=units,
        )
        project_packet(control)
        controls.append(control)
        expectations.append(
            dict(
                scenario_id=identity,
                checks=gold["checks"],
                critical_error=gold["critical_error"],
                units=expected_units,
                no_additional_issues=True,
            )
        )
    (target / "inputs").mkdir(parents=True)
    (target / "reference").mkdir()
    for path, value in (
        (target / "inputs/controls.json", controls),
        (target / "reference/expectations.json", expectations),
    ):
        with path.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    with (target / "proposal.json").open("x", encoding="utf-8") as stream:
        json.dump(
            dict(
                status="proposed_after_unblinding_NOT_approved_NOT_executed",
                method="Same v4 checks/rubric; known facts explicit; all repeated claims enumerated",
                limitations="Author-proposed corrective draft, not independent calibration/holdout",
                software_checks="6 public projector checks; private unit inventories bound",
                original_expectations_unchanged=True,
                actual_provider_calls=0,
                input_sha256=digest(controls),
                private_expectations_sha256=digest(expectations),
            ),
            stream,
            indent=2,
        )
    print(json.dumps(dict(proposed_controls=6, model_calls=0, team_review="required")))


if __name__ == "__main__":
    main()
