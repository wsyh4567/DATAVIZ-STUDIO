"""
代码预览面板组件

显示生成的Python代码并提供复制/下载功能
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Optional


def create_code_preview_panel(code: str = "", show_header: bool = True) -> html.Div:
    """创建代码预览面板
    
    Args:
        code: Python代码字符串
        show_header: 是否显示面板头部
    
    Returns:
        代码预览面板组件
    """
    if not code:
        return create_empty_code_panel()
    
    panel_content = [
        # 代码显示区
        html.Div([
            html.Pre([
                html.Code(code, className="language-python")
            ], style={
                "backgroundColor": "var(--bg-primary)",
                "padding": "1rem",
                "borderRadius": "4px",
                "maxHeight": "500px",
                "overflowY": "auto",
                "fontSize": "0.875rem",
                "fontFamily": "monospace",
                "border": "1px solid var(--border)"
            })
        ], id="code-display-area"),
        
        # 操作按钮
        html.Div([
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-clipboard me-2"),
                    "复制代码"
                ], id="btn-copy-code", color="primary", size="sm", outline=True),
                dbc.Button([
                    html.I(className="bi bi-download me-2"),
                    "下载 .py"
                ], id="btn-download-code", color="success", size="sm", outline=True),
            ], className="w-100")
        ], className="mt-3")
    ]
    
    if show_header:
        return dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.Span([
                        html.I(className="bi bi-code-slash me-2"),
                        "生成的Python代码"
                    ], style={"fontWeight": "bold"}),
                    dbc.Badge(f"{len(code.splitlines())} 行", color="info", className="ms-2"),
                ], className="d-flex align-items-center")
            ]),
            dbc.CardBody(panel_content, style={"padding": "1rem"})
        ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
    else:
        return html.Div(panel_content)


def create_empty_code_panel() -> html.Div:
    """创建空代码面板
    
    Returns:
        空面板组件
    """
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-code-slash me-2"),
            "生成的Python代码"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Div([
                html.I(className="bi bi-file-code", 
                      style={"fontSize": "2.5rem", "color": "var(--text-muted)"}),
                html.P("暂无代码", className="text-muted mt-3", style={"fontSize": "0.875rem"}),
                html.P("执行操作后将自动生成Python代码", 
                      style={"color": "var(--text-muted)", "fontSize": "0.75rem"}),
            ], className="text-center py-4", id="code-display-area")
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_code_modal(code: str = "") -> dbc.Modal:
    """创建代码预览模态框
    
    Args:
        code: Python代码字符串
    
    Returns:
        模态框组件
    """
    return dbc.Modal([
        dbc.ModalHeader([
            html.I(className="bi bi-code-slash me-2"),
            "Python代码预览"
        ]),
        dbc.ModalBody([
            create_code_preview_panel(code, show_header=False)
        ]),
        dbc.ModalFooter([
            dbc.Button("关闭", id="btn-close-code-modal", color="secondary", size="sm")
        ])
    ], id="code-preview-modal", size="lg", is_open=False)


def create_code_stats(code: str) -> html.Div:
    """创建代码统计信息
    
    Args:
        code: Python代码字符串
    
    Returns:
        统计信息组件
    """
    lines = code.splitlines()
    total_lines = len(lines)
    code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    comment_lines = len([l for l in lines if l.strip().startswith('#')])
    
    return html.Div([
        dbc.Badge([
            html.I(className="bi bi-file-text me-1"),
            f"{total_lines} 行"
        ], color="primary", className="me-2"),
        dbc.Badge([
            html.I(className="bi bi-code me-1"),
            f"{code_lines} 代码"
        ], color="success", className="me-2"),
        dbc.Badge([
            html.I(className="bi bi-chat-left-text me-1"),
            f"{comment_lines} 注释"
        ], color="info"),
    ], className="d-flex align-items-center")


def create_code_export_options() -> html.Div:
    """创建代码导出选项
    
    Returns:
        导出选项组件
    """
    return html.Div([
        html.Label("导出选项", className="form-label", style={"fontSize": "0.875rem", "fontWeight": "bold"}),
        dbc.Checklist(
            id="code-export-options",
            options=[
                {'label': ' 包含导入语句', 'value': 'include_imports'},
                {'label': ' 包含注释说明', 'value': 'include_comments'},
                {'label': ' 包含数据加载代码', 'value': 'include_loading'},
                {'label': ' 格式化代码 (Black)', 'value': 'format_code'},
            ],
            value=['include_imports', 'include_comments', 'include_loading'],
            className='mb-3',
            style={'fontSize': '0.875rem'}
        ),
    ])
