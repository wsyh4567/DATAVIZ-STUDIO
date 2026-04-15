# -*- coding: utf-8 -*-
"""智能图表推荐引擎

基于字段类型组合自动推荐最佳图表类型，附带推荐理由和适用场景。
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import List, Optional

import pandas as pd

from services.field_analyzer import infer_field_type, FieldType


@dataclass
class ChartRecommendation:
    """图表推荐结果"""
    chart_type: str        # 图表类型标识（对应 ChartType 枚举值）
    name: str              # 中文名称
    icon: str              # 表情图标
    reason: str            # 推荐理由
    score: int             # 推荐评分 (0-100)
    scene: str             # 适用场景


class ChartRecommender:
    """智能图表推荐器

    根据用户选择的字段类型组合，推荐最合适的图表类型。
    """

    # 字段类型组合 → 推荐规则
    _RULES = {
        # ── 双数值字段 ──────────────────────────────────
        ("measure", "measure"): [
            ChartRecommendation(
                chart_type="scatter", name="散点图", icon="bi bi-circle-fill",
                reason="展示两个数值变量之间的关系和分布趋势",
                score=95, scene="相关性分析、离群值发现"
            ),
            ChartRecommendation(
                chart_type="line", name="折线图", icon="bi bi-graph-up",
                reason="展示数值变量随另一数值变量的变化趋势",
                score=75, scene="趋势分析、对比走势"
            ),
            ChartRecommendation(
                chart_type="density_heatmap", name="密度热力图", icon="bi bi-grid-3x3-gap-fill",
                reason="数据点密集时，展示分布密度更清晰",
                score=70, scene="大数据量分布分析"
            ),
        ],
        # ── 维度 × 数值 ────────────────────────────────
        ("dimension", "measure"): [
            ChartRecommendation(
                chart_type="bar", name="柱状图", icon="bi bi-bar-chart",
                reason="对比不同类别的数值大小，直观清晰",
                score=95, scene="类别对比、排名分析"
            ),
            ChartRecommendation(
                chart_type="box", name="箱线图", icon="bi bi-box-seam",
                reason="展示各类别的数值分布（中位数、四分位、异常值）",
                score=80, scene="分组分布对比、异常值检测"
            ),
            ChartRecommendation(
                chart_type="violin", name="小提琴图", icon="bi bi-activity",
                reason="展示各类别的数据分布形态和密度",
                score=70, scene="分布形态对比"
            ),
        ],
        # ── 数值 × 维度 ────────────────────────────────
        ("measure", "dimension"): [
            ChartRecommendation(
                chart_type="hbar", name="水平柱状图", icon="bi bi-bar-chart",
                reason="类别名较长时用水平柱状图更易阅读",
                score=90, scene="清晰展示分类变量的度量值"
            ),
            ChartRecommendation(
                chart_type="bar", name="柱状图", icon="bi bi-bar-chart",
                reason="对比不同类别的数值大小",
                score=85, scene="类别对比分析"
            ),
            ChartRecommendation(
                chart_type="box", name="箱线图", icon="bi bi-box-seam",
                reason="展示各类别的数值分布特征",
                score=75, scene="分布对比分析"
            ),
        ],
        # ── 维度 × 维度 ────────────────────────────────
        ("dimension", "dimension"): [
            ChartRecommendation(
                chart_type="density_heatmap", name="热力图", icon="bi bi-grid-3x3-gap-fill",
                reason="展示两个分类变量的组合频率，发现关联模式",
                score=90, scene="交叉分析、关联discovering"
            ),
            ChartRecommendation(
                chart_type="bar", name="堆叠柱状图", icon="bi bi-bar-chart-steps",
                reason="展示一个分类变量在另一分类变量中的占比",
                score=80, scene="组成分析、占比对比"
            ),
            ChartRecommendation(
                chart_type="sunburst", name="旭日图", icon="bi bi-brightness-high",
                reason="展示层次化分类结构中的数量分布",
                score=65, scene="层次分析"
            ),
        ],
        # ── 时间 × 数值 ────────────────────────────────
        ("temporal", "measure"): [
            ChartRecommendation(
                chart_type="line", name="折线图", icon="bi bi-graph-up",
                reason="展示数值随时间的变化趋势，最经典的时序图表",
                score=98, scene="时间序列趋势分析"
            ),
            ChartRecommendation(
                chart_type="bar", name="柱状图", icon="bi bi-bar-chart",
                reason="展示各时间段的数值大小对比",
                score=70, scene="按时间段对比"
            ),
            ChartRecommendation(
                chart_type="scatter", name="散点图", icon="bi bi-circle-fill",
                reason="查看时间序列中的离群值和模式",
                score=60, scene="异常值发现"
            ),
        ],
        # ── 仅 X 轴（单数值） ──────────────────────────
        ("measure", None): [
            ChartRecommendation(
                chart_type="histogram", name="直方图", icon="bi bi-bar-chart",
                reason="查看单个数值变量的分布形态",
                score=95, scene="分布分析、正态性检查"
            ),
            ChartRecommendation(
                chart_type="box", name="箱线图", icon="bi bi-box-seam",
                reason="快速查看中位数、四分位和异常值",
                score=80, scene="快速统计概览"
            ),
            ChartRecommendation(
                chart_type="violin", name="小提琴图", icon="bi bi-activity",
                reason="查看数据密度分布的形态",
                score=70, scene="分布形态分析"
            ),
        ],
        # ── 仅 X 轴（单维度） ──────────────────────────
        ("dimension", None): [
            ChartRecommendation(
                chart_type="pie", name="饼图", icon="bi bi-pie-chart",
                reason="展示各类别在整体中的占比（类别 ≤ 8 时效果好）",
                score=85, scene="占比分析"
            ),
            ChartRecommendation(
                chart_type="bar", name="计数柱状图", icon="bi bi-bar-chart",
                reason="展示各类别的频次分布",
                score=90, scene="频率分析"
            ),
            ChartRecommendation(
                chart_type="treemap", name="矩形树图", icon="bi bi-diagram-3",
                reason="用面积展示各类别的占比关系",
                score=65, scene="多类别占比分析"
            ),
        ],
    }

    @classmethod
    def recommend(
        cls,
        df: pd.DataFrame,
        x: Optional[str] = None,
        y: Optional[str] = None,
        color: Optional[str] = None,
    ) -> List[ChartRecommendation]:
        """根据选定字段推荐最佳图表类型

        Args:
            df: 数据框
            x: X 轴字段名
            y: Y 轴字段名
            color: 颜色字段名（用于调整推荐权重）

        Returns:
            推荐列表（按评分降序，最多 3 个）
        """
        if df is None or df.empty:
            return []

        # 推断字段类型
        x_type = cls._get_role(df[x], axis="x") if x and x in df.columns else None
        y_type = cls._get_role(df[y], axis="y") if y and y in df.columns else None

        if x_type is None and y_type is None:
            return []

        # 查找匹配的规则
        key = (x_type, y_type)
        recommendations = [replace(rec) for rec in cls._RULES.get(key, [])]

        # 如果没有精确匹配，尝试反向
        if not recommendations:
            key_reversed = (y_type, x_type)
            recommendations = [replace(rec) for rec in cls._RULES.get(key_reversed, [])]

        # 如果有 color 字段，微调评分
        if color and recommendations:
            color_type = cls._get_role(df[color]) if color in df.columns else None
            if color_type == "dimension":
                for rec in recommendations:
                    if rec.chart_type in ("scatter", "bar", "line"):
                        rec.score = min(rec.score + 5, 100)

        # 根据数据特征调整推荐
        if x and x in df.columns:
            unique_x = df[x].nunique()
            total = len(df)

            # 数据量大时推荐密度图
            if total > 5000:
                for rec in recommendations:
                    if rec.chart_type == "density_heatmap":
                        rec.score = min(rec.score + 15, 100)

            # 类别太多时降低饼图评分
            if unique_x > 10:
                for rec in recommendations:
                    if rec.chart_type == "pie":
                        rec.score = max(rec.score - 30, 20)
                    if rec.chart_type == "treemap":
                        rec.score = min(rec.score + 10, 100)

        # 按评分降序排列，返回前 3 个
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:3]

    @staticmethod
    def _get_role(series: pd.Series, axis: Optional[str] = None) -> Optional[str]:
        """将 FieldType 映射为简化角色"""
        if axis == "y" and pd.api.types.is_numeric_dtype(series.dtype):
            # Y 轴数值字段在图表推荐场景中通常代表度量值，即使基数字段较小。
            return "measure"

        ft = infer_field_type(series)
        mapping = {
            FieldType.MEASURE: "measure",
            FieldType.DIMENSION: "dimension",
            FieldType.TEMPORAL: "temporal",
            FieldType.NOMINAL: "dimension",
        }
        return mapping.get(ft, "dimension")
