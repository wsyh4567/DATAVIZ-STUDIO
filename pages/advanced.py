# -*- coding: utf-8 -*-
"""DataViz Studio — 高级工具页面

提供数据变形工具：透视表、逆透视(Melt)、合并/连接数据集、随机抽样等。
"""

from __future__ import annotations

from dash import html, dcc, callback, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

from core.data_manager import DataManager


def create_advanced_page() -> html.Div:
    """创建高级工具页面"""
    dm = DataManager()
    df = dm.active_df

    if df is None or df.empty:
        return html.Div([
            html.Div(
                className="dvs-empty",
                style={"minHeight": "60vh"},
                children=[
                    html.Div("⚡", className="dvs-empty__icon"),
                    html.Div("高级工具", className="dvs-empty__text"),
                    html.Div("请先在数据中心加载数据集", style={
                        "color": "var(--text-muted)", "fontSize": "var(--text-sm)"
                    }),
                ],
            )
        ])

    columns = list(df.columns)
    col_options = [{'label': c, 'value': c} for c in columns]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_options = [{'label': c, 'value': c} for c in numeric_cols]

    # 数据集列表
    ds_names = dm.dataset_names
    ds_options = [{'label': n, 'value': n} for n in ds_names]

    return dbc.Container([
        # 标题
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="bi bi-tools me-3", style={"color": "var(--accent)"}),
                    "高级工具"
                ], className="mb-1", style={"fontWeight": "600"}),
                html.P("数据变形、合并、抽样等高级操作",
                       style={"color": "var(--text-muted)", "fontSize": "0.875rem"})
            ]),
        ], className="mb-4"),

        # 工具选择
        dbc.Tabs([
            # ─── 透视表 ──────────────────────────────
            dbc.Tab(label="透视表", tab_id="tab-pivot", children=[
                dbc.Card([
                    dbc.CardBody([
                        html.P("将长格式数据重组为宽格式交叉表", className="text-muted mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("行索引", className="form-label"),
                                dcc.Dropdown(id='adv-pivot-index', options=col_options, placeholder="选择行索引列"),
                            ], width=3),
                            dbc.Col([
                                html.Label("列头", className="form-label"),
                                dcc.Dropdown(id='adv-pivot-columns', options=col_options, placeholder="选择列头字段"),
                            ], width=3),
                            dbc.Col([
                                html.Label("值", className="form-label"),
                                dcc.Dropdown(id='adv-pivot-values', options=num_options, placeholder="选择值字段"),
                            ], width=3),
                            dbc.Col([
                                html.Label("聚合函数", className="form-label"),
                                dcc.Dropdown(id='adv-pivot-aggfunc', options=[
                                    {'label': '均值', 'value': 'mean'},
                                    {'label': '求和', 'value': 'sum'},
                                    {'label': '计数', 'value': 'count'},
                                    {'label': '最大', 'value': 'max'},
                                    {'label': '最小', 'value': 'min'},
                                ], value='mean', clearable=False),
                            ], width=3),
                        ], className="mb-3"),
                        dbc.Button("执行透视", id="btn-run-pivot", color="primary"),
                        html.Div(id="pivot-result", className="mt-3"),
                    ])
                ], className="mt-3", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ]),

            # ─── 逆透视 (Melt) ────────────────────────
            dbc.Tab(label="逆透视 (Melt)", tab_id="tab-melt", children=[
                dbc.Card([
                    dbc.CardBody([
                        html.P("将宽格式数据转换为长格式", className="text-muted mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("ID 列（保留列）", className="form-label"),
                                dcc.Dropdown(id='adv-melt-id', options=col_options, multi=True,
                                           placeholder="选择要保留的列"),
                            ], width=4),
                            dbc.Col([
                                html.Label("值列（要融化的列）", className="form-label"),
                                dcc.Dropdown(id='adv-melt-value', options=col_options, multi=True,
                                           placeholder="留空=融化所有非ID列"),
                            ], width=4),
                            dbc.Col([
                                html.Label("变量名 / 值名", className="form-label"),
                                dbc.Input(id='adv-melt-var-name', type='text', value='variable',
                                         placeholder='变量列名', size='sm', className='mb-1'),
                                dbc.Input(id='adv-melt-val-name', type='text', value='value',
                                         placeholder='值列名', size='sm'),
                            ], width=4),
                        ], className="mb-3"),
                        dbc.Button("执行逆透视", id="btn-run-melt", color="primary"),
                        html.Div(id="melt-result", className="mt-3"),
                    ])
                ], className="mt-3", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ]),

            # ─── 合并数据集 ────────────────────────────
            dbc.Tab(label="合并数据集", tab_id="tab-merge", children=[
                dbc.Card([
                    dbc.CardBody([
                        html.P("将两个数据集按键合并 (类似 SQL JOIN)", className="text-muted mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("右表数据集", className="form-label"),
                                dcc.Dropdown(id='adv-merge-right', options=ds_options,
                                           placeholder="选择要合并的数据集"),
                            ], width=3),
                            dbc.Col([
                                html.Label("左表键列", className="form-label"),
                                dcc.Dropdown(id='adv-merge-left-on', options=col_options,
                                           placeholder="活跃数据集的键列"),
                            ], width=3),
                            dbc.Col([
                                html.Label("右表键列", className="form-label"),
                                dcc.Dropdown(id='adv-merge-right-on', options=[],
                                           placeholder="先选择右表"),
                            ], width=3),
                            dbc.Col([
                                html.Label("合并方式", className="form-label"),
                                dcc.Dropdown(id='adv-merge-how', options=[
                                    {'label': '内连接 (inner)', 'value': 'inner'},
                                    {'label': '左连接 (left)', 'value': 'left'},
                                    {'label': '右连接 (right)', 'value': 'right'},
                                    {'label': '外连接 (outer)', 'value': 'outer'},
                                ], value='inner', clearable=False),
                            ], width=3),
                        ], className="mb-3"),
                        dbc.Button("执行合并", id="btn-run-merge", color="primary"),
                        html.Div(id="merge-result", className="mt-3"),
                    ])
                ], className="mt-3", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ]),

            # ─── 随机抽样 ──────────────────────────────
            dbc.Tab(label="随机抽样", tab_id="tab-sample", children=[
                dbc.Card([
                    dbc.CardBody([
                        html.P("从数据集中随机抽取样本", className="text-muted mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("抽样方式", className="form-label"),
                                dcc.Dropdown(id='adv-sample-method', options=[
                                    {'label': '按数量', 'value': 'n'},
                                    {'label': '按比例', 'value': 'frac'},
                                ], value='n', clearable=False),
                            ], width=3),
                            dbc.Col([
                                html.Label("数量 / 比例", className="form-label"),
                                dbc.Input(id='adv-sample-value', type='number', value=100, min=1, step=1),
                            ], width=3),
                            dbc.Col([
                                html.Label("分层列（可选）", className="form-label"),
                                dcc.Dropdown(id='adv-sample-stratify', options=col_options,
                                           placeholder="按此列分层抽样", clearable=True),
                            ], width=3),
                            dbc.Col([
                                html.Label("随机种子", className="form-label"),
                                dbc.Input(id='adv-sample-seed', type='number', value=42),
                            ], width=3),
                        ], className="mb-3"),
                        dbc.Button("执行抽样", id="btn-run-sample", color="primary"),
                        html.Div(id="sample-result", className="mt-3"),
                    ])
                ], className="mt-3", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ]),

            # ─── 纵向拼接 ──────────────────────────────
            dbc.Tab(label="纵向拼接", tab_id="tab-concat", children=[
                dbc.Card([
                    dbc.CardBody([
                        html.P("将多个数据集纵向拼接（堆叠）", className="text-muted mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("选择要拼接的数据集", className="form-label"),
                                dcc.Dropdown(id='adv-concat-datasets', options=ds_options, multi=True,
                                           placeholder="选择一个或多个数据集"),
                            ], width=6),
                            dbc.Col([
                                html.Label("忽略索引", className="form-label"),
                                dcc.Dropdown(id='adv-concat-ignore-index', options=[
                                    {'label': '是', 'value': 'true'},
                                    {'label': '否', 'value': 'false'},
                                ], value='true', clearable=False),
                            ], width=3),
                        ], className="mb-3"),
                        dbc.Button("执行拼接", id="btn-run-concat", color="primary"),
                        html.Div(id="concat-result", className="mt-3"),
                    ])
                ], className="mt-3", style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
            ]),

        ], id="advanced-tools-tabs", active_tab="tab-pivot"),

        # 存储
        dcc.Store(id="adv-result-store"),

    ], fluid=True, className="py-4")


