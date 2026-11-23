"""New development protocol: prompt coverage and calibration-gated machine ratings."""
import copy
import importlib.util
import json

from fraudlens.investigation.evaluation import input_only, verify_seal
from fraudlens.investigation.judge_calibration import assess_calibration
from fraudlens.investigation.judging import validate_rating
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.validation import validate_report

V3 = ROOT / 'evidence/tasks/feature-003-timeout-v3.py'
SPEC = importlib.util.spec_from_file_location('coverage_v4_adapter', V3)
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)
core = adapter.core
PACK = ROOT / 'evals/investigation/development-v4'
OUT = ROOT / 'evals/results/feature-003/development-v4'
IDS = ('DEV4-741', 'DEV4-742', 'DEV4-743')
adapter.PACK, adapter.OUT, adapter.IDS = PACK, OUT, IDS
core.PACK, core.OUT, core.IDS = PACK, OUT, IDS
core.CANARY = b'DEV4_REFERENCE_ONLY_CANARY_20261116'
core.BATCH_SCHEMA = copy.deepcopy(core.BATCH_SCHEMA)
core.BATCH_SCHEMA['properties']['ratings']['maxItems'] = 6
BASE_PACKETS, BASE_SUMMARIZE = core.packets_after_generation, core.summarize


def judge_prompt():
    return (ROOT / 'prompts/evaluation/report-judge-v3.md').read_text(encoding='utf-8')


def prepare(out=OUT):
    protocol = core.load(PACK / 'protocol.json')
    for name, expected in protocol['files_sha256'].items():
        if core.sha(ROOT / name) != expected:
            raise ValueError('New protocol input/source mismatch')
    inputs = [input_only(item) for item in core.load(PACK / 'inputs.json')]
    if tuple(item['id'] for item in inputs) != IDS:
        raise ValueError('Unexpected v4 generation identities')
    if core.CANARY in json.dumps(inputs, ensure_ascii=False).encode():
        raise ValueError('Reference marker in generation inputs')
    settings = core.load_settings()
    if settings.model.get_secret_value() != 'gpt-6-luna':
        raise ValueError('Explicit expected model required')
    settings = settings.model_copy(update=dict(enabled=True, provider='openai', source='fixture', store=out / 'runs.sqlite'))
    knowledge = KnowledgeStore(settings.store)
    corpus = knowledge.publish(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')
    candidate = core.load(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json')
    control = {**candidate, 'adequacy_cutoff': 1000000, 'status': 'controlled_no_match_development_fixture'}
    versions = dict(candidate=knowledge.save_configuration(candidate),
                    controlled_no_match=knowledge.save_configuration(control))
    freeze = dict(protocol_sha256=core.sha(PACK / 'protocol.json'), settings=settings.model_dump(mode='json'),
        model='gpt-6-luna', sdk_version=core.version('openai'),
        prompt_sha256=core.sha(ROOT / 'prompts/application/investigation-v3.md'),
        judge_prompt_sha256=digest(judge_prompt()), judge_schema_sha256=digest(core.BATCH_SCHEMA),
        corpus_version=corpus, retrieval_versions=versions,
        code_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): core.sha(p)
                    for p in (ROOT / 'backend/src/fraudlens/investigation').glob('*.py')},
        runner_sha256=core.sha(core.Path(core.__file__)), adapter_sha256=core.sha(V3),
        cap=25, judge_timeout=60, judge_output_tokens=8192,
        input_sha256={item['id']: digest(item) for item in inputs})
    core.frozen(out / 'freeze.json', freeze)
    return inputs, protocol, settings, knowledge, versions, freeze


def packets_after_generation(records, reference):
    # Invoked by judge only after all generation outcomes have been sealed.
    packets = BASE_PACKETS(records, reference)
    calibration_data = core.load(PACK / 'calibrations.json')
    return packets + copy.deepcopy(calibration_data['packets'])  # Expected labels stay local.


