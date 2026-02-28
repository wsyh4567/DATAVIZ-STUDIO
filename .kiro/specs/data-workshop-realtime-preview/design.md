# 数据工坊实时预览 - 设计文档

## 概述

本设计文档描述了数据工坊实时预览功能的技术架构和实现方案。该功能旨在提供类似 Power Query 和 Excel 的所见即所得数据操作体验，通过实时预览引擎、步骤管理系统和优化的UI设计，大幅提升数据清洗的效率和用户体验。

### 设计目标

1. **实时反馈**: 用户操作后500ms内显示预览结果
2. **高性能**: 支持百万级数据集流畅操作
3. **可追溯**: 完整的操作历史和步骤管理
4. **可导出**: 所有操作可导出为可执行的Python代码
5. **架构兼容**: 与现有DataViz Studio的Python优先架构保持一致

### 核心特性

- 实时数据预览引擎
- 内联列操作和筛选
- 可视化步骤管理器
- 撤销/重做功能
- 虚拟滚动和增量更新
- 代码导出功能
- 智能类型检测
- 数据质量分析

## 系统架构

### 高层架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端层 (Dash UI)                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 数据表格组件  │  │ 步骤管理面板  │  │ 操作工具栏    │      │
│  │ (AG Grid)    │  │ (Step Panel) │  │ (Toolbar)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 筛选面板      │  │ 代码预览      │  │ 质量报告      │      │
│  │ (Filter)     │  │ (Code View)  │  │ (Quality)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   状态管理层 (Dash Store)                    │
├─────────────────────────────────────────────────────────────┤
│  • 原始数据状态    • 预览数据状态    • 操作流水线状态        │
│  • 步骤历史栈      • UI配置状态      • 撤销/重做栈          │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   服务层 (Python Backend)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 预览引擎      │  │ 操作执行器    │  │ 代码生成器    │      │
│  │ PreviewEngine│  │ OperationExec│  │ CodeGenerator│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 类型检测器    │  │ 质量分析器    │  │ 步骤管理器    │      │
│  │ TypeDetector │  │ QualityAnalyz│  │ StepManager  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   数据层 (Pandas DataFrame)                  │
├─────────────────────────────────────────────────────────────┤
│  • 原始数据集      • 预览数据集      • 中间结果缓存          │
└─────────────────────────────────────────────────────────────┘
```


### 架构原则

#### 1. Python优先架构

遵循DataViz Studio的核心定位，所有数据操作都对应Python代码：

```
用户操作 → 操作对象 → Python代码 → 执行结果 → 前端展示
         ↓
    可导出的代码
```

#### 2. 前后端分离

- **前端职责**: UI渲染、用户交互、状态管理
- **后端职责**: 数据处理、代码生成、业务逻辑
- **通信方式**: Dash回调机制，JSON数据传输

#### 3. 响应式设计

- 使用Dash Store进行状态管理
- 回调函数处理用户交互
- 异步处理长时间操作
- 增量更新减少数据传输

#### 4. 性能优化

- 虚拟滚动渲染大数据集
- 预览限制（前1000/10000行）
- 操作结果缓存
- 延迟计算和批处理

### 数据流设计

#### 操作流水线 (Operation Pipeline)

操作流水线是核心数据结构，记录所有数据转换步骤：

```python
{
    "pipeline_id": "uuid",
    "steps": [
        {
            "step_id": "uuid",
            "operation": "filter",
            "params": {
                "column": "age",
                "operator": ">",
                "value": 18
            },
            "timestamp": "2024-01-01T12:00:00",
            "affected_rows": 1500,
            "affected_cols": 0
        },
        {
            "step_id": "uuid",
            "operation": "drop_column",
            "params": {
                "column": "temp_col"
            },
            "timestamp": "2024-01-01T12:01:00",
            "affected_rows": 0,
            "affected_cols": 1
        }
    ]
}
```

#### 预览数据流

```
原始数据 (DataFrame)
    ↓
应用操作流水线 (前N步)
    ↓
限制预览行数 (前1000行)
    ↓
转换为JSON格式
    ↓
传输到前端
    ↓
AG Grid渲染
```

#### 状态管理流

```
用户操作
    ↓
更新操作流水线
    ↓
触发预览计算
    ↓
更新预览数据状态
    ↓
更新步骤管理器显示
    ↓
更新代码预览
```


## 组件设计

### 1. 预览引擎 (Preview Engine)

预览引擎负责实时计算和显示数据变化。

#### 类设计

```python
class PreviewEngine:
    """实时预览引擎
    
    职责：
    - 执行操作流水线生成预览数据
    - 限制预览行数以保证性能
    - 计算操作影响统计
    - 支持异步计算和取消
    """
    
    def __init__(self, max_preview_rows: int = 1000):
        self.max_preview_rows = max_preview_rows
        self.cache = {}  # 步骤结果缓存
        self.cancel_flag = False
    
    def compute_preview(
        self,
        df: pd.DataFrame,
        pipeline: List[Dict],
        up_to_step: Optional[int] = None
    ) -> Dict:
        """计算预览数据
        
        Args:
            df: 原始数据框
            pipeline: 操作流水线
            up_to_step: 执行到第几步（None表示全部）
        
        Returns:
            {
                'preview_df': 预览数据框（限制行数）,
                'full_rows': 完整结果行数,
                'full_cols': 完整结果列数,
                'affected_rows': 本次操作影响的行数,
                'affected_cols': 本次操作影响的列数,
                'execution_time': 执行时间（秒）
            }
        """
        pass
    
    def compute_with_timeout(
        self,
        df: pd.DataFrame,
        pipeline: List[Dict],
        timeout: float = 3.0
    ) -> Optional[Dict]:
        """带超时的预览计算
        
        Args:
            df: 原始数据框
            pipeline: 操作流水线
            timeout: 超时时间（秒）
        
        Returns:
            预览结果或None（超时）
        """
        pass
    
    def cancel_computation(self):
        """取消当前计算"""
        self.cancel_flag = True
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
```

#### 性能优化策略

1. **增量计算**: 缓存中间步骤结果，只重新计算变化的部分
2. **行数限制**: 预览时只处理前N行数据
3. **延迟执行**: 用户停止输入后才触发计算（debounce）
4. **异步处理**: 长时间操作在后台线程执行
5. **取消机制**: 允许用户取消长时间运行的操作

### 2. 步骤管理器 (Step Manager)

步骤管理器负责管理操作历史和步骤导航。

#### 类设计

```python
class StepManager:
    """步骤管理器
    
    职责：
    - 管理操作流水线
    - 支持步骤的增删改查
    - 支持步骤重排序
    - 生成步骤描述
    """
    
    def __init__(self):
        self.pipeline = []
        self.current_step = -1
    
    def add_step(self, operation: str, params: Dict) -> str:
        """添加步骤
        
        Args:
            operation: 操作类型
            params: 操作参数
        
        Returns:
            步骤ID
        """
        pass
    
    def remove_step(self, step_id: str) -> bool:
        """删除步骤"""
        pass
    
    def update_step(self, step_id: str, params: Dict) -> bool:
        """更新步骤参数"""
        pass
    
    def reorder_steps(self, step_ids: List[str]) -> bool:
        """重新排序步骤"""
        pass
    
    def get_step_description(self, step: Dict) -> str:
        """生成步骤的人类可读描述
        
        Examples:
            "筛选: age > 18 (影响1500行)"
            "删除列: temp_col (影响1列)"
            "类型转换: price → 数值型"
        """
        pass
    
    def navigate_to_step(self, step_index: int) -> List[Dict]:
        """导航到指定步骤，返回该步骤之前的流水线"""
        pass
    
    def export_pipeline(self) -> Dict:
        """导出流水线为JSON"""
        pass
    
    def import_pipeline(self, pipeline_json: Dict) -> bool:
        """从JSON导入流水线"""
        pass
