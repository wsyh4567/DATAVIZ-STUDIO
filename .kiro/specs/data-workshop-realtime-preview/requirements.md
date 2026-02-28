# 需求文档

## 介绍

数据工坊实时预览重构项目旨在改善当前数据清洗模块的用户体验，实现所见即所得的数据操作流程。当前系统存在操作流程不直观、UI设计不合理、缺乏实时反馈等问题。本项目参考 Power Query、D-Tale、PyGWalker 等成熟产品的设计理念，重构前后端代码，提供类似 Excel/Power Query 的流畅操作体验。

## 术语表

- **Data_Workshop**: 数据工坊模块，提供数据清洗和转换功能的核心系统
- **Preview_Engine**: 预览引擎，负责实时计算和显示数据变化的子系统
- **Step_Manager**: 步骤管理器，管理用户操作历史和步骤导航的组件
- **Operation_Pipeline**: 操作流水线，存储和执行数据转换步骤序列的机制
- **Inline_Editor**: 内联编辑器，允许用户直接在表格中编辑数据的界面组件
- **Virtual_Scrolling**: 虚拟滚动，用于高性能渲染大数据集的技术
- **Code_Exporter**: 代码导出器，将操作历史转换为可执行Python代码的服务
- **Column_Header_Menu**: 列头菜单，提供快速访问列操作的右键菜单组件
- **Filter_Panel**: 筛选面板，用于配置数据筛选条件的界面组件
- **Undo_Redo_Stack**: 撤销重做栈，管理操作历史以支持撤销和重做功能的数据结构

## 需求

### 需求 1: 实时数据预览

**用户故事:** 作为数据分析师，我希望在执行任何数据操作时立即看到变化后的数据预览，以便快速验证操作结果是否符合预期

#### 验收标准

1. WHEN 用户配置任何数据操作参数时，THE Preview_Engine SHALL 在500毫秒内显示操作后的数据预览
2. THE Preview_Engine SHALL 仅预览前1000行数据以保证性能
3. WHILE 用户处于预览模式，THE Data_Workshop SHALL 保持原始数据不变
4. WHEN 用户点击"应用"按钮时，THE Data_Workshop SHALL 将预览的操作应用到实际数据集
5. THE Preview_Engine SHALL 显示操作影响的行数和列数统计信息
6. IF 预览计算超过3秒，THEN THE Preview_Engine SHALL 显示加载指示器并允许用户取消操作

### 需求 2: 内联列操作

**用户故事:** 作为数据分析师，我希望通过列头菜单快速访问常用操作，以便提高数据清洗效率

#### 验收标准

1. WHEN 用户右键点击列头时，THE Column_Header_Menu SHALL 显示该列可用的操作列表
2. THE Column_Header_Menu SHALL 包含删除列、重命名列、类型转换、排序、筛选操作
3. WHEN 用户选择列头菜单中的操作时，THE Data_Workshop SHALL 在主预览区显示操作配置界面
4. THE Column_Header_Menu SHALL 根据列的数据类型显示适用的操作选项
5. WHEN 用户点击列头的筛选图标时，THE Filter_Panel SHALL 在列头下方弹出
6. THE Inline_Editor SHALL 允许用户双击单元格直接编辑数据值
7. WHEN 用户完成单元格编辑时，THE Data_Workshop SHALL 将编辑操作记录到 Operation_Pipeline

### 需求 3: 步骤管理系统

**用户故事:** 作为数据分析师，我希望查看和管理所有应用的数据转换步骤，以便理解数据处理流程并进行调整

#### 验收标准

1. THE Step_Manager SHALL 在右侧面板显示所有已应用步骤的列表
2. WHEN 用户点击某个步骤时，THE Preview_Engine SHALL 显示该步骤执行后的数据状态
3. THE Step_Manager SHALL 为每个步骤显示操作描述和影响的行列数
4. THE Step_Manager SHALL 允许用户删除任意步骤
5. THE Step_Manager SHALL 允许用户通过拖拽重新排序步骤
6. WHEN 用户修改步骤顺序时，THE Preview_Engine SHALL 按新顺序重新计算数据预览
7. THE Step_Manager SHALL 允许用户编辑步骤参数
8. WHEN 用户编辑步骤参数时，THE Preview_Engine SHALL 实时更新该步骤及后续步骤的预览结果

### 需求 4: 撤销重做功能

**用户故事:** 作为数据分析师，我希望能够撤销和重做数据操作，以便在探索数据时自由尝试不同的清洗方案

#### 验收标准

