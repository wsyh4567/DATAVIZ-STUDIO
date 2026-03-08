# -*- coding: utf-8 -*-
"""DataViz Studio — 仪表盘页面

提供数据集概览、质量分数、快速统计摘要和操作快捷入口。
"""

from __future__ import annotations

from dash import html, dcc, callback, Input, Output, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from core.data_manager import DataManager
from services.data_workshop.quality_analyzer import QualityAnalyzer
from services.data_workshop.type_detector import TypeDetector


def create_dashboard_page() -> html.Div:
    """创建仪表盘页面"""
    dm = DataManager()
    df = dm.active_df

    if df is None or df.empty:
        return html.Div([
            html.Div(
                className="dvs-empty",
                style={"minHeight": "60vh"},
                children=[
                    html.I(className="bi bi-speedometer2 dvs-empty__icon"),
                    html.Div("仪表盘", className="dvs-empty__text"),
                    html.Div("请先在数据中心加载数据集", style={
                        "color": "var(--text-muted)", "fontSize": "var(--text-sm)"
                    }),
                    dbc.Button([
                        html.I(className="bi bi-folder2-open me-2"),
                        "前往数据中心"
                    ], href="/data", color="primary", className="mt-3"),
                ],
            )
        ])

    # 数据分析
    qa = QualityAnalyzer()
    analysis = qa.analyze_dataframe(df)
    ov = analysis['overview']

    td = TypeDetector()
    mismatches = td.get_mismatched_columns(df)

    # 数值列统计
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    return dbc.Container([
        # 个性化欢迎头（Monarch 风格）
        dbc.Row([
            dbc.Col([
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "marginBottom": "16px",
                    },
                    children=[
                        html.Div([
                            html.H2(
                                "工作台概览",
                                className="mb-1 fade-in",
                                style={"fontWeight": "700", "fontSize": "1.75rem", "color": "#1A202C"}
                            ),
                            html.P(
                                [
                                    html.I(className="bi bi-database me-2", style={"color": "#FF6B35"}),
                                    f"分析集: ",
                                    html.Strong(dm.active_name or '未命名', style={"color": "#FF6B35"}),
                                    f" · 记录数 {ov['rows']:,} 行 × 特征 {ov['cols']} 列",
                                ],
                                className="fade-in mb-0",
                                style={"color": "#718096", "fontSize": "0.95rem"}
                            )
                        ]),
                        # 数据质量 Badge
                        html.Div(
                            style={
                                "display": "flex", "alignItems": "center", "gap": "16px",
                                "background": "var(--bg-secondary)", "padding": "12px 24px",
                                "borderRadius": "16px", "boxShadow": "var(--shadow-sm)"
                            },
                            children=[
                                html.Div(
                                    [
                                        html.Div(
                                            f"{ov['quality_score']}",
                                            style={"fontSize": "2.4rem", "fontWeight": "800", "lineHeight": "1",
                                                   "color": "#38A169" if ov['quality_score'] >= 80 else "#DD6B20" if ov['quality_score'] >= 60 else "#E53E3E"}
                                        ),
                                        html.Div("数据健康度", style={"fontSize": "0.8rem", "color": "#718096", "marginTop": "4px", "fontWeight": "600"}),
                                    ],
                                    style={"textAlign": "center"},
                                ),
                            ]
                        ),
                    ]
                ),
            ]),
        ], className="mb-4"),

        # ══ 分区一：核心指标矩阵 ══
        dbc.Row([
            _metric_card("总观测值 (行)", f"{ov['rows']:,}", "bi-list-ol", "#3182CE"),
            _metric_card("特征数量 (列)", str(ov['cols']), "bi-layout-three-columns", "#805AD5"),
            _metric_card("缺失分布占比", f"{ov['missing_pct']}%", "bi-exclamation-circle",
                        "#DD6B20" if ov['missing_pct'] > 10 else "#38A169"),
            _metric_card("重复记录行数", f"{ov['duplicate_rows']:,}", "bi-files",
                        "#DD6B20" if ov['duplicate_rows'] > 0 else "#38A169"),
            _metric_card("综合数据评分", f"{ov['quality_score']}/100", "bi-trophy",
                        "#38A169" if ov['quality_score'] >= 80 else "#DD6B20" if ov['quality_score'] >= 60 else "#E53E3E"),
            _metric_card("内存预估占用", f"{ov['memory_mb']} MB", "bi-memory", "#718096"),
        ], className="g-3 mb-3 stagger-container"),

        # ══ 分区二：数据形态与结构 ══
        dbc.Row([
            # 缺失值长条图 (占据更大的主流视觉)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.Div([
                            html.Span("列缺失概貌 (Top 缺失)", style={"fontWeight": "600", "fontSize": "0.95rem"}),
                        ])
                    ),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=_missing_bar(df),
                            config={"displayModeBar": False},
                            style={"height": "280px"}
                        )
                    ], style={"padding": "10px"})
                ], className="card-hover", style={"height": "100%", "backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=7, className="stagger-item"),

            # 数据类型环形图
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.Span("字段类型占比", style={"fontWeight": "600", "fontSize": "0.95rem"}),
                    ),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=_dtype_pie(df),
                            config={"displayModeBar": False},
                            style={"height": "280px"}
                        )
                    ], style={"padding": "10px"})
                ], className="card-hover", style={"height": "100%", "backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=5, className="stagger-item"),
        ], className="g-3 mb-3 stagger-container"),

        # ══ 分区三：质量与异常洞察 ══
        dbc.Row([
            # 质量问题与建议 (并排显示)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("已发现的质量问题", style={"fontWeight": "bold", "fontSize": "0.95rem"}),
                        dbc.Badge(str(len(analysis['issues'])), color="warning", className="ms-2")
                    ]),
                    dbc.CardBody([
                        _issues_list(analysis['issues'], analysis['recommendations'])
                    ], style={"maxHeight": "300px", "overflowY": "auto", "padding": "12px"})
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)", "height": "100%"})
            ], width=6, className="stagger-item"),

            # 类型转换建议
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("潜在类型推断", style={"fontWeight": "bold", "fontSize": "0.95rem"}),
                        dbc.Badge(str(len(mismatches)), color="info", className="ms-2")
                    ]),
                    dbc.CardBody([
                        _type_suggestions(mismatches) if mismatches else
                        html.Div([
                            html.I(className="bi bi-check-circle text-success", style={"fontSize": "2.5rem"}),
                            html.P("所有列类型匹配完美", className="text-muted mt-2 font-weight-bold")
                        ], className="d-flex flex-column align-items-center justify-content-center h-100 py-4")
                    ], style={"maxHeight": "300px", "overflowY": "auto", "padding": "12px"})
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)", "height": "100%"})
            ], width=6, className="stagger-item"),
        ], className="g-3 mb-3 stagger-container"),

        # ══ 分区四：统计与相关性深度挖掘 ══
        # 统计摘要表格独立成宽屏卡片
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.Span("数值特征分布摘要", style={"fontWeight": "bold", "fontSize": "0.95rem"})),
                    dbc.CardBody([
                        _numeric_summary_table(df) if numeric_cols else
                        html.P("无有效数值列可供统计", className="text-muted text-center py-3")
                    ], style={"maxHeight": "250px", "overflowY": "auto", "padding": "4px"})
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=12, className="stagger-item"),
        ], className="g-3 mb-4 stagger-container"),

        # 直方图分布扫描
        _auto_distribution_charts(df, numeric_cols, cat_cols),
        
        # 相关性热力
        *(_correlation_heatmap_section(df, numeric_cols)),

    ], fluid=True, className="py-4 px-4")
