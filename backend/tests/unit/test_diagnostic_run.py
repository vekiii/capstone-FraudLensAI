"""Five-arm diagnostics on generated arrays only; no project-data fit."""

import csv
import json
from datetime import datetime, timezone

import lightgbm as lgb
import numpy as np
import pytest

from fraudlens.training import diagnostic_run
from fraudlens.training.candidates import LIGHTGBM_GRID, _fit_lightgbm
from fraudlens.training.resource_guard import ResourceLimitError, supervise_command


def test_five_arms_change_exactly_one_parameter():
    arms = diagnostic_run.arm_parameters(90, 10)
    assert [name for name, _ in arms] == [
        'control', 'unweighted', 'no_average', 'l2_one', 'delta_one',
    ]
    control = arms[0][1]
    assert control['scale_pos_weight'] == 9
    assert control['boost_from_average'] is True
    assert control['reg_lambda'] == 0
    assert control['max_delta_step'] == 0
    assert control['n_jobs'] == 4
    assert (control['num_leaves'], control['learning_rate'],
            control['min_child_samples']) == (31, 0.05, 200)
    assert [
        {key: value for key, value in params.items() if value != control[key]}
        for _, params in arms[1:]
    ] == [
        {'scale_pos_weight': 1.0}, {'boost_from_average': False},
        {'reg_lambda': 1.0}, {'max_delta_step': 1.0},
    ]


def test_tampered_five_arm_plan_is_rejected():
    expected = diagnostic_run.arm_plan()
    diagnostic_run.verify_arm_plan(expected)
    tampered = json.loads(json.dumps(expected))
    tampered[2]['overrides']['learning_rate'] = 0.1
    with pytest.raises(ValueError, match='five-arm plan'):
        diagnostic_run.verify_arm_plan(tampered)


def test_synthetic_diagnostic_writes_each_arm_and_roundtrips_model(tmp_path):
    rng = np.random.default_rng(42)
    train = rng.normal(size=(600, 3))
    train_labels = (train[:, 0] + train[:, 1] > 0).astype(np.int8)
    validation = rng.normal(size=(140, 3))
    validation_labels = (validation[:, 0] + validation[:, 1] > 0).astype(np.int8)
    ids = [f'id-{index:03d}' for index in range(len(validation))]
    times = [datetime(2022, 9, 5, tzinfo=timezone.utc)] * len(validation)

    results = diagnostic_run.run_matrix_diagnostics(
        train, train_labels, validation, validation_labels, ids, times, tmp_path,
    )

    assert len(results) == 5
    assert [row['arm'] for row in results] == [name for name, _ in
                                               diagnostic_run.arm_parameters(1, 1)]
    assert not (tmp_path / 'test-predictions-sealed.csv').exists()
    for row in results:
        arm_dir = tmp_path / 'arms' / row['arm']
        assert row['best_iteration'] >= 1
        assert row['total_rounds'] >= row['best_iteration']
        assert len(row['history']['validation']['binary_logloss']) == row['total_rounds']
        assert row['probability_metrics']['confusion_matrix']
        assert 'roc_auc' in row['probability_metrics']
        assert row['probability_metrics']['precision_at'][20] >= 0
        assert row['raw_diagnostics']['average_precision'] >= 0
        assert row['fit_elapsed_seconds'] >= 0
        assert row['worker_peak_bytes_cumulative_at_end'] >= 0
        probability = list(csv.DictReader((arm_dir / 'validation-probability.csv').open()))
        raw = list(csv.DictReader((arm_dir / 'validation-raw.csv').open()))
        assert [item['transaction_id'] for item in probability] == ids
        assert [item['transaction_id'] for item in raw] == ids
        booster = lgb.Booster(model_file=str(arm_dir / 'model.txt'))
        expected = booster.predict(validation, num_iteration=row['best_iteration'])
        assert np.array_equal(expected, np.array([float(item['score'])
                                                   for item in probability]))
    baseline = _fit_lightgbm(
        LIGHTGBM_GRID[1], train, train_labels, validation, validation_labels,
        float(np.count_nonzero(train_labels == 0) / np.count_nonzero(train_labels)), 4,
    )
    assert baseline.best_iteration_ == results[0]['best_iteration']
    control = lgb.Booster(model_file=str(tmp_path / 'arms/control/model.txt'))
    assert np.array_equal(
        baseline.predict_proba(validation, num_iteration=baseline.best_iteration_)[:, 1],
        control.predict(validation, num_iteration=results[0]['best_iteration']),
    )
    assert '[lambda_l2: 1]' in (tmp_path / 'arms/l2_one/model.txt').read_text()
    assert '[max_delta_step: 1]' in (tmp_path / 'arms/delta_one/model.txt').read_text()
    assert '[boost_from_average: 0]' in (tmp_path / 'arms/no_average/model.txt').read_text()


