# Week 2: 数值处理功能实现

## 目标
实现数值数据的高级处理功能，包括分箱、标准化、归一化、窗口函数等。

---

## Day 1-2: 分箱和标准化

### 1. 分箱 (Binning)

**文件**: `services/numeric_processor.py`

```python
import pandas as pd
import numpy as np

class NumericBinner:
    """数值分箱服务"""
    
    @staticmethod
    def bin_equal_width(df, column, n_bins, labels=None, new_name=None):
        """
        等宽分箱
        
        Args:
            df: DataFrame
            column: 列名
            n_bins: 分箱数量
            labels: 标签列表（可选）
            new_name: 新列名
        
        Returns:
            DataFrame with binned column
        """
        if new_name is None:
            new_name = f"{column}_binned"
        
        df[new_name] = pd.cut(df[column], bins=n_bins, labels=labels)
        
        return df
    
    @staticmethod
    def bin_equal_frequency(df, column, n_bins, labels=None, new_name=None):
        """
        等频分箱
        """
        if new_name is None:
            new_name = f"{column}_binned"
        
        df[new_name] = pd.qcut(df[column], q=n_bins, labels=labels, duplicates='drop')
        
        return df
    
    @staticmethod
    def bin_custom(df, column, bins, labels=None, new_name=None):
        """
        自定义边界分箱
        
        Args:
            bins: 边界列表，如 [0, 10, 20, 30, 100]
        """
        if new_name is None:
            new_name = f"{column}_binned"
        
        df[new_name] = pd.cut(df[column], bins=bins, labels=labels)
        
        return df
    
    @staticmethod
    def generate_code(method, column, n_bins=None, bins=None, labels=None, new_name=None):
        """生成 Python 代码"""
        if new_name is None:
            new_name = f"{column}_binned"
        
        code = f"# 分箱: {column}\n"
        
        if method == 'equal_width':
            code += f"df['{new_name}'] = pd.cut(df['{column}'], bins={n_bins}"
        elif method == 'equal_frequency':
            code += f"df['{new_name}'] = pd.qcut(df['{column}'], q={n_bins}"
        elif method == 'custom':
            code += f"df['{new_name}'] = pd.cut(df['{column}'], bins={bins}"
        
        if labels:
            code += f", labels={labels}"
        code += ")\n"
        
        return code
```

---

### 2. 标准化和归一化

```python
class NumericNormalizer:
    """数值标准化服务"""
    
    @staticmethod
    def standardize(df, column, new_name=None):
        """
        Z-score 标准化
        公式: (x - mean) / std
        """
        if new_name is None:
            new_name = f"{column}_standardized"
        
        mean = df[column].mean()
        std = df[column].std()
        df[new_name] = (df[column] - mean) / std
        
        return df
    
    @staticmethod
    def normalize(df, column, min_val=0, max_val=1, new_name=None):
        """
        Min-Max 归一化
        公式: (x - min) / (max - min) * (max_val - min_val) + min_val
        """
        if new_name is None:
            new_name = f"{column}_normalized"
        
        col_min = df[column].min()
        col_max = df[column].max()
        
        df[new_name] = (df[column] - col_min) / (col_max - col_min) * (max_val - min_val) + min_val
        
        return df
    
    @staticmethod
    def robust_scale(df, column, new_name=None):
        """
        鲁棒缩放（使用中位数和四分位距）
        对异常值不敏感
        """
        if new_name is None:
            new_name = f"{column}_robust"
        
        median = df[column].median()
        q75 = df[column].quantile(0.75)
        q25 = df[column].quantile(0.25)
        iqr = q75 - q25
        
        df[new_name] = (df[column] - median) / iqr
        
        return df
    
    @staticmethod
    def generate_code(method, column, new_name=None, **kwargs):
        """生成 Python 代码"""
        if new_name is None:
            new_name = f"{column}_{method}"
        
        code = f"# {method}: {column}\n"
        
        if method == 'standardize':
            code += f"mean = df['{column}'].mean()\n"
            code += f"std = df['{column}'].std()\n"
            code += f"df['{new_name}'] = (df['{column}'] - mean) / std\n"
        
        elif method == 'normalize':
            min_val = kwargs.get('min_val', 0)
            max_val = kwargs.get('max_val', 1)
            code += f"col_min = df['{column}'].min()\n"
            code += f"col_max = df['{column}'].max()\n"
            code += f"df['{new_name}'] = (df['{column}'] - col_min) / (col_max - col_min)"
            if min_val != 0 or max_val != 1:
                code += f" * {max_val - min_val} + {min_val}"
            code += "\n"
        
        elif method == 'robust':
            code += f"median = df['{column}'].median()\n"
            code += f"iqr = df['{column}'].quantile(0.75) - df['{column}'].quantile(0.25)\n"
            code += f"df['{new_name}'] = (df['{column}'] - median) / iqr\n"
        
        return code
```

