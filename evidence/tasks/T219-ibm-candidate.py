"""Build a verifiable, unfrozen FR-021 candidate for the IBM-style split."""

import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.data.research_split import plan_ibm_day_split

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/processed'
CANDIDATE = ROOT / 'specs/002-data-and-risk-scoring/t219-training-protocol.candidate.json'
OUTPUT = ROOT / 'specs/002-data-and-risk-scoring/t219-training-protocol.ibm-60-20-20.candidate.json'
AGGREGATE = DATA / 't218-hi-small-b19d39f5/aggregate-audit.json'
FEATURES = DATA / 't219-ibm-day-60-20-20-v1'
LABELS = DATA / 't219-ibm-day-60-20-20-labels-v1'
RESEARCH_METHOD = 'whole_utc_day_boundaries_minimize_max_relative_target_share_error'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
PARENT_FEATURE_SHA = '5ca1660eb582b68b27f58241b115eea5d69d3feb77f78f9fe46c12611b4f517a'
AGGREGATE_SHA = 'c27cdcfc45c146a504454019414833e93f48e020f76cbad3197ebdeeb902907f'
BOUNDARY_SHA = 'b1300cad3b94bb9c2325a221c2352ca327dc2c6cf0cd1268d0bdb39a0928a728'


def distribution(rows: int, positives: int) -> dict:
    return {
        'rows': rows,
        'positive': positives,
        'negative': rows - positives,
        'prevalence': positives / rows,
    }