```


### 3. 操作执行器 (Operation Executor)

操作执行器负责将操作对象转换为pandas代码并执行。

#### 类设计

```python
class OperationExecutor:
    """操作执行器
    
    职责：
    - 执行各种数据操作
    - 生成对应的pandas代码
    - 处理操作错误
    """
    
    def execute(self, df: pd.DataFrame, operation: str, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行操作
        
        Args:
            df: 输入数据框
            operation: 操作类型
            params: 操作参数
        
        Returns:
            (结果数据框, 对应的pandas代码)
        """
        pass
    
    def execute_filter(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行筛选操作"""
        pass
    
    def execute_drop_column(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行删除列操作"""
        pass
    
    def execute_rename_column(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行重命名列操作"""
        pass
    
    def execute_type_conversion(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行类型转换操作"""
        pass
    
    def execute_fill_missing(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行缺失值填充操作"""
        pass
    
    def execute_split_column(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行列拆分操作"""
        pass
    
    def execute_merge_columns(self, df: pd.DataFrame, params: Dict) -> Tuple[pd.DataFrame, str]:
        """执行列合并操作"""
        pass
```

#### 操作类型映射

```python
OPERATION_MAP = {
    'filter': execute_filter,
    'drop_column': execute_drop_column,
    'rename_column': execute_rename_column,
    'type_conversion': execute_type_conversion,
    'fill_missing': execute_fill_missing,
    'drop_duplicates': execute_drop_duplicates,
    'sort': execute_sort,
    'split_column': execute_split_column,
    'merge_columns': execute_merge_columns,
    'replace_value': execute_replace_value,
    'extract_pattern': execute_extract_pattern,
}
```

### 4. 代码生成器 (Code Generator)

代码生成器负责将操作流水线转换为可执行的Python代码。

#### 类设计

```python
class CodeGenerator:
    """代码生成器
    
    职责：
    - 将操作流水线转换为Python代码
    - 生成完整的可执行脚本
    - 添加注释和格式化
    """
    
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
        pass
    
    def generate_imports(self) -> str:
        """生成导入语句"""
        return """import pandas as pd
import numpy as np
from datetime import datetime
"""
    
    def generate_data_loading(self, data_source: str) -> str:
        """生成数据加载代码"""
        return f"""# 加载数据
df = pd.read_csv('{data_source}')
print(f"数据形状: {{df.shape}}")
"""
    
    def generate_step_code(self, step: Dict) -> str:
        """生成单个步骤的代码"""
        pass
    
    def format_code(self, code: str) -> str:
        """格式化代码（使用black或autopep8）"""
        pass
```

#### 代码模板示例

```python
# 筛选操作模板
FILTER_TEMPLATE = """# 步骤{step_num}: 筛选数据
# 条件: {condition_desc}
df = df[{condition_code}]
print(f"筛选后行数: {{len(df)}}")
"""

# 类型转换模板
TYPE_CONVERSION_TEMPLATE = """# 步骤{step_num}: 类型转换
# 将列 '{column}' 转换为 {target_type}
df['{column}'] = pd.to_{target_type}(df['{column}'], errors='coerce')
print(f"转换后 '{column}' 的类型: {{df['{column}'].dtype}}")
"""

# 列拆分模板
SPLIT_COLUMN_TEMPLATE = """# 步骤{step_num}: 拆分列
# 将列 '{column}' 按 '{delimiter}' 拆分
split_cols = df['{column}'].str.split('{delimiter}', n={max_split}, expand=True)
split_cols.columns = {new_column_names}
df = pd.concat([df, split_cols], axis=1)
df = df.drop(columns=['{column}'])
print(f"拆分后列数: {{len(df.columns)}}")
"""
```


### 5. 撤销/重做栈 (Undo/Redo Stack)

撤销重做栈管理操作历史以支持撤销和重做功能。

#### 类设计

```python
class UndoRedoStack:
    """撤销重做栈
    
    职责：
    - 记录操作历史状态
    - 支持撤销和重做
    - 限制历史记录数量
    - 处理分支操作
    """
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history = []  # 历史状态列表
        self.current_index = -1  # 当前位置
    
    def push_state(self, state: Dict):
        """添加新状态
        
        如果当前不在最新位置，清除后续历史
        如果超过最大历史数，删除最早的记录
        """
        # 清除当前位置之后的历史
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # 添加新状态
        self.history.append(state)
        
        # 限制历史数量
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.current_index += 1
    
    def undo(self) -> Optional[Dict]:
        """撤销操作，返回上一个状态"""
        if self.can_undo():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
    
    def redo(self) -> Optional[Dict]:
        """重做操作，返回下一个状态"""
        if self.can_redo():
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def can_undo(self) -> bool:
        """是否可以撤销"""
        return self.current_index > 0
    
    def can_redo(self) -> bool:
        """是否可以重做"""
        return self.current_index < len(self.history) - 1
    
    def get_current_state(self) -> Optional[Dict]:
        """获取当前状态"""
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None
    
    def clear(self):
        """清空历史"""
        self.history.clear()
        self.current_index = -1
```

#### 状态快照结构

```python
{
    "timestamp": "2024-01-01T12:00:00",
    "pipeline": [...],  # 操作流水线
    "data_hash": "abc123",  # 数据哈希（用于验证）
    "description": "筛选: age > 18"  # 操作描述
}
```

### 6. 类型检测器 (Type Detector)

类型检测器负责智能检测和建议数据类型转换。

#### 类设计

```python
class TypeDetector:
    """类型检测器
    
    职责：
    - 检测列的实际数据类型
    - 识别类型不匹配
    - 建议类型转换
    """
    
    def detect_column_type(self, series: pd.Series) -> Dict:
        """检测列的数据类型
        
        Returns:
            {
                'current_type': 当前pandas类型,
                'detected_type': 检测到的实际类型,
                'confidence': 置信度 (0-1),
                'mismatch': 是否类型不匹配,
                'suggestion': 建议的转换操作
            }
        """
        pass
    
    def is_numeric_string(self, series: pd.Series) -> Tuple[bool, float]:
        """检测是否为数值字符串
        
        Returns:
            (是否为数值, 置信度)
        """
        pass
    
    def is_date_string(self, series: pd.Series) -> Tuple[bool, float, Optional[str]]:
        """检测是否为日期字符串
        
        Returns:
            (是否为日期, 置信度, 日期格式)
        """
        pass
    
    def is_boolean_string(self, series: pd.Series) -> Tuple[bool, float]:
        """检测是否为布尔字符串"""
        pass
    
    def suggest_conversion(self, series: pd.Series) -> Optional[Dict]:
        """建议类型转换
        
        Returns:
            {
                'target_type': 目标类型,
                'conversion_code': 转换代码,
                'expected_failures': 预期失败数量
            }
        """
        pass
```


### 7. 质量分析器 (Quality Analyzer)

质量分析器负责生成数据质量报告。

#### 类设计

```python
class QualityAnalyzer:
    """质量分析器
    
    职责：
    - 分析数据质量指标
    - 识别数据质量问题
    - 生成质量报告
    """
    
    def analyze_dataframe(self, df: pd.DataFrame) -> Dict:
        """分析整个数据框
        
        Returns:
            {
                'overview': 总体概况,
                'columns': 各列详细分析,
                'issues': 识别的问题列表,
                'recommendations': 建议的清洗操作
            }
        """
        pass
    
    def analyze_column(self, series: pd.Series) -> Dict:
        """分析单列
        
        Returns:
            {
                'name': 列名,
                'dtype': 数据类型,
                'missing_count': 缺失值数量,
                'missing_percent': 缺失值百分比,
                'unique_count': 唯一值数量,
                'duplicate_count': 重复值数量,
                'statistics': 统计信息（数值列）,
                'patterns': 模式分析（文本列）,
                'issues': 问题列表
            }
        """
        pass
    
    def detect_outliers(self, series: pd.Series) -> List[int]:
        """检测异常值（使用IQR方法）"""
        pass
    
    def detect_format_inconsistency(self, series: pd.Series) -> Dict:
        """检测格式不一致"""
        pass
    
    def generate_report_html(self, analysis: Dict) -> str:
        """生成HTML格式的报告"""
        pass
```

### 8. 筛选面板 (Filter Panel)

筛选面板提供直观的筛选条件配置界面。

#### 组件设计

```python
def create_filter_panel(column: str, dtype: str) -> html.Div:
    """创建筛选面板
    
    Args:
        column: 列名
        dtype: 数据类型
    
    Returns:
        筛选面板组件
    """
    if dtype in ['int64', 'float64']:
        return create_numeric_filter(column)
    elif dtype == 'object':
        return create_text_filter(column)
    elif dtype == 'datetime64':
        return create_date_filter(column)
    else:
        return create_generic_filter(column)

def create_numeric_filter(column: str) -> html.Div:
    """数值列筛选面板"""
    return html.Div([
        html.Label(f"筛选: {column}"),
        dcc.Dropdown(
            id={'type': 'filter-operator', 'column': column},
            options=[
                {'label': '等于 (=)', 'value': '=='},
                {'label': '不等于 (≠)', 'value': '!='},
                {'label': '大于 (>)', 'value': '>'},
                {'label': '小于 (<)', 'value': '<'},
                {'label': '大于等于 (≥)', 'value': '>='},
                {'label': '小于等于 (≤)', 'value': '<='},
                {'label': '范围', 'value': 'between'},
            ],
            value='==',
            className='mb-2'
        ),
        dcc.Input(
            id={'type': 'filter-value', 'column': column},
            type='number',
            placeholder='输入数值',
            className='mb-2'
        ),
        html.Div(id={'type': 'filter-preview', 'column': column}),
        dbc.Button("应用筛选", id={'type': 'apply-filter', 'column': column})
    ])

def create_text_filter(column: str) -> html.Div:
    """文本列筛选面板"""
    return html.Div([
        html.Label(f"筛选: {column}"),
        dcc.Dropdown(
            id={'type': 'filter-operator', 'column': column},
            options=[
                {'label': '包含', 'value': 'contains'},
                {'label': '不包含', 'value': 'not_contains'},
                {'label': '等于', 'value': '=='},
                {'label': '开头是', 'value': 'startswith'},
                {'label': '结尾是', 'value': 'endswith'},
                {'label': '正则表达式', 'value': 'regex'},
            ],
            value='contains',
            className='mb-2'
        ),
        dcc.Input(
            id={'type': 'filter-value', 'column': column},
            type='text',
            placeholder='输入文本',
            className='mb-2'
        ),
        dcc.Checklist(
            id={'type': 'filter-options', 'column': column},
            options=[
                {'label': '忽略大小写', 'value': 'case_insensitive'}
            ],
            value=[]
        ),
        html.Div(id={'type': 'filter-preview', 'column': column}),
        dbc.Button("应用筛选", id={'type': 'apply-filter', 'column': column})
    ])
```

#### 筛选条件解析器

```python
class FilterParser:
    """筛选条件解析器
    
    职责：
    - 解析用户输入的筛选条件
    - 转换为pandas查询表达式
    - 验证条件语法
    """
    
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
        pass
    
    def parse_numeric_condition(self, column: str, operator: str, value: float) -> str:
        """解析数值筛选条件"""
        if operator == 'between':
            return f"(df['{column}'] >= {value[0]}) & (df['{column}'] <= {value[1]})"
        else:
            return f"df['{column}'] {operator} {value}"
    
    def parse_text_condition(self, column: str, operator: str, value: str, case_insensitive: bool = False) -> str:
        """解析文本筛选条件"""
        if operator == 'contains':
            return f"df['{column}'].str.contains('{value}', case={not case_insensitive}, na=False)"
        elif operator == 'startswith':
            return f"df['{column}'].str.startswith('{value}', na=False)"
        # ... 其他操作符
    
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
```


## 数据模型

### 操作对象 (Operation)

```python
@dataclass
class Operation:
    """数据操作对象"""
    step_id: str
    operation: str  # 操作类型
    params: Dict[str, Any]  # 操作参数
    timestamp: datetime
    affected_rows: int = 0
    affected_cols: int = 0
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'step_id': self.step_id,
            'operation': self.operation,
            'params': self.params,
            'timestamp': self.timestamp.isoformat(),
            'affected_rows': self.affected_rows,
            'affected_cols': self.affected_cols,
            'execution_time': self.execution_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Operation':
        """从字典创建"""
        return cls(
            step_id=data['step_id'],
            operation=data['operation'],
            params=data['params'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            affected_rows=data.get('affected_rows', 0),
            affected_cols=data.get('affected_cols', 0),
            execution_time=data.get('execution_time', 0.0)
        )
```

### 预览结果 (PreviewResult)

```python
@dataclass
class PreviewResult:
    """预览结果对象"""
    preview_df: pd.DataFrame  # 预览数据（限制行数）
    full_rows: int  # 完整结果行数
    full_cols: int  # 完整结果列数
    affected_rows: int  # 本次操作影响的行数
    affected_cols: int  # 本次操作影响的列数
    execution_time: float  # 执行时间
    is_truncated: bool  # 是否被截断
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON传输）"""
        return {
            'preview_data': self.preview_df.to_dict('records'),
            'columns': list(self.preview_df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.preview_df.dtypes.items()},
            'full_rows': self.full_rows,
            'full_cols': self.full_cols,
            'affected_rows': self.affected_rows,
            'affected_cols': self.affected_cols,
            'execution_time': self.execution_time,
            'is_truncated': self.is_truncated
        }
```

### 数据质量报告 (QualityReport)

```python
@dataclass
class QualityReport:
    """数据质量报告对象"""
    
    @dataclass
    class ColumnAnalysis:
        """列分析结果"""
        name: str
        dtype: str
        missing_count: int
        missing_percent: float
        unique_count: int
        duplicate_count: int
        statistics: Optional[Dict] = None  # 数值列统计
        patterns: Optional[Dict] = None  # 文本列模式
        issues: List[str] = field(default_factory=list)
    
    total_rows: int
    total_cols: int
    memory_usage: str
    columns: List[ColumnAnalysis]
    overall_issues: List[str]
    recommendations: List[Dict]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'total_rows': self.total_rows,
            'total_cols': self.total_cols,
            'memory_usage': self.memory_usage,
            'columns': [asdict(col) for col in self.columns],
            'overall_issues': self.overall_issues,
            'recommendations': self.recommendations
        }
```

## 接口设计

### 前端组件接口

#### 1. 数据表格组件 (AG Grid)

```python
def create_data_grid(df: pd.DataFrame, preview_mode: bool = False) -> dag.AgGrid:
    """创建数据表格组件
    
    Args:
        df: 数据框
        preview_mode: 是否为预览模式
    
    Returns:
        AG Grid组件
    """
    column_defs = []
    for col in df.columns:
        col_def = {
            'field': col,
            'headerName': col,
            'sortable': True,
            'filter': True,
            'resizable': True,
            'editable': not preview_mode,  # 预览模式不可编辑
        }
        
        # 根据数据类型设置列配置
        if df[col].dtype in ['int64', 'float64']:
            col_def['type'] = 'numericColumn'
            col_def['filter'] = 'agNumberColumnFilter'
        elif df[col].dtype == 'datetime64[ns]':
            col_def['filter'] = 'agDateColumnFilter'
        else:
            col_def['filter'] = 'agTextColumnFilter'
        
        column_defs.append(col_def)
    
    return dag.AgGrid(
        id='data-grid',
        rowData=df.to_dict('records'),
        columnDefs=column_defs,
        defaultColDef={
            'flex': 1,
            'minWidth': 100,
            'sortable': True,
            'filter': True,
            'resizable': True,
        },
        dashGridOptions={
            'pagination': True,
            'paginationPageSize': 100,
            'animateRows': True,
            'enableRangeSelection': True,
            'rowSelection': 'multiple',
        },
        style={'height': '600px'}
    )
```

#### 2. 步骤管理面板

```python
def create_step_panel(pipeline: List[Dict]) -> html.Div:
    """创建步骤管理面板
    
    Args:
        pipeline: 操作流水线
    
    Returns:
        步骤面板组件
    """
    step_items = []
    for i, step in enumerate(pipeline):
        step_items.append(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span(f"步骤 {i+1}", className="step-number"),
                        html.Span(get_step_description(step), className="step-description"),
                        html.Div([
                            html.Small(f"影响: {step['affected_rows']}行, {step['affected_cols']}列"),
                        ], className="step-stats"),
                    ]),
                    html.Div([
                        dbc.Button("编辑", id={'type': 'edit-step', 'index': i}, size='sm'),
                        dbc.Button("删除", id={'type': 'delete-step', 'index': i}, size='sm', color='danger'),
                    ], className="step-actions"),
                ])
            ], className="step-card mb-2", id={'type': 'step-card', 'index': i})
        )
    
    return html.Div([
        html.H6("操作步骤", className="mb-3"),
        html.Div(step_items, id='step-list'),
        html.Div([
            dbc.Button("清空所有步骤", id='clear-all-steps', color='warning', size='sm'),
        ], className="mt-3")
    ], className="step-panel")
