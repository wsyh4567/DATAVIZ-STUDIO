# DataViz Studio 快速上手

本指南面向第一次启动项目的用户，按当前 Phase 1 可用能力介绍最短使用路径。

## 前置要求

- Python 3.9+
- `pip`
- 建议使用虚拟环境

## 安装

```bash
cd "C:\Users\Toxic\Desktop\python\python项目DataViz Studio"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

依赖安装会包含完整运行栈，例如 `requests`、`scipy`、`scikit-learn`、`sqlalchemy`、`kaleido`。

## 启动

```bash
python app.py
```

默认地址：`http://127.0.0.1:8050`

可选方式：

```bash
python cli.py
```

## 首次使用流程

### 1. 加载数据

你可以在欢迎页直接：

- 上传本地 `CSV`、`TSV`、`Excel`、`JSON`、`Parquet`、`Feather`
- 使用示例数据集快速体验

### 2. 浏览数据画布

进入 `数据画布` 后可以：

- 查看行数、列数、缺失值、重复值和内存占用
- 在表格中排序、筛选、分页浏览
- 快速检查字段结构和基础数据质量

### 3. 在数据工坊清洗数据

`数据工坊` 已可用于常见清洗任务：

- 筛选、排序、去重、重命名
- 缺失值处理
- 字段类型转换
- 步骤预览、撤销 / 重做
- 导出当前流程为 Python 脚本或 Jupyter Notebook

### 4. 在图表工作室生成图表

`图表工作室` 当前支持 Plotly 与 Seaborn 双引擎：

- 选择图表类型并配置字段映射
- 实时预览图表
- 查看推荐理由与适用场景
- 导出 PNG / HTML
- 导出 Python 脚本与 Jupyter Notebook

导出限制：

- Plotly 静态图导出依赖 `kaleido`
- Seaborn 当前按 PNG 位图导出，不支持 SVG

### 5. 在机器学习页面完成引导式训练

`机器学习` 当前提供：

- 分类、回归、聚类与轻量时序分析流程
- 中文算法说明、适用场景和下一步提示
- 训练结果摘要、实验指标和预测反馈

Phase 1 的重点是流程引导和结果可读性，不包含 AutoML 或自动替你选模型。

### 6. 保存项目继续分析

顶栏支持打开 / 保存 `.dvs` 项目文件：

- `embedded`：把数据一并写入项目，适合迁移和归档
- `reference`：保留原始来源引用，适合减小项目体积

重新打开项目后，可恢复当前路由、数据集和部分页面状态。

## 主要导航

- `首页`：当前能力总览与快速入口
- `数据中心`：导入、切换、管理数据集
- `数据画布`：预览与基础探索
- `数据工坊`：清洗和转换
- `图表工作室`：可视化配置与导出
- `统计实验室`：描述统计、相关性和检验
- `机器学习`：引导式建模流程
- `高级工具`：聚合当前上下文并统一导出

## 常见问题

### 应用无法启动

先检查：

```bash
python --version
pip install -r requirements.txt --force-reinstall
```

若仍失败，再确认 `8050` 端口未被占用。

### 图表无法导出 PNG 或 SVG

- Plotly 静态图需要安装 `kaleido`
- 若当前图表来自 Seaborn，请直接使用 PNG 或 HTML 导出

### 项目恢复时数据未完全回到原始位置

优先检查项目保存模式：

- `embedded` 更适合跨机器或长期归档
- `reference` 依赖原始文件路径或来源仍然可访问

## 验证安装

```bash
pytest -q
```

当前基线：`177 passed, 1 skipped`

## 更多说明

- [README](../README.md)
- [QUICKSTART](../QUICKSTART.md)
- [实现计划](./implementation_plan.md)
