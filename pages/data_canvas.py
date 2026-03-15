# -*- coding: utf-8 -*-
"""Data Canvas page with enhanced EDA workflow."""

from __future__ import annotations

import io
from typing import Any, Dict, Iterable, List, Optional

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, ctx, dcc, html, no_update

from components.data_table import create_data_table
from core.data_manager import DataManager
from services.eda_service import EDAService
from services.report_generator import ReportGenerator
from utils.helpers import format_number


KPI_CONFIG = [
    {"label": "总行数", "icon": "bi-table", "color": "#3182CE"},
    {"label": "总列数", "icon": "bi-layout-three-columns", "color": "#7C3AED"},
    {"label": "缺失值", "icon": "bi-exclamation-circle", "color": "#DD6B20"},
    {"label": "重复行", "icon": "bi-files", "color": "#E53E3E"},
    {"label": "内存占用", "icon": "bi-cpu", "color": "#4A5568"},
    {"label": "数据健康度", "icon": "bi-shield-check", "color": "#38A169"},
]


def validate_n_value(n_value: Any) -> tuple[bool, Optional[int], Optional[str]]:
    if n_value is None or n_value == "":
        return False, None, "请输入有效的行数。"
    try:
        n = int(n_value)
    except (TypeError, ValueError):
        return False, None, "请输入有效的数字。"
    if n <= 0:
        return False, None, "行数必须大于 0。"
    return True, n, None


def _hex_to_rgba(hex_color: str) -> str:
    color = hex_color.lstrip("#")
    return f"{int(color[0:2], 16)},{int(color[2:4], 16)},{int(color[4:6], 16)}"


def _dataset_key(name: Optional[str], df: Optional[pd.DataFrame]) -> str:
    if df is None:
        return "empty"
    return f"{name or 'dataset'}::{len(df)}::{len(df.columns)}"


def _resolve_preview(df: pd.DataFrame, n_value: Any) -> tuple[str, int, Optional[html.Div]]:
    view_mode = "head"
    if ctx.triggered_id == "btn-view-middle":
        view_mode = "middle"
    elif ctx.triggered_id == "btn-view-tail":
        view_mode = "tail"
    elif ctx.triggered_id == "btn-view-all":
        view_mode = "all"

    if view_mode == "all":
        return view_mode, min(len(df), 10_000), None

    valid, n_rows, error = validate_n_value(n_value)
    if not valid:
        warning = html.Div(
            className="dvs-alert dvs-alert--warning",
            children=[
                html.Span("请输入有效的预览行数。" if error is None else error),
            ],
        )
        return view_mode, 10, warning

    if n_rows > len(df):
        warning = html.Div(
            className="dvs-alert dvs-alert--info",
            children=[html.Span(f"请求的行数超过总行数，将显示全部可用数据。")],
        )
        return view_mode, len(df), warning

    return view_mode, n_rows, None


