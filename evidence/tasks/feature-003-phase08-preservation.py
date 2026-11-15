"""Hash-only preservation check; never loads held-out answers or invokes a provider."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path, normalize=False):
    raw = path.read_bytes()
    return hashlib.sha256(raw.replace(b'\r\n', b'\n') if normalize else raw).hexdigest()


def unseal(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    assert set(value) == {'version', 'payload', 'sha256'} and value['version'] == 1
    raw = json.dumps(value['payload'], sort_keys=True, separators=(',', ':'),
                     ensure_ascii=False, allow_nan=False).encode('utf-8')
    assert hashlib.sha256(raw).hexdigest() == value['sha256'], path.name
    return value['payload']


def main():
    live = ROOT / 'evals/results/feature-003/live-v1'
    previous = json.loads((ROOT / 'evidence/tasks/feature-003-live-audit-results.json').read_text())
    for name, expected in previous['outputs'].items():
        assert sha(live / name) == expected, name
    freeze = unseal(live / 'freeze.json')
    for name, expected in freeze['code_sha256'].items():
        assert sha(ROOT / name, True) == expected, name
    retrieval = unseal(ROOT / 'evals/investigation/freezes/retrieval-v1.json')
    for name, expected in retrieval['artifacts'].items():
        assert sha(ROOT / name, True) == expected, name
    ledger = json.loads((live / 'transport-ledger.json').read_text())
    assert len(ledger['attempts']) == previous['transport_attempts'] == 86
    result = dict(status='PASS', live_outputs_unchanged=len(previous['outputs']),
                  live_generation_source_hashes_unchanged=len(freeze['code_sha256']),
                  retrieval_artifact_hashes_unchanged=len(retrieval['artifacts']),
                  live_transport_attempts_still=86, new_provider_calls=0,
                  human_reviews='pending; not inferred', quality_rerun=False,
                  original_audit_sha256=sha(ROOT / 'evidence/tasks/feature-003-live-audit-results.json'),
                  live_freeze_sha256=sha(live / 'freeze.json'))
    (ROOT / 'evidence/tasks/feature-003-phase08-preservation-results.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
