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
    return html.Div(className="dvs-container p-4", children=[
        # 页面标题
        html.Div([
            html.H3("统计实验室", className="page-title fade-in mb-1"),
            html.P("专业级统计分析与深度假设检验", className="page-subtitle fade-in text-muted mb-4", style={"fontSize": "0.9rem"})
        ]),

        # 主内容区域栅格
        dbc.Row(className="g-4 h-100", children=[
            # 左侧导航面板 (占据 2 列宽)
            dbc.Col(width=2, children=[
                html.Div(
                    className="h-100",
                    style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)", "borderRadius": "12px", "padding": "20px"},
                    children=[
                        html.H6("探索视角", className="mb-4 text-muted fw-bold", style={"letterSpacing": "1px"}),
                        dbc.Nav([
                            dbc.NavLink([html.I(className="bi bi-file-earmark-bar-graph me-2"), "描述性统计"], href="#", id="nav-descriptive", active=True, className="mb-2 py-2 rounded"),
                            dbc.NavLink([html.I(className="bi bi-intersect me-2"), "相关性分析"], href="#", id="nav-correlation", className="mb-2 py-2 rounded"),
                            dbc.NavLink([html.I(className="bi bi-layers me-2"), "分组聚合"], href="#", id="nav-groupby", className="mb-2 py-2 rounded"),
                            dbc.NavLink([html.I(className="bi bi-grid-3x3 me-2"), "交叉表分析"], href="#", id="nav-crosstab", className="mb-2 py-2 rounded"),
                            dbc.NavLink([html.I(className="bi bi-record-circle me-2"), "异常检测"], href="#", id="nav-outliers", className="mb-2 py-2 rounded"),
                            dbc.NavLink([html.I(className="bi bi-clipboard-data me-2"), "假设检验"], href="#", id="nav-hypothesis", className="mb-2 py-2 rounded"),
                        ], vertical=True, pills=True, style={"fontSize": "0.9rem"}),
                    ]
                )
            ]),

            # 右侧主内容展示区 (占据 10 列宽)
            dbc.Col(width=10, children=[
                html.Div(
                    id="stats-content-area",
                    className="h-100",
                    style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)", "borderRadius": "12px", "padding": "20px", "overflowY": "auto"}
                ),
            ]),
        ]),

        # 存储当前选择的功能
        dcc.Store(id="current-stats-function", data="descriptive"),

    ])


# 切换功能
@callback(
    [Output("current-stats-function", "data"),
     Output("nav-descriptive", "active"),
     Output("nav-correlation", "active"),
     Output("nav-groupby", "active"),
     Output("nav-crosstab", "active"),
     Output("nav-outliers", "active"),
     Output("nav-hypothesis", "active")],
    [Input("nav-descriptive", "n_clicks"),
     Input("nav-correlation", "n_clicks"),
     Input("nav-groupby", "n_clicks"),
     Input("nav-crosstab", "n_clicks"),
     Input("nav-outliers", "n_clicks"),
     Input("nav-hypothesis", "n_clicks")],
    prevent_initial_call=True
)
def switch_function(*args):
    from dash import ctx

    if not ctx.triggered:
        return "descriptive", True, False, False, False, False, False

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    active_states = {
        "nav-descriptive": ("descriptive", True, False, False, False, False, False),
        "nav-correlation": ("correlation", False, True, False, False, False, False),
        "nav-groupby": ("groupby", False, False, True, False, False, False),
        "nav-crosstab": ("crosstab", False, False, False, True, False, False),
        "nav-outliers": ("outliers", False, False, False, False, True, False),
        "nav-hypothesis": ("hypothesis", False, False, False, False, False, True),
    }

    return active_states.get(button_id, ("descriptive", True, False, False, False, False, False))


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
    elif function == "crosstab":
        return render_crosstab_analysis(df)
    elif function == "outliers":
        return render_outlier_detection(df)
    elif function == "hypothesis":
        return render_hypothesis_testing(df)

    return html.Div("未知功能")