def create_data_canvas_page() -> html.Div:
    return html.Div(
        children=[
            dcc.Store(id="eda-analysis-mode", data="full"),
            dcc.Store(id="eda-sample-size", data=None),
            dcc.Store(id="eda-user-sampling-choice", data=None),
            dcc.Store(id="eda-last-analysis-meta", data=None),
            html.H2("数据画布", className="dvs-page-title"),
            html.Div(id="canvas-stats-row", className="dvs-stats-row stagger-container"),
            html.Div(
                className="dvs-preview-control",
                style={"marginBottom": "var(--sp-3)"},
                children=[
                    html.Div(
                        className="dvs-preview-control__header",
                        children=[
                            html.Span("数据预览", className="dvs-section-header__title"),
                            html.Div(
                                className="dvs-preview-control__n-input",
                                children=[
                                    html.Label("显示行数", htmlFor="preview-n-value", style={"marginRight": "var(--sp-2)", "color": "var(--text-secondary)"}),
                                    dcc.Input(
                                        id="preview-n-value",
                                        type="number",
                                        value=10,
                                        min=1,
                                        step=1,
                                        className="dvs-input dvs-input--sm",
                                        style={"width": "88px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="dvs-preview-control__buttons",
                        children=[
                            html.Button("前 N 行", id="btn-view-head", className="dvs-btn dvs-btn--sm dvs-btn--primary btn-hover"),
                            html.Button("中间 N 行", id="btn-view-middle", className="dvs-btn dvs-btn--sm btn-hover"),
                            html.Button("后 N 行", id="btn-view-tail", className="dvs-btn dvs-btn--sm btn-hover"),
                            html.Button("全部数据", id="btn-view-all", className="dvs-btn dvs-btn--sm btn-hover"),
                        ],
                    ),
                    html.Div(id="preview-warning", className="dvs-preview-control__warning"),
                ],
            ),
            html.Div(id="canvas-table-container"),
            html.Div(
                className="dvs-preview-control",
                style={"marginTop": "var(--sp-3)", "display": "flex", "gap": "var(--sp-2)", "alignItems": "center"},
                children=[
                    html.Span("导出数据", style={"color": "var(--text-secondary)", "marginRight": "var(--sp-2)"}),
                    html.Button("CSV", id="btn-export-csv", className="dvs-btn dvs-btn--sm btn-hover"),
                    html.Button("Excel", id="btn-export-excel", className="dvs-btn dvs-btn--sm btn-hover"),
                    html.Button("JSON", id="btn-export-json", className="dvs-btn dvs-btn--sm btn-hover"),
                    html.Span("•", style={"color": "var(--border)", "margin": "0 var(--sp-2)"}),
                    html.Button("导出分析报告", id="btn-export-report", className="dvs-btn dvs-btn--sm dvs-btn--primary btn-hover"),
                ],
            ),
            dcc.Download(id="download-data-file"),
            dcc.Download(id="download-report-file"),
            dbc.Modal(
                id="eda-sampling-modal",
                is_open=False,
                centered=True,
                className="eda-sampling-modal",
                children=[
                    dbc.ModalHeader(dbc.ModalTitle("选择 EDA 分析模式"), close_button=False),
                    dbc.ModalBody(id="eda-sampling-modal-body"),
                    dbc.ModalFooter(
                        children=[
                            html.Button("本次取消", id="btn-eda-cancel", className="dvs-btn dvs-btn--sm"),
                            html.Button("全量分析", id="btn-eda-use-full", className="dvs-btn dvs-btn--sm"),
                            html.Button("推荐采样", id="btn-eda-use-sample", className="dvs-btn dvs-btn--sm dvs-btn--primary"),
                        ],
                    ),
                ],
            ),
            html.Div(id="canvas-insight-section"),
        ]
    )


@callback(
    Output("canvas-stats-row", "children"),
    Output("canvas-table-container", "children"),
    Output("preview-warning", "children"),
    Output("canvas-insight-section", "children"),
    Output("eda-sampling-modal", "is_open"),
    Output("eda-sampling-modal-body", "children"),
    Output("eda-analysis-mode", "data"),
    Output("eda-sample-size", "data"),
    Output("eda-user-sampling-choice", "data"),
    Output("eda-last-analysis-meta", "data"),
    Input("app-store", "data"),
    Input("btn-view-head", "n_clicks"),
    Input("btn-view-middle", "n_clicks"),
    Input("btn-view-tail", "n_clicks"),
    Input("btn-view-all", "n_clicks"),
    Input("btn-eda-use-sample", "n_clicks"),
    Input("btn-eda-use-full", "n_clicks"),
    Input("btn-eda-cancel", "n_clicks"),
    State("preview-n-value", "value"),
    State("eda-analysis-mode", "data"),
    State("eda-sample-size", "data"),
    State("eda-user-sampling-choice", "data"),
    State("eda-last-analysis-meta", "data"),
)
def update_canvas(
    store_data: Optional[dict],
    n_head: Optional[int],
    n_middle: Optional[int],
    n_tail: Optional[int],
    n_all: Optional[int],
    n_sample: Optional[int],
    n_full: Optional[int],
    n_cancel: Optional[int],
    n_value: Any,
    current_mode: Optional[str],
    current_sample_size: Optional[int],
    sampling_choice: Optional[dict],
    last_analysis_meta: Optional[dict],
):
    dm = DataManager()
    df = dm.active_df
    meta = dm.get_meta()
    name = dm.active_name or "data"

    if df is None or meta is None:
        empty = _empty_state("尚未加载数据", "前往数据中心或主页加载数据集。")
        return [], empty, None, [], False, no_update, current_mode, current_sample_size, sampling_choice, last_analysis_meta

    view_mode, n_rows, preview_warning = _resolve_preview(df, n_value)
    table = create_data_table(df, view_mode=view_mode, n_rows=n_rows)
    dataset_key = _dataset_key(name, df)
    recommended_size = EDAService.recommended_sample_size(len(df))
    should_prompt = EDAService.should_recommend_sampling(meta.rows, meta.memory_mb)

    decision = None
    if isinstance(sampling_choice, dict) and sampling_choice.get("dataset_key") == dataset_key:
        decision = sampling_choice.get("decision")

    trigger = ctx.triggered_id
    modal_body = _build_sampling_modal_body(meta.rows, meta.memory_mb, recommended_size)
    modal_open = False

    if trigger == "btn-eda-use-sample":
        decision = "sample"
    elif trigger == "btn-eda-use-full":
        decision = "full"
    elif trigger == "btn-eda-cancel":
        decision = "cancel"

    if should_prompt and decision is None:
        stats_cards = _build_stats_cards(meta, df)
        pending_section = _sampling_pending_section(meta.rows, meta.memory_mb, recommended_size)
        return (
            stats_cards,
            table,
            preview_warning,
            pending_section,
            True,
            modal_body,
            current_mode or "full",
            recommended_size,
            {"dataset_key": dataset_key, "decision": None},
            last_analysis_meta,
        )

    if should_prompt and decision == "cancel":
        stats_cards = _build_stats_cards(meta, df)
        cancelled_section = _sampling_cancelled_section()
        return (
            stats_cards,
            table,
            preview_warning,
            cancelled_section,
            False,
            modal_body,
            current_mode or "full",
            recommended_size,
            {"dataset_key": dataset_key, "decision": "cancel"},
            last_analysis_meta,
        )

    analysis_mode = "sample" if should_prompt and decision == "sample" else "full"
    sample_size = recommended_size if analysis_mode == "sample" else None
    report = EDAService.analyze_dataset(df, mode=analysis_mode, sample_size=sample_size)
    stats_cards = _build_stats_cards(meta, df, report)
    insight_section = _build_insight_section(df, report)
    new_last_meta = {**report["sample_meta"], "dataset_key": dataset_key}

    return (
        stats_cards,
        table,
        preview_warning,
        insight_section,
        False,
        modal_body,
        report["sample_meta"]["mode"],
        recommended_size,
        {"dataset_key": dataset_key, "decision": analysis_mode},
        new_last_meta,
    )


def _build_stats_cards(meta: Any, df: pd.DataFrame, report: Optional[Dict[str, Any]] = None) -> List[html.Div]:
    missing_total = int(df.isna().sum().sum())
    duplicate_count = int(df.duplicated().sum())
    if report is None:
        missing_pct = missing_total / max(meta.rows * meta.cols, 1) * 100
        duplicate_pct = duplicate_count / max(meta.rows, 1) * 100
        quality_score = max(0, 100 - int(missing_pct * 0.6) - min(20, int(duplicate_pct * 0.4)))
    else:
        missing_pct = report["overview"]["missing_pct"]
        duplicate_pct = report["overview"]["duplicate_pct"]
        quality_score = report["overview"]["quality_score"]
    quality_color = "#38A169" if quality_score >= 80 else "#DD6B20" if quality_score >= 60 else "#E53E3E"

    values = [
        ("总行数", format_number(meta.rows), f"{meta.rows:,} 条记录", "bi-table", "#3182CE"),
        ("总列数", str(meta.cols), f"{meta.cols} 个字段", "bi-layout-three-columns", "#7C3AED"),
        ("缺失值", format_number(missing_total), f"占比 {missing_pct:.1f}%", "bi-exclamation-circle", "#DD6B20" if missing_total else "#38A169"),
        ("重复行", format_number(duplicate_count), f"占比 {duplicate_pct:.1f}%", "bi-files", "#E53E3E" if duplicate_count else "#38A169"),
        ("内存占用", f"{meta.memory_mb:.1f} MB", "当前数据集", "bi-cpu", "#4A5568"),
        ("数据健康度", f"{quality_score:.1f}", "综合质量评分", "bi-shield-check", quality_color),
    ]
    return [_icon_stat_card(*item) for item in values]


def _icon_stat_card(label: str, value: str, sub: str, icon: str, color: str) -> html.Div:
    return html.Div(
        className="dvs-stat-card card-hover stagger-item",
        style={"borderLeft": f"3px solid {color}", "position": "relative", "overflow": "hidden"},
        children=[
            html.Div(
                style={
                    "position": "absolute",
                    "right": "-8px",
                    "top": "-8px",
                    "width": "60px",
                    "height": "60px",
                    "borderRadius": "50%",
                    "background": f"radial-gradient(circle, rgba({_hex_to_rgba(color)}, 0.12) 0%, transparent 70%)",
                    "pointerEvents": "none",
                }
            ),
            html.Div(
                html.I(className=f"bi {icon}", style={"fontSize": "1.1rem", "color": color}),
                style={
                    "width": "34px",
                    "height": "34px",
                    "borderRadius": "8px",
                    "background": f"rgba({_hex_to_rgba(color)}, 0.12)",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginBottom": "8px",
                },
            ),
            html.Span(label, className="dvs-stat-card__label"),
            html.Span(value, className="dvs-stat-card__value", style={"color": color}),
            html.Span(sub, className="dvs-stat-card__sub"),
        ],
    )


def _build_sampling_modal_body(rows: int, memory_mb: float, sample_size: int) -> html.Div:
    return html.Div(
        className="eda-sampling-copy",
        children=[
            html.P(
                f"当前数据集约 {rows:,} 行，内存占用 {memory_mb:.1f} MB。为了保证响应速度，EDA 默认建议使用采样。",
                className="mb-2",
            ),
            html.P(
                f"推荐样本量为 {sample_size:,} 行。你也可以选择全量分析，但大数据集下图表和统计计算会更慢。",
                className="mb-0 text-muted",
            ),
        ],
    )


def _empty_state(title: str, subtitle: str) -> html.Div:
    return html.Div(
        className="dvs-empty",
        children=[
            html.Div("📭", className="dvs-empty__icon"),
            html.Div(title, className="dvs-empty__text"),
            html.Div(subtitle, style={"color": "var(--text-muted)", "fontSize": "var(--text-sm)"}),
        ],
    )


def _sampling_pending_section(rows: int, memory_mb: float, sample_size: int) -> List[html.Div]:
    return [
        _section_header("自动洞察", "请先确认分析模式，再执行 EDA 计算。", icon="bi-stars"),
        html.Div(
            className="eda-empty-card",
            children=[
                html.Div("建议先选择采样或全量分析", className="eda-empty-card__title"),
                html.Div(
                    f"当前数据集 {rows:,} 行，{memory_mb:.1f} MB。推荐样本量 {sample_size:,} 行。",
                    className="eda-empty-card__text",
                ),
            ],
        ),
    ]


def _sampling_cancelled_section() -> List[html.Div]:
    return [
        _section_header("自动洞察", "本次已取消分析。", icon="bi-stars"),
        html.Div(
            className="eda-empty-card",
            children=[
                html.Div("EDA 尚未执行", className="eda-empty-card__title"),
                html.Div("你可以重新选择采样或全量分析后继续。", className="eda-empty-card__text"),
            ],
        ),
    ]


def _build_insight_section(df: pd.DataFrame, report: Dict[str, Any]) -> List[html.Div]:
    return [
        html.Hr(style={"borderColor": "var(--border)", "margin": "24px 0 20px 0"}),
        _build_business_intro_section(report),
        _build_readiness_section(report),
        _build_comparison_section(report),
        _build_relationship_section(report),
        _build_distribution_story_section(df, report),
        _build_field_guide_section(report),
        _build_next_steps_section(report),
        html.Div(style={"height": "32px"}),
    ]


def _build_business_intro_section(report: Dict[str, Any]) -> html.Div:
    overview = report["overview"]
    sample_meta = report["sample_meta"]
    use_cases = _derive_business_use_cases(report)
    return html.Div(
        className="eda-section-card",
        children=[
            _section_header(
                "这份数据可以帮你做什么",
                "直接告诉你可以做哪些业务分析，不需要先理解统计术语。",
                icon="bi-stars",
            ),
            html.Div(
                className="eda-summary-banner",
                children=[
                    html.Div(
                        className="eda-summary-banner__main",
                        children=[
                            html.Div(
                                "可直接开始分析" if overview["quality_score"] >= 80 else "建议先清理后再分析",
                                className="eda-summary-banner__title",
                            ),
                            html.Div(
                                f"当前共有 {overview['rows']:,} 行、{overview['cols']} 个字段。"
                                f"{' 使用了样本预览，适合先看方向。' if sample_meta['used_sampling'] else ' 当前是全量分析，更适合直接下判断。'}",
                                className="eda-summary-banner__text",
                            ),
                        ],
                    ),
                    html.Div(
                        className="eda-summary-banner__meta",
                        children=[
                            _summary_kv("当前模式", "推荐采样" if sample_meta["used_sampling"] else "全量分析"),
                            _summary_kv("样本量", f"{sample_meta['sample_rows']:,} 行"),
                            _summary_kv("数据健康度", f"{overview['quality_score']:.1f}/100"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="eda-usecase-grid",
                children=[_use_case_card(item) for item in use_cases],
            ),
        ],
    )


def _build_readiness_section(report: Dict[str, Any]) -> html.Div:
    overview = report["overview"]
    alerts = report["quality_alerts"]
    readiness_cards = [
        ("缺失值", f"{overview['missing_pct']:.2f}%", "看看是否有空白数据会影响统计口径。"),
        ("重复记录", f"{overview['duplicate_pct']:.2f}%", "避免同一单据、同一用户被重复计算。"),
        ("当前可用程度", "较高" if overview["quality_score"] >= 80 else "一般", "先判断能否直接给业务结论。"),
    ]
    return html.Div(
        className="eda-section-card",
        children=[
            _section_header("现在能不能直接拿来分析", "先看数据是否干净、是否容易误判。", icon="bi-shield-check"),
            html.Div(
                className="eda-readiness-grid",
                children=[
                    html.Div(
                        className="eda-subsection-card",
                        children=[
                            html.Div("先看这 3 件事", className="eda-subsection-title"),
                            html.Div(
                                className="eda-readiness-cards",
                                children=[
                                    html.Div(
                                        className="eda-readiness-card",
                                        children=[
                                            html.Div(label, className="eda-readiness-card__label"),
                                            html.Div(value, className="eda-readiness-card__value"),
                                            html.Div(desc, className="eda-readiness-card__text"),
                                        ],
                                    )
                                    for label, value, desc in readiness_cards
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="eda-subsection-card",
                        children=[
                            html.Div("建议先处理的问题", className="eda-subsection-title"),
                            html.Div(
                                className="eda-alert-grid",
                                children=[_alert_card(item) for item in alerts[:6]]
                                or [html.Div("目前没有明显问题，可以直接开始分析。", className="eda-empty-card__text")],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def _build_comparison_section(report: Dict[str, Any]) -> html.Div:
    relationships = report["relationship_findings"]
    comparison_items = [
        f"{item['category']} 可以拿来比较 {item['numeric']}，当前差距最明显。"
        for item in relationships["categorical_numeric_pairs"][:5]
    ]
    if not comparison_items:
        comparison_items = ["当前数据里还没有明显的分组差异，可优先查看分类字段是否足够。"]
    return html.Div(
        className="eda-section-card",
        children=[
            _section_header("适合做什么业务比较", "比如比较不同客户、门店、产品、区域谁表现更好。", icon="bi-people"),
            html.Div(
                className="eda-story-grid",
                children=[
                    html.Div(
                        className="eda-subsection-card",
                        children=[
                            html.Div("你现在可以直接做这些比较", className="eda-subsection-title"),
                            _relationship_list("优先推荐的比较方向", comparison_items),
                        ],
                    ),
                    html.Div(
                        className="eda-subsection-card",
                        children=[
                            html.Div("这类分析常见在这些场景", className="eda-subsection-title"),
                            html.Ul(
                                [
                                    html.Li("比较不同产品线、品牌、门店或区域的销售表现。"),
                                    html.Li("比较不同客户类型、渠道或活动带来的结果差异。"),
                                    html.Li("找出哪一类人群、商品或服务表现最好或最差。"),
                                ],
                                className="eda-relationship-list",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def _build_relationship_section(report: Dict[str, Any]) -> html.Div:
    relationships = report["relationship_findings"]
    relationship_items = [
        f"{item['var1']} 和 {item['var2']} 经常一起变化，可联动看。"
        for item in relationships["numeric_pairs"][:6]
    ]
    if not relationship_items:
        relationship_items = ["当前数值指标较少，暂时无法判断哪些指标会一起变化。"]
    return html.Div(
        className="eda-section-card",
        children=[
            _section_header("哪些指标通常会一起变化", "适合用来找联动关系、主次指标和关键驱动因素。", icon="bi-diagram-3"),
            html.Div(
                className="eda-story-grid",
                children=[
                    html.Div(
                        className="eda-chart-card",
                        children=[
                            html.Div("可联动查看的指标", className="eda-subsection-title"),
                            _relationship_list("优先关注", relationship_items),
                            html.Div(
                                "可用于看成交额和利润是否同步、曝光和转化是否同步、客单价和复购是否同步。",
                                className="eda-empty-card__text",
                            ),
                        ],
                    ),
                    html.Div(
                        className="eda-chart-card",
                        children=[dcc.Graph(figure=EDAService.create_correlation_heatmap(report), config={"displayModeBar": False})],
                    ),
                ],
            ),
        ],
    )


def _build_distribution_story_section(df: pd.DataFrame, report: Dict[str, Any]) -> html.Div:
    category_cards: List[html.Div] = []
    numeric_cards: List[html.Div] = []
    for item in report["quick_distributions"]["categorical"]:
        category_cards.append(
            html.Div(
                className="eda-chart-card",
                children=[
                    html.Div(f"{item['name']} 的构成", className="eda-subsection-title"),
                    dcc.Graph(figure=EDAService.create_categorical_distribution(df[item["name"]]), config={"displayModeBar": False}),
                ],
            )
        )
    for item in report["quick_distributions"]["numeric"]:
        numeric_cards.append(
            html.Div(
                className="eda-chart-card",
                children=[
                    html.Div(f"{item['name']} 的范围", className="eda-subsection-title"),
                    dcc.Graph(figure=EDAService.create_numeric_distribution(df[item["name"]]), config={"displayModeBar": False}),
                ],
            )
        )

    return html.Div(
        className="eda-section-card",
        children=[
            _section_header("可以看结构，也可以看波动", "一边看分类占比，一边看关键指标分布。", icon="bi-bar-chart-line"),
            html.Div(
                className="eda-story-grid",
                children=[
                    html.Div(
                        className="eda-subsection-card",
                        children=[
                            html.Div("看看分类构成", className="eda-subsection-title"),
                            html.Div(
                                className="eda-chart-grid",
                                children=category_cards or [html.Div("当前没有适合直接看构成的分类字段。", className="eda-empty-card__text")],
                            ),
                        ],
                    ),
                    html.Div(
                        className="eda-subsection-card",
                        children=[
                            html.Div("看看数值波动", className="eda-subsection-title"),
                            html.Div(
                                className="eda-chart-grid",
                                children=numeric_cards or [html.Div("当前没有适合直接看波动的数值字段。", className="eda-empty-card__text")],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def _build_field_guide_section(report: Dict[str, Any]) -> html.Div:
    return html.Div(
        className="eda-section-card",
        children=[
            _section_header("字段怎么用最合适", "不用懂字段类型，直接看它更适合做比较、做汇总还是做时间分析。", icon="bi-table"),
            html.Div(
                className="eda-profile-stack",
                children=[
                    _profile_table(
                        "适合做数值分析的字段",
                        [_profile_to_usage_row(item, "numeric") for item in report["numeric_profiles"]],
                        [("字段", "name"), ("更适合拿来做", "usage"), ("当前提醒", "note")],
                        "当前数据集没有可直接做数值分析的字段。",
                    ),
                    _profile_table(
                        "适合做人群/分类比较的字段",
                        [_profile_to_usage_row(item, "categorical") for item in report["categorical_profiles"]],
                        [("字段", "name"), ("更适合拿来做", "usage"), ("当前提醒", "note")],
                        "当前数据集没有可直接做分组比较的字段。",
                    ),
                    _profile_table(
                        "适合看趋势和周期的字段",
                        [_profile_to_usage_row(item, "datetime") for item in report["datetime_profiles"]],
                        [("字段", "name"), ("更适合拿来做", "usage"), ("当前提醒", "note")],
                        "当前数据集没有时间字段，暂时不适合做趋势分析。",
                    ),
                ],
            ),
        ],
    )


def _build_next_steps_section(report: Dict[str, Any]) -> html.Div:
    suggestions = _derive_next_steps(report)
    return html.Div(
        className="eda-section-card",
        children=[
            _section_header("下一步最值得做什么", "先给业务分析师一个清晰的动作建议。", icon="bi-lightbulb"),
            html.Div(
                className="eda-usecase-grid",
                children=[
                    html.Div(
                        className="eda-usecase-card",
                        children=[
                            html.Div("建议 01", className="eda-usecase-card__eyebrow"),
                            html.Div(item["title"], className="eda-usecase-card__title"),
                            html.Div(item["description"], className="eda-usecase-card__text"),
                        ],
                    )
                    for item in suggestions
                ],
            ),
        ],
    )


def _section_header(title: str, subtitle: str, icon: str) -> html.Div:
    return html.Div(
        className="eda-section-header",
        children=[
            html.Div(html.I(className=f"bi {icon}"), className="eda-section-header__icon"),
            html.Div(
                children=[
                    html.Div(title, className="eda-section-header__title"),
                    html.Div(subtitle, className="eda-section-header__subtitle"),
                ]
            ),
        ],
    )


def _alert_card(item: Dict[str, Any]) -> html.Div:
    severity_class = "eda-alert-card--warning" if item["severity"] == "warning" else "eda-alert-card--info"
    return html.Div(
        className=f"eda-alert-card {severity_class}",
        children=[
            html.Div(item["title"], className="eda-alert-card__title"),
            html.Div(item["message"], className="eda-alert-card__message"),
            html.Div(f"建议：{item['suggested_action']}", className="eda-alert-card__action"),
        ],
    )


def _summary_kv(label: str, value: str) -> html.Div:
    return html.Div(
        className="eda-summary-banner__kv",
        children=[
            html.Div(label, className="eda-summary-banner__kv-label"),
            html.Div(value, className="eda-summary-banner__kv-value"),
        ],
    )


def _use_case_card(item: Dict[str, str]) -> html.Div:
    return html.Div(
        className="eda-usecase-card",
        children=[
            html.Div(item["eyebrow"], className="eda-usecase-card__eyebrow"),
            html.Div(item["title"], className="eda-usecase-card__title"),
            html.Div(item["description"], className="eda-usecase-card__text"),
            html.Div(item["scene"], className="eda-usecase-card__scene"),
        ],
    )


def _derive_business_use_cases(report: Dict[str, Any]) -> List[Dict[str, str]]:
    use_cases: List[Dict[str, str]] = []
    if report["relationship_findings"]["categorical_numeric_pairs"]:
        use_cases.append(
            {
                "eyebrow": "分组比较",
                "title": "比较不同客户、门店、产品或区域的表现",
                "description": "直接找出哪一类对象更高、更低、差距最大。",
                "scene": "适合销售、运营、投放、门店经营分析。",
            }
        )
    if report["relationship_findings"]["numeric_pairs"]:
        use_cases.append(
            {
                "eyebrow": "指标联动",
                "title": "找到会一起变化的关键指标",
                "description": "判断一个指标变化时，哪些结果会一起跟着变。",
                "scene": "适合增长、转化、利润、成本联动分析。",
            }
        )
    if report["categorical_profiles"]:
        use_cases.append(
            {
                "eyebrow": "结构分析",
                "title": "看不同分类的构成和占比",
                "description": "快速判断主力分类、长尾分类和结构是否失衡。",
                "scene": "适合人群、品类、渠道、地区结构分析。",
            }
        )
    if report["numeric_profiles"]:
        use_cases.append(
            {
                "eyebrow": "波动查看",
                "title": "看关键指标大概落在哪些区间",
                "description": "可以快速发现值集中在哪、是否有明显异常波动。",
                "scene": "适合客单价、销量、利润、时长等指标。",
            }
        )
    if report["datetime_profiles"]:
        use_cases.append(
            {
                "eyebrow": "趋势分析",
                "title": "看时间趋势、节奏和周期",
                "description": "适合分析每天、每周、每月的变化方向。",
                "scene": "适合订单、流量、活跃、库存趋势分析。",
            }
        )
    use_cases.append(
        {
            "eyebrow": "分析前检查",
            "title": "先判断数据能不能直接拿来汇报",
            "description": "提前发现重复、空值、可疑字段，减少误判。",
            "scene": "适合所有业务分析场景。",
        }
    )
    return use_cases[:6]


def _derive_next_steps(report: Dict[str, Any]) -> List[Dict[str, str]]:
    steps: List[Dict[str, str]] = []
    if report["overview"]["missing_pct"] > 0 or report["overview"]["duplicate_pct"] > 0:
        steps.append(
            {
                "title": "先清理会影响结果的问题",
                "description": "优先处理空值、重复记录和不适合直接分析的字段，再做正式汇报。",
            }
        )
    if report["relationship_findings"]["categorical_numeric_pairs"]:
        pair = report["relationship_findings"]["categorical_numeric_pairs"][0]
        steps.append(
            {
                "title": f"先比较 {pair['category']} 对 {pair['numeric']} 的差异",
                "description": "这是当前最容易直接转成业务结论的一组比较。",
            }
        )
    if report["relationship_findings"]["numeric_pairs"]:
        pair = report["relationship_findings"]["numeric_pairs"][0]
        steps.append(
            {
                "title": f"联动查看 {pair['var1']} 和 {pair['var2']}",
                "description": "如果这两个指标同步变化，通常值得继续追溯原因。",
            }
        )
    if report["categorical_profiles"]:
        item = report["categorical_profiles"][0]
        steps.append(
            {
                "title": f"先看 {item['name']} 的分类构成",
                "description": "这能帮助你快速判断分析维度是否值得继续展开。",
            }
        )
    while len(steps) < 3:
        steps.append(
            {
                "title": "从一个业务问题开始切入",
                "description": "先选一个想回答的问题，再沿着这个页面给出的比较方向继续往下钻。",
            }
        )
    return steps[:3]


def _profile_to_usage_row(profile: Dict[str, Any], profile_type: str) -> Dict[str, str]:
    if profile_type == "numeric":
        note = "分布正常"
        if profile.get("outlier_pct", 0) > 5:
            note = "波动较大，建议留意异常值"
        elif profile.get("missing_pct", 0) > 0:
            note = "有空值，汇总前建议先处理"
        return {
            "name": profile["name"],
            "usage": "做汇总、做趋势、做高低比较",
            "note": note,
        }
    if profile_type == "categorical":
        note = "可直接用于分组比较"
        if profile.get("is_id_like"):
            note = "更像编号，不适合直接做分类比较"
        elif profile.get("is_high_cardinality"):
            note = "分类太多，建议先合并后分析"
        return {
            "name": profile["name"],
            "usage": "做人群、门店、区域、品类等分组比较",
            "note": note,
        }
    return {
        "name": profile["name"],
        "usage": "做趋势、周期、时间对比分析",
        "note": "可按日、周、月继续展开" if profile.get("range_days", 0) > 1 else "时间跨度较短，先确认是否适合做趋势",
    }


def _profile_table(title: str, rows: List[Dict[str, Any]], columns: List[tuple], empty_text: str) -> html.Div:
    if not rows:
        body = html.Div(empty_text, className="eda-empty-card__text")
    else:
        header = html.Tr([html.Th(col[0]) for col in columns])
        body_rows = []
        for row in rows[:10]:
            cells = []
            for column in columns:
                label, key = column[0], column[1]
                formatter = column[2] if len(column) > 2 else None
                cells.append(html.Td(_format_cell(row.get(key), formatter), className="eda-table__cell"))
            body_rows.append(html.Tr(cells))
        body = html.Div(
            className="eda-table-wrap",
            children=[html.Table([html.Thead(header), html.Tbody(body_rows)], className="eda-table")],
        )
    return html.Div(className="eda-subsection-card", children=[html.Div(title, className="eda-subsection-title"), body])


def _format_cell(value: Any, formatter: Optional[str]) -> str:
    if value is None:
        return "-"
    if formatter == "pct":
        return f"{float(value):.2f}%"
    if formatter == "float":
        return f"{float(value):.2f}"
    if formatter == "bool":
        return "是" if bool(value) else "否"
    return str(value)


def _relationship_list(title: str, items: Iterable[str]) -> html.Div:
    items = list(items)
    if not items:
        return html.Div([html.Div(title, className="eda-subsection-title"), html.Div("暂无可展示结果。", className="eda-empty-card__text")])
    return html.Div(
        className="eda-relationship-block",
        children=[
            html.Div(title, className="eda-subsection-title"),
            html.Ul([html.Li(item) for item in items], className="eda-relationship-list"),
        ],
    )


@callback(
    Output("download-data-file", "data"),
    Input("btn-export-csv", "n_clicks"),
    Input("btn-export-excel", "n_clicks"),
    Input("btn-export-json", "n_clicks"),
    prevent_initial_call=True,
)
def export_data(csv_clicks: Optional[int], excel_clicks: Optional[int], json_clicks: Optional[int]):
    dm = DataManager()
    df = dm.active_df
    if df is None:
        return no_update

    name = dm.active_name or "data"
    if ctx.triggered_id == "btn-export-csv":
        return dcc.send_data_frame(df.to_csv, f"{name}.csv", index=False)
    if ctx.triggered_id == "btn-export-excel":
        return dcc.send_data_frame(df.to_excel, f"{name}.xlsx", index=False)
    if ctx.triggered_id == "btn-export-json":
        return dcc.send_data_frame(df.to_json, f"{name}.json", orient="records", force_ascii=False)
    return no_update


@callback(
    Output("download-report-file", "data"),
    Input("btn-export-report", "n_clicks"),
    State("eda-analysis-mode", "data"),
    State("eda-sample-size", "data"),
    prevent_initial_call=True,
)
def export_report(n_clicks: Optional[int], analysis_mode: Optional[str], sample_size: Optional[int]):
    dm = DataManager()
    df = dm.active_df
    if df is None:
        return no_update

    name = dm.active_name or "data"
    mode = analysis_mode or "full"
    effective_sample_size = sample_size if mode == "sample" else None
    html_content = ReportGenerator.generate_html_report(df, name, mode=mode, sample_size=effective_sample_size)
    return {"content": html_content, "filename": f"{name}_分析报告.html"}
