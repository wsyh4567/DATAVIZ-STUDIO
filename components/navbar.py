# -*- coding: utf-8 -*-
"""DataViz Studio — 顶部导航栏组件

Monarch Money 风格：左侧品牌 Logo + 页面标题，右侧操作区含快速操作按钮。
"""

from __future__ import annotations

from dash import html, dcc
import dash_bootstrap_components as dbc

import config

# 路由路径 → 页面标题映射
_PAGE_LABELS = {
    "/":           "欢迎",
    "/canvas":     "数据画布",
    "/data":       "数据中心",
    "/workshop":   "数据工坊",
    "/charts":     "图表工作室",
    "/stats":      "统计实验室",
    "/profiling":  "数据概况",
    "/dashboard":  "仪表盘",
    "/advanced":   "高级工具",
}


def create_navbar() -> html.Div:
    """返回顶部导航栏布局（Monarch 风格）。"""
    return html.Div(
        className="dvs-topbar",
        children=[
            # ── 左侧：页面标题 + 系统状态面板 ──
            html.Div(
                className="dvs-topbar__left",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "16px",
                    "flex": "1",
                    "overflow": "hidden",
                },
                children=[
                    # 页面标题
                    html.Span(
                        id="topbar-page-title",
                        style={
                            "fontSize": "1rem",
                            "fontWeight": "600",
                            "color": "var(--text-primary)",
                            "whiteSpace": "nowrap",
                        },
                    ),
                    # 分隔线
                    html.Div(style={"width": "1px", "height": "20px", "background": "var(--border)", "flexShrink": "0"}),
                    # 系统状态面板（OpenWrt 风格）
                    html.Div(
                        id="topbar-sysinfo",
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "10px",
                            "flexWrap": "nowrap",
                            "overflow": "hidden",
                        },
                        children=[],  # 由 callback 动态渲染
                    ),
                    # 数据集徽章区（动态更新）
                    html.Div(
                        id="topbar-status-badges",
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[],
                    ),
                ],
            ),

            # dcc.Interval 每1秒刷新系统状态
            dcc.Interval(id="sysinfo-interval", interval=1000, n_intervals=0),


            # ── 右侧：操作按钮区 ──
            html.Div(
                className="dvs-topbar__actions",
                children=[
                    dcc.Upload(
                        id="project-upload",
                        accept=".dvsp",
                        children=html.Button(
                            [html.I(className="bi bi-folder2-open"), html.Span("项目", className="ms-1 d-none d-md-inline")],
                            id="btn-open-project",
                            className="dvs-topbar__btn btn-hover",
                            title="打开项目",
                        ),
                    ),
                    html.Button(
                        [html.I(className="bi bi-save"), html.Span("保存", className="ms-1 d-none d-md-inline")],
                        id="btn-save-project",
                        className="dvs-topbar__btn btn-hover",
                        title="保存项目",
                    ),
                    html.Button(
                        html.I(className="bi bi-lightning"),
                        id="btn-quick-action",
                        className="dvs-topbar__btn btn-hover",
                        title="快捷操作",
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
                        title="帮助文档 (GitHub)",
                        style={"textDecoration": "none"},
                    ),
                ],
            ),


            # 关于弹窗
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("关于 DataViz Studio")),
                dbc.ModalBody([
                    html.P([html.Strong("版本: "), config.APP_VERSION]),
                    html.P([html.Strong("框架: "), "Dash + Plotly + Pandas"]),
                    html.P([html.Strong("许可: "), "MIT License"]),
                    html.Hr(),
                    html.P(config.APP_DESCRIPTION, style={"color": "var(--text-muted)"}),
                ]),
            ], id="settings-modal", is_open=False, centered=True),

            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("保存项目")),
                    dbc.ModalBody(
                        [
                            dbc.Label("项目名称"),
                            dbc.Input(id="project-name-input", value="dataviz-project", placeholder="输入项目名称"),
                            dbc.Label("数据保存方式", className="mt-3"),
                            dbc.RadioItems(
                                id="project-storage-mode",
                                options=[
                                    {"label": "内嵌数据", "value": "embedded"},
                                    {"label": "仅保存引用", "value": "reference"},
                                ],
                                value="embedded",
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("取消", id="btn-cancel-save-project", color="secondary", outline=True),
                            dbc.Button("保存", id="btn-confirm-save-project", color="primary"),
                        ]
                    ),
                ],
                id="save-project-modal",
                is_open=False,
                centered=True,
            ),

            # 快速操作 Offcanvas 右侧滑出面板
            dbc.Offcanvas(
                id="quick-action-offcanvas",
                title=html.Div([
                    html.Div(
                        style={
                            "width": "28px", "height": "28px", "borderRadius": "7px",
                            "background": "rgba(255, 107, 53, 0.12)", "display": "inline-flex",
                            "alignItems": "center", "justifyContent": "center", "marginRight": "8px",
                        },
                        children=[html.I(className="bi bi-lightning-fill", style={"color": "#FF6B35", "fontSize": "0.9rem"})],
                    ),
                    "快速操作",
                ]),
                is_open=False,
                placement="end",
                style={"width": "360px"},
                className="dvs-offcanvas-quick",
                children=[
                    html.P("快速导航到常用功能", style={"color": "#718096", "fontSize": "0.8rem", "marginBottom": "16px"}),

                    # 快速操作项目列表
                    html.A(
                        className="dvs-quick-action-item",
                        href="/data",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon",
                                     children=[html.I(className="bi bi-server")]),
                            html.Div([
                                html.Div("上传 / 加载数据", className="dvs-quick-action-item__label"),
                                html.Div("支持 CSV、Excel、JSON、Parquet", className="dvs-quick-action-item__sub"),
                            ]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/charts",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon",
                                     children=[html.I(className="bi bi-graph-up")]),
                            html.Div([
                                html.Div("创建图表", className="dvs-quick-action-item__label"),
                                html.Div("30+ 种可视化图表，智能推荐", className="dvs-quick-action-item__sub"),
                            ]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/workshop",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon",
                                     children=[html.I(className="bi bi-hammer")]),
                            html.Div([
                                html.Div("数据清洗", className="dvs-quick-action-item__label"),
                                html.Div("拖拽式操作，支持撤销/重做", className="dvs-quick-action-item__sub"),
                            ]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/stats",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon",
                                     children=[html.I(className="bi bi-calculator")]),
                            html.Div([
                                html.Div("统计分析", className="dvs-quick-action-item__label"),
                                html.Div("假设检验、相关分析、分组统计", className="dvs-quick-action-item__sub"),
                            ]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/profiling",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon",
                                     children=[html.I(className="bi bi-file-earmark-bar-graph")]),
                            html.Div([
                                html.Div("数据概况报告", className="dvs-quick-action-item__label"),
                                html.Div("自动数据质量评分与分布分析", className="dvs-quick-action-item__sub"),
                            ]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),
                    html.A(
                        className="dvs-quick-action-item",
                        href="/dashboard",
                        children=[
                            html.Div(className="dvs-quick-action-item__icon",
                                     children=[html.I(className="bi bi-speedometer2")]),
                            html.Div([
                                html.Div("仪表盘", className="dvs-quick-action-item__label"),
                                html.Div("数据集指标总览与质量评分", className="dvs-quick-action-item__sub"),
                            ]),
                            html.I(className="bi bi-chevron-right ms-auto", style={"color": "#CBD5E0"}),
                        ],
                    ),

                    # 底部提示
                    html.Hr(style={"margin": "16px 0", "borderColor": "#E8EDF2"}),
                    html.Div(
                        style={"textAlign": "center", "color": "#A0AEC0", "fontSize": "0.75rem"},
                        children=["DataViz Studio  v", config.APP_VERSION],
                    ),
                ],
            ),
            dcc.Download(id="project-download"),
        ],
    )
