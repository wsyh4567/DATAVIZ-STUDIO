"""
操作工具栏组件

提供常用数据操作的快速访问
"""

from dash import html
import dash_bootstrap_components as dbc


def create_operation_toolbar() -> html.Div:
    """创建操作工具栏

    Returns:
        工具栏组件
    """
    return dbc.Card([
        dbc.CardHeader("操作工具", style={"fontWeight": "bold"}),
        dbc.CardBody([
            # 基础操作
            html.H6("基础操作", className="mb-3", style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                create_tool_button("筛选", "bi-funnel", "btn-filter", "primary"),
                create_tool_button("删除列", "bi-trash", "btn-drop-column", "danger"),
                create_tool_button("重命名", "bi-pencil", "btn-rename-column", "info"),
                create_tool_button("排序", "bi-sort-down", "btn-sort", "secondary"),
            ], vertical=True, className="w-100 mb-3"),

            # 数据转换
            html.H6("数据转换", className="mb-3", style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                create_tool_button("类型转换", "bi-type", "btn-type-convert", "info"),
                create_tool_button("填充缺失值", "bi-droplet", "btn-fill-missing", "warning"),
                create_tool_button("去重", "bi-files", "btn-drop-duplicates", "secondary"),
            ], vertical=True, className="w-100 mb-3"),

            # 高级操作
            html.H6("高级操作", className="mb-3", style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                create_tool_button("拆分列", "bi-scissors", "btn-split-column", "info"),
                create_tool_button("合并列", "bi-union", "btn-merge-columns", "info"),
                create_tool_button("替换值", "bi-arrow-repeat", "btn-replace-value", "secondary"),
            ], vertical=True, className="w-100 mb-3"),

            # 文本操作
            html.H6("文本操作", className="mb-3", style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                create_tool_button("去除空格", "bi-eraser", "btn-strip-whitespace", "secondary"),
                create_tool_button("大小写转换", "bi-fonts", "btn-change-case", "secondary"),
                create_tool_button("正则替换", "bi-braces", "btn-regex-replace", "secondary"),
                create_tool_button("提取子串", "bi-cursor-text", "btn-extract-substring", "secondary"),
            ], vertical=True, className="w-100 mb-3"),

            # 数值操作
            html.H6("数值操作", className="mb-3", style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                create_tool_button("分箱", "bi-distribute-vertical", "btn-bin-column", "info"),
                create_tool_button("标准化", "bi-rulers", "btn-normalize", "info"),
                create_tool_button("计算列", "bi-calculator", "btn-create-calculated", "info"),
            ], vertical=True, className="w-100 mb-3"),

            # 行列操作
            html.H6("行列操作", className="mb-3", style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                create_tool_button("删除缺失行", "bi-x-circle", "btn-drop-missing-rows", "warning"),
                create_tool_button("复制列", "bi-copy", "btn-duplicate-column", "secondary"),
            ], vertical=True, className="w-100 mb-3"),

            html.Hr(),

            # 历史操作
            html.H6("历史操作", className="mb-3", style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-arrow-counterclockwise me-2"),
                    "撤销"
                ], id="btn-undo", color="secondary", size="sm", disabled=True, className="w-100 btn-hover"),
                dbc.Button([
                    html.I(className="bi bi-arrow-clockwise me-2"),
                    "重做"
                ], id="btn-redo", color="secondary", size="sm", disabled=True, className="w-100 btn-hover"),
            ], vertical=True, className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_tool_button(label: str, icon: str, button_id: str, color: str) -> dbc.Button:
    """创建工具按钮

    Args:
        label: 按钮标签
        icon: Bootstrap图标类名
        button_id: 按钮ID
        color: 按钮颜色

    Returns:
        按钮组件
    """
    return dbc.Button([
        html.I(className=f"bi {icon} me-2"),
        label
    ], id=button_id, color=color, size="sm", outline=True, className="mb-2 w-100 text-start btn-hover")


def create_compact_toolbar() -> html.Div:
    """创建紧凑型工具栏（用于顶部）

    Returns:
        紧凑工具栏组件
    """
    return html.Div([
        dbc.ButtonGroup([
            dbc.Button(html.I(className="bi bi-funnel"), id="btn-filter-compact",
                      color="primary", size="sm", title="筛选", className="btn-hover"),
            dbc.Button(html.I(className="bi bi-trash"), id="btn-drop-column-compact",
                      color="danger", size="sm", title="删除列", className="btn-hover"),
            dbc.Button(html.I(className="bi bi-type"), id="btn-type-convert-compact",
                      color="info", size="sm", title="类型转换", className="btn-hover"),
            dbc.Button(html.I(className="bi bi-droplet"), id="btn-fill-missing-compact",
                      color="warning", size="sm", title="填充缺失值", className="btn-hover"),
        ], className="me-2"),

        dbc.ButtonGroup([
            dbc.Button(html.I(className="bi bi-arrow-counterclockwise"),
                      id="btn-undo-compact", color="secondary", size="sm",
                      disabled=True, title="撤销", className="btn-hover"),
            dbc.Button(html.I(className="bi bi-arrow-clockwise"),
                      id="btn-redo-compact", color="secondary", size="sm",
                      disabled=True, title="重做", className="btn-hover"),
        ], className="me-2"),

        dbc.ButtonGroup([
            dbc.Button([html.I(className="bi bi-code-slash me-1"), "代码"],
                      id="btn-view-code", color="success", size="sm", outline=True, className="btn-hover"),
            dbc.Button([html.I(className="bi bi-download me-1"), "导出"],
                      id="btn-export", color="primary", size="sm", outline=True, className="btn-hover"),
        ]),
    ], className="d-flex align-items-center")
