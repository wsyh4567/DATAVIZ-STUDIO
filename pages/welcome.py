# -*- coding: utf-8 -*-
"""DataViz Studio — 欢迎页

中央拖拽上传 + 示例数据集快速体验。
"""

from __future__ import annotations

import base64

from dash import html, dcc, Input, Output, State, callback, no_update, ctx

from core.data_manager import DataManager
from services.data_loader import load_file, load_sample_dataset, SAMPLE_DATASETS


def create_welcome_page() -> html.Div:
    """返回欢迎页布局。"""
    dm = DataManager()
    has_data = dm.active_df is not None

    return html.Div(
        className="dvs-welcome",
        children=[
            # ── Monarch 风格个性化欢迎横幅（有数据时显示）──
            html.Div(
                style={
                    "width": "100%",
                    "maxWidth": "820px",
                    "marginBottom": "32px",
                    "display": "block" if has_data else "none",
                },
                children=[
                    html.Div(
                        style={
                            "background": "#FFFFFF",
                            "border": "1px solid #E8EDF2",
                            "borderRadius": "16px",
                            "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
                            "padding": "24px 28px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "space-between",
                            "gap": "16px",
                        },
                        children=[
                            # 左侧：欢迎文字
                            html.Div([
                                html.Div(
                                    [
                                        html.Span("欢迎回来", style={"color": "#1A202C", "fontWeight": "700", "fontSize": "1.5rem"}),
                                        html.Span(" 👋", style={"fontSize": "1.4rem"}),
                                    ],
                                    style={"marginBottom": "6px"},
                                ),
                                html.Div(
                                    [
                                        "已加载数据集 ",
                                        html.Strong(
                                            dm.active_name or "未命名",
                                            style={"color": "#FF6B35"},
                                        ),
                                    ],
                                    style={"color": "#718096", "fontSize": "0.875rem"},
                                ),
                            ]),
                            # 右侧：快速数据摘要 Pill
                            html.Div(
                                style={"display": "flex", "gap": "12px", "flexWrap": "wrap"},
                                children=[
                                    _stat_pill(
                                        f"{len(dm.active_df):,}" if dm.active_df is not None else "—",
                                        "行", "#3182CE"
                                    ),
                                    _stat_pill(
                                        str(len(dm.active_df.columns)) if dm.active_df is not None else "—",
                                        "列", "#805AD5"
                                    ),
                                    _stat_pill("前往", "仪表盘", "#FF6B35", href="/dashboard"),
                                ] if has_data else [],
                            ),
                        ],
                    ),
                ],
            ),
            # Hero 标语
            html.Div(
                className="dvs-welcome__hero",
                children=[
                    html.I(className="bi bi-bar-chart-fill dvs-welcome__logo"),
                    html.H1("欢迎使用 DataViz Studio", className="dvs-welcome__title"),
                    html.P(
                        "免费开源的零代码数据分析可视化平台 — 拖入数据即可开始分析",
                        className="dvs-welcome__subtitle",
                    ),
                ],
            ),
            # Upload area

            html.Div(
                className="dvs-welcome__upload",
                children=[
                    dcc.Upload(
                        id="welcome-upload",
                        children=html.Div(
                            className="dvs-upload-zone",
                            children=[
                                html.I(className="bi bi-folder-plus dvs-upload-zone__icon"),
                                html.Div("拖拽文件到此处，或点击选择文件", className="dvs-upload-zone__title"),
                                html.Div("支持 CSV、TSV、Excel (.xlsx/.xls)、JSON、Parquet、Feather 格式", className="dvs-upload-zone__hint"),
                            ],
                        ),
                        multiple=False,
                    ),
                ],
            ),
            # Sample datasets
            html.Div(
                className="dvs-welcome__samples",
                children=[
                    html.Div("快速体验 — 示例数据集", className="dvs-welcome__samples-title"),
                    html.Div(
                        className="dvs-sample-btns",
                        children=[
                            _sample_button("sample-iris", "鸢尾花 (Iris)", "经典分类数据集 — 150 行 × 5 列"),
                            _sample_button("sample-tips", "餐饮小费 (Tips)", "餐厅消费数据 — 244 行 × 7 列"),
                            _sample_button("sample-titanic", "泰坦尼克 (Titanic)", "乘客生存数据 — 891 行 × 12 列"),
                            _sample_button("sample-gapminder", "国家经济 (Gapminder)", "全球经济发展数据 — 1704 行 × 6 列"),
                            _sample_button("sample-stocks", "科技股票 (Stocks)", "股票价格数据 — 504 行 × 7 列"),
                        ],
                    ),
                ],
            ),
            # 功能特性卡片区
            html.Div(
                className="dvs-welcome__samples",
                style={"marginTop": "2rem"},
                children=[
                    html.Div("核心功能", className="dvs-welcome__samples-title"),
                    html.Div(
                        className="dvs-sample-btns",
                        style={"gap": "12px"},
                        children=[
                            _feature_card("bi bi-hammer", "数据工坊", "拖拽式数据清洗、转换与处理\n支持撤销/重做、生成 Python 代码", "/workshop"),
                            _feature_card("bi bi-graph-up", "图表工作室", "30+ 种可视化图表类型\n智能推荐、交互式图表导出", "/charts"),
                            _feature_card("bi bi-file-earmark-bar-graph", "数据概况", "自动数据质量评估\n列级分布分析、相关性热力图", "/profiling"),
                            _feature_card("bi bi-calculator", "统计实验室", "假设检验、相关分析、异常检测\n交叉表分析、分组统计", "/stats"),
                            _feature_card("bi bi-lightning", "高级工具", "透视表、数据合并、抽样\n逾透视和数据重塑", "/advanced"),
                            _feature_card("bi bi-speedometer2", "仪表盘", "数据质量评分\n自动分布图、类型建议", "/dashboard"),
                        ],
                    ),
                ],
            ),
        ],
    )



