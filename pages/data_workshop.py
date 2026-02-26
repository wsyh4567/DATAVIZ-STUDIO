# -*- coding: utf-8 -*-
"""
数据工坊页面 - 数据清洗与转换
"""
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
from core.data_manager import DataManager
from services.code_generator import CodeGenerator

# 全局代码生成器实例
code_generator = CodeGenerator()

def layout():
    """数据工坊页面布局"""
    data_manager = DataManager()

    return html.Div([
        # 页面标题
        html.Div([
            html.H3("🧹 数据工坊", className="page-title"),
            html.P("数据清洗与转换", className="page-subtitle")
        ], className="page-header"),

        # 主内容区域
        html.Div([
            # 左侧操作菜单
            html.Div([
                html.H5("操作菜单", className="mb-3"),

                # 列操作
                dbc.Accordion([
                    dbc.AccordionItem([
                        dbc.Button("删除列", id="btn-delete-columns", color="danger", size="sm", className="w-100 mb-2"),
                        dbc.Button("重命名列", id="btn-rename-column", color="primary", size="sm", className="w-100 mb-2"),
                        dbc.Button("拆分列", id="btn-split-column", color="info", size="sm", className="w-100 mb-2"),
                        dbc.Button("合并列", id="btn-merge-columns", color="info", size="sm", className="w-100 mb-2"),
                    ], title="列操作"),

                    # 缺失值处理
                    dbc.AccordionItem([
                        dbc.Button("查看缺失值", id="btn-view-missing", color="warning", size="sm", className="w-100 mb-2"),
                        dbc.Button("填充缺失值", id="btn-fill-missing", color="primary", size="sm", className="w-100 mb-2"),
                        dbc.Button("删除缺失行", id="btn-drop-missing", color="danger", size="sm", className="w-100 mb-2"),
                    ], title="缺失值处理"),

                    # 数据类型转换
                    dbc.AccordionItem([
                        dbc.Button("转换类型", id="btn-convert-type", color="primary", size="sm", className="w-100 mb-2"),
                        dbc.Button("智能检测", id="btn-auto-detect", color="info", size="sm", className="w-100 mb-2"),
                    ], title="类型转换"),

                    # 筛选与排序
                    dbc.AccordionItem([
                        dbc.Button("添加筛选条件", id="btn-add-filter", color="primary", size="sm", className="w-100 mb-2"),
                        dbc.Button("多列排序", id="btn-sort-columns", color="info", size="sm", className="w-100 mb-2"),
                        dbc.Button("去重", id="btn-remove-duplicates", color="warning", size="sm", className="w-100 mb-2"),
                    ], title="筛选与排序"),

                    # 文本处理
                    dbc.AccordionItem([
                        dbc.Button("去空格", id="btn-strip-text", color="primary", size="sm", className="w-100 mb-2"),
                        dbc.Button("大小写转换", id="btn-case-convert", color="info", size="sm", className="w-100 mb-2"),
                        dbc.Button("查找替换", id="btn-find-replace", color="primary", size="sm", className="w-100 mb-2"),
                    ], title="文本处理"),

                    # 数值处理
                    dbc.AccordionItem([
                        dbc.Button("分箱", id="btn-binning", color="primary", size="sm", className="w-100 mb-2"),
                        dbc.Button("标准化", id="btn-standardize", color="info", size="sm", className="w-100 mb-2"),
                        dbc.Button("归一化", id="btn-normalize", color="info", size="sm", className="w-100 mb-2"),
                    ], title="数值处理"),

                    # 计算列
                    dbc.AccordionItem([
                        dbc.Button("新增计算列", id="btn-add-calc-column", color="success", size="sm", className="w-100 mb-2"),
                        dbc.Button("常用模板", id="btn-calc-templates", color="info", size="sm", className="w-100 mb-2"),
                    ], title="计算列"),
                ], start_collapsed=False, always_open=True),

            ], className="workshop-menu"),

            # 中间预览区域
            html.Div([
                html.Div([
                    html.H5("数据预览", className="mb-3"),
                    html.Div(id="workshop-preview-area", children=[
                        html.P("请选择左侧操作", className="text-muted text-center mt-5")
                    ])
                ], className="workshop-preview"),
            ], className="workshop-main"),

            # 右侧操作流水线
            html.Div([
                html.Div([
                    html.H5("操作流水线", className="mb-3"),
                    dbc.ButtonGroup([
                        dbc.Button("撤销", id="btn-undo", size="sm", outline=True),
                        dbc.Button("重做", id="btn-redo", size="sm", outline=True),
                        dbc.Button("清空", id="btn-clear-pipeline", size="sm", outline=True, color="danger"),
                    ], className="mb-3 w-100"),
                ]),

                html.Div(id="pipeline-list", children=[
                    html.P("暂无操作记录", className="text-muted text-center")
                ], className="pipeline-items"),

                html.Hr(),

                dbc.Button("导出为 Python 脚本", id="btn-export-code", color="primary", size="sm", className="w-100"),

            ], className="workshop-pipeline"),

        ], className="workshop-container"),

        # 模态框容器
        html.Div(id="workshop-modals"),

        # 存储操作历史
        dcc.Store(id="operation-history", data=[]),
        dcc.Store(id="operation-index", data=-1),

    ], className="page-container")


def create_pipeline_item(operation, index):
    """创建流水线操作项"""
    return html.Div([
        html.Div([
            html.Span(f"{index + 1}. ", className="pipeline-number"),
            html.Span(operation.get('description', '未知操作'), className="pipeline-desc"),
        ], className="pipeline-item-content"),
        html.Button("×", id={"type": "remove-operation", "index": index}, className="pipeline-remove-btn"),
    ], className="pipeline-item")


def update_pipeline_display(operations):
    """更新流水线显示"""
    if not operations:
        return html.P("暂无操作记录", className="text-muted text-center")

    return html.Div([
        create_pipeline_item(op, i) for i, op in enumerate(operations)
    ])


# 删除列模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-delete-columns", "n_clicks"),
    prevent_initial_call=True
)
def show_delete_columns_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("删除列"),
        dbc.ModalBody([
            html.Label("选择要删除的列："),
            dbc.Checklist(
                id="delete-columns-checklist",
                options=[{"label": col, "value": col} for col in columns],
                value=[],
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-delete", color="secondary", size="sm"),
            dbc.Button("确认删除", id="btn-confirm-delete", color="danger", size="sm"),
        ]),
    ], id="delete-columns-modal", is_open=True, size="lg")


