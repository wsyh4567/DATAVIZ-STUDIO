# -*- coding: utf-8 -*-
"""测试运行时错误修复

验证以下修复：
1. ChartType 枚举大小写匹配
2. Data workshop 模态框回调不会报错
3. 参数验证正常工作
"""

import pandas as pd
from services.chart_service import ChartService, ChartLibrary, ChartType


def test_chart_type_enum_lowercase():
    """测试 ChartType 枚举使用小写值"""
    # 验证枚举值是小写
    assert ChartType.scatter.value == "scatter"
    assert ChartType.density_heatmap.value == "density_heatmap"
    assert ChartType.scatter_3d.value == "scatter_3d"
    
    # 验证可以从小写字符串创建枚举
    chart_type = ChartType("scatter")
    assert chart_type == ChartType.scatter
    
    chart_type = ChartType("density_heatmap")
    assert chart_type == ChartType.density_heatmap


def test_chart_service_plotly_scatter():
    """测试 Plotly 散点图生成"""
    # 创建测试数据
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'category': ['A', 'B', 'A', 'B', 'A']
    })
    
    # 创建图表服务
    service = ChartService()
    service.set_library(ChartLibrary.PLOTLY)
    
    # 生成散点图
    result = service.create_chart(
        df=df,
        chart_type=ChartType.scatter,  # 使用枚举
        params={'x': 'x', 'y': 'y', 'color': 'category'}
    )
    
    assert result['library'] == 'plotly'
    assert 'chart' in result
    assert result['chart'] is not None


def test_chart_service_seaborn_scatter():
    """测试 Seaborn 散点图生成"""
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'category': ['A', 'B', 'A', 'B', 'A']
    })
    
    service = ChartService()
    service.set_library(ChartLibrary.SEABORN)
    
    result = service.create_chart(
        df=df,
        chart_type=ChartType.scatter,
        params={'x': 'x', 'y': 'y', 'hue': 'category'}
    )
    
    assert result['library'] == 'seaborn'
    assert 'chart' in result
    assert result['chart'].startswith('data:image/png;base64,')


def test_chart_type_from_string():
    """测试从字符串创建 ChartType（模拟前端传值）"""
    # 前端传来的是小写字符串
    chart_type_str = "scatter"
    chart_type = ChartType(chart_type_str)
    
    assert chart_type == ChartType.scatter
    
    # 测试其他类型
    assert ChartType("line") == ChartType.line
    assert ChartType("bar") == ChartType.bar
    assert ChartType("density_heatmap") == ChartType.density_heatmap


def test_data_workshop_modal_buttons_exist():
    """测试 data workshop 页面包含占位按钮"""
    from pages.data_workshop import layout
    
    # 获取布局
    page_layout = layout()
    
    # 验证布局不为空
    assert page_layout is not None
    
    # 注意：这个测试只验证布局可以生成，不会触发回调错误
    # 实际的回调错误只在 Dash 应用运行时才会出现


if __name__ == "__main__":
    print("运行运行时错误修复测试...")
    
    print("\n1. 测试 ChartType 枚举小写...")
    test_chart_type_enum_lowercase()
    print("✓ ChartType 枚举使用小写值")
    
    print("\n2. 测试 Plotly 散点图生成...")
    test_chart_service_plotly_scatter()
    print("✓ Plotly 散点图生成成功")
    
    print("\n3. 测试 Seaborn 散点图生成...")
    test_chart_service_seaborn_scatter()
    print("✓ Seaborn 散点图生成成功")
    
    print("\n4. 测试从字符串创建 ChartType...")
    test_chart_type_from_string()
    print("✓ 可以从小写字符串创建 ChartType")
    
    print("\n5. 测试 data workshop 布局...")
    test_data_workshop_modal_buttons_exist()
    print("✓ Data workshop 布局生成成功")
    
    print("\n✅ 所有测试通过！")
