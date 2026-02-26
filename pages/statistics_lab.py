# -*- coding: utf-8 -*-
"""
统计实验室页面 - 统计分析功能
"""
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from core.data_manager import DataManager
from services.stats_service import StatsService
import pandas as pd
import numpy as np


def layout():
    """统计实验室页面布局"""
    return html.Div([
        # 页面标题
        html.Div([
            html.H3("🧮 统计实验室", className="page-title"),
            html.P("统计分析与假设检验", className="page-subtitle")
        ], className="page-header"),

        # 主内容区域
        html.Div([
            # 左侧功能菜单
            html.Div([
                html.H5("分析功能", className="mb-3"),

                dbc.Nav([
                    dbc.NavLink("描述性统计", href="#", id="nav-descriptive", active=True),
                    dbc.NavLink("相关性分析", href="#", id="nav-correlation"),
                    dbc.NavLink("分组聚合", href="#", id="nav-groupby"),
                    dbc.NavLink("异常值检测", href="#", id="nav-outliers"),
                    dbc.NavLink("假设检验", href="#", id="nav-hypothesis"),
                ], vertical=True, pills=True),

            ], className="stats-menu"),

            # 主分析区域
            html.Div([
                html.Div(id="stats-content-area"),
            ], className="stats-main"),

        ], className="stats-container"),

        # 存储当前选择的功能
        dcc.Store(id="current-stats-function", data="descriptive"),

    ], className="page-container")


# 切换功能
@callback(
    [Output("current-stats-function", "data"),
     Output("nav-descriptive", "active"),
     Output("nav-correlation", "active"),
     Output("nav-groupby", "active"),
     Output("nav-outliers", "active"),
     Output("nav-hypothesis", "active")],
    [Input("nav-descriptive", "n_clicks"),
     Input("nav-correlation", "n_clicks"),
     Input("nav-groupby", "n_clicks"),
     Input("nav-outliers", "n_clicks"),
     Input("nav-hypothesis", "n_clicks")],
    prevent_initial_call=True
)
def switch_function(*args):
    from dash import ctx

    if not ctx.triggered:
        return "descriptive", True, False, False, False, False

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    active_states = {
        "nav-descriptive": ("descriptive", True, False, False, False, False),
        "nav-correlation": ("correlation", False, True, False, False, False),
        "nav-groupby": ("groupby", False, False, True, False, False),
        "nav-outliers": ("outliers", False, False, False, True, False),
        "nav-hypothesis": ("hypothesis", False, False, False, False, True),
    }

    return active_states.get(button_id, ("descriptive", True, False, False, False, False))


# 更新内容区域
@callback(
    Output("stats-content-area", "children"),
    Input("current-stats-function", "data")
)
def update_content(function):
    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return html.Div([
            dbc.Alert("请先在数据中心加载数据集", color="warning", className="mt-3")
        ])

    if function == "descriptive":
        return render_descriptive_stats(df)
    elif function == "correlation":
        return render_correlation_analysis(df)
    elif function == "groupby":
        return render_groupby_analysis(df)
    elif function == "outliers":
        return render_outlier_detection(df)
    elif function == "hypothesis":
        return render_hypothesis_testing(df)

    return html.Div("未知功能")


def render_descriptive_stats(df):
    """渲染描述性统计"""
    columns = df.columns.tolist()

    return html.Div([
        html.H4("描述性统计", className="mb-3"),

        dbc.Row([
            dbc.Col([
                html.Label("选择列："),
                dcc.Dropdown(
                    id="desc-column-select",
                    options=[{"label": col, "value": col} for col in columns],
                    value=columns[0] if columns else None,
                    placeholder="选择要分析的列"
                ),
            ], width=6),
        ], className="mb-3"),

        html.Div(id="descriptive-stats-output"),
    ])


