# -*- coding: utf-8 -*-
"""DataViz Studio — 应用入口

Dash SPA 应用：顶栏 + 侧边栏 + 路由 + 状态栏 + 全局状态。
"""

from __future__ import annotations
import os
import logging

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import dash
from dash import Dash, html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

import config
from core.state_manager import get_initial_state
from core.data_manager import DataManager
from components.navbar import create_navbar
from components.sidebar import create_sidebar
from components.statusbar import create_statusbar
from utils.helpers import format_number

# Import page modules to register their callbacks
import pages.home
import pages.data_hub
import pages.data_canvas
import pages.chart_studio
import pages.data_workshop
import pages.statistics_lab
import pages.advanced
import pages.ml_studio

# ── 初始化 Dash 应用 ──────────────────────────────────

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
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
    try:
        if pathname == "/canvas":
            return pages.data_canvas.create_data_canvas_page()
        elif pathname == "/data":
            return pages.data_hub.create_data_hub_page()
        elif pathname == "/charts":
            return pages.chart_studio.create_chart_studio_page()
        elif pathname == "/workshop":
            return pages.data_workshop.layout()
        elif pathname == "/stats":
            return pages.statistics_lab.layout()
        elif pathname == "/advanced":
            return pages.advanced.create_advanced_page()
        elif pathname == "/ml":
            return pages.ml_studio.create_ml_studio_page()
        elif pathname == "/home":
            return pages.home.create_home_page()
        else:
            # Default: home page
            return pages.home.create_home_page()
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        with open("debug_trace.txt", "w", encoding="utf-8") as f:
            f.write(err_msg)
        traceback.print_exc()
        return html.Div(
            className="dvs-empty",
            children=[
                html.Div("⚠️", className="dvs-empty__icon"),
                html.Div("页面加载出错", className="dvs-empty__text"),
                html.Div(f"错误：{str(e)}", style={"color": "var(--error)", "fontSize": "var(--text-sm)"}),
            ],
        )


# ── 侧边栏高亮 ────────────────────────────────────────

@callback(
    Output("sidebar", "children"),
    Input("url", "pathname"),
)
def update_sidebar_active(pathname: str):
    """根据当前路径高亮侧边栏。"""
    nav_items = []
    current_path = pathname
    if not current_path or current_path == "/":
        current_path = "/home"

    for item in config.NAV_ITEMS:
        active = current_path == item["href"]
        cls = "dvs-sidebar__item"
        if active:
            cls += " dvs-sidebar__item--active"

        nav_items.append(
            dcc.Link(
                className=cls,
                href=item["href"],
                children=[
                    html.I(className=f"{item['icon']} dvs-sidebar__icon"),
                    html.Span(item["label"], className="dvs-sidebar__label"),
                ],
            )
        )

    return [
        html.Div(
            className="dvs-topbar__brand",
            style={"padding": "0 16px", "marginBottom": "24px", "marginTop": "8px"},
            children=[
                html.I(className="bi bi-bar-chart-fill dvs-topbar__brand-icon"),
                html.Span("DataViz "),
                html.Span("Studio", className="dvs-topbar__brand-accent"),
            ],
        ),
        *nav_items,
        html.Div(
            id="sidebar-toggle",
            className="dvs-sidebar__toggle",
            children=[html.I(className="bi bi-chevron-bar-left", id="sidebar-toggle-icon")],
        ),
    ]


# ── 侧边栏折叠 ────────────────────────────────────────

