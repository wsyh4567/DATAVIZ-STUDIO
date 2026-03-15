# -*- coding: utf-8 -*-
"""Top navigation bar."""

from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc

import config
from services.project_persistence import PROJECT_EXTENSION


def _project_button(label: str, icon: str, button_id: str) -> dbc.Button:
    return dbc.Button(
        [html.I(className=f"bi {icon} me-2"), label],
        id=button_id,
        color="primary",
        size="sm",
        className="shadow-sm",
        style={
            "fontWeight": "700",
            "borderRadius": "999px",
            "padding": "6px 14px",
            "border": "1px solid rgba(255,255,255,0.1)",
            "background": "linear-gradient(135deg, #FF6B35 0%, #FF8A3D 100%)",
            "color": "white",
        },
    )


def create_navbar() -> html.Div:
    return html.Div(
        className="dvs-topbar",
        children=[
            html.Div(
                className="dvs-topbar__left",
                style={"display": "flex", "alignItems": "center", "gap": "16px", "flex": "1", "overflow": "hidden"},
                children=[
                    html.Span(
                        id="topbar-page-title",
                        style={
                            "fontSize": "1rem",
                            "fontWeight": "700",
                            "color": "var(--text-primary)",
                            "whiteSpace": "nowrap",
                        },
                    ),
                    html.Div(style={"width": "1px", "height": "20px", "background": "var(--border)", "flexShrink": "0"}),
                    html.Div(
                        className="d-flex align-items-center",
                        style={"gap": "10px", "flexShrink": "0"},
                        children=[
                            dcc.Upload(
                                id="project-upload",
                                accept=PROJECT_EXTENSION,
                                children=_project_button("打开项目", "bi-folder2-open", "btn-open-project"),
                            ),
                            _project_button("保存项目", "bi-save", "btn-save-project"),
                        ],
                    ),
                    html.Div(
                        id="topbar-sysinfo",
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "10px",
                            "flexWrap": "nowrap",
                            "overflow": "hidden",
                        },
                    ),
                    html.Div(
                        id="topbar-status-badges",
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[],
                    ),
                ],
            ),
            dcc.Interval(id="sysinfo-interval", interval=1000, n_intervals=0),
            html.Div(
                className="dvs-topbar__actions",
                children=[
                    html.Button(
                        html.I(className="bi bi-lightning"),
                        id="btn-quick-action",
                        className="dvs-topbar__btn btn-hover",
                        title="快速操作",
                    ),
                    html.Button(
                        html.I(className="bi bi-moon-stars"),
                        id="btn-theme-toggle",
                        className="dvs-topbar__btn btn-hover",
                        title="切换主题",
                    ),
                    html.Button(
                        html.I(className="bi bi-gear"),
                        id="btn-settings",
                        className="dvs-topbar__btn btn-hover",
                        title="关于",
                    ),
                    html.A(
                        html.I(className="bi bi-question-circle"),
                        href="https://github.com/wsyh4567/DATAVIZ-STUDIO",
                        target="_blank",
                        className="dvs-topbar__btn btn-hover",
                        title="帮助文档",
                        style={"textDecoration": "none"},
                    ),
                ],
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("关于 DataViz Studio")),
                    dbc.ModalBody(
                        [
                            html.P([html.Strong("版本: "), config.APP_VERSION]),
                            html.P([html.Strong("技术栈: "), "Dash + Plotly + Pandas"]),
                            html.P([html.Strong("协议: "), "MIT License"]),
                            html.Hr(),
                            html.P(config.APP_DESCRIPTION, style={"color": "var(--text-muted)"}),
                        ]
                    ),
                ],
                id="settings-modal",
                is_open=False,
                centered=True,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("保存项目")),
                    dbc.ModalBody(
                        [
                            dbc.Label("项目文件名"),
                            dbc.Input(
                                id="project-name-input",
                                value="dataviz-project",
                                placeholder="输入项目名称",
                            ),
                            html.Div(
                                className="d-flex align-items-center mt-3",
                                style={"gap": "8px"},
                                children=[
                                    dbc.Label("项目里要不要带上数据", className="mb-0"),
                                    html.Span(
                                        "?",
                                        id="project-storage-mode-help",
                                        style={
                                            "display": "inline-flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "width": "18px",
                                            "height": "18px",
                                            "borderRadius": "999px",
                                            "background": "var(--bg-tertiary, #EDF2F7)",
                                            "fontSize": "0.75rem",
                                            "fontWeight": "700",
                                            "cursor": "help",
                                        },
                                    ),
                                ],
                            ),
                            dbc.RadioItems(
                                id="project-storage-mode",
                                className="mt-2",
                                options=[
                                    {"label": "内嵌数据（换台机器也能直接打开）", "value": "embedded"},
                                    {"label": "仅保存引用（项目更小，优先重新读取原始来源）", "value": "reference"},
                                ],
                                value="embedded",
                            ),
                            html.Div(
                                f"导出格式：{PROJECT_EXTENSION} 项目文件",
                                className="small mt-3",
                                style={"color": "var(--text-muted)"},
                            ),
                            dbc.Tooltip(
                                "内嵌数据会把当前数据集一起写进项目文件；仅保存引用会优先记录原始文件、URL 或内置样本来源。"
                                " 如果某个数据集无法可靠重新定位，会自动改成内嵌保存，避免项目再次打开时丢数据。",
                                target="project-storage-mode-help",
                                placement="right",
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("取消", id="btn-cancel-save-project", color="secondary", outline=True),
                            dbc.Button("导出项目", id="btn-confirm-save-project", color="primary"),
                        ]
                    ),
                ],
                id="save-project-modal",
                is_open=False,
                centered=True,
            ),
            dbc.Offcanvas(
                id="quick-action-offcanvas",
                title="快速操作",
                is_open=False,
                placement="end",
                style={"width": "360px"},
                className="dvs-offcanvas-quick",
                children=[
                    html.P("快速跳到常用分析入口。", style={"color": "#718096", "fontSize": "0.8rem", "marginBottom": "16px"}),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/data",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon", children=[html.I(className="bi bi-server")]),
                            html.Div([html.Div("加载数据", className="dvs-quick-action-item__label"), html.Div("CSV / Excel / JSON / Parquet", className="dvs-quick-action-item__sub")]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/workshop",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon", children=[html.I(className="bi bi-hammer")]),
                            html.Div([html.Div("数据清洗", className="dvs-quick-action-item__label"), html.Div("拖拽式步骤、支持撤销和导出", className="dvs-quick-action-item__sub")]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/charts",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon", children=[html.I(className="bi bi-graph-up")]),
                            html.Div([html.Div("创建图表", className="dvs-quick-action-item__label"), html.Div("Plotly / Seaborn 图表和代码导出", className="dvs-quick-action-item__sub")]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/advanced",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon", children=[html.I(className="bi bi-tools")]),
                            html.Div([html.Div("高级工具", className="dvs-quick-action-item__label"), html.Div("聚合导出当前项目上下文", className="dvs-quick-action-item__sub")]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.Hr(style={"margin": "16px 0", "borderColor": "#E8EDF2"}),
                    html.Div(
                        style={"textAlign": "center", "color": "#A0AEC0", "fontSize": "0.75rem"},
                        children=["DataViz Studio v", config.APP_VERSION],
                    ),
                ],
            ),
            dcc.Download(id="project-download"),
        ],
    )
