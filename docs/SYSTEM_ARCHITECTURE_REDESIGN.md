# DataViz Studio 系统架构重新设计

## 🎯 核心定位

**DataViz Studio 是一个可视化的 Python 数据分析平台**

不是一个简单的前端图表工具，而是：
- Python 数据分析代码的可视化编辑器
- 所有操作都对应 Python 代码
- 所有成果都可以导出成可执行的 Python 脚本
- 用户可以在 Jupyter Notebook 中直接运行导出的代码

## 🏗️ 架构原则

### 1. Python 优先
```
用户操作 → Python 代码 → 执行结果 → 前端展示
         ↓
    可导出的代码
```

### 2. 代码即配置
每个操作都对应一段 Python 代码：
```python
# 用户拖拽字段配置
UI: x="city", y="sales", color="category"

# 对应的 Python 代码
import plotly.express as px
fig = px.bar(df, x='city', y='sales', color='category')
fig.show()
```

### 3. 完整的 Plotly 参数支持
不是简化的"维度/度量"，而是完整的 Plotly 参数：
```python
px.scatter(
    df,
    x='sales',              # X轴
    y='profit',             # Y轴
    color='category',       # 颜色
    size='quantity',        # 大小
    hover_data=['city'],    # 悬停数据
    facet_row='region',     # 分面行
    facet_col='year',       # 分面列
    text='label',           # 文本标签
    animation_frame='date', # 动画帧
    animation_group='id',   # 动画组
    trendline='ols',        # 趋势线
    marginal_x='histogram', # 边际图
    marginal_y='box',       # 边际图
    # ... 更多参数
)
```

## 📊 图表工作室重新设计

### 字段配置面板（完整版）

#### 基础参数
```
┌─────────────────────────────────────────────────┐
│ 基础配置                                         │
├─────────────────────────────────────────────────┤
│ X轴 (x):        [拖拽字段或选择]                 │
│ Y轴 (y):        [拖拽字段或选择]                 │
│ 颜色 (color):   [拖拽字段或选择]                 │
│ 大小 (size):    [拖拽字段或选择]                 │
└─────────────────────────────────────────────────┘
```

#### 高级参数
```
┌─────────────────────────────────────────────────┐
│ 高级配置                                         │
├─────────────────────────────────────────────────┤
│ 悬停数据 (hover_data):     [多选字段]            │
│ 文本标签 (text):           [选择字段]            │
│ 分面行 (facet_row):        [选择字段]            │
│ 分面列 (facet_col):        [选择字段]            │
│ 动画帧 (animation_frame):  [选择字段]            │
│ 动画组 (animation_group):  [选择字段]            │
└─────────────────────────────────────────────────┘
```

#### 数据处理参数
```
┌─────────────────────────────────────────────────┐
│ 数据处理                                         │
├─────────────────────────────────────────────────┤
│ 聚合方式:  □ sum  □ mean  □ count  □ median     │
│ 排序:      □ 升序  □ 降序  □ 不排序              │
│ 筛选:      [添加筛选条件]                        │
│ 分组:      [选择分组字段]                        │
└─────────────────────────────────────────────────┘
```

#### 图表增强
```
┌─────────────────────────────────────────────────┐
│ 图表增强                                         │
├─────────────────────────────────────────────────┤
│ 趋势线 (trendline):        □ ols  □ lowess      │
│ 边际图 X (marginal_x):     □ histogram  □ box   │
│ 边际图 Y (marginal_y):     □ histogram  □ violin│
│ 误差条 (error_x/error_y):  [选择字段]            │
└─────────────────────────────────────────────────┘
```

### 代码生成器

每次配置变化，实时生成对应的 Python 代码：

```python
# ============================================
# DataViz Studio 自动生成代码
# 生成时间: 2024-01-01 12:00:00
# ============================================

import pandas as pd
import plotly.express as px

# 1. 加载数据
df = pd.read_csv('sales_data.csv')

# 2. 数据预处理（如果有）
# df = df[df['sales'] > 1000]  # 筛选
# df = df.groupby('city')['sales'].sum().reset_index()  # 聚合

# 3. 创建图表
fig = px.bar(
    df,
    x='city',
    y='sales',
    color='category',
    hover_data=['profit', 'quantity'],
    title='各城市销售额分析',
    labels={'sales': '销售额', 'city': '城市'},
    color_discrete_sequence=px.colors.qualitative.Set2,
)

# 4. 样式配置
fig.update_layout(
    template='plotly_dark',
    showlegend=True,
    xaxis_title='城市',
    yaxis_title='销售额（元）',
    font=dict(family='Microsoft YaHei', size=12),
)

# 5. 显示图表
fig.show()

# 6. 保存图表
# fig.write_html('chart.html')
# fig.write_image('chart.png')
```

## 🔄 数据流架构

