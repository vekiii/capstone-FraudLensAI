"""Write and authenticate local LightGBM text artifacts without deserializing them.

The expected manifest digest must come from trusted configuration outside the
artifact directory. This module never constructs a LightGBM Booster.
"""

import hashlib
import json
import math
import re
import sys
import tempfile
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION

FORMAT_VERSION = 1
MODEL_FORMAT = 'lightgbm-native-text'
LIGHTGBM_VERSION = '4.7.0'
PYTHON_VERSION = '3.14.10'
_MAX_MANIFEST_BYTES = 65_536
_MAX_MODEL_BYTES = 1_073_741_824
_HEX = re.compile(r'[0-9a-f]{64}\Z')
_ARTIFACT_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z')
_REVISION = re.compile(r'[0-9a-f]{7,64}\Z')
_UNKNOWN = '__UNKNOWN__'
_CATEGORICAL = ('current_payment_currency', 'current_payment_format')
_NUMERIC = tuple(name for name in FEATURE_ORDER if name not in _CATEGORICAL)
_FIELDS = frozenset({
    'format_version', 'model_format', 'model_sha256', 'model_bytes',
    'feature_version', 'feature_order', 'matrix_feature_order',
    'currency_vocabulary', 'format_vocabulary', 'source_sha256',
    'protocol_sha256', 'code_revision', 'seed', 'threshold',
    'threshold_method', 'validation_metrics', 'lightgbm_version',
    'python_version',
})


class ArtifactError(ValueError):
    """Absent, malformed, incompatible, or unauthenticated local artifact."""


@dataclass(frozen=True)
class ArtifactMetadata:
    feature_version: str
    feature_order: tuple[str, ...]
    currency_vocabulary: tuple[str, ...]
    format_vocabulary: tuple[str, ...]
    source_sha256: str
    protocol_sha256: str
    code_revision: str
    seed: int
    threshold: float
    threshold_method: str
    validation_metrics: dict[str, float]


@dataclass(frozen=True)
class TrustedArtifact:
    """Expected values supplied independently of the artifact files."""

    manifest_sha256: str
    source_sha256: str
    protocol_sha256: str
    feature_version: str
    feature_order: tuple[str, ...]


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(value: object) -> bool:
    return isinstance(value, str) and _HEX.fullmatch(value) is not None


def _vocabulary(value: object) -> bool:
    return (
        isinstance(value, list) and len(value) >= 2
        and all(isinstance(item, str) and item for item in value)
        and value[-1] == _UNKNOWN and len(value) == len(set(value))
        and value[:-1] == sorted(value[:-1])
    )


def _matrix_order(currency: list[str], payment_format: list[str]) -> list[str]:
    return [*_NUMERIC,
            *(f'{_CATEGORICAL[0]}={value}' for value in currency),
            *(f'{_CATEGORICAL[1]}={value}' for value in payment_format)]


def _validate_manifest(manifest: object) -> dict[str, Any]:
    if not isinstance(manifest, dict) or set(manifest) != _FIELDS:
        raise ArtifactError('artifact manifest schema mismatch')
    m = manifest
    if (type(m['format_version']) is not int or m['format_version'] != FORMAT_VERSION
            or m['model_format'] != MODEL_FORMAT
            or not _sha256(m['model_sha256'])
            or type(m['model_bytes']) is not int
            or not 0 < m['model_bytes'] <= _MAX_MODEL_BYTES
            or m['feature_version'] != FEATURE_VERSION
            or m['feature_order'] != list(FEATURE_ORDER)
            or not _vocabulary(m['currency_vocabulary'])
            or not _vocabulary(m['format_vocabulary'])
            or m['matrix_feature_order'] != _matrix_order(
                m['currency_vocabulary'], m['format_vocabulary'])
            or not _sha256(m['source_sha256'])
            or not _sha256(m['protocol_sha256'])
            or not isinstance(m['code_revision'], str)
            or _REVISION.fullmatch(m['code_revision']) is None
            or type(m['seed']) is not int or m['seed'] != 42
            or type(m['threshold']) not in (int, float)
            or not math.isfinite(m['threshold']) or not 0 <= m['threshold'] <= 1
            or m['threshold_method'] != 'validation-positive-f1-v1'
            or not isinstance(m['validation_metrics'], dict)
            or not {'f1', 'average_precision'} <= set(m['validation_metrics'])
            or any(not isinstance(key, str) or not key for key in m['validation_metrics'])
            or any(type(value) not in (int, float) or not math.isfinite(value)
                   or not 0 <= value <= 1 for value in m['validation_metrics'].values())
            or m['lightgbm_version'] != LIGHTGBM_VERSION
            or m['python_version'] != PYTHON_VERSION):
        raise ArtifactError('artifact manifest metadata mismatch')
    return m


def _runtime_versions() -> None:
    if '.'.join(map(str, sys.version_info[:3])) != PYTHON_VERSION:
        raise ArtifactError('Python runtime version mismatch')
    try:
        installed = version('lightgbm')
    except PackageNotFoundError:
        raise ArtifactError('LightGBM is not installed') from None
    if installed != LIGHTGBM_VERSION:
        raise ArtifactError('LightGBM runtime version mismatch')


def _root(root: Path) -> Path:
    try:
        path = Path(root).resolve(strict=True)
    except (OSError, RuntimeError):
        raise ArtifactError('trusted artifact root is unavailable') from None
    if not path.is_dir():
        raise ArtifactError('trusted artifact root is not a directory')
    return path


