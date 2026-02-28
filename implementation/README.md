# DataViz Studio 功能增强实施指南

## 概述

本目录包含基于 D-Tale 和 PyGWalker 的功能增强实施计划。所有功能都经过精心设计，确保可实现性和实用性。

---

## 📁 文件结构

```
implementation/
├── README.md                      # 本文件
├── WEEK1_DATA_CLEANING.md         # 第1周：数据清洗
├── WEEK2_NUMERIC_PROCESSING.md    # 第2周：数值处理
├── WEEK3_CHART_ENHANCEMENT.md     # 第3周：图表增强
└── WEEK4_STATISTICS.md            # 第4周：统计分析（待创建）
```

---

## 🎯 总体目标

### 功能数量目标
- **数据清洗**: 20+ 功能
- **数值处理**: 15+ 功能
- **图表增强**: 30+ 图表类型
- **统计分析**: 10+ 功能

### 质量目标
- 代码覆盖率 > 80%
- 所有功能生成 Python 代码
- UI 响应时间 < 1秒
- 完整的错误处理

---

## 📅 实施时间表

### Week 1: 核心数据清洗（2026-02-27 ~ 03-03）
**目标**: 实现列操作和字符串处理

**Day 1-2**: 列拆分和合并
- 拆分列（按分隔符）
- 合并列（多列合一）
- UI 模态框
- 代码生成

**Day 3-4**: 字符串处理
- 查找替换（支持正则）
- 去除空格
- 大小写转换
- 提取子字符串

**Day 5**: 测试和文档
- 单元测试
- 集成测试
- 用户文档

**交付物**:
- [ ] `services/data_cleaner.py`
- [ ] 更新 `pages/data_workshop.py`
- [ ] `tests/test_data_cleaning.py`
- [ ] 用户文档

---

### Week 2: 数值处理（2026-03-04 ~ 03-08）
**目标**: 实现数值转换和窗口函数

**Day 1-2**: 分箱和标准化
- 等宽/等频/自定义分箱
- Z-score 标准化
- Min-Max 归一化
- 鲁棒缩放

**Day 3-4**: 窗口和累积函数
- 滚动平均/求和/标准差
- 指数平滑
- 累积和/积/最大/最小

**Day 5**: 测试和文档
- 单元测试
- 性能测试
- 用户文档

**交付物**:
- [ ] `services/numeric_processor.py`
- [ ] 更新 UI 组件
- [ ] `tests/test_numeric_processing.py`
- [ ] 用户文档

---

### Week 3: 图表增强（2026-03-09 ~ 03-13）
**目标**: 智能字段识别和动态参数

**Day 1-2**: 智能字段识别
- 字段类型推断
- 维度/度量识别
- 字段元数据
- 字段面板组件

**Day 3-4**: 动态参数面板
- 图表参数配置
- 参数验证
- 动态 UI 生成

**Day 5**: 新增图表类型
- 面积图、瀑布图
- 雷达图、极坐标图
- 等高线图、3D曲面图

**交付物**:
- [ ] `services/field_analyzer.py`
- [ ] `services/chart_config.py`
- [ ] `components/field_panel.py`
- [ ] 更新 `services/chart_service.py`
- [ ] 测试和文档

---

### Week 4: 统计分析（2026-03-14 ~ 03-18）
**目标**: 描述性统计和相关性分析

**详细计划**: 见 `WEEK4_STATISTICS.md`（待创建）

---

## 🔧 技术架构

### 服务层（Services）
```
services/
├── data_cleaner.py          # 数据清洗服务
├── numeric_processor.py     # 数值处理服务
├── field_analyzer.py        # 字段分析服务
├── chart_config.py          # 图表配置服务
├── chart_service.py         # 图表生成服务（已有）
└── code_generator.py        # 代码生成服务（已有）
```

### 组件层（Components）
```
components/
├── field_panel.py           # 字段面板组件
├── code_preview.py          # 代码预览组件（已有）
└── data_table.py            # 数据表格组件（已有）
```

### 页面层（Pages）
```
pages/
├── data_workshop.py         # 数据工坊页面（已有，需更新）
├── chart_studio.py          # 图表工作室页面（已有，需更新）
└── statistics_lab.py        # 统计实验室页面（已有）
```

---

## 🧪 测试策略

### 单元测试
```python
# 每个服务都有对应的测试文件
tests/
├── test_data_cleaning.py
├── test_numeric_processing.py
├── test_field_analyzer.py
└── test_chart_config.py
```

