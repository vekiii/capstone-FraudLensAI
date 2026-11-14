"""Local source inspection and reviewed, source-bound dataset import."""
import argparse
import hashlib
import io
import json
import math
import re
import sqlite3
import sys
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from fraudlens.benchmark_phase8 import labels as benchmark_labels
from fraudlens.benchmark_phase8 import predict as benchmark_predict
from fraudlens.data_contracts import CanonicalTransaction, ScoreRequestV2, score_v2
from fraudlens.data_import import derive_dataset_version, inspect_source, iter_canonical_rows
from fraudlens.data_store import DatasetStore, RunStore
from fraudlens.evaluation import consume_holdout, evaluate_frozen
from fraudlens.evaluation_store import audit_sqlite_split
from fraudlens.feature_history import HistoricalFeatureSnapshot
from fraudlens.model_scoring import ModelScorer, load_trusted_artifact
from fraudlens.rule_scoring import RuleScorer

_ROOT = Path(__file__).resolve().parents[3]
_APPROVAL = _ROOT / 'evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md'
_APPROVAL_PROMPT = _ROOT / 'prompts/development/002-t007-t008-final-team-approval-2026-11-13.md'
_MAPPING_M = 'a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57'
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')


class _Arguments(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default message can echo local paths or rejected values.
        raise ValueError('invalid_arguments')


def _load_authorization(mapping_path: Path) -> dict:
    """Bind execution to the team's final-byte approval, never mapping status flags."""
    raw = mapping_path.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf') or b'\r' in raw.replace(b'\r\n', b''):
        raise ValueError('mapping_mismatch')
    digest = hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()
    review = _APPROVAL.read_text(encoding='utf-8')
    confirmation = _APPROVAL_PROMPT.read_text(encoding='utf-8')
    if (digest != _MAPPING_M
            or '## Collective final-byte approval conveyed by the user' not in review
            or f'| `data/mappings/ibm_hi_small_v1.json` (normalized M; current raw LF also equal) | `{digest}` |' not in review
            or 'Potvrđujem da je cijeli tim pregledao i odobrio konačne izmjene' not in confirmation):
        raise ValueError('mapping_approval_mismatch')
    mapping = json.loads(raw)
    source = mapping['source']
    return {'mapping_sha256': digest, 'source_sha256': source['expected_sha256'],
            'source_size': source['expected_size_bytes'], 'namespace': source['namespace'],
            'member': source['member'],
            'time_policy_sha256': mapping['time']['time_policy_sha256']}


def _file_sha256(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


class _MeasuredReader(io.RawIOBase):
    """Measure the exact binary stream supplied to the CSV decoder."""

    def __init__(self, stream):
        self._stream = stream
        self._digest = hashlib.sha256()
        self.size = 0

    def readable(self):
        return True

    def readinto(self, buffer):
        count = self._stream.readinto(buffer)
        if count:
            self._digest.update(memoryview(buffer)[:count])
            self.size += count
        return count

    def hexdigest(self):
        return self._digest.hexdigest()


def _import(args) -> dict:
    if _SHA256.fullmatch(args.expected_sha256) is None or not args.namespace:
        raise ValueError('invalid_arguments')
    binding = _load_authorization(args.mapping)
    if (args.namespace != binding['namespace'] or args.source.name != binding['member']
            or args.expected_sha256 != binding['source_sha256']):
        raise ValueError('source_binding_mismatch')
    source_hash, source_size = _file_sha256(args.source)
    if (source_hash != args.expected_sha256
            or (binding['source_size'] is not None and source_size != binding['source_size'])):
        raise ValueError('source_mismatch')
    version = derive_dataset_version(
        bytes.fromhex(source_hash), bytes.fromhex(binding['mapping_sha256']),
        bytes.fromhex(binding['time_policy_sha256']))
    store = DatasetStore(args.store)
    try:
        if store.version_status(version) == 'complete':
            counts = store.complete_report(version)
            return dict(status='complete', dataset_version=version, schema_version=1,
                        source_sha256=source_hash,
                        mapping_sha256=binding['mapping_sha256'],
                        repeated=True, **counts)
        store.stage(version, source_records=0, source_sha256=source_hash,
                    mapping_sha256=binding['mapping_sha256'],
                    time_policy_sha256=binding['time_policy_sha256'])
        try:
            with args.source.open('rb') as stream:
                measured = _MeasuredReader(stream)
                with io.BufferedReader(measured) as parser_stream:
                    counts = store.ingest_canonical_rows(version, iter_canonical_rows(
                        parser_stream, namespace=args.namespace, member=binding['member'],
                        compact_collision_index=True))
                if (measured.hexdigest() != source_hash or measured.size != source_size):
                    raise ValueError('source_mismatch')
            store.set_source_records(version, counts['source_records'])
            if not (counts['source_records'] == counts['event_valid'] + counts['event_rejected']
                    and counts['event_valid'] == counts['label_eligible'] + counts['label_ineligible']
                    and counts['label_eligible'] == counts['positives'] + counts['negatives']):
                raise ValueError('row_reconciliation_failed')
            store.complete(version)
            store.activate(version)
        except Exception:
            if store.version_status(version) == 'staged':
                store.fail(version, reason='import_failed')
            raise
        counts = store.complete_report(version)
        return dict(status='complete', dataset_version=version, schema_version=1,
                    source_sha256=source_hash,
                    mapping_sha256=binding['mapping_sha256'],
                    repeated=False, **counts)
    finally:
        store.close()


def _build_features(args) -> dict:
    store = DatasetStore(args.store)
    try:
        result = store.build_features(args.dataset_version,
                                      feature_version=args.feature_version)
        return {'status': 'complete', 'dataset_version': args.dataset_version,
                'feature_version': args.feature_version, **result}
    finally:
        store.close()


def _freeze_protocol(args) -> dict:
    if not args.store.is_file():
        raise ValueError('source_missing')
    if not args.config.is_file():
        raise ValueError('protocol_missing')
    raw = args.config.read_bytes()
    protocol = json.loads(raw)
    audit = audit_sqlite_split(args.store, args.dataset_version)
    split = protocol.get('split', {})
    if (protocol.get('dataset_version') != audit['dataset_version']
            or protocol.get('source_sha256') != audit['source_sha256']
            or split.get('train_end_inclusive') != audit['train_end']
            or split.get('validation_end_inclusive') != audit['validation_end']
            or split.get('partitions') != audit['partitions']
            or protocol.get('eligibility', {}).get('eligible') != audit['eligible']):
        raise ValueError('protocol_source_mismatch')
    if not audit['eligible']:
        raise ValueError('source_ineligible')
    return {'status': 'frozen', 'protocol_sha256': hashlib.sha256(raw).hexdigest(),
            'dataset_version': args.dataset_version, 'eligible': audit['eligible']}


def _evaluate(args) -> dict:
    if args.report.exists():
        raise ValueError('report_exists')
    protocol_bytes = args.protocol.read_bytes()
    protocol = json.loads(protocol_bytes)
    prediction_bytes = args.predictions.read_bytes()
    bundle = json.loads(prediction_bytes)
    if (bundle.get('frozen') is not True
            or bundle.get('candidate_status') != 'selected'
            or bundle.get('protocol_sha256') != hashlib.sha256(protocol_bytes).hexdigest()
            or set(bundle.get('predictions', {})) != {'model', 'rules'}
            or set(bundle.get('thresholds', {})) != {'model', 'rules'}):
        raise ValueError('frozen_predictions_required')
    model_ids = [row[0] for row in bundle['predictions']['model']]
    rules_ids = [row[0] for row in bundle['predictions']['rules']]
    if (not model_ids or len(set(model_ids)) != len(model_ids)
            or model_ids != rules_ids):
        raise ValueError('prediction_identities_mismatch')
    expected_ids_hash = (protocol.get('split', {}).get('partitions', {})
                         .get('test', {}).get('ids_sha256'))
    if expected_ids_hash is not None:
        actual_ids_hash = hashlib.sha256(
            ''.join(event_id + '\n' for event_id in model_ids).encode('ascii')).hexdigest()
        if actual_ids_hash != expected_ids_hash:
            raise ValueError('prediction_identities_mismatch')
    if not args.labels.is_file():
        raise ValueError('labels_missing')
    predictions_hash = hashlib.sha256(prediction_bytes).hexdigest()
    disclosure = consume_holdout(args.ledger, bundle['protocol_sha256'],
                                 predictions_hash)
    labels = json.loads(args.labels.read_text())
    metrics = evaluate_frozen(bundle['predictions'], labels, bundle['thresholds'],
                              account_seen=bundle.get('account_seen'))
    report = {'status': 'complete', 'protocol_sha256': bundle['protocol_sha256'],
              'predictions_sha256': predictions_hash, 'disclosure': disclosure,
              'prior_test_exposure': protocol.get('holdout', {}).get(
                  'old_tree_60_20_20_test_exposure', False),
              'independent_confirmatory_claim': False,
              'metrics': metrics}
    encoded = json.dumps(report, indent=2, sort_keys=True).encode() + b'\n'
    with args.report.open('xb') as output:
        output.write(encoded)
    return {'status': 'complete', 'report_sha256': hashlib.sha256(encoded).hexdigest(),
            'disclosure': disclosure}


def _utc(value):
    return value.astimezone(__import__('datetime').UTC).isoformat().replace('+00:00', 'Z')


def _public_assessment(assessment):
    value = asdict(assessment)
    value.pop('artifact_version')
    for key in ('event_time_utc', 'history_cutoff_exclusive_at', 'scored_at'):
        value[key] = _utc(value[key])
    value['score'] = float(value['score'])
    value['history_coverage']['start'] = _utc(value['history_coverage']['start'])
    explanation = value['explanation']
    if explanation['status'] == 'available':
        explanation.pop('reason_code')
        explanation['items'] = list(explanation['items'])
        for key in ('base_value', 'remainder'):
            if explanation[key] is not None:
                explanation[key] = float(explanation[key])
        for item in explanation['items']:
            item['contribution'] = float(item['contribution'])
    else:
        for key in ('method', 'explained_scale', 'partial', 'base_value',
                    'remainder', 'items'):
            explanation.pop(key)
    return value


def _public_transaction(event):
    return {'transaction_id': event.transaction_id,
            'event_time_utc': _utc(event.event_time_utc),
            'event_time_raw': event.event_time_raw,
            'time_basis': ('assumed_utc_for_synthetic_benchmark'
                           if event.time_basis == 'assumed_utc' else event.time_basis),
            'sender': {'bank': event.sender_bank, 'account': event.sender_account},
            'receiver': {'bank': event.receiver_bank, 'account': event.receiver_account},
            'paid': {'amount': event.paid_amount, 'currency': event.paid_currency},
            'received': {'amount': event.received_amount,
                         'currency': event.received_currency},
            'payment_format': event.payment_format}


def _source_row(row, version):
    (transaction_id, case_id, event_payload, event_time, as_of, coverage_start,
     coverage_state, scoreable, digest, created_at, feature_payload) = row
    facts = json.loads(event_payload)
    event = CanonicalTransaction(
        transaction_id, case_id, facts['source_ordinal'], facts['event_time_raw'],
        datetime.fromisoformat(facts['event_time_utc']), facts['event_time_epoch_ns'],
        facts['time_basis'], facts['sender_bank'], facts['sender_account'],
        facts['receiver_bank'], facts['receiver_account'],
        bytes.fromhex(facts['sender_join_key']),
        bytes.fromhex(facts['receiver_join_key']), facts['paid_amount'],
        facts['paid_currency'], facts['received_amount'], facts['received_currency'],
        facts['payment_format'], bytes.fromhex(facts['event_fact_digest']))
    values = json.loads(feature_payload)
    for key in ('sender_paid_sum_same_currency_24h',
                'receiver_received_sum_same_currency_24h', 'current_paid_amount'):
        if values[key] is not None:
            values[key] = Decimal(values[key])
    snapshot = HistoricalFeatureSnapshot(
        transaction_id, version, 'history-v1', datetime.fromisoformat(event_time),
        datetime.fromisoformat(as_of), datetime.fromisoformat(coverage_start),
        coverage_state, bool(scoreable), values, digest,
        datetime.fromisoformat(created_at))
    return event, snapshot


def _score_run(args):
    if (args.source_store.resolve() == args.run_store.resolve()
            or not args.source_store.is_file() or not args.protocol.is_file()):
        raise ValueError('source_missing_or_output_conflict')
    protocol_raw = args.protocol.read_bytes()
    protocol = json.loads(protocol_raw)
    threshold = protocol[f'{args.scorer}_validation_threshold']['threshold']
    if (protocol['dataset_version'] != args.dataset_version
            or protocol['feature_version'] != 'history-v1'
            or threshold != args.threshold):
        raise ValueError('frozen_publication_mismatch')
    artifact_sha = None
    if args.scorer == 'rules':
        if args.artifact_dir is not None or args.manifest_sha is not None:
            raise ValueError('rules require no artifact')
        scorer = RuleScorer()
        scorer_version = 'rules-v1'
    else:
        if args.artifact_dir is None or args.manifest_sha is None:
            raise ValueError('verified model artifact required')
        artifact = load_trusted_artifact(
            args.artifact_dir, expected_manifest_sha256=args.manifest_sha,
            expected_dataset_version=args.dataset_version,
            expected_protocol_sha256=protocol.get(
                'protocol_sha256', hashlib.sha256(protocol_raw).hexdigest()))
        scorer = ModelScorer(artifact)
        scorer_version = 'model-history-v1'
        artifact_sha = artifact.manifest_sha256
    source = sqlite3.connect(f'{args.source_store.resolve().as_uri()}?mode=ro', uri=True)
    source.execute('PRAGMA query_only=ON')
    try:
        if (source.execute('SELECT status FROM dataset_versions WHERE id=?',
                           (args.dataset_version,)).fetchone() != ('complete',)
                or source.execute('''
                    SELECT status FROM feature_builds
                    WHERE version=? AND feature_version='history-v1' ''',
                    (args.dataset_version,)).fetchone() != ('complete',)):
            raise ValueError('source build incomplete')
        count = source.execute('''
            SELECT COUNT(*) FROM feature_snapshots WHERE version=?
              AND feature_version='history-v1' AND scoreable=1''',
            (args.dataset_version,)).fetchone()[0]
        runs = RunStore(args.run_store)
        try:
            runs.begin_run(args.run_id, args.dataset_version, args.scorer,
                           scorer_version, artifact_sha, threshold, count)
            cursor = source.execute('''
                SELECT s.transaction_id,e.case_id,e.payload_json,s.event_time,s.as_of,
                       s.coverage_start,s.coverage_state,s.scoreable,
                       s.feature_input_digest,s.created_at,s.payload_json
                FROM feature_snapshots AS s JOIN operational_events AS e
                  ON e.version=s.version AND e.transaction_id=s.transaction_id
                WHERE s.version=? AND s.feature_version='history-v1'
                  AND s.scoreable=1 ORDER BY s.event_time,s.transaction_id''',
                (args.dataset_version,))
            for row in cursor:
                event, snapshot = _source_row(row, args.dataset_version)
                request = ScoreRequestV2(event, snapshot, args.dataset_version,
                                         args.run_id, scorer_version, 'history-v1',
                                         event.event_time_utc)
                assessment = (score_v2(request, scorer) if args.scorer == 'rules'
                              else scorer.assess(request))
                runs.append(args.run_id, event.case_id, _public_transaction(event),
                            _public_assessment(assessment))
            runs.complete(args.run_id)
            return {'status': 'completed', 'run_id': args.run_id, 'scored_count': count,
                    'score_source': args.scorer, 'threshold': threshold}
        finally:
            runs.close()
    finally:
        source.close()


def _activate_run(args):
    runs = RunStore(args.run_store)
    try:
        runs.activate(args.run_id, args.scorer, args.manifest_sha)
        return {'status': 'active', 'run_id': args.run_id,
                'score_source': args.scorer}
    finally:
        runs.close()


def validate_reproduction_files(protocol, prediction_bytes, report):
    if (not protocol.get('holdout', {}).get('old_tree_60_20_20_test_exposure')
            or report.get('prior_test_exposure') is not True
            or report.get('independent_confirmatory_claim') is True
            or report.get('predictions_sha256')
            != hashlib.sha256(prediction_bytes).hexdigest()):
        raise ValueError('frozen report, prediction hash or exposure mismatch')
    return {'prior_test_exposure': True}


def compare_reproduction(protocol, original, repeated, report, repeated_metrics):
    """Compare frozen semantics and numeric values; exclude run/time/resource metadata."""
    for field in ('protocol_sha256', 'manifest_sha256', 'source_sha256',
                  'dataset_version', 'feature_version', 'ordered_features',
                  'thresholds', 'test_ids_sha256'):
        if original.get(field) != repeated.get(field):
            raise ValueError(f'frozen {field} changed')
    if (report.get('prior_test_exposure') is not True
            or not protocol.get('holdout', {}).get('old_tree_60_20_20_test_exposure')):
        raise ValueError('consumed test exposure missing')
    probability_tolerance = protocol['reproduction_tolerances']['probability_absolute']
    metric_tolerance = protocol['reproduction_tolerances']['metric_absolute']
    max_prediction = 0.0
    for scorer in ('model', 'rules'):
        before = original['predictions'][scorer]
        after = repeated['predictions'][scorer]
        if len(before) != len(after):
            raise ValueError('prediction row count changed')
        for (first_id, first_score), (next_id, next_score) in zip(
                before, after, strict=True):
            if first_id != next_id:
                raise ValueError('prediction identity changed')
            difference = abs(float(first_score) - float(next_score))
            if not math.isfinite(difference) or difference > probability_tolerance:
                raise ValueError('prediction tolerance exceeded')
            max_prediction = max(max_prediction, difference)

    max_metric = 0.0

    def compare(before, after):
        nonlocal max_metric
        if type(before) is not type(after):
            raise ValueError('metric type changed')
        if isinstance(before, dict):
            if set(before) != set(after):
                raise ValueError('metric shape changed')
            for key in before:
                compare(before[key], after[key])
        elif isinstance(before, list):
            if len(before) != len(after):
                raise ValueError('metric bin count changed')
            for first, second in zip(before, after, strict=True):
                compare(first, second)
        elif type(before) is float:
            difference = abs(before - after)
            if not math.isfinite(difference) or difference > metric_tolerance:
                raise ValueError('metric tolerance exceeded')
            max_metric = max(max_metric, difference)
        elif before != after:
            raise ValueError('metric semantic value changed')

    compare(report['metrics'], repeated_metrics)
    return {'status': 'exploratory_reuse',
            'prior_test_exposure': True,
            'max_prediction_abs_diff': max_prediction,
            'max_metric_abs_diff': max_metric,
            'prediction_tolerance': probability_tolerance,
            'metric_tolerance': metric_tolerance}


def _reproduce(args):
    for path in (args.source_store, args.protocol, args.artifact_dir,
                 args.predictions, args.report, args.ledger):
        if not path.exists():
            raise ValueError('reproduction input missing')
    if args.out_dir.exists():
        raise ValueError('reproduction output exists')
    protocol_raw = args.protocol.read_bytes()
    protocol = json.loads(protocol_raw)
    original_raw = args.predictions.read_bytes()
    original = json.loads(original_raw)
    report = json.loads(args.report.read_text())
    validate_reproduction_files(protocol, original_raw, report)
    protocol_sha = hashlib.sha256(protocol_raw).hexdigest()
    if (original.get('protocol_sha256') != protocol_sha
            or original.get('manifest_sha256') != args.manifest_sha
            or report.get('protocol_sha256') != protocol_sha):
        raise ValueError('reproduction frozen hash mismatch')
    if consume_holdout(args.ledger, protocol_sha,
                       hashlib.sha256(original_raw).hexdigest()) != 'exploratory_reuse':
        raise ValueError('holdout has not been consumed')
    args.out_dir.mkdir(parents=True)
    repeated_path = args.out_dir / 'predictions.json'
    labels_path = args.out_dir / 'labels.json'
    benchmark_predict(args.source_store, args.protocol, args.artifact_dir,
                      args.manifest_sha, repeated_path)
    benchmark_labels(args.source_store, args.protocol, repeated_path, labels_path)
    repeated = json.loads(repeated_path.read_text())
    truth = json.loads(labels_path.read_text())
    metrics = evaluate_frozen(repeated['predictions'], truth,
                              repeated['thresholds'])
    result = compare_reproduction(protocol, original, repeated, report, metrics)
    result.update({'original_predictions_sha256': hashlib.sha256(original_raw).hexdigest(),
                   'repeated_predictions_sha256': hashlib.sha256(
                       repeated_path.read_bytes()).hexdigest(),
                   'report_sha256': hashlib.sha256(args.report.read_bytes()).hexdigest(),
                   'rows': len(repeated['predictions']['model'])})
    (args.out_dir / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main(argv=None):
    parser = _Arguments(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect')
    inspect.add_argument('--source', type=Path, required=True)
    inspect.add_argument('--source-name')
    inspect.add_argument('--release')
    inspect.add_argument('--license-ref')
    inspect.add_argument('--expected-sha256')
    inspect.add_argument('--mapping', type=Path,
                         help='Source-bound pending configuration for read-only inspection only')
    inspect.add_argument('--encoding', default='utf-8')
    inspect.add_argument('--delimiter', default=',')
    inspect.add_argument('--column', action='append', default=[], metavar='ROLE=INDEX',
                         help='Zero-based inspection-only role; never an approved mapping')
    import_command = commands.add_parser('import')
    import_command.add_argument('--source', type=Path, required=True)
    import_command.add_argument('--mapping', type=Path, required=True)
    import_command.add_argument('--namespace', required=True)
    import_command.add_argument('--expected-sha256', required=True)
    import_command.add_argument('--store', type=Path, required=True)
    features = commands.add_parser('build-features')
    features.add_argument('--store', type=Path, required=True)
    features.add_argument('--dataset-version', required=True)
    features.add_argument('--feature-version', default='history-v1')
    freeze = commands.add_parser('freeze-protocol')
    freeze.add_argument('--store', type=Path, required=True)
    freeze.add_argument('--dataset-version', required=True)
    freeze.add_argument('--config', type=Path, required=True)
    evaluate = commands.add_parser('evaluate')
    evaluate.add_argument('--protocol', type=Path, required=True)
    evaluate.add_argument('--predictions', type=Path, required=True)
    evaluate.add_argument('--labels', type=Path, required=True)
    evaluate.add_argument('--ledger', type=Path, required=True)
    evaluate.add_argument('--report', type=Path, required=True)
    score_run = commands.add_parser('score-run')
    score_run.add_argument('--source-store', type=Path, required=True)
    score_run.add_argument('--run-store', type=Path, required=True)
    score_run.add_argument('--dataset-version', required=True)
    score_run.add_argument('--protocol', type=Path, required=True)
    score_run.add_argument('--run-id', required=True)
    score_run.add_argument('--scorer', choices=('rules', 'model'), required=True)
    score_run.add_argument('--threshold', required=True)
    score_run.add_argument('--artifact-dir', type=Path)
    score_run.add_argument('--manifest-sha')
    activate_run = commands.add_parser('activate-run')
    activate_run.add_argument('--run-store', type=Path, required=True)
    activate_run.add_argument('--run-id', required=True)
    activate_run.add_argument('--scorer', choices=('rules', 'model'), required=True)
    activate_run.add_argument('--manifest-sha')
    reproduce = commands.add_parser('reproduce')
    reproduce.add_argument('--source-store', type=Path, required=True)
    reproduce.add_argument('--protocol', type=Path, required=True)
    reproduce.add_argument('--artifact-dir', type=Path, required=True)
    reproduce.add_argument('--manifest-sha', required=True)
    reproduce.add_argument('--predictions', type=Path, required=True)
    reproduce.add_argument('--report', type=Path, required=True)
    reproduce.add_argument('--ledger', type=Path, required=True)
    reproduce.add_argument('--out-dir', type=Path, required=True)
    args = None
    try:
        args = parser.parse_args(argv)
        if args.command == 'import':
            report = _import(args)
            print(json.dumps(report, ensure_ascii=True, sort_keys=True))
            print('Import complete', file=sys.stderr)
            return 0
        if args.command == 'build-features':
            report = _build_features(args)
            print(json.dumps(report, ensure_ascii=True, sort_keys=True))
            print('Feature build complete', file=sys.stderr)
            return 0
        if args.command == 'freeze-protocol':
            report = _freeze_protocol(args)
            print(json.dumps(report, ensure_ascii=True, sort_keys=True))
            return 0
        if args.command == 'evaluate':
            report = _evaluate(args)
            print(json.dumps(report, ensure_ascii=True, sort_keys=True))
            return 0
        if args.command == 'score-run':
            print(json.dumps(_score_run(args), sort_keys=True))
            return 0
        if args.command == 'activate-run':
            print(json.dumps(_activate_run(args), sort_keys=True))
            return 0
        if args.command == 'reproduce':
            print(json.dumps(_reproduce(args), sort_keys=True))
            return 0
        columns = {}
        for declaration in args.column:
            role, index = declaration.split('=')
            if role in columns:
                raise ValueError('invalid_arguments')
            columns[role] = int(index)
        report = inspect_source(source=args.source, source_name=args.source_name,
                                release=args.release, license_ref=args.license_ref,
                                expected_sha256=args.expected_sha256, encoding=args.encoding,
                                delimiter=args.delimiter, columns=columns or None,
                                mapping_path=args.mapping)
    except (ValueError, OSError, sqlite3.Error, KeyError, json.JSONDecodeError) as exc:
        if args is not None and args.command in {'import', 'build-features', 'freeze-protocol', 'evaluate'} and isinstance(exc, ValueError) and str(exc) in {
                'source_binding_mismatch', 'source_mismatch', 'mapping_mismatch',
                'mapping_approval_mismatch', 'row_reconciliation_failed',
                'dataset_incomplete', 'dataset_incompatible', 'feature_count_mismatch',
                'feature_build_in_progress', 'source_missing', 'protocol_missing',
                'protocol_source_mismatch', 'frozen_predictions_required',
                'report_exists', 'source_ineligible', 'labels_missing',
                'prediction_identities_mismatch'}:
            code = str(exc)
        else:
            code = ('invalid_arguments' if isinstance(exc, ValueError) else
                    'feature_build_failed' if args is not None and
                    args.command == 'build-features' else 'import_failed')
        report = dict(status='failed', error_codes=[code])
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    if args is not None and args.command == 'import':
        print(f"Import {report['status']}; {','.join(report['error_codes'])}", file=sys.stderr)
    elif args is not None and args.command == 'build-features':
        print(f"Feature build {report['status']}; {','.join(report['error_codes'])}",
              file=sys.stderr)
    else:
        print(f"Inspection {report['status']}; "
              f"{','.join(report['error_codes']) or 'complete read-only scan; mapping unreviewed'}",
              file=sys.stderr)
    return 0 if report['status'] == 'inspected' else 2


if __name__ == '__main__':
    raise SystemExit(main())
