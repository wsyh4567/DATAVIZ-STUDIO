# -*- coding: utf-8 -*-
"""Data hub page."""

from __future__ import annotations

import base64
import io
import urllib.parse

from dash import ALL, Input, Output, State, callback, ctx, dcc, html, no_update
import dash_bootstrap_components as dbc
import pandas as pd

from core.data_manager import DataManager
from services.data_loader import load_file, load_from_database
from utils.helpers import format_number


DATA_SOURCES = [
    {"id": "csv", "icon": "bi bi-file-earmark-text", "label": "CSV / TSV", "type": "file"},
    {"id": "excel", "icon": "bi bi-file-earmark-spreadsheet", "label": "Excel", "type": "file"},
    {"id": "json", "icon": "bi bi-braces", "label": "JSON", "type": "file"},
    {"id": "db", "icon": "bi bi-database", "label": "数据库", "type": "modal"},
    {"id": "url", "icon": "bi bi-globe", "label": "URL", "type": "modal"},
    {"id": "paste", "icon": "bi bi-clipboard", "label": "粘贴板", "type": "modal"},
]

DB_ENGINES = [
    {
        "value": "postgresql",
        "label": "PostgreSQL",
        "mode": "server",
        "dialect": "postgresql+psycopg2",
        "port": "5432",
        "params_hint": "sslmode=require",
        "drivers": [
            {"label": "psycopg2", "value": "postgresql+psycopg2"},
            {"label": "psycopg 3", "value": "postgresql+psycopg"},
            {"label": "pg8000", "value": "postgresql+pg8000"},
        ],
    },
    {
        "value": "mysql",
        "label": "MySQL",
        "mode": "server",
        "dialect": "mysql+pymysql",
        "port": "3306",
        "params_hint": "charset=utf8mb4",
        "drivers": [
            {"label": "PyMySQL", "value": "mysql+pymysql"},
            {"label": "mysqlclient", "value": "mysql+mysqldb"},
            {"label": "mysql-connector", "value": "mysql+mysqlconnector"},
        ],
    },
    {
        "value": "mariadb",
        "label": "MariaDB",
        "mode": "server",
        "dialect": "mariadb+mariadbconnector",
        "port": "3306",
        "params_hint": "charset=utf8mb4",
        "drivers": [
            {"label": "MariaDB Connector", "value": "mariadb+mariadbconnector"},
            {"label": "PyMySQL", "value": "mysql+pymysql"},
        ],
    },
    {
        "value": "sqlserver",
        "label": "SQL Server",
        "mode": "server",
        "dialect": "mssql+pyodbc",
        "port": "1433",
        "params_hint": "driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes",
        "drivers": [
            {"label": "pyodbc", "value": "mssql+pyodbc"},
            {"label": "pymssql", "value": "mssql+pymssql"},
        ],
    },
    {
        "value": "oracle",
        "label": "Oracle",
        "mode": "server",
        "dialect": "oracle+oracledb",
        "port": "1521",
        "params_hint": "service_name=orclpdb1",
        "drivers": [
            {"label": "oracledb", "value": "oracle+oracledb"},
            {"label": "cx_Oracle", "value": "oracle+cx_oracle"},
        ],
    },
    {
        "value": "sqlite",
        "label": "SQLite",
        "mode": "file",
        "dialect": "sqlite",
        "port": "",
        "params_hint": "",
        "drivers": [
            {"label": "sqlite", "value": "sqlite"},
            {"label": "aiosqlite", "value": "sqlite+aiosqlite"},
        ],
    },
    {
        "value": "duckdb",
        "label": "DuckDB",
        "mode": "file",
        "dialect": "duckdb",
        "port": "",
        "params_hint": "",
        "drivers": [
            {"label": "duckdb-engine", "value": "duckdb"},
        ],
    },
]

DB_ENGINE_MAP = {item["value"]: item for item in DB_ENGINES}


def _db_label(text: str, required: bool = False) -> html.Label:
    marker = (
        html.Span(" *", className="dvs-db-form__required")
        if required
        else html.Span(" 选填", className="dvs-db-form__optional")
    )
    return html.Label([text, marker], className="dvs-db-form__label")


