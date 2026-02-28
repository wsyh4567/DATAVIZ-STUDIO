# -*- coding: utf-8 -*-
"""
数据清洗服务单元测试
"""

import pytest
import pandas as pd
import numpy as np
from services.data_cleaner import (
    ColumnSplitter,
    ColumnConcatenator,
    StringReplacer,
    StringCleaner
)


class TestColumnSplitter:
    """测试列拆分功能"""
    
    def test_split_column_basic(self):
        """测试基本列拆分"""
        df = pd.DataFrame({'name': ['张-三', '李-四', '王-五']})
        
        result = ColumnSplitter.split_column(
            df, 'name', '-', max_split=1, 
            new_names=['姓', '名']
        )
        
        assert '姓' in result.columns
        assert '名' in result.columns
        assert result['姓'].iloc[0] == '张'
        assert result['名'].iloc[0] == '三'
    
    def test_split_column_with_separator(self):
        """测试使用分隔符拆分"""
        df = pd.DataFrame({'email': ['user@example.com', 'admin@test.org']})
        
        result = ColumnSplitter.split_column(
            df, 'email', '@', max_split=1,
            new_names=['username', 'domain']
        )
        
        assert result['username'].iloc[0] == 'user'
        assert result['domain'].iloc[0] == 'example.com'
    
    def test_split_column_auto_names(self):
        """测试自动生成列名"""
        df = pd.DataFrame({'data': ['a,b,c', 'd,e,f']})
        
        result = ColumnSplitter.split_column(df, 'data', ',')
        
        assert 'data_part_1' in result.columns
        assert 'data_part_2' in result.columns
        assert 'data_part_3' in result.columns
    
    def test_split_column_invalid_column(self):
        """测试无效列名"""
        df = pd.DataFrame({'name': ['张三']})
        
        with pytest.raises(ValueError, match="列 'invalid' 不存在"):
            ColumnSplitter.split_column(df, 'invalid', '')
    
    def test_split_column_max_split(self):
        """测试限制拆分数量"""
        df = pd.DataFrame({'data': ['a,b,c,d,e']})
        
        result = ColumnSplitter.split_column(df, 'data', ',', max_split=2)
        
        # 应该只拆分成3列（max_split=2 表示最多拆分2次）
        assert result['data_part_1'].iloc[0] == 'a'
        assert result['data_part_2'].iloc[0] == 'b'
        assert result['data_part_3'].iloc[0] == 'c,d,e'
    
    def test_generate_code(self):
        """测试代码生成"""
        code = ColumnSplitter.generate_code(
            'name', '', max_split=1, new_names=['姓', '名']
        )
        
        assert "split_data = df['name']" in code
        assert "df['姓'] = split_data[0]" in code
        assert "df['名'] = split_data[1]" in code


class TestColumnConcatenator:
    """测试列合并功能"""
    
    def test_concatenate_columns_basic(self):
        """测试基本列合并"""
        df = pd.DataFrame({
            '姓': ['张', '李', '王'],
            '名': ['三', '四', '五']
        })
        
        result = ColumnConcatenator.concatenate_columns(
            df, ['姓', '名'], '', '全名'
        )
        
        assert '全名' in result.columns
        assert result['全名'].iloc[0] == '张三'
        assert result['全名'].iloc[1] == '李四'
    
    def test_concatenate_with_separator(self):
        """测试使用分隔符合并"""
        df = pd.DataFrame({
            'first': ['John', 'Jane'],
            'last': ['Doe', 'Smith']
        })
        
        result = ColumnConcatenator.concatenate_columns(
            df, ['first', 'last'], ' ', 'full_name'
        )
        
        assert result['full_name'].iloc[0] == 'John Doe'
        assert result['full_name'].iloc[1] == 'Jane Smith'
    
    def test_concatenate_drop_original(self):
        """测试删除原列"""
        df = pd.DataFrame({
            'col1': ['a', 'b'],
            'col2': ['c', 'd']
        })
        
        result = ColumnConcatenator.concatenate_columns(
            df, ['col1', 'col2'], '-', 'merged', drop_original=True
        )
        
        assert 'merged' in result.columns
        assert 'col1' not in result.columns
        assert 'col2' not in result.columns
    
    def test_concatenate_invalid_column(self):
        """测试无效列名"""
        df = pd.DataFrame({'col1': ['a']})
        
        with pytest.raises(ValueError, match="列 'invalid' 不存在"):
            ColumnConcatenator.concatenate_columns(
                df, ['col1', 'invalid'], '', 'merged'
            )
    
    def test_concatenate_empty_columns(self):
        """测试空列列表"""
        df = pd.DataFrame({'col1': ['a']})
        
        with pytest.raises(ValueError, match="必须至少选择一列"):
            ColumnConcatenator.concatenate_columns(df, [], '', 'merged')
    
    def test_concatenate_empty_name(self):
        """测试空新列名"""
        df = pd.DataFrame({'col1': ['a']})
        
        with pytest.raises(ValueError, match="必须提供新列名"):
            ColumnConcatenator.concatenate_columns(df, ['col1'], '', '')
    
    def test_generate_code(self):
        """测试代码生成"""
        code = ColumnConcatenator.generate_code(
            ['姓', '名'], '', '全名', drop_original=True
        )
        
        assert "df['全名']" in code
        assert "['姓', '名']" in code
        assert "drop(columns=" in code


