# DataViz Studio — Python优先架构设计

## 🎯 核心定位重新确认

**DataViz Studio 是一个可视化的 Python 数据分析平台**

### 核心特性
1. **Python后端生成图表** — 所有图表由Python生成，前端只负责显示
2. **多图表库支持** — 支持Plotly和Seaborn，用户可以切换选择
3. **完整API参数** — 使用Plotly/Seaborn的完整参数，不简化
4. **代码导出** — 所有操作都可以导出成可执行的Python代码

### 数据流架构

```
用户操作（UI配置）
    ↓
前端收集参数
    ↓
发送到Python后端
    ↓
Python后端：
  1. 根据选择的库（Plotly/Seaborn）生成代码
  2. 执行代码生成图表
  3. 记录代码到历史
    ↓
返回结果：
  - 图表对象（Plotly: JSON / Seaborn: base64图片）
  - 生成的Python代码字符串
    ↓
前端显示：
  - 图表展示区：显示图表
  - 代码预览区：显示生成的代码
```

## 📊 图表库支持

### 1. Plotly支持

**Plotly Express（简单快速）**
```python
import plotly.express as px

fig = px.scatter(
    df,
    x='sales',
    y='profit',
    color='category',
    size='quantity',
    hover_data=['city', 'date'],
    facet_row='region',
    facet_col='year',
    trendline='ols',
    marginal_x='histogram',
    marginal_y='box',
    animation_frame='month',
    title='销售分析'
)
```

**Plotly Graph Objects（高级定制）**
```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['sales'],
    y=df['profit'],
    mode='markers',
    marker=dict(
        size=df['quantity'],
        color=df['category_code'],
        colorscale='Viridis',
        showscale=True
    ),
    text=df['city'],
    hovertemplate='<b>%{text}</b><br>Sales: %{x}<br>Profit: %{y}'
))
fig.update_layout(
    title='销售分析',
    xaxis_title='销售额',
    yaxis_title='利润',
    template='plotly_dark'
)
```

### 2. Seaborn支持

**基础图表**
```python
import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    data=df,
    x='sales',
    y='profit',
    hue='category',
    size='quantity',
    sizes=(20, 200),
    palette='viridis',
    ax=ax
)
ax.set_title('销售分析')
ax.set_xlabel('销售额')
ax.set_ylabel('利润')
plt.tight_layout()
```

**高级图表**
```python
# 分面图
g = sns.FacetGrid(df, col='region', row='year', hue='category')
g.map(sns.scatterplot, 'sales', 'profit')
g.add_legend()

# 联合分布图
g = sns.jointplot(
    data=df,
    x='sales',
    y='profit',
    kind='scatter',
    hue='category',
    marginal_kws=dict(bins=30)
)
```

## 🏗️ 后端架构设计

### 1. 图表服务重构

```python
# services/chart_service.py

from enum import Enum
from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

class ChartLibrary(Enum):
    """图表库枚举"""
    PLOTLY = "plotly"
    SEABORN = "seaborn"

class ChartType(Enum):
    """图表类型枚举"""
    SCATTER = "scatter"
    LINE = "line"
    BAR = "bar"
    HISTOGRAM = "histogram"
    BOX = "box"
    VIOLIN = "violin"
    HEATMAP = "heatmap"
    # ... 更多类型

class ChartService:
    """图表生成服务"""
    
    def __init__(self):
        self.library = ChartLibrary.PLOTLY  # 默认使用Plotly
        self.code_history = []
    
    def set_library(self, library: ChartLibrary):
        """切换图表库"""
        self.library = library
    
    def create_chart(
        self,
        df: pd.DataFrame,
        chart_type: ChartType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建图表
        
        Args:
            df: 数据框
            chart_type: 图表类型
            params: 完整的图表参数
        
        Returns:
            {
                'chart': 图表对象或base64字符串,
                'code': 生成的Python代码,
                'library': 使用的图表库
            }
        """
        if self.library == ChartLibrary.PLOTLY:
            return self._create_plotly_chart(df, chart_type, params)
        else:
            return self._create_seaborn_chart(df, chart_type, params)
    
    def _create_plotly_chart(
        self,
        df: pd.DataFrame,
        chart_type: ChartType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用Plotly创建图表"""
        
        # 生成代码
        code = self._generate_plotly_code(df, chart_type, params)
        
        # 执行代码生成图表
        fig = self._execute_plotly_code(df, chart_type, params)
        
        # 记录到历史
        self.code_history.append({
            'library': 'plotly',
            'type': chart_type.value,
            'code': code,
            'params': params
        })
        
        return {
            'chart': fig.to_json(),  # Plotly返回JSON
            'code': code,
            'library': 'plotly'
        }
    
    def _create_seaborn_chart(
        self,
        df: pd.DataFrame,
        chart_type: ChartType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用Seaborn创建图表"""
        
        # 生成代码
        code = self._generate_seaborn_code(df, chart_type, params)
        
        # 执行代码生成图表
        fig = self._execute_seaborn_code(df, chart_type, params)
        
        # 转换为base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        
        # 记录到历史
        self.code_history.append({
            'library': 'seaborn',
            'type': chart_type.value,
            'code': code,
            'params': params
        })
        
        return {
            'chart': f'data:image/png;base64,{img_base64}',  # Seaborn返回base64
            'code': code,
            'library': 'seaborn'
        }
```

