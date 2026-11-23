"""Offline old-output preservation and new-policy rejection; no provider/client."""
import hashlib
import json

from fraudlens.investigation.evaluation import verify_seal
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.report_policy import HUMAN_AUTHORITY_POLICY
from fraudlens.investigation.validation import validate_report


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def main():
    out = ROOT / 'evals/results/feature-003/development-v6'
    freeze = verify_seal(load(out / 'freeze.json'))
    protocol = load(ROOT / 'evals/investigation/development-v6/protocol.json')
    assert sha(ROOT / 'evals/investigation/development-v6/protocol.json') == freeze['protocol_sha256']
    for name, expected in {**protocol['files_sha256'], **protocol['preserved_artifacts']}.items():
        assert sha(ROOT / name) == expected, name
    snapshot = ROOT / '.cache/evidence-snapshots/live-repair-v6'
    for name, expected in freeze['code_sha256'].items():
        assert sha(snapshot / name) == expected, name
    audit = load(ROOT / 'evidence/tasks/feature-003-live-repair-v6-results.json')
    for name, expected in audit['artifact_sha256'].items():
        assert sha(out / name) == expected, name
    assert load(out / 'audit.json') == audit or verify_seal(load(out / 'audit.json')) == audit
    assert audit['summary']['passing_development_reports'] == 1
    inputs = {item['id']: item for item in load(ROOT / 'evals/investigation/development-v6/inputs.json')}
    citations = 0
    for identity in ('DEV6-761', 'DEV6-762', 'DEV6-763'):
        saved = verify_seal(load(out / (identity + '.json')))
        result = saved['result']
        context = inputs[identity]['context']
        report = validate_report(result['report']['draft'], saved['evidence'], result['attempt_id'],
                                 context['context_revision'], context, result['corpus_version'])
        assert report['report_id'] == result['report']['report_id']
        citations += len(report['draft']['citations'])
        if identity == 'DEV6-762':
            try:
                validate_report(report['draft'], saved['evidence'], result['attempt_id'],
                    context['context_revision'], context, result['corpus_version'], report_policy=HUMAN_AUTHORITY_POLICY)
            except ValueError as error:
                assert str(error) == 'human_authority_notice_required'
            else:
                raise AssertionError('Missing notice must fail the new protocol')
    result = dict(status='PASS', kind='offline_preservation_and_protocol_guard_not_model_evaluation',
        actual_api_calls=0, v6_original_ordinary_score='1/2 unchanged',
        old_protocol_reports_still_validate=True, original_missing_notice_rejected_by_new_policy=True,
        cited_ids_resolved=citations, preserved_prior_artifacts=len(protocol['preserved_artifacts']),
        preserved_v6_artifacts=len(audit['artifact_sha256']), original_source_snapshot_verified=True,
        original_judge_ratings_unchanged=True,
        current_source_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
            for p in (ROOT / 'backend/src/fraudlens/investigation').glob('*.py')},
        prompt_v4_sha256=sha(ROOT / 'prompts/application/investigation-v4.md'))
    (ROOT / 'evidence/tasks/feature-003-human-authority-v7-results.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'current_source_sha256'}, indent=2))


if __name__ == '__main__':
    main()
