# -*- coding: utf-8 -*-
"""DataViz Studio — 数据画布页（一体化版）

AG Grid 高性能数据表格 + 数据概览 KPI 卡片 + 数据质量分析 + 分布图 + 相关性热力图 + 数据导出。
（原仪表盘内容已合并至此页面）
"""

from __future__ import annotations
import io

from dash import html, dcc, Input, Output, State, callback, no_update, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from core.data_manager import DataManager
from components.data_table import create_data_table
from utils.helpers import format_number


# ── 输入验证 ──────────────────────────────────────────────

def validate_n_value(n_value):
    """验证N值输入是否为有效的正整数。"""
    if n_value is None or n_value == "":
        return False, None, "请输入行数"
    try:
        n = int(n_value)
        if n <= 0:
            return False, None, "行数必须大于0"
        if n != float(n_value):
            return False, None, "行数必须是整数"
        return True, n, None
    except (ValueError, TypeError):
        return False, None, "请输入有效的数字"


# ── 颜色工具 ──────────────────────────────────────────────

def _hex_to_rgba(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


# ── KPI 卡片图标映射 ──────────────────────────────────────

_KPI_CONFIG = [
    {
        "key": "rows",
        "label": "总行数",
        "sub_key": "rows_sub",
        "icon": "bi-table",
        "color": "#3B82F6",
    },
    {
        "key": "cols",
        "label": "总列数",
        "sub_key": "cols_sub",
        "icon": "bi-layout-three-columns",
        "color": "#8B5CF6",
    },
    {
        "key": "missing",
        "label": "缺失值",
        "sub_key": "missing_sub",
        "icon": "bi-exclamation-circle",
        "color": "#F59E0B",
    },
    {
        "key": "dup",
        "label": "重复行",
        "sub_key": "dup_sub",
        "icon": "bi-files",
        "color": "#EF4444",
    },
    {
        "key": "memory",
        "label": "内存占用",
        "sub_key": "memory_sub",
        "icon": "bi-cpu",
        "color": "#6B7280",
    },
    {
        "key": "quality",
        "label": "数据健康度",
        "sub_key": "quality_sub",
        "icon": "bi-shield-check",
        "color": "#10B981",
    },
]


# ── 页面布局 ──────────────────────────────────────────────

def create_data_canvas_page() -> html.Div:
    """返回数据画布页面布局。"""
    return html.Div(
        children=[
            html.H2("数据画布", className="dvs-page-title"),

            # ── KPI 卡片行（带图标）
            html.Div(id="canvas-stats-row", className="dvs-stats-row stagger-container"),

            # ── 数据预览控制区
            html.Div(
                className="dvs-preview-control",
                style={"marginBottom": "var(--sp-3)"},
                role="region",
                **{"aria-label": "数据预览控制"},
                children=[
                    html.Div(
                        className="dvs-preview-control__header",
                        children=[
                            html.Span("数据预览", className="dvs-section-header__title"),
                            html.Div(
                                className="dvs-preview-control__n-input",
                                children=[
                                    html.Label("显示行数：", htmlFor="preview-n-value",
                                               style={"marginRight": "var(--sp-2)", "color": "var(--text-secondary)"}),
                                    dcc.Input(
                                        id="preview-n-value", type="number", value=10, min=1, step=1,
                                        className="dvs-input dvs-input--sm", style={"width": "80px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="dvs-preview-control__buttons",
                        style={"display": "flex", "gap": "var(--sp-2)", "marginTop": "var(--sp-2)"},
                        role="group",
                        **{"aria-label": "数据预览模式选择"},
                        children=[
                            html.Button("前 N 行", id="btn-view-head",
                                        className="dvs-btn dvs-btn--sm dvs-btn--primary btn-hover",
                                        **{"aria-label": "显示前N行数据"}),
                            html.Button("中间 N 行", id="btn-view-middle",
                                        className="dvs-btn dvs-btn--sm btn-hover",
                                        **{"aria-label": "显示中间N行数据"}),
                            html.Button("后 N 行", id="btn-view-tail",
                                        className="dvs-btn dvs-btn--sm btn-hover",
                                        **{"aria-label": "显示后N行数据"}),
                            html.Button("全部数据", id="btn-view-all",
                                        className="dvs-btn dvs-btn--sm btn-hover",
                                        **{"aria-label": "显示全部数据"}),
                        ],
                    ),
                    html.Div(id="preview-warning", className="dvs-preview-control__warning",
                             style={"marginTop": "var(--sp-2)"}, role="alert", **{"aria-live": "polite"}),
                ],
            ),

            # ── AG Grid 表格
            html.Div(id="canvas-table-container"),

            # ── 数据导出按钮行
            html.Div(
                className="dvs-preview-control",
                style={"marginTop": "var(--sp-3)", "display": "flex", "gap": "var(--sp-2)", "alignItems": "center"},
                children=[
                    html.Span("导出数据：", style={"color": "var(--text-secondary)", "marginRight": "var(--sp-2)"}),
                    html.Button("CSV", id="btn-export-csv", className="dvs-btn dvs-btn--sm btn-hover"),
                    html.Button("Excel", id="btn-export-excel", className="dvs-btn dvs-btn--sm btn-hover"),
                    html.Button("JSON", id="btn-export-json", className="dvs-btn dvs-btn--sm btn-hover"),
                    html.Span("│", style={"color": "var(--border)", "margin": "0 var(--sp-2)"}),
                    html.Button("📄 导出分析报告", id="btn-export-report",
                                className="dvs-btn dvs-btn--sm dvs-btn--primary btn-hover"),
                ],
            ),
            dcc.Download(id="download-data-file"),
            dcc.Download(id="download-report-file"),

            # ═══════════════════════════════════════════════════
            # ── 数据洞察分析区（原仪表盘内容）
            # ═══════════════════════════════════════════════════
            html.Div(id="canvas-insight-section"),
        ]
    )


# ═══════════════════════════════════════════════════════════
# ── Callbacks ───────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════

@callback(
    Output("canvas-stats-row", "children"),
    Output("canvas-table-container", "children"),
    Output("preview-warning", "children"),
    Output("canvas-insight-section", "children"),
    Input("app-store", "data"),
    Input("btn-view-head", "n_clicks"),
    Input("btn-view-middle", "n_clicks"),
    Input("btn-view-tail", "n_clicks"),
    Input("btn-view-all", "n_clicks"),
    State("preview-n-value", "value"),
    State("canvas-table-container", "children"),
)
def update_canvas(store_data, n_head, n_middle, n_tail, n_all, n_value, current_table):
    """当活跃数据集变化或预览模式改变时更新表格、KPI 卡片和洞察图表。"""
    warning_msg = None

    try:
        dm = DataManager()
        meta = dm.get_meta()
        df = dm.active_df

        if df is None or meta is None:
            empty = html.Div(
                className="dvs-empty",
                children=[
                    html.Div("📭", className="dvs-empty__icon"),
                    html.Div("尚未加载数据", className="dvs-empty__text"),
                    html.Div("前往主页或数据中心加载数据集",
                             style={"color": "var(--text-muted)", "fontSize": "var(--text-sm)"}),
                ],
            )
            return [], empty, None, []
    except Exception as e:
        error = html.Div(
            className="dvs-empty",
            children=[
                html.Div("⚠️", className="dvs-empty__icon"),
                html.Div("数据加载出错", className="dvs-empty__text"),
                html.Div(f"错误信息：{str(e)}", style={"color": "var(--error)", "fontSize": "var(--text-sm)"}),
            ],
        )
        return [], error, None, []

    # ── 计算 KPI 数据 ──────────────────────────────────────
    missing_total = int(df.isnull().sum().sum())
    missing_pct = (missing_total / (meta.rows * meta.cols) * 100) if meta.rows * meta.cols > 0 else 0
    dup_count = int(df.duplicated().sum())
    dup_pct = (dup_count / meta.rows * 100) if meta.rows > 0 else 0

    # 数据质量分数（简化计算）
    quality_score = max(0, 100 - int(missing_pct * 0.6) - min(20, int(dup_pct * 0.4)))
    quality_color = "#10B981" if quality_score >= 80 else "#F59E0B" if quality_score >= 60 else "#EF4444"

    # ── 带图标的 KPI 卡片 ──────────────────────────────────
    stats_cards = [
        _icon_stat_card("总行数", format_number(meta.rows), f"{meta.rows:,} 条记录",
                        "bi-table", "#3B82F6"),
        _icon_stat_card("总列数", str(meta.cols), f"{meta.cols} 个特征字段",
                        "bi-layout-three-columns", "#8B5CF6"),
        _icon_stat_card("缺失值", format_number(missing_total), f"占比 {missing_pct:.1f}%",
                        "bi-exclamation-circle",
                        "#F59E0B" if missing_total > 0 else "#10B981"),
        _icon_stat_card("重复行", format_number(dup_count), f"占比 {dup_pct:.1f}%",
                        "bi-files",
                        "#EF4444" if dup_count > 0 else "#10B981"),
        _icon_stat_card("内存占用", f"{meta.memory_mb:.1f} MB", "当前数据集",
                        "bi-cpu", "#6B7280"),
        _icon_stat_card("数据健康度", f"{quality_score}/100", "综合质量评分",
                        "bi-shield-check", quality_color),
    ]

    # ── 表格预览 ──────────────────────────────────────────
    view_mode = "head"
    if ctx.triggered_id == "btn-view-middle":
        view_mode = "middle"
    elif ctx.triggered_id == "btn-view-tail":
        view_mode = "tail"
    elif ctx.triggered_id == "btn-view-all":
        view_mode = "all"
    elif ctx.triggered_id == "btn-view-head":
        view_mode = "head"

    n = 10
    if view_mode != "all":
        is_valid, validated_n, error_msg = validate_n_value(n_value)
        if not is_valid:
            warning_msg = html.Div(
                className="dvs-alert dvs-alert--warning",
                children=[
                    html.Span("⚠️ ", style={"marginRight": "var(--sp-2)"}),
                    html.Span(error_msg or "无效的行数输入"),
                ],
            )
            n = 10
        else:
            n = validated_n
            if n > meta.rows:
                warning_msg = html.Div(
                    className="dvs-alert dvs-alert--info",
                    children=[
                        html.Span("ℹ️ ", style={"marginRight": "var(--sp-2)"}),
                        html.Span(f"请求的行数 ({n:,}) 超过总行数 ({meta.rows:,})，将显示所有可用数据"),
                    ],
                )

    table = create_data_table(df, view_mode=view_mode, n_rows=n)

    # ── 洞察分析区（仪表盘内容）──────────────────────────
    insight_section = _build_insight_section(df)

    return stats_cards, table, warning_msg, insight_section


# ── KPI 卡片（带图标）────────────────────────────────────

def _icon_stat_card(label: str, value: str, sub: str, icon: str, color: str) -> html.Div:
    """带 Bootstrap Icon 的商业风格 KPI 卡片。"""
    return html.Div(
        className="dvs-stat-card card-hover stagger-item",
        style={
            "borderLeft": f"3px solid {color}",
            "position": "relative",
            "overflow": "hidden",
        },
        children=[
            # 背景装饰
            html.Div(style={
                "position": "absolute", "right": "-8px", "top": "-8px",
                "width": "60px", "height": "60px", "borderRadius": "50%",
                "background": f"radial-gradient(circle, {color}25 0%, transparent 70%)",
                "pointerEvents": "none",
            }),
            # 图标
            html.Div([
                html.I(className=f"bi {icon}", style={"fontSize": "1.1rem", "color": color}),
            ], style={
                "width": "34px", "height": "34px", "borderRadius": "8px",
                "background": f"rgba({_hex_to_rgba(color)}, 0.12)",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "marginBottom": "8px",
            }),
            html.Span(label, className="dvs-stat-card__label"),
            html.Span(value, className="dvs-stat-card__value", style={"color": color}),
            html.Span(sub, className="dvs-stat-card__sub"),
        ],
    )


# ── 洞察分析区构建（原仪表盘逻辑）───────────────────────────

def _build_insight_section(df: pd.DataFrame) -> list:
    """构建仪表盘样式的数据洞察分析区块，嵌入数据画布底部。"""
    try:
        from services.data_workshop.quality_analyzer import QualityAnalyzer
        from services.data_workshop.type_detector import TypeDetector

        qa = QualityAnalyzer()
        analysis = qa.analyze_dataframe(df)
        ov = analysis['overview']

        td = TypeDetector()
        mismatches = td.get_mismatched_columns(df)
    except Exception:
        ov = {}
        analysis = {"issues": [], "recommendations": []}
        mismatches = []

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    return [
        # 分隔线 + 区块标题
        html.Hr(style={"borderColor": "var(--border)", "margin": "24px 0 20px 0"}),
        html.Div(
            style={"display": "flex", "alignItems": "center", "marginBottom": "16px", "gap": "10px"},
            children=[
                html.Div(
                    html.I(className="bi bi-bar-chart-line-fill",
                           style={"color": "#3B82F6", "fontSize": "1rem"}),
                    style={
                        "width": "32px", "height": "32px", "borderRadius": "8px",
                        "background": "rgba(59,130,246,0.12)",
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                    }
                ),
                html.H5("数据洞察分析", style={
                    "margin": 0, "fontWeight": "700", "fontSize": "1rem",
                    "color": "var(--text-primary)",
                }),
                html.Span("· 基于当前数据集自动生成",
                          style={"fontSize": "0.78rem", "color": "var(--text-secondary)"}),
            ]
        ),

        # ══ 分区一：缺失值 + 字段类型占比 ══
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.Div([
                            html.I(className="bi bi-bar-chart-steps me-2",
                                   style={"color": "#F59E0B"}),
                            html.Span("列缺失概貌", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                        ])
                    ),
                    dbc.CardBody([
                        dcc.Graph(figure=_missing_bar(df), config={"displayModeBar": False},
                                  style={"height": "240px"})
                    ], style={"padding": "8px"})
                ], className="card-hover h-100",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)",
                          "borderRadius": "10px"})
            ], width=7, className="stagger-item"),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.Div([
                            html.I(className="bi bi-pie-chart-fill me-2",
                                   style={"color": "#8B5CF6"}),
                            html.Span("字段类型占比", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                        ])
                    ),
                    dbc.CardBody([
                        dcc.Graph(figure=_dtype_pie(df), config={"displayModeBar": False},
                                  style={"height": "240px"})
                    ], style={"padding": "8px"})
                ], className="card-hover h-100",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)",
                          "borderRadius": "10px"})
            ], width=5, className="stagger-item"),
        ], className="g-3 mb-3 stagger-container"),

        # ══ 分区二：质量问题 + 类型推断 ══
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-bug me-2", style={"color": "#EF4444"}),
                        html.Span("已发现的质量问题", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                        dbc.Badge(str(len(analysis.get('issues', []))), color="danger", className="ms-2"),
                    ]),
                    dbc.CardBody([
                        _issues_list(analysis.get('issues', []), analysis.get('recommendations', []))
                    ], style={"maxHeight": "260px", "overflowY": "auto", "padding": "12px"})
                ], className="card-hover h-100",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)",
                          "borderRadius": "10px"})
            ], width=6, className="stagger-item"),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-arrow-left-right me-2", style={"color": "#06B6D4"}),
                        html.Span("潜在类型推断", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                        dbc.Badge(str(len(mismatches)), color="info", className="ms-2"),
                    ]),
                    dbc.CardBody([
                        _type_suggestions(mismatches) if mismatches else
                        html.Div([
                            html.I(className="bi bi-check-circle-fill text-success",
                                   style={"fontSize": "2rem", "marginBottom": "8px"}),
                            html.P("所有列类型匹配完美", className="text-muted mb-0",
                                   style={"fontSize": "0.85rem"}),
                        ], className="d-flex flex-column align-items-center justify-content-center h-100 py-4")
                    ], style={"maxHeight": "260px", "overflowY": "auto", "padding": "12px"})
                ], className="card-hover h-100",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)",
                          "borderRadius": "10px"})
            ], width=6, className="stagger-item"),
        ], className="g-3 mb-3 stagger-container"),

        # ══ 分区三：数值特征分布摘要 ══
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-table me-2", style={"color": "#3B82F6"}),
                        html.Span("数值特征分布摘要", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                    ]),
                    dbc.CardBody([
                        _numeric_summary_table(df) if numeric_cols else
                        html.P("无有效数值列可供统计", className="text-muted text-center py-3",
                               style={"fontSize": "0.85rem"})
                    ], style={"maxHeight": "220px", "overflowY": "auto", "padding": "8px"})
                ], className="card-hover",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)",
                          "borderRadius": "10px"})
            ], width=12, className="stagger-item"),
        ], className="g-3 mb-3 stagger-container"),

        # ══ 分区四：自动分布速览图 ══
        _auto_distribution_charts(df, numeric_cols, cat_cols),

        # ══ 分区五：相关性热力图 ══
        *(_correlation_heatmap_section(df, numeric_cols)),

        # 底部留白
        html.Div(style={"height": "32px"}),
    ]


