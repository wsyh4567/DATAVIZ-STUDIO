# -*- coding: utf-8 -*-
"""
数据清洗服务 - 提供列操作和字符串处理功能

本模块提供数据清洗的核心功能，包括：
- 列拆分和合并
- 字符串查找替换
- 字符串清理（空格、大小写、子字符串）

所有操作都生成可执行的 Python 代码。
"""

from __future__ import annotations

from typing import List, Optional, Union
import pandas as pd
import re


class ColumnSplitter:
    """列拆分服务
    
    提供按分隔符拆分列的功能，支持多种分隔符和拆分选项。
    """
    
    @staticmethod
    def split_column(
        df: pd.DataFrame,
        column: str,
        separator: str,
        max_split: Optional[int] = None,
        new_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """拆分列
        
        Args:
            df: 输入数据框
            column: 要拆分的列名
            separator: 分隔符
            max_split: 最大拆分数（None = 全部拆分）
            new_names: 新列名列表（None = 自动生成）
        
        Returns:
            包含新列的数据框
        
        Raises:
            ValueError: 如果列不存在或参数无效
        
        Example:
            >>> df = pd.DataFrame({'name': ['张三', '李四']})
            >>> result = ColumnSplitter.split_column(
            ...     df, 'name', '', max_split=1, 
            ...     new_names=['姓', '名']
            ... )
        """
        if column not in df.columns:
            raise ValueError(f"列 '{column}' 不存在")
        
        # 执行拆分
        split_data = df[column].astype(str).str.split(
            separator, 
            n=max_split, 
            expand=True
        )
        
        # 生成新列名
        if new_names is None:
            new_names = [f"{column}_part_{i+1}" for i in range(split_data.shape[1])]
        elif len(new_names) < split_data.shape[1]:
            # 如果提供的列名不够，自动补充
            for i in range(len(new_names), split_data.shape[1]):
                new_names.append(f"{column}_part_{i+1}")
        
        # 添加新列到数据框
        df_result = df.copy()
        for i, name in enumerate(new_names[:split_data.shape[1]]):
            df_result[name] = split_data[i]
        
        return df_result
    
    @staticmethod
    def generate_code(
        column: str,
        separator: str,
        max_split: Optional[int] = None,
        new_names: Optional[List[str]] = None
    ) -> str:
        """生成列拆分的 Python 代码
        
        Args:
            column: 列名
            separator: 分隔符
            max_split: 最大拆分数
            new_names: 新列名列表
        
        Returns:
            可执行的 Python 代码
        """
        code_lines = [
            f"# 拆分列 '{column}'",
            f"split_data = df['{column}'].astype(str).str.split("
        ]
        
        # 添加分隔符参数
        if separator == '':
            code_lines.append(f"    '',")
        else:
            code_lines.append(f"    '{separator}',")
        
        # 添加 max_split 参数
        if max_split is not None:
            code_lines.append(f"    n={max_split},")
        
        code_lines.append("    expand=True")
        code_lines.append(")")
        code_lines.append("")
        
        # 添加新列
        if new_names:
            for i, name in enumerate(new_names):
                code_lines.append(f"df['{name}'] = split_data[{i}]")
        else:
            code_lines.append("# 自动生成列名")
            code_lines.append(f"for i in range(split_data.shape[1]):")
            code_lines.append(f"    df[f'{column}_part_{{i+1}}'] = split_data[i]")
        
        return "\n".join(code_lines)


class ColumnConcatenator:
    """列合并服务
    
    提供将多列合并为一列的功能。
    """
    
    @staticmethod
    def concatenate_columns(
        df: pd.DataFrame,
        columns: List[str],
        separator: str,
        new_name: str,
        drop_original: bool = False
    ) -> pd.DataFrame:
        """合并多列
        
        Args:
            df: 输入数据框
            columns: 要合并的列名列表
            separator: 分隔符
            new_name: 新列名
            drop_original: 是否删除原列
        
        Returns:
            包含新列的数据框
        
        Raises:
            ValueError: 如果列不存在或参数无效
        
        Example:
            >>> df = pd.DataFrame({'姓': ['张', '李'], '名': ['三', '四']})
            >>> result = ColumnConcatenator.concatenate_columns(
            ...     df, ['姓', '名'], '', '全名'
            ... )
        """
        # 验证列是否存在
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"列 '{col}' 不存在")
        
        if not columns:
            raise ValueError("必须至少选择一列")
        
        if not new_name:
            raise ValueError("必须提供新列名")
        
        # 合并列
        df_result = df.copy()
        df_result[new_name] = df_result[columns].astype(str).agg(
            separator.join, 
            axis=1
        )
        
        # 删除原列（如果需要）
        if drop_original:
            df_result = df_result.drop(columns=columns)
        
        return df_result
    
    @staticmethod
    def generate_code(
        columns: List[str],
        separator: str,
        new_name: str,
        drop_original: bool = False
    ) -> str:
        """生成列合并的 Python 代码
        
        Args:
            columns: 列名列表
            separator: 分隔符
            new_name: 新列名
            drop_original: 是否删除原列
        
        Returns:
            可执行的 Python 代码
        """
        cols_str = str(columns)
        code_lines = [
            f"# 合并列 {cols_str}",
            f"df['{new_name}'] = df{cols_str}.astype(str).agg('{separator}'.join, axis=1)"
        ]
        
        if drop_original:
            code_lines.append("")
            code_lines.append(f"# 删除原列")
            code_lines.append(f"df = df.drop(columns={cols_str})")
        
        return "\n".join(code_lines)


