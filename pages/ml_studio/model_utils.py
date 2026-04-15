# -*- coding: utf-8 -*-
"""Reusable ML workflow helpers for ML Studio."""

from __future__ import annotations

import json
import math
import shutil
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .config import (
    ALGORITHM_LABELS,
    ARTIFACT_ROOT,
    ARTIFACT_VERSION,
    DEFAULT_PRIMARY_METRIC,
    PROJECT_INDEX_FILE,
)

_SKLEARN_IMPORT_ERROR: ImportError | None = None

try:
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import (
        GradientBoostingClassifier,
        GradientBoostingRegressor,
        RandomForestClassifier,
        RandomForestRegressor,
    )
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
        f1_score,
        mean_absolute_error,
        mean_squared_error,
        precision_score,
        r2_score,
        recall_score,
    )
    from sklearn.model_selection import (
        KFold,
        RandomizedSearchCV,
        StratifiedKFold,
        cross_validate,
        train_test_split,
    )
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler
    from sklearn.svm import SVC, SVR
    from sklearn.tree import DecisionTreeClassifier
except ImportError as exc:
    _SKLEARN_IMPORT_ERROR = exc


def _require_sklearn() -> None:
    if _SKLEARN_IMPORT_ERROR is not None:
        raise RuntimeError(
            "ML Studio requires a working scikit-learn installation. "
            "Reinstall project dependencies to restore model training."
        ) from _SKLEARN_IMPORT_ERROR


_MODEL_CACHE: dict[str, Any] = {
    "latest_run_id": None,
    "latest_model": None,
    "published_run_id": None,
    "published_model": None,
    "published_metadata": None,
    "runs": {},
}


@dataclass
class PreparedDataset:
    feature_frame: pd.DataFrame
    target: pd.Series
    numeric_features: list[str]
    categorical_features: list[str]
    dataset_snapshot: dict[str, Any]


def get_cached_model_context() -> dict[str, Any]:
    return _MODEL_CACHE


def update_cached_model_context(model: Any, metadata: dict[str, Any], run_id: str, *, published: bool = False) -> None:
    _MODEL_CACHE["latest_run_id"] = run_id
    _MODEL_CACHE["latest_model"] = model
    _MODEL_CACHE["runs"][run_id] = {"model": model, "metadata": metadata}
    if published:
        _MODEL_CACHE["published_run_id"] = run_id
        _MODEL_CACHE["published_model"] = model
        _MODEL_CACHE["published_metadata"] = metadata


def get_cached_run_model(run_id: str) -> Any | None:
    entry = _MODEL_CACHE["runs"].get(run_id)
    return entry["model"] if entry else None


def get_published_model_context() -> tuple[Any | None, dict[str, Any] | None]:
    return _MODEL_CACHE.get("published_model"), _MODEL_CACHE.get("published_metadata")


def publish_cached_run(run_id: str) -> bool:
    entry = _MODEL_CACHE["runs"].get(run_id)
    if not entry:
        return False
    _MODEL_CACHE["published_run_id"] = run_id
    _MODEL_CACHE["published_model"] = entry["model"]
    _MODEL_CACHE["published_metadata"] = entry["metadata"]
    return True


def calculate_clf_metrics(y_true, y_pred) -> dict[str, float | str]:
    avg = "weighted"
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred, average=avg, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, average=avg, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average=avg, zero_division=0)),
        "avg_type": avg,
    }


def calculate_reg_metrics(y_true, y_pred) -> dict[str, float]:
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)
    y_true_safe = np.where(np.abs(y_true_arr) < 1e-10, 1e-10, y_true_arr)
    return {
        "r2": float(r2_score(y_true_arr, y_pred_arr)),
        "rmse": float(np.sqrt(mean_squared_error(y_true_arr, y_pred_arr))),
        "mae": float(mean_absolute_error(y_true_arr, y_pred_arr)),
        "mape": float(np.mean(np.abs((y_true_arr - y_pred_arr) / y_true_safe)) * 100),
    }


