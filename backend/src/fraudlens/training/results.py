"""Hash-gated, aggregate-only presentation of existing frozen reports.

This module never opens source rows, labels, score CSVs, or runs evaluation.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from fraudlens.contracts import Metric, ModelResults, PartitionResults
from fraudlens.data.features import FEATURE_VERSION
from fraudlens.scoring.model_scorer import MANIFEST_SHA256, MODEL_SHA256, SOURCE_SHA256, THRESHOLD

_ROOT = Path(__file__).resolve().parents[4]
REPORT_SHA256 = '5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb'
PREDICTION_SHA256 = '99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7'
EXPERIMENT_SHA256 = 'a943836322fb2815d5cad85b291719333e21d22c1dcdb5fcbdbb18fbda1316ac'
LINEAGE_SHA256 = '9f1679c767aeab290467bddac764a8658664864751ae3f7e5aaa9a46eea14b25'
VALIDATION_SHA256 = '4d671b97714d816aa28386e1ecf9aa264d324726a51c0a89440bb06218eaf95d'
FEATURE_MANIFEST_SHA256 = '63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f'
AUTHORIZATION_SHA256 = '0000543f0755fb5d714c9f475ee6bd1022664ecde038cf9fadf72cb9dcf58245'
COMPLETION_SHA256 = 'd280179dc955eb994f19d922c82fc3d9515a4fefa87d60cc1bc4662f8b4a0e9f'
PROTOCOL_SHA256 = '7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32'


class ResultsNotAuthorized(ValueError):
    """The exact local test-evaluation approval/receipt is absent or changed."""


class ResultsUnavailable(ValueError):
    """A frozen report is absent, incompatible or unverifiable."""


@dataclass(frozen=True)
class ResultsPaths:
    authorization: Path = _ROOT / 'evidence/tasks/T230-authorization-2026-11-21.md'
    completion: Path = _ROOT / 'evidence/tasks/T230-snapshot-completion-and-evaluation-2026-11-21.md'
    report: Path = _ROOT / 'data/eval/t230-unweighted-test-evaluation-001.json'
    experiment: Path = _ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/experiment.json'
    lineage: Path = _ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/freeze-lineage.json'
    validation: Path = _ROOT / 'data/eval/ibm-day-lightgbm-numeric-diagnostic-001/arms/unweighted/result.json'
    feature_manifest: Path = _ROOT / 'data/processed/t219-ibm-day-60-20-20-v1/manifest.json'
    model: Path = _ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts/selected-unweighted-lightgbm/model.txt'
    model_manifest: Path = _ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts/selected-unweighted-lightgbm/manifest.json'


def _verified_bytes(path: Path, expected: str, maximum: int = 12_000_000) -> bytes:
    try:
        if path.stat().st_size > maximum:
            raise ResultsUnavailable('frozen input exceeds presentation limit')
        raw = path.read_bytes()
    except OSError:
        raise ResultsUnavailable('frozen input unavailable') from None
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ResultsUnavailable('frozen input identity mismatch')
    return raw


def _verified_json(path: Path, expected: str) -> dict:
    raw = _verified_bytes(path, expected)
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ResultsUnavailable('frozen report malformed') from None
    if not isinstance(value, dict):
        raise ResultsUnavailable('frozen report malformed')
    return value


def _metric(name: str, value: object, denominator: int, unit: str = 'ratio') -> Metric:
    return Metric(name=name, value=value, denominator=denominator, unit=unit)


def _partition(partition: str, metrics: dict, coverage: str) -> PartitionResults:
    count = metrics['count']
    positive = metrics['positive_count']
    negative = metrics['negative_count']
    confusion = metrics['confusion_matrix']
    if (type(count) is not int or type(positive) is not int or type(negative) is not int
            or min(count, positive, negative) < 0 or positive + negative != count
            or sum(confusion.values()) != count):
        raise ResultsUnavailable('aggregate counts inconsistent')
    tp, fp, tn, fn = (confusion[key] for key in ('tp', 'fp', 'tn', 'fn'))
    if (any(type(value) is not int or value < 0 for value in (tp, fp, tn, fn))
            or tp + fn != positive or tn + fp != negative):
        raise ResultsUnavailable('confusion counts inconsistent')
    items = [
        _metric('Average Precision', metrics['average_precision'], count),
        _metric('ROC AUC', metrics['roc_auc'], count),
        _metric('Precision', metrics['precision'], tp + fp),
        _metric('Recall', metrics['recall'], positive),
        _metric('F1', metrics['f1'], 2 * tp + fp + fn),
        _metric('Prevalence', metrics['prevalence'], count),
        _metric('Brier score — uncalibrated', metrics['brier_score'], count),
        _metric('True positives', tp, positive, 'rows'),
        _metric('False positives', fp, negative, 'rows'),
        _metric('True negatives', tn, negative, 'rows'),
        _metric('False negatives', fn, positive, 'rows'),
        _metric('Alerts at frozen threshold', tp + fp, count, 'rows'),
    ]
    for k in ('20', '50', '100'):
        denominator = metrics['top_k_denominators'][k]
        items.append(_metric(f'Whole-partition P@{k}', metrics['precision_at'][k], denominator))
        items.append(_metric(f'Whole-partition recall@{k}', metrics['recall_at'][k], positive))
    # Daily alert counts are counts, never daily P@K or a suppression rule.
    for day, alerts in sorted(metrics['daily_alert_counts'].items()):
        items.append(_metric(f'UTC {day} alerts', alerts, count, 'rows'))
    if len(items) > 40:
        raise ResultsUnavailable('too many aggregate metrics')
    return PartitionResults(partition=partition, state='available', synthetic_data=True,
                            coverage_utc=coverage, row_count=count,
                            positive_count=positive, negative_count=negative, metrics=items)


class ResultsService:
    """Read only the two exact authorized aggregate reports and provenance."""

    def __init__(self, paths: ResultsPaths = ResultsPaths()):
        self.paths = paths

    def load(self) -> ModelResults:
        try:
            _verified_bytes(self.paths.authorization, AUTHORIZATION_SHA256, 100_000)
            _verified_bytes(self.paths.completion, COMPLETION_SHA256, 100_000)
        except ResultsUnavailable:
            raise ResultsNotAuthorized('test evaluation authorization unavailable') from None
        report = _verified_json(self.paths.report, REPORT_SHA256)
        experiment = _verified_json(self.paths.experiment, EXPERIMENT_SHA256)
        lineage = _verified_json(self.paths.lineage, LINEAGE_SHA256)
        validation = _verified_json(self.paths.validation, VALIDATION_SHA256)
        features = _verified_json(self.paths.feature_manifest, FEATURE_MANIFEST_SHA256)
        _verified_bytes(self.paths.model, MODEL_SHA256)
        _verified_bytes(self.paths.model_manifest, MANIFEST_SHA256)
        try:
            if (report['explicit_authorization'] is not True
                    or report['authorization_flag'] != '--authorize-test-evaluation I_AUTHORIZE'
                    or report['record_level_test_labels_written'] is not False
                    or report['partition'] != 'research_test'
                    or report['prediction_sha256'] != PREDICTION_SHA256
                    or report['experiment_json_sha256'] != EXPERIMENT_SHA256
                    or report['protocol_sha256'] != PROTOCOL_SHA256
                    or report['threshold_source'] != 'frozen_validation_positive_class_f1'
                    or experiment['selected_model_sha256'] != MODEL_SHA256
                    or experiment['artifact_manifest_sha256'] != MANIFEST_SHA256
                    or experiment['prediction_sha256']['test'] != PREDICTION_SHA256
                    or experiment['freeze_lineage_sha256'] != LINEAGE_SHA256
                    or experiment['protocol_sha256'] != PROTOCOL_SHA256
                    or experiment['source_sha256'] != SOURCE_SHA256
                    or experiment['test_labels_read'] is not False
                    or experiment['showcase_labels_read'] is not False
                    or lineage['frozen_model_sha256'] != MODEL_SHA256
                    or lineage['test_prediction_sha256'] != PREDICTION_SHA256
                    or lineage['validation_result_sha256'] != VALIDATION_SHA256
                    or lineage['threshold'] != THRESHOLD
                    or lineage['feature_version'] != FEATURE_VERSION
                    or lineage['source_sha256'] != SOURCE_SHA256
                    or validation['model_sha256'] != MODEL_SHA256
                    or validation['arm'] != 'unweighted'
                    or validation['score_semantics'] != 'uncalibrated_weighted_training_probabilities'
                    or features['source_sha256'] != SOURCE_SHA256
                    or features['cutoffs_inclusive_utc_day']['validation_end'] != '2022-09-05'
                    or features['cutoffs_inclusive_utc_day']['test_end'] != '2022-09-06T11:12:00+00:00'):
                raise ResultsUnavailable('frozen report lineage mismatch')
            test = report['metrics']
            dev = validation['probability_metrics']
            if (test['threshold'] != THRESHOLD or dev['threshold'] != THRESHOLD
                    or experiment['validation_metrics']['threshold'] != THRESHOLD
                    or test['calibration_status'] != 'uncalibrated_probabilities'
                    or dev['calibration_status'] != 'uncalibrated_probabilities'
                    or test['count'] != experiment['test_prediction_count']
                    or dev['count'] != features['counts']['validation']
                    or test['count'] != features['counts']['test']):
                raise ResultsUnavailable('frozen metric identity mismatch')
            for name in ('average_precision', 'precision', 'recall', 'f1'):
                if experiment['validation_metrics'][name] != dev[name]:
                    raise ResultsUnavailable('validation metric lineage mismatch')
            return ModelResults(
                model_version=f'lightgbm-{MODEL_SHA256[:12]}', feature_version=FEATURE_VERSION,
                dataset_version=f'ibm-hi-small-sha256:{SOURCE_SHA256}', threshold=THRESHOLD,
                calibration_status='not_assessed',
                partitions=[
                    _partition('validation', dev, '2022-09-05 UTC'),
                    _partition('test', test, '2022-09-06 00:00–11:12 UTC'),
                ],
                limitations=[
                    'Synthetic IBM HI-Small data; local capstone integration only.',
                    'Validation was used for model selection; it is not independent generalization evidence.',
                    'Test is one authorized evaluation of the frozen model and threshold; no deployment claim.',
                    'Scores are uncalibrated risk scores, not probabilities of a criminal finding.',
                    'P@K is computed over each whole partition, not per UTC day or analyst capacity.',
                    'Daily alert counts are uncapped; no alerts are suppressed.',
                    'Upstream release and publisher timezone remain limited in the data card.',
                ],
            )
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            if isinstance(exc, ResultsUnavailable):
                raise
            raise ResultsUnavailable('frozen aggregate report incompatible') from None