# ============================================================================
# 回调
# ============================================================================

# 右表变更时刷新右表键列选项
@callback(
    Output('adv-merge-right-on', 'options'),
    Input('adv-merge-right', 'value'),
    prevent_initial_call=True
)
def update_right_columns(right_name):
    if not right_name:
        return []
    dm = DataManager()
    rdf = dm.get_dataset(right_name)
    if rdf is None:
        return []
    return [{'label': c, 'value': c} for c in rdf.columns]


# ── 透视表 ───────────────────────────────────────────────

@callback(
    Output('pivot-result', 'children'),
    Input('btn-run-pivot', 'n_clicks'),
    State('adv-pivot-index', 'value'),
    State('adv-pivot-columns', 'value'),
    State('adv-pivot-values', 'value'),
    State('adv-pivot-aggfunc', 'value'),
    prevent_initial_call=True
)
def run_pivot(n, index, columns, values, aggfunc):
    if not all([index, columns, values]):
        return dbc.Alert("请填写所有必填参数", color="warning")
    dm = DataManager()
    df = dm.active_df
    try:
        result = df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc)
        result_flat = result.reset_index()
        result_flat.columns = [str(c) for c in result_flat.columns]

        # 保存结果
        dm.add_dataset(f"pivot_{index}_{columns}", result_flat, source="advanced:pivot")

        return html.Div([
            dbc.Alert(f"透视完成: {result_flat.shape[0]} 行 × {result_flat.shape[1]} 列（已保存为新数据集）", color="success"),
            dbc.Table.from_dataframe(result_flat.head(50), striped=True, bordered=True, hover=True, size='sm'),
        ])
    except Exception as e:
        return dbc.Alert(f"透视失败: {e}", color="danger")


