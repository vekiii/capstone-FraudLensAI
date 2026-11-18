"""Opt-in evaluation boundaries. Never imported by application/worker defaults."""

import copy
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from fraudlens.investigation.context import HistoryReader
from fraudlens.investigation.evaluation import input_only
from fraudlens.investigation.models import canonical


class MaterializedReader:
    def __init__(self, inputs):
        rows = [input_only(row) for row in inputs]
        self.rows = {row["context"]["case_id"]: row for row in rows}
        if len(self.rows) != len(rows):
            raise ValueError("Duplicate case identity")

    def resolve(self, case_id, source_mode, snapshot_ref):
        row = self.rows.get(case_id)
        if row is None or source_mode != "fixture":
            raise ValueError("Fresh context unavailable; no fallback")
        context = row["context"]
        if snapshot_ref is not None and snapshot_ref != context["snapshot_ref"]:
            raise ValueError("stale_snapshot")
        return copy.deepcopy(context)

    def read(self, context, account_side, limit=50):
        expected = self.resolve(context["case_id"], context["source_mode"], context["snapshot_ref"])
        if context != expected:
            raise ValueError("Changed fresh context")
        return HistoryReader(**self.rows[context["case_id"]]["history_fixture"]).read(
            context, account_side, limit
        )


class DispatchLedger:
    def __init__(self, path, cap, model):
        if type(cap) is not int or not 1 <= cap <= 155 or not isinstance(model, str) or not model:
            raise ValueError("Explicit bounded budget/model required")
        self.path, self.cap, self.model = Path(path), cap, model
        with self.connection() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS identity (singleton INTEGER PRIMARY KEY "
                "CHECK(singleton=1), cap INTEGER NOT NULL, model TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS dispatches (sequence INTEGER PRIMARY KEY, "
                "request BLOB NOT NULL, request_sha256 TEXT NOT NULL, result TEXT)"
            )
            db.execute("INSERT OR IGNORE INTO identity VALUES (1,?,?)", (cap, model))
            if db.execute("SELECT cap,model FROM identity").fetchone() != (cap, model):
                raise ValueError("Frozen dispatch budget/model changed")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=1)
        try:
            db.execute("PRAGMA synchronous=FULL")
            with db:
                yield db
        finally:
            db.close()

    def reserve(self, body):
        data = json.loads(body)
        if len(body) > 65536 or data.get("model") != self.model:
            raise ValueError("Foreign model or oversized input")

        def private(value):
            forbidden = {
                "essential_facts",
                "expected_missing_fields",
                "expectations",
                "gold",
                "canary",
            }
            if isinstance(value, dict):
                return bool(forbidden.intersection(value)) or any(
                    private(v) for v in value.values()
                )
            if isinstance(value, list):
                return any(private(v) for v in value)
            return False

        if private(data):
            raise ValueError("Private references forbidden in transport input")
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute("SELECT result FROM dispatches ORDER BY sequence").fetchall()
            if any(r[0] is None for r in rows):
                raise ValueError("Previous dispatch outcome unknown; batch stopped")
            if any(json.loads(r[0]).get("stop_batch") for r in rows):
                raise ValueError("Provider access/quota failure; batch stopped")
            if len(rows) >= self.cap:
                raise ValueError("Provider budget exhausted")
            sequence = len(rows) + 1
            db.execute(
                "INSERT INTO dispatches VALUES (?,?,?,NULL)",
                (sequence, body, hashlib.sha256(body).hexdigest()),
            )
        return sequence

    def complete(self, sequence, result):
        result = dict(result)
        body = result.get("response_json", {})
        error = body.get("error", {}) if isinstance(body, dict) else {}
        quota = isinstance(error, dict) and (
            error.get("code")
            in ("insufficient_quota", "billing_hard_limit_reached", "billing_not_active")
            or error.get("type") == "insufficient_quota"
        )
        result["stop_batch"] = bool(
            result.get("stop_batch") or quota or result["status"] in (400, 401, 403, 404, 422)
        )
        with self.connection() as db:
            changed = db.execute(
                "UPDATE dispatches SET result=? WHERE sequence=? AND result IS NULL",
                (canonical(result).decode(), sequence),
            ).rowcount
            if changed != 1:
                raise ValueError("Missing or already completed dispatch")