def _build_db_connection_string(
    db_type: str,
    dialect: str | None,
    host: str | None,
    port: str | None,
    username: str | None,
    password: str | None,
    database: str | None,
    file_path: str | None,
    extra_params: str | None,
) -> str:
    config = DB_ENGINE_MAP.get(db_type or "postgresql", DB_ENGINE_MAP["postgresql"])
    final_dialect = (dialect or config["dialect"]).strip()
    params = (extra_params or "").strip()

    if config["mode"] == "file":
        final_path = (file_path or "").strip()
        if not final_path:
            raise ValueError("请填写数据库文件路径")
        normalized = final_path if final_path == ":memory:" else final_path.replace("\\", "/")
        conn_str = f"{final_dialect}:///{normalized}"
    else:
        host_value = (host or "").strip()
        database_value = (database or "").strip()
        if not host_value:
            raise ValueError("Host 为必填项")
        if not database_value:
            raise ValueError("数据库名称为必填项")

        user_value = urllib.parse.quote_plus((username or "").strip())
        password_raw = password or ""
        auth = ""
        if user_value:
            auth = user_value
            if password is not None:
                auth += f":{urllib.parse.quote_plus(password_raw)}"
            auth += "@"
        port_value = str(port).strip() if port else ""
        port_part = f":{port_value}" if port_value else ""
        conn_str = (
            f"{final_dialect}://{auth}{host_value}{port_part}/"
            f"{urllib.parse.quote_plus(database_value)}"
        )

    if params:
        conn_str = f"{conn_str}{'&' if '?' in conn_str else '?'}{params}"
    return conn_str


def _source_cards() -> list:
    cards = []
    for src in DATA_SOURCES:
        div_kwargs = {"className": "dvs-source-card card-hover stagger-item"}
        if src["type"] == "modal":
            div_kwargs["id"] = f"card-{src['id']}"
            div_kwargs["n_clicks"] = 0

        content = html.Div(
            children=[
                html.I(className=f"{src['icon']} dvs-source-card__icon"),
                html.Span(src["label"], className="dvs-source-card__label"),
            ],
            **div_kwargs,
        )
        if src["type"] == "file":
            cards.append(
                dcc.Upload(
                    id=f"upload-{src['id']}",
                    children=content,
                    multiple=True,
                    style={"display": "inline-block", "textDecoration": "none"},
                )
            )
        else:
            cards.append(content)
    return cards


