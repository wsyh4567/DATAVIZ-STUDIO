"""
步骤管理面板组件

显示和管理操作步骤
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import List, Dict
from services.data_workshop.step_manager import StepManager


def create_step_panel(pipeline: List[Dict], step_manager: StepManager = None) -> html.Div:
    """创建步骤管理面板
    
    Args:
        pipeline: 操作流水线
        step_manager: 步骤管理器实例
    
    Returns:
        步骤面板组件
    """
    if step_manager is None:
        step_manager = StepManager()
    
    if not pipeline:
        return html.Div([
            html.Div([
                html.I(className="bi bi-list-task", style={"fontSize": "2.5rem", "color": "var(--text-muted)"}),
                html.P("暂无操作步骤", className="text-muted mt-3", style={"fontSize": "0.875rem"}),
                html.P("开始添加数据操作", className="text-muted", style={"fontSize": "0.75rem"}),
            ], className="text-center py-4")
        ])
    
    # 创建步骤卡片
    step_cards = []
    for i, step in enumerate(pipeline):
        # 生成步骤描述
        desc = step_manager.get_step_description(step)
        
        # 获取操作图标
        icon = get_operation_icon(step['operation'])
        
        # 创建步骤卡片
        card = dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Div([
                        html.I(className=f"bi {icon} me-2", style={"color": "var(--accent)"}),
                        html.Span(f"步骤 {i+1}", className="badge bg-primary me-2"),
                    ], className="d-flex align-items-center mb-2"),
                    html.Div(desc, style={
                        "fontSize": "0.875rem",
                        "color": "var(--text-primary)",
                        "marginBottom": "0.5rem"
                    }),
                    html.Div([
                        html.Small([
                            html.I(className="bi bi-clock me-1"),
                            step.get('timestamp', 'N/A')[:19] if 'timestamp' in step else 'N/A'
                        ], style={"color": "var(--text-muted)"}),
                    ]),
                ]),
                html.Div([
                    dbc.ButtonGroup([
                        dbc.Button(
                            html.I(className="bi bi-pencil"),
                            id={'type': 'edit-step', 'index': i},
                            size="sm",
                            color="info",
                            outline=True,
                            title="编辑步骤",
                            className="btn-hover"
                        ),
                        dbc.Button(
                            html.I(className="bi bi-trash"),
                            id={'type': 'delete-step', 'index': i},
                            size="sm",
                            color="danger",
                            outline=True,
                            title="删除步骤",
                            className="btn-hover"
                        ),
                    ], size="sm"),
                ], className="mt-2"),
            ], style={"padding": "0.75rem"})
        ], className="mb-2", style={
            "backgroundColor": "var(--bg-secondary)",
            "border": "1px solid var(--border)",
            "cursor": "pointer",
        }, id={'type': 'step-card', 'index': i})
        
        step_cards.append(card)
    
    return html.Div(step_cards, id='step-list-container')


def create_step_header(step_count: int) -> html.Div:
    """创建步骤面板头部
    
    Args:
        step_count: 步骤数量
    
    Returns:
        头部组件
    """
    return html.Div([
        html.Div([
            html.Span("操作步骤", style={"fontWeight": "bold"}),
            dbc.Badge(str(step_count), color="secondary", className="ms-2"),
        ], className="d-flex align-items-center justify-content-between"),
    ])


def create_step_actions() -> html.Div:
    """创建步骤操作按钮
    
    Returns:
        操作按钮组件
    """
    return html.Div([
        html.Hr(className="my-3"),
        dbc.ButtonGroup([
            dbc.Button([
                html.I(className="bi bi-download me-2"),
                "导出代码"
            ], id="btn-export-code", color="primary", size="sm", outline=True, className="btn-hover"),
            dbc.Button([
                html.I(className="bi bi-trash me-2"),
                "清空步骤"
            ], id="btn-clear-steps", color="danger", size="sm", outline=True, className="btn-hover"),
        ], className="w-100"),
    ])


def get_operation_icon(operation: str) -> str:
    """获取操作对应的图标
    
    Args:
        operation: 操作类型
    
    Returns:
        Bootstrap图标类名
    """
    icon_map = {
        'filter': 'bi-funnel',
        'drop_column': 'bi-trash',
        'rename_column': 'bi-pencil',
        'type_conversion': 'bi-type',
        'fill_missing': 'bi-droplet',
        'drop_duplicates': 'bi-files',
        'sort': 'bi-sort-down',
        'split_column': 'bi-scissors',
        'merge_columns': 'bi-union',
        'replace_value': 'bi-arrow-repeat',
    }
    return icon_map.get(operation, 'bi-gear')


def create_empty_step_panel() -> html.Div:
    """创建空步骤面板
    
    Returns:
        空面板组件
    """
    return html.Div([
        html.Div([
            html.I(className="bi bi-list-task", style={"fontSize": "2.5rem", "color": "var(--text-muted)"}),
            html.P("暂无操作步骤", className="text-muted mt-3", style={"fontSize": "0.875rem"}),
            html.P("开始添加数据操作", className="text-muted", style={"fontSize": "0.75rem"}),
        ], className="text-center py-4")
    ])
