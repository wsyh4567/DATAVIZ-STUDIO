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
from services.data_loader import load_file, load_from_database
from utils.helpers import format_number, format_size


# ── 数据源定义 ─────────────────────────────────────────

DATA_SOURCES = [
    {"id": "csv", "icon": "bi bi-file-earmark-text", "label": "CSV / TSV", "type": "file"},
    {"id": "excel", "icon": "bi bi-file-earmark-spreadsheet", "label": "Excel", "type": "file"},
    {"id": "json", "icon": "bi bi-braces", "label": "JSON", "type": "file"},
    {"id": "db", "icon": "bi bi-database", "label": "数据库", "type": "modal"},
    {"id": "url", "icon": "bi bi-globe", "label": "URL", "type": "modal"},
    {"id": "paste", "icon": "bi bi-clipboard", "label": "粘贴板", "type": "modal"},
]


def create_data_hub_page() -> html.Div:
    """返回数据中心页面布局。"""

    # Source cards
    source_cards = []
    for src in DATA_SOURCES:
        cls = "dvs-source-card card-hover stagger-item"
        kwargs = {}
        if src["type"] == "modal":
            kwargs["id"] = f"card-{src['id']}"
            kwargs["n_clicks"] = 0

        card_content = html.Div(
            className=cls,
            children=[
                html.I(className=f"{src['icon']} dvs-source-card__icon"),
                html.Span(src["label"], className="dvs-source-card__label"),
            ],
            **kwargs
        )

        if src["type"] == "file":
            source_cards.append(
                dcc.Upload(
                    id=f"upload-{src['id']}",
                    children=card_content,
                    multiple=True,
                    style={"display": "inline-block", "textDecoration": "none"}
                )
            )
        else:
            source_cards.append(card_content)

    return html.Div(
        children=[
            html.H2("数据中心", className="dvs-page-title"),

            # Source type cards
            html.Div(className="dvs-source-cards stagger-container", children=source_cards),

            # Upload zone
            dcc.Upload(
                id="datahub-upload",
                children=html.Div(
                    className="dvs-upload-zone fade-in",
                    children=[
                        html.I(className="bi bi-folder-plus dvs-upload-zone__icon"),
                        html.Div("拖拽文件到此处，或点击选择文件", className="dvs-upload-zone__title"),
                        html.Div("支持 CSV、TSV、Excel (.xlsx/.xls)、JSON、Parquet、Feather 格式", className="dvs-upload-zone__hint"),
                    ],
                ),
                multiple=True,
                style={"marginBottom": "var(--sp-4)"},
            ),

            # ── Modals (隐藏的弹窗) ──
            
            # URL 导入弹窗
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("从 URL 导入", className="dvs-page-subtitle")),
                dbc.ModalBody(
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "12px", "padding": "8px 0"},
                        children=[
                            dcc.Input(
                                id="datahub-url-input", type="url",
                                placeholder="输入 CSV/JSON 文件的 URL，如 https://example.com/data.csv",
                                style={"width": "100%", "padding": "8px 12px", "borderRadius": "6px",
                                       "border": "1px solid var(--border)", "backgroundColor": "var(--bg-secondary)",
                                       "color": "var(--text-primary)", "fontSize": "0.875rem"},
                            ),
                        ]
                    )
                ),
                dbc.ModalFooter(
                    html.Button("导入", id="datahub-url-btn", className="dvs-btn dvs-btn--primary btn-hover")
                ),
            ], id="modal-url", is_open=False, centered=True),

            # 数据库导入弹窗
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("从数据库加载", className="dvs-page-subtitle")),
                dbc.ModalBody(
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "12px", "padding": "8px 0"},
                        children=[
                            html.Div(
                                "支持 SQLite、MySQL、PostgreSQL 等 (格式：sqlite:///data.db 或 mysql+pymysql://user:pwd@host:port/df_name)",
                                style={"fontSize": "0.8rem", "color": "var(--text-muted)"}
                            ),
                            dcc.Input(
                                id="datahub-db-connection", type="text",
                                placeholder="输入 SQLAlchemy 数据库连接字符串",
                                style={"width": "100%", "padding": "8px 12px", "borderRadius": "6px",
                                       "border": "1px solid var(--border)", "backgroundColor": "var(--bg-secondary)",
                                       "color": "var(--text-primary)", "fontSize": "0.875rem"},
                            ),
                            dcc.Textarea(
                                id="datahub-db-query",
                                placeholder="执行查询语句，例如：SELECT * FROM users LIMIT 1000",
                                style={"width": "100%", "height": "80px", "padding": "10px",
                                       "borderRadius": "6px", "border": "1px solid var(--border)",
                                       "backgroundColor": "var(--bg-secondary)", "color": "var(--text-primary)",
                                       "fontSize": "0.85rem", "fontFamily": "monospace", "resize": "vertical"},
                            ),
                        ],
                    )
                ),
                dbc.ModalFooter(
                    html.Button("查询并导入", id="datahub-db-btn", className="dvs-btn dvs-btn--primary btn-hover")
                ),
            ], id="modal-db", is_open=False, centered=True, size="lg"),

            # 粘贴板导入弹窗
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("从粘贴板导入", className="dvs-page-subtitle")),
                dbc.ModalBody(
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "12px", "padding": "8px 0"},
                        children=[
                            dcc.Textarea(
                                id="datahub-paste-input",
                                placeholder="粘贴表格数据（支持 Tab 分隔或逗号分隔）\n例如：\nname,age,city\nAlice,25,NYC\nBob,30,LA",
                                style={"width": "100%", "height": "160px", "padding": "10px",
                                       "borderRadius": "6px", "border": "1px solid var(--border)",
                                       "backgroundColor": "var(--bg-secondary)", "color": "var(--text-primary)",
                                       "fontSize": "0.85rem", "fontFamily": "monospace", "resize": "vertical"},
                            ),
                            dcc.Dropdown(
                                id="datahub-paste-sep",
                                options=[
                                    {"label": "自动检测模式", "value": "auto"},
                                    {"label": "使用逗号 (,)", "value": ","},
                                    {"label": "使用 Tab (\\t)", "value": "\t"},
                                    {"label": "使用分号 (;)", "value": ";"},
                                    {"label": "使用管道 (|)", "value": "|"},
                                ],
                                value="auto",
                                clearable=False,
                            ),
                        ]
                    )
                ),
                dbc.ModalFooter(
                    html.Button("导入粘贴数据", id="datahub-paste-btn", className="dvs-btn dvs-btn--primary btn-hover")
                ),
            ], id="modal-paste", is_open=False, centered=True, size="lg"),

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
    Input("upload-csv", "contents"),
    Input("upload-excel", "contents"),
    Input("upload-json", "contents"),
    State("datahub-upload", "filename"),
    State("upload-csv", "filename"),
    State("upload-excel", "filename"),
    State("upload-json", "filename"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_datahub_upload(c_main, c_csv, c_excel, c_json, f_main, f_csv, f_excel, f_json, store_data):
    """数据中心文件上传（支持多文件）。"""
    ctx_id = ctx.triggered_id
    if ctx_id == "datahub-upload":
        contents, filename = c_main, f_main
    elif ctx_id == "upload-csv":
        contents, filename = c_csv, f_csv
    elif ctx_id == "upload-excel":
        contents, filename = c_excel, f_excel
    elif ctx_id == "upload-json":
        contents, filename = c_json, f_json
    else:
        return no_update, no_update

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


# ── 弹窗控制 ──────────────────────────────────────────

@callback(
    Output("modal-url", "is_open"),
    Input("card-url", "n_clicks"),
    State("modal-url", "is_open"),
    prevent_initial_call=True
)
def toggle_modal_url(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("modal-db", "is_open"),
    Input("card-db", "n_clicks"),
    State("modal-db", "is_open"),
    prevent_initial_call=True
)
def toggle_modal_db(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("modal-paste", "is_open"),
    Input("card-paste", "n_clicks"),
    State("modal-paste", "is_open"),
    prevent_initial_call=True
)
def toggle_modal_paste(n, is_open):
    if n:
        return not is_open
    return is_open


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


# ── 数据库导入 ────────────────────────────────────────

@callback(
    Output("app-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("datahub-db-btn", "n_clicks"),
    State("datahub-db-connection", "value"),
    State("datahub-db-query", "value"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_db_import(n_clicks, conn_str, query_str, store_data):
    """从数据库加载数据"""
    if not conn_str or not conn_str.strip() or not query_str or not query_str.strip():
        return no_update, no_update

    store_data = store_data or {}
    try:
        df = load_from_database(conn_str.strip(), query_str.strip())
        
        # 提取连接字符串的 db 名字片段作为大致名称
        import urllib.parse
        parsed = urllib.parse.urlparse(conn_str.strip())
        db_name = parsed.path.lstrip('/') if parsed.path else "database"
        db_name = db_name.split('.')[0] # e.g. /my_data.db -> my_data
        if not db_name:
            db_name = "db_data"
            
        filename = f"{db_name}_query"

        dm = DataManager()
        name = dm.add_dataset(filename, df, source=f"db:{conn_str}")

        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {
            "message": f"已从数据库加载查询结果（{len(df)} 行 × {len(df.columns)} 列）",
            "type": "success",
        }
        return store_data, "/canvas"

    except Exception as e:
        store_data["toast"] = {"message": f"数据库加载失败：{str(e)}", "type": "error"}
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
                            html.Span(meta.name, className="dvs-dataset-item__name"),
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
