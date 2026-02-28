# Week 3: 图表功能增强

## 目标
实现智能字段识别、动态参数面板和新增图表类型。

---

## Day 1-2: 智能字段识别

### 1. 字段类型推断

**文件**: `services/field_analyzer.py`

```python
import pandas as pd
import numpy as np

class FieldAnalyzer:
    """字段分析服务"""
    
    @staticmethod
    def infer_field_type(series):
        """
        推断字段类型
        
        Returns:
            'quantitative' | 'temporal' | 'nominal' | 'ordinal'
        """
        # 数值型
        if pd.api.types.is_numeric_dtype(series):
            return 'quantitative'
        
        # 时间型
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'temporal'
        
        # 尝试转换为日期
        try:
            pd.to_datetime(series.dropna().head(100))
            return 'temporal'
        except:
            pass
        
        # 分类型
        unique_ratio = series.nunique() / len(series)
        if unique_ratio < 0.05:  # 唯一值比例 < 5%
            return 'nominal'
        
        return 'nominal'
    
    @staticmethod
    def infer_role(series):
        """
        推断字段角色
        
        Returns:
            'measure' | 'dimension'
        """
        field_type = FieldAnalyzer.infer_field_type(series)
        
        if field_type == 'quantitative':
            # 数值型默认为度量
            return 'measure'
        else:
            # 其他类型默认为维度
            return 'dimension'
    
    @staticmethod
    def get_field_metadata(df):
        """
        获取所有字段的元数据
        
        Returns:
            List of field metadata dicts
        """
        metadata = []
        
        for col in df.columns:
            series = df[col]
            
            meta = {
                'name': col,
                'type': FieldAnalyzer.infer_field_type(series),
                'role': FieldAnalyzer.infer_role(series),
                'dataType': str(series.dtype),
                'uniqueCount': series.nunique(),
                'nullCount': series.isnull().sum(),
                'nullPercent': series.isnull().sum() / len(series) * 100
            }
            
            # 数值型字段的统计信息
            if meta['type'] == 'quantitative':
                meta['min'] = float(series.min())
                meta['max'] = float(series.max())
                meta['mean'] = float(series.mean())
                meta['median'] = float(series.median())
                meta['std'] = float(series.std())
            
            # 分类型字段的频率信息
            elif meta['type'] in ['nominal', 'ordinal']:
                value_counts = series.value_counts()
                meta['topValues'] = value_counts.head(10).to_dict()
                meta['cardinality'] = len(value_counts)
            
            metadata.append(meta)
        
        return metadata
```

---

### 2. 字段面板组件

**文件**: `components/field_panel.py`

```python
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_field_panel(field_metadata):
    """
    创建字段面板
    
    Args:
        field_metadata: 字段元数据列表
    
    Returns:
        字段面板组件
    """
    # 分组字段
    dimensions = [f for f in field_metadata if f['role'] == 'dimension']
    measures = [f for f in field_metadata if f['role'] == 'measure']
    
    return html.Div([
        # 维度区域
        html.Div([
            html.H6([
                html.I(className="bi bi-tag me-2"),
                "维度 (Dimensions)"
            ], className="field-section-title"),
            
            html.Div([
                create_field_item(field) for field in dimensions
            ], className="field-list"),
        ], className="field-section mb-3"),
        
        # 度量区域
        html.Div([
            html.H6([
                html.I(className="bi bi-bar-chart me-2"),
                "度量 (Measures)"
            ], className="field-section-title"),
            
            html.Div([
                create_field_item(field) for field in measures
            ], className="field-list"),
        ], className="field-section"),
        
    ], className="field-panel")


def create_field_item(field):
    """创建字段项"""
    # 字段图标
    icon_map = {
        'quantitative': '📊',
        'temporal': '📅',
        'nominal': '🔤',
        'ordinal': '🔢'
    }
    icon = icon_map.get(field['type'], '📄')
    
    # 字段信息
    info_text = f"{field['uniqueCount']} 唯一值"
    if field['nullCount'] > 0:
        info_text += f", {field['nullPercent']:.1f}% 缺失"
    
    return html.Div([
        html.Div([
            html.Span(icon, className="field-icon"),
            html.Span(field['name'], className="field-name"),
        ], className="field-header"),
        
        html.Div(info_text, className="field-info text-muted small"),
        
        # 悬停显示详细信息
        dbc.Tooltip(
            create_field_tooltip(field),
            target=f"field-{field['name']}",
        ),
    ], id=f"field-{field['name']}", className="field-item")


def create_field_tooltip(field):
    """创建字段提示信息"""
    lines = [
        f"类型: {field['type']}",
        f"角色: {field['role']}",
        f"数据类型: {field['dataType']}",
        f"唯一值: {field['uniqueCount']}",
    ]
    
    if field['type'] == 'quantitative':
        lines.extend([
            f"最小值: {field['min']:.2f}",
            f"最大值: {field['max']:.2f}",
            f"平均值: {field['mean']:.2f}",
        ])
    
    return html.Div([html.Div(line) for line in lines])
```

---

## Day 3-4: 动态参数面板

