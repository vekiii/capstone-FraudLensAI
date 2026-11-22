"""Load a bounded, independently hash-pinned EDA summary before JSON parsing."""

import hashlib
import re
from pathlib import Path

from pydantic import ValidationError

from fraudlens.contracts import EdaSummary

_EXPECTED_SOURCE = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
_MAX_BYTES = 1_048_576


class EdaUnavailable(Exception):
    """The trusted precomputed aggregate is absent or incompatible."""


class EdaService:
    def __init__(self, path: Path | None = None, expected_sha256: str | None = None,
                 *, expected_source_sha256: str = _EXPECTED_SOURCE):
        self.path = path
        self.expected_sha256 = expected_sha256
        self.expected_source_sha256 = expected_source_sha256

    def load(self) -> EdaSummary:
        if (self.path is None or self.expected_sha256 is None
                or re.fullmatch(r'[0-9a-f]{64}', self.expected_sha256) is None
                or re.fullmatch(r'[0-9a-f]{64}', self.expected_source_sha256) is None):
            raise EdaUnavailable('EDA summary is not configured')
        try:
            if self.path.is_symlink() or not self.path.is_file():
                raise EdaUnavailable('EDA summary is missing')
            if self.path.stat().st_size > _MAX_BYTES:
                raise EdaUnavailable('EDA summary exceeds bound')
            raw = self.path.read_bytes()
            if len(raw) > _MAX_BYTES:
                raise EdaUnavailable('EDA summary exceeds bound')
            if hashlib.sha256(raw).hexdigest() != self.expected_sha256:
                raise EdaUnavailable('EDA summary digest mismatch')
            summary = EdaSummary.model_validate_json(raw, strict=True)
            if summary.source_sha256 != self.expected_source_sha256:
                raise EdaUnavailable('EDA source identity mismatch')
            return summary
        except (OSError, ValidationError, ValueError) as error:
            raise EdaUnavailable('EDA summary unavailable or invalid') from error
