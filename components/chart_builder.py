# -*- coding: utf-8 -*-
"""图表构建器组件 — 图表类型选择和配置

提供图表类型选择器、配置面板和图表预览。
"""

from __future__ import annotations

from typing import Optional, Dict, Any

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go

from services.chart_service import PLOTLY_CHART_TYPES, SEABORN_CHART_TYPES, ChartType


# 图表分类
_CHART_CATEGORIES = {
    "comparison": {"name": "比较", "icon": "bi-bar-chart"},
    "trend": {"name": "趋势", "icon": "bi-graph-up"},
    "distribution": {"name": "分布", "icon": "bi-bar-chart-steps"},
    "relationship": {"name": "关系", "icon": "bi-diagram-3"},
    "composition": {"name": "占比", "icon": "bi-pie-chart"},
}


def create_chart_type_selector() -> html.Div:
    """创建图表类型选择器

    Returns:
        图表类型选择器组件
    """
    # 合并所有图表类型并按类别分组
    all_charts = {}
    all_charts.update(PLOTLY_CHART_TYPES)
    for k, v in SEABORN_CHART_TYPES.items():
        if k not in all_charts:
            all_charts[k] = v

    chart_groups = {}
    for chart_id, info in all_charts.items():
        category = info.get("category", "comparison")
        if category not in chart_groups:
            chart_groups[category] = []
        chart_groups[category].append({"id": chart_id, **info})

    # 创建分类标签页
    tabs = []
    for category, cat_info in _CHART_CATEGORIES.items():
        if category in chart_groups:
            charts = chart_groups[category]
            tab_content = html.Div(
                [
                    _create_chart_type_card(chart)
                    for chart in charts
                ],
                className="chart-type-grid"
            )
            tabs.append(
                dbc.Tab(
                    tab_content,
                    label=cat_info["name"],
                    tab_id=category,
                    className="chart-category-tab"
                )
            )

    return html.Div(
        [
            html.H6("图表类型", className="mb-3"),
            dbc.Tabs(
                tabs,
                id="chart-category-tabs",
                active_tab="comparison",
                className="chart-category-tabs"
            ),
        ]
    )


def _create_chart_type_card(chart_info: dict) -> html.Div:
    """创建图表类型卡片

    Args:
        chart_info: 图表类型信息字典

    Returns:
        图表类型卡片
    """
    chart_id = chart_info.get("id", "")
    icon = chart_info.get("icon", "graph-up")
    name = chart_info.get("name", chart_id)
    description = chart_info.get("description", "")

    return html.Div(
        [
            html.Div(
                [
                    html.I(className=f"bi bi-{icon}", style={"fontSize": "24px"}),
                    html.Div(name, className="chart-type-name mt-2"),
                ],
                className="chart-type-card-inner"
            )
        ],
        id={"type": "chart-type-card", "chart_id": chart_id},
        className="chart-type-card",
        title=description,
        **{"data-chart-id": chart_id}
    )


def create_chart_canvas(figure: Optional[go.Figure] = None) -> html.Div:
    """创建图表画布

    Args:
        figure: Plotly 图表对象

    Returns:
        图表画布组件
    """
    if figure is None:
        # 空状态
        content = html.Div(
            [
                html.I(className="bi bi-graph-up", style={"fontSize": "64px", "color": "#64748B"}),
                html.H5("开始创建图表", className="mt-4 mb-2"),
                html.P("1. 从左侧拖拽字段到下方的字段配置区", className="text-muted"),
                html.P("2. 选择图表类型", className="text-muted"),
                html.P("3. 调整样式配置", className="text-muted"),
            ],
            className="chart-canvas-empty"
        )
    else:
        content = dcc.Graph(
            id="chart-preview",
            figure=figure,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            },
            style={"height": "100%"}
        )

    return html.Div(
        content,
        id="chart-canvas",
        className="chart-canvas"
    )


