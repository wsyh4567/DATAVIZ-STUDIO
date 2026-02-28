# -*- coding: utf-8 -*-
"""图表工作室页面 — Python 优先架构

可视化的 Python 数据分析平台，支持 Plotly 和 Seaborn 两种图表库。
所有操作可导出为可执行的 Python 代码。
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import json

from core.data_manager import DataManager
from components.code_preview import create_code_preview_panel
from services.chart_service import ChartService, ChartLibrary, ChartType, PLOTLY_CHART_TYPES, SEABORN_CHART_TYPES
from services.code_generator import CodeGenerator


def create_chart_studio_page() -> html.Div:
    """创建图表工作室页面
    
    布局：
    - 顶部：图表库切换器
    - 左侧：参数配置面板
    - 中间：图表画布
    - 右侧：代码预览面板
    
    Returns:
        图表工作室页面组件
    """
    dm = DataManager()
    df = dm.active_df
    
    if df is None or df.empty:
        return html.Div([
            dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    "请先在数据中心加载数据"
                ],
                color="warning",
                className="m-4"
            )
        ])
    
    return html.Div([
        # 顶部：图表库切换器
        html.Div([
            html.Label("图表库：", className="me-2"),
            dcc.RadioItems(
                id='chart-library-selector',
                options=[
                    {'label': ' 📊 Plotly（交互式）', 'value': 'plotly'},
                    {'label': ' 📈 Seaborn（静态美化）', 'value': 'seaborn'}
                ],
                value='plotly',
                inline=True,
                className='library-selector',
                labelStyle={'marginRight': '20px'}
            ),
            html.Div(id='library-info', className='library-info text-muted ms-3')
        ], className='library-switcher p-3 bg-secondary border-bottom'),
        
        # 主内容区
        dbc.Row([
            # 左侧：参数配置面板
            dbc.Col([
                html.Div([
                    html.H6("图表类型", className="mb-3"),
                    dcc.Dropdown(
                        id='chart-type-selector',
                        options=[],  # 将根据图表库动态更新
                        value='scatter',
                        placeholder='选择图表类型',
                        className='mb-3'
                    ),
                    
                    html.Hr(),
                    
                    # 参数配置区域（将根据图表库动态更新）
                    html.Div(id='params-panel-container'),
                    
                ], className='p-3')
            ], width=3, className='bg-secondary border-end', style={'height': 'calc(100vh - 140px)', 'overflowY': 'auto'}),
            
            # 中间：图表画布
            dbc.Col([
                html.Div([
                    html.Div(id='chart-container', children=[
                        html.Div([
                            html.I(className="bi bi-graph-up", style={'fontSize': '48px', 'color': '#6366F1'}),
                            html.P("👈 配置参数后，图表将在这里显示", 
                                   className='placeholder-text mt-3')
                        ], className='chart-placeholder text-center', 
                           style={'paddingTop': '100px'})
                    ], style={'height': '60%', 'borderBottom': '1px solid #333'}),
                    
                    # 代码预览面板
                    create_code_preview_panel(),
                    
                ], className='p-3')
            ], width=9, style={'height': 'calc(100vh - 140px)', 'overflowY': 'auto'}),
            
        ], className='g-0'),
        
        # 存储组件
        dcc.Store(id='chart-data-store'),
        
    ], id='chart-studio-page')


def create_plotly_params_panel(df: pd.DataFrame) -> html.Div:
    """创建 Plotly 参数配置面板
    
    Args:
        df: 数据框
    
    Returns:
        参数配置面板组件
    """
    columns = [{'label': col, 'value': col} for col in df.columns]
    
    return html.Div([
        html.H6("Plotly Express 参数", className="mb-3"),
        
        # 基础参数
        html.Div([
            html.Label("x (X轴)", className="form-label"),
            dcc.Dropdown(
                id='param-x',
                options=columns,
                placeholder='选择X轴字段',
                className='mb-2'
            ),
        ]),
        
        html.Div([
            html.Label("y (Y轴)", className="form-label"),
            dcc.Dropdown(
                id='param-y',
                options=columns,
                placeholder='选择Y轴字段',
                className='mb-2'
            ),
        ]),
        
        html.Div([
            html.Label("color (颜色分组)", className="form-label"),
            dcc.Dropdown(
                id='param-color',
                options=columns,
                placeholder='选择颜色字段（可选）',
                clearable=True,
                className='mb-2'
            ),
        ]),
        
        html.Div([
            html.Label("size (大小)", className="form-label"),
            dcc.Dropdown(
                id='param-size',
                options=columns,
                placeholder='选择大小字段（可选）',
                clearable=True,
                className='mb-2'
            ),
        ]),
        
        # 高级参数（可折叠）
        html.Hr(),
        dbc.Button(
            "展开高级参数",
            id='toggle-advanced-params',
            size='sm',
            color='link',
            className='mb-2'
        ),
        
        dbc.Collapse([
            html.H6("高级参数", className="mb-2 mt-2"),
            
            html.Div([
                html.Label("hover_data (悬停显示)", className="form-label"),
                dcc.Dropdown(
                    id='param-hover-data',
                    options=columns,
                    placeholder='选择悬停字段（可多选）',
                    multi=True,
                    className='mb-2'
                ),
            ]),
            
            html.Div([
                html.Label("facet_row (分面行)", className="form-label"),
                dcc.Dropdown(
                    id='param-facet-row',
                    options=columns,
                    placeholder='选择分面行字段（可选）',
                    clearable=True,
                    className='mb-2'
                ),
            ]),
            
            html.Div([
                html.Label("facet_col (分面列)", className="form-label"),
                dcc.Dropdown(
                    id='param-facet-col',
                    options=columns,
                    placeholder='选择分面列字段（可选）',
                    clearable=True,
                    className='mb-2'
                ),
            ]),
            
            html.Div([
                html.Label("animation_frame (动画帧)", className="form-label"),
                dcc.Dropdown(
                    id='param-animation-frame',
                    options=columns,
                    placeholder='选择动画帧字段（可选）',
                    clearable=True,
                    className='mb-2'
                ),
            ]),
            
            html.Div([
                html.Label("trendline (趋势线)", className="form-label"),
                dcc.Dropdown(
                    id='param-trendline',
                    options=[
                        {'label': 'OLS回归', 'value': 'ols'},
                        {'label': 'LOWESS平滑', 'value': 'lowess'},
                    ],
                    placeholder='选择趋势线类型（可选）',
                    clearable=True,
                    className='mb-2'
                ),
            ]),
            
            html.Div([
                html.Label("marginal_x (X轴边际图)", className="form-label"),
                dcc.Dropdown(
                    id='param-marginal-x',
                    options=[
                        {'label': '直方图', 'value': 'histogram'},
                        {'label': '箱线图', 'value': 'box'},
                        {'label': '小提琴图', 'value': 'violin'},
                    ],
                    placeholder='选择X轴边际图（可选）',
                    clearable=True,
                    className='mb-2'
                ),
            ]),
            
            html.Div([
                html.Label("marginal_y (Y轴边际图)", className="form-label"),
                dcc.Dropdown(
                    id='param-marginal-y',
                    options=[
                        {'label': '直方图', 'value': 'histogram'},
                        {'label': '箱线图', 'value': 'box'},
                        {'label': '小提琴图', 'value': 'violin'},
                    ],
                    placeholder='选择Y轴边际图（可选）',
                    clearable=True,
                    className='mb-2'
                ),
            ]),
            
        ], id='advanced-params-collapse', is_open=False),
        
    ], className='params-panel')



def create_seaborn_params_panel(df: pd.DataFrame) -> html.Div:
    """创建 Seaborn 参数配置面板
    
    Args:
        df: 数据框
    
    Returns:
        参数配置面板组件
    """
    columns = [{'label': col, 'value': col} for col in df.columns]
    
    return html.Div([
        html.H6("Seaborn 参数", className="mb-3"),
        
        # 基础参数
        html.Div([
            html.Label("x (X轴)", className="form-label"),
            dcc.Dropdown(
                id='param-x',
                options=columns,
                placeholder='选择X轴字段',
                className='mb-2'
            ),
        ]),
        
        html.Div([
            html.Label("y (Y轴)", className="form-label"),
            dcc.Dropdown(
                id='param-y',
                options=columns,
                placeholder='选择Y轴字段',
                className='mb-2'
            ),
        ]),
        
        html.Div([
            html.Label("hue (颜色分组)", className="form-label"),
            dcc.Dropdown(
                id='param-hue',
                options=columns,
                placeholder='选择颜色字段（可选）',
                clearable=True,
                className='mb-2'
            ),
        ]),
        
        html.Div([
            html.Label("size (大小)", className="form-label"),
            dcc.Dropdown(
                id='param-size',
                options=columns,
                placeholder='选择大小字段（可选）',
                clearable=True,
                className='mb-2'
            ),
        ]),
        
        html.Div([
            html.Label("style (样式)", className="form-label"),
            dcc.Dropdown(
                id='param-style',
                options=columns,
                placeholder='选择样式字段（可选）',
                clearable=True,
                className='mb-2'
            ),
        ]),
        
        html.Hr(),
        
        # Seaborn 特有参数
        html.Div([
            html.Label("palette (调色板)", className="form-label"),
            dcc.Dropdown(
                id='param-palette',
                options=[
                    {'label': 'deep', 'value': 'deep'},
                    {'label': 'muted', 'value': 'muted'},
                    {'label': 'pastel', 'value': 'pastel'},
                    {'label': 'bright', 'value': 'bright'},
                    {'label': 'dark', 'value': 'dark'},
                    {'label': 'colorblind', 'value': 'colorblind'},
                    {'label': 'viridis', 'value': 'viridis'},
                    {'label': 'plasma', 'value': 'plasma'},
                ],
                value='deep',
                clearable=False,
                className='mb-2'
            ),
        ]),
        
    ], className='params-panel')


# ============================================================================
# 回调函数
# ============================================================================

@callback(
    [Output('chart-type-selector', 'options'),
     Output('params-panel-container', 'children'),
     Output('library-info', 'children')],
    Input('chart-library-selector', 'value'),
)
def switch_library(library):
    """切换图表库时更新参数面板"""
    dm = DataManager()
    df = dm.active_df
    
    if df is None or df.empty:
        return [], html.Div("请先加载数据"), ""
    
    if library == 'plotly':
        # Plotly 图表类型选项
        options = [
            {'label': f"{info['name']} ({info['category']})", 'value': chart_type}
            for chart_type, info in PLOTLY_CHART_TYPES.items()
        ]
        params_panel = create_plotly_params_panel(df)
        info = "Plotly：交互式图表，支持缩放、悬停、动画等功能"
    else:
        # Seaborn 图表类型选项
        options = [
            {'label': f"{info['name']} ({info['category']})", 'value': chart_type}
            for chart_type, info in SEABORN_CHART_TYPES.items()
        ]
        params_panel = create_seaborn_params_panel(df)
        info = "Seaborn：静态图表，更美观的默认样式，适合出版和报告"
    
    return options, params_panel, info


@callback(
    Output('advanced-params-collapse', 'is_open'),
    Input('toggle-advanced-params', 'n_clicks'),
    State('advanced-params-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_advanced_params(n_clicks, is_open):
    """切换高级参数面板"""
    return not is_open


@callback(
    [Output('chart-container', 'children'),
     Output('generated-code-display', 'value')],
    [Input('chart-type-selector', 'value'),
     Input('param-x', 'value'),
     Input('param-y', 'value'),
     Input('param-color', 'value'),
     Input('param-size', 'value'),
     Input('param-hover-data', 'value'),
     Input('param-facet-row', 'value'),
     Input('param-facet-col', 'value'),
     Input('param-animation-frame', 'value'),
     Input('param-trendline', 'value'),
     Input('param-marginal-x', 'value'),
     Input('param-marginal-y', 'value')],
    [State('chart-library-selector', 'value')],
    prevent_initial_call=True
)
def generate_chart(
    chart_type, x, y, color, size, hover_data,
    facet_row, facet_col, animation_frame,
    trendline, marginal_x, marginal_y,
    library
):
    """生成图表和代码"""
    dm = DataManager()
    df = dm.active_df
    
    if df is None or df.empty:
        return html.Div("请先加载数据"), "# 请先加载数据"
    
    if not x and not y:
        return html.Div("请至少选择X轴或Y轴"), "# 请配置参数"
    
    # 构建参数字典
    if library == 'plotly':
        params = {
            'x': x,
            'y': y,
            'color': color,
            'size': size,
            'hover_data': hover_data,
            'facet_row': facet_row,
            'facet_col': facet_col,
            'animation_frame': animation_frame,
            'trendline': trendline,
            'marginal_x': marginal_x,
            'marginal_y': marginal_y,
        }
    else:  # seaborn
        params = {
            'x': x,
            'y': y,
            'hue': color,
            'size': size,
        }
    
    # 移除 None 值
    params = {k: v for k, v in params.items() if v is not None}
    
    try:
        # 创建图表服务
        chart_service = ChartService()
        chart_service.set_library(ChartLibrary(library))
        
        # 创建图表
        result = chart_service.create_chart(
            df=df,
            chart_type=ChartType(chart_type.upper()),
            params=params
        )
        
        # 生成代码
        code = CodeGenerator.generate_code(
            library=library,
            chart_type=chart_type,
            params=params
        )
        
        # 显示图表
        if library == 'plotly':
            chart_component = dcc.Graph(
                figure=json.loads(result['chart']),
                config={'displayModeBar': True, 'displaylogo': False},
                style={'height': '100%'}
            )
        else:  # seaborn
            chart_component = html.Img(
                src=result['chart'],
                style={'width': '100%', 'maxHeight': '500px', 'objectFit': 'contain'}
            )
        
        return chart_component, code
        
    except Exception as e:
        error_msg = f"生成图表时出错: {str(e)}"
        return html.Div(error_msg, className='text-danger'), f"# {error_msg}"


@callback(
    Output('download-code-file', 'data'),
    Input('download-py-btn', 'n_clicks'),
    State('generated-code-display', 'value'),
    prevent_initial_call=True
)
def download_code(n_clicks, code):
    """下载 Python 代码"""
    if not code or code.startswith('#'):
        return None
    
    return dict(
        content=code,
        filename='chart_code.py'
    )


@callback(
    Output('copy-success-toast', 'is_open'),
    Input('copy-code-btn', 'n_clicks'),
    State('generated-code-display', 'value'),
    prevent_initial_call=True
)
def copy_code(n_clicks, code):
    """复制代码到剪贴板（显示提示）"""
    if not code or code.startswith('#'):
        return False
    return True


# Clientside callback for actual clipboard copy
from dash import clientside_callback, ClientsideFunction

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='copyToClipboard'
    ),
    Output('copy-code-btn', 'n_clicks'),
    Input('copy-code-btn', 'n_clicks'),
    State('generated-code-display', 'value'),
    prevent_initial_call=True
)