def metric_to_sklearn_scoring(task: str, metric_name: str) -> str:
    mapping = {
        ("classification", "f1_weighted"): "f1_weighted",
        ("classification", "accuracy"): "accuracy",
        ("classification", "precision_weighted"): "precision_weighted",
        ("classification", "recall_weighted"): "recall_weighted",
        ("regression", "rmse"): "neg_root_mean_squared_error",
        ("regression", "mae"): "neg_mean_absolute_error",
        ("regression", "r2"): "r2",
        ("regression", "mape"): "neg_mean_absolute_percentage_error",
    }
    return mapping[(task, metric_name)]


def normalize_sklearn_score(task: str, metric_name: str, score: float) -> float:
    if task == "regression" and metric_name in {"rmse", "mae", "mape"}:
        return float(abs(score))
    return float(score)


def compute_primary_score(task: str, metric_name: str, metrics: dict[str, Any]) -> float:
    key_map = {
        ("classification", "f1_weighted"): "f1",
        ("classification", "accuracy"): "accuracy",
        ("classification", "precision_weighted"): "precision",
        ("classification", "recall_weighted"): "recall",
        ("regression", "rmse"): "rmse",
        ("regression", "mae"): "mae",
        ("regression", "r2"): "r2",
        ("regression", "mape"): "mape",
    }
    return float(metrics[key_map[(task, metric_name)]])


def prepare_supervised_dataset(df: pd.DataFrame, features: list[str], target: str, impute_strategy: str) -> PreparedDataset:
    data = df[features + [target]].copy()
    if impute_strategy == "drop":
        data = data.dropna(subset=features + [target])
    else:
        data = data.dropna(subset=[target])
    if data.empty:
        raise ValueError("No training rows remain after applying the selected missing-value strategy.")
    feature_frame = data[features].copy()
    target_series = data[target].copy()
    numeric_features = feature_frame.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = [col for col in features if col not in numeric_features]
    return PreparedDataset(
        feature_frame=feature_frame,
        target=target_series,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        dataset_snapshot={
            "rows": int(len(data)),
            "columns": int(len(features) + 1),
            "missing_by_feature": feature_frame.isna().sum().to_dict(),
            "target_missing": int(df[target].isna().sum()),
        },
    )


def build_preprocessing_pipeline(numeric_features: list[str], categorical_features: list[str], impute_strategy: str, scaler_type: str) -> ColumnTransformer:
    _require_sklearn()
    numeric_steps: list[tuple[str, Any]] = []
    if numeric_features:
        numeric_imputer = impute_strategy if impute_strategy in {"mean", "median", "most_frequent"} else "mean"
        numeric_steps.append(("imputer", SimpleImputer(strategy=numeric_imputer)))
        if scaler_type == "standard":
            numeric_steps.append(("scaler", StandardScaler()))
        elif scaler_type == "minmax":
            numeric_steps.append(("scaler", MinMaxScaler()))
    categorical_steps: list[tuple[str, Any]] = []
    if categorical_features:
        categorical_steps.append(("imputer", SimpleImputer(strategy="most_frequent")))
        categorical_steps.append(("encoder", OneHotEncoder(handle_unknown="ignore")))
    transformers = []
    if numeric_features:
        transformers.append(("num", Pipeline(steps=numeric_steps), numeric_features))
    if categorical_features:
        transformers.append(("cat", Pipeline(steps=categorical_steps), categorical_features))
    if not transformers:
        raise ValueError("At least one feature column is required.")
    return ColumnTransformer(transformers=transformers, remainder="drop")


