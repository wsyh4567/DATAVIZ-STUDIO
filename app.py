"""DataViz Studio — 应用入口

Dash SPA 应用：顶栏 + 侧边栏 + 路由 + 状态栏 + 全局状态。
"""

from __future__ import annotations

import dash
from dash import Dash, html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc

import config
from core.state_manager import get_initial_state
from core.data_manager import DataManager
from components.navbar import create_navbar
from components.sidebar import create_sidebar
from components.statusbar import create_statusbar
from utils.helpers import format_number

# ── 初始化 Dash 应用 ──────────────────────────────────

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title=config.APP_NAME,
    update_title=None,
    assets_folder=str(config.ASSETS_DIR),
)

server = app.server

# ── 主布局 ─────────────────────────────────────────────

app.layout = html.Div(
    id="app-root",
    className="dvs-app",
    **{"data-theme": "dark"},
    children=[
        # Global stores
        dcc.Store(id="app-store", data=get_initial_state(), storage_type="session"),
        dcc.Location(id="url", refresh=False),

        # Layout regions
        create_navbar(),
        create_sidebar(),
        html.Main(id="page-content", className="dvs-content"),
        create_statusbar(),

        # Toast container (for notifications)
        html.Div(id="toast-container", className="dvs-toast-container"),

        # Hidden div for theme toggle output
        html.Div(id="theme-dummy", style={"display": "none"}),
    ],
)


# ── 页面路由 ───────────────────────────────────────────

@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def route_page(pathname: str):
    """根据 URL 渲染对应页面。"""
    # Lazy imports to avoid circular deps
    from pages.welcome import create_welcome_page
    from pages.data_hub import create_data_hub_page
    from pages.data_canvas import create_data_canvas_page

    if pathname == "/canvas":
        return create_data_canvas_page()
    elif pathname == "/data":
        return create_data_hub_page()
    elif pathname in ("/workshop", "/charts", "/stats", "/dashboard", "/advanced"):
        # Placeholder pages for Phase 2+
        labels = {
            "/workshop": ("🧹", "数据工坊"),
            "/charts":   ("📈", "图表工作室"),
            "/stats":    ("🧮", "统计实验室"),
            "/dashboard":("📋", "仪表盘"),
            "/advanced": ("⚡", "高级工具"),
        }
        icon, name = labels[pathname]
        return html.Div(
            className="dvs-empty",
            style={"minHeight": "60vh"},
            children=[
                html.Div(icon, className="dvs-empty__icon"),
                html.Div(f"{name} — 即将推出", className="dvs-empty__text"),
                html.Div("该功能将在后续版本中实现", style={
                    "color": "var(--text-muted)", "fontSize": "var(--text-sm)"
                }),
            ],
        )
    else:
        # Default: welcome page
        return create_welcome_page()


# ── 侧边栏高亮 ────────────────────────────────────────

@callback(
    Output("sidebar", "children"),
    Input("url", "pathname"),
)
def update_sidebar_active(pathname: str):
    """根据当前路径高亮侧边栏。"""
    nav_items = []
    for item in config.NAV_ITEMS:
        active = pathname == item["href"]
        cls = "dvs-sidebar__item"
        if active:
            cls += " dvs-sidebar__item--active"

        nav_items.append(
            dcc.Link(
                className=cls,
                href=item["href"],
                children=[
                    html.Span(item["icon"], className="dvs-sidebar__icon"),
                    html.Span(item["label"], className="dvs-sidebar__label"),
                ],
            )
        )

    return [
        *nav_items,
        html.Div(
            id="sidebar-toggle",
            className="dvs-sidebar__toggle",
            children=[html.Span("◀", id="sidebar-toggle-icon")],
        ),
    ]


# ── 侧边栏折叠 ────────────────────────────────────────

@callback(
    Output("sidebar", "className"),
    Output("sidebar-toggle-icon", "children"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar", "className"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks, current_class):
    """切换侧边栏折叠状态。"""
    if n_clicks is None:
        return no_update, no_update
    collapsed = "dvs-sidebar--collapsed" in (current_class or "")
    if collapsed:
        return "dvs-sidebar", "◀"
    else:
        return "dvs-sidebar dvs-sidebar--collapsed", "▶"


# ── 主题切换 ───────────────────────────────────────────

app.clientside_callback(
    """
    function(n_clicks) {
        const root = document.getElementById('app-root');
        if (!root) return window.dash_clientside.no_update;
        const current = root.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next);
        return next;
    }
    """,
    Output("theme-dummy", "children"),
    Input("btn-theme-toggle", "n_clicks"),
    prevent_initial_call=True,
)


# ── 状态栏更新 ─────────────────────────────────────────

@callback(
    Output("statusbar-dataset", "children"),
    Output("statusbar-shape", "children"),
    Output("statusbar-memory", "children"),
    Input("app-store", "data"),
)
def update_statusbar(store_data):
    """更新状态栏数据集信息。"""
    dm = DataManager()
    meta = dm.get_meta()

    if meta is None:
        return "未加载数据", "—", "—"

    return (
        f"📊 {meta.name}",
        f"{format_number(meta.rows)} 行 × {meta.cols} 列",
        f"{meta.memory_mb:.1f} MB",
    )


# ── Toast 通知 ─────────────────────────────────────────

@callback(
    Output("toast-container", "children"),
    Input("app-store", "data"),
)
def show_toast(store_data):
    """显示 Toast 通知。"""
    if not store_data or not store_data.get("toast"):
        return []

    toast = store_data["toast"]
    toast_type = toast.get("type", "info")
    return html.Div(
        className=f"dvs-toast dvs-toast--{toast_type}",
        children=[
            html.Span(toast["message"], style={"fontSize": "var(--text-sm)"}),
        ],
    )


# ── 启动 ──────────────────────────────────────────────

if __name__ == "__main__":
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
