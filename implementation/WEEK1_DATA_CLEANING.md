# Week 1: 核心数据清洗功能实现

## 目标
实现 D-Tale 风格的核心数据清洗功能，包括列拆分、合并、字符串处理等。

---

## Day 1-2: 列拆分和合并

### 1. 拆分列 (Split Column)

**文件**: `services/data_cleaner.py`

```python
class ColumnSplitter:
    """列拆分服务"""
    
    @staticmethod
    def split_column(df, column, separator, max_split=None, new_names=None):
        """
        拆分列
        
        Args:
            df: DataFrame
            column: 要拆分的列名
            separator: 分隔符
            max_split: 最大拆分数（None = 全部拆分）
            new_names: 新列名列表
        
        Returns:
            DataFrame with new columns
        """
        split_data = df[column].str.split(separator, n=max_split, expand=True)
        
        if new_names is None:
            new_names = [f"{column}_part_{i+1}" for i in range(split_data.shape[1])]
        
        for i, name in enumerate(new_names):
            df[name] = split_data[i]
        
        return df
    
    @staticmethod
    def generate_code(column, separator, max_split, new_names):
        """生成 Python 代码"""
        code = f"# 拆分列 '{column}'\n"
        code += f"split_data = df['{column}'].str.split('{separator}'"
        if max_split:
            code += f", n={max_split}"
        code += ", expand=True)\n"
        
        for i, name in enumerate(new_names):
            code += f"df['{name}'] = split_data[{i}]\n"
        
        return code
```

**UI 组件**: `pages/data_workshop.py`

```python
def show_split_column_modal(n_clicks):
    """显示拆分列模态框"""
    return dbc.Modal([
        dbc.ModalHeader("拆分列"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(id="split-column-select", options=columns),
            
            html.Label("分隔符："),
            dcc.Dropdown(
                id="split-separator",
                options=[
                    {'label': '逗号 (,)', 'value': ','},
                    {'label': '空格', 'value': ' '},
                    {'label': '分号 (;)', 'value': ';'},
                    {'label': '竖线 (|)', 'value': '|'},
                    {'label': '自定义', 'value': 'custom'}
                ]
            ),
            
            html.Div(id="custom-separator-input"),
            
            html.Label("拆分数量："),
            dcc.Input(
                id="split-max-count",
                type="number",
                placeholder="留空表示全部拆分",
                min=2
            ),
            
            html.Label("新列名前缀："),
            dcc.Input(id="split-prefix", placeholder="默认使用原列名"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-split"),
            dbc.Button("确认拆分", id="btn-confirm-split", color="primary"),
        ]),
    ], is_open=True)
```

---

### 2. 合并列 (Concatenate Column)

**服务**: `services/data_cleaner.py`

```python
class ColumnConcatenator:
    """列合并服务"""
    
    @staticmethod
    def concatenate_columns(df, columns, separator, new_name, drop_original=False):
        """
        合并多列
        
        Args:
            df: DataFrame
            columns: 要合并的列名列表
            separator: 分隔符
            new_name: 新列名
            drop_original: 是否删除原列
        
        Returns:
            DataFrame with new column
        """
        df[new_name] = df[columns].astype(str).agg(separator.join, axis=1)
        
        if drop_original:
            df = df.drop(columns=columns)
        
        return df
    
    @staticmethod
    def generate_code(columns, separator, new_name, drop_original):
        """生成 Python 代码"""
        cols_str = str(columns)
        code = f"# 合并列 {cols_str}\n"
        code += f"df['{new_name}'] = df{cols_str}.astype(str).agg('{separator}'.join, axis=1)\n"
        
        if drop_original:
            code += f"df = df.drop(columns={cols_str})\n"
        
        return code
```

---

## Day 3-4: 字符串处理

### 3. 查找替换 (Find & Replace)

**服务**: `services/data_cleaner.py`