# ──────────────────────────────────────────────────────────
# ── 图表和辅助函数（原仪表盘 helpers）──────────────────────
# ──────────────────────────────────────────────────────────

def _dtype_pie(df: pd.DataFrame):
    type_counts = df.dtypes.astype(str).value_counts()
    colors = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#06B6D4"]
    fig = px.pie(
        names=type_counts.index, values=type_counts.values,
        hole=0.45, color_discrete_sequence=colors,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), font=dict(size=11),
        showlegend=True, legend=dict(font=dict(size=10)),
    )
    return fig


def _missing_bar(df: pd.DataFrame):
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=True)

    if missing.empty:
        fig = go.Figure()
        fig.add_annotation(text="✅ 无缺失值", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=16, color="#10B981"))
    else:
        fig = px.bar(
            x=missing.values, y=missing.index, orientation='h',
            labels={'x': '缺失数', 'y': '列名'},
            color=missing.values,
            color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"],
        )
        fig.update_coloraxes(showscale=False)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=10, b=20), font=dict(size=11),
        xaxis=dict(gridcolor="var(--border)"),
        yaxis=dict(gridcolor="var(--border)"),
    )
    return fig


def _numeric_summary_table(df: pd.DataFrame):
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return html.P("无数值列", className="text-muted")

    desc = numeric_df.describe().T
    desc = desc[['count', 'mean', 'std', 'min', '50%', 'max']].round(2)
    desc.columns = ['有效值', '均值', '标准差', '最小', '中位数', '最大']

    return dbc.Table.from_dataframe(
        desc.reset_index().rename(columns={'index': '列名'}),
        striped=True, bordered=True, hover=True, size='sm',
        style={"fontSize": "0.8rem"}
    )


