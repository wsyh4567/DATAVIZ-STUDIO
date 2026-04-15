# -*- coding: utf-8 -*-
"""ML Studio layout."""

from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from core.data_manager import DataManager
from .components import algorithm_guide_card, empty_placeholder, tutorial_offcanvas, workflow_hint_card
from .config import (
    ACCENT_COLORS,
    ALGORITHM_GUIDANCE,
    CARD_STYLE,
    CLASSIFIER_OPTIONS,
    CLUSTER_OPTIONS,
    CV_STRATEGY_OPTIONS,
    HAS_SKLEARN,
    PRIMARY_METRIC_OPTIONS,
    REGRESSOR_OPTIONS,
    TRAINING_MODE_OPTIONS,
    WORKFLOW_GUIDE_STEPS,
)


def create_ml_studio_page() -> html.Div:
    dm = DataManager()
    df = dm.active_df

    if not HAS_SKLEARN:
        return _no_sklearn_view()
    if df is None or df.empty:
        return _no_data_view()

    columns = [{"label": col, "value": col} for col in df.columns]
    numeric_columns = [{"label": col, "value": col} for col in df.select_dtypes(include="number").columns]

    return html.Div(
        style={"height": "calc(100vh - 56px)", "overflow": "hidden", "display": "flex", "flexDirection": "column"},
        children=[
            _page_header(df),
            html.Div(
                style={"flex": "1", "display": "flex", "overflow": "hidden", "minHeight": 0},
                children=[
                    _left_sidebar(columns, numeric_columns),
                    _right_panel(),
                ],
            ),
            dcc.Store(id="ml-result-store"),
            dcc.Store(id="ml-runs-store", data=[]),
            dcc.Store(id="ml-published-model-store"),
            dcc.Store(id="ml-project-store", storage_type="local"),
            dcc.Store(id="ml-columns-store", data={
                "all": [item["value"] for item in columns],
                "num": [item["value"] for item in numeric_columns],
            }),
            dcc.Store(id="ml-cluster-params-store", data={"algorithm": "kmeans", "n_clusters": 3, "eps": 0.5}),
            tutorial_offcanvas(),
        ],
    )


def _page_header(df: pd.DataFrame) -> html.Div:
    return html.Div(
        style={
            "padding": "10px 20px",
            "borderBottom": "1px solid var(--border)",
            "backgroundColor": "var(--bg-secondary)",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
        },
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "16px"},
                children=[
                    html.Div([
                        html.H5("ML Studio", style={
                            "margin": 0,
                            "fontWeight": "700",
                            "background": "linear-gradient(135deg, #3B82F6, #8B5CF6)",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                        }),
                        html.Span("面向本地表格数据的引导式建模工作台", style={"fontSize": "0.75rem", "color": "var(--text-secondary)"}),
                    ]),
                    dbc.Button([html.I(className="bi bi-book me-2"), "新手指引"], id="btn-ml-tutorial", color="info", outline=True, size="sm"),
                ],
            ),
            html.Div(
                style={"display": "flex", "gap": "8px", "alignItems": "center"},
                children=[
                    _header_pill(f"{len(df):,} rows", "bi-table", ACCENT_COLORS["blue"]),
                    _header_pill(f"{len(df.columns)} columns", "bi-layout-three-columns", ACCENT_COLORS["green"]),
                    dbc.Button([html.I(className="bi bi-folder2-open me-1"), "加载本地实验"], id="btn-ml-load-project", color="secondary", outline=True, size="sm"),
                    dbc.Button([html.I(className="bi bi-cloud-arrow-up me-1"), "同步实验索引"], id="btn-ml-save-project", color="primary", outline=True, size="sm"),
                ],
            ),
        ],
    )


def _header_pill(text: str, icon: str, color: str) -> html.Div:
    return html.Div(
        [html.I(className=f"bi {icon} me-1", style={"color": color}), text],
        style={
            "fontSize": "0.78rem",
            "padding": "4px 10px",
            "borderRadius": "20px",
            "border": f"1px solid {color}40",
            "backgroundColor": f"{color}15",
            "color": "var(--text-primary)",
            "display": "flex",
            "alignItems": "center",
        },
    )