def _artifact_id(value: str) -> None:
    if (not isinstance(value, str) or _ARTIFACT_ID.fullmatch(value) is None
            or value in ('.', '..')):
        raise ArtifactError('invalid artifact identifier')


def _trusted_file(root: Path, artifact_id: str, filename: str) -> Path:
    try:
        path = (root / artifact_id / filename).resolve(strict=True)
    except (OSError, RuntimeError):
        raise ArtifactError(f'artifact {filename} is unavailable') from None
    if not path.is_relative_to(root) or not path.is_file():
        raise ArtifactError(f'artifact {filename} is outside trusted root')
    return path


def _read_bounded(path: Path, maximum: int) -> bytes:
    try:
        if not 0 < path.stat().st_size <= maximum:
            raise ArtifactError(f'artifact {path.name} size is invalid')
        data = path.read_bytes()
    except OSError:
        raise ArtifactError(f'artifact {path.name} cannot be read') from None
    if not 0 < len(data) <= maximum:
        raise ArtifactError(f'artifact {path.name} size is invalid')
    return data


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ArtifactError('duplicate manifest field')
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ArtifactError(f'invalid JSON constant: {value}')


def write_artifact(root: Path, artifact_id: str, model_bytes: bytes,
                   metadata: ArtifactMetadata) -> str:
    """Atomically publish a new directory and return its manifest SHA-256.

    The caller must retain the returned digest in independently trusted config.
    No model fitting, parsing, or serialization is performed here.
    """
    _artifact_id(artifact_id)
    destination_root = _root(root)
    _runtime_versions()
    if (not isinstance(model_bytes, bytes)
            or not 0 < len(model_bytes) <= _MAX_MODEL_BYTES):
        raise ArtifactError('model bytes must be nonempty and bounded')
    if not isinstance(metadata, ArtifactMetadata):
        raise ArtifactError('artifact metadata is required')
    manifest = {
        **vars(metadata), 'format_version': FORMAT_VERSION,
        'model_format': MODEL_FORMAT, 'model_sha256': _digest(model_bytes),
        'model_bytes': len(model_bytes), 'feature_order': list(metadata.feature_order),
        'currency_vocabulary': list(metadata.currency_vocabulary),
        'format_vocabulary': list(metadata.format_vocabulary),
        'matrix_feature_order': _matrix_order(
            list(metadata.currency_vocabulary), list(metadata.format_vocabulary)),
        'lightgbm_version': LIGHTGBM_VERSION, 'python_version': PYTHON_VERSION,
    }
    _validate_manifest(manifest)
    manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(',', ':'),
                                allow_nan=False).encode('utf-8')
    if len(manifest_bytes) > _MAX_MANIFEST_BYTES:
        raise ArtifactError('artifact manifest is too large')
    target = destination_root / artifact_id
    if target.exists() or target.is_symlink():
        raise ArtifactError('artifact identifier already exists')
    with tempfile.TemporaryDirectory(prefix='.artifact-', dir=destination_root) as stage:
        staged = Path(stage)
        (staged / 'model.txt').write_bytes(model_bytes)
        (staged / 'manifest.json').write_bytes(manifest_bytes)
        try:
            staged.rename(target)
        except OSError:
            raise ArtifactError('artifact publication failed') from None
    return _digest(manifest_bytes)


def read_verified_artifact(root: Path, artifact_id: str,
                           trusted: TrustedArtifact) -> tuple[bytes, dict[str, Any]]:
    """Authenticate both files and compatibility before any native model parser.

    ``trusted.manifest_sha256`` must be pinned outside the artifact directory.
    The returned bytes may be passed to a native parser only by a trusted caller.
    """
    _artifact_id(artifact_id)
    if (not isinstance(trusted, TrustedArtifact)
            or not all(_sha256(value) for value in (
                trusted.manifest_sha256, trusted.source_sha256,
                trusted.protocol_sha256))
            or trusted.feature_version != FEATURE_VERSION
            or trusted.feature_order != FEATURE_ORDER):
        raise ArtifactError('trusted artifact expectation is invalid')
    destination_root = _root(root)
    manifest_bytes = _read_bounded(
        _trusted_file(destination_root, artifact_id, 'manifest.json'),
        _MAX_MANIFEST_BYTES)
    if _digest(manifest_bytes) != trusted.manifest_sha256:
        raise ArtifactError('manifest digest mismatch')
    try:
        manifest = json.loads(manifest_bytes, object_pairs_hook=_unique_pairs,
                              parse_constant=_reject_constant)
    except (ValueError, UnicodeDecodeError):
        raise ArtifactError('artifact manifest is invalid JSON') from None
    _validate_manifest(manifest)
    if (manifest['source_sha256'] != trusted.source_sha256
            or manifest['protocol_sha256'] != trusted.protocol_sha256
            or manifest['feature_version'] != trusted.feature_version
            or tuple(manifest['feature_order']) != trusted.feature_order):
        raise ArtifactError('artifact identity mismatch')
    _runtime_versions()
    model = _read_bounded(_trusted_file(destination_root, artifact_id, 'model.txt'),
                          _MAX_MODEL_BYTES)
    if len(model) != manifest['model_bytes'] or _digest(model) != manifest['model_sha256']:
        raise ArtifactError('model digest or size mismatch')
    return model, manifest
