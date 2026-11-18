"""OFFLINE fresh input authoring. No provider imports, training or old-run replay.

Creates only new files. Run once from repo root with backend/src on PYTHONPATH.
References are custodian-only source obligations, never generation inputs.
"""

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta
from importlib.metadata import version

from fraudlens.investigation.context import HistoryReader, outbound_context
from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT, context_digest, digest, validate
from fraudlens.investigation.retrieval_semantic_v6 import policy_identity
from fraudlens.investigation.settings import load_settings

PACK = ROOT / "evals/investigation/acceptance-v1-20261118"
LOCAL = ROOT / "evals/results/feature-003/acceptance-preparation-20261118"
QUESTION = "Review available transaction evidence, missing facts and human review authority."
NO_GUIDANCE = "What is the exact current statutory filing deadline for this transfer in Portugal?"


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authored(identity, number, amount, currency, score, history_kind, question=QUESTION):
    """Create from source literals, without reading any prior report or reference."""
    at = datetime.fromisoformat("2026-11-18T09:17:43+00:00") + timedelta(minutes=number % 100)

    def stamp(value):
        return value.isoformat().replace("+00:00", "Z")

    case, txid = f"CASE-{number}", f"TX-{number}"
    tx = dict(
        transaction_id=txid,
        occurred_at=stamp(at),
        amount=amount,
        currency=currency,
        sender_account=f"AUTHORED-S:{identity}",
        receiver_account=f"AUTHORED-R:{identity}",
    )
    explanation = (
        "Authored synthetic fixture illustration; not ML inference, calibrated "
        "probability, guilt or a legal finding. Review question: " + question
    )
    risk = dict(
        transaction_id=txid,
        score=score,
        source="fixture",
        scorer_version="fixture-v1",
        scored_at=stamp(at + timedelta(seconds=11)),
        explanation=explanation,
    )
    history = dict(
        availability="unavailable",
        coverage="unavailable",
        cutoff=None,
        start=None,
        lookback_days=7,
        view_scope="authored_fixture",
        reason="No historical records supplied for either account.",
    )
    accounts, events = {}, []
    if history_kind != "unavailable":
        history.update(
            availability="available",
            coverage="incomplete",
            cutoff=stamp(at),
            start=stamp(at - timedelta(days=7)),
            reason="Authored partial history only; not a complete account record.",
        )
        accounts[case] = {"sender": dict(bank="AUTHORED-S", account=identity + "-S")}
        event_currency = "USD" if currency != "USD" else "EUR"
        for offset, value, unit in (
            (2, "83.47", currency),
            (1, "29.61", event_currency if history_kind == "mixed" else currency),
        ):
            events.append(
                dict(
                    transaction_id=f"TX-{number - offset * 100}",
                    occurred_at=stamp(at - timedelta(days=offset)),
                    amount=value,
                    currency=unit,
                    **accounts[case]["sender"],
                )
            )
        if history_kind == "available":
            accounts[case]["receiver"] = dict(bank="AUTHORED-R", account=identity + "-R")
            events.append(
                dict(
                    transaction_id=f"TX-{number - 300}",
                    occurred_at=stamp(at - timedelta(hours=3)),
                    amount="41.92",
                    currency=currency,
                    **accounts[case]["receiver"],
                )
            )
        # Both same-focal-minute and future events must be excluded by HistoryReader.
        for offset, delta in ((400, timedelta(seconds=-10)), (500, timedelta(days=1))):
            events.append(
                dict(
                    transaction_id=f"TX-{number - offset}",
                    occurred_at=stamp(at + delta),
                    amount="987.65",
                    currency=currency,
                    **accounts[case]["sender"],
                )
            )
    payload = dict(case_id=case, transaction=tx, risk_assessment=risk)
    fixture = dict(accounts=accounts, events=events)
    context = dict(
        contract_version=1,
        source_mode="fixture",
        case_id=case,
        snapshot_ref="fixture_"
        + digest(dict(payload=payload, history=history, history_fixture=fixture)),
        dataset_version=None,
        observed_at="2026-11-18T18:00:00Z",
        source_payload=payload,
        history=history,
    )
    context["context_revision"] = context_digest(context)
    validate("InvestigationContext", context)
    item = input_only(
        dict(
            id=identity,
            language="sr-Latn",
            instruction="Use only supplied facts and authorized evidence; "
            "write Serbian Latin prose, search procedures in English. "
            "The analyst retains final decisions.",
            context=context,
            history_fixture=fixture,
            procedure_queries=[question],
        )
    )
    reader = HistoryReader(**fixture)
    actual_history = {side: reader.read(context, side) for side in ("sender", "receiver")}
    obligations = [
        f"Transaction identifier is {txid}.",
        f"Amount is exactly {amount} {currency}.",
        f"Event time is {tx['occurred_at']}.",
        f"Illustrative fixture risk score is {score}; not ML inference or probability.",
        "Human analysts retain final decisions; no automatic intervention.",
    ]
    for side, data in actual_history.items():
        if data["availability"] == "unavailable":
            obligations.append(f"{side.capitalize()} history is unavailable, not zero activity.")
        else:
            obligations.append(
                f"{side.capitalize()} history is incomplete; "
                f"{data['eligible_count']} eligible events; separate currency "
                f"totals {json.dumps(data['totals'], sort_keys=True)}; "
                "focal minute and future excluded."
            )
    reference = dict(
        id=identity,
        source_input_sha256=digest(item),
        essential_facts=obligations,
        source_history=actual_history,
        provenance="Derived offline from authored source literals and HistoryReader; "
        "not from report outputs; author review only, team review pending.",
    )
    # Runtime projections are schema-checked independently of private expectations.
    outbound = outbound_context(context, "inv_" + "1" * 32)
    assert "essential_facts" not in json.dumps(outbound)
    return item, reference


