# Superpowers Analysis: DataViz Studio 产品级优化方案 (Phase 2)

## Main Goal
从真实数据分析师的视角审视项目，发现功能缺失、UI设计缺陷、用户体验痛点，并实施改进。

## Tasks
- [x] 深度阅读全部页面代码 (welcome, data_hub, data_canvas, chart_studio, data_workshop, statistics_lab, dashboard, advanced)
- [x] 深度阅读全部服务层代码 (data_loader, chart_service, code_generator, stats_service, data_cleaner, field_analyzer)
- [x] 深度阅读核心层 (data_manager, state_manager) 和组件层 (navbar, sidebar, statusbar, data_table)
- [x] 以数据分析师身份列出功能缺失清单
- [x] 以 UI/UX 设计师身份列出界面问题清单
- [ ] 实施优化

## Findings

### Finding 1 - 数据导出功能完全缺失 (CRITICAL)
整个项目没有任何"导出数据"的入口。数据分析师处理完数据后，无法将清洗后的
DataFrame 导出为 CSV/Excel。只有图表可以导出(PNG/SVG/HTML)，但数据本身不行。
这是数据分析工具的核心功能。

### Finding 2 - 欢迎页只有3个示例数据集，且上传提示信息不完整 (HIGH)
config.py 支持 8 种格式(.csv .tsv .xlsx .xls .json .parquet .feather .ftr)，
但欢迎页和数据中心的上传提示都只写了"支持 CSV、Excel (.xlsx)、JSON 格式"，
遗漏了 Parquet/Feather/TSV。这会误导用户认为不支持这些格式。

### Finding 3 - 数据画布页仍有 stdout hack (MEDIUM)
data_canvas.py 第8-13行仍存在我们之前在 app.py 中已移除的 stdout 编码 hack。

### Finding 4 - 导航栏按钮全部是装饰性的 (MEDIUM)
navbar.py 中有通知🔔、设置⚙️、帮助❓三个按钮，但全部没有绑定任何回调。
点击后无任何反应。对用户来说这是明显的"假UI"。

### Finding 5 - 仪表盘图表硬编码 plotly_dark 主题 (LOW)
dashboard.py 中所有图表都硬编码了 template="plotly_dark" 和
paper_bgcolor='#1B1D2A'。当用户切换到亮色主题时，图表仍然是暗色背景，
视觉效果违和。

### Finding 6 - 多文件上传不支持 (MEDIUM)
welcome.py 和 data_hub.py 中 dcc.Upload 都设置了 multiple=False。
数据分析师经常需要一次性导入多个文件然后合并。

### Finding 7 - 统计实验室缺少"导出分析报告" (HIGH)
statistics_lab.py 虽然已有描述性统计、相关性分析、分组聚合、异常值检测、
假设检验5个模块，但没有任何方式可以将这些分析结果导出为报告(PDF/HTML)。

### Finding 8 - 数据集列表没有"删除"和"切换活跃"的回调 (HIGH)
data_hub.py 第360-370行创建了"设为活跃"和"🗑️删除"按钮，使用了
pattern-matching ID，但整个文件中并没有注册对应的回调函数。
这两个按钮点击后不会有任何反应。

## Current Step
准备实施优化。
