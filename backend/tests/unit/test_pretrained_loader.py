"""RED checks for a verified, optional IBM AML LightGBM loader.

All local model and graph bytes here are authored test stubs. A fake native
booster supplies metadata; no publisher model, joblib object or dataset is read.
"""

import hashlib
import importlib
import json
import pickle
import sys
from pathlib import Path

import joblib
import pytest

from fraudlens.contracts import Transaction
from fraudlens.scoring import FixtureScorer

REVISION = '4fc397afa0e22396d26153d69e46e46304411ca0'
PUBLISHER_PREPROC_SHA = '189ab48262821327abfdd38c04923608954e7869ca59801ef3c1291698236a76'
SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
VERSION = 'dv_' + 'a' * 64
NAMES = (
    'hour', 'dow', 'log_paid', 'log_recv', 'amt_diff', 'ccy_mismatch',
    'self_loop', 'is_round', 'same_bank', 'snd_out_deg', 'snd_in_deg',
    'snd_out_cnt', 'snd_in_cnt', 'snd_out_amt_mean', 'rcv_out_deg',
    'rcv_in_deg', 'rcv_in_cnt', 'gather_scatter', 'amt_to_snd_mean',
    'Receiving Currency', 'Payment Currency', 'Payment Format',
)
CATS = ('Receiving Currency', 'Payment Currency', 'Payment Format')
MODEL_BYTES = (
    'tree\nversion=v4\nnum_class=1\nmax_feature_idx=21\n'
    'objective=binary sigmoid:1\nfeature_names=' + ' '.join(NAMES) + '\n'
).encode('utf-8')
GRAPH_BYTES = json.dumps(
    {'schema': 'fraudsentinel-ibm-graph-v1', 'source_sha256': SOURCE_SHA,
     'dataset_version': VERSION, 'model_revision': REVISION,
     'features': NAMES, 'cat_cols': CATS, 'training_end_exclusive': '2026-01-04T00:00:00Z',
     'account_identity_policy': 'unqualified_account_collision_checked',
     'coverage_complete': True,
     'account_bank_index': {'sender-1': 'Bank A', 'receiver-2': 'Bank A'},
     'graph': {
         'out_deg': {'sender-1': 1}, 'in_deg': {'receiver-2': 1},
         'out_cnt': {'sender-1': 1}, 'in_cnt': {'receiver-2': 1},
         'out_amt_mean': {'sender-1': 100.0},
     }},
    sort_keys=True, separators=(',', ':'),
).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def api():
    # Collection succeeds even before the loader exists. The missing boundary
    # becomes an explicit in-test assertion rather than a setup/import crash.
    try:
        module = importlib.import_module('fraudlens.pretrained')
    except ModuleNotFoundError as exc:
        if exc.name != 'fraudlens.pretrained':
            raise
        pytest.fail('RED: verified pretrained loader is not implemented')
    assert callable(getattr(module, 'load_approved_model', None)), (
        'RED: load_approved_model is not implemented'
    )
    return module


class FakeBooster:
    def __init__(self, names=NAMES, categorical_values=None):
        self.names = names
        self.pandas_categorical = (
            [['US Dollar'], ['Euro'], ['Wire']]
            if categorical_values is None else categorical_values
        )

    def feature_name(self):
        return list(self.names)

    def num_feature(self):
        return len(self.names)

    def fit(self, *_args, **_kwargs):
        pytest.fail('Loading must never fit the model')

    def train(self, *_args, **_kwargs):
        pytest.fail('Loading must never train the model')

    def partial_fit(self, *_args, **_kwargs):
        pytest.fail('Loading must never refit the model')


class FakeNativeFactory:
    def __init__(self, booster=None):
        self.booster = FakeBooster() if booster is None else booster
        self.calls = []

    def __call__(self, path):
        self.calls.append(Path(path))
        return self.booster


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / 'artifacts'
    root.mkdir()
    (root / 'aml_lgbm_model.txt').write_bytes(MODEL_BYTES)
    (root / 'aml_lgbm_graph.json').write_bytes(GRAPH_BYTES)
    manifest = {
        'manifest_schema': 'fraudlens-pretrained-ibm-v1',
        'model_id': 'fraudsentinel-ibm-hi-small-aml-lightgbm',
        'domain': 'ibm_hi_small_is_laundering',
        'upstream_repo': 'naazimsnh02/fraudsentinel-tier1-scorers',
        'upstream_revision': REVISION,
        'source_sha256': SOURCE_SHA,
        'dataset_version': VERSION,
        'model_file': 'aml_lgbm_model.txt',
        'model_sha256': sha(MODEL_BYTES),
        'model_size_bytes': len(MODEL_BYTES),
        'model_format': 'lightgbm_native_text',
        'model_objective': 'binary',
        'preprocessing_source_file': 'aml_lgbm_preproc.joblib',
        'preprocessing_source_sha256': PUBLISHER_PREPROC_SHA,
        'graph_file': 'aml_lgbm_graph.json',
        'graph_sha256': sha(GRAPH_BYTES),
        'graph_training_end_exclusive': '2026-01-04T00:00:00Z',
        'graph_identity_policy': 'unqualified_account_collision_checked',
        'feature_policy': 'fraudsentinel-ibm-aml-v1',
        'feature_names': list(NAMES),
        'categorical_columns': list(CATS),
        'runtime': {'python': '3.14', 'lightgbm': 'approved-version-stub'},
    }
    return root, manifest