def main() -> None:
    protocol = json.loads(CANDIDATE.read_bytes())
    feature_manifest = json.loads((FEATURES / 'manifest.json').read_bytes())
    label_manifest = json.loads((LABELS / 'manifest.json').read_bytes())
    audit = json.loads(AGGREGATE.read_bytes())
    if (sha256_file(AGGREGATE) != AGGREGATE_SHA
            or sha256_file(DATA / 't210-hi-small-temporal-v1/manifest.json')
            != PARENT_FEATURE_SHA
            or feature_manifest.get('source_sha256') != SOURCE_SHA
            or feature_manifest.get('parent_feature_manifest_sha256') != PARENT_FEATURE_SHA
            or label_manifest.get('source_sha256') != SOURCE_SHA
            or label_manifest.get('feature_manifest_sha256')
            != sha256_file(FEATURES / 'manifest.json')
            or label_manifest.get('scope') != 'train_and_validation_only'):
        raise ValueError('source, parent feature, aggregate audit or label provenance mismatch')
    for part, expected_hash in label_manifest['files'].items():
        if sha256_file(LABELS / f'{part}.jsonl') != expected_hash:
            raise ValueError(f'{part} training-label file checksum mismatch')
    if (audit.get('source_sha256') != SOURCE_SHA
            or audit.get('boundary_sha256') != BOUNDARY_SHA
            or audit.get('tolerance', {}).get('pass') is not False):
        raise ValueError('aggregate audit source/boundary/result identity mismatch')
    for part, expected_hash in feature_manifest['files'].items():
        if sha256_file(FEATURES / f'{part}.jsonl') != expected_hash:
            raise ValueError(f'{part} research feature checksum mismatch')
    def feature_rows():
        for part in ('train', 'validation', 'test'):
            with (FEATURES / f'{part}.jsonl').open(encoding='utf-8') as stream:
                yield from (json.loads(line) for line in stream)

    recomputed = plan_ibm_day_split(feature_rows())
    expected_split = feature_manifest['partition_scoreable_id_sha256']
    for part in ('train', 'validation', 'test'):
        digest = hashlib.sha256(''.join(
            f'{identity}\n' for identity in getattr(recomputed, f'{part}_ids')
        ).encode()).hexdigest()
        if digest != expected_split[part] or recomputed.counts[part] != feature_manifest['counts'][part]:
            raise ValueError(f'{part} research split does not independently reproduce')
    if (recomputed.train_end_utc.isoformat()
            != feature_manifest['cutoffs_inclusive_utc_day']['train_end']
            or recomputed.validation_end_utc.isoformat()
            != feature_manifest['cutoffs_inclusive_utc_day']['validation_end']):
        raise ValueError('research split day cutoffs do not reproduce')
    train_end = date.fromisoformat(
        feature_manifest['cutoffs_inclusive_utc_day']['train_end'])
    validation_end = date.fromisoformat(
        feature_manifest['cutoffs_inclusive_utc_day']['validation_end'])
    daily = audit['results']['development_daily']
    by_partition = {'train': [0, 0], 'validation': [0, 0], 'test': [0, 0]}
    for day_record in daily:
        day = date.fromisoformat(day_record['utc_day'])
        partition = ('train' if day <= train_end else
                     'validation' if day <= validation_end else 'test')
        by_partition[partition][0] += day_record['scoreable_count']
        by_partition[partition][1] += day_record['positive_count']
    if {part: values[0] for part, values in by_partition.items()} != feature_manifest['counts']:
        raise ValueError('daily aggregate counts do not match versioned research features')
    if sum(values[1] for values in by_partition.values()) != audit['results'][
            'overall_development_positive_count']:
        raise ValueError('daily aggregate positives do not reconcile')
    if label_manifest['counts'] != {
        part: {'rows': values[0], 'positive': values[1], 'negative': values[0] - values[1]}
        for part, values in by_partition.items() if part != 'test'
    }:
        raise ValueError('restricted train/validation labels differ from approved aggregates')

    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, check=True,
                                capture_output=True, text=True).stdout.strip())
    code_files = [
        'backend/src/fraudlens/data/research_split.py',
        'backend/src/fraudlens/data/research_labels.py',
        'backend/src/fraudlens/training/evaluation.py',
        'backend/src/fraudlens/training/candidates.py',
        'backend/src/fraudlens/training/local_run.py',
        'backend/src/fraudlens/training/evaluate_saved.py',
        'backend/src/fraudlens/training/protocol.py',
        'evidence/tasks/T230-evaluate.py',
        'evidence/tasks/T219-ibm-split.py',
        'evidence/tasks/T219-ibm-labels.py',
        'backend/tests/unit/test_research_split.py',
        'backend/tests/unit/test_research_labels.py',
        'backend/tests/unit/test_local_run.py',
        'backend/tests/unit/test_lightgbm_matrices.py',
        'backend/tests/unit/test_evaluation.py',
        'backend/tests/unit/test_research_protocol.py',
    ]
    protocol.update({
        'format': 'fraudlens-fr021-training-protocol-v2',
        'split_method': {
            'reference': 'IBM Multi-GNN Appendix E.1 AML day split',
            'reference_urls': [
                'https://arxiv.org/abs/2306.11586',
                'https://github.com/IBM/Multi-GNN/blob/main/data_loading.py',
                'https://github.com/IBM/Multi-GNN/blob/main/format_kaggle_files.py',
            ],
            'method': RESEARCH_METHOD,
            'targets': {'train': 0.6, 'validation': 0.2, 'test': 0.2},
            'timezone': 'UTC, using the existing project UTC assumption for this exact copy',
            'label_values_used_for_boundaries': False,
            'whole_day_granularity': True,
            'scope': 'scoreable development rows only; warm-up and showcase remain excluded',
            'limitation': 'whole-day granularity yields 62.03/25.61/12.36 shares on this five-day development period',
        },
        'historical_partition_counts': protocol['partition_counts'],
        'historical_partition_boundaries': protocol['partition_boundaries'],
        'historical_partition_scoreable_id_sha256': protocol['partition_scoreable_id_sha256'],
        'research_feature_manifest_sha256': sha256_file(FEATURES / 'manifest.json'),
        'research_label_manifest_sha256': sha256_file(LABELS / 'manifest.json'),
        'research_partition_counts': feature_manifest['counts'],
        'research_partition_scoreable_id_sha256': feature_manifest[
            'partition_scoreable_id_sha256'],
        'partition_counts': {
            **protocol['partition_counts'],
            'train_count': feature_manifest['counts']['train'],
            'validation_count': feature_manifest['counts']['validation'],
            'test_count': feature_manifest['counts']['test'],
        },
        'partition_boundaries': {
            **protocol['partition_boundaries'],
            'research_train_end_utc_day_inclusive': train_end.isoformat(),
            'research_validation_end_utc_day_inclusive': validation_end.isoformat(),
            'research_test_end_utc': feature_manifest['cutoffs_inclusive_utc_day'][
                'test_end'],
        },
        'class_distribution': {
            part: distribution(*values) for part, values in by_partition.items()
        },
        'class_distribution_source': {
            'kind': 'existing_t218_development_daily_aggregate',
            'sha256': sha256_file(AGGREGATE),
            'test_record_labels_read_for_v2': False,
        },
        'fr018': {
            'minimum_positive_gate': False,
            'prevalence_ratio_gate': False,
            'class_distribution_is_diagnostic': True,
            'training_single_class': 'refuse fitting',
            'evaluation_missing_class': 'report affected metrics as null with explicit denominators',
            'historical_audit_sha256': audit['format'] and sha256_file(AGGREGATE),
            'historical_failed_result_preserved': True,
        },
        'metrics': [
            'positive_class_f1_at_validation_selected_threshold', 'precision', 'recall',
            'confusion_matrix', 'precision_recall_curve', 'average_precision',
            'roc_auc_when_both_classes_exist', 'positive_and_negative_denominators',
            'positive_class_prevalence', 'brier_score_uncalibrated_probabilities',
            'precision_recall_at_20_50_100_with_denominators', 'daily_alert_counts',
        ],
        'metric_undefined_policy': {
            'no_validation_positives': 'skip model ranking and threshold selection; report undefined positive-class metrics',
            'single_class_roc_auc': 'null',
            'no_positive_recall_and_average_precision': 'null',
            'test': 'evaluate only from frozen test predictions and separate explicit authorization',
        },
        'reproducibility': {
            'seed': 42,
            'python': sys.version.split()[0],
            'lightgbm': '4.7.0',
            'scikit_learn': '1.9.1',
            'candidate_grid_sha256': protocol['model_choices_sha256'],
            'code_revision_at_candidate_generation': revision,
            'working_tree_dirty_at_candidate_generation': dirty,
            'implementation_file_sha256': {path: sha256_file(ROOT / path)
                                           for path in code_files},
            'candidate_builder_sha256': sha256_file(Path(__file__)),
            'thread_count': 'configurable --n-jobs; default 4; actual value recorded per run',
            'lightgbm_deterministic': True,
            'lightgbm_force_col_wise': True,
            'upstream_dataset_revision': 'unknown',
            'acquisition_date': 'unknown',
        },
        'resource_configuration': {
            'feature_and_label_publication_limits': 'recorded in associated manifests/evidence',
            'fit_thread_count': 'operator-configurable; no physical-core gate',
            'fit_resource_usage': 'not measured because no model fit was run',
        },
        'protocol_status': 'candidate_pending_explicit_human_review',
        'model_fitting_performed': False,
    })
    protocol['historical_t218_audit'] = {
        'audit_report_sha256': protocol.pop('audit_report_sha256'),
        'audit_passed': protocol.pop('audit_passed'),
        'decision': protocol.pop('audit_decision'),
        'retired_thresholds': protocol.pop('allowed_prevalence'),
    }
    fit_limits = protocol['resource_ceilings']['fit']
    fit_limits['n_jobs'] = 'configurable CLI --n-jobs; default 4'
    fit_limits['physical_core_count'] = 'record if observed; not a gate'
    OUTPUT.write_bytes(canonical_json_bytes(protocol) + b'\n')
    print(json.dumps({
        'candidate': str(OUTPUT.relative_to(ROOT)),
        'canonical_sha256': hashlib.sha256(canonical_json_bytes(protocol)).hexdigest(),
        'file_sha256': sha256_file(OUTPUT),
        'counts': feature_manifest['counts'],
        'class_distribution': protocol['class_distribution'],
        'cutoffs': protocol['partition_boundaries'],
        'approval': 'not approved or frozen',
    }, sort_keys=True))


if __name__ == '__main__':
    main()