1. THE Undo_Redo_Stack SHALL 记录所有数据操作的历史状态
2. WHEN 用户点击撤销按钮时，THE Data_Workshop SHALL 恢复到上一个操作状态
3. WHEN 用户点击重做按钮时，THE Data_Workshop SHALL 前进到下一个操作状态
4. THE Data_Workshop SHALL 支持键盘快捷键 Ctrl+Z 执行撤销操作
5. THE Data_Workshop SHALL 支持键盘快捷键 Ctrl+Y 执行重做操作
6. THE Undo_Redo_Stack SHALL 保留最近50个操作状态
7. WHEN 用户在历史记录中间执行新操作时，THE Undo_Redo_Stack SHALL 清除该点之后的所有重做历史

### 需求 5: 优化的操作界面

**用户故事:** 作为数据分析师，我希望操作界面简洁直观，以便快速找到需要的功能

#### 验收标准

1. THE Data_Workshop SHALL 使用工具栏形式替代左侧折叠菜单
2. THE Data_Workshop SHALL 在工具栏中直接显示常用操作按钮
3. THE Data_Workshop SHALL 将高级操作收起在下拉菜单中
4. THE Data_Workshop SHALL 减少模态框的使用，优先使用内联面板
5. WHEN 用户选择操作时，THE Data_Workshop SHALL 在主预览区下方显示参数配置面板
6. THE Data_Workshop SHALL 使用图标和文字组合的方式标识操作按钮
7. THE Data_Workshop SHALL 提供操作搜索功能以快速定位功能

### 需求 6: 高性能表格渲染

**用户故事:** 作为数据分析师，我希望系统能够流畅处理大数据集，以便分析包含数十万行的数据

#### 验收标准

1. THE Data_Workshop SHALL 使用 Dash AG Grid 组件渲染数据表格
2. THE Virtual_Scrolling SHALL 仅渲染可见区域的数据行
3. WHEN 数据集超过10000行时，THE Preview_Engine SHALL 仅加载前10000行用于预览
4. THE Data_Workshop SHALL 显示数据集总行数和当前预览行数的提示信息
5. THE Data_Workshop SHALL 允许用户配置预览行数限制
6. WHEN 用户滚动表格时，THE Virtual_Scrolling SHALL 在100毫秒内渲染新的可见行
7. THE Data_Workshop SHALL 支持100万行以上数据集的操作而不出现明显卡顿

### 需求 7: 智能筛选系统

**用户故事:** 作为数据分析师，我希望使用直观的界面配置复杂的筛选条件，以便精确提取需要的数据

#### 验收标准

1. WHEN 用户点击列头筛选图标时，THE Filter_Panel SHALL 显示该列的筛选选项
2. THE Filter_Panel SHALL 根据列的数据类型提供适当的筛选操作符
3. WHERE 列为数值类型，THE Filter_Panel SHALL 提供等于、不等于、大于、小于、范围筛选操作
4. WHERE 列为文本类型，THE Filter_Panel SHALL 提供包含、不包含、开头、结尾、正则表达式筛选操作
5. WHERE 列为日期类型，THE Filter_Panel SHALL 提供日期范围、相对日期筛选操作
6. THE Filter_Panel SHALL 支持多条件组合筛选（AND/OR逻辑）
7. THE Filter_Panel SHALL 显示筛选条件匹配的行数预览
8. WHEN 用户应用筛选时，THE Step_Manager SHALL 将筛选条件添加为新步骤

### 需求 8: 代码导出功能

**用户故事:** 作为数据分析师，我希望将所有数据清洗操作导出为Python代码，以便在其他环境中重现数据处理流程

#### 验收标准

1. THE Code_Exporter SHALL 将 Operation_Pipeline 中的所有步骤转换为可执行的Python代码
2. THE Code_Exporter SHALL 生成包含 pandas 导入语句的完整代码
3. THE Code_Exporter SHALL 为每个操作步骤生成注释说明
4. THE Code_Exporter SHALL 保持操作步骤的执行顺序
5. THE Code_Exporter SHALL 生成的代码能够在标准Python环境中直接运行
6. THE Code_Exporter SHALL 提供代码复制到剪贴板的功能
7. THE Code_Exporter SHALL 提供代码下载为.py文件的功能
8. FOR ALL 有效的 Operation_Pipeline，导出代码然后执行该代码然后再次导出代码 SHALL 产生等价的代码（往返属性）

### 需求 9: 数据类型智能检测

**用户故事:** 作为数据分析师，我希望系统能够自动检测和建议合适的数据类型，以便快速完成数据类型转换

#### 验收标准

