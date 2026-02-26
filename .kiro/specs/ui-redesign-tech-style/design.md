# Design Document: UI重设计 - 科技感风格

## Overview

本设计文档详细说明DataViz Studio的UI重设计技术方案，将界面升级为现代科技感风格。设计采用深空黑配色方案、玻璃拟态视觉效果和流畅动画系统，同时优化数据预览控制功能，提升用户体验和视觉吸引力。

### Design Goals

1. **视觉现代化**: 采用科技感配色和玻璃拟态效果，打造专业现代的视觉体验
2. **交互流畅性**: 实现平滑的动画过渡和即时的视觉反馈
3. **功能增强**: 优化数据预览控制，提供更灵活的数据查看方式
4. **可维护性**: 建立清晰的CSS架构和设计系统，便于后续扩展
5. **响应式适配**: 确保在不同设备和屏幕尺寸上都有良好体验
6. **可访问性**: 保持足够的对比度和可操作性，支持无障碍访问

### Key Features

- 科技感配色方案（深空黑 + 科技蓝 + 荧光青）
- 玻璃拟态视觉效果（半透明背景 + 背景模糊 + 发光边框）
- 统一的动画系统（0.3s过渡 + ease-in-out缓动）
- 增强的数据预览控制（前N行/中间N行/后N行/全部数据 + 自定义N值）
- 响应式布局系统（支持桌面/平板/移动设备）
- 规范的栅格系统（8px基础单位）

## Architecture

### System Architecture

```
DataViz Studio UI System
│
├── Style System (CSS层)
│   ├── base.css - 基础样式和设计令牌
│   │   ├── CSS Reset
│   │   ├── CSS Custom Properties (设计令牌)
│   │   ├── Typography System
│   │   ├── Grid System (8px基础单位)
│   │   └── Utility Classes
│   │
│   ├── themes.css - 主题系统
│   │   ├── Dark Theme (默认 - 科技感配色)
│   │   └── Light Theme (可选)
│   │
│   └── components.css - 组件样式
│       ├── Layout Components (Sidebar, Topbar, Content)
│       ├── UI Components (Button, Card, Badge)
│       ├── Data Components (Table, Stats)
│       └── Feedback Components (Toast, Loading)
│
├── Component Layer (Python/Dash组件)
│   ├── Layout Components
│   │   ├── sidebar.py - 侧边栏（支持折叠/展开）
│   │   ├── navbar.py - 顶部导航栏
│   │   └── statusbar.py - 底部状态栏
│   │
│   ├── Data Components
│   │   └── data_table.py - 数据表格组件
│   │
│   └── Page Components
│       ├── welcome.py - 欢迎页
│       ├── data_hub.py - 数据中心
│       └── data_canvas.py - 数据画布（包含新的预览控制）
│
└── State Management
    ├── Browser Session Storage - 侧边栏状态持久化
    └── Dash Store - 应用状态管理
```

### Design System Architecture

设计系统采用分层架构，从底层的设计令牌到顶层的组件样式：

```
Layer 4: Components (具体组件样式)
         ↑
Layer 3: Patterns (设计模式 - 玻璃拟态、动画)
         ↑
Layer 2: Semantic Tokens (语义化令牌 - 颜色、间距、字体)
         ↑
Layer 1: Design Tokens (基础令牌 - CSS Custom Properties)
```

### CSS Architecture

采用模块化CSS架构，遵循以下原则：

1. **关注点分离**: base.css处理基础，themes.css处理主题，components.css处理组件
2. **CSS Custom Properties**: 所有设计令牌使用CSS变量，便于主题切换和维护
3. **BEM命名规范**: 组件样式使用BEM命名，提高可读性和可维护性
4. **渐进增强**: 基础功能在所有浏览器可用，高级效果（如backdrop-filter）提供降级方案

## Components and Interfaces

### 1. Data Preview Control Component

#### Component Structure

```python
# 在 pages/data_canvas.py 中实现

html.Div(
    className="dvs-preview-control",
    children=[
        html.Div(
            className="dvs-preview-control__header",
            children=[
                html.Span("数据预览", className="dvs-preview-control__title"),
                html.Div(
                    className="dvs-preview-control__n-input-group",
                    children=[
                        html.Label("显示行数:", className="dvs-preview-control__label"),
                        dcc.Input(
                            id="preview-n-value",
                            type="number",
                            value=10,
                            min=1,
                            className="dvs-preview-control__input",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="dvs-preview-control__buttons",
            children=[
                html.Button("前 N 行", id="btn-view-head", className="dvs-btn dvs-btn--sm dvs-btn--primary"),
                html.Button("中间 N 行", id="btn-view-middle", className="dvs-btn dvs-btn--sm"),
                html.Button("后 N 行", id="btn-view-tail", className="dvs-btn dvs-btn--sm"),
                html.Button("全部数据", id="btn-view-all", className="dvs-btn dvs-btn--sm"),
            ],
        ),
        html.Div(id="preview-warning", className="dvs-preview-control__warning"),
    ],
)
```

#### Component Behavior

**N值输入验证**:
- 接受正整数输入
- 拒绝负数、零、小数和非数字输入
- 实时验证并显示错误提示

**预览模式**:
- **前N行**: 显示 `df.head(n)`
- **中间N行**: 显示 `df.iloc[start:end]`，其中 `start = (total_rows - n) // 2`
- **后N行**: 显示 `df.tail(n)`
- **全部数据**: 显示 `df`（忽略N值）

**边界情况处理**:
- 当 N > 总行数时，显示所有行并显示警告消息
- 当数据集为空时，显示空状态提示
- 当数据加载失败时，显示错误状态

#### State Management