def _issues_list(issues, recommendations):
    items = []
    severity_icons = {'high': '🔴', 'medium': '🟡', 'low': '🔵', 'info': 'ℹ️'}

    for issue in issues[:10]:
        sev = issue.get('severity', 'info')
        items.append(
            html.Li([
                html.Span(severity_icons.get(sev, 'ℹ️'), className="me-2"),
                issue['message']
            ], className="mb-1", style={"fontSize": "0.83rem"})
        )

    if recommendations:
        items.append(html.Hr(className="my-2"))
        items.append(html.Strong("建议:", style={"fontSize": "0.83rem"}))
        for rec in recommendations[:5]:
            items.append(
                html.Li([html.Span("💡", className="me-2"), rec],
                        className="mb-1", style={"fontSize": "0.83rem"})
            )

    if not items:
        return html.P("✅ 数据质量良好", className="text-muted text-center",
                      style={"fontSize": "0.85rem"})

    return html.Ul(items, style={"listStyle": "none", "paddingLeft": "0", "margin": 0})


def _type_suggestions(mismatches):
    items = []
    for m in mismatches[:8]:
        sugg = m.get('suggestion', {}) or {}
        items.append(
            dbc.ListGroupItem([
                html.Div([
                    html.Strong(m['column'], className="me-2"),
                    dbc.Badge(m['current_type'], color="secondary", className="me-1"),
                    html.Span("→", className="mx-1"),
                    dbc.Badge(sugg.get('target_type', '?'), color="info"),
                    html.Span(
                        f" (置信度: {m['confidence']:.0%}, 预计失败: {sugg.get('expected_failures', 0)})",
                        style={"fontSize": "0.73rem", "color": "var(--text-muted)"}
                    ),
                ]),
            ], style={"fontSize": "0.83rem"})
        )
    return dbc.ListGroup(items, flush=True)


