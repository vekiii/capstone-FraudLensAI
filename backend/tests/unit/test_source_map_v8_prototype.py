"""Prototype boundary negatives only; no real provider or retrieval-quality claim."""

import importlib.util
import json

import pytest

from fraudlens.investigation.models import ROOT


@pytest.fixture
def module():
    path = ROOT / "evidence/tasks/feature-003-source-map-v8-prototype-20261118.py"
    spec = importlib.util.spec_from_file_location("test_only_source_map_prototype", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sources(count=2):
    return [
        dict(passage_id=f"p{i}", text=f"Source {i}.\nExact line breaks remain. ")
        for i in range(count)
    ]


def test_one_key_per_source_and_authoritative_quote_bytes(module):
    values = sources()
    schema = module.source_schema(values)
    assert set(schema["properties"]["source_ranks"]["properties"]) == {"p0", "p1"}
    output = module.decode_selection(
        json.dumps(dict(verdict="supported", reason="source", source_ranks={"p0": 2, "p1": 1})),
        values,
    )
    assert output["selected"] == [
        dict(passage_id="p1", quote=values[1]["text"]),
        dict(passage_id="p0", quote=values[0]["text"]),
    ]


def test_duplicate_json_keys_never_silently_collapse(module):
    with pytest.raises(ValueError):
        module.decode_selection(
            '{"verdict":"supported","reason":"x","source_ranks":{"p0":1,"p0":2,"p1":0}}', sources()
        )


@pytest.mark.parametrize(
    "rank_map", [{"p0": 1, "foreign": 0}, {"p0": True, "p1": 0}, {"p0": 6, "p1": 0}, {"p0": 1}]
)
def test_foreign_missing_boolean_or_out_of_range_ranks_rejected(module, rank_map):
    with pytest.raises(ValueError):
        module.decode_selection(
            json.dumps(dict(verdict="supported", reason="x", source_ranks=rank_map)), sources()
        )


def test_more_than_five_sources_rejected_not_truncated(module):
    values = sources(6)
    with pytest.raises(ValueError):
        module.decode_selection(
            json.dumps(
                dict(
                    verdict="supported",
                    reason="x",
                    source_ranks={p["passage_id"]: 1 for p in values},
                )
            ),
            values,
        )


def test_model_cannot_supply_its_own_quote_or_contradict_verdict(module):
    with pytest.raises(ValueError):
        module.decode_selection(
            json.dumps(
                dict(
                    verdict="supported",
                    reason="x",
                    source_ranks={"p0": 1, "p1": 0},
                    quote="Invented source quotation",
                )
            ),
            sources(),
        )
    with pytest.raises(ValueError):
        module.decode_selection(
            json.dumps(dict(verdict="insufficient", reason="x", source_ranks={"p0": 1, "p1": 0})),
            sources(),
        )


def test_source_pool_bounds_fail_before_any_provider(module):
    for values in (
        [],
        sources(21),
        sources() + sources(),
        [dict(passage_id="p0", text="x" * 1201)],
    ):
        with pytest.raises(ValueError):
            module.source_schema(values)
