"""T222 synthetic package and native LightGBM artifact compatibility probe.

Run from the repository root with ``uv run --locked --group ml python
evidence/tasks/T222-compat.py``. No real dataset, labels or model artifact is read.
"""

import hashlib
import json
import sys
import tempfile
import tomllib
from importlib import metadata
from pathlib import Path

import lightgbm
import numpy as np
import scipy
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier


def main():
    project = tomllib.loads(Path('pyproject.toml').read_text(encoding='utf-8'))
    assert sys.version_info[:2] == (3, 14)
    for requirement in project['dependency-groups']['ml']:
        name, expected = requirement.split('==')
        assert metadata.version(name) == expected

    # Invented and balanced; this checks binary compatibility, not model quality.
    features = np.array([[i, i % 3] for i in range(40)], dtype=np.float64)
    labels = np.array([i % 2 for i in range(40)], dtype=np.int32)
    baseline_types = (
        DecisionTreeClassifier(max_depth=5, min_samples_leaf=2, random_state=42),
        LogisticRegression(max_iter=100, random_state=42),
        HistGradientBoostingClassifier(max_iter=5, min_samples_leaf=2,
                                       early_stopping=False, random_state=42),
    )
    for estimator in baseline_types:
        scores = estimator.fit(features, labels).predict_proba(features)[:, 1]
        assert np.isfinite(scores).all()
        assert ((0 <= scores) & (scores <= 1)).all()

    model = lightgbm.LGBMClassifier(
        objective='binary', n_estimators=12, num_leaves=3, min_child_samples=1,
        n_jobs=1, random_state=42, deterministic=True, verbosity=-1,
    )
    before = model.fit(features, labels).predict_proba(features)[:, 1]
    assert np.isfinite(before).all()

    cache = Path('.cache/t222-compat')
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as directory:
        artifact = Path(directory) / 'synthetic-lightgbm.txt'
        model.booster_.save_model(str(artifact))
        artifact_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
        reloaded = lightgbm.Booster(model_file=str(artifact))
        after = reloaded.predict(features)
        assert np.allclose(before, after, rtol=0, atol=1e-12)

    print(json.dumps({
        'python': sys.version.split()[0],
        'scikit_learn': sklearn.__version__,
        'lightgbm': lightgbm.__version__,
        'numpy': np.__version__,
        'scipy': scipy.__version__,
        'baseline_import_fit_predict': 'passed',
        'lightgbm_native_roundtrip': 'passed',
        'artifact_sha256': artifact_hash,
        'synthetic_rows': len(labels),
    }, sort_keys=True))


if __name__ == '__main__':
    main()
