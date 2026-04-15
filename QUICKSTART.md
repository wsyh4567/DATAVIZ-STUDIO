# 🚀 DataViz Studio 快速启动指南

## 5分钟上手教程

### 1. 安装依赖（1分钟）

```bash
pip install -r requirements.txt
```

### 2. 启动应用（30秒）

```bash
python app.py
```

默认地址：`http://localhost:8050`

### 3. 加载数据（1分钟）

#### 方式 1：使用示例数据
1. 在欢迎页点击"示例数据集"
2. 选择"鸢尾花数据集"或"泰坦尼克数据集"
3. 数据自动加载完成

#### 方式 2：上传自己的数据
1. 拖拽 CSV/Excel 文件到上传区域
2. 或点击上传区域选择文件
3. 支持格式：CSV、TSV、Excel (.xlsx/.xls)、JSON

### 4. 浏览数据（1分钟）

点击左侧导航栏的"📊 数据画布"：

- **数据表格**：查看完整数据，支持排序、筛选
- **概览卡片**：查看行数、列数、缺失值、重复行、内存占用
- **列级摘要**：点击列头查看统计信息

### 5. 创建图表（2分钟）

点击左侧导航栏的"📈 图表工作室"：

#### 步骤 1：拖拽字段
- 从左侧字段面板拖拽字段到配置区
- 例如：将"城市"拖到 X轴，将"销售额"拖到 Y轴

#### 步骤 2：选择图表类型
- 点击顶部的图表类型卡片
- 例如：选择"柱状图"

#### 步骤 3：配置样式（可选）
- 右侧面板调整标题、主题、配色
- 显示/隐藏图例和网格线

#### 步骤 4：导出图表（可选）
- 点击"PNG"导出静态图片
- 点击"HTML"导出交互式网页
- Plotly 图表可在安装 `kaleido` 后导出 SVG；Seaborn 静态图当前会提示改用 PNG

## 🎯 常见使用场景

### 场景 1：销售数据分析

```
1. 加载销售数据（CSV）
2. 创建柱状图：城市 vs 销售额
3. 创建折线图：日期 vs 销售额
4. 创建散点图：销售额 vs 利润
5. 导出为 PNG 用于报告
```

### 场景 2：学生成绩分析

```
1. 加载成绩数据（Excel）
2. 创建直方图：查看成绩分布
3. 创建箱线图：比较不同班级成绩
4. 创建饼图：查看及格率
5. 保存图表供后续使用
```

### 场景 3：产品数据对比

```
1. 加载产品数据（CSV）
2. 创建分组柱状图：产品类别 vs 销量（按季度分组）
3. 创建气泡图：价格 vs 销量（气泡大小=利润）
4. 创建热力图：查看相关性
5. 导出为 HTML 分享给团队
```

## 📊 支持的图表类型

### 比较类（4种）
- 柱状图：比较不同类别的数值
- 分组柱状图：比较多个分组的数值
- 堆叠柱状图：显示部分与整体的关系
- 条形图：横向比较类别数值

### 趋势类（3种）
- 折线图：显示数据随时间的变化趋势
- 面积图：强调数量随时间的变化
- 堆叠面积图：显示多个系列的累积趋势

### 分布类（3种）
- 直方图：显示数值的分布情况
- 箱线图：显示数据的统计分布
- 小提琴图：显示数据的密度分布

### 关系类（3种）
- 散点图：显示两个变量之间的关系
- 气泡图：三维数据关系可视化
- 热力图：显示矩阵数据的模式

### 占比类（2种）
- 饼图：显示部分占整体的比例
- 环形图：饼图的变体，中心留空

## 💡 使用技巧

### 技巧 1：快速切换图表类型
创建图表后，直接点击其他图表类型卡片即可切换，无需重新配置字段。

### 技巧 2：使用主题
- 暗色主题：适合演示和长时间使用
- 亮色主题：适合打印和报告
- 点击顶栏 🌓 按钮切换

### 技巧 3：字段分类
- 数值字段自动识别为"度量"（可聚合）
- 分类/日期字段自动识别为"维度"（可分组）
- 系统会自动推荐最适合的图表类型

### 技巧 4：机器学习流程引导
- 先选择目标列和特征列，页面会自动判断是分类还是回归任务
- 主界面会直接展示算法中文说明、适用场景和下一步操作提示
- 建议先跑基线模型，再根据结果切换算法和调参方式
### 技巧 5：图表交互
所有图表都支持 Plotly 原生交互：
- 缩放：框选区域
- 平移：拖拽图表
- 悬停：查看数据点详情
- 重置：双击图表

### 技巧 6：数据预览
在数据画布页面，可以：
- 点击列头排序
- 使用列筛选器过滤数据
- 查看列级统计信息
- 检查数据质量

## 🔧 故障排除

### 问题 1：应用无法启动
```bash
# 检查 Python 版本（需要 3.9+）
python --version

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 问题 2：数据加载失败
- 检查文件编码（推荐 UTF-8）
- 检查文件格式（CSV 需要有表头）
- 检查文件大小（推荐 < 100MB）

### 问题 3：图表不显示
- 检查是否选择了图表类型
- 检查是否拖拽了必需字段
- 刷新浏览器页面

### 问题 4：拖拽不工作
- 确保使用现代浏览器（Chrome/Firefox/Edge）
- 清除浏览器缓存
- 刷新页面

### 问题 5：PNG / SVG 导出失败
- Plotly 静态图导出依赖 `kaleido`
- 若当前使用 Seaborn，引擎会提示 SVG 暂不可用，可直接改导出 PNG
- 若只需要分享交互图表，可继续使用 HTML 导出

## 📚 进阶功能

### 数据工坊
- 可视化执行筛选、排序、缺失值处理、去重、重命名和类型转换
- 支持步骤预览、撤销 / 重做，以及 Python / Notebook 导出

### 机器学习
- 支持分类、回归、聚类与轻量时序分析流程
- 提供中文算法说明、训练结果摘要和预测反馈

### 项目工作流
- 顶栏支持打开 / 保存 `.dvs` 项目文件
- 可恢复当前路由、数据集和部分页面状态，便于继续上次分析

## 🆘 获取帮助

- 📖 查看完整文档：[docs/](docs/)
- 🐛 报告问题：[GitHub Issues](https://github.com/yourusername/dataviz-studio/issues)
- 💬 讨论交流：[GitHub Discussions](https://github.com/yourusername/dataviz-studio/discussions)

## 🎓 学习资源

- [Plotly 文档](https://plotly.com/python/)
- [Dash 文档](https://dash.plotly.com/)
- [pandas 文档](https://pandas.pydata.org/docs/)

---

**祝你使用愉快！如有问题，欢迎反馈。**


## Runtime Notes

- Install with `pip install -r requirements.txt` to get the full app stack, including `requests`, `scipy`, `scikit-learn`, `sqlalchemy`, and `kaleido`.
- `kaleido` is required for Plotly PNG/SVG export. If it is missing, HTML export still works.
- Seaborn charts currently export as PNG bitmaps; SVG export is intentionally limited to supported Plotly flows.
- `python app.py` is the primary startup command. `python cli.py` remains available when supported by your local environment.
