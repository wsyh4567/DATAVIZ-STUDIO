# -*- coding: utf-8 -*-
"""DataViz Studio — 数据中心页

数据源卡片 + 上传区域 + 已加载数据集列表。
"""

from __future__ import annotations

import base64

from dash import html, dcc, Input, Output, State, callback, no_update

from core.data_manager import DataManager
from services.data_loader import load_file
from utils.helpers import format_number, format_size


# ── 数据源定义 ─────────────────────────────────────────

DATA_SOURCES = [
    {"icon": "📄", "label": "CSV / TSV", "enabled": True},
    {"icon": "📊", "label": "Excel", "enabled": True},
    {"icon": "🔗", "label": "JSON", "enabled": True},
    {"icon": "🗄️", "label": "数据库", "enabled": False},
    {"icon": "🌐", "label": "URL", "enabled": False},
    {"icon": "📋", "label": "粘贴板", "enabled": False},
]


def create_data_hub_page() -> html.Div:
    """返回数据中心页面布局。"""

    # Source cards
    source_cards = []
    for src in DATA_SOURCES:
        cls = "dvs-source-card" if src["enabled"] else "dvs-source-card dvs-source-card--disabled"
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
            html.Div(className="dvs-source-cards", children=source_cards),

            # Upload zone
            dcc.Upload(
                id="datahub-upload",
                children=html.Div(
                    className="dvs-upload-zone",
                    children=[
                        html.Div("📂", className="dvs-upload-zone__icon"),
                        html.Div("拖拽文件到此处，或点击选择文件", className="dvs-upload-zone__title"),
                        html.Div("支持 CSV、Excel (.xlsx)、JSON 格式", className="dvs-upload-zone__hint"),
                    ],
                ),
                multiple=False,
                style={"marginBottom": "var(--sp-8)"},
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
    """数据中心文件上传。"""
    print(f"[DEBUG] on_datahub_upload called: filename={filename}")
    
    if contents is None or filename is None:
        print(f"[DEBUG] contents or filename is None, returning no_update")
        return no_update, no_update

    try:
        print(f"[DEBUG] Decoding file content...")
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        print(f"[DEBUG] Loading file...")
        dm = DataManager()
        df = load_file(decoded, filename)
        print(f"[DEBUG] File loaded: {len(df)} rows × {len(df.columns)} columns")
        
        name = dm.add_dataset(filename, df, source=f"file:{filename}")
        print(f"[DEBUG] Dataset added: {name}")

        store_data = store_data or {}
        store_data["active_dataset"] = name
        store_data["datasets"] = dm.dataset_names
        store_data["toast"] = {
            "message": f"✅ 已加载 {name}（{len(df)} 行 × {len(df.columns)} 列）",
            "type": "success",
        }
        print(f"[DEBUG] Redirecting to /canvas")
        return store_data, "/canvas"
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        store_data = store_data or {}
        store_data["toast"] = {"message": f"❌ 加载失败：{str(e)}", "type": "error"}
        return store_data, no_update


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
        cls = "dvs-dataset-item dvs-dataset-item--active" if is_active else "dvs-dataset-item"
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

    return html.Div(items), f"{len(datasets)} 个数据集"