def build_estimator(task: str, algo: str, params: dict[str, Any]) -> Any:
    _require_sklearn()
    params = params or {}
    if task == "classification":
        if algo == "rf_clf":
            return RandomForestClassifier(n_estimators=int(params.get("n_estimators", 100)), max_depth=_nullable_int(params.get("max_depth")), min_samples_split=int(params.get("min_samples_split", 2)), random_state=42, n_jobs=-1)
        if algo == "gbm_clf":
            return GradientBoostingClassifier(n_estimators=int(params.get("n_estimators", 100)), learning_rate=float(params.get("learning_rate", 0.1)), max_depth=int(params.get("max_depth", 3)), random_state=42)
        if algo == "svm_clf":
            return SVC(C=float(params.get("C", 1.0)), kernel=params.get("kernel", "rbf"), gamma=params.get("gamma", "scale"), probability=True, random_state=42)
        if algo == "lr_clf":
            return LogisticRegression(C=float(params.get("C", 1.0)), max_iter=int(params.get("max_iter", 1000)), solver=params.get("solver", "lbfgs"), random_state=42)
        if algo == "knn_clf":
            return KNeighborsClassifier(n_neighbors=int(params.get("n_neighbors", params.get("k", 5))), weights=params.get("weights", "uniform"))
        if algo == "dt_clf":
            return DecisionTreeClassifier(max_depth=_nullable_int(params.get("max_depth")), min_samples_split=int(params.get("min_samples_split", 2)), random_state=42)
    if task == "regression":
        if algo == "rf_reg":
            return RandomForestRegressor(n_estimators=int(params.get("n_estimators", 100)), max_depth=_nullable_int(params.get("max_depth")), min_samples_split=int(params.get("min_samples_split", 2)), random_state=42, n_jobs=-1)
        if algo == "gbm_reg":
            return GradientBoostingRegressor(n_estimators=int(params.get("n_estimators", 100)), learning_rate=float(params.get("learning_rate", 0.1)), max_depth=int(params.get("max_depth", 3)), random_state=42)
        if algo == "lr_reg":
            return LinearRegression()
        if algo == "ridge_reg":
            return Ridge(alpha=float(params.get("alpha", 1.0)), random_state=42)
        if algo == "svr_reg":
            return SVR(C=float(params.get("C", 1.0)), kernel=params.get("kernel", "rbf"), gamma=params.get("gamma", "scale"))
    raise ValueError(f"Unsupported task/algo combination: {task}/{algo}")


def build_training_pipeline(task: str, algo: str, params: dict[str, Any], numeric_features: list[str], categorical_features: list[str], impute_strategy: str, scaler_type: str) -> Pipeline:
    return Pipeline([("preprocessor", build_preprocessing_pipeline(numeric_features, categorical_features, impute_strategy, scaler_type)), ("model", build_estimator(task, algo, params))])


def get_search_space(task: str, algo: str) -> dict[str, list[Any]]:
    spaces = {
        ("classification", "rf_clf"): {"model__n_estimators": [100, 200, 300], "model__max_depth": [None, 5, 10, 20], "model__min_samples_split": [2, 5, 10]},
        ("classification", "gbm_clf"): {"model__n_estimators": [100, 150, 200], "model__learning_rate": [0.03, 0.05, 0.1], "model__max_depth": [2, 3, 4]},
        ("classification", "svm_clf"): {"model__C": [0.1, 1.0, 10.0], "model__kernel": ["rbf", "linear"], "model__gamma": ["scale", "auto"]},
        ("classification", "lr_clf"): {"model__C": [0.1, 1.0, 10.0], "model__solver": ["lbfgs", "liblinear"], "model__max_iter": [500, 1000]},
        ("classification", "knn_clf"): {"model__n_neighbors": [3, 5, 7, 9], "model__weights": ["uniform", "distance"]},
        ("classification", "dt_clf"): {"model__max_depth": [None, 5, 10, 20], "model__min_samples_split": [2, 5, 10]},
        ("regression", "rf_reg"): {"model__n_estimators": [100, 200, 300], "model__max_depth": [None, 5, 10, 20], "model__min_samples_split": [2, 5, 10]},
        ("regression", "gbm_reg"): {"model__n_estimators": [100, 150, 200], "model__learning_rate": [0.03, 0.05, 0.1], "model__max_depth": [2, 3, 4]},
        ("regression", "ridge_reg"): {"model__alpha": [0.1, 1.0, 10.0, 100.0]},
        ("regression", "svr_reg"): {"model__C": [0.1, 1.0, 10.0], "model__kernel": ["rbf", "linear"], "model__gamma": ["scale", "auto"]},
        ("regression", "lr_reg"): {},
    }
    return spaces.get((task, algo), {})


