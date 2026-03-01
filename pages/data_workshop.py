"""
数据工坊实时预览页面

提供实时数据预览和操作管理功能，支持交互式参数配置弹窗。
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, no_update, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import json
import uuid
from datetime import datetime

from core.data_manager import DataManager
from services.data_workshop.preview_engine import PreviewEngine
from services.data_workshop.step_manager import StepManager
from services.data_workshop.undo_redo_stack import UndoRedoStack
from services.data_workshop.operation_executor import OperationExecutor
from services.data_workshop.code_generator import CodeGenerator
from components.data_workshop.data_grid import create_data_grid, create_data_stats
from components.data_workshop.step_panel import create_step_panel, create_step_header, create_step_actions
from components.data_workshop.toolbar import create_operation_toolbar
from components.data_workshop.code_preview_panel import create_code_modal

# 初始化全局组件
preview_engine = PreviewEngine(max_preview_rows=1000)
step_manager = StepManager()
undo_stack = UndoRedoStack()
operation_executor = OperationExecutor()
code_generator = CodeGenerator()

# 所有操作按钮ID及其对应的操作类型和中文名
OPERATION_BUTTONS = {
    'btn-filter': ('filter', '筛选'),
    'btn-drop-column': ('drop_column', '删除列'),
    'btn-rename-column': ('rename_column', '重命名'),
    'btn-sort': ('sort', '排序'),
    'btn-type-convert': ('type_conversion', '类型转换'),
    'btn-fill-missing': ('fill_missing', '填充缺失值'),
    'btn-drop-duplicates': ('drop_duplicates', '去重'),
    'btn-split-column': ('split_column', '拆分列'),
    'btn-merge-columns': ('merge_columns', '合并列'),
    'btn-replace-value': ('replace_value', '替换值'),
    'btn-strip-whitespace': ('strip_whitespace', '去除空格'),
    'btn-change-case': ('change_case', '大小写转换'),
    'btn-regex-replace': ('find_replace_regex', '正则替换'),
    'btn-extract-substring': ('extract_substring', '提取子串'),
    'btn-bin-column': ('bin_column', '分箱'),
    'btn-normalize': ('normalize', '标准化'),
    'btn-drop-missing-rows': ('drop_missing_rows', '删除缺失行'),
    'btn-duplicate-column': ('duplicate_column', '复制列'),
    'btn-create-calculated': ('create_calculated', '计算列'),
}


def _get_columns_from_store(store_data):
    """从 store 数据中获取列名列表"""
    if not store_data:
        return []
    try:
        df = pd.read_json(store_data, orient='split')
        return list(df.columns)
    except Exception:
        return []


def layout():
    """数据工坊页面布局"""
    # 尝试从 DataManager 加载活跃数据集
    dm = DataManager()
    has_active = dm.active_df is not None and not dm.active_df.empty

    return dbc.Container([
        # 标题栏
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="bi bi-magic me-3", style={"color": "var(--accent)"}),
                        "数据工坊 - 实时预览"
                    ], className="mb-2 fade-in", style={"fontWeight": "600"}),
                    html.P("所见即所得的数据清洗和转换体验",
                          className="fade-in", style={"color": "var(--text-muted)", "fontSize": "0.875rem"})
                ])
            ], width=6),
            dbc.Col([
                html.Div([
                    dbc.Button([
                        html.I(className="bi bi-check2-circle me-2"),
                        "应用到数据集"
                    ], id="btn-apply-to-dataset", color="warning", size="sm", outline=True, className="me-2 btn-hover"),
                    dbc.Button([
                        html.I(className="bi bi-code-slash me-2"),
                        "查看代码"
                    ], id="btn-view-code", color="success", size="sm", outline=True, className="me-2 btn-hover"),
                    dbc.Button([
                        html.I(className="bi bi-download me-2"),
                        "导出"
                    ], id="btn-export", color="primary", size="sm", outline=True, className="btn-hover"),
                ], className="d-flex justify-content-end fade-in")
            ], width=6),
        ], className="mb-4"),

        # 主要内容区
        dbc.Row([
            # 左侧：操作工具栏
            dbc.Col([
                create_operation_toolbar()
            ], width=2, className="slide-in-left"),

            # 中间：数据预览区
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.Span("数据预览", style={"fontWeight": "bold"}),
                            html.Div(id="data-stats", children=[
                                dbc.Badge("0 行", color="primary", className="me-1"),
                                dbc.Badge("0 列", color="info"),
                            ]),
                        ], className="d-flex align-items-center justify-content-between")
                    ]),
                    dbc.CardBody([
                        html.Div(id="data-table-container", children=[
                            html.Div([
                                html.I(className="bi bi-inbox", style={"fontSize": "3rem", "color": "var(--text-muted)"}),
                                html.P("暂无数据", className="text-muted mt-3"),
                                html.P("请先加载数据集", style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
                            ], className="text-center py-5")
                        ]),

                        # 仅当没有活跃数据集时显示"加载示例数据"按钮
                        html.Div([
                            dbc.Button([
                                html.I(className="bi bi-file-earmark-spreadsheet me-2"),
                                "加载示例数据"
                            ], id="btn-load-sample", color="primary", className="mt-3 btn-hover")
                        ], className="text-center", style={"display": "none"} if has_active else {})
                    ], style={"padding": "1rem"})
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=7, className="scale-in"),

            # 右侧：步骤管理面板
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div(id="step-header", children=create_step_header(0))
                    ]),
                    dbc.CardBody([
                        html.Div(id="step-list", children=create_step_panel([], step_manager)),
                        create_step_actions(),
                    ], style={"padding": "1rem", "maxHeight": "600px", "overflowY": "auto"})
                ], className="card-hover", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ], width=3, className="slide-in-right"),
        ]),

        # 数据存储
        dcc.Store(id='original-data-store'),
        dcc.Store(id='preview-data-store'),
        dcc.Store(id='pipeline-store', data=[]),
        dcc.Store(id='undo-redo-store', data={'can_undo': False, 'can_redo': False}),
        dcc.Store(id='pending-operation-type', data=None),
        dcc.Store(id='dm-loaded', data=has_active),

        # 操作配置模态框
        _create_operation_modal(),

        # 代码预览模态框
        create_code_modal(),

        # 下载组件
        dcc.Download(id='download-code'),
        dcc.Download(id='download-code-file'),

        # 状态提示
        html.Div(id='copy-code-status', style={'display': 'none'}),
        html.Div(id='preview-stats-display', style={'display': 'none'}),
        html.Div(id='apply-dataset-status', style={'display': 'none'}),

    ], fluid=True, className="py-4")


# ============================================================================
# 操作配置模态框
# ============================================================================

def _create_operation_modal():
    """创建通用操作配置模态框"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="operation-modal-title", children="操作配置")),
        dbc.ModalBody(id="operation-modal-body", children=[]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-modal-cancel", color="secondary", className="me-2"),
            dbc.Button("应用", id="btn-modal-apply", color="primary"),
        ]),
    ], id="operation-modal", is_open=False, size="lg")


