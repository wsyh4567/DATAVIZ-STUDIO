# 数据工坊实时预览 - 快速开始指南

## 🚀 快速开始

### 1. 基本使用

```python
import pandas as pd
from services.data_workshop.preview_engine import PreviewEngine
from services.data_workshop.step_manager import StepManager

# 创建示例数据
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'SF']
})

# 初始化组件
engine = PreviewEngine(max_preview_rows=1000)
manager = StepManager()

# 添加操作步骤
manager.add_step('filter', {
    'column': 'age',
    'operator': '>',
    'value': 25
})

# 计算预览
result = engine.compute_preview(df, manager.get_pipeline())

print(f"预览结果: {result['full_rows']} 行 × {result['full_cols']} 列")
print(f"执行时间: {result['execution_time']:.3f} 秒")
print(result['preview_df'])
```

### 2. 支持的操作

#### 筛选数据
```python
# 数值筛选
manager.add_step('filter', {
    'column': 'age',
    'operator': '>',  # ==, !=, >, <, >=, <=
    'value': 25
})

# 文本筛选
manager.add_step('filter', {
    'column': 'name',
    'operator': 'contains',  # contains, startswith, endswith
    'value': 'Alice'
})
```

#### 删除列
```python
# 删除单列
manager.add_step('drop_column', {
    'column': 'temp_col'
})

# 删除多列
manager.add_step('drop_column', {
    'columns': ['col1', 'col2']
})
```

#### 重命名列
```python
manager.add_step('rename_column', {
    'old_name': 'old_col',
    'new_name': 'new_col'
})
```

#### 类型转换
```python
manager.add_step('type_conversion', {
    'column': 'age',
    'target_type': 'int'  # int, float, str, datetime, bool
})
```

#### 填充缺失值
```python
# 用均值填充
manager.add_step('fill_missing', {
    'column': 'salary',
    'method': 'mean'  # mean, median, mode, ffill, bfill, value
})

# 用固定值填充
manager.add_step('fill_missing', {
    'column': 'status',
    'method': 'value',
    'value': 'unknown'
})
```

#### 排序
```python
manager.add_step('sort', {
    'column': 'age',
    'ascending': True  # True=升序, False=降序
})
```

#### 去重
```python
# 全列去重
manager.add_step('drop_duplicates', {})

# 基于特定列去重
manager.add_step('drop_duplicates', {
    'subset': ['name', 'email'],
    'keep': 'first'  # first, last
})
```

#### 列拆分
```python
manager.add_step('split_column', {
    'column': 'full_name',
    'delimiter': ' ',
    'new_columns': ['first_name', 'last_name']
})
```

#### 列合并
```python
manager.add_step('merge_columns', {
    'columns': ['first_name', 'last_name'],
    'delimiter': ' ',
    'new_column': 'full_name'
})
```

#### 值替换
```python
manager.add_step('replace_value', {
    'column': 'status',
    'old_value': 'active',
    'new_value': 'enabled'
})
```

### 3. 撤销和重做

```python
from services.data_workshop.undo_redo_stack import UndoRedoStack

# 初始化撤销重做栈
stack = UndoRedoStack(max_history=50)

# 保存状态
state = {
    'pipeline': manager.get_pipeline(),
    'timestamp': datetime.now().isoformat()
}
stack.push_state(state)

# 撤销
if stack.can_undo():
    previous_state = stack.undo()
    print(f"撤销到: {previous_state}")

# 重做
if stack.can_redo():
    next_state = stack.redo()
    print(f"重做到: {next_state}")
```

### 4. 步骤管理

```python
# 获取步骤描述
for i, step in enumerate(manager.get_pipeline()):
    desc = manager.get_step_description(step)
    print(f"步骤 {i+1}: {desc}")

# 导航到特定步骤
pipeline_up_to_step_2 = manager.navigate_to_step(1)
result = engine.compute_preview(df, pipeline_up_to_step_2)

# 删除步骤
step_id = manager.pipeline[0]['step_id']
manager.remove_step(step_id)

# 更新步骤参数
manager.update_step(step_id, {
    'column': 'age',
    'operator': '>=',
    'value': 30
})

# 重新排序步骤
step_ids = [step['step_id'] for step in manager.pipeline]
manager.reorder_steps([step_ids[1], step_ids[0]])  # 交换前两个步骤
```

### 5. 导入导出

```python
# 导出流水线
exported = manager.export_pipeline()
import json
with open('pipeline.json', 'w') as f:
    json.dump(exported, f, indent=2)

# 导入流水线
with open('pipeline.json', 'r') as f:
    pipeline_json = json.load(f)
manager.import_pipeline(pipeline_json)
```

### 6. 性能优化

```python
# 使用缓存
engine = PreviewEngine(max_preview_rows=1000)

# 第一次计算
result1 = engine.compute_preview(df, pipeline)
print(f"第一次: {result1['execution_time']:.3f}秒")

# 第二次使用缓存（更快）
result2 = engine.compute_preview(df, pipeline)
print(f"第二次: {result2['execution_time']:.3f}秒")

# 清除缓存
engine.clear_cache()

# 带超时的计算
result = engine.compute_with_timeout(df, pipeline, timeout=3.0)
if result is None:
    print("计算超时")
```

