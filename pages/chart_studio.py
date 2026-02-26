# -*- coding: utf-8 -*-
"""图表工作室页面 — 拖拽式图表创建

提供 Tableau/Power BI 级别的图表创建体验。
"""

from __future__ import annotations

from typing import Optional

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, MATCH, ALL
import pandas as pd

from core.data_manager import DataManager
from components.field_panel import create_field_panel, create_chart_fields_panel
from components.chart_builder import (
    create_chart_type_selector,
    create_chart_canvas,
    create_chart_config_panel,
    create_saved_charts_panel,
)
from services.chart_service import create_chart, get_chart_type, recommend_charts


def create_chart_studio_page() -> html.Div:
    """创建图表工作室页面

    Returns:
        图表工作室页面组件
    """
    dm = DataManager()
    df = dm.active_df

    return html.Div(
        [
            dbc.Row(
                [
                    # 左侧：字段面板
                    create_field_panel(df),

                    # 中间：图表画布和字段配置
                    dbc.Col(
                        [
                            # 图表类型选择器
                            html.Div(
                                create_chart_type_selector(),
                                className="mb-3"
                            ),

                            # 字段配置区
                            html.Div(
                                create_chart_fields_panel(),
                                className="mb-3"
                            ),

                            # 图表画布
                            html.Div(
                                create_chart_canvas(),
                                style={"height": "calc(100vh - 400px)"}
                            ),
                        ],
                        width=6,
                        className="p-3",
                        style={"height": "calc(100vh - 76px)", "overflowY": "auto"}
                    ),

                    # 右侧：配置面板
                    dbc.Col(
                        [
                            create_chart_config_panel(),
                            create_saved_charts_panel(),
                        ],
                        width=3,
                        className="p-3 bg-secondary border-start",
                        style={"height": "calc(100vh - 76px)", "overflowY": "auto"}
                    ),
                ],
                className="g-0"
            ),

            # Toast 通知
            html.Div(id="chart-toast-container"),

            # 下载组件
            dcc.Download(id="chart-download"),
        ],
        id="chart-studio-page"
    )


# ═══════════════════════════════════════════════════════════
# 回调函数
# ═══════════════════════════════════════════════════════════

@callback(
    Output("chart-fields-store", "data"),
    Input({"type": "drop-zone", "zone": ALL}, "n_clicks"),
    State("chart-fields-store", "data"),
    prevent_initial_call=True
)
def handle_field_drop(n_clicks, current_fields):
    """处理字段拖放（通过 JavaScript 事件触发）
    
    这个回调主要用于初始化，实际的拖放逻辑在 drag_drop.js 中处理
    """
    return current_fields or {}


@callback(
    Output("chart-canvas", "children"),
    Output("chart-toast-container", "children"),
    Input("current-chart-type", "data"),
    Input("chart-fields-store", "data"),
    Input("chart-title-input", "value"),
    Input("chart-subtitle-input", "value"),
    Input("chart-theme-dropdown", "value"),
    Input("chart-legend-checkbox", "value"),
    Input("chart-grid-checkbox", "value"),
    prevent_initial_call=True
)
def update_chart(
    chart_type: Optional[str],
    fields: dict,
    title: Optional[str],
    subtitle: Optional[str],
    theme: str,
    show_legend: bool,
    show_grid: bool
):
    """更新图表预览

    Args:
        chart_type: 图表类型
        fields: 字段映射
        title: 标题
        subtitle: 副标题
        theme: 主题
        show_legend: 显示图例
        show_grid: 显示网格线

    Returns:
        图表组件和通知
    """
    dm = DataManager()
    df = dm.active_df

    if df is None:
        return (
            html.Div(
                [
                    html.I(className="bi bi-inbox", style={"fontSize": "64px", "color": "#64748B"}),
                    html.H5("未加载数据", className="mt-4 mb-2"),
                    html.P("请先在数据中心加载数据", className="text-muted"),
                ],
                className="chart-canvas-empty"
            ),
            None
        )

    if not chart_type or not fields:
        return create_chart_canvas(), None

    # 检查必需字段
    chart_type_obj = get_chart_type(chart_type)
    if not chart_type_obj:
        return create_chart_canvas(), None

    # 验证字段
    missing_fields = []
    for field_role, field_type in chart_type_obj.required_fields.items():
        if field_role not in fields or not fields[field_role]:
            missing_fields.append(field_role)

    if missing_fields:
        return (
            html.Div(
                [
                    html.I(className="bi bi-exclamation-triangle", style={"fontSize": "48px", "color": "#F59E0B"}),
                    html.H5("缺少必需字段", className="mt-4 mb-2"),
                    html.P(f"请拖拽字段到: {', '.join(missing_fields)}", className="text-muted"),
                ],
                className="chart-canvas-empty"
            ),
            None
        )

    try:
        # 创建图表配置
        config = {
            "title": title or "",
            "template": theme,
        }

        # 创建图表
        fig = create_chart(df, chart_type, fields, config)

        # 应用配置
        if subtitle:
            fig.update_layout(
                title={
                    "text": f"{title}<br><sub>{subtitle}</sub>" if title else f"<sub>{subtitle}</sub>",
                    "x": 0.5,
                    "xanchor": "center",
                }
            )
        elif title:
            fig.update_layout(
                title={
                    "text": title,
                    "x": 0.5,
                    "xanchor": "center",
                }
            )

        fig.update_layout(
            showlegend=show_legend,
            xaxis=dict(showgrid=show_grid),
            yaxis=dict(showgrid=show_grid),
        )

        return (
            dcc.Graph(
                id="chart-preview",
                figure=fig,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                },
                style={"height": "100%"}
            ),
            None
        )

    except Exception as e:
        return (
            html.Div(
                [
                    html.I(className="bi bi-x-circle", style={"fontSize": "48px", "color": "#EF4444"}),
                    html.H5("图表创建失败", className="mt-4 mb-2"),
                    html.P(str(e), className="text-muted small"),
                ],
                className="chart-canvas-empty"
            ),
            dbc.Toast(
                f"图表创建失败: {str(e)}",
                header="错误",
                icon="danger",
                duration=4000,
                is_open=True,
                style={"position": "fixed", "top": 80, "right": 10, "width": 350, "zIndex": 9999},
            )
        )


