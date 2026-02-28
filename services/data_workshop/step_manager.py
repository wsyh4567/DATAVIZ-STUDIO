"""
步骤管理器

管理操作历史和步骤导航
"""

import uuid
import json
from typing import Dict, List, Optional
from datetime import datetime


class StepManager:
    """步骤管理器
    
    职责：
    - 管理操作流水线
    - 支持步骤的增删改查
    - 支持步骤重排序
    - 生成步骤描述
    """
    
    def __init__(self):
        """初始化步骤管理器"""
        self.pipeline: List[Dict] = []
        self.current_step: int = -1
    
    def add_step(self, operation: str, params: Dict) -> str:
        """添加步骤
        
        Args:
            operation: 操作类型
            params: 操作参数
        
        Returns:
            步骤ID
        """
        step_id = str(uuid.uuid4())
        step = {
            'step_id': step_id,
            'operation': operation,
            'params': params,
            'timestamp': datetime.now().isoformat(),
            'affected_rows': 0,
            'affected_cols': 0
        }
        self.pipeline.append(step)
        self.current_step = len(self.pipeline) - 1
        return step_id
    
    def remove_step(self, step_id: str) -> bool:
        """删除步骤
        
        Args:
            step_id: 步骤ID
        
        Returns:
            True如果删除成功，否则False
        """
        for i, step in enumerate(self.pipeline):
            if step['step_id'] == step_id:
                self.pipeline.pop(i)
                # 调整current_step
                if self.current_step >= len(self.pipeline):
                    self.current_step = len(self.pipeline) - 1
                return True
        return False
    
    def update_step(self, step_id: str, params: Dict) -> bool:
        """更新步骤参数
        
        Args:
            step_id: 步骤ID
            params: 新的操作参数
        
        Returns:
            True如果更新成功，否则False
        """
        for step in self.pipeline:
            if step['step_id'] == step_id:
                step['params'] = params
                step['timestamp'] = datetime.now().isoformat()
                return True
        return False
    
    def reorder_steps(self, step_ids: List[str]) -> bool:
        """重新排序步骤
        
        Args:
            step_ids: 新顺序的步骤ID列表
        
        Returns:
            True如果重排序成功，否则False
        """
        if len(step_ids) != len(self.pipeline):
            return False
        
        # 创建ID到步骤的映射
        step_map = {step['step_id']: step for step in self.pipeline}
        
        # 验证所有ID都存在
        if not all(step_id in step_map for step_id in step_ids):
            return False
        
        # 重新排序
        self.pipeline = [step_map[step_id] for step_id in step_ids]
        return True
    
    def get_step_description(self, step: Dict) -> str:
        """生成步骤的人类可读描述
        
        Args:
            step: 步骤字典
        
        Returns:
            步骤描述字符串
        
        Examples:
            "筛选: age > 18 (影响1500行)"
            "删除列: temp_col (影响1列)"
            "类型转换: price → 数值型"
        """
        operation = step['operation']
        params = step['params']
        affected_rows = step.get('affected_rows', 0)
        affected_cols = step.get('affected_cols', 0)
        
        # 根据操作类型生成描述
        if operation == 'filter':
            column = params.get('column', '')
            operator = params.get('operator', '')
            value = params.get('value', '')
            desc = f"筛选: {column} {operator} {value}"
        elif operation == 'drop_column':
            column = params.get('column', '')
            desc = f"删除列: {column}"
        elif operation == 'rename_column':
            old_name = params.get('old_name', '')
            new_name = params.get('new_name', '')
            desc = f"重命名列: {old_name} → {new_name}"
        elif operation == 'type_conversion':
            column = params.get('column', '')
            target_type = params.get('target_type', '')
            desc = f"类型转换: {column} → {target_type}"
        elif operation == 'fill_missing':
            column = params.get('column', '')
            method = params.get('method', '')
            desc = f"填充缺失值: {column} ({method})"
        elif operation == 'sort':
            column = params.get('column', '')
            ascending = params.get('ascending', True)
            order = "升序" if ascending else "降序"
            desc = f"排序: {column} ({order})"
        elif operation == 'split_column':
            column = params.get('column', '')
            delimiter = params.get('delimiter', '')
            desc = f"拆分列: {column} (分隔符: {delimiter})"
        elif operation == 'merge_columns':
            columns = params.get('columns', [])
            desc = f"合并列: {', '.join(columns)}"
        elif operation == 'replace_value':
            column = params.get('column', '')
            old_val = params.get('old_value', '')
            new_val = params.get('new_value', '')
            desc = f"替换值: {column} ({old_val} → {new_val})"
        elif operation == 'drop_duplicates':
            subset = params.get('subset', None)
            keep = params.get('keep', 'first')
            if subset:
                desc = f"去重: 按 {subset} (保留{keep})"
            else:
                desc = f"去重: 全部列 (保留{keep})"
        elif operation == 'strip_whitespace':
            column = params.get('column', '')
            desc = f"去除空格: {column}"
        elif operation == 'change_case':
            column = params.get('column', '')
            case_type = params.get('case_type', '')
            case_labels = {'lower': '小写', 'upper': '大写', 'title': '标题格式', 'capitalize': '首字母大写'}
            desc = f"大小写转换: {column} → {case_labels.get(case_type, case_type)}"
        elif operation == 'find_replace_regex':
            column = params.get('column', '')
            pattern = params.get('pattern', '')
            desc = f"正则替换: {column} (/{pattern}/)"
        elif operation == 'extract_substring':
            column = params.get('column', '')
            pattern = params.get('pattern', '')
            if pattern:
                desc = f"提取子串: {column} (模式: {pattern})"
            else:
                start = params.get('start', '')
                end = params.get('end', '')
                desc = f"提取子串: {column} [{start}:{end}]"
        elif operation == 'bin_column':
            column = params.get('column', '')
            bins = params.get('bins', 5)
            method = params.get('method', 'equal_width')
            method_label = '等宽' if method == 'equal_width' else '等频'
            desc = f"分箱: {column} ({method_label}, {bins}组)"
        elif operation == 'normalize':
            column = params.get('column', '')
            method = params.get('method', 'minmax')
            method_labels = {'minmax': 'Min-Max', 'zscore': 'Z-Score', 'robust': 'Robust'}
            desc = f"标准化: {column} ({method_labels.get(method, method)})"
        elif operation == 'drop_missing_rows':
            column = params.get('column', '')
            how = params.get('how', 'any')
            if column:
                desc = f"删除缺失行: 列 {column}"
            else:
                desc = f"删除缺失行: {how}"
        elif operation == 'duplicate_column':
            column = params.get('column', '')
            new_name = params.get('new_name', '')
            desc = f"复制列: {column} → {new_name}"
        elif operation == 'create_calculated':
            new_column = params.get('new_column', 'calculated')
            expression = params.get('expression', '')
            desc = f"计算列: {new_column} = {expression}"
        else:
            desc = f"{operation}"
        
        # 添加影响统计
        if affected_rows > 0 or affected_cols > 0:
            stats = []
            if affected_rows > 0:
                stats.append(f"{affected_rows}行")
            if affected_cols > 0:
                stats.append(f"{affected_cols}列")
            desc += f" (影响{', '.join(stats)})"
        
        return desc
    
    def navigate_to_step(self, step_index: int) -> List[Dict]:
        """导航到指定步骤，返回该步骤之前的流水线
        
        Args:
            step_index: 步骤索引（0-based）
        
        Returns:
            从开始到指定步骤的流水线列表
        """
        if 0 <= step_index < len(self.pipeline):
            self.current_step = step_index
            return self.pipeline[:step_index + 1]
        return []
    
    def export_pipeline(self) -> Dict:
        """导出流水线为JSON
        
        Returns:
            包含流水线信息的字典
        """
        return {
            'pipeline_id': str(uuid.uuid4()),
            'steps': self.pipeline,
            'current_step': self.current_step,
            'exported_at': datetime.now().isoformat()
        }
    
    def import_pipeline(self, pipeline_json: Dict) -> bool:
        """从JSON导入流水线
        
        Args:
            pipeline_json: 流水线JSON字典
        
        Returns:
            True如果导入成功，否则False
        """
        try:
            self.pipeline = pipeline_json.get('steps', [])
            self.current_step = pipeline_json.get('current_step', len(self.pipeline) - 1)
            return True
        except Exception:
            return False
    
    def get_pipeline(self) -> List[Dict]:
        """获取完整的操作流水线
        
        Returns:
            操作流水线列表
        """
        return self.pipeline.copy()
    
    def clear_pipeline(self):
        """清空流水线"""
        self.pipeline.clear()
        self.current_step = -1