def load(bundle, *, factory=None, manifest=None):
    root, approved = bundle
    return api().load_approved_model(
        artifact_root=root,
        manifest=approved if manifest is None else manifest,
        native_booster_factory=FakeNativeFactory() if factory is None else factory,
    )


def rejected(bundle, reason, *, factory=None, manifest=None):
    module = api()
    spy = FakeNativeFactory() if factory is None else factory
    with pytest.raises(module.PretrainedLoadError) as caught:
        load(bundle, factory=spy, manifest=manifest)
    assert caught.value.reason_code == reason
    assert not spy.calls, 'Rejected bytes must never reach native parsing'


def test_authored_bundle_pins_ibm_identity_revision_and_exact_test_checksums(bundle):
    _, spec = bundle
    assert spec['model_id'] == 'fraudsentinel-ibm-hi-small-aml-lightgbm'
    assert spec['domain'] == 'ibm_hi_small_is_laundering'
    assert 'apexfi' not in repr(spec).lower()
    assert spec['upstream_revision'] == REVISION
    assert spec['model_sha256'] == sha(MODEL_BYTES)
    assert spec['graph_sha256'] == sha(GRAPH_BYTES)
    assert spec['preprocessing_source_sha256'] == PUBLISHER_PREPROC_SHA
    assert spec['model_format'] == 'lightgbm_native_text'
    assert tuple(spec['feature_names']) == NAMES
    assert tuple(spec['categorical_columns']) == CATS


def test_valid_local_native_artifact_reaches_only_fake_booster(bundle):
    factory = FakeNativeFactory()
    result = load(bundle, factory=factory)
    assert len(factory.calls) == 1
    assert factory.calls[0].name == 'aml_lgbm_model.txt'
    assert result.model_id == 'fraudsentinel-ibm-hi-small-aml-lightgbm'
    assert result.revision == REVISION
    assert result.model_sha256 == sha(MODEL_BYTES)
    assert tuple(result.feature_names) == NAMES
    assert tuple(result.categorical_columns) == CATS


def test_missing_model_is_unavailable_without_zero_risk_fallback(bundle):
    (bundle[0] / 'aml_lgbm_model.txt').unlink()
    rejected(bundle, 'model_unavailable')


@pytest.mark.parametrize('content', [b'', MODEL_BYTES[:-11], MODEL_BYTES + b'modified'])
def test_corrupt_truncated_or_modified_model_rejects_before_native_load(bundle, content):
    (bundle[0] / 'aml_lgbm_model.txt').write_bytes(content)
    rejected(bundle, 'model_integrity_mismatch')


def test_substituted_wrong_domain_artifact_rejects_even_with_recomputed_hash(bundle):
    other = b'tree\nobjective=binary sigmoid:1\nfeature_names=card1 TransactionDT\n'
    (bundle[0] / 'aml_lgbm_model.txt').write_bytes(other)
    spec = {**bundle[1], 'model_sha256': sha(other), 'model_size_bytes': len(other)}
    rejected(bundle, 'model_schema_mismatch', manifest=spec)


@pytest.mark.parametrize('field,value', [
    ('model_id', 'apexfi-ieee-cis'), ('domain', 'ieee_cis_isFraud'),
    ('upstream_revision', 'main'), ('upstream_revision', '0' * 40),
    ('model_format', 'pickle'), ('model_format', 'joblib'),
    ('model_file', 'model.pkl'), ('preprocessing_source_file', 'preproc.pkl'),
])
def test_wrong_model_revision_or_serialization_is_rejected(bundle, field, value):
    rejected(bundle, 'unapproved_manifest', manifest={**bundle[1], field: value})


@pytest.mark.parametrize('field,value', [
    ('model_sha256', '0' * 64), ('graph_sha256', '0' * 64),
    ('preprocessing_source_sha256', '0' * 64),
])
def test_expected_hash_mismatch_is_rejected(bundle, field, value):
    rejected(bundle, 'artifact_integrity_mismatch',
             manifest={**bundle[1], field: value})


