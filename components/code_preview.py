# -*- coding: utf-8 -*-
"""代码预览组件 — 显示生成的 Python 代码

提供代码显示、复制、下载功能。
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_code_preview_panel():
    """创建代码预览面板
    
    Returns:
        Dash 组件
    """
    return html.Div([
        # 标题和操作按钮
        html.Div([
            html.H6("生成的 Python 代码", className="code-preview-title"),
            dbc.ButtonGroup([
                dbc.Button(
                    [html.I(className="bi bi-clipboard me-1"), "复制代码"],
                    id="copy-code-btn",
                    size="sm",
                    color="primary",
                    outline=True
                ),
                dbc.Button(
                    [html.I(className="bi bi-download me-1"), "下载 .py"],
                    id="download-py-btn",
                    size="sm",
                    color="secondary",
                    outline=True
                ),
                dbc.Button(
                    [html.I(className="bi bi-journal-code me-1"), "导出 Jupyter"],
                    id="export-jupyter-btn",
                    size="sm",
                    color="info",
                    outline=True
                ),
            ], size="sm"),
        ], className="code-preview-header"),
        
        # 代码显示区域
        html.Div([
            dcc.Textarea(
                id='generated-code-display',
                value='# 配置参数后，这里将显示生成的 Python 代码\n# 代码可以直接在 Python 环境中运行',
                readOnly=True,
                style={
                    'width': '100%',
                    'height': '400px',
                    'fontFamily': 'JetBrains Mono, Consolas, monospace',
                    'fontSize': '13px',
                    'backgroundColor': '#1e1e1e',
                    'color': '#d4d4d4',
                    'padding': '16px',
                    'border': '1px solid #333',
                    'borderRadius': '8px',
                    'lineHeight': '1.6',
                    'resize': 'vertical'
                }
            ),
        ], className="code-preview-content"),
        
        # 下载组件
        dcc.Download(id='download-code-file'),
        
        # Toast 通知
        dbc.Toast(
            "代码已复制到剪贴板！",
            id="copy-success-toast",
            header="成功",
            is_open=False,
            dismissable=True,
            icon="success",
            duration=3000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
        ),
        
    ], className='code-preview-panel', style={'marginTop': '20px'})
