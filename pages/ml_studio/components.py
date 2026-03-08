# -*- coding: utf-8 -*-
"""机器学习通用 UI 组件与辅助视图"""
from dash import html
import dash_bootstrap_components as dbc
from .config import ACCENT_COLORS

def kpi_card(label: str, value: str, sub: str, color: str, icon: str) -> html.Div:
    """商业大屏 KPI 卡片"""
    return html.Div(
        style={
            "backgroundColor": "var(--bg-secondary)",
            "border": "1px solid var(--border)",
            "borderRadius": "10px",
            "borderLeft": f"4px solid {color}",
            "padding": "14px 16px",
            "position": "relative", "overflow": "hidden",
        },
        children=[
            # 背景渐变装饰
            html.Div(style={
                "position": "absolute", "right": "-10px", "top": "-10px",
                "width": "70px", "height": "70px", "borderRadius": "50%",
                "background": f"radial-gradient(circle, {color}30 0%, transparent 70%)",
            }),
            html.Div([
                html.I(className=f"bi {icon}", style={"color": color, "fontSize": "1.1rem"}),
            ], style={
                "position": "absolute", "right": "14px", "top": "14px",
                "opacity": "0.7",
            }),
            html.Div(label, style={
                "fontSize": "0.72rem", "color": "var(--text-secondary)",
                "marginBottom": "6px", "textTransform": "uppercase", "letterSpacing": "0.05em",
            }),
            html.Div(value, style={
                "fontSize": "1.7rem", "fontWeight": "700", "color": "var(--text-primary)",
                "lineHeight": "1.1", "marginBottom": "4px",
            }),
            html.Div(sub, style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
        ]
    )

def empty_placeholder(msg: str = "请先训练模型") -> html.Div:
    return html.Div(
        className="d-flex flex-column align-items-center justify-content-center",
        style={"height": "300px", "color": "var(--text-muted)"},
        children=[
            html.I(className="bi bi-robot", style={"fontSize": "3rem", "marginBottom": "12px"}),
            html.Div(msg, style={"fontSize": "0.9rem"}),
        ]
    )

def tutorial_offcanvas():
    """新手教程左侧抽屉"""
    content = html.Div([
        html.P("欢迎来到机器学习工作室！在这里你可以让计算机从数据中发现规律。", style={"color": "var(--text-secondary)", "fontSize": "0.9rem"}),
        
        html.H6("📘 基础概念速成", className="mt-4 mb-2"),
        dbc.Accordion([
            dbc.AccordionItem(title="1. 什么是目标变量?", children=[
                html.P("目标变量（Y）就是你想要预测的东西。比如预测房价，房价就是目标；预测病人是否患病，是否患病就是目标。")
            ]),
            dbc.AccordionItem(title="2. 什么是特征变量?", children=[
                html.P("特征变量（X）是影响目标的线索。要预测房价，房子的面积、卧室数量、位置就是特征。")
            ]),
            dbc.AccordionItem(title="3. 选择什么算法?", children=[
                html.P("• 分类任务：预测具体类别（生病/没病，猫/狗）。选【随机森林】最稳妥！\n"
                       "• 回归任务：预测具体数值（价格，温度）。选【随机森林回归】或【线性回归】。\n"
                       "• 聚类任务：不知道目标，只想把相似的东西分在一起（比如用户画像）。选【K均值聚类】。"),
            ]),
        ], start_collapsed=True),

        html.H6("🛠️ 如何操作?", className="mt-4 mb-2"),
        html.Ol([
            html.Li("在左侧【数据预处理】设定缺失值和标准化策略。"),
            html.Li("在【特征与目标】选择你要预测什么（目标Y），以及根据什么预测（特征X）。"),
            html.Li("在【算法配置】选择一种算法，初学者请保持默认参数。"),
            html.Li("点击蓝色的【开始训练模型】大按钮。"),
            html.Li("查看右侧生成的报告，切换【预测新样本】输入新数据查看结果！"),
        ], style={"fontSize": "0.85rem", "color": "var(--text-secondary)"})
    ])
    
    return dbc.Offcanvas(
        content,
        id="ml-tutorial-offcanvas",
        title="🤖 机器学习新手教程",
        is_open=False,
        placement="end",
        style={"backgroundColor": "var(--bg-primary)", "color": "var(--text-primary)"}
    )

def result_interpretation_card(text_content: list, icon="bi-lightbulb-fill", color="#F59E0B"):
    """结果解读模块UI"""
    return html.Div(
        style={
            "backgroundColor": f"rgba({_hex_to_rgba(color)}, 0.05)",
            "border": f"1px solid {color}40",
            "borderRadius": "8px",
            "padding": "16px",
            "marginTop": "20px",
            "display": "flex",
            "gap": "12px",
        },
        children=[
            html.I(className=f"bi {icon}", style={"color": color, "fontSize": "1.5rem"}),
            html.Div(
                children=[
                    html.H6("AI 模型解读结论", style={"color": color, "fontWeight": "600", "marginBottom": "8px"}),
                    html.Div(text_content, style={"fontSize": "0.85rem", "color": "var(--text-secondary)", "lineHeight": "1.6"}),
                ]
            )
        ]
    )

def _hex_to_rgba(hex_color: str) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"
