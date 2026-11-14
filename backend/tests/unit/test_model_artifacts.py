"""T037: rejected pickle inputs must never reach deserialization."""

import hashlib
import importlib
import json

import pytest


def api():
    module = importlib.import_module('fraudlens.model_scoring')
    assert callable(getattr(module, 'create_manifest', None))
    assert callable(getattr(module, 'load_trusted_artifact', None))
    return module


@pytest.fixture
def local_artifact(tmp_path):
    root = tmp_path / 'approved'
    artifact = root / 'run'
    artifact.mkdir(parents=True)
    model = artifact / 'model.joblib'
    model.write_bytes(b'local test model')
    protocol = tmp_path / 'protocol.json'
    protocol.write_text(json.dumps({'feature_version': 'history-v1'}))
    protocol_sha = hashlib.sha256(protocol.read_bytes()).hexdigest()
    metadata = {
        'status': 'frozen_development_only', 'protocol_sha256': protocol_sha,
        'dataset_version': 'dv_' + 'a' * 64, 'feature_version': 'history-v1',
        'ordered_features': ['current_paid_amount'],
        'numeric_features': ['current_paid_amount'], 'categorical_features': [],
        'dependencies': {'numpy': '2.5.4', 'scikit_learn': '1.9.1', 'joblib': '1.6.0'},
        'winner_index': 0, 'model_validation_threshold': {'threshold': 'no_alert'},
        'calibration': 'none', 'model_file': 'model.joblib',
        'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
    }
    (artifact / 'metadata.json').write_text(json.dumps(metadata))
    return root, artifact, protocol, metadata


def test_manifest_and_load_checks_before_deserialization(local_artifact, monkeypatch):
    module = api()
    root, artifact, protocol, metadata = local_artifact
    manifest_sha = module.create_manifest(artifact, protocol, trusted_root=root)
    calls = []
    monkeypatch.setattr(module.joblib, 'load', lambda path: calls.append(path) or 'loaded')
    kwargs = dict(trusted_root=root, expected_manifest_sha256=manifest_sha,
                  expected_dataset_version=metadata['dataset_version'],
                  expected_protocol_sha256=metadata['protocol_sha256'])
    assert module.load_trusted_artifact(artifact, **kwargs).pipeline == 'loaded'
    assert len(calls) == 1
    calls.clear()
    for bad in (
        {'expected_manifest_sha256': '0' * 64},
        {'expected_dataset_version': 'dv_' + 'b' * 64},
        {'expected_protocol_sha256': '1' * 64},
        {'expected_scorer_version': 'wrong'},
        {'expected_feature_version': 'wrong'},
    ):
        with pytest.raises((ValueError, FileNotFoundError)):
            module.load_trusted_artifact(artifact, **(kwargs | bad))
        assert not calls
    metadata_file = artifact / 'metadata.json'
    metadata_bytes = metadata_file.read_bytes()
    metadata_file.write_bytes(metadata_bytes + b'\n')
    with pytest.raises(ValueError, match='metadata hash'):
        module.load_trusted_artifact(artifact, **kwargs)
    assert not calls
    metadata_file.write_bytes(metadata_bytes)
    (artifact / 'model.joblib').write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='hash'):
        module.load_trusted_artifact(artifact, **kwargs)
    assert not calls
    (artifact / 'model.joblib').unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        module.load_trusted_artifact(artifact, **kwargs)
    assert not calls


def test_escaped_path_upload_and_incompatible_manifest_reject(local_artifact, monkeypatch):
    module = api()
    root, artifact, protocol, metadata = local_artifact
    digest = module.create_manifest(artifact, protocol, trusted_root=root)
    calls = []
    monkeypatch.setattr(module.joblib, 'load', lambda path: calls.append(path))
    kwargs = dict(trusted_root=root, expected_manifest_sha256=digest,
                  expected_dataset_version=metadata['dataset_version'],
                  expected_protocol_sha256=metadata['protocol_sha256'])
    outside = root.parent / 'outside'
    outside.mkdir()
    (root / 'escape').symlink_to(outside, target_is_directory=True)
    for path in (outside, root / 'escape', root / '..' / 'outside'):
        with pytest.raises((ValueError, FileNotFoundError)):
            module.load_trusted_artifact(path, **kwargs)
    model = artifact / 'model.joblib'
    model_bytes = model.read_bytes()
    model.unlink()
    outside_model = outside / 'model.joblib'
    outside_model.write_bytes(model_bytes)
    model.symlink_to(outside_model)
    with pytest.raises(ValueError, match='outside trusted local root'):
        module.load_trusted_artifact(artifact, **kwargs)
    model.unlink()
    model.write_bytes(model_bytes)
    with pytest.raises(ValueError):
        module.load_trusted_artifact(artifact, upload=b'pickle', **kwargs)
    manifest = artifact / 'manifest.json'
    content = json.loads(manifest.read_text())
    for change in ({'origin': 'uploaded'}, {'model_file': '../outside/model.joblib'},
                   {'transform_version': 'unknown'}, {'dependencies': {'joblib': '0'}}):
        manifest.write_text(json.dumps(content | change))
        modified_sha = hashlib.sha256(manifest.read_bytes()).hexdigest()
        with pytest.raises(ValueError):
            module.load_trusted_artifact(
                artifact, **(kwargs | {'expected_manifest_sha256': modified_sha}))
    assert not calls
