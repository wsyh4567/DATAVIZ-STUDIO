# -*- coding: utf-8 -*-
"""字段面板组件 — 拖拽式字段选择

提供字段分类展示和拖拽功能。
"""

from __future__ import annotations

from typing import Optional, Dict, List

import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd

from services.chart_service import classify_dataframe, FieldType


def create_field_panel(df: Optional[pd.DataFrame] = None) -> dbc.Col:
    """创建字段面板

    Args:
        df: 数据框

    Returns:
        字段面板组件
    """
    if df is None:
        return dbc.Col(
            [
                html.Div(
                    [
                        html.I(className="bi bi-inbox", style={"fontSize": "48px", "color": "#64748B"}),
                        html.P("未加载数据", className="text-muted mt-3"),
                        html.P("请先在数据中心加载数据", className="text-muted small"),
                    ],
                    className="text-center py-5"
                )
            ],
            width=3,
            className="field-panel bg-secondary border-end",
            style={"height": "calc(100vh - 76px)", "overflowY": "auto"}
        )

    # 分类字段
    field_info = classify_dataframe(df)
    measures = [info for info in field_info.values() if info.type == FieldType.MEASURE]
    dimensions = [info for info in field_info.values() if info.type == FieldType.DIMENSION]

    return dbc.Col(
        [
            # 标题
            html.Div(
                [
                    html.H6("字段列表", className="mb-0"),
                    html.Small(f"{len(field_info)} 个字段", className="text-muted"),
                ],
                className="p-3 border-bottom"
            ),

            # 度量字段
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="bi bi-hash me-2", style={"color": "#6366F1"}),
                            html.Strong("度量", style={"color": "#F1F5F9"}),
                            html.Span(f" ({len(measures)})", className="text-muted small ms-1"),
                        ],
                        className="d-flex align-items-center mb-2"
                    ),
                    html.Div(
                        [
                            _create_field_item(info, "measure")
                            for info in measures
                        ],
                        id="measure-fields-list"
                    )
                ],
                className="p-3 border-bottom"
            ),

            # 维度字段
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="bi bi-tag me-2", style={"color": "#10B981"}),
                            html.Strong("维度", style={"color": "#F1F5F9"}),
                            html.Span(f" ({len(dimensions)})", className="text-muted small ms-1"),
                        ],
                        className="d-flex align-items-center mb-2"
                    ),
                    html.Div(
                        [
                            _create_field_item(info, "dimension")
                            for info in dimensions
                        ],
                        id="dimension-fields-list"
                    )
                ],
                className="p-3"
            ),
        ],
        width=3,
        className="field-panel bg-secondary border-end",
        style={"height": "calc(100vh - 76px)", "overflowY": "auto"}
    )


def _create_field_item(field_info, field_category: str) -> html.Div:
    """创建字段项

    Args:
        field_info: 字段信息
        field_category: 字段类别

    Returns:
        字段项组件
    """
    # 根据数据类型选择图标
    if "int" in field_info.dtype or "float" in field_info.dtype:
        icon = "bi-123"
        icon_color = "#6366F1"
    elif "datetime" in field_info.dtype:
        icon = "bi-calendar"
        icon_color = "#F59E0B"
    elif "bool" in field_info.dtype:
        icon = "bi-toggle-on"
        icon_color = "#10B981"
    else:
        icon = "bi-fonts"
        icon_color = "#94A3B8"

    return html.Div(
        [
            html.Div(
                [
                    html.I(className=f"bi {icon} me-2", style={"color": icon_color}),
                    html.Span(field_info.name, className="field-name"),
                    html.Span(
                        f"{field_info.unique_count}",
                        className="badge bg-dark ms-auto",
                        title=f"{field_info.unique_count} 个唯一值"
                    ),
                ],
                className="field-item d-flex align-items-center",
                id={"type": "field-item", "field": field_info.name, "category": field_category},
                draggable="true",
                **{"data-field": field_info.name, "data-category": field_category}
            )
        ],
        className="mb-2"
    )


def create_drop_zone(label: str, zone_id: str, field_name: Optional[str] = None) -> html.Div:
    """创建拖放区域

    Args:
        label: 区域标签
        zone_id: 区域 ID
        field_name: 当前字段名

    Returns:
        拖放区域组件
    """
    if field_name:
        content = html.Div(
            [
                html.Span(field_name, className="me-2"),
                html.I(
                    className="bi bi-x-circle",
                    id={"type": "remove-field", "zone": zone_id},
                    style={"cursor": "pointer", "color": "#EF4444"}
                ),
            ],
            className="d-flex align-items-center justify-content-between"
        )
        class_name = "drop-zone drop-zone-filled"
    else:
        content = html.Span("拖拽字段到此处", className="text-muted small")
        class_name = "drop-zone drop-zone-empty"

    return html.Div(
        [
            html.Label(label, className="form-label small text-muted mb-1"),
            html.Div(
                content,
                id={"type": "drop-zone", "zone": zone_id},
                className=class_name,
                **{"data-zone": zone_id}
            ),
        ],
        className="mb-3"
    )


def create_chart_fields_panel() -> html.Div:
    """创建图表字段配置面板

    Returns:
        字段配置面板
    """
    return html.Div(
        [
            html.H6("字段配置", className="mb-3"),

            # X 轴
            create_drop_zone("X 轴", "x"),

            # Y 轴
            create_drop_zone("Y 轴", "y"),

            # 颜色
            create_drop_zone("颜色", "color"),

            # 大小
            create_drop_zone("大小", "size"),

            # 分面
            create_drop_zone("分面", "facet"),

            # 聚合方式（仅度量字段）
            html.Div(
                [
                    html.Label("聚合方式", className="form-label small text-muted mb-1"),
                    dcc.Dropdown(
                        id="aggregation-dropdown",
                        options=[
                            {"label": "求和 (SUM)", "value": "sum"},
                            {"label": "平均值 (AVG)", "value": "mean"},
                            {"label": "计数 (COUNT)", "value": "count"},
                            {"label": "最大值 (MAX)", "value": "max"},
                            {"label": "最小值 (MIN)", "value": "min"},
                            {"label": "中位数 (MEDIAN)", "value": "median"},
                        ],
                        value="sum",
                        clearable=False,
                        className="dropdown-dark",
                    ),
                ],
                className="mb-3"
            ),

            # 存储字段映射
            dcc.Store(id="chart-fields-store", data={}),
        ],
        className="p-3 bg-tertiary rounded"
    )
