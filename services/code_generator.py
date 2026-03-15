# -*- coding: utf-8 -*-
"""代码生成服务 — 生成可执行的 Python 代码

将图表配置转换为完整的 Python 代码，可以直接在 Python 环境中运行。
"""

from __future__ import annotations

from typing import Any, Dict
from datetime import datetime


class CodeGenerator:
    """Python 代码生成器"""
    
    @staticmethod
    def generate_plotly_code(
        chart_type: str,
        params: Dict[str, Any],
        data_source: str = "df"
    ) -> str:
        """生成 Plotly 代码"""
        # 过滤掉样式参数，不要传入 px 函数
        style_keys = {'template', 'show_legend', 'show_grid', 'chart_width', 'chart_height',
                       'color_scale', 'chart_title', 'title'}
        clean_params = {k: v for k, v in params.items() if k not in style_keys and v is not None}

        # 特殊图表需要 go 而非 px
        special_go_types = {'waterfall', 'radar', 'surface_3d'}

        lines = [
            "# " + "=" * 50,
            "# DataViz Studio 自动生成代码",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# " + "=" * 50,
            "",
            "import pandas as pd",
        ]

        if chart_type in special_go_types:
            lines.append("import plotly.graph_objects as go")
        else:
            lines.append("import plotly.express as px")

        lines += [
            "",
            "# 1. 加载数据",
            "# df = pd.read_csv('your_data.csv')  # 替换为你的数据文件",
            "",
            f"# 2. 创建{CHART_TYPE_NAMES.get(chart_type, chart_type)}",
        ]

        # 映射 px 函数名
        px_func_map = {
            'hbar': 'bar',
            'parallel': 'parallel_coordinates',
            'parallel_cat': 'parallel_categories',
            'contour': 'density_contour',
            'splom': 'scatter_matrix',
        }
        px_func = px_func_map.get(chart_type, chart_type)

        if chart_type in special_go_types:
            lines.append(f"# 需要使用 plotly.graph_objects 创建 {CHART_TYPE_NAMES.get(chart_type, chart_type)}")
            lines.append(f"# 请参考 Plotly 文档: https://plotly.com/python/")
            lines.append(f"fig = go.Figure()")
        else:
            if chart_type == 'hbar':
                lines.append(f"fig = px.{px_func}(")
                lines.append(f"    {data_source},")
                for key, value in clean_params.items():
                    if isinstance(value, str):
                        lines.append(f"    {key}='{value}',")
                    elif isinstance(value, list):
                        lines.append(f"    {key}={value},")
                    elif isinstance(value, bool):
                        lines.append(f"    {key}={value},")
                    else:
                        lines.append(f"    {key}={value},")
                lines.append("    orientation='h',")
                lines.append(")")
            else:
                lines.append(f"fig = px.{px_func}(")
                lines.append(f"    {data_source},")
                for key, value in clean_params.items():
                    if isinstance(value, str):
                        lines.append(f"    {key}='{value}',")
                    elif isinstance(value, list):
                        lines.append(f"    {key}={value},")
                    elif isinstance(value, bool):
                        lines.append(f"    {key}={value},")
                    else:
                        lines.append(f"    {key}={value},")
                lines.append(")")

        # 添加样式代码
        title = params.get('title') or params.get('chart_title')
        template = params.get('template')
        if title or template:
            lines.append("")
            lines.append("# 样式设置")
            update_parts = []
            if title:
                update_parts.append(f"    title='{title}'")
            if template:
                update_parts.append(f"    template='{template}'")
            lines.append("fig.update_layout(")
            lines.append(",\n".join(update_parts))
            lines.append(")")

        lines.append("")
        lines.append("# 3. 显示图表")
        lines.append("fig.show()")
        lines.append("")
        lines.append("# 4. 保存图表（可选）")
        lines.append("# fig.write_html('chart.html')")
        lines.append("# fig.write_image('chart.png')")

        return "\n".join(lines)
    
    @staticmethod
    def generate_seaborn_code(
        chart_type: str,
        params: Dict[str, Any],
        data_source: str = "df"
    ) -> str:
        """生成 Seaborn 代码"""
        # 过滤掉样式参数和非 seaborn 参数
        style_keys = {'template', 'show_legend', 'show_grid', 'chart_width', 'chart_height',
                       'color_scale', 'chart_title', 'title'}
        clean_params = {k: v for k, v in params.items()
                        if k not in style_keys and v is not None and k not in ['values']}

        # 多面板图表（不使用 ax 参数）
        multi_panel_types = {'pairplot', 'jointplot'}

        lines = [
            "# " + "=" * 50,
            "# DataViz Studio 自动生成代码",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# " + "=" * 50,
            "",
            "import pandas as pd",
            "import seaborn as sns",
            "import matplotlib.pyplot as plt",
            "",
            "# 1. 加载数据",
            "# df = pd.read_csv('your_data.csv')  # 替换为你的数据文件",
            "",
            f"# 2. 创建{CHART_TYPE_NAMES.get(chart_type, chart_type)}",
        ]

        if chart_type in multi_panel_types:
            # pairplot / jointplot 返回自己的 Figure，不需要 fig, ax
            lines.append(f"g = sns.{chart_type}(")
            lines.append(f"    data={data_source},")
            for key, value in clean_params.items():
                if isinstance(value, str):
                    lines.append(f"    {key}='{value}',")
                elif isinstance(value, tuple):
                    lines.append(f"    {key}={value},")
                elif isinstance(value, bool):
                    lines.append(f"    {key}={value},")
                else:
                    lines.append(f"    {key}={value},")
            lines.append(")")
        else:
            lines.append("fig, ax = plt.subplots(figsize=(10, 6))")
            lines.append(f"sns.{chart_type}(")
            lines.append(f"    data={data_source},")
            for key, value in clean_params.items():
                if isinstance(value, str):
                    lines.append(f"    {key}='{value}',")
                elif isinstance(value, tuple):
                    lines.append(f"    {key}={value},")
                elif isinstance(value, bool):
                    lines.append(f"    {key}={value},")
                else:
                    lines.append(f"    {key}={value},")
            lines.append("    ax=ax")
            lines.append(")")

        lines.append("")
        lines.append("# 3. 设置标题和标签（可选）")
        title = params.get('title') or params.get('chart_title')
        if title:
            if chart_type in multi_panel_types:
                lines.append(f"g.fig.suptitle('{title}', y=1.02)")
            else:
                lines.append(f"ax.set_title('{title}', fontsize=16)")
        else:
            lines.append("# ax.set_title('图表标题', fontsize=16)")
        lines.append("# ax.set_xlabel('X轴标签', fontsize=12)")
        lines.append("# ax.set_ylabel('Y轴标签', fontsize=12)")
        lines.append("")
        lines.append("plt.tight_layout()")
        lines.append("plt.show()")
        lines.append("")
        lines.append("# 4. 保存图表（可选）")
        lines.append("# plt.savefig('chart.png', dpi=300, bbox_inches='tight')")

        return "\n".join(lines)
    
    @staticmethod
    def generate_code(
        library: str,
        chart_type: str,
        params: Dict[str, Any],
        data_source: str = "df"
    ) -> str:
        """生成代码（根据图表库）
        
        Args:
            library: 图表库（'plotly' 或 'seaborn'）
            chart_type: 图表类型
            params: 图表参数
            data_source: 数据源名称
        
        Returns:
            完整的 Python 代码
        """
        if library == 'plotly':
            return CodeGenerator.generate_plotly_code(chart_type, params, data_source)
        elif library == 'seaborn':
            return CodeGenerator.generate_seaborn_code(chart_type, params, data_source)
        else:
            raise ValueError(f"不支持的图表库: {library}")


