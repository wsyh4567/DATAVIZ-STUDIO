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
from services.export_service import build_workshop_export
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
    """数据工坊页面布局 — 紧凑版

    布局: [50px 图标条] [填充剩余的表格区] [可折叠右抽屉]
    """
    dm = DataManager()
    has_active = dm.active_df is not None and not dm.active_df.empty

    return html.Div([
        # ── 顶部工具栏 ──
        html.Div([
            html.Div([
                # 抽屉切换按钮
                dbc.Button([html.I(className="bi bi-list")],
                           id="btn-toggle-left-drawer", color="link", size="sm",
                           title="显示/隐藏左侧面板", className="btn-hover text-muted me-2", style={"padding": "0", "fontSize": "1.2rem"}),
                html.I(className="bi bi-magic me-2", style={"color": "var(--accent)", "fontSize": "1.1rem"}),
                html.Span("数据工坊", style={"fontWeight": "700", "fontSize": "1rem", "marginRight": "16px"}),
                
                # 新增：打开算子工具箱按钮
                dbc.Button([html.I(className="bi bi-tools me-1"), "算子工具箱"],
                           id="btn-open-toolbox", color="primary", size="sm", className="btn-hover"),
            ], style={"display": "flex", "alignItems": "center"}),

            # 隐藏的 data-stats (满足后续回调依赖)
            html.Div(id="data-stats", style={"display": "none"}),

        ], style={
            "display": "flex",
            "justifyContent": "flex-start",
            "alignItems": "center",
            "padding": "8px 16px",
            "backgroundColor": "var(--bg-secondary)",
            "border": "1px solid var(--border)",
            "borderRadius": "10px",
            "marginBottom": "8px",
        }),

        # ── 主内容：左抽屉 + 图标条 + 表格 ──
        html.Div([
            # 1. 左侧：可折叠抽屉（操作步骤 + 代码 + 应用导出按钮）
            html.Div([
                dbc.Accordion([
                    dbc.AccordionItem([
                        html.Div(id="step-header", children=create_step_header(0), style={"marginBottom": "8px"}),
                        html.Div(id="step-list", children=create_step_panel([], step_manager),
                                 style={"maxHeight": "30vh", "padding": "0 4px", "overflowY": "auto"}),
                        html.Div([create_step_actions()], style={"borderTop": "1px solid var(--border)", "paddingTop": "8px", "marginTop": "8px"}),
                        html.Div([
                            dbc.Button([html.I(className="bi bi-check2-circle me-1"), "应用执行"],
                                       id="btn-apply-to-dataset", color="warning", size="sm", outline=True, className="mt-2 w-100 btn-hover"),
                            dbc.Button([html.I(className="bi bi-download me-1"), "导出数据"],
                                       id="btn-export", color="primary", size="sm", outline=True, className="mt-2 text-nowrap w-100 btn-hover"),
                        ], style={"borderTop": "1px solid var(--border)", "paddingTop": "8px", "marginTop": "8px"}),
                    ], title="🔄 管线与操作步骤", item_id="tab-pipeline"),

                    dbc.AccordionItem([
                        html.Div(id="inline-code-display", children=[
                            html.Pre(
                                html.Code("# 暂无操作\n# 请先执行一些数据操作",
                                          style={"color": "#a8b2c1", "fontSize": "0.72rem"}),
                                style={
                                    "backgroundColor": "#1e2533",
                                    "padding": "10px", "borderRadius": "4px",
                                    "margin": "0", "maxHeight": "30vh", "overflowY": "auto"
                                }
                            )
                        ]),
                        dbc.Button([html.I(className="bi bi-clipboard me-1"), "复制代码"],
                                   id="btn-copy-code", color="primary", size="sm", outline=True, className="mt-2 btn-hover w-100"),
                        dbc.Button([html.I(className="bi bi-download me-1"), "下载 .py"],
                                   id="btn-download-inline-code", color="success", size="sm", outline=True, className="mt-2 btn-hover w-100"),
                                   dbc.Button([html.I(className="bi bi-journal-code me-1"), "Export .ipynb"],
                                              id="btn-download-inline-notebook", color="info", size="sm", outline=True, className="mt-2 btn-hover w-100"),
                    ], title="💻 Python 导出代码", item_id="tab-code")
                ], active_item="tab-pipeline", id="workshop-sidebar-accordion", start_collapsed=False)
            ], id="left-drawer",
               style={
                   "position": "relative",
                   "marginRight": "8px",
                   "border": "1px solid var(--border)",
                   "borderRadius": "10px",
                   "overflow": "hidden",
                   "transition": "width 0.3s, opacity 0.3s",
                   "width": "300px",
                   "flexShrink": "0",
               }),

            # 3. 中间：数据预览（flex-grow: 1，占据剩余空间）
            html.Div([
                html.Div(id="data-table-container", children=[
                    html.Div([
                        html.I(className="bi bi-inbox", style={"fontSize": "3rem", "color": "var(--text-muted)"}),
                        html.P("暂无数据", className="text-muted mt-3"),
                        html.P("请先加载数据集", className="text-muted", style={"fontSize": "0.875rem"}),
                    ], className="text-center py-5")
                ]),
                # 加载示例数据按钮
                html.Div([
                    dbc.Button([
                        html.I(className="bi bi-file-earmark-spreadsheet me-2"),
                        "加载示例数据"
                    ], id="btn-load-sample", color="primary", size="sm", className="btn-hover")
                ], className="text-center", style={"display": "none"} if has_active else {}),
            ], style={
                "flex": "1",
                "minWidth": "0",
                "overflow": "hidden",
                "backgroundColor": "var(--bg-secondary)",
                "border": "1px solid var(--border)",
                "borderRadius": "10px",
                "padding": "8px",
                "marginLeft": "8px",
            }),

        ], style={
            "display": "flex",
            "gap": "0",
            "height": "calc(100vh - 180px)",
            "alignItems": "stretch",
        }),

        # 数据存储
        dcc.Store(id='original-data-store'),
        dcc.Store(id='preview-data-store'),
        dcc.Store(id='pipeline-store', data=[]),
        dcc.Store(id='undo-redo-store', data={'can_undo': False, 'can_redo': False}),
        dcc.Store(id='pending-operation-type', data=None),
        dcc.Store(id='dm-loaded', data=has_active),
        dcc.Store(id='left-drawer-open', data=True),

        dcc.Store(id='left-drawer-open', data=True),

        # 抽屉式的算子工具箱
        dbc.Offcanvas(
            create_operation_toolbar(),
            id="toolbox-offcanvas",
            title="🛠️ 算子工具箱",
            is_open=False,
            placement="start",
            style={"width": "260px"}
        ),

        # 弹窗式的操作配置框
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("待配置", id="operation-modal-title", className="fw-bold text-primary")),
            dbc.ModalBody(id="operation-modal-body", children=[
                html.P("请先从工具箱选择一个操作以开始设置", className="text-muted small")
            ]),
            dbc.ModalFooter([
                dbc.Button("取消", id="btn-modal-cancel", color="secondary", size="sm", className="me-2"),
                dbc.Button("应用", id="btn-modal-apply", color="primary", size="sm"),
            ])
        ], id="operation-modal", is_open=False, backdrop="static"),

        # 下载组件
        dcc.Download(id='download-code'),
        dcc.Download(id='download-workshop-py-file'),
        dcc.Download(id='download-workshop-ipynb-file'),

        # 状态提示
        html.Div(id='copy-code-status', style={'display': 'none'}),
        html.Div(id='preview-stats-display', style={'display': 'none'}),
        html.Div(id='apply-dataset-status', style={'display': 'none'}),

        # 内联代码折叠兼容
        html.Div(id='inline-code-collapse', style={'display': 'none'}),
        html.Div(id='inline-code-collapse-icon', style={'display': 'none'}),
        html.Div(id='btn-toggle-inline-code', style={'display': 'none'}),

    ], style={"padding": "12px 16px"})


