# DataViz Studio

[中文](./README.md) | [English](./README_EN.md)

一个面向数据分析师、数据科学家与业务团队的本地化 Python 低代码数据分析工作台。  
项目基于 Dash、pandas、Plotly 和 scikit-learn，覆盖数据导入、EDA、数据清洗、统计分析、可视化分析、机器学习，以及项目与代码导出。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14+-green.svg)](https://dash.plotly.com/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-orange.svg)](https://plotly.com/)
[![Version](https://img.shields.io/badge/version-0.4.0-success.svg)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 最新版本

### v0.4.0 · 2026-03-09

最近一个正式版本记录见 [CHANGELOG.md](/Users/Toxic/Desktop/python/python项目DataViz%20Studio/CHANGELOG.md)。

- Data Workshop 重构，改为更适合步骤化清洗的操作流。
- ML Studio 增强，补充时序分析、交互式推断和批量预测能力。
- Chart Studio 增加参数校验和多类图表交互修复。
- 修复 DataTable、Seaborn 渲染和全局通知等一批稳定性问题。

### main 分支当前还包含的近期增强

- 顶栏支持“打开项目 / 保存项目”，可导入导出 `.dvs` 项目文件。
- 项目重新打开后，可恢复当前路由、数据集、页面状态和部分分析上下文。
- Chart Studio、Data Workshop、Advanced Tools 统一支持导出 `.py` 和 `.ipynb`。
- ML Studio 主界面补充中文流程引导、算法适用场景和下一步提示，降低上手门槛。
- Chart Studio 推荐卡片直接展示推荐理由与适用场景，常见 `城市 -> 销售额`、`日期 -> 销售额` 场景推荐更稳定。
- 顶栏增加系统状态、Python 版本、数据集徽标和快捷操作入口。
- 运行依赖补全，包含 `requests`、`scipy`、`scikit-learn`、`sqlalchemy`、`kaleido`。

## 产品预览

| 首页 / 数据总览 | Data Workshop |
| --- | --- |
| ![Home](./assets/screenshots/showcase_home.png) | ![Workshop](./assets/screenshots/showcase_workshop.png) |
| Chart Studio | ML Studio |
| ![Charts](./assets/screenshots/showcase_charts.png) | ![ML](./assets/screenshots/showcase_ml.webp) |

## 按导航区查看功能

### 首页

- 作为工作台入口，汇总主要模块与快捷导航。
- 适合首次进入项目时快速了解当前可用能力。

### 数据中心

- 导入 CSV、Excel、JSON、Parquet、Feather 等数据文件。
- 支持本地文件、示例数据，以及基于引用的项目恢复。
- 管理多数据集和当前活跃数据集。

### 数据画布

- 提供 EDA 入口、字段结构浏览、导出和分析报告操作。
- 适合快速完成数据质量检查和探索式分析。

### 数据工坊

- 通过可视化步骤完成筛选、排序、缺失值处理、去重、重命名等清洗操作。
- 支持步骤预览、撤销 / 重做和数据导出。
- 支持将处理流程导出为 Python 脚本和 Jupyter Notebook。

### 图表工作室

- 支持 Plotly 与 Seaborn 双引擎。
- 提供图表参数配置、实时预览以及 PNG / HTML 导出；SVG 导出目前仅适用于 Plotly 图表，Seaborn 静态图会明确提示改用 PNG。
- 统一支持代码导出和 Notebook 导出。

### 统计实验室

- 提供描述统计、相关性分析、分组汇总和常见统计检验。
- 适合快速完成基础统计验证和结果查看。

### 机器学习

- 覆盖分类、回归、聚类和时序相关分析流程。
- 支持保存部分页面状态到项目文件，方便继续分析。

### 高级工具

- 聚合当前项目上下文，统一导出分析流水线。
- 适合把交互式分析结果整理为脚本化交付物。

## 顶栏与项目工作流

### 顶栏能力

- 打开项目
- 保存项目
- 系统状态
- Python 版本显示
- 当前数据集徽标
- 快捷操作入口

### 项目文件 `.dvs`

- 支持 `embedded` 和 `reference` 两种保存模式。
- `embedded` 会把数据一并写入项目文件，适合迁移和归档。
- `reference` 会优先保留原始来源引用，适合减小项目体积。

### 项目恢复

- 重新打开项目时，可恢复路由、数据集、应用状态和部分页面状态。
- 当前 Chart Studio、Data Workshop、ML Studio 已接入这套状态恢复机制。

## 技术栈

- Python 3.9+
- Dash
- Plotly
- pandas
- NumPy
- Seaborn / Matplotlib
- SciPy
- scikit-learn
- SQLAlchemy
- Dash Bootstrap Components
- Dash AG Grid

## 安装

```bash
git clone https://github.com/wsyh4567/DATAVIZ-STUDIO.git
cd DATAVIZ-STUDIO
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 启动

```bash
python app.py
```

默认地址：

```text
http://127.0.0.1:8050
```

## 目录结构

```text
app.py                    Dash 应用入口
components/               顶栏、侧栏、状态栏等复用组件
core/                     数据与状态管理
pages/                    各导航页面
services/                 导入、导出、统计、项目持久化等服务
assets/                   静态资源与截图
tests/                    测试
```

## 适合谁使用

- 需要在本地环境完成分析工作的数据科学家
- 希望用 GUI 加速 pandas / Plotly 工作流的数据分析师
- 需要把交互分析结果导出为 Python 脚本或 Notebook 的团队
- 对数据隐私、本地运行和可复现性有要求的项目

## 当前限制

- 仍以单机本地分析为主，不是多用户协作平台。
- 大数据量场景下仍依赖 pandas 内存模型。
- Plotly 静态图导出依赖 `kaleido`；缺少该依赖时仍可导出 HTML，但 PNG / SVG 会提示不可用。
- 部分模块测试覆盖率仍有提升空间。
- 当前文档以快速上手为主，尚未覆盖所有页面细节。

## 开发说明

运行测试：

```bash
pytest
```

只验证 Data Workshop 核心执行器：

```bash
pytest tests/data_workshop/test_operation_executor.py
```

## License

MIT