```


### 3. 操作工具栏

```python
def create_operation_toolbar() -> html.Div:
    """创建操作工具栏"""
    return html.Div([
        dbc.ButtonGroup([
            dbc.Button([html.I(className="bi bi-funnel"), " 筛选"], id='btn-filter'),
            dbc.Button([html.I(className="bi bi-type"), " 类型转换"], id='btn-type-convert'),
            dbc.Button([html.I(className="bi bi-trash"), " 删除列"], id='btn-drop-column'),
            dbc.Button([html.I(className="bi bi-pencil"), " 重命名"], id='btn-rename'),
            dbc.Button([html.I(className="bi bi-sort-down"), " 排序"], id='btn-sort'),
        ], className="me-2"),
        
        dbc.ButtonGroup([
            dbc.Button([html.I(className="bi bi-arrow-left"), " 撤销"], id='btn-undo', disabled=True),
            dbc.Button([html.I(className="bi bi-arrow-right"), " 重做"], id='btn-redo', disabled=True),
        ], className="me-2"),
        
        dbc.ButtonGroup([
            dbc.Button([html.I(className="bi bi-code-slash"), " 查看代码"], id='btn-view-code'),
            dbc.Button([html.I(className="bi bi-download"), " 导出"], id='btn-export'),
        ]),
    ], className="operation-toolbar p-3 bg-secondary border-bottom")
