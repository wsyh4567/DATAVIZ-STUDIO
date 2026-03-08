"""
数据表格组件

基于 Dash DataTable 的高性能数据表格
- 双行列头：第一行 列名 / 第二行 dtype + 有效/空 统计
- 无独立统计条（直接集成进表头）
"""

from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from typing import Optional


# ── 数据类型 → 显示图标映射 ──
DTYPE_ICONS = {
    'int64': '123', 'int32': '123', 'Int64': '123', 'Int32': '123',
    'float64': '1.2', 'float32': '1.2', 'Float64': '1.2', 'Float32': '1.2',
    'object': 'Abc', 'string': 'Abc',
    'category': '🏷', 'bool': 'T/F', 'boolean': 'T/F',
    'datetime64[ns]': '📅', 'timedelta64[ns]': '⏱',
}


def _get_dtype_icon(dtype) -> str:
    dtype_str = str(dtype)
    if dtype_str in DTYPE_ICONS:
        return DTYPE_ICONS[dtype_str]
    for key, icon in DTYPE_ICONS.items():
        if dtype_str.startswith(key.split('[')[0]):
            return icon
    return '?'


def create_data_grid(df: Optional[pd.DataFrame] = None, preview_mode: bool = False) -> html.Div:
    """创建数据表格组件（单行列头 + 外部 Power Query 风格统计条）"""
    if df is None or df.empty:
        return html.Div([
            html.Div([
                html.I(className="bi bi-inbox", style={"fontSize": "3rem", "color": "var(--text-muted)"}),
                html.P("暂无数据", className="text-muted mt-3"),
                html.P("请先加载数据集", className="text-muted", style={"fontSize": "0.875rem"}),
            ], className="text-center py-5")
        ])

    total = len(df)

    # 顶部全局统计面板 (Power Query 风格彩色小卡片)
    stats_panels = []
    columns = []

    for col in df.columns:
        dtype_icon = _get_dtype_icon(df[col].dtype)
        null_count = int(df[col].isnull().sum())
        valid_count = total - null_count
        null_pct = round(null_count / total * 100)
        valid_pct = 100 - null_pct

        # 构建头部统计块 (彩色进度条 + 文字说明)
        stats_panels.append(
            html.Div([
                html.Div([
                    html.Span(dtype_icon, style={"color": "var(--text-muted)", "marginRight": "4px"}),
                    html.Span(col, style={"fontWeight": "600", "color": "var(--text-primary)"})
                ], style={"fontSize": "0.75rem", "marginBottom": "6px", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"}),
                
                html.Div([
                    html.Div(style={"width": f"{valid_pct}%", "backgroundColor": "#10B981", "height": "100%"}),  # 绿色代表有效
                    html.Div(style={"width": f"{null_pct}%", "backgroundColor": "#EF4444", "height": "100%"})   # 红色代表空/错误
                ], style={"display": "flex", "height": "4px", "width": "100%", "borderRadius": "2px", "overflow": "hidden"}),
                
                html.Div([
                    html.Span([html.Span("●", style={"color": "#10B981"}), f" 有效 {valid_pct}%"]),
                    html.Span([html.Span("●", style={"color": "#EF4444"}), f" 空 {null_pct}%"]) if null_pct > 0 else None
                ], style={"display": "flex", "justifyContent": "space-between", "fontSize": "0.65rem", "marginTop": "4px", "color": "var(--text-secondary)"})
            ], style={"minWidth": "140px", "maxWidth": "200px", "padding": "8px 10px", "backgroundColor": "white", "border": "1px solid var(--border)", "borderRadius": "8px", "flexShrink": "0", "boxShadow": "0 1px 2px rgba(0,0,0,0.02)"})
        )

        # 单行列头 (仅保留图标和名称)
        col_def = {
            'name': f"{dtype_icon} {col}",
            'id': col,
            'editable': not preview_mode,
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_def['type'] = 'numeric'

        columns.append(col_def)

    stats_bar = html.Div(
        stats_panels,
        style={
            "display": "flex",
            "gap": "8px",
            "padding": "4px 4px 12px 4px",
            "overflowX": "auto",
            "borderBottom": "1px solid var(--border)",
            "marginBottom": "8px",
            # 隐藏滚动条但保留功能
            "scrollbarWidth": "thin", 
        }
    )

    table = dash_table.DataTable(
        id='data-grid',
        data=df.to_dict('records'),
        columns=columns,

        style_table={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'maxHeight': 'calc(100vh - 310px)',  # 为 stats_bar 留出空间
        },
        style_cell={
            'textAlign': 'left',
            'padding': '8px 12px',
            'fontFamily': '"Cascadia Mono", "Consolas", monospace',
            'fontSize': '0.82rem',
            'backgroundColor': 'var(--bg-secondary)',
            'color': 'var(--text-primary)',
            'border': '1px solid #E2E8F0',
            'minWidth': '120px',  # 增大最小宽度，防止第一列等价列被挤压
            'maxWidth': '280px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
        style_header={
            'backgroundColor': '#EDF2F7',
            'fontWeight': '600',
            'color': '#2D3748',
            'border': '1px solid #CBD5E0',
            'position': 'sticky',
            'top': 0,
            'zIndex': 1,
            'fontSize': '0.78rem',
            'padding': '8px 12px',
            'whiteSpace': 'nowrap',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#FAFBFC',
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': 'rgba(255, 107, 53, 0.12)',
                'border': '1px solid rgba(255, 107, 53, 0.3)',
            },
        ],

        page_size=100,
        page_action='native',
        sort_action='native',
        sort_mode='multi',
        row_selectable='multi',
        selected_rows=[],
        fixed_rows={'headers': True},
        css=[
            {"selector": ".dash-spreadsheet tr th:first-child", "rule": "min-width: 60px; max-width: 60px; width: 60px !important;"},
            {"selector": ".dash-spreadsheet tr td:first-child", "rule": "min-width: 60px; max-width: 60px; width: 60px !important; text-align: center;"},
        ],
    )

    components = []
    if preview_mode:
        components.append(dbc.Alert([
            html.I(className="bi bi-eye me-2"),
            "预览模式 - 数据未保存",
        ], color="info", className="mb-2 py-1", style={"fontSize": "0.8rem"}))
    
    components.append(stats_bar)
    components.append(table)

    return html.Div(components)


def create_empty_grid() -> html.Div:
    return html.Div([
        html.Div([
            html.I(className="bi bi-inbox", style={"fontSize": "3rem", "color": "var(--text-muted)"}),
            html.P("暂无数据", className="text-muted mt-3"),
            html.P("请先加载数据集", className="text-muted", style={"fontSize": "0.875rem"}),
        ], className="text-center py-5")
    ])


def create_data_stats(df: pd.DataFrame) -> html.Div:
    return html.Div([
        dbc.Badge(f"{len(df):,} 行", color="primary", className="me-1"),
        dbc.Badge(f"{len(df.columns)} 列", color="info", className="me-1"),
        dbc.Badge(f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB", color="secondary"),
    ], className="d-flex align-items-center")
