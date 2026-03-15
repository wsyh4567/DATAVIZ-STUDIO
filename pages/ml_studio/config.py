# -*- coding: utf-8 -*-
"""Configuration for ML Studio."""

from __future__ import annotations

from pathlib import Path


CARD_STYLE = {
    "backgroundColor": "var(--bg-secondary)",
    "border": "1px solid var(--border)",
    "borderRadius": "10px",
    "padding": "16px",
}

ACCENT_COLORS = {
    "blue": "#3B82F6",
    "green": "#10B981",
    "purple": "#8B5CF6",
    "orange": "#F59E0B",
    "red": "#EF4444",
    "cyan": "#06B6D4",
}

CLASSIFIER_OPTIONS = [
    {"label": "Random Forest", "value": "rf_clf"},
    {"label": "Gradient Boosting", "value": "gbm_clf"},
    {"label": "Support Vector Machine", "value": "svm_clf"},
    {"label": "Logistic Regression", "value": "lr_clf"},
    {"label": "K-Nearest Neighbors", "value": "knn_clf"},
    {"label": "Decision Tree", "value": "dt_clf"},
]

REGRESSOR_OPTIONS = [
    {"label": "Random Forest Regressor", "value": "rf_reg"},
    {"label": "Gradient Boosting Regressor", "value": "gbm_reg"},
    {"label": "Linear Regression", "value": "lr_reg"},
    {"label": "Ridge Regression", "value": "ridge_reg"},
    {"label": "Support Vector Regressor", "value": "svr_reg"},
]

CLUSTER_OPTIONS = [
    {"label": "K-Means", "value": "kmeans"},
    {"label": "DBSCAN", "value": "dbscan"},
    {"label": "Agglomerative", "value": "agg"},
]

TRAINING_MODE_OPTIONS = [
    {"label": "Quick Train", "value": "quick"},
    {"label": "Cross Validation", "value": "cv"},
    {"label": "Random Search", "value": "random_search"},
]

CV_STRATEGY_OPTIONS = [
    {"label": "Holdout", "value": "holdout"},
    {"label": "K-Fold", "value": "kfold"},
    {"label": "Stratified K-Fold", "value": "stratified_kfold"},
]

PRIMARY_METRIC_OPTIONS = {
    "classification": [
        {"label": "F1 Weighted", "value": "f1_weighted"},
        {"label": "Accuracy", "value": "accuracy"},
        {"label": "Precision Weighted", "value": "precision_weighted"},
        {"label": "Recall Weighted", "value": "recall_weighted"},
    ],
    "regression": [
        {"label": "RMSE", "value": "rmse"},
        {"label": "MAE", "value": "mae"},
        {"label": "R2", "value": "r2"},
        {"label": "MAPE", "value": "mape"},
    ],
}

ALGORITHM_LABELS = {
    "rf_clf": "Random Forest",
    "gbm_clf": "Gradient Boosting",
    "svm_clf": "Support Vector Machine",
    "lr_clf": "Logistic Regression",
    "knn_clf": "KNN",
    "dt_clf": "Decision Tree",
    "rf_reg": "Random Forest Regressor",
    "gbm_reg": "Gradient Boosting Regressor",
    "lr_reg": "Linear Regression",
    "ridge_reg": "Ridge Regression",
    "svr_reg": "SVR",
    "kmeans": "K-Means",
    "dbscan": "DBSCAN",
    "agg": "Agglomerative",
    "ts_linear": "Linear Trend",
    "ts_rf": "Random Forest Forecaster",
    "ts_arima": "AR-like Baseline",
}

TASK_LABELS = {
    "classification": "Classification",
    "regression": "Regression",
    "clustering": "Clustering",
    "timeseries": "Time Series",
}

DEFAULT_PRIMARY_METRIC = {
    "classification": "f1_weighted",
    "regression": "rmse",
}

ARTIFACT_ROOT = Path("artifacts") / "ml"
PROJECT_INDEX_FILE = ARTIFACT_ROOT / "project_index.json"
ARTIFACT_VERSION = 1


try:
    import sklearn  # noqa: F401
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