class TestStringReplacer:
    """测试字符串替换功能"""
    
    def test_find_replace_basic(self):
        """测试基本查找替换"""
        df = pd.DataFrame({'text': ['hello world', 'hello python']})
        
        result = StringReplacer.find_replace(
            df, 'text', 'hello', 'hi'
        )
        
        assert result['text'].iloc[0] == 'hi world'
        assert result['text'].iloc[1] == 'hi python'
    
    def test_find_replace_case_insensitive(self):
        """测试不区分大小写"""
        df = pd.DataFrame({'text': ['Hello World', 'HELLO WORLD']})
        
        result = StringReplacer.find_replace(
            df, 'text', 'hello', 'hi', case_sensitive=False
        )
        
        assert result['text'].iloc[0] == 'hi World'
        assert result['text'].iloc[1] == 'hi WORLD'
    
    def test_find_replace_regex(self):
        """测试正则表达式"""
        df = pd.DataFrame({'text': ['test123', 'test456']})
        
        result = StringReplacer.find_replace(
            df, 'text', r'\d+', 'XXX', use_regex=True
        )
        
        assert result['text'].iloc[0] == 'testXXX'
        assert result['text'].iloc[1] == 'testXXX'
    
    def test_find_replace_invalid_column(self):
        """测试无效列名"""
        df = pd.DataFrame({'text': ['hello']})
        
        with pytest.raises(ValueError, match="列 'invalid' 不存在"):
            StringReplacer.find_replace(df, 'invalid', 'hello', 'hi')
    
    def test_find_replace_empty_find(self):
        """测试空查找内容"""
        df = pd.DataFrame({'text': ['hello']})
        
        with pytest.raises(ValueError, match="查找内容不能为空"):
            StringReplacer.find_replace(df, 'text', '', 'hi')
    
    def test_find_replace_invalid_regex(self):
        """测试无效正则表达式"""
        df = pd.DataFrame({'text': ['hello']})
        
        with pytest.raises(ValueError, match="正则表达式错误"):
            StringReplacer.find_replace(
                df, 'text', '[invalid', 'hi', use_regex=True
            )
    
    def test_generate_code(self):
        """测试代码生成"""
        code = StringReplacer.generate_code(
            'text', 'hello', 'hi', use_regex=False, case_sensitive=True
        )
        
        assert "df['text']" in code
        assert "'hello'" in code
        assert "'hi'" in code
        assert "case=True" in code
        assert "regex=False" in code