# 重命名列模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-rename-column", "n_clicks"),
    prevent_initial_call=True
)
def show_rename_column_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("重命名列"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="rename-column-select",
                options=[{"label": col, "value": col} for col in columns],
                placeholder="选择要重命名的列"
            ),
            html.Br(),
            html.Label("新名称："),
            dbc.Input(id="rename-column-input", placeholder="输入新列名"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-rename", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-rename", color="primary", size="sm"),
        ]),
    ], id="rename-column-modal", is_open=True)


# 查看缺失值
@callback(
    Output("workshop-preview-area", "children", allow_duplicate=True),
    Input("btn-view-missing", "n_clicks"),
    prevent_initial_call=True
)
def view_missing_values(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("请先加载数据集", className="text-muted")

    # 计算缺失值
    missing_data = []
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        if missing_count > 0:
            missing_data.append({
                "column": col,
                "count": missing_count,
                "percentage": missing_pct
            })

    if not missing_data:
        return html.Div([
            html.H5("缺失值分析", className="mb-3"),
            dbc.Alert("✓ 数据集中没有缺失值", color="success")
        ])

    # 按缺失数量排序
    missing_data.sort(key=lambda x: x["count"], reverse=True)

    return html.Div([
        html.H5("缺失值分析", className="mb-3"),
        dbc.Alert(f"发现 {len(missing_data)} 列包含缺失值", color="warning"),

        html.Div([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("列名"),
                        html.Th("缺失数量"),
                        html.Th("缺失比例"),
                        html.Th("可视化"),
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(item["column"]),
                        html.Td(f"{item['count']:,}"),
                        html.Td(f"{item['percentage']:.2f}%"),
                        html.Td([
                            html.Div([
                                html.Div(style={
                                    "width": f"{item['percentage']:.1f}%",
                                    "height": "20px",
                                    "backgroundColor": "#ef4444",
                                    "borderRadius": "4px"
                                })
                            ], style={"width": "100%", "backgroundColor": "#f1f5f9", "borderRadius": "4px"})
                        ]),
                    ]) for item in missing_data
                ])
            ], bordered=True, hover=True, striped=True)
        ])
    ])


# 填充缺失值模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-fill-missing", "n_clicks"),
    prevent_initial_call=True
)
def show_fill_missing_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    # 找出有缺失值的列
    columns_with_missing = [col for col in df.columns if df[col].isnull().sum() > 0]

    if not columns_with_missing:
        return dbc.Modal([
            dbc.ModalHeader("提示"),
            dbc.ModalBody("数据集中没有缺失值"),
        ], is_open=True)

    return dbc.Modal([
        dbc.ModalHeader("填充缺失值"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="fill-missing-column-select",
                options=[{"label": col, "value": col} for col in columns_with_missing],
                placeholder="选择要填充的列"
            ),
            html.Br(),
            html.Label("填充策略："),
            dcc.Dropdown(
                id="fill-missing-strategy",
                options=[
                    {"label": "均值（仅数值列）", "value": "mean"},
                    {"label": "中位数（仅数值列）", "value": "median"},
                    {"label": "众数", "value": "mode"},
                    {"label": "固定值", "value": "constant"},
                    {"label": "前向填充", "value": "ffill"},
                    {"label": "后向填充", "value": "bfill"},
                ],
                placeholder="选择填充策略"
            ),
            html.Br(),
            html.Div(id="fill-constant-input-container"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-fill", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-fill", color="primary", size="sm"),
        ]),
    ], id="fill-missing-modal", is_open=True, size="lg")


# 显示固定值输入框
@callback(
    Output("fill-constant-input-container", "children"),
    Input("fill-missing-strategy", "value")
)
def show_constant_input(strategy):
    if strategy == "constant":
        return html.Div([
            html.Label("填充值："),
            dbc.Input(id="fill-constant-value", placeholder="输入填充值", type="text")
        ])
    return None


# 类型转换模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-convert-type", "n_clicks"),
    prevent_initial_call=True
)
def show_convert_type_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("数据类型转换"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="convert-type-column-select",
                options=[{"label": f"{col} ({df[col].dtype})", "value": col} for col in columns],
                placeholder="选择要转换的列"
            ),
            html.Br(),
            html.Label("目标类型："),
            dcc.Dropdown(
                id="convert-target-type",
                options=[
                    {"label": "整数 (int)", "value": "int"},
                    {"label": "浮点数 (float)", "value": "float"},
                    {"label": "字符串 (str)", "value": "str"},
                    {"label": "日期时间 (datetime)", "value": "datetime"},
                    {"label": "布尔值 (bool)", "value": "bool"},
                    {"label": "分类 (category)", "value": "category"},
                ],
                placeholder="选择目标类型"
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-convert", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-convert", color="primary", size="sm"),
        ]),
    ], id="convert-type-modal", is_open=True)


