"""One-shot authorized v4 judging; public packets only, zero SDK retries.

prepare is offline. run requires hash-bound recorded user approval. Calibration
expectations are NEVER loaded by run; assess joins only saved immutable outputs.
"""

import argparse
import asyncio
import hashlib
import json
import os
from copy import deepcopy
from pathlib import Path

from fraudlens.investigation.acceptance_harness import (
    DispatchLedger,
    metered_transport,
    require_authorization,
)
from fraudlens.investigation.judging_v4 import (
    RATING_SCHEMA,
    assess_calibration,
    project_packet,
    ratings_map,
    validate_rating,
)
from fraudlens.investigation.models import ROOT, canonical
from fraudlens.investigation.settings import load_settings


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def provider_rating_schema(packet=None):
    """Provider subset only; unchanged local RATING_SCHEMA retains uniqueness.

    Matches the application's existing compile_report_schema treatment of
    uniqueItems. Closed objects, required fields, enums and binding rules remain.
    Every actual rating is still validated against the full original v4 schema.
    """

    def project(node):
        if isinstance(node, dict):
            return {key: project(value) for key, value in node.items() if key != "uniqueItems"}
        if isinstance(node, list):
            return [project(value) for value in node]
        return node

    schema = project(RATING_SCHEMA)
    if packet is None:
        return schema
    pointers = ["/" + key.replace("~", "~0").replace("/", "~1") for key in packet["report"]]
    for check in schema["properties"]["checks"]["properties"].values():
        check["properties"]["report_locations"]["items"]["enum"] = pointers
    witness = schema["properties"]["contradictions"]["items"]["properties"]
    witness["claim_location"]["enum"] = pointers
    witness["counter_location"]["enum"] = [*pointers, None]
    units = schema["properties"]["units"]
    allowed = {
        "observation": ["supported", "unsupported", "uncertain"],
        "procedure": ["applicable", "unsupported", "uncertain"],
        "essential_fact": ["present", "missing", "uncertain"],
    }
    branches = []
    for kind, judgments in allowed.items():
        ids = [unit["unit_id"] for unit in packet["units"] if unit["claim_kind"] == kind]
        if ids:
            branch = deepcopy(units["items"])
            branch["properties"]["unit_id"]["enum"] = ids
            branch["properties"]["judgment"]["enum"] = judgments
            branches.append(branch)
    if branches:
        units["items"] = {"anyOf": branches}
    else:
        units["maxItems"] = 0
    return schema


def prepare(args):
    args.batch.mkdir(parents=True, exist_ok=False)
    if args.packets:
        packets = load(args.packets)
    else:
        packets = load(ROOT / "evals/investigation/report-quality-v4/inputs/controls.json")
    packets = [project_packet(p) for p in packets]
    stage = "calibration" if all(p["role"] == "calibration" for p in packets) else "judging"
    expected = 6 if stage == "calibration" else 13
    if len(packets) != expected or len({p["packet_id"] for p in packets}) != expected:
        raise ValueError("Frozen complete six or eight-plus-five packet inventory required")
    save(args.batch / "packets.json", packets)
    save(args.batch / "rating-schema.json", RATING_SCHEMA)
    wire = (
        {p["packet_id"]: provider_rating_schema(p) for p in packets}
        if args.typed_units
        else provider_rating_schema()
    )
    save(args.batch / "wire-rating-schema.json", wire)
    model = load_settings().model.get_secret_value()
    DispatchLedger(args.batch / "dispatch.sqlite", expected, model)
    paths = [
        args.batch / "packets.json",
        args.batch / "rating-schema.json",
        args.batch / "wire-rating-schema.json",
        Path(__file__).resolve(),
        ROOT / "prompts/evaluation/report-judge-v4-clarified.md",
        ROOT / "uv.lock",
    ]
    paths += list((ROOT / "backend/src/fraudlens/investigation").glob("*.py"))
    freeze = dict(
        batch_directory=str(args.batch.resolve()),
        stage=stage,
        maximum_requests=expected,
        model=model,
        max_output_tokens=8192,
        max_input_bytes=65536,
        timeout_seconds=60,
        retries=0,
        role_contexts="separate_single_packet_no_peer_ratings",
        packet_order=[p["packet_id"] for p in packets],
        typed_units=args.typed_units,
        files_sha256={str(p.resolve()): sha(p) for p in paths},
        private_control_expectations_path=str(args.reference.resolve()),
        private_control_expectations_sha256=sha(args.reference),
    )
    save(args.batch / "freeze.json", freeze)
    print(
        json.dumps(
            dict(
                prepared=True,
                stage=stage,
                cap=expected,
                actual_calls=0,
                freeze_sha256=sha(args.batch / "freeze.json"),
            )
        )
    )


