"""Offline consumer compatibility with actual pinned producer code, no ML fit.

Run from root: .venv/Scripts/python.exe backend/tests/support/producer_dataset_smoke.py
Only authored records are published. Export/source and generated stores stay in
ignored .cache; no checkout, merge, live provider, raw IBM data or label reads.
"""
import copy
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHA = '487c427ea50e169f5e36898420d659f05ead2c60'


def produce(work):
    from fraudlens.data_contracts import CanonicalTransaction
    from fraudlens.data_store import DatasetStore, RunStore
    ctx = json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/context-dataset.json').read_text())
    version = ctx['dataset_version']
    tx = ctx['source_payload']['transaction']
    source = DatasetStore(work / 'source.sqlite')
    source.stage(version, source_records=3)
    for index, at in enumerate(['2025-12-24T10:00:00+00:00', '2026-01-01T09:59:00+00:00', '2026-01-01T10:00:00+00:00']):
        time = datetime.fromisoformat(at)
        source.add_event(version, CanonicalTransaction(
            transaction_id=tx['transaction_id'] if index == 2 else 'D' + f'{index:032x}',
            case_id=ctx['case_id'] if index == 2 else 'C' + f'{index:032x}',
            source_ordinal=index, event_time_raw=time.strftime('%Y/%m/%d %H:%M'),
            event_time_utc=time, event_time_epoch_ns=int(time.timestamp()) * 10**9,
            time_basis=tx['time_basis'], sender_bank=tx['sender']['bank'], sender_account=tx['sender']['account'],
            receiver_bank=tx['receiver']['bank'], receiver_account=tx['receiver']['account'],
            sender_join_key=b'a' * 32, receiver_join_key=b'b' * 32,
            paid_amount=tx['paid']['amount'], paid_currency=tx['paid']['currency'],
            received_amount=tx['received']['amount'], received_currency=tx['received']['currency'],
            payment_format=None, event_fact_digest=bytes([index]) * 32))
    source.complete(version)
    source.activate(version)
    source.close()
    for mode in ('rules', 'model'):
        risk = copy.deepcopy(ctx['source_payload']['risk_assessment'])
        if mode == 'model':
            risk.update(score_source='model', score_kind='uncalibrated_probability_estimate',
                        scorer_version='model-history-v1-boosted-candidate')
            risk['explanation'].update(method='boosted_sequential_probability', explained_scale='positive_class_estimate')
        store = RunStore(work / f'{mode}.sqlite')
        artifact = 'a' * 64 if mode == 'model' else None
        store.begin_run(ctx['snapshot_ref'], version, mode, risk['scorer_version'], artifact, '0.5', 1)
        store.append(ctx['snapshot_ref'], ctx['case_id'], tx, risk)
        store.complete(ctx['snapshot_ref'])
        store.activate(ctx['snapshot_ref'], mode, artifact)
        expected = store.detail_active(mode, ctx['snapshot_ref'], ctx['case_id'])
        (work / f'{mode}.json').write_text(json.dumps(expected), encoding='utf-8')
        store.close()


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--produce':
        produce(Path(sys.argv[2]))
        return
    cache = ROOT / '.cache'
    cache.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='dataset-producer-smoke-', dir=cache))
    export = work / 'producer'
    archive = subprocess.check_output(['git', 'archive', SHA, 'backend/src', 'specs/002-data-and-risk-scoring/contracts'])
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(export, filter='data')
    environment = {**os.environ, 'PYTHONPATH': str(export / 'backend/src')}
    subprocess.run([sys.executable, str(Path(__file__).resolve()), '--produce', str(work)],
                   env=environment, check=True, cwd=ROOT)
    sys.path.insert(0, str(ROOT / 'backend/src'))
    from fraudlens.investigation.context import outbound_context
    from fraudlens.investigation.dataset import DatasetReader
    from fraudlens.investigation.provider import project_conversation
    files = [work / 'source.sqlite', work / 'rules.sqlite', work / 'model.sqlite']
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    outcomes = []
    for mode in ('rules', 'model'):
        expected = json.loads((work / f'{mode}.json').read_text())
        reader = DatasetReader(work / f'{mode}.sqlite', work / 'source.sqlite', mode)
        context = reader.resolve(expected['case_id'], expected['snapshot_ref'])
        assert context['source_payload'] == expected
        history = reader.read(context, 'sender')
        assert history['eligible_count'] == 1 and history['coverage'] == 'full'
        assert history['events'][0]['amount'] == expected['transaction']['paid']['amount']
        assert project_conversation([dict(type='context', data=outbound_context(context, 'inv_' + 'a' * 32))])
        outcomes.append(dict(score_source=mode, context_version=context['contract_version'],
                             exact_producer_detail_match=True, history_eligible_count=1,
                             projection_valid=True, status='PASS'))
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    assert before == after
    result = dict(status='PASS', producer_sha=SHA, producer_archive_sha256=hashlib.sha256(archive).hexdigest(),
                  dataset='controlled authored canonical records, NOT IBM dataset evaluation',
                  assessments='authored rules/model-shaped values published by actual producer; no inference/fit',
                  immutable_source_hashes=after, source_bytes_unchanged=True, provider_calls=0,
                  label_reads=0, outcomes=outcomes)
    target = ROOT / 'evidence/tasks/feature-003-dataset-producer-smoke-20261116.json'
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
