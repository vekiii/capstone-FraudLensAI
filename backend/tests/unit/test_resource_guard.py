"""Controlled process checks; one small synthetic fit, no project data."""

import json
import sys
from textwrap import dedent

import numpy as np
import pytest

from fraudlens.training import candidates
from fraudlens.training.resource_guard import ResourceLimitError, supervise_command

LIMITS = {
    'initial_free_disk_bytes_min': 10,
    'ending_free_disk_bytes_min': 5,
    'peak_working_set_bytes_max': 1_000_000_000,
    'fit_seconds_max_each': 2,
    'fit_seconds_max_current_phase': 3,
    'fit_seconds_max_all': 4,
}


def _incomplete(tmp_path):
    return tmp_path / 'out.incomplete'


def test_fit_start_markers_follow_all_eight_declared_candidates(monkeypatch):
    started = []
    fitted = []

    def fake_fit(candidate, *_args):
        fitted.append(candidate)
        return candidate

    monkeypatch.setattr(candidates, '_fit_lightgbm', fake_fit)
    models = candidates.fit_lightgbm_matrix_grid(
        np.zeros((4, 2)), np.array([1, 0, 0, 0]),
        np.zeros((3, 2)), np.array([1, 0, 0]), n_jobs=1,
        on_candidate_start=started.append,
    )
    assert started == list(range(8))
    assert fitted == list(candidates.LIGHTGBM_GRID)
    assert models == candidates.LIGHTGBM_GRID


def test_insufficient_initial_disk_refuses_to_start(tmp_path, monkeypatch):
    monkeypatch.setattr('fraudlens.training.resource_guard.free_disk_bytes', lambda _: 9)
    with pytest.raises(ResourceLimitError, match='initial free disk'):
        supervise_command([sys.executable, '-c', 'pass'], tmp_path / 'out', LIMITS)
    assert json.loads((_incomplete(tmp_path) / 'status.json').read_text())['state'] == 'incomplete'
    assert not (tmp_path / 'out').exists()


def test_active_job_stops_on_memory_limit(tmp_path, monkeypatch):
    monkeypatch.setattr('fraudlens.training.resource_guard.process_tree_rss_bytes',
                        lambda _: 1_000_000_001)
    with pytest.raises(ResourceLimitError, match='memory'):
        supervise_command([sys.executable, '-c', 'import time; time.sleep(5)'],
                          tmp_path / 'out', LIMITS, poll_seconds=0.02)
    assert json.loads((_incomplete(tmp_path) / 'status.json').read_text())['state'] == 'incomplete'
    assert not (tmp_path / 'out').exists()


def test_active_fit_times_out(tmp_path):
    limits = {**LIMITS, 'fit_seconds_max_each': 0.1}
    command = [sys.executable, '-c',
               "import json,time,sys; open(sys.argv[1], 'w').write(json.dumps({'candidate_index': 0, 'started_monotonic': time.monotonic()})); time.sleep(5)",
               '{output}/fit-progress.json']
    with pytest.raises(ResourceLimitError, match='individual fit'):
        supervise_command(command, tmp_path / 'out', limits, poll_seconds=0.02)
    assert json.loads((_incomplete(tmp_path) / 'status.json').read_text())['state'] == 'incomplete'
    assert not (tmp_path / 'out').exists()


def test_current_phase_times_out_without_fit_marker(tmp_path):
    limits = {**LIMITS, 'fit_seconds_max_current_phase': 0.1}
    with pytest.raises(ResourceLimitError, match='current phase time'):
        supervise_command([sys.executable, '-c', 'import time; time.sleep(5)'],
                          tmp_path / 'out', limits, poll_seconds=0.02)


def test_all_fits_time_limit_is_enforced(tmp_path):
    limits = {**LIMITS, 'fit_seconds_max_all': 0.1}
    with pytest.raises(ResourceLimitError, match='all fits time'):
        supervise_command([sys.executable, '-c', 'import time; time.sleep(5)'],
                          tmp_path / 'out', limits, poll_seconds=0.02)


def test_running_disk_loss_stops_job(tmp_path, monkeypatch):
    values = iter([10, 4])
    monkeypatch.setattr('fraudlens.training.resource_guard.free_disk_bytes',
                        lambda _: next(values))
    with pytest.raises(ResourceLimitError, match='free disk'):
        supervise_command([sys.executable, '-c', 'import time; time.sleep(5)'],
                          tmp_path / 'out', LIMITS, poll_seconds=0.02)