@callback(
    Output("descriptive-stats-output", "children"),
    Input("desc-column-select", "value")
)
def show_descriptive_stats(column):
    if not column:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return None

    stats_service = StatsService()
    stats = stats_service.descriptive_stats(df, column)
    summary = stats_service.generate_summary(stats)

    # 创建统计卡片
    cards = []

    # 基本信息卡片
    cards.append(dbc.Card([
        dbc.CardBody([
            html.H5("基本信息", className="card-title"),
            html.Hr(),
            html.P([html.Strong("数据类型: "), stats['dtype']]),
            html.P([html.Strong("有效值: "), f"{stats['count']:,}"]),
            html.P([html.Strong("缺失值: "), f"{stats['missing']:,} ({stats['missing_pct']:.1f}%)"]),
        ])
    ], className="mb-3"))

    # 数值列统计
    if 'mean' in stats:
        cards.append(dbc.Card([
            dbc.CardBody([
                html.H5("数值统计", className="card-title"),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.P([html.Strong("均值: "), f"{stats['mean']:.2f}"]),
                        html.P([html.Strong("中位数: "), f"{stats['median']:.2f}"]),
                        html.P([html.Strong("标准差: "), f"{stats['std']:.2f}"]),
                    ], width=6),
                    dbc.Col([
                        html.P([html.Strong("最小值: "), f"{stats['min']:.2f}"]),
                        html.P([html.Strong("最大值: "), f"{stats['max']:.2f}"]),
                        html.P([html.Strong("范围: "), f"{stats['max'] - stats['min']:.2f}"]),
                    ], width=6),
                ]),
                html.Hr(),
                html.P([html.Strong("分布特征: "), stats.get('distribution', '未知')]),
                html.P([html.Strong("偏度: "), f"{stats['skewness']:.2f}"]),
                html.P([html.Strong("峰度: "), f"{stats['kurtosis']:.2f}"]),
            ])
        ], className="mb-3"))

        # 绘制直方图
        fig = px.histogram(df, x=column, nbins=30, title=f"{column} 分布图")
        fig.add_vline(x=stats['mean'], line_dash="dash", line_color="red",
                     annotation_text="均值", annotation_position="top")
        fig.add_vline(x=stats['median'], line_dash="dash", line_color="green",
                     annotation_text="中位数", annotation_position="top")

        cards.append(dcc.Graph(figure=fig, className="mb-3"))

        # 箱线图
        fig_box = px.box(df, y=column, title=f"{column} 箱线图")
        cards.append(dcc.Graph(figure=fig_box, className="mb-3"))

    # 分类列统计
    elif 'unique' in stats:
        cards.append(dbc.Card([
            dbc.CardBody([
                html.H5("分类统计", className="card-title"),
                html.Hr(),
                html.P([html.Strong("唯一值数量: "), f"{stats['unique']}"]),
                html.P([html.Strong("最常见值: "), stats['top']]),
                html.P([html.Strong("出现次数: "), f"{stats['top_freq']:,} ({stats['top_pct']:.1f}%)"]),
            ])
        ], className="mb-3"))

        # 绘制频率条形图
        value_counts = df[column].value_counts().head(20)
        fig = px.bar(x=value_counts.index, y=value_counts.values,
                    title=f"{column} 频率分布（前20）",
                    labels={'x': column, 'y': '频数'})
        cards.append(dcc.Graph(figure=fig, className="mb-3"))

    # 自然语言摘要
    cards.insert(0, dbc.Alert([
        html.H5("📊 统计摘要", className="alert-heading"),
        html.P(summary, className="mb-0")
    ], color="info", className="mb-3"))

    return html.Div(cards)