def _build_form_for_operation(op_type, columns):
    """根据操作类型构建配置表单"""
    col_options = [{'label': c, 'value': c} for c in columns]

    if op_type == 'filter':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=4),
                dbc.Col([
                    html.Label("运算符", className="form-label"),
                    dcc.Dropdown(id='modal-param-operator', options=[
                        {'label': '等于 (==)', 'value': '=='},
                        {'label': '不等于 (!=)', 'value': '!='},
                        {'label': '大于 (>)', 'value': '>'},
                        {'label': '小于 (<)', 'value': '<'},
                        {'label': '大于等于 (>=)', 'value': '>='},
                        {'label': '小于等于 (<=)', 'value': '<='},
                        {'label': '包含', 'value': 'contains'},
                        {'label': '开头是', 'value': 'startswith'},
                        {'label': '结尾是', 'value': 'endswith'},
                    ], placeholder="选择运算符"),
                ], width=4),
                dbc.Col([
                    html.Label("值", className="form-label"),
                    dbc.Input(id='modal-param-value', type='text', placeholder="输入筛选值"),
                ], width=4),
            ]),
        ])

    elif op_type == 'drop_column':
        return html.Div([
            html.Label("选择要删除的列（可多选）", className="form-label"),
            dcc.Dropdown(id='modal-param-columns-multi', options=col_options, multi=True, placeholder="选择列"),
        ])

    elif op_type == 'rename_column':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择要重命名的列"),
                ], width=6),
                dbc.Col([
                    html.Label("新名称", className="form-label"),
                    dbc.Input(id='modal-param-new-name', type='text', placeholder="输入新列名"),
                ], width=6),
            ]),
        ])

    elif op_type == 'sort':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择排序列"),
                ], width=6),
                dbc.Col([
                    html.Label("排序方式", className="form-label"),
                    dcc.Dropdown(id='modal-param-ascending', options=[
                        {'label': '升序', 'value': 'true'},
                        {'label': '降序', 'value': 'false'},
                    ], value='true', clearable=False),
                ], width=6),
            ]),
        ])

    elif op_type == 'type_conversion':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=6),
                dbc.Col([
                    html.Label("目标类型", className="form-label"),
                    dcc.Dropdown(id='modal-param-target-type', options=[
                        {'label': '整数 (int)', 'value': 'int'},
                        {'label': '浮点数 (float)', 'value': 'float'},
                        {'label': '字符串 (str)', 'value': 'str'},
                        {'label': '日期时间 (datetime)', 'value': 'datetime'},
                        {'label': '布尔 (bool)', 'value': 'bool'},
                    ], placeholder="选择目标类型"),
                ], width=6),
            ]),
        ])

    elif op_type == 'fill_missing':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=4),
                dbc.Col([
                    html.Label("填充方法", className="form-label"),
                    dcc.Dropdown(id='modal-param-method', options=[
                        {'label': '均值', 'value': 'mean'},
                        {'label': '中位数', 'value': 'median'},
                        {'label': '众数', 'value': 'mode'},
                        {'label': '前向填充', 'value': 'ffill'},
                        {'label': '后向填充', 'value': 'bfill'},
                        {'label': '固定值', 'value': 'value'},
                    ], placeholder="选择方法"),
                ], width=4),
                dbc.Col([
                    html.Label("固定值（仅固定值方法）", className="form-label"),
                    dbc.Input(id='modal-param-fill-value', type='text', placeholder="输入固定值"),
                ], width=4),
            ]),
        ])

    elif op_type == 'drop_duplicates':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("子集列（可选，多选）", className="form-label"),
                    dcc.Dropdown(id='modal-param-columns-multi', options=col_options, multi=True,
                               placeholder="留空则对所有列去重"),
                ], width=8),
                dbc.Col([
                    html.Label("保留策略", className="form-label"),
                    dcc.Dropdown(id='modal-param-keep', options=[
                        {'label': '保留第一个', 'value': 'first'},
                        {'label': '保留最后一个', 'value': 'last'},
                    ], value='first', clearable=False),
                ], width=4),
            ]),
        ])

    elif op_type == 'split_column':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择要拆分的列"),
                ], width=4),
                dbc.Col([
                    html.Label("分隔符", className="form-label"),
                    dbc.Input(id='modal-param-delimiter', type='text', placeholder='如: , 或 -'),
                ], width=4),
                dbc.Col([
                    html.Label("最大拆分数", className="form-label"),
                    dbc.Input(id='modal-param-max-split', type='number', value=-1, placeholder="-1为不限"),
                ], width=4),
            ]),
        ])

    elif op_type == 'merge_columns':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择要合并的列（多选）", className="form-label"),
                    dcc.Dropdown(id='modal-param-columns-multi', options=col_options, multi=True,
                               placeholder="选择至少两列"),
                ], width=4),
                dbc.Col([
                    html.Label("分隔符", className="form-label"),
                    dbc.Input(id='modal-param-delimiter', type='text', placeholder='如: _ 或 -', value='_'),
                ], width=4),
                dbc.Col([
                    html.Label("新列名", className="form-label"),
                    dbc.Input(id='modal-param-new-name', type='text', placeholder="输入新列名"),
                ], width=4),
            ]),
        ])

    elif op_type == 'replace_value':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=4),
                dbc.Col([
                    html.Label("原始值", className="form-label"),
                    dbc.Input(id='modal-param-old-value', type='text', placeholder="要替换的值"),
                ], width=4),
                dbc.Col([
                    html.Label("新值", className="form-label"),
                    dbc.Input(id='modal-param-new-value', type='text', placeholder="替换为"),
                ], width=4),
            ]),
        ])

    elif op_type == 'strip_whitespace':
        return html.Div([
            html.Label("选择列", className="form-label"),
            dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择要去除空格的列"),
        ])

    elif op_type == 'change_case':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=6),
                dbc.Col([
                    html.Label("转换方式", className="form-label"),
                    dcc.Dropdown(id='modal-param-case-type', options=[
                        {'label': '大写 (UPPER)', 'value': 'upper'},
                        {'label': '小写 (lower)', 'value': 'lower'},
                        {'label': '标题 (Title)', 'value': 'title'},
                        {'label': '首字母大写', 'value': 'capitalize'},
                    ], placeholder="选择转换方式"),
                ], width=6),
            ]),
        ])

    elif op_type == 'find_replace_regex':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=3),
                dbc.Col([
                    html.Label("查找模式", className="form-label"),
                    dbc.Input(id='modal-param-pattern', type='text', placeholder="正则表达式或文本"),
                ], width=3),
                dbc.Col([
                    html.Label("替换为", className="form-label"),
                    dbc.Input(id='modal-param-replacement', type='text', placeholder="替换文本"),
                ], width=3),
                dbc.Col([
                    html.Label("正则模式", className="form-label"),
                    dcc.Dropdown(id='modal-param-is-regex', options=[
                        {'label': '正则', 'value': 'true'},
                        {'label': '文本', 'value': 'false'},
                    ], value='true', clearable=False),
                ], width=3),
            ]),
        ])

    elif op_type == 'extract_substring':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=4),
                dbc.Col([
                    html.Label("正则模式（优先）", className="form-label"),
                    dbc.Input(id='modal-param-pattern', type='text', placeholder="如: \\d+"),
                ], width=4),
                dbc.Col([
                    html.Label("起始位置", className="form-label"),
                    dbc.Input(id='modal-param-start', type='number', placeholder="0"),
                ], width=2),
                dbc.Col([
                    html.Label("结束位置", className="form-label"),
                    dbc.Input(id='modal-param-end', type='number', placeholder="空=末尾"),
                ], width=2),
            ]),
            html.Small("提示：填写正则模式时忽略位置参数；留空正则时使用位置切片", className="text-muted"),
        ])

    elif op_type == 'bin_column':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列（数值型）", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=4),
                dbc.Col([
                    html.Label("分箱数", className="form-label"),
                    dbc.Input(id='modal-param-bins', type='number', value=5, min=2),
                ], width=4),
                dbc.Col([
                    html.Label("分箱方法", className="form-label"),
                    dcc.Dropdown(id='modal-param-bin-method', options=[
                        {'label': '等宽分箱', 'value': 'equal_width'},
                        {'label': '等频分箱', 'value': 'equal_freq'},
                    ], value='equal_width', clearable=False),
                ], width=4),
            ]),
        ])

    elif op_type == 'normalize':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列（数值型）", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择列"),
                ], width=6),
                dbc.Col([
                    html.Label("标准化方法", className="form-label"),
                    dcc.Dropdown(id='modal-param-norm-method', options=[
                        {'label': 'Min-Max 归一化', 'value': 'minmax'},
                        {'label': 'Z-Score 标准化', 'value': 'zscore'},
                        {'label': 'Robust (中位/IQR)', 'value': 'robust'},
                    ], value='minmax', clearable=False),
                ], width=6),
            ]),
        ])

    elif op_type == 'drop_missing_rows':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("指定列（可选）", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options,
                               placeholder="留空=检查所有列", clearable=True),
                ], width=4),
                dbc.Col([
                    html.Label("删除条件", className="form-label"),
                    dcc.Dropdown(id='modal-param-how', options=[
                        {'label': '任一缺失 (any)', 'value': 'any'},
                        {'label': '全部缺失 (all)', 'value': 'all'},
                    ], value='any', clearable=False),
                ], width=4),
                dbc.Col([
                    html.Label("阈值（可选）", className="form-label"),
                    dbc.Input(id='modal-param-threshold', type='number', placeholder="最少非空数"),
                ], width=4),
            ]),
            html.Small("提示：设置阈值时将忽略删除条件", className="text-muted"),
        ])

    elif op_type == 'duplicate_column':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("选择列", className="form-label"),
                    dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择要复制的列"),
                ], width=6),
                dbc.Col([
                    html.Label("新列名", className="form-label"),
                    dbc.Input(id='modal-param-new-name', type='text', placeholder="输入新列名"),
                ], width=6),
            ]),
        ])

    elif op_type == 'create_calculated':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("计算表达式", className="form-label"),
                    dbc.Input(id='modal-param-expression', type='text',
                             placeholder="如: salary * 1.1 或 col1 + col2"),
                ], width=8),
                dbc.Col([
                    html.Label("新列名", className="form-label"),
                    dbc.Input(id='modal-param-new-name', type='text', placeholder="calculated", value="calculated"),
                ], width=4),
            ]),
            html.Small(f"可用列名: {', '.join(columns)}", className="text-muted d-block mt-2"),
        ])

    return html.Div("未知操作类型")