### 2. 代码生成器

```python
# services/code_generator.py

class CodeGenerator:
    """Python代码生成器"""
    
    @staticmethod
    def generate_plotly_scatter(df_name: str, params: Dict[str, Any]) -> str:
        """生成Plotly散点图代码"""
        lines = [
            "import plotly.express as px",
            "import pandas as pd",
            "",
            f"# 创建散点图",
            f"fig = px.scatter(",
            f"    {df_name},"
        ]
        
        # 添加所有参数
        for key, value in params.items():
            if value is not None:
                if isinstance(value, str):
                    lines.append(f"    {key}='{value}',")
                elif isinstance(value, list):
                    lines.append(f"    {key}={value},")
                else:
                    lines.append(f"    {key}={value},")
        
        lines.append(")")
        lines.append("fig.show()")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_seaborn_scatter(df_name: str, params: Dict[str, Any]) -> str:
        """生成Seaborn散点图代码"""
        lines = [
            "import seaborn as sns",
            "import matplotlib.pyplot as plt",
            "import pandas as pd",
            "",
            f"# 创建散点图",
            f"fig, ax = plt.subplots(figsize=(10, 6))",
            f"sns.scatterplot(",
            f"    data={df_name},"
        ]
        
        # 添加所有参数
        for key, value in params.items():
            if value is not None:
                if isinstance(value, str):
                    lines.append(f"    {key}='{value}',")
                elif isinstance(value, tuple):
                    lines.append(f"    {key}={value},")
                else:
                    lines.append(f"    {key}={value},")
        
        lines.append("    ax=ax")
        lines.append(")")
        lines.append("plt.tight_layout()")
        lines.append("plt.show()")
        
        return "\n".join(lines)
```


## 🎨 前端UI设计

### 1. 图表库切换器

```python
# 顶部工具栏
html.Div([
    html.Label("图表库："),
    dcc.RadioItems(
        id='chart-library-selector',
        options=[
            {'label': '📊 Plotly（交互式）', 'value': 'plotly'},
            {'label': '📈 Seaborn（静态美化）', 'value': 'seaborn'}
        ],
        value='plotly',
        inline=True,
        className='library-selector'
    ),
    html.Div(id='library-info', className='library-info')
], className='library-switcher')
```

### 2. 参数配置面板（完整版）

**不再使用"维度/度量"的简化概念，而是直接使用Plotly/Seaborn的参数名**