class StringReplacer:
    """字符串替换服务
    
    提供查找和替换字符串的功能，支持正则表达式。
    """
    
    @staticmethod
    def find_replace(
        df: pd.DataFrame,
        column: str,
        find_value: str,
        replace_value: str,
        use_regex: bool = False,
        case_sensitive: bool = True
    ) -> pd.DataFrame:
        """查找并替换
        
        Args:
            df: 输入数据框
            column: 列名
            find_value: 查找内容
            replace_value: 替换内容
            use_regex: 是否使用正则表达式
            case_sensitive: 是否区分大小写
        
        Returns:
            替换后的数据框
        
        Raises:
            ValueError: 如果列不存在或参数无效
        
        Example:
            >>> df = pd.DataFrame({'text': ['Hello World', 'hello world']})
            >>> result = StringReplacer.find_replace(
            ...     df, 'text', 'hello', 'hi', 
            ...     case_sensitive=False
            ... )
        """
        if column not in df.columns:
            raise ValueError(f"列 '{column}' 不存在")
        
        if not find_value:
            raise ValueError("查找内容不能为空")
        
        df_result = df.copy()
        
        try:
            df_result[column] = df_result[column].astype(str).str.replace(
                find_value,
                replace_value,
                case=case_sensitive,
                regex=use_regex
            )
        except re.error as e:
            raise ValueError(f"正则表达式错误: {str(e)}")
        
        return df_result
    
    @staticmethod
    def generate_code(
        column: str,
        find_value: str,
        replace_value: str,
        use_regex: bool = False,
        case_sensitive: bool = True
    ) -> str:
        """生成查找替换的 Python 代码
        
        Args:
            column: 列名
            find_value: 查找内容
            replace_value: 替换内容
            use_regex: 是否使用正则表达式
            case_sensitive: 是否区分大小写
        
        Returns:
            可执行的 Python 代码
        """
        code_lines = [
            f"# 查找替换: '{find_value}' → '{replace_value}'",
            f"df['{column}'] = df['{column}'].astype(str).str.replace("
        ]
        
        # 转义特殊字符
        find_escaped = find_value.replace("'", "\\'")
        replace_escaped = replace_value.replace("'", "\\'")
        
        code_lines.append(f"    '{find_escaped}',")
        code_lines.append(f"    '{replace_escaped}',")
        code_lines.append(f"    case={case_sensitive},")
        code_lines.append(f"    regex={use_regex}")
        code_lines.append(")")
        
        return "\n".join(code_lines)


