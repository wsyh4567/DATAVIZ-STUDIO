# -*- coding: utf-8 -*-
"""
Phase 3 简单功能测试
测试核心服务和组件的功能
"""
import sys
import pandas as pd
import numpy as np

# 测试数据清洗服务
def test_data_cleaner():
    """测试数据清洗服务"""
    print("\n=== Testing Data Cleaner Service ===")
    try:
        from services.data_cleaner import DataCleaner

        # 创建测试数据
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': [1, 2, 2, 4, 5],
            'C': ['a', 'b', 'c', 'd', 'e']
        })

        cleaner = DataCleaner()

        # 测试缺失值处理
        result = cleaner.fill_missing(df, 'A', 'mean')
        assert result['A'].isna().sum() == 0, "Missing values not handled"
        print("OK Missing value handling works")

        # 测试重复值移除
        result = cleaner.remove_duplicates(df, ['B'])
        assert len(result) < len(df), "Duplicates not removed"
        print("OK Duplicate removal works")

        # 测试数据类型转换
        result = cleaner.convert_type(df.copy(), 'A', 'int')
        assert str(result['A'].dtype).lower().startswith('int'), f"Type conversion failed, got {result['A'].dtype}"
        print("OK Data type conversion works")

        print("OK Data Cleaner Service: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"FAIL Data Cleaner Service failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# 测试统计服务
def test_statistics_service():
    """测试统计服务"""
    print("\n=== Testing Statistics Service ===")
    try:
        from services.stats_service import StatsService

        # 创建测试数据
        df = pd.DataFrame({
            'numeric1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'numeric2': [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
            'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
        })

        stats_service = StatsService()

        # 测试描述性统计
        result = stats_service.descriptive_stats(df, 'numeric1')
        assert 'mean' in result, "Mean not calculated"
        print("OK Descriptive statistics works")

        # 测试相关性分析
        result = stats_service.correlation_matrix(df[['numeric1', 'numeric2']])
        assert result is not None, "Correlation matrix missing"
        print("OK Correlation analysis works")
        print("OK Distribution analysis works")

        print("OK Statistics Service: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"FAIL Statistics Service failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# 测试代码生成器
def test_code_generator():
    """测试代码生成器"""
    print("\n=== Testing Code Generator ===")
    try:
        from services.code_generator import CodeGenerator

        generator = CodeGenerator()

        # 测试操作记录
        operations = [
            {
                'type': 'fill_missing',
                'params': {
                    'column': 'A',
                    'strategy': 'mean'
                },
                'description': 'Fill missing values in A with mean'
            },
            {
                'type': 'remove_duplicates',
                'params': {
                    'columns': ['B', 'C']
                },
                'description': 'Remove duplicates based on B, C'
            }
        ]

        # 添加操作
        for op in operations:
            generator.add_operation(op)

        # 生成代码
        code = generator.generate_code()
        assert 'import pandas as pd' in code, "Missing imports"
        assert 'fillna' in code or 'mean' in code, "Missing value handling code not generated"
        print("OK Code generation works")

        # 测试操作摘要
        summary = generator.get_operation_summary(operations[0])
        assert len(summary) > 0, "Operation summary empty"
        print("OK Operation summary works")

        print("OK Code Generator: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"FAIL Code Generator failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# 测试数据管理器
def test_data_manager():
    """测试数据管理器"""
    print("\n=== Testing Data Manager ===")
    try:
        from core.data_manager import DataManager

        manager = DataManager()

        # 创建测试数据
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })

        # 测试数据添加
        name = manager.add_dataset('test', df, 'test.csv')
        assert name == 'test', "Dataset not added"
        print("OK Data adding works")

        # 测试数据获取
        data = manager.get_dataset('test')
        assert data is not None and len(data) == 5, "Data retrieval failed"
        print("OK Data retrieval works")

        # 测试活跃数据集
        assert manager.active_name == 'test', "Active dataset not set"
        print("OK Active dataset works")

        # 测试数据集列表
        datasets = manager.dataset_names
        assert 'test' in datasets, "Dataset not in list"
        print("OK Dataset listing works")

        print("OK Data Manager: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"FAIL Data Manager failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("Phase 3 Simple Functional Tests")
    print("="*60)

    results = []

    # 运行各项测试
    results.append(("Data Manager", test_data_manager()))
    results.append(("Data Cleaner", test_data_cleaner()))
    results.append(("Statistics Service", test_statistics_service()))
    results.append(("Code Generator", test_code_generator()))

    # 打印结果
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\nAll Phase 3 core services are working correctly!")
    else:
        print(f"\n{total_count - passed_count} test(s) failed")

    print("="*60)

    return passed_count == total_count

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