# ============================================================================
# 回调：加载数据（示例数据或从 DataManager）
# ============================================================================

@callback(
    Output('original-data-store', 'data'),
    Output('data-table-container', 'children'),
    Output('data-stats', 'children'),
    Input('btn-load-sample', 'n_clicks'),
    Input('dm-loaded', 'data'),
    prevent_initial_call=True
)
def load_data(n_clicks, dm_loaded):
    """加载数据：优先从 DataManager，否则加载示例"""
    triggered_id = ctx.triggered_id

    if triggered_id == 'dm-loaded' and dm_loaded:
        dm = DataManager()
        df = dm.active_df
        if df is not None and not df.empty:
            table = create_data_grid(df, preview_mode=False)
            stats = create_data_stats(df)
            return df.to_json(date_format='iso', orient='split'), table, stats
        return no_update, no_update, no_update

    # 加载示例数据
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
        'age': ['25', '30', '35', '28', '32', '29', '31', '27'],
        'city': ['NYC', 'LA', 'SF', 'NYC', 'LA', 'SF', 'NYC', 'LA'],
        'salary': [50000, 60000, 75000, 55000, 65000, 58000, 62000, 53000],
        'department': ['Sales', 'Engineering', 'Sales', 'Engineering', 'Sales', 'Engineering', 'Sales', 'Engineering']
    })

    # 也存入 DataManager
    dm = DataManager()
    dm.add_dataset("示例数据", df, source="sample:demo")

    table = create_data_grid(df, preview_mode=False)
    stats = create_data_stats(df)
    return df.to_json(date_format='iso', orient='split'), table, stats


