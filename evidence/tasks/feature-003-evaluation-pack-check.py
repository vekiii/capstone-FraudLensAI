"""T052 artifact integrity only; never search, generate, tune or score reports.

Run from any directory with the existing project .venv. References are deliberately
read here by a trusted offline verifier, never by a runtime/generation command.
This is not the T053 evaluation test suite or the T054 evaluation implementation.
"""
import copy
import hashlib
import json
import platform
import sqlite3
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'evals/investigation'
blocked_events = []


def offline_guard(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, Path)):
        name = Path(args[0]).name
        if name == '.env' or (name.startswith('.env.') and name != '.env.example'):
            blocked_events.append('environment_file_open')
            raise PermissionError('T052 verifier forbids environment file reads')
    if event in ('socket.connect', 'socket.getaddrinfo', 'subprocess.Popen', 'os.system'):
        blocked_events.append(event)
        raise PermissionError('T052 verifier is offline and cannot spawn commands')


sys.addaudithook(offline_guard)
sys.path.insert(0, str(ROOT / 'backend/src'))
from fraudlens.investigation.context import CaseContextReader  # noqa: E402
from fraudlens.investigation.knowledge import stage  # noqa: E402
from fraudlens.investigation.models import context_digest, digest, validate  # noqa: E402


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def local_path(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), 'Path escapes workspace')
    return path


def file_digest(relative):
    raw = local_path(relative).read_bytes().replace(b'\r\n', b'\n')
    require(b'\r' not in raw, 'Invalid LF source')
    require(not raw.startswith(b'\xef\xbb\xbf') or relative.endswith('.py'), 'BOM in authored JSON/corpus')
    raw.decode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def exact_keys(value, keys):
    require(isinstance(value, dict) and set(value) == set(keys), 'Unexpected/missing artifact field')


def indexed(rows, count):
    require(isinstance(rows, list) and len(rows) == count, 'Wrong artifact count')
    index = {item['id']: item for item in rows}
    require(len(index) == count, 'Duplicate artifact identity')
    return index


def check_join(inputs, references):
    require(inputs.keys() == references.keys(), 'Input/reference identity mismatch')
    for identity, item in inputs.items():
        require(references[identity]['input_sha256'] == digest(item), 'Input/reference hash mismatch')


def check_partition(value, ids, development, held_out):
    exact_keys(value, ['development', 'held_out'])
    dev, held = value['development'], value['held_out']
    require(len(dev) == development and len(held) == held_out, 'Wrong split counts')
    require(len(set(dev + held)) == development + held_out, 'Duplicate/overlapping split')
    require(set(dev + held) == set(ids), 'Split identity mismatch')


def pointer(value, path):
    for key in path.strip('/').split('/'):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def check_context(item):
    context = item['context']
    validate('InvestigationContext', context)
    require(context['context_revision'] == context_digest(context), 'Context hash mismatch')
    tx, risk = context['source_payload']['transaction'], context['source_payload']['risk_assessment']
    require(tx['transaction_id'] == risk['transaction_id'], 'Transaction mismatch')
    fixture = item['history_fixture']
    exact_keys(fixture, ['accounts', 'events'])
    require(set(fixture['accounts']) == {context['case_id']}, 'Unrelated account scope')
    identities = fixture['accounts'][context['case_id']]
    exact_keys(identities, ['sender', 'receiver'])
    for identity in identities.values():
        exact_keys(identity, ['bank', 'account'])
    for event in fixture['events']:
        exact_keys(event, ['transaction_id', 'occurred_at', 'bank', 'account', 'amount', 'currency'])
        require(Decimal(event['amount']).is_finite() and Decimal(event['amount']) >= 0, 'Bad history amount')
        require(event['occurred_at'].endswith('Z'), 'History must use explicit UTC')
        datetime.fromisoformat(event['occurred_at'].replace('Z', '+00:00'))
    ids = [e['transaction_id'] for e in fixture['events']]
    require(len(ids) == len(set(ids)), 'Duplicate history event')
    if context['source_mode'] == 'dataset':
        require(identities == {side: tx[side] for side in ('sender', 'receiver')}, 'Dataset bank/account identity mismatch')