# _create_operation_modal 已弃用，配置表单直接注入左栏


def _build_form_for_operation(op_type, columns):
    """根据操作类型构建配置表单"""
    col_options = [{'label': c, 'value': c} for c in columns]

    # ── 辅助：在表单后追加所有缺失 State ID 的隐藏占位组件 ──
    # apply_operation 回调显式声明了以下全部 ID 为 State，
    # Dash 要求它们全部存在于 DOM 中。每个操作只生成部分表单字段，
    # 此辅助函数会自动为缺失的 ID 追加隐藏的空组件。
    ALL_STATE_IDS = {
        'modal-param-column': lambda: dcc.Dropdown(id='modal-param-column', value=None, style={'display': 'none'}),
        'modal-param-operator': lambda: dcc.Dropdown(id='modal-param-operator', value=None, style={'display': 'none'}),
        'modal-param-value': lambda: dbc.Input(id='modal-param-value', value='', style={'display': 'none'}),
        'modal-param-columns-multi': lambda: dcc.Dropdown(id='modal-param-columns-multi', value=[], style={'display': 'none'}),
        'modal-param-new-name': lambda: dbc.Input(id='modal-param-new-name', value='', style={'display': 'none'}),
        'modal-param-ascending': lambda: dcc.Dropdown(id='modal-param-ascending', value=None, style={'display': 'none'}),
        'modal-param-target-type': lambda: dcc.Dropdown(id='modal-param-target-type', value=None, style={'display': 'none'}),
        'modal-param-method': lambda: dcc.Dropdown(id='modal-param-method', value=None, style={'display': 'none'}),
        'modal-param-fill-value': lambda: dbc.Input(id='modal-param-fill-value', value='', style={'display': 'none'}),
        'modal-param-keep': lambda: dcc.Dropdown(id='modal-param-keep', value=None, style={'display': 'none'}),
        'modal-param-delimiter': lambda: dbc.Input(id='modal-param-delimiter', value='', style={'display': 'none'}),
        'modal-param-max-split': lambda: dbc.Input(id='modal-param-max-split', value=None, type='number', style={'display': 'none'}),
        'modal-param-old-value': lambda: dbc.Input(id='modal-param-old-value', value='', style={'display': 'none'}),
        'modal-param-new-value': lambda: dbc.Input(id='modal-param-new-value', value='', style={'display': 'none'}),
        'modal-param-case-type': lambda: dcc.Dropdown(id='modal-param-case-type', value=None, style={'display': 'none'}),
        'modal-param-pattern': lambda: dbc.Input(id='modal-param-pattern', value='', style={'display': 'none'}),
        'modal-param-replacement': lambda: dbc.Input(id='modal-param-replacement', value='', style={'display': 'none'}),
        'modal-param-is-regex': lambda: dbc.Checklist(id='modal-param-is-regex', value=[], style={'display': 'none'}),
        'modal-param-start': lambda: dbc.Input(id='modal-param-start', value=None, type='number', style={'display': 'none'}),
        'modal-param-end': lambda: dbc.Input(id='modal-param-end', value=None, type='number', style={'display': 'none'}),
        'modal-param-bins': lambda: dbc.Input(id='modal-param-bins', value=None, type='number', style={'display': 'none'}),
        'modal-param-bin-method': lambda: dcc.Dropdown(id='modal-param-bin-method', value=None, style={'display': 'none'}),
        'modal-param-norm-method': lambda: dcc.Dropdown(id='modal-param-norm-method', value=None, style={'display': 'none'}),
        'modal-param-how': lambda: dcc.Dropdown(id='modal-param-how', value=None, style={'display': 'none'}),
        'modal-param-threshold': lambda: dbc.Input(id='modal-param-threshold', value=None, type='number', style={'display': 'none'}),
        'modal-param-expression': lambda: dbc.Input(id='modal-param-expression', value='', style={'display': 'none'}),
        'modal-filter-tabs': lambda: dbc.Tabs(id='modal-filter-tabs', active_tab=None, children=[], style={'display': 'none'}),
        'modal-param-checklist': lambda: dbc.Checklist(id='modal-param-checklist', value=[], style={'display': 'none'}),
    }

    def _collect_ids(component):
        """递归收集组件树中所有 id"""
        ids = set()
        if hasattr(component, 'id') and component.id:
            ids.add(component.id)
        if hasattr(component, 'children'):
            kids = component.children
            if isinstance(kids, list):
                for child in kids:
                    if hasattr(child, 'id') or hasattr(child, 'children'):
                        ids |= _collect_ids(child)
            elif hasattr(kids, 'id') or hasattr(kids, 'children'):
                ids |= _collect_ids(kids)
        return ids

    def _wrap_with_placeholders(form_div):
        """在表单后追加缺失 ID 的隐藏占位"""
        used = _collect_ids(form_div)
        missing = [create_fn() for sid, create_fn in ALL_STATE_IDS.items() if sid not in used]
        if not missing:
            return form_div
        return _wrap_with_placeholders(html.Div([form_div, html.Div(missing, style={'display': 'none'})]))

    if op_type == 'filter':
        return _wrap_with_placeholders(html.Div([
            html.Label("1. 选择要筛选的列", className="form-label fw-bold"),
            dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="请选择或输入列名", className="mb-3"),
            
            html.Div(id="modal-filter-options-container", style={"display": "none"}, children=[
                html.Label("2. 设置筛选规则", className="form-label fw-bold mt-2"),
                dbc.Tabs([
                    dbc.Tab(label="条件筛选", tab_id="tab-condition", children=[
                        dbc.Row([
                            dbc.Col([
                                html.Label("运算符", className="form-label text-muted mt-2"),
                                dcc.Dropdown(id='modal-param-operator', options=[
                                    {'label': '等于', 'value': '=='},
                                    {'label': '不等于', 'value': '!='},
                                    {'label': '大于', 'value': '>'},
                                    {'label': '重大于等于', 'value': '>='},
                                    {'label': '小于', 'value': '<'},
                                    {'label': '小于等于', 'value': '<='},
                                    {'label': '包含文本', 'value': 'contains'},
                                    {'label': '不包含文本', 'value': 'not_contains'},
                                    {'label': '开头是', 'value': 'startswith'},
                                    {'label': '结尾是', 'value': 'endswith'},
                                    {'label': '为空 (null)', 'value': 'isnull'},
                                    {'label': '非空 (not null)', 'value': 'notnull'},
                                ], placeholder="选择运算符", value='==', className="mb-2"),
                            ], width=5),
                            
                            dbc.Col([
                                html.Label("值", className="form-label text-muted mt-2"),
                                dbc.Input(id='modal-param-value', type='text', placeholder="输入筛选值 (数字/文本)"),
                            ], width=7),
                        ])
                    ], className="py-3"),
                    
                    dbc.Tab(label="列表勾选 (多选)", tab_id="tab-checklist", children=[
                        html.Div([
                            html.Div([
                                dbc.Input(id="modal-filter-search", placeholder="在列表中搜索...", size="sm", className="mb-2"),
                                dbc.Button("全选", id="btn-filter-select-all", size="sm", color="link", className="p-0 me-3 text-decoration-none"),
                                dbc.Button("清空", id="btn-filter-clear-all", size="sm", color="link", className="p-0 text-decoration-none text-danger"),
                            ], className="d-flex justify-content-between align-items-center mb-2 mt-2"),
                            
                            html.Div(
                                id='modal-param-checklist-container',
                                children=dcc.Checklist(
                                    id='modal-param-checklist',
                                    options=[],
                                    value=[],
                                    className="dvs-checklist",
                                    labelClassName="d-block mb-1",
                                    inputClassName="me-2"
                                ),
                                style={"maxHeight": "200px", "overflowY": "auto", "border": "1px solid var(--border)", "padding": "0.5rem", "borderRadius": "4px"}
                            )
                        ], className="py-2")
                    ])
                ], id="modal-filter-tabs", active_tab="tab-condition")
            ])
        ]))

    elif op_type == 'drop_column':
        return _wrap_with_placeholders(html.Div([
            html.Label("选择要删除的列（可多选）", className="form-label"),
            dcc.Dropdown(id='modal-param-columns-multi', options=col_options, multi=True, placeholder="选择列"),
        ]))

    elif op_type == 'rename_column':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'sort':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'type_conversion':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'fill_missing':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'drop_duplicates':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'split_column':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'merge_columns':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'replace_value':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'strip_whitespace':
        return _wrap_with_placeholders(html.Div([
            html.Label("选择列", className="form-label"),
            dcc.Dropdown(id='modal-param-column', options=col_options, placeholder="选择要去除空格的列"),
        ]))

    elif op_type == 'change_case':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'find_replace_regex':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'extract_substring':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'bin_column':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'normalize':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'drop_missing_rows':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'duplicate_column':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    elif op_type == 'create_calculated':
        return _wrap_with_placeholders(html.Div([
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
        ]))

    return _wrap_with_placeholders(html.Div("未知操作类型"))