### 7. 错误处理

```python
try:
    result = engine.compute_preview(df, pipeline)
    
    if 'error' in result:
        print(f"操作失败: {result['error']}")
        print(f"失败步骤: {result['failed_step']}")
    else:
        print("操作成功")
        
except Exception as e:
    print(f"发生错误: {e}")
```

## 📊 完整示例

```python
import pandas as pd
from services.data_workshop.preview_engine import PreviewEngine
from services.data_workshop.step_manager import StepManager
from services.data_workshop.undo_redo_stack import UndoRedoStack

# 1. 创建数据
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': ['25', '30', '35', '28', '32'],  # 字符串类型
    'city': ['NYC', 'LA', 'SF', 'NYC', 'LA'],
    'salary': [50000, 60000, 75000, 55000, 65000]
})

print("原始数据:")
print(df)
print(f"数据类型: {df.dtypes.to_dict()}")

# 2. 初始化组件
engine = PreviewEngine(max_preview_rows=1000)
manager = StepManager()
stack = UndoRedoStack()

# 保存初始状态
stack.push_state({'pipeline': []})

# 3. 添加操作步骤

# 步骤1: 类型转换
manager.add_step('type_conversion', {
    'column': 'age',
    'target_type': 'int'
})
stack.push_state({'pipeline': manager.get_pipeline()})

# 步骤2: 筛选
manager.add_step('filter', {
    'column': 'age',
    'operator': '>',
    'value': 25
})
stack.push_state({'pipeline': manager.get_pipeline()})

# 步骤3: 排序
manager.add_step('sort', {
    'column': 'salary',
    'ascending': False
})
stack.push_state({'pipeline': manager.get_pipeline()})

# 4. 计算预览
result = engine.compute_preview(df, manager.get_pipeline())

print("\n预览结果:")
print(result['preview_df'])
print(f"\n统计信息:")
print(f"- 结果行数: {result['full_rows']}")
print(f"- 结果列数: {result['full_cols']}")
print(f"- 影响行数: {result['affected_rows']}")
print(f"- 执行时间: {result['execution_time']:.3f}秒")

# 5. 显示步骤
print("\n操作步骤:")
for i, step in enumerate(manager.get_pipeline()):
    desc = manager.get_step_description(step)
    print(f"{i+1}. {desc}")

# 6. 撤销操作
print("\n撤销最后一步...")
if stack.can_undo():
    previous_state = stack.undo()
    manager.import_pipeline({'steps': previous_state['pipeline']})
    
    result = engine.compute_preview(df, manager.get_pipeline())
    print(f"撤销后行数: {result['full_rows']}")

# 7. 重做操作
print("\n重做...")
if stack.can_redo():
    next_state = stack.redo()
    manager.import_pipeline({'steps': next_state['pipeline']})
    
    result = engine.compute_preview(df, manager.get_pipeline())
    print(f"重做后行数: {result['full_rows']}")

# 8. 导出流水线
exported = manager.export_pipeline()
print(f"\n流水线已导出，包含 {len(exported['steps'])} 个步骤")
```

## 🧪 运行测试

```bash
# 运行所有测试
python -m pytest tests/data_workshop/ -v

# 运行特定测试文件
python -m pytest tests/data_workshop/test_preview_engine.py -v

# 运行特定测试
python -m pytest tests/data_workshop/test_preview_engine.py::TestPreviewEngine::test_filter_operation -v

# 查看测试覆盖率
python -m pytest tests/data_workshop/ --cov=services.data_workshop --cov-report=html
```

## 📚 更多资源

- [完整设计文档](.kiro/specs/data-workshop-realtime-preview/design.md)
- [需求文档](.kiro/specs/data-workshop-realtime-preview/requirements.md)
- [任务列表](.kiro/specs/data-workshop-realtime-preview/tasks.md)
- [阶段1完成报告](DATA_WORKSHOP_PHASE1_COMPLETE.md)
- [进度跟踪](DATA_WORKSHOP_PROGRESS.md)

## 💡 提示

1. **性能优化**: 对于大数据集，使用 `max_preview_rows` 限制预览行数
2. **缓存利用**: 相同的流水线会使用缓存，避免重复计算
3. **错误处理**: 始终检查 `result` 中是否有 `error` 字段
4. **原始数据保护**: 所有操作都不会修改原始数据框
5. **步骤描述**: 使用 `get_step_description()` 生成人类可读的描述

## 🐛 常见问题

### Q: 预览很慢怎么办？
A: 减少 `max_preview_rows` 的值，或者使用 `compute_with_timeout()` 设置超时。

### Q: 如何查看生成的pandas代码？
A: 使用 `OperationExecutor.execute()` 方法，它会返回 `(result_df, code)` 元组。

### Q: 撤销重做有数量限制吗？
A: 是的，默认保留最近50个操作。可以通过 `UndoRedoStack(max_history=100)` 调整。

### Q: 如何添加自定义操作？
A: 在 `OperationExecutor` 中添加新的 `execute_xxx()` 方法，并更新 `operation_map`。

---

开始使用数据工坊，享受所见即所得的数据清洗体验！🚀
