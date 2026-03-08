"""
操作工具栏组件 — 紧凑图标条版本

窄条图标布局（50px），点击图标直接触发操作模态框
"""

from dash import html
import dash_bootstrap_components as dbc


# ── 工具按钮定义 ──
TOOL_GROUPS = [
    {
        'label': '基础',
        'items': [
            ('筛选', 'bi-funnel', 'btn-filter'),
            ('删除列', 'bi-trash', 'btn-drop-column'),
            ('重命名', 'bi-pencil', 'btn-rename-column'),
            ('排序', 'bi-sort-down', 'btn-sort'),
        ]
    },
    {
        'label': '转换',
        'items': [
            ('类型转换', 'bi-type', 'btn-type-convert'),
            ('填充缺失', 'bi-droplet', 'btn-fill-missing'),
            ('去重', 'bi-files', 'btn-drop-duplicates'),
        ]
    },
    {
        'label': '高级',
        'items': [
            ('拆分列', 'bi-scissors', 'btn-split-column'),
            ('合并列', 'bi-union', 'btn-merge-columns'),
            ('替换值', 'bi-arrow-repeat', 'btn-replace-value'),
        ]
    },
    {
        'label': '文本',
        'items': [
            ('去空格', 'bi-eraser', 'btn-strip-whitespace'),
            ('大小写', 'bi-fonts', 'btn-change-case'),
            ('正则', 'bi-braces', 'btn-regex-replace'),
            ('提取', 'bi-cursor-text', 'btn-extract-substring'),
        ]
    },
    {
        'label': '数值',
        'items': [
            ('分箱', 'bi-distribute-vertical', 'btn-bin-column'),
            ('标准化', 'bi-rulers', 'btn-normalize'),
            ('计算列', 'bi-calculator', 'btn-create-calculated'),
        ]
    },
    {
        'label': '行列',
        'items': [
            ('删缺失行', 'bi-x-circle', 'btn-drop-missing-rows'),
            ('复制列', 'bi-copy', 'btn-duplicate-column'),
        ]
    },
]


def _action_btn(label, icon, btn_id):
    """创建包含图标和说明文字的宽幅按钮"""
    return html.Button(
        children=[
            html.I(className=f"bi {icon}", style={"fontSize": "1.1rem", "marginRight": "10px", "color": "var(--text-secondary)"}),
            html.Span(label, style={"fontSize": "0.85rem", "fontWeight": "500"}),
        ],
        id=btn_id,
        title=label,
        className="toolbar-action-btn",
        n_clicks=0,
        style={
            "width": "100%",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "flex-start",
            "border": "1px solid transparent",
            "borderRadius": "6px",
            "backgroundColor": "transparent",
            "color": "var(--text-primary)",
            "cursor": "pointer",
            "transition": "all 0.15s",
            "padding": "6px 12px",
            "marginBottom": "2px",
        }
    )


def create_operation_toolbar() -> html.Div:
    """创建明细版工具栏（宽屏带文字）"""
    children = []

    for group in TOOL_GROUPS:
        # 分组标签占据整行，靠左对齐
        children.append(
            html.Div(group['label'], style={
                "width": "100%",
                "fontSize": "0.7rem",
                "color": "var(--text-muted)",
                "textAlign": "left",
                "padding": "6px 4px 2px 8px",
                "fontWeight": "600",
                "letterSpacing": "0.5px",
            })
        )
        
        # 图标组变为单行垂直铺排
        btn_group = []
        for label, icon, btn_id in group['items']:
            btn_group.append(_action_btn(label, icon, btn_id))
            
        children.append(
            html.Div(btn_group, style={
                "display": "flex",
                "flexDirection": "column",
                "gap": "2px",
                "width": "100%",
                "padding": "2px 4px"
            })
        )

        # 分隔线
        children.append(html.Hr(style={
            "width": "85%",
            "margin": "8px auto",
            "borderColor": "var(--border)",
            "opacity": "0.4",
        }))

    # 历史操作区
    children.append(
        html.Div("历史操作", style={
            "width": "100%",
            "fontSize": "0.7rem",
            "color": "var(--text-muted)",
            "textAlign": "left",
            "padding": "6px 4px 2px 8px",
            "fontWeight": "600",
            "letterSpacing": "0.5px",
        })
    )
    
    history_btns = [
        _action_btn("撤销 (Undo)", "bi-arrow-counterclockwise", "btn-undo"),
        _action_btn("重做 (Redo)", "bi-arrow-clockwise", "btn-redo"),
    ]
    
    children.append(
        html.Div(history_btns, style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "2px",
            "width": "100%",
            "padding": "2px 4px"
        })
    )

    return html.Div(
        children,
        style={
            "width": "100%",
            "minWidth": "200px",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "stretch",
            "backgroundColor": "var(--bg-secondary)",
            "borderRight": "1px solid var(--border)",
            "padding": "8px 4px",
            "overflowY": "auto",
            "maxHeight": "calc(100vh - 180px)",
            "flexShrink": "0",
            "scrollbarWidth": "thin",
        }
    )


def create_compact_toolbar() -> html.Div:
    """兼容性保留"""
    return create_operation_toolbar()