```python
# Callback signature
@callback(
    Output("canvas-table-container", "children"),
    Output("preview-warning", "children"),
    Input("btn-view-head", "n_clicks"),
    Input("btn-view-middle", "n_clicks"),
    Input("btn-view-tail", "n_clicks"),
    Input("btn-view-all", "n_clicks"),
    State("preview-n-value", "value"),
    State("app-store", "data"),
)
def update_preview(n_head, n_middle, n_tail, n_all, n_value, store_data):
    """更新数据预览显示"""
    # 1. 验证 n_value
    # 2. 确定触发的按钮
    # 3. 根据模式切片数据
    # 4. 生成警告消息（如果需要）
    # 5. 返回表格和警告
```

### 2. Glassmorphism Component Pattern

#### CSS Implementation

```css
/* 玻璃拟态基础样式 */
.dvs-glass {
    background: rgba(15, 23, 42, 0.7);  /* 半透明深色背景 */
    backdrop-filter: blur(12px);         /* 背景模糊 */
    -webkit-backdrop-filter: blur(12px); /* Safari支持 */
    border: 1px solid rgba(14, 165, 233, 0.3);  /* 半透明发光边框 */
    border-radius: 12px;
    box-shadow: 0 0 15px rgba(14, 165, 233, 0.15);  /* 外发光 */
    transition: all 0.3s ease-in-out;
}

.dvs-glass:hover {
    border-color: rgba(14, 165, 233, 0.5);  /* 悬停时边框更亮 */
    box-shadow: 0 0 20px rgba(14, 165, 233, 0.25);
}

/* 降级方案（不支持backdrop-filter的浏览器） */
@supports not (backdrop-filter: blur(12px)) {
    .dvs-glass {
        background: rgba(15, 23, 42, 0.95);  /* 更不透明的背景 */
    }
}
```

#### Application

玻璃拟态效果应用于以下组件：
- 卡片组件 (`.dvs-card`)
- 统计卡片 (`.dvs-stat-card`)
- 侧边栏 (`.dvs-sidebar`)
- 顶部导航栏 (`.dvs-topbar`)
- 模态框和弹出层

### 3. Animation System

#### Transition Configuration

```css
:root {
    /* 动画时长 */
    --transition-fast: 150ms ease-in-out;
    --transition-base: 200ms ease-in-out;
    --transition-slow: 300ms ease-in-out;
    
    /* 缓动函数 */
    --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
    --ease-out: cubic-bezier(0, 0, 0.2, 1);
    --ease-in: cubic-bezier(0.4, 0, 1, 1);
}
```

#### Animation Patterns

**1. 状态过渡动画**:
```css
.dvs-btn {
    transition: all var(--transition-fast);
}

.dvs-btn:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-glow);
}
```

**2. 加载动画**:
```css
@keyframes dvs-pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.dvs-loading {
    animation: dvs-pulse 1.5s ease-in-out infinite;
}
```

**3. 侧边栏折叠动画**:
```css
.dvs-sidebar {
    width: var(--sidebar-width);
    transition: width var(--transition-slow);
}

.dvs-sidebar--collapsed {
    width: var(--sidebar-collapsed);
}
```

#### Accessibility

```css
/* 尊重用户的动画偏好 */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### 4. Responsive Layout System

#### Breakpoints

```css
:root {
    --breakpoint-mobile: 768px;
    --breakpoint-tablet: 1024px;
    --breakpoint-desktop: 1280px;
}
```

#### Media Queries

```css
/* Mobile First Approach */

/* 基础样式 - Mobile (<768px) */
.dvs-content {
    padding: var(--sp-4);
}

/* Tablet (768px - 1023px) */
@media (min-width: 768px) {
    .dvs-content {
        padding: var(--sp-5);
    }
}