# ============================================================================
# 回调：点击操作按钮 → 打开配置模态框
# ============================================================================

@callback(
    Output('operation-modal', 'is_open'),
    Output('operation-modal-title', 'children'),
    Output('operation-modal-body', 'children'),
    Output('pending-operation-type', 'data'),
    # 所有操作按钮作为 Input
    Input('btn-filter', 'n_clicks'),
    Input('btn-drop-column', 'n_clicks'),
    Input('btn-rename-column', 'n_clicks'),
    Input('btn-sort', 'n_clicks'),
    Input('btn-type-convert', 'n_clicks'),
    Input('btn-fill-missing', 'n_clicks'),
    Input('btn-drop-duplicates', 'n_clicks'),
    Input('btn-split-column', 'n_clicks'),
    Input('btn-merge-columns', 'n_clicks'),
    Input('btn-replace-value', 'n_clicks'),
    Input('btn-strip-whitespace', 'n_clicks'),
    Input('btn-change-case', 'n_clicks'),
    Input('btn-regex-replace', 'n_clicks'),
    Input('btn-extract-substring', 'n_clicks'),
    Input('btn-bin-column', 'n_clicks'),
    Input('btn-normalize', 'n_clicks'),
    Input('btn-drop-missing-rows', 'n_clicks'),
    Input('btn-duplicate-column', 'n_clicks'),
    Input('btn-create-calculated', 'n_clicks'),
    Input('btn-modal-cancel', 'n_clicks'),
    State('original-data-store', 'data'),
    State('preview-data-store', 'data'),
    prevent_initial_call=True
)
def open_operation_modal(*args):
    """点击操作按钮时弹出配置表单"""
    triggered_id = ctx.triggered_id

    if triggered_id == 'btn-modal-cancel':
        return False, "", [], None

    if triggered_id not in OPERATION_BUTTONS:
        return no_update, no_update, no_update, no_update

    # 获取原始数据中的列名
    original_data = args[-2]  # State: original-data-store
    preview_data = args[-1]   # State: preview-data-store

    # 使用最新的预览数据，以便列名反映已执行的操作
    data_to_use = preview_data or original_data
    columns = _get_columns_from_store(data_to_use)

    if not columns:
        return True, "提示", html.Div([
            dbc.Alert("请先加载数据", color="warning"),
        ]), None

    op_type, op_name = OPERATION_BUTTONS[triggered_id]
    form = _build_form_for_operation(op_type, columns)

    return True, f"配置 — {op_name}", form, op_type


