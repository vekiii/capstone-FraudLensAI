"""Closed source ranks; code copies authoritative quotes without repairing bad responses."""

import json
import re

from jsonschema import Draft202012Validator

from fraudlens.investigation.retrieval_semantic_v6 import validate_selection


def source_schema(passages):
    if not isinstance(passages, list) or not 1 <= len(passages) <= 20:
        raise ValueError("Bounded source pool required")
    identifiers = []
    for item in passages:
        identifier = item.get("passage_id")
        text = item.get("text")
        if (
            not isinstance(identifier, str)
            or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", identifier)
            or identifier in identifiers
            or not isinstance(text, str)
            or not text.strip()
            or len(text) > 1200
        ):
            raise ValueError("Unique known IDs and bounded exact source text required")
        identifiers.append(identifier)
    return dict(
        type="object",
        additionalProperties=False,
        required=["verdict", "reason", "source_ranks"],
        properties=dict(
            verdict=dict(type="string", enum=["supported", "insufficient"]),
            reason=dict(type="string", minLength=1, maxLength=1000),
            source_ranks=dict(
                type="object",
                additionalProperties=False,
                required=identifiers,
                properties={
                    key: dict(type="integer", enum=[0, 1, 2, 3, 4, 5]) for key in identifiers
                },
            ),
        ),
    )


def decode_selection(raw, passages):
    schema = source_schema(passages)

    def unique_members(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Repeated JSON member, no silent collapse")
            result[key] = value
        return result

    try:
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > 2097152:
            raise ValueError("Bounded raw response required")
        value = json.loads(raw, object_pairs_hook=unique_members)
        Draft202012Validator(schema).validate(value)
        by_id = {p["passage_id"]: p for p in passages}
        ranked = sorted((rank, key) for key, rank in value["source_ranks"].items() if rank > 0)
        projected = dict(
            verdict=value["verdict"],
            reason=value["reason"],
            selected=[dict(passage_id=key, quote=by_id[key]["text"]) for _, key in ranked],
        )
        validate_selection(projected, passages)  # unchanged max5/verdict/unique/verbatim checks
        return projected
    except Exception:
        raise ValueError("Invalid source-rank response") from None