def _journey_card() -> html.Div:
    step_blocks = []
    for step in WORKFLOW_GUIDE_STEPS:
        step_blocks.append(
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "32px 1fr",
                    "gap": "10px",
                    "alignItems": "start",
                    "marginBottom": "12px",
                },
                children=[
                    html.Div(
                        step["id"],
                        style={
                            "width": "32px",
                            "height": "32px",
                            "borderRadius": "50%",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "backgroundColor": f"{ACCENT_COLORS['blue']}18",
                            "color": ACCENT_COLORS["blue"],
                            "fontWeight": "700",
                            "fontSize": "0.82rem",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(step["title"], className="fw-semibold", style={"fontSize": "0.9rem"}),
                            html.Div(step["description"], style={"fontSize": "0.82rem", "color": "var(--text-secondary)", "lineHeight": "1.6"}),
                        ]
                    ),
                ],
            )
        )
    return html.Div(
        style=CARD_STYLE,
        children=[
            html.Div("三步完成一次训练", className="fw-semibold mb-1"),
            html.Div("Phase 1 重点保障分类和回归；聚类与时间序列保留基础入口。", style={"fontSize": "0.82rem", "color": "var(--text-secondary)", "lineHeight": "1.6"}),
            html.Div(step_blocks, className="mt-3"),
            html.Div(
                id="ml-workflow-hint",
                children=workflow_hint_card(
                    "下一步建议",
                    "先在下方选择目标列与特征列，系统会自动判断这是分类还是回归任务。",
                    color="primary",
                ),
            ),
        ],
    )


def _left_sidebar(columns: list[dict[str, str]], numeric_columns: list[dict[str, str]]) -> html.Div:
    return html.Div(
        style={
            "width": "360px",
            "flexShrink": "0",
            "backgroundColor": "var(--bg-secondary)",
            "borderRight": "1px solid var(--border)",
            "overflowY": "auto",
            "padding": "16px",
            "display": "flex",
            "flexDirection": "column",
            "gap": "12px",
        },
        children=[
            _journey_card(),
            _data_card(),
            _feature_card(columns),
            _workflow_card(),
            _algorithm_card(columns, numeric_columns),
            dbc.Button(
                [html.I(className="bi bi-play-circle-fill me-2"), "开始训练"],
                id="btn-ml-train",
                color="primary",
                className="w-100 fw-bold",
                style={"borderRadius": "8px", "padding": "10px", "background": "linear-gradient(135deg, #3B82F6, #8B5CF6)", "border": "none"},
            ),
            html.Div(id="ml-train-status"),
        ],
    )


def _data_card() -> html.Div:
    return html.Div(
        style=CARD_STYLE,
        children=[
            html.H6("数据预处理", className="mb-3"),
            html.Label("缺失值处理", className="form-label small"),
            dcc.Dropdown(
                id="ml-impute-strategy",
                options=[
                    {"label": "均值填补", "value": "mean"},
                    {"label": "中位数填补", "value": "median"},
                    {"label": "众数填补", "value": "most_frequent"},
                    {"label": "删除缺失行", "value": "drop"},
                ],
                value="mean",
                clearable=False,
                className="mb-3",
            ),
            html.Label("数值缩放", className="form-label small"),
            dcc.Dropdown(
                id="ml-scaler",
                options=[
                    {"label": "不缩放", "value": "none"},
                    {"label": "标准化 StandardScaler", "value": "standard"},
                    {"label": "归一化 MinMaxScaler", "value": "minmax"},
                ],
                value="standard",
                clearable=False,
                className="mb-3",
            ),
            html.Label("留出测试集比例", className="form-label small"),
            dcc.Slider(id="ml-test-size", min=0.1, max=0.4, step=0.05, value=0.2, marks={0.1: "10%", 0.2: "20%", 0.3: "30%", 0.4: "40%"}),
        ],
    )


def _feature_card(columns: list[dict[str, str]]) -> html.Div:
    return html.Div(
        style=CARD_STYLE,
        children=[
            html.H6("特征与目标", className="mb-3"),
            html.Label("目标列（Y）", className="form-label small"),
            dcc.Dropdown(id="ml-target-var", options=columns, placeholder="选择你要预测的列", className="mb-2"),
            html.Div(id="ml-task-type-badge", className="mb-3", style={"minHeight": "24px"}),
            html.Label("特征列（X）", className="form-label small"),
            dcc.Dropdown(id="ml-feature-vars", options=columns, multi=True, placeholder="选择用于预测的列，通常 2-8 列更容易解释"),
        ],
    )