# 确认删除列
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "children", allow_duplicate=True)],
    Input("btn-confirm-delete", "n_clicks"),
    [State("delete-columns-select", "value"),
     State("operation-history", "children")],
    prevent_initial_call=True
)
def confirm_delete_columns(n_clicks, columns, current_history):
    if not n_clicks or not columns:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        # 删除列
        df_new = df.drop(columns=columns)
        data_manager.active_df = df_new

        # 添加到操作历史
        new_history = add_operation_to_history(
            current_history,
            f"删除列：{', '.join(columns)}",
            f"{len(df.columns)} → {len(df_new.columns)} 列"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 列删除完成"),
                html.Br(),
                f"已删除 {len(columns)} 列：{', '.join(columns)}"
            ], color="success"),
            html.H5("更新后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"删除列失败：{str(e)}", className="text-danger"), None, current_history


# 确认重命名列
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "children", allow_duplicate=True)],
    Input("btn-confirm-rename", "n_clicks"),
    [State("rename-column-select", "value"),
     State("rename-column-input", "value"),
     State("operation-history", "children")],
    prevent_initial_call=True
)
def confirm_rename_column(n_clicks, old_name, new_name, current_history):
    if not n_clicks or not old_name or not new_name:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        # 重命名列
        df_new = df.rename(columns={old_name: new_name})
        data_manager.active_df = df_new

        # 添加到操作历史
        new_history = add_operation_to_history(
            current_history,
            f"重命名列：{old_name} → {new_name}",
            "列名已更新"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 列重命名完成"),
                html.Br(),
                f"'{old_name}' → '{new_name}'"
            ], color="success"),
            html.H5("更新后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"重命名列失败：{str(e)}", className="text-danger"), None, current_history


# 确认填充缺失值
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "children", allow_duplicate=True)],
    Input("btn-confirm-fill", "n_clicks"),
    [State("fill-columns-select", "value"),
     State("fill-method-select", "value"),
     State("fill-value-input", "value"),
     State("operation-history", "children")],
    prevent_initial_call=True
)
def confirm_fill_missing(n_clicks, columns, method, custom_value, current_history):
    if not n_clicks or not columns or not method:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        df_new = df.copy()
        filled_count = 0

        for col in columns:
            missing_before = df_new[col].isnull().sum()

            if method == "mean":
                df_new[col].fillna(df_new[col].mean(), inplace=True)
            elif method == "median":
                df_new[col].fillna(df_new[col].median(), inplace=True)
            elif method == "mode":
                mode_val = df_new[col].mode()
                if len(mode_val) > 0:
                    df_new[col].fillna(mode_val[0], inplace=True)
            elif method == "forward":
                df_new[col].fillna(method='ffill', inplace=True)
            elif method == "backward":
                df_new[col].fillna(method='bfill', inplace=True)
            elif method == "custom" and custom_value:
                df_new[col].fillna(custom_value, inplace=True)

            filled_count += missing_before - df_new[col].isnull().sum()

        data_manager.active_df = df_new

        # 添加到操作历史
        method_names = {
            "mean": "均值", "median": "中位数", "mode": "众数",
            "forward": "前向填充", "backward": "后向填充", "custom": "自定义值"
        }
        new_history = add_operation_to_history(
            current_history,
            f"填充缺失值：{method_names.get(method, method)}",
            f"填充了 {filled_count} 个缺失值"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 缺失值填充完成"),
                html.Br(),
                f"填充方法：{method_names.get(method, method)}",
                html.Br(),
                f"填充了 {filled_count} 个缺失值"
            ], color="success"),
            html.H5("更新后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"填充缺失值失败：{str(e)}", className="text-danger"), None, current_history


# 确认类型转换
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "children", allow_duplicate=True)],
    Input("btn-confirm-convert", "n_clicks"),
    [State("convert-column-select", "value"),
     State("convert-type-select", "value"),
     State("operation-history", "children")],
    prevent_initial_call=True
)
def confirm_convert_type(n_clicks, column, target_type, current_history):
    if not n_clicks or not column or not target_type:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        df_new = df.copy()
        old_type = str(df_new[column].dtype)

        # 类型转换
        if target_type == "int":
            df_new[column] = pd.to_numeric(df_new[column], errors='coerce').astype('Int64')
        elif target_type == "float":
            df_new[column] = pd.to_numeric(df_new[column], errors='coerce')
        elif target_type == "str":
            df_new[column] = df_new[column].astype(str)
        elif target_type == "datetime":
            df_new[column] = pd.to_datetime(df_new[column], errors='coerce')
        elif target_type == "bool":
            df_new[column] = df_new[column].astype(bool)

        data_manager.active_df = df_new

        # 添加到操作历史
        new_history = add_operation_to_history(
            current_history,
            f"类型转换：{column}",
            f"{old_type} → {target_type}"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 类型转换完成"),
                html.Br(),
                f"列：{column}",
                html.Br(),
                f"{old_type} → {target_type}"
            ], color="success"),
            html.H5("更新后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"类型转换失败：{str(e)}", className="text-danger"), None, current_history


# 关闭基础操作模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    [Input("btn-cancel-delete", "n_clicks"),
     Input("btn-cancel-rename", "n_clicks"),
     Input("btn-cancel-fill", "n_clicks"),
     Input("btn-cancel-convert", "n_clicks"),
     Input("btn-cancel-filter", "n_clicks"),
     Input("btn-cancel-sort", "n_clicks"),
     Input("btn-cancel-dedup", "n_clicks")],
    prevent_initial_call=True
)
def close_basic_modals(*args):
    return None


# 添加筛选条件模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-add-filter", "n_clicks"),
    prevent_initial_call=True
)
def show_filter_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("添加筛选条件"),
        dbc.ModalBody([
            html.Div([
                html.Label("选择列："),
                dcc.Dropdown(
                    id="filter-column-select",
                    options=[{"label": col, "value": col} for col in columns],
                    placeholder="选择要筛选的列"
                ),
                html.Br(),
                html.Label("操作符："),
                dcc.Dropdown(
                    id="filter-operator-select",
                    options=[
                        {"label": "等于 (=)", "value": "eq"},
                        {"label": "不等于 (≠)", "value": "ne"},
                        {"label": "大于 (>)", "value": "gt"},
                        {"label": "大于等于 (≥)", "value": "ge"},
                        {"label": "小于 (<)", "value": "lt"},
                        {"label": "小于等于 (≤)", "value": "le"},
                        {"label": "包含", "value": "contains"},
                        {"label": "不包含", "value": "not_contains"},
                        {"label": "以...开头", "value": "startswith"},
                        {"label": "以...结尾", "value": "endswith"},
                    ],
                    placeholder="选择操作符"
                ),
                html.Br(),
                html.Label("值："),
                dbc.Input(id="filter-value-input", placeholder="输入筛选值", type="text"),
                html.Br(),
                html.Div(id="filter-preview-info", className="text-muted small"),
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-filter", color="secondary", size="sm"),
            dbc.Button("应用筛选", id="btn-confirm-filter", color="primary", size="sm"),
        ]),
    ], id="filter-modal", is_open=True, size="lg")