# 图表类型中文名称映射
CHART_TYPE_NAMES = {
    'scatter': '散点图',
    'line': '折线图',
    'bar': '柱状图',
    'histogram': '直方图',
    'box': '箱线图',
    'violin': '小提琴图',
    'scatter_3d': '3D散点图',
    'pie': '饼图',
    'sunburst': '旭日图',
    'treemap': '矩形树图',
    'funnel': '漏斗图',
    'density_heatmap': '密度热力图',
    'heatmap': '热力图',
    # 新增 Plotly 图表类型
    'area': '面积图',
    'waterfall': '瀑布图',
    'radar': '雷达图',
    'parallel': '平行坐标图',
    'parallel_cat': '平行类别图',
    'contour': '等高线图',
    'surface_3d': '3D曲面图',
    'bar_polar': '极坐标柱图',
    'splom': '散点矩阵',
    'hbar': '水平条形图',
    # Seaborn 图表类型
    'kdeplot': 'KDE密度图',
    'pairplot': '配对图',
    'jointplot': '联合图',
    'regplot': '回归图',
    'countplot': '计数图',
    'rugplot': '地毯图',
    'scatterplot': '散点图',
    'lineplot': '折线图',
    'barplot': '柱状图',
    'boxplot': '箱线图',
    'violinplot': '小提琴图',
    'stripplot': '带状图',
    'swarmplot': '蜂群图',
}