def get_cv_strategy(task: str, cv_strategy: str, folds: int):
    _require_sklearn()
    folds = max(2, int(folds or 5))
    if cv_strategy == "stratified_kfold" and task == "classification":
        return StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    return KFold(n_splits=folds, shuffle=True, random_state=42)

def run_single_training(df: pd.DataFrame, features: list[str], target: str, task: str, algo: str, params: dict[str, Any], impute_strategy: str, scaler_type: str, test_size: float, primary_metric: str | None = None) -> tuple[dict[str, Any], Pipeline]:
    primary_metric = primary_metric or DEFAULT_PRIMARY_METRIC[task]
    prepared = prepare_supervised_dataset(df, features, target, impute_strategy)
    X = prepared.feature_frame
    y = _prepare_target(prepared.target, task)
    stratify = y if task == "classification" and y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=float(test_size), random_state=42, stratify=stratify)
    pipeline = build_training_pipeline(task, algo, params, prepared.numeric_features, prepared.categorical_features, impute_strategy, scaler_type)
    started_at = time.perf_counter()
    pipeline.fit(X_train, y_train)
    fit_time = time.perf_counter() - started_at
    y_pred = pipeline.predict(X_test)
    metrics, report_payload = evaluate_predictions(task, y_test, y_pred)
    primary_score = compute_primary_score(task, primary_metric, metrics)
    importances = extract_feature_importance(pipeline, prepared.numeric_features, prepared.categorical_features)
    run = base_run_payload(task=task, algo=algo, mode="quick", cv_strategy="holdout", primary_metric=primary_metric, prepared=prepared, target=target, features=features, fit_time=fit_time, best_score=primary_score, best_params=params, impute_strategy=impute_strategy, scaler_type=scaler_type)
    run["holdout_metrics"] = metrics
    run["metrics"] = {"holdout": metrics}
    run["report"] = report_payload
    run["importances"] = importances
    run["y_test"] = y_test.tolist()
    run["y_pred"] = np.asarray(y_pred).tolist()
    run["classes"] = sorted(pd.Series(y).astype(str).unique().tolist()) if task == "classification" else []
    return run, pipeline


def run_cross_validation(df: pd.DataFrame, features: list[str], target: str, task: str, algo: str, params: dict[str, Any], impute_strategy: str, scaler_type: str, cv_strategy: str, folds: int, primary_metric: str | None = None) -> tuple[dict[str, Any], Pipeline]:
    primary_metric = primary_metric or DEFAULT_PRIMARY_METRIC[task]
    prepared = prepare_supervised_dataset(df, features, target, impute_strategy)
    X = prepared.feature_frame
    y = _prepare_target(prepared.target, task)
    pipeline = build_training_pipeline(task, algo, params, prepared.numeric_features, prepared.categorical_features, impute_strategy, scaler_type)
    scoring = metric_to_sklearn_scoring(task, primary_metric)
    cv_obj = get_cv_strategy(task, cv_strategy, folds)
    started_at = time.perf_counter()
    cv_result = cross_validate(pipeline, X, y, cv=cv_obj, scoring=scoring, n_jobs=1, return_train_score=False)
    fit_time = time.perf_counter() - started_at
    scores = [normalize_sklearn_score(task, primary_metric, score) for score in cv_result["test_score"]]
    pipeline.fit(X, y)
    importances = extract_feature_importance(pipeline, prepared.numeric_features, prepared.categorical_features)
    mean_score = float(np.mean(scores))
    std_score = float(np.std(scores))
    run = base_run_payload(task=task, algo=algo, mode="cv", cv_strategy=cv_strategy, primary_metric=primary_metric, prepared=prepared, target=target, features=features, fit_time=fit_time, best_score=mean_score, best_params=params, impute_strategy=impute_strategy, scaler_type=scaler_type)
    run["cv_scores"] = scores
    run["cv_summary"] = {"mean": mean_score, "std": std_score}
    run["metrics"] = {"cv": {"mean": mean_score, "std": std_score}}
    run["holdout_metrics"] = {}
    run["report"] = {"cv_scores": scores}
    run["importances"] = importances
    return run, pipeline


