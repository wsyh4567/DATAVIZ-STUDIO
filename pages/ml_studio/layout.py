# -*- coding: utf-8 -*-
"""机器学习页面整体布局"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from core.data_manager import DataManager
from .config import HAS_SKLEARN, ACCENT_COLORS, CARD_STYLE, CLASSIFIER_OPTIONS, REGRESSOR_OPTIONS, CLUSTER_OPTIONS
from .components import empty_placeholder, tutorial_offcanvas

def create_ml_studio_page() -> html.Div:
    """创建机器学习工作室页面布局"""
    dm = DataManager()
    df = dm.active_df

    if not HAS_SKLEARN:
        return _no_sklearn_view()

    if df is None or df.empty:
        return _no_data_view()

    columns = [{"label": col, "value": col} for col in df.columns]
    num_cols = [{"label": c, "value": c} for c in df.select_dtypes(include="number").columns]

    return html.Div(
        style={"height": "calc(100vh - 56px)", "overflow": "hidden", "display": "flex", "flexDirection": "column", "padding": "0"},
        children=[
            _page_header(df),
            html.Div(
                style={"flex": "1", "display": "flex", "overflow": "hidden", "minHeight": 0},
                children=[
                    _left_sidebar(columns),
                    _right_panel(),
                ]
            ),
            # 隐藏状态存储
            dcc.Store(id="ml-result-store"),  # 存储训练结果
            dcc.Store(id="ml-project-store", storage_type="local"),  # 存储已保存的项目进度
            dcc.Store(id="ml-columns-store", data={
                "all": [c["value"] for c in columns],
                "num": [c["value"] for c in num_cols],
            }),
            # 聚类专属 Store，修复 display:none 无法读取 State 的问题
            dcc.Store(id="ml-cluster-params-store", data={"algorithm": "kmeans", "n_clusters": 3, "eps": 0.5}),
            tutorial_offcanvas(), # 新手教程抽屉
        ]
    )


def _page_header(df: pd.DataFrame) -> html.Div:
    n_rows, n_cols = df.shape
    return html.Div(
        style={
            "padding": "10px 20px", "borderBottom": "1px solid var(--border)",
            "backgroundColor": "var(--bg-secondary)",
            "display": "flex", "alignItems": "center", "justifyContent": "space-between",
        },
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "16px"},
                children=[
                    html.Div([
                        html.H5("机器学习工作室", style={
                            "margin": 0, "fontWeight": "700",
                            "background": "linear-gradient(135deg, #3B82F6, #8B5CF6)",
                            "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent",
                        }),
                        html.Span("ML Studio · scikit-learn 驱动", style={"fontSize": "0.75rem", "color": "var(--text-secondary)"}),
                    ]),
                    # 教程按钮
                    dbc.Button(
                        [html.I(className="bi bi-book me-2"), "新手指南"],
                        id="btn-ml-tutorial", color="info", outline=True, size="sm",
                        style={"borderRadius": "20px", "fontSize": "0.8rem"}
                    )
                ]
            ),
            html.Div([
                _header_pill(f"{n_rows:,} 行", "bi-table", "#3B82F6"),
                _header_pill(f"{n_cols} 列", "bi-layout-three-columns", "#10B981"),
                # 项目保存与加载按钮
                dbc.Button([html.I(className="bi bi-folder2-open me-1"), "历史项目"], id="btn-ml-load-project", color="secondary", outline=True, size="sm", className="ms-2 px-2 py-0 border-0"),
                dbc.Button([html.I(className="bi bi-cloud-arrow-up me-1"), "保存进度"], id="btn-ml-save-project", color="primary", outline=True, size="sm", className="ms-1 px-2 py-0 border-0"),
            ], style={"display": "flex", "gap": "8px", "alignItems": "center"}),
        ]
    )

def _header_pill(text: str, icon: str, color: str) -> html.Div:
    return html.Div(
        [html.I(className=f"bi {icon} me-1", style={"color": color}), text],
        style={
            "fontSize": "0.78rem", "padding": "4px 10px", "borderRadius": "20px",
            "border": f"1px solid {color}40", "backgroundColor": f"{color}15",
            "color": "var(--text-primary)", "display": "flex", "alignItems": "center",
        }
    )

def _left_sidebar(columns: list) -> html.Div:
    return html.Div(
        style={
            "width": "300px", "flexShrink": "0", "backgroundColor": "var(--bg-secondary)",
            "borderRight": "1px solid var(--border)", "overflowY": "auto", "padding": "16px",
            "display": "flex", "flexDirection": "column", "gap": "12px",
        },
        children=[
            # 数据预处理
            html.Div(style=CARD_STYLE, children=[
                html.Div([
                    html.I(className="bi bi-tools me-2", style={"color": ACCENT_COLORS["blue"]}),
                    html.Span("数据预处理", style={"fontWeight": "600", "fontSize": "0.85rem"}),
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
                html.Label("缺失值处理", style={"fontSize": "0.78rem", "color": "var(--text-secondary)", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="ml-impute-strategy",
                    options=[
                        {"label": "均值填充 (mean)", "value": "mean"},
                        {"label": "中位数填充 (median)", "value": "median"},
                        {"label": "众数填充 (most)", "value": "most_frequent"},
                        {"label": "删除含缺失行", "value": "drop"},
                    ], value="mean", clearable=False, className="mb-3", style={"fontSize": "0.82rem"},
                ),
                html.Label("特征标准化", style={"fontSize": "0.78rem", "color": "var(--text-secondary)", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="ml-scaler",
                    options=[
                        {"label": "无缩放 (None)", "value": "none"},
                        {"label": "标准化 (Z-score)", "value": "standard"},
                        {"label": "归一化 (MinMax)", "value": "minmax"},
                    ], value="standard", clearable=False, className="mb-3", style={"fontSize": "0.82rem"},
                ),
                html.Label("测试集比例", style={"fontSize": "0.78rem", "color": "var(--text-secondary)", "marginBottom": "4px"}),
                dcc.Slider(
                    id="ml-test-size", min=0.1, max=0.4, step=0.05, value=0.2,
                    marks={0.1: "10%", 0.2: "20%", 0.3: "30%", 0.4: "40%"},
                    tooltip={"placement": "bottom", "always_visible": False}, className="mb-1",
                ),
            ]),
            
            # 特征与目标
            html.Div(style=CARD_STYLE, children=[
                html.Div([
                    html.I(className="bi bi-bullseye me-2", style={"color": ACCENT_COLORS["orange"]}),
                    html.Span("特征与目标", style={"fontWeight": "600", "fontSize": "0.85rem"}),
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
                html.Label("目标变量 (Y)", style={"fontSize": "0.78rem", "color": "var(--text-secondary)", "marginBottom": "4px"}),
                dcc.Dropdown(id="ml-target-var", options=columns, placeholder="选择目标列...", className="mb-2", style={"fontSize": "0.82rem"}),
                html.Div(id="ml-task-type-badge", className="mb-3", style={"fontSize": "0.75rem", "minHeight": "24px"}),
                html.Label("特征变量 (X)", style={"fontSize": "0.78rem", "color": "var(--text-secondary)", "marginBottom": "4px"}),
                dcc.Dropdown(id="ml-feature-vars", options=columns, multi=True, placeholder="选择特征列...", style={"fontSize": "0.82rem"}),
            ]),

            # 算法配置
            html.Div(style=CARD_STYLE, children=[
                html.Div([
                    html.I(className="bi bi-cpu me-2", style={"color": ACCENT_COLORS["purple"]}),
                    html.Span("算法配置", style={"fontWeight": "600", "fontSize": "0.85rem"}),
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
                dbc.Tabs(
                    id="ml-algo-tabs", active_tab="tab-clf",
                    children=[
                        dbc.Tab(label="分类", tab_id="tab-clf"),
                        dbc.Tab(label="回归", tab_id="tab-reg"),
                        dbc.Tab(label="聚类", tab_id="tab-cluster"),
                        dbc.Tab(label="时序", tab_id="tab-ts"),
                    ], className="mb-3",
                ),
                html.Div(id="ml-clf-panel", children=[
                    dcc.Dropdown(id="ml-classifier", options=CLASSIFIER_OPTIONS, value="rf_clf", clearable=False, className="mb-3", style={"fontSize": "0.82rem"}),
                    html.Div(id="wrap-param-n-est", style={"display": "none"}, children=[
                        html.Label("树的数量 (n_estimators)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-n-est", type="number", value=100, className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(id="wrap-param-max-depth", style={"display": "none"}, children=[
                        html.Label("最大深度 (max_depth)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-max-depth", type="number", placeholder="无限制", className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(id="wrap-param-c", style={"display": "none"}, children=[
                        html.Label("正则化系数 (C)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-c", type="number", value=1.0, step=0.1, className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(id="wrap-param-kernel", style={"display": "none"}, children=[
                        html.Label("核函数 (Kernel)", style={"fontSize": "0.75rem"}),
                        dcc.Dropdown(id="param-kernel", options=["rbf", "linear", "poly"], value="rbf", className="mb-2", style={"fontSize": "0.8rem"})
                    ]),
                    html.Div(id="wrap-param-lr-c", style={"display": "none"}, children=[
                        html.Label("正则化系数 (C)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-lr-c", type="number", value=1.0, step=0.1, className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(id="wrap-param-k", style={"display": "none"}, children=[
                        html.Label("近邻数 (k)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-k", type="number", value=5, className="form-control form-control-sm mb-2")
                    ]),
                ]),
                html.Div(id="ml-reg-panel", style={"display": "none"}, children=[
                    dcc.Dropdown(id="ml-regressor", options=REGRESSOR_OPTIONS, value="rf_reg", clearable=False, className="mb-3", style={"fontSize": "0.82rem"}),
                    html.Div(id="wrap-param-reg-n-est", style={"display": "none"}, children=[
                        html.Label("树的数量", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-reg-n-est", type="number", value=100, className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(id="wrap-param-reg-max-depth", style={"display": "none"}, children=[
                        html.Label("最大深度", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-reg-max-depth", type="number", placeholder="无限制", className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(id="wrap-param-alpha", style={"display": "none"}, children=[
                        html.Label("正则化强度 (alpha)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-alpha", type="number", value=1.0, step=0.1, className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(id="wrap-param-svr-c", style={"display": "none"}, children=[
                        html.Label("正则化系数 (C)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-svr-c", type="number", value=1.0, step=0.1, className="form-control form-control-sm mb-2")
                    ]),
                ]),
                html.Div(id="ml-cluster-panel", style={"display": "none"}, children=[
                    dcc.Dropdown(id="ml-cluster-algo", options=CLUSTER_OPTIONS, value="kmeans", clearable=False, className="mb-3", style={"fontSize": "0.82rem"}),
                    html.Div(id="wrap-param-n-clusters", style={"display": "none"}, children=[
                        html.Label("簇的数量 (K / n_clusters)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-n-clusters", type="number", value=3, min=2, className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(id="wrap-param-eps", style={"display": "none"}, children=[
                        html.Label("邻域半径 (eps)", style={"fontSize": "0.75rem"}),
                        dcc.Input(id="param-eps", type="number", value=0.5, step=0.1, className="form-control form-control-sm mb-2")
                    ]),
                ]),
                html.Div(id="ml-ts-panel", style={"display": "none"}, children=[
                    dcc.Dropdown(id="ml-ts-algo", options=[
                        {"label": "👑 快速基线回归 (Sklearn)", "value": "ts_linear"},
                        {"label": "🌲 随机森林预测 (Sklearn)", "value": "ts_rf"},
                        {"label": "📈 AR 模型近似 (SARIMAX)", "value": "ts_arima"},
                    ], value="ts_linear", clearable=False, className="mb-3", style={"fontSize": "0.82rem"}),
                    html.Div(children=[
                        html.Label("时间列 (Time Column)", style={"fontSize": "0.75rem", "color": "var(--text-secondary)"}),
                        dcc.Dropdown(id="param-ts-timecol", options=[], placeholder="选择包含日期的列...", className="mb-2", style={"fontSize": "0.82rem"})
                    ]),
                    html.Div(children=[
                        html.Label("预测地平线 (Horizon 步数)", style={"fontSize": "0.75rem", "color": "var(--text-secondary)"}),
                        dcc.Input(id="param-ts-horizon", type="number", value=10, min=1, className="form-control form-control-sm mb-2")
                    ]),
                    html.Div(children=[
                        html.Label("置信区间占比 (%)", style={"fontSize": "0.75rem", "color": "var(--text-secondary)"}),
                        dcc.Slider(id="param-ts-ci", min=50, max=99, step=1, value=95, marks={80:"80", 90:"90", 95:"95", 99:"99"}, tooltip={"placement": "bottom"}),
                    ], className="mt-2 mb-2"),
                ]),
            ]),

            dbc.Button(
                [html.I(className="bi bi-play-circle-fill me-2"), "开始训练模型"],
                id="btn-ml-train", color="primary", className="w-100 fw-bold",
                style={"borderRadius": "8px", "padding": "10px", "marginTop": "4px", "background": "linear-gradient(135deg, #3B82F6, #8B5CF6)", "border": "none", "letterSpacing": "0.05em"},
            ),
            html.Div(id="ml-train-status", className="mt-1"),
        ]
    )

def _right_panel() -> html.Div:
    return html.Div(
        style={"flex": "1", "overflowY": "auto", "padding": "16px", "display": "flex", "flexDirection": "column", "gap": "12px", "minWidth": 0},
        children=[
            html.Div(id="ml-kpi-row", style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "12px"}),
            html.Div(
                style={**CARD_STYLE, "flex": "1", "display": "flex", "flexDirection": "column"},
                children=[
                    dbc.Tabs(
                        id="ml-eval-tabs", active_tab="tab-overview",
                        children=[
                            dbc.Tab(label="📊 综合评估", tab_id="tab-overview"),
                            dbc.Tab(label="🔑 特征重要性", tab_id="tab-feature"),
                            dbc.Tab(label="📄 详细报告", tab_id="tab-report"),
                            dbc.Tab(label="🔮 预测新样本", tab_id="tab-predict", id="ml-predict-tab"),
                        ],
                    ),
                    html.Div(id="ml-tab-content", style={"marginTop": "16px", "flex": "1", "overflowY": "auto"}, children=[empty_placeholder()]),
                ]
            ),
        ]
    )

def _no_sklearn_view() -> html.Div:
    return html.Div(
        className="d-flex flex-column align-items-center justify-content-center h-100",
        children=[
            html.I(className="bi bi-x-octagon", style={"fontSize": "4rem", "color": "var(--error)", "marginBottom": "20px"}),
            html.H4("缺少关键依赖：scikit-learn"),
            html.P("要使用机器学习工作室，请在服务器中安装所需库："),
            html.Code("pip install scikit-learn", style={"backgroundColor": "var(--bg-secondary)", "padding": "10px", "borderRadius": "8px", "fontSize": "1.2rem"})
        ]
    )

def _no_data_view() -> html.Div:
    return html.Div(
        className="dvs-empty",
        children=[
            html.Div("📭", className="dvs-empty__icon"),
            html.Div("尚未加载数据", className="dvs-empty__text"),
            html.Div("请前往欢迎页或数据中心加载数据集，然后再试。", style={"color": "var(--text-muted)", "fontSize": "var(--text-sm)"}),
        ],
    )
