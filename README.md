# 🧪 DataViz Studio

> 免费开源的零代码数据分析可视化平台 — Power BI / Tableau 的开源替代方案

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14+-green.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 产品定位

DataViz Studio 是一个**完全免费、开源**的数据分析可视化平台，对标 Power BI Desktop、Tableau 和 FineBI。

- 🎯 **零代码**：全程 GUI 操作，无需编程基础
- 🚀 **本地运行**：数据留在本地，无需云服务
- 💎 **专业级**：商业产品级别的设计和交互体验
- 🔓 **开源免费**：MIT 许可证，永久免费使用

**目标用户**：数据分析师、运营人员、产品经理、学生、科研人员

---

## 🎬 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动应用

```bash
# 方式 1：直接运行
python app.py

# 方式 2：使用 CLI
python cli.py

# 方式 3：安装后使用命令（可选）
pip install -e .
dataviz-studio
```

应用将在 `http://localhost:8050` 启动，浏览器会自动打开。

---

## 📦 技术栈

- **框架**：Dash (Plotly) — 基于 Flask + React
- **图表**：Plotly.js — 交互式图表库
- **表格**：Dash AG Grid — 高性能数据表格
- **数据处理**：pandas, numpy
- **样式**：Dash Bootstrap Components + 自定义 CSS

---

## 🗺️ 功能路线图

### ✅ Phase 1 — 可用骨架（已完成）

- [x] 应用框架 + 暗色主题 + 导航路由
- [x] 欢迎页（拖拽上传 + 示例数据）
- [x] 数据加载（CSV / Excel / JSON）
- [x] 数据表格预览（AG Grid）
- [x] 数据概览卡片

### ✅ Phase 2 — 核心体验（已完成）

- [x] 图表工作室（拖拽式，15 种图表类型）
- [x] 智能图表推荐
- [x] 样式配置面板（4种主题 + 7种配色）
- [x] 图表导出（PNG / HTML）
- [x] 字段自动分类（度量 vs 维度）
- [x] 实时图表预览

**详细报告**：查看 [docs/PHASE2_COMPLETION.md](docs/PHASE2_COMPLETION.md)

### 🚧 Phase 3 — 分析能力（进行中）

- [ ] 数据清洗面板 + 操作流水线
- [ ] 描述性统计 + 相关性分析
- [ ] 筛选构建器
- [ ] 代码生成功能

### 📅 Phase 4 — 看板与高级

- [ ] 仪表盘构建器 + 交叉筛选
- [ ] KPI 指标卡
- [ ] 假设检验向导
- [ ] 数据透视表

### 📅 Phase 5 — 差异化

- [ ] 数据故事（Scrollytelling）
- [ ] 时间序列分析
- [ ] 数据对比
- [ ] 项目保存/加载
- [ ] 导出为 Jupyter Notebook

---

## 📂 项目结构

```
dataviz-studio/
├── app.py                  # 应用入口
├── cli.py                  # 命令行入口
├── config.py               # 全局配置
├── core/                   # 核心逻辑
│   ├── data_manager.py     # 数据管理（多 DataFrame + undo/redo）
│   └── state_manager.py    # 状态管理
├── pages/                  # 页面模块
│   ├── welcome.py          # 欢迎页
│   ├── data_hub.py         # 数据中心
│   └── data_canvas.py      # 数据画布
├── components/             # UI 组件
│   ├── navbar.py           # 顶部导航栏
│   ├── sidebar.py          # 左侧侧边栏
│   ├── statusbar.py        # 底部状态栏
│   └── data_table.py       # AG Grid 封装
├── services/               # 业务逻辑
│   └── data_loader.py      # 数据加载服务
├── assets/css/             # 样式文件
│   ├── base.css            # 基础样式 + CSS 变量
│   ├── components.css      # 组件样式
│   └── themes.css          # 主题切换
├── utils/                  # 工具函数
│   ├── helpers.py
│   └── i18n.py             # 国际化
├── tests/                  # 测试脚本
│   └── README.md           # 测试说明
└── docs/                   # 项目文档
    ├── archive/            # 历史文档归档
    ├── GETTING_STARTED.md
    ├── FRONTEND_REVIEW.md
    └── task.md
```

---

## 🎨 设计系统

### 暗色主题（默认）

- **背景**：`#0F1117` / `#1B1D2A` / `#262940`
- **强调色**：`#6366F1` (Indigo)
- **文字**：`#F1F5F9` / `#94A3B8` / `#64748B`
- **成功/警告/错误**：`#10B981` / `#F59E0B` / `#EF4444`

### 亮色主题

- **背景**：`#F8FAFC` / `#FFFFFF` / `#F1F5F9`
- **强调色**：`#4F46E5` (Indigo)
- **文字**：`#0F172A` / `#475569` / `#94A3B8`

点击顶栏的 🌓 按钮可切换主题。

---

## 🤝 贡献指南

欢迎贡献代码、报告 Bug 或提出功能建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

- [Dash](https://dash.plotly.com/) — 强大的 Python Web 框架
- [Plotly](https://plotly.com/) — 优秀的交互式图表库
- [AG Grid](https://www.ag-grid.com/) — 高性能数据表格
- [pandas](https://pandas.pydata.org/) — 数据处理利器

---

## 📧 联系方式

- 项目主页：[GitHub](https://github.com/yourusername/dataviz-studio)
- 问题反馈：[Issues](https://github.com/yourusername/dataviz-studio/issues)

---

**Made with ❤️ by DataViz Studio Contributors**