def main():
    if PACK.exists() or LOCAL.exists():
        raise ValueError("New pack/output required; never overwrite or rerun an old batch")
    specifications = {
        "development": [
            ("supported", "available", "2168.39", "EUR", 0.48),
            ("missing", "unavailable", "91.74", "USD", 0.27),
            ("mixed", "mixed", "634.82", "GBP", 0.63),
            ("no_guidance", "unavailable", "129.56", "EUR", 0.34),
        ],
        "quality": [
            ("supported", "available", "3074.29", "EUR", 0.57),
            ("unavailable", "unavailable", "76.43", "USD", 0.31),
            ("mixed", "mixed", "851.67", "GBP", 0.66),
            ("no_guidance", "unavailable", "143.28", "EUR", 0.38),
            ("elevated", "available", "11762.94", "USD", 0.89),
            ("small", "available", "18.53", "GBP", 0.19),
            ("missing", "unavailable", "4296.81", "EUR", 0.74),
            ("mixed_large", "mixed", "6853.47", "USD", 0.81),
        ],
        "timing": [
            ("supported", "available", "2687.41", "EUR", 0.52),
            ("unavailable", "unavailable", "84.26", "USD", 0.29),
            ("mixed", "mixed", "723.58", "GBP", 0.61),
            ("no_guidance", "unavailable", "157.93", "EUR", 0.36),
            ("elevated", "available", "12534.68", "USD", 0.91),
        ],
    }
    prefixes = dict(development=("DEVQ1", 900), quality=("QUAL1", 910), timing=("TIME1", 930))
    inputs, refs, roles = {}, {}, {}
    for split, rows in specifications.items():
        prefix, base = prefixes[split]
        inputs[split], refs[split] = [], []
        for pos, (kind, history, amount, currency, score) in enumerate(rows, 1):
            identity = f"{prefix}-{pos:02}"
            item, reference = authored(
                identity,
                base + pos,
                amount,
                currency,
                score,
                history,
                NO_GUIDANCE if kind == "no_guidance" else QUESTION,
            )
            inputs[split].append(item)
            refs[split].append(reference)
            roles[identity] = dict(
                split=split,
                kind=kind,
                primary=split == "quality",
                secondary=split == "quality" and pos in (2, 3, 4, 6, 8),
            )
        save(PACK / "inputs" / (split + ".json"), inputs[split])
        save(
            PACK / "reference" / (split + ".json"),
            dict(
                custodian="Codex offline authoring automation; script SHA pinned in freeze",
                review="author_only_team_review_pending",
                items=refs[split],
            ),
        )
    queries = [
        "How should missing customer information be disclosed?",
        "When is human review required before disposition?",
        "How do I cite the exact evidence version?",
        "How should synthetic benchmark limitations be described?",
        "How should a risk score be distinguished from guilt?",
        "How do I handle a missing source of funds?",
        "What does unavailable account history mean?",
        "How do I document an alternative explanation?",
        "How should confidential customer facts be handled?",
        "How should an unresolved evidence gap be recorded?",
        "Which source provenance details should a reviewer see?",
        "How do I avoid treating an alert as a legal finding?",
        "What should a report say about historical source guidance?",
        "What is required before a case can be escalated?",
        "How should contradictory evidence be presented?",
        "How should incomplete information limit conclusions?",
        "How should unsupported procedural advice be handled?",
        "How do I keep mixed currency amounts separate?",
        "What is the exact current filing deadline in Portugal?",
        "What are the official fees for a Portuguese filing?",
    ]
    searches = [
        input_only(dict(id=f"SEARCH1-{i:02}", language="en", query=q))
        for i, q in enumerate(queries, 1)
    ]
    save(PACK / "inputs/search.json", searches)
    save(PACK / "reference/roles.json", roles)
    settings = load_settings()  # No provider initialization or capability probe.
    knowledge = KnowledgeStore(LOCAL / "knowledge.sqlite")
    corpus = knowledge.publish(ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/manifest.json")
    config_path = ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json"
    retrieval = knowledge.save_configuration(json.loads(config_path.read_text(encoding="utf-8")))
    model = settings.model.get_secret_value()
    protocol = dict(
        version=1,
        status="offline_authored_proposal_not_authorized_for_execution",
        development_order=[i["id"] for i in inputs["development"]],
        quality_order=[i["id"] for i in inputs["quality"]],
        secondary_order=[i["id"] for i in inputs["quality"] if roles[i["id"]]["secondary"]],
        timing_order=[i["id"] for i in inputs["timing"]],
        search_order=[i["id"] for i in searches],
        source_mode="authored_synthetic_fixture_not_ML_evaluation",
        proposed_model=model,
        model_access="not_probed_no_new_calls",
        generation=dict(
            provider="openai",
            semantic_retrieval=True,
            max_provider_requests_per_case=8,
            max_tool_calls=12,
            max_output_tokens=4096,
            request_timeout_seconds=30,
            total_timeout_seconds=120,
        ),
        judge=dict(
            prompt="prompts/evaluation/report-judge-v4.md",
            max_output_tokens=8192,
            timeout_seconds=60,
            retries=0,
            contexts="isolated_primary_secondary",
            limitation="Same model judgments are not independent human validation",
        ),
        proposed_caps=dict(
            development_generation=32,
            calibration=6,
            quality_generation=64,
            primary_judging=8,
            secondary_judging=5,
            T101_total=115,
            T102_total=40,
            combined_total=155,
        ),
        sequencing="Review sources and development first; freeze final settings before "
        "held-out generation; exact6/6 calibration before quality acceptance. "
        "No replacement slots, replay, tuning on exposed held-out outcomes or "
        "model fallback; stop on access/quota/unknown outcome.",
        additional_approval_required=True,
        corpus_version=corpus,
        local_retrieval_version=retrieval,
        semantic_policy=policy_identity(model, knowledge.passages(corpus)) if model else None,
        preparation_only=True,
        execution_ready=False,
        pending=[
            "team source/reference review and explicit new bounded budget",
            "final post-development settings freeze for held-out dispatch",
            "wire fresh materialized readers to matching external API/worker",
            "end-to-end transport ledger and immutable v4 report/unit materializer",
        ],
    )
    save(PACK / "protocol.json", protocol)
    files = [p for p in PACK.rglob("*.json")]
    files += list((ROOT / "backend/src/fraudlens").rglob("*.py"))
    files += list((ROOT / "data/knowledge/fraudlens-aml-knowledge-v1").rglob("*"))
    files += list((ROOT / "specs/003-ai-investigation/contracts").glob("*.json"))
    files += [
        ROOT / p
        for p in (
            "prompts/application/investigation-v4.md",
            "prompts/application/semantic-worker-addendum-v1.md",
            "prompts/evaluation/report-judge-v4.md",
            "uv.lock",
            "pyproject.toml",
            "frontend/package-lock.json",
            "frontend/package.json",
            "specs/003-ai-investigation/report-quality-v4-validation.md",
            "specs/003-ai-investigation/timing-v1-protocol.md",
            "evidence/tasks/feature-003-t101-t102-prepare-20261118.py",
        )
    ]
    files += list((ROOT / "evals/investigation/report-quality-v4").rglob("*.json"))

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

    # No secrets or .env bytes in this freeze, only presence/configured model.
    freeze = dict(
        kind="offline_preparation_snapshot_not_execution_freeze",
        branch=git("branch", "--show-current"),
        commit=git("rev-parse", "HEAD"),
        dirty_status=git("status", "--porcelain"),
        python=sys.version,
        platform=platform.platform(),
        processor=platform.processor(),
        sdk_versions={name: version(name) for name in ("openai", "httpx", "pydantic")},
        node=subprocess.check_output(["node", "--version"], text=True).strip(),
        api_key_present=bool(settings.api_key.get_secret_value()),
        model=model,
        observer=dict(
            clock="time.perf_counter",
            poll_seconds=0.25,
            separate_from="API and worker processes",
            report_validation="bound source/evidence required, not status alone",
        ),
        corpus_version=corpus,
        local_retrieval_version=retrieval,
        bytes_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in files if p.is_file()},
        actual_provider_calls=0,
        model_access_verified=False,
        review_status="author_only_team_pending",
        execution_ready=False,
    )
    save(LOCAL / "freeze.json", freeze)
    save(
        PACK / "manifest.json",
        dict(
            algorithm="SHA256 exact working-tree bytes; input/corpus identities use canonical JSON",
            files_sha256={p.relative_to(PACK).as_posix(): sha(p) for p in PACK.rglob("*.json")},
            machine_freeze_sha256=sha(LOCAL / "freeze.json"),
            execution_ready=False,
        ),
    )
    print(
        json.dumps(
            dict(
                development=4,
                quality=8,
                paired_secondary=5,
                timing=5,
                searches=20,
                configured_model=model,
                api_key_present=freeze["api_key_present"],
                new_provider_calls=0,
                execution_ready=False,
                corpus_version=corpus,
            )
        )
    )


if __name__ == "__main__":
    main()