# 多列排序模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-sort-columns", "n_clicks"),
    prevent_initial_call=True
)
def show_sort_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("多列排序"),
        dbc.ModalBody([
            html.Label("选择排序列（按优先级顺序）："),
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id={"type": "sort-column", "index": 0},
                        options=[{"label": col, "value": col} for col in columns],
                        placeholder="第一排序列",
                        className="mb-2"
                    ),
                    dcc.Dropdown(
                        id={"type": "sort-order", "index": 0},
                        options=[
                            {"label": "升序 ↑", "value": "asc"},
                            {"label": "降序 ↓", "value": "desc"},
                        ],
                        value="asc",
                        className="mb-3"
                    ),
                ]),
                html.Div([
                    dcc.Dropdown(
                        id={"type": "sort-column", "index": 1},
                        options=[{"label": col, "value": col} for col in columns],
                        placeholder="第二排序列（可选）",
                        className="mb-2"
                    ),
                    dcc.Dropdown(
                        id={"type": "sort-order", "index": 1},
                        options=[
                            {"label": "升序 ↑", "value": "asc"},
                            {"label": "降序 ↓", "value": "desc"},
                        ],
                        value="asc",
                        className="mb-3"
                    ),
                ]),
                html.Div([
                    dcc.Dropdown(
                        id={"type": "sort-column", "index": 2},
                        options=[{"label": col, "value": col} for col in columns],
                        placeholder="第三排序列（可选）",
                        className="mb-2"
                    ),
                    dcc.Dropdown(
                        id={"type": "sort-order", "index": 2},
                        options=[
                            {"label": "升序 ↑", "value": "asc"},
                            {"label": "降序 ↓", "value": "desc"},
                        ],
                        value="asc",
                    ),
                ]),
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-sort", color="secondary", size="sm"),
            dbc.Button("应用排序", id="btn-confirm-sort", color="primary", size="sm"),
        ]),
    ], id="sort-modal", is_open=True, size="lg")


# 去重模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-remove-duplicates", "n_clicks"),
    prevent_initial_call=True
)
def show_dedup_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()
    total_rows = len(df)
    duplicate_rows = df.duplicated().sum()

    return dbc.Modal([
        dbc.ModalHeader("去重"),
        dbc.ModalBody([
            dbc.Alert([
                html.Strong(f"当前数据集：{total_rows:,} 行"),
                html.Br(),
                f"重复行数：{duplicate_rows:,} ({duplicate_rows/total_rows*100:.2f}%)" if duplicate_rows > 0 else "没有发现重复行"
            ], color="info" if duplicate_rows > 0 else "success"),
            html.Br(),
            html.Label("判断依据列（留空则使用所有列）："),
            dcc.Dropdown(
                id="dedup-columns-select",
                options=[{"label": col, "value": col} for col in columns],
                placeholder="选择用于判断重复的列",
                multi=True
            ),
            html.Br(),
            html.Label("保留策略："),
            dcc.Dropdown(
                id="dedup-keep-strategy",
                options=[
                    {"label": "保留第一个", "value": "first"},
                    {"label": "保留最后一个", "value": "last"},
                    {"label": "删除所有重复", "value": False},
                ],
                value="first",
                placeholder="选择保留策略"
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-dedup", color="secondary", size="sm"),
            dbc.Button("确认去重", id="btn-confirm-dedup", color="warning", size="sm"),
        ]),
    ], id="dedup-modal", is_open=True, size="lg")


# 确认筛选
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "children", allow_duplicate=True)],
    Input("btn-confirm-filter", "n_clicks"),
    [State("filter-column-select", "value"),
     State("filter-operator-select", "value"),
     State("filter-value-input", "value"),
     State("operation-history", "children")],
    prevent_initial_call=True
)
def confirm_filter(n_clicks, column, operator, value, current_history):
    if not n_clicks or not column or not operator or value is None:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        # 应用筛选
        original_count = len(df)

        if operator == "eq":
            mask = df[column] == value
        elif operator == "ne":
            mask = df[column] != value
        elif operator == "gt":
            mask = df[column] > float(value)
        elif operator == "ge":
            mask = df[column] >= float(value)
        elif operator == "lt":
            mask = df[column] < float(value)
        elif operator == "le":
            mask = df[column] <= float(value)
        elif operator == "contains":
            mask = df[column].astype(str).str.contains(str(value), na=False)
        elif operator == "not_contains":
            mask = ~df[column].astype(str).str.contains(str(value), na=False)
        elif operator == "startswith":
            mask = df[column].astype(str).str.startswith(str(value), na=False)
        elif operator == "endswith":
            mask = df[column].astype(str).str.endswith(str(value), na=False)
        else:
            return html.P("不支持的操作符", className="text-danger"), None, current_history

        filtered_df = df[mask]
        filtered_count = len(filtered_df)

        # 更新数据管理器
        data_manager.active_df = filtered_df

        # 添加到操作历史
        operator_labels = {
            "eq": "=", "ne": "≠", "gt": ">", "ge": "≥", "lt": "<", "le": "≤",
            "contains": "包含", "not_contains": "不包含",
            "startswith": "开头", "endswith": "结尾"
        }
        op_label = operator_labels.get(operator, operator)
        new_history = add_operation_to_history(
            current_history,
            f"筛选数据：{column} {op_label} {value}",
            f"{original_count:,} → {filtered_count:,} 行"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 筛选完成"),
                html.Br(),
                f"原始行数：{original_count:,}",
                html.Br(),
                f"筛选后：{filtered_count:,} 行",
                html.Br(),
                f"保留比例：{filtered_count/original_count*100:.2f}%"
            ], color="success"),
            html.H5("筛选后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                filtered_df.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"筛选失败：{str(e)}", className="text-danger"), None, current_history


# 确认排序
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "children", allow_duplicate=True)],
    Input("btn-confirm-sort", "n_clicks"),
    [State({"type": "sort-column", "index": ALL}, "value"),
     State({"type": "sort-order", "index": ALL}, "value"),
     State("operation-history", "children")],
    prevent_initial_call=True
)
def confirm_sort(n_clicks, columns, orders, current_history):
    if not n_clicks:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        # 过滤出有效的排序列
        sort_columns = []
        sort_orders = []
        for col, order in zip(columns, orders):
            if col:
                sort_columns.append(col)
                sort_orders.append(order == "asc")

        if not sort_columns:
            return html.P("请至少选择一个排序列", className="text-warning"), None, current_history

        # 应用排序
        sorted_df = df.sort_values(by=sort_columns, ascending=sort_orders)

        # 更新数据管理器
        data_manager.active_df = sorted_df

        # 添加到操作历史
        sort_desc = ', '.join([f"{col}({'升序' if asc else '降序'})" for col, asc in zip(sort_columns, sort_orders)])
        new_history = add_operation_to_history(
            current_history,
            f"排序数据：{sort_desc}",
            f"{len(sorted_df):,} 行"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 排序完成"),
                html.Br(),
                f"排序列：{', '.join(sort_columns)}",
                html.Br(),
                f"排序方式：{', '.join(['升序' if asc else '降序' for asc in sort_orders])}"
            ], color="success"),
            html.H5("排序后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                sorted_df.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"排序失败：{str(e)}", className="text-danger"), None, current_history


# 确认去重
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "children", allow_duplicate=True)],
    Input("btn-confirm-dedup", "n_clicks"),
    [State("dedup-columns-select", "value"),
     State("dedup-keep-strategy", "value"),
     State("operation-history", "children")],
    prevent_initial_call=True
)
def confirm_dedup(n_clicks, columns, keep, current_history):
    if not n_clicks:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        original_count = len(df)

        # 应用去重
        if columns:
            deduped_df = df.drop_duplicates(subset=columns, keep=keep)
        else:
            deduped_df = df.drop_duplicates(keep=keep)

        deduped_count = len(deduped_df)
        removed_count = original_count - deduped_count

        # 更新数据管理器
        data_manager.active_df = deduped_df

        # 添加到操作历史
        col_desc = f"基于 {', '.join(columns)}" if columns else "所有列"
        new_history = add_operation_to_history(
            current_history,
            f"去重：{col_desc}",
            f"{original_count:,} → {deduped_count:,} 行 (删除 {removed_count:,})"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 去重完成"),
                html.Br(),
                f"原始行数：{original_count:,}",
                html.Br(),
                f"去重后：{deduped_count:,} 行",
                html.Br(),
                f"删除了 {removed_count:,} 行重复数据 ({removed_count/original_count*100:.2f}%)"
            ], color="success"),
            html.H5("去重后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                deduped_df.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"去重失败：{str(e)}", className="text-danger"), None, current_history


# 更新流水线显示
@callback(
    Output("pipeline-list", "children"),
    Input("operation-history", "data")
)
def update_pipeline(operations):
    """更新流水线显示"""
    return update_pipeline_display(operations or [])


# 导出代码
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-export-code", "n_clicks"),
    State("operation-history", "data"),
    prevent_initial_call=True
)
def export_code(n_clicks, operations):
    """导出 Python 代码"""
    if not n_clicks:
        return None

    # 清空并重建代码生成器
    code_generator.clear_operations()
    for op in (operations or []):
        code_generator.add_operation(op)

    # 生成代码
    code = code_generator.generate_code()

    # 创建代码显示模态框
    modal = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("导出 Python 代码")),
        dbc.ModalBody([
            html.Pre(code, style={
                "backgroundColor": "#f5f5f5",
                "padding": "15px",
                "borderRadius": "5px",
                "maxHeight": "500px",
                "overflow": "auto",
                "fontSize": "12px"
            }),
            dbc.Button("复制代码", id="btn-copy-code", color="primary", size="sm", className="mt-2"),
            dcc.Clipboard(
                target_id="btn-copy-code",
                content=code,
                style={"display": "inline-block", "marginLeft": "10px"}
            )
        ]),
        dbc.ModalFooter(
            dbc.Button("关闭", id="btn-close-export", color="secondary", size="sm")
        ),
    ], is_open=True, size="lg")

    return modal