def run_model_search(df: pd.DataFrame, features: list[str], target: str, task: str, algo: str, params: dict[str, Any], impute_strategy: str, scaler_type: str, cv_strategy: str, folds: int, primary_metric: str, search_iterations: int) -> tuple[dict[str, Any], Pipeline]:
    prepared = prepare_supervised_dataset(df, features, target, impute_strategy)
    X = prepared.feature_frame
    y = _prepare_target(prepared.target, task)
    pipeline = build_training_pipeline(task, algo, params, prepared.numeric_features, prepared.categorical_features, impute_strategy, scaler_type)
    search_space = get_search_space(task, algo)
    if algo == "knn_clf" and "model__n_neighbors" in search_space:
        fold_count = max(2, int(folds or 5))
        max_valid_neighbors = max(1, len(X) - math.ceil(len(X) / fold_count))
        valid_neighbors = [value for value in search_space["model__n_neighbors"] if int(value) <= max_valid_neighbors]
        search_space["model__n_neighbors"] = valid_neighbors or [min(5, max_valid_neighbors)]
    if not search_space:
        return run_cross_validation(df, features, target, task, algo, params, impute_strategy, scaler_type, cv_strategy, folds, primary_metric)
    scoring = metric_to_sklearn_scoring(task, primary_metric)
    cv_obj = get_cv_strategy(task, cv_strategy, folds)
    started_at = time.perf_counter()
    search = RandomizedSearchCV(estimator=pipeline, param_distributions=search_space, n_iter=max(1, int(search_iterations or 10)), scoring=scoring, cv=cv_obj, random_state=42, n_jobs=1, refit=True)
    search.fit(X, y)
    fit_time = time.perf_counter() - started_at
    best_pipeline = search.best_estimator_
    best_params = {key.replace("model__", ""): _json_safe_value(value) for key, value in search.best_params_.items()}
    best_score = normalize_sklearn_score(task, primary_metric, float(search.best_score_))
    importances = extract_feature_importance(best_pipeline, prepared.numeric_features, prepared.categorical_features)
    search_results = pd.DataFrame(search.cv_results_)
    top_runs = []
    for _, row in search_results.sort_values("rank_test_score").head(5).iterrows():
        top_runs.append({
            "rank": int(row["rank_test_score"]),
            "score": normalize_sklearn_score(task, primary_metric, float(row["mean_test_score"])),
            "std": float(row["std_test_score"]),
            "params": {key.replace("param_model__", ""): _json_safe_value(row[key]) for key in search_results.columns if key.startswith("param_model__") and pd.notna(row[key])},
        })
    run = base_run_payload(task=task, algo=algo, mode="random_search", cv_strategy=cv_strategy, primary_metric=primary_metric, prepared=prepared, target=target, features=features, fit_time=fit_time, best_score=best_score, best_params=best_params, impute_strategy=impute_strategy, scaler_type=scaler_type)
    run["cv_summary"] = {"mean": best_score, "std": float(search.cv_results_["std_test_score"][search.best_index_])}
    run["cv_scores"] = []
    run["metrics"] = {"search": {"mean": best_score, "std": run["cv_summary"]["std"]}}
    run["holdout_metrics"] = {}
    run["report"] = {"top_candidates": top_runs}
    run["search_summary"] = top_runs
    run["importances"] = importances
    return run, best_pipeline


def evaluate_predictions(task: str, y_true, y_pred) -> tuple[dict[str, Any], dict[str, Any]]:
    _require_sklearn()
    if task == "classification":
        return calculate_clf_metrics(y_true, y_pred), {"classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0), "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()}
    metrics = calculate_reg_metrics(y_true, y_pred)
    residuals = (np.asarray(y_true) - np.asarray(y_pred)).tolist()
    return metrics, {"residuals": residuals}