# ============================================================================
# 回调：应用操作（模态框"应用"按钮）
# ============================================================================

@callback(
    Output('operation-modal', 'is_open', allow_duplicate=True),
    Output('pipeline-store', 'data'),
    Output('preview-data-store', 'data'),
    Output('data-table-container', 'children', allow_duplicate=True),
    Output('data-stats', 'children', allow_duplicate=True),
    Output('undo-redo-store', 'data'),
    Input('btn-modal-apply', 'n_clicks'),
    State('pending-operation-type', 'data'),
    State('original-data-store', 'data'),
    State('pipeline-store', 'data'),
    # 所有可能的表单字段（统一ID方式）
    State('modal-param-column', 'value'),
    State('modal-param-operator', 'value'),
    State('modal-param-value', 'value'),
    State('modal-param-columns-multi', 'value'),
    State('modal-param-new-name', 'value'),
    State('modal-param-ascending', 'value'),
    State('modal-param-target-type', 'value'),
    State('modal-param-method', 'value'),
    State('modal-param-fill-value', 'value'),
    State('modal-param-keep', 'value'),
    State('modal-param-delimiter', 'value'),
    State('modal-param-max-split', 'value'),
    State('modal-param-old-value', 'value'),
    State('modal-param-new-value', 'value'),
    State('modal-param-case-type', 'value'),
    State('modal-param-pattern', 'value'),
    State('modal-param-replacement', 'value'),
    State('modal-param-is-regex', 'value'),
    State('modal-param-start', 'value'),
    State('modal-param-end', 'value'),
    State('modal-param-bins', 'value'),
    State('modal-param-bin-method', 'value'),
    State('modal-param-norm-method', 'value'),
    State('modal-param-how', 'value'),
    State('modal-param-threshold', 'value'),
    State('modal-param-expression', 'value'),
    prevent_initial_call=True
)
def apply_operation(
    apply_clicks, op_type, original_data, current_pipeline,
    column, operator, value, columns_multi, new_name,
    ascending, target_type, method, fill_value, keep,
    delimiter, max_split, old_value, new_value,
    case_type, pattern, replacement, is_regex,
    start, end, bins, bin_method, norm_method,
    how, threshold, expression
):
    """在用户填写参数后执行操作"""
    if not op_type or not original_data:
        return no_update, no_update, no_update, no_update, no_update, no_update

    # 根据操作类型构建参数
    params = _build_params(
        op_type, column, operator, value, columns_multi, new_name,
        ascending, target_type, method, fill_value, keep,
        delimiter, max_split, old_value, new_value,
        case_type, pattern, replacement, is_regex,
        start, end, bins, bin_method, norm_method,
        how, threshold, expression
    )

    if params is None:
        return no_update, no_update, no_update, no_update, no_update, no_update

    # 创建操作记录
    operation = {
        'step_id': str(uuid.uuid4()),
        'operation': op_type,
        'params': params,
        'timestamp': datetime.now().isoformat()
    }

    # 添加到 pipeline
    new_pipeline = current_pipeline.copy() if current_pipeline else []
    new_pipeline.append(operation)

    # 计算预览
    df = pd.read_json(original_data, orient='split')
    result = preview_engine.compute_preview(df, new_pipeline)

    if 'error' in result:
        return no_update, no_update, no_update, no_update, no_update, no_update

    operation['affected_rows'] = result.get('affected_rows', 0)
    operation['affected_cols'] = result.get('affected_cols', 0)
    operation['execution_time'] = result.get('execution_time', 0)

    # 保存撤销状态
    undo_stack.push_state({
        'pipeline': new_pipeline.copy(),
        'timestamp': datetime.now().isoformat()
    })

    preview_df = result['preview_df']
    table = create_data_grid(preview_df, preview_mode=True)
    stats = create_data_stats(preview_df)

    undo_redo_state = {
        'can_undo': undo_stack.can_undo(),
        'can_redo': undo_stack.can_redo()
    }

    return False, new_pipeline, preview_df.to_json(orient='split'), table, stats, undo_redo_state


