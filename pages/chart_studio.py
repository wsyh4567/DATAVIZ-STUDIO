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
    """创建图表工作室页面（FineBI 风格）

    布局：
    - 左侧：字段面板（窄）
    - 中间：图表画布（主要区域）+ 顶部字段配置条
    - 右侧：图表类型 + 样式配置（窄）

    Returns:
        图表工作室页面组件
    """
    dm = DataManager()
    df = dm.active_df

    return html.Div(
        [
            dbc.Row(
                [
                    # 左侧：字段面板（窄）
                    create_field_panel(df),

                    # 中间：主工作区
                    dbc.Col(
                        [
                            # 顶部：紧凑的字段配置条
                            html.Div(
                                create_compact_field_config(),
                                className="mb-2",
                                style={"background": "var(--bg-secondary)", "padding": "12px", "borderRadius": "8px"}
                            ),

                            # 图表画布（占据主要空间）
                            html.Div(
                                create_chart_canvas(),
                                style={"height": "calc(100vh - 180px)"}
                            ),
                        ],
                        width=7,
                        className="p-3",
                        style={"height": "calc(100vh - 76px)"}
                    ),

                    # 右侧：图表类型 + 配置面板（窄）
                    dbc.Col(
                        [
                            # 图表类型选择器（紧凑版）
                            html.Div(
                                create_compact_chart_type_selector(),
                                className="mb-3"
                            ),
                            
                            # 样式配置面板
                            create_chart_config_panel(),
                        ],
                        width=2,
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


def create_compact_field_config() -> html.Div:
    """创建紧凑的字段配置条（FineBI 风格）
    
    横向排列：维度 | 度量 | 颜色 | 大小
    """
    return html.Div(
        [
            html.Div(
                [
                    # 维度（X轴）
                    html.Div(
                        [
                            html.Label("维度", className="field-config-label"),
                            html.Div(
                                id={"type": "drop-zone", "zone": "x"},
                                className="drop-zone drop-zone-compact drop-zone-empty",
                                children=html.Span("拖拽维度字段", className="text-muted small"),
                                **{"data-zone": "x"}
                            ),
                        ],
                        className="field-config-item"
                    ),
                    
                    # 度量（Y轴）
                    html.Div(
                        [
                            html.Label("度量", className="field-config-label"),
                            html.Div(
                                id={"type": "drop-zone", "zone": "y"},
                                className="drop-zone drop-zone-compact drop-zone-empty",
                                children=html.Span("拖拽度量字段", className="text-muted small"),
                                **{"data-zone": "y"}
                            ),
                        ],
                        className="field-config-item"
                    ),
                    
                    # 颜色（可选）
                    html.Div(
                        [
                            html.Label("颜色", className="field-config-label"),
                            html.Div(
                                id={"type": "drop-zone", "zone": "color"},
                                className="drop-zone drop-zone-compact drop-zone-empty",
                                children=html.Span("可选", className="text-muted small"),
                                **{"data-zone": "color"}
                            ),
                        ],
                        className="field-config-item"
                    ),
                    
                    # 大小（可选）
                    html.Div(
                        [
                            html.Label("大小", className="field-config-label"),
                            html.Div(
                                id={"type": "drop-zone", "zone": "size"},
                                className="drop-zone drop-zone-compact drop-zone-empty",
                                children=html.Span("可选", className="text-muted small"),
                                **{"data-zone": "size"}
                            ),
                        ],
                        className="field-config-item"
                    ),
                ],
                className="field-config-row"
            ),
            
            # 存储字段映射
            dcc.Store(id="chart-fields-store", data={}),
        ]
    )


def create_compact_chart_type_selector() -> html.Div:
    """创建紧凑的图表类型选择器
    
    垂直排列的图标按钮
    """
    from services.chart_service import CHART_TYPES, ChartCategory
    
    # 常用图表类型（精简版）
    common_charts = [
        "bar",           # 柱状图
        "line",          # 折线图
        "scatter",       # 散点图
        "pie",           # 饼图
        "histogram",     # 直方图
        "box",           # 箱线图
    ]
    
    chart_buttons = []
    for chart_id in common_charts:
        chart_type = next((ct for ct in CHART_TYPES if ct.id == chart_id), None)
        if chart_type:
            chart_buttons.append(
                html.Div(
                    [
                        html.I(className=f"bi bi-{chart_type.icon}", style={"fontSize": "20px"}),
                        html.Div(chart_type.name, className="chart-type-label"),
                    ],
                    id={"type": "chart-type-card", "chart_id": chart_type.id},
                    className="chart-type-btn",
                    title=chart_type.description,
                    **{"data-chart-id": chart_type.id}
                )
            )
    
    return html.Div(
        [
            html.H6("图表类型", className="mb-2", style={"fontSize": "14px"}),
            html.Div(
                chart_buttons,
                className="chart-type-list"
            ),
            dcc.Store(id="current-chart-type", data="bar"),  # 默认柱状图
        ]
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
    Output("current-chart-type", "data", allow_duplicate=True),
    Input("chart-fields-store", "data"),
    Input("current-chart-type", "data"),
    Input("chart-title-input", "value"),
    Input("chart-subtitle-input", "value"),
    Input("chart-theme-dropdown", "value"),
    Input("chart-legend-checkbox", "value"),
    Input("chart-grid-checkbox", "value"),
    prevent_initial_call=True
)
def update_chart_auto(
    fields: dict,
    chart_type: Optional[str],
    title: Optional[str],
    subtitle: Optional[str],
    theme: str,
    show_legend: bool,
    show_grid: bool
):
    """自动更新图表（即拖即用）

    当字段变化时：
    1. 如果没有选择图表类型，自动推荐并选择
    2. 立即生成图表

    Args:
        fields: 字段映射
        chart_type: 图表类型
        title: 标题
        subtitle: 副标题
        theme: 主题
        show_legend: 显示图例
        show_grid: 显示网格线

    Returns:
        图表组件、通知、图表类型
    """
    from dash import ctx
    
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
            None,
            chart_type
        )

    # 如果没有字段，显示提示
    if not fields or not any(fields.values()):
        return (
            html.Div(
                [
                    html.I(className="bi bi-graph-up", style={"fontSize": "64px", "color": "#64748B"}),
                    html.H5("开始创建图表", className="mt-4 mb-2"),
                    html.P("从左侧拖拽字段到顶部配置区", className="text-muted"),
                ],
                className="chart-canvas-empty"
            ),
            None,
            chart_type
        )

    # 智能推荐图表类型（如果用户没有手动选择）
    triggered_id = ctx.triggered_id
    if triggered_id == "chart-fields-store" and fields:
        # 字段变化时，自动推荐图表类型
        recommendations = recommend_charts(fields)
        if recommendations and not chart_type:
            chart_type = recommendations[0][0]  # 使用推荐度最高的图表

    if not chart_type:
        chart_type = "bar"  # 默认柱状图

    # 获取图表类型对象
    chart_type_obj = get_chart_type(chart_type)
    if not chart_type_obj:
        return create_chart_canvas(), None, chart_type

    # 验证必需字段
    missing_fields = []
    for field_role, field_type in chart_type_obj.required_fields.items():
        if field_role not in fields or not fields[field_role]:
            missing_fields.append(field_role)

    if missing_fields:
        # 尝试自动映射字段
        if "x" in missing_fields and "y" in fields and fields["y"]:
            # 如果只有 Y 轴，尝试创建直方图
            chart_type = "histogram"
            chart_type_obj = get_chart_type(chart_type)
            missing_fields = []
        elif "y" in missing_fields and "x" in fields and fields["x"]:
            # 如果只有 X 轴，也尝试直方图
            chart_type = "histogram"
            chart_type_obj = get_chart_type(chart_type)
            missing_fields = []

    if missing_fields:
        return (
            html.Div(
                [
                    html.I(className="bi bi-exclamation-triangle", style={"fontSize": "48px", "color": "#F59E0B"}),
                    html.H5("需要更多字段", className="mt-4 mb-2"),
                    html.P(f"请拖拽字段到: {', '.join(missing_fields)}", className="text-muted"),
                ],
                className="chart-canvas-empty"
            ),
            None,
            chart_type
        )

    try:
        # 创建图表配置
        config = {
            "title": title or "",
            "template": theme or "plotly_dark",
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
            showlegend=show_legend if show_legend is not None else True,
            xaxis=dict(showgrid=show_grid if show_grid is not None else True),
            yaxis=dict(showgrid=show_grid if show_grid is not None else True),
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
            None,
            chart_type
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
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
            ),
            chart_type
        )


@callback(
    Output("current-chart-type", "data", allow_duplicate=True),
    Output({"type": "chart-type-card", "chart_id": ALL}, "className"),
    Input({"type": "chart-type-card", "chart_id": ALL}, "n_clicks"),
    State({"type": "chart-type-card", "chart_id": ALL}, "id"),
    State("current-chart-type", "data"),
    prevent_initial_call=True
)
def select_chart_type(n_clicks_list, ids, current_type):
    """选择图表类型并更新视觉状态

    Args:
        n_clicks_list: 点击次数列表
        ids: ID 列表
        current_type: 当前图表类型

    Returns:
        选中的图表类型和按钮样式列表
    """
    from dash import ctx
    
    if not any(n_clicks_list):
        # 初始化：高亮当前类型
        class_names = []
        for id_dict in ids:
            if id_dict["chart_id"] == current_type:
                class_names.append("chart-type-btn active")
            else:
                class_names.append("chart-type-btn")
        return current_type, class_names

    # 找到被点击的卡片
    selected_type = current_type
    for i, n_clicks in enumerate(n_clicks_list):
        if n_clicks and ctx.triggered_id == ids[i]:
            selected_type = ids[i]["chart_id"]
            break

    # 更新样式
    class_names = []
    for id_dict in ids:
        if id_dict["chart_id"] == selected_type:
            class_names.append("chart-type-btn active")
        else:
            class_names.append("chart-type-btn")

    return selected_type, class_names


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
