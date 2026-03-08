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
                    html.I(className=f"{item['icon']} dvs-sidebar__icon"),
                    html.Span(item["label"], className="dvs-sidebar__label"),
                ],
            )
        )

    return html.Div(
        id="sidebar",
        className="dvs-sidebar",
        children=[
            # ── Brand ──
            html.Div(
                className="dvs-topbar__brand",
                style={"padding": "0 16px", "marginBottom": "24px", "marginTop": "8px"},
                children=[
                    html.I(className="bi bi-bar-chart-fill dvs-topbar__brand-icon"),
                    html.Span("DataViz "),
                    html.Span("Studio", className="dvs-topbar__brand-accent"),
                ],
            ),
            # Navigation Items
            *nav_items,
            # Toggle button at bottom
            html.Div(
                id="sidebar-toggle",
                className="dvs-sidebar__toggle",
                children=[html.I(className="bi bi-chevron-bar-left", id="sidebar-toggle-icon")],
            ),
        ],
    )
