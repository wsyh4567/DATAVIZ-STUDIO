# -*- coding: utf-8 -*-
"""DataViz Studio — 数据中心页

数据源卡片 + 上传区域 + URL导入 + 粘贴板导入 + 已加载数据集列表。
"""

from __future__ import annotations

import base64
import io

from dash import html, dcc, Input, Output, State, callback, no_update, ctx, ALL, MATCH
import dash_bootstrap_components as dbc
import pandas as pd

from core.data_manager import DataManager
from services.data_loader import load_file
from utils.helpers import format_number, format_size


# ── 数据源定义 ─────────────────────────────────────────

DATA_SOURCES = [
    {"icon": "📄", "label": "CSV / TSV", "enabled": True},
    {"icon": "📊", "label": "Excel", "enabled": True},
    {"icon": "🔗", "label": "JSON", "enabled": True},
    {"icon": "🗄️", "label": "数据库", "enabled": False},
    {"icon": "🌐", "label": "URL", "enabled": True},
    {"icon": "📋", "label": "粘贴板", "enabled": True},
]


def create_data_hub_page() -> html.Div:
    """返回数据中心页面布局。"""

    # Source cards
    source_cards = []
    for src in DATA_SOURCES:
        cls = "dvs-source-card card-hover stagger-item"
        if not src["enabled"]:
            cls += " dvs-source-card--disabled"
        card = html.Div(
            className=cls,
            children=[
                html.Span(src["icon"], className="dvs-source-card__icon"),
                html.Span(src["label"], className="dvs-source-card__label"),
                *([] if src["enabled"] else [
                    html.Span("即将推出", className="dvs-badge dvs-badge--soon"),
                ]),
            ],
        )
        source_cards.append(card)

    return html.Div(
        children=[
            html.H2("📁 数据中心", className="dvs-page-title"),

            # Source type cards
            html.Div(className="dvs-source-cards stagger-container", children=source_cards),

            # Upload zone
            dcc.Upload(
                id="datahub-upload",
                children=html.Div(
                    className="dvs-upload-zone fade-in",
                    children=[
                        html.Div("📂", className="dvs-upload-zone__icon"),
                        html.Div("拖拽文件到此处，或点击选择文件", className="dvs-upload-zone__title"),
                        html.Div("支持 CSV、TSV、Excel (.xlsx/.xls)、JSON、Parquet、Feather 格式", className="dvs-upload-zone__hint"),
                    ],
                ),
                multiple=True,
                style={"marginBottom": "var(--sp-4)"},
            ),

            # URL 导入区域
            html.Div(
                style={"marginBottom": "var(--sp-4)"},
                children=[
                    html.Div(
                        className="dvs-section-header",
                        children=[
                            html.Span("🌐 从 URL 导入", className="dvs-section-header__title"),
                        ],
                    ),
                    html.Div(
                        style={"display": "flex", "gap": "8px", "alignItems": "center", "padding": "8px 0"},
                        children=[
                            dcc.Input(
                                id="datahub-url-input",
                                type="url",
                                placeholder="输入 CSV/JSON 文件的 URL，如 https://example.com/data.csv",
                                style={"flex": "1", "padding": "8px 12px", "borderRadius": "6px",
                                       "border": "1px solid var(--border)", "backgroundColor": "var(--bg-secondary)",
                                       "color": "var(--text-primary)", "fontSize": "0.875rem"},
                            ),
                            html.Button(
                                "导入",
                                id="datahub-url-btn",
                                className="dvs-btn dvs-btn--primary btn-hover",
                                style={"padding": "8px 20px", "whiteSpace": "nowrap"},
                            ),
                        ],
                    ),
                ],
            ),

            # 粘贴板导入区域
            html.Div(
                style={"marginBottom": "var(--sp-4)"},
                children=[
                    html.Div(
                        className="dvs-section-header",
                        children=[
                            html.Span("📋 从粘贴板导入", className="dvs-section-header__title"),
                        ],
                    ),
                    dcc.Textarea(
                        id="datahub-paste-input",
                        placeholder="粘贴表格数据（支持 Tab 分隔或逗号分隔）\n例如：\nname,age,city\nAlice,25,NYC\nBob,30,LA",
                        style={"width": "100%", "height": "120px", "padding": "10px",
                               "borderRadius": "6px", "border": "1px solid var(--border)",
                               "backgroundColor": "var(--bg-secondary)", "color": "var(--text-primary)",
                               "fontSize": "0.85rem", "fontFamily": "monospace", "resize": "vertical"},
                    ),
                    html.Div(
                        style={"display": "flex", "gap": "8px", "marginTop": "8px", "alignItems": "center"},
                        children=[
                            dcc.Dropdown(
                                id="datahub-paste-sep",
                                options=[
                                    {"label": "自动检测", "value": "auto"},
                                    {"label": "逗号 (,)", "value": ","},
                                    {"label": "Tab (\\t)", "value": "\t"},
                                    {"label": "分号 (;)", "value": ";"},
                                    {"label": "管道 (|)", "value": "|"},
                                ],
                                value="auto",
                                clearable=False,
                                style={"width": "160px"},
                            ),
                            html.Button(
                                "导入粘贴数据",
                                id="datahub-paste-btn",
                                className="dvs-btn dvs-btn--primary btn-hover",
                                style={"padding": "8px 20px"},
                            ),
                        ],
                    ),
                ],
            ),

            # Dataset list
            html.Div(
                className="dvs-section-header",
                children=[
                    html.Span("已加载数据集", className="dvs-section-header__title"),
                    html.Span(id="datahub-count", className="dvs-section-header__sub"),
                ],
            ),
            html.Div(id="datahub-dataset-list"),
        ]
    )


