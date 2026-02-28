"""
列头菜单组件

提供列操作的快捷菜单
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import List, Dict, Optional


def create_column_menu(column: str, dtype: str) -> html.Div:
    """创建列头右键菜单
    
    Args:
        column: 列名
        dtype: 数据类型
    
    Returns:
        列头菜单组件
    """
    # 根据数据类型确定可用操作
    operations = get_column_operations(dtype)
    
    menu_items = []
    for op in operations:
        menu_items.append(
            dbc.DropdownMenuItem([
                html.I(className=f"bi bi-{op['icon']} me-2"),
                op['label']
            ], id={'type': 'column-menu-item', 'column': column, 'operation': op['value']})
        )
    
    return dbc.DropdownMenu(
        menu_items,
        label=column,
        id={'type': 'column-menu', 'column': column},
        className="column-menu"
    )


def get_column_operations(dtype: str) -> List[Dict]:
    """根据数据类型获取可用操作
    
    Args:
        dtype: 数据类型
    
    Returns:
        操作列表
    """
    # 所有列通用操作
    common_ops = [
        {'label': '重命名列', 'value': 'rename', 'icon': 'pencil'},
        {'label': '删除列', 'value': 'drop', 'icon': 'trash'},
        {'label': '复制列', 'value': 'duplicate', 'icon': 'files'},
        {'label': '排序 (升序)', 'value': 'sort_asc', 'icon': 'sort-up'},
        {'label': '排序 (降序)', 'value': 'sort_desc', 'icon': 'sort-down'},
    ]
    
    # 数值列特定操作
    numeric_ops = [
        {'label': '筛选数值', 'value': 'filter_numeric', 'icon': 'funnel'},
        {'label': '填充缺失值', 'value': 'fill_missing', 'icon': 'patch-check'},
        {'label': '标准化', 'value': 'normalize', 'icon': 'arrows-collapse'},
        {'label': '离散化', 'value': 'bin', 'icon': 'bar-chart'},
    ]
    
    # 文本列特定操作
    text_ops = [
        {'label': '筛选文本', 'value': 'filter_text', 'icon': 'funnel'},
        {'label': '转换大小写', 'value': 'change_case', 'icon': 'type'},
        {'label': '去除空格', 'value': 'strip', 'icon': 'scissors'},
        {'label': '拆分列', 'value': 'split', 'icon': 'distribute-vertical'},
        {'label': '提取模式', 'value': 'extract', 'icon': 'regex'},
    ]
    
    # 日期列特定操作
    date_ops = [
        {'label': '筛选日期', 'value': 'filter_date', 'icon': 'funnel'},
        {'label': '提取年份', 'value': 'extract_year', 'icon': 'calendar'},
        {'label': '提取月份', 'value': 'extract_month', 'icon': 'calendar'},
        {'label': '提取星期', 'value': 'extract_weekday', 'icon': 'calendar-week'},
    ]
    
    # 类型转换操作
    conversion_ops = [
        {'label': '转换为数值', 'value': 'to_numeric', 'icon': 'hash'},
        {'label': '转换为文本', 'value': 'to_text', 'icon': 'type'},
        {'label': '转换为日期', 'value': 'to_date', 'icon': 'calendar'},
    ]
    
    # 根据类型组合操作
    if dtype in ['int64', 'float64', 'Int64', 'Float64']:
        return common_ops + numeric_ops + conversion_ops
    elif 'datetime' in str(dtype):
        return common_ops + date_ops + conversion_ops
    elif dtype == 'object':
        return common_ops + text_ops + conversion_ops
    else:
        return common_ops + conversion_ops


def create_column_header_with_menu(column: str, dtype: str, has_missing: bool = False) -> html.Div:
    """创建带菜单的列头
    
    Args:
        column: 列名
        dtype: 数据类型
        has_missing: 是否有缺失值
    
    Returns:
        列头组件
    """
    return html.Div([
        html.Span(column, className="column-name"),
        html.Div([
            # 数据类型图标
            html.I(className=f"bi bi-{get_dtype_icon(dtype)} me-1", 
                  title=dtype, style={"fontSize": "0.75rem", "color": "var(--text-muted)"}),
            # 缺失值警告
            html.I(className="bi bi-exclamation-triangle me-1", 
                  title="包含缺失值", 
                  style={"fontSize": "0.75rem", "color": "var(--warning)", 
                        "display": "inline" if has_missing else "none"}),
            # 菜单按钮
            html.I(className="bi bi-three-dots-vertical column-menu-icon", 
                  id={'type': 'column-menu-trigger', 'column': column},
                  style={"fontSize": "0.875rem", "cursor": "pointer"}),
        ], className="column-icons"),
    ], className="column-header d-flex align-items-center justify-content-between")


def get_dtype_icon(dtype: str) -> str:
    """获取数据类型对应的图标
    
    Args:
        dtype: 数据类型
    
    Returns:
        Bootstrap图标类名
    """
    if dtype in ['int64', 'float64', 'Int64', 'Float64']:
        return 'hash'
    elif 'datetime' in str(dtype):
        return 'calendar'
    elif dtype == 'bool':
        return 'toggle-on'
    else:
        return 'type'


def create_column_operation_panel(column: str, operation: str, dtype: str) -> html.Div:
    """创建列操作配置面板"""
    if operation == 'rename':
        return create_rename_panel(column)
    elif operation == 'filter_numeric':
        from components.data_workshop.filter_panel import create_numeric_filter
        return create_numeric_filter(column)
    elif operation == 'filter_text':
        from components.data_workshop.filter_panel import create_text_filter
        return create_text_filter(column)
    elif operation == 'filter_date':
        from components.data_workshop.filter_panel import create_date_filter
        return create_date_filter(column)
    elif operation == 'split':
        return create_split_panel(column)
    elif operation in ['to_numeric', 'to_text', 'to_date']:
        return create_type_conversion_panel(column, operation)
    elif operation == 'drop':
        return _create_drop_panel(column)
    elif operation == 'duplicate':
        return _create_duplicate_panel(column)
    elif operation == 'sort_asc':
        return _create_sort_panel(column, ascending=True)
    elif operation == 'sort_desc':
        return _create_sort_panel(column, ascending=False)
    elif operation == 'fill_missing':
        return _create_fill_missing_panel(column, dtype)
    elif operation == 'normalize':
        return _create_normalize_panel(column)
    elif operation == 'bin':
        return _create_bin_panel(column)
    elif operation == 'change_case':
        return _create_change_case_panel(column)
    elif operation == 'strip':
        return _create_strip_panel(column)
    elif operation == 'extract':
        return _create_extract_panel(column)
    elif operation == 'extract_year':
        return _create_date_extract_panel(column, 'year', '年份')
    elif operation == 'extract_month':
        return _create_date_extract_panel(column, 'month', '月份')
    elif operation == 'extract_weekday':
        return _create_date_extract_panel(column, 'weekday', '星期')
    else:
        return create_generic_operation_panel(column, operation)


def create_rename_panel(column: str) -> html.Div:
    """创建重命名面板
    
    Args:
        column: 列名
    
    Returns:
        重命名面板
    """
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-pencil me-2"),
            f"重命名列: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Label("新列名", className="form-label", style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'rename-input', 'column': column},
                type='text',
                value=column,
                placeholder='输入新列名',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用"
                ], id={'type': 'apply-rename', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-rename', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_split_panel(column: str) -> html.Div:
    """创建列拆分面板
    
    Args:
        column: 列名
    
    Returns:
        拆分面板
    """
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-distribute-vertical me-2"),
            f"拆分列: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Label("分隔符", className="form-label", style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'split-delimiter', 'column': column},
                type='text',
                placeholder='输入分隔符',
                className='mb-2',
                style={'fontSize': '0.875rem'}
            ),
            html.Div([
                dbc.Button(",", id={'type': 'quick-delimiter', 'column': column, 'value': ','}, 
                          size="sm", outline=True, className="me-1"),
                dbc.Button(" ", id={'type': 'quick-delimiter', 'column': column, 'value': ' '}, 
                          size="sm", outline=True, className="me-1"),
                dbc.Button("-", id={'type': 'quick-delimiter', 'column': column, 'value': '-'}, 
                          size="sm", outline=True, className="me-1"),
                dbc.Button("_", id={'type': 'quick-delimiter', 'column': column, 'value': '_'}, 
                          size="sm", outline=True),
            ], className="mb-3"),
            
            html.Label("最大拆分数", className="form-label", style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'split-max', 'column': column},
                type='number',
                value=-1,
                placeholder='-1 表示不限制',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            
            html.Div(id={'type': 'split-preview', 'column': column}, className='mb-3'),
            
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用拆分"
                ], id={'type': 'apply-split', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-split', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_type_conversion_panel(column: str, target_type: str) -> html.Div:
    """创建类型转换面板
    
    Args:
        column: 列名
        target_type: 目标类型
    
    Returns:
        类型转换面板
    """
    type_labels = {
        'to_numeric': '数值型',
        'to_text': '文本型',
        'to_date': '日期型'
    }
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-arrow-left-right me-2"),
            f"类型转换: {column} → {type_labels.get(target_type, '未知')}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            dbc.Alert([
                html.I(className="bi bi-info-circle me-2"),
                "转换失败的值将被设置为缺失值 (NaN)"
            ], color="info", className="mb-3", style={"fontSize": "0.875rem"}),
            
            html.Div(id={'type': 'conversion-preview', 'column': column}, className='mb-3'),
            
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用转换"
                ], id={'type': 'apply-conversion', 'column': column, 'target': target_type}, 
                   color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-conversion', 'column': column}, 
                   color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def create_generic_operation_panel(column: str, operation: str) -> html.Div:
    """创建通用操作面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-gear me-2"),
            f"操作: {operation}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.P(f"列: {column}", style={"fontSize": "0.875rem"}),
            html.P("该操作的配置界面正在开发中",
                  style={"color": "var(--text-muted)", "fontSize": "0.875rem"}),
            dbc.Button("关闭", id={'type': 'cancel-operation', 'column': column},
                      color="secondary", size="sm", className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


# ── 新增操作面板 ──────────────────────────────────────

def _create_drop_panel(column: str) -> html.Div:
    """删除列确认面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-trash me-2"),
            f"删除列: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            dbc.Alert([
                html.I(className="bi bi-exclamation-triangle me-2"),
                f"确定要删除列 '{column}' 吗？此操作可通过撤销恢复。"
            ], color="warning", className="mb-3", style={"fontSize": "0.875rem"}),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-trash me-2"),
                    "确认删除"
                ], id={'type': 'apply-drop', 'column': column}, color="danger", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_duplicate_panel(column: str) -> html.Div:
    """复制列面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-files me-2"),
            f"复制列: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Label("新列名", className="form-label", style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'duplicate-name', 'column': column},
                type='text',
                value=f"{column}_copy",
                placeholder='输入新列名',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "复制"
                ], id={'type': 'apply-duplicate', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_sort_panel(column: str, ascending: bool = True) -> html.Div:
    """排序确认面板"""
    order = "升序" if ascending else "降序"
    return dbc.Card([
        dbc.CardHeader([
            html.I(className=f"bi bi-sort-{'up' if ascending else 'down'} me-2"),
            f"排序: {column} ({order})"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.P(f"将按列 '{column}' 进行{order}排序。", style={"fontSize": "0.875rem"}),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    f"确认{order}排序"
                ], id={'type': 'apply-sort', 'column': column, 'ascending': ascending}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_fill_missing_panel(column: str, dtype: str) -> html.Div:
    """填充缺失值面板"""
    # 数值列有更多填充选项
    if dtype in ['int64', 'float64', 'Int64', 'Float64']:
        methods = [
            {'label': '均值', 'value': 'mean'},
            {'label': '中位数', 'value': 'median'},
            {'label': '众数', 'value': 'mode'},
            {'label': '前向填充', 'value': 'ffill'},
            {'label': '后向填充', 'value': 'bfill'},
            {'label': '固定值', 'value': 'value'},
        ]
    else:
        methods = [
            {'label': '众数', 'value': 'mode'},
            {'label': '前向填充', 'value': 'ffill'},
            {'label': '后向填充', 'value': 'bfill'},
            {'label': '固定值', 'value': 'value'},
        ]

    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-patch-check me-2"),
            f"填充缺失值: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Label("填充方法", className="form-label", style={"fontSize": "0.875rem"}),
            dcc.Dropdown(
                id={'type': 'fill-method', 'column': column},
                options=methods,
                value=methods[0]['value'],
                clearable=False,
                className='mb-2',
            ),
            html.Label("固定值（仅当方法为固定值时）", className="form-label",
                       style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'fill-value', 'column': column},
                type='text',
                placeholder='输入固定值',
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用填充"
                ], id={'type': 'apply-fill', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_normalize_panel(column: str) -> html.Div:
    """标准化/归一化面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-arrows-collapse me-2"),
            f"标准化: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Label("标准化方法", className="form-label", style={"fontSize": "0.875rem"}),
            dcc.Dropdown(
                id={'type': 'normalize-method', 'column': column},
                options=[
                    {'label': 'Min-Max 归一化 (0~1)', 'value': 'minmax'},
                    {'label': 'Z-Score 标准化', 'value': 'zscore'},
                    {'label': 'Robust 标准化 (抗异常值)', 'value': 'robust'},
                ],
                value='minmax',
                clearable=False,
                className='mb-3',
            ),
            dbc.Alert([
                html.I(className="bi bi-info-circle me-2"),
                "将创建新列保存标准化结果，原列不受影响。"
            ], color="info", className="mb-3", style={"fontSize": "0.875rem"}),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用"
                ], id={'type': 'apply-normalize', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_bin_panel(column: str) -> html.Div:
    """分箱/离散化面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-bar-chart me-2"),
            f"离散化: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Label("分箱方法", className="form-label", style={"fontSize": "0.875rem"}),
            dcc.Dropdown(
                id={'type': 'bin-method', 'column': column},
                options=[
                    {'label': '等宽分箱', 'value': 'equal_width'},
                    {'label': '等频分箱', 'value': 'equal_freq'},
                ],
                value='equal_width',
                clearable=False,
                className='mb-2',
            ),
            html.Label("分箱数量", className="form-label", style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'bin-count', 'column': column},
                type='number',
                value=5,
                min=2,
                max=100,
                className='mb-3',
                style={'fontSize': '0.875rem'}
            ),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用分箱"
                ], id={'type': 'apply-bin', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_change_case_panel(column: str) -> html.Div:
    """大小写转换面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-type me-2"),
            f"大小写转换: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Label("转换方式", className="form-label", style={"fontSize": "0.875rem"}),
            dcc.Dropdown(
                id={'type': 'case-type', 'column': column},
                options=[
                    {'label': '全部小写 (lowercase)', 'value': 'lower'},
                    {'label': '全部大写 (UPPERCASE)', 'value': 'upper'},
                    {'label': '标题格式 (Title Case)', 'value': 'title'},
                    {'label': '首字母大写 (Capitalize)', 'value': 'capitalize'},
                ],
                value='lower',
                clearable=False,
                className='mb-3',
            ),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "应用转换"
                ], id={'type': 'apply-case', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_strip_panel(column: str) -> html.Div:
    """去除空格面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-scissors me-2"),
            f"去除空格: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.P("将去除该列所有值的首尾空格（包括制表符、换行符等空白字符）。",
                   style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "确认去除空格"
                ], id={'type': 'apply-strip', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_extract_panel(column: str) -> html.Div:
    """提取模式面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-regex me-2"),
            f"提取模式: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.Label("正则表达式", className="form-label", style={"fontSize": "0.875rem"}),
            dbc.Input(
                id={'type': 'extract-pattern', 'column': column},
                type='text',
                placeholder=r'例如: \d+ (提取数字)',
                className='mb-2',
                style={'fontSize': '0.875rem', 'fontFamily': 'monospace'}
            ),
            html.Div([
                html.Small("常用模式: ", style={"color": "var(--text-muted)"}),
                html.Small(r"\d+ 数字  ", style={"fontFamily": "monospace", "color": "var(--text-muted)"}),
                html.Small(r"[a-zA-Z]+ 字母  ", style={"fontFamily": "monospace", "color": "var(--text-muted)"}),
                html.Small(r"\w+@\w+ 邮箱", style={"fontFamily": "monospace", "color": "var(--text-muted)"}),
            ], className="mb-3"),
            dbc.Alert([
                html.I(className="bi bi-info-circle me-2"),
                "提取结果将保存为新列。"
            ], color="info", className="mb-3", style={"fontSize": "0.875rem"}),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    "提取"
                ], id={'type': 'apply-extract', 'column': column}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})


def _create_date_extract_panel(column: str, component: str, label: str) -> html.Div:
    """日期组件提取面板"""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-calendar me-2"),
            f"提取{label}: {column}"
        ], style={"fontWeight": "bold"}),
        dbc.CardBody([
            html.P(f"将从日期列 '{column}' 中提取{label}，并保存为新列 '{column}_{component}'。",
                   style={"fontSize": "0.875rem", "color": "var(--text-muted)"}),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="bi bi-check-circle me-2"),
                    f"确认提取{label}"
                ], id={'type': 'apply-date-extract', 'column': column, 'component': component}, color="primary", size="sm"),
                dbc.Button([
                    html.I(className="bi bi-x-circle me-2"),
                    "取消"
                ], id={'type': 'cancel-operation', 'column': column}, color="secondary", size="sm", outline=True),
            ], className="w-100"),
        ], style={"padding": "1rem"})
    ], style={"backgroundColor": "var(--bg-secondary)", "border": "1px solid var(--border)"})
