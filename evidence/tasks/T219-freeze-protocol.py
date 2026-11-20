"""Build a reviewable FR-021 protocol candidate from frozen local artifacts.

This does not approve the resulting hash or fit a model. Run after the verified
feature publication succeeds, from the repository root with PYTHONPATH=backend/src.
"""

import json
from pathlib import Path

from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
from fraudlens.data.manifest import (
    canonical_json_bytes,
    sha256_bytes,
    sha256_file,
    verify_completed_snapshot,
)
from fraudlens.training.protocol import verify_prefit_protocol

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / 'specs/002-data-and-risk-scoring'
PROCESSED = ROOT / 'data/processed'
OUTPUT = SPEC / 't219-training-protocol.candidate.json'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
BOUNDARY_SHA = 'b1300cad3b94bb9c2325a221c2352ca327dc2c6cf0cd1268d0bdb39a0928a728'
SNAPSHOT_SHA = '38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88'
ACCEPTED_SHA = '8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba'
ID_REPORT_SHA = 'e283752549b1f8f6b0bc6b21ce9569854cf6c4cdb593636ab3dc7381466dbf60'
AUDIT_SHA = 'c27cdcfc45c146a504454019414833e93f48e020f76cbad3197ebdeeb902907f'
SHOWCASE_DECISION_SHA = '8cc3d56a3f48311fa515f71bd44cbfcdce26fb0702169181a937e5a8aa1e1797'
FITTING_DECISION_SHA = '672a512d38c03aa6a11b7c37c15525c399e480d2e20988ff64eb87a90f291153'
CHOICES_SHA = '3ee00698879c428a6a4ca46bff6564da6e68c48363daf0ba9b5dba4da3b59f5e'


def _checked_json(path: Path, expected_sha: str) -> dict:
    if sha256_file(path) != expected_sha:
        raise ValueError(f'frozen input hash mismatch: {path.name}')
    return json.loads(path.read_bytes())


