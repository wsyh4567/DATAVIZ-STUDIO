# DataViz Studio 项目结构

## 核心文件
- `app.py` - 主应用入口
- `cli.py` - 命令行接口
- `config.py` - 配置文件
- `requirements.txt` - Python依赖
- `pyproject.toml` - 项目配置

## 目录结构

### `/assets` - 前端资源
- `css/` - 样式文件
  - `base.css` - 基础样式
  - `themes.css` - 主题样式
  - `components.css` - 组件样式
  - `animations.css` - 动画效果
- `js/` - JavaScript文件
  - `clipboard.js` - 剪贴板功能
  - `code_copy.js` - 代码复制
  - `drag_drop.js` - 拖拽功能

### `/components` - UI组件
- `chart_builder.py` - 图表构建器
- `code_preview.py` - 代码预览
- `data_table.py` - 数据表格
- `field_panel.py` - 字段面板
- `filter_builder.py` - 过滤器构建器
- `navbar.py` - 导航栏
- `pipeline_view.py` - 流程视图
- `sidebar.py` - 侧边栏
- `statusbar.py` - 状态栏
- `data_workshop/` - Data Workshop组件
  - `code_preview_panel.py` - 代码预览面板
  - `column_menu.py` - 列菜单
  - `data_grid.py` - 数据网格
  - `filter_panel.py` - 过滤面板
  - `step_panel.py` - 步骤面板
  - `toolbar.py` - 工具栏

### `/core` - 核心模块
- `data_manager.py` - 数据管理器
- `state_manager.py` - 状态管理器

### `/services` - 业务逻辑
- `code_generator.py` - 代码生成器
- `data_cleaner.py` - 数据清洗服务
- `data_workshop/` - Data Workshop服务
  - `models.py` - 数据模型
  - `operation_executor.py` - 操作执行器
  - `preview_engine.py` - 预览引擎
  - `step_manager.py` - 步骤管理器
  - `undo_redo_stack.py` - 撤销重做栈
  - `code_generator.py` - 代码生成器
  - `quality_analyzer.py` - 质量分析器
  - `type_detector.py` - 类型检测器

### `/pages` - 页面模块
- `chart_studio.py` - 图表工作室
- `chart_studio_new.py` - 新版图表工作室
- `data_workshop.py` - 数据工作坊
- `data_workshop_callbacks.py` - 数据工作坊回调
- `data_workshop_preview.py` - 数据工作坊预览

### `/tests` - 测试文件
- `test_app.py` - 应用测试
- `test_data_cleaning.py` - 数据清洗测试
- `test_data_loading.py` - 数据加载测试
- `test_filter_sort.py` - 过滤排序测试
- `data_workshop/` - Data Workshop测试
- `integration/` - 集成测试
- `manual/` - 手动验证脚本
- `archived/` - 已归档测试

### `/docs` - 文档
- `INDEX.md` - 文档索引
- `GETTING_STARTED.md` - 快速开始
- `CHART_STUDIO_REDESIGN.md` - 图表工作室重设计
- `PYTHON_FIRST_ARCHITECTURE.md` - Python优先架构
- `SYSTEM_ARCHITECTURE_REDESIGN.md` - 系统架构重设计
- `FRONTEND_REVIEW.md` - 前端审查
- `PHASE2_COMPLETION.md` - Phase 2完成报告
- `PHASE2_REBUILD_COMPLETE.md` - Phase 2重构完成
- `PHASE2_REBUILD_GUIDE.md` - Phase 2重构指南
- `task.md` - 任务列表
- `archive/` - 归档文档
- `archived/` - 已归档文档

### `/scripts` - 工具脚本
- `convert_to_docx.py` - 转换为DOCX
- `copy_to_desktop.py` - 复制到桌面
- `fix_encoding.py` - 修复编码

### `/implementation` - 实现计划
- `README.md` - 实现说明
- `WEEK1_DATA_CLEANING.md` - 第1周：数据清洗
- `WEEK2_NUMERIC_PROCESSING.md` - 第2周：数值处理
- `WEEK3_CHART_ENHANCEMENT.md` - 第3周：图表增强

### `/reference_projects` - 参考项目
外部参考项目（dtale, pygwalker等）

### `/.kiro` - Kiro配置
- `settings/` - 设置
- `specs/` - 规格说明

## 主要文档
- `README.md` - 项目说明
- `QUICKSTART.md` - 快速开始指南
- `DOCUMENTATION_INDEX.md` - 文档索引
- `FEATURE_ENHANCEMENT_PLAN.md` - 功能增强计划
- `REFERENCE_PROJECTS_SETUP.md` - 参考项目设置