# 关闭导出模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-close-export", "n_clicks"),
    prevent_initial_call=True
)
def close_export_modal(n_clicks):
    return None


# 清空流水线
@callback(
    Output("operation-history", "data", allow_duplicate=True),
    Input("btn-clear-pipeline", "n_clicks"),
    prevent_initial_call=True
)
def clear_pipeline(n_clicks):
    """清空操作流水线"""
    if not n_clicks:
        return []
    code_generator.clear_operations()
    return []


# 撤销操作
@callback(
    Output("operation-history", "data", allow_duplicate=True),
    Output("operation-index", "data", allow_duplicate=True),
    Input("btn-undo", "n_clicks"),
    State("operation-history", "data"),
    State("operation-index", "data"),
    prevent_initial_call=True
)
def undo_operation(n_clicks, operations, current_index):
    """撤销操作"""
    if not n_clicks or not operations:
        return operations or [], current_index or -1

    # 如果当前索引是-1，表示在最新状态，设置为倒数第二个
    if current_index == -1:
        new_index = len(operations) - 2
    else:
        new_index = max(-1, current_index - 1)

    return operations, new_index


# 重做操作
@callback(
    Output("operation-history", "data", allow_duplicate=True),
    Output("operation-index", "data", allow_duplicate=True),
    Input("btn-redo", "n_clicks"),
    State("operation-history", "data"),
    State("operation-index", "data"),
    prevent_initial_call=True
)
def redo_operation(n_clicks, operations, current_index):
    """重做操作"""
    if not n_clicks or not operations:
        return operations or [], current_index or -1

    # 如果已经在最新状态，不能重做
    if current_index >= len(operations) - 1:
        return operations, current_index

    new_index = min(len(operations) - 1, current_index + 1)
    return operations, new_index


# 移除单个操作
@callback(
    Output("operation-history", "data", allow_duplicate=True),
    Input({"type": "remove-operation", "index": ALL}, "n_clicks"),
    State("operation-history", "data"),
    prevent_initial_call=True
)
def remove_operation(n_clicks_list, operations):
    """移除单个操作"""
    if not any(n_clicks_list) or not operations:
        return operations or []

    # 找到被点击的按钮索引
    clicked_index = None
    for i, n_clicks in enumerate(n_clicks_list):
        if n_clicks:
            clicked_index = i
            break

    if clicked_index is not None and 0 <= clicked_index < len(operations):
        operations = operations.copy()
        operations.pop(clicked_index)

    return operations


# 辅助函数：添加操作到历史
def add_operation_to_history(current_history, description, details):
    """添加操作到历史记录"""
    if current_history is None:
        current_history = []

    operation = {
        'description': description,
        'details': details,
        'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    new_history = current_history.copy() if isinstance(current_history, list) else []
    new_history.append(operation)

    return new_history


# 拆分列模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-split-column", "n_clicks"),
    prevent_initial_call=True
)
def show_split_column_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("拆分列"),
        dbc.ModalBody([
            html.Label("选择要拆分的列："),
            dcc.Dropdown(
                id="split-column-select",
                options=[{"label": col, "value": col} for col in columns],
                placeholder="选择列"
            ),
            html.Br(),
            html.Label("分隔符："),
            dbc.Input(id="split-delimiter-input", placeholder="例如: , 或 - 或空格", value=","),
            html.Br(),
            html.Label("新列名（可选，用逗号分隔）："),
            dbc.Input(id="split-new-names-input", placeholder="例如: 列1,列2,列3"),
            html.Br(),
            html.Div(id="split-preview-info", className="text-muted small"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-split", color="secondary", size="sm"),
            dbc.Button("确认拆分", id="btn-confirm-split", color="primary", size="sm"),
        ]),
    ], id="split-column-modal", is_open=True, size="lg")


