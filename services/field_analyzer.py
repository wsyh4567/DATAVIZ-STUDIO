# -*- coding: utf-8 -*-
"""字段类型推断服务

自动判断字段是度量(measure)还是维度(dimension)，对标 PyGWalker 的智能字段推断。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pandas as pd


class FieldType(Enum):
    """字段语义类型"""
    MEASURE = "measure"       # 度量（连续数值）
    DIMENSION = "dimension"   # 维度（分类）
    TEMPORAL = "temporal"     # 时间
    NOMINAL = "nominal"       # 名义（文本类别）


@dataclass
class FieldInfo:
    """字段信息"""
    name: str
    dtype: str
    field_type: FieldType
    unique_count: int
    null_count: int
    label: str  # 带标识的显示标签，如 "[M] salary"


# 类型标识前缀
_TYPE_PREFIXES = {
    FieldType.MEASURE: "[M]",
    FieldType.DIMENSION: "[D]",
    FieldType.TEMPORAL: "[T]",
    FieldType.NOMINAL: "[N]",
}


def infer_field_type(series: pd.Series) -> FieldType:
    """推断单个字段的语义类型

    规则：
    - datetime 类型 → temporal
    - 数值型且 unique > 16 → measure
    - 数值型且 unique <= 16 → dimension
    - 布尔型 → dimension
    - 其他 → nominal (dimension)

    Args:
        series: pandas Series

    Returns:
        字段语义类型
    """
    dtype = series.dtype

    # 时间类型
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return FieldType.TEMPORAL

    # 布尔类型
    if pd.api.types.is_bool_dtype(dtype):
        return FieldType.DIMENSION

    # 数值类型
    if pd.api.types.is_numeric_dtype(dtype):
        unique_count = series.nunique()
        if unique_count > 16:
            return FieldType.MEASURE
        else:
            return FieldType.DIMENSION

    # 字符串/对象类型 - 尝试判断是否可以转为数值
    if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
        # 尝试转换为数值
        try:
            numeric = pd.to_numeric(series.dropna(), errors='coerce')
            non_null_ratio = numeric.notna().sum() / max(len(numeric), 1)
            if non_null_ratio > 0.8:  # 超过80%可以转为数值
                unique_count = numeric.nunique()
                if unique_count > 16:
                    return FieldType.MEASURE
                else:
                    return FieldType.DIMENSION
        except (ValueError, TypeError):
            pass

        return FieldType.NOMINAL

    # 分类类型
    if isinstance(dtype, pd.CategoricalDtype):
        return FieldType.DIMENSION

    return FieldType.NOMINAL


def analyze_fields(df: pd.DataFrame) -> list[FieldInfo]:
    """分析 DataFrame 所有字段

    Args:
        df: 数据框

    Returns:
        字段信息列表
    """
    fields = []
    for col in df.columns:
        series = df[col]
        field_type = infer_field_type(series)
        prefix = _TYPE_PREFIXES[field_type]
        fields.append(FieldInfo(
            name=col,
            dtype=str(series.dtype),
            field_type=field_type,
            unique_count=series.nunique(),
            null_count=int(series.isna().sum()),
            label=f"{prefix} {col}",
        ))
    return fields


def get_labeled_options(df: pd.DataFrame) -> list[dict]:
    """获取带类型标签的下拉选项列表

    Args:
        df: 数据框

    Returns:
        [{'label': '[M] salary', 'value': 'salary'}, ...]
    """
    fields = analyze_fields(df)
    return [{'label': f.label, 'value': f.name} for f in fields]


def get_measures(df: pd.DataFrame) -> list[str]:
    """获取所有度量字段名"""
    return [f.name for f in analyze_fields(df) if f.field_type == FieldType.MEASURE]


def get_dimensions(df: pd.DataFrame) -> list[str]:
    """获取所有维度字段名"""
    return [f.name for f in analyze_fields(df)
            if f.field_type in (FieldType.DIMENSION, FieldType.NOMINAL)]