def _build_params(
    op_type, column, operator, value, columns_multi, new_name,
    ascending, target_type, method, fill_value, keep,
    delimiter, max_split, old_value, new_value,
    case_type, pattern, replacement, is_regex,
    start, end, bins, bin_method, norm_method,
    how, threshold, expression
):
    """根据操作类型从表单字段值构建参数字典"""

    if op_type == 'filter':
        if not column or not operator:
            return None
        return {'column': column, 'operator': operator, 'value': value or ''}

    elif op_type == 'drop_column':
        if not columns_multi:
            return None
        return {'columns': columns_multi}

    elif op_type == 'rename_column':
        if not column or not new_name:
            return None
        return {'old_name': column, 'new_name': new_name}

    elif op_type == 'sort':
        if not column:
            return None
        return {'column': column, 'ascending': ascending == 'true'}

    elif op_type == 'type_conversion':
        if not column or not target_type:
            return None
        return {'column': column, 'target_type': target_type}

    elif op_type == 'fill_missing':
        if not column or not method:
            return None
        params = {'column': column, 'method': method}
        if method == 'value':
            params['value'] = fill_value or 0
        return params

    elif op_type == 'drop_duplicates':
        params = {'keep': keep or 'first'}
        if columns_multi:
            params['subset'] = columns_multi
        return params

    elif op_type == 'split_column':
        if not column or not delimiter:
            return None
        params = {'column': column, 'delimiter': delimiter}
        if max_split is not None:
            params['max_split'] = int(max_split)
        return params

    elif op_type == 'merge_columns':
        if not columns_multi or len(columns_multi) < 2:
            return None
        params = {'columns': columns_multi, 'delimiter': delimiter or '_'}
        if new_name:
            params['new_column'] = new_name
        return params

    elif op_type == 'replace_value':
        if not column:
            return None
        return {'column': column, 'old_value': old_value or '', 'new_value': new_value or ''}

    elif op_type == 'strip_whitespace':
        if not column:
            return None
        return {'column': column}

    elif op_type == 'change_case':
        if not column or not case_type:
            return None
        return {'column': column, 'case_type': case_type}

    elif op_type == 'find_replace_regex':
        if not column or not pattern:
            return None
        return {
            'column': column,
            'pattern': pattern,
            'replacement': replacement or '',
            'is_regex': is_regex == 'true',
        }

    elif op_type == 'extract_substring':
        if not column:
            return None
        params = {'column': column}
        if pattern:
            params['pattern'] = pattern
        else:
            params['start'] = start or 0
            params['end'] = end
        return params

    elif op_type == 'bin_column':
        if not column:
            return None
        return {
            'column': column,
            'bins': bins or 5,
            'method': bin_method or 'equal_width',
        }

    elif op_type == 'normalize':
        if not column:
            return None
        return {'column': column, 'method': norm_method or 'minmax'}

    elif op_type == 'drop_missing_rows':
        params = {'how': how or 'any'}
        if column:
            params['column'] = column
        if threshold is not None and threshold != '':
            params['threshold'] = int(threshold)
        return params

    elif op_type == 'duplicate_column':
        if not column:
            return None
        return {'column': column, 'new_name': new_name or f"{column}_copy"}

    elif op_type == 'create_calculated':
        if not expression:
            return None
        return {'expression': expression, 'new_column': new_name or 'calculated'}

    return None