# ── 逆透视 ───────────────────────────────────────────────

@callback(
    Output('melt-result', 'children'),
    Input('btn-run-melt', 'n_clicks'),
    State('adv-melt-id', 'value'),
    State('adv-melt-value', 'value'),
    State('adv-melt-var-name', 'value'),
    State('adv-melt-val-name', 'value'),
    prevent_initial_call=True
)
def run_melt(n, id_vars, value_vars, var_name, val_name):
    if not id_vars:
        return dbc.Alert("请至少选择一个 ID 列", color="warning")
    dm = DataManager()
    df = dm.active_df
    try:
        kwargs = {
            'id_vars': id_vars,
            'var_name': var_name or 'variable',
            'value_name': val_name or 'value',
        }
        if value_vars:
            kwargs['value_vars'] = value_vars
        result = df.melt(**kwargs)
        dm.add_dataset("melted", result, source="advanced:melt")
        return html.Div([
            dbc.Alert(f"逆透视完成: {result.shape[0]} 行 × {result.shape[1]} 列（已保存）", color="success"),
            dbc.Table.from_dataframe(result.head(50), striped=True, bordered=True, hover=True, size='sm'),
        ])
    except Exception as e:
        return dbc.Alert(f"逆透视失败: {e}", color="danger")


# ── 合并 ─────────────────────────────────────────────────

