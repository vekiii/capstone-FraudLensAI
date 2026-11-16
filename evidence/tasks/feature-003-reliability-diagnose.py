"""Read committed aggregate evidence only; no .env, held-out text or API calls."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'evidence/tasks/feature-003-reliability-v2-baseline.json'
EXPECTED_SOURCE_CHANGES = {
    'backend/src/fraudlens/investigation/provider.py',
    'backend/src/fraudlens/investigation/workflow.py',
    'backend/src/fraudlens/investigation/retrieval.py',
}


def main():
    baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
    missing, changed = [], []
    for name, expected in baseline['files'].items():
        path = ROOT / name
        if not path.is_file():
            missing.append(name)
        elif hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest() != expected:
            changed.append(name)
    unexpected = sorted(set(changed) - EXPECTED_SOURCE_CHANGES)
    live = json.loads((ROOT / 'evidence/tasks/feature-003-live-results.json').read_text(encoding='utf-8'))
    roles = {}
    for role, values in live['roles'].items():
        rows = values['rows']
        roles[role] = dict(
            count=len(rows),
            states=dict(Counter(row['state'] for row in rows)),
            failure_codes=dict(Counter(row['failure']['code'] for row in rows if row['failure'])),
            successful_within_90=values['successful_within_90'],
            all_terminal_within_120=values['all_terminal_within_120'],
            maximum_seconds=max(row['seconds'] for row in rows),
        )
    result = dict(
        kind='offline_aggregate_diagnosis_not_new_evaluation',
        baseline_commit=baseline['baseline_commit'],
        protected_files=len(baseline['files']),
        expected_changed_runtime_sources=sorted(set(changed) & EXPECTED_SOURCE_CHANGES),
        unexpected_changes=unexpected,
        missing_baseline_files=missing,
        protected_artifact_integrity='PASS' if not unexpected and not missing else 'FAIL',
        raw_archives_present={name: (ROOT / 'evals/results/feature-003' / name).is_dir()
                              for name in baseline['raw_archives_present']},
        original_generation_transport_attempts=live['transport_attempts'],
        historical_generation=roles,
        new_provider_calls=0,
        limitations=['Aggregate codes cannot establish the precise rejected field or prose.',
                     'Historical outlier cause remains unknown without raw timing/transport traces.',
                     'Current source is a post-evaluation revision, not the old frozen runtime.'],
    )
    print(json.dumps(result, indent=2))
    return 0 if result['protected_artifact_integrity'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