```

### 后端服务接口

#### 1. 预览服务 API

```python
@app.callback(
    Output('preview-data-store', 'data'),
    Output('preview-stats', 'children'),
    Input('operation-trigger', 'n_clicks'),
    State('pipeline-store', 'data'),
    State('original-data-store', 'data'),
)
def compute_preview(n_clicks, pipeline, original_data):
    """计算预览数据
    
    Returns:
        (预览数据JSON, 统计信息组件)
    """
    if not pipeline or not original_data:
        return None, "无数据"
    
    df = pd.DataFrame(original_data)
    engine = PreviewEngine(max_preview_rows=1000)
    
    result = engine.compute_preview(df, pipeline)
    
    stats = html.Div([
        html.Span(f"预览: {len(result['preview_df'])} / {result['full_rows']} 行"),
        html.Span(f" | {result['full_cols']} 列"),
        html.Span(f" | 耗时: {result['execution_time']:.2f}s"),
    ])
    
    return result['preview_df'].to_dict('records'), stats
```

#### 2. 代码生成服务 API

```python
@app.callback(
    Output('generated-code-display', 'value'),
    Input('pipeline-store', 'data'),
)
def generate_code(pipeline):
    """生成Python代码"""
    if not pipeline:
        return "# 暂无操作"
    
    generator = CodeGenerator()
    code = generator.generate_code(pipeline)
    return code
```

#### 3. 质量分析服务 API

```python
@app.callback(
    Output('quality-report-modal', 'is_open'),
    Output('quality-report-content', 'children'),
    Input('btn-quality-report', 'n_clicks'),
    State('original-data-store', 'data'),
)
def generate_quality_report(n_clicks, original_data):
    """生成数据质量报告"""
    if not n_clicks or not original_data:
        return False, None
    
    df = pd.DataFrame(original_data)
    analyzer = QualityAnalyzer()
    report = analyzer.analyze_dataframe(df)
    
    # 生成报告UI
    report_ui = create_quality_report_ui(report)
    
    return True, report_ui
```

## 性能优化

### 1. 虚拟滚动

使用Dash AG Grid的内置虚拟滚动功能：

```python
dashGridOptions={
    'rowModelType': 'infinite',  # 无限滚动模式
    'cacheBlockSize': 100,  # 每次加载100行
    'maxBlocksInCache': 10,  # 最多缓存10个块
}
```

### 2. 增量更新

只更新变化的数据，而不是重新渲染整个表格：

```python
@app.callback(
    Output('data-grid', 'rowTransaction'),
    Input('cell-edit-event', 'data'),
)
def update_cell(edit_event):
    """增量更新单元格"""
    return {
        'update': [edit_event['data']]  # 只更新修改的行
    }
```

### 3. 异步处理

对于长时间操作，使用后台任务：

```python
from dash import long_callback
from celery import Celery

celery_app = Celery(__name__, broker='redis://localhost:6379/0')

@long_callback(
    Output('preview-data-store', 'data'),
    Input('heavy-operation-trigger', 'n_clicks'),
    running=[
        (Output('loading-indicator', 'style'), {'display': 'block'}, {'display': 'none'}),
        (Output('cancel-button', 'disabled'), False, True),
    ],
    cancel=[Input('cancel-button', 'n_clicks')],
    manager=celery_app,
)
def heavy_operation(n_clicks):
    """长时间运行的操作"""
    # 执行耗时操作
    time.sleep(5)
    return result
```

### 4. 数据缓存

缓存中间计算结果：

```python
from functools import lru_cache
import hashlib

class PreviewEngine:
    def __init__(self):
        self.cache = {}
    
    def _get_cache_key(self, df: pd.DataFrame, pipeline: List[Dict]) -> str:
        """生成缓存键"""
        df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()
        pipeline_hash = hashlib.md5(json.dumps(pipeline, sort_keys=True).encode()).hexdigest()
        return f"{df_hash}_{pipeline_hash}"
    
    def compute_preview(self, df: pd.DataFrame, pipeline: List[Dict]) -> Dict:
        """带缓存的预览计算"""
        cache_key = self._get_cache_key(df, pipeline)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self._compute_preview_impl(df, pipeline)
        self.cache[cache_key] = result
        return result
