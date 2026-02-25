"""DataViz Studio — 顶部导航栏组件"""

from __future__ import annotations

from dash import html

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
                        "🔔", id="btn-notifications",
                        className="dvs-topbar__btn",
                        title="通知",
                    ),
                    html.Button(
                        "🌓", id="btn-theme-toggle",
                        className="dvs-topbar__btn",
                        title="切换主题",
                    ),
                    html.Button(
                        "⚙️", id="btn-settings",
                        className="dvs-topbar__btn",
                        title="设置",
                    ),
                    html.Button(
                        "❓", id="btn-help",
                        className="dvs-topbar__btn",
                        title="帮助",
                    ),
                ],
            ),
        ],
    )
