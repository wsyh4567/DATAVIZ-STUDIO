# -*- coding: utf-8 -*-
"""
筛选条件构建器组件
可视化构建复杂的数据筛选条件，支持 AND/OR 逻辑组合
"""
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_filter_builder(filter_id="filter-builder", columns=None):
    """
    创建筛选条件构建器

    Args:
        filter_id: 组件ID前缀
        columns: 可用的列名列表

    Returns:
        Dash组件
    """
    if columns is None:
        columns = []

    return html.Div([
        # 筛选条件列表
        html.Div(id=f"{filter_id}-conditions-container", children=[
            html.P("暂无筛选条件", className="text-muted text-center",
                   id=f"{filter_id}-empty-message")
        ]),

        # 添加条件按钮
        html.Div([
            dbc.Button([
                html.I(className="bi bi-plus-circle me-2"),
                "添加条件"
            ], id=f"{filter_id}-add-btn", color="primary", size="sm", outline=True),

            dbc.Button([
                html.I(className="bi bi-braces me-2"),
                "添加条件组"
            ], id=f"{filter_id}-add-group-btn", color="info", size="sm", outline=True, className="ms-2"),
        ], className="mt-3"),

        # 存储筛选条件数据
        dcc.Store(id=f"{filter_id}-data", data={"conditions": [], "logic": "AND"}),

        # 存储可用列
        dcc.Store(id=f"{filter_id}-columns", data=columns),
    ], className="filter-builder")


def create_filter_condition(condition_id, columns, condition_data=None):
    """
    创建单个筛选条件卡片

    Args:
        condition_id: 条件唯一ID
        columns: 可用列名列表
        condition_data: 条件数据 {"column": "", "operator": "", "value": ""}

    Returns:
        条件卡片组件
    """
    if condition_data is None:
        condition_data = {"column": "", "operator": "==", "value": ""}

    # 操作符选项
    operators = [
        {"label": "等于 (=)", "value": "=="},
        {"label": "不等于 (≠)", "value": "!="},
        {"label": "大于 (>)", "value": ">"},
        {"label": "大于等于 (≥)", "value": ">="},
        {"label": "小于 (<)", "value": "<"},
        {"label": "小于等于 (≤)", "value": "<="},
        {"label": "包含", "value": "contains"},
        {"label": "不包含", "value": "not_contains"},
        {"label": "以...开头", "value": "startswith"},
        {"label": "以...结尾", "value": "endswith"},
        {"label": "在列表中", "value": "in"},
        {"label": "不在列表中", "value": "not_in"},
        {"label": "为空", "value": "isnull"},
        {"label": "不为空", "value": "notnull"},
    ]

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # 列选择
                dbc.Col([
                    dcc.Dropdown(
                        id={"type": "filter-column", "index": condition_id},
                        options=[{"label": col, "value": col} for col in columns],
                        value=condition_data.get("column"),
                        placeholder="选择列",
                        className="filter-dropdown"
                    )
                ], width=4),

                # 操作符选择
                dbc.Col([
                    dcc.Dropdown(
                        id={"type": "filter-operator", "index": condition_id},
                        options=operators,
                        value=condition_data.get("operator", "=="),
                        placeholder="操作符",
                        className="filter-dropdown"
                    )
                ], width=3),

                # 值输入
                dbc.Col([
                    dbc.Input(
                        id={"type": "filter-value", "index": condition_id},
                        type="text",
                        value=condition_data.get("value", ""),
                        placeholder="输入值",
                        className="filter-input"
                    )
                ], width=4),

                # 删除按钮
                dbc.Col([
                    dbc.Button(
                        html.I(className="bi bi-trash"),
                        id={"type": "filter-delete", "index": condition_id},
                        color="danger",
                        size="sm",
                        outline=True
                    )
                ], width=1),
            ], className="align-items-center"),
        ])
    ], className="mb-2 filter-condition-card")


