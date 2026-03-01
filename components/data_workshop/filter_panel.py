"""
筛选面板组件

提供可视化的筛选条件配置界面
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Optional


def create_filter_panel(column: str = None, dtype: str = 'object') -> html.Div:
    """创建筛选面板
    
    Args:
        column: 列名
        dtype: 数据类型
    
    Returns:
        筛选面板组件
    """
    if column is None:
        return create_empty_filter_panel()
    
    if dtype in ['int64', 'float64', 'Int64', 'Float64']:
        return create_numeric_filter(column)
    elif dtype == 'object':
        return create_text_filter(column)
    elif 'datetime' in str(dtype):
        return create_date_filter(column)
    else:
        return create_generic_filter(column)


def create_numeric_filter(column: str) -> html.Div:
    """创建数值列筛选面板
    
    Args:
        column: 列名
    
    Returns:
        数值筛选面板
    """
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-funnel me-2"),
            f"筛选: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            # 操作符选择
            html.Label("条件", className="form-label", style={"fontSize": "0.875rem"}),
            dcc.Dropdown(
                id={'type': 'filter-operator', 'column': column},
                options=[
                    {'label': '等于 (=)', 'value': '=='},
                    {'label': '不等于 (≠)', 'value': '!='},
                    {'label': '大于 (>)', 'value': '>'},
                    {'label': '小于 (<)', 'value': '<'},
                    {'label': '大于等于 (≥)', 'value': '>='},
                    {'label': '小于等于 (≤)', 'value': '<='},
                    {'label': '范围', 'value': 'between'},
                ],
                value='==',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            
            # 数值输入
            html.Label("值", className="form-label", style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'filter-value', 'column': column},
                type='number',
                placeholder='输入数值',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            
            # 范围输入（当选择between时显示）
            html.Div([
                html.Label("最小值", className="form-label", style={"fontSize": "0.875rem"}),
                dbc.Input(
                    id={'type': 'filter-min', 'column': column},
                    type='number',
                    placeholder='最小值',
                    className='mb-2',
                    style={'fontSize': '0.875rem'}
                ),
                html.Label("最大值", className="form-label", style={"fontSize": "0.875rem"}),
                dbc.Input(
                    id={'type': 'filter-max', 'column': column},
                    type='number',
                    placeholder='最大值',
                    className='mb-3',
                    style={'fontSize': '0.875rem'}
                ),
            ], id={'type': 'filter-range-inputs', 'column': column}, style={'display': 'none'}),
            
            # 预览信息
            html.Div(id={'type': 'filter-preview', 'column': column}, className='mb-3'),
            
            # 操作按钮
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用筛选"
                ], id={'type': 'apply-filter', 'column': column}, color="primary", size="sm", className="btn-hover"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-filter', 'column': column}, color="secondary", size="sm", outline=True, className="btn-hover"),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_text_filter(column: str) -> html.Div:
    """创建文本列筛选面板
    
    Args:
        column: 列名
    
    Returns:
        文本筛选面板
    """
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-funnel me-2"),
            f"筛选: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            # 操作符选择
            html.Label("条件", className="form-label", style={"fontSize": "0.875rem"}),
            dcc.Dropdown(
                id={'type': 'filter-operator', 'column': column},
                options=[
                    {'label': '包含', 'value': 'contains'},
                    {'label': '不包含', 'value': 'not_contains'},
                    {'label': '等于', 'value': '=='},
                    {'label': '不等于', 'value': '!='},
                    {'label': '开头是', 'value': 'startswith'},
                    {'label': '结尾是', 'value': 'endswith'},
                    {'label': '正则表达式', 'value': 'regex'},
                ],
                value='contains',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            
            # 文本输入
            html.Label("值", className="form-label", style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'filter-value', 'column': column},
                type='text',
                placeholder='输入文本',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            
            # 选项
            dbc.Checklist(
                id={'type': 'filter-options', 'column': column},
                options=[
                    {'label': ' 忽略大小写', 'value': 'case_insensitive'}
                ],
                value=[],
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            
            # 预览信息
            html.Div(id={'type': 'filter-preview', 'column': column}, className='mb-3'),
            
            # 操作按钮
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用筛选"
                ], id={'type': 'apply-filter', 'column': column}, color="primary", size="sm", className="btn-hover"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-filter', 'column': column}, color="secondary", size="sm", outline=True, className="btn-hover"),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_date_filter(column: str) -> html.Div:
    """创建日期列筛选面板
    
    Args:
        column: 列名
    
    Returns:
        日期筛选面板
    """
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-funnel me-2"),
            f"筛选: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            # 操作符选择
            html.Label("条件", className="form-label", style={"fontSize": "0.875rem"}),
            dcc.Dropdown(
                id={'type': 'filter-operator', 'column': column},
                options=[
                    {'label': '等于', 'value': '=='},
                    {'label': '早于', 'value': '<'},
                    {'label': '晚于', 'value': '>'},
                    {'label': '日期范围', 'value': 'between'},
                ],
                value='==',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            
            # 日期选择
            html.Label("日期", className="form-label", style={"fontSize": "0.875rem"}),
            dcc.DatePickerSingle(
                id={'type': 'filter-date', 'column': column},
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            
            # 预览信息
            html.Div(id={'type': 'filter-preview', 'column': column}, className='mb-3'),
            
            # 操作按钮
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用筛选"
                ], id={'type': 'apply-filter', 'column': column}, color="primary", size="sm", className="btn-hover"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-filter', 'column': column}, color="secondary", size="sm", outline=True, className="btn-hover"),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_generic_filter(column: str) -> html.Div:
    """创建通用筛选面板
    
    Args:
        column: 列名
    
    Returns:
        通用筛选面板
    """
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-funnel me-2"),
            f"筛选: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.P("该列类型暂不支持可视化筛选",
                  style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
            dbc.Button("关闭", id={'type': 'cancel-filter', 'column': column},
                      color="secondary", size="sm", className="w-100 btn-hover"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_empty_filter_panel() -> html.Div:
    """创建空筛选面板
    
    Returns:
        空面板
    """
    return html.Div([
        html.Div([
            html.I(className="bi bi-funnel", style={"fontSize": "2.5rem", "color": "var(--text-muted)"}),
            html.P("选择列进行筛选", className="text-muted mt-3", style={"fontSize": "0.875rem"}),
        ], className="text-center py-4")
    ])


def create_filter_preview_info(matched_rows: int, total_rows: int) -> html.Div:
    """创建筛选预览信息
    
    Args:
        matched_rows: 匹配的行数
        total_rows: 总行数
    
    Returns:
        预览信息组件
    """
    percentage = (matched_rows / total_rows * 100) if total_rows > 0 else 0
    
    return dbc.Alert([
        html.I(className="bi bi-info-circle me-2"),
        f"匹配 {matched_rows:,} 行 / {total_rows:,} 行 ({percentage:.1f}%)"
    ], color="info", className="mb-0", style={"fontSize": "0.875rem"})
