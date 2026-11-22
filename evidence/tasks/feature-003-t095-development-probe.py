"""Offline T095 authored controls; no private evaluation files or provider access.

Run from root with .venv/Scripts/python.exe -X utf8 and PYTHONPATH=backend/src.
Output is exclusive, in a fresh ignored cache directory on every invocation.
This diagnoses existing mechanics, not retrieval relevance or SC-002 acceptance.
"""

import hashlib
import json
import platform
import uuid

from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.retrieval import search

QUERIES = {
    'documentation_en': 'documentation',
    'documentation_latin': 'dokumentacija',
    'documentation_cyrillic': 'документација',
    'confidentiality_en': 'confidentiality',
    'confidentiality_latin': 'poverljivost',
    'confidentiality_cyrillic': 'поверљивост',
    'unknown': 'nomatcht095xyz',
    'mixed_unknown': 'poverljivost nomatcht095xyz',
    'inflected': 'dokumentacijom',
}


def main():
    corpus_root = ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1'
    run_root = ROOT / '.cache/t095-20261117' / ('probe-' + uuid.uuid4().hex)
    run_root.mkdir(parents=True, exist_ok=False)
    store = KnowledgeStore(run_root / 'knowledge.sqlite')
    corpus = store.publish(corpus_root / 'manifest.json')
    rows, versions, hashes = {}, {}, {}
    for name, filename in (
        ('demo_legacy', 'retrieval.json'),
        ('development_v2', 'retrieval-development-v2.json'),
    ):
        path = corpus_root / filename
        raw = path.read_bytes()
        config = json.loads(raw)
        assert config['adequacy_cutoff'] == 0.5, 'Diagnostic must not tune a threshold'
        versions[name] = store.save_configuration(config)
        hashes[str(path.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(raw).hexdigest()
        rows[name] = {}
        for identifier, query in QUERIES.items():
            result = search(store, query, corpus, versions[name])
            rows[name][identifier] = dict(
                query=query, status=result['status'],
                hits=[dict(passage_id=h['passage']['passage_id'],
                           doc_id=h['passage']['document']['doc_id'], score=h['score'])
                      for h in result['hits']],
            )
    candidate = rows['development_v2']
    controls = {
        'documentation_script_equivalent': (
            candidate['documentation_latin']['hits']
            == candidate['documentation_cyrillic']['hits']
            and candidate['documentation_latin']['status'] == 'matched'
        ),
        'confidentiality_script_equivalent': (
            candidate['confidentiality_latin']['hits']
            == candidate['confidentiality_cyrillic']['hits']
            and candidate['confidentiality_latin']['status'] == 'matched'
        ),
        'unknown_is_no_match_both': all(
            r['unknown']['status'] == 'no_match' for r in rows.values()
        ),
        'maximum_five_hits': all(
            len(row['hits']) <= 5 for group in rows.values() for row in group.values()
        ),
    }
    report = dict(
        kind='authored_development_diagnostic_not_acceptance',
        python=platform.python_version(), corpus_version=corpus,
        configuration_versions=versions, configuration_file_sha256=hashes,
        controls=controls, rows=rows, provider_calls=0,
        limitations=[
            'Published controls are excluded from fresh evaluation splits.',
            'No relevance judgments, recall/MRR or semantic adequacy measured.',
            'Mixed unknown query and inflection are observations, not scored references.',
            'Only existing demo/v2 configurations run; v3 remains design-only.',
        ],
    )
    output = run_root / 'results.json'
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(dict(
        output=str(output.relative_to(ROOT)), controls=controls,
        statuses={name: {key: row['status'] for key, row in group.items()}
                  for name, group in rows.items()},
        sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
    ), ensure_ascii=False, indent=2))
    if not all(controls.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
