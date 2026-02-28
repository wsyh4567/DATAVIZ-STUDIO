# -*- coding: utf-8 -*-
"""测试新的图表工作室（Python 优先架构）"""

import pandas as pd
from services.chart_service import ChartService, ChartLibrary, ChartType
from services.code_generator import CodeGenerator


def test_plotly_chart():
    """测试 Plotly 图表生成"""
    print("=" * 50)
    print("测试 Plotly 图表生成")
    print("=" * 50)
    
    # 创建测试数据
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'category': ['A', 'B', 'A', 'B', 'A']
    })
    
    # 创建图表服务
    service = ChartService()
    service.set_library(ChartLibrary.PLOTLY)
    
    # 测试参数
    params = {
        'x': 'x',
        'y': 'y',
        'color': 'category',
        'title': '测试散点图'
    }
    
    # 生成图表
    result = service.create_chart(df, ChartType.SCATTER, params)
    
    print(f"图表库: {result['library']}")
    print(f"图表数据长度: {len(result['chart'])}")
    print("✓ Plotly 图表生成成功")
    print()


def test_seaborn_chart():
    """测试 Seaborn 图表生成"""
    print("=" * 50)
    print("测试 Seaborn 图表生成")
    print("=" * 50)
    
    # 创建测试数据
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'category': ['A', 'B', 'A', 'B', 'A']
    })
    
    # 创建图表服务
    service = ChartService()
    service.set_library(ChartLibrary.SEABORN)
    
    # 测试参数
    params = {
        'x': 'x',
        'y': 'y',
        'hue': 'category'
    }
    
    # 生成图表
    result = service.create_chart(df, ChartType.SCATTER, params)
    
    print(f"图表库: {result['library']}")
    print(f"图表数据类型: base64 image")
    print(f"图表数据长度: {len(result['chart'])}")
    print("✓ Seaborn 图表生成成功")
    print()


def test_code_generation():
    """测试代码生成"""
    print("=" * 50)
    print("测试代码生成")
    print("=" * 50)
    
    params = {
        'x': 'sales',
        'y': 'profit',
        'color': 'category',
        'size': 'quantity',
        'hover_data': ['city'],
        'trendline': 'ols'
    }
    
    # 生成 Plotly 代码
    print("\n--- Plotly 代码 ---")
    plotly_code = CodeGenerator.generate_plotly_code('scatter', params)
    print(plotly_code)
    
    # 生成 Seaborn 代码
    print("\n--- Seaborn 代码 ---")
    seaborn_code = CodeGenerator.generate_seaborn_code('scatter', params)
    print(seaborn_code)
    
    print("\n✓ 代码生成成功")
    print()


if __name__ == '__main__':
    test_plotly_chart()
    test_seaborn_chart()
    test_code_generation()
    
    print("=" * 50)
    print("所有测试通过！")
    print("=" * 50)