def validate_batch(packets, value):
    expected = {p['scenario_id']: p for p in packets if not p['failed']}
    if len(expected) != sum(not p['failed'] for p in packets):
        raise ValueError('Duplicate packet identities')
    if not isinstance(value, dict) or set(value) != {'ratings'} or not isinstance(value['ratings'], list):
        raise ValueError('Invalid calibrated batch shape')
    rows = value['ratings']
    if any(not isinstance(r, dict) or set(r) != {'scenario_id', 'rating'} for r in rows):
        raise ValueError('Invalid calibrated row')
    if len(rows) != len(expected) or {r['scenario_id'] for r in rows} != set(expected):
        raise ValueError('Missing, duplicate or foreign calibrated scenario')
    return {(expected[r['scenario_id']]['role'], r['scenario_id']):
            validate_rating(expected[r['scenario_id']], r['rating']) for r in rows}


def summarize(records, packets, ratings, judge_meta, ledger, freeze):
    result = BASE_SUMMARIZE(records, packets, ratings, judge_meta, ledger, freeze)
    expected = core.load(PACK / 'calibrations.json')['expectations']
    gate = assess_calibration(packets, ratings or {}, expected)
    result.update(calibration=gate, quality_assessment_valid=gate['passed'],
                  raw_passing_development_reports=result['passing_development_reports'])
    if not gate['passed']:
        result['passing_development_reports'] = None
        result['judge_status'] = 'calibration_failed_or_unavailable'
    return result


core.prepare, core.judge_prompt = prepare, judge_prompt
core.packets_after_generation, core.validate_batch, core.summarize = packets_after_generation, validate_batch, summarize


def audit():
    freeze = verify_seal(core.load(OUT / 'freeze.json'))
    protocol = core.load(PACK / 'protocol.json')
    assert core.sha(PACK / 'protocol.json') == freeze['protocol_sha256']
    for name, expected in {**protocol['files_sha256'], **freeze['code_sha256'],
                           **protocol['preserved_v2_artifacts'], **protocol['preserved_v3_source']}.items():
        assert core.sha(ROOT / name) == expected, name
    summary = verify_seal(core.load(OUT / 'summary.json'))
    ledger = core.load(OUT / 'transport-ledger.json')
    assert len(ledger['attempts']) <= 25
    assert sum(a['phase'] == 'judge' for a in ledger['attempts']) <= 1
    assert all(sum(a['identity'] == identity for a in ledger['attempts']) <= 8 for identity in IDS)
    inputs = {i['id']: i for i in core.load(PACK / 'inputs.json')}
    citations, records = 0, []
    for identity in IDS:
        path = OUT / (identity + '.json')
        if not path.exists():
            continue
        saved = verify_seal(core.load(path))
        assert saved['input_sha256'] == digest(inputs[identity]) and saved['freeze_sha256'] == digest(freeze)
        value = saved['result']
        assert value['context_revision'] == inputs[identity]['context']['context_revision']
        if value['report']:
            checked = validate_report(value['report']['draft'], saved['evidence'], value['attempt_id'],
                value['context_revision'], inputs[identity]['context'], value['corpus_version'])
            assert checked['report_id'] == value['report']['report_id']
            citations += len(value['report']['draft']['citations'])
        records.append(saved)
    if (OUT / 'judge-result.json').exists():
        packets = verify_seal(core.load(OUT / 'judge-packets.json'))
        judge = verify_seal(core.load(OUT / 'judge-result.json'))
        assert judge['packets_sha256'] == digest(packets)
        ratings = validate_batch(packets, judge['value'])
        actual = summarize(records, packets, ratings, judge, core.Ledger(OUT / 'transport-ledger.json'), freeze)
        for key in ('calibration', 'quality_assessment_valid', 'passing_development_reports', 'judged_reports'):
            assert actual[key] == summary[key]
    result = dict(status='PASS', kind='calibrated_development_not_independent_holdout',
        summary=summary, prior_outputs_preserved=True, v3_source_snapshot_preserved=True,
        cited_ids_resolved=citations, unknown_citations=0, human_validation=False,
        artifact_sha256={p.name: core.sha(p) for p in OUT.glob('*.json') if p.name != 'audit.json'})
    core.frozen(OUT / 'audit.json', result)
    target = ROOT / 'evidence/tasks/feature-003-coverage-v4-results.json'
    if target.exists():
        assert core.load(target) == result
    else:
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    import asyncio
    import sys
    if '--audit' in sys.argv:
        raise SystemExit(audit())
    raise SystemExit(asyncio.run(adapter.main()))
