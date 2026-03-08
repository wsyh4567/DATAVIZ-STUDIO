# -*- coding: utf-8 -*-
"""DataViz Studio — 主页 (Home)

全新的全屏无滚动主页一站式体验，左侧上传/选源，右侧特效展示区。
"""

from __future__ import annotations

import base64
from dash import html, dcc, Input, Output, State, callback, no_update, ctx
import dash_bootstrap_components as dbc
from core.data_manager import DataManager
from services.data_loader import load_file, load_sample_dataset, SAMPLE_DATASETS

def create_home_page() -> html.Div:
    """返回全屏无滚动的主页布局。"""
    dm = DataManager()
    has_data = dm.active_df is not None

    # 左侧控制面板 (上传 + 示例)
    left_panel = html.Div(
        className="d-flex flex-column h-100 justify-content-center px-4 px-xl-5",
        children=[
            html.H1("DataViz Studio", className="mb-3", style={"fontWeight": "800", "fontSize": "3.5rem", "background": "linear-gradient(45deg, var(--primary), var(--accent))", "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent"}),
            html.P("免费开源的零代码数据分析可视化平台", className="text-muted mb-5", style={"fontSize": "1.2rem"}),
            
            # 状态提示 (若已加载数据)
            html.Div(
                className="mb-4 p-3 rounded-4 shadow-sm",
                style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--success)", "display": "block" if has_data else "none"},
                children=[
                    html.I(className="bi bi-check-circle-fill me-2 text-success"),
                    html.Span(f"当前已加载数据集：{dm.active_name or '未命名'}", className="fw-bold me-3"),
                    dbc.Button("去图表工作室", href="/charts", color="primary", size="sm", outline=True, className="rounded-pill")
                ]
            ),
            
            # 上传区域
            html.Div(
                className="mb-4",
                children=[
                    dcc.Upload(
                        id="welcome-upload",
                        children=html.Div(
                            className="p-5 text-center upload-zone-hover",
                            style={"border": "2px dashed var(--border)", "borderRadius": "24px", "backgroundColor": "var(--bg-secondary)", "cursor": "pointer", "transition": "all 0.3s ease"},
                            children=[
                                html.I(className="bi bi-cloud-arrow-up", style={"fontSize": "4rem", "color": "var(--text-muted)"}),
                                html.H5("拖拽或点击上传本地数据", className="mt-3 mb-2 fw-bold"),
                                html.P("支持 CSV, Excel, JSON, Parquet, Feather 等格式 (最大 500MB)", className="text-muted small mb-0"),
                            ],
                        ),
                        multiple=False,
                    ),
                ],
            ),
            
            # 示例数据
            html.Div(
                children=[
                    html.H6("或者开始使用示例数据集：", className="text-muted mb-3 fs-6"),
                    html.Div(
                        className="d-flex flex-wrap gap-3",
                        children=[
                            dbc.Button([html.I(className="bi bi-flower1 me-2"), "鸢尾花"], id="sample-iris", color="light", className="rounded-pill px-4 py-2 border shadow-sm btn-hover"),
                            dbc.Button([html.I(className="bi bi-cup-hot me-2"), "餐饮小费"], id="sample-tips", color="light", className="rounded-pill px-4 py-2 border shadow-sm btn-hover"),
                            dbc.Button([html.I(className="bi bi-tsunami me-2"), "泰坦尼克"], id="sample-titanic", color="light", className="rounded-pill px-4 py-2 border shadow-sm btn-hover"),
                            dbc.Button([html.I(className="bi bi-globe me-2"), "国家经济"], id="sample-gapminder", color="light", className="rounded-pill px-4 py-2 border shadow-sm btn-hover"),
                            dbc.Button([html.I(className="bi bi-graph-up-arrow me-2"), "科技股票"], id="sample-stocks", color="light", className="rounded-pill px-4 py-2 border shadow-sm btn-hover"),
                        ]
                    )
                ]
            )
        ]
    )

    # 右侧展示区域（动态图表占位区）
    right_panel = html.Div(
        className="h-100 d-flex flex-column justify-content-center align-items-center p-5 position-relative overflow-hidden",
        style={"backgroundColor": "var(--bg-secondary)", "borderRadius": "40px 0 0 40px", "boxShadow": "-10px 0 30px rgba(0,0,0,0.03)"},
        children=[
            # 背景点缀
            html.Div(style={"position": "absolute", "top": "-10%", "right": "-10%", "width": "400px", "height": "400px", "background": "radial-gradient(circle, var(--primary) 0%, transparent 70%)", "opacity": "0.1", "borderRadius": "50%"}),
            html.Div(style={"position": "absolute", "bottom": "-10%", "left": "-10%", "width": "300px", "height": "300px", "background": "radial-gradient(circle, var(--accent) 0%, transparent 70%)", "opacity": "0.1", "borderRadius": "50%"}),
            
            html.Div(
                className="text-center z-index-1",
                style={"zIndex": "1"},
                children=[
                    html.I(className="bi bi-layout-wtf", style={"fontSize": "8rem", "color": "var(--primary)", "opacity": "0.9"}),
                    html.H2("重新定义数据分析", className="mt-4 mb-3", style={"fontWeight": "800"}),
                    html.P("释放数据潜能，连接无限可能", className="text-muted fs-5"),
                    
                    html.Div(
                        className="mt-5 d-flex gap-5 justify-content-center",
                        children=[
                            html.Div([
                                html.I(className="bi bi-magic fs-1 mb-3 d-block", style={"color": "#EC4899"}),
                                html.Span("数据工坊清洗", className="fw-bold d-block fs-6")
                            ], className="text-center transition-transform hover-scale"),
                            html.Div([
                                html.I(className="bi bi-pie-chart-fill fs-1 mb-3 d-block", style={"color": "#8B5CF6"}),
                                html.Span("高级图表探索", className="fw-bold d-block fs-6")
                            ], className="text-center transition-transform hover-scale"),
                            html.Div([
                                html.I(className="bi bi-robot fs-1 mb-3 d-block", style={"color": "#3B82F6"}),
                                html.Span("智能 AI 解读", className="fw-bold d-block fs-6")
                            ], className="text-center transition-transform hover-scale")
                        ]
                    )
                ]
            )
        ]
    )

    return html.Div(
        className="container-fluid p-0",
        style={"height": "calc(100vh - 56px)", "overflow": "hidden", "backgroundColor": "var(--bg-main)"},
        children=[
            dbc.Row(
                className="g-0 h-100",
                children=[
                    dbc.Col(left_panel, width=12, lg=5),
                    dbc.Col(right_panel, width=12, lg=7, className="d-none d-lg-block")
                ]
            )
        ]
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

    # 重点修复：拦截页面的组件动态初始加载幽灵触发
    if not ctx.triggered or ctx.triggered[0]['value'] is None:
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
