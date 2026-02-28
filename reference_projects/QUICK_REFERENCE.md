# 快速参考指南

## D-Tale 关键代码位置

### 后端架构
```
dtale/
├── app.py                    # Flask 应用入口
├── views.py                  # API 路由和视图
├── global_state.py           # 全局状态管理
├── cli/                      # 命令行接口
│   └── loaders.py           # 数据加载器
├── dash_application/         # Dash 组件
│   ├── layout.py            # 布局定义
│   ├── charts.py            # 图表组件
│   └── custom_geojson.py    # 地图组件
└── query.py                  # 数据查询逻辑
```

### 前端架构
```
frontend/
├── static/
│   ├── dtale/               # React 应用
│   │   ├── DataViewer.jsx   # 数据查看器
│   │   ├── menu/            # 菜单组件
│   │   ├── side/            # 侧边栏
│   │   └── popups/          # 弹出窗口
│   └── dash/                # Dash 组件
└── package.json
```

### 核心功能实现

**1. 数据表格 (DataViewer.jsx)**
- 虚拟滚动
- 列排序和筛选
- 单元格编辑
- 上下文菜单

**2. 列操作 (views.py)**
```python
# 删除列
@app.route('/dtale/delete-col/<data_id>')
def delete_col(data_id):
    # 实现逻辑

# 重命名列
@app.route('/dtale/rename-col/<data_id>')
def rename_col(data_id):
    # 实现逻辑
```

**3. 图表生成 (charts.py)**
```python
def build_chart(data_id, **inputs):
    # 根据参数生成 Plotly 图表
    chart_type = inputs.get('chart_type')
    x = inputs.get('x')
    y = inputs.get('y')
    # ...
```

---

## PyGWalker 关键代码位置

### 后端架构
```
pygwalker/
├── api/                      # Python API
│   ├── pygwalker.py         # 主入口
│   └── jupyter.py           # Jupyter 集成
├── services/                 # 核心服务
│   ├── data_parsers.py      # 数据解析
│   ├── spec.py              # 图表规范
│   └── render.py            # 渲染逻辑
├── data_parsers/            # 数据源解析器
│   ├── pandas_parser.py     # Pandas 支持
│   └── polars_parser.py     # Polars 支持
└── utils/                   # 工具函数
```

### 前端架构
```
app/
├── src/
│   ├── components/          # React 组件
│   │   ├── dataTable/       # 数据表格
│   │   ├── fieldPane/       # 字段面板
│   │   └── visualPane/      # 可视化面板
│   ├── store/               # 状态管理
│   └── utils/               # 工具函数
└── package.json
```

### 核心功能实现

**1. 字段识别 (data_parsers.py)**
```python
def infer_semantic_type(series):
    """推断字段的语义类型（维度/度量）"""
    if is_numeric_dtype(series):
        return "quantitative"
    elif is_datetime64_any_dtype(series):
        return "temporal"
    else:
        return "nominal"
```

**2. 拖拽交互 (fieldPane/)**
- 字段列表渲染
- 拖拽事件处理
- 放置区域验证

**3. 图表规范 (spec.py)**
```python
def build_vega_spec(data, encoding):
    """构建 Vega-Lite 规范"""
    spec = {
        "data": {"values": data},
        "mark": encoding.get("mark"),
        "encoding": {
            "x": encoding.get("x"),
            "y": encoding.get("y"),
            # ...
        }
    }
    return spec
```

---

## 对比分析

### 架构对比

| 特性 | D-Tale | PyGWalker | DataViz Studio |
|------|--------|-----------|----------------|
| 后端框架 | Flask | FastAPI | Dash |
| 前端框架 | React | React | Dash Components |
| 图表库 | Plotly | Vega-Lite | Plotly + Seaborn |
| 数据处理 | Pandas | Pandas/Polars | Pandas |
| 交互方式 | 菜单驱动 | 拖拽驱动 | 下拉选择 |

### 功能对比

| 功能 | D-Tale | PyGWalker | DataViz Studio |
|------|--------|-----------|----------------|
| 数据清洗 | ✅ 强大 | ❌ 无 | ✅ 完整 |
| 图表类型 | ✅ 丰富 | ✅ 丰富 | ✅ 双库支持 |
| 代码导出 | ✅ 有 | ❌ 无 | ✅ 实时生成 |
| 拖拽交互 | ❌ 无 | ✅ 核心 | ❌ 无 |
| 统计分析 | ✅ 有 | ✅ 有 | ✅ 计划中 |

---

## 学习路径建议

### 第一周：D-Tale
1. **Day 1-2**: 浏览整体架构
   - 阅读 `app.py` 和 `views.py`
   - 理解路由和 API 设计
   
2. **Day 3-4**: 数据清洗功能
   - 研究 `dtale/column_builders.py`
   - 学习列操作实现
   
3. **Day 5-7**: 图表生成
   - 分析 `dash_application/charts.py`
   - 理解参数到图表的转换

### 第二周：PyGWalker
1. **Day 1-2**: 数据解析
   - 研究 `data_parsers/pandas_parser.py`
   - 学习字段类型推断
   
2. **Day 3-4**: 拖拽交互
   - 查看前端 `fieldPane` 组件
   - 理解拖拽事件处理
   
3. **Day 5-7**: 图表规范
   - 分析 `services/spec.py`
   - 学习 Vega-Lite 规范

### 第三周：应用到 DataViz Studio
1. **Day 1-3**: 改进数据清洗
   - 参考 D-Tale 的列操作
   - 优化工作流设计
   
2. **Day 4-5**: 增强图表配置
   - 借鉴 PyGWalker 的字段识别
   - 改进参数面板
   
3. **Day 6-7**: 代码生成优化
   - 参考 D-Tale 的代码导出
   - 完善代码模板

---

## 关键代码片段

### D-Tale: 数据筛选
```python
# dtale/views.py
@app.route('/dtale/filter/<data_id>')
def filter_data(data_id):
    query = request.args.get('query')
    data = global_state.get_data(data_id)
    
    if query:
        filtered = data.query(query)
        return jsonify(success=True, data=filtered.to_dict())
    
    return jsonify(success=False)
```

### PyGWalker: 字段推断
```python
# pygwalker/data_parsers/pandas_parser.py
def get_field_meta(df):
    fields = []
    for col in df.columns:
        field = {
            "name": col,
            "type": infer_semantic_type(df[col]),
            "analyticType": infer_analytic_type(df[col])
        }
        fields.append(field)
    return fields
```

### DataViz Studio: 图表生成
```python
# services/chart_service.py
def create_chart(df, chart_type, params):
    if chart_type == ChartType.scatter:
        fig = px.scatter(df, **params)
    elif chart_type == ChartType.line:
        fig = px.line(df, **params)
    # ...
    return fig.to_json()
```

---

## 实用技巧

### 1. 快速查找功能实现
```bash
# 在 D-Tale 中查找列删除功能
grep -r "delete.*col" dtale/

# 在 PyGWalker 中查找拖拽逻辑
grep -r "drag" app/src/
```

### 2. 运行本地示例
```python
# D-Tale 示例
import dtale
import pandas as pd

df = pd.DataFrame({
    'x': range(10),
    'y': range(10, 20)
})
dtale.show(df).open_browser()

# PyGWalker 示例
import pygwalker as pyg
pyg.walk(df)
```

### 3. 调试技巧
- 使用浏览器开发者工具查看网络请求
- 在 Python 代码中添加 `print()` 或 `logging`
- 使用 React DevTools 查看组件状态

---

**更新日期**: 2026-02-26  
**用途**: 快速定位和学习参考项目的关键代码
