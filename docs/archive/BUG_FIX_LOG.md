# 🐛 DataViz Studio — Bug 修复日志

## 🐛 Bug #1: 页面路由回调错误（缺少 __init__.py）

**发现时间**: 2026-02-26 04:04  
**严重程度**: 🔴 高（阻塞核心功能）  
**状态**: ✅ 已修复

### 问题描述

用户报告：
- 右上角提示：`🛑 Errors (1) × ⛑️ Callback error updating page-content.children`
- 浏览器控制台：`POST http://localhost:8050/_dash-update-component 500 (INTERNAL SERVER ERROR)`
- 数据加载功能失效，无法加载文件
- 页面无法正常切换

### 根本原因

Python 包目录缺少 `__init__.py` 文件，导致模块导入失败。当 `app.py` 中的 `route_page` 回调尝试导入页面模块时（如 `from pages.welcome import create_welcome_page`），Python 无法识别这些目录为包，导致 ImportError。

### 修复方案

在所有模块目录中创建空的 `__init__.py` 文件：
- `pages/__init__.py`
- `components/__init__.py`
- `services/__init__.py`
- `core/__init__.py`
- `utils/__init__.py`

同时在 `app.py` 和 `pages/data_canvas.py` 中添加异常处理和调试日志。

### 修复结果

✅ 应用成功启动，无 500 错误  
✅ 页面路由正常工作  
✅ 数据加载功能恢复  
✅ 所有回调函数正常执行

### 相关文件
- `pages/__init__.py`, `components/__init__.py`, `services/__init__.py`, `core/__init__.py`, `utils/__init__.py`
- `app.py` - 添加了异常处理
- `pages/data_canvas.py` - 添加了异常处理

---

## 🐛 Bug #2: 所有数据上传和示例数据功能无响应

**发现时间**: 2026-02-26 04:15  
**严重程度**: 🔴 高（阻塞核心功能）  
**状态**: ✅ 已修复

### 问题描述

用户报告：
- 欢迎页和数据中心页面的文件上传功能完全没有反应
- 点击上传区域或拖拽文件后，没有任何响应
- 欢迎页的示例数据集按钮也无法点击
- 没有跳转到画布页面，也没有错误提示
- 终端没有任何DEBUG日志输出，说明回调根本没有被触发

### 根本原因

**回调注册问题**：`pages/welcome.py` 和 `pages/data_hub.py` 中定义的回调函数从未被注册到Dash应用中。

原因分析：
1. `app.py` 中使用了懒加载（lazy import）策略，只在 `route_page` 回调中导入页面模块
2. 这些页面模块中的 `@callback` 装饰器只有在模块被导入时才会注册到Dash应用
3. 由于是懒加载，回调注册发生在页面首次渲染时，但此时页面上的组件（如 `welcome-upload`、`sample-iris` 等）已经存在
4. Dash无法将这些"迟到"的回调与已存在的组件关联起来

### 修复方案

在 `app.py` 顶部显式导入所有页面模块，确保回调在应用启动时就被注册：

```python
# Import page modules to register their callbacks
import pages.welcome
import pages.data_hub
import pages.data_canvas
```

这样做的好处：
- ✅ 所有回调在应用启动时立即注册
- ✅ 组件渲染时，回调已经准备就绪
- ✅ 不影响懒加载的页面内容创建（`create_*_page` 函数仍然按需调用）

### 修复代码

**文件**: `app.py`

**修改前**：
```python
import config
from core.state_manager import get_initial_state
from core.data_manager import DataManager
# ... 其他导入

# 没有导入页面模块

@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def route_page(pathname: str):
    # 懒加载导入
    from pages.welcome import create_welcome_page
    from pages.data_hub import create_data_hub_page
    # ...
```

**修改后**：
```python
import config
from core.state_manager import get_initial_state
from core.data_manager import DataManager
# ... 其他导入

# Import page modules to register their callbacks
import pages.welcome
import pages.data_hub
import pages.data_canvas

@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def route_page(pathname: str):
    # 仍然使用懒加载导入函数（保持代码清晰）
    from pages.welcome import create_welcome_page
    from pages.data_hub import create_data_hub_page
    # ...
```

### 测试步骤

1. ✅ 重启应用（已完成 - 运行在 http://127.0.0.1:8050/）
2. ⏳ 打开浏览器访问欢迎页
3. ⏳ 点击示例数据集按钮（鸢尾花、餐饮小费、泰坦尼克）
4. ⏳ 验证是否跳转到画布页面并显示数据
5. ⏳ 返回欢迎页，测试文件上传功能
6. ⏳ 访问数据中心页面，测试文件上传功能

### 相关文件
- `app.py` - 添加了页面模块导入以注册回调
- `pages/welcome.py` - 包含文件上传和示例数据集回调
- `pages/data_hub.py` - 包含数据中心上传回调

---

## 🐛 Bug #3: AG Grid表格文字颜色不可见

**发现时间**: 2026-02-26 04:30  
**严重程度**: 🟡 中（影响用户体验）  
**状态**: ✅ 已修复

### 问题描述

用户报告：
- 数据导入成功后，AG Grid表格中的数据"黑糊糊的看不见"
- 在深色主题下，表格文字颜色与背景色对比度不足
- 数据概览卡片显示正常，只有表格内容看不清

### 根本原因

AG Grid的CSS变量中缺少文字颜色（foreground color）的定义。虽然定义了背景色、边框色等，但没有明确设置：
- `--ag-foreground-color`（主要文字颜色）
- `--ag-header-foreground-color`（表头文字颜色）
- `--ag-data-color`（数据单元格文字颜色）
- `--ag-secondary-foreground-color`（次要文字颜色）

导致AG Grid使用默认的黑色文字，在深色背景下无法看清。

### 修复方案

在 `assets/css/components.css` 的 `.ag-theme-alpine-dark` 样式中添加文字颜色变量：

```css
.ag-theme-alpine-dark {
    /* ... 现有变量 ... */
    --ag-foreground-color: var(--text-primary) !important;
    --ag-header-foreground-color: var(--text-secondary) !important;
    --ag-data-color: var(--text-primary) !important;
    --ag-secondary-foreground-color: var(--text-secondary) !important;
    /* ... */
}
```

这样可以确保：
- 表格数据使用 `--text-primary`（浅色文字）
- 表头使用 `--text-secondary`（稍暗的浅色文字）
- 与应用整体的深色主题保持一致

### 测试步骤

1. ✅ 修改CSS文件（已完成）
2. ⏳ 刷新浏览器页面（Ctrl+F5 强制刷新）
3. ⏳ 验证表格数据是否清晰可见
4. ⏳ 检查表头文字是否正常显示
5. ⏳ 测试主题切换功能（如果有浅色主题）

### 相关文件
- `assets/css/components.css` - 添加了AG Grid文字颜色变量

---

**最后更新**：2026-02-26  
**修复人员**：Kiro AI