@callback(
    Output('merge-result', 'children'),
    Input('btn-run-merge', 'n_clicks'),
    State('adv-merge-right', 'value'),
    State('adv-merge-left-on', 'value'),
    State('adv-merge-right-on', 'value'),
    State('adv-merge-how', 'value'),
    prevent_initial_call=True
)
def run_merge(n, right_name, left_on, right_on, how):
    if not all([right_name, left_on, right_on]):
        return dbc.Alert("请填写所有必填参数", color="warning")
    dm = DataManager()
    left_df = dm.active_df
    right_df = dm.get_dataset(right_name)
    if right_df is None:
        return dbc.Alert("右表数据集不存在", color="danger")
    try:
        result = left_df.merge(right_df, left_on=left_on, right_on=right_on, how=how)
        dm.add_dataset(f"merged_{right_name}", result, source="advanced:merge")
        return html.Div([
            dbc.Alert(f"合并完成: {result.shape[0]} 行 × {result.shape[1]} 列（已保存）", color="success"),
            dbc.Table.from_dataframe(result.head(50), striped=True, bordered=True, hover=True, size='sm'),
        ])
    except Exception as e:
        return dbc.Alert(f"合并失败: {e}", color="danger")


# ── 抽样 ─────────────────────────────────────────────────

@callback(
    Output('sample-result', 'children'),
    Input('btn-run-sample', 'n_clicks'),
    State('adv-sample-method', 'value'),
    State('adv-sample-value', 'value'),
    State('adv-sample-stratify', 'value'),
    State('adv-sample-seed', 'value'),
    prevent_initial_call=True
)
def run_sample(n, method, value, stratify, seed):
    dm = DataManager()
    df = dm.active_df
    try:
        kwargs = {'random_state': int(seed) if seed else 42}

        if method == 'frac':
            frac = float(value)
            if frac > 1:
                frac = frac / 100
            kwargs['frac'] = frac
        else:
            kwargs['n'] = min(int(value), len(df))

        if stratify and stratify in df.columns:
            # 分层抽样：按组抽样
            groups = df.groupby(stratify)
            if method == 'frac':
                result = groups.apply(lambda x: x.sample(frac=kwargs['frac'],
                    random_state=kwargs['random_state'])).reset_index(drop=True)
            else:
                per_group = max(1, kwargs['n'] // len(groups))
                result = groups.apply(lambda x: x.sample(n=min(per_group, len(x)),
                    random_state=kwargs['random_state'])).reset_index(drop=True)
        else:
            result = df.sample(**kwargs)

        dm.add_dataset("sample", result, source="advanced:sample")
        return html.Div([
            dbc.Alert(f"抽样完成: {result.shape[0]} 行（已保存为新数据集）", color="success"),
            dbc.Table.from_dataframe(result.head(50), striped=True, bordered=True, hover=True, size='sm'),
        ])
    except Exception as e:
        return dbc.Alert(f"抽样失败: {e}", color="danger")


# ── 拼接 ─────────────────────────────────────────────────

@callback(
    Output('concat-result', 'children'),
    Input('btn-run-concat', 'n_clicks'),
    State('adv-concat-datasets', 'value'),
    State('adv-concat-ignore-index', 'value'),
    prevent_initial_call=True
)
def run_concat(n, dataset_names, ignore_index):
    if not dataset_names:
        return dbc.Alert("请至少选择一个数据集", color="warning")
    dm = DataManager()
    dfs = [dm.active_df]
    for name in dataset_names:
        rdf = dm.get_dataset(name)
        if rdf is not None:
            dfs.append(rdf)
    try:
        result = pd.concat(dfs, ignore_index=(ignore_index == 'true'))
        dm.add_dataset("concatenated", result, source="advanced:concat")
        return html.Div([
            dbc.Alert(f"拼接完成: {result.shape[0]} 行 × {result.shape[1]} 列（已保存）", color="success"),
            dbc.Table.from_dataframe(result.head(50), striped=True, bordered=True, hover=True, size='sm'),
        ])
    except Exception as e:
        return dbc.Alert(f"拼接失败: {e}", color="danger")
