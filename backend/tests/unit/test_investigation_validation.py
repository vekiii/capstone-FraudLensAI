"""Exact source binding is separate from the truth of natural-language claims."""

import copy
import hashlib

import pytest

from fraudlens.investigation.context import CaseContextReader
from fraudlens.investigation.knowledge import stage
from fraudlens.investigation.models import canonical, digest, validate
from fraudlens.investigation.tools import content_digest
from fraudlens.investigation.validation import validate_report


def claim(ref, kind="observation", text="Iznos je preuzet iz izvora."):
    return dict(text=text, kind=kind, evidence_refs=[ref], exact_assertions=[], quotes=[])


@pytest.fixture
def pack(knowledge_factory):
    context = CaseContextReader().resolve("CASE-001", "fixture", None)
    attempt = "att_" + "a" * 32
    case = dict(
        contract_version=1,
        evidence_id="ev_" + "b" * 32,
        attempt_id=attempt,
        context_revision=context["context_revision"],
        kind="case_fact",
        text="Observed amount 9800.00 EUR; fixture score, not calibrated probability.",
        facts=[
            dict(path="transaction.amount", value="9800.00"),
            dict(path="transaction.currency", value="EUR"),
            dict(path="assessment.source", value="fixture"),
        ],
        passage=None,
        history=None,
        returned_count=1,
        eligible_count=1,
        truncated=False,
        content_sha256="0" * 64,
        created_at="2026-11-14T10:00:00Z",
    )
    case["content_sha256"] = content_digest(case)
    passage = stage(knowledge_factory())["passages"][0]
    procedure = {
        **copy.deepcopy(case),
        "evidence_id": "ev_" + "c" * 32,
        "kind": "procedure",
        "text": passage["text"],
        "facts": [],
        "passage": passage,
    }
    procedure["content_sha256"] = content_digest(procedure)
    fact = claim(case["evidence_id"])
    fact["exact_assertions"] = [
        dict(evidence_ref=case["evidence_id"], path="transaction.amount", value="9800.00")
    ]
    fact["quotes"] = [dict(evidence_ref=case["evidence_id"], text="9800.00 EUR")]
    draft = dict(
        outcome="ready_for_review",
        summary=[copy.deepcopy(fact)],
        observed_facts=[fact],
        risk_indicators=[],
        alternative_explanations=[],
        missing_information=["Zanimanje i poreklo sredstava nisu dostupni."],
        recommended_checks=[claim(procedure["evidence_id"], "procedure")],
        limitations=["Sinteticki podaci; skor nije kalibrisana verovatnoca."],
        citations=[case["evidence_id"], procedure["evidence_id"]],
    )
    return context, attempt, [case, procedure], draft


def checked(pack):
    ctx, attempt, evidence, draft = pack
    return validate_report(
        draft,
        evidence,
        attempt,
        ctx["context_revision"],
        ctx,
        evidence[1]["passage"]["corpus_version"],
    )


def test_bound_report_is_immutable_and_explicitly_not_semantically_reviewed(pack):
    original = copy.deepcopy(pack[3])
    report = checked(pack)
    validate("Report", report)
    assert report["semantic_review"] == "not_reviewed"
    assert report["validation"] == "schema_reference_passed"
    assert report["report_id"] == digest(
        dict(attempt_id=pack[1], context_revision=pack[0]["context_revision"], draft=original)
    )
    assert pack[3] == original and report["draft"] is not pack[3]


@pytest.mark.parametrize(
    "change",
    [
        "unknown",
        "other-attempt",
        "other-context",
        "missing",
        "duplicate-id",
        "changed-hash",
        "wrong-corpus",
        "changed-passage",
    ],
)
def test_unknown_or_mismatched_evidence_is_rejected(pack, change):
    ctx, attempt, evidence, draft = pack
    if change == "unknown":
        draft["citations"].append("ev_" + "d" * 32)
    if change == "other-attempt":
        evidence[0]["attempt_id"] = "att_" + "d" * 32
    if change == "other-context":
        evidence[0]["context_revision"] = "d" * 64
    if change == "missing":
        evidence.pop(0)
    if change == "duplicate-id":
        evidence.append(copy.deepcopy(evidence[0]))
    if change == "changed-hash":
        evidence[0]["text"] += " changed"
    if change == "wrong-corpus":
        evidence[1]["passage"]["corpus_version"] = "corpus_" + "d" * 64
    if change == "changed-passage":
        evidence[1]["passage"]["text"] += " changed"
        evidence[1]["content_sha256"] = content_digest(evidence[1])
    with pytest.raises(ValueError):
        validate_report(
            draft,
            evidence,
            attempt,
            ctx["context_revision"],
            ctx,
            "corpus_" + "e" * 64 if change == "wrong-corpus" else None,
        )