def _workflow_card() -> html.Div:
    return html.Div(
        style=CARD_STYLE,
        children=[
            html.H6("训练策略", className="mb-3"),
            html.Label("训练模式", className="form-label small"),
            dcc.Dropdown(id="ml-training-mode", options=TRAINING_MODE_OPTIONS, value="quick", clearable=False, className="mb-3"),
            html.Label("验证方式", className="form-label small"),
            dcc.Dropdown(id="ml-cv-strategy", options=CV_STRATEGY_OPTIONS, value="holdout", clearable=False, className="mb-3"),
            html.Label("交叉验证折数", className="form-label small"),
            dcc.Input(id="ml-cv-folds", type="number", value=5, min=2, className="form-control form-control-sm mb-3"),
            html.Label("随机搜索轮数", className="form-label small"),
            dcc.Input(id="ml-search-iterations", type="number", value=10, min=1, className="form-control form-control-sm mb-3"),
            html.Label("主指标", className="form-label small"),
            dcc.Dropdown(id="ml-primary-metric", options=PRIMARY_METRIC_OPTIONS["classification"], value="f1_weighted", clearable=False),
        ],
    )


def _algorithm_card(columns: list[dict[str, str]], numeric_columns: list[dict[str, str]]) -> html.Div:
    return html.Div(
        style=CARD_STYLE,
        children=[
            html.H6("算法与适用场景", className="mb-3"),
            dbc.Tabs(
                id="ml-algo-tabs",
                active_tab="tab-clf",
                children=[
                    dbc.Tab(label="分类", tab_id="tab-clf"),
                    dbc.Tab(label="回归", tab_id="tab-reg"),
                    dbc.Tab(label="聚类（基础）", tab_id="tab-cluster"),
                    dbc.Tab(label="时间序列（基础）", tab_id="tab-ts"),
                ],
                className="mb-3",
            ),
            html.Div(id="ml-clf-panel", children=[
                dcc.Dropdown(id="ml-classifier", options=CLASSIFIER_OPTIONS, value="rf_clf", clearable=False, className="mb-3"),
                dcc.Input(id="param-n-est", type="number", value=200, min=10, className="form-control form-control-sm mb-2", placeholder="n_estimators"),
                dcc.Input(id="param-max-depth", type="number", value=10, min=1, className="form-control form-control-sm mb-2", placeholder="max_depth"),
                dcc.Input(id="param-c", type="number", value=1.0, step=0.1, className="form-control form-control-sm mb-2", placeholder="C"),
                dcc.Dropdown(id="param-kernel", options=["rbf", "linear"], value="rbf", className="mb-2"),
                dcc.Input(id="param-lr-c", type="number", value=1.0, step=0.1, className="form-control form-control-sm mb-2", placeholder="logistic C"),
                dcc.Input(id="param-k", type="number", value=5, min=1, className="form-control form-control-sm mb-2", placeholder="k neighbors"),
            ]),
            html.Div(id="ml-reg-panel", style={"display": "none"}, children=[
                dcc.Dropdown(id="ml-regressor", options=REGRESSOR_OPTIONS, value="rf_reg", clearable=False, className="mb-3"),
                dcc.Input(id="param-reg-n-est", type="number", value=200, min=10, className="form-control form-control-sm mb-2", placeholder="n_estimators"),
                dcc.Input(id="param-reg-max-depth", type="number", value=10, min=1, className="form-control form-control-sm mb-2", placeholder="max_depth"),
                dcc.Input(id="param-alpha", type="number", value=1.0, step=0.1, className="form-control form-control-sm mb-2", placeholder="alpha"),
                dcc.Input(id="param-svr-c", type="number", value=1.0, step=0.1, className="form-control form-control-sm mb-2", placeholder="SVR C"),
            ]),
            html.Div(id="ml-cluster-panel", style={"display": "none"}, children=[
                dbc.Alert("Phase 1 仍只保留基础聚类入口，暂不纳入完整专业流程。", color="secondary", className="mb-2"),
                dcc.Dropdown(id="ml-cluster-algo", options=CLUSTER_OPTIONS, value="kmeans", clearable=False, className="mb-2"),
                dcc.Input(id="param-n-clusters", type="number", value=3, min=2, className="form-control form-control-sm mb-2"),
                dcc.Input(id="param-eps", type="number", value=0.5, step=0.1, className="form-control form-control-sm mb-2"),
            ]),
            html.Div(id="ml-ts-panel", style={"display": "none"}, children=[
                dbc.Alert("Phase 1 仍只保留基础时间序列入口，暂不做复杂时序建模引导。", color="secondary", className="mb-2"),
                dcc.Dropdown(
                    id="ml-ts-algo",
                    options=[
                        {"label": "线性趋势基线", "value": "ts_linear"},
                        {"label": "随机森林时序基线", "value": "ts_rf"},
                        {"label": "AR-like 基线", "value": "ts_arima"},
                    ],
                    value="ts_linear",
                    clearable=False,
                    className="mb-2",
                ),
                dcc.Dropdown(id="param-ts-timecol", options=columns, placeholder="选择时间列", className="mb-2"),
                dcc.Dropdown(id="param-ts-targetcol", options=numeric_columns, placeholder="选择数值目标列", className="mb-2"),
                dcc.Input(id="param-ts-horizon", type="number", value=10, min=1, className="form-control form-control-sm mb-2"),
                dcc.Slider(id="param-ts-ci", min=50, max=99, step=1, value=95, marks={80: "80", 90: "90", 95: "95", 99: "99"}),
            ]),
            html.Div(id="ml-algo-guidance", className="mt-3", children=algorithm_guide_card(ALGORITHM_GUIDANCE["classification"]["rf_clf"])),
        ],
    )