def independent_history(item):
    """Source-fixture arithmetic only; no runtime HistoryReader or search."""
    context = item['context']
    history = context['history']
    require(history['availability'] == 'available', 'Expected authored available history')
    cutoff = datetime.fromisoformat(history['cutoff'].replace('Z', '+00:00'))
    lower = cutoff - timedelta(days=7)
    upper = cutoff.replace(second=0, microsecond=0)
    sender = item['history_fixture']['accounts'][context['case_id']]['sender']
    focal = context['source_payload']['transaction']['transaction_id']
    eligible = [event for event in item['history_fixture']['events']
                if event['bank'] == sender['bank'] and event['account'] == sender['account']
                and event['transaction_id'] != focal
                and lower <= datetime.fromisoformat(event['occurred_at'].replace('Z', '+00:00')) < upper]
    eligible.sort(key=lambda e: (e['occurred_at'], e['transaction_id']))
    totals = {}
    for event in eligible:
        currency = event['currency']
        totals[currency] = totals.get(currency, Decimal('0')) + Decimal(event['amount'])
    return {'eligible_count': len(eligible), 'returned_count': min(50, len(eligible)),
            'truncated': len(eligible) > 50, 'totals': {k: str(v) for k, v in totals.items()},
            'coverage': history['coverage'], 'eligible_event_ids': [e['transaction_id'] for e in eligible]}


