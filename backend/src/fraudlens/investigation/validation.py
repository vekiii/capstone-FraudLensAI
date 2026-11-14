"""Report-validation boundary; semantic faithfulness requires human review."""

import hashlib
from datetime import UTC, datetime

from fraudlens.investigation.models import digest, validate
from fraudlens.investigation.tools import content_digest

SECTIONS = (
    "summary",
    "observed_facts",
    "risk_indicators",
    "alternative_explanations",
    "recommended_checks",
)


def _evidence(items, attempt_id, context_revision, corpus_version):
    by_id = {}
    for item in items:
        item = validate("Evidence", item)
        if (
            item["attempt_id"] != attempt_id
            or item["context_revision"] != context_revision
            or item["evidence_id"] in by_id
            or item["content_sha256"] != content_digest(item)
        ):
            raise ValueError("evidence_binding_invalid")
        if len({fact["path"] for fact in item["facts"]}) != len(item["facts"]):
            raise ValueError("ambiguous_evidence_facts")
        if item["kind"] == "procedure":
            passage = item["passage"]
            if (
                passage is None
                or passage["text"] != item["text"]
                or passage["content_sha256"] != hashlib.sha256(item["text"].encode()).hexdigest()
                or (corpus_version is not None and passage["corpus_version"] != corpus_version)
                or item["history"] is not None
            ):
                raise ValueError("procedure_binding_invalid")
        elif item["passage"] is not None:
            raise ValueError("wrong_evidence_kind")
        if item["kind"] == "history":
            if item["history"] is None or item["returned_count"] > 50:
                raise ValueError("history_binding_invalid")
            validate("History", item["history"])
        elif item["history"] is not None:
            raise ValueError("wrong_evidence_kind")
        by_id[item["evidence_id"]] = item
    return by_id


def _claim(claim, section, sources):
    refs = claim["evidence_refs"]
    if len(set(refs)) != len(refs) or not set(refs) <= sources.keys():
        raise ValueError("unknown_or_duplicate_evidence_reference")
    kinds = {sources[ref]["kind"] for ref in refs}
    kind = claim["kind"]
    if section == "observed_facts" and kind != "observation":
        raise ValueError("observation_required")
    if section == "recommended_checks" and kind != "procedure":
        raise ValueError("procedure_required")
    if section == "alternative_explanations" and kind != "hypothesis":
        raise ValueError("hypothesis_required")
    if (
        kind == "observation"
        and not kinds <= {"case_fact", "history"}
        or kind == "procedure"
        and "procedure" not in kinds
        or kind == "hypothesis"
        and not kinds.intersection({"case_fact", "history"})
    ):
        raise ValueError("claim_evidence_kind_mismatch")
    for assertion in claim["exact_assertions"]:
        ref = assertion["evidence_ref"]
        if ref not in refs:
            raise ValueError("assertion_scope_mismatch")
        values = {fact["path"]: fact["value"] for fact in sources[ref]["facts"]}
        if assertion["path"] not in values or values[assertion["path"]] != assertion["value"]:
            raise ValueError("exact_assertion_mismatch")
    for quote in claim["quotes"]:
        if (
            quote["evidence_ref"] not in refs
            or quote["text"] not in sources[quote["evidence_ref"]]["text"]
        ):
            raise ValueError("exact_quote_mismatch")
    return set(refs)


def validate_report(
    draft, evidence, attempt_id, context_revision, context=None, corpus_version=None
):
    draft = validate("ReportDraft", draft)
    validate("AttemptId", attempt_id)
    validate("Digest", context_revision)
    if context is not None:
        context = validate("InvestigationContext", context)
        if context["context_revision"] != context_revision:
            raise ValueError("context_binding_invalid")
    sources = _evidence(evidence, attempt_id, context_revision, corpus_version)
    used = set()
    for section in SECTIONS:
        for claim in draft[section]:
            used.update(_claim(claim, section, sources))
    if set(draft["citations"]) != used:
        raise ValueError("citation_set_mismatch")
    # Require disclosure when the evidence has known limitations. The truth of
    # its wording is a separate human semantic check, never a keyword guarantee.
    limited = context is not None and (
        context["source_mode"] == "fixture" or context["history"]["coverage"] != "full"
    )
    limited = limited or any(
        fact["path"] in ("assessment.source", "assessment.explanation.status")
        and fact["value"] in ("fixture", "rules", "partial", "unavailable")
        for item in sources.values()
        for fact in item["facts"]
    )
    if limited and not draft["limitations"]:
        raise ValueError("source_limitations_required")
    content = dict(attempt_id=attempt_id, context_revision=context_revision, draft=draft)
    return validate(
        "Report",
        dict(
            report_id=digest(content),
            attempt_id=attempt_id,
            context_revision=context_revision,
            created_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            validation="schema_reference_passed",
            semantic_review="not_reviewed",
            draft=draft,
        ),
    )