def create_filter_group(group_id, columns, group_data=None):
    """
    创建筛选条件组（支持嵌套逻辑）

    Args:
        group_id: 组唯一ID
        columns: 可用列名列表
        group_data: 组数据 {"logic": "AND", "conditions": [...]}

    Returns:
        条件组组件
    """
    if group_data is None:
        group_data = {"logic": "AND", "conditions": []}

    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    dbc.RadioItems(
                        id={"type": "filter-group-logic", "index": group_id},
                        options=[
                            {"label": "满足所有条件 (AND)", "value": "AND"},
                            {"label": "满足任一条件 (OR)", "value": "OR"},
                        ],
                        value=group_data.get("logic", "AND"),
                        inline=True,
                        className="filter-logic-radio"
                    )
                ], width=10),
                dbc.Col([
                    dbc.Button(
                        html.I(className="bi bi-x-lg"),
                        id={"type": "filter-group-delete", "index": group_id},
                        color="danger",
                        size="sm",
                        outline=True
                    )
                ], width=2, className="text-end"),
            ])
        ]),
        dbc.CardBody([
            html.Div(
                id={"type": "filter-group-conditions", "index": group_id},
                children=[]
            ),
            dbc.Button([
                html.I(className="bi bi-plus me-2"),
                "添加条件"
            ], id={"type": "filter-group-add", "index": group_id},
            color="primary", size="sm", outline=True, className="mt-2")
        ])
    ], className="mb-3 filter-group-card", color="light", outline=True)


def create_filter_summary(filter_data):
    """
    创建筛选条件摘要显示

    Args:
        filter_data: 筛选条件数据

    Returns:
        摘要组件
    """
    if not filter_data or not filter_data.get("conditions"):
        return html.Div([
            html.I(className="bi bi-funnel me-2"),
            html.Span("无筛选条件", className="text-muted")
        ], className="filter-summary")

    conditions = filter_data.get("conditions", [])
    logic = filter_data.get("logic", "AND")

    summary_text = f"已设置 {len(conditions)} 个筛选条件 ({logic})"

    return html.Div([
        html.I(className="bi bi-funnel-fill me-2", style={"color": "#0d6efd"}),
        html.Span(summary_text, className="fw-bold"),
        html.Span(f" - 预计筛选后剩余行数将更新", className="text-muted ms-2")
    ], className="filter-summary")


def parse_filter_to_query(filter_data):
    """
    将筛选条件转换为 pandas query 字符串

    Args:
        filter_data: 筛选条件数据

    Returns:
        query字符串
    """
    if not filter_data or not filter_data.get("conditions"):
        return None

    conditions = filter_data.get("conditions", [])
    logic = filter_data.get("logic", "AND")

    query_parts = []

    for cond in conditions:
        column = cond.get("column")
        operator = cond.get("operator")
        value = cond.get("value")

        if not column or not operator:
            continue

        # 构建查询字符串
        if operator == "==":
            query_parts.append(f"`{column}` == '{value}'")
        elif operator == "!=":
            query_parts.append(f"`{column}` != '{value}'")
        elif operator == ">":
            query_parts.append(f"`{column}` > {value}")
        elif operator == ">=":
            query_parts.append(f"`{column}` >= {value}")
        elif operator == "<":
            query_parts.append(f"`{column}` < {value}")
        elif operator == "<=":
            query_parts.append(f"`{column}` <= {value}")
        elif operator == "contains":
            query_parts.append(f"`{column}`.str.contains('{value}', na=False)")
        elif operator == "not_contains":
            query_parts.append(f"~`{column}`.str.contains('{value}', na=False)")
        elif operator == "startswith":
            query_parts.append(f"`{column}`.str.startswith('{value}', na=False)")
        elif operator == "endswith":
            query_parts.append(f"`{column}`.str.endswith('{value}', na=False)")
        elif operator == "isnull":
            query_parts.append(f"`{column}`.isnull()")
        elif operator == "notnull":
            query_parts.append(f"`{column}`.notnull()")

    if not query_parts:
        return None

    # 组合条件
    logic_op = " & " if logic == "AND" else " | "
    return logic_op.join(f"({q})" for q in query_parts)
