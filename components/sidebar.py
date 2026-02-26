# -*- coding: utf-8 -*-
"""DataViz Studio — 左侧侧边栏组件"""

from __future__ import annotations

from dash import html, dcc

import config


def create_sidebar() -> html.Div:
    """返回左侧导航侧边栏。"""
    nav_items = []
    for item in config.NAV_ITEMS:
        nav_items.append(
            dcc.Link(
                className="dvs-sidebar__item",
                href=item["href"],
                children=[
                    html.Span(item["icon"], className="dvs-sidebar__icon"),
                    html.Span(item["label"], className="dvs-sidebar__label"),
                ],
            )
        )

    return html.Div(
        id="sidebar",
        className="dvs-sidebar",
        children=[
            *nav_items,
            # Toggle button at bottom
            html.Div(
                id="sidebar-toggle",
                className="dvs-sidebar__toggle",
                children=[html.Span("◀", id="sidebar-toggle-icon")],
            ),
        ],
    )