def _auto_distribution_charts(df, numeric_cols, cat_cols):
    """自动生成数值+分类特征分布速览图"""
    charts = []

    for col in numeric_cols[:3]:
        clean = df[col].dropna()
        if len(clean) == 0:
            continue
        fig = px.histogram(x=clean, nbins=min(30, max(10, int(len(clean) ** 0.5))),
                           color_discrete_sequence=["#6366F1"])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=5, b=25), height=175,
            font=dict(size=9), showlegend=False,
            xaxis=dict(title=None, gridcolor="var(--border)"),
            yaxis=dict(title=None),
        )
        charts.append(dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.I(className="bi bi-hash me-1", style={"color": "#6366F1"}),
                                f" {col}"],
                               style={"fontWeight": "600", "fontSize": "0.78rem", "padding": "6px 10px"}),
                dbc.CardBody([dcc.Graph(figure=fig, config={"displayModeBar": False})],
                             style={"padding": "4px"})
            ], className="card-hover",
               style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)",
                      "borderRadius": "10px"})
        ], width=4, className="stagger-item"))

    for col in cat_cols[:3]:
        freq = df[col].value_counts().head(6)
        if len(freq) == 0:
            continue
        fig = px.bar(x=freq.values, y=freq.index, orientation="h",
                     color_discrete_sequence=["#8B5CF6"])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=5, b=25), height=175,
            font=dict(size=9), showlegend=False,
            xaxis=dict(title=None, gridcolor="var(--border)"),
            yaxis=dict(title=None, autorange="reversed"),
        )
        charts.append(dbc.Col([
            dbc.Card([
                dbc.CardHeader([html.I(className="bi bi-tag me-1", style={"color": "#8B5CF6"}),
                                f" {col}"],
                               style={"fontWeight": "600", "fontSize": "0.78rem", "padding": "6px 10px"}),
                dbc.CardBody([dcc.Graph(figure=fig, config={"displayModeBar": False})],
                             style={"padding": "4px"})
            ], className="card-hover",
               style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)",
                      "borderRadius": "10px"})
        ], width=4, className="stagger-item"))

    if not charts:
        return html.Div()

    return dbc.Row([
        dbc.Col(html.Div([
            html.I(className="bi bi-grid-3x3 me-2", style={"color": "#6366F1"}),
            html.Span("特征分布速览", style={"fontWeight": "600", "fontSize": "0.9rem"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}), width=12),
        *charts,
    ], className="mb-3 stagger-container")


def _correlation_heatmap_section(df, numeric_cols):
    """相关性热力图区域"""
    if len(numeric_cols) < 2:
        return []

    corr = df[numeric_cols].corr().round(2)
    fig = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1, aspect="auto",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        height=max(280, len(numeric_cols) * 35),
        font=dict(size=10),
    )

    return [
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-grid-3x3-gap me-2", style={"color": "#F59E0B"}),
                        html.Span("相关性热力图", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                    ]),
                    dbc.CardBody([dcc.Graph(figure=fig, config={"displayModeBar": False})])
                ], className="card-hover",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)",
                          "borderRadius": "10px"})
            ], width=12, className="stagger-item"),
        ], className="mb-4 stagger-container"),
    ]


