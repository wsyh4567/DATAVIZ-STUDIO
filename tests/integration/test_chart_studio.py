# -*- coding: utf-8 -*-
"""测试图表工作室功能"""

import pandas as pd
import numpy as np
from services.chart_service import (
    classify_dataframe,
    get_chart_type,
    create_chart,
    recommend_charts,
    CHART_TYPES
)

def test_field_classification():
    """测试字段分类"""
    print("=" * 60)
    print("测试字段分类")
    print("=" * 60)
    
    # 创建测试数据
    df = pd.DataFrame({
        'city': ['北京', '上海', '广州', '深圳', '杭州'] * 20,
        'sales': np.random.randint(1000, 10000, 100),
        'quantity': np.random.randint(10, 100, 100),
        'date': pd.date_range('2024-01-01', periods=100),
        'is_active': np.random.choice([True, False], 100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
    })
    
    field_info = classify_dataframe(df)
    
    print(f"\n数据集形状: {df.shape}")
    print(f"\n字段分类结果:")
    for name, info in field_info.items():
        print(f"  {name:15} | {info.type.value:10} | {info.dtype:15} | 唯一值: {info.unique_count}")
    
    return df


def test_chart_types():
    """测试图表类型"""
    print("\n" + "=" * 60)
    print("测试图表类型")
    print("=" * 60)
    
    print(f"\n总共 {len(CHART_TYPES)} 种图表类型:")
    
    from services.chart_service import ChartCategory
    categories = {}
    for chart in CHART_TYPES:
        if chart.category not in categories:
            categories[chart.category] = []
        categories[chart.category].append(chart)
    
    for category, charts in categories.items():
        print(f"\n{category.value.upper()} ({len(charts)} 种):")
        for chart in charts:
            print(f"  - {chart.name:12} ({chart.id:20}) | {chart.description}")


def test_chart_creation(df):
    """测试图表创建"""
    print("\n" + "=" * 60)
    print("测试图表创建")
    print("=" * 60)
    
    # 测试柱状图
    print("\n1. 创建柱状图 (city vs sales)")
    try:
        fig = create_chart(
            df,
            "bar",
            {"x": "city", "y": "sales"},
            {"title": "各城市销售额"}
        )
        print("   ✓ 柱状图创建成功")
    except Exception as e:
        print(f"   ✗ 柱状图创建失败: {e}")
    
    # 测试折线图
    print("\n2. 创建折线图 (date vs sales)")
    try:
        fig = create_chart(
            df,
            "line",
            {"x": "date", "y": "sales"},
            {"title": "销售趋势"}
        )
        print("   ✓ 折线图创建成功")
    except Exception as e:
        print(f"   ✗ 折线图创建失败: {e}")
    
    # 测试散点图
    print("\n3. 创建散点图 (sales vs quantity)")
    try:
        fig = create_chart(
            df,
            "scatter",
            {"x": "sales", "y": "quantity", "color": "city"},
            {"title": "销售额与数量关系"}
        )
        print("   ✓ 散点图创建成功")
    except Exception as e:
        print(f"   ✗ 散点图创建失败: {e}")
    
    # 测试饼图
    print("\n4. 创建饼图 (category distribution)")
    try:
        # 聚合数据
        pie_data = df.groupby('category')['sales'].sum().reset_index()
        fig = create_chart(
            pie_data,
            "pie",
            {"names": "category", "values": "sales"},
            {"title": "类别销售占比"}
        )
        print("   ✓ 饼图创建成功")
    except Exception as e:
        print(f"   ✗ 饼图创建失败: {e}")


def test_chart_recommendation():
    """测试图表推荐"""
    print("\n" + "=" * 60)
    print("测试图表推荐")
    print("=" * 60)
    
    test_cases = [
        {"x": "city", "y": "sales"},
        {"x": "date", "y": "sales"},
        {"x": "sales", "y": "quantity"},
        {"names": "category", "values": "sales"},
    ]
    
    for i, fields in enumerate(test_cases, 1):
        print(f"\n{i}. 字段: {fields}")
        recommendations = recommend_charts(fields)
        if recommendations:
            print("   推荐图表:")
            for chart_id, score in recommendations[:3]:
                chart = get_chart_type(chart_id)
                print(f"     - {chart.name:15} (评分: {score})")
        else:
            print("   无推荐")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("DataViz Studio - 图表工作室功能测试")
    print("=" * 60)
    
    # 测试字段分类
    df = test_field_classification()
    
    # 测试图表类型
    test_chart_types()
    
    # 测试图表创建
    test_chart_creation(df)
    
    # 测试图表推荐
    test_chart_recommendation()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
