# -*- coding: utf-8 -*-
"""
代码生成服务 - 将操作转换为 Python 代码
"""
from typing import List, Dict, Any


class CodeGenerator:
    """代码生成器类"""

    def __init__(self):
        self.operations = []

    def add_operation(self, operation: Dict[str, Any]):
        """添加操作记录"""
        self.operations.append(operation)

    def clear_operations(self):
        """清空操作记录"""
        self.operations = []

    def generate_code(self) -> str:
        """
        生成 Python 代码

        Returns:
            生成的代码字符串
        """
        if not self.operations:
            return "# 暂无操作记录"

        code_lines = [
            "import pandas as pd",
            "import numpy as np",
            "",
            "# 加载数据",
            "df = pd.read_csv('your_data.csv')  # 请替换为实际文件路径",
            "",
            "# 数据处理操作",
        ]

        for i, op in enumerate(self.operations, 1):
            code_lines.append(f"\n# 操作 {i}: {self.get_operation_summary(op)}")
            code_lines.extend(self._generate_operation_code(op))

        code_lines.extend([
            "",
            "# 保存处理后的数据",
            "df.to_csv('processed_data.csv', index=False)",
        ])

        return "\n".join(code_lines)

    def _generate_operation_code(self, operation: Dict[str, Any]) -> List[str]:
        """
        根据操作类型生成对应代码

        Args:
            operation: 操作字典

        Returns:
            代码行列表
        """
        op_type = operation['type']
        params = operation.get('params', {})

        if op_type == "delete_columns":
            columns = params['columns']
            return [f"df = df.drop(columns={columns})"]

        elif op_type == "rename_column":
            old_name = params['old_name']
            new_name = params['new_name']
            return [f"df = df.rename(columns={{'{old_name}': '{new_name}'}})"]

        elif op_type == "split_column":
            column = params['column']
            delimiter = params['delimiter']
            new_columns = params.get('new_columns', [])
            if new_columns:
                return [
                    f"split_data = df['{column}'].str.split('{delimiter}', expand=True)",
                    f"split_data.columns = {new_columns}",
                    f"df = pd.concat([df, split_data], axis=1)"
                ]
            else:
                return [f"df[['{column}_1', '{column}_2']] = df['{column}'].str.split('{delimiter}', expand=True)"]

        elif op_type == "merge_columns":
            columns = params['columns']
            new_column = params['new_column']
            delimiter = params.get('delimiter', ' ')
            return [f"df['{new_column}'] = df{columns}.astype(str).agg('{delimiter}'.join, axis=1)"]

        elif op_type == "fill_missing":
            column = params['column']
            strategy = params['strategy']

            if strategy == "mean":
                return [f"df['{column}'] = df['{column}'].fillna(df['{column}'].mean())"]
            elif strategy == "median":
                return [f"df['{column}'] = df['{column}'].fillna(df['{column}'].median())"]
            elif strategy == "mode":
                return [f"df['{column}'] = df['{column}'].fillna(df['{column}'].mode()[0])"]
            elif strategy == "constant":
                value = params.get('constant_value', 0)
                return [f"df['{column}'] = df['{column}'].fillna({repr(value)})"]
            elif strategy == "ffill":
                return [f"df['{column}'] = df['{column}'].fillna(method='ffill')"]
            elif strategy == "bfill":
                return [f"df['{column}'] = df['{column}'].fillna(method='bfill')"]

        elif op_type == "drop_missing_rows":
            columns = params.get('columns')
            if columns:
                return [f"df = df.dropna(subset={columns})"]
            else:
                return ["df = df.dropna()"]

        elif op_type == "convert_type":
            column = params['column']
            target_type = params['target_type']

            if target_type == "int":
                return [f"df['{column}'] = pd.to_numeric(df['{column}'], errors='coerce').astype('Int64')"]
            elif target_type == "float":
                return [f"df['{column}'] = pd.to_numeric(df['{column}'], errors='coerce')"]
            elif target_type == "str":
                return [f"df['{column}'] = df['{column}'].astype(str)"]
            elif target_type == "datetime":
                return [f"df['{column}'] = pd.to_datetime(df['{column}'], errors='coerce')"]
            elif target_type == "bool":
                return [f"df['{column}'] = df['{column}'].astype(bool)"]
            elif target_type == "category":
                return [f"df['{column}'] = df['{column}'].astype('category')"]

        elif op_type == "filter_data":
            conditions = params['conditions']
            condition_strs = []
            for cond in conditions:
                col = cond['column']
                op = cond['operator']
                val = cond['value']

                if op == "==":
                    condition_strs.append(f"(df['{col}'] == {repr(val)})")
                elif op == "!=":
                    condition_strs.append(f"(df['{col}'] != {repr(val)})")
                elif op == ">":
                    condition_strs.append(f"(df['{col}'] > {repr(val)})")
                elif op == ">=":
                    condition_strs.append(f"(df['{col}'] >= {repr(val)})")
                elif op == "<":
                    condition_strs.append(f"(df['{col}'] < {repr(val)})")
                elif op == "<=":
                    condition_strs.append(f"(df['{col}'] <= {repr(val)})")
                elif op == "contains":
                    condition_strs.append(f"df['{col}'].astype(str).str.contains({repr(val)}, na=False)")

            return [f"df = df[{' & '.join(condition_strs)}]"]

        elif op_type == "sort_data":
            columns = params['columns']
            ascending = params.get('ascending', True)
            return [f"df = df.sort_values(by={columns}, ascending={ascending})"]

        elif op_type == "remove_duplicates":
            columns = params.get('columns')
            keep = params.get('keep', 'first')
            if columns:
                return [f"df = df.drop_duplicates(subset={columns}, keep='{keep}')"]
            else:
                return [f"df = df.drop_duplicates(keep='{keep}')"]

        elif op_type == "strip_text":
            column = params['column']
            return [f"df['{column}'] = df['{column}'].astype(str).str.strip()"]

        elif op_type == "convert_case":
            column = params['column']
            case_type = params['case_type']
            return [f"df['{column}'] = df['{column}'].astype(str).str.{case_type}()"]

        elif op_type == "find_replace":
            column = params['column']
            find = params['find']
            replace = params['replace']
            regex = params.get('regex', False)
            return [f"df['{column}'] = df['{column}'].astype(str).str.replace({repr(find)}, {repr(replace)}, regex={regex})"]

        elif op_type == "binning":
            column = params['column']
            bins = params['bins']
            new_column = params.get('new_column', f"{column}_binned")
            return [f"df['{new_column}'] = pd.cut(df['{column}'], bins={bins})"]

        elif op_type == "standardize":
            column = params['column']
            new_column = params.get('new_column', f"{column}_standardized")
            return [f"df['{new_column}'] = (df['{column}'] - df['{column}'].mean()) / df['{column}'].std()"]

        elif op_type == "normalize":
            column = params['column']
            new_column = params.get('new_column', f"{column}_normalized")
            return [f"df['{new_column}'] = (df['{column}'] - df['{column}'].min()) / (df['{column}'].max() - df['{column}'].min())"]

        elif op_type == "add_calculated_column":
            new_column = params['new_column']
            expression = params['expression']
            return [f"df['{new_column}'] = df.eval('{expression}')"]

        else:
            return [f"# 未知操作类型: {op_type}"]

    def get_operation_summary(self, operation: Dict[str, Any]) -> str:
        """
        获取操作摘要描述

        Args:
            operation: 操作字典

        Returns:
            操作摘要字符串
        """
        return operation.get('description', '未知操作')