def _right_panel() -> html.Div:
    return html.Div(
        style={"flex": "1", "overflowY": "auto", "padding": "16px", "display": "flex", "flexDirection": "column", "gap": "12px", "minWidth": 0},
        children=[
            html.Div(id="ml-kpi-row", style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "12px"}),
            dbc.Row([
                dbc.Col(html.Div(id="ml-published-model-panel", style={**CARD_STYLE, "height": "100%"}), width=5),
                dbc.Col(html.Div(id="ml-runs-panel", style={**CARD_STYLE, "height": "100%"}), width=7),
            ], className="g-3"),
            html.Div(
                style={**CARD_STYLE, "flex": "1", "display": "flex", "flexDirection": "column"},
                children=[
                    dbc.Tabs(
                        id="ml-eval-tabs",
                        active_tab="tab-overview",
                        children=[
                            dbc.Tab(label="总览", tab_id="tab-overview"),
                            dbc.Tab(label="特征重要性", tab_id="tab-feature"),
                            dbc.Tab(label="详细报告", tab_id="tab-report"),
                            dbc.Tab(label="预测", tab_id="tab-predict", id="ml-predict-tab"),
                        ],
                    ),
                    html.Div(id="ml-tab-content", style={"marginTop": "16px", "flex": "1", "overflowY": "auto"}, children=[empty_placeholder()]),
                ],
            ),
        ],
    )


def _no_sklearn_view() -> html.Div:
    return html.Div(
        className="d-flex flex-column align-items-center justify-content-center h-100",
        children=[
            html.I(className="bi bi-x-octagon", style={"fontSize": "4rem", "color": "var(--error)", "marginBottom": "20px"}),
            html.H4("缺少必需依赖：scikit-learn"),
            html.P("安装机器学习依赖后才能使用 ML Studio。"),
            html.Code("pip install scikit-learn scipy joblib", style={"backgroundColor": "var(--bg-secondary)", "padding": "10px", "borderRadius": "8px", "fontSize": "1.1rem"}),
        ],
    )


def _no_data_view() -> html.Div:
    return html.Div(
        className="dvs-empty",
        children=[
            html.Div("暂无数据", className="dvs-empty__icon"),
            html.Div("使用 ML Studio 前请先加载数据集", className="dvs-empty__text"),
            html.Div("先去 Data Hub 或首页加载一份数据，再回来建模。", style={"color": "var(--text-muted)", "fontSize": "var(--text-sm)"}),
        ],
    )