def metered_transport(ledger, inner=None):
    """Reserve durably before network, including semantic/retry/repair requests.

    Construct only after an external, hash-bound approval gate. No headers/secrets
    enter the ledger. A body-read/network/cancellation unknown blocks later sends.
    """
    import httpx2

    inner = inner or httpx2.AsyncHTTPTransport(retries=0)

    class Metered(httpx2.AsyncBaseTransport):
        async def handle_async_request(self, request):
            sequence = ledger.reserve(request.content)
            response = await inner.handle_async_request(request)
            content = bytearray()
            try:
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > 2097152:
                        raise ValueError("Provider response exceeds bounded archive")
            finally:
                await response.aclose()
            try:
                value = json.loads(content)
            except ValueError, UnicodeDecodeError:
                value = None
            ledger.complete(
                sequence,
                dict(
                    status=response.status_code,
                    request_id=response.headers.get("x-request-id"),
                    response_body=bytes(content).decode("utf-8", errors="replace"),
                    response_sha256=hashlib.sha256(content).hexdigest(),
                    response_json=value,
                    usage=value.get("usage") if isinstance(value, dict) else None,
                    stop_batch=value is None,
                ),
            )
            return httpx2.Response(
                response.status_code,
                headers=response.headers,
                content=bytes(content),
                request=request,
            )

        async def aclose(self):
            await inner.aclose()

    return Metered()


def require_authorization(approval_path, freeze_path):
    """Validate an operator-recorded explicit approval, never manufacture one.

    Software binding is not proof of human consent. The operator must first
    obtain the user's actual review/authorization and preserve its exact scope.
    """
    raw = freeze_path.read_bytes()
    freeze = json.loads(raw)
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if (
        freeze.get("batch_directory") != str(freeze_path.parent.resolve())
        or approval.get("approved") is not True
        or approval.get("freeze_sha256") != hashlib.sha256(raw).hexdigest()
        or approval.get("stage") != freeze["stage"]
        or type(approval.get("maximum_requests")) is not int
        or approval["maximum_requests"] != freeze["maximum_requests"]
        or approval.get("model") != freeze["model"]
        or not isinstance(approval.get("user_authorization"), str)
        or not approval["user_authorization"].strip()
    ):
        raise ValueError("Separate reviewed hash-bound approval required")
    for path, expected in freeze["files_sha256"].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            raise ValueError("Frozen execution source changed")
    return freeze


def build_service(knowledge, inputs, settings, *, ledger=None):
    """Match API and worker readers; no default application composition changes."""
    from fraudlens.investigation.workflow import InvestigationService

    if settings.source != "fixture":
        raise ValueError("Fresh authored fixture source required")
    provider_factory = None
    if settings.provider == "openai":
        if ledger is None or ledger.model != settings.model.get_secret_value():
            raise ValueError("Explicit reviewed metered provider required")

        def provider_factory(binding):
            from fraudlens.investigation.provider import OpenAIProvider

            cap_args = (
                {"request_timeout_cap": 45}
                if binding.get("semantic_profile") in ("v7", "v8")
                and binding.get("limits", {}).get("request_timeout_seconds", 30) > 30
                else {}
            )
            if binding.get('limits', {}).get('request_timeout_seconds', 30) > 45:
                cap_args['request_timeout_cap'] = 60
            if binding.get('report_parallel_tools') is True:
                cap_args['parallel_tools'] = True
            if binding.get('report_reasoning_effort') is not None:
                cap_args['reasoning_effort'] = binding['report_reasoning_effort']
            if binding.get('limits', {}).get('max_output_tokens', 4096) > 4096:
                cap_args['output_token_cap'] = 8192
            return OpenAIProvider(
                settings.api_key.get_secret_value(),
                binding["requested_model"],
                prompt=binding["prompt"],
                transport=metered_transport(ledger),
                **cap_args,
            )

    reader = MaterializedReader(inputs)
    service = InvestigationService(
        knowledge.repository,
        knowledge,
        settings,
        provider_factory=provider_factory,
        history_reader=reader,
    )
    service.context_reader = reader
    return service