```

### 5. 延迟执行 (Debounce)

用户停止输入后才触发计算：

```javascript
// assets/js/debounce.js
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        debounce_input: function(value) {
            clearTimeout(window.debounceTimer);
            return new Promise((resolve) => {
                window.debounceTimer = setTimeout(() => {
                    resolve(value);
                }, 500);  // 500ms延迟
            });
        }
    }
});
```


## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性反思

在编写正确性属性之前，我对prework中识别的可测试需求进行了反思，以消除冗余：

**识别的冗余：**

1. **预览行数限制**: 需求1.2（预览前1000行）和需求6.3（超过10000行时预览前10000行）可以合并为一个综合属性，验证预览行数限制规则
2. **步骤操作**: 需求3.2（点击步骤显示状态）、3.6（修改顺序重新计算）、3.8（编辑参数更新预览）都涉及步骤变化后的预览更新，可以合并为一个属性
3. **撤销重做**: 需求4.2（撤销）和4.3（重做）是互逆操作，可以合并为一个往返属性
4. **筛选条件**: 需求7.2（根据类型提供操作符）和7.3/7.4/7.5（具体类型的操作符）存在包含关系，7.2是通用属性
5. **代码生成**: 需求8.1-8.5涉及代码生成的多个方面，但8.8的往返属性是最强的正确性保证

**保留的独特属性：**
- 每个保留的属性提供独特的验证价值
- 往返属性优先于单向属性
- 通用属性优先于特定示例

### 核心属性

### 属性 1: 预览模式数据不变性

*对于任何*数据集和任何操作序列，在预览模式下执行操作后，原始数据应该保持完全不变。

**验证: 需求 1.3**

### 属性 2: 预览行数限制

*对于任何*数据集，预览结果的行数应该不超过配置的最大预览行数（默认1000行，大数据集10000行）。

**验证: 需求 1.2, 6.3**

### 属性 3: 应用操作后数据一致性

*对于任何*预览操作，当用户点击"应用"后，实际数据集应该与预览数据完全一致（在预览行数范围内）。

**验证: 需求 1.4**

### 属性 4: 操作统计准确性

*对于任何*数据操作，显示的影响行数和列数统计应该与实际变化的行列数相等。

**验证: 需求 1.5, 3.3**

### 属性 5: 列操作菜单类型匹配

*对于任何*列，列头菜单显示的操作选项应该适用于该列的数据类型。

**验证: 需求 2.4**

### 属性 6: 单元格编辑记录

*对于任何*单元格编辑操作，操作流水线中应该包含对应的编辑记录。

**验证: 需求 2.7**

### 属性 7: 步骤导航一致性

*对于任何*步骤序列，导航到任意步骤后显示的数据状态应该等于从头执行到该步骤的结果。

**验证: 需求 3.2, 3.6, 3.8**

### 属性 8: 步骤删除级联更新

*对于任何*步骤序列，删除任意步骤后，后续步骤的预览结果应该相应更新。

**验证: 需求 3.4**

### 属性 9: 撤销重做往返

*对于任何*操作状态，执行撤销然后重做应该恢复到原始状态。

**验证: 需求 4.2, 4.3**

### 属性 10: 历史栈容量限制

*对于任何*操作序列，当操作数量超过50时，撤销栈应该只保留最近的50个操作。

**验证: 需求 4.6**

### 属性 11: 分支操作历史清理

*对于任何*历史状态，在历史中间位置执行新操作后，该位置之后的所有重做历史应该被清除。

**验证: 需求 4.7**

### 属性 12: 操作搜索完整性

*对于任何*操作名称或关键词，搜索功能应该返回所有名称或描述中包含该关键词的操作。

**验证: 需求 5.7**

### 属性 13: 筛选操作符类型匹配

*对于任何*列，筛选面板提供的操作符应该适合该列的数据类型（数值、文本、日期）。

**验证: 需求 7.2**

### 属性 14: 多条件筛选逻辑

*对于任何*多条件筛选（AND/OR组合），筛选结果应该符合布尔逻辑规则。

**验证: 需求 7.6**

### 属性 15: 筛选结果统计准确性

*对于任何*筛选条件，显示的匹配行数应该等于实际满足条件的行数。

**验证: 需求 7.7**

### 属性 16: 筛选操作记录

*对于任何*应用的筛选条件，步骤管理器中应该包含对应的筛选步骤。

**验证: 需求 7.8**

### 属性 17: 代码生成完整性

*对于任何*操作流水线，生成的Python代码应该包含所有步骤的对应代码。

**验证: 需求 8.1**

### 属性 18: 代码包含必要导入

*对于任何*生成的代码，应该包含所有必要的导入语句（至少包含pandas）。

**验证: 需求 8.2**

### 属性 19: 代码步骤顺序一致性

*对于任何*操作流水线，生成代码中的步骤顺序应该与流水线中的顺序完全一致。

**验证: 需求 8.4**

### 属性 20: 代码可执行性

*对于任何*有效的操作流水线，生成的代码应该能在标准Python环境中成功执行。

**验证: 需求 8.5**

### 属性 21: 代码导出往返

*对于任何*有效的操作流水线，导出代码→执行代码→再次导出代码，应该产生等价的代码。

**验证: 需求 8.8**

### 属性 22: 类型检测准确性

*对于任何*数据集，自动类型检测应该能识别出明显的类型不匹配（如数值字符串、日期字符串）。

**验证: 需求 9.1, 9.2, 9.3**

### 属性 23: 类型转换错误报告

*对于任何*类型转换失败，应该显示详细的错误信息和失败的行数。

**验证: 需求 9.7**

### 属性 24: 缺失值统计准确性

*对于任何*列，显示的缺失值百分比应该等于实际缺失值数量除以总行数。

**验证: 需求 10.2**

### 属性 25: 缺失值筛选准确性

*对于任何*数据集，筛选显示包含缺失值的行应该只返回至少有一个缺失值的行。

**验证: 需求 10.7**

### 属性 26: 列拆分分隔符支持

*对于任何*有效的分隔符（单字符、多字符、正则表达式），列拆分操作应该正确工作。

**验证: 需求 11.2**

### 属性 27: 拆分结果预览准确性

*对于任何*列拆分操作，预览显示的列数和示例数据应该与实际拆分结果一致。

**验证: 需求 11.3**

### 属性 28: 拆分数量限制

*对于任何*指定的最大拆分数量N，拆分结果的列数应该不超过N。

**验证: 需求 11.4**

### 属性 29: 列拆分合并往返

*对于任何*有效的列拆分操作，拆分然后使用相同分隔符合并应该恢复原始数据。

**验证: 需求 11.8**

### 属性 30: 质量报告完整性

*对于任何*数据集，质量报告应该包含每列的数据类型、缺失值、唯一值和重复值信息。

**验证: 需求 12.3**

### 属性 31: 数值统计准确性

*对于任何*数值列，质量报告中的统计信息（均值、中位数、标准差）应该与pandas计算结果一致。

**验证: 需求 12.4**

### 属性 32: 文本模式分析

*对于任何*文本列，质量报告应该包含长度分布和常见模式的分析。

**验证: 需求 12.5**


## 错误处理

### 错误类型

#### 1. 数据操作错误

```python
class DataOperationError(Exception):
    """数据操作错误基类"""
    pass

class FilterError(DataOperationError):
    """筛选操作错误"""
    pass

class TypeConversionError(DataOperationError):
    """类型转换错误"""
    pass

class ColumnNotFoundError(DataOperationError):
    """列不存在错误"""
    pass
```

#### 2. 错误处理策略

```python
def safe_execute_operation(df: pd.DataFrame, operation: str, params: Dict) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """安全执行操作
    
    Returns:
        (结果数据框, 错误信息)
    """
    try:
        executor = OperationExecutor()
        result_df, code = executor.execute(df, operation, params)
        return result_df, None
    except ColumnNotFoundError as e:
        return None, f"列不存在: {e}"
    except TypeConversionError as e:
        return None, f"类型转换失败: {e}"
    except FilterError as e:
        return None, f"筛选条件错误: {e}"
    except Exception as e:
        return None, f"操作执行失败: {e}"
```

#### 3. 用户友好的错误提示

```python
def create_error_alert(error_msg: str, operation: str) -> dbc.Alert:
    """创建错误提示组件"""
    return dbc.Alert([
        html.H5([html.I(className="bi bi-exclamation-triangle me-2"), "操作失败"]),
        html.P(f"操作: {operation}"),
        html.P(f"错误: {error_msg}"),
        html.Hr(),
        html.P("建议:", className="mb-1"),
        html.Ul([
            html.Li("检查列名是否正确"),
            html.Li("检查数据类型是否匹配"),
            html.Li("检查筛选条件语法"),
        ]),
        dbc.Button("查看详细日志", id="view-error-log", size="sm"),
    ], color="danger", dismissable=True)