### 完整的数据流
```
┌─────────────┐
│  用户操作    │ (拖拽字段、选择参数)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 配置状态管理 │ (Dash Store)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Python 后端  │ (生成代码 + 执行)
│             │
│ 1. 代码生成  │ → 生成 Python 代码字符串
│ 2. 数据处理  │ → pandas 操作
│ 3. 图表生成  │ → plotly.express / plotly.graph_objects
│ 4. 代码记录  │ → 保存到操作历史
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  前端展示    │
│             │
│ 1. 图表显示  │ (dcc.Graph)
│ 2. 代码显示  │ (代码编辑器)
│ 3. 导出按钮  │ (下载 .py 文件)
└─────────────┘
```

### 代码生成服务

```python
# services/code_generator.py

class ChartCodeGenerator:
    """图表代码生成器"""
    
    def __init__(self):
        self.imports = set()
        self.data_operations = []
        self.chart_code = ""
        self.layout_code = ""
    
    def generate_full_code(
        self,
        data_source: str,
        chart_type: str,
        params: dict,
        data_ops: list = None,
        layout_config: dict = None
    ) -> str:
        """生成完整的 Python 代码
        
        Args:
            data_source: 数据源（文件路径或 DataFrame 名称）
            chart_type: 图表类型（bar, line, scatter 等）
            params: 图表参数（x, y, color, size 等）
            data_ops: 数据操作列表（筛选、聚合等）
            layout_config: 布局配置（标题、主题等）
        
        Returns:
            完整的可执行 Python 代码
        """
        code_parts = []
        
        # 1. 导入语句
        code_parts.append(self._generate_imports())
        
        # 2. 数据加载
        code_parts.append(self._generate_data_loading(data_source))
        
        # 3. 数据预处理
        if data_ops:
            code_parts.append(self._generate_data_operations(data_ops))
        
        # 4. 图表创建
        code_parts.append(self._generate_chart_code(chart_type, params))
        
        # 5. 样式配置
        if layout_config:
            code_parts.append(self._generate_layout_code(layout_config))
        
        # 6. 显示和保存
        code_parts.append(self._generate_output_code())
        
        return "\n\n".join(code_parts)
    
    def _generate_chart_code(self, chart_type: str, params: dict) -> str:
        """生成图表创建代码"""
        # 构建参数字符串
        param_lines = []
        for key, value in params.items():
            if value is not None:
                if isinstance(value, str):
                    param_lines.append(f"    {key}='{value}',")
                elif isinstance(value, list):
                    param_lines.append(f"    {key}={value},")
                else:
                    param_lines.append(f"    {key}={value},")
        
        params_str = "\n".join(param_lines)
        
        return f"""# 创建图表
fig = px.{chart_type}(
    df,
{params_str}
)"""
```

## 🎨 UI 组件重新设计

### 1. 字段选择器（不是拖拽，而是下拉选择）

```python
def create_field_selector(field_name: str, label: str, df: pd.DataFrame):
    """创建字段选择器
    
    Args:
        field_name: 参数名（x, y, color 等）
        label: 显示标签
        df: 数据框
    """
    return html.Div([
        html.Label(label, className="field-label"),
        dcc.Dropdown(
            id={"type": "field-selector", "field": field_name},
            options=[{"label": col, "value": col} for col in df.columns],
            placeholder=f"选择 {label}",
            clearable=True,
            className="field-dropdown"
        ),
    ], className="field-selector-item")
```

### 2. 参数配置面板

```python
def create_chart_config_panel(df: pd.DataFrame):
    """创建完整的参数配置面板"""
    return html.Div([
        # 基础参数
        html.Div([
            html.H6("基础参数"),
            create_field_selector("x", "X轴", df),
            create_field_selector("y", "Y轴", df),
            create_field_selector("color", "颜色", df),
            create_field_selector("size", "大小", df),
        ], className="config-section"),
        
        # 高级参数（可折叠）
        dbc.Collapse([
            html.H6("高级参数"),
            create_field_selector("hover_data", "悬停数据", df, multi=True),
            create_field_selector("text", "文本标签", df),
            create_field_selector("facet_row", "分面行", df),
            create_field_selector("facet_col", "分面列", df),
            create_field_selector("animation_frame", "动画帧", df),
        ], id="advanced-params-collapse"),
        
        # 数据处理
        html.Div([
            html.H6("数据处理"),
            dcc.Dropdown(
                id="aggregation-method",
                options=[
                    {"label": "求和 (sum)", "value": "sum"},
                    {"label": "平均值 (mean)", "value": "mean"},
                    {"label": "计数 (count)", "value": "count"},
                    {"label": "中位数 (median)", "value": "median"},
                    {"label": "最大值 (max)", "value": "max"},
                    {"label": "最小值 (min)", "value": "min"},
                ],
                placeholder="选择聚合方式（可选）"
            ),
        ], className="config-section"),
        
        # 图表增强
        html.Div([
            html.H6("图表增强"),
            dcc.Dropdown(
                id="trendline",
                options=[
                    {"label": "OLS 回归", "value": "ols"},
                    {"label": "LOWESS 平滑", "value": "lowess"},
                ],
                placeholder="添加趋势线（可选）"
            ),
            dcc.Dropdown(
                id="marginal-x",
                options=[
                    {"label": "直方图", "value": "histogram"},
                    {"label": "箱线图", "value": "box"},
                    {"label": "小提琴图", "value": "violin"},
                ],
                placeholder="X轴边际图（可选）"
            ),
        ], className="config-section"),
    ])
```