### 测试覆盖率目标
- 服务层: > 90%
- 组件层: > 70%
- 页面层: > 60%

### 测试类型
1. **功能测试**: 验证功能正确性
2. **边界测试**: 测试边界情况
3. **性能测试**: 确保响应时间
4. **集成测试**: 验证端到端流程

---

## 📖 代码规范

### Python 代码风格
- 遵循 PEP 8
- 使用类型提示
- 完整的文档字符串
- 有意义的变量名

### 示例
```python
def split_column(
    df: pd.DataFrame,
    column: str,
    separator: str,
    max_split: Optional[int] = None,
    new_names: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    拆分列
    
    Args:
        df: 输入数据框
        column: 要拆分的列名
        separator: 分隔符
        max_split: 最大拆分数（None = 全部）
        new_names: 新列名列表
    
    Returns:
        包含新列的数据框
    
    Raises:
        ValueError: 如果列不存在
    
    Example:
        >>> df = pd.DataFrame({'name': ['张三', '李四']})
        >>> split_column(df, 'name', '', new_names=['姓', '名'])
    """
    # 实现代码
```

---

## 🚀 快速开始

### 1. 环境准备
```bash
# 确保所有依赖已安装
pip install -r requirements.txt

# 运行现有测试
python -m pytest tests/
```

### 2. 开始第一周任务
```bash
# 阅读实施计划
cat implementation/WEEK1_DATA_CLEANING.md

# 创建新服务文件
touch services/data_cleaner.py

# 开始编码
code services/data_cleaner.py
```

### 3. 测试驱动开发
```bash
# 先写测试
touch tests/test_data_cleaning.py

# 运行测试（应该失败）
pytest tests/test_data_cleaning.py

# 实现功能直到测试通过
pytest tests/test_data_cleaning.py -v
```

---

## 📊 进度跟踪

### Week 1 进度
- [ ] Day 1: 列拆分功能
- [ ] Day 2: 列合并功能
- [ ] Day 3: 查找替换功能
- [ ] Day 4: 字符串清理功能
- [ ] Day 5: 测试和文档

### Week 2 进度
- [ ] Day 1: 分箱功能
- [ ] Day 2: 标准化功能
- [ ] Day 3: 窗口函数
- [ ] Day 4: 累积函数
- [ ] Day 5: 测试和文档

### Week 3 进度
- [ ] Day 1: 字段类型推断
- [ ] Day 2: 字段面板组件
- [ ] Day 3: 图表参数配置
- [ ] Day 4: 动态参数面板
- [ ] Day 5: 新增图表类型

---

## 🤝 协作指南

### Git 工作流
```bash
# 创建功能分支
git checkout -b feature/week1-data-cleaning

# 提交代码
git add services/data_cleaner.py
git commit -m "feat: 实现列拆分功能"

# 推送分支
git push origin feature/week1-data-cleaning
```

### 提交信息规范
- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `test:` 测试相关
- `refactor:` 代码重构

---

## 📚 参考资源

### D-Tale 参考
- 列构建器: `reference_projects/dtale/dtale/column_builders.py`
- 数据清洗: `reference_projects/dtale/dtale/column_replacements.py`
- 视图路由: `reference_projects/dtale/dtale/views.py`

### PyGWalker 参考
- 字段解析: `reference_projects/pygwalker/pygwalker/data_parsers/pandas_parser.py`
- 图表规范: `reference_projects/pygwalker/pygwalker/services/spec.py`

### 文档
- D-Tale 文档: https://dtale.readthedocs.io/
- PyGWalker 文档: https://docs.kanaries.net/pygwalker
- Pandas 文档: https://pandas.pydata.org/docs/
- Plotly 文档: https://plotly.com/python/

---

## ❓ 常见问题

### Q: 如何选择实现优先级？
A: 参考 `FEATURE_ENHANCEMENT_PLAN.md` 中的优先级矩阵，优先实现高价值、低难度的功能。

### Q: 如何确保代码质量？
A: 遵循测试驱动开发（TDD），先写测试，再实现功能。

### Q: 如何处理复杂功能？
A: 将复杂功能分解为小的、可测试的单元，逐步实现。

### Q: 遇到技术难题怎么办？
A: 参考 D-Tale 和 PyGWalker 的实现，或查阅相关文档。

---

## 📞 联系方式

如有问题或建议，请：
1. 查看相关文档
2. 参考示例代码
3. 提交 Issue

---

**文档版本**: 1.0  
**创建日期**: 2026-02-26  
**最后更新**: 2026-02-26
