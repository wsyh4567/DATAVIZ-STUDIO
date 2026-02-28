"""
测试数据模型类
"""

import pytest
from datetime import datetime
import pandas as pd
from services.data_workshop.models import Operation, PreviewResult, ColumnAnalysis, QualityReport


class TestOperation:
    """测试Operation类"""
    
    def test_to_dict(self):
        """测试序列化为字典"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        op = Operation(
            step_id='test-id',
            operation='filter',
            params={'column': 'age', 'operator': '>', 'value': 18},
            timestamp=timestamp,
            affected_rows=100,
            affected_cols=0,
            execution_time=0.5
        )
        
        result = op.to_dict()
        
        assert result['step_id'] == 'test-id'
        assert result['operation'] == 'filter'
        assert result['params'] == {'column': 'age', 'operator': '>', 'value': 18}
        assert result['timestamp'] == '2024-01-01T12:00:00'
        assert result['affected_rows'] == 100
        assert result['affected_cols'] == 0
        assert result['execution_time'] == 0.5
    
    def test_from_dict(self):
        """测试从字典反序列化"""
        data = {
            'step_id': 'test-id',
            'operation': 'filter',
            'params': {'column': 'age', 'operator': '>', 'value': 18},
            'timestamp': '2024-01-01T12:00:00',
            'affected_rows': 100,
            'affected_cols': 0,
            'execution_time': 0.5
        }
        
        op = Operation.from_dict(data)
        
        assert op.step_id == 'test-id'
        assert op.operation == 'filter'
        assert op.params == {'column': 'age', 'operator': '>', 'value': 18}
        assert op.timestamp == datetime(2024, 1, 1, 12, 0, 0)
        assert op.affected_rows == 100
        assert op.affected_cols == 0
        assert op.execution_time == 0.5
    
    def test_roundtrip(self):
        """测试序列化和反序列化的往返"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        original = Operation(
            step_id='test-id',
            operation='filter',
            params={'column': 'age', 'operator': '>', 'value': 18},
            timestamp=timestamp
        )
        
        # 序列化然后反序列化
        data = original.to_dict()
        restored = Operation.from_dict(data)
        
        assert restored.step_id == original.step_id
        assert restored.operation == original.operation
        assert restored.params == original.params
        assert restored.timestamp == original.timestamp
    
    def test_empty_params(self):
        """测试空参数"""
        timestamp = datetime.now()
        op = Operation(
            step_id='test-id',
            operation='test',
            params={},
            timestamp=timestamp
        )
        
        result = op.to_dict()
        assert result['params'] == {}
    
    def test_special_characters_in_params(self):
        """测试参数中的特殊字符"""
        timestamp = datetime.now()
        op = Operation(
            step_id='test-id',
            operation='filter',
            params={'column': 'name', 'operator': 'contains', 'value': 'O\'Brien'},
            timestamp=timestamp
        )
        
        result = op.to_dict()
        assert result['params']['value'] == 'O\'Brien'
        
        # 测试往返
        restored = Operation.from_dict(result)
        assert restored.params['value'] == 'O\'Brien'


class TestPreviewResult:
    """测试PreviewResult类"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        result = PreviewResult(
            preview_df=df,
            full_rows=100,
            full_cols=2,
            affected_rows=10,
            affected_cols=0,
            execution_time=0.5,
            is_truncated=True
        )
        
        data = result.to_dict()
        
        assert len(data['preview_data']) == 3
        assert data['columns'] == ['a', 'b']
        assert 'a' in data['dtypes']
        assert 'b' in data['dtypes']
        assert data['full_rows'] == 100
        assert data['full_cols'] == 2
        assert data['affected_rows'] == 10
        assert data['affected_cols'] == 0
        assert data['execution_time'] == 0.5
        assert data['is_truncated'] == True
    
    def test_empty_dataframe(self):
        """测试空数据框"""
        df = pd.DataFrame()
        result = PreviewResult(
            preview_df=df,
            full_rows=0,
            full_cols=0,
            affected_rows=0,
            affected_cols=0,
            execution_time=0.0,
            is_truncated=False
        )
        
        data = result.to_dict()
        
        assert len(data['preview_data']) == 0
        assert len(data['columns']) == 0
        assert data['full_rows'] == 0
