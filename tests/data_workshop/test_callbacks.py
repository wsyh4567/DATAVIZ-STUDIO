"""
测试数据工坊回调功能
"""

import pytest
import pandas as pd
from datetime import datetime

from services.data_workshop.preview_engine import PreviewEngine
from services.data_workshop.step_manager import StepManager
from services.data_workshop.undo_redo_stack import UndoRedoStack
from services.data_workshop.code_generator import CodeGenerator


class TestCallbackIntegration:
    """测试回调集成功能"""
    
    def setup_method(self):
        """设置测试环境"""
        self.preview_engine = PreviewEngine(max_preview_rows=1000)
        self.step_manager = StepManager()
        self.undo_stack = UndoRedoStack()
        self.code_generator = CodeGenerator()
        
        # 创建测试数据
        self.test_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': ['25', '30', '35'],
            'city': ['NYC', 'LA', 'SF'],
            'salary': [50000, 60000, 75000]
        })
    
    def test_operation_execution_flow(self):
        """测试操作执行流程"""
        # 创建操作
        operation = {
            'step_id': 'test-1',
            'operation': 'filter',
            'params': {'column': 'city', 'operator': '==', 'value': 'NYC'},
            'timestamp': datetime.now().isoformat()
        }
        
        # 执行预览
        pipeline = [operation]
        result = self.preview_engine.compute_preview(self.test_df, pipeline)
        
        # 验证结果
        assert 'preview_df' in result
        assert len(result['preview_df']) == 1
        assert result['preview_df']['city'].iloc[0] == 'NYC'
    
    def test_undo_redo_flow(self):
        """测试撤销重做流程"""
        # 创建初始状态
        state1 = {'pipeline': [], 'timestamp': datetime.now().isoformat()}
        self.undo_stack.push_state(state1)
        
        # 添加操作
        state2 = {
            'pipeline': [{'operation': 'filter', 'params': {}}],
            'timestamp': datetime.now().isoformat()
        }
        self.undo_stack.push_state(state2)
        
        # 验证可以撤销
        assert self.undo_stack.can_undo()
        
        # 执行撤销
        previous_state = self.undo_stack.undo()
        assert previous_state == state1
        
        # 验证可以重做
        assert self.undo_stack.can_redo()
        
        # 执行重做
        next_state = self.undo_stack.redo()
        assert next_state == state2
    
    def test_code_generation_flow(self):
        """测试代码生成流程"""
        # 创建操作流水线
        pipeline = [
            {
                'operation': 'filter',
                'params': {'column': 'city', 'operator': '==', 'value': 'NYC'}
            },
            {
                'operation': 'type_conversion',
                'params': {'column': 'age', 'target_type': 'numeric'}
            },
            {
                'operation': 'sort',
                'params': {'column': 'salary', 'ascending': False}
            }
        ]
        
        # 生成代码
        code = self.code_generator.generate_code(
            pipeline,
            data_source='test.csv',
            include_imports=True,
            include_comments=True
        )
        
        # 验证代码包含必要元素
        assert 'import pandas as pd' in code
        assert 'pd.read_csv' in code
        assert "df[df['city'] == 'NYC']" in code
        assert 'pd.to_numeric' in code
        assert 'sort_values' in code
    
    def test_step_management_flow(self):
        """测试步骤管理流程"""
        # 添加步骤
        step_id1 = self.step_manager.add_step('filter', {'column': 'age'})
        step_id2 = self.step_manager.add_step('sort', {'column': 'salary'})
        
        # 验证步骤数量
        assert len(self.step_manager.pipeline) == 2
        
        # 删除步骤
        self.step_manager.remove_step(step_id1)
        assert len(self.step_manager.pipeline) == 1
        
        # 验证剩余步骤
        assert self.step_manager.pipeline[0]['step_id'] == step_id2
    
    def test_preview_with_multiple_operations(self):
        """测试多操作预览"""
        pipeline = [
            {
                'operation': 'type_conversion',
                'params': {'column': 'age', 'target_type': 'numeric'}
            },
            {
                'operation': 'filter',
                'params': {'column': 'age', 'operator': '>', 'value': 25}
            }
        ]
        
        result = self.preview_engine.compute_preview(self.test_df, pipeline)
        
        # 验证结果
        assert 'preview_df' in result
        assert len(result['preview_df']) == 2  # Bob and Charlie
        assert result['preview_df']['age'].dtype in ['int64', 'float64']


class TestCodeGenerator:
    """测试代码生成器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.generator = CodeGenerator()
    
    def test_generate_filter_code(self):
        """测试筛选代码生成"""
        params = {'column': 'age', 'operator': '>', 'value': 25}
        code = self.generator._generate_filter_code(params)
        
        assert "df[df['age'] > 25]" in code
        assert 'print' in code
    
    def test_generate_type_conversion_code(self):
        """测试类型转换代码生成"""
        params = {'column': 'age', 'target_type': 'numeric'}
        code = self.generator._generate_type_conversion_code(params)
        
        assert 'pd.to_numeric' in code
        assert "df['age']" in code
        assert "errors='coerce'" in code
    
    def test_generate_sort_code(self):
        """测试排序代码生成"""
        params = {'column': 'salary', 'ascending': False}
        code = self.generator._generate_sort_code(params)
        
        assert 'sort_values' in code
        assert "by='salary'" in code
        assert 'ascending=False' in code
    
    def test_generate_fill_missing_code(self):
        """测试填充缺失值代码生成"""
        # 测试固定值填充
        params = {'column': 'age', 'method': 'value', 'value': 0}
        code = self.generator._generate_fill_missing_code(params)
        assert 'fillna(0)' in code
        
        # 测试均值填充
        params = {'column': 'age', 'method': 'mean'}
        code = self.generator._generate_fill_missing_code(params)
        assert 'mean()' in code
    
    def test_generate_complete_code(self):
        """测试完整代码生成"""
        pipeline = [
            {'operation': 'filter', 'params': {'column': 'age', 'operator': '>', 'value': 25}},
            {'operation': 'sort', 'params': {'column': 'salary', 'ascending': False}}
        ]
        
        code = self.generator.generate_code(
            pipeline,
            data_source='data.csv',
            include_imports=True,
            include_comments=True
        )
        
        # 验证代码结构
        lines = code.split('\n')
        assert len(lines) > 5
        assert any('import pandas' in line for line in lines)
        assert any('read_csv' in line for line in lines)
        assert any('步骤1' in line for line in lines)
        assert any('步骤2' in line for line in lines)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
