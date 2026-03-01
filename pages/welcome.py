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
    return html.Div(
        className="dvs-welcome",
        children=[
            # Hero
            html.Div(
                className="dvs-welcome__hero",
                children=[
                    html.Div("🧪", className="dvs-welcome__logo"),
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
                                html.Div("📂", className="dvs-upload-zone__icon"),
                                html.Div("拖拽文件到此处，或点击选择文件", className="dvs-upload-zone__title"),
                                html.Div("支持 CSV、Excel (.xlsx)、JSON 格式", className="dvs-upload-zone__hint"),
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
                    html.Div("✨ 快速体验 — 示例数据集", className="dvs-welcome__samples-title"),
                    html.Div(
                        className="dvs-sample-btns",
                        children=[
                            _sample_button("sample-iris", "🌸 鸢尾花 (Iris)", "经典分类数据集 — 150 行 × 5 列"),
                            _sample_button("sample-tips", "🍽️ 餐饮小费 (Tips)", "餐厅消费数据 — 244 行 × 7 列"),
                            _sample_button("sample-titanic", "🚢 泰坦尼克 (Titanic)", "乘客生存数据 — 891 行 × 12 列"),
                        ],
                    ),
                ],
            ),
        ],
    )


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
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_sample_click(n_iris, n_tips, n_titanic, store_data):
    """处理示例数据集点击。"""
    if not ctx.triggered_id:
        return no_update, no_update

    sample_map = {
        "sample-iris": "iris",
        "sample-tips": "tips",
        "sample-titanic": "titanic",
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