def create_data_hub_page() -> html.Div:
    return html.Div(
        children=[
            html.H2("数据中心", className="dvs-page-title"),
            html.Div(className="dvs-source-cards stagger-container", children=_source_cards()),
            dcc.Upload(
                id="datahub-upload",
                children=html.Div(
                    className="dvs-upload-zone fade-in",
                    children=[
                        html.I(className="bi bi-folder-plus dvs-upload-zone__icon"),
                        html.Div("拖拽文件到此处，或点击选择文件", className="dvs-upload-zone__title"),
                        html.Div("支持 CSV、TSV、Excel、JSON、Parquet、Feather", className="dvs-upload-zone__hint"),
                    ],
                ),
                multiple=True,
                style={"marginBottom": "var(--sp-4)"},
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("从 URL 导入", className="dvs-page-subtitle")),
                    dbc.ModalBody(
                        html.Div(
                            style={"display": "flex", "flexDirection": "column", "gap": "12px", "padding": "8px 0"},
                            children=[
                                dcc.Input(
                                    id="datahub-url-input",
                                    type="url",
                                    placeholder="输入 CSV / JSON 文件 URL，例如 https://example.com/data.csv",
                                    style={
                                        "width": "100%",
                                        "padding": "8px 12px",
                                        "borderRadius": "6px",
                                        "border": "1px solid var(--border)",
                                        "backgroundColor": "var(--bg-secondary)",
                                        "color": "var(--text-primary)",
                                        "fontSize": "0.875rem",
                                    },
                                )
                            ],
                        )
                    ),
                    dbc.ModalFooter(
                        html.Button("导入", id="datahub-url-btn", className="dvs-btn dvs-btn--primary btn-hover")
                    ),
                ],
                id="modal-url",
                is_open=False,
                centered=True,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("从数据库加载", className="dvs-page-subtitle")),
                    dbc.ModalBody(
                        html.Div(
                            className="dvs-db-modal",
                            children=[
                                html.Div(
                                    className="dvs-db-form dvs-db-form--compact",
                                    children=[
                                        html.Div(className="dvs-db-form__row dvs-db-form__row--half", children=[_db_label("数据库类型", required=True), dcc.Dropdown(id="datahub-db-type", options=[{"label": item["label"], "value": item["value"]} for item in DB_ENGINES], value="postgresql", clearable=False)]),
                                        html.Div(className="dvs-db-form__row dvs-db-form__row--half", children=[_db_label("驱动", required=True), dcc.Dropdown(id="datahub-db-dialect", options=[driver for driver in DB_ENGINES[0]["drivers"]], value="postgresql+psycopg2", clearable=False)]),
                                        html.Div(id="datahub-db-host-row", className="dvs-db-form__row dvs-db-form__row--half", children=[_db_label("Host", required=True), dcc.Input(id="datahub-db-host", type="text", placeholder="127.0.0.1")]),
                                        html.Div(id="datahub-db-port-row", className="dvs-db-form__row dvs-db-form__row--half", children=[_db_label("Port"), dcc.Input(id="datahub-db-port", type="text", value="5432", placeholder="5432")]),
                                        html.Div(id="datahub-db-user-row", className="dvs-db-form__row dvs-db-form__row--half", children=[_db_label("用户名"), dcc.Input(id="datahub-db-username", type="text", placeholder="user")]),
                                        html.Div(id="datahub-db-password-row", className="dvs-db-form__row dvs-db-form__row--half", children=[_db_label("密码"), dcc.Input(id="datahub-db-password", type="password", placeholder="password")]),
                                        html.Div(id="datahub-db-name-row", className="dvs-db-form__row dvs-db-form__row--half", children=[_db_label("数据库名称", required=True), dcc.Input(id="datahub-db-name", type="text", placeholder="analytics")]),
                                        html.Div(id="datahub-db-file-row", className="dvs-db-form__row dvs-db-form__row--half", style={"display": "none"}, children=[_db_label("数据库文件", required=True), dcc.Input(id="datahub-db-file", type="text", placeholder="D:/data/warehouse.duckdb 或 :memory:")]),
                                        html.Div(className="dvs-db-form__row dvs-db-form__row--full", children=[_db_label("额外参数"), dcc.Input(id="datahub-db-options", type="text", placeholder="例如 sslmode=require 或 charset=utf8mb4")]),
                                        html.Div(id="datahub-db-form-hint", className="dvs-db-form__hint dvs-db-form__row dvs-db-form__row--full"),
                                    ],
                                ),
                                html.Div(
                                    className="dvs-db-sql-panel",
                                    children=[
                                        html.Div(className="dvs-db-sql-panel__header", children=[html.Div("SQL 查询", className="dvs-db-sql-panel__title"), html.Div("必填", className="dvs-db-sql-panel__meta")]),
                                        dcc.Textarea(id="datahub-db-query", className="dvs-db-sql-panel__textarea", placeholder="SELECT *\nFROM your_table\nLIMIT 1000"),
                                    ],
                                ),
                            ],
                        )
                    ),
                    dbc.ModalFooter(
                        html.Button("查询并导入", id="datahub-db-btn", className="dvs-btn dvs-btn--primary btn-hover")
                    ),
                ],
                id="modal-db",
                is_open=False,
                centered=True,
                size="xl",
                className="dvs-db-config-modal",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("从粘贴板导入", className="dvs-page-subtitle")),
                    dbc.ModalBody(
                        html.Div(
                            style={"display": "flex", "flexDirection": "column", "gap": "12px", "padding": "8px 0"},
                            children=[
                                dcc.Textarea(
                                    id="datahub-paste-input",
                                    placeholder="粘贴表格数据，支持 Tab 或逗号分隔",
                                    style={"width": "100%", "height": "160px", "padding": "10px", "borderRadius": "6px", "border": "1px solid var(--border)", "backgroundColor": "var(--bg-secondary)", "color": "var(--text-primary)", "fontSize": "0.85rem", "fontFamily": "monospace", "resize": "vertical"},
                                ),
                                dcc.Dropdown(id="datahub-paste-sep", options=[{"label": "自动检测", "value": "auto"}, {"label": "逗号 (,)", "value": ","}, {"label": "Tab (\\t)", "value": "\t"}, {"label": "分号 (;)", "value": ";"}, {"label": "竖线 (|)", "value": "|"}], value="auto", clearable=False),
                            ],
                        )
                    ),
                    dbc.ModalFooter(
                        html.Button("导入粘贴数据", id="datahub-paste-btn", className="dvs-btn dvs-btn--primary btn-hover")
                    ),
                ],
                id="modal-paste",
                is_open=False,
                centered=True,
                size="lg",
            ),
            html.Div(className="dvs-section-header", children=[html.Span("已加载数据集", className="dvs-section-header__title"), html.Span(id="datahub-count", className="dvs-section-header__sub")]),
            html.Div(id="datahub-dataset-list"),
        ]
    )


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

    if isinstance(contents, str):
        contents = [contents]
        filename = [filename]

    store_data = store_data or {}
    dm = DataManager()
    loaded = []
    errors = []

    for content, fname in zip(contents, filename):
        try:
            _, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            df = load_file(decoded, fname)
            name = dm.add_dataset(fname, df, source=f"file:{fname}")
            loaded.append(f"{name}({len(df)}行)")
        except Exception as exc:
            errors.append(f"{fname}: {exc}")

    if loaded:
        store_data["active_dataset"] = dm.active_name
        store_data["datasets"] = dm.dataset_names
        msg = f"已加载 {len(loaded)} 个文件：{', '.join(loaded)}"
        if errors:
            msg += f"；另有 {len(errors)} 个失败"
        store_data["toast"] = {"message": msg, "type": "success"}
        return store_data, "/canvas"

    store_data["toast"] = {"message": f"全部加载失败：{'; '.join(errors)}", "type": "error"}
    return store_data, no_update