# 确认拆分列
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-split", "n_clicks"),
    [State("split-column-select", "value"),
     State("split-delimiter-input", "value"),
     State("split-new-names-input", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_split_column(n_clicks, column, delimiter, new_names, current_history):
    if not n_clicks or not column or not delimiter:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        from services.data_cleaner import DataCleaner

        # 处理新列名
        new_columns = None
        if new_names and new_names.strip():
            new_columns = [name.strip() for name in new_names.split(',')]

        # 拆分列
        df_new = DataCleaner.split_column(df, column, delimiter, new_columns)
        data_manager.active_df = df_new

        # 添加到操作历史
        new_history = add_operation_to_history(
            current_history,
            f"拆分列：{column}",
            f"使用分隔符 '{delimiter}'"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 列拆分完成"),
                html.Br(),
                f"原列：{column}",
                html.Br(),
                f"分隔符：'{delimiter}'"
            ], color="success"),
            html.H5("拆分后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"拆分列失败：{str(e)}", className="text-danger"), None, current_history


# 合并列模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-merge-columns", "n_clicks"),
    prevent_initial_call=True
)
def show_merge_columns_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("合并列"),
        dbc.ModalBody([
            html.Label("选择要合并的列："),
            dcc.Dropdown(
                id="merge-columns-select",
                options=[{"label": col, "value": col} for col in columns],
                placeholder="选择多个列",
                multi=True
            ),
            html.Br(),
            html.Label("新列名："),
            dbc.Input(id="merge-new-name-input", placeholder="输入新列名"),
            html.Br(),
            html.Label("分隔符："),
            dbc.Input(id="merge-delimiter-input", placeholder="例如: 空格 或 - 或 ,", value=" "),
            html.Br(),
            html.Div(id="merge-preview-info", className="text-muted small"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-merge", color="secondary", size="sm"),
            dbc.Button("确认合并", id="btn-confirm-merge", color="primary", size="sm"),
        ]),
    ], id="merge-columns-modal", is_open=True, size="lg")


# 确认合并列
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-merge", "n_clicks"),
    [State("merge-columns-select", "value"),
     State("merge-new-name-input", "value"),
     State("merge-delimiter-input", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_merge_columns(n_clicks, columns, new_name, delimiter, current_history):
    if not n_clicks or not columns or not new_name:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        from services.data_cleaner import DataCleaner

        # 合并列
        df_new = DataCleaner.merge_columns(df, columns, new_name, delimiter)
        data_manager.active_df = df_new

        # 添加到操作历史
        new_history = add_operation_to_history(
            current_history,
            f"合并列：{', '.join(columns)} → {new_name}",
            f"使用分隔符 '{delimiter}'"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 列合并完成"),
                html.Br(),
                f"合并列：{', '.join(columns)}",
                html.Br(),
                f"新列名：{new_name}",
                html.Br(),
                f"分隔符：'{delimiter}'"
            ], color="success"),
            html.H5("合并后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"合并列失败：{str(e)}", className="text-danger"), None, current_history


# 更新关闭模态框回调（添加新的取消按钮）
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    [Input("btn-cancel-split", "n_clicks"),
     Input("btn-cancel-merge", "n_clicks"),
     Input("btn-cancel-calc", "n_clicks")],
    prevent_initial_call=True
)
def close_split_merge_modals(*args):
    return None


# 新增计算列模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-add-calc-column", "n_clicks"),
    prevent_initial_call=True
)
def show_calc_column_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("新增计算列"),
        dbc.ModalBody([
            html.Label("新列名："),
            dbc.Input(id="calc-column-name-input", placeholder="输入新列名"),
            html.Br(),
            html.Label("计算表达式："),
            dbc.Textarea(
                id="calc-expression-input",
                placeholder="例如: column1 + column2\n或: column1 * 2\n或: column1 / column2",
                style={"height": "100px"}
            ),
            html.Br(),
            dbc.Alert([
                html.Strong("提示："),
                html.Br(),
                "• 直接使用列名进行计算",
                html.Br(),
                "• 支持 +, -, *, / 等运算符",
                html.Br(),
                f"• 可用列名：{', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}"
            ], color="info", className="small"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-calc", color="secondary", size="sm"),
            dbc.Button("确认添加", id="btn-confirm-calc", color="success", size="sm"),
        ]),
    ], id="calc-column-modal", is_open=True, size="lg")


# 确认添加计算列
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-calc", "n_clicks"),
    [State("calc-column-name-input", "value"),
     State("calc-expression-input", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_calc_column(n_clicks, new_column, expression, current_history):
    if not n_clicks or not new_column or not expression:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        from services.data_cleaner import DataCleaner

        # 添加计算列
        df_new = DataCleaner.add_calculated_column(df, new_column, expression)
        data_manager.active_df = df_new

        # 添加到操作历史
        new_history = add_operation_to_history(
            current_history,
            f"新增计算列：{new_column}",
            f"表达式：{expression}"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 计算列添加完成"),
                html.Br(),
                f"新列名：{new_column}",
                html.Br(),
                f"表达式：{expression}"
            ], color="success"),
            html.H5("更新后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"添加计算列失败：{str(e)}", className="text-danger"), None, current_history


# 常用模板模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-calc-templates", "n_clicks"),
    prevent_initial_call=True
)
def show_calc_templates_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    # 获取数值列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    templates = [
        {"name": "百分比变化", "expr": "(new_value - old_value) / old_value * 100", "desc": "计算两列之间的百分比变化"},
        {"name": "累计求和", "expr": "column.cumsum()", "desc": "计算累计和"},
        {"name": "移动平均", "expr": "column.rolling(window=3).mean()", "desc": "计算3期移动平均"},
        {"name": "标准化", "expr": "(column - column.mean()) / column.std()", "desc": "Z-score标准化"},
        {"name": "归一化", "expr": "(column - column.min()) / (column.max() - column.min())", "desc": "Min-Max归一化"},
    ]

    return dbc.Modal([
        dbc.ModalHeader("计算列模板"),
        dbc.ModalBody([
            html.P("选择一个模板快速创建计算列：", className="mb-3"),
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(template["name"], className="card-title"),
                        html.P(template["desc"], className="card-text small text-muted"),
                        html.Code(template["expr"], className="small"),
                    ])
                ], className="mb-2")
                for template in templates
            ]),
            html.Br(),
            dbc.Alert([
                html.Strong("提示："),
                html.Br(),
                "将模板中的列名替换为实际列名即可使用",
                html.Br(),
                f"可用数值列：{', '.join(numeric_cols[:5])}{'...' if len(numeric_cols) > 5 else ''}"
            ], color="info", className="small"),
        ]),
        dbc.ModalFooter([
            dbc.Button("关闭", id="btn-close-templates", color="secondary", size="sm"),
        ]),
    ], id="calc-templates-modal", is_open=True, size="lg")


