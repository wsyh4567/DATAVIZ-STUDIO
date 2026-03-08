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


class ChartLibrary(str, Enum):
    """图表库枚举"""
    PLOTLY = "plotly"
    SEABORN = "seaborn"


class ChartType(str, Enum):
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
        template = style_params.get('template', 'plotly_white')
        title = style_params.get('title', None)
        show_legend = style_params.get('show_legend', True)
        show_grid = style_params.get('show_grid', True)
        width = style_params.get('width', None)
        height = style_params.get('height', None)
        color_scale = style_params.get('color_scale', None)
        color_discrete_sequence = style_params.get('color_discrete_sequence')

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
            
        opacity = style_params.get('opacity')
        if opacity is not None and opacity < 1.0:
            fig.update_traces(opacity=opacity)

    def _create_plotly_chart(
        self,
        df: pd.DataFrame,
        chart_type: ChartType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用 Plotly 创建图表"""

        # 分离样式参数和图表参数
        style_keys = {'template', 'title', 'show_legend', 'show_grid', 'width', 'height', 'color_scale', 'color_discrete_sequence', 'opacity', 'secondary_y'}
        style_params = {k: v for k, v in params.items() if k in style_keys and v is not None}
        chart_params = {k: v for k, v in params.items() if k not in style_keys and v is not None}

        chart_type_str = getattr(chart_type, 'value', str(chart_type))

        if chart_type_str == "scatter":
            fig = px.scatter(df, **chart_params)
        elif chart_type_str == "line":
            fig = px.line(df, **chart_params)
        elif chart_type_str == "bar":
            fig = px.bar(df, barmode='group', **chart_params)
        elif chart_type_str == "hbar":
            fig = px.bar(df, barmode='group', orientation='h', **chart_params)
        elif chart_type_str == "histogram":
            fig = px.histogram(df, **chart_params)
        elif chart_type_str == "box":
            fig = px.box(df, **chart_params)
        elif chart_type_str == "violin":
            fig = px.violin(df, box=True, **chart_params)
        elif chart_type_str == "scatter_3d":
            fig = px.scatter_3d(df, **chart_params)
        elif chart_type_str == "pie":
            # 针对特殊图表类型做参数重映射
            # pie 不接受 x/y，需映射到各自的专用参数名
            remap = {}
            if 'x' in chart_params:
                remap['names'] = chart_params.pop('x')
            if 'y' in chart_params:
                remap['values'] = chart_params.pop('y')
            # 移除不支持的通用参数
            for k in ('size', 'facet_row', 'facet_col',
                      'animation_frame', 'trendline',
                      'marginal_x', 'marginal_y', 'hover_data'):
                chart_params.pop(k, None)
            chart_params.update(remap)
            fig = px.pie(df, **chart_params)
        elif chart_type_str == "sunburst":
            remap = {}
            if 'x' in chart_params:
                # path 需要列表（层级列）
                x_val = chart_params.pop('x')
                remap['path'] = [x_val]  # 单层层级
            if 'color' in chart_params and 'y' not in chart_params:
                # 有 color 但无 values，用 color 列作为值
                pass
            if 'y' in chart_params:
                remap['values'] = chart_params.pop('y')
            for k in ('size', 'facet_row', 'facet_col',
                      'animation_frame', 'trendline',
                      'marginal_x', 'marginal_y', 'hover_data'):
                chart_params.pop(k, None)
            chart_params.update(remap)
            fig = px.sunburst(df, **chart_params)
        elif chart_type_str == "treemap":
            remap = {}
            if 'x' in chart_params:
                # path 需要列表（层级列）
                x_val = chart_params.pop('x')
                remap['path'] = [x_val]  # 单层层级
            if 'color' in chart_params and 'y' not in chart_params:
                # 有 color 但无 values，用 color 列作为值
                pass
            if 'y' in chart_params:
                remap['values'] = chart_params.pop('y')
            for k in ('size', 'facet_row', 'facet_col',
                      'animation_frame', 'trendline',
                      'marginal_x', 'marginal_y', 'hover_data'):
                chart_params.pop(k, None)
            chart_params.update(remap)
            fig = px.treemap(df, **chart_params)
        elif chart_type_str == "funnel":
            # funnel 接受 x(值) 和 y(阶段)
            fig = px.funnel(df, **chart_params)
        elif chart_type_str == "density_heatmap":
            fig = px.density_heatmap(df, **chart_params)
        elif chart_type_str == "area":
            fig = px.area(df, **chart_params)
        elif chart_type_str == "waterfall":
            # Plotly Express 暂无 waterfall，直接报错或使用 GO
            raise NotImplementedError("Plotly Express 暂不支持瀑布图参数化，需特定数据结构。")
        elif chart_type_str == "radar":
            fig = px.line_polar(df, line_close=True, **chart_params)
        elif chart_type_str == "parallel":
            # 过滤非数值列
            num_cols = df.select_dtypes(include=[np.number]).columns
            color = chart_params.pop('color', None)
            fig = px.parallel_coordinates(df, dimensions=num_cols, color=color, **chart_params)
        elif chart_type_str == "parallel_cat":
            # 类别平行坐标
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            fig = px.parallel_categories(df, dimensions=cat_cols, **chart_params)
        elif chart_type_str == "contour":
            fig = px.density_contour(df, **chart_params)
        elif chart_type_str == "surface_3d":
            # 通常需要网格数据，如果输入是三列的散点数据，可能无法直接绘制
            if 'z' in chart_params:
                fig = go.Figure(data=[go.Surface(z=df[chart_params['z']].values)])
            else:
                raise ValueError("3D 曲面图需要 'z' 参数的二维矩阵。")
        elif chart_type_str == "bar_polar":
            remap = {}
            if 'x' in chart_params:
                remap['theta'] = chart_params.pop('x')
            if 'y' in chart_params:
                remap['r'] = chart_params.pop('y')
            for k in ('size', 'facet_row', 'facet_col',
                      'animation_frame', 'trendline',
                      'marginal_x', 'marginal_y', 'hover_data'):
                chart_params.pop(k, None)
            chart_params.update(remap)
            fig = px.bar_polar(df, **chart_params)
        elif chart_type_str == "splom":
            # 散点矩阵
            num_cols = df.select_dtypes(include=[np.number]).columns
            fig = px.scatter_matrix(df, dimensions=num_cols, **chart_params)
        else:
            raise ValueError(f"不支持的 Plotly 图表类型: {chart_type}")

        secondary_y_col = style_params.get('secondary_y')
        if secondary_y_col and secondary_y_col in df.columns and chart_params.get('x') and chart_type_str in ["scatter", "line", "bar"]:
            from plotly.subplots import make_subplots
            sub_fig = make_subplots(specs=[[{"secondary_y": True}]])
            for trace in fig.data:
                sub_fig.add_trace(trace, secondary_y=False)
            
            sub_fig.add_trace(
                go.Scatter(
                    x=df[chart_params.get('x')], 
                    y=df[secondary_y_col], 
                    name=secondary_y_col, 
                    mode='lines',
                    line=dict(color='#E53E3E', dash='dash')
                ),
                secondary_y=True
            )
            sub_fig.layout.update(fig.layout)
            sub_fig.update_yaxes(title_text=chart_params.get('y', ''), secondary_y=False)
            sub_fig.update_yaxes(title_text=secondary_y_col, secondary_y=True)
            fig = sub_fig

        # 应用样式
        self._apply_plotly_style(fig, style_params if style_params else {
            'template': 'plotly_white'
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

        chart_type_str = getattr(chart_type, 'value', str(chart_type))

        # 分离样式参数
        style_keys = {'template', 'title', 'show_legend', 'show_grid', 'width', 'height', 'color_scale'}
        style_params = {k: v for k, v in params.items() if k in style_keys and v is not None}
        chart_params = {k: v for k, v in params.items() if k not in style_keys and v is not None}

        # 设置样式
        template = style_params.get('template', 'plotly_white')
        is_dark = 'dark' in str(template).lower()
        
        if is_dark:
            sns.set_theme(style="darkgrid")
            face_color = '#1B1D2A'
            plt.rcParams['figure.facecolor'] = face_color
            plt.rcParams['axes.facecolor'] = '#262940'
            plt.rcParams['text.color'] = '#F1F5F9'
            plt.rcParams['axes.labelcolor'] = '#F1F5F9'
            plt.rcParams['xtick.color'] = '#F1F5F9'
            plt.rcParams['ytick.color'] = '#F1F5F9'
        else:
            sns.set_theme(style="whitegrid")
            face_color = '#FFFFFF'
            plt.rcParams['figure.facecolor'] = face_color
            plt.rcParams['axes.facecolor'] = '#F8F9FA'
            plt.rcParams['text.color'] = '#2D3748'
            plt.rcParams['axes.labelcolor'] = '#4A5568'
            plt.rcParams['xtick.color'] = '#718096'
            plt.rcParams['ytick.color'] = '#718096'

        # 设置调色板：优先取样式面板的 color_scale，若无则取专用面板的 palette
        palette = style_params.get('color_scale') or chart_params.pop('palette', 'deep')
        if palette:
            try:
                # 尽量转为小写适配 Seaborn
                palette_name = palette.lower() if isinstance(palette, str) else palette
                sns.set_palette(palette_name)
                # 存回 chart_params 供某些图表强制重写（如 heatmap cmap）
                chart_params['palette'] = palette_name
            except Exception:
                sns.set_palette('deep')

        # 透明度参数
        opacity = style_params.get('opacity')
        if opacity is not None:
            chart_params['alpha'] = float(opacity)

        fig_width = int(style_params.get('width', 800)) / 80
        fig_height = int(style_params.get('height', 480)) / 80

        # 特殊多面板图表（pairplot, jointplot 自带 figure）
        needs_fig = True

        if chart_type_str == "pairplot":
            needs_fig = False
            pp_params = {}
            if 'hue' in chart_params:
                pp_params['hue'] = chart_params['hue']
            g = sns.pairplot(df, **pp_params)
            fig = g.figure
            fig.set_facecolor(face_color)

        elif chart_type_str == "jointplot":
            needs_fig = False
            jp_params = {}
            for k in ('x', 'y', 'hue'):
                if k in chart_params:
                    jp_params[k] = chart_params[k]
            g = sns.jointplot(data=df, **jp_params)
            fig = g.figure
            fig.set_facecolor(face_color)

        else:
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))

            # 提前弹出 secondary_y 用于双Y轴，防止报错
            secondary_y_col = chart_params.pop('secondary_y', None)

            if chart_type_str == "scatter":
                sns.scatterplot(data=df, ax=ax, **chart_params)
            elif chart_type_str == "line":
                sns.lineplot(data=df, ax=ax, **chart_params)
            elif chart_type_str == "bar":
                sns.barplot(data=df, ax=ax, **chart_params)
            elif chart_type_str == "histogram":
                sns.histplot(data=df, ax=ax, **chart_params)
            elif chart_type_str == "box":
                sns.boxplot(data=df, ax=ax, **chart_params)
            elif chart_type_str == "violin":
                sns.violinplot(data=df, ax=ax, **chart_params)
            elif chart_type_str == "heatmap":
                val_col = chart_params.get('z') or chart_params.get('values')
                if not val_col:
                    # 如果没有指定 values，计算频数
                    pivot_data = pd.crosstab(df[chart_params.get('y')], df[chart_params.get('x')])
                else:
                    pivot_data = df.pivot_table(
                        index=chart_params.get('y'),
                        columns=chart_params.get('x'),
                        values=val_col,
                        aggfunc='mean'
                    )
                cmap = chart_params.get('palette', 'viridis')
                sns.heatmap(pivot_data, ax=ax, cmap=cmap, alpha=chart_params.get('alpha', 1.0))
            elif chart_type_str == "kdeplot":
                kde_params = {k: v for k, v in chart_params.items() if k in ('x', 'y', 'hue', 'alpha')}
                sns.kdeplot(data=df, ax=ax, fill=True, **kde_params)
            elif chart_type_str == "regplot":
                reg_params = {k: v for k, v in chart_params.items() if k in ('x', 'y')}
                scatter_kws = {'alpha': chart_params.get('alpha', 1.0)}
                sns.regplot(data=df, ax=ax, scatter_kws=scatter_kws, **reg_params)
            elif chart_type_str == "countplot":
                cnt_params = {k: v for k, v in chart_params.items() if k in ('x', 'y', 'hue', 'alpha')}
                # countplot 不能同时拥有 x 和 y，剥离 y 如果 x 存在
                if 'x' in cnt_params and 'y' in cnt_params:
                    cnt_params.pop('y')
                sns.countplot(data=df, ax=ax, **cnt_params)
            elif chart_type_str == "rugplot":
                rug_params = {k: v for k, v in chart_params.items() if k in ('x', 'y', 'hue', 'alpha')}
                sns.rugplot(data=df, ax=ax, **rug_params)
            else:
                raise ValueError(f"不支持的 Seaborn 图表类型: {chart_type}")

            # 双 Y 轴逻辑 (ax.twinx())
            if secondary_y_col and secondary_y_col in df.columns and chart_type_str in ["scatter", "line", "bar"]:
                ax2 = ax.twinx()
                twin_params = chart_params.copy()
                twin_params['y'] = secondary_y_col
                
                # 绘制辅助Y轴图形（用不冲突的颜色，避免颜色冲突）
                if 'palette' in twin_params:
                    del twin_params['palette']
                if 'hue' in twin_params:
                    del twin_params['hue']

                if chart_type_str == "line":
                    sns.lineplot(data=df, ax=ax2, color='coral', linestyle='--', linewidth=2, **twin_params)
                elif chart_type_str == "bar":
                    sns.barplot(data=df, ax=ax2, color='teal', alpha=0.4, **twin_params)
                elif chart_type_str == "scatter":
                    sns.scatterplot(data=df, ax=ax2, color='coral', marker='D', s=80, **twin_params)
                
                ax2.set_ylabel(secondary_y_col, color='coral' if chart_type_str != "bar" else 'teal')
                ax2.tick_params(axis='y', labelcolor='coral' if chart_type_str != "bar" else 'teal')

            # 处理双Y轴 (Secondary Y)
            secondary_y_col = style_params.get('secondary_y')
            if secondary_y_col and secondary_y_col in df.columns:
                ax2 = ax.twinx()
                sns.lineplot(data=df, x=chart_params.get('x'), y=secondary_y_col, ax=ax2, color='r', alpha=chart_params.get('alpha', 1.0))
                ax2.set_ylabel(secondary_y_col)

            # 应用标题
            chart_title = style_params.get('title')
            if chart_title:
                ax.set_title(chart_title, color=plt.rcParams['text.color'])

            # 图例显示逻辑
            if not style_params.get('show_legend', True):
                try:
                    ax.get_legend().remove()
                except Exception:
                    pass

            if not style_params.get('show_grid', True):
                ax.grid(False)

        plt.tight_layout()

        # 转换为 base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor=face_color, edgecolor='none')
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
