# -*- coding: utf-8 -*-
"""图表服务 — Python 优先架构

所有图表由 Python 后端生成，支持 Plotly 和 Seaborn 两种图表库。
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from enum import Enum
import io
import base64

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端


class ChartLibrary(Enum):
    """图表库枚举"""
    PLOTLY = "plotly"
    SEABORN = "seaborn"


class ChartType(Enum):
    """图表类型枚举"""
    # Plotly 和 Seaborn 通用
    scatter = "scatter"
    line = "line"
    bar = "bar"
    histogram = "histogram"
    box = "box"
    violin = "violin"

    # Plotly 特有
    scatter_3d = "scatter_3d"
    pie = "pie"
    sunburst = "sunburst"
    treemap = "treemap"
    funnel = "funnel"
    density_heatmap = "density_heatmap"

    # 新增 Plotly 图表
    area = "area"
    waterfall = "waterfall"
    radar = "radar"
    parallel = "parallel"
    parallel_cat = "parallel_cat"
    contour = "contour"
    surface_3d = "surface_3d"
    bar_polar = "bar_polar"
    splom = "splom"
    hbar = "hbar"

    # Seaborn 特有
    heatmap = "heatmap"
    pairplot = "pairplot"
    jointplot = "jointplot"
    regplot = "regplot"

    # 新增 Seaborn 图表
    kdeplot = "kdeplot"
    countplot = "countplot"
    rugplot = "rugplot"


class ChartService:
    """图表生成服务"""

    def __init__(self):
        self.library = ChartLibrary.PLOTLY
        self.code_history = []

    def set_library(self, library: ChartLibrary):
        """切换图表库"""
        self.library = library

    def create_chart(
        self,
        df: pd.DataFrame,
        chart_type: ChartType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建图表"""
        if self.library == ChartLibrary.PLOTLY:
            return self._create_plotly_chart(df, chart_type, params)
        else:
            return self._create_seaborn_chart(df, chart_type, params)

    def _apply_plotly_style(self, fig, style_params: Dict[str, Any]):
        """应用 Plotly 图表样式配置"""
        template = style_params.get('template', 'plotly_dark')
        title = style_params.get('title', None)
        show_legend = style_params.get('show_legend', True)
        show_grid = style_params.get('show_grid', True)
        width = style_params.get('width', None)
        height = style_params.get('height', None)
        color_scale = style_params.get('color_scale', None)

        layout_update = {
            'template': template,
            'showlegend': show_legend,
            'margin': dict(l=40, r=40, t=60, b=40),
        }

        # 根据模板设置背景色
        if template == 'plotly_dark':
            layout_update['paper_bgcolor'] = '#1B1D2A'
            layout_update['plot_bgcolor'] = '#262940'
            layout_update['font'] = dict(color='#F1F5F9', family='Inter, sans-serif')
        elif template == 'plotly_white':
            layout_update['paper_bgcolor'] = '#FFFFFF'
            layout_update['plot_bgcolor'] = '#FFFFFF'
        # 其他模板使用默认配色

        if title:
            layout_update['title'] = dict(text=title, x=0.5)

        if width:
            layout_update['width'] = int(width)
        if height:
            layout_update['height'] = int(height)

        fig.update_layout(**layout_update)

        if not show_grid:
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)

    def _create_plotly_chart(
        self,
        df: pd.DataFrame,
        chart_type: ChartType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用 Plotly 创建图表"""

        # 分离样式参数和图表参数
        style_keys = {'template', 'title', 'show_legend', 'show_grid', 'width', 'height', 'color_scale'}
        style_params = {k: v for k, v in params.items() if k in style_keys and v is not None}
        chart_params = {k: v for k, v in params.items() if k not in style_keys and v is not None}

        # px 函数映射
        chart_functions = {
            ChartType.scatter: px.scatter,
            ChartType.line: px.line,
            ChartType.bar: px.bar,
            ChartType.histogram: px.histogram,
            ChartType.box: px.box,
            ChartType.violin: px.violin,
            ChartType.scatter_3d: px.scatter_3d,
            ChartType.pie: px.pie,
            ChartType.sunburst: px.sunburst,
            ChartType.treemap: px.treemap,
            ChartType.funnel: px.funnel,
            ChartType.density_heatmap: px.density_heatmap,
            ChartType.area: px.area,
            ChartType.contour: px.density_contour,
            ChartType.bar_polar: px.bar_polar,
            ChartType.splom: px.scatter_matrix,
            ChartType.parallel: px.parallel_coordinates,
            ChartType.parallel_cat: px.parallel_categories,
        }

        # 处理需要特殊逻辑的图表
        if chart_type == ChartType.hbar:
            chart_params['orientation'] = 'h'
            fig = px.bar(df, **chart_params)

        elif chart_type == ChartType.waterfall:
            x = chart_params.get('x')
            y = chart_params.get('y')
            if x and y:
                fig = go.Figure(go.Waterfall(
                    x=df[x].tolist(),
                    y=df[y].tolist(),
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                ))
                fig.update_layout(title=f"瀑布图: {y} by {x}")
            else:
                raise ValueError("瀑布图需要 x 和 y 参数")

        elif chart_type == ChartType.radar:
            x = chart_params.get('x')
            y = chart_params.get('y')
            color = chart_params.get('color')
            if x and y:
                if color and color in df.columns:
                    fig = go.Figure()
                    for group_name in df[color].unique():
                        group_df = df[df[color] == group_name]
                        fig.add_trace(go.Scatterpolar(
                            r=group_df[y].tolist(),
                            theta=group_df[x].tolist(),
                            fill='toself',
                            name=str(group_name),
                        ))
                else:
                    fig = go.Figure(go.Scatterpolar(
                        r=df[y].tolist(),
                        theta=df[x].tolist(),
                        fill='toself',
                    ))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
            else:
                raise ValueError("雷达图需要 x 和 y 参数")

        elif chart_type == ChartType.surface_3d:
            x = chart_params.get('x')
            y = chart_params.get('y')
            z = chart_params.get('z') or chart_params.get('color')
            if x and y and z:
                pivot = df.pivot_table(index=y, columns=x, values=z, aggfunc='mean')
                fig = go.Figure(data=[go.Surface(
                    z=pivot.values,
                    x=pivot.columns.tolist(),
                    y=pivot.index.tolist(),
                )])
                fig.update_layout(scene=dict(
                    xaxis_title=x, yaxis_title=y, zaxis_title=z
                ))
            else:
                raise ValueError("3D曲面图需要 x, y 和 z(color) 参数")

        else:
            chart_func = chart_functions.get(chart_type)
            if not chart_func:
                raise ValueError(f"不支持的 Plotly 图表类型: {chart_type}")

            # 对 parallel_coordinates 和 scatter_matrix，需要特别处理参数
            if chart_type == ChartType.parallel:
                valid_params = {}
                if 'color' in chart_params:
                    valid_params['color'] = chart_params['color']
                fig = chart_func(df, **valid_params)
            elif chart_type == ChartType.parallel_cat:
                valid_params = {}
                if 'color' in chart_params:
                    valid_params['color'] = chart_params['color']
                fig = chart_func(df, **valid_params)
            elif chart_type == ChartType.splom:
                valid_params = {}
                if 'color' in chart_params:
                    valid_params['color'] = chart_params['color']
                fig = chart_func(df, **valid_params)
            else:
                fig = chart_func(df, **chart_params)

        # 应用样式
        self._apply_plotly_style(fig, style_params if style_params else {
            'template': 'plotly_dark'
        })

        return {
            'chart': fig.to_json(),
            'library': 'plotly'
        }

    def _create_seaborn_chart(
        self,
        df: pd.DataFrame,
        chart_type: ChartType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用 Seaborn 创建图表"""

        # 分离样式参数
        style_keys = {'template', 'title', 'show_legend', 'show_grid', 'width', 'height', 'color_scale'}
        style_params = {k: v for k, v in params.items() if k in style_keys and v is not None}
        chart_params = {k: v for k, v in params.items() if k not in style_keys and v is not None}

        # 设置样式
        sns.set_theme(style="darkgrid")
        plt.rcParams['figure.facecolor'] = '#1B1D2A'
        plt.rcParams['axes.facecolor'] = '#262940'
        plt.rcParams['text.color'] = '#F1F5F9'
        plt.rcParams['axes.labelcolor'] = '#F1F5F9'
        plt.rcParams['xtick.color'] = '#F1F5F9'
        plt.rcParams['ytick.color'] = '#F1F5F9'

        fig_width = int(style_params.get('width', 800)) / 80
        fig_height = int(style_params.get('height', 480)) / 80

        # 特殊多面板图表（pairplot, jointplot 自带 figure）
        needs_fig = True

        if chart_type == ChartType.pairplot:
            needs_fig = False
            pp_params = {}
            if 'hue' in chart_params:
                pp_params['hue'] = chart_params['hue']
            if 'palette' in chart_params:
                pp_params['palette'] = chart_params['palette']
            g = sns.pairplot(df, **pp_params)
            fig = g.figure
            fig.set_facecolor('#1B1D2A')

        elif chart_type == ChartType.jointplot:
            needs_fig = False
            jp_params = {}
            for k in ('x', 'y', 'hue'):
                if k in chart_params:
                    jp_params[k] = chart_params[k]
            g = sns.jointplot(data=df, **jp_params)
            fig = g.figure
            fig.set_facecolor('#1B1D2A')

        else:
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))

            if chart_type == ChartType.scatter:
                sns.scatterplot(data=df, ax=ax, **chart_params)
            elif chart_type == ChartType.line:
                sns.lineplot(data=df, ax=ax, **chart_params)
            elif chart_type == ChartType.bar:
                sns.barplot(data=df, ax=ax, **chart_params)
            elif chart_type == ChartType.histogram:
                sns.histplot(data=df, ax=ax, **chart_params)
            elif chart_type == ChartType.box:
                sns.boxplot(data=df, ax=ax, **chart_params)
            elif chart_type == ChartType.violin:
                sns.violinplot(data=df, ax=ax, **chart_params)
            elif chart_type == ChartType.heatmap:
                pivot_data = df.pivot_table(
                    index=chart_params.get('y'),
                    columns=chart_params.get('x'),
                    values=chart_params.get('values'),
                    aggfunc='mean'
                )
                sns.heatmap(pivot_data, ax=ax, cmap=chart_params.get('palette', 'viridis'))
            elif chart_type == ChartType.kdeplot:
                kde_params = {k: v for k, v in chart_params.items() if k in ('x', 'y', 'hue')}
                sns.kdeplot(data=df, ax=ax, fill=True, **kde_params)
            elif chart_type == ChartType.regplot:
                reg_params = {k: v for k, v in chart_params.items() if k in ('x', 'y')}
                sns.regplot(data=df, ax=ax, **reg_params)
            elif chart_type == ChartType.countplot:
                cnt_params = {k: v for k, v in chart_params.items() if k in ('x', 'y', 'hue')}
                sns.countplot(data=df, ax=ax, **cnt_params)
            elif chart_type == ChartType.rugplot:
                rug_params = {k: v for k, v in chart_params.items() if k in ('x', 'y', 'hue')}
                sns.rugplot(data=df, ax=ax, **rug_params)
            else:
                raise ValueError(f"不支持的 Seaborn 图表类型: {chart_type}")

            # 应用标题
            chart_title = style_params.get('title')
            if chart_title:
                ax.set_title(chart_title, color='#F1F5F9')

            if not style_params.get('show_grid', True):
                ax.grid(False)

        plt.tight_layout()

        # 转换为 base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor='#1B1D2A', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()
        plt.close(fig)

        return {
            'chart': f'data:image/png;base64,{img_base64}',
            'library': 'seaborn'
        }


