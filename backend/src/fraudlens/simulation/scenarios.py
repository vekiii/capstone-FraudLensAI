"""Read-only trusted catalog; selection facts never contain private outcomes."""

import json
from dataclasses import dataclass
from pathlib import Path

from fraudlens.simulation.models import Id, OutcomeSet, Scenario, fingerprint, validate_pair

ROOT = Path(__file__).resolve().parents[4] / "data/fixtures/simulation"


def members(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON key")
        value[key] = item
    return value


def read(path, root):
    if not path.resolve().is_relative_to(root):
        raise ValueError("Catalog root boundary")
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=members,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Nonfinite JSON")),
    )


@dataclass(frozen=True)
class Revision:
    facts: Scenario
    _outcomes: OutcomeSet

    def metadata(self):
        return self.facts.model_dump(exclude={"alerts"})

    def evaluation_outcomes(self):
        """Explicit post-selection boundary; never pass this to a ranking function."""
        return self._outcomes.model_copy(deep=True)


class Catalog:
    def __init__(self, root=None):
        # root is trusted deployment/test configuration, not a request parameter.
        root = Path(root or ROOT).resolve()
        self._revisions = {}
        try:
            if not root.is_dir():
                raise ValueError("Missing catalog")
            for path in sorted(root.glob("*.json")):
                if path.name.endswith(".outcomes.json"):
                    continue
                s, o = validate_pair(
                    read(path, root), read(path.with_suffix(".outcomes.json"), root)
                )
                computed = fingerprint(s, o)
                if computed != s.content_sha256:
                    raise ValueError("Fingerprint mismatch")
                key = (s.scenario_id, s.scenario_version)
                if key in self._revisions and self._revisions[key].facts.content_sha256 != computed:
                    raise ValueError("Conflicting revision")
                self._revisions[key] = Revision(s, o)
        except ValueError, OSError:
            raise ValueError("Invalid trusted simulation catalog") from None

    def resolve(self, scenario_id: Id, scenario_version: int):
        # Identity lookup only: no filesystem path derived from caller input.
        if type(scenario_id) is not str or type(scenario_version) is not int:
            raise ValueError("Invalid scenario reference")
        try:
            revision = self._revisions[(scenario_id, scenario_version)]
        except KeyError:
            raise ValueError("Scenario revision unavailable") from None
        return Revision(
            revision.facts.model_copy(deep=True), revision._outcomes.model_copy(deep=True)
        )

    def metadata(self):
        return [self._revisions[key].metadata() for key in sorted(self._revisions)]
