"""
操作执行器

将操作对象转换为pandas代码并执行
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any


class OperationExecutor:
    """操作执行器

    职责：
    - 执行各种数据操作
    - 生成对应的pandas代码
    - 处理操作错误
    """

    def __init__(self):
        """初始化操作执行器"""
        self.operation_map = {
            'filter': self.execute_filter,
            'drop_column': self.execute_drop_column,
            'rename_column': self.execute_rename_column,
            'type_conversion': self.execute_type_conversion,
            'fill_missing': self.execute_fill_missing,
            'drop_duplicates': self.execute_drop_duplicates,
            'sort': self.execute_sort,
            'split_column': self.execute_split_column,
            'merge_columns': self.execute_merge_columns,
            'replace_value': self.execute_replace_value,
            # 新增操作
            'strip_whitespace': self.execute_strip,
            'change_case': self.execute_change_case,
            'find_replace_regex': self.execute_regex_replace,
            'extract_substring': self.execute_extract,
            'bin_column': self.execute_bin,
            'normalize': self.execute_normalize,
            'drop_missing_rows': self.execute_drop_na,
            'duplicate_column': self.execute_duplicate_col,
            'create_calculated': self.execute_calculated,
        }

    def execute(self, df: pd.DataFrame, operation: str, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行操作

        Args:
            df: 输入数据框
            operation: 操作类型
            params: 操作参数

        Returns:
            (结果数据框, 对应的pandas代码)

        Raises:
            ValueError: 如果操作类型不支持
        """
        if operation not in self.operation_map:
            raise ValueError(f"不支持的操作类型: {operation}")

        return self.operation_map[operation](df, params)

    def execute_filter(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行筛选操作"""
        column = params['column']
        operator = params['operator']
        value = params['value']

        # 尝试转换数值
        try:
            numeric_value = float(value)
            if numeric_value == int(numeric_value):
                numeric_value = int(numeric_value)
            if operator in ('>', '<', '>=', '<='):
                value = numeric_value
        except (ValueError, TypeError):
            pass

        if operator == '==':
            result_df = df[df[column] == value].copy()
            code = f"df = df[df['{column}'] == {repr(value)}]"
        elif operator == '!=':
            result_df = df[df[column] != value].copy()
            code = f"df = df[df['{column}'] != {repr(value)}]"
        elif operator == '>':
            result_df = df[df[column] > value].copy()
            code = f"df = df[df['{column}'] > {value}]"
        elif operator == '<':
            result_df = df[df[column] < value].copy()
            code = f"df = df[df['{column}'] < {value}]"
        elif operator == '>=':
            result_df = df[df[column] >= value].copy()
            code = f"df = df[df['{column}'] >= {value}]"
        elif operator == '<=':
            result_df = df[df[column] <= value].copy()
            code = f"df = df[df['{column}'] <= {value}]"
        elif operator == 'contains':
            case_sensitive = params.get('case_sensitive', True)
            result_df = df[df[column].str.contains(str(value), case=case_sensitive, na=False)].copy()
            code = f"df = df[df['{column}'].astype(str).str.contains({repr(value)}, case={case_sensitive}, na=False)]"
        elif operator == 'not_contains':
            case_sensitive = params.get('case_sensitive', True)
            result_df = df[~df[column].astype(str).str.contains(str(value), case=case_sensitive, na=False)].copy()
            code = f"df = df[~df['{column}'].astype(str).str.contains({repr(value)}, case={case_sensitive}, na=False)]"
        elif operator == 'startswith':
            result_df = df[df[column].str.startswith(str(value), na=False)].copy()
            code = f"df = df[df['{column}'].astype(str).str.startswith({repr(value)}, na=False)]"
        elif operator == 'endswith':
            result_df = df[df[column].str.endswith(str(value), na=False)].copy()
            code = f"df = df[df['{column}'].astype(str).str.endswith({repr(value)}, na=False)]"
        elif operator == 'isnull':
            result_df = df[df[column].isnull()].copy()
            code = f"df = df[df['{column}'].isnull()]"
        elif operator == 'notnull':
            result_df = df[df[column].notnull()].copy()
            code = f"df = df[df['{column}'].notnull()]"
        elif operator == 'isin':
            if not isinstance(value, list):
                value = [value]
            result_df = df[df[column].astype(str).isin(value)].copy()
            code = f"df = df[df['{column}'].astype(str).isin({repr(value)})]"
        else:
            raise ValueError(f"不支持的筛选操作符: {operator}")

        return result_df, code

    def execute_drop_column(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行删除列操作"""
        if 'columns' in params:
            columns = params['columns']
            result_df = df.drop(columns=columns).copy()
            code = f"df = df.drop(columns={columns})"
        else:
            column = params['column']
            result_df = df.drop(columns=[column]).copy()
            code = f"df = df.drop(columns=['{column}'])"

        return result_df, code

    def execute_rename_column(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行重命名列操作"""
        old_name = params['old_name']
        new_name = params['new_name']

        result_df = df.rename(columns={old_name: new_name}).copy()
        code = f"df = df.rename(columns={{'{old_name}': '{new_name}'}})"

        return result_df, code

    def execute_type_conversion(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行类型转换操作"""
        column = params['column']
        target_type = params['target_type']

        result_df = df.copy()

        if target_type in ['int', 'int64', 'integer']:
            result_df[column] = pd.to_numeric(result_df[column], errors='coerce').astype('Int64')
            code = f"df['{column}'] = pd.to_numeric(df['{column}'], errors='coerce').astype('Int64')"
        elif target_type in ['float', 'float64', 'numeric', 'number']:
            result_df[column] = pd.to_numeric(result_df[column], errors='coerce')
            code = f"df['{column}'] = pd.to_numeric(df['{column}'], errors='coerce')"
        elif target_type in ['str', 'string', 'text']:
            result_df[column] = result_df[column].astype(str)
            code = f"df['{column}'] = df['{column}'].astype(str)"
        elif target_type in ['datetime', 'date', 'datetime64']:
            result_df[column] = pd.to_datetime(result_df[column], errors='coerce')
            code = f"df['{column}'] = pd.to_datetime(df['{column}'], errors='coerce')"
        elif target_type in ['bool', 'boolean']:
            result_df[column] = result_df[column].astype(bool)
            code = f"df['{column}'] = df['{column}'].astype(bool)"
        else:
            raise ValueError(f"不支持的目标类型: {target_type}")

        return result_df, code

    def execute_fill_missing(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行缺失值填充操作"""
        column = params['column']
        method = params['method']

        result_df = df.copy()

        if method == 'mean':
            fill_value = result_df[column].mean()
            result_df[column] = result_df[column].fillna(fill_value)
            code = f"df['{column}'] = df['{column}'].fillna(df['{column}'].mean())"
        elif method == 'median':
            fill_value = result_df[column].median()
            result_df[column] = result_df[column].fillna(fill_value)
            code = f"df['{column}'] = df['{column}'].fillna(df['{column}'].median())"
        elif method == 'mode':
            fill_value = result_df[column].mode()[0] if not result_df[column].mode().empty else None
            result_df[column] = result_df[column].fillna(fill_value)
            code = f"df['{column}'] = df['{column}'].fillna(df['{column}'].mode()[0])"
        elif method == 'ffill':
            result_df[column] = result_df[column].ffill()
            code = f"df['{column}'] = df['{column}'].ffill()"
        elif method == 'bfill':
            result_df[column] = result_df[column].bfill()
            code = f"df['{column}'] = df['{column}'].bfill()"
        elif method == 'value':
            value = params.get('value', 0)
            result_df[column] = result_df[column].fillna(value)
            code = f"df['{column}'] = df['{column}'].fillna({repr(value)})"
        else:
            raise ValueError(f"不支持的填充方法: {method}")

        return result_df, code

    def execute_drop_duplicates(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行去重操作"""
        subset = params.get('subset', None)
        keep = params.get('keep', 'first')

        result_df = df.drop_duplicates(subset=subset, keep=keep).copy()

        if subset:
            code = f"df = df.drop_duplicates(subset={subset}, keep='{keep}')"
        else:
            code = f"df = df.drop_duplicates(keep='{keep}')"

        return result_df, code

    def execute_sort(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行排序操作"""
        column = params['column']
        ascending = params.get('ascending', True)

        result_df = df.sort_values(by=column, ascending=ascending).copy()
        code = f"df = df.sort_values(by='{column}', ascending={ascending})"

        return result_df, code

    def execute_split_column(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行列拆分操作"""
        column = params['column']
        delimiter = params['delimiter']
        max_split = params.get('max_split', -1)
        new_columns = params.get('new_columns', None)

        result_df = df.copy()

        split_data = result_df[column].str.split(delimiter, n=max_split, expand=True)

        if new_columns:
            split_data.columns = new_columns[:len(split_data.columns)]
        else:
            split_data.columns = [f"{column}_{i+1}" for i in range(len(split_data.columns))]

        result_df = pd.concat([result_df, split_data], axis=1)
        result_df = result_df.drop(columns=[column])

        code = f"""split_cols = df['{column}'].str.split('{delimiter}', n={max_split}, expand=True)
split_cols.columns = {list(split_data.columns)}
df = pd.concat([df, split_cols], axis=1)
df = df.drop(columns=['{column}'])"""

        return result_df, code

    def execute_merge_columns(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行列合并操作"""
        columns = params['columns']
        delimiter = params['delimiter']
        new_column = params.get('new_column', '_'.join(columns))

        result_df = df.copy()
        result_df[new_column] = result_df[columns].astype(str).agg(delimiter.join, axis=1)

        code = f"df['{new_column}'] = df[{columns}].astype(str).agg('{delimiter}'.join, axis=1)"

        return result_df, code

    def execute_replace_value(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行值替换操作"""
        column = params['column']
        old_value = params['old_value']
        new_value = params['new_value']

        result_df = df.copy()
        result_df[column] = result_df[column].replace(old_value, new_value)

        code = f"df['{column}'] = df['{column}'].replace({repr(old_value)}, {repr(new_value)})"

        return result_df, code

    # ========================================================================
    # 新增操作
    # ========================================================================

    def execute_strip(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """去除空格

        Args:
            params: {'column': str}
        """
        column = params['column']
        result_df = df.copy()
        result_df[column] = result_df[column].astype(str).str.strip()
        code = f"df['{column}'] = df['{column}'].astype(str).str.strip()"
        return result_df, code

    def execute_change_case(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """大小写转换

        Args:
            params: {'column': str, 'case_type': str}
                case_type: upper / lower / title / capitalize
        """
        column = params['column']
        case_type = params.get('case_type', 'lower')

        result_df = df.copy()
        case_methods = {
            'upper': ('str.upper()', lambda s: s.str.upper()),
            'lower': ('str.lower()', lambda s: s.str.lower()),
            'title': ('str.title()', lambda s: s.str.title()),
            'capitalize': ('str.capitalize()', lambda s: s.str.capitalize()),
        }

        if case_type not in case_methods:
            raise ValueError(f"不支持的大小写类型: {case_type}")

        method_str, method_fn = case_methods[case_type]
        result_df[column] = method_fn(result_df[column].astype(str))
        code = f"df['{column}'] = df['{column}'].astype(str).{method_str}"

        return result_df, code

    def execute_regex_replace(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """正则替换

        Args:
            params: {'column': str, 'pattern': str, 'replacement': str, 'is_regex': bool}
        """
        column = params['column']
        pattern = params['pattern']
        replacement = params.get('replacement', '')
        is_regex = params.get('is_regex', True)

        result_df = df.copy()
        result_df[column] = result_df[column].astype(str).str.replace(
            pattern, replacement, regex=is_regex
        )
        code = f"df['{column}'] = df['{column}'].astype(str).str.replace({repr(pattern)}, {repr(replacement)}, regex={is_regex})"

        return result_df, code

    def execute_extract(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """提取子串

        Args:
            params: {'column': str, 'pattern': str} 或 {'column': str, 'start': int, 'end': int}
        """
        column = params['column']
        result_df = df.copy()

        if 'pattern' in params and params['pattern']:
            pattern = params['pattern']
            result_df[f"{column}_extracted"] = result_df[column].astype(str).str.extract(
                f"({pattern})", expand=False
            )
            code = f"df['{column}_extracted'] = df['{column}'].astype(str).str.extract(r'({pattern})', expand=False)"
        else:
            start = int(params.get('start', 0))
            end = params.get('end', None)
            end = int(end) if end is not None and end != '' else None
            result_df[f"{column}_extracted"] = result_df[column].astype(str).str[start:end]
            code = f"df['{column}_extracted'] = df['{column}'].astype(str).str[{start}:{end}]"

        return result_df, code

    def execute_bin(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """分箱操作

        Args:
            params: {'column': str, 'bins': int, 'labels': list|None, 'method': str}
                method: equal_width / equal_freq
        """
        column = params['column']
        bins = int(params.get('bins', 5))
        labels = params.get('labels', None)
        method = params.get('method', 'equal_width')

        result_df = df.copy()
        new_col = f"{column}_binned"

        if method == 'equal_freq':
            result_df[new_col] = pd.qcut(
                result_df[column], q=bins, labels=labels, duplicates='drop'
            )
            code = f"df['{new_col}'] = pd.qcut(df['{column}'], q={bins}, labels={labels}, duplicates='drop')"
        else:  # equal_width
            result_df[new_col] = pd.cut(
                result_df[column], bins=bins, labels=labels
            )
            code = f"df['{new_col}'] = pd.cut(df['{column}'], bins={bins}, labels={labels})"

        # 转为字符串避免 JSON 序列化问题
        result_df[new_col] = result_df[new_col].astype(str)

        return result_df, code

    def execute_normalize(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """标准化/归一化

        Args:
            params: {'column': str, 'method': str}
                method: minmax / zscore / robust
        """
        column = params['column']
        method = params.get('method', 'minmax')

        result_df = df.copy()
        col_data = pd.to_numeric(result_df[column], errors='coerce')
        new_col = f"{column}_normalized"

        if method == 'minmax':
            min_val = col_data.min()
            max_val = col_data.max()
            range_val = max_val - min_val
            if range_val == 0:
                result_df[new_col] = 0.0
            else:
                result_df[new_col] = (col_data - min_val) / range_val
            code = f"df['{new_col}'] = (df['{column}'] - df['{column}'].min()) / (df['{column}'].max() - df['{column}'].min())"
        elif method == 'zscore':
            mean = col_data.mean()
            std = col_data.std()
            if std == 0:
                result_df[new_col] = 0.0
            else:
                result_df[new_col] = (col_data - mean) / std
            code = f"df['{new_col}'] = (df['{column}'] - df['{column}'].mean()) / df['{column}'].std()"
        elif method == 'robust':
            median = col_data.median()
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                result_df[new_col] = 0.0
            else:
                result_df[new_col] = (col_data - median) / iqr
            code = f"df['{new_col}'] = (df['{column}'] - df['{column}'].median()) / (df['{column}'].quantile(0.75) - df['{column}'].quantile(0.25))"
        else:
            raise ValueError(f"不支持的标准化方法: {method}")

        return result_df, code

    def execute_drop_na(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """删除缺失行

        Args:
            params: {'column': str|None, 'how': str, 'threshold': int|None}
        """
        column = params.get('column', None)
        how = params.get('how', 'any')
        threshold = params.get('threshold', None)

        result_df = df.copy()

        kwargs = {}
        if column:
            kwargs['subset'] = [column] if isinstance(column, str) else column
        if threshold is not None and threshold != '':
            kwargs['thresh'] = int(threshold)
        else:
            kwargs['how'] = how

        result_df = result_df.dropna(**kwargs).copy()

        parts = ["df = df.dropna("]
        kw_strs = []
        if 'subset' in kwargs:
            kw_strs.append(f"subset={kwargs['subset']}")
        if 'thresh' in kwargs:
            kw_strs.append(f"thresh={kwargs['thresh']}")
        if 'how' in kwargs:
            kw_strs.append(f"how='{kwargs['how']}'")
        code = f"df = df.dropna({', '.join(kw_strs)})"

        return result_df, code

    def execute_duplicate_col(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """复制列

        Args:
            params: {'column': str, 'new_name': str}
        """
        column = params['column']
        new_name = params.get('new_name', f"{column}_copy")

        result_df = df.copy()
        result_df[new_name] = result_df[column]

        code = f"df['{new_name}'] = df['{column}']"

        return result_df, code

    def execute_calculated(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """计算列 — 基于表达式创建新列

        Args:
            params: {'expression': str, 'new_column': str}

        支持的表达式中可以用列名作为变量，如:
            salary * 1.1
            age + 10
            col1 + col2
        """
        expression = params['expression']
        new_column = params.get('new_column', 'calculated')

        result_df = df.copy()

        # 使用 pandas eval 安全执行表达式
        try:
            result_df[new_column] = result_df.eval(expression)
        except Exception as e:
            raise ValueError(f"表达式执行错误: {e}")

        code = f"df['{new_column}'] = df.eval({repr(expression)})"

        return result_df, code