# ── Callbacks ─────────────────────────────────────────

@callback(
    Output("app-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("datahub-upload", "contents"),
    State("datahub-upload", "filename"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_datahub_upload(contents, filename, store_data):
    """数据中心文件上传（支持多文件）。"""
    if contents is None or filename is None:
        return no_update, no_update

    # 统一为列表格式（兼容单文件和多文件）
    if isinstance(contents, str):
        contents = [contents]
        filename = [filename]

    store_data = store_data or {}
    dm = DataManager()
    loaded = []
    errors = []

    for content, fname in zip(contents, filename):
        try:
            content_type, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            df = load_file(decoded, fname)
            name = dm.add_dataset(fname, df, source=f"file:{fname}")
            loaded.append(f"{name}({len(df)}行)")
        except Exception as e:
            errors.append(f"{fname}: {e}")

    if loaded:
        store_data["active_dataset"] = dm.active_name
        store_data["datasets"] = dm.dataset_names
        msg = f"已加载 {len(loaded)} 个文件：{', '.join(loaded)}"
        if errors:
            msg += f"；{len(errors)} 个失败"
        store_data["toast"] = {"message": msg, "type": "success"}
        return store_data, "/canvas"

    store_data["toast"] = {"message": f"全部加载失败：{'; '.join(errors)}", "type": "error"}
    return store_data, no_update


# ── URL 导入 ──────────────────────────────────────────

@callback(
    Output("app-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("datahub-url-btn", "n_clicks"),
    State("datahub-url-input", "value"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_url_import(n_clicks, url_value, store_data):
    """从 URL 导入 CSV/JSON 数据。"""
    if not url_value or not url_value.strip():
        return no_update, no_update

    url = url_value.strip()
    store_data = store_data or {}

    try:
        # 根据 URL 后缀猜测格式
        url_lower = url.lower().split('?')[0]

        if url_lower.endswith('.json'):
            df = pd.read_json(url)
        elif url_lower.endswith('.tsv'):
            df = pd.read_csv(url, sep='\t')
        elif url_lower.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(url)
        elif url_lower.endswith('.parquet'):
            df = pd.read_parquet(url)
        else:
            # 默认尝试 CSV
            df = pd.read_csv(url)

        # 提取文件名
        filename = url.split('/')[-1].split('?')[0] or "url_data"

        dm = DataManager()
        name = dm.add_dataset(filename, df, source=f"url:{url}")

        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {
            "message": f"已从 URL 加载 {name}（{len(df)} 行 × {len(df.columns)} 列）",
            "type": "success",
        }
        return store_data, "/canvas"

    except Exception as e:
        store_data["toast"] = {"message": f"URL 导入失败：{str(e)}", "type": "error"}
        return store_data, no_update


# ── 粘贴板导入 ────────────────────────────────────────

@callback(
    Output("app-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("datahub-paste-btn", "n_clicks"),
    State("datahub-paste-input", "value"),
    State("datahub-paste-sep", "value"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_paste_import(n_clicks, paste_text, sep, store_data):
    """从粘贴板文本导入数据。"""
    if not paste_text or not paste_text.strip():
        return no_update, no_update

    store_data = store_data or {}

    try:
        text = paste_text.strip()

        # 自动检测分隔符
        if sep == "auto":
            first_line = text.split('\n')[0]
            if '\t' in first_line:
                sep = '\t'
            elif ',' in first_line:
                sep = ','
            elif ';' in first_line:
                sep = ';'
            elif '|' in first_line:
                sep = '|'
            else:
                sep = ','

        df = pd.read_csv(io.StringIO(text), sep=sep)

        if df.empty:
            store_data["toast"] = {"message": "粘贴的数据为空", "type": "error"}
            return store_data, no_update

        dm = DataManager()
        name = dm.add_dataset("粘贴数据", df, source="clipboard")

        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {
            "message": f"已从粘贴板加载 {name}（{len(df)} 行 × {len(df.columns)} 列）",
            "type": "success",
        }
        return store_data, "/canvas"

    except Exception as e:
        store_data["toast"] = {"message": f"粘贴板导入失败：{str(e)}", "type": "error"}
        return store_data, no_update


# ── 数据集列表 ────────────────────────────────────────

@callback(
    Output("datahub-dataset-list", "children"),
    Output("datahub-count", "children"),
    Input("app-store", "data"),
)
def update_dataset_list(store_data):
    """更新已加载数据集列表。"""
    dm = DataManager()
    datasets = dm.list_datasets()
    active = (store_data or {}).get("active_dataset")

    if not datasets:
        return html.Div(
            className="dvs-empty",
            children=[
                html.Div("📭", className="dvs-empty__icon"),
                html.Div("尚未加载任何数据集", className="dvs-empty__text"),
                html.Div("通过上方区域上传文件，或从欢迎页加载示例数据", style={"color": "var(--text-muted)", "fontSize": "var(--text-sm)"}),
            ],
        ), "0 个数据集"

    items = []
    for meta in datasets:
        is_active = meta.name == active
        cls = "dvs-dataset-item card-hover stagger-item"
        if is_active:
            cls += " dvs-dataset-item--active"
        items.append(
            html.Div(
                className=cls,
                children=[
                    html.Div(
                        className="dvs-dataset-item__info",
                        children=[
                            html.Span(f"📊 {meta.name}", className="dvs-dataset-item__name"),
                            html.Span(
                                f"{format_number(meta.rows)} 行 × {meta.cols} 列 | {meta.memory_mb:.1f} MB",
                                className="dvs-dataset-item__meta",
                            ),
                        ],
                    ),
                    html.Div(
                        className="dvs-dataset-item__actions",
                        children=[
                            html.Button(
                                "✓ 活跃" if is_active else "设为活跃",
                                className="dvs-btn dvs-btn--sm" + (" dvs-btn--primary" if is_active else ""),
                                id={"type": "activate-btn", "index": meta.name},
                                disabled=is_active,
                            ),
                            html.Button(
                                "🗑️",
                                className="dvs-btn dvs-btn--sm dvs-btn--ghost",
                                id={"type": "delete-btn", "index": meta.name},
                                title="删除",
                            ),
                        ],
                    ),
                ],
            )
        )

    return html.Div(className="stagger-container", children=items), f"{len(datasets)} 个数据集"


# ── 设为活跃数据集 ────────────────────────────────────

@callback(
    Output("app-store", "data", allow_duplicate=True),
    Input({"type": "activate-btn", "index": ALL}, "n_clicks"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def activate_dataset(n_clicks_list, store_data):
    """点击'设为活跃'按钮时切换活跃数据集。"""
    if not any(n_clicks_list):
        return no_update

    triggered = ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        return no_update

    name = triggered["index"]
    dm = DataManager()
    if name in dm.dataset_names:
        dm.active_name = name
        store_data = store_data or {}
        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {
            "message": f"已切换活跃数据集为：{name}",
            "type": "success",
        }
        return store_data

    return no_update


# ── 删除数据集 ────────────────────────────────────────

@callback(
    Output("app-store", "data", allow_duplicate=True),
    Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def delete_dataset(n_clicks_list, store_data):
    """点击'删除'按钮时移除数据集。"""
    if not any(n_clicks_list):
        return no_update

    triggered = ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        return no_update

    name = triggered["index"]
    dm = DataManager()
    dm.remove_dataset(name)

    store_data = store_data or {}
    store_data["active_dataset"] = dm.active_name
    store_data["datasets"] = dm.dataset_names
    store_data["toast"] = {
        "message": f"已删除数据集：{name}",
        "type": "info",
    }
    return store_data
