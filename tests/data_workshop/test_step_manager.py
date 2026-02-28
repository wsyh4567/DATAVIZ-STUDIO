"""
测试步骤管理器
"""

import pytest
from services.data_workshop.step_manager import StepManager


class TestStepManager:
    """测试StepManager类"""
    
    def test_initial_state(self):
        """测试初始状态"""
        manager = StepManager()
        
        assert len(manager.pipeline) == 0
        assert manager.current_step == -1
    
    def test_add_step(self):
        """测试添加步骤"""
        manager = StepManager()
        
        step_id = manager.add_step('filter', {'column': 'age', 'operator': '>', 'value': 18})
        
        assert len(manager.pipeline) == 1
        assert manager.current_step == 0
        assert manager.pipeline[0]['step_id'] == step_id
        assert manager.pipeline[0]['operation'] == 'filter'
        assert manager.pipeline[0]['params'] == {'column': 'age', 'operator': '>', 'value': 18}
    
    def test_remove_step(self):
        """测试删除步骤"""
        manager = StepManager()
        
        step_id1 = manager.add_step('filter', {'column': 'age', 'operator': '>', 'value': 18})
        step_id2 = manager.add_step('drop_column', {'column': 'temp'})
        
        # 删除第一个步骤
        result = manager.remove_step(step_id1)
        
        assert result == True
        assert len(manager.pipeline) == 1
        assert manager.pipeline[0]['step_id'] == step_id2
    
    def test_remove_nonexistent_step(self):
        """测试删除不存在的步骤"""
        manager = StepManager()
        
        result = manager.remove_step('nonexistent-id')
        
        assert result == False
    
    def test_update_step(self):
        """测试更新步骤参数"""
        manager = StepManager()
        
        step_id = manager.add_step('filter', {'column': 'age', 'operator': '>', 'value': 18})
        
        # 更新参数
        new_params = {'column': 'age', 'operator': '>=', 'value': 20}
        result = manager.update_step(step_id, new_params)
        
        assert result == True
        assert manager.pipeline[0]['params'] == new_params
    
    def test_update_nonexistent_step(self):
        """测试更新不存在的步骤"""
        manager = StepManager()
        
        result = manager.update_step('nonexistent-id', {})
        
        assert result == False
    
    def test_reorder_steps(self):
        """测试重新排序步骤"""
        manager = StepManager()
        
        step_id1 = manager.add_step('filter', {'column': 'age', 'operator': '>', 'value': 18})
        step_id2 = manager.add_step('drop_column', {'column': 'temp'})
        step_id3 = manager.add_step('sort', {'column': 'name', 'ascending': True})
        
        # 重新排序：2, 1, 3
        result = manager.reorder_steps([step_id2, step_id1, step_id3])
        
        assert result == True
        assert manager.pipeline[0]['step_id'] == step_id2
        assert manager.pipeline[1]['step_id'] == step_id1
        assert manager.pipeline[2]['step_id'] == step_id3
    
    def test_reorder_steps_invalid_count(self):
        """测试重排序时步骤数量不匹配"""
        manager = StepManager()
        
        step_id1 = manager.add_step('filter', {})
        step_id2 = manager.add_step('drop_column', {})
        
        # 只提供一个ID，应该失败
        result = manager.reorder_steps([step_id1])
        
        assert result == False
    
    def test_reorder_steps_invalid_id(self):
        """测试重排序时包含不存在的ID"""
        manager = StepManager()
        
        step_id1 = manager.add_step('filter', {})
        
        # 包含不存在的ID
        result = manager.reorder_steps([step_id1, 'nonexistent-id'])
        
        assert result == False
    
    def test_get_step_description_filter(self):
        """测试筛选操作的描述"""
        manager = StepManager()
        
        step = {
            'operation': 'filter',
            'params': {'column': 'age', 'operator': '>', 'value': 18},
            'affected_rows': 100,
            'affected_cols': 0
        }
        
        desc = manager.get_step_description(step)
        
        assert 'age' in desc
        assert '>' in desc
        assert '18' in desc
        assert '100行' in desc
    
    def test_get_step_description_drop_column(self):
        """测试删除列操作的描述"""
        manager = StepManager()
        
        step = {
            'operation': 'drop_column',
            'params': {'column': 'temp_col'},
            'affected_rows': 0,
            'affected_cols': 1
        }
        
        desc = manager.get_step_description(step)
        
        assert '删除列' in desc
        assert 'temp_col' in desc
        assert '1列' in desc
    
    def test_get_step_description_rename_column(self):
        """测试重命名列操作的描述"""
        manager = StepManager()
        
        step = {
            'operation': 'rename_column',
            'params': {'old_name': 'old_col', 'new_name': 'new_col'},
            'affected_rows': 0,
            'affected_cols': 0
        }
        
        desc = manager.get_step_description(step)
        
        assert '重命名列' in desc
        assert 'old_col' in desc
        assert 'new_col' in desc
    
    def test_get_step_description_type_conversion(self):
        """测试类型转换操作的描述"""
        manager = StepManager()
        
        step = {
            'operation': 'type_conversion',
            'params': {'column': 'price', 'target_type': 'float'},
            'affected_rows': 0,
            'affected_cols': 0
        }
        
        desc = manager.get_step_description(step)
        
        assert '类型转换' in desc
        assert 'price' in desc
        assert 'float' in desc
    
    def test_navigate_to_step(self):
        """测试导航到指定步骤"""
        manager = StepManager()
        
        manager.add_step('filter', {'column': 'age', 'operator': '>', 'value': 18})
        manager.add_step('drop_column', {'column': 'temp'})
        manager.add_step('sort', {'column': 'name', 'ascending': True})
        
        # 导航到第二步（索引1）
        pipeline = manager.navigate_to_step(1)
        
        assert len(pipeline) == 2
        assert manager.current_step == 1
    
    def test_navigate_to_invalid_step(self):
        """测试导航到无效步骤"""
        manager = StepManager()
        
        manager.add_step('filter', {})
        
        # 导航到不存在的步骤
        pipeline = manager.navigate_to_step(10)
        
        assert len(pipeline) == 0
    
    def test_export_pipeline(self):
        """测试导出流水线"""
        manager = StepManager()
        
        manager.add_step('filter', {'column': 'age', 'operator': '>', 'value': 18})
        manager.add_step('drop_column', {'column': 'temp'})
        
        exported = manager.export_pipeline()
        
        assert 'pipeline_id' in exported
        assert 'steps' in exported
        assert 'current_step' in exported
        assert 'exported_at' in exported
        assert len(exported['steps']) == 2
    
    def test_import_pipeline(self):
        """测试导入流水线"""
        manager = StepManager()
        
        # 创建要导入的流水线
        pipeline_json = {
            'pipeline_id': 'test-id',
            'steps': [
                {'step_id': 'step1', 'operation': 'filter', 'params': {}},
                {'step_id': 'step2', 'operation': 'drop_column', 'params': {}}
            ],
            'current_step': 1
        }
        
        result = manager.import_pipeline(pipeline_json)
        
        assert result == True
        assert len(manager.pipeline) == 2
        assert manager.current_step == 1
    
    def test_import_invalid_pipeline(self):
        """测试导入无效流水线"""
        manager = StepManager()
        
        # 无效的JSON
        result = manager.import_pipeline({'invalid': 'data'})
        
        # 应该成功但流水线为空
        assert result == True
        assert len(manager.pipeline) == 0
    
    def test_get_pipeline(self):
        """测试获取流水线"""
        manager = StepManager()
        
        manager.add_step('filter', {})
        manager.add_step('drop_column', {})
        
        pipeline = manager.get_pipeline()
        
        assert len(pipeline) == 2
        # 应该返回副本，不影响原始流水线
        pipeline.append({'test': 'data'})
        assert len(manager.pipeline) == 2
    
    def test_clear_pipeline(self):
        """测试清空流水线"""
        manager = StepManager()
        
        manager.add_step('filter', {})
        manager.add_step('drop_column', {})
        
        manager.clear_pipeline()
        
        assert len(manager.pipeline) == 0
        assert manager.current_step == -1
    
    def test_multiple_operations(self):
        """测试多个操作的完整流程"""
        manager = StepManager()
        
        # 添加多个步骤
        step_id1 = manager.add_step('filter', {'column': 'age', 'operator': '>', 'value': 18})
        step_id2 = manager.add_step('drop_column', {'column': 'temp'})
        step_id3 = manager.add_step('sort', {'column': 'name', 'ascending': True})
        
        # 更新第二个步骤
        manager.update_step(step_id2, {'column': 'other_temp'})
        
        # 删除第一个步骤
        manager.remove_step(step_id1)
        
        # 验证结果
        assert len(manager.pipeline) == 2
        assert manager.pipeline[0]['step_id'] == step_id2
        assert manager.pipeline[0]['params']['column'] == 'other_temp'
        assert manager.pipeline[1]['step_id'] == step_id3