def extract_feature_importance(pipeline: Pipeline, numeric_features: list[str], categorical_features: list[str]) -> list[dict[str, Any]]:
    preprocessor: ColumnTransformer = pipeline.named_steps["preprocessor"]
    try:
        feature_names = preprocessor.get_feature_names_out().tolist()
    except Exception:
        feature_names = numeric_features + categorical_features
    model = pipeline.named_steps["model"]
    importances = None
    if hasattr(model, "feature_importances_"):
        importances = np.asarray(model.feature_importances_)
    elif hasattr(model, "coef_"):
        coef = np.asarray(model.coef_)
        importances = np.abs(coef[0] if coef.ndim > 1 else coef)
    if importances is None or len(feature_names) != len(importances):
        return []
    values = [{"feature": feature, "importance": float(value)} for feature, value in zip(feature_names, importances)]
    return sorted(values, key=lambda item: item["importance"], reverse=True)

def serialize_artifact(run: dict[str, Any], model: Pipeline) -> dict[str, Any]:
    artifact_dir = ARTIFACT_ROOT / run["run_id"]
    artifact_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "artifact_version": ARTIFACT_VERSION,
        "saved_at": pd.Timestamp.utcnow().isoformat(),
        "run_id": run["run_id"],
        "task": run["task"],
        "algorithm": run["algorithm"],
        "algorithm_label": run["algorithm_label"],
        "training_mode": run["training_mode"],
        "cv_strategy": run["cv_strategy"],
        "primary_metric": run["primary_metric"],
        "best_score": run["best_score"],
        "best_params": run.get("best_params", {}),
        "feature_columns": run["feature_schema"]["all"],
        "target_column": run["target_column"],
        "feature_schema": run["feature_schema"],
        "preprocessing_config": run["preprocessing_config"],
        "estimator_config": {"task": run["task"], "algorithm": run["algorithm"], "algorithm_label": run["algorithm_label"]},
        "metrics": run["metrics"],
        "dataset_snapshot": run["dataset_snapshot"],
    }
    joblib.dump(model, artifact_dir / "model.joblib")
    (artifact_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (artifact_dir / "report.json").write_text(json.dumps(run.get("report", {}), ensure_ascii=False, indent=2), encoding="utf-8")
    run["artifact_path"] = str(artifact_dir)
    sync_run_to_project_index(run)
    return metadata


def load_artifact(artifact_path: str | Path) -> tuple[Pipeline, dict[str, Any], dict[str, Any]]:
    artifact_dir = Path(artifact_path)
    model = joblib.load(artifact_dir / "model.joblib")
    metadata = json.loads((artifact_dir / "metadata.json").read_text(encoding="utf-8"))
    report = json.loads((artifact_dir / "report.json").read_text(encoding="utf-8"))
    return model, metadata, report


def load_project_index() -> dict[str, Any]:
    if not PROJECT_INDEX_FILE.exists():
        return {"runs": [], "published_run_id": None, "updated_at": None}
    return json.loads(PROJECT_INDEX_FILE.read_text(encoding="utf-8"))


def write_project_index(index: dict[str, Any]) -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    index["updated_at"] = pd.Timestamp.utcnow().isoformat()
    PROJECT_INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_run_for_index(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run["run_id"],
        "status": run.get("status", "success"),
        "task": run["task"],
        "algorithm": run["algorithm"],
        "algorithm_label": run["algorithm_label"],
        "training_mode": run["training_mode"],
        "cv_strategy": run["cv_strategy"],
        "primary_metric": run["primary_metric"],
        "best_score": run["best_score"],
        "metrics": run.get("metrics", {}),
        "best_params": run.get("best_params", {}),
        "fit_time": run.get("fit_time", 0.0),
        "feature_schema": run.get("feature_schema", {}),
        "target_column": run.get("target_column"),
        "dataset_snapshot": run.get("dataset_snapshot", {}),
        "artifact_path": run.get("artifact_path"),
        "created_at": run.get("created_at"),
        "is_published": run.get("is_published", False),
    }


def sync_run_to_project_index(run: dict[str, Any]) -> None:
    index = load_project_index()
    runs = [item for item in index.get("runs", []) if item.get("run_id") != run["run_id"]]
    runs.insert(0, summarize_run_for_index(run))
    index["runs"] = runs
    if any(item.get("is_published") for item in runs):
        index["published_run_id"] = next(item["run_id"] for item in runs if item.get("is_published"))
    write_project_index(index)


def set_published_run_in_index(run_id: str | None) -> dict[str, Any]:
    index = load_project_index()
    for item in index.get("runs", []):
        item["is_published"] = item.get("run_id") == run_id
    index["published_run_id"] = run_id
    write_project_index(index)
    return index


def delete_run_artifact(run_id: str, artifact_path: str | None) -> dict[str, Any]:
    index = load_project_index()
    index["runs"] = [item for item in index.get("runs", []) if item.get("run_id") != run_id]
    if index.get("published_run_id") == run_id:
        index["published_run_id"] = None
    write_project_index(index)
    if artifact_path:
        path = Path(artifact_path)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
    _MODEL_CACHE["runs"].pop(run_id, None)
    if _MODEL_CACHE.get("published_run_id") == run_id:
        _MODEL_CACHE["published_run_id"] = None
        _MODEL_CACHE["published_model"] = None
        _MODEL_CACHE["published_metadata"] = None
    if _MODEL_CACHE.get("latest_run_id") == run_id:
        _MODEL_CACHE["latest_run_id"] = None
        _MODEL_CACHE["latest_model"] = None
    return index


def load_runs_from_index() -> list[dict[str, Any]]:
    return load_project_index().get("runs", [])


def convert_metadata_to_published(metadata: dict[str, Any], artifact_path: str | None = None) -> dict[str, Any]:
    return {
        "run_id": metadata.get("run_id"),
        "task": metadata.get("task"),
        "algorithm": metadata.get("algorithm"),
        "algorithm_label": metadata.get("algorithm_label", ALGORITHM_LABELS.get(metadata.get("algorithm", ""), metadata.get("algorithm", ""))),
        "training_mode": metadata.get("training_mode"),
        "cv_strategy": metadata.get("cv_strategy"),
        "primary_metric": metadata.get("primary_metric"),
        "best_score": metadata.get("best_score"),
        "best_params": metadata.get("best_params", {}),
        "feature_schema": metadata.get("feature_schema", {}),
        "feature_columns": metadata.get("feature_columns", []),
        "target_column": metadata.get("target_column"),
        "metrics": metadata.get("metrics", {}),
        "dataset_snapshot": metadata.get("dataset_snapshot", {}),
        "preprocessing_config": metadata.get("preprocessing_config", {}),
        "artifact_path": artifact_path or metadata.get("artifact_path"),
        "published_at": pd.Timestamp.utcnow().isoformat(),
    }


def base_run_payload(*, task: str, algo: str, mode: str, cv_strategy: str, primary_metric: str, prepared: PreparedDataset, target: str, features: list[str], fit_time: float, best_score: float, best_params: dict[str, Any], impute_strategy: str, scaler_type: str) -> dict[str, Any]:
    return {
        "run_id": str(uuid.uuid4()),
        "status": "success",
        "task": task,
        "algorithm": algo,
        "algorithm_label": ALGORITHM_LABELS.get(algo, algo),
        "training_mode": mode,
        "cv_strategy": cv_strategy,
        "primary_metric": primary_metric,
        "best_score": float(best_score),
        "fit_time": float(fit_time),
        "best_params": {key: _json_safe_value(value) for key, value in (best_params or {}).items()},
        "target_column": target,
        "feature_schema": {"all": features, "numeric": prepared.numeric_features, "categorical": prepared.categorical_features},
        "dataset_snapshot": prepared.dataset_snapshot,
        "preprocessing_config": make_preprocessing_config(impute_strategy, scaler_type),
        "created_at": pd.Timestamp.utcnow().isoformat(),
        "artifact_path": None,
        "report": {},
        "metrics": {},
        "holdout_metrics": {},
        "is_published": False,
    }


def make_preprocessing_config(impute_strategy: str, scaler_type: str) -> dict[str, Any]:
    return {"impute_strategy": impute_strategy, "scaler_type": scaler_type}


def _prepare_target(target: pd.Series, task: str) -> pd.Series:
    if task == "classification":
        return target.astype(str)
    return pd.to_numeric(target, errors="coerce").fillna(0.0)


def _nullable_int(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    return int(value)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value