# ============================================================================
# 回调：应用到数据集（写回 DataManager）
# ============================================================================

@callback(
    Output('apply-dataset-status', 'children'),
    Input('btn-apply-to-dataset', 'n_clicks'),
    State('preview-data-store', 'data'),
    State('original-data-store', 'data'),
    prevent_initial_call=True
)
def apply_to_dataset(n_clicks, preview_data, original_data):
    """将清洗结果写回 DataManager"""
    data_to_use = preview_data or original_data
    if not data_to_use:
        return "无数据"

    df = pd.read_json(data_to_use, orient='split')
    dm = DataManager()

    if dm.active_name:
        dm.update_active_dataset(df, snapshot=True)
    else:
        dm.add_dataset("清洗结果", df, source="workshop")

    return "已应用"


# ============================================================================
# 回调：更新步骤列表
# ============================================================================

@callback(
    Output('step-list', 'children'),
    Output('step-header', 'children'),
    Output('btn-clear-steps', 'disabled'),
    Input('pipeline-store', 'data'),
)
def update_step_list(pipeline):
    """更新步骤列表显示"""
    if not pipeline:
        return create_step_panel([]), create_step_header(0), True

    step_panel = create_step_panel(pipeline, step_manager)
    header = create_step_header(len(pipeline))

    return step_panel, header, False


