"""Read-only verified bridge consumer; never accepts caller paths or SQL."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from fraudlens.bridge import validate_binding, validate_crosswalk
from fraudlens.data.manifest import sha256_file
from fraudlens.investigation.dataset import DatasetReader
from fraudlens.investigation.models import PRODUCER_V2
from fraudlens.scoring.model_scorer import (
    FEATURE_MANIFEST_SHA256,
    MANIFEST_SHA256,
    MODEL_SHA256,
    SOURCE_SHA256,
    THRESHOLD,
)

ACCEPTED_SHA256 = '8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba'
PREDICTIONS_SHA256 = '99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7'


class BridgeUnavailable(ValueError):
    pass


class BridgeNotFound(ValueError):
    pass


class BridgeReader:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.runs = self.root / 'runs.sqlite'
        self.dataset = self.root / 'dataset.sqlite'
        self.reader = DatasetReader(self.runs, self.dataset, 'model')

    def _check(self):
        try:
            raw = (self.root / 'manifest.json').read_bytes()
            if (self.root / 'COMPLETE').read_text().strip() != sha256_file(self.root / 'manifest.json'):
                raise ValueError('Completion marker mismatch')
            manifest = json.loads(raw)
            if (manifest['bridge_version'] != 1 or manifest['status'] != 'complete'
                    or manifest['source_sha256'] != SOURCE_SHA256
                    or manifest['model_sha256'] != MODEL_SHA256
                    or manifest['model_manifest_sha256'] != MANIFEST_SHA256
                    or manifest['accepted_sha256'] != ACCEPTED_SHA256
                    or manifest['predictions_sha256'] != PREDICTIONS_SHA256
                    or manifest['feature_manifest_sha256'] != FEATURE_MANIFEST_SHA256
                    or manifest['threshold'] != THRESHOLD
                    or sha256_file(self.runs) != manifest['runs_sha256']
                    or sha256_file(self.dataset) != manifest['dataset_sha256']):
                raise ValueError('Bridge manifest mismatch')
            return manifest
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            raise BridgeUnavailable('Bridge source unavailable') from None

    def _connection(self):
        db = sqlite3.connect(self.runs.resolve().as_uri() + '?mode=ro', uri=True, timeout=1)
        db.set_authorizer(lambda action, table, column, database, trigger:
                          sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_READ and table not in {
                              'active_run', 'scored_runs', 'scored_assessments', 'bridge_crosswalk'
                          } else sqlite3.SQLITE_OK)
        return db

    def _binding(self, canonical=None, case_id=None):
        manifest = self._check()
        if (canonical is None) == (case_id is None):
            raise ValueError('One identity required')
        with closing(self._connection()) as db:
            active = db.execute('SELECT run_id FROM active_run WHERE singleton=1').fetchone()
            if active is None or active[0] != manifest['run_id']:
                raise ValueError('stale_snapshot')
            column = 'canonical_id' if canonical is not None else 'case_id'
            needle = canonical if canonical is not None else case_id
            row = db.execute(f'SELECT binding_json FROM bridge_crosswalk WHERE {column}=?', (needle,)).fetchone()
            if row is None:
                raise BridgeNotFound('Published alert not found')
            binding = json.loads(row[0])
            validate_binding(binding, expected_run=manifest['run_id'])
            assessment = db.execute('SELECT transaction_json,assessment_json,alert FROM scored_assessments WHERE run_id=? AND case_id=?',
                                    (manifest['run_id'], binding['case_id'])).fetchone()
            if assessment is None or assessment[2] != 1:
                raise ValueError('Published assessment mismatch')
            tx, risk = json.loads(assessment[0]), json.loads(assessment[1])
            if (tx['transaction_id'] != binding['transaction_id']
                    or tx['event_time_utc'] != binding['event_time_utc']
                    or risk['score'] != binding['risk_score']
                    or risk['scored_at'] != binding['assessed_at_utc']
                    or risk['feature_version'] != binding['feature_version']):
                raise ValueError('Binding/assessment mismatch')
            return binding

    def binding(self, canonical):
        return self._binding(canonical=canonical)

    def resolve(self, case_id, snapshot_ref):
        binding = self._binding(case_id=case_id)
        if snapshot_ref is not None and snapshot_ref != binding['snapshot_ref']:
            raise ValueError('stale_snapshot')
        context = self.reader.resolve(case_id, binding['snapshot_ref'])
        if (context['source_payload']['risk_assessment']['score'] != binding['risk_score']
                or context['source_payload']['transaction']['transaction_id'] != binding['transaction_id']):
            raise ValueError('Bridge context mismatch')
        return context

    def read(self, context, account_side, limit=50):
        current = self.resolve(context['case_id'], context['snapshot_ref'])
        if current['context_revision'] != context['context_revision']:
            raise ValueError('stale_snapshot')
        return self.reader.read(context, account_side, limit)

    def detail(self, case_id, snapshot_ref=None):
        context = self.resolve(case_id, snapshot_ref)
        payload = context['source_payload']
        Draft202012Validator({**PRODUCER_V2, '$ref': '#/$defs/CaseDetailV2'},
                             format_checker=FormatChecker()).validate(payload)
        return payload

    def list_cases(self):
        manifest = self._check()
        with closing(self._connection()) as db:
            rows = db.execute('SELECT binding_json FROM bridge_crosswalk ORDER BY case_id').fetchall()
        bindings = [json.loads(row[0]) for row in rows]
        validate_crosswalk(bindings)
        bindings.sort(key=lambda item: (item['event_time_utc'], item['transaction_id']))
        if len(bindings) != manifest['alert_count']:
            raise BridgeUnavailable('Bridge count mismatch')
        items = []
        for binding in bindings[:100]:
            detail = self.detail(binding['case_id'], binding['snapshot_ref'])
            risk = detail['risk_assessment']
            items.append(dict(case_id=binding['case_id'], transaction_id=binding['transaction_id'],
                              event_time=binding['event_time_utc'], score=risk['score'],
                              score_kind=risk['score_kind'], score_source='model'))
        payload = dict(contract_version=2, snapshot_ref=manifest['run_id'],
                       dataset_version=manifest['dataset_version'], data_source='ibm_aml_hi_small',
                       score_source='model', scorer_version='lightgbm-'+MODEL_SHA256[:12],
                       total_alerts=len(bindings), displayed_count=len(items),
                       truncated=len(bindings)>len(items),
                       selected_time_range={'from':items[0]['event_time'] if items else None,
                                            'to':items[-1]['event_time'] if items else None},
                       items=items)
        Draft202012Validator({**PRODUCER_V2, '$ref': '#/$defs/CaseListV2'},
                             format_checker=FormatChecker()).validate(payload)
        return payload