# ============================================================================
# 回调：加载数据（示例数据或从 DataManager）
# ============================================================================

@callback(
    Output('original-data-store', 'data'),
    Output('data-table-container', 'children'),
    Output('data-stats', 'children'),
    Input('btn-load-sample', 'n_clicks'),
    State('dm-loaded', 'data'),
    prevent_initial_call=False  # 允许初始调用以自动加载数据
)
def load_data(n_clicks, dm_loaded):
    """加载数据：优先从 DataManager，否则加载示例"""
    dm = DataManager()

    # 首先尝试从 DataManager 加载活跃数据集
    if dm.active_df is not None and not dm.active_df.empty:
        df = dm.active_df
        table = create_data_grid(df, preview_mode=False)
        stats = create_data_stats(df)
        return df.to_json(date_format='iso', orient='split'), table, stats

    # 如果点击了加载示例按钮
    if n_clicks:
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
            'age': ['25', '30', '35', '28', '32', '29', '31', '27'],
            'city': ['NYC', 'LA', 'SF', 'NYC', 'LA', 'SF', 'NYC', 'LA'],
            'salary': [50000, 60000, 75000, 55000, 65000, 58000, 62000, 53000],
            'department': ['Sales', 'Engineering', 'Sales', 'Engineering', 'Sales', 'Engineering', 'Sales', 'Engineering']
        })

        # 存入 DataManager
        dm.add_dataset("示例数据", df, source="sample:demo")

        table = create_data_grid(df, preview_mode=False)
        stats = create_data_stats(df)
        return df.to_json(date_format='iso', orient='split'), table, stats

    # 没有数据时返回空状态
    return no_update, no_update, no_update