def _section_header(icon: str, title: str, color: str) -> dbc.Row:
    """分区标题行，带彩色图标和底部分割线。"""
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Div(
                    html.I(className=f"bi {icon}", style={"color": color, "fontSize": "0.9rem"}),
                    style={
                        "width": "28px", "height": "28px", "borderRadius": "7px",
                        "background": f"rgba(0,0,0,0.05)",
                        "display": "inline-flex", "alignItems": "center",
                        "justifyContent": "center", "marginRight": "8px",
                        "border": f"1px solid {color}33",
                    }
                ),
                html.Span(title, style={
                    "fontWeight": "700", "fontSize": "0.8rem",
                    "color": color, "textTransform": "uppercase",
                    "letterSpacing": "0.06em",
                }),
            ], style={"display": "flex", "alignItems": "center",
                      "borderBottom": f"2px solid {color}20",
                      "paddingBottom": "8px"}),
        ])
    ], className="mb-3 mt-1")


def _hex_to_rgba(hex_color: str) -> str:
    """Convert hex color to r,g,b string for rgba() usage."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


def _metric_card(label: str, value: str, icon: str, color: str) -> dbc.Col:
    """更紧凑的数据指标卡片，具有大厂风范"""
    return dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Div(
                        html.I(className=f"bi {icon}", style={"fontSize": "1.1rem", "color": color}),
                        style={
                            "width": "32px", "height": "32px",
                            "borderRadius": "8px",
                            "background": f"rgba({_hex_to_rgba(color)}, 0.15)",
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "flexShrink": "0",
                        }
                    ),
                    html.Div([
                        html.Div(value, style={"fontSize": "1.2rem", "fontWeight": "700", "color": "var(--text-primary)", "lineHeight": "1.1"}),
                        html.Div(label, style={"fontSize": "0.7rem", "color": "var(--text-secondary)", "marginTop": "2px"}),
                    ]),
                ], className="d-flex align-items-center gap-2")
            ], style={"padding": "10px 12px"})
        ], className="card-hover stagger-item", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)", "borderRadius": "10px"})
    ], width=2)


def _dtype_pie(df: pd.DataFrame):
    type_counts = df.dtypes.astype(str).value_counts()
    fig = px.pie(
        names=type_counts.index,
        values=type_counts.values,
        hole=0.4,
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(size=11),
        showlegend=True,
        legend=dict(font=dict(size=10)),
    )
    return fig


def _missing_bar(df: pd.DataFrame):
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=True)

    if missing.empty:
        fig = go.Figure()
        fig.add_annotation(text="无缺失值 ✓", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#22c55e"))
    else:
        fig = px.bar(
            x=missing.values,
            y=missing.index,
            orientation='h',
            labels={'x': '缺失数', 'y': '列名'},
        )

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=20),
        font=dict(size=11),
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
            ], className="mb-1", style={"fontSize": "0.85rem"})
        )

    if recommendations:
        items.append(html.Hr(className="my-2"))
        items.append(html.Strong("建议:", style={"fontSize": "0.85rem"}))
        for rec in recommendations[:5]:
            items.append(
                html.Li([
                    html.Span("💡", className="me-2"),
                    rec
                ], className="mb-1", style={"fontSize": "0.85rem"})
            )

    if not items:
        return html.P("✅ 数据质量良好", className="text-muted text-center")

    return html.Ul(items, style={"listStyle": "none", "paddingLeft": "0"})


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
                        style={"fontSize": "0.75rem", "color": "var(--text-muted)"}
                    ),
                ]),
            ], style={"fontSize": "0.85rem"})
        )
    return dbc.ListGroup(items, flush=True)


def _auto_distribution_charts(df, numeric_cols, cat_cols):
    """自动生成数据分布速览图"""
    charts = []

    # 数值列直方图 (Top-3)
    for col in numeric_cols[:3]:
        clean = df[col].dropna()
        if len(clean) == 0:
            continue
        fig = px.histogram(
            x=clean, nbins=min(30, max(10, int(len(clean) ** 0.5))),
            color_discrete_sequence=["#6366F1"],
        )
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=5, b=25),
            height=180,
            font=dict(size=9),
            showlegend=False,
            xaxis=dict(title=None),
            yaxis=dict(title=None),
        )
        charts.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(f"🔢 {col}", style={"fontWeight": "bold", "fontSize": "0.8rem",
                                                         "padding": "6px 10px"}),
                    dbc.CardBody([
                        dcc.Graph(figure=fig, config={"displayModeBar": False})
                    ], style={"padding": "4px"})
                ], className="card-hover",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=4, className="stagger-item")
        )

    # 分类列柱状图 (Top-3)
    for col in cat_cols[:3]:
        freq = df[col].value_counts().head(6)
        if len(freq) == 0:
            continue
        fig = px.bar(
            x=freq.values, y=freq.index, orientation="h",
            color_discrete_sequence=["#8B5CF6"],
        )
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=5, b=25),
            height=180,
            font=dict(size=9),
            showlegend=False,
            xaxis=dict(title=None),
            yaxis=dict(title=None, autorange="reversed"),
        )
        charts.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(f"🏷️ {col}", style={"fontWeight": "bold", "fontSize": "0.8rem",
                                                          "padding": "6px 10px"}),
                    dbc.CardBody([
                        dcc.Graph(figure=fig, config={"displayModeBar": False})
                    ], style={"padding": "4px"})
                ], className="card-hover",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=4, className="stagger-item")
        )

    if not charts:
        return html.Div()

    return dbc.Row(charts, className="mb-4 stagger-container")


def _correlation_heatmap_section(df, numeric_cols):
    """相关性热力图区域"""
    if len(numeric_cols) < 2:
        return []

    corr = df[numeric_cols].corr().round(2)
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        aspect="auto",
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        height=max(280, len(numeric_cols) * 35),
        font=dict(size=10),
    )

    return [
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("相关性热力图", style={"fontWeight": "bold"}),
                    dbc.CardBody([
                        dcc.Graph(figure=fig, config={"displayModeBar": False})
                    ])
                ], className="card-hover",
                   style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=12, className="stagger-item"),
        ], className="mb-4 stagger-container"),
    ]
