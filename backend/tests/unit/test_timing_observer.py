import asyncio
import json

import pytest

from fraudlens.investigation.timing_observer import observe


class Clock:
    now = 0.0

    def __call__(self):
        return self.now

    async def sleep(self, seconds):
        self.now += seconds


class Response:
    def __init__(self, value):
        self.value = value

    def raise_for_status(self):
        pass

    def json(self):
        return self.value


class Client:
    def __init__(self, clock, rows, post_seconds=2):
        self.clock, self.rows, self.post_seconds = clock, iter(rows), post_seconds
        self.calls = []

    async def post(self, path, **kwargs):
        self.calls.append((path, kwargs))
        self.clock.now += self.post_seconds
        return Response(dict(attempt_id="att_" + "a" * 32, state="created"))

    async def get(self, path):
        self.calls.append((path, {}))
        row, delay = next(self.rows)
        self.clock.now += delay
        if isinstance(row, Exception):
            raise row
        return Response(dict(attempt_id="att_" + "a" * 32, **row))


def run(tmp_path, rows, *, validator=lambda view: True, post_seconds=2):
    clock = Clock()
    client = Client(clock, rows, post_seconds)
    result = asyncio.run(
        observe(
            client,
            {"case_id": "CASE-931"},
            tmp_path / "intent.json",
            validator,
            clock=clock,
            sleep=clock.sleep,
        )
    )
    return result, client


def test_creation_and_poll_time_included_and_durable_intent(tmp_path):
    result, client = run(
        tmp_path, [({"state": "drafting"}, 3), ({"state": "needs_information", "report": {}}, 4)]
    )
    assert result["seconds"] == 9.25
    assert result["state"] == "needs_information" and result["report_validated"]
    intent = json.loads((tmp_path / "intent.json").read_text())
    assert client.calls[0][1]["headers"]["Idempotency-Key"] == intent["idempotency_key"]
    assert len(result["http_observations"]) == 3


def test_existing_intent_blocks_even_unknown_outcome_replay(tmp_path):
    (tmp_path / "intent.json").write_text("{}")
    clock = Clock()
    client = Client(clock, [])
    with pytest.raises(FileExistsError):
        asyncio.run(observe(client, {}, tmp_path / "intent.json", lambda _: True))
    assert client.calls == []


def test_overrun_never_clamped_or_called_success(tmp_path):
    result, _ = run(tmp_path, [({"state": "ready_for_review", "report": {}}, 121.5)])
    assert result["seconds"] == 123.5
    assert result["deadline_exceeded"] and result["state"] == "ready_for_review"


def test_nonterminal_at_deadline_stops_batch_without_claiming_cancellation(tmp_path):
    result, _ = run(tmp_path, [({"state": "drafting"}, 118)])
    assert result["state"] == "drafting" and result["stop_batch"]
    assert not result["report_validated"]


def test_network_unknown_stops_and_does_not_leak_exception_text(tmp_path):
    result, client = run(tmp_path, [(RuntimeError("private-key-value"), 1)])
    assert result["state"] == "unknown" and result["stop_batch"]
    assert "private-key-value" not in json.dumps(result)
    assert len(client.calls) == 2


@pytest.mark.parametrize("state", ["failed", "cancelled"])
def test_failed_terminal_never_validated(tmp_path, state):
    result, _ = run(
        tmp_path,
        [({"state": state}, 1)],
        validator=lambda _: pytest.fail("must not validate failure"),
    )
    assert not result["report_validated"] and not result["stop_batch"]


def test_invalid_report_is_retained_as_terminal_failure(tmp_path):
    def invalid(_):
        raise ValueError("bad bound report")

    result, _ = run(
        tmp_path, [({"state": "needs_information", "report": {}}, 1)], validator=invalid
    )
    assert result["state"] == "needs_information" and not result["report_validated"]
    assert result["validation_error"] == "ValueError"


def test_post_exhausting_deadline_never_observes_or_infers_terminal(tmp_path):
    result, client = run(tmp_path, [], post_seconds=121)
    assert len(client.calls) == 1
    assert result["seconds"] == 121 and result["state"] == "unknown"
    assert result["stop_batch"]


def test_invalid_http_state_stops_batch(tmp_path):
    result, client = run(tmp_path, [({"state": "imaginary_success"}, 1)])
    assert result["state"] == "unknown" and result["error"] == "ValueError"
    assert len(client.calls) == 2


def test_terminal_validation_does_not_replace_first_visible_timestamp(tmp_path):
    clock = Clock()
    client = Client(clock, [({"state": "ready_for_review"}, 4)])

    def validate(_):
        clock.now += 5
        return True

    result = asyncio.run(
        observe(client, {}, tmp_path / "intent.json", validate, clock=clock, sleep=clock.sleep)
    )
    assert result["seconds"] == 6
    assert clock.now == 11


def test_real_async_network_timeout_records_unknown_without_second_post(tmp_path, monkeypatch):
    import fraudlens.investigation.timing_observer as observer

    actual_timeout = asyncio.timeout
    monkeypatch.setattr(observer.asyncio, "timeout", lambda _: actual_timeout(0.01))

    class BlockedClient:
        count = 0

        async def post(self, *args, **kwargs):
            self.count += 1
            await asyncio.Event().wait()

    client = BlockedClient()
    result = asyncio.run(observe(client, {}, tmp_path / "intent.json", lambda _: True))
    assert result["error"] == "TimeoutError" and result["state"] == "unknown"
    assert client.count == 1 and result["stop_batch"]
