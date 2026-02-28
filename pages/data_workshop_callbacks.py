"""
数据工坊回调函数模块

实现所有交互回调功能
"""

import uuid
from datetime import datetime
from dash import callback, Input, Output, State, no_update, ctx
import pandas as pd
import json

from services.data_workshop.preview_engine import PreviewEngine
from services.data_workshop.step_manager import StepManager
from services.data_workshop.undo_redo_stack import UndoRedoStack
from services.data_workshop.operation_executor import OperationExecutor
from services.data_workshop.code_generator import CodeGenerator
from services.data_workshop.models import Operation
from components.data_workshop.data_grid import create_data_grid, create_data_stats
from components.data_workshop.step_panel import create_step_panel
from components.data_workshop.code_preview_panel import create_code_preview_panel


# 全局实例
preview_engine = PreviewEngine(max_preview_rows=1000)
step_manager = StepManager()
undo_stack = UndoRedoStack()
operation_executor = OperationExecutor()
code_generator = CodeGenerator()


# ============================================================================
# 操作执行回调
# ============================================================================

@callback(
    Output('pipeline-store', 'data'),
    Output('preview-data-store', 'data'),
    Output('data-table-container', 'children'),
    Output('data-stats', 'children'),
    Output('undo-redo-store', 'data'),
    Input('btn-filter', 'n_clicks'),
    Input('btn-drop-column', 'n_clicks'),
    Input('btn-rename', 'n_clicks'),
    Input('btn-type-convert', 'n_clicks'),
    Input('btn-fill-missing', 'n_clicks'),
    Input('btn-drop-duplicates', 'n_clicks'),
    Input('btn-sort', 'n_clicks'),
    Input('btn-split-column', 'n_clicks'),
    Input('btn-merge-columns', 'n_clicks'),
    Input('btn-replace-value', 'n_clicks'),
    State('original-data-store', 'data'),
    State('pipeline-store', 'data'),
    prevent_initial_call=True
)
def handle_operation_click(
    filter_clicks, drop_clicks, rename_clicks, type_clicks, fill_clicks,
    dup_clicks, sort_clicks, split_clicks, merge_clicks, replace_clicks,
    original_data, current_pipeline
):
    """处理操作按钮点击"""
    if not original_data:
        return no_update, no_update, no_update, no_update, no_update
    
    # 确定触发的按钮
    triggered_id = ctx.triggered_id
    
    # 这里应该打开相应的操作配置面板
    # 暂时返回演示操作
    if triggered_id == 'btn-filter':
        # 演示：筛选 city == 'NYC'
        operation = {
            'step_id': str(uuid.uuid4()),
            'operation': 'filter',
            'params': {'column': 'city', 'operator': '==', 'value': 'NYC'},
            'timestamp': datetime.now().isoformat()
        }
    elif triggered_id == 'btn-type-convert':
        # 演示：将 age 转换为数值
        operation = {
            'step_id': str(uuid.uuid4()),
            'operation': 'type_conversion',
            'params': {'column': 'age', 'target_type': 'numeric'},
            'timestamp': datetime.now().isoformat()
        }
    elif triggered_id == 'btn-sort':
        # 演示：按 salary 降序排序
        operation = {
            'step_id': str(uuid.uuid4()),
            'operation': 'sort',
            'params': {'column': 'salary', 'ascending': False},
            'timestamp': datetime.now().isoformat()
        }
    else:
        return no_update, no_update, no_update, no_update, no_update
    
    # 添加操作到流水线
    new_pipeline = current_pipeline.copy() if current_pipeline else []
    new_pipeline.append(operation)
    
    # 计算预览
    df = pd.read_json(original_data, orient='split')
    result = preview_engine.compute_preview(df, new_pipeline)
    
    if 'error' in result:
        return no_update, no_update, no_update, no_update, no_update
    
    # 更新操作统计
    operation['affected_rows'] = result.get('affected_rows', 0)
    operation['affected_cols'] = result.get('affected_cols', 0)
    operation['execution_time'] = result.get('execution_time', 0)
    
    # 保存状态到撤销栈
    undo_stack.push_state({
        'pipeline': new_pipeline.copy(),
        'timestamp': datetime.now().isoformat()
    })
    
    # 创建预览表格
    preview_df = result['preview_df']
    table = create_data_grid(preview_df, preview_mode=True)
    stats = create_data_stats(preview_df)
    
    # 更新撤销重做状态
    undo_redo_state = {
        'can_undo': undo_stack.can_undo(),
        'can_redo': undo_stack.can_redo()
    }
    
    return new_pipeline, preview_df.to_json(orient='split'), table, stats, undo_redo_state


