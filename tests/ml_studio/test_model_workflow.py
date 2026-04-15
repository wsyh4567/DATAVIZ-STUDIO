import importlib.util
import sys
import types
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "pages" / "ml_studio"


def _load_model_utils():
    sys.modules.pop("pages.ml_studio.model_utils", None)
    sys.modules.pop("pages.ml_studio.config", None)

    pages_pkg = sys.modules.setdefault("pages", types.ModuleType("pages"))
    pages_pkg.__path__ = [str(ROOT / "pages")]

    ml_pkg = sys.modules.setdefault("pages.ml_studio", types.ModuleType("pages.ml_studio"))
    ml_pkg.__path__ = [str(PACKAGE_ROOT)]

    config_spec = importlib.util.spec_from_file_location("pages.ml_studio.config", PACKAGE_ROOT / "config.py")
    config_module = importlib.util.module_from_spec(config_spec)
    sys.modules["pages.ml_studio.config"] = config_module
    config_spec.loader.exec_module(config_module)

    model_spec = importlib.util.spec_from_file_location("pages.ml_studio.model_utils", PACKAGE_ROOT / "model_utils.py")
    model_module = importlib.util.module_from_spec(model_spec)
    sys.modules["pages.ml_studio.model_utils"] = model_module
    model_spec.loader.exec_module(model_module)
    return model_module


mu = _load_model_utils()


def _classification_df():
    return pd.DataFrame(
        {
            "num_a": [1, 2, 3, 4, 5, 6, 7, 8],
            "num_b": [8, 7, 6, 5, 4, 3, 2, 1],
            "cat": ["a", "a", "b", "b", "a", "b", "a", "b"],
            "target": ["no", "no", "no", "yes", "yes", "yes", "yes", "yes"],
        }
    )


def _regression_df():
    return pd.DataFrame(
        {
            "x1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "x2": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            "group": ["a", "a", "a", "b", "b", "b", "c", "c", "c", "c"],
            "y": [2.0, 3.5, 5.2, 7.1, 8.9, 11.2, 12.8, 15.1, 17.2, 19.0],
        }
    )


def _patch_artifact_paths(tmp_path):
    mu.ARTIFACT_ROOT = tmp_path / "ml"
    mu.PROJECT_INDEX_FILE = mu.ARTIFACT_ROOT / "project_index.json"


def test_run_single_training_classification_returns_pipeline_and_metrics(tmp_path):
    _patch_artifact_paths(tmp_path)
    run, pipeline = mu.run_single_training(
        df=_classification_df(),
        features=["num_a", "num_b", "cat"],
        target="target",
        task="classification",
        algo="rf_clf",
        params={"n_estimators": 20, "max_depth": 4},
        impute_strategy="mean",
        scaler_type="standard",
        test_size=0.25,
        primary_metric="f1_weighted",
    )

    assert pipeline is not None
    assert run["task"] == "classification"
    assert run["training_mode"] == "quick"
    assert "holdout" in run["metrics"]
    assert run["preprocessing_config"] == {"impute_strategy": "mean", "scaler_type": "standard"}


def test_run_cross_validation_regression_returns_cv_summary(tmp_path):
    _patch_artifact_paths(tmp_path)
    run, pipeline = mu.run_cross_validation(
        df=_regression_df(),
        features=["x1", "x2", "group"],
        target="y",
        task="regression",
        algo="ridge_reg",
        params={"alpha": 1.0},
        impute_strategy="mean",
        scaler_type="standard",
        cv_strategy="kfold",
        folds=3,
        primary_metric="rmse",
    )

    assert pipeline is not None
    assert run["training_mode"] == "cv"
    assert "cv_summary" in run
    assert run["cv_summary"]["mean"] >= 0


def test_run_model_search_returns_best_params(tmp_path):
    _patch_artifact_paths(tmp_path)
    run, pipeline = mu.run_model_search(
        df=_classification_df(),
        features=["num_a", "num_b", "cat"],
        target="target",
        task="classification",
        algo="knn_clf",
        params={"n_neighbors": 3},
        impute_strategy="mean",
        scaler_type="standard",
        cv_strategy="stratified_kfold",
        folds=3,
        primary_metric="f1_weighted",
        search_iterations=2,
    )

    assert pipeline is not None
    assert run["training_mode"] == "random_search"
    assert isinstance(run["best_params"], dict)
    assert run["best_params"]


def test_serialize_and_load_artifact_roundtrip(tmp_path):
    _patch_artifact_paths(tmp_path)
    run, pipeline = mu.run_single_training(
        df=_regression_df(),
        features=["x1", "x2", "group"],
        target="y",
        task="regression",
        algo="rf_reg",
        params={"n_estimators": 10, "max_depth": 3},
        impute_strategy="mean",
        scaler_type="standard",
        test_size=0.2,
        primary_metric="rmse",
    )

    metadata = mu.serialize_artifact(run, pipeline)
    loaded_model, loaded_metadata, report = mu.load_artifact(run["artifact_path"])

    assert metadata["run_id"] == run["run_id"]
    assert loaded_metadata["run_id"] == run["run_id"]
    assert isinstance(report, dict)
    assert len(loaded_model.predict(_regression_df()[["x1", "x2", "group"]].head(2))) == 2


def test_build_estimator_raises_clear_error_when_sklearn_is_unavailable(monkeypatch):
    monkeypatch.setattr(mu, "_SKLEARN_IMPORT_ERROR", ImportError("broken sklearn"))

    with pytest.raises(RuntimeError, match="scikit-learn"):
        mu.build_estimator("classification", "rf_clf", {})
