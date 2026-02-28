# Phase 2 重构指南 — Python 优先架构

## 🎯 重构目标

将图表工作室从拖拽式架构重构为 Python 优先架构，实现真正的"可视化 Python 数据分析平台"。

## ✅ 已完成的工作

### 1. 后端服务重构

#### `services/chart_service.py`
- ✅ 添加 `ChartLibrary` 枚举（Plotly/Seaborn）
- ✅ 添加 `ChartType` 枚举
- ✅ 实现 `ChartService` 类
- ✅ 实现 `_create_plotly_chart()` 方法
- ✅ 实现 `_create_seaborn_chart()` 方法
- ✅ 支持完整的 Plotly Express 参数
- ✅ 支持 Seaborn 基础参数
- ✅ Plotly 返回 JSON，Seaborn 返回 base64 图片

#### `services/code_generator.py`
- ✅ 实现 `CodeGenerator` 类
- ✅ 实现 `generate_plotly_code()` 方法
- ✅ 实现 `generate_seaborn_code()` 方法
- ✅ 生成完整可执行的 Python 代码
- ✅ 包含导入语句、数据加载、图表创建、保存

### 2. 前端组件

#### `components/code_preview.py`
- ✅ 创建代码预览面板组件
- ✅ 代码显示区域（Textarea）
- ✅ 复制代码按钮
- ✅ 下载 .py 文件按钮
- ✅ 导出 Jupyter Notebook 按钮（UI）
- ✅ Toast 通知

#### `pages/chart_studio_new.py`
- ✅ 创建新的图表工作室页面
- ✅ 图表库切换器（Plotly/Seaborn）
- ✅ Plotly 参数配置面板（基础 + 高级）
- ✅ Seaborn 参数配置面板
- ✅ 图表画布
- ✅ 代码预览面板集成
- ✅ 所有回调函数

#### `assets/js/clipboard.js`
- ✅ 客户端复制到剪贴板功能

### 3. 依赖更新

#### `requirements.txt`
- ✅ 添加 seaborn>=0.12
- ✅ 添加 matplotlib>=3.7

### 4. 测试文件

#### `test_chart_studio_new.py`
- ✅ Plotly 图表生成测试
- ✅ Seaborn 图表生成测试
- ✅ 代码生成测试

## 🔧 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
python test_chart_studio_new.py
```

### 3. 启动应用

```bash
python app.py
```

### 4. 使用新的图表工作室

1. 在数据中心加载数据
2. 进入图表工作室
3. 选择图表库（Plotly 或 Seaborn）
4. 选择图表类型
5. 配置参数（使用下拉选择器）
6. 查看生成的图表和代码
7. 复制或下载代码

## 📊 支持的图表类型

### Plotly
- scatter（散点图）
- line（折线图）
- bar（柱状图）
- histogram（直方图）
- box（箱线图）
- violin（小提琴图）
- scatter_3d（3D散点图）
- pie（饼图）
- sunburst（旭日图）
- treemap（矩形树图）
- funnel（漏斗图）
- density_heatmap（密度热力图）

### Seaborn
- scatter（散点图）
- line（折线图）
- bar（柱状图）
- histogram（直方图）
- box（箱线图）
- violin（小提琴图）
- heatmap（热力图）

## 🎨 参数支持

### Plotly 参数
- **基础参数**：x, y, color, size
- **高级参数**：hover_data, facet_row, facet_col, animation_frame
- **增强参数**：trendline, marginal_x, marginal_y

### Seaborn 参数
- **基础参数**：x, y, hue, size, style
- **样式参数**：palette

## 📝 生成的代码示例

### Plotly 代码
```python
# ==================================================
# DataViz Studio 自动生成代码
# 生成时间: 2024-01-01 12:00:00
# ==================================================

import pandas as pd
import plotly.express as px

# 1. 加载数据
# df = pd.read_csv('your_data.csv')

# 2. 创建散点图
fig = px.scatter(
    df,
    x='sales',
    y='profit',
    color='category',
    size='quantity',
    hover_data=['city'],
    trendline='ols',
)

# 3. 显示图表
fig.show()

# 4. 保存图表（可选）
# fig.write_html('chart.html')
# fig.write_image('chart.png')
```

### Seaborn 代码
```python
# ==================================================
# DataViz Studio 自动生成代码
# 生成时间: 2024-01-01 12:00:00
# ==================================================

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 加载数据
# df = pd.read_csv('your_data.csv')

# 2. 创建散点图
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    data=df,
    x='sales',
    y='profit',
    hue='category',
    size='quantity',
    ax=ax
)

# 3. 设置标题和标签（可选）
# ax.set_title('图表标题', fontsize=16)
# ax.set_xlabel('X轴标签', fontsize=12)
# ax.set_ylabel('Y轴标签', fontsize=12)

plt.tight_layout()
plt.show()

# 4. 保存图表（可选）
# plt.savefig('chart.png', dpi=300, bbox_inches='tight')
```

## 🚀 下一步工作

### 待完成功能
- [ ] Jupyter Notebook 导出功能实现
- [ ] 更多图表类型支持
- [ ] 参数验证和错误提示
- [ ] 图表保存和管理
- [ ] 代码历史记录
- [ ] 代码模板系统

### 集成到主应用
- [ ] 将 `chart_studio_new.py` 替换 `chart_studio.py`
- [ ] 更新路由配置
- [ ] 更新导航链接
- [ ] 删除旧的拖拽相关文件

## 📚 参考文档

- [Plotly Express API](https://plotly.com/python-api-reference/plotly.express.html)
- [Seaborn API](https://seaborn.pydata.org/api.html)
- [Python 优先架构设计](./PYTHON_FIRST_ARCHITECTURE.md)

---

**重构完成时间**：2024年
**重构原因**：拖拽功能不可靠，参数过于简化，缺少代码导出功能
**核心改进**：Python 后端生成图表，完整 API 参数，实时代码预览和导出
