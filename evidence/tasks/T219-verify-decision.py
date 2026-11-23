"""Read-only check of the exact T218 aggregate report and human exception."""

import hashlib
from pathlib import Path

from fraudlens.training.protocol import verify_showcase_exception

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'data/processed/t218-hi-small-b19d39f5/aggregate-audit.json'
DECISION = ROOT / 'prompts/development/002-T218-showcase-decision.md'
SOURCE = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
BOUNDARY = 'b1300cad3b94bb9c2325a221c2352ca327dc2c6cf0cd1268d0bdb39a0928a728'
REPORT_SHA = 'c27cdcfc45c146a504454019414833e93f48e020f76cbad3197ebdeeb902907f'
DECISION_SHA = '8cc3d56a3f48311fa515f71bd44cbfcdce26fb0702169181a937e5a8aa1e1797'


def main() -> None:
    report_bytes = REPORT.read_bytes()
    decision_sha = hashlib.sha256(DECISION.read_bytes()).hexdigest()
    protocol = {
        'dataset_sha256': SOURCE,
        'boundary_sha256': BOUNDARY,
        'allowed_prevalence': {'minimum_ratio': 0.75, 'maximum_ratio': 1.25},
        'audit_decision': {
            'kind': 'showcase_ratio_diagnostic_after_human_review',
            'source_sha256': SOURCE,
            'boundary_sha256': BOUNDARY,
            'audit_report_sha256': REPORT_SHA,
            'decision_record_sha256': DECISION_SHA,
            'showcase_role': 'demo_only_record_labels_unread',
        },
    }
    verify_showcase_exception(protocol, {
        'audit_report_bytes': report_bytes,
        'decision_record_sha256': decision_sha,
    })
    print('T219 original aggregate audit and human exception checks passed')
    print(f'audit_report_sha256={REPORT_SHA}')
    print(f'decision_record_sha256={DECISION_SHA}')


if __name__ == '__main__':
    main()
