# -*- coding: utf-8 -*-
"""
数据清洗服务 - 处理各种数据清洗操作
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union


class DataCleaner:
    """数据清洗服务类"""

    @staticmethod
    def delete_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        删除指定列

        Args:
            df: 数据框
            columns: 要删除的列名列表

        Returns:
            处理后的数据框
        """
        return df.drop(columns=columns, errors='ignore')

    @staticmethod
    def rename_column(df: pd.DataFrame, old_name: str, new_name: str) -> pd.DataFrame:
        """
        重命名列

        Args:
            df: 数据框
            old_name: 原列名
            new_name: 新列名

        Returns:
            处理后的数据框
        """
        return df.rename(columns={old_name: new_name})

    @staticmethod
    def split_column(df: pd.DataFrame, column: str, delimiter: str,
                     new_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        拆分列

        Args:
            df: 数据框
            column: 要拆分的列名
            delimiter: 分隔符
            new_columns: 新列名列表（可选）

        Returns:
            处理后的数据框
        """
        split_data = df[column].str.split(delimiter, expand=True)

        if new_columns:
            split_data.columns = new_columns[:split_data.shape[1]]
        else:
            split_data.columns = [f"{column}_{i+1}" for i in range(split_data.shape[1])]

        # 在原列后插入新列
        col_idx = df.columns.get_loc(column)
        result = pd.concat([df.iloc[:, :col_idx+1], split_data, df.iloc[:, col_idx+1:]], axis=1)

        return result

    @staticmethod
    def merge_columns(df: pd.DataFrame, columns: List[str],
                     new_column: str, delimiter: str = " ") -> pd.DataFrame:
        """
        合并列

        Args:
            df: 数据框
            columns: 要合并的列名列表
            new_column: 新列名
            delimiter: 分隔符

        Returns:
            处理后的数据框
        """
        df[new_column] = df[columns].astype(str).agg(delimiter.join, axis=1)
        return df

    @staticmethod
    def fill_missing(df: pd.DataFrame, column: str, strategy: str,
                    constant_value: Any = None) -> pd.DataFrame:
        """
        填充缺失值

        Args:
            df: 数据框
            column: 列名
            strategy: 填充策略 (mean/median/mode/constant/ffill/bfill)
            constant_value: 固定值（当strategy为constant时使用）

        Returns:
            处理后的数据框
        """
        df = df.copy()

        if strategy == "mean":
            df[column] = df[column].fillna(df[column].mean())
        elif strategy == "median":
            df[column] = df[column].fillna(df[column].median())
        elif strategy == "mode":
            mode_value = df[column].mode()
            if len(mode_value) > 0:
                df[column] = df[column].fillna(mode_value[0])
        elif strategy == "constant":
            df[column] = df[column].fillna(constant_value)
        elif strategy == "ffill":
            df[column] = df[column].fillna(method='ffill')
        elif strategy == "bfill":
            df[column] = df[column].fillna(method='bfill')

        return df

    @staticmethod
    def drop_missing_rows(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        删除包含缺失值的行

        Args:
            df: 数据框
            columns: 指定列（可选），如果为None则检查所有列

        Returns:
            处理后的数据框
        """
        if columns:
            return df.dropna(subset=columns)
        return df.dropna()

    @staticmethod
    def convert_type(df: pd.DataFrame, column: str, target_type: str) -> pd.DataFrame:
        """
        转换数据类型

        Args:
            df: 数据框
            column: 列名
            target_type: 目标类型 (int/float/str/datetime/bool/category)

        Returns:
            处理后的数据框
        """
        df = df.copy()

        try:
            if target_type == "int":
                df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
            elif target_type == "float":
                df[column] = pd.to_numeric(df[column], errors='coerce')
            elif target_type == "str":
                df[column] = df[column].astype(str)
            elif target_type == "datetime":
                df[column] = pd.to_datetime(df[column], errors='coerce')
            elif target_type == "bool":
                df[column] = df[column].astype(bool)
            elif target_type == "category":
                df[column] = df[column].astype('category')
        except Exception as e:
            raise ValueError(f"类型转换失败: {str(e)}")

        return df

    @staticmethod
    def filter_data(df: pd.DataFrame, conditions: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        根据条件筛选数据

        Args:
            df: 数据框
            conditions: 条件列表，每个条件包含 column, operator, value

        Returns:
            筛选后的数据框
        """
        mask = pd.Series([True] * len(df))

        for condition in conditions:
            column = condition['column']
            operator = condition['operator']
            value = condition['value']

            if operator == "==":
                mask &= (df[column] == value)
            elif operator == "!=":
                mask &= (df[column] != value)
            elif operator == ">":
                mask &= (df[column] > value)
            elif operator == ">=":
                mask &= (df[column] >= value)
            elif operator == "<":
                mask &= (df[column] < value)
            elif operator == "<=":
                mask &= (df[column] <= value)
            elif operator == "contains":
                mask &= df[column].astype(str).str.contains(str(value), na=False)
            elif operator == "startswith":
                mask &= df[column].astype(str).str.startswith(str(value), na=False)
            elif operator == "endswith":
                mask &= df[column].astype(str).str.endswith(str(value), na=False)

        return df[mask]

    @staticmethod
    def sort_data(df: pd.DataFrame, columns: List[str],
                 ascending: Union[bool, List[bool]] = True) -> pd.DataFrame:
        """
        排序数据

        Args:
            df: 数据框
            columns: 排序列名列表
            ascending: 升序或降序

        Returns:
            排序后的数据框
        """
        return df.sort_values(by=columns, ascending=ascending)

    @staticmethod
    def remove_duplicates(df: pd.DataFrame, columns: Optional[List[str]] = None,
                         keep: str = 'first') -> pd.DataFrame:
        """
        去除重复行

        Args:
            df: 数据框
            columns: 判断重复的列（可选）
            keep: 保留策略 (first/last/False)

        Returns:
            去重后的数据框
        """
        return df.drop_duplicates(subset=columns, keep=keep)

    @staticmethod
    def strip_text(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        去除文本列的首尾空格

        Args:
            df: 数据框
            column: 列名

        Returns:
            处理后的数据框
        """
        df = df.copy()
        df[column] = df[column].astype(str).str.strip()
        return df

    @staticmethod
    def convert_case(df: pd.DataFrame, column: str, case_type: str) -> pd.DataFrame:
        """
        转换文本大小写

        Args:
            df: 数据框
            column: 列名
            case_type: 类型 (upper/lower/title/capitalize)

        Returns:
            处理后的数据框
        """
        df = df.copy()

        if case_type == "upper":
            df[column] = df[column].astype(str).str.upper()
        elif case_type == "lower":
            df[column] = df[column].astype(str).str.lower()
        elif case_type == "title":
            df[column] = df[column].astype(str).str.title()
        elif case_type == "capitalize":
            df[column] = df[column].astype(str).str.capitalize()

        return df

    @staticmethod
    def find_replace(df: pd.DataFrame, column: str, find: str,
                    replace: str, regex: bool = False) -> pd.DataFrame:
        """
        查找替换

        Args:
            df: 数据框
            column: 列名
            find: 查找内容
            replace: 替换内容
            regex: 是否使用正则表达式

        Returns:
            处理后的数据框
        """
        df = df.copy()
        df[column] = df[column].astype(str).str.replace(find, replace, regex=regex)
        return df

    @staticmethod
    def binning(df: pd.DataFrame, column: str, bins: int,
               labels: Optional[List[str]] = None) -> pd.DataFrame:
        """
        数值分箱

        Args:
            df: 数据框
            column: 列名
            bins: 箱数
            labels: 标签（可选）

        Returns:
            处理后的数据框
        """
        df = df.copy()
        new_column = f"{column}_binned"
        df[new_column] = pd.cut(df[column], bins=bins, labels=labels)
        return df

    @staticmethod
    def standardize(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        标准化（Z-score）

        Args:
            df: 数据框
            column: 列名

        Returns:
            处理后的数据框
        """
        df = df.copy()
        new_column = f"{column}_standardized"
        df[new_column] = (df[column] - df[column].mean()) / df[column].std()
        return df

    @staticmethod
    def normalize(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        归一化（Min-Max）

        Args:
            df: 数据框
            column: 列名

        Returns:
            处理后的数据框
        """
        df = df.copy()
        new_column = f"{column}_normalized"
        df[new_column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
        return df

    @staticmethod
    def add_calculated_column(df: pd.DataFrame, new_column: str,
                            expression: str) -> pd.DataFrame:
        """
        添加计算列

        Args:
            df: 数据框
            new_column: 新列名
            expression: 计算表达式

        Returns:
            处理后的数据框
        """
        df = df.copy()
        df[new_column] = df.eval(expression)
        return df
