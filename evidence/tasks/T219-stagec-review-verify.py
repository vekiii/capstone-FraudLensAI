"""Read-only receiving-Mac check for the revised FR-021 review candidate.

Hashes transferred files without parsing any record-level label values.
Does not run the historical candidate builder or fit a model.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.training.local_run import _load_protocol
from fraudlens.training.protocol import verify_research_protocol

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'specs/002-data-and-risk-scoring/t219-training-protocol.ibm-60-20-20.candidate.json'
FEATURES = ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'
LABELS = ROOT / 'data/processed/t219-ibm-day-60-20-20-labels-v1'
METHOD_FIELDS = (
    'candidate_grid', 'seed', 'preprocessing', 'imbalance_option',
    'threshold_objective', 'tie_rules', 'split_method',
    'partition_boundaries', 'partition_counts', 'research_partition_counts',
    'research_partition_scoreable_id_sha256', 'label_rules', 'metrics',
    'feature_order', 'feature_version', 'class_distribution', 'resource_ceilings',
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--expected-canonical', required=True)
    parser.add_argument('--parent', type=Path, default=OLD,
                        help='immediate parent candidate; defaults to original IBM-day candidate')
    args = parser.parse_args()
    candidate_path = args.candidate.resolve(strict=True)
    parent_path = args.parent.resolve(strict=True)
    old_raw = parent_path.read_bytes()
    old = json.loads(old_raw)
    raw = candidate_path.read_bytes()
    candidate = json.loads(raw)
    canonical = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()
    if canonical != args.expected_canonical:
        raise ValueError('candidate canonical digest differs from independent expectation')
    if _load_protocol(candidate_path, args.expected_canonical)[1] != canonical:
        raise ValueError('runner protocol loader rejected candidate')
    lineage = candidate['candidate_lineage']
    if (lineage['parent_file'] != parent_path.name
            or lineage['parent_file_sha256'] != hashlib.sha256(old_raw).hexdigest()
            or lineage['parent_canonical_sha256']
            != hashlib.sha256(canonical_json_bytes(old)).hexdigest()):
        raise ValueError('parent candidate identity mismatch')
    if (candidate['format'] != old['format']
            or candidate['protocol_status'] != 'candidate_pending_explicit_human_review'
            or any(candidate[key] != old[key] for key in METHOD_FIELDS)):
        raise ValueError('format, review status or methodology changed')
    feature_sha = sha256_file(FEATURES / 'manifest.json')
    label_sha = sha256_file(LABELS / 'manifest.json')
    features = json.loads((FEATURES / 'manifest.json').read_bytes())
    labels = json.loads((LABELS / 'manifest.json').read_bytes())
    for directory, manifest in ((FEATURES, features), (LABELS, labels)):
        for part, expected in manifest['files'].items():
            if sha256_file(directory / f'{part}.jsonl') != expected:
                raise ValueError(f'{directory.name}/{part} checksum mismatch')
    if (feature_sha != candidate['research_feature_manifest_sha256']
            or label_sha != candidate['research_label_manifest_sha256']
            or labels['feature_manifest_sha256'] != feature_sha):
        raise ValueError('transferred manifest binding mismatch')
    verify_research_protocol(candidate, canonical, features, labels, feature_sha, label_sha)
    implementation = candidate['reproducibility']['implementation_file_sha256']
    for name, expected in implementation.items():
        if sha256_file(ROOT / name) != expected:
            raise ValueError(f'implementation checksum mismatch: {name}')
    if sha256_file(ROOT / 'uv.lock') != candidate['reproducibility']['uv_lock_sha256']:
        raise ValueError('locked environment identity mismatch')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if head != candidate['reproducibility']['code_revision_at_candidate_generation']:
        raise ValueError('Git HEAD differs from candidate')
    print(json.dumps({
        'canonical_sha256': canonical,
        'file_sha256': hashlib.sha256(raw).hexdigest(),
        'feature_manifest_sha256': feature_sha,
        'feature_files_checked': len(features['files']),
        'label_manifest_sha256': label_sha,
        'label_files_checked': len(labels['files']),
        'implementation_files_checked': len(implementation),
        'methodology_unchanged': True,
        'verifier': 'passed',
    }, sort_keys=True))


if __name__ == '__main__':
    main()
