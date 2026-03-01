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
                    html.Div("📋", className="dvs-empty__icon"),
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
        # 标题
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="bi bi-speedometer2 me-3", style={"color": "var(--accent)"}),
                    "仪表盘"
                ], className="mb-1 fade-in", style={"fontWeight": "600"}),
                html.P(f"当前数据集: {dm.active_name or '未命名'}",
                       className="fade-in",
                       style={"color": "var(--text-muted)", "fontSize": "0.875rem"})
            ]),
        ], className="mb-4"),

        # 顶部指标卡片
        dbc.Row([
            _metric_card("行数", f"{ov['rows']:,}", "bi-list-ol", "primary"),
            _metric_card("列数", str(ov['cols']), "bi-layout-three-columns", "info"),
            _metric_card("缺失率", f"{ov['missing_pct']}%", "bi-exclamation-circle",
                        "warning" if ov['missing_pct'] > 10 else "success"),
            _metric_card("重复行", f"{ov['duplicate_rows']:,}", "bi-files",
                        "warning" if ov['duplicate_rows'] > 0 else "success"),
            _metric_card("质量分数", f"{ov['quality_score']}/100", "bi-trophy",
                        "success" if ov['quality_score'] >= 80 else "warning" if ov['quality_score'] >= 60 else "danger"),
            _metric_card("内存", f"{ov['memory_mb']} MB", "bi-memory", "secondary"),
        ], className="mb-4 stagger-container"),

        # 第二行：数据类型分布 + 缺失值概览
        dbc.Row([
            # 数据类型分布
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("数据类型分布", style={"fontWeight": "bold"}),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=_dtype_pie(df),
                            config={"displayModeBar": False},
                            style={"height": "280px"}
                        )
                    ])
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=4, className="stagger-item"),

            # 缺失值热图
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("各列缺失值", style={"fontWeight": "bold"}),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=_missing_bar(df),
                            config={"displayModeBar": False},
                            style={"height": "280px"}
                        )
                    ])
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=8, className="stagger-item"),
        ], className="mb-4 stagger-container"),

        # 第三行：数值列摘要 + 问题和建议
        dbc.Row([
            # 数值列快速摘要
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("数值列摘要", style={"fontWeight": "bold"}),
                    dbc.CardBody([
                        _numeric_summary_table(df) if numeric_cols else
                        html.P("无数值列", className="text-muted text-center py-3")
                    ], style={"maxHeight": "350px", "overflowY": "auto"})
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=7, className="stagger-item"),

            # 问题 & 建议
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        "质量问题",
                        dbc.Badge(str(len(analysis['issues'])), color="warning", className="ms-2")
                    ], style={"fontWeight": "bold"}),
                    dbc.CardBody([
                        _issues_list(analysis['issues'], analysis['recommendations'])
                    ], style={"maxHeight": "350px", "overflowY": "auto"})
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=5, className="stagger-item"),
        ], className="mb-4 stagger-container"),

        # 第四行：类型不匹配建议 + 快捷操作
        dbc.Row([
            # 类型建议
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        "类型转换建议",
                        dbc.Badge(str(len(mismatches)), color="info", className="ms-2")
                    ], style={"fontWeight": "bold"}),
                    dbc.CardBody([
                        _type_suggestions(mismatches) if mismatches else
                        html.P("所有列类型匹配正确 ✓", className="text-muted text-center py-3")
                    ])
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=6, className="stagger-item"),

            # 快捷导航
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("快捷操作", style={"fontWeight": "bold"}),
                    dbc.CardBody([
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.I(className="bi bi-magic me-2"),
                                "数据清洗"
                            ], href="/workshop", action=True, className="d-flex align-items-center"),
                            dbc.ListGroupItem([
                                html.I(className="bi bi-graph-up me-2"),
                                "创建图表"
                            ], href="/charts", action=True, className="d-flex align-items-center"),
                            dbc.ListGroupItem([
                                html.I(className="bi bi-calculator me-2"),
                                "统计分析"
                            ], href="/stats", action=True, className="d-flex align-items-center"),
                            dbc.ListGroupItem([
                                html.I(className="bi bi-tools me-2"),
                                "高级工具"
                            ], href="/advanced", action=True, className="d-flex align-items-center"),
                        ], flush=True)
                    ])
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=6, className="stagger-item"),
        ], className="stagger-container"),

    ], fluid=True, className="py-4")


# ── 辅助组件 ────────────────────────────────────────────

def _metric_card(label: str, value: str, icon: str, color: str) -> dbc.Col:
    return dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className=f"bi {icon}", style={"fontSize": "1.5rem", "opacity": "0.7"}),
                    html.Div([
                        html.Div(value, style={"fontSize": "1.5rem", "fontWeight": "700"}),
                        html.Div(label, style={"fontSize": "0.75rem", "color": "var(--text-muted)"}),
                    ]),
                ], className="d-flex align-items-center gap-3")
            ], style={"padding": "1rem"})
        ], color=color, outline=True, className="card-hover stagger-item",
            style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
    ], width=2)


def _dtype_pie(df: pd.DataFrame):
    type_counts = df.dtypes.astype(str).value_counts()
    fig = px.pie(
        names=type_counts.index,
        values=type_counts.values,
        hole=0.4,
    )
    fig.update_layout(
        template="plotly_dark",
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
        template="plotly_dark",
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
