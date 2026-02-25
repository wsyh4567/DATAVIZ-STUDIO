# DataViz Studio — Phase 1：可用骨架

## 项目搭建
- [ ] 初始化 Git 仓库
- [x] 创建项目目录结构（按 Prompt 10 规范）
- [x] 创建 `pyproject.toml` + `requirements.txt`（Dash 技术栈）
- [x] 创建 `app.py` 应用入口

## 设计系统与主题
- [x] 创建 `assets/css/base.css`（CSS 变量 + 暗色/亮色主题）
- [x] 创建 `assets/css/components.css`（组件样式）
- [x] 创建 `assets/css/themes.css`（主题切换）

## 应用外壳与导航
- [x] 顶部导航栏（Logo、设置、帮助按钮）
- [x] 左侧侧边栏（图标 + 文字，可折叠）
- [x] SPA 路由（`dcc.Location` 实现页面切换）
- [x] 底部状态栏（数据集信息、内存、日志）
- [x] 全局状态管理（`dcc.Store`）

## 欢迎页（`/welcome`）
- [x] 拖拽文件上传区域
- [x] 最近项目列表（占位）
- [x] 示例数据集快速体验按钮
- [x] 产品 Logo 与简介

## 数据加载服务
- [x] `services/data_loader.py` — CSV/Excel/JSON 加载
- [x] 自动检测编码（UTF-8/GBK/Latin1）
- [x] 智能推断分隔符与表头
- [x] Excel Sheet 选择

## 数据管理器
- [x] `core/data_manager.py` — 多 DataFrame 管理
- [x] 活跃数据集追踪
- [x] Undo/Redo 操作历史栈

## 数据画布页（`/canvas`）
- [x] AG Grid 高性能表格（排序、筛选、虚拟滚动）
- [x] 数据概览卡片（行数、列数、缺失值、重复行、内存）

## Git 与验证
- [ ] 每个主要里程碑提交 commit
- [ ] 验证应用启动和页面导航
- [ ] 验证数据加载和表格展示
