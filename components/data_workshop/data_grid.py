"""
数据表格组件

基于Dash AG Grid的高性能数据表格
"""

from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from typing import Optional


def create_data_grid(df: Optional[pd.DataFrame] = None, preview_mode: bool = False) -> html.Div:
    """创建数据表格组件
    
    Args:
        df: 数据框
        preview_mode: 是否为预览模式
    
    Returns:
        数据表格组件
    """
    if df is None or df.empty:
        return html.Div([
            html.Div([
                html.I(className="bi bi-inbox", style={"fontSize": "3rem", "color": "var(--text-muted)"}),
                html.P("暂无数据", className="text-muted mt-3"),
                html.P("请先加载数据集", className="text-muted", style={"fontSize": "0.875rem"}),
            ], className="text-center py-5")
        ])
    
    # 配置列定义
    columns = []
    for col in df.columns:
        col_def = {
            'name': col,
            'id': col,
            'editable': not preview_mode,  # 预览模式不可编辑
        }
        
        # 根据数据类型设置列配置
        if df[col].dtype in ['int64', 'float64', 'Int64', 'Float64']:
            col_def['type'] = 'numeric'
        
        columns.append(col_def)
    
    # 创建表格
    table = dash_table.DataTable(
        id='data-grid',
        data=df.to_dict('records'),
        columns=columns,
        
        # 样式配置
        style_table={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'maxHeight': '600px',
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'var(--font-mono)',
            'fontSize': '0.875rem',
            'backgroundColor': 'var(--bg-secondary)',
            'color': 'var(--text-primary)',
            'border': '1px solid var(--border)',
        },
        style_header={
            'backgroundColor': 'var(--bg-tertiary)',
            'fontWeight': 'bold',
            'color': 'var(--text-primary)',
            'border': '1px solid var(--border)',
            'position': 'sticky',
            'top': 0,
            'zIndex': 1,
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'var(--bg-primary)',
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': 'var(--accent)',
                'color': 'white',
            },
        ],
        
        # 功能配置
        page_size=50,
        page_action='native',
        sort_action='native',
        sort_mode='multi',
        filter_action='native',
        row_selectable='multi',
        selected_rows=[],
        
        # 固定列
        fixed_rows={'headers': True},
        
        # 虚拟化
        virtualization=True,
    )
    
    # 添加预览模式标识
    if preview_mode:
        return html.Div([
            dbc.Alert([
                html.I(className="bi bi-eye me-2"),
                "预览模式 - 数据未保存",
            ], color="info", className="mb-3"),
            table
        ])
    
    return table


def create_empty_grid() -> html.Div:
    """创建空表格占位符
    
    Returns:
        空表格占位符组件
    """
    return html.Div([
        html.Div([
            html.I(className="bi bi-inbox", style={"fontSize": "3rem", "color": "var(--text-muted)"}),
            html.P("暂无数据", className="text-muted mt-3"),
            html.P("请先加载数据集", className="text-muted", style={"fontSize": "0.875rem"}),
        ], className="text-center py-5")
    ])


def create_data_stats(df: pd.DataFrame) -> html.Div:
    """创建数据统计信息
    
    Args:
        df: 数据框
    
    Returns:
        统计信息组件
    """
    return html.Div([
        dbc.Badge(f"{len(df):,} 行", color="primary", className="me-2"),
        dbc.Badge(f"{len(df.columns)} 列", color="info", className="me-2"),
        dbc.Badge(f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB", color="secondary"),
    ], className="d-flex align-items-center")
