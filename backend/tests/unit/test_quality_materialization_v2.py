"""Source/prose binding checks only, not model report quality."""

import copy
import importlib.util
import json

import pytest

from fraudlens.investigation.models import ROOT


@pytest.fixture
def module():
    path = ROOT / "evidence/tasks/feature-003-materialize-quality-v2-20261118.py"
    spec = importlib.util.spec_from_file_location("test_only_materializer", path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


@pytest.fixture
def example():
    item = json.loads(
        (ROOT / "evals/investigation/acceptance-v2-20261118/inputs/cohort.json").read_text()
    )[0]
    evidence_id = "ev_" + "a" * 32

    def claim(text, kind="observation"):
        return dict(
            text=text, kind=kind, evidence_refs=[evidence_id], exact_assertions=[], quotes=[]
        )

    draft = dict(
        outcome="needs_information",
        summary=[claim("Amount is supplied.")],
        observed_facts=[claim("Amount is supplied.")],
        risk_indicators=[],
        alternative_explanations=[
            claim("A hypothetical alternative remains uncertain.", "hypothesis")
        ],
        missing_information=["Identity is unknown."],
        limitations=["Synthetic source; human decision."],
        recommended_checks=[claim("Review source; obtain authorization.", "procedure")],
        citations=[evidence_id],
    )
    archive = dict(
        context=item["context"],
        view=dict(run_id="inv_" + "a" * 32, state="needs_information", report=dict(draft=draft)),
        evidence=[
            dict(
                evidence_id=evidence_id,
                text="Authorized source text.",
                kind="case_fact",
                facts=[],
                returned_count=1,
                eligible_count=1,
                truncated=False,
                passage=None,
            )
        ],
    )
    return archive, item


def test_every_section_and_repeat_preserved_with_distinct_units(module, example):
    archive, item = example
    result = module.materialize(archive, item, ["Predeclared source obligation."])
    packet = result["packet"]
    duplicates = [u for u in packet["units"] if u["text"] == "Amount is supplied."]
    assert len(duplicates) == 2 and len({u["location"] for u in duplicates}) == 2
    assert "Identity is unknown." in packet["report"]["missing_information"]
    assert "Synthetic source; human decision." in packet["report"]["limitations"]
    assert "hypothetical alternative" in packet["report"]["alternative_explanations"]
    procedures = [u for u in packet["units"] if u["claim_kind"] == "procedure"]
    assert len(procedures) == 2
    assert result["review_required"] is True


def test_source_snapshot_never_discloses_raw_bank_account_or_gold(module, example):
    archive, item = example
    packet = module.materialize(archive, item, ["Source obligation."])["packet"]
    serialized = json.dumps(packet)
    assert item["context"]["source_payload"]["transaction"]["sender_account"] not in serialized
    assert "expected_missing_fields" not in serialized and "essential_facts" not in serialized


def test_changed_context_rejected_before_projection(module, example):
    archive, item = example
    archive = copy.deepcopy(archive)
    archive["context"]["source_payload"]["transaction"]["amount"] = "999999.00"
    with pytest.raises(ValueError, match="context"):
        module.materialize(archive, item, ["Source obligation."])


def test_foreign_report_citation_rejected(module, example):
    archive, item = example
    archive["view"]["report"]["draft"]["summary"][0]["evidence_refs"] = ["ev_" + "b" * 32]
    with pytest.raises(ValueError):
        module.materialize(archive, item, ["Source obligation."])


def test_absent_report_retains_failed_slot_without_inventing_prose(module, example):
    archive, item = example
    archive["view"]["state"] = "failed"
    archive["view"]["report"] = None
    packet = module.materialize(archive, item, ["Source obligation."])["packet"]
    assert packet["failed"] is True and all(not v for v in packet["report"].values())
    assert all(u["claim_kind"] == "essential_fact" for u in packet["units"])


def test_procedure_scope_provenance_preserved_without_source_reviewer_notes(module, example):
    archive, item = example
    e = archive["evidence"][0]
    e["kind"] = "procedure"
    document = {
        key: "test"
        for key in (
            "doc_id",
            "title",
            "origin_kind",
            "source_uri",
            "published_at",
            "unknown_date_reason",
            "retrieved_at",
            "jurisdiction",
            "version",
            "content_sha256",
            "applicability_notes",
            "reuse_terms",
        )
    }
    document.update(
        jurisdiction="HISTORICAL TEST JURISDICTION",
        version="scope-test-v1",
        reviewed_by="PRIVATE_SOURCE_REVIEWER_CANARY",
    )
    e["passage"] = dict(
        document=document, passage_id="p-test", section="Scope", corpus_version="corpus-test"
    )
    packet = module.materialize(archive, item, ["Source obligation."])["packet"]
    text = json.dumps(packet)
    assert "HISTORICAL TEST JURISDICTION" in text and "scope-test-v1" in text
    assert "PRIVATE_SOURCE_REVIEWER_CANARY" not in text


def test_opt_in_runtime_facts_include_observed_no_match_and_scope(module, example):
    archive, item = example
    archive["events"] = [
        dict(operation="dispatch_result", sequence=2, outcome="completed"),
        dict(
            operation="semantic_selection",
            sequence=2,
            policy_version="policy",
            selection=dict(verdict="insufficient", selected=[], reason="PRIVATE_REASON_CANARY"),
        ),
        dict(
            operation="semantic_selection",
            sequence=3,
            policy_version="policy",
            selection=dict(verdict="insufficient", selected=[]),
        ),
    ]
    legacy = module.materialize(archive, item, ["Source obligation."])["packet"]
    new = module.materialize(archive, item, ["Source obligation."], runtime_facts=True)["packet"]
    old_snapshot, snapshot = [json.loads(p["evidence"][-1]["text"]) for p in (legacy, new)]
    assert "procedure_selection_observations" not in old_snapshot
    assert snapshot["procedure_selection_observations"] == [
        dict(
            sequence=2,
            policy_version="policy",
            verdict="insufficient",
            selected_passage_ids=[],
            projected_search_status="no_match",
        )
    ]
    assert "PRIVATE_REASON_CANARY" not in json.dumps(new)
    assert "does not establish bank loss" in snapshot["source_scope"]["amount"]
    assert "read-only" in snapshot["source_scope"]["workflow"]
    assert new["report"] == legacy["report"] and new["units"] == legacy["units"]
