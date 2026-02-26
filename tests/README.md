# 测试脚本说明

本目录包含 DataViz Studio 的各类测试脚本。

## 测试文件分类

### 基础功能测试
- `test_app.py` - 应用核心功能测试
- `test_data_loading.py` - 数据加载流程测试
- `test_filter_sort.py` - 筛选和排序功能测试

### Phase 2 测试
- `test_phase2.py` - 图表工作室功能测试

### Phase 3 测试
- `test_phase3.py` - Phase 3 功能测试（Selenium）
- `test_phase3_auto.py` - Phase 3 自动化测试
- `test_phase3_comprehensive.py` - Phase 3 综合测试
- `test_phase3_features.py` - Phase 3 功能单元测试
- `test_phase3_manual.py` - Phase 3 手动测试检查清单
- `test_phase3_simple.py` - Phase 3 简单功能测试

## 运行测试

```bash
# 运行单个测试
python tests/test_app.py

# 运行 Phase 3 自动化测试
python tests/test_phase3_auto.py
```