class DataCleaningCodeGenerator:
    """数据清洗代码生成器"""
    
    @staticmethod
    def generate_data_cleaning_code(operations: list) -> str:
        """生成数据清洗代码
        
        Args:
            operations: 操作列表，每个操作包含 type 和相关参数
        
        Returns:
            完整的 Python 代码
        """
        from services.data_cleaner import (
            ColumnSplitter,
            ColumnConcatenator,
            StringReplacer,
            StringCleaner
        )
        
        lines = [
            "# " + "=" * 50,
            "# DataViz Studio 数据清洗代码",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# " + "=" * 50,
            "",
            "import pandas as pd",
            "",
            "# 1. 加载数据",
            "# df = pd.read_csv('your_data.csv')  # 替换为你的数据文件",
            "",
            "# 2. 数据清洗操作",
        ]
        
        for i, op in enumerate(operations, 1):
            lines.append(f"\n# 操作 {i}: {op.get('description', '未知操作')}")
            
            op_type = op.get('type')
            
            if op_type == 'split_column':
                code = ColumnSplitter.generate_code(
                    op['column'],
                    op['separator'],
                    op.get('max_split'),
                    op.get('new_names')
                )
                lines.append(code)
            
            elif op_type == 'concatenate_columns':
                code = ColumnConcatenator.generate_code(
                    op['columns'],
                    op['separator'],
                    op['new_name'],
                    op.get('drop_original', False)
                )
                lines.append(code)
            
            elif op_type == 'find_replace':
                code = StringReplacer.generate_code(
                    op['column'],
                    op['find_value'],
                    op['replace_value'],
                    op.get('use_regex', False),
                    op.get('case_sensitive', True)
                )
                lines.append(code)
            
            elif op_type == 'strip_whitespace':
                code = StringCleaner.generate_strip_code(
                    op['column'],
                    op['mode']
                )
                lines.append(code)
            
            elif op_type == 'case_conversion':
                code = StringCleaner.generate_case_code(
                    op['column'],
                    op['case_type']
                )
                lines.append(code)
            
            elif op_type == 'extract_substring':
                code = StringCleaner.generate_substring_code(
                    op['column'],
                    op['start'],
                    op.get('end'),
                    op.get('new_name')
                )
                lines.append(code)
        
        lines.append("")
        lines.append("# 3. 保存清洗后的数据")
        lines.append("# df.to_csv('cleaned_data.csv', index=False)")
        lines.append("")
        lines.append("# 4. 查看结果")
        lines.append("print(df.head())")
        lines.append("print(f'\\n数据形状: {df.shape}')")
        
        return "\n".join(lines)
