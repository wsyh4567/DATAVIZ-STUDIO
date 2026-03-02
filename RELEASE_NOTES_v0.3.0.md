# DataViz Studio v0.3.0 发布说明

**发布日期**: 2026年3月2日

---

## 🎉 版本亮点

v0.3.0 是一个重要的维护版本，专注于项目结构优化和代码组织改进，为后续功能开发奠定更好的基础。

### 核心改进

1. **项目结构重构** - 更清晰的目录组织
2. **测试文件规范化** - 按功能分类的测试结构
3. **文档完善** - 新增项目结构说明文档
4. **代码质量提升** - 更好的可维护性

---

## ✨ 新增功能

### 项目结构优化

#### 新增目录
- `scripts/` - 工具脚本目录
  - `convert_to_docx.py` - Markdown 转 DOCX 工具
  - `copy_to_desktop.py` - 文件复制工具
  - `fix_encoding.py` - 编码修复工具
  - `README.md` - 脚本使用说明

- `docs/archived/` - 归档文档目录
  - 历史文档和已完成阶段记录
  - UI 改进记录
  - 分析报告
  - 设计文档
  - `README.md` - 归档文档索引

#### 测试文件组织
- `tests/integration/` - 集成测试
  - `test_chart_studio.py`
  - `test_chart_studio_new.py`

- `tests/manual/` - 手动验证脚本
  - `verify_duplicate_fix.py`
  - `test_app_access.py`
  - `test_data_cleaning_demo.py`
  - `verify_app_startup.py`
  - `verify_checkpoint.py`

- `tests/archived/` - 已归档测试
  - 历史版本测试文件

### 文档改进

#### 新增文档
- `PROJECT_STRUCTURE.md` - 完整的项目结构说明
  - 核心文件说明
  - 目录结构详解
  - 各模块功能介绍
  - 主要文档索引

- `CHANGELOG.md` - 更新日志
  - 遵循 Keep a Changelog 规范
  - 语义化版本管理
  - 详细的变更记录

- `scripts/README.md` - 工具脚本说明
- `docs/archived/README.md` - 归档文档索引
- `tests/README.md` - 测试文件说明（更新）

---

## 🔧 改进优化

### 代码组织
- 清理根目录，移除散乱的临时文件
- 将历史文档移至归档目录
- 将工具脚本集中到 scripts 目录
- 按功能分类组织测试文件

### 配置优化
- 更新 `.gitignore`
  - 忽略日志文件 (`*.log`)
  - 忽略覆盖率文件 (`.coverage`, `htmlcov/`)
  - 忽略 pytest 缓存 (`.pytest_cache/`)
  - 忽略临时文件 (`*.tmp`, `*.bak`)

### 可维护性提升
- 更清晰的目录结构
- 完善的文档说明
- 规范的测试组织
- 更好的代码可读性

---

## 🐛 Bug 修复

### 主题样式修复
- 修复 DataTable 在暗色主题下的文本可见性问题
- 修复浅色主题的玻璃效果显示问题
- 优化主题切换的平滑过渡

---

## 📚 文档更新

### 新增文档
- 项目结构完整说明
- 更新日志规范
- 工具脚本使用指南
- 归档文档索引
- 测试文件组织说明

### 文档改进
- 完善 README.md 项目结构部分
- 更新测试说明文档
- 添加目录导航和索引

---

## 🔄 迁移指南

### 从 v0.2.0 升级

本版本主要是文件结构调整，不涉及 API 变更，升级过程简单：

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 无需额外操作，项目可直接运行
python app.py
```

### 文件位置变更

如果你有自定义脚本引用了以下文件，需要更新路径：

| 旧路径 | 新路径 |
|--------|--------|
| `convert_to_docx.py` | `scripts/convert_to_docx.py` |
| `copy_to_desktop.py` | `scripts/copy_to_desktop.py` |
| `fix_encoding.py` | `scripts/fix_encoding.py` |
| `BUG_ANALYSIS.md` | `docs/archived/BUG_ANALYSIS.md` |
| `UI_IMPROVEMENTS_COMPLETE.md` | `docs/archived/UI_IMPROVEMENTS_COMPLETE.md` |

### 测试文件位置

测试文件已重新组织，如果你有 CI/CD 配置，可能需要更新：

```bash
# 运行所有测试
pytest tests/

# 运行单元测试（排除集成测试和手动测试）
pytest tests/ --ignore=tests/integration --ignore=tests/manual --ignore=tests/archived

# 运行集成测试
pytest tests/integration/

# 手动验证脚本需要单独运行
python tests/manual/verify_app_startup.py
```

---

## 📊 项目统计

### 代码统计
- **总文件数**: 100+
- **Python 代码**: 15,000+ 行
- **测试文件**: 15 个
- **文档文件**: 30+ 个

### 目录结构
```
DATAVIZ-STUDIO/
├── 核心代码: 50+ 文件
├── 测试文件: 15 个（已分类）
├── 文档: 30+ 个（已归档）
├── 工具脚本: 3 个（已集中）
└── 静态资源: 10+ 个
```

---

## 🎯 下一步计划

### v0.4.0 计划功能
- 描述性统计分析
- 相关性分析矩阵
- 数据透视表功能
- 假设检验向导
- 性能优化

### 长期路线图
- 仪表盘构建器
- 交叉筛选联动
- AI 辅助分析
- 多语言支持
- 插件系统

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

特别感谢：
- 提出改进建议的用户
- 报告 Bug 的测试者
- 贡献代码的开发者

---

## 📦 下载

### 源码下载
- [ZIP 压缩包](https://github.com/wsyh4567/DATAVIZ-STUDIO/archive/refs/tags/v0.3.0.zip)
- [TAR.GZ 压缩包](https://github.com/wsyh4567/DATAVIZ-STUDIO/archive/refs/tags/v0.3.0.tar.gz)

### Git 克隆
```bash
git clone -b v0.3.0 https://github.com/wsyh4567/DATAVIZ-STUDIO.git
```

---

## 📞 联系方式

- **项目主页**: https://github.com/wsyh4567/DATAVIZ-STUDIO
- **问题反馈**: https://github.com/wsyh4567/DATAVIZ-STUDIO/issues
- **讨论区**: https://github.com/wsyh4567/DATAVIZ-STUDIO/discussions

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

**DataViz Studio Team**  
2026年3月2日