def create_chart_config_panel() -> html.Div:
    """创建图表配置面板

    Returns:
        配置面板组件
    """
    return html.Div(
        [
            html.H6("样式配置", className="mb-3"),

            # 标题
            html.Div(
                [
                    html.Label("图表标题", className="form-label small text-muted mb-1"),
                    dbc.Input(
                        id="chart-title-input",
                        type="text",
                        placeholder="输入图表标题",
                        className="input-dark",
                    ),
                ],
                className="mb-3"
            ),

            # 副标题
            html.Div(
                [
                    html.Label("副标题", className="form-label small text-muted mb-1"),
                    dbc.Input(
                        id="chart-subtitle-input",
                        type="text",
                        placeholder="输入副标题（可选）",
                        className="input-dark",
                    ),
                ],
                className="mb-3"
            ),

            # 主题
            html.Div(
                [
                    html.Label("主题", className="form-label small text-muted mb-1"),
                    dcc.Dropdown(
                        id="chart-theme-dropdown",
                        options=[
                            {"label": "暗色（默认）", "value": "plotly_dark"},
                            {"label": "亮色", "value": "plotly_white"},
                            {"label": "简约", "value": "simple_white"},
                            {"label": "科技", "value": "plotly"},
                        ],
                        value="plotly_dark",
                        clearable=False,
                        className="dropdown-dark",
                    ),
                ],
                className="mb-3"
            ),

            # 配色方案
            html.Div(
                [
                    html.Label("配色方案", className="form-label small text-muted mb-1"),
                    dcc.Dropdown(
                        id="chart-colorscale-dropdown",
                        options=[
                            {"label": "默认", "value": "default"},
                            {"label": "Viridis", "value": "Viridis"},
                            {"label": "Plasma", "value": "Plasma"},
                            {"label": "Blues", "value": "Blues"},
                            {"label": "Reds", "value": "Reds"},
                            {"label": "Greens", "value": "Greens"},
                            {"label": "Rainbow", "value": "Rainbow"},
                        ],
                        value="default",
                        clearable=False,
                        className="dropdown-dark",
                    ),
                ],
                className="mb-3"
            ),

            # 显示图例
            html.Div(
                [
                    dbc.Checkbox(
                        id="chart-legend-checkbox",
                        label="显示图例",
                        value=True,
                        className="checkbox-dark",
                    ),
                ],
                className="mb-3"
            ),

            # 显示网格线
            html.Div(
                [
                    dbc.Checkbox(
                        id="chart-grid-checkbox",
                        label="显示网格线",
                        value=True,
                        className="checkbox-dark",
                    ),
                ],
                className="mb-3"
            ),

            html.Hr(className="my-4"),

            # 导出按钮
            html.H6("导出图表", className="mb-3"),
            html.Div(
                [
                    dbc.Button(
                        [html.I(className="bi bi-file-earmark-image me-2"), "PNG"],
                        id="export-png-btn",
                        color="secondary",
                        size="sm",
                        className="w-100 mb-2 btn-hover",
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-file-earmark-code me-2"), "HTML"],
                        id="export-html-btn",
                        color="secondary",
                        size="sm",
                        className="w-100 mb-2 btn-hover",
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-file-earmark-pdf me-2"), "PDF"],
                        id="export-pdf-btn",
                        color="secondary",
                        size="sm",
                        className="w-100 mb-2 btn-hover",
                    ),
                ],
            ),

            html.Hr(className="my-4"),

            # 保存图表
            html.H6("保存图表", className="mb-3"),
            html.Div(
                [
                    dbc.Input(
                        id="chart-name-input",
                        type="text",
                        placeholder="输入图表名称",
                        className="input-dark mb-2",
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-save me-2"), "保存图表"],
                        id="save-chart-btn",
                        color="primary",
                        size="sm",
                        className="w-100 btn-hover",
                    ),
                ],
            ),

            # 存储配置
            dcc.Store(id="chart-config-store", data={}),
            dcc.Store(id="current-chart-type", data=None),
        ],
        className="p-3 bg-tertiary rounded"
    )


def create_saved_charts_panel(saved_charts: list = None) -> html.Div:
    """创建已保存图表面板

    Args:
        saved_charts: 已保存的图表列表

    Returns:
        已保存图表面板
    """
    if not saved_charts:
        content = html.Div(
            [
                html.I(className="bi bi-inbox", style={"fontSize": "32px", "color": "#64748B"}),
                html.P("暂无保存的图表", className="text-muted mt-2 mb-0 small"),
            ],
            className="text-center py-4"
        )
    else:
        content = html.Div(
            [
                _create_saved_chart_card(chart)
                for chart in saved_charts
            ]
        )

    return html.Div(
        [
            html.Div(
                [
                    html.H6("已保存图表", className="mb-0"),
                    html.Small(f"{len(saved_charts) if saved_charts else 0} 个", className="text-muted"),
                ],
                className="d-flex justify-content-between align-items-center mb-3"
            ),
            content,
        ],
        className="p-3 bg-tertiary rounded mt-3"
    )


def _create_saved_chart_card(chart: Dict[str, Any]) -> html.Div:
    """创建已保存图表卡片

    Args:
        chart: 图表信息

    Returns:
        图表卡片
    """
    return html.Div(
        [
            html.Div(
                [
                    html.I(className="bi bi-graph-up me-2"),
                    html.Span(chart.get("name", "未命名图表")),
                ],
                className="d-flex align-items-center mb-1"
            ),
            html.Small(chart.get("type", ""), className="text-muted"),
            html.Div(
                [
                    html.I(
                        className="bi bi-pencil me-2",
                        id={"type": "edit-chart", "id": chart.get("id")},
                        style={"cursor": "pointer"}
                    ),
                    html.I(
                        className="bi bi-trash",
                        id={"type": "delete-chart", "id": chart.get("id")},
                        style={"cursor": "pointer", "color": "#EF4444"}
                    ),
                ],
                className="mt-2"
            ),
        ],
        className="saved-chart-card p-2 mb-2 bg-secondary rounded"
    )