@callback(Output("modal-url", "is_open"), Input("card-url", "n_clicks"), State("modal-url", "is_open"), prevent_initial_call=True)
def toggle_modal_url(n, is_open):
    return (not is_open) if n else is_open


@callback(Output("modal-db", "is_open"), Input("card-db", "n_clicks"), State("modal-db", "is_open"), prevent_initial_call=True)
def toggle_modal_db(n, is_open):
    return (not is_open) if n else is_open


@callback(Output("modal-paste", "is_open"), Input("card-paste", "n_clicks"), State("modal-paste", "is_open"), prevent_initial_call=True)
def toggle_modal_paste(n, is_open):
    return (not is_open) if n else is_open


@callback(
    Output("datahub-db-dialect", "options"),
    Output("datahub-db-dialect", "value"),
    Output("datahub-db-port", "value"),
    Output("datahub-db-file-row", "style"),
    Output("datahub-db-host-row", "style"),
    Output("datahub-db-port-row", "style"),
    Output("datahub-db-name-row", "style"),
    Output("datahub-db-user-row", "style"),
    Output("datahub-db-password-row", "style"),
    Output("datahub-db-form-hint", "children"),
    Input("datahub-db-type", "value"),
)
def sync_db_form(db_type):
    config = DB_ENGINE_MAP.get(db_type or "postgresql", DB_ENGINE_MAP["postgresql"])
    is_file = config["mode"] == "file"
    visible = {"display": "grid"}
    hidden = {"display": "none"}
    hints = [
        html.Span(config["dialect"], className="dvs-db-form__hint-chip"),
        html.Span(config["label"], className="dvs-db-form__hint-chip"),
    ]
    if config["params_hint"]:
        hints.append(html.Span(config["params_hint"], className="dvs-db-form__hint-chip"))
    return (
        config["drivers"],
        config["dialect"],
        config["port"],
        visible if is_file else hidden,
        hidden if is_file else visible,
        hidden if is_file else visible,
        visible,
        hidden if is_file else visible,
        hidden if is_file else visible,
        hints,
    )