# JS 已提取到 assets/js/sidebar-toggle.js
app.clientside_callback(
    dash.ClientsideFunction(namespace="sidebar", function_name="toggle"),
    Output("sidebar", "className"),
    Output("sidebar-toggle-icon", "className"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar", "className"),
)


# ── 主题切换 ───────────────────────────────────────────

# JS 已提取到 assets/js/theme-toggle.js
app.clientside_callback(
    dash.ClientsideFunction(namespace="theme", function_name="toggle"),
    Output("theme-dummy", "children"),
    Input("btn-theme-toggle", "n_clicks"),
    prevent_initial_call=True,
)


# ── 顶栏页面标题同步 ───────────────────────────────────────────

_PAGE_LABEL_MAP = {
    "/":          "欢迎",
    "/canvas":    "数据画布",
    "/data":      "数据中心",
    "/workshop":  "数据工坊",
    "/charts":    "图表工作室",
    "/stats":     "统计实验室",
    "/profiling": "数据概况",
    "/dashboard": "仪表盘",
    "/advanced":  "高级工具",
    "/ml":        "机器学习",
}

@callback(
    Output("topbar-page-title", "children"),
    Input("url", "pathname"),
)
def update_page_title(pathname: str):
    """同步顶栏页面标题为静态文字。"""
    return "系统状态"


@callback(
    Output("topbar-status-badges", "children"),
    Input("url", "pathname"),
    Input("app-store", "data"),
)
def update_topbar_badges(pathname, store_data):
    """在页面标题右侧显示平台状态数据集徽章。"""
    dm = DataManager()
    meta = dm.get_meta()
    if meta is None:
        return []
    return [
        html.Span(
            style={
                "display": "inline-flex", "alignItems": "center", "gap": "4px",
                "background": "rgba(56,161,105,0.10)", "color": "#38A169",
                "borderRadius": "6px", "padding": "2px 8px",
                "fontSize": "0.75rem", "fontWeight": "600",
            },
            children=[
                html.I(className="bi bi-check-circle-fill", style={"fontSize": "0.7rem"}),
                f" 当前数据集: {meta.name}",
            ]
        ),
        html.Span(
            style={
                "display": "inline-flex", "alignItems": "center",
                "background": "rgba(49,130,206,0.08)", "color": "#3182CE",
                "borderRadius": "6px", "padding": "2px 8px",
                "fontSize": "0.75rem", "fontWeight": "600",
            },
            children=f"{meta.rows:,} 行 \u00d7 {meta.cols} 列",
        ),
    ]


def _sysinfo_bar(label: str, icon: str, pct: float, color: str) -> html.Div:
    """渲染单个系统指标：进度条 + 图标 + 数字（OpenWrt 风格）"""
    # 根据使用率调整颜色
    if pct >= 90:
        bar_color = "#E53E3E"  # 红 - 危险
    elif pct >= 70:
        bar_color = "#DD6B20"  # 橙 - 警告
    else:
        bar_color = color
    return html.Div(
        style={
            "display": "flex", "flexDirection": "column", "gap": "2px",
            "minWidth": "80px", "maxWidth": "110px",
        },
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                children=[
                    html.Span(
                        [html.I(className=f"bi {icon}", style={"marginRight": "3px"}), label],
                        style={"fontSize": "0.68rem", "color": "var(--text-secondary, #718096)", "fontWeight": "600"}
                    ),
                    html.Span(
                        f"{pct:.0f}%",
                        style={"fontSize": "0.72rem", "fontWeight": "700", "color": bar_color}
                    ),
                ]
            ),
            # 进度条背景
            html.Div(
                style={
                    "width": "100%", "height": "4px",
                    "borderRadius": "2px",
                    "background": "rgba(0,0,0,0.08)",
                    "overflow": "hidden",
                },
                children=[
                    html.Div(style={
                        "width": f"{min(pct, 100):.1f}%",
                        "height": "100%",
                        "background": bar_color,
                        "transition": "width 0.4s ease",
                        "borderRadius": "2px",
                    })
                ]
            ),
        ]
    )