---

## Day 3-4: 窗口函数和累积函数

### 3. 滚动窗口

```python
class RollingWindow:
    """滚动窗口服务"""
    
    @staticmethod
    def rolling_mean(df, column, window, new_name=None):
        """滚动平均"""
        if new_name is None:
            new_name = f"{column}_rolling_mean_{window}"
        
        df[new_name] = df[column].rolling(window=window).mean()
        
        return df
    
    @staticmethod
    def rolling_sum(df, column, window, new_name=None):
        """滚动求和"""
        if new_name is None:
            new_name = f"{column}_rolling_sum_{window}"
        
        df[new_name] = df[column].rolling(window=window).sum()
        
        return df
    
    @staticmethod
    def rolling_std(df, column, window, new_name=None):
        """滚动标准差"""
        if new_name is None:
            new_name = f"{column}_rolling_std_{window}"
        
        df[new_name] = df[column].rolling(window=window).std()
        
        return df
    
    @staticmethod
    def exponential_smoothing(df, column, alpha, new_name=None):
        """指数平滑"""
        if new_name is None:
            new_name = f"{column}_ema_{alpha}"
        
        df[new_name] = df[column].ewm(alpha=alpha).mean()
        
        return df
```

---

### 4. 累积函数

```python
class CumulativeOperations:
    """累积操作服务"""
    
    @staticmethod
    def cumsum(df, column, new_name=None):
        """累积和"""
        if new_name is None:
            new_name = f"{column}_cumsum"
        
        df[new_name] = df[column].cumsum()
        
        return df
    
    @staticmethod
    def cumprod(df, column, new_name=None):
        """累积积"""
        if new_name is None:
            new_name = f"{column}_cumprod"
        
        df[new_name] = df[column].cumprod()
        
        return df
    
    @staticmethod
    def cummax(df, column, new_name=None):
        """累积最大值"""
        if new_name is None:
            new_name = f"{column}_cummax"
        
        df[new_name] = df[column].cummax()
        
        return df
    
    @staticmethod
    def cummin(df, column, new_name=None):
        """累积最小值"""
        if new_name is None:
            new_name = f"{column}_cummin"
        
        df[new_name] = df[column].cummin()
        
        return df
```

---

## Day 5: UI 集成和测试

### UI 组件

```python
# 分箱模态框
def show_binning_modal():
    return dbc.Modal([
        dbc.ModalHeader("数值分箱"),
        dbc.ModalBody([
            html.Label("选择列："),
            dcc.Dropdown(id="bin-column-select"),
            
            html.Label("分箱方法："),
            dcc.RadioItems(
                id="bin-method",
                options=[
                    {'label': '等宽分箱', 'value': 'equal_width'},
                    {'label': '等频分箱', 'value': 'equal_frequency'},
                    {'label': '自定义边界', 'value': 'custom'}
                ],
                value='equal_width'
            ),
            
            html.Div(id="bin-params-container"),
            
            html.Label("新列名："),
            dcc.Input(id="bin-new-name", placeholder="留空自动生成"),
        ]),
        dbc.ModalFooter([
            dbc.Button("取消", id="btn-cancel-bin"),
            dbc.Button("确认", id="btn-confirm-bin", color="primary"),
        ]),
    ], is_open=True)
```

---

## 测试

```python
def test_binning():
    """测试分箱"""
    df = pd.DataFrame({'value': range(100)})
    
    result = NumericBinner.bin_equal_width(df, 'value', n_bins=5)
    
    assert 'value_binned' in result.columns
    assert result['value_binned'].nunique() == 5

def test_standardization():
    """测试标准化"""
    df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
    
    result = NumericNormalizer.standardize(df, 'value')
    
    assert 'value_standardized' in result.columns
    assert abs(result['value_standardized'].mean()) < 0.0001
    assert abs(result['value_standardized'].std() - 1) < 0.0001
```

---

## 验收标准

- [ ] 分箱功能（等宽、等频、自定义）
- [ ] 标准化功能（Z-score、Min-Max、鲁棒）
- [ ] 滚动窗口功能
- [ ] 累积函数功能
- [ ] 代码生成正确
- [ ] 单元测试通过
- [ ] UI 集成完成

---

**预计完成时间**: 5 天  
**难度**: 中等  
**优先级**: 高
