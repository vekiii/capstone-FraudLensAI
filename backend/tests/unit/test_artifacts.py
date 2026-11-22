"""T227 artifact integrity checks use invented bytes and never fit a model."""

import hashlib
import json
import sys

import pytest

from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
from fraudlens.scoring.artifacts import (
    ArtifactError,
    ArtifactMetadata,
    TrustedArtifact,
    read_verified_artifact,
    write_artifact,
)

HEX_A = 'a' * 64
HEX_B = 'b' * 64
MODEL = b'tree\nsynthetic model bytes\n'


def metadata(**changes):
    values = dict(
        feature_version=FEATURE_VERSION,
        feature_order=FEATURE_ORDER,
        currency_vocabulary=('USD', '__UNKNOWN__'),
        format_vocabulary=('Wire', '__UNKNOWN__'),
        source_sha256=HEX_A,
        protocol_sha256=HEX_B,
        code_revision='abc1234',
        seed=42,
        threshold=0.4,
        threshold_method='validation-positive-f1-v1',
        validation_metrics={'f1': 0.5, 'average_precision': 0.6},
    )
    values.update(changes)
    return ArtifactMetadata(**values)


def written(tmp_path):
    root = tmp_path / 'trusted'
    root.mkdir()
    digest = write_artifact(root, 'run-001', MODEL, metadata())
    trusted = TrustedArtifact(
        manifest_sha256=digest,
        source_sha256=HEX_A,
        protocol_sha256=HEX_B,
        feature_version=FEATURE_VERSION,
        feature_order=FEATURE_ORDER,
    )
    return root, trusted


def test_roundtrip_returns_bytes_and_compatible_metadata_without_deserializing(tmp_path):
    root, trusted = written(tmp_path)
    model, manifest = read_verified_artifact(root, 'run-001', trusted)
    assert model == MODEL
    assert manifest['model_sha256'] == hashlib.sha256(MODEL).hexdigest()
    assert manifest['currency_vocabulary'] == ['USD', '__UNKNOWN__']
    assert manifest['feature_order'] == list(FEATURE_ORDER)
    assert manifest['python_version'] == '.'.join(map(str, sys.version_info[:3]))


@pytest.mark.parametrize('field,value', [
    ('manifest_sha256', HEX_A), ('source_sha256', HEX_B),
    ('protocol_sha256', HEX_A), ('feature_version', 'changed-v1'),
    ('feature_order', tuple(reversed(FEATURE_ORDER))),
])
def test_independent_expectation_mismatch_fails_closed(tmp_path, field, value):
    root, trusted = written(tmp_path)
    altered = TrustedArtifact(**{**vars(trusted), field: value})
    with pytest.raises(ArtifactError):
        read_verified_artifact(root, 'run-001', altered)


def test_modified_model_fails_even_with_original_manifest(tmp_path):
    root, trusted = written(tmp_path)
    (root / 'run-001' / 'model.txt').write_bytes(b'changed')
    with pytest.raises(ArtifactError, match='model'):
        read_verified_artifact(root, 'run-001', trusted)


@pytest.mark.parametrize('raw', [b'{', b'{"format_version":1,"format_version":1}',
                                 b'{"format_version":NaN}'])
def test_malformed_or_duplicate_manifest_is_rejected_after_digest_check(tmp_path, raw):
    root, trusted = written(tmp_path)
    (root / 'run-001' / 'manifest.json').write_bytes(raw)
    trusted = TrustedArtifact(**{**vars(trusted), 'manifest_sha256': hashlib.sha256(raw).hexdigest()})
    with pytest.raises(ArtifactError):
        read_verified_artifact(root, 'run-001', trusted)


def test_manifest_and_model_replacement_cannot_use_old_trusted_digest(tmp_path):
    root, trusted = written(tmp_path)
    path = root / 'run-001' / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    replacement = b'forged native text'
    (root / 'run-001' / 'model.txt').write_bytes(replacement)
    manifest['model_sha256'] = hashlib.sha256(replacement).hexdigest()
    manifest['model_bytes'] = len(replacement)
    path.write_text(json.dumps(manifest), encoding='utf-8')
    with pytest.raises(ArtifactError, match='manifest digest'):
        read_verified_artifact(root, 'run-001', trusted)


@pytest.mark.parametrize('change', [
    {'lightgbm_version': '0.0'}, {'python_version': '0.0.0'},
    {'format_version': 99}, {'feature_order': ['wrong']},
    {'model_sha256': HEX_A}, {'unexpected': 'field'},
])
def test_manifest_fields_are_validated_even_when_digest_is_trusted(tmp_path, change):
    root, trusted = written(tmp_path)
    path = root / 'run-001' / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    manifest.update(change)
    raw = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()
    path.write_bytes(raw)
    trusted = TrustedArtifact(**{**vars(trusted), 'manifest_sha256': hashlib.sha256(raw).hexdigest()})
    with pytest.raises(ArtifactError):
        read_verified_artifact(root, 'run-001', trusted)


def test_traversal_and_symlink_escape_rejected(tmp_path):
    root, trusted = written(tmp_path)
    with pytest.raises(ArtifactError):
        read_verified_artifact(root, '../outside', trusted)
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'model.txt').write_bytes(MODEL)
    (root / 'run-001' / 'model.txt').unlink()
    try:
        (root / 'run-001' / 'model.txt').symlink_to(outside / 'model.txt')
    except (OSError, NotImplementedError):
        pytest.skip('symlink creation unavailable')
    with pytest.raises(ArtifactError):
        read_verified_artifact(root, 'run-001', trusted)


@pytest.mark.parametrize('changes', [
    {'threshold': float('nan')}, {'seed': True},
    {'source_sha256': 'bad'}, {'currency_vocabulary': ('USD', 'USD')},
    {'validation_metrics': {'f1': float('inf')}},
])
def test_writer_rejects_bad_metadata(tmp_path, changes):
    root = tmp_path / 'trusted'
    root.mkdir()
    with pytest.raises(ArtifactError):
        write_artifact(root, 'run-001', MODEL, metadata(**changes))
    assert not (root / 'run-001').exists()


def test_writer_rejects_overwrite_and_empty_model(tmp_path):
    root, _ = written(tmp_path)
    with pytest.raises(ArtifactError):
        write_artifact(root, 'run-001', MODEL, metadata())
    with pytest.raises(ArtifactError):
        write_artifact(root, 'run-002', b'', metadata())
