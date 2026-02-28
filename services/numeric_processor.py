# -*- coding: utf-8 -*-
"""数值处理服务

提供分箱、标准化/归一化、滚动窗口函数、累积函数等数值处理能力。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


class NumericBinner:
    """数值分箱器

    支持等宽分箱、等频分箱和自定义边界分箱。
    """

    @staticmethod
    def equal_width(
        series: pd.Series,
        bins: int = 5,
        labels: Optional[List[str]] = None,
    ) -> Tuple[pd.Series, str]:
        """等宽分箱"""
        result = pd.cut(series, bins=bins, labels=labels)
        code = f"pd.cut(df['{series.name}'], bins={bins}, labels={labels})"
        return result.astype(str), code

    @staticmethod
    def equal_freq(
        series: pd.Series,
        q: int = 5,
        labels: Optional[List[str]] = None,
    ) -> Tuple[pd.Series, str]:
        """等频分箱"""
        result = pd.qcut(series, q=q, labels=labels, duplicates="drop")
        code = f"pd.qcut(df['{series.name}'], q={q}, labels={labels}, duplicates='drop')"
        return result.astype(str), code

    @staticmethod
    def custom(
        series: pd.Series,
        boundaries: List[float],
        labels: Optional[List[str]] = None,
    ) -> Tuple[pd.Series, str]:
        """自定义边界分箱"""
        result = pd.cut(series, bins=boundaries, labels=labels, include_lowest=True)
        code = f"pd.cut(df['{series.name}'], bins={boundaries}, labels={labels}, include_lowest=True)"
        return result.astype(str), code


class NumericNormalizer:
    """数值标准化/归一化器"""

    @staticmethod
    def min_max(series: pd.Series) -> Tuple[pd.Series, str]:
        """Min-Max 归一化到 [0, 1]"""
        min_val = series.min()
        max_val = series.max()
        rng = max_val - min_val
        if rng == 0:
            result = pd.Series(0.0, index=series.index, name=series.name)
        else:
            result = (series - min_val) / rng
        code = (
            f"df['{series.name}_norm'] = "
            f"(df['{series.name}'] - df['{series.name}'].min()) / "
            f"(df['{series.name}'].max() - df['{series.name}'].min())"
        )
        return result, code

    @staticmethod
    def z_score(series: pd.Series) -> Tuple[pd.Series, str]:
        """Z-Score 标准化"""
        mean = series.mean()
        std = series.std()
        if std == 0:
            result = pd.Series(0.0, index=series.index, name=series.name)
        else:
            result = (series - mean) / std
        code = (
            f"df['{series.name}_zscore'] = "
            f"(df['{series.name}'] - df['{series.name}'].mean()) / df['{series.name}'].std()"
        )
        return result, code

    @staticmethod
    def robust(series: pd.Series) -> Tuple[pd.Series, str]:
        """Robust 标准化 (中位数 / IQR)"""
        median = series.median()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            result = pd.Series(0.0, index=series.index, name=series.name)
        else:
            result = (series - median) / iqr
        code = (
            f"median = df['{series.name}'].median()\n"
            f"iqr = df['{series.name}'].quantile(0.75) - df['{series.name}'].quantile(0.25)\n"
            f"df['{series.name}_robust'] = (df['{series.name}'] - median) / iqr"
        )
        return result, code

    @staticmethod
    def winsorize(
        series: pd.Series, lower: float = 0.05, upper: float = 0.95
    ) -> Tuple[pd.Series, str]:
        """Winsorize：截断极端值"""
        lo = series.quantile(lower)
        hi = series.quantile(upper)
        result = series.clip(lower=lo, upper=hi)
        code = (
            f"lo = df['{series.name}'].quantile({lower})\n"
            f"hi = df['{series.name}'].quantile({upper})\n"
            f"df['{series.name}_winsor'] = df['{series.name}'].clip(lower=lo, upper=hi)"
        )
        return result, code

    @staticmethod
    def log_transform(series: pd.Series) -> Tuple[pd.Series, str]:
        """对数变换 (log1p，安全处理 0 值)"""
        result = np.log1p(series)
        code = f"df['{series.name}_log'] = np.log1p(df['{series.name}'])"
        return result, code


class RollingWindow:
    """滚动窗口函数"""

    @staticmethod
    def rolling_mean(
        series: pd.Series, window: int = 3
    ) -> Tuple[pd.Series, str]:
        """滚动均值"""
        result = series.rolling(window=window, min_periods=1).mean()
        code = f"df['{series.name}_rolling_mean'] = df['{series.name}'].rolling(window={window}, min_periods=1).mean()"
        return result, code

    @staticmethod
    def rolling_sum(
        series: pd.Series, window: int = 3
    ) -> Tuple[pd.Series, str]:
        """滚动求和"""
        result = series.rolling(window=window, min_periods=1).sum()
        code = f"df['{series.name}_rolling_sum'] = df['{series.name}'].rolling(window={window}, min_periods=1).sum()"
        return result, code

    @staticmethod
    def rolling_std(
        series: pd.Series, window: int = 3
    ) -> Tuple[pd.Series, str]:
        """滚动标准差"""
        result = series.rolling(window=window, min_periods=1).std()
        code = f"df['{series.name}_rolling_std'] = df['{series.name}'].rolling(window={window}, min_periods=1).std()"
        return result, code

    @staticmethod
    def rolling_min(
        series: pd.Series, window: int = 3
    ) -> Tuple[pd.Series, str]:
        """滚动最小值"""
        result = series.rolling(window=window, min_periods=1).min()
        code = f"df['{series.name}_rolling_min'] = df['{series.name}'].rolling(window={window}, min_periods=1).min()"
        return result, code

    @staticmethod
    def rolling_max(
        series: pd.Series, window: int = 3
    ) -> Tuple[pd.Series, str]:
        """滚动最大值"""
        result = series.rolling(window=window, min_periods=1).max()
        code = f"df['{series.name}_rolling_max'] = df['{series.name}'].rolling(window={window}, min_periods=1).max()"
        return result, code

    @staticmethod
    def ewm_mean(
        series: pd.Series, span: int = 5
    ) -> Tuple[pd.Series, str]:
        """指数加权移动平均"""
        result = series.ewm(span=span, adjust=False).mean()
        code = f"df['{series.name}_ewm'] = df['{series.name}'].ewm(span={span}, adjust=False).mean()"
        return result, code


class CumulativeOperations:
    """累积函数"""

    @staticmethod
    def cumsum(series: pd.Series) -> Tuple[pd.Series, str]:
        result = series.cumsum()
        code = f"df['{series.name}_cumsum'] = df['{series.name}'].cumsum()"
        return result, code

    @staticmethod
    def cumprod(series: pd.Series) -> Tuple[pd.Series, str]:
        result = series.cumprod()
        code = f"df['{series.name}_cumprod'] = df['{series.name}'].cumprod()"
        return result, code

    @staticmethod
    def cummax(series: pd.Series) -> Tuple[pd.Series, str]:
        result = series.cummax()
        code = f"df['{series.name}_cummax'] = df['{series.name}'].cummax()"
        return result, code

    @staticmethod
    def cummin(series: pd.Series) -> Tuple[pd.Series, str]:
        result = series.cummin()
        code = f"df['{series.name}_cummin'] = df['{series.name}'].cummin()"
        return result, code

    @staticmethod
    def pct_change(series: pd.Series, periods: int = 1) -> Tuple[pd.Series, str]:
        """百分比变化"""
        result = series.pct_change(periods=periods)
        code = f"df['{series.name}_pct_change'] = df['{series.name}'].pct_change(periods={periods})"
        return result, code

    @staticmethod
    def diff(series: pd.Series, periods: int = 1) -> Tuple[pd.Series, str]:
        """差分"""
        result = series.diff(periods=periods)
        code = f"df['{series.name}_diff'] = df['{series.name}'].diff(periods={periods})"
        return result, code

    @staticmethod
    def shift(series: pd.Series, periods: int = 1) -> Tuple[pd.Series, str]:
        """移位 (lag/lead)"""
        result = series.shift(periods=periods)
        direction = "lag" if periods > 0 else "lead"
        code = f"df['{series.name}_{direction}_{abs(periods)}'] = df['{series.name}'].shift(periods={periods})"
        return result, code


class NumericProcessor:
    """数值处理统一入口"""

    def __init__(self):
        self.binner = NumericBinner()
        self.normalizer = NumericNormalizer()
        self.rolling = RollingWindow()
        self.cumulative = CumulativeOperations()

    def process(
        self,
        df: pd.DataFrame,
        column: str,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[pd.DataFrame, str]:
        """统一处理入口

        Args:
            df: 数据框
            column: 目标列
            operation: 操作名
            params: 额外参数

        Returns:
            (结果数据框, pandas 代码)
        """
        params = params or {}
        series = pd.to_numeric(df[column], errors="coerce")
        result_df = df.copy()

        op_map = {
            # 分箱
            "bin_equal_width": lambda: self.binner.equal_width(series, bins=params.get("bins", 5)),
            "bin_equal_freq": lambda: self.binner.equal_freq(series, q=params.get("q", 5)),
            "bin_custom": lambda: self.binner.custom(series, boundaries=params["boundaries"], labels=params.get("labels")),
            # 标准化
            "normalize_minmax": lambda: self.normalizer.min_max(series),
            "normalize_zscore": lambda: self.normalizer.z_score(series),
            "normalize_robust": lambda: self.normalizer.robust(series),
            "winsorize": lambda: self.normalizer.winsorize(series, lower=params.get("lower", 0.05), upper=params.get("upper", 0.95)),
            "log_transform": lambda: self.normalizer.log_transform(series),
            # 滚动窗口
            "rolling_mean": lambda: self.rolling.rolling_mean(series, window=params.get("window", 3)),
            "rolling_sum": lambda: self.rolling.rolling_sum(series, window=params.get("window", 3)),
            "rolling_std": lambda: self.rolling.rolling_std(series, window=params.get("window", 3)),
            "rolling_min": lambda: self.rolling.rolling_min(series, window=params.get("window", 3)),
            "rolling_max": lambda: self.rolling.rolling_max(series, window=params.get("window", 3)),
            "ewm_mean": lambda: self.rolling.ewm_mean(series, span=params.get("span", 5)),
            # 累积
            "cumsum": lambda: self.cumulative.cumsum(series),
            "cumprod": lambda: self.cumulative.cumprod(series),
            "cummax": lambda: self.cumulative.cummax(series),
            "cummin": lambda: self.cumulative.cummin(series),
            "pct_change": lambda: self.cumulative.pct_change(series, periods=params.get("periods", 1)),
            "diff": lambda: self.cumulative.diff(series, periods=params.get("periods", 1)),
            "shift": lambda: self.cumulative.shift(series, periods=params.get("periods", 1)),
        }

        if operation not in op_map:
            raise ValueError(f"不支持的数值操作: {operation}")

        result_series, code = op_map[operation]()
        new_col = f"{column}_{operation}"
        result_df[new_col] = result_series
        return result_df, code
