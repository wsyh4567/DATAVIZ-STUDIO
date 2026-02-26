# -*- coding: utf-8 -*-
"""图表服务 — 图表生成和智能推荐逻辑

提供图表类型定义、字段分类、图表生成和智能推荐功能。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


class FieldType(Enum):
    """字段类型枚举"""
    MEASURE = "measure"  # 度量（数值）
    DIMENSION = "dimension"  # 维度（分类/日期）


class ChartCategory(Enum):
    """图表分类"""
    COMPARISON = "comparison"  # 比较
    TREND = "trend"  # 趋势
    DISTRIBUTION = "distribution"  # 分布
    RELATIONSHIP = "relationship"  # 关系
    COMPOSITION = "composition"  # 占比


@dataclass
class FieldInfo:
    """字段信息"""
    name: str
    type: FieldType
    dtype: str  # pandas dtype
    unique_count: int
    null_count: int
    sample_values: List[Any]


@dataclass
class ChartType:
    """图表类型定义"""
    id: str
    name: str
    category: ChartCategory
    icon: str  # 图标名称
    description: str
    required_fields: Dict[str, str]  # 字段要求：{"x": "dimension", "y": "measure"}
    optional_fields: Dict[str, str]
    plotly_func: str  # plotly 函数名


# 图表类型定义
CHART_TYPES = [
    # 比较类
    ChartType(
        id="bar",
        name="柱状图",
        category=ChartCategory.COMPARISON,
        icon="bar-chart",
        description="比较不同类别的数值",
        required_fields={"x": "dimension", "y": "measure"},
        optional_fields={"color": "dimension"},
        plotly_func="bar"
    ),
    ChartType(
        id="bar_grouped",
        name="分组柱状图",
        category=ChartCategory.COMPARISON,
        icon="bar-chart-2",
        description="比较多个分组的数值",
        required_fields={"x": "dimension", "y": "measure", "color": "dimension"},
        optional_fields={},
        plotly_func="bar"
    ),
    ChartType(
        id="bar_stacked",
        name="堆叠柱状图",
        category=ChartCategory.COMPARISON,
        icon="bar-chart-3",
        description="显示部分与整体的关系",
        required_fields={"x": "dimension", "y": "measure", "color": "dimension"},
        optional_fields={},
        plotly_func="bar"
    ),
    ChartType(
        id="bar_horizontal",
        name="条形图",
        category=ChartCategory.COMPARISON,
        icon="bar-chart-horizontal",
        description="横向比较类别数值",
        required_fields={"x": "measure", "y": "dimension"},
        optional_fields={"color": "dimension"},
        plotly_func="bar"
    ),

    # 趋势类
    ChartType(
        id="line",
        name="折线图",
        category=ChartCategory.TREND,
        icon="trending-up",
        description="显示数据随时间的变化趋势",
        required_fields={"x": "dimension", "y": "measure"},
        optional_fields={"color": "dimension"},
        plotly_func="line"
    ),
    ChartType(
        id="area",
        name="面积图",
        category=ChartCategory.TREND,
        icon="area-chart",
        description="强调数量随时间的变化",
        required_fields={"x": "dimension", "y": "measure"},
        optional_fields={"color": "dimension"},
        plotly_func="area"
    ),
    ChartType(
        id="area_stacked",
        name="堆叠面积图",
        category=ChartCategory.TREND,
        icon="layers",
        description="显示多个系列的累积趋势",
        required_fields={"x": "dimension", "y": "measure", "color": "dimension"},
        optional_fields={},
        plotly_func="area"
    ),

    # 分布类
    ChartType(
        id="histogram",
        name="直方图",
        category=ChartCategory.DISTRIBUTION,
        icon="bar-chart-4",
        description="显示数值的分布情况",
        required_fields={"x": "measure"},
        optional_fields={"color": "dimension"},
        plotly_func="histogram"
    ),
    ChartType(
        id="box",
        name="箱线图",
        category=ChartCategory.DISTRIBUTION,
        icon="box",
        description="显示数据的统计分布",
        required_fields={"y": "measure"},
        optional_fields={"x": "dimension", "color": "dimension"},
        plotly_func="box"
    ),
    ChartType(
        id="violin",
        name="小提琴图",
        category=ChartCategory.DISTRIBUTION,
        icon="activity",
        description="显示数据的密度分布",
        required_fields={"y": "measure"},
        optional_fields={"x": "dimension", "color": "dimension"},
        plotly_func="violin"
    ),

    # 关系类
    ChartType(
        id="scatter",
        name="散点图",
        category=ChartCategory.RELATIONSHIP,
        icon="circle",
        description="显示两个变量之间的关系",
        required_fields={"x": "measure", "y": "measure"},
        optional_fields={"color": "dimension", "size": "measure"},
        plotly_func="scatter"
    ),
    ChartType(
        id="bubble",
        name="气泡图",
        category=ChartCategory.RELATIONSHIP,
        icon="circle-dot",
        description="三维数据关系可视化",
        required_fields={"x": "measure", "y": "measure", "size": "measure"},
        optional_fields={"color": "dimension"},
        plotly_func="scatter"
    ),
    ChartType(
        id="heatmap",
        name="热力图",
        category=ChartCategory.RELATIONSHIP,
        icon="grid",
        description="显示矩阵数据的模式",
        required_fields={"x": "dimension", "y": "dimension", "color": "measure"},
        optional_fields={},
        plotly_func="density_heatmap"
    ),

    # 占比类
    ChartType(
        id="pie",
        name="饼图",
        category=ChartCategory.COMPOSITION,
        icon="pie-chart",
        description="显示部分占整体的比例",
        required_fields={"names": "dimension", "values": "measure"},
        optional_fields={},
        plotly_func="pie"
    ),
    ChartType(
        id="donut",
        name="环形图",
        category=ChartCategory.COMPOSITION,
        icon="donut",
        description="饼图的变体，中心留空",
        required_fields={"names": "dimension", "values": "measure"},
        optional_fields={},
        plotly_func="pie"
    ),
]


def classify_field(series: pd.Series) -> FieldInfo:
    """分类字段为度量或维度

    Args:
        series: pandas Series

    Returns:
        FieldInfo: 字段信息
    """
    name = series.name
    dtype = str(series.dtype)
    unique_count = series.nunique()
    null_count = series.isnull().sum()
    total_count = len(series)

    # 获取样本值
    sample_values = series.dropna().head(5).tolist()

    # 分类逻辑
    if pd.api.types.is_numeric_dtype(series):
        # 数值类型
        if unique_count < 10 or unique_count / total_count < 0.05:
            # 唯一值少或占比低，视为维度
            field_type = FieldType.DIMENSION
        else:
            # 视为度量
            field_type = FieldType.MEASURE
    elif pd.api.types.is_datetime64_any_dtype(series):
        # 日期类型视为维度
        field_type = FieldType.DIMENSION
    elif pd.api.types.is_bool_dtype(series):
        # 布尔类型视为维度
        field_type = FieldType.DIMENSION
    else:
        # 其他类型（字符串等）视为维度
        field_type = FieldType.DIMENSION

    return FieldInfo(
        name=name,
        type=field_type,
        dtype=dtype,
        unique_count=unique_count,
        null_count=null_count,
        sample_values=sample_values
    )


def classify_dataframe(df: pd.DataFrame) -> Dict[str, FieldInfo]:
    """分类 DataFrame 的所有字段

    Args:
        df: pandas DataFrame

    Returns:
        Dict[str, FieldInfo]: 字段名 -> 字段信息
    """
    return {col: classify_field(df[col]) for col in df.columns}


def get_chart_type(chart_id: str) -> Optional[ChartType]:
    """根据 ID 获取图表类型

    Args:
        chart_id: 图表类型 ID

    Returns:
        ChartType 或 None
    """
    for chart_type in CHART_TYPES:
        if chart_type.id == chart_id:
            return chart_type
    return None


def recommend_charts(fields: Dict[str, Any]) -> List[Tuple[str, int]]:
    """根据选择的字段推荐图表类型

    Args:
        fields: 字段映射，例如 {"x": "age", "y": "salary"}

    Returns:
        List[Tuple[str, int]]: (图表ID, 推荐分数) 列表，按分数降序
    """
    field_info = {}
    for role, field_name in fields.items():
        if field_name:
            field_info[role] = field_name

    recommendations = []

    # 简单推荐逻辑
    if "x" in field_info and "y" in field_info:
        if "color" in field_info:
            # 三个字段
            recommendations.append(("bar_grouped", 90))
            recommendations.append(("scatter", 85))
            recommendations.append(("line", 80))
        else:
            # 两个字段
            recommendations.append(("bar", 95))
            recommendations.append(("line", 90))
            recommendations.append(("scatter", 85))
    elif "x" in field_info:
        # 只有 X 轴
        recommendations.append(("histogram", 95))
    elif "y" in field_info:
        # 只有 Y 轴
        recommendations.append(("box", 90))
        recommendations.append(("violin", 85))

    # 如果有 names 和 values，推荐饼图
    if "names" in field_info and "values" in field_info:
        recommendations.append(("pie", 95))
        recommendations.append(("donut", 90))

    # 按分数排序
    recommendations.sort(key=lambda x: x[1], reverse=True)

    return recommendations


def create_chart(
    df: pd.DataFrame,
    chart_id: str,
    fields: Dict[str, str],
    config: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """创建图表

    Args:
        df: 数据
        chart_id: 图表类型 ID
        fields: 字段映射
        config: 图表配置

    Returns:
        plotly Figure
    """
    chart_type = get_chart_type(chart_id)
    if not chart_type:
        raise ValueError(f"未知的图表类型: {chart_id}")

    config = config or {}

    # 根据图表类型创建图表
    if chart_id == "bar":
        fig = px.bar(df, x=fields.get("x"), y=fields.get("y"),
                     color=fields.get("color"), **config)
    elif chart_id == "bar_grouped":
        fig = px.bar(df, x=fields.get("x"), y=fields.get("y"),
                     color=fields.get("color"), barmode="group", **config)
    elif chart_id == "bar_stacked":
        fig = px.bar(df, x=fields.get("x"), y=fields.get("y"),
                     color=fields.get("color"), barmode="stack", **config)
    elif chart_id == "bar_horizontal":
        fig = px.bar(df, x=fields.get("x"), y=fields.get("y"),
                     color=fields.get("color"), orientation="h", **config)
    elif chart_id == "line":
        fig = px.line(df, x=fields.get("x"), y=fields.get("y"),
                      color=fields.get("color"), **config)
    elif chart_id == "area":
        fig = px.area(df, x=fields.get("x"), y=fields.get("y"),
                      color=fields.get("color"), **config)
    elif chart_id == "area_stacked":
        fig = px.area(df, x=fields.get("x"), y=fields.get("y"),
                      color=fields.get("color"), **config)
    elif chart_id == "histogram":
        fig = px.histogram(df, x=fields.get("x"), color=fields.get("color"), **config)
    elif chart_id == "box":
        fig = px.box(df, x=fields.get("x"), y=fields.get("y"),
                     color=fields.get("color"), **config)
    elif chart_id == "violin":
        fig = px.violin(df, x=fields.get("x"), y=fields.get("y"),
                        color=fields.get("color"), **config)
    elif chart_id == "scatter":
        fig = px.scatter(df, x=fields.get("x"), y=fields.get("y"),
                         color=fields.get("color"), size=fields.get("size"), **config)
    elif chart_id == "bubble":
        fig = px.scatter(df, x=fields.get("x"), y=fields.get("y"),
                         size=fields.get("size"), color=fields.get("color"), **config)
    elif chart_id == "heatmap":
        fig = px.density_heatmap(df, x=fields.get("x"), y=fields.get("y"),
                                 z=fields.get("color"), **config)
    elif chart_id == "pie":
        fig = px.pie(df, names=fields.get("names"), values=fields.get("values"), **config)
    elif chart_id == "donut":
        fig = px.pie(df, names=fields.get("names"), values=fields.get("values"),
                     hole=0.4, **config)
    else:
        raise ValueError(f"图表类型 {chart_id} 尚未实现")

    # 应用暗色主题
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1B1D2A",
        plot_bgcolor="#262940",
        font=dict(color="#F1F5F9", family="Inter, sans-serif"),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig


def get_aggregation_options() -> List[Dict[str, str]]:
    """获取聚合方式选项

    Returns:
        List[Dict]: 聚合选项列表
    """
    return [
        {"label": "求和 (SUM)", "value": "sum"},
        {"label": "平均值 (AVG)", "value": "mean"},
        {"label": "计数 (COUNT)", "value": "count"},
        {"label": "最大值 (MAX)", "value": "max"},
        {"label": "最小值 (MIN)", "value": "min"},
        {"label": "中位数 (MEDIAN)", "value": "median"},
        {"label": "标准差 (STD)", "value": "std"},
    ]