```python
def create_plotly_params_panel(df: pd.DataFrame):
    """Plotly参数配置面板"""
    return html.Div([
        html.H6("Plotly Express 参数"),
        
        # 基础参数
        html.Div([
            html.Label("x (X轴)"),
            dcc.Dropdown(
                id='param-x',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择X轴字段'
            ),
        ]),
        
        html.Div([
            html.Label("y (Y轴)"),
            dcc.Dropdown(
                id='param-y',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择Y轴字段'
            ),
        ]),
        
        html.Div([
            html.Label("color (颜色分组)"),
            dcc.Dropdown(
                id='param-color',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择颜色字段（可选）',
                clearable=True
            ),
        ]),
        
        html.Div([
            html.Label("size (大小)"),
            dcc.Dropdown(
                id='param-size',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择大小字段（可选）',
                clearable=True
            ),
        ]),
        
        # 高级参数（可折叠）
        dbc.Collapse([
            html.H6("高级参数"),
            
            html.Div([
                html.Label("hover_data (悬停显示)"),
                dcc.Dropdown(
                    id='param-hover-data',
                    options=[{'label': col, 'value': col} for col in df.columns],
                    placeholder='选择悬停字段（可多选）',
                    multi=True
                ),
            ]),
            
            html.Div([
                html.Label("facet_row (分面行)"),
                dcc.Dropdown(
                    id='param-facet-row',
                    options=[{'label': col, 'value': col} for col in df.columns],
                    placeholder='选择分面行字段（可选）',
                    clearable=True
                ),
            ]),
            
            html.Div([
                html.Label("facet_col (分面列)"),
                dcc.Dropdown(
                    id='param-facet-col',
                    options=[{'label': col, 'value': col} for col in df.columns],
                    placeholder='选择分面列字段（可选）',
                    clearable=True
                ),
            ]),
            
            html.Div([
                html.Label("animation_frame (动画帧)"),
                dcc.Dropdown(
                    id='param-animation-frame',
                    options=[{'label': col, 'value': col} for col in df.columns],
                    placeholder='选择动画帧字段（可选）',
                    clearable=True
                ),
            ]),
            
            html.Div([
                html.Label("trendline (趋势线)"),
                dcc.Dropdown(
                    id='param-trendline',
                    options=[
                        {'label': 'OLS回归', 'value': 'ols'},
                        {'label': 'LOWESS平滑', 'value': 'lowess'},
                        {'label': '无', 'value': None}
                    ],
                    placeholder='选择趋势线类型（可选）',
                    clearable=True
                ),
            ]),
            
            html.Div([
                html.Label("marginal_x (X轴边际图)"),
                dcc.Dropdown(
                    id='param-marginal-x',
                    options=[
                        {'label': '直方图', 'value': 'histogram'},
                        {'label': '箱线图', 'value': 'box'},
                        {'label': '小提琴图', 'value': 'violin'},
                        {'label': '无', 'value': None}
                    ],
                    placeholder='选择X轴边际图（可选）',
                    clearable=True
                ),
            ]),
            
            html.Div([
                html.Label("marginal_y (Y轴边际图)"),
                dcc.Dropdown(
                    id='param-marginal-y',
                    options=[
                        {'label': '直方图', 'value': 'histogram'},
                        {'label': '箱线图', 'value': 'box'},
                        {'label': '小提琴图', 'value': 'violin'},
                        {'label': '无', 'value': None}
                    ],
                    placeholder='选择Y轴边际图（可选）',
                    clearable=True
                ),
            ]),
            
        ], id='advanced-params-collapse'),
        
        dbc.Button(
            "展开高级参数",
            id='toggle-advanced-params',
            size='sm',
            className='mt-2'
        ),
        
    ], className='params-panel')


def create_seaborn_params_panel(df: pd.DataFrame):
    """Seaborn参数配置面板"""
    return html.Div([
        html.H6("Seaborn 参数"),
        
        # 基础参数
        html.Div([
            html.Label("x (X轴)"),
            dcc.Dropdown(
                id='param-x',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择X轴字段'
            ),
        ]),
        
        html.Div([
            html.Label("y (Y轴)"),
            dcc.Dropdown(
                id='param-y',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择Y轴字段'
            ),
        ]),
        
        html.Div([
            html.Label("hue (颜色分组)"),
            dcc.Dropdown(
                id='param-hue',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择颜色字段（可选）',
                clearable=True
            ),
        ]),
        
        html.Div([
            html.Label("size (大小)"),
            dcc.Dropdown(
                id='param-size',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择大小字段（可选）',
                clearable=True
            ),
        ]),
        
        html.Div([
            html.Label("style (样式)"),
            dcc.Dropdown(
                id='param-style',
                options=[{'label': col, 'value': col} for col in df.columns],
                placeholder='选择样式字段（可选）',
                clearable=True
            ),
        ]),
        
        # Seaborn特有参数
        html.Div([
            html.Label("palette (调色板)"),
            dcc.Dropdown(
                id='param-palette',
                options=[
                    {'label': 'deep', 'value': 'deep'},
                    {'label': 'muted', 'value': 'muted'},
                    {'label': 'pastel', 'value': 'pastel'},
                    {'label': 'bright', 'value': 'bright'},
                    {'label': 'dark', 'value': 'dark'},
                    {'label': 'colorblind', 'value': 'colorblind'},
                    {'label': 'viridis', 'value': 'viridis'},
                    {'label': 'plasma', 'value': 'plasma'},
                ],
                value='deep',
                clearable=False
            ),
        ]),
        
        html.Div([
            html.Label("sizes (大小范围)"),
            dcc.RangeSlider(
                id='param-sizes',
                min=10,
                max=500,
                step=10,
                value=[20, 200],
                marks={10: '10', 100: '100', 200: '200', 500: '500'}
            ),
        ]),
        
    ], className='params-panel')
```

