"""
代码生成器

将操作流水线转换为可执行的Python代码
"""

from typing import List, Dict


class CodeGenerator:
    """代码生成器
    
    职责：
    - 将操作流水线转换为Python代码
    - 生成完整的可执行脚本
    - 添加注释和格式化
    """
    
    def __init__(self):
        """初始化代码生成器"""
        pass
    
    def generate_code(
        self,
        pipeline: List[Dict],
        data_source: str = "data.csv",
        include_imports: bool = True,
        include_comments: bool = True
    ) -> str:
        """生成完整的Python代码
        
        Args:
            pipeline: 操作流水线
            data_source: 数据源文件名
            include_imports: 是否包含导入语句
            include_comments: 是否包含注释
        
        Returns:
            完整的Python代码字符串
        """
        code_lines = []
        
        if include_imports:
            code_lines.append(self.generate_imports())
            code_lines.append("")
        
        code_lines.append(self.generate_data_loading(data_source))
        code_lines.append("")
        
        for i, step in enumerate(pipeline, 1):
            if include_comments:
                code_lines.append(f"# 步骤{i}: {step.get('operation', 'unknown')}")
            step_code = self.generate_step_code(step)
            code_lines.append(step_code)
            code_lines.append("")
        
        return "\n".join(code_lines)
    
    def generate_imports(self) -> str:
        """生成导入语句"""
        return """import pandas as pd
import numpy as np
from datetime import datetime"""
    
    def generate_data_loading(self, data_source: str) -> str:
        """生成数据加载代码"""
        return f"""# 加载数据
df = pd.read_csv('{data_source}')
print(f"数据形状: {{df.shape}}")"""
    
    def generate_step_code(self, step: Dict) -> str:
        """生成单个步骤的代码
        
        Args:
            step: 步骤字典
        
        Returns:
            步骤的Python代码
        """
        operation = step.get('operation', 'unknown')
        params = step.get('params', {})
        
        # 根据操作类型生成代码
        if operation == 'filter':
            return self._generate_filter_code(params)
        elif operation == 'drop_column':
            return self._generate_drop_column_code(params)
        elif operation == 'rename_column':
            return self._generate_rename_column_code(params)
        elif operation == 'type_conversion':
            return self._generate_type_conversion_code(params)
        elif operation == 'fill_missing':
            return self._generate_fill_missing_code(params)
        elif operation == 'drop_duplicates':
            return self._generate_drop_duplicates_code(params)
        elif operation == 'sort':
            return self._generate_sort_code(params)
        elif operation == 'split_column':
            return self._generate_split_column_code(params)
        elif operation == 'merge_columns':
            return self._generate_merge_columns_code(params)
        elif operation == 'replace_value':
            return self._generate_replace_value_code(params)
        elif operation == 'strip_whitespace':
            return self._generate_strip_code(params)
        elif operation == 'change_case':
            return self._generate_change_case_code(params)
        elif operation == 'find_replace_regex':
            return self._generate_regex_replace_code(params)
        elif operation == 'extract_substring':
            return self._generate_extract_code(params)
        elif operation == 'bin_column':
            return self._generate_bin_code(params)
        elif operation == 'normalize':
            return self._generate_normalize_code(params)
        elif operation == 'drop_missing_rows':
            return self._generate_drop_na_code(params)
        elif operation == 'duplicate_column':
            return self._generate_duplicate_col_code(params)
        elif operation == 'create_calculated':
            return self._generate_calculated_code(params)
        else:
            return f"# TODO: Generate code for {operation}"
    
    def _generate_filter_code(self, params: Dict) -> str:
        """生成筛选代码"""
        column = params.get('column', '')
        operator = params.get('operator', '==')
        value = params.get('value', '')
        
        # 处理布尔值和不需要值的操作符
        if operator in ['isnull', 'notnull']:
            return f"df = df[df['{column}'].{operator}()]\nprint(f'筛选后行数: {{len(df)}}')"
            
        if operator == 'isin':
            if not isinstance(value, list):
                value = [value]
            return f"df = df[df['{column}'].astype(str).isin({repr(value)})]\nprint(f'筛选后行数: {{len(df)}}')"
            
        if operator == 'contains':
            return f"df = df[df['{column}'].astype(str).str.contains({repr(value)}, case=True, na=False)]\nprint(f'筛选后行数: {{len(df)}}')"
            
        if operator == 'not_contains':
            return f"df = df[~df['{column}'].astype(str).str.contains({repr(value)}, case=True, na=False)]\nprint(f'筛选后行数: {{len(df)}}')"
            
        if operator == 'startswith':
            return f"df = df[df['{column}'].astype(str).str.startswith({repr(value)}, na=False)]\nprint(f'筛选后行数: {{len(df)}}')"
            
        if operator == 'endswith':
            return f"df = df[df['{column}'].astype(str).str.endswith({repr(value)}, na=False)]\nprint(f'筛选后行数: {{len(df)}}')"

        # 处理常规值
        if isinstance(value, str):
            value_str = f"{repr(value)}"
        else:
            value_str = str(value)
        
        return f"df = df[df['{column}'] {operator} {value_str}]\nprint(f'筛选后行数: {{len(df)}}')"
    
    def _generate_drop_column_code(self, params: Dict) -> str:
        """生成删除列代码"""
        column = params.get('column', '')
        return f"df = df.drop(columns=['{column}'])\nprint(f'删除列后列数: {{len(df.columns)}}')"
    
    def _generate_rename_column_code(self, params: Dict) -> str:
        """生成重命名列代码"""
        old_name = params.get('old_name', '')
        new_name = params.get('new_name', '')
        return f"df = df.rename(columns={{'{old_name}': '{new_name}'}})\nprint(f'列 {old_name} 已重命名为 {new_name}')"
    
    def _generate_type_conversion_code(self, params: Dict) -> str:
        """生成类型转换代码"""
        column = params.get('column', '')
        target_type = params.get('target_type', 'numeric')
        
        if target_type == 'numeric':
            return f"df['{column}'] = pd.to_numeric(df['{column}'], errors='coerce')\nprint(f'列 {column} 已转换为数值型')"
        elif target_type == 'datetime':
            return f"df['{column}'] = pd.to_datetime(df['{column}'], errors='coerce')\nprint(f'列 {column} 已转换为日期型')"
        elif target_type == 'string':
            return f"df['{column}'] = df['{column}'].astype(str)\nprint(f'列 {column} 已转换为字符串型')"
        else:
            return f"# 未知的目标类型: {target_type}"
    
    def _generate_fill_missing_code(self, params: Dict) -> str:
        """生成填充缺失值代码"""
        column = params.get('column', '')
        method = params.get('method', 'value')
        value = params.get('value', 0)
        
        if method == 'value':
            if isinstance(value, str):
                value_str = f"'{value}'"
            else:
                value_str = str(value)
            return f"df['{column}'] = df['{column}'].fillna({value_str})\nprint(f'列 {column} 缺失值已填充')"
        elif method == 'mean':
            return f"df['{column}'] = df['{column}'].fillna(df['{column}'].mean())\nprint(f'列 {column} 缺失值已用均值填充')"
        elif method == 'median':
            return f"df['{column}'] = df['{column}'].fillna(df['{column}'].median())\nprint(f'列 {column} 缺失值已用中位数填充')"
        elif method == 'mode':
            return f"df['{column}'] = df['{column}'].fillna(df['{column}'].mode().iloc[0])\nprint(f'列 {column} 缺失值已用众数填充')"
        elif method == 'ffill':
            return f"df['{column}'] = df['{column}'].ffill()\nprint(f'列 {column} 缺失值已前向填充')"
        elif method == 'bfill':
            return f"df['{column}'] = df['{column}'].bfill()\nprint(f'列 {column} 缺失值已后向填充')"
        else:
            return f"# 未知的填充方法: {method}"
    
    def _generate_drop_duplicates_code(self, params: Dict) -> str:
        """生成去重代码"""
        subset = params.get('subset', None)
        keep = params.get('keep', 'first')
        
        if subset:
            return f"df = df.drop_duplicates(subset={subset}, keep='{keep}')\nprint(f'去重后行数: {{len(df)}}')"
        else:
            return f"df = df.drop_duplicates(keep='{keep}')\nprint(f'去重后行数: {{len(df)}}')"
    
    def _generate_sort_code(self, params: Dict) -> str:
        """生成排序代码"""
        column = params.get('column', '')
        ascending = params.get('ascending', True)
        order = '升序' if ascending else '降序'
        return f"df = df.sort_values(by='{column}', ascending={ascending})\nprint(f'已按 {column} {order}排序')"
    
    def _generate_split_column_code(self, params: Dict) -> str:
        """生成列拆分代码"""
        column = params.get('column', '')
        delimiter = params.get('delimiter', ',')
        max_split = params.get('max_split', -1)
        new_columns = params.get('new_columns', [])
        
        if new_columns:
            col_names = str(new_columns)
        else:
            col_names = f"['{column}_1', '{column}_2']"
        
        return f"""split_cols = df['{column}'].str.split('{delimiter}', n={max_split}, expand=True)
split_cols.columns = {col_names}
df = pd.concat([df, split_cols], axis=1)
df = df.drop(columns=['{column}'])
print(f'列 {column} 已拆分')"""
    
    def _generate_merge_columns_code(self, params: Dict) -> str:
        """生成列合并代码"""
        columns = params.get('columns', [])
        delimiter = params.get('delimiter', ' ')
        new_column = params.get('new_column', 'merged')
        
        cols_list = "[" + ", ".join(f"'{c}'" for c in columns) + "]"
        return f"""df['{new_column}'] = df[{cols_list}].astype(str).agg('{delimiter}'.join, axis=1)
print(f'列已合并为 {new_column}')"""
    
    def _generate_replace_value_code(self, params: Dict) -> str:
        """生成替换值代码"""
        column = params.get('column', '')
        old_value = params.get('old_value', '')
        new_value = params.get('new_value', '')
        
        # 处理字符串值
        if isinstance(old_value, str):
            old_str = f"'{old_value}'"
        else:
            old_str = str(old_value)
        
        if isinstance(new_value, str):
            new_str = f"'{new_value}'"
        else:
            new_str = str(new_value)
        
        return f"df['{column}'] = df['{column}'].replace({old_str}, {new_str})\nprint(f'列 {column} 值已替换')"
    
    def _generate_strip_code(self, params: Dict) -> str:
        """生成去除空格代码"""
        column = params.get('column', '')
        return f"df['{column}'] = df['{column}'].astype(str).str.strip()\nprint(f'列 {column} 已去除首尾空格')"

    def _generate_change_case_code(self, params: Dict) -> str:
        """生成大小写转换代码"""
        column = params.get('column', '')
        case_type = params.get('case_type', 'lower')
        case_map = {
            'lower': ('str.lower()', '小写'),
            'upper': ('str.upper()', '大写'),
            'title': ('str.title()', '标题格式'),
            'capitalize': ('str.capitalize()', '首字母大写'),
        }
        method, label = case_map.get(case_type, ('str.lower()', '小写'))
        return f"df['{column}'] = df['{column}'].astype(str).{method}\nprint(f'列 {column} 已转换为{label}')"

    def _generate_regex_replace_code(self, params: Dict) -> str:
        """生成正则替换代码"""
        column = params.get('column', '')
        pattern = params.get('pattern', '')
        replacement = params.get('replacement', '')
        is_regex = params.get('is_regex', False)
        return f"df['{column}'] = df['{column}'].astype(str).str.replace(r'{pattern}', '{replacement}', regex={is_regex})\nprint(f'列 {column} 替换完成')"

    def _generate_extract_code(self, params: Dict) -> str:
        """生成提取子串代码"""
        column = params.get('column', '')
        pattern = params.get('pattern', '')
        start = params.get('start', None)
        end = params.get('end', None)
        if pattern:
            return f"df['{column}_extracted'] = df['{column}'].astype(str).str.extract(r'({pattern})', expand=False)\nprint(f'已从 {column} 提取匹配内容')"
        else:
            start_val = start if start is not None else ''
            end_val = end if end is not None else ''
            return f"df['{column}_extracted'] = df['{column}'].astype(str).str[{start_val}:{end_val}]\nprint(f'已从 {column} 提取子串')"

    def _generate_bin_code(self, params: Dict) -> str:
        """生成分箱代码"""
        column = params.get('column', '')
        bins = params.get('bins', 5)
        method = params.get('method', 'equal_width')
        labels = params.get('labels', None)
        if method == 'equal_freq':
            return f"df['{column}_binned'] = pd.qcut(df['{column}'], q={bins}, duplicates='drop')\nprint(f'列 {column} 已等频分箱为 {bins} 组')"
        else:
            if labels:
                return f"df['{column}_binned'] = pd.cut(df['{column}'], bins={bins}, labels={labels})\nprint(f'列 {column} 已等宽分箱为 {bins} 组')"
            return f"df['{column}_binned'] = pd.cut(df['{column}'], bins={bins})\nprint(f'列 {column} 已等宽分箱为 {bins} 组')"

    def _generate_normalize_code(self, params: Dict) -> str:
        """生成标准化/归一化代码"""
        column = params.get('column', '')
        method = params.get('method', 'minmax')
        if method == 'zscore':
            return f"df['{column}_normalized'] = (df['{column}'] - df['{column}'].mean()) / df['{column}'].std()\nprint(f'列 {column} 已Z-Score标准化')"
        elif method == 'robust':
            return f"""q1 = df['{column}'].quantile(0.25)
q3 = df['{column}'].quantile(0.75)
df['{column}_normalized'] = (df['{column}'] - df['{column}'].median()) / (q3 - q1)
print(f'列 {column} 已Robust标准化')"""
        else:
            return f"df['{column}_normalized'] = (df['{column}'] - df['{column}'].min()) / (df['{column}'].max() - df['{column}'].min())\nprint(f'列 {column} 已Min-Max归一化')"

    def _generate_drop_na_code(self, params: Dict) -> str:
        """生成删除缺失行代码"""
        column = params.get('column', None)
        how = params.get('how', 'any')
        threshold = params.get('threshold', None)
        if column:
            return f"df = df.dropna(subset=['{column}'])\nprint(f'已删除列 {column} 中缺失值所在行，剩余 {{len(df)}} 行')"
        elif threshold:
            return f"df = df.dropna(thresh={threshold})\nprint(f'已删除非空值少于 {threshold} 个的行，剩余 {{len(df)}} 行')"
        else:
            return f"df = df.dropna(how='{how}')\nprint(f'已删除缺失行（{how}），剩余 {{len(df)}} 行')"

    def _generate_duplicate_col_code(self, params: Dict) -> str:
        """生成复制列代码"""
        column = params.get('column', '')
        new_name = params.get('new_name', f'{column}_copy')
        return f"df['{new_name}'] = df['{column}']\nprint(f'列 {column} 已复制为 {new_name}')"

    def _generate_calculated_code(self, params: Dict) -> str:
        """生成计算列代码"""
        expression = params.get('expression', '')
        new_column = params.get('new_column', 'calculated')
        return f"df['{new_column}'] = {expression}\nprint(f'已创建计算列 {new_column}')"

    def format_code(self, code: str) -> str:
        """格式化代码
        
        Args:
            code: 原始代码
        
        Returns:
            格式化后的代码
        """
        # 简单实现，实际可以使用black或autopep8
        return code