@callback(
    Output("app-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("datahub-url-btn", "n_clicks"),
    State("datahub-url-input", "value"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_url_import(n_clicks, url_value, store_data):
    if not url_value or not url_value.strip():
        return no_update, no_update

    url = url_value.strip()
    store_data = store_data or {}
    try:
        url_lower = url.lower().split("?")[0]
        if url_lower.endswith(".json"):
            df = pd.read_json(url)
        elif url_lower.endswith(".tsv"):
            df = pd.read_csv(url, sep="\t")
        elif url_lower.endswith((".xls", ".xlsx")):
            df = pd.read_excel(url)
        elif url_lower.endswith(".parquet"):
            df = pd.read_parquet(url)
        else:
            df = pd.read_csv(url)

        filename = url.split("/")[-1].split("?")[0] or "url_data"
        dm = DataManager()
        name = dm.add_dataset(filename, df, source=f"url:{url}")
        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {"message": f"已从 URL 加载 {name}（{len(df)} 行 × {len(df.columns)} 列）", "type": "success"}
        return store_data, "/canvas"
    except Exception as exc:
        store_data["toast"] = {"message": f"URL 导入失败：{exc}", "type": "error"}
        return store_data, no_update


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
    if not paste_text or not paste_text.strip():
        return no_update, no_update

    store_data = store_data or {}
    try:
        text = paste_text.strip()
        if sep == "auto":
            first_line = text.split("\n")[0]
            if "\t" in first_line:
                sep = "\t"
            elif "," in first_line:
                sep = ","
            elif ";" in first_line:
                sep = ";"
            elif "|" in first_line:
                sep = "|"
            else:
                sep = ","

        df = pd.read_csv(io.StringIO(text), sep=sep)
        if df.empty:
            store_data["toast"] = {"message": "粘贴的数据为空", "type": "error"}
            return store_data, no_update

        dm = DataManager()
        name = dm.add_dataset("粘贴数据", df, source="clipboard")
        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {"message": f"已从粘贴板加载 {name}（{len(df)} 行 × {len(df.columns)} 列）", "type": "success"}
        return store_data, "/canvas"
    except Exception as exc:
        store_data["toast"] = {"message": f"粘贴板导入失败：{exc}", "type": "error"}
        return store_data, no_update


@callback(
    Output("app-store", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("datahub-db-btn", "n_clicks"),
    State("datahub-db-type", "value"),
    State("datahub-db-dialect", "value"),
    State("datahub-db-host", "value"),
    State("datahub-db-port", "value"),
    State("datahub-db-username", "value"),
    State("datahub-db-password", "value"),
    State("datahub-db-name", "value"),
    State("datahub-db-file", "value"),
    State("datahub-db-options", "value"),
    State("datahub-db-query", "value"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def on_db_import(n_clicks, db_type, dialect, host, port, username, password, database, file_path, extra_params, query_str, store_data):
    if not query_str or not query_str.strip():
        return no_update, no_update

    store_data = store_data or {}
    try:
        conn_str = _build_db_connection_string(db_type, dialect, host, port, username, password, database, file_path, extra_params)
        df = load_from_database(conn_str, query_str.strip())
        parsed = urllib.parse.urlparse(conn_str)
        db_name = (parsed.path.lstrip("/") if parsed.path else "database").split(".")[0] or "db_data"

        dm = DataManager()
        name = dm.add_dataset(f"{db_name}_query", df, source=f"db:{conn_str}")
        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {"message": f"已从数据库加载查询结果（{len(df)} 行 × {len(df.columns)} 列）", "type": "success"}
        return store_data, "/canvas"
    except Exception as exc:
        store_data["toast"] = {"message": f"数据库加载失败：{exc}", "type": "error"}
        return store_data, no_update


@callback(
    Output("datahub-dataset-list", "children"),
    Output("datahub-count", "children"),
    Input("app-store", "data"),
)
def update_dataset_list(store_data):
    dm = DataManager()
    datasets = dm.list_datasets()
    active = (store_data or {}).get("active_dataset")

    if not datasets:
        return (
            html.Div(
                className="dvs-empty",
                children=[
                    html.Div("暂无数据", className="dvs-empty__text"),
                    html.Div("通过上方上传、URL、数据库或粘贴板导入数据", style={"color": "var(--text-muted)", "fontSize": "var(--text-sm)"}),
                ],
            ),
            "0 个数据集",
        )

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
                            html.Span(f"{format_number(meta.rows)} 行 × {meta.cols} 列 | {meta.memory_mb:.1f} MB", className="dvs-dataset-item__meta"),
                        ],
                    ),
                    html.Div(
                        className="dvs-dataset-item__actions",
                        children=[
                            html.Button("当前激活" if is_active else "设为激活", className="dvs-btn dvs-btn--sm" + (" dvs-btn--primary" if is_active else ""), id={"type": "activate-btn", "index": meta.name}, disabled=is_active),
                            html.Button("删除", className="dvs-btn dvs-btn--sm dvs-btn--ghost", id={"type": "delete-btn", "index": meta.name}),
                        ],
                    ),
                ],
            )
        )
    return html.Div(className="stagger-container", children=items), f"{len(datasets)} 个数据集"


@callback(
    Output("app-store", "data", allow_duplicate=True),
    Input({"type": "activate-btn", "index": ALL}, "n_clicks"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def activate_dataset(n_clicks_list, store_data):
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
        store_data["toast"] = {"message": f"已切换激活数据集：{name}", "type": "success"}
        return store_data
    return no_update


@callback(
    Output("app-store", "data", allow_duplicate=True),
    Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def delete_dataset(n_clicks_list, store_data):
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
    store_data["toast"] = {"message": f"已删除数据集：{name}", "type": "info"}
    return store_data