# Plotly 图表类型映射
PLOTLY_CHART_TYPES = {
    'scatter': {'name': '散点图', 'category': '关系'},
    'line': {'name': '折线图', 'category': '趋势'},
    'bar': {'name': '柱状图', 'category': '比较'},
    'hbar': {'name': '条形图(水平)', 'category': '比较'},
    'histogram': {'name': '直方图', 'category': '分布'},
    'box': {'name': '箱线图', 'category': '分布'},
    'violin': {'name': '小提琴图', 'category': '分布'},
    'scatter_3d': {'name': '3D散点图', 'category': '关系'},
    'pie': {'name': '饼图', 'category': '占比'},
    'sunburst': {'name': '旭日图', 'category': '占比'},
    'treemap': {'name': '矩形树图', 'category': '占比'},
    'funnel': {'name': '漏斗图', 'category': '流程'},
    'density_heatmap': {'name': '密度热力图', 'category': '关系'},
    # 新增
    'area': {'name': '面积图', 'category': '趋势'},
    'waterfall': {'name': '瀑布图', 'category': '比较'},
    'radar': {'name': '雷达图', 'category': '比较'},
    'parallel': {'name': '平行坐标图', 'category': '关系'},
    'parallel_cat': {'name': '平行类别图', 'category': '关系'},
    'contour': {'name': '等高线图', 'category': '分布'},
    'surface_3d': {'name': '3D曲面图', 'category': '关系'},
    'bar_polar': {'name': '极坐标柱图', 'category': '占比'},
    'splom': {'name': '散点矩阵', 'category': '关系'},
}

# Seaborn 图表类型映射
SEABORN_CHART_TYPES = {
    'scatter': {'name': '散点图', 'category': '关系'},
    'line': {'name': '折线图', 'category': '趋势'},
    'bar': {'name': '柱状图', 'category': '比较'},
    'histogram': {'name': '直方图', 'category': '分布'},
    'box': {'name': '箱线图', 'category': '分布'},
    'violin': {'name': '小提琴图', 'category': '分布'},
    'heatmap': {'name': '热力图', 'category': '关系'},
    # 新增
    'kdeplot': {'name': 'KDE密度图', 'category': '分布'},
    'pairplot': {'name': '配对图', 'category': '关系'},
    'jointplot': {'name': '联合图', 'category': '关系'},
    'regplot': {'name': '回归图', 'category': '关系'},
    'countplot': {'name': '计数图', 'category': '比较'},
    'rugplot': {'name': '地毯图', 'category': '分布'},
}