# ============================================================================
# 回调：点击操作按钮 → 打开配置模态框
# ============================================================================

@callback(
    Output('operation-modal', 'is_open'),
    Output('operation-modal-title', 'children'),
    Output('operation-modal-body', 'children'),
    Output('pending-operation-type', 'data'),
    Output('toolbox-offcanvas', 'is_open'),
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
    Input('btn-open-toolbox', 'n_clicks'),
    State('original-data-store', 'data'),
    State('preview-data-store', 'data'),
    State('toolbox-offcanvas', 'is_open'),
    prevent_initial_call=True
)
def open_operation_modal(*args):
    triggered_id = ctx.triggered_id

    original_data = args[-3]
    preview_data = args[-2]
    toolbox_is_open = args[-1]

    if triggered_id == 'btn-open-toolbox':
        return False, dash.no_update, dash.no_update, dash.no_update, not toolbox_is_open

    if triggered_id == 'btn-modal-cancel':
        return False, dash.no_update, dash.no_update, None, False

    if triggered_id not in OPERATION_BUTTONS:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # 使用最新的预览数据，以便列名反映已执行的操作
    data_to_use = preview_data or original_data
    columns = _get_columns_from_store(data_to_use)

    if not columns:
        return True, "提示", html.Div([
            dbc.Alert("请先加载数据", color="warning"),
        ]), None, False

    op_type, op_name = OPERATION_BUTTONS[triggered_id]
    form = _build_form_for_operation(op_type, columns)

    return True, f"⚙️ {op_name}配置", form, op_type, False


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
    State('modal-filter-tabs', 'active_tab'),
    State('modal-param-checklist', 'value'),
    prevent_initial_call=True
)
def apply_operation(
    apply_clicks, op_type, original_data, current_pipeline,
    column, operator, value, columns_multi, new_name,
    ascending, target_type, method, fill_value, keep,
    delimiter, max_split, old_value, new_value,
    case_type, pattern, replacement, is_regex,
    start, end, bins, bin_method, norm_method,
    how, threshold, expression, filter_active_tab, filter_checklist
):
    """在用户填写参数后执行操作"""
    if not op_type or not original_data:
        return False, no_update, no_update, no_update, no_update, no_update

    # 根据操作类型构建参数
    params = _build_params(
        op_type, column, operator, value, columns_multi, new_name,
        ascending, target_type, method, fill_value, keep,
        delimiter, max_split, old_value, new_value,
        case_type, pattern, replacement, is_regex,
        start, end, bins, bin_method, norm_method,
        how, threshold, expression, filter_active_tab, filter_checklist
    )

    if params is None:
        return False, no_update, no_update, no_update, no_update, no_update

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
        return False, no_update, no_update, no_update, no_update, no_update

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
    how, threshold, expression, filter_active_tab=None, filter_checklist=None
):
    """根据操作类型从表单字段值构建参数字典"""

    if op_type == 'filter':
        if not column:
            return None
            
        if filter_active_tab == 'tab-checklist':
            # Checklist 模式：转换为 isin
            if not filter_checklist:
                # 没有任何勾选，等效于清空数据 (或者根据需求抛错)
                return {'column': column, 'operator': 'isin', 'value': []}
            return {'column': column, 'operator': 'isin', 'value': filter_checklist}
        else:
            # 基础 Condition 模式
            if not operator:
                return None
            # 对于 isnull / notnull, 不需要 value
            if operator in ['isnull', 'notnull']:
                return {'column': column, 'operator': operator, 'value': ''}
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
# 回调：代码折叠切换
# ============================================================================