### 3. 图表参数配置

**文件**: `services/chart_config.py`

```python
class ChartConfig:
    """图表配置服务"""
    
    # 图表类型参数映射
    CHART_PARAMS = {
        'scatter': {
            'required': ['x', 'y'],
            'optional': ['color', 'size', 'hover_data', 'trendline', 'marginal_x', 'marginal_y'],
            'groups': {
                'basic': ['x', 'y', 'color', 'size'],
                'advanced': ['hover_data', 'trendline'],
                'marginal': ['marginal_x', 'marginal_y']
            }
        },
        'line': {
            'required': ['x', 'y'],
            'optional': ['color', 'line_dash', 'hover_data'],
        },
        'bar': {
            'required': ['x', 'y'],
            'optional': ['color', 'barmode', 'orientation'],
        },
        'pie': {
            'required': ['names', 'values'],
            'optional': ['hole', 'pull'],
        },
        'histogram': {
            'required': ['x'],
            'optional': ['color', 'nbins', 'histnorm'],
        },
        # ... 更多图表类型
    }
    
    @staticmethod
    def get_params_for_chart(chart_type):
        """获取图表类型的参数配置"""
        return ChartConfig.CHART_PARAMS.get(chart_type, {})
    
    @staticmethod
    def validate_params(chart_type, params, field_metadata):
        """
        验证参数
        
        Returns:
            (is_valid, error_message)
        """
        config = ChartConfig.get_params_for_chart(chart_type)
        
        # 检查必需参数
        for param in config.get('required', []):
            if param not in params or params[param] is None:
                return False, f"缺少必需参数: {param}"
        
        # 检查字段类型匹配
        for param, field_name in params.items():
            if field_name is None:
                continue
            
            field = next((f for f in field_metadata if f['name'] == field_name), None)
            if field is None:
                return False, f"字段不存在: {field_name}"
            
            # 验证字段类型
            if param in ['x', 'y'] and chart_type in ['scatter', 'line']:
                if field['type'] not in ['quantitative', 'temporal']:
                    return False, f"{param} 需要数值或时间类型字段"
        
        return True, ""
```

---

### 4. 动态参数面板组件

```python
def create_dynamic_params_panel(chart_type, field_metadata):
    """
    根据图表类型创建动态参数面板
    
    Args:
        chart_type: 图表类型
        field_metadata: 字段元数据
    
    Returns:
        参数面板组件
    """
    config = ChartConfig.get_params_for_chart(chart_type)
    
    # 按字段角色分组
    dimensions = [f['name'] for f in field_metadata if f['role'] == 'dimension']
    measures = [f['name'] for f in field_metadata if f['role'] == 'measure']
    all_fields = [f['name'] for f in field_metadata]
    
    params_components = []
    
    # 必需参数
    if config.get('required'):
        params_components.append(
            html.H6("必需参数", className="params-section-title")
        )
        
        for param in config['required']:
            params_components.append(
                create_param_input(param, all_fields, required=True)
            )
    
    # 可选参数
    if config.get('optional'):
        params_components.append(
            html.H6("可选参数", className="params-section-title mt-3")
        )
        
        for param in config['optional']:
            params_components.append(
                create_param_input(param, all_fields, required=False)
            )
    
    return html.Div(params_components, className="dynamic-params-panel")


def create_param_input(param_name, field_options, required=False):
    """创建参数输入组件"""
    label = param_name.replace('_', ' ').title()
    if required:
        label += " *"
    
    return html.Div([
        html.Label(label, className="form-label"),
        dcc.Dropdown(
            id=f'param-{param_name}',
            options=[{'label': f, 'value': f} for f in field_options],
            placeholder=f'选择{label}',
            clearable=not required,
            className='mb-2'
        ),
    ])
```

---

## Day 5: 新增图表类型

### 5. 扩展图表服务

**更新**: `services/chart_service.py`

```python
# 新增 Plotly 图表类型
class ChartType(Enum):
    # ... 现有类型
    
    # 新增
    area = "area"
    waterfall = "waterfall"
    funnel_area = "funnel_area"
    radar = "radar"
    polar = "polar"
    contour = "contour"
    surface_3d = "surface_3d"


# 更新图表函数映射
PLOTLY_CHART_TYPES = {
    # ... 现有类型
    
    'area': {'name': '面积图', 'category': '趋势'},
    'waterfall': {'name': '瀑布图', 'category': '比较'},
    'radar': {'name': '雷达图', 'category': '比较'},
    'polar': {'name': '极坐标图', 'category': '关系'},
    'contour': {'name': '等高线图', 'category': '分布'},
    'surface_3d': {'name': '3D曲面图', 'category': '关系'},
}
```

---

## 验收标准

- [ ] 字段类型自动推断
- [ ] 字段面板显示维度和度量
- [ ] 动态参数面板根据图表类型变化
- [ ] 参数验证功能
- [ ] 新增 6+ 种图表类型
- [ ] 所有功能有测试
- [ ] UI 响应流畅

---

**预计完成时间**: 5 天  
**难度**: 中高  
**优先级**: 高
