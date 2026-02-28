# 参考项目

本文件夹包含用于学习和参考的开源数据可视化项目。

## 项目列表

### 1. D-Tale
- **仓库**: https://github.com/man-group/dtale
- **描述**: 基于 Flask 和 React 的交互式数据分析和可视化工具
- **技术栈**: Python (Flask, Pandas), React, Plotly
- **特点**:
  - 强大的数据探索功能
  - 内置数据清洗工具
  - 丰富的图表类型
  - 代码导出功能
  - 列操作和数据转换

**学习重点**:
- 数据表格交互设计
- 数据清洗工作流
- 图表配置界面
- Python 后端架构
- 代码生成逻辑

---

### 2. PyGWalker
- **仓库**: https://github.com/Kanaries/pygwalker
- **描述**: 将 Pandas/Polars DataFrame 转换为 Tableau 风格的可视化界面
- **技术栈**: Python, TypeScript, React
- **特点**:
  - 拖拽式图表构建
  - 类 Tableau 的用户体验
  - 支持 Jupyter Notebook
  - 自动数据类型推断
  - 丰富的图表类型

**学习重点**:
- 拖拽交互设计
- 字段面板布局
- 图表类型自动推荐
- 数据类型处理
- 可视化最佳实践

---

## 如何使用这些参考项目

### 1. 浏览代码结构
```bash
# D-Tale 项目结构
cd dtale
tree -L 2

# PyGWalker 项目结构
cd pygwalker
tree -L 2
```

### 2. 查看关键文件

**D-Tale 关键文件**:
- `dtale/app.py` - Flask 应用主文件
- `dtale/views.py` - 视图和路由
- `dtale/dash_application/` - Dash 组件
- `static/` - 前端资源

**PyGWalker 关键文件**:
- `pygwalker/api/` - Python API
- `pygwalker/services/` - 核心服务
- `app/` - 前端应用

### 3. 运行示例

**D-Tale**:
```python
import dtale
import pandas as pd

df = pd.read_csv('data.csv')
d = dtale.show(df)
d.open_browser()
```

**PyGWalker**:
```python
import pygwalker as pyg
import pandas as pd

df = pd.read_csv('data.csv')
walker = pyg.walk(df)
```

---

## 对 DataViz Studio 的启发

### 从 D-Tale 学习
1. **数据清洗工作流**
   - 列操作（删除、重命名、拆分、合并）
   - 缺失值处理
   - 数据类型转换
   - 筛选和排序

2. **代码导出功能**
   - 生成可执行的 Python 代码
   - 包含所有操作步骤
   - 支持复制和下载

3. **UI/UX 设计**
   - 清晰的操作菜单
   - 实时数据预览
   - 操作历史记录

### 从 PyGWalker 学习
1. **拖拽交互**
   - 字段面板设计
   - 拖拽区域布局
   - 视觉反馈

2. **图表配置**
   - 自动类型推断
   - 智能图表推荐
   - 参数面板设计

3. **数据处理**
   - 维度和度量识别
   - 聚合函数支持
   - 数据转换

---

## 注意事项

1. **许可证**
   - D-Tale: LGPL-2.1 License
   - PyGWalker: Apache-2.0 License
   - 请遵守各项目的许可证要求

2. **仅供参考**
   - 这些项目仅用于学习和参考
   - 不要直接复制代码
   - 理解设计思路和实现方式

3. **版本更新**
   - 定期拉取最新代码
   - 关注新功能和改进
   - 学习最佳实践

---

## 更新参考项目

```bash
# 更新 D-Tale
cd reference_projects/dtale
git pull origin master

# 更新 PyGWalker
cd reference_projects/pygwalker
git pull origin main
```

---

## 相关资源

### D-Tale
- 文档: https://dtale.readthedocs.io/
- 演示: https://alphatechadmin.pythonanywhere.com/
- 视频: https://www.youtube.com/watch?v=0RlPPYQQdKo

### PyGWalker
- 文档: https://docs.kanaries.net/pygwalker
- 演示: https://kanaries.net/pygwalker
- GitHub: https://github.com/Kanaries/pygwalker

---

**创建日期**: 2026-02-26  
**用途**: 学习和参考优秀的数据可视化项目