# ═══════════════════════════════════════════════════════════
# ── 导出回调 ─────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════

@callback(
    Output("download-data-file", "data"),
    Input("btn-export-csv", "n_clicks"),
    Input("btn-export-excel", "n_clicks"),
    Input("btn-export-json", "n_clicks"),
    prevent_initial_call=True,
)
def export_data(csv_clicks, excel_clicks, json_clicks):
    """将当前活跃数据集导出为 CSV / Excel / JSON。"""
    dm = DataManager()
    df = dm.active_df
    if df is None:
        return no_update

    name = dm.active_name or "data"
    triggered = ctx.triggered_id

    if triggered == "btn-export-csv":
        return dcc.send_data_frame(df.to_csv, f"{name}.csv", index=False)
    elif triggered == "btn-export-excel":
        return dcc.send_data_frame(df.to_excel, f"{name}.xlsx", index=False)
    elif triggered == "btn-export-json":
        return dcc.send_data_frame(df.to_json, f"{name}.json", orient="records", force_ascii=False)
    return no_update


@callback(
    Output("download-report-file", "data"),
    Input("btn-export-report", "n_clicks"),
    prevent_initial_call=True,
)
def export_report(n_clicks):
    """导出 HTML 分析报告。"""
    dm = DataManager()
    df = dm.active_df
    if df is None:
        return no_update

    from services.report_generator import ReportGenerator
    name = dm.active_name or "data"
    html_content = ReportGenerator.generate_html_report(df, name)
    return dict(content=html_content, filename=f"{name}_分析报告.html")