@callback(
    Output("current-chart-type", "data"),
    Input({"type": "chart-type-card", "chart_id": ALL}, "n_clicks"),
    State({"type": "chart-type-card", "chart_id": ALL}, "id"),
    prevent_initial_call=True
)
def select_chart_type(n_clicks_list, ids):
    """选择图表类型

    Args:
        n_clicks_list: 点击次数列表
        ids: ID 列表

    Returns:
        选中的图表类型
    """
    if not any(n_clicks_list):
        return None

    # 找到被点击的卡片
    for i, n_clicks in enumerate(n_clicks_list):
        if n_clicks:
            return ids[i]["chart_id"]

    return None


@callback(
    Output("chart-download", "data"),
    Input("export-png-btn", "n_clicks"),
    Input("export-html-btn", "n_clicks"),
    State("chart-preview", "figure"),
    prevent_initial_call=True
)
def export_chart(png_clicks, html_clicks, figure):
    """导出图表

    Args:
        png_clicks: PNG 按钮点击
        html_clicks: HTML 按钮点击
        figure: 图表对象

    Returns:
        下载数据
    """
    if not figure:
        return None

    import plotly.graph_objects as go
    from dash import ctx

    fig = go.Figure(figure)

    if ctx.triggered_id == "export-png-btn":
        # 导出 PNG
        img_bytes = fig.to_image(format="png", width=1200, height=800)
        return dcc.send_bytes(img_bytes, "chart.png")

    elif ctx.triggered_id == "export-html-btn":
        # 导出 HTML
        html_str = fig.to_html(include_plotlyjs="cdn")
        return dcc.send_string(html_str, "chart.html")

    return None


@callback(
    Output("chart-toast-container", "children", allow_duplicate=True),
    Input("save-chart-btn", "n_clicks"),
    State("chart-name-input", "value"),
    State("current-chart-type", "data"),
    State("chart-fields-store", "data"),
    State("chart-preview", "figure"),
    prevent_initial_call=True
)
def save_chart(n_clicks, chart_name, chart_type, fields, figure):
    """保存图表

    Args:
        n_clicks: 点击次数
        chart_name: 图表名称
        chart_type: 图表类型
        fields: 字段映射
        figure: 图表对象

    Returns:
        通知
    """
    if not n_clicks or not chart_name:
        return dbc.Toast(
            "请输入图表名称",
            header="提示",
            icon="warning",
            duration=3000,
            is_open=True,
            style={"position": "fixed", "top": 80, "right": 10, "width": 350, "zIndex": 9999},
        )

    if not figure:
        return dbc.Toast(
            "请先创建图表",
            header="提示",
            icon="warning",
            duration=3000,
            is_open=True,
            style={"position": "fixed", "top": 80, "right": 10, "width": 350, "zIndex": 9999},
        )

    # TODO: 实现图表保存逻辑（Phase 4）
    # 这里暂时只显示成功消息

    return dbc.Toast(
        f"图表 '{chart_name}' 已保存",
        header="成功",
        icon="success",
        duration=3000,
        is_open=True,
        style={"position": "fixed", "top": 80, "right": 10, "width": 350, "zIndex": 9999},
    )