### 3. 代码预览面板

```python
def create_code_preview_panel():
    """代码预览和导出面板"""
    return html.Div([
        html.Div([
            html.H6("生成的Python代码"),
            dbc.ButtonGroup([
                dbc.Button("📋 复制代码", id='copy-code-btn', size='sm', color='primary'),
                dbc.Button("💾 下载.py", id='download-py-btn', size='sm', color='secondary'),
                dbc.Button("📓 导出Jupyter", id='export-jupyter-btn', size='sm', color='info'),
            ]),
        ], className='code-header'),
        
        dcc.Textarea(
            id='generated-code-display',
            readOnly=True,
            style={
                'width': '100%',
                'height': '400px',
                'fontFamily': 'JetBrains Mono, Consolas, monospace',
                'fontSize': '13px',
                'backgroundColor': '#1e1e1e',
                'color': '#d4d4d4',
                'padding': '16px',
                'border': '1px solid #333',
                'borderRadius': '8px',
                'lineHeight': '1.6'
            }
        ),
        
        dcc.Download(id='download-code-file'),
        
    ], className='code-preview-panel')
```

### 4. 图表显示区

```python
def create_chart_display():
    """图表显示区"""
    return html.Div([
        html.Div(id='chart-container', children=[
            html.Div([
                html.P("👈 配置参数后，图表将在这里显示", 
                       className='placeholder-text')
            ], className='chart-placeholder')
        ]),
    ], className='chart-display-area')
```


## 🔄 完整的回调逻辑

### 1. 图表库切换回调

```python
@app.callback(
    Output('params-panel-container', 'children'),
    Output('library-info', 'children'),
    Input('chart-library-selector', 'value'),
    State('data-store', 'data')
)
def switch_library(library, data_store):
    """切换图表库时更新参数面板"""
    if data_store is None or 'active_df' not in data_store:
        return html.Div("请先加载数据"), ""
    
    df = pd.DataFrame(data_store['active_df'])
    
    if library == 'plotly':
        params_panel = create_plotly_params_panel(df)
        info = "Plotly：交互式图表，支持缩放、悬停、动画等功能"
    else:
        params_panel = create_seaborn_params_panel(df)
        info = "Seaborn：静态图表，更美观的默认样式，适合出版和报告"
    
    return params_panel, info
```

### 2. 图表生成回调