class StringCleaner:
    """字符串清理服务
    
    提供字符串清理功能，包括空格处理、大小写转换、子字符串提取。
    """
    
    @staticmethod
    def strip_whitespace(
        df: pd.DataFrame,
        column: str,
        mode: str = 'both'
    ) -> pd.DataFrame:
        """去除空格
        
        Args:
            df: 输入数据框
            column: 列名
            mode: 模式 ('both', 'left', 'right', 'all')
        
        Returns:
            清理后的数据框
        
        Raises:
            ValueError: 如果列不存在或模式无效
        
        Example:
            >>> df = pd.DataFrame({'text': ['  hello  ', '  world  ']})
            >>> result = StringCleaner.strip_whitespace(df, 'text', 'both')
        """
        if column not in df.columns:
            raise ValueError(f"列 '{column}' 不存在")
        
        valid_modes = ['both', 'left', 'right', 'all']
        if mode not in valid_modes:
            raise ValueError(f"无效的模式: {mode}，必须是 {valid_modes} 之一")
        
        df_result = df.copy()
        
        if mode == 'both':
            df_result[column] = df_result[column].astype(str).str.strip()
        elif mode == 'left':
            df_result[column] = df_result[column].astype(str).str.lstrip()
        elif mode == 'right':
            df_result[column] = df_result[column].astype(str).str.rstrip()
        elif mode == 'all':
            df_result[column] = df_result[column].astype(str).str.replace(
                r'\s+', '', regex=True
            )
        
        return df_result
    
    @staticmethod
    def case_conversion(
        df: pd.DataFrame,
        column: str,
        case_type: str
    ) -> pd.DataFrame:
        """大小写转换
        
        Args:
            df: 输入数据框
            column: 列名
            case_type: 转换类型 ('upper', 'lower', 'title', 'capitalize')
        
        Returns:
            转换后的数据框
        
        Raises:
            ValueError: 如果列不存在或类型无效
        
        Example:
            >>> df = pd.DataFrame({'text': ['hello world', 'HELLO WORLD']})
            >>> result = StringCleaner.case_conversion(df, 'text', 'title')
        """
        if column not in df.columns:
            raise ValueError(f"列 '{column}' 不存在")
        
        valid_types = ['upper', 'lower', 'title', 'capitalize']
        if case_type not in valid_types:
            raise ValueError(f"无效的类型: {case_type}，必须是 {valid_types} 之一")
        
        df_result = df.copy()
        
        if case_type == 'upper':
            df_result[column] = df_result[column].astype(str).str.upper()
        elif case_type == 'lower':
            df_result[column] = df_result[column].astype(str).str.lower()
        elif case_type == 'title':
            df_result[column] = df_result[column].astype(str).str.title()
        elif case_type == 'capitalize':
            df_result[column] = df_result[column].astype(str).str.capitalize()
        
        return df_result
    
    @staticmethod
    def extract_substring(
        df: pd.DataFrame,
        column: str,
        start: int,
        end: Optional[int] = None,
        new_name: Optional[str] = None
    ) -> pd.DataFrame:
        """提取子字符串
        
        Args:
            df: 输入数据框
            column: 列名
            start: 起始位置（从0开始）
            end: 结束位置（None = 到末尾）
            new_name: 新列名（None = 覆盖原列）
        
        Returns:
            包含提取结果的数据框
        
        Raises:
            ValueError: 如果列不存在或参数无效
        
        Example:
            >>> df = pd.DataFrame({'text': ['hello', 'world']})
            >>> result = StringCleaner.extract_substring(
            ...     df, 'text', 0, 3, 'prefix'
            ... )
        """
        if column not in df.columns:
            raise ValueError(f"列 '{column}' 不存在")
        
        if start < 0:
            raise ValueError("起始位置不能为负数")
        
        if end is not None and end <= start:
            raise ValueError("结束位置必须大于起始位置")
        
        df_result = df.copy()
        target_col = new_name if new_name else column
        
        df_result[target_col] = df_result[column].astype(str).str[start:end]
        
        return df_result
    
    @staticmethod
    def generate_strip_code(column: str, mode: str) -> str:
        """生成去除空格的代码"""
        code_lines = [f"# 去除空格: {mode}"]
        
        if mode == 'both':
            code_lines.append(f"df['{column}'] = df['{column}'].astype(str).str.strip()")
        elif mode == 'left':
            code_lines.append(f"df['{column}'] = df['{column}'].astype(str).str.lstrip()")
        elif mode == 'right':
            code_lines.append(f"df['{column}'] = df['{column}'].astype(str).str.rstrip()")
        elif mode == 'all':
            code_lines.append(f"df['{column}'] = df['{column}'].astype(str).str.replace(r'\\s+', '', regex=True)")
        
        return "\n".join(code_lines)
    
    @staticmethod
    def generate_case_code(column: str, case_type: str) -> str:
        """生成大小写转换的代码"""
        case_names = {
            'upper': '全部大写',
            'lower': '全部小写',
            'title': '标题格式',
            'capitalize': '首字母大写'
        }
        
        code_lines = [
            f"# 大小写转换: {case_names.get(case_type, case_type)}",
            f"df['{column}'] = df['{column}'].astype(str).str.{case_type}()"
        ]
        
        return "\n".join(code_lines)
    
    @staticmethod
    def generate_substring_code(
        column: str,
        start: int,
        end: Optional[int],
        new_name: Optional[str]
    ) -> str:
        """生成提取子字符串的代码"""
        target_col = new_name if new_name else column
        end_str = str(end) if end is not None else ''
        
        code_lines = [
            f"# 提取子字符串: 位置 {start}:{end_str}",
            f"df['{target_col}'] = df['{column}'].astype(str).str[{start}:{end_str}]"
        ]
        
        return "\n".join(code_lines)