# ============================================================================
# 回调：更新撤销重做按钮状态
# ============================================================================

@callback(
    Output('btn-undo', 'disabled'),
    Output('btn-redo', 'disabled'),
    Input('undo-redo-store', 'data'),
)
def update_undo_redo_buttons(undo_redo_state):
    """更新撤销重做按钮状态"""
    return not undo_redo_state['can_undo'], not undo_redo_state['can_redo']


# ============================================================================
# 回调：撤销重做
# ============================================================================

@callback(
    Output('pipeline-store', 'data', allow_duplicate=True),
    Output('preview-data-store', 'data', allow_duplicate=True),
    Output('data-table-container', 'children', allow_duplicate=True),
    Output('data-stats', 'children', allow_duplicate=True),
    Output('undo-redo-store', 'data', allow_duplicate=True),
    Input('btn-undo', 'n_clicks'),
    Input('btn-redo', 'n_clicks'),
    State('original-data-store', 'data'),
    prevent_initial_call=True
)
def handle_undo_redo(undo_clicks, redo_clicks, original_data):
    """处理撤销重做操作"""
    if not original_data:
        return no_update, no_update, no_update, no_update, no_update

    triggered_id = ctx.triggered_id

    if triggered_id == 'btn-undo':
        state = undo_stack.undo()
    elif triggered_id == 'btn-redo':
        state = undo_stack.redo()
    else:
        return no_update, no_update, no_update, no_update, no_update

    if not state:
        return no_update, no_update, no_update, no_update, no_update

    pipeline = state.get('pipeline', [])

    df = pd.read_json(original_data, orient='split')

    if pipeline:
        result = preview_engine.compute_preview(df, pipeline)
        if 'error' in result:
            return no_update, no_update, no_update, no_update, no_update
        preview_df = result['preview_df']
    else:
        preview_df = df

    table = create_data_grid(preview_df, preview_mode=True)
    stats = create_data_stats(preview_df)

    undo_redo_state = {
        'can_undo': undo_stack.can_undo(),
        'can_redo': undo_stack.can_redo()
    }

    return pipeline, preview_df.to_json(orient='split'), table, stats, undo_redo_state


# ============================================================================
# 回调：代码生成
# ============================================================================

@callback(
    Output('code-preview-modal', 'is_open'),
    Output('code-display-area', 'children'),
    Input('btn-view-code', 'n_clicks'),
    Input('btn-close-code-modal', 'n_clicks'),
    State('pipeline-store', 'data'),
    State('code-preview-modal', 'is_open'),
    prevent_initial_call=True
)
def handle_code_preview(view_clicks, close_clicks, pipeline, is_open):
    """处理代码预览"""
    triggered_id = ctx.triggered_id

    if triggered_id == 'btn-view-code':
        if not pipeline:
            code = "# 暂无操作\n# 请先执行一些数据操作"
        else:
            code = code_generator.generate_code(
                pipeline,
                data_source='data.csv',
                include_imports=True,
                include_comments=True
            )

        from components.data_workshop.code_preview_panel import create_code_preview_panel
        code_display = create_code_preview_panel(code, show_header=False)
        return True, code_display

    elif triggered_id == 'btn-close-code-modal':
        return False, no_update

    return no_update, no_update
