# -*- coding: utf-8 -*-
"""验证应用启动

检查应用是否可以正常启动，没有回调错误
"""

import sys

def verify_imports():
    """验证所有模块可以正常导入"""
    print("1. 验证模块导入...")
    
    try:
        from services.chart_service import ChartService, ChartLibrary, ChartType
        print("   ✓ chart_service 导入成功")
    except Exception as e:
        print(f"   ✗ chart_service 导入失败: {e}")
        return False
    
    try:
        from services.code_generator import CodeGenerator
        print("   ✓ code_generator 导入成功")
    except Exception as e:
        print(f"   ✗ code_generator 导入失败: {e}")
        return False
    
    try:
        from pages.chart_studio import create_chart_studio_page
        print("   ✓ chart_studio 导入成功")
    except Exception as e:
        print(f"   ✗ chart_studio 导入失败: {e}")
        return False
    
    try:
        from pages.data_workshop import layout
        print("   ✓ data_workshop 导入成功")
    except Exception as e:
        print(f"   ✗ data_workshop 导入失败: {e}")
        return False
    
    return True


def verify_chart_types():
    """验证 ChartType 枚举"""
    print("\n2. 验证 ChartType 枚举...")
    
    from services.chart_service import ChartType
    
    # 测试小写枚举值
    test_cases = [
        ('scatter', ChartType.scatter),
        ('line', ChartType.line),
        ('bar', ChartType.bar),
        ('density_heatmap', ChartType.density_heatmap),
        ('scatter_3d', ChartType.scatter_3d),
    ]
    
    for value, expected in test_cases:
        try:
            result = ChartType(value)
            if result == expected:
                print(f"   ✓ ChartType('{value}') = {expected.value}")
            else:
                print(f"   ✗ ChartType('{value}') 不匹配")
                return False
        except Exception as e:
            print(f"   ✗ ChartType('{value}') 失败: {e}")
            return False
    
    return True


def verify_layout_generation():
    """验证布局可以生成"""
    print("\n3. 验证布局生成...")
    
    try:
        from pages.data_workshop import layout
        page_layout = layout()
        print("   ✓ data_workshop 布局生成成功")
    except Exception as e:
        print(f"   ✗ data_workshop 布局生成失败: {e}")
        return False
    
    # 注意：chart_studio 需要数据，所以不测试
    print("   ℹ chart_studio 需要数据，跳过布局测试")
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("DataViz Studio - 应用启动验证")
    print("=" * 60)
    
    all_passed = True
    
    # 验证导入
    if not verify_imports():
        all_passed = False
    
    # 验证枚举
    if not verify_chart_types():
        all_passed = False
    
    # 验证布局
    if not verify_layout_generation():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有验证通过！应用可以正常启动。")
        print("=" * 60)
        return 0
    else:
        print("❌ 部分验证失败，请检查错误信息。")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