@pytest.mark.parametrize("change", ["amount", "path", "quote", "assertion-owner", "quote-owner"])
def test_changed_structured_assertions_and_quotes_are_rejected(pack, change):
    item = pack[3]["observed_facts"][0]
    if change == "amount":
        item["exact_assertions"][0]["value"] = "9801.00"
    if change == "path":
        item["exact_assertions"][0]["path"] = "transaction.source_of_funds"
    if change == "quote":
        item["quotes"][0]["text"] = "9801.00 EUR"
    if change == "assertion-owner":
        item["exact_assertions"][0]["evidence_ref"] = pack[2][1]["evidence_id"]
    if change == "quote-owner":
        item["quotes"][0]["evidence_ref"] = pack[2][1]["evidence_id"]
    with pytest.raises(ValueError):
        checked(pack)


@pytest.mark.parametrize(
    "section,kind,source",
    [
        ("observed_facts", "observation", 1),
        ("observed_facts", "hypothesis", 0),
        ("recommended_checks", "procedure", 0),
        ("recommended_checks", "observation", 0),
        ("alternative_explanations", "hypothesis", 1),
    ],
)
def test_claim_and_evidence_kinds_cannot_be_confused(pack, section, kind, source):
    pack[3][section] = [claim(pack[2][source]["evidence_id"], kind)]
    with pytest.raises(ValueError):
        checked(pack)


@pytest.mark.parametrize(
    "change", ["missing-field", "extra-field", "empty-ready", "no-limitations"]
)
def test_required_shape_and_source_limitations(pack, change):
    draft = pack[3]
    if change == "missing-field":
        del draft["missing_information"]
    if change == "extra-field":
        draft["actor"] = "model-chosen"
    if change == "empty-ready":
        draft["observed_facts"] = []
    if change == "no-limitations":
        draft["limitations"] = []
    with pytest.raises(ValueError):
        checked(pack)


def test_valid_limitation_only_draft_without_fabricated_facts(pack):
    ctx, attempt, _, _ = pack
    draft = dict(
        outcome="needs_information",
        summary=[],
        observed_facts=[],
        risk_indicators=[],
        alternative_explanations=[],
        missing_information=["Nema dokaza."],
        recommended_checks=[],
        limitations=["Nema dovoljno podataka za koristan zakljucak."],
        citations=[],
    )
    result = validate_report(draft, [], attempt, ctx["context_revision"], ctx)
    assert result["draft"]["outcome"] == "needs_information"


def test_hypothesis_requires_case_premises_and_remains_typed(pack):
    pack[3]["alternative_explanations"] = [
        claim(
            pack[2][0]["evidence_id"],
            "hypothesis",
            "Moguce alternativno objasnjenje; nije utvrdjena cinjenica.",
        )
    ]
    assert checked(pack)["draft"]["alternative_explanations"][0]["kind"] == "hypothesis"


def test_valid_reference_can_still_have_a_false_natural_language_interpretation(pack):
    # Deliberate semantic defect: deterministic schema/source checks cannot prove prose.
    pack[3]["observed_facts"][0]["text"] = "Ovaj iznos dokazuje da je klijent kriv."
    report = checked(pack)
    assert report["semantic_review"] == "not_reviewed"
    assert report["validation"] == "schema_reference_passed"


def test_procedure_text_and_digest_are_preserved(pack):
    item = pack[2][1]
    assert hashlib.sha256(item["text"].encode()).hexdigest() == item["passage"]["content_sha256"]
    report = checked(pack)
    assert canonical(report["draft"]) == canonical(pack[3])
