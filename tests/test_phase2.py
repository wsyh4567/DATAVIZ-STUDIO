# -*- coding: utf-8 -*-
"""测试图表工作室功能

验证 Phase 2 的核心功能。
"""

from __future__ import annotations

import sys
import io

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_chart_service():
    """测试图表服务模块"""
    print("\n测试 1：图表服务模块...")
    try:
        from services.chart_service import (
            classify_field,
            classify_dataframe,
            get_chart_type,
            recommend_charts,
            create_chart,
            CHART_TYPES,
            FieldType,
        )
        import pandas as pd
        import numpy as np

        # 测试字段分类 - 使用足够多的数据以确保正确分类
        df = pd.DataFrame({
            "category": ["A", "B", "C"] * 10,
            "value": np.random.randint(10, 100, 30),
            "date": pd.date_range("2024-01-01", periods=30),
            "flag": [True, False] * 15,
        })

        field_info = classify_dataframe(df)
        assert len(field_info) == 4, "字段数量不正确"
        assert field_info["category"].type == FieldType.DIMENSION, "category 应为维度"
        assert field_info["value"].type == FieldType.MEASURE, "value 应为度量"
        assert field_info["date"].type == FieldType.DIMENSION, "date 应为维度"
        assert field_info["flag"].type == FieldType.DIMENSION, "flag 应为维度"
        print("  [OK] 字段分类正确")

        # 测试图表类型
        assert len(CHART_TYPES) >= 15, f"图表类型数量不足: {len(CHART_TYPES)}"
        bar_chart = get_chart_type("bar")
        assert bar_chart is not None, "未找到柱状图类型"
        assert bar_chart.name == "柱状图", "图表名称不正确"
        print(f"  [OK] 图表类型定义正确 ({len(CHART_TYPES)} 种)")

        # 测试图表推荐
        recommendations = recommend_charts({"x": "category", "y": "value"})
        assert len(recommendations) > 0, "推荐列表为空"
        assert recommendations[0][0] in ["bar", "line", "scatter"], "推荐不合理"
        print(f"  [OK] 图表推荐功能正常 (推荐 {len(recommendations)} 种)")

        # 测试图表创建
        fig = create_chart(df, "bar", {"x": "category", "y": "value"})
        assert fig is not None, "图表创建失败"
        assert hasattr(fig, "data"), "图表对象无效"
        print("  [OK] 图表创建成功")

        print("  [OK] 图表服务模块功能正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 图表服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_field_panel():
    """测试字段面板组件"""
    print("\n测试 2：字段面板组件...")
    try:
        from components.field_panel import (
            create_field_panel,
            create_drop_zone,
            create_chart_fields_panel,
        )
        import pandas as pd

        # 测试空数据
        panel = create_field_panel(None)
        assert panel is not None, "空面板创建失败"
        print("  [OK] 空面板创建成功")

        # 测试有数据
        df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": ["x", "y", "z"],
        })
        panel = create_field_panel(df)
        assert panel is not None, "字段面板创建失败"
        print("  [OK] 字段面板创建成功")

        # 测试拖放区域
        drop_zone = create_drop_zone("X 轴", "x")
        assert drop_zone is not None, "拖放区域创建失败"
        print("  [OK] 拖放区域创建成功")

        # 测试字段配置面板
        config_panel = create_chart_fields_panel()
        assert config_panel is not None, "字段配置面板创建失败"
        print("  [OK] 字段配置面板创建成功")

        print("  [OK] 字段面板组件功能正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 字段面板测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chart_builder():
    """测试图表构建器组件"""
    print("\n测试 3：图表构建器组件...")
    try:
        from components.chart_builder import (
            create_chart_type_selector,
            create_chart_canvas,
            create_chart_config_panel,
            create_saved_charts_panel,
        )

        # 测试图表类型选择器
        selector = create_chart_type_selector()
        assert selector is not None, "图表类型选择器创建失败"
        print("  [OK] 图表类型选择器创建成功")

        # 测试图表画布
        canvas = create_chart_canvas()
        assert canvas is not None, "图表画布创建失败"
        print("  [OK] 图表画布创建成功")

        # 测试配置面板
        config_panel = create_chart_config_panel()
        assert config_panel is not None, "配置面板创建失败"
        print("  [OK] 配置面板创建成功")

        # 测试已保存图表面板
        saved_panel = create_saved_charts_panel()
        assert saved_panel is not None, "已保存图表面板创建失败"
        print("  [OK] 已保存图表面板创建成功")

        print("  [OK] 图表构建器组件功能正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 图表构建器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chart_studio_page():
    """测试图表工作室页面"""
    print("\n测试 4：图表工作室页面...")
    try:
        from pages.chart_studio import create_chart_studio_page
        from core.data_manager import DataManager
        import pandas as pd

        # 加载测试数据
        dm = DataManager()
        df = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [10, 20, 30],
        })
        dm.add_dataset("test", df)

        # 创建页面
        page = create_chart_studio_page()
        assert page is not None, "图表工作室页面创建失败"
        print("  [OK] 图表工作室页面创建成功")

        # 清理
        dm.clear()

        print("  [OK] 图表工作室页面功能正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 图表工作室页面测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_integration():
    """测试应用集成"""
    print("\n测试 5：应用集成...")
    try:
        from app import app

        # 检查应用是否正确初始化
        assert app is not None, "应用未初始化"
        assert app.server is not None, "Flask 服务器未初始化"
        print("  [OK] 应用初始化成功")

        # 检查路由是否包含图表工作室
        # 这个测试比较简单，只检查导入是否成功
        import pages.chart_studio
        print("  [OK] 图表工作室模块已导入")

        print("  [OK] 应用集成正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 应用集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("DataViz Studio — Phase 2 功能测试")
    print("=" * 60)

    tests = [
        test_chart_service,
        test_field_panel,
        test_chart_builder,
        test_chart_studio_page,
        test_app_integration,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print(f"测试结果：{sum(results)}/{len(results)} 通过")
    print("=" * 60)

    if all(results):
        print("\n所有测试通过！Phase 2 功能已就绪。")
        print("\n启动应用：")
        print("  python app.py")
        print("\n访问图表工作室：")
        print("  http://localhost:8050/charts")
        return 0
    else:
        print("\n部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
