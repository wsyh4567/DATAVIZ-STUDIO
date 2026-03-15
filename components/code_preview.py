# -*- coding: utf-8 -*-
"""Code preview component for generated Python and notebook export."""

from dash import dcc, html
import dash_bootstrap_components as dbc


def create_code_preview_panel():
    """Create the code preview panel."""
    return html.Div([
        html.Div([
            html.H6("Generated Python Code", className="code-preview-title"),
            dbc.ButtonGroup([
                dbc.Button(
                    [html.I(className="bi bi-clipboard me-1"), "复制代码"],
                    id="copy-code-btn",
                    size="sm",
                    color="primary",
                    outline=True,
                    className="btn-hover",
                ),
                dbc.Button(
                    [html.I(className="bi bi-download me-1"), "下载 .py"],
                    id="download-py-btn",
                    size="sm",
                    color="secondary",
                    outline=True,
                    className="btn-hover",
                ),
                dbc.Button(
                    [html.I(className="bi bi-journal-code me-1"), "导出 Jupyter"],
                    id="export-jupyter-btn",
                    size="sm",
                    color="info",
                    outline=True,
                    className="btn-hover",
                ),
            ], size="sm"),
        ], className="code-preview-header"),
        html.Div([
            dcc.Textarea(
                id="generated-code-display",
                value="# 配置参数后，这里将显示生成的 Python 代码\n# 代码可以直接在 Python 环境中运行",
                readOnly=True,
                style={
                    "width": "100%",
                    "height": "400px",
                    "fontFamily": "JetBrains Mono, Consolas, monospace",
                    "fontSize": "13px",
                    "backgroundColor": "#1e1e1e",
                    "color": "#d4d4d4",
                    "padding": "16px",
                    "border": "1px solid #333",
                    "borderRadius": "8px",
                    "lineHeight": "1.6",
                    "resize": "vertical",
                },
            ),
        ], className="code-preview-content"),
        dcc.Download(id="download-code-file"),
    ], className="code-preview-panel", style={"marginTop": "20px"})