```python
class StringReplacer:
    """字符串替换服务"""
    
    @staticmethod
    def find_replace(df, column, find_value, replace_value, 
                     use_regex=False, case_sensitive=True):
        """
        查找并替换
        
        Args:
            df: DataFrame
            column: 列名
            find_value: 查找内容
            replace_value: 替换内容
            use_regex: 是否使用正则表达式
            case_sensitive: 是否区分大小写
        
        Returns:
            DataFrame with replaced values
        """
        if use_regex:
            df[column] = df[column].str.replace(
                find_value, 
                replace_value, 
                case=case_sensitive,
                regex=True
            )
        else:
            df[column] = df[column].str.replace(
                find_value, 
                replace_value, 
                case=case_sensitive
            )
        
        return df
```

### 4. 字符串清理

```python
class StringCleaner:
    """字符串清理服务"""
    
    @staticmethod
    def strip_whitespace(df, column, mode='both'):
        """
        去除空格
        
        Args:
            mode: 'both', 'left', 'right', 'all'
        """
        if mode == 'both':
            df[column] = df[column].str.strip()
        elif mode == 'left':
            df[column] = df[column].str.lstrip()
        elif mode == 'right':
            df[column] = df[column].str.rstrip()
        elif mode == 'all':
            df[column] = df[column].str.replace(r'\s+', '', regex=True)
        
        return df
    
    @staticmethod
    def case_conversion(df, column, case_type):
        """
        大小写转换
        
        Args:
            case_type: 'upper', 'lower', 'title', 'capitalize'
        """
        if case_type == 'upper':
            df[column] = df[column].str.upper()
        elif case_type == 'lower':
            df[column] = df[column].str.lower()
        elif case_type == 'title':
            df[column] = df[column].str.title()
        elif case_type == 'capitalize':
            df[column] = df[column].str.capitalize()
        
        return df
```

---

## Day 5: 测试和文档

### 单元测试

**文件**: `tests/test_data_cleaning.py`

```python
import pytest
import pandas as pd
from services.data_cleaner import ColumnSplitter, ColumnConcatenator

def test_split_column():
    """测试列拆分"""
    df = pd.DataFrame({'name': ['张三', '李四', '王五']})
    
    result = ColumnSplitter.split_column(
        df, 'name', '', max_split=1, 
        new_names=['姓', '名']
    )
    
    assert '姓' in result.columns
    assert '名' in result.columns
    assert result['姓'].iloc[0] == '张'
    assert result['名'].iloc[0] == '三'

def test_concatenate_columns():
    """测试列合并"""
    df = pd.DataFrame({
        '姓': ['张', '李', '王'],
        '名': ['三', '四', '五']
    })
    
    result = ColumnConcatenator.concatenate_columns(
        df, ['姓', '名'], '', '全名'
    )
    
    assert '全名' in result.columns
    assert result['全名'].iloc[0] == '张三'
```

---

## 集成到 UI

### 更新 data_workshop.py

```python
# 添加新按钮
dbc.Button("拆分列", id="btn-split-column", color="info"),
dbc.Button("合并列", id="btn-merge-columns", color="info"),
dbc.Button("查找替换", id="btn-find-replace", color="primary"),
dbc.Button("去空格", id="btn-strip-text", color="primary"),
dbc.Button("大小写转换", id="btn-case-convert", color="info"),
```

---

## 代码生成集成

### 更新 code_generator.py

```python
class CodeGenerator:
    @staticmethod
    def generate_split_code(column, separator, max_split, new_names):
        return ColumnSplitter.generate_code(column, separator, max_split, new_names)
    
    @staticmethod
    def generate_concatenate_code(columns, separator, new_name, drop_original):
        return ColumnConcatenator.generate_code(columns, separator, new_name, drop_original)
```

---

## 验收标准

- [ ] 列拆分功能正常工作
- [ ] 列合并功能正常工作
- [ ] 查找替换支持正则表达式
- [ ] 字符串清理功能完整
- [ ] 所有功能生成正确的 Python 代码
- [ ] 单元测试覆盖率 > 80%
- [ ] UI 交互流畅
- [ ] 错误处理完善

---

**预计完成时间**: 5 天  
**难度**: 中等  
**优先级**: 高