1. WHEN 用户加载数据集时，THE Data_Workshop SHALL 自动分析每列的数据类型
2. THE Data_Workshop SHALL 检测可能被错误识别为文本的数值列
3. THE Data_Workshop SHALL 检测可能被错误识别为文本的日期列
4. WHEN 检测到类型不匹配时，THE Data_Workshop SHALL 在列头显示警告图标
5. WHEN 用户点击类型警告图标时，THE Data_Workshop SHALL 显示建议的类型转换操作
6. THE Data_Workshop SHALL 允许用户一键应用建议的类型转换
7. THE Data_Workshop SHALL 在类型转换失败时显示详细的错误信息和失败行数

### 需求 10: 缺失值可视化

**用户故事:** 作为数据分析师，我希望直观地看到数据集中的缺失值分布，以便制定合适的缺失值处理策略

#### 验收标准

1. THE Data_Workshop SHALL 在表格中使用特殊样式高亮显示缺失值单元格
2. THE Data_Workshop SHALL 在列头显示该列的缺失值百分比
3. WHEN 用户点击"查看缺失值"按钮时，THE Data_Workshop SHALL 显示缺失值分析面板
4. THE Data_Workshop SHALL 使用热力图可视化缺失值的分布模式
5. THE Data_Workshop SHALL 显示每列的缺失值数量和百分比排序列表
6. THE Data_Workshop SHALL 提供快速访问缺失值处理操作的按钮
7. THE Data_Workshop SHALL 在预览区支持筛选显示包含缺失值的行

### 需求 11: 列拆分与合并解析器

**用户故事:** 作为数据分析师，我希望使用灵活的分隔符拆分和合并列，以便处理各种格式的文本数据

#### 验收标准

1. WHEN 用户选择拆分列操作时，THE Data_Workshop SHALL 显示分隔符配置界面
2. THE Data_Workshop SHALL 支持单字符、多字符、正则表达式作为分隔符
3. THE Data_Workshop SHALL 实时预览拆分结果的列数和示例数据
4. THE Data_Workshop SHALL 允许用户指定最大拆分数量
5. THE Data_Workshop SHALL 允许用户自定义新列的名称
6. WHEN 用户选择合并列操作时，THE Data_Workshop SHALL 允许选择多个列和分隔符
7. THE Data_Workshop SHALL 提供常用分隔符的快捷选择（逗号、空格、制表符、连字符）
8. FOR ALL 有效的列拆分操作，拆分然后合并 SHALL 恢复原始数据（往返属性）

### 需求 12: 数据质量报告

**用户故事:** 作为数据分析师，我希望获得数据集的质量报告，以便快速了解数据的整体状况

#### 验收标准

1. THE Data_Workshop SHALL 提供"生成数据质量报告"功能按钮
2. WHEN 用户点击生成报告时，THE Data_Workshop SHALL 分析数据集的各项质量指标
3. THE Data_Workshop SHALL 报告每列的数据类型、缺失值、唯一值数量、重复值数量
4. THE Data_Workshop SHALL 报告数值列的基本统计信息（均值、中位数、标准差、范围）
5. THE Data_Workshop SHALL 报告文本列的长度分布和常见模式
6. THE Data_Workshop SHALL 识别潜在的数据质量问题（如异常值、格式不一致）
7. THE Data_Workshop SHALL 为识别的问题提供建议的清洗操作
8. THE Data_Workshop SHALL 允许用户导出数据质量报告为HTML或PDF格式

## 特殊需求指导

### 解析器和序列化器需求

本项目涉及多个数据解析和序列化场景：

**操作历史序列化器**:
- THE Code_Exporter SHALL 解析 Operation_Pipeline 中的操作对象
- THE Code_Exporter SHALL 将操作对象序列化为Python代码字符串
- THE Code_Exporter SHALL 提供代码格式化功能以提高可读性
- FOR ALL 有效的 Operation_Pipeline，序列化为代码然后执行代码然后再次序列化 SHALL 产生等价的代码（往返属性）

**筛选条件解析器**:
- THE Filter_Panel SHALL 解析用户输入的筛选条件
- THE Filter_Panel SHALL 将筛选条件转换为pandas查询表达式
- THE Filter_Panel SHALL 验证筛选条件的语法正确性
- FOR ALL 有效的筛选条件，解析为查询表达式然后应用查询然后显示条件 SHALL 保持条件的语义（往返属性）

**步骤状态序列化器**:
- THE Step_Manager SHALL 序列化操作步骤为JSON格式以支持保存和加载
- THE Step_Manager SHALL 反序列化JSON格式的步骤历史
- FOR ALL 有效的步骤历史，序列化为JSON然后反序列化 SHALL 恢复完整的步骤信息（往返属性）