def render_correlation_analysis(df):
    """渲染相关性分析"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        return dbc.Alert("数据集中没有数值列，无法进行相关性分析", color="warning")

    return html.Div([
        html.H4("相关性分析", className="mb-3"),

        dbc.Row([
            dbc.Col([
                html.Label("相关系数方法："),
                dcc.Dropdown(
                    id="corr-method-select",
                    options=[
                        {"label": "Pearson（线性相关）", "value": "pearson"},
                        {"label": "Spearman（秩相关）", "value": "spearman"},
                        {"label": "Kendall（秩相关）", "value": "kendall"},
                    ],
                    value="pearson"
                ),
            ], width=4),
            dbc.Col([
                html.Label("相关阈值："),
                dcc.Slider(
                    id="corr-threshold-slider",
                    min=0,
                    max=1,
                    step=0.1,
                    value=0.5,
                    marks={i/10: f"{i/10:.1f}" for i in range(0, 11, 2)},
                ),
            ], width=4),
        ], className="mb-3"),

        html.Div(id="correlation-output"),
    ])


@callback(
    Output("correlation-output", "children"),
    [Input("corr-method-select", "value"),
     Input("corr-threshold-slider", "value")]
)
def show_correlation_analysis(method, threshold):
    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return None

    stats_service = StatsService()

    try:
        # 计算相关矩阵
        corr_matrix = stats_service.correlation_matrix(df, method=method)

        # 绘制热力图
        fig = px.imshow(corr_matrix,
                       labels=dict(color="相关系数"),
                       x=corr_matrix.columns,
                       y=corr_matrix.columns,
                       color_continuous_scale="RdBu_r",
                       zmin=-1, zmax=1,
                       title="相关矩阵热力图")
        fig.update_layout(height=600)

        # 获取强相关变量对
        pairs = stats_service.correlation_pairs(df, threshold=threshold, method=method)

        pairs_table = None
        if pairs:
            pairs_table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("变量1"),
                        html.Th("变量2"),
                        html.Th("相关系数"),
                        html.Th("强度"),
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(pair['var1']),
                        html.Td(pair['var2']),
                        html.Td(f"{pair['correlation']:.3f}"),
                        html.Td(pair['strength']),
                    ]) for pair in pairs[:20]  # 只显示前20对
                ])
            ], bordered=True, hover=True, striped=True, className="mt-3")
        else:
            pairs_table = dbc.Alert(f"没有找到相关系数绝对值 ≥ {threshold} 的变量对", color="info", className="mt-3")

        return html.Div([
            dcc.Graph(figure=fig),
            html.H5(f"强相关变量对（阈值 ≥ {threshold}）", className="mt-4 mb-3"),
            pairs_table,
        ])

    except Exception as e:
        return dbc.Alert(f"分析失败: {str(e)}", color="danger")


def render_groupby_analysis(df):
    """渲染分组聚合分析"""
    columns = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    return html.Div([
        html.H4("分组聚合分析", className="mb-3"),

        dbc.Row([
            dbc.Col([
                html.Label("分组列："),
                dcc.Dropdown(
                    id="groupby-column-select",
                    options=[{"label": col, "value": col} for col in columns],
                    placeholder="选择分组列"
                ),
            ], width=4),
            dbc.Col([
                html.Label("聚合列："),
                dcc.Dropdown(
                    id="agg-column-select",
                    options=[{"label": col, "value": col} for col in numeric_cols],
                    placeholder="选择聚合列"
                ),
            ], width=4),
            dbc.Col([
                html.Label("聚合函数："),
                dcc.Dropdown(
                    id="agg-func-select",
                    options=[
                        {"label": "求和", "value": "sum"},
                        {"label": "平均值", "value": "mean"},
                        {"label": "中位数", "value": "median"},
                        {"label": "计数", "value": "count"},
                        {"label": "最小值", "value": "min"},
                        {"label": "最大值", "value": "max"},
                        {"label": "标准差", "value": "std"},
                    ],
                    value="mean"
                ),
            ], width=4),
        ], className="mb-3"),

        dbc.Button("执行分析", id="btn-run-groupby", color="primary", className="mb-3"),

        html.Div(id="groupby-output"),
    ])


@callback(
    Output("groupby-output", "children"),
    Input("btn-run-groupby", "n_clicks"),
    [State("groupby-column-select", "value"),
     State("agg-column-select", "value"),
     State("agg-func-select", "value")],
    prevent_initial_call=True
)
def show_groupby_analysis(n_clicks, group_col, agg_col, agg_func):
    if not all([group_col, agg_col, agg_func]):
        return dbc.Alert("请选择所有参数", color="warning")

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return None

    stats_service = StatsService()

    try:
        result = stats_service.group_aggregate(df, [group_col], agg_col, agg_func)

        # 绘制图表
        fig = px.bar(result, x=group_col, y=result.columns[-1],
                    title=f"{group_col} 分组的 {agg_col} {agg_func}")

        return html.Div([
            dcc.Graph(figure=fig),
            html.H5("聚合结果", className="mt-3 mb-2"),
            dbc.Table.from_dataframe(result.head(50), striped=True, bordered=True, hover=True),
        ])

    except Exception as e:
        return dbc.Alert(f"分析失败: {str(e)}", color="danger")


def render_outlier_detection(df):
    """渲染异常值检测"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        return dbc.Alert("数据集中没有数值列", color="warning")

    return html.Div([
        html.H4("异常值检测", className="mb-3"),

        dbc.Row([
            dbc.Col([
                html.Label("选择列："),
                dcc.Dropdown(
                    id="outlier-column-select",
                    options=[{"label": col, "value": col} for col in numeric_cols],
                    value=numeric_cols[0] if numeric_cols else None
                ),
            ], width=6),
            dbc.Col([
                html.Label("检测方法："),
                dcc.Dropdown(
                    id="outlier-method-select",
                    options=[
                        {"label": "IQR（四分位距）", "value": "iqr"},
                        {"label": "Z-Score（标准分数）", "value": "zscore"},
                    ],
                    value="iqr"
                ),
            ], width=6),
        ], className="mb-3"),

        html.Div(id="outlier-output"),
    ])