@callback(
    Output('inline-code-collapse', 'is_open'),
    Output('inline-code-collapse-icon', 'className'),
    Input('btn-toggle-inline-code', 'n_clicks'),
    State('inline-code-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_code_collapse(n_clicks, is_open):
    """切换侧边代码展示区的折叠状态"""
    new_state = not is_open
    icon_class = "bi bi-chevron-up" if new_state else "bi bi-chevron-down"
    return new_state, icon_class


# ============================================================================
# 回调：代码生成
# ============================================================================

@callback(
    Output('inline-code-display', 'children'),
    Input('pipeline-store', 'data'),
    prevent_initial_call=False
)
def handle_code_preview(pipeline):
    """处理代码预览 - 并在时更新内联显示"""
    # 获取数据集名称
    dm = DataManager()
    dataset_name = dm.active_name if dm.active_name else "data.csv"

    # 生成代码
    if not pipeline:
        code = "# 暂无操作\n# 请先执行一些数据操作"
    else:
        code = code_generator.generate_code(
            pipeline,
            data_source=dataset_name,
            include_imports=True,
            include_comments=True
        )

    # 创建内联代码显示
    inline_display = html.Pre([
        html.Code(code, className="language-python", style={
            "color": "var(--text-primary)",
            "fontSize": "0.875rem",
            "fontFamily": "monospace"
        })
    ], style={
        "backgroundColor": "var(--bg-primary)",
        "padding": "1rem",
        "borderRadius": "8px",
        "maxHeight": "400px",
        "overflowY": "auto"
    })

    return inline_display


@callback(
    Output('download-workshop-py-file', 'data'),
    Input('btn-download-inline-code', 'n_clicks'),
    State('pipeline-store', 'data'),
    prevent_initial_call=True
)
def download_workshop_python(n_clicks, pipeline):
    if not n_clicks:
        return no_update

    bundle = build_workshop_export(pipeline or [])
    return dcc.send_string(bundle.py_content, filename=bundle.py_filename)


@callback(
    Output('download-workshop-ipynb-file', 'data'),
    Input('btn-download-inline-notebook', 'n_clicks'),
    State('pipeline-store', 'data'),
    prevent_initial_call=True
)
def download_workshop_notebook(n_clicks, pipeline):
    if not n_clicks:
        return no_update

    bundle = build_workshop_export(pipeline or [])
    return dict(content=bundle.ipynb_content, filename=bundle.ipynb_filename)

# ============================================================================
# 高级过滤联动配置回调 (Power Query Style)
# ============================================================================

@callback(
    [Output('modal-filter-options-container', 'style'),
     Output('modal-param-checklist', 'options'),
     Output('modal-param-checklist', 'value')],
    [Input('modal-param-column', 'value'),
     Input('modal-filter-search', 'value'),
     Input('btn-filter-select-all', 'n_clicks'),
     Input('btn-filter-clear-all', 'n_clicks')],
    [State('original-data-store', 'data'),
     State('pending-operation-type', 'data'),
     State('modal-param-checklist', 'options')],
    prevent_initial_call=True
)
def update_filter_options(column, search_term, select_all, clear_all, data, op_type, current_options):
    if op_type != 'filter' or not data:
        return {'display': 'none'}, [], []
        
    if not column:
        return {'display': 'none'}, [], []
        
    ctx_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    
    # 无论怎么点，全选清空都只操作当前的 options
    if ctx_id == 'btn-filter-select-all' and current_options:
        return {'display': 'block'}, current_options, [opt['value'] for opt in current_options]
        
    if ctx_id == 'btn-filter-clear-all' and current_options:
        return {'display': 'block'}, current_options, []
        
    try:
        df = pd.read_json(data, orient='split')
        if column not in df.columns:
            return {'display': 'none'}, [], []
            
        # 提取高频唯一值 (取前 200 个防卡顿)
        unique_vals = df[column].dropna().unique()
        # 尽可能保证排序
        try:
             unique_vals = sorted(unique_vals)
        except TypeError:
             pass # 如果遇到混用的数据类型无法 sort，跳过
        
        unique_vals = list(unique_vals)[:200]
        
        # 搜索过滤
        if search_term:
            term = str(search_term).lower()
            filtered_vals = [v for v in unique_vals if term in str(v).lower()]
        else:
            filtered_vals = unique_vals
            
        opts = [{'label': str(v), 'value': str(v)} for v in filtered_vals]
        
        # 搜索时不覆盖已勾选的 value 逻辑比较复杂，这里简单处理为搜出什么默认全都不选，需用户手动勾。
        # 如果是首次加载列，默认全选。
        if ctx_id == 'modal-param-column':
            init_vals = [str(v) for v in filtered_vals]
            return {'display': 'block'}, opts, init_vals
             
        return {'display': 'block'}, opts, dash.no_update
        
    except Exception as e:
        print(f"Error fetching unique values: {e}")
        return {'display': 'block'}, [], []


# ============================================================================
# 回调：左侧抽屉折叠/展开
# ============================================================================

@callback(
    Output('left-drawer', 'style'),
    Input('btn-toggle-left-drawer', 'n_clicks'),
    State('left-drawer', 'style'),
    prevent_initial_call=True
)
def toggle_left_drawer(n_clicks, current_style):
    if not current_style:
        current_style = {}
    
    # 复制字典避免直接修改引用
    new_style = dict(current_style)
    current_width = new_style.get("width", "280px")
    
    if current_width == "0px":
        new_style["width"] = "300px"
        new_style["opacity"] = "1"
        new_style["borderWidth"] = "1px"
        new_style["padding"] = "0"
    else:
        new_style["width"] = "0px"
        new_style["opacity"] = "0"
        new_style["borderWidth"] = "0px"
        new_style["padding"] = "0"
        
    return new_style


@callback(
    Output("project-page-store", "data", allow_duplicate=True),
    Input("original-data-store", "data"),
    Input("preview-data-store", "data"),
    Input("pipeline-store", "data"),
    Input("undo-redo-store", "data"),
    State("project-page-store", "data"),
    prevent_initial_call=True,
)
def sync_workshop_project_state(original_data, preview_data, pipeline, undo_redo_state, project_state):
    state = dict(project_state or {})
    state["data_workshop"] = {
        "original_data": original_data,
        "preview_data": preview_data,
        "pipeline": pipeline or [],
        "undo_redo_state": undo_redo_state or {"can_undo": False, "can_redo": False},
    }
    return state


@callback(
    Output("original-data-store", "data", allow_duplicate=True),
    Output("preview-data-store", "data", allow_duplicate=True),
    Output("pipeline-store", "data", allow_duplicate=True),
    Output("undo-redo-store", "data", allow_duplicate=True),
    Output("data-table-container", "children", allow_duplicate=True),
    Output("data-stats", "children", allow_duplicate=True),
    Input("project-restore-store", "data"),
    Input("url", "pathname"),
    prevent_initial_call=True,
)
def restore_workshop_project_state(project_restore, pathname):
    if pathname != "/workshop" or not project_restore:
        return no_update, no_update, no_update, no_update, no_update, no_update

    page_state = (project_restore.get("page_state") or {}).get("data_workshop")
    if not page_state:
        return no_update, no_update, no_update, no_update, no_update, no_update

    original_data = page_state.get("original_data")
    preview_data = page_state.get("preview_data")
    pipeline = page_state.get("pipeline", [])
    undo_redo_state = page_state.get("undo_redo_state", {"can_undo": False, "can_redo": False})
    active_json = preview_data or original_data
    if not active_json:
        return original_data, preview_data, pipeline, undo_redo_state, no_update, no_update

    df = pd.read_json(active_json, orient="split")
    table = create_data_grid(df, preview_mode=bool(preview_data))
    stats = create_data_stats(df)
    return original_data, preview_data, pipeline, undo_redo_state, table, stats