def render_descriptive_stats(df):
    """渲染描述性统计"""
    columns = df.columns.tolist()

    return html.Div([
        dbc.Row(className="mb-4 align-items-center", children=[
            dbc.Col(html.H5("特征描述性统计矩阵", className="m-0 fw-bold"), width=3),
            dbc.Col([
                dcc.Dropdown(
                    id="desc-column-select",
                    options=[{"label": col, "value": col} for col in columns],
                    value=columns[0] if columns else None,
                    placeholder="请选定探索列...",
                    className="shadow-sm"
                ),
            ], width=4),
        ]),
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

    # 自然语言摘要 (Alert)
    cards.append(dbc.Alert([
        html.H6("高层级洞见摘要", className="alert-heading fw-bold mb-2"),
        html.P(summary, className="mb-0", style={"fontSize": "0.9rem"})
    ], color="primary", className="mb-4 border-0 shadow-sm", style={"backgroundColor": "rgba(49,130,206,0.1)", "color": "var(--text-primary)"}))

    # 第一块 Row：基础指标 / 核心统计量
    top_metrics_cols = []
    
    top_metrics_cols.append(
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("存储与填报健康度", className="text-muted mb-3 font-sm"),
            html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("数据类型"), html.Strong(stats['dtype'])]),
            html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("有效非空集"), html.Strong(f"{stats['count']:,}")]),
            html.Div(className="d-flex justify-content-between", children=[html.Span("缺失值"), html.Strong(f"{stats['missing']:,} ({stats['missing_pct']:.1f}%)", className="text-danger" if stats['missing']>0 else "text-success")]),
        ]), className="card-hover h-100 border-0 shadow-sm", style={"backgroundColor": "var(--bg-primary)"}), width=4)
    )

    if 'mean' in stats:
        top_metrics_cols.append(
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("集中趋势分布", className="text-muted mb-3 font-sm"),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("算术平均数 (Mean)"), html.Strong(f"{stats['mean']:.2f}")]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("中位数 (Median)"), html.Strong(f"{stats['median']:.2f}")]),
                html.Div(className="d-flex justify-content-between", children=[html.Span("标准差 (Std)"), html.Strong(f"{stats['std']:.2f}")]),
            ]), className="card-hover h-100 border-0 shadow-sm", style={"backgroundColor": "var(--bg-primary)"}), width=4)
        )
        top_metrics_cols.append(
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("极值与形状度量", className="text-muted mb-3 font-sm"),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("范围跨度 (Max-Min)"), html.Strong(f"{stats['max'] - stats['min']:.2f}")]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("偏态 (Skewness)"), html.Strong(f"{stats['skewness']:.2f}")]),
                html.Div(className="d-flex justify-content-between", children=[html.Span("峰态 (Kurtosis)"), html.Strong(f"{stats['kurtosis']:.2f}")]),
            ]), className="card-hover h-100 border-0 shadow-sm", style={"backgroundColor": "var(--bg-primary)"}), width=4)
        )
    elif 'unique' in stats:
        top_metrics_cols.append(
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("分类频次检测", className="text-muted mb-3 font-sm"),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("独立唯一值数量"), html.Strong(f"{stats['unique']}")]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("绝对高频项目"), html.Strong(stats['top'])]),
                html.Div(className="d-flex justify-content-between", children=[html.Span("顶流出现频次"), html.Strong(f"{stats['top_freq']:,} ({stats['top_pct']:.1f}%)")]),
            ]), className="card-hover h-100 border-0 shadow-sm", style={"backgroundColor": "var(--bg-primary)"}), width=8)
        )

    cards.append(dbc.Row(className="g-3 mb-4", children=top_metrics_cols))

    # 第二块 Row：数据分布画布
    if 'mean' in stats:
        fig_hist = px.histogram(df, x=column, nbins=40, title=f"特征【{column}】 细粒度直方密度估算", color_discrete_sequence=["#3182CE"])
        fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="var(--bg-primary)", margin=dict(t=50, l=20, r=20, b=20), font_color="var(--text-primary)")
        fig_hist.add_vline(x=stats['mean'], line_dash="dash", line_color="#E53E3E", annotation_text="平均水准", annotation_position="top")
        fig_hist.add_vline(x=stats['median'], line_dash="dot", line_color="#38A169", annotation_text="中心位", annotation_position="bottom")

        fig_box = px.box(df, y=column, title=f"特征【{column}】 极端值与分位数透视", color_discrete_sequence=["#DD6B20"])
        fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="var(--bg-primary)", margin=dict(t=50, l=20, r=20, b=20), font_color="var(--text-primary)")

        cards.append(dbc.Row(className="g-3", children=[
            dbc.Col(dcc.Graph(figure=fig_hist, style={"height": "350px", "border": "1px solid var(--border)", "borderRadius": "12px", "backgroundColor": "var(--bg-primary)"}), width=8),
            dbc.Col(dcc.Graph(figure=fig_box, style={"height": "350px", "border": "1px solid var(--border)", "borderRadius": "12px", "backgroundColor": "var(--bg-primary)"}), width=4)
        ]))

    elif 'unique' in stats:
        value_counts = df[column].value_counts().head(20)
        fig_bar = px.bar(x=value_counts.index, y=value_counts.values, title=f"TOP 20 类别绝对频数解析", labels={'x': "类别字典项", 'y': '观测频数'}, color=value_counts.values, color_continuous_scale="Blues")
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="var(--bg-primary)", margin=dict(t=50, l=20, r=20, b=20), font_color="var(--text-primary)")

        cards.append(dbc.Row(className="g-3", children=[
            dbc.Col(dcc.Graph(figure=fig_bar, style={"height": "380px", "border": "1px solid var(--border)", "borderRadius": "12px", "backgroundColor": "var(--bg-primary)"}), width=12),
        ]))

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