def _stat_pill(value: str, label: str, color: str, href: str = None) -> html.Div:
    """Compact stat pill for the welcome banner."""
    inner = html.Div(
        style={
            "background": f"rgba({_welcome_hex_rgba(color)}, 0.10)",
            "border": f"1px solid rgba({_welcome_hex_rgba(color)}, 0.20)",
            "borderRadius": "10px",
            "padding": "8px 14px",
            "textAlign": "center",
            "cursor": "pointer" if href else "default",
        },
        children=[
            html.Div(value, style={"fontSize": "1.1rem", "fontWeight": "700", "color": color, "lineHeight": "1"}),
            html.Div(label, style={"fontSize": "0.7rem", "color": "#A0AEC0", "marginTop": "2px"}),
        ],
    )
    if href:
        return html.A(inner, href=href, style={"textDecoration": "none"})
    return inner


def _welcome_hex_rgba(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


def _sample_button(btn_id: str, label: str, desc: str) -> html.Button:
    return html.Button(
        children=[
            html.Span(label, style={"fontSize": "var(--text-base)", "fontWeight": "var(--font-semibold)"}),
            html.Br(),
            html.Span(desc, style={"fontSize": "var(--text-xs)", "color": "var(--text-muted)", "fontWeight": "var(--font-normal)"}),
        ],
        id=btn_id,
        className="dvs-btn card-hover stagger-item",
        style={
            "flexDirection": "column",
            "padding": "var(--sp-4) var(--sp-5)",
            "minWidth": "200px",
            "minHeight": "100px",
            "textAlign": "center",
            "gap": "var(--sp-2)",
        },
    )


def _feature_card(icon: str, title: str, desc: str, href: str) -> html.A:
    """功能特性卡片"""
    return html.A(
        children=[
            html.I(className=icon, style={"fontSize": "2rem", "color": "#FF6B35"}),
            html.Div(title, style={"fontWeight": "var(--font-semibold)", "fontSize": "var(--text-base)", "marginTop": "8px"}),
            html.Div(desc, style={
                "fontSize": "var(--text-xs)", "color": "var(--text-muted)",
                "whiteSpace": "pre-line", "lineHeight": "1.4", "marginTop": "4px",
            }),
        ],
        href=href,
        className="dvs-btn card-hover stagger-item",
        style={
            "flexDirection": "column",
            "padding": "var(--sp-4)",
            "minWidth": "180px",
            "minHeight": "120px",
            "textAlign": "center",
            "gap": "var(--sp-1)",
            "textDecoration": "none",
            "color": "inherit",
            "border": "1px solid var(--border)",
            "borderRadius": "12px",
            "backgroundColor": "var(--bg-secondary)",
        },
    )


# ── Callbacks ─────────────────────────────────────────

@callback(
    Output("app-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("welcome-upload", "contents"),
    State("welcome-upload", "filename"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_file_upload(contents, filename, store_data):
    """处理文件上传。"""
    if contents is None or filename is None:
        return no_update, no_update

    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        dm = DataManager()
        df = load_file(decoded, filename)
        name = dm.add_dataset(filename, df, source=f"file:{filename}")

        store_data = dict(store_data or {})
        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {"message": f"✅ 已加载 {name}（{len(df)} 行 × {len(df.columns)} 列）", "type": "success"}

        return store_data, "/canvas"
    except Exception as e:
        store_data = dict(store_data or {})
        store_data["toast"] = {"message": f"❌ 加载失败：{str(e)}", "type": "error"}
        return store_data, no_update


@callback(
    Output("app-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("sample-iris", "n_clicks"),
    Input("sample-tips", "n_clicks"),
    Input("sample-titanic", "n_clicks"),
    Input("sample-gapminder", "n_clicks"),
    Input("sample-stocks", "n_clicks"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_sample_click(n_iris, n_tips, n_titanic, n_gapminder, n_stocks, store_data):
    """处理示例数据集点击。"""
    if not ctx.triggered_id:
        return no_update, no_update

    sample_map = {
        "sample-iris": "iris",
        "sample-tips": "tips",
        "sample-titanic": "titanic",
        "sample-gapminder": "gapminder",
        "sample-stocks": "stocks",
    }
    sample_name = sample_map.get(ctx.triggered_id)
    if sample_name is None:
        return no_update, no_update

    try:
        dm = DataManager()
        df = load_sample_dataset(sample_name)
        label = SAMPLE_DATASETS[sample_name]["label"]
        name = dm.add_dataset(sample_name, df, source=f"sample:{sample_name}")

        store_data = dict(store_data or {})
        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {"message": f"✅ 已加载 {label}（{len(df)} 行 × {len(df.columns)} 列）", "type": "success"}

        return store_data, "/canvas"
    except Exception as e:
        store_data = dict(store_data or {})
        store_data["toast"] = {"message": f"❌ 加载失败：{str(e)}", "type": "error"}
        return store_data, no_update