/* Desktop (≥1024px) */
@media (min-width: 1024px) {
    .dvs-content {
        padding: var(--sp-6);
    }
}
```

#### Touch Target Sizing

```css
/* 移动设备上的触摸目标最小尺寸 */
@media (max-width: 767px) {
    .dvs-btn,
    .dvs-sidebar__item,
    .dvs-topbar__btn {
        min-height: 44px;
        min-width: 44px;
    }
}
```

## Data Models

### CSS Custom Properties (Design Tokens)

#### Color Tokens

```css
:root {
    /* 背景色 */
    --bg-primary: #0F172A;      /* 深空黑 - 主背景 */
    --bg-secondary: #1B1D2A;    /* 次级背景 - 卡片、侧边栏 */
    --bg-tertiary: #262940;     /* 三级背景 - 悬停状态 */
    
    /* 强调色 */
    --accent-primary: #0EA5E9;  /* 科技蓝 - 主强调色 */
    --accent-secondary: #22D3EE; /* 荧光青 - 次强调色 */
    --accent-hover: #38BDF8;    /* 悬停状态 */
    
    /* 文本色 */
    --text-primary: #F1F5F9;    /* 主文本 */
    --text-secondary: #94A3B8;  /* 次要文本 */
    --text-muted: #64748B;      /* 弱化文本 */
    
    /* 语义色 */
    --success: #10B981;
    --warning: #F59E0B;
    --error: #EF4444;
    --info: #3B82F6;
    
    /* 边框色 */
    --border: #2E3348;
    --border-hover: #404668;
    --border-glow: rgba(14, 165, 233, 0.3);
}
```

#### Spacing Tokens

```css
:root {
    /* 基础单位: 8px */
    --sp-base: 8px;
    
    /* 间距刻度 */
    --sp-1: 4px;    /* 0.5x */
    --sp-2: 8px;    /* 1x - 基础单位 */
    --sp-3: 12px;   /* 1.5x */
    --sp-4: 16px;   /* 2x */
    --sp-5: 20px;   /* 2.5x */
    --sp-6: 24px;   /* 3x */
    --sp-8: 32px;   /* 4x */
    --sp-10: 40px;  /* 5x */
    --sp-12: 48px;  /* 6x */
}
```

#### Typography Tokens

```css
:root {
    /* 字体家族 */
    --font-sans: 'Inter', -apple-system, 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
    --font-mono: 'Roboto Mono', 'JetBrains Mono', 'Consolas', monospace;
    
    /* 字体大小刻度 (1.125比例) */
    --text-xs: 0.75rem;     /* 12px */
    --text-sm: 0.875rem;    /* 14px */
    --text-base: 1rem;      /* 16px */
    --text-md: 1.125rem;    /* 18px */
    --text-lg: 1.25rem;     /* 20px */
    --text-xl: 1.5rem;      /* 24px */
    --text-2xl: 1.875rem;   /* 30px */
    
    /* 字重 */
    --font-normal: 400;
    --font-medium: 500;
    --font-semibold: 600;
    --font-bold: 700;
}
```

#### Shadow Tokens

```css
:root {
    /* 阴影 */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
    
    /* 发光效果 */
    --shadow-glow-sm: 0 0 10px rgba(14, 165, 233, 0.15);
    --shadow-glow-md: 0 0 15px rgba(14, 165, 233, 0.25);
    --shadow-glow-lg: 0 0 20px rgba(14, 165, 233, 0.35);
}
```

### Component State Model

#### Preview Control State

```python
@dataclass
class PreviewControlState:
    """数据预览控制状态"""
    n_value: int = 10           # 显示行数
    mode: str = "head"          # 预览模式: "head" | "middle" | "tail" | "all"
    total_rows: int = 0         # 数据集总行数
    warning_message: str = ""   # 警告消息
    
    def validate_n_value(self) -> bool:
        """验证N值是否有效"""
        return isinstance(self.n_value, int) and self.n_value > 0
    
    def should_show_warning(self) -> bool:
        """判断是否需要显示警告"""
        return self.n_value > self.total_rows
    
    def get_slice_range(self) -> tuple[int, int]:
        """获取数据切片范围"""
        if self.mode == "all":
            return (0, self.total_rows)
        elif self.mode == "head":
            return (0, min(self.n_value, self.total_rows))
        elif self.mode == "tail":
            start = max(0, self.total_rows - self.n_value)
            return (start, self.total_rows)
        elif self.mode == "middle":
            start = max(0, (self.total_rows - self.n_value) // 2)
            end = min(self.total_rows, start + self.n_value)
            return (start, end)
        return (0, 0)
```

#### Sidebar State Model

```python
@dataclass
class SidebarState:
    """侧边栏状态"""
    collapsed: bool = False     # 是否折叠
    active_item: str = ""       # 当前激活的导航项
    
    def toggle(self) -> None:
        """切换折叠状态"""
        self.collapsed = not self.collapsed
    
    def get_width(self) -> str:
        """获取侧边栏宽度"""
        return "var(--sidebar-collapsed)" if self.collapsed else "var(--sidebar-width)"
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: N值输入验证

*For any* input value to the N_Value field, the system should accept only positive integers and reject negative numbers, zero, decimals, and non-numeric inputs.

**Validates: Requirements 1.3**

### Property 2: 前N行显示正确性

*For any* dataset and any valid N value, clicking "前N行" should display exactly the first min(N, total_rows) rows of the dataset.

**Validates: Requirements 1.4**

### Property 3: 中间N行显示正确性

*For any* dataset and any valid N value, clicking "中间N行" should display N rows from the middle of the dataset, calculated as rows from index `(total_rows - N) // 2` to `(total_rows - N) // 2 + N`.

**Validates: Requirements 1.5**

### Property 4: 后N行显示正确性

*For any* dataset and any valid N value, clicking "后N行" should display exactly the last min(N, total_rows) rows of the dataset.

**Validates: Requirements 1.6**

### Property 5: 全部数据显示独立性

*For any* dataset and any N value, clicking "全部数据" should display all rows of the dataset, completely ignoring the N value.

**Validates: Requirements 1.7**

### Property 6: N值状态持久性

*For any* sequence of button clicks (前N行/中间N行/后N行/全部数据), the N value should remain unchanged unless explicitly modified by the user.

**Validates: Requirements 1.8**

### Property 7: 文本对比度可访问性

*For all* text elements in the UI, the contrast ratio between text color and background color should be at least 4.5:1 to meet WCAG AA accessibility standards.

**Validates: Requirements 2.5**

### Property 8: 颜色令牌一致性

*For all* color values used in the CSS, they should be defined as CSS custom properties rather than hardcoded hex/rgb values, ensuring theme consistency.

**Validates: Requirements 2.7**

### Property 9: 玻璃拟态背景效果

*For all* components with glassmorphism styling, they should have semi-transparent background with `backdrop-filter: blur()` applied.

**Validates: Requirements 3.1**

### Property 10: 玻璃拟态边框规范

*For all* glassmorphism components, they should have a border width between 1-2px using accent colors.

**Validates: Requirements 3.2**

### Property 11: 卡片圆角一致性

*For all* card and panel elements, they should have a border-radius of 12px.

**Validates: Requirements 3.4**

### Property 12: Z-index层级正确性

*For all* glassmorphism components, their z-index values should be properly ordered to maintain correct visual layering (e.g., modals > dropdowns > cards).

**Validates: Requirements 3.5**

### Property 13: 悬停边框亮度变化

*For any* glassmorphism component, when hovered, the border color luminosity should increase by approximately 20%.

**Validates: Requirements 3.6**

### Property 14: 标题字重一致性

*For all* heading and title elements (h1-h6, .dvs-page-title, etc.), they should have font-weight of 600.

**Validates: Requirements 4.3**

### Property 15: 正文字重一致性

*For all* body text elements, they should have font-weight of 400.

**Validates: Requirements 4.4**

### Property 16: 字体大小比例一致性

*For all* defined font size tokens, the ratio between consecutive sizes should be consistent (approximately 1.125x scale).

**Validates: Requirements 4.5**

### Property 17: 字体降级方案完整性

*For all* font-family declarations, they should include fallback fonts (e.g., system fonts) after the primary font.

**Validates: Requirements 4.7**

### Property 18: 间距令牌使用一致性

*For all* UI components, spacing values (margin, padding) should use defined spacing tokens (--sp-*) rather than arbitrary pixel values.

**Validates: Requirements 5.4, 5.5**

### Property 19: 响应式间距缩放

*For all* spacing values, they should scale proportionally at different breakpoints (mobile/tablet/desktop) using media queries.

**Validates: Requirements 5.6**

### Property 20: 过渡时长一致性

*For all* CSS transition declarations, they should use the standard 0.3s duration (or defined transition tokens).

**Validates: Requirements 6.1**

### Property 21: 缓动函数一致性

*For all* CSS transition declarations, they should use ease-in-out timing function for smooth motion.

**Validates: Requirements 6.2**

### Property 22: 交互元素悬停动画

*For all* interactive elements (buttons, links, cards), they should have transition properties defined for hover state changes.

**Validates: Requirements 6.3**

### Property 23: 加载状态动画一致性

*For all* loading indicators, they should use the same pulsing animation style.

**Validates: Requirements 6.5, 10.7**

### Property 24: 动画可访问性支持

*For all* animations and transitions, they should be reducible or disabled when `prefers-reduced-motion: reduce` media query is active.

**Validates: Requirements 6.7**

### Property 25: 导航项选中状态高亮

*For any* navigation item in the sidebar, when selected, it should have the active highlight style (luminous border) applied.

**Validates: Requirements 7.3**

### Property 26: 侧边栏状态持久化

*For any* sidebar collapse/expand action, the state should be saved to browser session storage and restored on page reload.

**Validates: Requirements 7.5**

### Property 27: 侧边栏折叠时图标显示

*For any* navigation item, when the sidebar is collapsed, only the icon should be visible (label should be hidden).

**Validates: Requirements 7.6**

### Property 28: 侧边栏状态影响内容区宽度

*For any* sidebar state change (collapse/expand), the main content area width should adjust responsively.

**Validates: Requirements 7.7**

### Property 29: 响应式布局媒体查询

*For all* responsive layout adaptations, they should be implemented using CSS media queries at defined breakpoints.

**Validates: Requirements 8.5**

### Property 30: 移动端触摸目标尺寸

*For all* interactive elements on mobile devices (<768px), they should have a minimum size of 44x44px for touch accessibility.

**Validates: Requirements 8.6**

### Property 31: 主题值使用CSS变量

*For all* theme-related values (colors, shadows, etc.), they should be defined as CSS custom properties.

**Validates: Requirements 9.4**

### Property 32: CSS类命名规范一致性

*For all* CSS class names, they should follow BEM or similar consistent naming convention (e.g., block__element--modifier).

**Validates: Requirements 9.5**

### Property 33: CSS文件注释文档化

*For all* major sections in CSS files, they should have descriptive comments explaining their purpose.

**Validates: Requirements 9.6**

### Property 34: 加载指示器显示规则

*For any* loading state, a pulsing animation indicator should be displayed.

**Validates: Requirements 10.1**

### Property 35: 加载指示器位置关联性

*For any* loading indicator, it should be positioned near or within the content area that is being loaded.

**Validates: Requirements 10.2**

### Property 36: 加载消息颜色规范

*For all* loading messages, they should use accent colors for visual consistency.

**Validates: Requirements 10.3**

### Property 37: 加载动画非阻塞性

*For all* loading indicators, they should not block user interaction with other areas of the interface (no full-screen blocking overlays unless explicitly required).

**Validates: Requirements 10.5**


## Error Handling

### Input Validation Errors

#### N值输入验证

**错误场景**:
- 用户输入负数
- 用户输入零
- 用户输入小数
- 用户输入非数字字符

**处理策略**:
```python
def validate_n_value(n_value: Any) -> tuple[bool, str]:
    """验证N值输入
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(n_value, (int, float)):
        return False, "请输入数字"
    
    if isinstance(n_value, float) and not n_value.is_integer():
        return False, "请输入整数"
    
    n = int(n_value)
    if n <= 0:
        return False, "行数必须大于0"
    
    return True, ""
```

**用户反馈**:
- 在输入框下方显示红色错误提示
- 禁用预览按钮直到输入有效
- 使用 `--error` 颜色和 `.text-error` 类

### Data Boundary Errors

#### N值超出数据集范围

**错误场景**:
- N值大于数据集总行数

**处理策略**:
```python
def handle_n_exceeds_total(n_value: int, total_rows: int) -> dict:
    """处理N值超出总行数的情况
    
    Returns:
        {
            "display_rows": int,  # 实际显示的行数
            "warning": str,       # 警告消息
        }
    """
    return {
        "display_rows": total_rows,
        "warning": f"⚠️ 数据集仅有 {total_rows} 行，已显示全部数据"
    }
```

**用户反馈**:
- 显示所有可用行
- 在表格上方显示黄色警告横幅
- 使用 `--warning` 颜色和 `.dvs-toast--warning` 样式

#### 空数据集

**错误场景**:
- 数据集为空（0行）

**处理策略**:
```python
def handle_empty_dataset() -> html.Div:
    """处理空数据集"""
    return html.Div(
        className="dvs-empty",
        children=[
            html.Div("📭", className="dvs-empty__icon"),
            html.Div("数据集为空", className="dvs-empty__text"),
            html.Div("请加载包含数据的文件", className="dvs-empty__sub"),
        ],
    )
```

### CSS Compatibility Errors

#### backdrop-filter不支持

**错误场景**:
- 浏览器不支持 `backdrop-filter` 属性（主要是Firefox旧版本）

**处理策略**:
```css
/* 降级方案 */
.dvs-glass {
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(12px);
}

@supports not (backdrop-filter: blur(12px)) {
    .dvs-glass {
        background: rgba(15, 23, 42, 0.95);  /* 更不透明 */
    }
}
```

**用户影响**:
- 玻璃拟态效果降级为半透明背景
- 功能完全可用，仅视觉效果略有差异

### State Management Errors

#### Session Storage不可用

**错误场景**:
- 浏览器禁用了localStorage/sessionStorage
- 隐私模式下存储受限

**处理策略**:
```javascript
function saveSidebarState(collapsed) {
    try {
        sessionStorage.setItem('sidebar-collapsed', collapsed);
    } catch (e) {
        console.warn('Session storage unavailable:', e);
        // 降级：仅在内存中保持状态
    }
}

function loadSidebarState() {
    try {
        return sessionStorage.getItem('sidebar-collapsed') === 'true';
    } catch (e) {
        console.warn('Session storage unavailable:', e);
        return false;  // 默认展开
    }
}
```

**用户影响**:
- 侧边栏状态不会在页面刷新后保持
- 功能正常，仅失去持久化能力

### Animation Performance Errors

#### 低性能设备

**错误场景**:
- 设备性能不足，动画卡顿

**处理策略**:
```css
/* 用户可以通过系统设置禁用动画 */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

**用户影响**:
- 动画被禁用或大幅简化
- 功能完全可用，仅失去动画效果

### Error Display Components

#### Toast通知

```python
def show_error_toast(message: str) -> html.Div:
    """显示错误Toast"""
    return html.Div(
        className="dvs-toast dvs-toast--error",
        children=[
            html.Span("❌", style={"fontSize": "1.2rem"}),
            html.Span(message, style={"flex": "1"}),
        ],
    )
```

#### 内联错误提示

```python
def show_inline_error(message: str) -> html.Div:
    """显示内联错误提示"""
    return html.Div(
        className="dvs-error-message",
        style={
            "color": "var(--error)",
            "fontSize": "var(--text-xs)",
            "marginTop": "var(--sp-1)",
        },
        children=message,
    )
```


## Testing Strategy

### Overview

本项目采用双重测试策略，结合单元测试和属性测试，确保UI重设计的正确性和可靠性。

**测试方法**:
- **单元测试**: 验证特定示例、边界情况和错误条件
- **属性测试**: 验证跨所有输入的通用属性
- **视觉回归测试**: 确保UI变更不会破坏现有视觉效果
- **可访问性测试**: 验证WCAG合规性

### Property-Based Testing

#### 测试库选择

**Python**: 使用 `hypothesis` 库进行属性测试

```bash
pip install hypothesis pytest
```

#### 配置要求

- 每个属性测试最少运行 100 次迭代
- 每个测试必须引用设计文档中的属性编号
- 标签格式: `# Feature: ui-redesign-tech-style, Property {number}: {property_text}`

#### 示例属性测试

**Property 2: 前N行显示正确性**

```python
from hypothesis import given, strategies as st
import pandas as pd
import pytest

@given(
    n_rows=st.integers(min_value=10, max_value=1000),
    n_value=st.integers(min_value=1, max_value=100)
)
@pytest.mark.property_test
def test_head_preview_correctness(n_rows, n_value):
    """
    Feature: ui-redesign-tech-style, Property 2: 前N行显示正确性
    
    For any dataset and any valid N value, clicking "前N行" should display 
    exactly the first min(N, total_rows) rows of the dataset.
    """
    # 生成随机数据集
    df = pd.DataFrame({
        'col1': range(n_rows),
        'col2': range(n_rows, n_rows * 2)
    })
    
    # 执行前N行预览
    result = get_preview_data(df, mode="head", n=n_value)
    
    # 验证
    expected_rows = min(n_value, n_rows)
    assert len(result) == expected_rows
    assert result.equals(df.head(expected_rows))
```

**Property 3: 中间N行显示正确性**

```python
@given(
    n_rows=st.integers(min_value=10, max_value=1000),
    n_value=st.integers(min_value=1, max_value=100)
)
@pytest.mark.property_test
def test_middle_preview_correctness(n_rows, n_value):
    """
    Feature: ui-redesign-tech-style, Property 3: 中间N行显示正确性
    
    For any dataset and any valid N value, clicking "中间N行" should display 
    N rows from the middle of the dataset.
    """
    df = pd.DataFrame({'col': range(n_rows)})
    
    result = get_preview_data(df, mode="middle", n=n_value)
    
    # 计算期望的中间位置
    start = max(0, (n_rows - n_value) // 2)
    end = min(n_rows, start + n_value)
    expected = df.iloc[start:end]
    
    assert len(result) == len(expected)
    assert result.equals(expected)
```

**Property 7: 文本对比度可访问性**

```python
from hypothesis import given, strategies as st
from colour import Color

def calculate_contrast_ratio(fg_color: str, bg_color: str) -> float:
    """计算对比度比率"""
    fg = Color(fg_color)
    bg = Color(bg_color)
    
    # 计算相对亮度
    def get_luminance(color):
        rgb = [color.red, color.green, color.blue]
        rgb = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb]
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    
    l1 = get_luminance(fg)
    l2 = get_luminance(bg)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)

@pytest.mark.property_test
def test_text_contrast_accessibility():
    """
    Feature: ui-redesign-tech-style, Property 7: 文本对比度可访问性
    
    For all text elements in the UI, the contrast ratio between text color 
    and background color should be at least 4.5:1.
    """
    # 定义所有文本/背景组合
    text_bg_pairs = [
        ("--text-primary", "--bg-primary"),
        ("--text-primary", "--bg-secondary"),
        ("--text-secondary", "--bg-primary"),
        ("--text-secondary", "--bg-secondary"),
    ]
    
    # 从CSS中读取实际颜色值
    colors = parse_css_variables("assets/css/base.css")
    
    for text_var, bg_var in text_bg_pairs:
        text_color = colors[text_var]
        bg_color = colors[bg_var]
        
        ratio = calculate_contrast_ratio(text_color, bg_color)
        
        assert ratio >= 4.5, (
            f"Contrast ratio {ratio:.2f} for {text_var} on {bg_var} "
            f"is below WCAG AA standard (4.5:1)"
        )
```

### Unit Testing

#### 功能单元测试

**测试N值验证**

```python
import pytest

def test_n_value_validation_positive_integer():
    """测试正整数输入被接受"""
    is_valid, error = validate_n_value(10)
    assert is_valid is True
    assert error == ""

def test_n_value_validation_negative():
    """测试负数被拒绝"""
    is_valid, error = validate_n_value(-5)
    assert is_valid is False
    assert "必须大于0" in error

def test_n_value_validation_zero():
    """测试零被拒绝"""
    is_valid, error = validate_n_value(0)
    assert is_valid is False
    assert "必须大于0" in error

def test_n_value_validation_decimal():
    """测试小数被拒绝"""
    is_valid, error = validate_n_value(10.5)
    assert is_valid is False
    assert "整数" in error

def test_n_value_validation_non_numeric():
    """测试非数字被拒绝"""
    is_valid, error = validate_n_value("abc")
    assert is_valid is False
    assert "数字" in error
```

**测试边界情况**

```python
def test_n_exceeds_total_rows():
    """测试N值超出总行数的边界情况"""
    df = pd.DataFrame({'col': range(5)})
    n_value = 10
    
    result = get_preview_data(df, mode="head", n=n_value)
    warning = check_n_exceeds_warning(n_value, len(df))
    
    # 应该显示所有可用行
    assert len(result) == 5
    # 应该有警告消息
    assert warning is not None
    assert "仅有 5 行" in warning

def test_empty_dataset():
    """测试空数据集"""
    df = pd.DataFrame()
    
    result = get_preview_data(df, mode="head", n=10)
    
    assert len(result) == 0
```

#### CSS测试

**测试CSS变量定义**

```python
import re

def test_color_tokens_defined():
    """测试所有颜色令牌已定义"""
    # Feature: ui-redesign-tech-style, Property 8: 颜色令牌一致性
    
    with open("assets/css/base.css", "r") as f:
        content = f.read()
    
    required_colors = [
        "--bg-primary",
        "--bg-secondary",
        "--accent-primary",
        "--accent-secondary",
        "--text-primary",
        "--text-secondary",
    ]
    
    for color in required_colors:
        assert f"{color}:" in content, f"Color token {color} not defined"

def test_spacing_tokens_use_8px_base():
    """测试间距令牌使用8px基础单位"""
    # Feature: ui-redesign-tech-style, Property 18: 间距令牌使用一致性
    
    with open("assets/css/base.css", "r") as f:
        content = f.read()
    
    # 提取所有 --sp-* 变量
    spacing_pattern = r'--sp-\d+:\s*(\d+)px'
    spacings = re.findall(spacing_pattern, content)
    
    for spacing in spacings:
        value = int(spacing)
        # 所有间距应该是4的倍数（8px基础单位的一半或倍数）
        assert value % 4 == 0, f"Spacing {value}px is not a multiple of 4"

def test_glassmorphism_properties():
    """测试玻璃拟态效果属性"""
    # Feature: ui-redesign-tech-style, Property 9: 玻璃拟态背景效果
    
    with open("assets/css/components.css", "r") as f:
        content = f.read()
    
    # 查找玻璃拟态类
    glass_section = extract_css_rule(content, ".dvs-glass")
    
    assert "backdrop-filter" in glass_section
    assert "blur" in glass_section
    assert "rgba" in glass_section  # 半透明背景
```

### Visual Regression Testing

#### 工具选择

使用 `playwright` 进行视觉回归测试

```bash
pip install playwright pytest-playwright
playwright install
```

#### 视觉测试示例

```python
from playwright.sync_api import Page, expect

def test_glassmorphism_visual(page: Page):
    """测试玻璃拟态效果的视觉呈现"""
    page.goto("http://localhost:8050")
    
    # 截取卡片组件
    card = page.locator(".dvs-card").first
    screenshot = card.screenshot()
    
    # 与基准图像比较
    expect(card).to_have_screenshot("card-glassmorphism.png")

def test_sidebar_collapse_animation(page: Page):
    """测试侧边栏折叠动画"""
    page.goto("http://localhost:8050")
    
    # 初始状态
    sidebar = page.locator(".dvs-sidebar")
    initial_width = sidebar.bounding_box()["width"]
    
    # 点击折叠按钮
    page.locator("#sidebar-toggle").click()
    
    # 等待动画完成
    page.wait_for_timeout(300)
    
    # 验证宽度变化
    collapsed_width = sidebar.bounding_box()["width"]
    assert collapsed_width < initial_width
    
    # 截图验证
    expect(sidebar).to_have_screenshot("sidebar-collapsed.png")

def test_responsive_layout_mobile(page: Page):
    """测试移动端响应式布局"""
    # 设置移动设备视口
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:8050")
    
    # 验证触摸目标尺寸
    buttons = page.locator(".dvs-btn").all()
    for button in buttons:
        box = button.bounding_box()
        assert box["width"] >= 44, "Touch target too small"
        assert box["height"] >= 44, "Touch target too small"
```

### Accessibility Testing

#### 自动化可访问性测试

```python
from axe_playwright_python import Axe

def test_accessibility_compliance(page: Page):
    """测试WCAG可访问性合规性"""
    page.goto("http://localhost:8050")
    
    # 运行axe可访问性检查
    axe = Axe()
    results = axe.run(page)
    
    # 验证没有严重违规
    assert len(results.violations) == 0, (
        f"Accessibility violations found: {results.violations}"
    )

def test_keyboard_navigation(page: Page):
    """测试键盘导航"""
    page.goto("http://localhost:8050")
    
    # Tab键导航
    page.keyboard.press("Tab")
    
    # 验证焦点可见
    focused = page.evaluate("document.activeElement.className")
    assert "dvs-" in focused, "Focus not on app element"
    
    # 继续Tab导航所有交互元素
    interactive_elements = page.locator("button, a, input").all()
    for _ in range(len(interactive_elements)):
        page.keyboard.press("Tab")
        # 验证焦点环可见
        focused_element = page.evaluate("document.activeElement")
        assert focused_element is not None
```

### Performance Testing

#### 动画性能测试

```python
def test_animation_performance(page: Page):
    """测试动画性能（60fps目标）"""
    page.goto("http://localhost:8050")
    
    # 开始性能追踪
    page.evaluate("performance.mark('animation-start')")
    
    # 触发侧边栏动画
    page.locator("#sidebar-toggle").click()
    
    # 等待动画完成
    page.wait_for_timeout(300)
    
    page.evaluate("performance.mark('animation-end')")
    page.evaluate("""
        performance.measure('animation', 'animation-start', 'animation-end')
    """)
    
    # 获取性能指标
    metrics = page.evaluate("""
        performance.getEntriesByName('animation')[0].duration
    """)
    
    # 验证动画在预期时间内完成
    assert metrics <= 350, f"Animation took {metrics}ms, expected ≤350ms"
```

### Test Organization

```
tests/
├── unit/
│   ├── test_preview_control.py      # 数据预览控制单元测试
│   ├── test_validation.py           # 输入验证测试
│   └── test_css_structure.py        # CSS结构测试
├── property/
│   ├── test_preview_properties.py   # 预览功能属性测试
│   ├── test_style_properties.py     # 样式系统属性测试
│   └── test_responsive_properties.py # 响应式属性测试
├── visual/
│   ├── test_glassmorphism.py        # 玻璃拟态视觉测试
│   ├── test_animations.py           # 动画视觉测试
│   └── test_responsive.py           # 响应式视觉测试
├── accessibility/
│   ├── test_wcag_compliance.py      # WCAG合规性测试
│   └── test_keyboard_nav.py         # 键盘导航测试
└── conftest.py                      # pytest配置
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install hypothesis pytest pytest-playwright
          playwright install
      
      - name: Run unit tests
        run: pytest tests/unit/ -v
      
      - name: Run property tests
        run: pytest tests/property/ -v --hypothesis-show-statistics
      
      - name: Run visual tests
        run: pytest tests/visual/ -v
      
      - name: Run accessibility tests
        run: pytest tests/accessibility/ -v
```

### Test Coverage Goals

- **单元测试覆盖率**: ≥80% 代码覆盖
- **属性测试**: 每个correctness property至少一个测试
- **视觉回归**: 所有主要UI组件有基准截图
- **可访问性**: 零严重WCAG违规


## Implementation Plan

### Phase 1: CSS基础架构更新

**目标**: 建立新的设计系统基础

**任务**:
1. 更新 `base.css`
   - 添加科技感配色CSS变量
   - 定义新的间距令牌（8px基础单位）
   - 更新字体系统（Inter + Roboto Mono）
   - 添加动画令牌

2. 更新 `themes.css`
   - 定义深空黑主题（默认）
   - 保留浅色主题支持
   - 添加玻璃拟态效果变量

3. 创建玻璃拟态工具类
   - `.dvs-glass` 基础类
   - 悬停状态变体
   - 浏览器兼容性降级

**验收标准**:
- 所有颜色使用CSS变量定义
- 间距系统基于8px基础单位
- 字体加载正确且有降级方案
- 玻璃拟态效果在支持的浏览器中正常显示

**预计时间**: 2-3天

### Phase 2: 组件样式更新

**目标**: 应用新设计系统到现有组件

**任务**:
1. 更新布局组件
   - 侧边栏：添加玻璃拟态效果、优化折叠动画
   - 顶部导航栏：应用新配色和边框样式
   - 状态栏：更新颜色和字体

2. 更新UI组件
   - 按钮：新的悬停效果和发光边框
   - 卡片：玻璃拟态效果、圆角12px
   - 统计卡片：科技感数字显示
   - Badge：新配色

3. 更新数据组件
   - AG Grid主题定制
   - 表格边框和悬停效果

4. 添加动画效果
   - 统一过渡时长（0.3s）
   - 悬停动画
   - 加载动画（脉冲效果）

**验收标准**:
- 所有组件应用新的视觉风格
- 动画流畅（60fps）
- 悬停状态有明显反馈
- 在不同主题下正常显示

**预计时间**: 3-4天

### Phase 3: 数据预览控制实现

**目标**: 实现增强的数据预览功能

**任务**:
1. 创建预览控制组件
   - N值输入框（默认10）
   - 四个预览按钮
   - 警告消息区域

2. 实现预览逻辑
   - 前N行：`df.head(n)`
   - 中间N行：计算中间位置切片
   - 后N行：`df.tail(n)`
   - 全部数据：显示完整数据集

3. 添加输入验证
   - 正整数验证
   - 实时错误提示
   - 边界情况处理

4. 实现状态管理
   - N值持久化
   - 预览模式状态
   - 警告消息显示

**验收标准**:
- 四个预览按钮功能正确
- N值验证有效
- 边界情况正确处理
- 用户反馈清晰及时

**预计时间**: 2-3天

### Phase 4: 响应式布局优化

**目标**: 确保在不同设备上的良好体验

**任务**:
1. 定义断点
   - Mobile: <768px
   - Tablet: 768px-1023px
   - Desktop: ≥1024px

2. 实现响应式样式
   - 间距自适应
   - 字体大小调整
   - 组件布局重排

3. 移动端优化
   - 触摸目标≥44px
   - 侧边栏移动端行为
   - 表格横向滚动

4. 测试不同设备
   - 桌面浏览器
   - 平板设备
   - 移动设备

**验收标准**:
- 三个断点正确响应
- 移动端触摸目标符合标准
- 布局在所有尺寸下可用
- 无横向滚动（除表格）

**预计时间**: 2-3天

### Phase 5: 可访问性和性能优化

**目标**: 确保可访问性和性能标准

**任务**:
1. 可访问性改进
   - 验证对比度≥4.5:1
   - 添加ARIA标签
   - 键盘导航支持
   - prefers-reduced-motion支持

2. 性能优化
   - CSS文件压缩
   - 动画性能优化
   - 减少重绘/重排
   - 懒加载优化

3. 浏览器兼容性
   - 测试主流浏览器
   - 添加必要的前缀
   - 提供降级方案

**验收标准**:
- WCAG AA标准合规
- 动画保持60fps
- 主流浏览器兼容
- Lighthouse评分≥90

**预计时间**: 2天

### Phase 6: 测试和文档

**目标**: 完善测试覆盖和文档

**任务**:
1. 编写测试
   - 单元测试（输入验证、数据切片）
   - 属性测试（预览正确性、样式一致性）
   - 视觉回归测试
   - 可访问性测试

2. 更新文档
   - 设计系统文档
   - 组件使用指南
   - CSS变量参考
   - 迁移指南

3. 代码审查
   - CSS代码质量
   - Python代码质量
   - 性能检查
   - 可访问性检查

**验收标准**:
- 测试覆盖率≥80%
- 所有属性有对应测试
- 文档完整准确
- 代码审查通过

**预计时间**: 3-4天

### 总体时间线

- **Phase 1**: 第1-3天
- **Phase 2**: 第4-7天
- **Phase 3**: 第8-10天
- **Phase 4**: 第11-13天
- **Phase 5**: 第14-15天
- **Phase 6**: 第16-19天

**总计**: 约3周（19个工作日）

### 风险和缓解

**风险1**: 浏览器兼容性问题
- **缓解**: 提前测试，准备降级方案，使用autoprefixer

**风险2**: 性能问题（动画卡顿）
- **缓解**: 使用transform和opacity动画，避免layout thrashing

**风险3**: 响应式布局复杂度
- **缓解**: 采用mobile-first方法，渐进增强

**风险4**: 数据预览逻辑边界情况
- **缓解**: 充分的单元测试和属性测试覆盖

## Technical Considerations

### Browser Compatibility

**目标浏览器**:
- Chrome/Edge ≥90
- Firefox ≥88
- Safari ≥14

**关键特性兼容性**:

| 特性 | Chrome | Firefox | Safari | 降级方案 |
|------|--------|---------|--------|----------|
| backdrop-filter | ✅ 76+ | ✅ 103+ | ✅ 9+ | 更不透明的背景 |
| CSS Custom Properties | ✅ 49+ | ✅ 31+ | ✅ 9.1+ | 无需降级 |
| CSS Grid | ✅ 57+ | ✅ 52+ | ✅ 10.1+ | 无需降级 |
| Flexbox | ✅ 29+ | ✅ 28+ | ✅ 9+ | 无需降级 |
| prefers-reduced-motion | ✅ 74+ | ✅ 63+ | ✅ 10.1+ | 默认启用动画 |

### Performance Optimization

**CSS性能**:
- 使用 `transform` 和 `opacity` 进行动画（GPU加速）
- 避免在动画中使用 `width`、`height`、`top`、`left`
- 使用 `will-change` 提示浏览器优化
- 最小化重绘和重排

```css
/* 好的做法 - GPU加速 */
.dvs-sidebar {
    transform: translateX(0);
    transition: transform 0.3s ease-in-out;
}

.dvs-sidebar--collapsed {
    transform: translateX(-160px);
}

/* 避免 - 触发layout */
.dvs-sidebar {
    width: 220px;
    transition: width 0.3s ease-in-out;
}
```

**JavaScript性能**:
- 使用防抖（debounce）处理输入验证
- 避免在回调中进行大量计算
- 使用虚拟化处理大数据集

```python
# 使用Dash的防抖功能
dcc.Input(
    id="preview-n-value",
    type="number",
    debounce=True,  # 等待用户停止输入
)
```

### Security Considerations

**输入验证**:
- 所有用户输入必须验证
- N值必须是正整数
- 防止注入攻击

**CSS安全**:
- 不使用用户输入直接生成CSS
- 避免内联样式（使用类名）

### Accessibility Best Practices

**颜色对比度**:
- 所有文本对比度≥4.5:1（WCAG AA）
- 大文本（≥18pt）对比度≥3:1

**键盘导航**:
- 所有交互元素可通过Tab访问
- 焦点状态清晰可见
- 支持Enter/Space激活

**屏幕阅读器**:
- 使用语义化HTML
- 添加适当的ARIA标签
- 提供替代文本

**动画**:
- 尊重 `prefers-reduced-motion`
- 提供禁用动画选项

## Conclusion

本设计文档详细说明了DataViz Studio UI重设计的技术方案，包括：

1. **完整的设计系统**: 基于CSS变量的可维护设计令牌系统
2. **现代视觉风格**: 科技感配色和玻璃拟态效果
3. **增强的功能**: 灵活的数据预览控制
4. **响应式设计**: 适配多种设备和屏幕尺寸
5. **可访问性**: 符合WCAG AA标准
6. **全面的测试**: 单元测试、属性测试、视觉测试和可访问性测试

通过遵循本设计文档，开发团队可以系统地实现UI重设计，确保代码质量、用户体验和可维护性。

### Next Steps

1. 审查并批准本设计文档
2. 创建详细的任务列表（tasks.md）
3. 开始Phase 1实现
4. 定期进行设计评审和用户测试
5. 根据反馈迭代优化

