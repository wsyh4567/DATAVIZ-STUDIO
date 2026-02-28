"""
测试操作执行器
"""

import pytest
import pandas as pd
import numpy as np
from services.data_workshop.operation_executor import OperationExecutor


class TestOperationExecutor:
    """测试OperationExecutor类"""
    
    def test_execute_filter_greater_than(self):
        """测试大于筛选"""
        df = pd.DataFrame({'age': [15, 20, 25, 30]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_filter(df, {
            'column': 'age',
            'operator': '>',
            'value': 18
        })
        
        assert len(result_df) == 3
        assert all(result_df['age'] > 18)
        assert "df['age'] > 18" in code
    
    def test_execute_filter_equals(self):
        """测试等于筛选"""
        df = pd.DataFrame({'name': ['Alice', 'Bob', 'Alice']})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_filter(df, {
            'column': 'name',
            'operator': '==',
            'value': 'Alice'
        })
        
        assert len(result_df) == 2
        assert all(result_df['name'] == 'Alice')
    
    def test_execute_filter_contains(self):
        """测试包含筛选"""
        df = pd.DataFrame({'text': ['hello world', 'goodbye', 'hello there']})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_filter(df, {
            'column': 'text',
            'operator': 'contains',
            'value': 'hello'
        })
        
        assert len(result_df) == 2
        assert 'contains' in code
    
    def test_execute_drop_column(self):
        """测试删除单列"""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_drop_column(df, {'column': 'b'})
        
        assert 'b' not in result_df.columns
        assert len(result_df.columns) == 2
        assert "drop(columns=['b'])" in code
    
    def test_execute_drop_multiple_columns(self):
        """测试删除多列"""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_drop_column(df, {'columns': ['b', 'c']})
        
        assert 'b' not in result_df.columns
        assert 'c' not in result_df.columns
        assert len(result_df.columns) == 1
    
    def test_execute_rename_column(self):
        """测试重命名列"""
        df = pd.DataFrame({'old_name': [1, 2, 3]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_rename_column(df, {
            'old_name': 'old_name',
            'new_name': 'new_name'
        })
        
        assert 'new_name' in result_df.columns
        assert 'old_name' not in result_df.columns
        assert 'rename' in code
    
    def test_execute_type_conversion_to_int(self):
        """测试转换为整数"""
        df = pd.DataFrame({'value': ['1', '2', '3']})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_type_conversion(df, {
            'column': 'value',
            'target_type': 'int'
        })
        
        assert result_df['value'].dtype == 'Int64'
        assert 'to_numeric' in code
    
    def test_execute_type_conversion_to_float(self):
        """测试转换为浮点数"""
        df = pd.DataFrame({'value': ['1.5', '2.5', '3.5']})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_type_conversion(df, {
            'column': 'value',
            'target_type': 'float'
        })
        
        assert result_df['value'].dtype == 'float64'
    
    def test_execute_type_conversion_to_str(self):
        """测试转换为字符串"""
        df = pd.DataFrame({'value': [1, 2, 3]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_type_conversion(df, {
            'column': 'value',
            'target_type': 'str'
        })
        
        assert result_df['value'].dtype == 'object'
        assert all(isinstance(x, str) for x in result_df['value'])
    
    def test_execute_fill_missing_mean(self):
        """测试用均值填充缺失值"""
        df = pd.DataFrame({'value': [1.0, 2.0, np.nan, 4.0]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_fill_missing(df, {
            'column': 'value',
            'method': 'mean'
        })
        
        assert result_df['value'].isnull().sum() == 0
        assert 'mean()' in code
    
    def test_execute_fill_missing_median(self):
        """测试用中位数填充缺失值"""
        df = pd.DataFrame({'value': [1.0, 2.0, np.nan, 4.0]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_fill_missing(df, {
            'column': 'value',
            'method': 'median'
        })
        
        assert result_df['value'].isnull().sum() == 0
        assert 'median()' in code
    
    def test_execute_fill_missing_value(self):
        """测试用固定值填充缺失值"""
        df = pd.DataFrame({'value': [1.0, 2.0, np.nan, 4.0]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_fill_missing(df, {
            'column': 'value',
            'method': 'value',
            'value': 0
        })
        
        assert result_df['value'].isnull().sum() == 0
        assert result_df['value'].iloc[2] == 0
    
    def test_execute_drop_duplicates(self):
        """测试去重"""
        df = pd.DataFrame({'a': [1, 1, 2, 3], 'b': [4, 4, 5, 6]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_drop_duplicates(df, {})
        
        assert len(result_df) == 3
        assert 'drop_duplicates' in code
    
    def test_execute_drop_duplicates_subset(self):
        """测试基于特定列去重"""
        df = pd.DataFrame({'a': [1, 1, 2], 'b': [4, 5, 6]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_drop_duplicates(df, {
            'subset': ['a']
        })
        
        assert len(result_df) == 2
    
    def test_execute_sort_ascending(self):
        """测试升序排序"""
        df = pd.DataFrame({'value': [3, 1, 2]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_sort(df, {
            'column': 'value',
            'ascending': True
        })
        
        assert list(result_df['value']) == [1, 2, 3]
        assert 'sort_values' in code
    
    def test_execute_sort_descending(self):
        """测试降序排序"""
        df = pd.DataFrame({'value': [3, 1, 2]})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_sort(df, {
            'column': 'value',
            'ascending': False
        })
        
        assert list(result_df['value']) == [3, 2, 1]
    
    def test_execute_split_column(self):
        """测试列拆分"""
        df = pd.DataFrame({'name': ['John Doe', 'Jane Smith']})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_split_column(df, {
            'column': 'name',
            'delimiter': ' ',
            'new_columns': ['first_name', 'last_name']
        })
        
        assert 'first_name' in result_df.columns
        assert 'last_name' in result_df.columns
        assert 'name' not in result_df.columns
        assert result_df['first_name'].iloc[0] == 'John'
        assert result_df['last_name'].iloc[0] == 'Doe'
    
    def test_execute_split_column_max_split(self):
        """测试限制拆分数量"""
        df = pd.DataFrame({'text': ['a-b-c-d']})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_split_column(df, {
            'column': 'text',
            'delimiter': '-',
            'max_split': 2
        })
        
        # 应该拆分为3列（max_split=2表示最多拆分2次）
        assert len(result_df.columns) == 3
    
    def test_execute_merge_columns(self):
        """测试列合并"""
        df = pd.DataFrame({'first': ['John', 'Jane'], 'last': ['Doe', 'Smith']})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_merge_columns(df, {
            'columns': ['first', 'last'],
            'delimiter': ' ',
            'new_column': 'full_name'
        })
        
        assert 'full_name' in result_df.columns
        assert result_df['full_name'].iloc[0] == 'John Doe'
        assert result_df['full_name'].iloc[1] == 'Jane Smith'
    
    def test_execute_replace_value(self):
        """测试值替换"""
        df = pd.DataFrame({'status': ['active', 'inactive', 'active']})
        executor = OperationExecutor()
        
        result_df, code = executor.execute_replace_value(df, {
            'column': 'status',
            'old_value': 'active',
            'new_value': 'enabled'
        })
        
        assert result_df['status'].iloc[0] == 'enabled'
        assert result_df['status'].iloc[1] == 'inactive'
        assert 'replace' in code
    
    def test_execute_unsupported_operation(self):
        """测试不支持的操作"""
        df = pd.DataFrame({'a': [1, 2, 3]})
        executor = OperationExecutor()
        
        with pytest.raises(ValueError, match="不支持的操作类型"):
            executor.execute(df, 'unsupported_operation', {})
    
    def test_execute_filter_invalid_operator(self):
        """测试无效的筛选操作符"""
        df = pd.DataFrame({'a': [1, 2, 3]})
        executor = OperationExecutor()
        
        with pytest.raises(ValueError, match="不支持的筛选操作符"):
            executor.execute_filter(df, {
                'column': 'a',
                'operator': 'invalid',
                'value': 1
            })
    
    def test_execute_type_conversion_invalid_type(self):
        """测试无效的目标类型"""
        df = pd.DataFrame({'a': [1, 2, 3]})
        executor = OperationExecutor()
        
        with pytest.raises(ValueError, match="不支持的目标类型"):
            executor.execute_type_conversion(df, {
                'column': 'a',
                'target_type': 'invalid_type'
            })
    
    def test_execute_fill_missing_invalid_method(self):
        """测试无效的填充方法"""
        df = pd.DataFrame({'a': [1.0, np.nan, 3.0]})
        executor = OperationExecutor()
        
        with pytest.raises(ValueError, match="不支持的填充方法"):
            executor.execute_fill_missing(df, {
                'column': 'a',
                'method': 'invalid_method'
            })
    
    def test_original_dataframe_unchanged(self):
        """测试原始数据框不被修改"""
        df = pd.DataFrame({'a': [1, 2, 3, 4, 5]})
        df_original = df.copy()
        executor = OperationExecutor()
        
        # 执行筛选操作
        result_df, _ = executor.execute_filter(df, {
            'column': 'a',
            'operator': '>',
            'value': 2
        })
        
        # 原始数据框应该不变
        pd.testing.assert_frame_equal(df, df_original)
        # 结果数据框应该不同
        assert len(result_df) != len(df)