async def run(args):
    if args.approval is None:
        raise ValueError("Explicit user approval required")
    freeze = require_authorization(args.approval, args.batch / "freeze.json")
    settings = load_settings()
    if settings.model.get_secret_value() != freeze["model"]:
        raise ValueError("Configured model changed")
    packets = load(args.batch / "packets.json")
    wire = load(args.batch / "wire-rating-schema.json")
    save(
        args.batch / "batch-intent.json",
        dict(freeze_sha256=sha(args.batch / "freeze.json"), packet_order=freeze["packet_order"]),
    )
    ledger = DispatchLedger(
        args.batch / "dispatch.sqlite", freeze["maximum_requests"], freeze["model"]
    )
    ratings = []
    for index, packet in enumerate(packets):
        # No private reference, expected judgment or peer response is ever loaded.
        if project_packet(packet) != packet:
            raise ValueError("Public packet changed")
        payload = dict(
            model=freeze["model"],
            store=False,
            max_output_tokens=8192,
            instructions=(ROOT / "prompts/evaluation/report-judge-v4-clarified.md").read_text(
                encoding="utf-8"
            ),
            input=canonical(packet).decode(),
            text=dict(
                format=dict(
                    type="json_schema",
                    name="report_rating_v4",
                    strict=True,
                    schema=wire[packet["packet_id"]] if freeze.get("typed_units") else wire,
                )
            ),
        )
        if len(canonical(payload)) > 65536:
            raise ValueError("Judge input exceeds frozen byte limit")
        save(
            args.batch / f"{index:02}-intent.json",
            dict(
                packet_id=packet["packet_id"],
                payload_sha256=hashlib.sha256(canonical(payload)).hexdigest(),
            ),
        )
        provider = None
        error = None
        value = None
        try:
            from fraudlens.investigation.provider import OpenAIProvider

            provider = OpenAIProvider(
                settings.api_key.get_secret_value(),
                freeze["model"],
                transport=metered_transport(ledger),
            )
            provider.transport.input_limit = 65536
            async with asyncio.timeout(60):
                response = await provider.client.responses.create(**payload, timeout=60)
            raw = response.model_dump(mode="json")
            save(args.batch / f"{index:02}-raw.json", raw)
            if raw.get("status") != "completed":
                raise ValueError("Incomplete judge response")
            texts = [
                part["text"]
                for item in raw.get("output", [])
                if item.get("type") == "message"
                for part in item.get("content", [])
                if part.get("type") == "output_text"
            ]
            if len(texts) != 1:
                raise ValueError("Missing/ambiguous/refused judge result")
            value = json.loads(texts[0])
            validate_rating(packet, value)
        except Exception as exc:
            error = type(exc).__name__
        finally:
            if provider is not None:
                try:
                    async with asyncio.timeout(1):
                        await provider.aclose()
                except Exception:
                    pass
        save(
            args.batch / f"{index:02}-result.json",
            dict(packet_id=packet["packet_id"], rating=value, validation_error=error),
        )
        if value is not None:
            ratings.append(
                dict(role=packet["role"], scenario_id=packet["scenario_id"], rating=value)
            )
        print(
            json.dumps(
                dict(
                    index=index,
                    scenario_id=packet["scenario_id"],
                    role=packet["role"],
                    response_present=value is not None,
                    validation_error=error,
                )
            ),
            flush=True,
        )
        with ledger.connection() as db:
            outcomes = db.execute("SELECT result FROM dispatches").fetchall()
        if any(r[0] is None or json.loads(r[0]).get("stop_batch") for r in outcomes):
            break
    save(args.batch / "ratings.json", ratings)


def assess(args):
    freeze = load(args.batch / "freeze.json")
    reference = Path(
        freeze.get(
            "private_control_expectations_path",
            ROOT / "evals/investigation/report-quality-v4/reference/expectations.json",
        )
    )
    if sha(reference) != freeze["private_control_expectations_sha256"]:
        raise ValueError("Private calibration expectations changed")
    packets = load(args.batch / "packets.json")
    ratings = load(args.batch / "ratings.json")
    expectations = load(reference)
    result = assess_calibration(packets, ratings_map(ratings), expectations)
    save(args.batch / "calibration-result.json", result)
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "assess"))
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--packets", type=Path)
    parser.add_argument(
        "--typed-units", action="store_true", help="Freeze unit-specific judgment choices"
    )
    parser.add_argument(
        "--reference",
        type=Path,
        default=ROOT / "evals/investigation/report-quality-v4/reference/expectations.json",
    )
    parser.add_argument("--approval", type=Path)
    args = parser.parse_args()
    args.batch = args.batch.resolve()
    if args.command == "prepare":
        prepare(args)
    elif args.command == "run":
        asyncio.run(run(args))
    else:
        assess(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps(dict(failed=True, error_type=type(error).__name__)))
        raise SystemExit(2) from None
