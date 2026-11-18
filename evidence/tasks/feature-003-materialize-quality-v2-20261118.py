"""Offline report/unit materialization. Custodian review required before judging."""

import re

from fraudlens.investigation.context import HistoryReader, outbound_context
from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.judging_v4 import POLICY, SECTIONS, project_packet
from fraudlens.investigation.models import canonical, digest, validate
from fraudlens.investigation.tools import provider_evidence

HISTORY_POLICY = (
    "Available history uses the recorded cutoff minus seven days as an inclusive start; "
    "the focal minute is an exclusive upper bound. The focal transaction, same-minute "
    "and future events are excluded. Totals are computed separately per currency. "
    "Unavailable history does not establish that no events occurred."
)


def clauses(text):
    # Exact spans retained; a custodian must inspect compound/shared predicates
    # and recommendations in free-text sections before freezing the final pack.
    return [
        v.strip() for v in re.split(r"(?<=;)\s+|(?<=[.!?])\s+(?=[A-ZČĆŠŽĐ])", text) if v.strip()
    ]


def runtime_source_facts(archive):
    """Allowlisted outcomes from completed selections, excluding model explanations."""
    events = archive.get("events", [])
    completed = {
        event["sequence"]
        for event in events
        if event["operation"] == "dispatch_result" and event["outcome"] == "completed"
    }
    selections = []
    for event in events:
        if event["operation"] != "semantic_selection" or event["sequence"] not in completed:
            continue
        selection = event["selection"]
        selections.append(
            dict(
                sequence=event["sequence"],
                policy_version=event["policy_version"],
                verdict=selection["verdict"],
                selected_passage_ids=[row["passage_id"] for row in selection["selected"]],
            )
        )
    return dict(
        procedure_selection_observations=selections,
        source_scope=dict(
            amount="The case amount describes the synthetic transfer. It does not establish bank loss.",
            workflow="Investigation tools are read-only. The AI draft does not execute case actions. The human analyst decides.",
        ),
    )


def materialize(archive, item, source_obligations, role="primary", *, runtime_facts=False):
    item = input_only(item)
    context = item["context"]
    if archive["context"] != context:
        raise ValueError("Changed source context")
    report = {key: "" for key in SECTIONS}
    units, inventory = [], []
    evidence = [
        dict(
            evidence_id=e["evidence_id"],
            text=canonical(provider_evidence(e)).decode(),
        )
        for e in archive["evidence"]
    ]
    source_id = "source_" + context["context_revision"][:16]
    reader = HistoryReader(**item["history_fixture"])
    histories = {}
    for side in ("sender", "receiver"):
        history = reader.read(context, side)
        histories[side] = {key: value for key, value in history.items() if key != "events"}
        histories[side]["events"] = [
            {
                key: value
                for key, value in event.items()
                if key in ("transaction_id", "occurred_at", "amount", "currency")
            }
            for event in history["events"]
        ]
    snapshot = dict(
        context=outbound_context(context, archive["view"]["run_id"]),
        history=histories,
        history_policy=HISTORY_POLICY,
        policy=POLICY,
        tool_trace=archive["view"].get("trace", []),
    )
    if runtime_facts:
        snapshot.update(runtime_source_facts(archive))
    evidence.append(dict(evidence_id=source_id, text=canonical(snapshot).decode()))
    runtime_report = archive["view"].get("report")
    draft = runtime_report["draft"] if runtime_report else None
    if draft is not None:
        validate("ReportDraft", draft)
        mapping = (
            "summary",
            "observed_facts",
            "risk_indicators",
            "alternative_explanations",
            "missing_information",
            "limitations",
            "recommended_checks",
        )
        for field in mapping:
            target = "observations" if field in ("observed_facts", "risk_indicators") else field
            for index, raw in enumerate(draft[field]):
                claim = (
                    raw
                    if isinstance(raw, dict)
                    else dict(text=raw, kind="observation", evidence_refs=[source_id])
                )
                text = claim["text"]
                report[target] += ("\n" if report[target] else "") + text
                kind = (
                    "procedure"
                    if field == "recommended_checks" or claim["kind"] == "procedure"
                    else "observation"
                )
                for atom in clauses(text):
                    identity = f"u{len(units) + 1:03}"
                    units.append(
                        dict(
                            unit_id=identity,
                            claim_kind=kind,
                            text=atom,
                            location="/" + target,
                            evidence_refs=claim["evidence_refs"],
                        )
                    )
                    inventory.append(
                        dict(
                            unit_id=identity,
                            original_field=field,
                            original_index=index,
                            original_kind=claim["kind"],
                            source_text=text,
                        )
                    )
    for index, obligation in enumerate(source_obligations, 1):
        if not isinstance(obligation, str) or not obligation.strip():
            raise ValueError("Predeclared source obligation required")
        units.append(
            dict(
                unit_id=f"e{index:03}",
                claim_kind="essential_fact",
                text=obligation,
                location="",
                evidence_refs=[source_id],
            )
        )
    packet = project_packet(
        dict(
            scenario_id=item["id"],
            role=role,
            failed=draft is None,
            report=report,
            evidence=evidence,
            units=units,
        )
    )
    return dict(
        packet=packet,
        review_required=True,
        inventory=inventory,
        original_draft_sha256=digest(draft),
        source_input_sha256=digest(item),
        note="Exact prose/initial clause inventory only; no semantic truth or quality assessed",
    )