### 3. 代码预览和导出

```python
def create_code_preview_panel():
    """创建代码预览面板"""
    return html.Div([
        html.Div([
            html.H6("生成的 Python 代码"),
            dbc.ButtonGroup([
                dbc.Button("复制代码", id="copy-code-btn", size="sm"),
                dbc.Button("下载 .py", id="download-code-btn", size="sm"),
                dbc.Button("在 Jupyter 中打开", id="open-jupyter-btn", size="sm"),
            ]),
        ], className="code-header"),
        
        html.Div([
            dcc.Textarea(
                id="generated-code",
                readOnly=True,
                style={
                    "width": "100%",
                    "height": "400px",
                    "fontFamily": "monospace",
                    "fontSize": "12px",
                    "backgroundColor": "#1e1e1e",
                    "color": "#d4d4d4",
                    "padding": "12px",
                    "border": "1px solid #333",
                    "borderRadius": "4px",
                }
            ),
        ], className="code-content"),
    ], className="code-preview-panel")
```

## 📝 操作历史和代码导出

### 操作历史记录

```python
class OperationHistory:
    """操作历史管理器"""
    
    def __init__(self):
        self.operations = []
        self.current_index = -1
    
    def add_operation(self, operation: dict):
        """添加操作
        
        Args:
            operation: {
                'type': 'chart_create',
                'timestamp': '2024-01-01 12:00:00',
                'code': 'fig = px.bar(...)',
                'params': {...},
                'result': 'success'
            }
        """
        # 如果不在最新位置，删除后面的操作
        if self.current_index < len(self.operations) - 1:
            self.operations = self.operations[:self.current_index + 1]
        
        self.operations.append(operation)
        self.current_index += 1
    
    def undo(self):
        """撤销操作"""
        if self.current_index > 0:
            self.current_index -= 1
            return self.operations[self.current_index]
        return None
    
    def redo(self):
        """重做操作"""
        if self.current_index < len(self.operations) - 1:
            self.current_index += 1
            return self.operations[self.current_index]
        return None
    
    def export_notebook(self, filename: str):
        """导出为 Jupyter Notebook"""
        import nbformat
        from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
        
        nb = new_notebook()
        
        # 添加标题
        nb.cells.append(new_markdown_cell("# DataViz Studio 导出的分析"))
        
        # 添加每个操作的代码
        for op in self.operations:
            if op['type'] == 'data_load':
                nb.cells.append(new_markdown_cell("## 数据加载"))
                nb.cells.append(new_code_cell(op['code']))
            elif op['type'] == 'data_process':
                nb.cells.append(new_markdown_cell("## 数据处理"))
                nb.cells.append(new_code_cell(op['code']))
            elif op['type'] == 'chart_create':
                nb.cells.append(new_markdown_cell("## 图表创建"))
                nb.cells.append(new_code_cell(op['code']))
        
        # 保存
        with open(filename, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
```

## 🚀 实现路线图

### Phase 1: 核心架构重构
1. 重新设计 `services/chart_service.py`
   - 完整的 Plotly 参数支持
   - 代码生成功能
   
2. 创建 `services/code_generator.py`
   - 代码生成器
   - 操作历史管理
   
3. 更新 `pages/chart_studio.py`
   - 使用下拉选择代替拖拽
   - 完整的参数配置面板
   - 代码预览面板

### Phase 2: 代码导出功能
1. 实现代码复制功能
2. 实现 .py 文件下载
3. 实现 Jupyter Notebook 导出
4. 实现操作历史记录

### Phase 3: 数据处理集成
1. 数据筛选代码生成
2. 数据聚合代码生成
3. 数据转换代码生成
4. 完整的 pandas 操作支持

## 📚 参考资料

- [Plotly Express API](https://plotly.com/python-api-reference/plotly.express.html)
- [Plotly Graph Objects](https://plotly.com/python-api-reference/plotly.graph_objects.html)
- [pandas API](https://pandas.pydata.org/docs/reference/index.html)

---

**这才是 DataViz Studio 应该有的样子：一个真正的可视化 Python 数据分析平台！**