# ── 交叉表分析 ──────────────────────────────────────

def render_crosstab_analysis(df):
    """渲染交叉表分析"""
    columns = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # 优先显示分类列
    row_options = [{"label": col, "value": col} for col in (cat_cols + [c for c in columns if c not in cat_cols])]
    col_options = row_options.copy()

    return html.Div([
        html.H4("交叉表分析", className="mb-3 fade-in"),

        dbc.Alert([
            "交叉表用于分析两个分类变量之间的关系，常用于“按XX和YY统计ZZ”这类分析场景。"
        ], color="info", className="mb-3 fade-in"),

        dbc.Row([
            dbc.Col([
                html.Label("行变量："),
                dcc.Dropdown(
                    id="crosstab-row-var",
                    options=row_options,
                    placeholder="选择行变量（如：城市）"
                ),
            ], width=3),
            dbc.Col([
                html.Label("列变量："),
                dcc.Dropdown(
                    id="crosstab-col-var",
                    options=col_options,
                    placeholder="选择列变量（如：产品类别）"
                ),
            ], width=3),
            dbc.Col([
                html.Label("值变量（可选）："),
                dcc.Dropdown(
                    id="crosstab-value-var",
                    options=[{"label": col, "value": col} for col in numeric_cols],
                    placeholder="选择值变量（留空=计数）",
                    clearable=True,
                ),
            ], width=3),
            dbc.Col([
                html.Label("聚合函数："),
                dcc.Dropdown(
                    id="crosstab-agg-func",
                    options=[
                        {"label": "计数", "value": "count"},
                        {"label": "求和", "value": "sum"},
                        {"label": "平均值", "value": "mean"},
                        {"label": "中位数", "value": "median"},
                    ],
                    value="count",
                ),
            ], width=3),
        ], className="mb-3 fade-in"),

        dbc.Row([
            dbc.Col([
                html.Label("显示模式："),
                dbc.RadioItems(
                    id="crosstab-normalize",
                    options=[
                        {"label": "原始值", "value": ""},
                        {"label": "行百分比", "value": "index"},
                        {"label": "列百分比", "value": "columns"},
                        {"label": "总百分比", "value": "all"},
                    ],
                    value="",
                    inline=True,
                ),
            ]),
        ], className="mb-3 fade-in"),

        dbc.Button("生成交叉表", id="btn-run-crosstab", color="primary", className="mb-3"),

        html.Div(id="crosstab-output"),
    ])


@callback(
    Output("crosstab-output", "children"),
    Input("btn-run-crosstab", "n_clicks"),
    [State("crosstab-row-var", "value"),
     State("crosstab-col-var", "value"),
     State("crosstab-value-var", "value"),
     State("crosstab-agg-func", "value"),
     State("crosstab-normalize", "value")],
    prevent_initial_call=True
)
def run_crosstab(n_clicks, row_var, col_var, value_var, agg_func, normalize):
    """执行交叉表分析"""
    if not row_var or not col_var:
        return dbc.Alert("请选择行变量和列变量", color="warning")

    if row_var == col_var:
        return dbc.Alert("行变量和列变量不能相同", color="warning")

    dm = DataManager()
    df = dm.active_df
    if df is None:
        return dbc.Alert("请先加载数据", color="warning")

    try:
        # 生成交叉表
        if value_var and agg_func != "count":
            ct = pd.crosstab(
                df[row_var], df[col_var],
                values=df[value_var], aggfunc=agg_func,
            )
        else:
            ct = pd.crosstab(df[row_var], df[col_var])

        # 百分比模式
        display_ct = ct.copy()
        if normalize:
            display_ct = pd.crosstab(
                df[row_var], df[col_var],
                values=df[value_var] if (value_var and agg_func != "count") else None,
                aggfunc=agg_func if (value_var and agg_func != "count") else None,
                normalize=normalize,
            )
            display_ct = (display_ct * 100).round(1)

        # 表格
        table_df = display_ct.reset_index()
        suffix = "%" if normalize else ""

        # 热力图
        fig = px.imshow(
            ct.values,
            x=[str(c) for c in ct.columns],
            y=[str(r) for r in ct.index],
            text_auto=True,
            color_continuous_scale="Blues",
            labels={"x": col_var, "y": row_var, "color": agg_func},
            aspect="auto",
        )
        fig.update_layout(
            title=f"{row_var} × {col_var} 交叉{agg_func}",
            height=max(300, len(ct.index) * 30 + 100),
        )

        return html.Div([
            dcc.Graph(figure=fig, className="mb-3"),
            html.H5(f"交叉表结果 {suffix}", className="mt-3 mb-2"),
            dbc.Table.from_dataframe(
                table_df, striped=True, bordered=True, hover=True, size="sm",
                style={"fontSize": "0.85rem"}
            ),
        ])

    except Exception as e:
        return dbc.Alert(f"交叉表生成失败: {str(e)}", color="danger")