# 关闭模板模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-close-templates", "n_clicks"),
    prevent_initial_call=True
)
def close_templates_modal(n_clicks):
    return None


# 去空格模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-strip-text", "n_clicks"),
    prevent_initial_call=True
)
def show_strip_text_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    # 获取文本列
    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("去除空格"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="strip-columns-select",
                options=[{"label": col, "value": col} for col in text_cols],
                placeholder="选择要处理的列",
                multi=True
            ),
            html.Br(),
            html.Label("去除方式："),
            dcc.Dropdown(
                id="strip-method-select",
                options=[
                    {"label": "去除两端空格", "value": "both"},
                    {"label": "去除左侧空格", "value": "left"},
                    {"label": "去除右侧空格", "value": "right"},
                ],
                value="both",
                placeholder="选择去除方式"
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-strip", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-strip", color="primary", size="sm"),
        ]),
    ], id="strip-text-modal", is_open=True)


# 确认去空格
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-strip", "n_clicks"),
    [State("strip-columns-select", "value"),
     State("strip-method-select", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_strip_text(n_clicks, columns, method, current_history):
    if not n_clicks or not columns:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        df_new = df.copy()

        for col in columns:
            if method == "both":
                df_new[col] = df_new[col].str.strip()
            elif method == "left":
                df_new[col] = df_new[col].str.lstrip()
            elif method == "right":
                df_new[col] = df_new[col].str.rstrip()

        data_manager.active_df = df_new

        method_names = {"both": "两端", "left": "左侧", "right": "右侧"}
        new_history = add_operation_to_history(
            current_history,
            f"去除空格：{', '.join(columns)}",
            f"去除{method_names.get(method, method)}空格"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 空格去除完成"),
                html.Br(),
                f"处理列：{', '.join(columns)}",
                html.Br(),
                f"方式：去除{method_names.get(method, method)}空格"
            ], color="success"),
            html.H5("处理后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"去除空格失败：{str(e)}", className="text-danger"), None, current_history


# 大小写转换模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-case-convert", "n_clicks"),
    prevent_initial_call=True
)
def show_case_convert_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("大小写转换"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="case-columns-select",
                options=[{"label": col, "value": col} for col in text_cols],
                placeholder="选择要处理的列",
                multi=True
            ),
            html.Br(),
            html.Label("转换方式："),
            dcc.Dropdown(
                id="case-method-select",
                options=[
                    {"label": "转为大写", "value": "upper"},
                    {"label": "转为小写", "value": "lower"},
                    {"label": "首字母大写", "value": "title"},
                    {"label": "首字母大写其余小写", "value": "capitalize"},
                ],
                placeholder="选择转换方式"
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-case", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-case", color="primary", size="sm"),
        ]),
    ], id="case-convert-modal", is_open=True)


# 确认大小写转换
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-case", "n_clicks"),
    [State("case-columns-select", "value"),
     State("case-method-select", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_case_convert(n_clicks, columns, method, current_history):
    if not n_clicks or not columns or not method:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        df_new = df.copy()

        for col in columns:
            if method == "upper":
                df_new[col] = df_new[col].str.upper()
            elif method == "lower":
                df_new[col] = df_new[col].str.lower()
            elif method == "title":
                df_new[col] = df_new[col].str.title()
            elif method == "capitalize":
                df_new[col] = df_new[col].str.capitalize()

        data_manager.active_df = df_new

        method_names = {"upper": "大写", "lower": "小写", "title": "首字母大写", "capitalize": "句首大写"}
        new_history = add_operation_to_history(
            current_history,
            f"大小写转换：{', '.join(columns)}",
            f"转换为{method_names.get(method, method)}"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 大小写转换完成"),
                html.Br(),
                f"处理列：{', '.join(columns)}",
                html.Br(),
                f"方式：{method_names.get(method, method)}"
            ], color="success"),
            html.H5("处理后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"大小写转换失败：{str(e)}", className="text-danger"), None, current_history


# 查找替换模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-find-replace", "n_clicks"),
    prevent_initial_call=True
)
def show_find_replace_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    columns = df.columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("查找替换"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="replace-columns-select",
                options=[{"label": col, "value": col} for col in columns],
                placeholder="选择要处理的列",
                multi=True
            ),
            html.Br(),
            html.Label("查找内容："),
            dbc.Input(id="replace-find-input", placeholder="输入要查找的内容"),
            html.Br(),
            html.Label("替换为："),
            dbc.Input(id="replace-with-input", placeholder="输入替换后的内容"),
            html.Br(),
            dbc.Checklist(
                id="replace-regex-check",
                options=[{"label": "使用正则表达式", "value": "regex"}],
                value=[]
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-replace", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-replace", color="primary", size="sm"),
        ]),
    ], id="find-replace-modal", is_open=True)


# 确认查找替换
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-replace", "n_clicks"),
    [State("replace-columns-select", "value"),
     State("replace-find-input", "value"),
     State("replace-with-input", "value"),
     State("replace-regex-check", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_find_replace(n_clicks, columns, find_text, replace_text, use_regex, current_history):
    if not n_clicks or not columns or find_text is None:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        df_new = df.copy()
        replace_text = replace_text if replace_text is not None else ""
        is_regex = "regex" in use_regex

        for col in columns:
            df_new[col] = df_new[col].astype(str).str.replace(find_text, replace_text, regex=is_regex)

        data_manager.active_df = df_new

        new_history = add_operation_to_history(
            current_history,
            f"查找替换：{', '.join(columns)}",
            f"'{find_text}' → '{replace_text}'"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 查找替换完成"),
                html.Br(),
                f"处理列：{', '.join(columns)}",
                html.Br(),
                f"查找：'{find_text}'",
                html.Br(),
                f"替换为：'{replace_text}'"
            ], color="success"),
            html.H5("处理后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new.head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"查找替换失败：{str(e)}", className="text-danger"), None, current_history


# 更新关闭模态框回调
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    [Input("btn-cancel-strip", "n_clicks"),
     Input("btn-cancel-case", "n_clicks"),
     Input("btn-cancel-replace", "n_clicks")],
    prevent_initial_call=True
)
def close_text_modals(*args):
    return None


# 分箱模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-binning", "n_clicks"),
    prevent_initial_call=True
)
def show_binning_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("数值分箱"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="binning-column-select",
                options=[{"label": col, "value": col} for col in numeric_cols],
                placeholder="选择要分箱的列"
            ),
            html.Br(),
            html.Label("分箱数量："),
            dbc.Input(id="binning-bins-input", type="number", value=5, min=2, max=20),
            html.Br(),
            html.Label("新列名："),
            dbc.Input(id="binning-new-name-input", placeholder="输入新列名（可选）"),
            html.Br(),
            html.Label("标签（可选，用逗号分隔）："),
            dbc.Input(id="binning-labels-input", placeholder="例如: 低,中,高"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-binning", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-binning", color="primary", size="sm"),
        ]),
    ], id="binning-modal", is_open=True)