```

### 数据验证

#### 1. 输入验证

```python
def validate_filter_params(params: Dict) -> Tuple[bool, Optional[str]]:
    """验证筛选参数
    
    Returns:
        (是否有效, 错误信息)
    """
    if 'column' not in params:
        return False, "缺少列名参数"
    
    if 'operator' not in params:
        return False, "缺少操作符参数"
    
    if 'value' not in params:
        return False, "缺少筛选值参数"
    
    # 验证操作符
    valid_operators = ['==', '!=', '>', '<', '>=', '<=', 'contains', 'startswith', 'endswith']
    if params['operator'] not in valid_operators:
        return False, f"无效的操作符: {params['operator']}"
    
    return True, None
```

#### 2. 数据完整性检查

```python
def check_data_integrity(df: pd.DataFrame) -> List[str]:
    """检查数据完整性
    
    Returns:
        问题列表
    """
    issues = []
    
    # 检查空数据框
    if df.empty:
        issues.append("数据框为空")
    
    # 检查重复列名
    if df.columns.duplicated().any():
        dup_cols = df.columns[df.columns.duplicated()].tolist()
        issues.append(f"存在重复列名: {dup_cols}")
    
    # 检查全空列
    null_cols = df.columns[df.isnull().all()].tolist()
    if null_cols:
        issues.append(f"存在全空列: {null_cols}")
    
    return issues
```

## 测试策略

### 双重测试方法

本项目采用单元测试和属性测试相结合的方法，以确保全面的测试覆盖：

- **单元测试**: 验证特定示例、边缘情况和错误条件
- **属性测试**: 验证跨所有输入的通用属性
- 两者互补，对于全面覆盖都是必要的

### 单元测试

单元测试专注于：
- 演示正确行为的特定示例
- 组件之间的集成点
- 边缘情况和错误条件

避免编写过多的单元测试——属性测试处理大量输入的覆盖。

#### 示例单元测试

```python
import pytest
import pandas as pd
from services.preview_engine import PreviewEngine

class TestPreviewEngine:
    """预览引擎单元测试"""
    
    def test_preview_limits_rows(self):
        """测试预览行数限制"""
        df = pd.DataFrame({'a': range(2000)})
        engine = PreviewEngine(max_preview_rows=1000)
        
        result = engine.compute_preview(df, [])
        
        assert len(result['preview_df']) == 1000
        assert result['full_rows'] == 2000
        assert result['is_truncated'] == True
    
    def test_empty_pipeline(self):
        """测试空操作流水线"""
        df = pd.DataFrame({'a': [1, 2, 3]})
        engine = PreviewEngine()
        
        result = engine.compute_preview(df, [])
        
        assert len(result['preview_df']) == 3
        assert result['affected_rows'] == 0
        assert result['affected_cols'] == 0
    
    def test_filter_operation(self):
        """测试筛选操作"""
        df = pd.DataFrame({'age': [15, 20, 25, 30]})
        pipeline = [{
            'operation': 'filter',
            'params': {'column': 'age', 'operator': '>', 'value': 18}
        }]
        engine = PreviewEngine()
        
        result = engine.compute_preview(df, pipeline)
        
        assert result['full_rows'] == 3
        assert result['affected_rows'] == 1  # 1行被过滤掉
```

### 属性测试

属性测试专注于：
- 跨所有输入保持的通用属性
- 通过随机化实现全面的输入覆盖

#### 属性测试配置

- **测试库**: 使用 Hypothesis (Python)
- **最小迭代次数**: 每个属性测试100次
- **标签格式**: `Feature: data-workshop-realtime-preview, Property {number}: {property_text}`

#### 示例属性测试

```python
from hypothesis import given, strategies as st
import pandas as pd
from services.preview_engine import PreviewEngine

class TestPreviewEngineProperties:
    """预览引擎属性测试
    
    Feature: data-workshop-realtime-preview
    """
    
    @given(
        data=st.lists(st.integers(), min_size=0, max_size=10000),
        max_rows=st.integers(min_value=10, max_value=1000)
    )
    def test_property_2_preview_row_limit(self, data, max_rows):
        """Property 2: 预览行数限制
        
        对于任何数据集，预览结果的行数应该不超过配置的最大预览行数
        
        Feature: data-workshop-realtime-preview, Property 2: 预览行数限制
        """
        df = pd.DataFrame({'value': data})
        engine = PreviewEngine(max_preview_rows=max_rows)
        
        result = engine.compute_preview(df, [])
        
        assert len(result['preview_df']) <= max_rows
        assert len(result['preview_df']) <= len(df)
    
    @given(
        data=st.lists(st.integers(), min_size=1, max_size=100)
    )
    def test_property_1_preview_mode_immutability(self, data):
        """Property 1: 预览模式数据不变性
        
        对于任何数据集和任何操作序列，在预览模式下执行操作后，
        原始数据应该保持完全不变
        
        Feature: data-workshop-realtime-preview, Property 1: 预览模式数据不变性
        """
        df = pd.DataFrame({'value': data})
        df_original = df.copy()
        
        engine = PreviewEngine()
        pipeline = [{
            'operation': 'filter',
            'params': {'column': 'value', 'operator': '>', 'value': data[0]}
        }]
        
        result = engine.compute_preview(df, pipeline)
        
        # 原始数据应该完全不变
        pd.testing.assert_frame_equal(df, df_original)
    
    @given(
        data=st.lists(st.integers(), min_size=1, max_size=100)
    )
    def test_property_9_undo_redo_roundtrip(self, data):
        """Property 9: 撤销重做往返
        
        对于任何操作状态，执行撤销然后重做应该恢复到原始状态
        
        Feature: data-workshop-realtime-preview, Property 9: 撤销重做往返
        """
        from services.undo_redo_stack import UndoRedoStack
        
        stack = UndoRedoStack()
        
        # 创建初始状态
        initial_state = {'data': data, 'step': 0}
        stack.push_state(initial_state)
        
        # 添加新状态
        new_state = {'data': data + [999], 'step': 1}
        stack.push_state(new_state)
        
        # 撤销
        undone_state = stack.undo()
        assert undone_state == initial_state
        
        # 重做
        redone_state = stack.redo()
        assert redone_state == new_state
```


#### 更多属性测试示例

```python
class TestCodeGeneratorProperties:
    """代码生成器属性测试"""
    
    @given(
        operations=st.lists(
            st.fixed_dictionaries({
                'operation': st.sampled_from(['filter', 'drop_column', 'rename_column']),
                'params': st.dictionaries(st.text(), st.text())
            }),
            min_size=1,
            max_size=10
        )
    )
    def test_property_17_code_generation_completeness(self, operations):
        """Property 17: 代码生成完整性
        
        对于任何操作流水线，生成的Python代码应该包含所有步骤的对应代码
        
        Feature: data-workshop-realtime-preview, Property 17: 代码生成完整性
        """
        from services.code_generator import CodeGenerator
        
        generator = CodeGenerator()
        code = generator.generate_code(operations)
        
        # 验证每个操作都在生成的代码中
        for i, op in enumerate(operations):
            assert f"步骤{i+1}" in code or op['operation'] in code
    
    @given(
        operations=st.lists(
            st.fixed_dictionaries({
                'operation': st.sampled_from(['filter', 'drop_column']),
                'params': st.dictionaries(st.text(), st.text())
            }),
            min_size=1,
            max_size=5
        )
    )
    def test_property_18_code_includes_imports(self, operations):
        """Property 18: 代码包含必要导入
        
        对于任何生成的代码，应该包含所有必要的导入语句
        
        Feature: data-workshop-realtime-preview, Property 18: 代码包含必要导入
        """
        from services.code_generator import CodeGenerator
        
        generator = CodeGenerator()
        code = generator.generate_code(operations, include_imports=True)
        
        # 验证包含pandas导入
        assert 'import pandas as pd' in code