def main() -> None:
    if OUTPUT.exists():
        raise ValueError('protocol candidate already exists; refusing overwrite')
    if (ROOT / 'data/raw/HI-Small_Trans.csv').stat().st_size != 475_664_283:
        raise ValueError('source size mismatch')
    if sha256_file(ROOT / 'data/raw/HI-Small_Trans.csv') != SOURCE_SHA:
        raise ValueError('source checksum mismatch')
    snapshot_root = PROCESSED / 't210-hi-small-b19d39f5'
    snapshot = verify_completed_snapshot(snapshot_root)
    if (sha256_file(snapshot_root / 'manifest.json') != SNAPSHOT_SHA
            or snapshot['source_sha256'] != SOURCE_SHA
            or snapshot['accepted_count'] != 5_078_345
            or next(item['sha256'] for item in snapshot['processed_files']
                    if item['name'] == 'accepted.jsonl') != ACCEPTED_SHA):
        raise ValueError('snapshot identity mismatch')
    boundary = _checked_json(
        PROCESSED / 't218-hi-small-b19d39f5/boundaries.json', BOUNDARY_SHA,
    )
    ids = _checked_json(
        PROCESSED / 't219-hi-small-b19d39f5/partition-id-hashes.json', ID_REPORT_SHA,
    )
    choices = json.loads((SPEC / 't221-model-choices.json').read_bytes())
    if sha256_bytes(canonical_json_bytes(choices)) != CHOICES_SHA:
        raise ValueError('frozen model choices mismatch')
    feature_root = PROCESSED / 't210-hi-small-temporal-v1'
    feature_manifest = json.loads((feature_root / 'manifest.json').read_bytes())
    if (feature_manifest.get('format') != 'hi-small-training-features-v1'
            or feature_manifest.get('source_sha256') != SOURCE_SHA
            or feature_manifest.get('feature_version') != FEATURE_VERSION
            or feature_manifest.get('feature_order') != list(FEATURE_ORDER)
            or feature_manifest.get('partition_scoreable_id_sha256')
            != ids['partition_scoreable_id_sha256']
            or set(feature_manifest.get('files', {}))
            != {'train', 'validation', 'test', 'showcase'}
            or feature_manifest.get('counts') != {
                name: boundary[f'{name}_count']
                for name in ('warmup', 'train', 'validation', 'test', 'showcase')
            }):
        raise ValueError('published feature manifest contract mismatch')
    for name, digest in feature_manifest['files'].items():
        if sha256_file(feature_root / f'{name}.jsonl') != digest:
            raise ValueError(f'published {name} features hash mismatch')
    labels_root = PROCESSED / 't210-hi-small-train-validation-labels-v1'
    labels_manifest = json.loads((labels_root / 'manifest.json').read_bytes())
    if (labels_manifest.get('format') != 'hi-small-restricted-training-labels-v1'
            or labels_manifest.get('source_sha256') != SOURCE_SHA
            or labels_manifest.get('feature_manifest_sha256')
            != sha256_file(feature_root / 'manifest.json')
            or labels_manifest.get('label_scope') != 'train_and_validation_only'
            or labels_manifest.get('counts') != {
                'train': boundary['train_count'],
                'validation': boundary['validation_count'],
            }
            or labels_manifest.get('partition_scoreable_id_sha256') != {
                name: ids['partition_scoreable_id_sha256'][name]
                for name in ('train', 'validation')
            }
            or set(labels_manifest.get('files', {})) != {'train', 'validation'}
            or {path.name for path in labels_root.iterdir()}
            != {'manifest.json', 'train.jsonl', 'validation.jsonl'}):
        raise ValueError('restricted label manifest contract mismatch')
    for name, digest in labels_manifest['files'].items():
        if sha256_file(labels_root / f'{name}.jsonl') != digest:
            raise ValueError(f'published {name} labels hash mismatch')
    audit_bytes = (PROCESSED / 't218-hi-small-b19d39f5/aggregate-audit.json').read_bytes()
    if sha256_bytes(audit_bytes) != AUDIT_SHA:
        raise ValueError('original aggregate audit checksum mismatch')
    showcase_decision = (ROOT / 'prompts/development/002-T218-showcase-decision.md').read_bytes()
    fitting_decision = (ROOT / 'prompts/development/002-T228-input-clarification.md').read_bytes()
    if (sha256_bytes(showcase_decision) != SHOWCASE_DECISION_SHA
            or sha256_bytes(fitting_decision) != FITTING_DECISION_SHA):
        raise ValueError('human decision-record checksum mismatch')
    if (boundary['source_sha256'] != SOURCE_SHA
            or boundary['snapshot_manifest_sha256'] != SNAPSHOT_SHA
            or ids['source_sha256'] != SOURCE_SHA
            or ids['boundary_sha256'] != BOUNDARY_SHA):
        raise ValueError('boundary or partition report provenance mismatch')
    protocol = {
        'format': 'fraudlens-fr021-training-protocol-v1',
        'dataset_sha256': SOURCE_SHA,
        'boundary_sha256': BOUNDARY_SHA,
        'snapshot_manifest_sha256': SNAPSHOT_SHA,
        'accepted_snapshot_sha256': ACCEPTED_SHA,
        'partition_hash_report_sha256': ID_REPORT_SHA,
        'audit_report_sha256': AUDIT_SHA,
        'feature_manifest_sha256': sha256_file(feature_root / 'manifest.json'),
        'training_labels_manifest_sha256': sha256_file(labels_root / 'manifest.json'),
        'partition_scoreable_id_sha256': ids['partition_scoreable_id_sha256'],
        'timezone_policy': 'naive_source_minute_as_UTC_project_assumption',
        'warmup_rule': '[t0,t0+24h)_history_only',
        'feature_version': FEATURE_VERSION,
        'feature_order': list(FEATURE_ORDER),
        'partition_boundaries': {
            key: boundary[key] for key in (
                't0_utc', 'warmup_end_exclusive_utc', 'train_end_utc',
                'validation_end_utc', 'development_end_utc',
            )
        },
        'partition_counts': {
            key: boundary[key] for key in (
                'accepted_count', 'warmup_count', 'development_count',
                'train_count', 'validation_count', 'test_count', 'showcase_count',
            )
        },
        'allowed_prevalence': {'minimum_ratio': 0.75, 'maximum_ratio': 1.25},
        'seed': 42,
        'tie_rules': {
            'partition': 'earlier_whole_timestamp_boundary_then_source_row_number',
            'selection': choices['selection'],
        },
        'preprocessing': choices['preprocessing'],
        'imbalance_option': choices['imbalance'],
        'candidate_grid': choices['candidates'],
        'metrics': choices['report_metrics'],
        'threshold_objective': choices['selection']['threshold_objective'],
        'resource_ceilings': {
            'feature_publication': {
                'max_rows': 5_078_345,
                'initial_free_disk_bytes_min': 20 * 1024**3,
                'ending_free_disk_bytes_min': 10 * 1024**3,
                'peak_working_set_bytes_max': 8 * 1024**3,
                'elapsed_seconds_max': 45 * 60,
            },
            'label_publication': {
                'scope': 'train_and_validation_only',
                'initial_free_disk_bytes_min': 20 * 1024**3,
                'ending_free_disk_bytes_min': 10 * 1024**3,
                'peak_working_set_bytes_max': 8 * 1024**3,
                'elapsed_seconds_max': 30 * 60,
            },
            'fit': choices['budget'],
        },
        'label_rules': choices['label_access'],
        'showcase_role': 'demo_only_record_labels_unread',
        'audit_passed': False,
        'audit_decision': {
            'kind': 'showcase_ratio_diagnostic_after_human_review',
            'source_sha256': SOURCE_SHA,
            'boundary_sha256': BOUNDARY_SHA,
            'audit_report_sha256': AUDIT_SHA,
            'decision_record_sha256': SHOWCASE_DECISION_SHA,
            'showcase_role': 'demo_only_record_labels_unread',
        },
        'provenance_complete': False,
        'provenance_decision': {
            'kind': 'exact_local_copy_fitting_after_team_approval',
            'source_sha256': SOURCE_SHA,
            'snapshot_manifest_sha256': SNAPSHOT_SHA,
            'decision_record_sha256': FITTING_DECISION_SHA,
        },
        'model_choices_sha256': CHOICES_SHA,
    }
    canonical = canonical_json_bytes(protocol)
    observed = {
        key: protocol[key] for key in (
            'dataset_sha256', 'boundary_sha256', 'snapshot_manifest_sha256',
            'accepted_snapshot_sha256', 'partition_hash_report_sha256',
            'audit_report_sha256', 'feature_manifest_sha256',
            'training_labels_manifest_sha256',
            'partition_scoreable_id_sha256',
        )
    }
    observed.update({
        'audit_report_bytes': audit_bytes,
        'decision_record_sha256': sha256_bytes(showcase_decision),
        'fitting_decision_record_bytes': fitting_decision,
    })
    # Structural rehearsal with a self-computed digest is not human approval.
    verify_prefit_protocol(protocol, sha256_bytes(canonical), observed)
    OUTPUT.write_bytes(canonical + b'\n')
    print(json.dumps({
        'candidate_path': str(OUTPUT.relative_to(ROOT)),
        'canonical_sha256': sha256_bytes(canonical),
        'file_sha256': sha256_file(OUTPUT),
        'feature_manifest_sha256': protocol['feature_manifest_sha256'],
        'approval_status': 'pending',
    }, sort_keys=True))


if __name__ == '__main__':
    main()
