"""External HTTP timing helper; never imported by application or worker.

The operator must separately authorize and freeze a batch before using this helper.
It does not start a worker, grant a budget, or assert report semantic quality.
"""

import asyncio
import json
import os
import re
import time
from datetime import UTC, datetime
from uuid import uuid4

from fraudlens.investigation.timing_evaluation import STATES, SUCCESS, TERMINAL


def _save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


async def observe(
    client, request, intent_path, validator, *, clock=time.perf_counter, sleep=asyncio.sleep
):
    """One slot, no POST retry; run in a process separate from API and worker.

    client must be a dedicated loopback AsyncClient with redirects/retries disabled.
    validator must check the saved report against its bound context and evidence.
    Durable intent blocks a second invocation even if the first result is unknown.
    This helper has no CLI and is not a complete authorized/metered batch runner.
    """
    key = str(uuid4())
    _save(
        intent_path,
        dict(
            request=request,
            idempotency_key=key,
            wall_utc=datetime.now(UTC).isoformat(),
            poll_seconds=0.25,
        ),
    )
    rows = []
    state, attempt, validated, validation_error = "unknown", None, False, None
    error = None
    started = clock()
    observed = started

    async def exchange(method, path, **kwargs):
        remaining = 120 - (clock() - started)
        if remaining <= 0:
            raise TimeoutError("Observation deadline")
        async with asyncio.timeout(remaining):
            response = await getattr(client, method)(path, **kwargs)
            response.raise_for_status()
            value = response.json()
        elapsed = clock() - started
        # Archive exact HTTP bodies separately from judgments; never infer a state
        # transition from a timeout or from client cancellation.
        row = dict(
            method=method, seconds=elapsed, body=value, wall_utc=datetime.now(UTC).isoformat()
        )
        _save(intent_path.with_name(intent_path.stem + f"-http-{len(rows):03}.json"), row)
        rows.append(row)
        return value, elapsed

    try:
        created, observed = await exchange(
            "post", "/api/investigation/runs", json=request, headers={"Idempotency-Key": key}
        )
        attempt = created["attempt_id"]
        if not isinstance(attempt, str) or not re.fullmatch(r"att_[a-f0-9]{32}", attempt):
            raise ValueError("Invalid attempt identity")
        # A creation response is never substituted for the required GET observation.
        while clock() - started < 120:
            view, observed = await exchange("get", "/api/investigation/attempts/" + attempt)
            if view.get("attempt_id") != attempt:
                raise ValueError("Foreign attempt observation")
            state = view["state"]
            if state not in STATES:
                raise ValueError("Unknown observation state")
            if state in TERMINAL:
                if state in SUCCESS:
                    try:
                        validated = validator(view) is True
                    except Exception as exc:
                        validation_error = type(exc).__name__
                break
            remaining = 120 - (clock() - started)
            if remaining <= 0:
                break
            await sleep(min(0.25, remaining))
        if state not in TERMINAL:
            observed = clock() - started
    except Exception as exc:
        error = type(exc).__name__
        state, validated = "unknown", False
        observed = clock() - started
    result = dict(
        state=state,
        seconds=observed,
        report_validated=validated,
        validation_error=validation_error,
        error=error,
        attempt_id=attempt,
        deadline_exceeded=observed > 120 or state not in TERMINAL,
        stop_batch=state not in TERMINAL,
        poll_seconds=0.25,
        http_observations=rows,
    )
    _save(intent_path.with_name(intent_path.stem + "-result.json"), result)
    return result
