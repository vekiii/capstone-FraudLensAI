"""Read-only design checks; no application/model/provider evaluation."""
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
FEATURE = ROOT / 'specs/003-ai-investigation'
CONTRACTS = FEATURE / 'contracts'
PRODUCER = '2dd815d85bfc9c2fc70a28baef9c142d551e57e0'


def main():
    schema = json.loads((CONTRACTS / 'schemas.json').read_text(encoding='utf-8'))
    fixture = ROOT / 'specs/001-project-foundation/contracts/schemas.json'
    registry = Registry()
    for path in (CONTRACTS / 'schemas.json', CONTRACTS / 'producer-v2.snapshot.json', fixture):
        document = json.loads(path.read_text(encoding='utf-8'))
        Draft202012Validator.check_schema(document)
        resource = Resource.from_contents(document)
        registry = registry.with_resource(path.as_uri(), resource)
        registry = registry.with_resource(document['$id'], resource)
    for uri, path in (
        ('https://fraudlens.local/specs/003/contracts/producer-v2.snapshot.json',
         CONTRACTS / 'producer-v2.snapshot.json'),
        ('https://fraudlens.local/specs/001-project-foundation/contracts/schemas.json', fixture),
    ):
        registry = registry.with_resource(
            uri, Resource.from_contents(json.loads(path.read_text(encoding='utf-8'))))

    def validator(name):
        selected = {**schema, '$ref': '#/$defs/' + name}
        return Draft202012Validator(selected, registry=registry, format_checker=FormatChecker())

    examples = {
        'context-fixture': 'InvestigationContext', 'context-dataset': 'InvestigationContext',
        'create-request': 'CreateRequest', 'needs-information-draft': 'ReportDraft',
        'error-stale-snapshot': 'ErrorEnvelope', 'report-ready': 'Report',
        'run-ready': 'RunView', 'evidence-fixture': 'Evidence',
    }
    for filename, definition in examples.items():
        validator(definition).validate(json.loads(
            (CONTRACTS / 'examples' / (filename + '.json')).read_text(encoding='utf-8')))
    for filename in ('context-fixture', 'context-dataset'):
        context = json.loads((CONTRACTS / 'examples' / (filename + '.json')).read_text(
            encoding='utf-8'))
        digest = context.pop('context_revision')
        encoded = json.dumps(context, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False, allow_nan=False).encode()
        assert digest == hashlib.sha256(encoded).hexdigest(), filename
    report = json.loads((CONTRACTS / 'examples/report-ready.json').read_text(encoding='utf-8'))
    report_identity = {key: report[key] for key in ('attempt_id', 'context_revision', 'draft')}
    assert report['report_id'] == hashlib.sha256(json.dumps(
        report_identity, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    invalid = json.loads((CONTRACTS / 'examples/context-fixture.json').read_text())
    invalid['hidden_label'] = 1
    assert list(validator('InvestigationContext').iter_errors(invalid))
    invalid = json.loads((CONTRACTS / 'examples/context-dataset.json').read_text())
    invalid['source_payload']['transaction']['paid']['amount'] = 12.5
    assert list(validator('InvestigationContext').iter_errors(invalid))
    raw = subprocess.check_output([
        'git', 'show', PRODUCER + ':specs/002-data-and-risk-scoring/contracts/schemas.json'],
        cwd=ROOT)
    # Git text checkout may use CRLF on Windows; compare canonical LF content.
    checked_out = (CONTRACTS / 'producer-v2.snapshot.json').read_bytes()
    assert checked_out.replace(b'\r\n', b'\n') == raw

    tasks = (FEATURE / 'tasks.md').read_text(encoding='utf-8')
    entries = re.findall(r'^- \[ \] (T\d{3})(.*)$', tasks, re.M)
    assert [task for task, _ in entries] == [f'T{i:03}' for i in range(1, 68)]
    counts = Counter()
    for task, description in entries:
        assert re.search(r'`[^`]+(?:/|\.md|\.toml|\.json|\.ts)[^`]*`', description), task
        # Future RED/GREEN cross-references are not prerequisites.
        dependencies = re.search(r'\(Depends: ([^)]*)\)', description)
        if dependencies:
            for prerequisite in re.findall(r'T(\d{3})', dependencies[1]):
                assert int(prerequisite) < int(task[1:]), (task, prerequisite)
        story = re.search(r'\[US(\d)\]', description)
        if story:
            counts[story[1]] += 1
    assert dict(counts) == {'1': 10, '2': 16, '3': 6, '4': 7, '5': 10}, counts
    for prefix, maximum in (('FR', 28), ('SC', 8)):
        covered = set(re.findall(prefix + r'-(\d{3})', tasks))
        for start, end in re.findall(prefix + r'-(\d{3})-(\d{3})', tasks):
            covered.update(f'{i:03}' for i in range(int(start), int(end) + 1))
        assert {f'{i:03}' for i in range(1, maximum + 1)} <= covered, prefix
    for path in FEATURE.rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        assert not re.search(r'^(<<<<<<<|=======|>>>>>>>)', text, re.M), path
        assert not re.search(r'NEEDS CLARIFICATION|\[FEATURE\]|TXXX|\[###', text), path
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent / target.split('#')[0]).exists(), (path, target)
        for number, line in enumerate(text.splitlines(), 1):
            assert line == line.rstrip(), (path, number)
    print('PASS: 3 schemas, 8 authored examples, context digests, 2 negative examples,')
    print('exact producer snapshot, 67 task IDs/paths/prior-only prerequisites,')
    print('story counts', dict(counts), ', 28 FR/8 SC coverage, links/placeholders/whitespace.')
    print('This is design validation, not implemented semantic checks or live evaluation.')


if __name__ == '__main__':
    main()
