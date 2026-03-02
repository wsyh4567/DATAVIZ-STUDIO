# -*- coding: utf-8 -*-
"""
Phase 3 功能测试脚本
测试数据工坊、统计实验室和代码生成器的所有功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from services.data_cleaner import DataCleaner
from services.stats_service import StatsService
from services.code_generator import CodeGenerator
from core.data_manager import DataManager

def test_data_workshop():
    """测试数据工坊功能"""
    print("\n" + "="*60)
    print("测试数据工坊 (Data Workshop)")
    print("="*60)

    # 创建测试数据
    df = pd.DataFrame({
        'name': ['  Alice  ', 'BOB', 'charlie', None, 'David'],
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 70000, 80000, 90000],
        'score': [85.5, 90.2, 78.3, 92.1, 88.7],
        'city': ['New York', 'Los Angeles', 'New York', 'Chicago', 'Los Angeles']
    })

    data_cleaner = DataCleaner()

    print("\n原始数据:")
    print(df)

    # 测试缺失值处理
    print("\n1. 测试缺失值处理")
    try:
        result = data_cleaner.fill_missing(df, 'name', 'constant', 'Unknown')
        print("OK 缺失值填充成功")
        print(f"  处理后: {result['name'].tolist()}")
    except Exception as e:
        print(f"FAIL 缺失值处理失败: {e}")

    # 测试重复值处理
    print("\n2. 测试重复值检测")
    try:
        result = data_cleaner.remove_duplicates(df, ['city'], keep='first')
        print(f"OK 重复值处理成功，剩余 {len(result)} 行")
    except Exception as e:
        print(f"FAIL 重复值处理失败: {e}")

    # 测试文本清理
    print("\n3. 测试文本清理")
    try:
        result = data_cleaner.strip_text(df, 'name')
        print(f"OK 文本清理成功")
        print(f"  处理后: {result['name'].tolist()}")
    except Exception as e:
        print(f"FAIL 文本清理失败: {e}")

    # 测试数据类型转换
    print("\n4. 测试数据类型转换")
    try:
        result = data_cleaner.convert_type(df, 'age', 'float')
        print(f"OK 类型转换成功: {result['age'].dtype}")
    except Exception as e:
        print(f"FAIL 类型转换失败: {e}")

    # 测试文本处理
    print("\n5. 测试文本处理")
    try:
        # 去空格
        result = df.copy()
        result['name'] = result['name'].str.strip()
        print(f"OK 去空格成功: {result['name'].tolist()}")

        # 大小写转换
        result['name'] = result['name'].str.upper()
        print(f"OK 大写转换成功: {result['name'].tolist()}")
    except Exception as e:
        print(f"FAIL 文本处理失败: {e}")

    # 测试数值处理
    print("\n6. 测试数值处理")
    try:
        # 分箱
        result = df.copy()
        result['age_binned'] = pd.cut(result['age'], bins=3, labels=['年轻', '中年', '老年'])
        print(f"OK 分箱成功: {result['age_binned'].tolist()}")

        # 标准化
        result['salary_std'] = (result['salary'] - result['salary'].mean()) / result['salary'].std()
        print(f"OK 标准化成功: {result['salary_std'].tolist()}")

        # 归一化
        result['score_norm'] = (result['score'] - result['score'].min()) / (result['score'].max() - result['score'].min())
        print(f"OK 归一化成功: {result['score_norm'].tolist()}")
    except Exception as e:
        print(f"FAIL 数值处理失败: {e}")


def test_statistics_lab():
    """测试统计实验室功能"""
    print("\n" + "="*60)
    print("测试统计实验室 (Statistics Lab)")
    print("="*60)

    # 创建测试数据
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, 50, 55, 60],
        'salary': [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000],
        'score': [85, 90, 78, 92, 88, 95, 82, 87],
        'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
    })

    stats_service = StatsService()

    print("\n测试数据:")
    print(df)

    # 测试描述性统计
    print("\n1. 测试描述性统计")
    try:
        desc_stats = stats_service.descriptive_stats(df, 'age')
        print("OK 描述性统计成功")
        print(f"  均值: {desc_stats['mean']:.2f}")
        print(f"  中位数: {desc_stats['median']:.2f}")
        print(f"  标准差: {desc_stats['std']:.2f}")
    except Exception as e:
        print(f"FAIL 描述性统计失败: {e}")

    # 测试相关性分析
    print("\n2. 测试相关性分析")
    try:
        corr_matrix = stats_service.correlation_matrix(df[['age', 'salary', 'score']])
        print("OK 相关性分析成功")
        print(f"  矩阵形状: {corr_matrix.shape}")
    except Exception as e:
        print(f"FAIL 相关性分析失败: {e}")

    # 测试分组聚合
    print("\n3. 测试分组聚合")
    try:
        grouped = stats_service.group_aggregate(df, ['category'], 'age', 'mean')
        print("OK 分组聚合成功")
        print(f"  结果行数: {len(grouped)}")
    except Exception as e:
        print(f"FAIL 分组聚合失败: {e}")

    # 测试异常值检测
    print("\n4. 测试异常值检测")
    try:
        outliers = stats_service.detect_outliers(df, 'score', method='iqr')
        print(f"OK 异常值检测成功，发现 {len(outliers)} 个异常值")
    except Exception as e:
        print(f"FAIL 异常值检测失败: {e}")


def test_code_generator():
    """测试代码生成器功能"""
    print("\n" + "="*60)
    print("测试代码生成器 (Code Generator)")
    print("="*60)

    code_gen = CodeGenerator()

    # 测试添加操作
    print("\n1. 测试添加操作")
    try:
        code_gen.add_operation({
            'type': 'fill_missing',
            'params': {
                'column': 'age',
                'strategy': 'mean'
            }
        })
        code_gen.add_operation({
            'type': 'remove_duplicates',
            'params': {
                'columns': ['name']
            }
        })
        print("OK 添加操作成功")
    except Exception as e:
        print(f"FAIL 添加操作失败: {e}")

    # 测试生成代码
    print("\n2. 测试生成代码")
    try:
        code = code_gen.generate_code()
        print("OK 代码生成成功")
        print(f"  代码长度: {len(code)} 字符")
        print("\n生成的代码片段:")
        print(code[:300] + "...")
    except Exception as e:
        print(f"FAIL 代码生成失败: {e}")

    # 测试操作摘要
    print("\n3. 测试操作摘要")
    try:
        operation = {'type': 'fill_missing', 'column': 'age', 'strategy': 'mean'}
        summary = code_gen.get_operation_summary(operation)
        print(f"OK 操作摘要: {summary}")
    except Exception as e:
        print(f"FAIL 操作摘要失败: {e}")

    # 测试清空操作
    print("\n4. 测试清空操作")
    try:
        code_gen.clear_operations()
        code = code_gen.generate_code()
        print(f"OK 清空操作成功，代码长度: {len(code)}")
    except Exception as e:
        print(f"FAIL 清空操作失败: {e}")


def test_integration():
    """测试集成功能"""
    print("\n" + "="*60)
    print("测试集成功能")
    print("="*60)

    # 创建完整的数据处理流程
    print("\n完整数据处理流程测试:")

    # 1. 加载数据
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', None, 'David'],
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 70000, 80000, 90000],
        'score': [85.5, 90.2, 78.3, 92.1, 88.7]
    })

    data_manager = DataManager()
    data_manager.active_df = df
    print("OK 步骤1: 数据加载完成")

    # 2. 数据清洗
    data_cleaner = DataCleaner()
    df = data_cleaner.fill_missing(df, 'name', 'constant', 'Unknown')
    print("OK 步骤2: 数据清洗完成")

    # 3. 统计分析
    stats_service = StatsService()
    desc_stats = stats_service.descriptive_stats(df, 'age')
    print("OK 步骤3: 统计分析完成")

    # 4. 代码生成
    code_gen = CodeGenerator()
    code_gen.add_operation({
        'type': 'fill_missing',
        'params': {
            'column': 'name',
            'strategy': 'constant',
            'constant_value': 'Unknown'
        }
    })
    code = code_gen.generate_code()
    print("OK 步骤4: 代码生成完成")

    print("\nOK 集成测试通过！")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Phase 3 功能测试")
    print("="*60)

    try:
        test_data_workshop()
        test_statistics_lab()
        test_code_generator()
        test_integration()

        print("\n" + "="*60)
        print("所有测试完成！")
        print("="*60)

    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
