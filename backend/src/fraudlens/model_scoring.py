"""Trusted local history-v1 model loading and scoring."""

import hashlib
import io
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import joblib
import numpy
import sklearn

from fraudlens.data_contracts import _request_v2, score_v2
from fraudlens.explanations import model_explanation

SCORER_VERSION = 'model-history-v1'
TRANSFORM_VERSION = 'sklearn-column-transformer-v1'
LOCAL_ROOT = Path(__file__).resolve().parents[3] / 'artifacts'


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _inside(path: Path, root: Path) -> Path:
    root = root.resolve(strict=True)
    resolved = path.resolve(strict=False)
    if not resolved.is_relative_to(root) or resolved == root:
        raise ValueError('artifact path outside trusted local root')
    return resolved


def _local_file(directory: Path, name: str, root: Path) -> Path:
    if not isinstance(name, str) or Path(name).name != name or name in {'.', '..'}:
        raise ValueError('unapproved artifact filename')
    path = _inside(directory / name, root)
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def _dependencies() -> dict:
    return {'numpy': numpy.__version__, 'scikit_learn': sklearn.__version__,
            'joblib': joblib.__version__}


def create_manifest(artifact_dir: Path, protocol_path: Path, *,
                    trusted_root: Path = LOCAL_ROOT) -> str:
    """Seal reviewed, locally produced metadata and binary; return pin for caller."""
    directory = _inside(Path(artifact_dir), Path(trusted_root))
    metadata_file = _local_file(directory, 'metadata.json', Path(trusted_root))
    metadata = json.loads(metadata_file.read_text())
    protocol = Path(protocol_path).resolve(strict=True)
    if (metadata.get('status') != 'frozen_development_only'
            or _sha(protocol) != metadata.get('protocol_sha256')
            or json.loads(protocol.read_text()).get('feature_version') != 'history-v1'
            or metadata.get('model_file') != 'model.joblib'
            or _sha(_local_file(directory, 'model.joblib', Path(trusted_root)))
            != metadata.get('model_sha256')):
        raise ValueError('local training provenance or hash mismatch')
    manifest = {
        'manifest_version': 1, 'origin': 'reviewed_local_training',
        'model_file': 'model.joblib', 'model_sha256': metadata['model_sha256'],
        'metadata_sha256': _sha(metadata_file),
        'protocol_sha256': metadata['protocol_sha256'],
        'dataset_version': metadata['dataset_version'],
        'feature_version': metadata['feature_version'],
        'scorer_version': SCORER_VERSION, 'transform_version': TRANSFORM_VERSION,
        'dependencies': metadata['dependencies'],
        'ordered_features': metadata['ordered_features'],
        'numeric_features': metadata['numeric_features'],
        'categorical_features': metadata['categorical_features'],
        'winner_index': metadata['winner_index'],
        'validation_threshold': metadata['model_validation_threshold'],
        'calibration': metadata['calibration'],
    }
    target = directory / 'manifest.json'
    target.write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    return _sha(target)


@dataclass(frozen=True)
class TrustedArtifact:
    pipeline: object
    manifest: dict
    manifest_sha256: str


def load_trusted_artifact(artifact_dir: Path, *, trusted_root: Path = LOCAL_ROOT,
                          expected_manifest_sha256: str,
                          expected_dataset_version: str,
                          expected_protocol_sha256: str,
                          expected_scorer_version: str = SCORER_VERSION,
                          expected_feature_version: str = 'history-v1',
                          upload: object = None) -> TrustedArtifact:
    """Verify every trust/compatibility condition before executable joblib.load."""
    if upload is not None:
        raise ValueError('uploaded model artifacts forbidden')
    directory = _inside(Path(artifact_dir), Path(trusted_root))
    manifest_file = _local_file(directory, 'manifest.json', Path(trusted_root))
    if _sha(manifest_file) != expected_manifest_sha256:
        raise ValueError('manifest hash mismatch')
    manifest = json.loads(manifest_file.read_text())
    if set(manifest) != {
            'manifest_version', 'origin', 'model_file', 'model_sha256',
            'metadata_sha256', 'protocol_sha256', 'dataset_version',
            'feature_version', 'scorer_version', 'transform_version',
            'dependencies', 'ordered_features', 'numeric_features',
            'categorical_features', 'winner_index', 'validation_threshold',
            'calibration'}:
        raise ValueError('artifact manifest schema mismatch')
    expected = {
        'manifest_version': 1, 'origin': 'reviewed_local_training',
        'model_file': 'model.joblib', 'dataset_version': expected_dataset_version,
        'protocol_sha256': expected_protocol_sha256,
        'feature_version': expected_feature_version,
        'scorer_version': expected_scorer_version,
        'transform_version': TRANSFORM_VERSION, 'dependencies': _dependencies(),
        'calibration': 'none',
    }
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError('artifact origin or version incompatible')
    metadata_file = _local_file(directory, 'metadata.json', Path(trusted_root))
    if _sha(metadata_file) != manifest.get('metadata_sha256'):
        raise ValueError('metadata hash mismatch')
    metadata = json.loads(metadata_file.read_text())
    if (metadata.get('status') != 'frozen_development_only'
            or metadata.get('model_sha256') != manifest.get('model_sha256')
            or metadata.get('protocol_sha256') != expected_protocol_sha256
            or metadata.get('dataset_version') != expected_dataset_version
            or metadata.get('dependencies') != _dependencies()
            or metadata.get('feature_version') != expected_feature_version
            or metadata.get('model_validation_threshold') != manifest.get('validation_threshold')
            or metadata.get('winner_index') != manifest.get('winner_index')
            or metadata.get('ordered_features') != manifest.get('ordered_features')
            or metadata.get('numeric_features') != manifest.get('numeric_features')
            or metadata.get('categorical_features') != manifest.get('categorical_features')
            or metadata.get('model_file') != 'model.joblib'):
        raise ValueError('artifact metadata incompatible')
    if (not isinstance(manifest.get('ordered_features'), list)
            or manifest['ordered_features'] != manifest.get('numeric_features', [])
            + manifest.get('categorical_features', [])
            or not manifest['ordered_features']):
        raise ValueError('artifact feature order incompatible')
    model_file = _local_file(directory, manifest['model_file'], Path(trusted_root))
    model_bytes = model_file.read_bytes()
    if hashlib.sha256(model_bytes).hexdigest() != manifest.get('model_sha256'):
        raise ValueError('model hash mismatch')
    pipeline = joblib.load(io.BytesIO(model_bytes))
    return TrustedArtifact(pipeline, manifest, expected_manifest_sha256)