class TestFilterParserProperties:
    """筛选解析器属性测试"""
    
    @given(
        column=st.text(min_size=1),
        operator=st.sampled_from(['==', '!=', '>', '<', '>=', '<=']),
        value=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_property_14_multi_condition_logic(self, column, operator, value):
        """Property 14: 多条件筛选逻辑
        
        对于任何多条件筛选，筛选结果应该符合布尔逻辑规则
        
        Feature: data-workshop-realtime-preview, Property 14: 多条件筛选逻辑
        """
        from services.filter_parser import FilterParser
        
        parser = FilterParser()
        
        # 创建两个条件
        cond1 = parser.parse_numeric_condition(column, operator, value)
        cond2 = parser.parse_numeric_condition(column, '!=', value + 1)
        
        # AND组合
        and_result = parser.combine_conditions([cond1, cond2], 'AND')
        assert '&' in and_result
        assert cond1 in and_result
        assert cond2 in and_result
        
        # OR组合
        or_result = parser.combine_conditions([cond1, cond2], 'OR')
        assert '|' in or_result


class TestStepManagerProperties:
    """步骤管理器属性测试"""
    
    @given(
        steps=st.lists(
            st.fixed_dictionaries({
                'operation': st.text(min_size=1),
                'params': st.dictionaries(st.text(), st.text())
            }),
            min_size=1,
            max_size=60
        )
    )
    def test_property_10_history_capacity_limit(self, steps):
        """Property 10: 历史栈容量限制
        
        对于任何操作序列，当操作数量超过50时，撤销栈应该只保留最近的50个操作
        
        Feature: data-workshop-realtime-preview, Property 10: 历史栈容量限制
        """
        from services.undo_redo_stack import UndoRedoStack
        
        stack = UndoRedoStack(max_history=50)
        
        # 添加所有步骤
        for step in steps:
            stack.push_state(step)
        
        # 验证历史数量不超过50
        assert len(stack.history) <= 50
        
        # 如果步骤数超过50，应该保留最近的50个
        if len(steps) > 50:
            assert len(stack.history) == 50
            # 最新的步骤应该在历史中
            assert stack.history[-1] == steps[-1]


class TestTypeDetectorProperties:
    """类型检测器属性测试"""
    
    @given(
        numeric_strings=st.lists(
            st.integers().map(str),
            min_size=10,
            max_size=100
        )
    )
    def test_property_22_type_detection_accuracy(self, numeric_strings):
        """Property 22: 类型检测准确性
        
        对于任何数据集，自动类型检测应该能识别出明显的类型不匹配
        
        Feature: data-workshop-realtime-preview, Property 22: 类型检测准确性
        """
        from services.type_detector import TypeDetector
        
        # 创建数值字符串列
        series = pd.Series(numeric_strings, dtype='object')
        
        detector = TypeDetector()
        result = detector.detect_column_type(series)
        
        # 应该检测出这是数值字符串
        assert result['detected_type'] in ['int', 'float', 'numeric']
        assert result['mismatch'] == True
        assert result['confidence'] > 0.8


class TestQualityAnalyzerProperties:
    """质量分析器属性测试"""
    
    @given(
        data=st.lists(
            st.one_of(st.integers(), st.none()),
            min_size=10,
            max_size=100
        )
    )
    def test_property_24_missing_value_statistics(self, data):
        """Property 24: 缺失值统计准确性
        
        对于任何列，显示的缺失值百分比应该等于实际缺失值数量除以总行数
        
        Feature: data-workshop-realtime-preview, Property 24: 缺失值统计准确性
        """
        from services.quality_analyzer import QualityAnalyzer
        
        df = pd.DataFrame({'value': data})
        analyzer = QualityAnalyzer()
        
        result = analyzer.analyze_column(df['value'])
        
        # 计算实际缺失值百分比
        actual_missing_count = df['value'].isnull().sum()
        actual_missing_percent = (actual_missing_count / len(df)) * 100
        
        # 验证统计准确性
        assert result['missing_count'] == actual_missing_count
        assert abs(result['missing_percent'] - actual_missing_percent) < 0.01
    
    @given(
        numeric_data=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=10, max_size=100)
    )
    def test_property_31_numeric_statistics_accuracy(self, numeric_data):
        """Property 31: 数值统计准确性
        
        对于任何数值列，质量报告中的统计信息应该与pandas计算结果一致
        
        Feature: data-workshop-realtime-preview, Property 31: 数值统计准确性
        """
        from services.quality_analyzer import QualityAnalyzer
        
        df = pd.DataFrame({'value': numeric_data})
        analyzer = QualityAnalyzer()
        
        result = analyzer.analyze_column(df['value'])
        
        # 验证统计信息
        assert abs(result['statistics']['mean'] - df['value'].mean()) < 0.01
        assert abs(result['statistics']['median'] - df['value'].median()) < 0.01
        assert abs(result['statistics']['std'] - df['value'].std()) < 0.01
```

### 集成测试

集成测试验证组件之间的交互：

```python
class TestDataWorkshopIntegration:
    """数据工坊集成测试"""
    
    def test_end_to_end_workflow(self):
        """测试完整的工作流程"""
        # 1. 加载数据
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': ['25', '30', '35'],  # 数值字符串
            'city': ['NYC', 'LA', 'SF']
        })
        
        # 2. 类型检测
        detector = TypeDetector()
        age_type = detector.detect_column_type(df['age'])
        assert age_type['mismatch'] == True
        
        # 3. 应用类型转换
        executor = OperationExecutor()
        df_converted, code = executor.execute_type_conversion(
            df, {'column': 'age', 'target_type': 'int'}
        )
        assert df_converted['age'].dtype == 'int64'
        
        # 4. 添加筛选
        df_filtered, code = executor.execute_filter(
            df_converted, {'column': 'age', 'operator': '>', 'value': 25}
        )
        assert len(df_filtered) == 2
        
        # 5. 生成代码
        pipeline = [
            {'operation': 'type_conversion', 'params': {'column': 'age', 'target_type': 'int'}},
            {'operation': 'filter', 'params': {'column': 'age', 'operator': '>', 'value': 25}}
        ]
        generator = CodeGenerator()
        code = generator.generate_code(pipeline)
        
        assert 'pd.to_numeric' in code
        assert "df['age'] > 25" in code
    
    def test_undo_redo_with_preview(self):
        """测试撤销重做与预览的集成"""
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        
        # 创建组件
        engine = PreviewEngine()
        stack = UndoRedoStack()
        
        # 初始状态
        initial_pipeline = []
        stack.push_state({'pipeline': initial_pipeline})
        
        # 添加筛选
        filter_pipeline = [{'operation': 'filter', 'params': {'column': 'value', 'operator': '>', 'value': 2}}]
        stack.push_state({'pipeline': filter_pipeline})
        result1 = engine.compute_preview(df, filter_pipeline)
        assert result1['full_rows'] == 3
        
        # 撤销
        undone = stack.undo()
        result2 = engine.compute_preview(df, undone['pipeline'])
        assert result2['full_rows'] == 5
        
        # 重做
        redone = stack.redo()
        result3 = engine.compute_preview(df, redone['pipeline'])
        assert result3['full_rows'] == 3
```

### 性能测试

```python
import time
import pytest

class TestPerformance:
    """性能测试"""
    
    def test_preview_performance_large_dataset(self):
        """测试大数据集预览性能"""
        # 创建100万行数据
        df = pd.DataFrame({
            'id': range(1000000),
            'value': np.random.randn(1000000)
        })
        
        engine = PreviewEngine(max_preview_rows=1000)
        
        start_time = time.time()
        result = engine.compute_preview(df, [])
        elapsed = time.time() - start_time
        
        # 预览应该在1秒内完成
        assert elapsed < 1.0
        assert len(result['preview_df']) == 1000
    
    def test_code_generation_performance(self):
        """测试代码生成性能"""
        # 创建50个操作步骤
        pipeline = [
            {'operation': 'filter', 'params': {'column': 'value', 'operator': '>', 'value': i}}
            for i in range(50)
        ]
        
        generator = CodeGenerator()
        
        start_time = time.time()
        code = generator.generate_code(pipeline)
        elapsed = time.time() - start_time
        
        # 代码生成应该在0.5秒内完成
        assert elapsed < 0.5
        assert len(code) > 0
