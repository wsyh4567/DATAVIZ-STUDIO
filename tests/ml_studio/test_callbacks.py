from __future__ import annotations

import pytest
from dash import dcc
from dash.development.base_component import Component

pytest.importorskip("dash")
pytest.importorskip("dash_bootstrap_components")

from pages.ml_studio.callbacks import (
    _render_feature_tab,
    _render_overview,
    predict_batch,
    render_kpis,
    render_published_panel,
    render_runs_panel,
    render_tab_content,
    train_model,
)


def _collect_text(node, chunks=None):
    if chunks is None:
        chunks = []
    if isinstance(node, (list, tuple)):
        for child in node:
            _collect_text(child, chunks)
        return chunks
    if isinstance(node, str):
        chunks.append(node)
        return chunks
    if isinstance(node, Component):
        children = getattr(node, "children", None)
        if isinstance(children, (list, tuple)):
            for child in children:
                _collect_text(child, chunks)
        elif children is not None:
            _collect_text(children, chunks)
    return chunks


def test_render_kpis_uses_chinese_labels():
    cards = render_kpis(
        {
            "best_score": 0.9123,
            "primary_metric": "f1_weighted",
            "training_mode": "quick",
            "cv_strategy": "holdout",
            "fit_time": 1.52,
            "feature_schema": {"all": ["面积", "房龄"]},
            "dataset_snapshot": {"rows": 48},
        }
    )

    text = " ".join(_collect_text(cards))

    assert "主指标" in text
    assert "训练模式" in text
    assert "训练耗时" in text
    assert "数据集" in text
    assert "快速训练" in text
    assert "留出验证" in text
    assert "Primary Score" not in text


def test_render_runs_panel_and_published_panel_use_chinese_copy():
    runs_panel = render_runs_panel(
        [
            {
                "run_id": "run-1",
                "algorithm_label": "随机森林 Random Forest",
                "task": "classification",
                "cv_strategy": "holdout",
                "training_mode": "quick",
                "created_at": "2026-04-15 09:30:00",
                "best_score": 0.88,
                "metrics": {"holdout": {"accuracy": 0.87}},
                "is_published": True,
            }
        ]
    )
    published_panel = render_published_panel(
        {
            "algorithm_label": "随机森林 Random Forest",
            "task": "classification",
            "primary_metric": "f1_weighted",
            "best_score": 0.88,
            "target_column": "是否成交",
            "feature_schema": {"all": ["面积", "房龄"]},
            "best_params": {"n_estimators": 200},
        }
    )

    runs_text = " ".join(_collect_text(runs_panel))
    published_text = " ".join(_collect_text(published_panel))

    assert "已发布" in runs_text
    assert "分类任务" in runs_text
    assert "留出验证" in runs_text
    assert "查看" in runs_text and "发布" in runs_text
    assert "Published" not in runs_text
    assert "任务类型：" in published_text
    assert "主指标：" in published_text
    assert "目标列：" in published_text
    assert "最佳参数" in published_text
    assert "Primary metric" not in published_text


def test_overview_and_feature_views_are_localized():
    classification_view = _render_overview(
        {
            "task": "classification",
            "report": {"confusion_matrix": [[6, 1], [0, 5]]},
        }
    )
    regression_view = _render_overview(
        {
            "task": "regression",
            "y_test": [1.0, 2.0, 3.0],
            "y_pred": [0.9, 2.1, 2.8],
        }
    )
    feature_view = _render_feature_tab(
        {
            "importances": [
                {"feature": "面积", "importance": 0.7},
                {"feature": "房龄", "importance": 0.3},
            ]
        }
    )

    assert isinstance(classification_view, dcc.Graph)
    assert classification_view.figure.layout.title.text == "混淆矩阵"
    assert isinstance(regression_view, dcc.Graph)
    assert regression_view.figure.layout.title.text == "实际值 vs 预测值"
    assert isinstance(feature_view, dcc.Graph)
    assert feature_view.figure.layout.title.text == "特征重要性 Top 20"


def test_predict_tab_and_batch_prediction_messages_are_localized(monkeypatch):
    predict_tab = render_tab_content("tab-predict", run=None, published_model=None)
    assert "请先发布模型，再进入预测。" in " ".join(_collect_text(predict_tab))

    class _DummyDataManager:
        active_df = None

    monkeypatch.setattr("pages.ml_studio.callbacks.DataManager", _DummyDataManager)
    monkeypatch.setattr("pages.ml_studio.callbacks.get_published_model_context", lambda: (object(), {}))
    status = predict_batch(None, None, {"feature_schema": {"all": ["面积"]}})
    assert "当前没有可用于批量预测的数据集。" in " ".join(_collect_text(status))


def test_train_model_degraded_tabs_return_chinese_guardrail():
    status, *_ = train_model(
        None,
        "tab-cluster",
        None,
        None,
        "mean",
        "standard",
        0.2,
        "quick",
        "holdout",
        5,
        10,
        "f1_weighted",
        "rf_clf",
        "rf_reg",
        200,
        10,
        1.0,
        "rbf",
        1.0,
        5,
        200,
        10,
        1.0,
        1.0,
        [],
    )

    assert "完整工作流只支持分类和回归" in " ".join(_collect_text(status))
