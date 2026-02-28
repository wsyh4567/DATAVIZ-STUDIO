"""
数据工坊实时预览页面

提供实时数据预览和操作管理功能
"""

import dash
from dash import html, dcc, callback, Input, Output, State, dash_table, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import json

from services.data_workshop.preview_engine import PreviewEngine
from services.data_workshop.step_manager import StepManager
from services.data_workshop.undo_redo_stack import UndoRedoStack
from components.data_workshop.data_grid import create_data_grid, create_data_stats
from components.data_workshop.step_panel import create_step_panel, create_step_header, create_step_actions
from components.data_workshop.toolbar import create_operation_toolbar
from components.data_workshop.code_preview_panel import create_code_modal

# 注册页面
dash.register_page(__name__, path='/data-workshop-preview', name='数据工坊预览')

# 初始化全局组件
preview_engine = PreviewEngine(max_preview_rows=1000)
step_manager = StepManager()
undo_stack = UndoRedoStack()

# 页面布局
layout = dbc.Container([
    # 标题栏
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2([
                    html.I(className="bi bi-magic me-3", style={"color": "var(--accent)"}),
                    "数据工坊 - 实时预览"
                ], className="mb-2", style={"fontWeight": "600"}),
                html.P("所见即所得的数据清洗和转换体验", 
                      style={"color": "var(--text-muted)", "fontSize": "0.875rem"})
            ])
        ], width=8),
        dbc.Col([
            html.Div([
                dbc.Button([
                    html.I(className="bi bi-code-slash me-2"),
                    "查看代码"
                ], id="btn-view-code", color="success", size="sm", outline=True, className="me-2"),
                dbc.Button([
                    html.I(className="bi bi-download me-2"),
                    "导出"
                ], id="btn-export", color="primary", size="sm", outline=True),
            ], className="d-flex justify-content-end")
        ], width=4),
    ], className="mb-4"),
    
    # 主要内容区
    dbc.Row([
        # 左侧：操作工具栏
        dbc.Col([
            create_operation_toolbar()
        ], width=2),
        
        # 中间：数据预览区
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.Span("数据预览", style={"fontWeight": "bold"}),
                        html.Div(id="data-stats", children=[
                            dbc.Badge("0 行", color="primary", className="me-1"),
                            dbc.Badge("0 列", color="info"),
                        ]),
                    ], className="d-flex align-items-center justify-content-between")
                ]),
                dbc.CardBody([
                    # 数据表格
                    html.Div(id="data-table-container", children=[
                        html.Div([
                            html.I(className="bi bi-inbox", style={"fontSize": "3rem", "color": "var(--text-muted)"}),
                            html.P("暂无数据", className="text-muted mt-3"),
                            html.P("请先加载数据集", style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
                        ], className="text-center py-5")
                    ]),
                    
                    # 加载示例数据按钮
                    html.Div([
                        dbc.Button([
                            html.I(className="bi bi-file-earmark-spreadsheet me-2"),
                            "加载示例数据"
                        ], id="btn-load-sample", color="primary", className="mt-3")
                    ], className="text-center")
                ], style={"padding": "1rem"})
            ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
        ], width=7),
        
        # 右侧：步骤管理面板
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Div(id="step-header", children=create_step_header(0))
                ]),
                dbc.CardBody([
                    html.Div(id="step-list", children=create_step_panel([])),
                    create_step_actions(),
                ], style={"padding": "1rem", "maxHeight": "600px", "overflowY": "auto"})
            ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
        ], width=3),
    ]),
    
    # 数据存储
    dcc.Store(id='original-data-store'),
    dcc.Store(id='preview-data-store'),
    dcc.Store(id='pipeline-store', data=[]),
    dcc.Store(id='undo-redo-store', data={'can_undo': False, 'can_redo': False}),
    
    # 代码预览模态框
    create_code_modal(),
    
    # 下载组件
    dcc.Download(id='download-code'),
    
    # 状态提示
    html.Div(id='copy-code-status', style={'display': 'none'}),
    html.Div(id='preview-stats-display', style={'display': 'none'}),
    
], fluid=True, className="py-4")


# 回调：加载示例数据
@callback(
    Output('original-data-store', 'data'),
    Output('data-table-container', 'children'),
    Output('data-stats', 'children'),
    Input('btn-load-sample', 'n_clicks'),
    prevent_initial_call=True
)
def load_sample_data(n_clicks):
    """加载示例数据"""
    # 创建示例数据
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
        'age': ['25', '30', '35', '28', '32', '29', '31', '27'],  # 故意使用字符串
        'city': ['NYC', 'LA', 'SF', 'NYC', 'LA', 'SF', 'NYC', 'LA'],
        'salary': [50000, 60000, 75000, 55000, 65000, 58000, 62000, 53000],
        'department': ['Sales', 'Engineering', 'Sales', 'Engineering', 'Sales', 'Engineering', 'Sales', 'Engineering']
    })
    
    # 创建数据表格
    table = create_data_grid(df, preview_mode=False)
    
    # 创建统计信息
    stats = create_data_stats(df)
    
    return df.to_json(date_format='iso', orient='split'), table, stats


# 回调：更新步骤列表
@callback(
    Output('step-list', 'children'),
    Output('step-header', 'children'),
    Output('btn-clear-steps', 'disabled'),
    Input('pipeline-store', 'data'),
)
def update_step_list(pipeline):
    """更新步骤列表显示"""
    if not pipeline:
        return create_step_panel([]), create_step_header(0), True
    
    # 创建步骤面板
    step_panel = create_step_panel(pipeline, step_manager)
    header = create_step_header(len(pipeline))
    
    return step_panel, header, False


# 回调：更新撤销重做按钮状态
@callback(
    Output('btn-undo', 'disabled'),
    Output('btn-redo', 'disabled'),
    Input('undo-redo-store', 'data'),
)
def update_undo_redo_buttons(undo_redo_state):
    """更新撤销重做按钮状态"""
    return not undo_redo_state['can_undo'], not undo_redo_state['can_redo']


# 演示信息
@callback(
    Output('data-table-container', 'children', allow_duplicate=True),
    Input('btn-filter', 'n_clicks'),
    State('original-data-store', 'data'),
    prevent_initial_call=True
)
def demo_filter(n_clicks, data_json):
    """演示筛选功能"""
    if not data_json:
        return dash.no_update
    
    # 解析数据
    df = pd.read_json(data_json, orient='split')
    
    # 应用筛选（演示）
    pipeline = [{
        'operation': 'filter',
        'params': {'column': 'city', 'operator': '==', 'value': 'NYC'}
    }]
    
    result = preview_engine.compute_preview(df, pipeline)
    
    if 'error' in result:
        return html.Div([
            dbc.Alert(f"操作失败: {result['error']}", color="danger")
        ])
    
    # 创建预览表格
    preview_df = result['preview_df']
    table = dash_table.DataTable(
        data=preview_df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in preview_df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'monospace'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        page_size=10,
    )
    
    return [
        dbc.Alert([
            html.I(className="bi bi-info-circle me-2"),
            f"筛选预览: {result['full_rows']} 行 × {result['full_cols']} 列 "
            f"(耗时 {result['execution_time']:.3f}秒)"
        ], color="info", className="mb-3"),
        table
    ]