def test_ieee_fields_cannot_replace_exact_ibm_schema(bundle):
    names = list(NAMES)
    names[0] = 'TransactionDT'
    names[-1] = 'card1'
    rejected(bundle, 'model_schema_mismatch',
             manifest={**bundle[1], 'feature_names': names})


def test_feature_order_count_and_categorical_fields_are_verified(bundle):
    reversed_names = list(reversed(NAMES))
    rejected(bundle, 'model_schema_mismatch',
             manifest={**bundle[1], 'feature_names': reversed_names})
    rejected(bundle, 'model_schema_mismatch',
             manifest={**bundle[1], 'categorical_columns': ['Payment Format']})


def test_native_booster_feature_metadata_must_agree_with_manifest(bundle):
    factory = FakeNativeFactory(FakeBooster(names=NAMES[::-1]))
    module = api()
    with pytest.raises(module.PretrainedLoadError) as caught:
        load(bundle, factory=factory)
    assert caught.value.reason_code == 'model_schema_mismatch'
    assert len(factory.calls) == 1


def test_native_categorical_metadata_must_agree_with_manifest(bundle):
    factory = FakeNativeFactory(FakeBooster(categorical_values=[['Wire']]))
    module = api()
    with pytest.raises(module.PretrainedLoadError) as caught:
        load(bundle, factory=factory)
    assert caught.value.reason_code == 'model_schema_mismatch'
    assert len(factory.calls) == 1


@pytest.mark.parametrize('runtime', [
    {'python': '3.13', 'lightgbm': 'approved-version-stub'},
    {'python': '3.14', 'lightgbm': 'unsupported-version'},
])
def test_unsupported_runtime_rejects_before_native_load(bundle, runtime):
    rejected(bundle, 'unsupported_runtime',
             manifest={**bundle[1], 'runtime': runtime})


def test_missing_or_changed_graph_state_fails_before_native_load(bundle):
    path = bundle[0] / 'aml_lgbm_graph.json'
    path.unlink()
    rejected(bundle, 'graph_state_unavailable')
    path.write_bytes(GRAPH_BYTES + b'changed')
    rejected(bundle, 'graph_state_integrity_mismatch')


@pytest.mark.parametrize('key,value', [
    ('account_identity_policy', 'bank_qualified_as_if_original'),
    ('coverage_complete', False),
    ('training_end_exclusive', '2026-01-06T00:00:00Z'),
])
def test_incompatible_identity_or_temporal_graph_metadata_is_rejected(bundle, key, value):
    data = json.loads(GRAPH_BYTES)
    data[key] = value
    changed = json.dumps(data, sort_keys=True, separators=(',', ':')).encode()
    (bundle[0] / 'aml_lgbm_graph.json').write_bytes(changed)
    spec = {**bundle[1], 'graph_sha256': sha(changed)}
    rejected(bundle, 'incompatible_graph_state', manifest=spec)


def test_untrusted_joblib_and_pickle_are_never_deserialized(bundle, monkeypatch):
    calls = []

    def forbidden(*_args, **_kwargs):
        calls.append('unsafe_deserialization')
        raise AssertionError('Untrusted deserialization is forbidden')

    monkeypatch.setattr(joblib, 'load', forbidden)
    monkeypatch.setattr(pickle, 'load', forbidden)
    load(bundle)
    assert calls == []


def test_loader_never_trains_or_refits_and_never_contacts_network(bundle, monkeypatch):
    calls = []

    def forbidden(*_args, **_kwargs):
        calls.append('network')
        raise AssertionError('Loader must stay local')

    monkeypatch.setattr('urllib.request.urlopen', forbidden)
    monkeypatch.setitem(sys.modules, 'requests', None)
    result = load(bundle, factory=FakeNativeFactory(FakeBooster()))
    assert result.model_id == bundle[1]['model_id']
    assert calls == []


def test_label_or_holdout_metadata_in_manifest_is_rejected(bundle):
    spec = {**bundle[1], 'Is Laundering': 1, 'holdout_labels': [0, 1]}
    rejected(bundle, 'unapproved_manifest', manifest=spec)


def test_fixture_scorer_still_operates_when_pretrained_artifact_is_absent(bundle):
    (bundle[0] / 'aml_lgbm_model.txt').unlink()
    tx = Transaction(
        transaction_id='TX-001', occurred_at='2026-01-01T10:00:00Z',
        sender_account='DEMO-BANK-A:001', receiver_account='DEMO-BANK-B:002',
        amount='1250.00', currency='EUR',
    )
    result = FixtureScorer().score(tx)
    assert result.source == 'fixture'
    assert result.score == 0.75


def test_rules_scorer_still_imports_without_pretrained_artifact(bundle):
    (bundle[0] / 'aml_lgbm_model.txt').unlink()
    module = importlib.import_module('fraudlens.rule_scoring')
    assert callable(getattr(module, 'RuleScorer', None))
