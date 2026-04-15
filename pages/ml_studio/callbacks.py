# -*- coding: utf-8 -*-
"""Callbacks for the professional ML workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import ALL, Input, Output, State, callback, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate

from core.data_manager import DataManager
from .components import algorithm_guide_card, empty_placeholder, kpi_card, workflow_hint_card
from .config import ALGORITHM_GUIDANCE, ACCENT_COLORS, CV_STRATEGY_OPTIONS, DEFAULT_PRIMARY_METRIC, HAS_SKLEARN, PRIMARY_METRIC_OPTIONS, TASK_LABELS
from .model_utils import (
    convert_metadata_to_published,
    delete_run_artifact,
    get_published_model_context,
    load_artifact,
    load_project_index,
    load_runs_from_index,
    publish_cached_run,
    run_cross_validation,
    run_model_search,
    run_single_training,
    serialize_artifact,
    set_published_run_in_index,
    summarize_run_for_index,
    sync_run_to_project_index,
    update_cached_model_context,
    write_project_index,
)


def _infer_task(active_tab: str, target: str | None) -> str | None:
    if active_tab == "tab-clf":
        return "classification"
    if active_tab == "tab-reg":
        return "regression"
    if active_tab == "tab-cluster":
        return "clustering"
    if active_tab == "tab-ts":
        return "timeseries"
    if not target:
        return None
    df = DataManager().active_df
    if df is None or target not in df.columns:
        return None
    series = df[target]
    if pd.api.types.is_numeric_dtype(series) and series.nunique(dropna=True) > 10:
        return "regression"
    return "classification"


def _status(message: str, color: str = "info"):
    return dbc.Alert(message, color=color, className="py-2 px-3 mb-0")


def _format_metric(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.4f}"
    except Exception:
        return str(value)


def _run_metric_summary(run: dict[str, Any]) -> tuple[str, str]:
    metrics = run.get("metrics", {})
    if "holdout" in metrics:
        secondary = metrics["holdout"]
        if run.get("task") == "classification":
            return _format_metric(run.get("best_score")), f"acc={_format_metric(secondary.get('accuracy'))}"
        return _format_metric(run.get("best_score")), f"r2={_format_metric(secondary.get('r2'))}"
    if "cv" in metrics:
        secondary = metrics["cv"]
        return _format_metric(secondary.get("mean")), f"std={_format_metric(secondary.get('std'))}"
    if "search" in metrics:
        secondary = metrics["search"]
        return _format_metric(secondary.get("mean")), f"std={_format_metric(secondary.get('std'))}"
    return _format_metric(run.get("best_score")), ""


def _load_run_detail(run_summary: dict[str, Any]) -> tuple[dict[str, Any], Any | None]:
    artifact_path = run_summary.get("artifact_path")
    if artifact_path and Path(artifact_path).exists():
        model, metadata, report = load_artifact(artifact_path)
        detail = dict(run_summary)
        detail.update(metadata)
        detail["report"] = report
        detail["artifact_path"] = artifact_path
        update_cached_model_context(model, detail, detail["run_id"], published=run_summary.get("is_published", False))
        return detail, model
    return dict(run_summary), None


def _build_classifier_params(algo: str, n_est, max_depth, c_val, kernel, lr_c, k_val) -> dict[str, Any]:
    if algo in {"rf_clf", "gbm_clf"}:
        return {"n_estimators": n_est or 200, "max_depth": max_depth}
    if algo == "svm_clf":
        return {"C": c_val or 1.0, "kernel": kernel or "rbf"}
    if algo == "lr_clf":
        return {"C": lr_c or 1.0}
    if algo == "knn_clf":
        return {"n_neighbors": k_val or 5}
    return {"max_depth": max_depth}


def _build_regressor_params(algo: str, n_est, max_depth, alpha, svr_c) -> dict[str, Any]:
    if algo in {"rf_reg", "gbm_reg"}:
        return {"n_estimators": n_est or 200, "max_depth": max_depth}
    if algo == "ridge_reg":
        return {"alpha": alpha or 1.0}
    if algo == "svr_reg":
        return {"C": svr_c or 1.0}
    return {}


def _published_summary(published_model: dict[str, Any] | None):
    if not published_model:
        return None
    return convert_metadata_to_published(published_model, published_model.get("artifact_path"))


def _resolve_algorithm_guide(active_tab: str, classifier: str | None, regressor: str | None, cluster_algo: str | None, ts_algo: str | None) -> dict[str, Any]:
    if active_tab == "tab-reg":
        return ALGORITHM_GUIDANCE["regression"].get(regressor or "rf_reg", ALGORITHM_GUIDANCE["regression"]["rf_reg"])
    if active_tab == "tab-cluster":
        return ALGORITHM_GUIDANCE["clustering"].get(cluster_algo or "kmeans", ALGORITHM_GUIDANCE["clustering"]["kmeans"])
    if active_tab == "tab-ts":
        return ALGORITHM_GUIDANCE["timeseries"].get(ts_algo or "ts_linear", ALGORITHM_GUIDANCE["timeseries"]["ts_linear"])
    return ALGORITHM_GUIDANCE["classification"].get(classifier or "rf_clf", ALGORITHM_GUIDANCE["classification"]["rf_clf"])


def _workflow_next_step(active_tab: str, target: str | None, features: list[str] | None, run: dict[str, Any] | None, published_model: dict[str, Any] | None) -> html.Div:
    if active_tab in {"tab-cluster", "tab-ts"}:
        label = "聚类" if active_tab == "tab-cluster" else "时间序列"
        return workflow_hint_card(
            "当前阶段说明",
            f"{label}仍处于基础模式。若你要稳定交付，请优先使用分类或回归工作流。",
            color="secondary",
        )
    if not target:
        return workflow_hint_card("下一步建议", "先选目标列，系统会据此判断任务类型并刷新主指标建议。", color="primary")
    if not features:
        return workflow_hint_card("下一步建议", "目标列选好后，再补充至少一个特征列；优先选择和目标最相关的字段。", color="primary")
    if not run:
        return workflow_hint_card("下一步建议", "当前已经可以训练。第一次建议用“快速训练”，先确认流程和结果是否合理。", color="success")
    if not published_model:
        return workflow_hint_card("训练后建议", "先查看总览和特征重要性；确认结果可靠后，再发布模型进入预测环节。", color="info")
    return workflow_hint_card("模型已就绪", "当前模型已经发布，可以去“预测”页签做单样本或整表预测。", color="success")


def _prediction_form(published_model: dict[str, Any]) -> html.Div:
    schema = published_model.get("feature_schema", {})
    numeric = set(schema.get("numeric", []))
    inputs = []
    for feature in schema.get("all", []):
        input_type = "number" if feature in numeric else "text"
        inputs.append(
            dbc.Col(
                [
                    html.Label(feature, className="form-label small"),
                    dcc.Input(id={"type": "ml-single-input", "feature": feature}, type=input_type, className="form-control form-control-sm", debounce=True),
                ],
                md=6,
                className="mb-3",
            )
        )
    return html.Div([
        dbc.Row(inputs, className="g-2"),
        dbc.Button("预测单条样本", id="btn-ml-single-predict", color="primary", className="me-2"),
        html.Div(id="ml-single-predict-output", className="mt-3"),
        html.Hr(),
        html.H6("批量预测"),
        dbc.Input(id="ml-batch-pred-col", placeholder="预测结果列名", value="prediction", className="mb-2"),
        dbc.Button("写回当前数据集", id="btn-ml-batch-predict", color="secondary"),
        html.Div(id="ml-batch-predict-output", className="mt-3"),
    ])


def _render_overview(run: dict[str, Any]):
    task = run.get("task")
    if task == "classification" and run.get("report", {}).get("confusion_matrix"):
        fig = px.imshow(run["report"]["confusion_matrix"], text_auto=True, color_continuous_scale="Blues", title="Confusion Matrix")
        return dcc.Graph(figure=fig, config={"displayModeBar": False})
    if task == "regression" and run.get("y_test") and run.get("y_pred"):
        df = pd.DataFrame({"Actual": run["y_test"], "Predicted": run["y_pred"]})
        fig = px.scatter(df, x="Actual", y="Predicted", trendline="ols", title="Actual vs Predicted")
        return dcc.Graph(figure=fig, config={"displayModeBar": False})
    if run.get("search_summary"):
        return dbc.Table.from_dataframe(pd.DataFrame(run["search_summary"]), striped=True, bordered=False, hover=True, size="sm")
    if run.get("cv_scores"):
        fig = px.line(y=run["cv_scores"], markers=True, title="Cross-validation Scores")
        return dcc.Graph(figure=fig, config={"displayModeBar": False})
    return empty_placeholder("No visualization available for this run.")


def _render_feature_tab(run: dict[str, Any]):
    importances = run.get("importances") or []
    if not importances:
        return dbc.Alert("This model does not expose feature importance.", color="secondary")
    frame = pd.DataFrame(importances[:20])
    fig = px.bar(frame.sort_values("importance"), x="importance", y="feature", orientation="h", title="Top Feature Importance")
    fig.update_layout(height=500)
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def _render_report_tab(run: dict[str, Any]):
    return html.Pre(json.dumps(run.get("report", {}), ensure_ascii=False, indent=2), style={"whiteSpace": "pre-wrap", "fontSize": "0.8rem"})

@callback(
    Output("ml-clf-panel", "style"),
    Output("ml-reg-panel", "style"),
    Output("ml-cluster-panel", "style"),
    Output("ml-ts-panel", "style"),
    Input("ml-algo-tabs", "active_tab"),
)
def toggle_algo_panels(active_tab):
    d_none = {"display": "none"}
    if active_tab == "tab-clf":
        return {}, d_none, d_none, d_none
    if active_tab == "tab-reg":
        return d_none, {}, d_none, d_none
    if active_tab == "tab-cluster":
        return d_none, d_none, {}, d_none
    return d_none, d_none, d_none, {}


@callback(Output("ml-tutorial-offcanvas", "is_open"), Input("btn-ml-tutorial", "n_clicks"), State("ml-tutorial-offcanvas", "is_open"), prevent_initial_call=True)
def toggle_tutorial(_, is_open):
    return not is_open


@callback(
    Output("ml-task-type-badge", "children"),
    Output("ml-primary-metric", "options"),
    Output("ml-primary-metric", "value"),
    Output("ml-cv-strategy", "options"),
    Output("ml-cv-strategy", "value"),
    Input("ml-target-var", "value"),
    Input("ml-algo-tabs", "active_tab"),
    State("ml-primary-metric", "value"),
    State("ml-cv-strategy", "value"),
)
def update_workflow_controls(target, active_tab, current_metric, current_cv):
    task = _infer_task(active_tab, target)
    if task == "classification":
        badge = dbc.Badge("分类任务：预测离散类别", color="primary")
        metric_options = PRIMARY_METRIC_OPTIONS["classification"]
        cv_options = CV_STRATEGY_OPTIONS
        metric_value = current_metric if current_metric in {item["value"] for item in metric_options} else DEFAULT_PRIMARY_METRIC["classification"]
        cv_value = current_cv if current_cv in {item["value"] for item in cv_options} else "holdout"
        return badge, metric_options, metric_value, cv_options, cv_value
    if task == "regression":
        badge = dbc.Badge("回归任务：预测连续数值", color="success")
        metric_options = PRIMARY_METRIC_OPTIONS["regression"]
        cv_options = [item for item in CV_STRATEGY_OPTIONS if item["value"] != "stratified_kfold"]
        metric_value = current_metric if current_metric in {item["value"] for item in metric_options} else DEFAULT_PRIMARY_METRIC["regression"]
        cv_value = current_cv if current_cv in {item["value"] for item in cv_options} else "holdout"
        return badge, metric_options, metric_value, cv_options, cv_value
    label = TASK_LABELS.get(task, "请选择目标列") if task else "请选择目标列"
    return dbc.Badge(label, color="secondary"), no_update, no_update, no_update, no_update


@callback(
    Output("ml-workflow-hint", "children"),
    Input("ml-algo-tabs", "active_tab"),
    Input("ml-target-var", "value"),
    Input("ml-feature-vars", "value"),
    Input("ml-result-store", "data"),
    Input("ml-published-model-store", "data"),
)
def render_workflow_hint(active_tab, target, features, run, published_model):
    return _workflow_next_step(active_tab, target, features, run, published_model)


@callback(
    Output("ml-algo-guidance", "children"),
    Input("ml-algo-tabs", "active_tab"),
    Input("ml-classifier", "value"),
    Input("ml-regressor", "value"),
    Input("ml-cluster-algo", "value"),
    Input("ml-ts-algo", "value"),
)
def render_algorithm_guidance(active_tab, classifier, regressor, cluster_algo, ts_algo):
    return algorithm_guide_card(_resolve_algorithm_guide(active_tab, classifier, regressor, cluster_algo, ts_algo))


@callback(Output("ml-predict-tab", "disabled"), Input("ml-published-model-store", "data"), Input("ml-algo-tabs", "active_tab"))
def toggle_predict_tab(published_model, active_tab):
    return not published_model or active_tab in {"tab-cluster", "tab-ts"}


@callback(Output("ml-cluster-params-store", "data"), Input("ml-cluster-algo", "value"), Input("param-n-clusters", "value"), Input("param-eps", "value"), prevent_initial_call=True)
def store_cluster_params(algo, n_clusters, eps):
    return {"algorithm": algo, "n_clusters": n_clusters, "eps": eps}


@callback(
    Output("ml-runs-store", "data", allow_duplicate=True),
    Output("ml-published-model-store", "data", allow_duplicate=True),
    Output("ml-project-store", "data", allow_duplicate=True),
    Output("ml-train-status", "children", allow_duplicate=True),
    Input("btn-ml-load-project", "n_clicks"),
    prevent_initial_call="initial_duplicate",
)
def load_local_project(_):
    index = load_project_index()
    runs = load_runs_from_index()
    published_model = None
    published_run_id = index.get("published_run_id")
    if published_run_id:
        selected = next((run for run in runs if run.get("run_id") == published_run_id and run.get("artifact_path")), None)
        if selected and Path(selected["artifact_path"]).exists():
            model, metadata, report = load_artifact(selected["artifact_path"])
            detail = dict(selected)
            detail.update(metadata)
            detail["report"] = report
            detail["artifact_path"] = selected["artifact_path"]
            update_cached_model_context(model, detail, detail["run_id"], published=True)
            published_model = convert_metadata_to_published(detail, selected["artifact_path"])
    message = _status(f"Loaded {len(runs)} local runs.", "secondary")
    return runs, published_model, index, message


@callback(
    Output("ml-project-store", "data", allow_duplicate=True),
    Output("ml-train-status", "children", allow_duplicate=True),
    Input("btn-ml-save-project", "n_clicks"),
    State("ml-runs-store", "data"),
    State("ml-published-model-store", "data"),
    prevent_initial_call=True,
)
def sync_local_project(_, runs, published_model):
    index = {"runs": list(runs or []), "published_run_id": published_model.get("run_id") if published_model else None}
    write_project_index(index)
    return load_project_index(), _status("Project index synchronized.", "success")


@callback(
    Output("ml-train-status", "children", allow_duplicate=True),
    Output("ml-result-store", "data"),
    Output("ml-eval-tabs", "active_tab", allow_duplicate=True),
    Output("ml-runs-store", "data", allow_duplicate=True),
    Output("ml-project-store", "data", allow_duplicate=True),
    Input("btn-ml-train", "n_clicks"),
    State("ml-algo-tabs", "active_tab"),
    State("ml-target-var", "value"),
    State("ml-feature-vars", "value"),
    State("ml-impute-strategy", "value"),
    State("ml-scaler", "value"),
    State("ml-test-size", "value"),
    State("ml-training-mode", "value"),
    State("ml-cv-strategy", "value"),
    State("ml-cv-folds", "value"),
    State("ml-search-iterations", "value"),
    State("ml-primary-metric", "value"),
    State("ml-classifier", "value"),
    State("ml-regressor", "value"),
    State("param-n-est", "value"),
    State("param-max-depth", "value"),
    State("param-c", "value"),
    State("param-kernel", "value"),
    State("param-lr-c", "value"),
    State("param-k", "value"),
    State("param-reg-n-est", "value"),
    State("param-reg-max-depth", "value"),
    State("param-alpha", "value"),
    State("param-svr-c", "value"),
    State("ml-runs-store", "data"),
    prevent_initial_call=True,
)
def train_model(_, active_tab, target, features, impute_strategy, scaler_type, test_size, training_mode, cv_strategy, cv_folds, search_iterations, primary_metric, classifier, regressor, n_est, max_depth, c_val, kernel, lr_c, k_val, reg_n_est, reg_max_depth, alpha, svr_c, run_history):
    if not HAS_SKLEARN:
        return _status("scikit-learn is not installed.", "danger"), no_update, no_update, no_update, no_update
    if active_tab in {"tab-cluster", "tab-ts"}:
        return _status("Phase 1 keeps clustering and time-series on the basic path. The professional workflow is enabled for classification and regression.", "warning"), no_update, no_update, no_update, no_update
    if not target or not features:
        return _status("Select one target column and at least one feature column.", "warning"), no_update, no_update, no_update, no_update
    df = DataManager().active_df
    if df is None or df.empty:
        return _status("No active dataset available.", "warning"), no_update, no_update, no_update, no_update
    task = _infer_task(active_tab, target)
    algo = classifier if task == "classification" else regressor
    params = _build_classifier_params(algo, n_est, max_depth, c_val, kernel, lr_c, k_val) if task == "classification" else _build_regressor_params(algo, reg_n_est, reg_max_depth, alpha, svr_c)
    effective_cv = cv_strategy if cv_strategy != "holdout" else ("stratified_kfold" if task == "classification" else "kfold")
    try:
        if training_mode == "quick" or cv_strategy == "holdout":
            run, model = run_single_training(df, features, target, task, algo, params, impute_strategy, scaler_type, test_size, primary_metric)
        elif training_mode == "cv":
            run, model = run_cross_validation(df, features, target, task, algo, params, impute_strategy, scaler_type, effective_cv, int(cv_folds or 5), primary_metric)
        else:
            run, model = run_model_search(df, features, target, task, algo, params, impute_strategy, scaler_type, effective_cv, int(cv_folds or 5), primary_metric or DEFAULT_PRIMARY_METRIC[task], int(search_iterations or 10))
        metadata = serialize_artifact(run, model)
        detail = dict(run)
        detail.update(metadata)
        update_cached_model_context(model, detail, run["run_id"])
        summary = summarize_run_for_index(run)
        new_runs = [summary] + [item for item in (run_history or []) if item.get("run_id") != run["run_id"]]
        return _status(f"Training finished: {run['algorithm_label']} ({run['training_mode']}).", "success"), detail, "tab-overview", new_runs, load_project_index()
    except Exception as exc:
        return _status(f"Training failed: {exc}", "danger"), no_update, no_update, no_update, no_update

@callback(
    Output("ml-runs-store", "data", allow_duplicate=True),
    Output("ml-published-model-store", "data", allow_duplicate=True),
    Output("ml-result-store", "data", allow_duplicate=True),
    Output("ml-train-status", "children", allow_duplicate=True),
    Output("ml-project-store", "data", allow_duplicate=True),
    Output("ml-eval-tabs", "active_tab", allow_duplicate=True),
    Input({"type": "ml-run-action", "action": ALL, "run_id": ALL}, "n_clicks"),
    State("ml-runs-store", "data"),
    State("ml-published-model-store", "data"),
    State("ml-result-store", "data"),
    prevent_initial_call=True,
)
def handle_run_actions(_, runs, published_model, current_result):
    trigger = ctx.triggered_id
    if not trigger:
        raise PreventUpdate
    run_id = trigger.get("run_id")
    action = trigger.get("action")
    run_list = list(runs or [])
    selected = next((item for item in run_list if item.get("run_id") == run_id), None)
    if not selected:
        return no_update, no_update, no_update, _status("Run not found.", "warning"), no_update, no_update

    if action in {"view", "load", "publish", "save"}:
        detail, model = _load_run_detail(selected)
    else:
        detail, model = selected, None

    if action in {"view", "load"}:
        return run_list, published_model, detail, _status(f"Run {action}ed.", "secondary"), load_project_index(), "tab-overview"

    if action == "publish":
        if model is None:
            return no_update, no_update, no_update, _status("Unable to load artifact for publishing.", "danger"), no_update, no_update
        update_cached_model_context(model, detail, run_id, published=True)
        publish_cached_run(run_id)
        updated_runs = []
        for item in run_list:
            next_item = dict(item)
            next_item["is_published"] = item.get("run_id") == run_id
            updated_runs.append(next_item)
        set_published_run_in_index(run_id)
        published_summary = convert_metadata_to_published(detail, detail.get("artifact_path"))
        return updated_runs, published_summary, detail, _status("Model published for inference.", "success"), load_project_index(), "tab-overview"

    if action == "save":
        if selected.get("artifact_path"):
            sync_run_to_project_index(selected)
            return run_list, published_model, current_result, _status("Run already saved locally.", "secondary"), load_project_index(), no_update
        if model is None:
            return no_update, no_update, no_update, _status("No in-memory model available to save.", "warning"), no_update, no_update
        serialize_artifact(detail, model)
        updated_runs = [summarize_run_for_index(detail) if item.get("run_id") == run_id else item for item in run_list]
        return updated_runs, published_model, detail, _status("Run saved locally.", "success"), load_project_index(), no_update

    if action == "delete":
        project_index = delete_run_artifact(run_id, selected.get("artifact_path"))
        updated_runs = [item for item in run_list if item.get("run_id") != run_id]
        next_published = published_model if not published_model or published_model.get("run_id") != run_id else None
        next_result = current_result if not current_result or current_result.get("run_id") != run_id else None
        if next_published is None:
            set_published_run_in_index(None)
        return updated_runs, next_published, next_result, _status("Run deleted.", "secondary"), project_index, "tab-overview"

    raise PreventUpdate


@callback(Output("ml-runs-panel", "children"), Input("ml-runs-store", "data"))
def render_runs_panel(runs):
    items = runs or []
    if not items:
        return empty_placeholder("No experiment runs yet.")
    cards = []
    for run in items[:12]:
        primary, secondary = _run_metric_summary(run)
        cards.append(
            html.Div(
                style={"border": "1px solid var(--border)", "borderRadius": "10px", "padding": "12px", "marginBottom": "10px"},
                children=[
                    html.Div([
                        html.Strong(run.get("algorithm_label", run.get("algorithm"))),
                        dbc.Badge("Published" if run.get("is_published") else run.get("training_mode", "run"), color="success" if run.get("is_published") else "secondary", className="ms-2"),
                    ]),
                    html.Div(f"{run.get('task')} | {run.get('cv_strategy')} | {run.get('created_at', '')[:19]}", className="text-muted small mb-2"),
                    html.Div(f"Primary: {primary}", className="small"),
                    html.Div(secondary, className="small text-muted mb-2"),
                    html.Div([
                        dbc.Button("View", id={"type": "ml-run-action", "action": "view", "run_id": run["run_id"]}, size="sm", color="secondary", outline=True, className="me-1"),
                        dbc.Button("Load", id={"type": "ml-run-action", "action": "load", "run_id": run["run_id"]}, size="sm", color="secondary", outline=True, className="me-1"),
                        dbc.Button("Publish", id={"type": "ml-run-action", "action": "publish", "run_id": run["run_id"]}, size="sm", color="primary", className="me-1"),
                        dbc.Button("Save", id={"type": "ml-run-action", "action": "save", "run_id": run["run_id"]}, size="sm", color="info", outline=True, className="me-1"),
                        dbc.Button("Delete", id={"type": "ml-run-action", "action": "delete", "run_id": run["run_id"]}, size="sm", color="danger", outline=True),
                    ]),
                ],
            )
        )
    return html.Div(cards)


@callback(Output("ml-published-model-panel", "children"), Input("ml-published-model-store", "data"))
def render_published_panel(published_model):
    if not published_model:
        return empty_placeholder("Publish a run to enable formal inference.")
    return html.Div([
        html.H6(published_model.get("algorithm_label", "Published Model")),
        html.Div(f"Task: {published_model.get('task')}", className="small mb-1"),
        html.Div(f"Primary metric: {published_model.get('primary_metric')} = {_format_metric(published_model.get('best_score'))}", className="small mb-1"),
        html.Div(f"Target: {published_model.get('target_column')}", className="small mb-1"),
        html.Div(f"Features: {len(published_model.get('feature_schema', {}).get('all', []))}", className="small mb-2"),
        html.Div("Best params", className="fw-semibold small"),
        html.Pre(json.dumps(published_model.get("best_params", {}), ensure_ascii=False, indent=2), style={"fontSize": "0.75rem", "whiteSpace": "pre-wrap"}),
    ])


@callback(Output("ml-kpi-row", "children"), Input("ml-result-store", "data"))
def render_kpis(run):
    if not run:
        return [kpi_card("status", "No run", "Train a model to see experiment KPIs", ACCENT_COLORS["blue"], "bi bi-cpu")]
    features = run.get("feature_schema", {}).get("all", [])
    snapshot = run.get("dataset_snapshot", {})
    return [
        kpi_card("Primary Score", _format_metric(run.get("best_score")), run.get("primary_metric", "metric"), ACCENT_COLORS["blue"], "bi bi-trophy"),
        kpi_card("Training Mode", str(run.get("training_mode", "-")).upper(), run.get("cv_strategy", "-"), ACCENT_COLORS["green"], "bi bi-diagram-3"),
        kpi_card("Fit Time", _format_metric(run.get("fit_time")), "seconds", ACCENT_COLORS["purple"], "bi bi-stopwatch"),
        kpi_card("Dataset", str(snapshot.get("rows", 0)), f"rows | {len(features)} features", ACCENT_COLORS["orange"], "bi bi-table"),
    ]


@callback(Output("ml-tab-content", "children"), Input("ml-eval-tabs", "active_tab"), Input("ml-result-store", "data"), Input("ml-published-model-store", "data"))
def render_tab_content(active_tab, run, published_model):
    if active_tab == "tab-predict":
        if not published_model:
            return dbc.Alert("Publish a model before using prediction.", color="warning")
        return _prediction_form(published_model)
    if not run:
        return empty_placeholder()
    if active_tab == "tab-overview":
        return _render_overview(run)
    if active_tab == "tab-feature":
        return _render_feature_tab(run)
    return _render_report_tab(run)


@callback(Output("ml-single-predict-output", "children"), Input("btn-ml-single-predict", "n_clicks"), State({"type": "ml-single-input", "feature": ALL}, "value"), State({"type": "ml-single-input", "feature": ALL}, "id"), State("ml-published-model-store", "data"), prevent_initial_call=True)
def predict_single_sample(_, values, ids, published_model):
    model, metadata = get_published_model_context()
    if not model or not published_model:
        raise PreventUpdate
    feature_schema = published_model.get("feature_schema", {})
    numeric = set(feature_schema.get("numeric", []))
    record = {}
    for value, item in zip(values, ids):
        feature = item["feature"]
        if feature in numeric and value not in (None, ""):
            record[feature] = float(value)
        else:
            record[feature] = value
    input_df = pd.DataFrame([record], columns=feature_schema.get("all", []))
    prediction = model.predict(input_df)[0]
    blocks = [html.Div(f"Prediction: {prediction}", className="fw-semibold")]
    if hasattr(model, "predict_proba") and published_model.get("task") == "classification":
        proba = model.predict_proba(input_df)[0]
        classes = getattr(model.named_steps["model"], "classes_", None)
        if classes is not None:
            probs = {str(label): float(score) for label, score in zip(classes, proba)}
            blocks.append(html.Pre(json.dumps(probs, ensure_ascii=False, indent=2), style={"fontSize": "0.8rem"}))
    return dbc.Alert(blocks, color="success")


@callback(Output("ml-batch-predict-output", "children"), Input("btn-ml-batch-predict", "n_clicks"), State("ml-batch-pred-col", "value"), State("ml-published-model-store", "data"), prevent_initial_call=True)
def predict_batch(_, prediction_col, published_model):
    model, metadata = get_published_model_context()
    if not model or not published_model:
        raise PreventUpdate
    dm = DataManager()
    df = dm.active_df
    if df is None or df.empty:
        return _status("No active dataset available for batch prediction.", "warning")
    required = published_model.get("feature_schema", {}).get("all", [])
    missing = [column for column in required if column not in df.columns]
    if missing:
        return _status(f"Missing required columns: {', '.join(missing)}", "danger")
    result_df = df.copy()
    column_name = prediction_col or "prediction"
    result_df[column_name] = model.predict(result_df[required])
    dm.update_active_dataset(result_df, snapshot=True)
    return _status(f"Predictions written to active dataset column '{column_name}'.", "success")


@callback(
    Output("project-page-store", "data", allow_duplicate=True),
    Input("ml-algo-tabs", "active_tab"),
    Input("ml-target-var", "value"),
    Input("ml-feature-vars", "value"),
    Input("ml-impute-strategy", "value"),
    Input("ml-scaler", "value"),
    Input("ml-test-size", "value"),
    Input("ml-training-mode", "value"),
    Input("ml-cv-strategy", "value"),
    Input("ml-cv-folds", "value"),
    Input("ml-search-iterations", "value"),
    Input("ml-primary-metric", "value"),
    Input("ml-classifier", "value"),
    Input("ml-regressor", "value"),
    Input("ml-cluster-algo", "value"),
    Input("param-n-clusters", "value"),
    Input("param-eps", "value"),
    Input("ml-ts-algo", "value"),
    Input("param-ts-timecol", "value"),
    Input("param-ts-targetcol", "value"),
    Input("param-ts-horizon", "value"),
    Input("param-ts-ci", "value"),
    Input("ml-result-store", "data"),
    Input("ml-runs-store", "data"),
    Input("ml-published-model-store", "data"),
    Input("ml-project-store", "data"),
    Input("ml-eval-tabs", "active_tab"),
    State("project-page-store", "data"),
    prevent_initial_call=True,
)
def sync_ml_project_state(
    algo_tab,
    target,
    features,
    impute_strategy,
    scaler,
    test_size,
    training_mode,
    cv_strategy,
    cv_folds,
    search_iterations,
    primary_metric,
    classifier,
    regressor,
    cluster_algo,
    n_clusters,
    eps,
    ts_algo,
    ts_timecol,
    ts_targetcol,
    ts_horizon,
    ts_ci,
    result_data,
    runs_data,
    published_model,
    ml_project_store,
    eval_tab,
    project_state,
):
    state = dict(project_state or {})
    state["ml_studio"] = {
        "controls": {
            "algo_tab": algo_tab,
            "target": target,
            "features": features,
            "impute_strategy": impute_strategy,
            "scaler": scaler,
            "test_size": test_size,
            "training_mode": training_mode,
            "cv_strategy": cv_strategy,
            "cv_folds": cv_folds,
            "search_iterations": search_iterations,
            "primary_metric": primary_metric,
            "classifier": classifier,
            "regressor": regressor,
            "cluster_algo": cluster_algo,
            "n_clusters": n_clusters,
            "eps": eps,
            "ts_algo": ts_algo,
            "ts_timecol": ts_timecol,
            "ts_targetcol": ts_targetcol,
            "ts_horizon": ts_horizon,
            "ts_ci": ts_ci,
            "eval_tab": eval_tab,
        },
        "result": result_data,
        "runs": runs_data or [],
        "published_model": published_model,
        "project_store": ml_project_store,
    }
    return state


@callback(
    Output("ml-algo-tabs", "active_tab", allow_duplicate=True),
    Output("ml-target-var", "value", allow_duplicate=True),
    Output("ml-feature-vars", "value", allow_duplicate=True),
    Output("ml-impute-strategy", "value", allow_duplicate=True),
    Output("ml-scaler", "value", allow_duplicate=True),
    Output("ml-test-size", "value", allow_duplicate=True),
    Output("ml-training-mode", "value", allow_duplicate=True),
    Output("ml-cv-strategy", "value", allow_duplicate=True),
    Output("ml-cv-folds", "value", allow_duplicate=True),
    Output("ml-search-iterations", "value", allow_duplicate=True),
    Output("ml-primary-metric", "value", allow_duplicate=True),
    Output("ml-classifier", "value", allow_duplicate=True),
    Output("ml-regressor", "value", allow_duplicate=True),
    Output("ml-cluster-algo", "value", allow_duplicate=True),
    Output("param-n-clusters", "value", allow_duplicate=True),
    Output("param-eps", "value", allow_duplicate=True),
    Output("ml-ts-algo", "value", allow_duplicate=True),
    Output("param-ts-timecol", "value", allow_duplicate=True),
    Output("param-ts-targetcol", "value", allow_duplicate=True),
    Output("param-ts-horizon", "value", allow_duplicate=True),
    Output("param-ts-ci", "value", allow_duplicate=True),
    Output("ml-result-store", "data", allow_duplicate=True),
    Output("ml-runs-store", "data", allow_duplicate=True),
    Output("ml-published-model-store", "data", allow_duplicate=True),
    Output("ml-project-store", "data", allow_duplicate=True),
    Output("ml-eval-tabs", "active_tab", allow_duplicate=True),
    Input("project-restore-store", "data"),
    Input("url", "pathname"),
    prevent_initial_call=True,
)
def restore_ml_project_state(project_restore, pathname):
    if pathname != "/ml" or not project_restore:
        return (no_update,) * 26

    page_state = (project_restore.get("page_state") or {}).get("ml_studio")
    if not page_state:
        return (no_update,) * 26

    controls = page_state.get("controls") or {}
    return (
        controls.get("algo_tab", "tab-clf"),
        controls.get("target"),
        controls.get("features"),
        controls.get("impute_strategy", "mean"),
        controls.get("scaler", "standard"),
        controls.get("test_size", 0.2),
        controls.get("training_mode", "quick"),
        controls.get("cv_strategy", "holdout"),
        controls.get("cv_folds", 5),
        controls.get("search_iterations", 10),
        controls.get("primary_metric", DEFAULT_PRIMARY_METRIC["classification"]),
        controls.get("classifier", "rf_clf"),
        controls.get("regressor", "rf_reg"),
        controls.get("cluster_algo", "kmeans"),
        controls.get("n_clusters", 3),
        controls.get("eps", 0.5),
        controls.get("ts_algo", "ts_linear"),
        controls.get("ts_timecol"),
        controls.get("ts_targetcol"),
        controls.get("ts_horizon", 10),
        controls.get("ts_ci", 95),
        page_state.get("result"),
        page_state.get("runs", []),
        page_state.get("published_model"),
        page_state.get("project_store"),
        controls.get("eval_tab", "tab-overview"),
    )