```


## 实现计划

### 阶段 1: 核心架构 (第1-2周)

#### 1.1 数据层和服务层基础

- [ ] 实现 `PreviewEngine` 类
  - 基础预览计算
  - 行数限制
  - 结果缓存
- [ ] 实现 `OperationExecutor` 类
  - 基础操作执行（筛选、删除列、重命名）
  - 错误处理
- [ ] 实现 `StepManager` 类
  - 流水线管理
  - 步骤增删改查
- [ ] 实现 `UndoRedoStack` 类
  - 历史记录管理
  - 撤销重做逻辑

#### 1.2 前端基础组件

- [ ] 创建数据表格组件（使用Dash AG Grid）
  - 基础表格渲染
  - 虚拟滚动配置
- [ ] 创建步骤管理面板
  - 步骤列表显示
  - 基础交互（点击、删除）
- [ ] 创建操作工具栏
  - 常用操作按钮
  - 撤销重做按钮

### 阶段 2: 实时预览功能 (第3-4周)

#### 2.1 预览引擎优化

- [ ] 实现增量计算
- [ ] 实现异步处理
- [ ] 实现取消机制
- [ ] 添加性能监控

#### 2.2 UI交互优化

- [ ] 实现延迟执行（debounce）
- [ ] 添加加载指示器
- [ ] 实现预览统计显示
- [ ] 优化状态管理

#### 2.3 列操作功能

- [ ] 实现列头右键菜单
- [ ] 实现内联编辑
- [ ] 实现列头筛选图标
- [ ] 根据数据类型动态显示操作

### 阶段 3: 高级功能 (第5-6周)

#### 3.1 筛选系统

- [ ] 实现 `FilterPanel` 组件
  - 数值筛选
  - 文本筛选
  - 日期筛选
- [ ] 实现 `FilterParser` 类
  - 条件解析
  - 多条件组合
- [ ] 实现筛选预览

#### 3.2 代码导出功能

- [ ] 实现 `CodeGenerator` 类
  - 基础代码生成
  - 代码格式化
  - 注释生成
- [ ] 创建代码预览面板
- [ ] 实现代码复制和下载

#### 3.3 类型检测和质量分析

- [ ] 实现 `TypeDetector` 类
  - 数值字符串检测
  - 日期字符串检测
  - 类型建议
- [ ] 实现 `QualityAnalyzer` 类
  - 列分析
  - 问题识别
  - 报告生成

### 阶段 4: 测试和优化 (第7-8周)

#### 4.1 测试实现

- [ ] 编写单元测试
  - 核心组件测试
  - 边缘情况测试
- [ ] 编写属性测试
  - 实现所有32个属性测试
  - 配置Hypothesis
- [ ] 编写集成测试
  - 端到端工作流测试
  - 组件交互测试
- [ ] 编写性能测试

#### 4.2 性能优化

- [ ] 优化预览计算性能
- [ ] 优化前端渲染性能
- [ ] 优化内存使用
- [ ] 添加性能监控

#### 4.3 文档和部署

- [ ] 编写用户文档
- [ ] 编写开发者文档
- [ ] 准备演示数据
- [ ] 部署到测试环境

## 技术栈

### 后端

- **Python 3.9+**
- **Pandas**: 数据处理
- **NumPy**: 数值计算
- **Dash**: Web框架
- **Dash AG Grid**: 高性能表格组件
- **Hypothesis**: 属性测试框架
- **pytest**: 单元测试框架

### 前端

- **Dash**: 组件框架
- **Dash Bootstrap Components**: UI组件库
- **AG Grid**: 表格组件
- **Bootstrap Icons**: 图标库
- **JavaScript**: 客户端交互

### 开发工具

- **Black**: 代码格式化
- **Pylint**: 代码检查
- **mypy**: 类型检查
- **pytest-cov**: 测试覆盖率

## 部署架构

### 开发环境

```
┌─────────────────────────────────────┐
│  开发服务器 (localhost:8050)         │
├─────────────────────────────────────┤
│  Dash App                           │
│  - 热重载                            │
│  - 调试模式                          │
│  - 详细日志                          │
└─────────────────────────────────────┘
```

### 生产环境

```
┌─────────────────────────────────────┐
│  Nginx (反向代理)                    │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Gunicorn (WSGI服务器)               │
│  - 多进程                            │
│  - 负载均衡                          │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Dash App                           │
│  - 生产模式                          │
│  - 错误处理                          │
│  - 性能监控                          │
└─────────────────────────────────────┘
```

## 安全考虑

### 1. 数据安全

- 用户数据仅在内存中处理，不持久化到磁盘
- 支持数据加密传输（HTTPS）
- 实现会话隔离，防止数据泄露

### 2. 代码注入防护

```python
def sanitize_column_name(column: str) -> str:
    """清理列名，防止代码注入"""
    # 只允许字母、数字、下划线
    import re
    return re.sub(r'[^\w]', '_', column)

def safe_eval_filter(condition: str) -> bool:
    """安全评估筛选条件"""
    # 使用白名单方法，只允许特定操作
    allowed_operators = ['==', '!=', '>', '<', '>=', '<=', '&', '|']
    # 禁止使用eval，使用pandas的query方法
    return True
```

### 3. 资源限制

```python
# 限制数据集大小
MAX_DATASET_SIZE = 100_000_000  # 100MB
MAX_ROWS = 10_000_000  # 1000万行

# 限制操作超时
OPERATION_TIMEOUT = 30  # 30秒

# 限制历史记录
MAX_HISTORY = 50
```

## 监控和日志

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_workshop.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('data_workshop')

# 记录关键操作
logger.info(f"Preview computed: {result['full_rows']} rows, {result['execution_time']:.2f}s")
logger.warning(f"Large dataset detected: {len(df)} rows")
logger.error(f"Operation failed: {error_msg}")
```

### 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        logger.info(f"{func.__name__} executed in {elapsed:.2f}s")
        
        if elapsed > 1.0:
            logger.warning(f"{func.__name__} took longer than 1s: {elapsed:.2f}s")
        
        return result
    return wrapper

@monitor_performance
def compute_preview(df, pipeline):
    # 实现
    pass
```

## 兼容性说明

### 与现有架构的兼容性

本设计完全兼容DataViz Studio的现有架构：

1. **Python优先**: 所有操作都生成Python代码，可导出执行
2. **Dash框架**: 使用相同的Dash框架和组件库
3. **数据管理**: 集成现有的DataManager
4. **代码生成**: 遵循现有的CodeGenerator模式
5. **UI风格**: 使用相同的Bootstrap主题和样式

### 集成点

```python
# 与现有DataManager集成
from core.data_manager import DataManager

dm = DataManager()
df = dm.active_df  # 获取当前活动数据集

# 与现有CodeGenerator集成
from services.code_generator import CodeGenerator

generator = CodeGenerator()
code = generator.generate_code(pipeline)

# 与现有UI组件集成
from components.code_preview import create_code_preview_panel

code_panel = create_code_preview_panel()
```

## 总结

本设计文档详细描述了数据工坊实时预览功能的完整技术方案，包括：

- **系统架构**: 前后端分离，Python优先
- **核心组件**: 预览引擎、步骤管理器、代码生成器等
- **数据流设计**: 操作流水线、状态管理、预览计算
- **性能优化**: 虚拟滚动、增量更新、异步处理、缓存
- **正确性保证**: 32个属性测试确保系统正确性
- **测试策略**: 单元测试、属性测试、集成测试、性能测试
- **实现计划**: 8周分4个阶段完成

该设计完全兼容现有的DataViz Studio架构，可以无缝集成到现有系统中。通过实时预览、步骤管理和代码导出功能，将大幅提升数据清洗的用户体验和工作效率。