```python
@app.callback(
    Output('chart-container', 'children'),
    Output('generated-code-display', 'value'),
    Input('chart-type-selector', 'value'),
    Input('param-x', 'value'),
    Input('param-y', 'value'),
    Input('param-color', 'value'),
    Input('param-size', 'value'),
    Input('param-hover-data', 'value'),
    Input('param-facet-row', 'value'),
    Input('param-facet-col', 'value'),
    Input('param-animation-frame', 'value'),
    Input('param-trendline', 'value'),
    Input('param-marginal-x', 'value'),
    Input('param-marginal-y', 'value'),
    State('chart-library-selector', 'value'),
    State('data-store', 'data'),
    prevent_initial_call=True
)
def generate_chart(
    chart_type, x, y, color, size, hover_data,
    facet_row, facet_col, animation_frame,
    trendline, marginal_x, marginal_y,
    library, data_store
):
    """生成图表"""
    
    if data_store is None or 'active_df' not in data_store:
        return html.Div("请先加载数据"), ""
    
    if not x or not y:
        return html.Div("请至少选择X轴和Y轴"), ""
    
    # 获取数据
    df = pd.DataFrame(data_store['active_df'])
    
    # 构建参数字典
    params = {
        'x': x,
        'y': y,
        'color': color,
        'size': size,
        'hover_data': hover_data,
        'facet_row': facet_row,
        'facet_col': facet_col,
        'animation_frame': animation_frame,
        'trendline': trendline,
        'marginal_x': marginal_x,
        'marginal_y': marginal_y,
    }
    
    # 移除None值
    params = {k: v for k, v in params.items() if v is not None}
    
    # 调用图表服务
    chart_service = ChartService()
    chart_service.set_library(ChartLibrary(library))
    
    result = chart_service.create_chart(
        df=df,
        chart_type=ChartType(chart_type),
        params=params
    )
    
    # 显示图表
    if library == 'plotly':
        chart_component = dcc.Graph(
            figure=result['chart'],
            config={'displayModeBar': True, 'displaylogo': False},
            style={'height': '600px'}
        )
    else:  # seaborn
        chart_component = html.Img(
            src=result['chart'],
            style={'width': '100%', 'maxHeight': '600px', 'objectFit': 'contain'}
        )
    
    return chart_component, result['code']
```

### 3. 代码导出回调

```python
@app.callback(
    Output('download-code-file', 'data'),
    Input('download-py-btn', 'n_clicks'),
    State('generated-code-display', 'value'),
    prevent_initial_call=True
)
def download_code(n_clicks, code):
    """下载Python代码"""
    if not code:
        return None
    
    return dict(
        content=code,
        filename='chart_code.py'
    )


@app.callback(
    Output('copy-code-btn', 'children'),
    Input('copy-code-btn', 'n_clicks'),
    State('generated-code-display', 'value'),
    prevent_initial_call=True
)
def copy_code(n_clicks, code):
    """复制代码到剪贴板"""
    if not code:
        return "📋 复制代码"
    
    # 使用clientside callback实现真正的复制
    # 这里只是UI反馈
    return "✅ 已复制"


# Clientside callback for actual clipboard copy
app.clientside_callback(
    """
    function(n_clicks, code) {
        if (n_clicks && code) {
            navigator.clipboard.writeText(code);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('copy-code-btn', 'n_clicks'),
    Input('copy-code-btn', 'n_clicks'),
    State('generated-code-display', 'value'),
    prevent_initial_call=True
)
```

## 📦 完整的图表类型支持

### Plotly图表类型映射

```python
PLOTLY_CHART_TYPES = {
    'scatter': px.scatter,
    'line': px.line,
    'bar': px.bar,
    'histogram': px.histogram,
    'box': px.box,
    'violin': px.violin,
    'strip': px.strip,
    'scatter_3d': px.scatter_3d,
    'line_3d': px.line_3d,
    'scatter_matrix': px.scatter_matrix,
    'parallel_coordinates': px.parallel_coordinates,
    'parallel_categories': px.parallel_categories,
    'pie': px.pie,
    'sunburst': px.sunburst,
    'treemap': px.treemap,
    'funnel': px.funnel,
    'density_heatmap': px.density_heatmap,
    'density_contour': px.density_contour,
}
```

### Seaborn图表类型映射

```python
SEABORN_CHART_TYPES = {
    'scatter': sns.scatterplot,
    'line': sns.lineplot,
    'bar': sns.barplot,
    'histogram': sns.histplot,
    'box': sns.boxplot,
    'violin': sns.violinplot,
    'strip': sns.stripplot,
    'swarm': sns.swarmplot,
    'kde': sns.kdeplot,
    'heatmap': sns.heatmap,
    'clustermap': sns.clustermap,
    'pairplot': sns.pairplot,
    'jointplot': sns.jointplot,
    'regplot': sns.regplot,
    'lmplot': sns.lmplot,
}
```