def verify():
    protocol = load('evals/investigation/protocol.json')
    require(protocol['status'] in ('proposed_not_frozen', 'frozen'), 'Unknown T052 state')
    hashes = protocol['files_sha256']
    for path, expected in hashes.items():
        require(file_digest(path) == expected, 'Hash mismatch: ' + path)
    require(digest(hashes) == protocol['sealed_inventory_sha256'], 'Inventory root mismatch')
    content_hashes = {p: h for p, h in hashes.items() if p != 'evals/investigation/reference/review-record.json'}
    require(digest(content_hashes) == protocol['bundle_sha256'], 'Bundle root mismatch')
    # No JSON input/reference can silently escape the sealed file inventory.
    actual = {p.relative_to(ROOT).as_posix() for p in PACK.rglob('*.json') if p.name != 'protocol.json'}
    require({p for p in hashes if p.startswith('evals/investigation/')} == actual, 'Unsealed pack JSON')
    corpus = stage(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')
    require(protocol['corpus_version'] == corpus['corpus_version'], 'Corpus identity mismatch')
    archive_path = ROOT / 'data/processed/investigations.sqlite'
    archive_status = 'absent; historical T015/T022 evidence only, no store created'
    if archive_path.is_file():
        with sqlite3.connect(archive_path.as_uri() + '?mode=ro', uri=True) as db:
            row = db.execute('SELECT content FROM corpus_versions WHERE corpus_version=?',
                             (corpus['corpus_version'],)).fetchone()
        require(row is not None and json.loads(row[0]) == corpus, 'Published corpus archive mismatch')
        archive_status = 'read-only archive equals staged corpus; no database writes'
    sources = load('evals/investigation/reference/passages.json')
    require(sources['corpus_version'] == corpus['corpus_version'], 'Reference corpus mismatch')
    require(len(sources['passages']) == len(corpus['passages']) == 6, 'Expected six stable passages')
    passage_index = {p['passage_id']: p for p in corpus['passages']}
    doc_index = {p['document']['doc_id']: p for p in corpus['passages']}
    for entry in sources['passages']:
        p = passage_index[entry['passage_id']]
        require(entry['doc_id'] == p['document']['doc_id'] and entry['section'] == p['section']
                and entry['ordinal'] == p['ordinal'] and entry['content_sha256'] == p['content_sha256']
                and entry['document_version'] == p['document']['version']
                and entry['document_content_sha256'] == p['document']['content_sha256'], 'Passage/document linkage mismatch')
        require(file_digest(entry['source_path']) == entry['document_content_sha256'], 'Source text mismatch')
    questions = indexed(load('evals/investigation/inputs/retrieval.json'), 30)
    relevance = indexed(load('evals/investigation/reference/retrieval.json'), 30)
    check_join(questions, relevance)
    splits = load('evals/investigation/splits.json')
    check_partition(splits['retrieval'], questions, 10, 20)
    no_answers = {}
    languages = set()
    for identity, q in questions.items():
        exact_keys(q, ['id', 'language', 'query'])
        require(isinstance(q['query'], str) and q['query'] == q['query'].strip() and 1 <= len(q['query']) <= 500, 'Query bound')
        languages.add(q['language'])
        r = relevance[identity]
        exact_keys(r, ['id', 'input_sha256', 'answerability', 'relevant_passage_ids', 'relevant_document_ids', 'source_rationale'])
        require(r['answerability'] in ('answerable', 'no_answer') and bool(r['source_rationale']), 'Bad relevance judgment')
        require((r['answerability'] == 'answerable') == bool(r['relevant_passage_ids']), 'No-answer/relevance conflict')
        require(len(r['relevant_passage_ids']) == len(set(r['relevant_passage_ids'])), 'Duplicate passage relevance')
        require(r['relevant_passage_ids'] == [doc_index[d]['passage_id'] for d in r['relevant_document_ids']], 'Relevant document/passage mismatch')
    for split, ids in splits['retrieval'].items():
        no_answers[split] = sum(relevance[i]['answerability'] == 'no_answer' for i in ids)
    require(no_answers == {'development': 2, 'held_out': 4}, 'No-answer split counts')
    require({'en', 'sr-Latn', 'sr-Cyrl'} <= languages, 'Bilingual/script coverage missing')
    for ids in splits['retrieval'].values():
        require(any(questions[i]['language'] == 'en' for i in ids) and any(questions[i]['language'].startswith('sr') for i in ids), 'Both languages needed per split')
    cases = indexed(load('evals/investigation/inputs/investigation.json'), 12)
    expectations = indexed(load('evals/investigation/reference/investigation.json'), 12)
    origins = indexed(load('evals/investigation/reference/scenario-origins.json'), 12)
    check_partition(splits['investigation'], cases, 4, 8)
    check_join(cases, expectations)
    check_join(cases, origins)
    subset, demos = splits['second_review_subset'], splits['ordinary_live_demo_cases']
    require(len(subset) >= 4 and len(subset) == len(set(subset)) and set(subset) <= set(splits['investigation']['held_out']), 'Second review assignment')
    require(len(demos) == 5 and len(set(demos)) == 5 and set(demos) <= set(cases), 'Five preselected ordinary cases')
    base_dataset = load('specs/003-ai-investigation/contracts/examples/context-dataset.json')
    history_checked = []
    for sid, item in cases.items():
        exact_keys(item, ['id', 'language', 'instruction', 'context', 'history_fixture', 'procedure_queries'])
        check_context(item)
        require(all(isinstance(q, str) and q == q.strip() and 1 <= len(q) <= 500 for q in item['procedure_queries']), 'Procedure query bound')
        ctx, r, origin = item['context'], expectations[sid], origins[sid]
        require(r['context_revision'] == origin['context_revision'] == ctx['context_revision'], 'Scenario context linkage')
        base = base_dataset if ctx['source_mode'] == 'dataset' else CaseContextReader().resolve(ctx['case_id'], 'fixture', None)
        require(origin['base_context_sha256'] == digest(base), 'Authored origin mismatch')
        facts = r['essential_facts']
        require(facts and len({f['fact_id'] for f in facts}) == len(facts), 'Essential fact identities')
        for fact in facts:
            require(bool(fact['statement']) and fact['source'] == 'input', 'Fact needs independent source')
            if 'pointer' in fact:
                require(pointer(item, fact['pointer']) == fact['expected_value'], 'Expected exact fact contradicts source')
        require(r['expected_missing_fields'] and r['expected_limitations'] and r['critical_errors'], 'Incomplete rubric reference')
        require(set(r['applicable_guidance_passage_ids']) <= set(passage_index), 'Unknown applicable guidance')
        probe = r['valid_id_false_interpretation_probe']
        require(probe['passage_id'] in passage_index and probe['judgment'].startswith('unsupported'), 'Missing semantic counterexample')
        if r['history_expectation'] is not None:
            actual_history = independent_history(item)
            require(all(r['history_expectation'][k] == v for k, v in actual_history.items()), 'Authored history arithmetic/boundary mismatch')
            excluded = r['history_expectation'].get('excluded_event_ids')
            if excluded is not None:
                all_ids = {e['transaction_id'] for e in item['history_fixture']['events']}
                require(set(excluded) == all_ids - set(actual_history['eligible_event_ids']), 'History exclusion mismatch')
            history_checked.append(sid)
    require(len({x['context']['context_revision'] for x in cases.values()}) == 12, 'Context collision')
    require(len({x['context']['snapshot_ref'] for x in cases.values()}) == 12, 'Snapshot collision')
    safety = indexed(load('evals/investigation/inputs/safety.json'), 12)
    safety_refs = indexed(load('evals/investigation/reference/safety.json'), 12)
    check_join(safety, safety_refs)
    require(set(splits['safety']) == set(safety) and len(splits['safety']) == 12, 'Safety identities')
    for sid, item in safety.items():
        exact_keys(item, ['id', 'category', 'stimulus'])
        r = safety_refs[sid]
        require(r['allowed_unauthorized_tool_or_action_count'] == 0 and r['execution_status'] == 'not_run_in_T052'
                and r['red_green_evidence'] is None and r['requirements'] and r['expected_controls'], 'Safety preparation is not execution')
    rubric = load('evals/investigation/reference/rubric.json')
    require(rubric['pack_pass']['primary_reports'] == 8 and rubric['pack_pass']['passing_reports_min'] == 7, 'Report denominator/target')
    require(rubric['report_pass']['support_rate_min'] == .9 and rubric['report_pass']['essential_coverage_min'] == .8, 'Report target')
    review = load('evals/investigation/reference/review-record.json')
    require(review['prepared_by']['kind'] == 'AI coding agent'
            and review['prepared_by']['human_authorship_claimed'] is False, 'Authorship claim')
    frozen = protocol['status'] == 'frozen'
    approval = review['independent_expectation_review']
    if frozen:
        require(review['status'] == 'approved' and approval['decision'] == 'approved'
                and bool(approval['reviewer_identity']) and bool(approval['reviewed_at'])
                and approval['reviewed_bundle_sha256'] == protocol['bundle_sha256'], 'Missing bound approval')
        require(review['freeze']['status'] == 'frozen'
                and review['freeze']['bundle_sha256'] == protocol['bundle_sha256']
                and review['freeze']['approved_by'] == approval['reviewer_identity']
                and review['freeze']['approved_at'] == approval['reviewed_at']
                and protocol['freeze_gate']['frozen_by'] == approval['reviewer_identity']
                and protocol['freeze_gate']['frozen_at'] == approval['reviewed_at']
                and protocol['freeze_gate']['t052_complete'] is True, 'Freeze mismatch')
    else:
        require(review['status'] == 'proposed' and review['freeze']['status'] == 'not_frozen', 'Invented freeze')
        require(all(approval[key] is None for key in ('reviewer_identity', 'reviewed_at', 'decision', 'reviewed_bundle_sha256')), 'Unbound full review')
    canaries = load('evals/investigation/reference/private-canaries.json')
    public_text = json.dumps(list(questions.values()) + list(cases.values()) + list(safety.values()), ensure_ascii=False)
    public_text += ''.join(p['text'] for p in corpus['passages'])
    public_text += (ROOT / 'prompts/application/investigation-v1.md').read_text(encoding='utf-8')
    for key in ('reference_answer_canary', 'reviewer_note_canary', 'private_label_canary'):
        require(canaries[key] not in public_text, 'Private canary leaked into authored runtime material')
    require(not any(name.startswith('openai') or name in ('fraudlens.investigation.provider', 'fraudlens.investigation.settings') for name in sys.modules), 'Provider/settings must not load')
    require(not blocked_events, 'Forbidden access attempted')
    return {'status': 'PASS', 'scope': 'T052 structural verification only; not retrieval/live/safety evaluation',
            'python': platform.python_version(), 'corpus_version': corpus['corpus_version'],
            'published_archive': archive_status,
            'documents': 6, 'passages': 6, 'retrieval': {'development': 10, 'held_out': 20, 'no_answers': no_answers},
            'investigation': {'development': 4, 'held_out': 8}, 'safety_prepared_not_executed': 12,
            'second_review_subset': subset, 'ordinary_live_demo_cases': demos,
            'independent_history_reference_checks': history_checked, 'sealed_files': len(hashes),
            'bundle_sha256': protocol['bundle_sha256'], 'independent_human_review': 'approved' if frozen else 'pending', 't052': 'complete' if frozen else 'incomplete',
            'sealed_inventory_sha256': protocol['sealed_inventory_sha256'],
            'provider_settings_imported': False, 'environment_or_network_attempts': blocked_events}


def negative_integrity_checks():
    """Small in-memory corruptions prove integrity checks reject damaged artifacts.

    These are not T053 RED/GREEN business/metrics tests and perform no evaluation.
    """
    cases = load('evals/investigation/inputs/investigation.json')
    refs = load('evals/investigation/reference/investigation.json')
    split = load('evals/investigation/splits.json')['investigation']
    rejected = []
    bad_hash = copy.deepcopy(refs[0])
    bad_hash['input_sha256'] = '0' * 64
    duplicate_split = copy.deepcopy(split)
    duplicate_split['held_out'][0] = duplicate_split['development'][0]
    wrong_context = copy.deepcopy(cases[0])
    wrong_context['context']['source_payload']['transaction']['amount'] = '1.00'
    for name, check in [
        ('wrong_input_reference_hash', lambda: check_join({cases[0]['id']: cases[0]}, {bad_hash['id']: bad_hash})),
        ('overlapping_split', lambda: check_partition(duplicate_split, [c['id'] for c in cases], 4, 8)),
        ('changed_context_money_without_rehash', lambda: check_context(wrong_context)),
        ('wrong_cardinality', lambda: indexed(cases[:-1], 12)),
        ('duplicate_identity', lambda: indexed(cases[:-1] + [cases[0]], 12)),
    ]:
        try:
            check()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('Corruption not rejected: ' + name)
    return rejected


if __name__ == '__main__':
    result = verify()
    result['in_memory_corruptions_rejected'] = negative_integrity_checks()
    # Protocol cannot contain its own file hash; record it separately in evidence.
    result['protocol_file_sha256'] = file_digest('evals/investigation/protocol.json')
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if len(sys.argv) == 3 and sys.argv[1] == '--output':
        output = local_path(sys.argv[2])
        require(output.parent == ROOT / 'evidence/tasks', 'Evidence output must stay in evidence/tasks')
        output.write_text(rendered, encoding='utf-8', newline='\n')
    else:
        require(len(sys.argv) == 1, 'Usage: checker [--output evidence/tasks/result.json]')
    print(rendered, end='')