@callback(
    Output("topbar-sysinfo", "children"),
    Input("sysinfo-interval", "n_intervals"),
)
def update_topbar_sysinfo(n):
    """每 5 秒刷新系统状态（CPU / 内存 / 磁盘）。"""
    if not _HAS_PSUTIL:
        return [html.Span("psutil 未安装", style={"fontSize": "0.7rem", "color": "#718096"})]
    try:
        p = psutil.Process(os.getpid())
        # 获取自上次调用以来的进程CPU使用率
        app_cpu = p.cpu_percent(interval=None)
        
        # 判定执行状态 (> 2.0 视为计算中)
        is_executing = app_cpu > 2.0
        if is_executing:
            status_color = "#DD6B20"
            status_text = "Python 执行中"
            status_icon = "bi bi-gear-wide-connected"
            pulse_class = "spin-slow" # 假设有一点旋转效果，退而求其次用静态
        else:
            status_color = "#38A169"
            status_text = "Python 空闲中"
            status_icon = "bi bi-check-circle-fill"
            pulse_class = ""

        status_badge = html.Div(
            [html.I(className=f"{status_icon} {pulse_class}", style={"color": status_color, "fontSize": "10px", "marginRight": "6px"}), status_text],
            style={
                "fontSize": "0.72rem",
                "fontWeight": "600",
                "color": status_color,
                "display": "flex",
                "alignItems": "center",
                "background": f"rgba({int(status_color[1:3], 16)}, {int(status_color[3:5], 16)}, {int(status_color[5:7], 16)}, 0.1)",
                "padding": "4px 12px",
                "borderRadius": "16px",
                "marginRight": "8px",
                "border": f"1px solid rgba({int(status_color[1:3], 16)}, {int(status_color[3:5], 16)}, {int(status_color[5:7], 16)}, 0.3)"
            }
        )

        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        
        from datetime import datetime
        import time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 计算已运行时间
        uptime_seconds = int(time.time() - p.create_time())
        hours, rem = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        if hours > 0:
            uptime_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            uptime_str = f"{minutes}m {seconds}s"
        else:
            uptime_str = f"{seconds}s"

        return [
            status_badge,
            html.Div(
                [
                    html.I(className="bi bi-clock", style={"marginRight": "6px"}), 
                    html.Span(current_time, style={"marginRight": "12px"}),
                    html.I(className="bi bi-hourglass-split", style={"marginRight": "4px", "color": "var(--primary)"}),
                    html.Span(f"已运行: {uptime_str}", style={"color": "var(--primary)"})
                ],
                style={
                    "fontSize": "0.72rem",
                    "fontWeight": "600",
                    "color": "var(--text-secondary)",
                    "display": "flex",
                    "alignItems": "center",
                    "background": "rgba(0,0,0,0.04)",
                    "padding": "4px 12px",
                    "borderRadius": "16px",
                    "marginRight": "12px",
                }
            ),
            _sysinfo_bar("CPU", "bi-cpu", cpu, "#FF6B35"),
            _sysinfo_bar("内存", "bi-memory", mem, "#3182CE"),
            _sysinfo_bar("磁盘", "bi-hdd", disk, "#805AD5"),
        ]
    except Exception:
        return []


# ── 快速操作 Offcanvas ───────────────────────────────────────────

@callback(
    Output("quick-action-offcanvas", "is_open"),
    Input("btn-quick-action", "n_clicks"),
    State("quick-action-offcanvas", "is_open"),
    prevent_initial_call=True,
)
def toggle_quick_action(n_clicks, is_open):
    """切换快速操作面板。"""
    return not is_open


# ── 关于弹窗 ───────────────────────────────────────────

@callback(
    Output("settings-modal", "is_open"),
    Input("btn-settings", "n_clicks"),
    State("settings-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_settings_modal(n_clicks, is_open):
    """切换关于弹窗。"""
    return not is_open


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
    # 映射图标类型
    icon_type = "danger" if toast_type == "error" else toast_type
    if icon_type not in ["primary", "secondary", "success", "warning", "danger", "info"]:
        icon_type = "info"

    return dbc.Toast(
        [html.Span(toast["message"], style={"fontSize": "var(--text-sm)"})],
        id="global-toast",
        header="消息提示",
        is_open=True,
        dismissable=True,
        icon=icon_type,
        duration=4000,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
    )


# ── 启动 ──────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