def test_nonfinite_validation_fails_before_any_fit(tmp_path, monkeypatch):
    def forbidden(*_args, **_kwargs):
        pytest.fail('fit must not run with invalid input')

    monkeypatch.setattr(lgb.LGBMClassifier, 'fit', forbidden)
    with pytest.raises(ValueError, match='finite aligned'):
        diagnostic_run.run_matrix_diagnostics(
            np.array([[0.0], [1.0]]), np.array([0, 1]),
            np.array([[np.nan], [1.0]]), np.array([0, 1]),
            ['a', 'b'], [datetime(2022, 9, 5, tzinfo=timezone.utc)] * 2, tmp_path,
        )


def test_diagnostic_supervision_marks_partial_worker_incomplete(tmp_path, monkeypatch):
    monkeypatch.setattr('fraudlens.training.resource_guard._require_memory_monitor',
                        lambda: None)
    monkeypatch.setattr('fraudlens.training.resource_guard.process_tree_rss_bytes',
                        lambda _: 0)
    limits = {
        'initial_free_disk_bytes_min': 10,
        'ending_free_disk_bytes_min': 5,
        'peak_working_set_bytes_max': 1_000_000_000,
        'fit_seconds_max_each': 5,
        'fit_seconds_max_current_phase': 5,
        'fit_seconds_max_all': 5,
    }
    command = [
        __import__('sys').executable, '-c',
        "import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.mkdir(parents=True); (p/'model.txt').write_text('partial'); pathlib.Path(sys.argv[2]).write_text('{}'); sys.exit(7)",
        '{output}/arms/control', '{output}/diagnostic.json',
    ]
    with pytest.raises(ResourceLimitError, match='worker exited with code 7'):
        supervise_command(command, tmp_path / 'out', limits, poll_seconds=0.02,
                          report_name='diagnostic.json')
    incomplete = tmp_path / 'out.incomplete'
    assert json.loads((incomplete / 'status.json').read_text())['state'] == 'incomplete'
    assert (incomplete / 'arms/control/model.txt').exists()
    assert not (incomplete / 'diagnostic.json').exists()
    assert not (tmp_path / 'out').exists()


def test_diagnostic_supervision_publishes_only_complete_report(tmp_path, monkeypatch):
    monkeypatch.setattr('fraudlens.training.resource_guard._require_memory_monitor',
                        lambda: None)
    monkeypatch.setattr('fraudlens.training.resource_guard.process_tree_rss_bytes',
                        lambda _: 0)
    limits = {
        'initial_free_disk_bytes_min': 10,
        'ending_free_disk_bytes_min': 5,
        'peak_working_set_bytes_max': 1_000_000_000,
        'fit_seconds_max_each': 5,
        'fit_seconds_max_current_phase': 5,
        'fit_seconds_max_all': 5,
    }
    command = [__import__('sys').executable, '-c',
               "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('{}')",
               '{output}/diagnostic.json']
    status = supervise_command(command, tmp_path / 'out', limits, poll_seconds=0.02,
                               report_name='diagnostic.json')
    assert status['state'] == 'complete'
    assert (tmp_path / 'out/diagnostic.json').exists()
    assert not (tmp_path / 'out.incomplete').exists()