## 🚀 实现路线图

### Phase 1: 核心架构重构（1周）
- [ ] 重写 `services/chart_service.py`
  - [ ] 添加 `ChartLibrary` 枚举
  - [ ] 实现 `_create_plotly_chart` 方法
  - [ ] 实现 `_create_seaborn_chart` 方法
  - [ ] 实现图表库切换逻辑

- [ ] 重写 `services/code_generator.py`
  - [ ] 实现 Plotly 代码生成
  - [ ] 实现 Seaborn 代码生成
  - [ ] 支持完整参数

- [ ] 更新 `pages/chart_studio.py`
  - [ ] 添加图表库切换器
  - [ ] 创建 Plotly 参数面板
  - [ ] 创建 Seaborn 参数面板
  - [ ] 添加代码预览面板
  - [ ] 移除拖拽功能，改用下拉选择

### Phase 2: 参数支持（1周）
- [ ] Plotly 完整参数支持
  - [ ] 基础参数：x, y, color, size
  - [ ] 高级参数：hover_data, facet_row, facet_col, animation_frame
  - [ ] 增强参数：trendline, marginal_x, marginal_y
  - [ ] 样式参数：title, labels, color_discrete_sequence

- [ ] Seaborn 完整参数支持
  - [ ] 基础参数：x, y, hue, size, style
  - [ ] 样式参数：palette, sizes, markers
  - [ ] 图表特定参数：kind, diag_kind, corner

### Phase 3: 代码导出（3天）
- [ ] 代码复制功能
- [ ] .py 文件下载
- [ ] Jupyter Notebook 导出
- [ ] 代码历史记录
- [ ] 代码模板系统

### Phase 4: 测试和优化（3天）
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 文档完善

## 📝 使用示例

### 用户操作流程

1. **选择图表库**
   - 用户点击 "Plotly" 或 "Seaborn"
   - 参数面板自动切换

2. **配置参数**
   - 从下拉菜单选择字段
   - 配置高级参数（可选）
   - 实时预览图表

3. **查看代码**
   - 代码预览区实时显示生成的Python代码
   - 可以直接复制或下载

4. **导出使用**
   - 下载 .py 文件
   - 在本地Python环境运行
   - 或导出为Jupyter Notebook

### 生成的代码示例

**Plotly示例**
```python
import plotly.express as px
import pandas as pd

# 加载数据
df = pd.read_csv('sales_data.csv')

# 创建散点图
fig = px.scatter(
    df,
    x='sales',
    y='profit',
    color='category',
    size='quantity',
    hover_data=['city', 'date'],
    facet_col='region',
    trendline='ols',
    marginal_x='histogram',
    marginal_y='box',
    title='销售分析',
    labels={'sales': '销售额', 'profit': '利润'}
)

fig.show()

# 保存图表
fig.write_html('chart.html')
fig.write_image('chart.png')
```

**Seaborn示例**
```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# 加载数据
df = pd.read_csv('sales_data.csv')

# 创建散点图
fig, ax = plt.subplots(figsize=(12, 8))
sns.scatterplot(
    data=df,
    x='sales',
    y='profit',
    hue='category',
    size='quantity',
    sizes=(20, 200),
    palette='viridis',
    ax=ax
)

ax.set_title('销售分析', fontsize=16)
ax.set_xlabel('销售额', fontsize=12)
ax.set_ylabel('利润', fontsize=12)
plt.tight_layout()
plt.show()

# 保存图表
plt.savefig('chart.png', dpi=300, bbox_inches='tight')
```

## ✅ 核心改进总结

### 之前的问题
1. ❌ 使用简化的"维度/度量"概念
2. ❌ 拖拽功能不可靠
3. ❌ 只支持Plotly
4. ❌ 参数不完整
5. ❌ 没有代码导出

### 现在的解决方案
1. ✅ 使用完整的Plotly/Seaborn参数名
2. ✅ 使用下拉选择器（更可靠）
3. ✅ 支持Plotly和Seaborn切换
4. ✅ 支持完整的API参数
5. ✅ 实时代码预览和导出

---

**这才是真正的可视化Python数据分析平台！**
