# -*- coding: utf-8 -*-
"""DataViz Studio — 简单功能测试

验证核心功能是否正常工作。
"""

from __future__ import annotations

import sys
import io

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_imports():
    """测试所有依赖是否正确安装。"""
    print("测试 1：检查依赖...")
    try:
        import dash
        import dash_bootstrap_components
        import dash_ag_grid
        import pandas
        import plotly
        import openpyxl
        import chardet
        import numpy
        print("  [OK] 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"  [FAIL] 依赖缺失：{e}")
        return False


def test_app_structure():
    """测试应用结构是否完整。"""
    print("\n测试 2：检查应用结构...")
    try:
        from app import app, server
        from core.data_manager import DataManager
        from core.state_manager import get_initial_state
        from services.data_loader import load_sample_dataset
        from components.navbar import create_navbar
        from components.sidebar import create_sidebar
        from components.statusbar import create_statusbar
        from components.data_table import create_data_table
        from pages.welcome import create_welcome_page
        from pages.data_hub import create_data_hub_page
        from pages.data_canvas import create_data_canvas_page
        print("  [OK] 应用结构完整")
        return True
    except ImportError as e:
        print(f"  [FAIL] 模块导入失败：{e}")
        return False


def test_data_manager():
    """测试数据管理器功能。"""
    print("\n测试 3：测试数据管理器...")
    try:
        from core.data_manager import DataManager
        import pandas as pd

        dm = DataManager()
        dm.clear()

        # 测试添加数据集
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        name = dm.add_dataset("test", df)
        assert name == "test", "数据集名称不匹配"
        assert dm.active_name == "test", "活跃数据集未设置"

        # 测试获取元数据
        meta = dm.get_meta()
        assert meta is not None, "元数据为空"
        assert meta.rows == 3, f"行数错误：{meta.rows}"
        assert meta.cols == 2, f"列数错误：{meta.cols}"

        # 测试列表数据集
        datasets = dm.list_datasets()
        assert len(datasets) == 1, f"数据集数量错误：{len(datasets)}"

        dm.clear()
        print("  [OK] 数据管理器功能正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 数据管理器测试失败：{e}")
        return False


def test_data_loader():
    """测试数据加载功能。"""
    print("\n测试 4：测试数据加载...")
    try:
        from services.data_loader import load_sample_dataset, SAMPLE_DATASETS

        # 测试加载示例数据集
        for name in SAMPLE_DATASETS:
            df = load_sample_dataset(name)
            assert df is not None, f"{name} 加载失败"
            assert len(df) > 0, f"{name} 数据为空"
            print(f"  [OK] {name}: {len(df)} 行 × {len(df.columns)} 列")

        print("  [OK] 数据加载功能正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 数据加载测试失败：{e}")
        return False


def test_components():
    """测试组件创建。"""
    print("\n测试 5：测试组件创建...")
    try:
        from components.navbar import create_navbar
        from components.sidebar import create_sidebar
        from components.statusbar import create_statusbar
        from components.data_table import create_data_table
        import pandas as pd

        navbar = create_navbar()
        assert navbar is not None, "导航栏创建失败"

        sidebar = create_sidebar()
        assert sidebar is not None, "侧边栏创建失败"

        statusbar = create_statusbar()
        assert statusbar is not None, "状态栏创建失败"

        # 测试空表格
        table = create_data_table(None)
        assert table is not None, "空表格创建失败"

        # 测试有数据的表格
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        table = create_data_table(df)
        assert table is not None, "数据表格创建失败"

        print("  [OK] 组件创建功能正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 组件测试失败：{e}")
        return False


def test_pages():
    """测试页面创建。"""
    print("\n测试 6：测试页面创建...")
    try:
        from pages.welcome import create_welcome_page
        from pages.data_hub import create_data_hub_page
        from pages.data_canvas import create_data_canvas_page

        welcome = create_welcome_page()
        assert welcome is not None, "欢迎页创建失败"

        hub = create_data_hub_page()
        assert hub is not None, "数据中心页创建失败"

        canvas = create_data_canvas_page()
        assert canvas is not None, "数据画布页创建失败"

        print("  [OK] 页面创建功能正常")
        return True
    except Exception as e:
        print(f"  [FAIL] 页面测试失败：{e}")
        return False


def main():
    """运行所有测试。"""
    print("=" * 60)
    print("DataViz Studio — 功能测试")
    print("=" * 60)

    tests = [
        test_imports,
        test_app_structure,
        test_data_manager,
        test_data_loader,
        test_components,
        test_pages,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print(f"测试结果：{sum(results)}/{len(results)} 通过")
    print("=" * 60)

    if all(results):
        print("\n所有测试通过！应用已准备就绪。")
        print("\n启动应用：")
        print("  python app.py")
        print("  或")
        print("  python cli.py")
        return 0
    else:
        print("\n部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