# 确认分箱
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-binning", "n_clicks"),
    [State("binning-column-select", "value"),
     State("binning-bins-input", "value"),
     State("binning-new-name-input", "value"),
     State("binning-labels-input", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_binning(n_clicks, column, bins, new_name, labels_str, current_history):
    if not n_clicks or not column or not bins:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        df_new = df.copy()

        # 处理标签
        labels = None
        if labels_str and labels_str.strip():
            labels = [label.strip() for label in labels_str.split(',')]
            if len(labels) != bins:
                return html.P(f"标签数量({len(labels)})必须等于分箱数量({bins})", className="text-danger"), None, current_history

        # 分箱
        new_col_name = new_name if new_name else f"{column}_binned"
        df_new[new_col_name] = pd.cut(df_new[column], bins=bins, labels=labels)

        data_manager.active_df = df_new

        new_history = add_operation_to_history(
            current_history,
            f"分箱：{column} → {new_col_name}",
            f"分为 {bins} 个箱"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 分箱完成"),
                html.Br(),
                f"原列：{column}",
                html.Br(),
                f"新列：{new_col_name}",
                html.Br(),
                f"分箱数：{bins}"
            ], color="success"),
            html.H5("分箱后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new[[column, new_col_name]].head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"分箱失败：{str(e)}", className="text-danger"), None, current_history


# 标准化模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-standardize", "n_clicks"),
    prevent_initial_call=True
)
def show_standardize_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("标准化（Z-score）"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="standardize-columns-select",
                options=[{"label": col, "value": col} for col in numeric_cols],
                placeholder="选择要标准化的列",
                multi=True
            ),
            html.Br(),
            dbc.Alert([
                html.Strong("说明："),
                html.Br(),
                "标准化将数据转换为均值为0，标准差为1的分布",
                html.Br(),
                "公式：(x - mean) / std"
            ], color="info", className="small"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-standardize", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-standardize", color="primary", size="sm"),
        ]),
    ], id="standardize-modal", is_open=True)


# 确认标准化
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-standardize", "n_clicks"),
    [State("standardize-columns-select", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_standardize(n_clicks, columns, current_history):
    if not n_clicks or not columns:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        df_new = df.copy()

        for col in columns:
            mean = df_new[col].mean()
            std = df_new[col].std()
            df_new[col] = (df_new[col] - mean) / std

        data_manager.active_df = df_new

        new_history = add_operation_to_history(
            current_history,
            f"标准化：{', '.join(columns)}",
            "Z-score标准化"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 标准化完成"),
                html.Br(),
                f"处理列：{', '.join(columns)}",
                html.Br(),
                "方法：Z-score标准化"
            ], color="success"),
            html.H5("标准化后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new[columns].head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"标准化失败：{str(e)}", className="text-danger"), None, current_history


# 归一化模态框
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    Input("btn-normalize", "n_clicks"),
    prevent_initial_call=True
)
def show_normalize_modal(n_clicks):
    if not n_clicks:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return dbc.Modal([
            dbc.ModalHeader("错误"),
            dbc.ModalBody("请先加载数据集"),
        ], is_open=True)

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    return dbc.Modal([
        dbc.ModalHeader("归一化（Min-Max）"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(
                id="normalize-columns-select",
                options=[{"label": col, "value": col} for col in numeric_cols],
                placeholder="选择要归一化的列",
                multi=True
            ),
            html.Br(),
            dbc.Alert([
                html.Strong("说明："),
                html.Br(),
                "归一化将数据缩放到[0, 1]区间",
                html.Br(),
                "公式：(x - min) / (max - min)"
            ], color="info", className="small"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-normalize", color="secondary", size="sm"),
            dbc.Button("确认", id="btn-confirm-normalize", color="primary", size="sm"),
        ]),
    ], id="normalize-modal", is_open=True)


# 确认归一化
@callback(
    [Output("workshop-preview-area", "children", allow_duplicate=True),
     Output("workshop-modals", "children", allow_duplicate=True),
     Output("operation-history", "data", allow_duplicate=True)],
    Input("btn-confirm-normalize", "n_clicks"),
    [State("normalize-columns-select", "value"),
     State("operation-history", "data")],
    prevent_initial_call=True
)
def confirm_normalize(n_clicks, columns, current_history):
    if not n_clicks or not columns:
        return None, None, current_history

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.P("数据集不存在", className="text-danger"), None, current_history

    try:
        df_new = df.copy()

        for col in columns:
            min_val = df_new[col].min()
            max_val = df_new[col].max()
            df_new[col] = (df_new[col] - min_val) / (max_val - min_val)

        data_manager.active_df = df_new

        new_history = add_operation_to_history(
            current_history,
            f"归一化：{', '.join(columns)}",
            "Min-Max归一化"
        )

        result = html.Div([
            dbc.Alert([
                html.Strong("✓ 归一化完成"),
                html.Br(),
                f"处理列：{', '.join(columns)}",
                html.Br(),
                "方法：Min-Max归一化"
            ], color="success"),
            html.H5("归一化后数据预览：", className="mt-3"),
            dbc.Table.from_dataframe(
                df_new[columns].head(20),
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )
        ])

        return result, None, new_history

    except Exception as e:
        return html.P(f"归一化失败：{str(e)}", className="text-danger"), None, current_history


# 更新关闭模态框回调
@callback(
    Output("workshop-modals", "children", allow_duplicate=True),
    [Input("btn-cancel-binning", "n_clicks"),
     Input("btn-cancel-standardize", "n_clicks"),
     Input("btn-cancel-normalize", "n_clicks")],
    prevent_initial_call=True
)
def close_numeric_modals(*args):
    return None

