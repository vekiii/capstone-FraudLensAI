"""Opt-in, label-free adapter for one authenticated local LightGBM artifact."""

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fraudlens.contracts import PredictionResult
from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
from fraudlens.scoring import Scorer
from fraudlens.scoring.artifacts import ArtifactError, TrustedArtifact, read_verified_artifact

MODEL_SHA256 = '3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c'
MANIFEST_SHA256 = 'c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45'
SOURCE_SHA256 = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
PROTOCOL_SHA256 = '7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32'
FEATURE_MANIFEST_SHA256 = '63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f'
THRESHOLD = 0.2489517623052024
ARTIFACT_ID = 'selected-unweighted-lightgbm'
_CANONICAL_ID = re.compile(r'ibm-hi-small:[0-9a-f]{64}:row:[1-9][0-9]*\Z')


def valid_canonical_id(value: str) -> bool:
    return isinstance(value, str) and _CANONICAL_ID.fullmatch(value) is not None


class ModelUnavailable(ValueError):
    """Model inputs, output, or provenance cannot be trusted."""


@dataclass(frozen=True)
class FeatureTransaction:
    transaction_id: str
    occurred_at_utc: str
    features: dict[str, Any]
    is_scoreable: bool = True


class FeatureStore:
    """Read only the pinned, label-free research feature snapshot."""

    def __init__(self, feature_root: Path):
        self.root = feature_root
        self.paths = tuple(feature_root / f'{part}.jsonl'
                           for part in ('train', 'validation', 'test'))
        self._verify()

    def _verify(self) -> None:
        try:
            with (self.root / 'manifest.json').open('rb') as stream:
                raw = stream.read()
            if hashlib.sha256(raw).hexdigest() != FEATURE_MANIFEST_SHA256:
                raise ModelUnavailable('feature manifest identity mismatch')
            manifest = json.loads(raw)
            if (set(manifest['files']) != {'train', 'validation', 'test'}
                    or manifest['source_sha256'] != SOURCE_SHA256):
                raise ModelUnavailable('feature manifest contract mismatch')
            for path in self.paths:
                with path.open('rb') as stream:
                    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                if digest != manifest['files'][path.stem]:
                    raise ModelUnavailable('feature snapshot identity mismatch')
            self.expected_files = manifest['files']
        except (OSError, ValueError, KeyError, TypeError):
            raise ModelUnavailable('feature snapshot unavailable') from None

    def get(self, transaction_id: str) -> FeatureTransaction | None:
        if not valid_canonical_id(transaction_id):
            return None
        needle = transaction_id.encode('utf-8')
        try:
            for path in self.paths:
                found = None
                digest = hashlib.sha256()
                with path.open('rb') as stream:
                    for line in stream:
                        digest.update(line)
                        if needle not in line:
                            continue
                        item = json.loads(line)
                        if (set(item) != {'transaction_id', 'occurred_at_utc', 'features'}
                                or item['transaction_id'] != transaction_id):
                            raise ModelUnavailable('feature row identity mismatch')
                        if found is not None:
                            raise ModelUnavailable('duplicate transaction identity')
                        found = FeatureTransaction(**item)
                if digest.hexdigest() != self.expected_files[path.stem]:
                    raise ModelUnavailable('feature snapshot changed during lookup')
                if found is not None:
                    return found
        except (OSError, ValueError, TypeError):
            raise ModelUnavailable('feature snapshot unreadable') from None
        return None


class ModelScorer(Scorer[FeatureTransaction, PredictionResult]):
    """Implements the replaceable scorer's score method for Feature 002 rows."""

    def __init__(self, artifact_root: Path):
        try:
            import lightgbm as lgb

            from fraudlens.training.boundaries import TrainingPreprocessor
        except ImportError as exc:
            raise ModelUnavailable('model runtime unavailable') from exc
        trusted = TrustedArtifact(MANIFEST_SHA256, SOURCE_SHA256, PROTOCOL_SHA256,
                                  FEATURE_VERSION, FEATURE_ORDER)
        try:
            model_bytes, manifest = read_verified_artifact(artifact_root, ARTIFACT_ID, trusted)
            if (hashlib.sha256(model_bytes).hexdigest() != MODEL_SHA256
                    or manifest['threshold'] != THRESHOLD):
                raise ArtifactError('selected model or threshold mismatch')
            booster = lgb.Booster(model_str=model_bytes.decode('utf-8'))
            if booster.num_feature() != 32:
                raise ArtifactError('model feature width mismatch')
        except (ArtifactError, ValueError, UnicodeDecodeError, lgb.basic.LightGBMError) as exc:
            raise ModelUnavailable('model artifact unavailable or incompatible') from exc
        self.booster = booster
        self.manifest = manifest
        self.preprocessor = TrainingPreprocessor(
            tuple(manifest['currency_vocabulary']), tuple(manifest['format_vocabulary']))

    def score(self, transaction: FeatureTransaction) -> PredictionResult:
        import lightgbm as lgb
        import numpy as np

        from fraudlens.training.boundaries import _validate_row
        if not isinstance(transaction, FeatureTransaction) or not transaction.is_scoreable:
            raise ModelUnavailable('transaction is not scoreable')
        if not valid_canonical_id(transaction.transaction_id):
            raise ModelUnavailable('invalid transaction identity')
        try:
            instant = datetime.fromisoformat(transaction.occurred_at_utc)
            if instant.tzinfo is None or instant.utcoffset().total_seconds() != 0:
                raise ValueError('event time must be UTC')
            row = {'transaction_id': transaction.transaction_id, **transaction.features}
            _validate_row(row)
            transformed = self.preprocessor.transform((row,))
            matrix = self.preprocessor.matrix(transformed)
            if matrix.shape != (1, 32):
                raise ValueError('model matrix width mismatch')
            prediction = np.asarray(self.booster.predict(matrix, num_threads=4), dtype=np.float64)
            if prediction.shape != (1,):
                raise ValueError('model output shape mismatch')
            value = float(prediction[0])
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError('model score outside [0,1]')
            facts = transaction.features
            explanation = (
                'Synthetic AML risk score for this transaction. Observed features: '
                f"sender prior 24h count {facts['sender_out_count_24h']}; "
                f"receiver prior 24h count {facts['receiver_in_count_24h']}; "
                f"payment currency {facts['current_payment_currency']}; "
                f"payment format {facts['current_payment_format']}. "
                'These facts are not proof of laundering; an analyst makes the final decision.'
            )
            return PredictionResult(
                transaction_id=transaction.transaction_id, risk_score=value,
                review_status=('review_recommended' if value >= THRESHOLD else 'below_threshold'),
                source='model', model_version=f'lightgbm-{MODEL_SHA256[:12]}',
                feature_version=FEATURE_VERSION, synthetic_data=True,
                scored_at=instant.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
                explanation=explanation,
            )
        except (KeyError, TypeError, ValueError, OverflowError,
                lgb.basic.LightGBMError) as exc:
            raise ModelUnavailable('transaction features or score are invalid') from exc