class TestStringCleaner:
    """测试字符串清理功能"""
    
    def test_strip_whitespace_both(self):
        """测试去除两端空格"""
        df = pd.DataFrame({'text': ['  hello  ', '  world  ']})
        
        result = StringCleaner.strip_whitespace(df, 'text', 'both')
        
        assert result['text'].iloc[0] == 'hello'
        assert result['text'].iloc[1] == 'world'
    
    def test_strip_whitespace_left(self):
        """测试去除左侧空格"""
        df = pd.DataFrame({'text': ['  hello  ']})
        
        result = StringCleaner.strip_whitespace(df, 'text', 'left')
        
        assert result['text'].iloc[0] == 'hello  '
    
    def test_strip_whitespace_right(self):
        """测试去除右侧空格"""
        df = pd.DataFrame({'text': ['  hello  ']})
        
        result = StringCleaner.strip_whitespace(df, 'text', 'right')
        
        assert result['text'].iloc[0] == '  hello'
    
    def test_strip_whitespace_all(self):
        """测试去除所有空格"""
        df = pd.DataFrame({'text': ['  hello  world  ']})
        
        result = StringCleaner.strip_whitespace(df, 'text', 'all')
        
        assert result['text'].iloc[0] == 'helloworld'
    
    def test_strip_invalid_mode(self):
        """测试无效模式"""
        df = pd.DataFrame({'text': ['hello']})
        
        with pytest.raises(ValueError, match="无效的模式"):
            StringCleaner.strip_whitespace(df, 'text', 'invalid')
    
    def test_case_conversion_upper(self):
        """测试转换为大写"""
        df = pd.DataFrame({'text': ['hello world']})
        
        result = StringCleaner.case_conversion(df, 'text', 'upper')
        
        assert result['text'].iloc[0] == 'HELLO WORLD'
    
    def test_case_conversion_lower(self):
        """测试转换为小写"""
        df = pd.DataFrame({'text': ['HELLO WORLD']})
        
        result = StringCleaner.case_conversion(df, 'text', 'lower')
        
        assert result['text'].iloc[0] == 'hello world'
    
    def test_case_conversion_title(self):
        """测试转换为标题格式"""
        df = pd.DataFrame({'text': ['hello world']})
        
        result = StringCleaner.case_conversion(df, 'text', 'title')
        
        assert result['text'].iloc[0] == 'Hello World'
    
    def test_case_conversion_capitalize(self):
        """测试首字母大写"""
        df = pd.DataFrame({'text': ['hello world']})
        
        result = StringCleaner.case_conversion(df, 'text', 'capitalize')
        
        assert result['text'].iloc[0] == 'Hello world'
    
    def test_case_invalid_type(self):
        """测试无效类型"""
        df = pd.DataFrame({'text': ['hello']})
        
        with pytest.raises(ValueError, match="无效的类型"):
            StringCleaner.case_conversion(df, 'text', 'invalid')
    
    def test_extract_substring_basic(self):
        """测试提取子字符串"""
        df = pd.DataFrame({'text': ['hello world']})
        
        result = StringCleaner.extract_substring(
            df, 'text', 0, 5, 'prefix'
        )
        
        assert result['prefix'].iloc[0] == 'hello'
    
    def test_extract_substring_no_end(self):
        """测试提取到末尾"""
        df = pd.DataFrame({'text': ['hello world']})
        
        result = StringCleaner.extract_substring(
            df, 'text', 6, None, 'suffix'
        )
        
        assert result['suffix'].iloc[0] == 'world'
    
    def test_extract_substring_overwrite(self):
        """测试覆盖原列"""
        df = pd.DataFrame({'text': ['hello world']})
        
        result = StringCleaner.extract_substring(df, 'text', 0, 5)
        
        assert result['text'].iloc[0] == 'hello'
    
    def test_extract_substring_negative_start(self):
        """测试负数起始位置"""
        df = pd.DataFrame({'text': ['hello']})
        
        with pytest.raises(ValueError, match="起始位置不能为负数"):
            StringCleaner.extract_substring(df, 'text', -1, 3)
    
    def test_extract_substring_invalid_range(self):
        """测试无效范围"""
        df = pd.DataFrame({'text': ['hello']})
        
        with pytest.raises(ValueError, match="结束位置必须大于起始位置"):
            StringCleaner.extract_substring(df, 'text', 5, 3)
    
    def test_generate_strip_code(self):
        """测试生成去除空格代码"""
        code = StringCleaner.generate_strip_code('text', 'both')
        
        assert "df['text']" in code
        assert "strip()" in code
    
    def test_generate_case_code(self):
        """测试生成大小写转换代码"""
        code = StringCleaner.generate_case_code('text', 'upper')
        
        assert "df['text']" in code
        assert "upper()" in code
    
    def test_generate_substring_code(self):
        """测试生成提取子字符串代码"""
        code = StringCleaner.generate_substring_code('text', 0, 5, 'prefix')
        
        assert "df['prefix']" in code
        assert "df['text']" in code
        assert "[0:5]" in code


class TestEdgeCases:
    """测试边界情况"""
    
    def test_empty_dataframe(self):
        """测试空数据框"""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            ColumnSplitter.split_column(df, 'col', ',')
    
    def test_single_row(self):
        """测试单行数据"""
        df = pd.DataFrame({'text': ['hello']})
        
        result = StringCleaner.case_conversion(df, 'text', 'upper')
        
        assert len(result) == 1
        assert result['text'].iloc[0] == 'HELLO'
    
    def test_null_values(self):
        """测试空值处理"""
        df = pd.DataFrame({'text': ['hello', None, 'world']})
        
        result = StringCleaner.case_conversion(df, 'text', 'upper')
        
        assert result['text'].iloc[0] == 'HELLO'
        assert result['text'].iloc[1] == 'NONE'  # None 转为字符串 'None'
        assert result['text'].iloc[2] == 'WORLD'
    
    def test_numeric_column(self):
        """测试数值列"""
        df = pd.DataFrame({'num': [1, 2, 3]})
        
        # 应该自动转换为字符串
        result = ColumnSplitter.split_column(df, 'num', '', max_split=1)
        
        assert 'num_part_1' in result.columns
    
    def test_large_dataframe(self):
        """测试大数据框性能"""
        df = pd.DataFrame({
            'text': ['hello world'] * 10000
        })
        
        result = StringReplacer.find_replace(df, 'text', 'hello', 'hi')
        
        assert len(result) == 10000
        assert result['text'].iloc[0] == 'hi world'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
