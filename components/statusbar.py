# -*- coding: utf-8 -*-
"""DataViz Studio — 底部状态栏组件"""

from __future__ import annotations

from dash import html


def create_statusbar() -> html.Div:
    """返回底部状态栏。"""
    return html.Div(
        className="dvs-statusbar",
        children=[
            html.Div(
                className="dvs-statusbar__section",
                children=[
                    html.Div(
                        className="dvs-statusbar__item",
                        children=[
                            html.Span(className="dvs-statusbar__dot"),
                            html.Span("就绪"),
                        ],
                    ),
                    html.Span(
                        id="statusbar-dataset",
                        children="未加载数据",
                    ),
                ],
            ),
            html.Div(
                className="dvs-statusbar__section",
                children=[
                    html.Span(id="statusbar-shape", children="—"),
                    html.Span(id="statusbar-memory", children="—"),
                    html.Span(f"v{__import__('config').APP_VERSION}"),
                ],
            ),
        ],
    )
