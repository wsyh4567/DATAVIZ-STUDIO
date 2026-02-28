"""
测试预览引擎
"""

import pytest
import pandas as pd
import numpy as np
from services.data_workshop.preview_engine import PreviewEngine


class TestPreviewEngine:
    """测试PreviewEngine类"""
    
    def test_preview_limits_rows(self):
        """测试预览行数限制"""
        df = pd.DataFrame({'a': range(2000)})
        engine = PreviewEngine(max_preview_rows=1000)
        
        result = engine.compute_preview(df, [])
        
        assert len(result['preview_df']) == 1000
        assert result['full_rows'] == 2000
        assert result['is_truncated'] == True
    
    def test_empty_pipeline(self):
        """测试空操作流水线"""
        df = pd.DataFrame({'a': [1, 2, 3]})
        engine = PreviewEngine()
        
        result = engine.compute_preview(df, [])
        
        assert len(result['preview_df']) == 3
        assert result['affected_rows'] == 0
        assert result['affected_cols'] == 0
    
    def test_filter_operation(self):
        """测试筛选操作"""
        df = pd.DataFrame({'age': [15, 20, 25, 30]})
        pipeline = [{
            'operation': 'filter',
            'params': {'column': 'age', 'operator': '>', 'value': 18}
        }]
        engine = PreviewEngine()
        
        result = engine.compute_preview(df, pipeline)
        
        assert result['full_rows'] == 3
        assert result['affected_rows'] == 1  # 1行被过滤掉
    
    def test_drop_column_operation(self):
        """测试删除列操作"""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})
        pipeline = [{
            'operation': 'drop_column',
            'params': {'column': 'b'}
        }]
        engine = PreviewEngine()
        
        result = engine.compute_preview(df, pipeline)
        
        assert result['full_cols'] == 2
        assert result['affected_cols'] == 1
        assert 'b' not in result['preview_df'].columns
    
    def test_multiple_operations(self):
        """测试多个操作"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['NYC', 'LA', 'SF']
        })
        pipeline = [
            {'operation': 'filter', 'params': {'column': 'age', 'operator': '>', 'value': 25}},
            {'operation': 'drop_column', 'params': {'column': 'city'}}
        ]
        engine = PreviewEngine()
        
        result = engine.compute_preview(df, pipeline)
        
        assert result['full_rows'] == 2
        assert result['full_cols'] == 2
        assert 'city' not in result['preview_df'].columns
    
    def test_up_to_step(self):
        """测试执行到指定步骤"""
        df = pd.DataFrame({'a': [1, 2, 3, 4, 5]})
        pipeline = [
            {'operation': 'filter', 'params': {'column': 'a', 'operator': '>', 'value': 2}},
            {'operation': 'filter', 'params': {'column': 'a', 'operator': '<', 'value': 5}}
        ]
        engine = PreviewEngine()
        
        # 只执行第一步
        result = engine.compute_preview(df, pipeline, up_to_step=0)
        
        assert result['full_rows'] == 3  # 3, 4, 5
    
    def test_cache(self):
        """测试缓存功能"""
        df = pd.DataFrame({'a': range(1000)})
        pipeline = [{'operation': 'filter', 'params': {'column': 'a', 'operator': '>', 'value': 500}}]
        engine = PreviewEngine()
        
        # 第一次计算
        result1 = engine.compute_preview(df, pipeline)
        time1 = result1['execution_time']
        
        # 第二次应该使用缓存，更快
        result2 = engine.compute_preview(df, pipeline)
        time2 = result2['execution_time']
        
        assert result1['full_rows'] == result2['full_rows']
        # 缓存的结果应该更快（或相同）
        assert time2 <= time1 * 1.1  # 允许10%的误差
    
    def test_clear_cache(self):
        """测试清除缓存"""
        df = pd.DataFrame({'a': range(100)})
        pipeline = [{'operation': 'filter', 'params': {'column': 'a', 'operator': '>', 'value': 50}}]
        engine = PreviewEngine()
        
        # 计算并缓存
        engine.compute_preview(df, pipeline)
        assert len(engine.cache) > 0
        
        # 清除缓存
        engine.clear_cache()
        assert len(engine.cache) == 0
    
    def test_error_handling(self):
        """测试错误处理"""
        df = pd.DataFrame({'a': [1, 2, 3]})
        pipeline = [{
            'operation': 'filter',
            'params': {'column': 'nonexistent', 'operator': '>', 'value': 1}
        }]
        engine = PreviewEngine()
        
        result = engine.compute_preview(df, pipeline)
        
        assert 'error' in result
        assert 'failed_step' in result
    
    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        # 创建10万行数据
        df = pd.DataFrame({
            'id': range(100000),
            'value': np.random.randn(100000)
        })
        engine = PreviewEngine(max_preview_rows=1000)
        
        import time
        start_time = time.time()
        result = engine.compute_preview(df, [])
        elapsed = time.time() - start_time
        
        # 预览应该在1秒内完成
        assert elapsed < 1.0
        assert len(result['preview_df']) == 1000
        assert result['full_rows'] == 100000
    
    def test_original_data_unchanged(self):
        """测试原始数据不变"""
        df = pd.DataFrame({'a': [1, 2, 3, 4, 5]})
        df_original = df.copy()
        
        pipeline = [{'operation': 'filter', 'params': {'column': 'a', 'operator': '>', 'value': 2}}]
        engine = PreviewEngine()
        
        engine.compute_preview(df, pipeline)
        
        # 原始数据应该完全不变
        pd.testing.assert_frame_equal(df, df_original)