@callback(
    Output("outlier-output", "children"),
    [Input("outlier-column-select", "value"),
     Input("outlier-method-select", "value")]
)
def show_outlier_detection(column, method):
    if not column:
        return None

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return None

    stats_service = StatsService()

    try:
        result = stats_service.detect_outliers(df, column, method=method)

        # 创建箱线图标注异常值
        fig = go.Figure()
        fig.add_trace(go.Box(y=df[column], name=column, boxpoints='outliers'))

        if method == 'iqr':
            fig.add_hline(y=result['lower_bound'], line_dash="dash", line_color="red",
                         annotation_text="下界")
            fig.add_hline(y=result['upper_bound'], line_dash="dash", line_color="red",
                         annotation_text="上界")

        fig.update_layout(title=f"{column} 异常值检测（{result['method']}）", height=400)

        info_card = dbc.Card([
            dbc.CardBody([
                html.H5("检测结果", className="card-title"),
                html.Hr(),
                html.P([html.Strong("检测方法: "), result['method']]),
                html.P([html.Strong("异常值数量: "), f"{result['outlier_count']} ({result['outlier_pct']:.2f}%)"]),

                html.P([html.Strong("边界: "),
                       f"[{result.get('lower_bound', 'N/A'):.2f}, {result.get('upper_bound', 'N/A'):.2f}]"
                       if 'lower_bound' in result else f"Z-Score > {result.get('threshold', 3)}"]),
            ])
        ], className="mb-3")

        return html.Div([
            info_card,
            dcc.Graph(figure=fig),
        ])

    except Exception as e:
        return dbc.Alert(f"检测失败: {str(e)}", color="danger")


def render_hypothesis_testing(df):
    """渲染假设检验"""
    return html.Div([
        html.H4("假设检验", className="mb-3"),

        dbc.Alert([
            html.H5("你想做什么？", className="alert-heading"),
            dbc.RadioItems(
                id="hypothesis-test-type",
                options=[
                    {"label": "比较两组数据是否有显著差异（t检验）", "value": "ttest"},
                    {"label": "检验两个分类变量是否相关（卡方检验）", "value": "chi2"},
                    {"label": "检验数据是否符合正态分布", "value": "normality"},
                ],
                value="ttest"
            ),
        ], color="light", className="mb-3"),

        html.Div(id="hypothesis-test-params"),
        html.Div(id="hypothesis-test-output"),
    ])


@callback(
    Output("hypothesis-test-params", "children"),
    Input("hypothesis-test-type", "value")
)
def show_hypothesis_params(test_type):
    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return None

    columns = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if test_type == "ttest":
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("数值列："),
                    dcc.Dropdown(
                        id="ttest-value-column",
                        options=[{"label": col, "value": col} for col in numeric_cols],
                        placeholder="选择数值列"
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("分组列（必须有2个组）："),
                    dcc.Dropdown(
                        id="ttest-group-column",
                        options=[{"label": col, "value": col} for col in columns],
                        placeholder="选择分组列"
                    ),
                ], width=6),
            ], className="mb-3"),
            dbc.Button("执行检验", id="btn-run-ttest", color="primary"),
        ])

    elif test_type == "chi2":
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("分类变量1："),
                    dcc.Dropdown(
                        id="chi2-var1",
                        options=[{"label": col, "value": col} for col in columns],
                        placeholder="选择变量1"
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("分类变量2："),
                    dcc.Dropdown(
                        id="chi2-var2",
                        options=[{"label": col, "value": col} for col in columns],
                        placeholder="选择变量2"
                    ),
                ], width=6),
            ], className="mb-3"),
            dbc.Button("执行检验", id="btn-run-chi2", color="primary"),
        ])

    elif test_type == "normality":
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label("数值列："),
                    dcc.Dropdown(
                        id="normality-column",
                        options=[{"label": col, "value": col} for col in numeric_cols],
                        placeholder="选择数值列"
                    ),
                ], width=6),
            ], className="mb-3"),
            dbc.Button("执行检验", id="btn-run-normality", color="primary"),
        ])


