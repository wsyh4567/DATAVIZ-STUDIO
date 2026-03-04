# -*- coding: utf-8 -*-
"""DataViz Studio — 顶部导航栏组件"""

from __future__ import annotations

from dash import html, dcc
import dash_bootstrap_components as dbc

import config


def create_navbar() -> html.Div:
    """返回顶部导航栏布局。"""
    return html.Div(
        className="dvs-topbar",
        children=[
            # ── Brand ──
            html.Div(
                className="dvs-topbar__brand",
                children=[
                    html.Span("🧪", className="dvs-topbar__brand-icon"),
                    html.Span("DataViz "),
                    html.Span("Studio", className="dvs-topbar__brand-accent"),
                ],
            ),
            # ── Actions ──
            html.Div(
                className="dvs-topbar__actions",
                children=[
                    html.Button(
                        "🌓", id="btn-theme-toggle",
                        className="dvs-topbar__btn btn-hover",
                        title="切换主题",
                    ),
                    html.Button(
                        "⚙️", id="btn-settings",
                        className="dvs-topbar__btn btn-hover",
                        title="关于",
                    ),
                    html.A(
                        "❓",
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
        ],
    )