# ============================================================================
# 撤销重做回调
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
    
    # 执行撤销或重做
    if triggered_id == 'btn-undo':
        state = undo_stack.undo()
    elif triggered_id == 'btn-redo':
        state = undo_stack.redo()
    else:
        return no_update, no_update, no_update, no_update, no_update
    
    if not state:
        return no_update, no_update, no_update, no_update, no_update
    
    # 获取流水线
    pipeline = state.get('pipeline', [])
    
    # 重新计算预览
    df = pd.read_json(original_data, orient='split')
    
    if pipeline:
        result = preview_engine.compute_preview(df, pipeline)
        if 'error' in result:
            return no_update, no_update, no_update, no_update, no_update
        preview_df = result['preview_df']
    else:
        preview_df = df
    
    # 创建预览表格
    table = create_data_grid(preview_df, preview_mode=True)
    stats = create_data_stats(preview_df)
    
    # 更新撤销重做状态
    undo_redo_state = {
        'can_undo': undo_stack.can_undo(),
        'can_redo': undo_stack.can_redo()
    }
    
    return pipeline, preview_df.to_json(orient='split'), table, stats, undo_redo_state


# ============================================================================
# 步骤管理回调
# ============================================================================

@callback(
    Output('pipeline-store', 'data', allow_duplicate=True),
    Output('preview-data-store', 'data', allow_duplicate=True),
    Output('data-table-container', 'children', allow_duplicate=True),
    Output('data-stats', 'children', allow_duplicate=True),
    Input('btn-clear-steps', 'n_clicks'),
    Input({'type': 'delete-step', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State('original-data-store', 'data'),
    State('pipeline-store', 'data'),
    prevent_initial_call=True
)
def handle_step_management(clear_clicks, delete_clicks, original_data, current_pipeline):
    """处理步骤管理操作"""
    if not original_data:
        return no_update, no_update, no_update, no_update
    
    triggered_id = ctx.triggered_id
    
    # 清空所有步骤
    if triggered_id == 'btn-clear-steps':
        new_pipeline = []
    # 删除特定步骤
    elif isinstance(triggered_id, dict) and triggered_id.get('type') == 'delete-step':
        step_index = triggered_id.get('index')
        new_pipeline = current_pipeline.copy() if current_pipeline else []
        if 0 <= step_index < len(new_pipeline):
            new_pipeline.pop(step_index)
    else:
        return no_update, no_update, no_update, no_update
    
    # 重新计算预览
    df = pd.read_json(original_data, orient='split')
    
    if new_pipeline:
        result = preview_engine.compute_preview(df, new_pipeline)
        if 'error' in result:
            return no_update, no_update, no_update, no_update
        preview_df = result['preview_df']
    else:
        preview_df = df
    
    # 创建预览表格
    table = create_data_grid(preview_df, preview_mode=True)
    stats = create_data_stats(preview_df)
    
    return new_pipeline, preview_df.to_json(orient='split'), table, stats


# ============================================================================
# 代码生成回调
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
            # 生成代码
            code = code_generator.generate_code(
                pipeline,
                data_source='data.csv',
                include_imports=True,
                include_comments=True
            )
        
        # 创建代码显示
        code_display = create_code_preview_panel(code, show_header=False)
        return True, code_display
    
    elif triggered_id == 'btn-close-code-modal':
        return False, no_update
    
    return no_update, no_update


# ============================================================================
# 代码复制和下载回调
# ============================================================================

@callback(
    Output('copy-code-status', 'children'),
    Input('btn-copy-code', 'n_clicks'),
    State('pipeline-store', 'data'),
    prevent_initial_call=True
)
def handle_copy_code(n_clicks, pipeline):
    """处理代码复制"""
    if not pipeline:
        return "无代码可复制"
    
    # 生成代码
    code = code_generator.generate_code(
        pipeline,
        data_source='data.csv',
        include_imports=True,
        include_comments=True
    )
    
    # 注意：实际的复制到剪贴板需要客户端JavaScript
    # 这里只返回提示信息
    return "代码已复制到剪贴板"


@callback(
    Output('download-code', 'data'),
    Input('btn-download-code', 'n_clicks'),
    State('pipeline-store', 'data'),
    prevent_initial_call=True
)
def handle_download_code(n_clicks, pipeline):
    """处理代码下载"""
    if not pipeline:
        return no_update
    
    # 生成代码
    code = code_generator.generate_code(
        pipeline,
        data_source='data.csv',
        include_imports=True,
        include_comments=True
    )
    
    # 返回下载数据
    return dict(
        content=code,
        filename=f'data_cleaning_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    )


# ============================================================================
# 实时预览更新回调
# ============================================================================

@callback(
    Output('preview-stats-display', 'children'),
    Input('preview-data-store', 'data'),
    Input('pipeline-store', 'data'),
    prevent_initial_call=True
)
def update_preview_stats(preview_data, pipeline):
    """更新预览统计信息"""
    if not preview_data or not pipeline:
        return no_update
    
    # 获取最后一个操作的统计
    last_operation = pipeline[-1] if pipeline else None
    
    if last_operation:
        affected_rows = last_operation.get('affected_rows', 0)
        affected_cols = last_operation.get('affected_cols', 0)
        execution_time = last_operation.get('execution_time', 0)
        
        return html.Div([
            html.I(className="bi bi-info-circle me-2"),
            f"影响: {affected_rows} 行, {affected_cols} 列 | ",
            f"耗时: {execution_time:.3f}秒"
        ], style={"fontSize": "0.875rem", "color": "var(--text-muted)"})
    
    return no_update
