# -*- coding: utf-8 -*-
"""
操作流水线视图组件
显示数据处理操作的历史记录，支持撤销/重做/重排序
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime


def create_pipeline_view(pipeline_id="operation-pipeline", operations=None):
    """
    创建操作流水线视图

    Args:
        pipeline_id: 组件ID前缀
        operations: 操作列表

    Returns:
        Dash组件
    """
    if operations is None:
        operations = []

    return html.Div([
        # 流水线标题和控制按钮
        html.Div([
            html.H5("操作流水线", className="mb-3"),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-arrow-counterclockwise me-1"),
                    "撤销"
                ], id=f"{pipeline_id}-undo-btn", size="sm", outline=True, disabled=len(operations) == 0),
                dbc.Button([
                    html.I(className="bi bi-arrow-clockwise me-1"),
                    "重做"
                ], id=f"{pipeline_id}-redo-btn", size="sm", outline=True, disabled=True),
                dbc.Button([
                    html.I(className="bi bi-trash me-1"),
                    "清空"
                ], id=f"{pipeline_id}-clear-btn", size="sm", outline=True, color="danger", disabled=len(operations) == 0),
            ], className="mb-3 w-100"),
        ]),

        # 操作列表
        html.Div(
            id=f"{pipeline_id}-list",
            children=_render_operations(operations) if operations else [
                html.Div([
                    html.I(className="bi bi-inbox", style={"fontSize": "2rem", "color": "#6c757d"}),
                    html.P("暂无操作", className="text-muted mt-2")
                ], className="text-center py-5")
            ],
            className="pipeline-operations"
        ),

        # 流水线统计
        html.Div([
            html.Hr(),
            html.Div([
                html.Small([
                    html.I(className="bi bi-list-check me-1"),
                    f"共 {len(operations)} 个操作"
                ], className="text-muted")
            ])
        ], className="pipeline-stats"),

        # 导出按钮
        html.Div([
            dbc.Button([
                html.I(className="bi bi-code-square me-2"),
                "导出为代码"
            ], id=f"{pipeline_id}-export-btn", color="success", size="sm", outline=True, className="w-100 mt-3", disabled=len(operations) == 0),
        ]),

        # 存储操作数据
        dcc.Store(id=f"{pipeline_id}-data", data=operations),
        dcc.Store(id=f"{pipeline_id}-undo-stack", data=[]),
        dcc.Store(id=f"{pipeline_id}-redo-stack", data=[]),

    ], className="pipeline-view")


def _render_operations(operations):
    """渲染操作列表"""
    if not operations:
        return []

    operation_cards = []
    for idx, op in enumerate(operations):
        operation_cards.append(create_operation_card(idx, op))

    return operation_cards


def create_operation_card(index, operation):
    """
    创建单个操作卡片

    Args:
        index: 操作索引
        operation: 操作数据字典
            {
                "type": "操作类型",
                "description": "操作描述",
                "params": {...},
                "timestamp": "时间戳",
                "enabled": True/False
            }

    Returns:
        操作卡片组件
    """
    op_type = operation.get("type", "未知操作")
    description = operation.get("description", "")
    enabled = operation.get("enabled", True)
    timestamp = operation.get("timestamp", "")

    # 操作类型图标映射
    icon_map = {
        "delete_columns": "bi-trash",
        "rename_column": "bi-pencil",
        "fill_missing": "bi-droplet-fill",
        "drop_missing": "bi-x-circle",
        "convert_type": "bi-arrow-left-right",
        "filter": "bi-funnel",
        "sort": "bi-sort-down",
        "deduplicate": "bi-layers",
        "strip_text": "bi-scissors",
        "case_convert": "bi-type",
        "find_replace": "bi-search",
        "binning": "bi-bar-chart-steps",
        "standardize": "bi-graph-up",
        "normalize": "bi-speedometer",
        "split_column": "bi-distribute-vertical",
        "merge_columns": "bi-union",
        "add_column": "bi-plus-square",
    }

    icon_class = icon_map.get(op_type, "bi-gear")

    # 操作类型颜色映射
    color_map = {
        "delete_columns": "danger",
        "drop_missing": "danger",
        "fill_missing": "primary",
        "filter": "info",
        "sort": "info",
        "deduplicate": "warning",
        "add_column": "success",
    }

    border_color = color_map.get(op_type, "secondary")

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # 操作序号和图标
                dbc.Col([
                    html.Div([
                        html.Span(f"#{index + 1}", className="operation-number"),
                        html.I(className=f"{icon_class} ms-2", style={"fontSize": "1.2rem"})
                    ])
                ], width=2, className="text-center"),

                # 操作描述
                dbc.Col([
                    html.Div([
                        html.Strong(op_type, className="d-block"),
                        html.Small(description, className="text-muted")
                    ])
                ], width=7),

                # 操作按钮
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button(
                            html.I(className="bi bi-eye" if enabled else "bi bi-eye-slash"),
                            id={"type": "operation-toggle", "index": index},
                            size="sm",
                            outline=True,
                            color="secondary",
                            title="启用/禁用"
                        ),
                        dbc.Button(
                            html.I(className="bi bi-x"),
                            id={"type": "operation-delete", "index": index},
                            size="sm",
                            outline=True,
                            color="danger",
                            title="删除"
                        ),
                    ], size="sm")
                ], width=3, className="text-end"),
            ], className="align-items-center"),

            # 时间戳
            html.Div([
                html.Small([
                    html.I(className="bi bi-clock me-1"),
                    timestamp or datetime.now().strftime("%H:%M:%S")
                ], className="text-muted")
            ], className="mt-2") if timestamp else None,
        ])
    ], className=f"mb-2 operation-card {'operation-disabled' if not enabled else ''}",
       color=border_color, outline=True)


def create_pipeline_summary(operations):
    """
    创建流水线摘要

    Args:
        operations: 操作列表

    Returns:
        摘要组件
    """
    if not operations:
        return html.Div([
            html.I(className="bi bi-inbox me-2"),
            html.Span("暂无操作", className="text-muted")
        ], className="pipeline-summary")

    enabled_count = sum(1 for op in operations if op.get("enabled", True))
    disabled_count = len(operations) - enabled_count

    return html.Div([
        html.Div([
            html.I(className="bi bi-list-check me-2", style={"color": "#198754"}),
            html.Span(f"共 {len(operations)} 个操作", className="fw-bold"),
        ]),
        html.Div([
            html.Small([
                html.Span(f"已启用: {enabled_count}", className="text-success me-3"),
                html.Span(f"已禁用: {disabled_count}", className="text-muted") if disabled_count > 0 else None
            ])
        ], className="mt-1")
    ], className="pipeline-summary")


def create_operation_template_selector():
    """
    创建操作模板选择器
    允许用户保存和加载常用的操作流水线模板

    Returns:
        模板选择器组件
    """
    return html.Div([
        html.H6("流水线模板", className="mb-2"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="pipeline-template-select",
                    options=[
                        {"label": "数据清洗标准流程", "value": "standard_cleaning"},
                        {"label": "文本数据预处理", "value": "text_preprocessing"},
                        {"label": "数值数据标准化", "value": "numeric_standardization"},
                        {"label": "自定义模板...", "value": "custom"},
                    ],
                    placeholder="选择模板",
                    className="mb-2"
                )
            ], width=8),
            dbc.Col([
                dbc.Button([
                    html.I(className="bi bi-save me-1"),
                    "保存"
                ], id="pipeline-template-save-btn", size="sm", outline=True, color="primary")
            ], width=4),
        ]),
    ], className="pipeline-template-selector mb-3")


def format_operation_for_display(operation_type, params):
    """
    格式化操作信息用于显示

    Args:
        operation_type: 操作类型
        params: 操作参数

    Returns:
        格式化的描述字符串
    """
    descriptions = {
        "delete_columns": lambda p: f"删除列: {', '.join(p.get('columns', []))}",
        "rename_column": lambda p: f"重命名: {p.get('old_name')} → {p.get('new_name')}",
        "fill_missing": lambda p: f"填充缺失值: {p.get('column')} 使用 {p.get('method')}",
        "drop_missing": lambda p: f"删除缺失行: {p.get('subset', '所有列')}",
        "convert_type": lambda p: f"类型转换: {p.get('column')} → {p.get('target_type')}",
        "filter": lambda p: f"筛选: {p.get('condition', '未知条件')}",
        "sort": lambda p: f"排序: {', '.join(p.get('columns', []))} ({p.get('ascending', 'asc')})",
        "deduplicate": lambda p: f"去重: 基于 {', '.join(p.get('subset', ['所有列']))}",
        "strip_text": lambda p: f"去空格: {p.get('column')}",
        "case_convert": lambda p: f"大小写转换: {p.get('column')} → {p.get('case_type')}",
        "find_replace": lambda p: f"查找替换: {p.get('column')} 中 '{p.get('find')}' → '{p.get('replace')}'",
        "binning": lambda p: f"分箱: {p.get('column')} ({p.get('bins')} 个箱)",
        "standardize": lambda p: f"标准化: {p.get('column')}",
        "normalize": lambda p: f"归一化: {p.get('column')}",
        "split_column": lambda p: f"拆分列: {p.get('column')} 按 '{p.get('delimiter')}'",
        "merge_columns": lambda p: f"合并列: {', '.join(p.get('columns', []))}",
        "add_column": lambda p: f"新增列: {p.get('column_name')}",
    }

    formatter = descriptions.get(operation_type)
    if formatter:
        try:
            return formatter(params)
        except Exception:
            return f"{operation_type}: {str(params)}"
    else:
        return f"{operation_type}: {str(params)}"