def test_completed_job_is_marked_success(tmp_path):
    command = [sys.executable, '-c',
               "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('{}')",
               '{output}/experiment.json']
    result = supervise_command(command, tmp_path / 'out', LIMITS, poll_seconds=0.02)
    assert result['state'] == 'complete'
    assert json.loads((tmp_path / 'out' / 'status.json').read_text())['state'] == 'complete'


def test_preflight_report_is_published_without_experiment_report(tmp_path):
    command = [sys.executable, '-c',
               "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('{}')",
               '{output}/preflight.json']
    result = supervise_command(command, tmp_path / 'out', LIMITS,
                               poll_seconds=0.02, report_name='preflight.json')
    assert result['state'] == 'complete'
    assert (tmp_path / 'out' / 'preflight.json').is_file()
    assert not (tmp_path / 'out' / 'experiment.json').exists()


def test_worker_failure_cannot_mark_partial_output_complete(tmp_path):
    command = [sys.executable, '-c',
               "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('partial'); pathlib.Path(sys.argv[2]).write_text('partial'); sys.exit(7)",
               '{output}/test-predictions-sealed.csv',
               '{output}/experiment.json']
    with pytest.raises(ResourceLimitError, match='worker exited with code 7'):
        supervise_command(command, tmp_path / 'out', LIMITS, poll_seconds=0.02)
    assert json.loads((_incomplete(tmp_path) / 'status.json').read_text())['state'] == 'incomplete'
    assert not (tmp_path / 'out' / 'experiment.json').exists()
    assert not (tmp_path / 'out' / 'test-predictions-sealed.csv').exists()
    assert not (tmp_path / 'out').exists()


def test_small_synthetic_lightgbm_fit_and_artifact_roundtrip_under_supervisor(tmp_path):
    # Input is generated in the child; it opens no project data or label files.
    script = dedent('''
        import json
        import sys
        from pathlib import Path

        import numpy as np

        from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
        from fraudlens.scoring.artifacts import (
            ArtifactMetadata, TrustedArtifact, read_verified_artifact, write_artifact,
        )
        from fraudlens.training.candidates import LIGHTGBM_GRID, _fit_lightgbm

        output = Path(sys.argv[1])
        train = np.zeros((120, 13), dtype=np.float64)
        train[:, 0] = np.arange(120)
        labels = (np.arange(120) % 2).astype(np.int8)
        validation = np.zeros((40, 13), dtype=np.float64)
        validation[:, 0] = np.arange(40)
        validation_labels = (np.arange(40) % 2).astype(np.int8)
        model = _fit_lightgbm(
            LIGHTGBM_GRID[0], train, labels, validation, validation_labels, 1.0, 1,
        )
        root = output / 'artifacts'
        root.mkdir()
        digest = write_artifact(root, 'synthetic', model.booster_.model_to_string().encode(),
            ArtifactMetadata(
                feature_version=FEATURE_VERSION, feature_order=FEATURE_ORDER,
                currency_vocabulary=('USD', '__UNKNOWN__'),
                format_vocabulary=('ACH', '__UNKNOWN__'),
                source_sha256='a' * 64, protocol_sha256='b' * 64,
                code_revision='abc1234', seed=42, threshold=0.5,
                threshold_method='validation-positive-f1-v1',
                validation_metrics={'f1': 0.5, 'average_precision': 0.5},
            ))
        native, _ = read_verified_artifact(root, 'synthetic', TrustedArtifact(
            manifest_sha256=digest, source_sha256='a' * 64,
            protocol_sha256='b' * 64, feature_version=FEATURE_VERSION,
            feature_order=FEATURE_ORDER,
        ))
        assert native.startswith(b'tree')
        (output / 'experiment.json').write_text(json.dumps({'artifact_manifest_sha256': digest}))
    ''')
    output = tmp_path / 'out'
    limits = {**LIMITS, 'fit_seconds_max_each': 30,
              'fit_seconds_max_current_phase': 30, 'fit_seconds_max_all': 30}
    result = supervise_command([sys.executable, '-c', script, '{output}'],
                               output, limits, poll_seconds=0.02)
    assert result['state'] == 'complete'
    assert (output / 'artifacts' / 'synthetic' / 'model.txt').is_file()