@callback(
    Output("hypothesis-test-output", "children"),
    [Input("btn-run-ttest", "n_clicks"),
     Input("btn-run-chi2", "n_clicks"),
     Input("btn-run-normality", "n_clicks")],
    [State("ttest-value-column", "value"),
     State("ttest-group-column", "value"),
     State("chi2-var1", "value"),
     State("chi2-var2", "value"),
     State("normality-column", "value")],
    prevent_initial_call=True
)
def run_hypothesis_test(n1, n2, n3, ttest_val, ttest_grp, chi2_v1, chi2_v2, norm_col):
    from dash import ctx

    if not ctx.triggered:
        return None

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    data_manager = DataManager()
    df = data_manager.active_df

    if df is None:
        return None

    stats_service = StatsService()

    try:
        if button_id == "btn-run-ttest" and ttest_val and ttest_grp:
            result = stats_service.t_test(df, ttest_val, ttest_grp)

            if 'error' in result:
                return dbc.Alert(result['error'], color="danger")

            return dbc.Card([
                dbc.CardBody([
                    html.H5("t 检验结果", className="card-title"),
                    html.Hr(),
                    html.P([html.Strong("检验类型: "), result['test']]),
                    html.P([html.Strong("组1: "), f"{result['group1']} (均值: {result['group1_mean']:.2f})"]),
                    html.P([html.Strong("组2: "), f"{result['group2']} (均值: {result['group2_mean']:.2f})"]),
                    html.P([html.Strong("t 统计量: "), f"{result['statistic']:.4f}"]),
                    html.P([html.Strong("p 值: "), f"{result['p_value']:.4f}"]),
                    html.Hr(),
                    dbc.Alert(result['interpretation'],
                             color="success" if result['significant'] else "info"),
                ])
            ])

        elif button_id == "btn-run-chi2" and chi2_v1 and chi2_v2:
            result = stats_service.chi_square_test(df, chi2_v1, chi2_v2)

            return dbc.Card([
                dbc.CardBody([
                    html.H5("卡方检验结果", className="card-title"),
                    html.Hr(),
                    html.P([html.Strong("检验类型: "), result['test']]),
                    html.P([html.Strong("变量1: "), result['variable1']]),
                    html.P([html.Strong("变量2: "), result['variable2']]),
                    html.P([html.Strong("卡方统计量: "), f"{result['chi2']:.4f}"]),
                    html.P([html.Strong("自由度: "), f"{result['dof']}"]),
                    html.P([html.Strong("p 值: "), f"{result['p_value']:.4f}"]),
                    html.Hr(),
                    dbc.Alert(result['interpretation'],
                             color="success" if result['significant'] else "info"),
                ])
            ])

        elif button_id == "btn-run-normality" and norm_col:
            result = stats_service.normality_test(df, norm_col)

            if 'error' in result:
                return dbc.Alert(result['error'], color="danger")

            return dbc.Card([
                dbc.CardBody([
                    html.H5("正态性检验结果", className="card-title"),
                    html.Hr(),
                    html.P([html.Strong("检验类型: "), result['test']]),
                    html.P([html.Strong("统计量: "), f"{result['statistic']:.4f}"]),
                    html.P([html.Strong("p 值: "), f"{result['p_value']:.4f}"]),
                    html.Hr(),
                    dbc.Alert(result['interpretation'],
                             color="success" if result['is_normal'] else "warning"),
                ])
            ])

    except Exception as e:
        return dbc.Alert(f"检验失败: {str(e)}", color="danger")

    return None
