"""
筛选条件解析器

解析用户输入的筛选条件并转换为pandas查询表达式
"""

from typing import Any, List


class FilterParser:
    """筛选条件解析器
    
    职责：
    - 解析用户输入的筛选条件
    - 转换为pandas查询表达式
    - 验证条件语法
    """
    
    def __init__(self):
        """初始化筛选解析器"""
        pass
    
    def parse_condition(self, column: str, operator: str, value: Any, options: List[str] = None) -> str:
        """解析筛选条件为pandas代码
        
        Args:
            column: 列名
            operator: 操作符
            value: 筛选值
            options: 选项（如忽略大小写）
        
        Returns:
            pandas查询表达式
        """
        return f"df['{column}'] {operator} {repr(value)}"
    
    def parse_numeric_condition(self, column: str, operator: str, value: float) -> str:
        """解析数值筛选条件
        
        Args:
            column: 列名
            operator: 操作符
            value: 数值
        
        Returns:
            pandas查询表达式
        """
        if operator == 'between':
            return f"(df['{column}'] >= {value[0]}) & (df['{column}'] <= {value[1]})"
        else:
            return f"df['{column}'] {operator} {value}"
    
    def parse_text_condition(self, column: str, operator: str, value: str, case_insensitive: bool = False) -> str:
        """解析文本筛选条件
        
        Args:
            column: 列名
            operator: 操作符
            value: 文本值
            case_insensitive: 是否忽略大小写
        
        Returns:
            pandas查询表达式
        """
        if operator == 'contains':
            return f"df['{column}'].str.contains('{value}', case={not case_insensitive}, na=False)"
        elif operator == 'startswith':
            return f"df['{column}'].str.startswith('{value}', na=False)"
        else:
            return f"df['{column}'] {operator} '{value}'"
    
    def combine_conditions(self, conditions: List[str], logic: str = 'AND') -> str:
        """组合多个筛选条件
        
        Args:
            conditions: 条件列表
            logic: 逻辑运算符 ('AND' 或 'OR')
        
        Returns:
            组合后的查询表达式
        """
        if logic == 'AND':
            return ' & '.join(f"({c})" for c in conditions)
        else:
            return ' | '.join(f"({c})" for c in conditions)
