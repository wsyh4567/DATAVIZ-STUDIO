"""DataViz Studio — 数据画布页

AG Grid 高性能数据表格 + 数据概览卡片。
"""

from __future__ import annotations

from dash import html, Input, Output, callback, no_update

from core.data_manager import DataManager
from components.data_table import create_data_table
from utils.helpers import format_number


def create_data_canvas_page() -> html.Div:
    """返回数据画布页面布局。"""
    return html.Div(
        children=[
            html.H2("📊 数据画布", className="dvs-page-title"),

            # Overview stat cards row
            html.Div(id="canvas-stats-row", className="dvs-stats-row"),

            # AG Grid table
            html.Div(id="canvas-table-container"),
        ]
    )


# ── Callbacks ─────────────────────────────────────────

@callback(
    Output("canvas-stats-row", "children"),
    Output("canvas-table-container", "children"),
    Input("app-store", "data"),
)
def update_canvas(store_data):
    """当活跃数据集变化时更新表格和概览卡片。"""
    dm = DataManager()
    meta = dm.get_meta()
    df = dm.active_df

    if df is None or meta is None:
        # Empty state
        empty = html.Div(
            className="dvs-empty",
            children=[
                html.Div("📭", className="dvs-empty__icon"),
                html.Div("尚未加载数据", className="dvs-empty__text"),
                html.Div("前往欢迎页或数据中心加载数据集", style={"color": "var(--text-muted)", "fontSize": "var(--text-sm)"}),
            ],
        )
        return [], empty

    # ── Stats cards ──
    missing_total = int(df.isnull().sum().sum())
    missing_pct = (missing_total / (meta.rows * meta.cols) * 100) if meta.rows * meta.cols > 0 else 0
    dup_count = int(df.duplicated().sum())
    dup_pct = (dup_count / meta.rows * 100) if meta.rows > 0 else 0

    stats_cards = [
        _stat_card("总行数", format_number(meta.rows), "行记录"),
        _stat_card("总列数", str(meta.cols), "个字段"),
        _stat_card("缺失值", format_number(missing_total), f"({missing_pct:.1f}%)",
                   color="var(--warning)" if missing_total > 0 else None),
        _stat_card("重复行", format_number(dup_count), f"({dup_pct:.1f}%)",
                   color="var(--warning)" if dup_count > 0 else None),
        _stat_card("内存", f"{meta.memory_mb:.1f}", "MB"),
    ]

    # ── Table ──
    table = create_data_table(df)

    return stats_cards, table


def _stat_card(
    label: str,
    value: str,
    sub: str = "",
    color: str | None = None,
) -> html.Div:
    """创建单个概览统计卡片。"""
    value_style = {}
    if color:
        value_style["color"] = color
    return html.Div(
        className="dvs-stat-card",
        children=[
            html.Span(label, className="dvs-stat-card__label"),
            html.Span(value, className="dvs-stat-card__value", style=value_style),
            html.Span(sub, className="dvs-stat-card__sub"),
        ],
    )
