# -*- coding: utf-8 -*-
"""DataViz Studio — 数据画布页

AG Grid 高性能数据表格 + 数据概览卡片。
"""

from __future__ import annotations
import sys
import io

# 设置标准输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dash import html, dcc, Input, Output, State, callback, no_update

from core.data_manager import DataManager
from components.data_table import create_data_table
from utils.helpers import format_number


def validate_n_value(n_value):
    """验证N值输入是否为有效的正整数。
    
    Parameters
    ----------
    n_value : any
        用户输入的N值
        
    Returns
    -------
    tuple[bool, int | None, str | None]
        (是否有效, 验证后的值, 错误消息)
    """
    if n_value is None or n_value == "":
        return False, None, "请输入行数"
    
    try:
        n = int(n_value)
        if n <= 0:
            return False, None, "行数必须大于0"
        if n != float(n_value):  # Check if it was a decimal
            return False, None, "行数必须是整数"
        return True, n, None
    except (ValueError, TypeError):
        return False, None, "请输入有效的数字"


def create_data_canvas_page() -> html.Div:
    """返回数据画布页面布局。"""
    return html.Div(
        children=[
            html.H2("📊 数据画布", className="dvs-page-title"),

            # Overview stat cards row
            html.Div(id="canvas-stats-row", className="dvs-stats-row stagger-container"),

            # Data view selector (for large datasets)
            html.Div(
                className="dvs-preview-control",
                style={"marginBottom": "var(--sp-3)"},
                role="region",
                **{"aria-label": "数据预览控制"},
                children=[
                    html.Div(
                        className="dvs-preview-control__header",
                        children=[
                            html.Span("数据预览", className="dvs-section-header__title"),
                            html.Div(
                                className="dvs-preview-control__n-input",
                                children=[
                                    html.Label("显示行数：", htmlFor="preview-n-value", style={"marginRight": "var(--sp-2)", "color": "var(--text-secondary)"}),
                                    dcc.Input(
                                        id="preview-n-value",
                                        type="number",
                                        value=10,
                                        min=1,
                                        step=1,
                                        className="dvs-input dvs-input--sm",
                                        style={"width": "80px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="dvs-preview-control__buttons",
                        style={"display": "flex", "gap": "var(--sp-2)", "marginTop": "var(--sp-2)"},
                        role="group",
                        **{"aria-label": "数据预览模式选择"},
                        children=[
                            html.Button("前 N 行", id="btn-view-head", className="dvs-btn dvs-btn--sm dvs-btn--primary btn-hover", **{"aria-label": "显示前N行数据"}),
                            html.Button("中间 N 行", id="btn-view-middle", className="dvs-btn dvs-btn--sm btn-hover", **{"aria-label": "显示中间N行数据"}),
                            html.Button("后 N 行", id="btn-view-tail", className="dvs-btn dvs-btn--sm btn-hover", **{"aria-label": "显示后N行数据"}),
                            html.Button("全部数据", id="btn-view-all", className="dvs-btn dvs-btn--sm btn-hover", **{"aria-label": "显示全部数据"}),
                        ],
                    ),
                    html.Div(id="preview-warning", className="dvs-preview-control__warning", style={"marginTop": "var(--sp-2)"}, role="alert", **{"aria-live": "polite"}),
                ],
            ),

            # AG Grid table
            html.Div(id="canvas-table-container"),
        ]
    )


# ── Callbacks ─────────────────────────────────────────

@callback(
    Output("canvas-stats-row", "children"),
    Output("canvas-table-container", "children"),
    Output("preview-warning", "children"),
    Input("app-store", "data"),
    Input("btn-view-head", "n_clicks"),
    Input("btn-view-middle", "n_clicks"),
    Input("btn-view-tail", "n_clicks"),
    Input("btn-view-all", "n_clicks"),
    State("preview-n-value", "value"),
    State("canvas-table-container", "children"),
)
def update_canvas(store_data, n_head, n_middle, n_tail, n_all, n_value, current_table):
    """当活跃数据集变化或预览模式改变时更新表格和概览卡片。"""
    from dash import ctx
    
    warning_msg = None
    
    try:
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
            return [], empty, None
    except Exception as e:
        # Error state
        error = html.Div(
            className="dvs-empty",
            children=[
                html.Div("⚠️", className="dvs-empty__icon"),
                html.Div("数据加载出错", className="dvs-empty__text"),
                html.Div(f"错误信息：{str(e)}", style={"color": "var(--error)", "fontSize": "var(--text-sm)"}),
            ],
        )
        return [], error, None

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

    # ── Determine view mode ──
    view_mode = "head"  # default
    if ctx.triggered_id == "btn-view-middle":
        view_mode = "middle"
    elif ctx.triggered_id == "btn-view-tail":
        view_mode = "tail"
    elif ctx.triggered_id == "btn-view-all":
        view_mode = "all"
    elif ctx.triggered_id == "btn-view-head":
        view_mode = "head"
    
    # ── Validate N value (only for non-"all" modes) ──
    n = 10  # default
    if view_mode != "all":
        is_valid, validated_n, error_msg = validate_n_value(n_value)
        if not is_valid:
            warning_msg = html.Div(
                className="dvs-alert dvs-alert--warning",
                children=[
                    html.Span("⚠️ ", style={"marginRight": "var(--sp-2)"}),
                    html.Span(error_msg or "无效的行数输入"),
                ],
            )
            # Use default value of 10
            n = 10
        else:
            n = validated_n
            # Check if N exceeds total rows
            if n > meta.rows:
                warning_msg = html.Div(
                    className="dvs-alert dvs-alert--info",
                    children=[
                        html.Span("ℹ️ ", style={"marginRight": "var(--sp-2)"}),
                        html.Span(f"请求的行数 ({n:,}) 超过总行数 ({meta.rows:,})，将显示所有可用数据"),
                    ],
                )

    # ── Table ──
    table = create_data_table(df, view_mode=view_mode, n_rows=n)

    return stats_cards, table, warning_msg


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
        className="dvs-stat-card card-hover stagger-item",
        children=[
            html.Span(label, className="dvs-stat-card__label"),
            html.Span(value, className="dvs-stat-card__value", style=value_style),
            html.Span(sub, className="dvs-stat-card__sub"),
        ],
    )
