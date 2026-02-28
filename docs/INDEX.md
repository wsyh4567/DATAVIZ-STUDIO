# DataViz Studio 文档索引

## 📚 快速导航

### 用户文档
- [快速开始指南](../QUICKSTART.md) - 5分钟上手 DataViz Studio
- [入门教程](GETTING_STARTED.md) - 详细的功能介绍和使用教程
- [前端功能概览](FRONTEND_REVIEW.md) - UI 组件和交互说明

### 开发文档
- [功能增强计划](../FEATURE_ENHANCEMENT_PLAN.md) - 当前开发计划（Week 1-4）
- [Python 优先架构](PYTHON_FIRST_ARCHITECTURE.md) - 核心架构设计理念
- [系统架构重设计](SYSTEM_ARCHITECTURE_REDESIGN.md) - 系统架构文档

### 设计文档
- [图表工作室重设计](CHART_STUDIO_REDESIGN.md) - 图表工作室的设计方案
- [Phase 2 重构指南](PHASE2_REBUILD_GUIDE.md) - Phase 2 重构说明
- [Phase 2 完成报告](PHASE2_COMPLETION.md) - Phase 2 完成总结

### AI 提示词
- [设计提示词（独立版）](../design_prompts_standalone.md) - 用于 AI 辅助开发的完整提示词
- [设计提示词（JupyterLab 版）](../design_prompts.md) - JupyterLab 内嵌版本的提示词

### 规范文档
位于 `.kiro/specs/` 目录：
- `feature-enhancement/` - 功能增强规范（当前活跃）
  - `requirements.md` - 需求文档
  - `tasks.md` - 任务列表
- `data-workshop-realtime-preview/` - 数据工坊实时预览规范
  - `requirements.md` - 需求文档
  - `tasks.md` - 任务列表

### 参考项目
- [参考项目设置](../REFERENCE_PROJECTS_SETUP.md) - D-Tale 和 PyGWalker 参考项目说明

### 历史文档
- [历史任务归档](archive/old_tasks/) - 已完成的历史任务文档

---

## 🎯 当前开发阶段

**Phase 4 - 功能增强（2026-02）**

### Week 1: 核心数据清洗功能 ✅
- 列拆分、列合并
- 查找替换、字符串清理
- 单元测试覆盖率 > 80%

### Week 2: 数值处理功能 🔄
- 数值分箱（等宽、等频、自定义）
- 标准化归一化（Z-score、Min-Max、鲁棒）
- 滚动窗口函数、累积函数

### Week 3: 图表功能增强 ⏳
- 智能字段识别和字段面板
- 动态参数面板
- 扩展图表类型（6+ Plotly, 4+ Seaborn）

### Week 4: 集成测试和文档 ⏳
- 端到端集成测试
- 性能优化
- 用户文档更新

---

## 📖 文档编写规范

### 文档类型
1. **需求文档** (`requirements.md`) - 功能需求、验收标准
2. **任务文档** (`tasks.md`) - 具体任务、时间估计、依赖关系
3. **设计文档** (`design.md`) - 架构设计、技术方案
4. **完成报告** (`*_COMPLETE.md`) - 阶段性完成总结

### 文档位置
- 活跃规范：`.kiro/specs/[spec-name]/`
- 用户文档：`docs/`
- 历史文档：`docs/archive/`
- AI 提示词：根目录

### 文档更新
- 完成的任务文档移至 `docs/archive/old_tasks/`
- 保持根目录整洁，只保留活跃文档
- 更新文档索引（本文件）

---

**最后更新**: 2026-02-27  
**维护者**: DataViz Studio Team
