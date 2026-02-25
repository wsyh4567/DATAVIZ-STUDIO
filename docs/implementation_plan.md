# DataViz Studio — Phase 1 实现计划（可用骨架）

在 `C:\Users\Toxic\Desktop\python\python项目DataViz Studio\` 目录下构建项目。本阶段交付：应用框架 + 暗色主题 + 导航路由 + 欢迎页 + 数据加载(CSV/Excel/JSON) + AG Grid 表格预览 + 数据概览卡片。

> [!IMPORTANT]
> 技术栈使用 **Dash + Plotly**（不是 Streamlit）。全程用 Git 管理版本。

---

## 变更方案

### 1. 项目脚手架与 Git 初始化

#### [NEW] pyproject.toml
- 包元数据，CLI 入口 `dataviz-studio`
- 依赖：`dash>=2.14`、`dash-bootstrap-components`、`dash-ag-grid`、`pandas`、`plotly`、`openpyxl`、`numpy`、`chardet`

#### [NEW] requirements.txt

#### [NEW] 目录结构
```
├── app.py                  # 应用入口
├── cli.py                  # 命令行入口
├── config.py               # 全局配置
├── core/
│   ├── data_manager.py     # 数据管理（多 DataFrame + undo/redo）
│   └── state_manager.py    # 状态管理
├── pages/
│   ├── welcome.py          # 欢迎页
│   ├── data_hub.py         # 数据中心
│   └── data_canvas.py      # 数据画布
├── components/
│   ├── navbar.py           # 顶部导航栏
│   ├── sidebar.py          # 左侧侧边栏
│   ├── statusbar.py        # 底部状态栏
│   └── data_table.py       # AG Grid 封装
├── services/
│   └── data_loader.py      # 数据加载服务
├── assets/css/
│   ├── base.css            # 基础样式 + CSS 变量
│   ├── components.css      # 组件样式
│   └── themes.css          # 暗色/亮色主题
└── utils/
    ├── helpers.py           # 工具函数
    └── i18n.py              # 国际化
```

---

### 2. 设计系统（CSS）

#### [NEW] base.css
- 暗色主题 CSS 变量（Prompt 9 中全部配色）
- 亮色主题变量放在 `[data-theme="light"]`
- 字体：Inter + JetBrains Mono（Google Fonts）
- 间距、圆角、过渡动画 Token

#### [NEW] components.css
- 侧边栏、顶栏、状态栏、卡片、按钮、上传区域样式
- 所有 hover/active/focus 状态带 150-200ms 过渡

#### [NEW] themes.css
- 暗色（默认）与亮色主题变量覆盖

---

### 3. 应用外壳（布局 + 路由 + 状态）

#### [NEW] app.py
- 初始化 Dash 应用，加载 DBC 主题
- 整体布局：顶栏 + 侧边栏 + `dcc.Location` + 页面内容区 + 状态栏
- `dcc.Store` 存储全局状态（活跃数据集、主题、操作历史）
- 回调：导航切换、侧边栏折叠、主题切换

#### [NEW] cli.py
- `dataviz-studio` 命令行入口：启动服务器 `localhost:8050`，自动打开浏览器

#### [NEW] navbar.py / sidebar.py / statusbar.py
- 顶部导航栏：Logo + 通知/设置/帮助按钮
- 左侧侧边栏：7 个功能页面图标导航 + 折叠切换
- 底部状态栏：当前数据集名称、行×列、内存

---

### 4. 欢迎页

#### [NEW] welcome.py
- 中央拖拽上传区域
- 示例数据集按钮（鸢尾花、泰坦尼克、Tips）
- 最近项目占位
- 回调：上传文件 → 加载到 DataManager → 跳转 `/canvas`

---

### 5. 数据加载与管理

#### [NEW] data_loader.py
- `load_csv()`：通过 `chardet` 自动检测编码，智能推断分隔符
- `load_excel()`：支持选择 Sheet
- `load_json()`：`pd.read_json` / `pd.json_normalize`
- `load_sample_dataset()`：内置示例数据集

#### [NEW] data_manager.py
- 单例 `DataManager` 类
- 多 DataFrame 存储（字典：名称 → DataFrame）
- 活跃数据集选择
- Undo/Redo 历史栈
- 元数据：行数、列数、内存占用、数据类型

---

### 6. 数据画布页

#### [NEW] data_canvas.py
- 顶部概览卡片行：总行数、总列数、缺失值、重复行、内存
- Dash AG Grid 表格：排序、筛选、列调序、虚拟滚动
- 回调：活跃数据集变化时更新表格和卡片

#### [NEW] data_table.py
- 可复用 AG Grid 封装组件

---

### 7. 数据中心页（基础版）

#### [NEW] data_hub.py
- 数据源卡片（CSV、Excel、JSON，其余标记"即将推出"）
- 上传区域
- 已加载数据集列表（卡片式：名称、行×列、大小、操作按钮）

---

### 8. Git 工作流
- 项目根目录 `git init`
- `.gitignore`（`__pycache__`、`.venv`、`*.pyc` 等）
- 按里程碑提交：脚手架 → CSS → 应用外壳 → 欢迎页 → 数据加载 → 数据画布

---

## 验证计划

### 自动验证 — 应用启动
```bash
cd "C:\Users\Toxic\Desktop\python\python项目DataViz Studio"
pip install -r requirements.txt
python app.py
```
确认应用在 `localhost:8050` 无报错启动。

### 浏览器验证
1. 打开 `http://localhost:8050` → 欢迎页渲染正常
2. 点击侧边栏导航 → 页面正确切换
3. 点击示例数据集按钮 → 数据加载并跳转到数据画布
4. 数据画布 → AG Grid 表格正确显示，概览卡片数据准确
5. 侧边栏折叠/展开正常
6. 暗色主题外观正确（深色背景、浅色文字）
