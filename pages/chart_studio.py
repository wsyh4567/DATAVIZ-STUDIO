# -*- coding: utf-8 -*-
"""图表工作室页面 — Python 优先架构

可视化的 Python 数据分析平台，支持 Plotly 和 Seaborn 两种图表库。
所有操作可导出为可执行的 Python 代码。
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, no_update
import pandas as pd
import json
import io

from core.data_manager import DataManager
from components.code_preview import create_code_preview_panel
from services.chart_service import ChartService, ChartLibrary, ChartType, PLOTLY_CHART_TYPES, SEABORN_CHART_TYPES
from services.code_generator import CodeGenerator
from services.field_analyzer import get_labeled_options


def create_chart_studio_page() -> html.Div:
    """创建图表工作室页面"""
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
        ], className='library-switcher p-3 bg-secondary border-bottom fade-in'),

        # 主内容区
        dbc.Row([
            # 左侧：参数配置面板
            dbc.Col([
                html.Div([
                    html.H6("图表类型", className="mb-3"),
                    dcc.Dropdown(
                        id='chart-type-selector',
                        options=[],
                        value='scatter',
                        placeholder='选择图表类型',
                        className='mb-3'
                    ),

                    html.Hr(),

                    # 参数配置区域（初始加载Plotly参数面板）
                    html.Div(
                        id='params-panel-container',
                        children=create_plotly_params_panel(df) if df is not None else html.Div()
                    ),

                ], className='p-3 slide-in-left')
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
                    ], className='fade-in', style={'height': '60%', 'borderBottom': '1px solid #333'}),

                    # 导出按钮行
                    html.Div([
                        dbc.Button([
                            html.I(className="bi bi-file-image me-1"), "导出PNG"
                        ], id='export-png-btn', color='outline-primary', size='sm', className='me-2 btn-hover'),
                        dbc.Button([
                            html.I(className="bi bi-filetype-svg me-1"), "导出SVG"
                        ], id='export-svg-btn', color='outline-info', size='sm', className='me-2 btn-hover'),
                        dbc.Button([
                            html.I(className="bi bi-filetype-html me-1"), "导出HTML"
                        ], id='export-html-btn', color='outline-success', size='sm', className='btn-hover'),
                    ], className='d-flex p-2 border-bottom', style={'backgroundColor': 'var(--bg-secondary)'}),

                    # 代码预览面板
                    create_code_preview_panel(),

                ], className='p-3')
            ], width=9, style={'height': 'calc(100vh - 140px)', 'overflowY': 'auto'}),

        ], className='g-0'),

        # 存储组件
        dcc.Store(id='chart-data-store'),
        dcc.Store(id='chart-figure-store'),
        dcc.Download(id='download-chart-file'),

    ], id='chart-studio-page')


def _create_style_panel() -> html.Div:
    """创建图表样式配置区域"""
    return html.Div([
        html.Hr(),
        html.H6("图表样式", className="mb-3 mt-2"),

        # 标题
        html.Div([
            html.Label("图表标题", className="form-label"),
            dbc.Input(
                id='style-title',
                type='text',
                placeholder='输入图表标题（可选）',
                size='sm',
                className='mb-2'
            ),
        ]),

        # 主题
        html.Div([
            html.Label("主题模板", className="form-label"),
            dcc.Dropdown(
                id='style-template',
                options=[
                    {'label': '暗色主题', 'value': 'plotly_dark'},
                    {'label': '白色主题', 'value': 'plotly_white'},
                    {'label': 'ggplot2', 'value': 'ggplot2'},
                    {'label': 'seaborn', 'value': 'seaborn'},
                    {'label': '简洁白', 'value': 'simple_white'},
                ],
                value='plotly_dark',
                clearable=False,
                className='mb-2'
            ),
        ]),

        # 配色
        html.Div([
            html.Label("配色方案", className="form-label"),
            dcc.Dropdown(
                id='style-color-scale',
                options=[
                    {'label': '默认', 'value': ''},
                    {'label': 'Viridis', 'value': 'Viridis'},
                    {'label': 'Plasma', 'value': 'Plasma'},
                    {'label': 'Inferno', 'value': 'Inferno'},
                    {'label': 'Magma', 'value': 'Magma'},
                    {'label': 'Cividis', 'value': 'Cividis'},
                    {'label': 'Turbo', 'value': 'Turbo'},
                    {'label': 'Bluered', 'value': 'Bluered'},
                    {'label': 'Rainbow', 'value': 'Rainbow'},
                ],
                value='',
                clearable=True,
                className='mb-2'
            ),
        ]),

        # 显示图例
        html.Div([
            dbc.Checkbox(
                id='style-show-legend',
                label='显示图例',
                value=True,
                className='mb-2'
            ),
        ]),

        # 显示网格
        html.Div([
            dbc.Checkbox(
                id='style-show-grid',
                label='显示网格',
                value=True,
                className='mb-2'
            ),
        ]),

        # 尺寸
        dbc.Row([
            dbc.Col([
                html.Label("宽度", className="form-label"),
                dbc.Input(
                    id='style-width',
                    type='number',
                    placeholder='自动',
                    size='sm',
                    className='mb-2'
                ),
            ], width=6),
            dbc.Col([
                html.Label("高度", className="form-label"),
                dbc.Input(
                    id='style-height',
                    type='number',
                    placeholder='自动',
                    size='sm',
                    className='mb-2'
                ),
            ], width=6),
        ]),
    ])


def create_plotly_params_panel(df: pd.DataFrame) -> html.Div:
    """创建 Plotly 参数配置面板"""
    columns = get_labeled_options(df)

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
            className='mb-2 btn-hover'
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

        # 图表样式
        _create_style_panel(),

    ], className='params-panel')



def create_seaborn_params_panel(df: pd.DataFrame) -> html.Div:
    """创建 Seaborn 参数配置面板"""
    columns = get_labeled_options(df)

    return html.Div([
        html.H6("Seaborn 参数", className="mb-3"),

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

        # 图表样式
        _create_style_panel(),

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
        options = []
        categories = {}
        for chart_type, info in PLOTLY_CHART_TYPES.items():
            category = info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append({'label': f"{info['name']} [{category}]", 'value': chart_type})

        for category, items in categories.items():
            options.extend(items)

        params_panel = create_plotly_params_panel(df)
        info = "Plotly：交互式图表，支持缩放、悬停、动画等功能"
    else:
        options = []
        for chart_type, info_item in SEABORN_CHART_TYPES.items():
            options.append({'label': f"{info_item['name']} [{info_item['category']}]", 'value': chart_type})

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
    [Output('param-y', 'options'),
     Output('param-color', 'options'),
     Output('param-size', 'options')],
    [Input('param-x', 'value'),
     Input('param-y', 'value'),
     Input('param-color', 'value')],
    prevent_initial_call=False
)
def validate_params(x_val, y_val, color_val):
    """校验参数，避免重复选择"""
    dm = DataManager()
    df = dm.active_df

    if df is None or df.empty:
        return [], [], []

    all_columns = get_labeled_options(df)

    y_options = [opt for opt in all_columns if opt['value'] != x_val]
    color_options = [opt for opt in all_columns if opt['value'] not in [x_val, y_val]]
    size_options = [opt for opt in all_columns if opt['value'] not in [x_val, y_val, color_val]]

    return y_options, color_options, size_options


@callback(
    [Output('chart-container', 'children'),
     Output('generated-code-display', 'value'),
     Output('chart-figure-store', 'data')],
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
     Input('param-marginal-y', 'value'),
     Input('style-title', 'value'),
     Input('style-template', 'value'),
     Input('style-color-scale', 'value'),
     Input('style-show-legend', 'value'),
     Input('style-show-grid', 'value'),
     Input('style-width', 'value'),
     Input('style-height', 'value')],
    [State('chart-library-selector', 'value')],
    prevent_initial_call=True
)
def generate_chart(
    chart_type, x, y, color, size, hover_data,
    facet_row, facet_col, animation_frame,
    trendline, marginal_x, marginal_y,
    style_title, style_template, style_color_scale,
    style_show_legend, style_show_grid,
    style_width, style_height,
    library
):
    """生成图表和代码"""
    dm = DataManager()
    df = dm.active_df

    if df is None or df.empty:
        return html.Div("请先加载数据"), "# 请先加载数据", None

    if not x and not y:
        return html.Div("请至少选择X轴或Y轴"), "# 请配置参数", None

    # 构建参数字典（含样式参数）
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
            # 样式参数
            'title': style_title,
            'template': style_template or 'plotly_dark',
            'color_scale': style_color_scale if style_color_scale else None,
            'show_legend': style_show_legend if style_show_legend is not None else True,
            'show_grid': style_show_grid if style_show_grid is not None else True,
            'width': style_width,
            'height': style_height,
        }
    else:  # seaborn
        params = {
            'x': x,
            'y': y,
            'hue': color,
            'size': size,
            'title': style_title,
            'show_grid': style_show_grid if style_show_grid is not None else True,
            'width': style_width or 800,
            'height': style_height or 480,
        }

    # 移除 None 值
    params = {k: v for k, v in params.items() if v is not None}

    try:
        chart_service = ChartService()
        chart_service.set_library(ChartLibrary(library))

        # 验证chart_type不为None
        if not chart_type:
            return {
                "success": False,
                "error": "图表类型不能为空"
            }

        result = chart_service.create_chart(
            df=df,
            chart_type=ChartType(chart_type),
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
            fig_json = result['chart']
            chart_component = dcc.Graph(
                figure=json.loads(fig_json),
                config={'displayModeBar': True, 'displaylogo': False},
                style={'height': '100%'}
            )
            return chart_component, code, fig_json
        else:  # seaborn
            chart_component = html.Img(
                src=result['chart'],
                style={'width': '100%', 'maxHeight': '500px', 'objectFit': 'contain'}
            )
            return chart_component, code, None

    except Exception as e:
        error_msg = f"生成图表时出错: {str(e)}"
        return html.Div(error_msg, className='text-danger'), f"# {error_msg}", None


@callback(
    Output('download-chart-file', 'data'),
    Input('export-png-btn', 'n_clicks'),
    Input('export-svg-btn', 'n_clicks'),
    Input('export-html-btn', 'n_clicks'),
    State('chart-figure-store', 'data'),
    State('chart-library-selector', 'value'),
    prevent_initial_call=True
)
def export_chart(png_clicks, svg_clicks, html_clicks, fig_json, library):
    """导出图表为 PNG/SVG/HTML"""
    from dash import ctx
    if not fig_json or library != 'plotly':
        return no_update

    triggered = ctx.triggered_id

    try:
        import plotly.io as pio
        fig = go.Figure(json.loads(fig_json))

        if triggered == 'export-png-btn':
            img_bytes = pio.to_image(fig, format='png', width=1200, height=700, scale=2)
            import base64
            b64 = base64.b64encode(img_bytes).decode()
            return dict(
                content=b64,
                filename='chart.png',
                base64=True
            )
        elif triggered == 'export-svg-btn':
            img_bytes = pio.to_image(fig, format='svg', width=1200, height=700)
            return dict(
                content=img_bytes.decode('utf-8'),
                filename='chart.svg'
            )
        elif triggered == 'export-html-btn':
            html_str = pio.to_html(fig, full_html=True, include_plotlyjs='cdn')
            return dict(
                content=html_str,
                filename='chart.html'
            )
    except ImportError:
        # kaleido not installed for image export
        return no_update
    except Exception:
        return no_update

    return no_update


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
