# -*- coding: utf-8 -*-
"""数据概况分析服务

为每列生成详细的统计信息、分布概况和数据质量预警。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ProfilingService:
    """数据概况分析服务"""

    @staticmethod
    def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """生成完整的数据概况

        Returns:
            {
                "overview": {...},
                "columns": {col_name: {...}, ...},
                "alerts": [...],
                "correlation": pd.DataFrame | None,
            }
        """
        overview = ProfilingService._compute_overview(df)
        columns = {}
        for col in df.columns:
            columns[col] = ProfilingService.profile_column(df[col])
        alerts = ProfilingService.get_alerts(df)

        # 相关性矩阵
        numeric_df = df.select_dtypes(include=[np.number])
        correlation = None
        if len(numeric_df.columns) >= 2:
            correlation = numeric_df.corr()

        return {
            "overview": overview,
            "columns": columns,
            "alerts": alerts,
            "correlation": correlation,
        }

    @staticmethod
    def _compute_overview(df: pd.DataFrame) -> Dict[str, Any]:
        """计算数据集概览"""
        mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        missing_cells = int(df.isnull().sum().sum())
        total_cells = int(df.shape[0] * df.shape[1])
        dup_rows = int(df.duplicated().sum())

        return {
            "rows": len(df),
            "cols": len(df.columns),
            "memory_mb": round(mem_mb, 2),
            "missing_cells": missing_cells,
            "total_cells": total_cells,
            "missing_pct": round(missing_cells / max(total_cells, 1) * 100, 1),
            "duplicate_rows": dup_rows,
            "duplicate_pct": round(dup_rows / max(len(df), 1) * 100, 1),
            "numeric_cols": len(df.select_dtypes(include=[np.number]).columns),
            "categorical_cols": len(df.select_dtypes(include=["object", "category"]).columns),
            "datetime_cols": len(df.select_dtypes(include=["datetime64"]).columns),
        }

    @staticmethod
    def profile_column(series: pd.Series) -> Dict[str, Any]:
        """单列深度分析"""
        profile: Dict[str, Any] = {
            "name": series.name,
            "dtype": str(series.dtype),
            "count": int(series.count()),
            "missing": int(series.isnull().sum()),
            "missing_pct": round(series.isnull().sum() / max(len(series), 1) * 100, 1),
            "unique": int(series.nunique()),
            "unique_pct": round(series.nunique() / max(series.count(), 1) * 100, 1),
        }

        if pd.api.types.is_numeric_dtype(series.dtype):
            profile["type"] = "numeric"
            clean = series.dropna()
            if len(clean) > 0:
                profile.update({
                    "mean": round(float(clean.mean()), 4),
                    "std": round(float(clean.std()), 4),
                    "min": round(float(clean.min()), 4),
                    "q25": round(float(clean.quantile(0.25)), 4),
                    "median": round(float(clean.median()), 4),
                    "q75": round(float(clean.quantile(0.75)), 4),
                    "max": round(float(clean.max()), 4),
                    "skewness": round(float(clean.skew()), 4),
                    "kurtosis": round(float(clean.kurtosis()), 4),
                    "zeros": int((clean == 0).sum()),
                    "negatives": int((clean < 0).sum()),
                })
                # 异常值检测 (IQR)
                q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
                iqr = q3 - q1
                outliers = ((clean < q1 - 1.5 * iqr) | (clean > q3 + 1.5 * iqr)).sum()
                profile["outliers"] = int(outliers)
        elif pd.api.types.is_datetime64_any_dtype(series.dtype):
            profile["type"] = "datetime"
            clean = series.dropna()
            if len(clean) > 0:
                profile.update({
                    "min_date": str(clean.min()),
                    "max_date": str(clean.max()),
                    "range_days": int((clean.max() - clean.min()).days),
                })
        else:
            profile["type"] = "categorical"
            clean = series.dropna().astype(str)
            if len(clean) > 0:
                freq = clean.value_counts()
                profile.update({
                    "top_values": freq.head(10).to_dict(),
                    "most_common": str(freq.index[0]),
                    "most_common_freq": int(freq.iloc[0]),
                    "least_common": str(freq.index[-1]) if len(freq) > 1 else str(freq.index[0]),
                    "avg_length": round(float(clean.str.len().mean()), 1),
                })

        return profile

    @staticmethod
    def get_alerts(df: pd.DataFrame) -> List[Dict[str, str]]:
        """自动检测数据质量预警"""
        alerts = []

        for col in df.columns:
            series = df[col]
            missing_pct = series.isnull().sum() / max(len(series), 1) * 100

            # 高缺失率
            if missing_pct > 30:
                alerts.append({
                    "type": "warning",
                    "icon": "⚠️",
                    "column": col,
                    "message": f"「{col}」缺失率 {missing_pct:.1f}%，建议处理后再分析",
                })

            # 常量列
            if series.nunique() <= 1:
                alerts.append({
                    "type": "info",
                    "icon": "ℹ️",
                    "column": col,
                    "message": f"「{col}」为常量列（唯一值仅 {series.nunique()} 个），对分析无贡献",
                })

            # 高基数列
            if series.nunique() == len(series) and not pd.api.types.is_numeric_dtype(series):
                alerts.append({
                    "type": "info",
                    "icon": "🔤",
                    "column": col,
                    "message": f"「{col}」每行值都不同（可能是 ID 列），不适合做分组分析",
                })

            # 数值列异常值
            if pd.api.types.is_numeric_dtype(series.dtype):
                clean = series.dropna()
                if len(clean) > 10:
                    q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
                    iqr = q3 - q1
                    if iqr > 0:
                        outlier_pct = ((clean < q1 - 1.5 * iqr) | (clean > q3 + 1.5 * iqr)).mean() * 100
                        if outlier_pct > 5:
                            alerts.append({
                                "type": "warning",
                                "icon": "📊",
                                "column": col,
                                "message": f"「{col}」异常值占比 {outlier_pct:.1f}%，可能影响分析结果",
                            })

        # 高相关列对
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) >= 2:
            corr = numeric_df.corr().abs()
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    if corr.iloc[i, j] > 0.95:
                        alerts.append({
                            "type": "info",
                            "icon": "🔗",
                            "column": f"{corr.columns[i]} & {corr.columns[j]}",
                            "message": f"「{corr.columns[i]}」与「{corr.columns[j]}」高度相关 (r={corr.iloc[i,j]:.3f})，可能存在多重共线性",
                        })

        return alerts

    @staticmethod
    def generate_column_chart(series: pd.Series) -> go.Figure:
        """为单列生成分布图"""
        if pd.api.types.is_numeric_dtype(series.dtype):
            clean = series.dropna()
            fig = px.histogram(
                x=clean, nbins=min(50, max(10, int(len(clean) ** 0.5))),
                labels={"x": str(series.name), "count": "频次"},
                color_discrete_sequence=["#6366F1"],
            )
            fig.update_layout(
                title="数值特征分布",
                margin=dict(l=20, r=20, t=40, b=20),
                height=300,
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=10),
                xaxis=dict(title=None),
                yaxis=dict(title=None),
            )
        else:
            clean = series.dropna().astype(str)
            freq = clean.value_counts().head(10)
            fig = px.bar(
                x=freq.values, y=freq.index, orientation="h",
                labels={"x": "计数", "y": str(series.name)},
                color_discrete_sequence=["#8B5CF6"],
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=30),
                height=max(150, len(freq) * 28),
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=10),
                xaxis=dict(title=None),
                yaxis=dict(title=None, autorange="reversed"),
            )

        return fig
