# 测试文件说明

本目录包含 DataViz Studio 的所有测试文件，已按功能分类整理。

## 目录结构

### 核心单元测试 (`tests/`)
- `test_app.py` - 应用主程序测试
- `test_data_cleaning.py` - 数据清洗功能测试
- `test_data_loading.py` - 数据加载测试
- `test_filter_sort.py` - 过滤排序功能测试

### Data Workshop 模块测试 (`tests/data_workshop/`)
- `test_callbacks.py` - 回调函数测试
- `test_models.py` - 数据模型测试
- `test_operation_executor.py` - 操作执行器测试
- `test_preview_engine.py` - 预览引擎测试
- `test_step_manager.py` - 步骤管理器测试
- `test_undo_redo_stack.py` - 撤销重做栈测试

### 集成测试 (`tests/integration/`)
- `test_chart_studio.py` - Chart Studio 集成测试
- `test_chart_studio_new.py` - 新版 Chart Studio 测试

### 手动验证脚本 (`tests/manual/`)
- `verify_duplicate_fix.py` - 重复问题修复验证
- `test_app_access.py` - 应用访问测试
- `test_data_cleaning_demo.py` - 数据清洗演示
- `verify_app_startup.py` - 应用启动验证
- `verify_checkpoint.py` - 检查点验证

### 已归档测试 (`tests/archived/`)
包含历史版本和已废弃的测试文件，保留用于参考。

## 运行测试

```bash
# 运行所有单元测试
pytest tests/

# 运行特定模块测试
pytest tests/data_workshop/

# 运行集成测试
pytest tests/integration/

# 运行单个测试文件
pytest tests/test_app.py

# 手动验证脚本需要单独运行
python tests/manual/verify_app_startup.py
```

## 测试覆盖率

```bash
# 生成测试覆盖率报告
pytest --cov=. --cov-report=html tests/
```