class ModelScorer:
    """Frozen fitted pipeline adapter for the label-free ScorerV2 boundary."""

    requires_artifact = True

    def __init__(self, artifact: TrustedArtifact):
        if not isinstance(artifact, TrustedArtifact):
            raise TypeError('verified local artifact required')
        manifest = artifact.manifest
        pipeline = artifact.pipeline
        if (manifest.get('scorer_version') != SCORER_VERSION
                or manifest.get('feature_version') != 'history-v1'
                or manifest.get('calibration') != 'none'
                or not hasattr(pipeline, 'named_steps')
                or set(pipeline.named_steps) != {'prepare', 'model'}
                or pipeline.named_steps['prepare'].n_features_in_
                != len(manifest['ordered_features'])
                or list(pipeline.named_steps['model'].classes_) != [0, 1]):
            raise ValueError('fitted model schema incompatible')
        self.artifact = artifact
        self.artifact_reference = {
            'sha256': artifact.manifest_sha256,
            'scorer_version': SCORER_VERSION,
            'artifact_version': SCORER_VERSION,
            'calibrated': False,
        }

    def input_row(self, request):
        """Apply frozen input order; all learned transforms remain in the pipeline."""
        _request_v2(request)
        if (request.dataset_version != self.artifact.manifest['dataset_version']
                or request.scorer_version != SCORER_VERSION):
            raise ValueError('model request version mismatch')
        manifest = self.artifact.manifest
        values = request.feature_snapshot.feature_values
        row = numpy.empty((1, len(manifest['ordered_features'])), dtype=object)
        for index, key in enumerate(manifest['ordered_features']):
            value = values[key]
            if key in manifest['numeric_features']:
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError('nonfinite model feature')
                row[0, index] = number
            else:
                row[0, index] = value if value is not None else '__missing__'
        return row

    def score(self, request):
        row = self.input_row(request)
        predictions = self.artifact.pipeline.predict_proba(row)
        if getattr(predictions, 'shape', None) != (1, 2):
            raise ValueError('model probability shape mismatch')
        probability = float(predictions[0, 1])
        if not math.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError('model probability invalid')
        score = Decimal(str(probability))
        explanation = model_explanation(
            request, self.artifact.pipeline, row, score,
            self.artifact.manifest['ordered_features'])
        snapshot = request.feature_snapshot
        return {
            'transaction_id': request.canonical_transaction.transaction_id,
            'dataset_version': request.dataset_version, 'run_id': request.run_id,
            'score': score, 'score_kind': 'uncalibrated_probability_estimate',
            'score_source': 'model', 'scorer_version': SCORER_VERSION,
            'feature_version': request.feature_version,
            'artifact_version': SCORER_VERSION,
            'event_time_utc': request.canonical_transaction.event_time_utc,
            'history_cutoff_exclusive_at': request.history_cutoff_exclusive_at,
            'scored_at': datetime.now(UTC),
            'history_coverage': {'state': snapshot.coverage_state,
                                 'start': snapshot.coverage_start},
            'explanation': explanation,
        }

    def assess(self, request):
        return score_v2(request, self, artifact=self.artifact_reference)
