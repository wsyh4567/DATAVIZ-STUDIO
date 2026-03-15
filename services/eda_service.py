# -*- coding: utf-8 -*-
"""Unified EDA service for Data Canvas and report generation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.stats_service import StatsService


class EDAService:
    """Generate a stable EDA report structure for the active dataset."""

    SAMPLE_RANDOM_STATE = 42
    SAMPLE_ROW_THRESHOLD = 50_000
    SAMPLE_MEMORY_THRESHOLD_MB = 50

    @classmethod
    def analyze_dataset(
        cls,
        df: pd.DataFrame,
        mode: str = "full",
        sample_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Analyze the dataset and return a stable EDA report."""
        original_df = df.copy()
        analyzed_df = original_df
        used_sampling = False
        reason = "全量分析"

        if mode == "sample" and len(original_df) > 0:
            effective_size = cls.recommended_sample_size(len(original_df), sample_size)
            if effective_size < len(original_df):
                analyzed_df = original_df.sample(
                    n=effective_size,
                    random_state=cls.SAMPLE_RANDOM_STATE,
                )
                used_sampling = True
                reason = "数据量较大，使用随机采样提升分析速度"
            else:
                effective_size = len(original_df)
        else:
            effective_size = len(original_df)

        overview = cls._compute_overview(original_df)
        sample_meta = {
            "mode": "sample" if used_sampling else "full",
            "used_sampling": used_sampling,
            "sample_rows": int(len(analyzed_df)),
            "sample_ratio": round(len(analyzed_df) / max(len(original_df), 1), 4),
            "reason": reason,
        }

        numeric_profiles = cls._profile_numeric_columns(analyzed_df)
        categorical_profiles = cls._profile_categorical_columns(analyzed_df)
        datetime_profiles = cls._profile_datetime_columns(analyzed_df)
        missingness = cls._analyze_missingness(analyzed_df)
        relationship_findings = cls._analyze_relationships(
            analyzed_df, numeric_profiles, categorical_profiles
        )
        quality_alerts = cls._build_alerts(
            analyzed_df,
            overview,
            missingness,
            numeric_profiles,
            categorical_profiles,
            datetime_profiles,
            relationship_findings,
        )

        quick_distributions = {
            "numeric": [{"name": item["name"]} for item in numeric_profiles[:3]],
            "categorical": [{"name": item["name"]} for item in categorical_profiles[:3]],
        }

        return {
            "overview": overview,
            "sample_meta": sample_meta,
            "quality_alerts": quality_alerts,
            "missingness": missingness,
            "numeric_profiles": numeric_profiles,
            "categorical_profiles": categorical_profiles,
            "datetime_profiles": datetime_profiles,
            "relationship_findings": relationship_findings,
            "quick_distributions": quick_distributions,
        }

    @classmethod
    def should_recommend_sampling(cls, rows: int, memory_mb: float) -> bool:
        return rows > cls.SAMPLE_ROW_THRESHOLD or memory_mb > cls.SAMPLE_MEMORY_THRESHOLD_MB

    @classmethod
    def recommended_sample_size(
        cls,
        rows: int,
        sample_size: Optional[int] = None,
    ) -> int:
        recommended = min(10_000, max(2_000, int(rows * 0.2))) if rows > 0 else 0
        if sample_size is None:
            return min(rows, recommended)
        return max(1, min(int(sample_size), rows))

    @staticmethod
    def create_missing_bar_chart(report: Dict[str, Any]) -> go.Figure:
        columns = report["missingness"]["columns"]
        if not columns:
            fig = go.Figure()
            fig.add_annotation(
                text="无缺失值",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16, color="#38A169"),
            )
            return EDAService._apply_light_layout(fig, height=260)

        data = pd.DataFrame(columns[:10]).sort_values("missing_pct", ascending=True)
        fig = px.bar(
            data,
            x="missing_count",
            y="name",
            orientation="h",
            color="missing_pct",
            color_continuous_scale=["#FBD38D", "#F6AD55", "#DD6B20"],
            labels={"missing_count": "缺失数", "name": "字段"},
        )
        fig.update_coloraxes(showscale=False)
        return EDAService._apply_light_layout(fig, height=max(260, len(data) * 28))

    @staticmethod
    def create_missing_heatmap(report: Dict[str, Any]) -> go.Figure:
        matrix_info = report["missingness"]["cooccurrence"]
        labels = matrix_info["columns"]
        matrix = matrix_info["matrix"]
        if not labels or not matrix:
            fig = go.Figure()
            fig.add_annotation(
                text="没有足够的缺失模式用于展示",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="#718096"),
            )
            return EDAService._apply_light_layout(fig, height=300)

        fig = px.imshow(
            np.array(matrix),
            x=labels,
            y=labels,
            text_auto=True,
            color_continuous_scale="Oranges",
            aspect="auto",
        )
        return EDAService._apply_light_layout(fig, height=max(320, len(labels) * 36))

    @staticmethod
    def create_correlation_heatmap(report: Dict[str, Any]) -> go.Figure:
        pairs = report["relationship_findings"]["numeric_pairs"]
        labels = sorted({item["var1"] for item in pairs} | {item["var2"] for item in pairs})
        if len(labels) < 2:
            fig = go.Figure()
            fig.add_annotation(
                text="数值字段不足，无法生成相关性热力图",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color="#718096"),
            )
            return EDAService._apply_light_layout(fig, height=280)

        matrix = np.eye(len(labels))
        lookup = {(item["var1"], item["var2"]): item["correlation"] for item in pairs}
        lookup.update({(item["var2"], item["var1"]): item["correlation"] for item in pairs})
        for row_index, row_name in enumerate(labels):
            for col_index, col_name in enumerate(labels):
                if row_name == col_name:
                    continue
                matrix[row_index, col_index] = lookup.get((row_name, col_name), 0)

        fig = px.imshow(
            matrix,
            x=labels,
            y=labels,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
        )
        return EDAService._apply_light_layout(fig, height=max(320, len(labels) * 40))

    @staticmethod
    def create_numeric_distribution(series: pd.Series) -> go.Figure:
        clean = pd.to_numeric(series, errors="coerce").dropna()
        fig = px.histogram(
            x=clean,
            nbins=min(40, max(10, int(len(clean) ** 0.5))) if len(clean) else 10,
            color_discrete_sequence=["#FF6B35"],
            labels={"x": str(series.name), "count": "频次"},
        )
        fig.update_traces(marker_line_width=0)
        return EDAService._apply_light_layout(fig, height=220)

    @staticmethod
    def create_categorical_distribution(series: pd.Series) -> go.Figure:
        freq = series.dropna().astype(str).value_counts().head(8)
        fig = px.bar(
            x=freq.values,
            y=freq.index,
            orientation="h",
            color_discrete_sequence=["#ED8936"],
            labels={"x": "计数", "y": str(series.name)},
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        return EDAService._apply_light_layout(fig, height=max(220, len(freq) * 28))

    @staticmethod
    def _compute_overview(df: pd.DataFrame) -> Dict[str, Any]:
        total_cells = int(df.shape[0] * df.shape[1])
        missing_cells = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        memory_mb = float(df.memory_usage(deep=True).sum() / (1024 * 1024))
        missing_pct = round(missing_cells / max(total_cells, 1) * 100, 2)
        duplicate_pct = round(duplicate_rows / max(len(df), 1) * 100, 2)
        quality_score = round(
            max(0.0, 100 - missing_pct * 0.5 - min(25, duplicate_pct * 0.8)),
            1,
        )
        return {
            "rows": int(len(df)),
            "cols": int(len(df.columns)),
            "memory_mb": round(memory_mb, 2),
            "missing_pct": missing_pct,
            "duplicate_pct": duplicate_pct,
            "quality_score": quality_score,
        }

    @staticmethod
    def _profile_numeric_columns(df: pd.DataFrame) -> List[Dict[str, Any]]:
        profiles: List[Dict[str, Any]] = []
        for column in df.select_dtypes(include=[np.number]).columns:
            clean = pd.to_numeric(df[column], errors="coerce").dropna()
            if clean.empty:
                continue
            q1 = clean.quantile(0.25)
            q3 = clean.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                outlier_mask = pd.Series(False, index=clean.index)
            else:
                outlier_mask = (clean < q1 - 1.5 * iqr) | (clean > q3 + 1.5 * iqr)
            profiles.append(
                {
                    "name": column,
                    "dtype": str(df[column].dtype),
                    "missing_pct": round(df[column].isna().mean() * 100, 2),
                    "unique_count": int(df[column].nunique(dropna=True)),
                    "mean": round(float(clean.mean()), 4),
                    "std": round(float(clean.std()), 4) if len(clean) > 1 else 0.0,
                    "q1": round(float(q1), 4),
                    "median": round(float(clean.median()), 4),
                    "q3": round(float(q3), 4),
                    "min": round(float(clean.min()), 4),
                    "max": round(float(clean.max()), 4),
                    "skewness": round(float(clean.skew()), 4) if len(clean) > 2 else 0.0,
                    "kurtosis": round(float(clean.kurtosis()), 4) if len(clean) > 3 else 0.0,
                    "outlier_pct": round(float(outlier_mask.mean() * 100), 2),
                    "zero_pct": round(float((clean == 0).mean() * 100), 2),
                    "negative_pct": round(float((clean < 0).mean() * 100), 2),
                    "is_near_constant": bool(clean.nunique() <= 2 or clean.std() == 0),
                }
            )
        profiles.sort(key=lambda item: item["missing_pct"], reverse=True)
        return profiles

    @staticmethod
    def _profile_categorical_columns(df: pd.DataFrame) -> List[Dict[str, Any]]:
        profiles: List[Dict[str, Any]] = []
        for column in df.select_dtypes(include=["object", "category", "string"]).columns:
            clean = df[column].dropna().astype(str)
            if clean.empty:
                continue
            counts = clean.value_counts()
            unique_count = int(clean.nunique())
            blank_pct = float(clean.str.strip().eq("").mean() * 100)
            unique_ratio = unique_count / max(len(clean), 1)
            avg_length = float(clean.str.len().mean())
            is_id_like = unique_ratio > 0.9 and avg_length >= 4
            is_high_cardinality = unique_ratio > 0.5 or unique_count > 50
            profiles.append(
                {
                    "name": column,
                    "dtype": str(df[column].dtype),
                    "missing_pct": round(df[column].isna().mean() * 100, 2),
                    "unique_count": unique_count,
                    "unique_pct": round(unique_ratio * 100, 2),
                    "top_value": str(counts.index[0]),
                    "top_pct": round(float(counts.iloc[0] / len(clean) * 100), 2),
                    "avg_length": round(avg_length, 1),
                    "blank_pct": round(blank_pct, 2),
                    "is_id_like": is_id_like,
                    "is_high_cardinality": is_high_cardinality,
                }
            )
        profiles.sort(key=lambda item: item["unique_count"], reverse=True)
        return profiles

    @staticmethod
    def _profile_datetime_columns(df: pd.DataFrame) -> List[Dict[str, Any]]:
        profiles: List[Dict[str, Any]] = []
        for column in df.columns:
            series = df[column]
            if not pd.api.types.is_datetime64_any_dtype(series):
                continue
            clean = series.dropna().sort_values()
            if clean.empty:
                continue
            inferred_freq = None
            if len(clean) >= 3:
                try:
                    inferred_freq = pd.infer_freq(clean.head(20))
                except ValueError:
                    inferred_freq = None
            profiles.append(
                {
                    "name": column,
                    "dtype": str(series.dtype),
                    "missing_pct": round(series.isna().mean() * 100, 2),
                    "unique_count": int(series.nunique(dropna=True)),
                    "min_date": str(clean.min()),
                    "max_date": str(clean.max()),
                    "range_days": int((clean.max() - clean.min()).days),
                    "inferred_freq": inferred_freq or "未识别",
                }
            )
        return profiles

    @staticmethod
    def _analyze_missingness(df: pd.DataFrame) -> Dict[str, Any]:
        missing = df.isna().sum().sort_values(ascending=False)
        missing_columns = [
            {
                "name": column,
                "missing_count": int(count),
                "missing_pct": round(float(count / max(len(df), 1) * 100), 2),
            }
            for column, count in missing.items()
            if count > 0
        ]

        candidate_columns = [item["name"] for item in missing_columns[:8]]
        matrix: List[List[int]] = []
        if candidate_columns:
            bool_df = df[candidate_columns].isna().astype(int)
            cooccurrence = bool_df.T.dot(bool_df)
            matrix = cooccurrence.values.tolist()

        summary = "数据中没有缺失值。"
        if missing_columns:
            top = missing_columns[0]
            summary = (
                f"共有 {len(missing_columns)} 个字段存在缺失，"
                f"其中 {top['name']} 缺失率最高，为 {top['missing_pct']:.1f}%。"
            )

        return {
            "columns": missing_columns,
            "cooccurrence": {"columns": candidate_columns, "matrix": matrix},
            "summary": summary,
        }

    @staticmethod
    def _analyze_relationships(
        df: pd.DataFrame,
        numeric_profiles: List[Dict[str, Any]],
        categorical_profiles: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        numeric_pairs = []
        if len(numeric_profiles) >= 2:
            corr_pairs = StatsService.correlation_pairs(df, threshold=0.5)
            numeric_pairs = [
                {
                    "var1": item["var1"],
                    "var2": item["var2"],
                    "correlation": round(float(item["correlation"]), 4),
                    "strength": item["strength"],
                }
                for item in corr_pairs[:10]
            ]

        categorical_numeric_pairs = []
        cat_columns = [item["name"] for item in categorical_profiles[:8]]
        num_columns = [item["name"] for item in numeric_profiles[:8]]
        for cat_column in cat_columns:
            grouped = df.groupby(cat_column, dropna=False)
            if grouped.ngroups < 2 or grouped.ngroups > 20:
                continue
            for num_column in num_columns:
                series = pd.to_numeric(df[num_column], errors="coerce")
                stats_df = (
                    pd.DataFrame({cat_column: df[cat_column], num_column: series})
                    .dropna()
                    .groupby(cat_column)[num_column]
                    .agg(["mean", "count"])
                    .sort_values("mean", ascending=False)
                )
                if len(stats_df) < 2:
                    continue
                spread = float(stats_df["mean"].max() - stats_df["mean"].min())
                if spread <= 0:
                    continue
                categorical_numeric_pairs.append(
                    {
                        "category": cat_column,
                        "numeric": num_column,
                        "top_group": str(stats_df.index[0]),
                        "bottom_group": str(stats_df.index[-1]),
                        "mean_spread": round(spread, 4),
                    }
                )
        categorical_numeric_pairs.sort(key=lambda item: item["mean_spread"], reverse=True)

        categorical_pairs = []
        for first_index, first_column in enumerate(cat_columns):
            for second_column in cat_columns[first_index + 1:]:
                cross_tab = pd.crosstab(df[first_column], df[second_column])
                if cross_tab.empty:
                    continue
                max_value = int(cross_tab.to_numpy().max())
                if max_value <= 1:
                    continue
                row_name, col_name = cross_tab.stack().idxmax()
                categorical_pairs.append(
                    {
                        "var1": first_column,
                        "var2": second_column,
                        "top_combination": f"{row_name} / {col_name}",
                        "count": max_value,
                    }
                )
        categorical_pairs.sort(key=lambda item: item["count"], reverse=True)

        return {
            "numeric_pairs": numeric_pairs,
            "categorical_numeric_pairs": categorical_numeric_pairs[:8],
            "categorical_pairs": categorical_pairs[:8],
        }

    @staticmethod
    def _build_alerts(
        df: pd.DataFrame,
        overview: Dict[str, Any],
        missingness: Dict[str, Any],
        numeric_profiles: List[Dict[str, Any]],
        categorical_profiles: List[Dict[str, Any]],
        datetime_profiles: List[Dict[str, Any]],
        relationship_findings: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []

        if overview["missing_pct"] > 0:
            for item in missingness["columns"][:3]:
                if item["missing_pct"] >= 30:
                    alerts.append(
                        {
                            "severity": "warning",
                            "type": "missing",
                            "title": f"{item['name']} 缺失率偏高",
                            "message": f"缺失率为 {item['missing_pct']:.1f}%，建议先处理缺失值再分析。",
                            "column": item["name"],
                            "suggested_action": "考虑填补、删除或标记缺失来源。",
                        }
                    )

        for item in numeric_profiles:
            if item["is_near_constant"]:
                alerts.append(
                    {
                        "severity": "info",
                        "type": "constant",
                        "title": f"{item['name']} 接近常量列",
                        "message": "唯一值极少，建模和分析贡献通常有限。",
                        "column": item["name"],
                        "suggested_action": "确认是否需要保留该字段。",
                    }
                )
            if abs(item["skewness"]) >= 1:
                alerts.append(
                    {
                        "severity": "info",
                        "type": "skewness",
                        "title": f"{item['name']} 偏态明显",
                        "message": f"偏度为 {item['skewness']:.2f}，分布不对称。",
                        "column": item["name"],
                        "suggested_action": "可考虑对数变换或分箱。",
                    }
                )
            if item["outlier_pct"] >= 5:
                alerts.append(
                    {
                        "severity": "warning",
                        "type": "outlier",
                        "title": f"{item['name']} 异常值占比偏高",
                        "message": f"IQR 检测异常值占比 {item['outlier_pct']:.1f}%。",
                        "column": item["name"],
                        "suggested_action": "建议核查业务口径或使用稳健统计方法。",
                    }
                )

        for item in categorical_profiles[:6]:
            if item["is_id_like"]:
                alerts.append(
                    {
                        "severity": "info",
                        "type": "id_like",
                        "title": f"{item['name']} 疑似 ID 列",
                        "message": f"唯一值占比 {item['unique_pct']:.1f}%，更像标识字段。",
                        "column": item["name"],
                        "suggested_action": "避免直接用于聚合或类别比较。",
                    }
                )
            elif item["is_high_cardinality"]:
                alerts.append(
                    {
                        "severity": "info",
                        "type": "cardinality",
                        "title": f"{item['name']} 基数较高",
                        "message": f"唯一值数量 {item['unique_count']}，分组后容易碎片化。",
                        "column": item["name"],
                        "suggested_action": "可先归并类别或只保留 top N。",
                    }
                )
            if item["blank_pct"] > 0:
                alerts.append(
                    {
                        "severity": "warning",
                        "type": "format",
                        "title": f"{item['name']} 含空白字符串",
                        "message": f"空白字符串占比 {item['blank_pct']:.1f}%。",
                        "column": item["name"],
                        "suggested_action": "将空白字符串统一为真正的缺失值。",
                    }
                )

        for item in datetime_profiles:
            if item["range_days"] <= 1:
                alerts.append(
                    {
                        "severity": "info",
                        "type": "datetime_gap",
                        "title": f"{item['name']} 时间跨度很短",
                        "message": f"时间跨度仅 {item['range_days']} 天。",
                        "column": item["name"],
                        "suggested_action": "确认字段是否适合做时序分析。",
                    }
                )

        for pair in relationship_findings["numeric_pairs"][:3]:
            if abs(pair["correlation"]) >= 0.85:
                alerts.append(
                    {
                        "severity": "warning",
                        "type": "correlation",
                        "title": f"{pair['var1']} 与 {pair['var2']} 高度相关",
                        "message": f"相关系数为 {pair['correlation']:.2f}。",
                        "column": f"{pair['var1']} / {pair['var2']}",
                        "suggested_action": "建模前注意多重共线性。",
                    }
                )

        severity_order = {"warning": 0, "info": 1}
        alerts.sort(key=lambda item: (severity_order.get(item["severity"], 9), item["title"]))
        return alerts[:12]

    @staticmethod
    def _apply_light_layout(fig: go.Figure, height: int = 260) -> go.Figure:
        fig.update_layout(
            template="plotly_white",
            height=height,
            margin=dict(l=16, r=16, t=24, b=16),
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="rgba(255,255,255,0)",
            font=dict(family="Inter, Microsoft YaHei UI, sans-serif", size=11, color="#1A202C"),
            xaxis=dict(
                title=None,
                gridcolor="rgba(226, 232, 240, 0.9)",
                zeroline=False,
            ),
            yaxis=dict(
                title=None,
                gridcolor="rgba(226, 232, 240, 0.9)",
                zeroline=False,
            ),
            legend=dict(
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(226, 232, 240, 1)",
                borderwidth=1,
                font=dict(size=10),
            ),
        )
        return fig
