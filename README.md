# 🧪 DataViz Studio

> 开源的 Python 低代码数据分析与可视化平台 — 专为数据极客与业务分析师打造的敏捷工作台

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14+-green.svg)](https://dash.plotly.com/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-orange.svg)](https://plotly.com/)
[![Version](https://img.shields.io/badge/version-0.4.0-success.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 目录

- [近期更新](#-近期更新)
- [产品定位](#-产品定位)
- [核心特性](#-核心特性)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [使用指南](#-使用指南)
- [项目结构](#-项目结构)
- [功能路线图](#️-功能路线图)
- [贡献指南](#-贡献指南)

---

## 📢 近期更新 (v0.4.0)

1. **机器学习工作室增强**：新增基于 Prophet/ARIMA 的时间序列预测专区、交互式单样本推断，以及批量预估导出管道。
2. **数据工坊重塑**：引入 Offcanvas（算子工具箱）集中管理处理算子，并改用 Modal 模态弹窗配置参数，释放画布操作空间。
3. **Chart Studio 参数智能校验**：增加针对 Plotly 与 Seaborn 的特定图表入参错误拦截（如：提醒用数字字段做大小映射），在 UI 抛出明确修复建议。
4. **全面恢复 Seaborn 渲染**：彻底修复 Dash 组件状态造成的类别校验失效，同时优化了前后端双 Y 轴 (`ax.twinx()`) 堆叠图绘制能力。
5. **底层 Bug 与交互修复**：剔除了导致 DataTable 分页报错“Dataset not found”的越界配置；升级全局 Toast 通知组件使其具备 4 秒自动消退功能。

## 📸 产品展示 (Showcase)

| 仪表板与质量透视 (Data Dashboard) | 数据清洗流水线 (Data Workshop) |
| :---: | :---: |
| ![Data Dashboard](./assets/screenshots/showcase_home.png) | ![Data Workshop](./assets/screenshots/showcase_workshop.png) |
| **多图探索与生成 (Chart Studio)** | **交互式机器学习 (ML Studio)** |
| ![Chart Studio](./assets/screenshots/showcase_charts.png) | ![ML Studio](./assets/screenshots/showcase_ml.webp) |

---

## ✨ 产品定位

DataViz Studio 是一个**注重敏捷与可复现**的 Python 低代码数据分析可视化平台。不同于传统重依赖的商业 BI（如 Power BI、Tableau），它的核心哲学是“可视化连接一切，代码驱动未来”。

### 核心优势

- 🎯 **低代码敏捷操作**：全程直观的 GUI 拖拽操作，降低分析门槛，但不仅限于零代码。
- 🐍 **原生 Python 驱动**：每一次点击都在生成背后的 Python 生产级代码（基于 pandas, Plotly, Scikit-learn 等），实现所见即所得的代码导出引擎。
- 🚀 **私有化安全运行**：100% 数据留在本地算力环境，无需云接口，绝对保障商业数据隐私。
- 💎 **模块化数据流**：从清洗工坊、机器学习推断到图表组装，形成无缝衔接的本地数据流管线。
- 🔓 **开放且免费**：MIT 许可证，拥抱强大的 Python 数据科学生态开源社区。

**目标人群**：寻求通过代码提效的数据分析师、渴望摆脱繁琐开发的数据开发人员、科研人员，以及所有希望掌控数据链条链路条理性的业务专家。

---

## 🎯 核心特性

### 1. 数据工作坊（Data Workshop）
- ✅ 可视化数据清洗和转换
- ✅ 实时预览操作结果
- ✅ 步骤管理（撤销/重做）
- ✅ 自动生成 Python 代码
- ✅ 数据质量分析

### 2. 图表工作室（Chart Studio）
- ✅ 支持 30+ 种图表类型（Plotly + Seaborn）
- ✅ 拖拽式参数配置
- ✅ 实时图表预览
- ✅ 多种主题和配色方案
- ✅ 导出为 PNG/SVG/HTML
- ✅ 生成可复现的 Python 代码

### 3. 数据中心（Data Hub）
- ✅ 支持 CSV、Excel、JSON 格式
- ✅ 拖拽上传文件
- ✅ 内置示例数据集
- ✅ 数据预览和统计信息
- ✅ 多数据集管理

### 4. 仪表板（Dashboard）
- ✅ 数据质量评分
- ✅ 快速统计摘要
- ✅ 数据类型分布
- ✅ 缺失值分析
- ✅ 类型不匹配检测

### 5. 机器学习工作室（ML Studio）🆕
- ✅ 时间序列探测与预测 (Prophet / ARIMA)
- ✅ 交互式单样本模型推断
- ✅ 自动化批量外推分析
- ✅ 二元/多分类与回归特征评估

---

## 🏗️ 技术架构

### 核心技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.9+ | 后端语言 |
| **Dash** | 2.14+ | Web 应用框架（基于 Flask + React） |
| **Plotly** | 5.18+ | 交互式图表库 |
| **Seaborn** | 0.12+ | 统计图表库 |
| **pandas** | 2.0+ | 数据处理和分析 |
| **NumPy** | 1.24+ | 数值计算 |
| **Dash Bootstrap Components** | 1.5+ | UI 组件库 |
| **Dash AG Grid** | 31.0+ | 高性能数据表格 |

### 架构设计原理

#### 1. Python 优先架构
```
用户操作 → Python 服务层 → 数据处理 → 结果返回 → 前端渲染
                ↓
         代码生成器（可导出）
```

所有数据操作都在 Python 后端完成，确保：
- 操作可追溯、可复现
- 可导出为标准 Python 代码
- 便于集成到数据分析工作流

#### 2. 响应式回调机制
基于 Dash 的回调系统实现实时交互：
```python
@callback(
    Output('chart-container', 'children'),
    Input('chart-type', 'value'),
    Input('param-x', 'value')
)
def update_chart(chart_type, x_column):
    # 实时生成图表
    return create_chart(chart_type, x_column)
```

#### 3. 状态管理
- **DataManager**：单例模式管理多个数据集
- **StateManager**：全局状态管理（主题、语言等）
- **UndoRedoStack**：操作历史栈，支持撤销/重做

#### 4. 服务层设计
```
pages/          # 页面层（UI 组件）
    ↓
components/     # 可复用组件
    ↓
services/       # 业务逻辑层
    ↓
core/           # 核心数据管理
```

---

## 🎬 快速开始

### 系统要求

- Python 3.9 或更高版本
- 操作系统：Windows / macOS / Linux
- 内存：建议 4GB 以上
- 浏览器：Chrome / Firefox / Edge（推荐）

### 安装步骤

#### 1. 克隆项目

```bash
# 使用 HTTPS
git clone https://github.com/wsyh4567/DATAVIZ-STUDIO.git

# 或使用 SSH
git clone git@github.com:wsyh4567/DATAVIZ-STUDIO.git

# 进入项目目录
cd DATAVIZ-STUDIO
```

#### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 4. 启动应用

```bash
# 方式 1：直接运行（推荐）
python app.py

# 方式 2：使用 CLI
python cli.py

# 方式 3：开发模式（自动重载）
python app.py --debug
```

启动成功后，浏览器会自动打开 `http://localhost:8050`

如果浏览器没有自动打开，请手动访问该地址。

---

## 📚 使用指南

### 第一步：加载数据

1. 启动应用后，点击顶部导航栏的 **"数据中心"**
2. 选择以下方式之一加载数据：
   - **拖拽上传**：将 CSV/Excel/JSON 文件拖入上传区域
   - **点击上传**：点击上传按钮选择文件
   - **示例数据**：点击 "加载示例数据" 快速体验

3. 数据加载后会显示：
   - 数据预览表格（前 100 行）
   - 基本统计信息（行数、列数、内存占用）
   - 数据类型分布

### 第二步：查看仪表板

1. 点击顶部导航栏的 **"仪表板"**
2. 查看数据质量分析：
   - **质量评分**：综合评估数据质量（0-100分）
   - **缺失值分析**：查看各列缺失情况
   - **数据类型分布**：了解数值型、文本型、日期型列的占比
   - **类型不匹配**：发现潜在的数据类型问题

### 第三步：数据清洗（Data Workshop）

1. 点击顶部导航栏的 **"数据工作坊"**
2. 使用工具栏进行数据操作：
   - **筛选**：按条件筛选数据
   - **排序**：对列进行升序/降序排序
   - **删除列**：移除不需要的列
   - **重命名**：修改列名
   - **填充缺失值**：使用均值/中位数/众数填充
   - **删除重复行**：去除重复数据

3. 每个操作都会：
   - 实时显示预览结果
   - 记录在步骤面板中
   - 可以撤销/重做
   - 自动生成 Python 代码

4. 点击 **"应用更改"** 将操作应用到数据集

### 第四步：创建图表（Chart Studio）

1. 点击顶部导航栏的 **"图表工作室"**
2. 选择图表库：
   - **Plotly**：交互式图表，支持缩放、悬停、动画
   - **Seaborn**：静态图表，更美观的默认样式

3. 配置图表参数：
   - **图表类型**：散点图、折线图、柱状图、饼图等 30+ 种
   - **X 轴**：选择横轴字段
   - **Y 轴**：选择纵轴字段
   - **颜色**：按类别着色
   - **大小**：按数值调整点大小
   - **高级参数**：趋势线、边际图、分面等

4. 图表会实时更新预览

5. 导出图表：
   - **PNG**：静态图片，适合报告
   - **SVG**：矢量图，适合编辑
   - **HTML**：交互式网页，可分享

6. 查看生成的 Python 代码：
   - 点击 **"复制代码"** 复制到剪贴板
   - 点击 **"下载 .py"** 保存为 Python 文件
   - 代码可直接在 Jupyter Notebook 中运行

### 第五步：主题切换

- 点击顶部导航栏右侧的 **🌓** 图标
- 在暗色主题和亮色主题之间切换
- 主题设置会自动保存

---

## 📦 技术栈详解

### 为什么选择 Dash？

Dash 是 Plotly 开发的 Python Web 框架，特别适合数据可视化应用：

1. **纯 Python 开发**：无需编写 JavaScript
2. **响应式设计**：基于 React 的现代化 UI
3. **高性能**：支持大规模数据集
4. **丰富的组件**：内置图表、表格、表单等组件
5. **活跃的社区**：大量示例和文档

### 数据处理流程

```
文件上传 → 编码检测 → pandas 读取 → 数据验证 → 存储到 DataManager
                                              ↓
                                    用户操作（筛选、排序等）
                                              ↓
                                    实时预览 + 代码生成
                                              ↓
                                    应用更改 → 更新数据集
```

### 图表生成原理

```python
# 1. 用户选择参数
chart_type = "scatter"
x = "sepal_length"
y = "sepal_width"

# 2. 服务层处理
chart_service = ChartService()
result = chart_service.create_chart(
    df=df,
    chart_type=ChartType(chart_type),
    params={'x': x, 'y': y}
)

# 3. 返回图表对象 + 代码
return {
    'figure': plotly_figure,  # 可直接渲染
    'code': generated_code     # 可复现的代码
}
```


---

## 📂 项目结构

```
DATAVIZ-STUDIO/
├── app.py                      # 应用入口
├── cli.py                      # 命令行入口
├── config.py                   # 全局配置
├── requirements.txt            # 项目依赖
│
├── core/                       # 核心逻辑层
│   ├── data_manager.py         # 数据管理器（单例模式）
│   └── state_manager.py        # 全局状态管理
│
├── pages/                      # 页面模块
│   ├── welcome.py              # 欢迎页
│   ├── data_hub.py             # 数据中心
│   ├── dashboard.py            # 仪表板
│   ├── data_workshop.py        # 数据工作坊
│   ├── data_workshop_callbacks.py  # 工作坊回调
│   └── chart_studio.py         # 图表工作室
│
├── components/                 # UI 组件
│   ├── navbar.py               # 顶部导航栏
│   ├── sidebar.py              # 左侧侧边栏
│   ├── statusbar.py            # 底部状态栏
│   ├── data_table.py           # AG Grid 封装
│   ├── chart_builder.py        # 图表构建器
│   ├── code_preview.py         # 代码预览面板
│   └── data_workshop/          # 数据工作坊组件
│       ├── toolbar.py          # 工具栏
│       ├── data_grid.py        # 数据网格
│       ├── step_panel.py       # 步骤面板
│       ├── filter_panel.py     # 筛选面板
│       └── code_preview_panel.py  # 代码预览
│
├── services/                   # 业务逻辑层
│   ├── data_loader.py          # 数据加载服务
│   ├── chart_service.py        # 图表生成服务
│   ├── code_generator.py       # 代码生成器
│   ├── data_cleaner.py         # 数据清洗服务
│   ├── field_analyzer.py       # 字段分析器
│   └── data_workshop/          # 数据工作坊服务
│       ├── models.py           # 数据模型
│       ├── operation_executor.py   # 操作执行器
│       ├── step_manager.py     # 步骤管理器
│       ├── preview_engine.py   # 预览引擎
│       ├── code_generator.py   # 代码生成器
│       ├── quality_analyzer.py # 质量分析器
│       └── type_detector.py    # 类型检测器
│
├── assets/                     # 静态资源
│   ├── css/
│   │   ├── base.css            # 基础样式 + CSS 变量
│   │   ├── components.css      # 组件样式
│   │   └── themes.css          # 主题切换
│   └── js/
│       ├── drag_drop.js        # 拖拽上传
│       ├── code_copy.js        # 代码复制
│       └── clipboard.js        # 剪贴板操作
│
├── tests/                      # 测试脚本
│   ├── data_workshop/          # 数据工作坊测试
│   └── test_data_cleaning.py   # 数据清洗测试
│
├── docs/                       # 项目文档
│   ├── INDEX.md                # 文档索引
│   ├── GETTING_STARTED.md      # 入门指南
│   ├── PYTHON_FIRST_ARCHITECTURE.md  # 架构设计
│   ├── CHART_STUDIO_REDESIGN.md      # 图表工作室设计
│   └── archive/                # 历史文档归档
│
└── implementation/             # 实现计划
    ├── WEEK1_DATA_CLEANING.md
    ├── WEEK2_NUMERIC_PROCESSING.md
    └── WEEK3_CHART_ENHANCEMENT.md
```

---

## 🗺️ 功能路线图

### ✅ Phase 1 — 可用骨架（已完成）

- [x] 应用框架 + 暗色主题 + 导航路由
- [x] 欢迎页（拖拽上传 + 示例数据）
- [x] 数据加载（CSV / Excel / JSON）
- [x] 数据表格预览（AG Grid）
- [x] 数据概览卡片

### ✅ Phase 2 — 核心体验（已完成）

- [x] 图表工作室（拖拽式，30+ 种图表类型）
- [x] 智能图表推荐
- [x] 样式配置面板（多种主题 + 配色）
- [x] 图表导出（PNG / SVG / HTML）
- [x] 字段自动分类（度量 vs 维度）
- [x] 实时图表预览
- [x] Python 代码生成

**详细报告**：查看 [docs/PHASE2_COMPLETION.md](docs/PHASE2_COMPLETION.md)

### ✅ Phase 3 — 数据工作坊（已完成）

- [x] 数据清洗面板 + 操作流水线
- [x] 实时预览引擎
- [x] 步骤管理（撤销/重做）
- [x] 数据质量分析
- [x] 类型检测和转换
- [x] 代码生成功能

### 🚧 Phase 4 — 高级分析（完成度 90%）

- [x] 描述性统计分析 (融合于 Data Canvas)
- [x] 相关性分析矩阵 (整合进 Data Canvas)
- [x] 分类回归单样本/批量推断 (ML Studio)
- [x] 时间序列分析预测 (ML Studio)
- [ ] 假设检验向导
- [ ] 数据透视表

### 📅 Phase 5 — 看板与协作

- [ ] 仪表盘构建器
- [ ] 交叉筛选联动
- [ ] KPI 指标卡
- [ ] 项目保存/加载
- [ ] 导出为 Jupyter Notebook

### 📅 Phase 6 — 差异化功能

- [ ] 数据故事（Scrollytelling）
- [ ] AI 辅助分析
- [ ] 数据对比工具
- [ ] 多语言支持
- [ ] 插件系统

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

## 🔧 常见问题

### 1. 启动失败：端口被占用

```bash
# 查看占用 8050 端口的进程
# Windows
netstat -ano | findstr :8050

# macOS/Linux
lsof -i :8050

# 修改端口（在 config.py 中）
PORT = 8051
```

### 2. 依赖安装失败

```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 图表不显示

- 检查浏览器控制台是否有错误
- 确保数据已正确加载
- 尝试刷新页面（Ctrl+F5）

### 4. 文件上传失败

- 检查文件格式（支持 CSV、Excel、JSON）
- 确保文件大小不超过 500MB
- 检查文件编码（推荐 UTF-8）

---

## 🤝 贡献指南

欢迎贡献代码、报告 Bug 或提出功能建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循 PEP 8 代码风格
- 添加必要的注释和文档字符串
- 编写单元测试
- 更新相关文档

### 报告 Bug

请在 [Issues](https://github.com/wsyh4567/DATAVIZ-STUDIO/issues) 中提交，包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Python 版本等）

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

感谢以下开源项目：

- [Dash](https://dash.plotly.com/) — 强大的 Python Web 框架
- [Plotly](https://plotly.com/) — 优秀的交互式图表库
- [Seaborn](https://seaborn.pydata.org/) — 美观的统计图表库
- [pandas](https://pandas.pydata.org/) — 数据处理利器
- [AG Grid](https://www.ag-grid.com/) — 高性能数据表格
- [Bootstrap](https://getbootstrap.com/) — UI 组件库

---

## 📧 联系方式

- 项目主页：[GitHub](https://github.com/wsyh4567/DATAVIZ-STUDIO)
- 问题反馈：[Issues](https://github.com/wsyh4567/DATAVIZ-STUDIO/issues)
- 讨论区：[Discussions](https://github.com/wsyh4567/DATAVIZ-STUDIO/discussions)

---

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/wsyh4567/DATAVIZ-STUDIO?style=social)
![GitHub forks](https://img.shields.io/github/forks/wsyh4567/DATAVIZ-STUDIO?style=social)
![GitHub issues](https://img.shields.io/github/issues/wsyh4567/DATAVIZ-STUDIO)
![GitHub pull requests](https://img.shields.io/github/issues-pr/wsyh4567/DATAVIZ-STUDIO)

---

**Made with ❤️ by DataViz Studio Contributors**
