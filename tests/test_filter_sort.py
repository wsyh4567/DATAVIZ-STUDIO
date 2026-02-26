# -*- coding: utf-8 -*-
"""
测试筛选和排序功能
"""
import pandas as pd
import sys
sys.path.insert(0, '.')

from core.data_manager import DataManager

def test_filter_and_sort():
    """测试筛选和排序功能"""
    print("=" * 60)
    print("测试筛选和排序功能")
    print("=" * 60)

    # 创建测试数据
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
        'age': [25, 30, 35, 28, 32, 27, 29, 31],
        'city': ['Beijing', 'Shanghai', 'Beijing', 'Shanghai', 'Beijing', 'Shanghai', 'Beijing', 'Shanghai'],
        'salary': [5000, 6000, 7000, 5500, 6500, 5800, 6200, 6800]
    }
    df = pd.DataFrame(data)

    print("\n原始数据：")
    print(df)
    print(f"总行数：{len(df)}")

    # 测试筛选
    print("\n" + "=" * 60)
    print("测试 1: 筛选 age > 30")
    print("=" * 60)

    data_manager = DataManager()
    data_manager.active_df = df.copy()

    # 模拟筛选操作
    filtered_df = df[df['age'] > 30]
    print(f"筛选后行数：{len(filtered_df)}")
    print(filtered_df)

    # 测试排序
    print("\n" + "=" * 60)
    print("测试 2: 按 salary 降序排序")
    print("=" * 60)

    sorted_df = df.sort_values(by='salary', ascending=False)
    print(sorted_df)

    # 测试多列排序
    print("\n" + "=" * 60)
    print("测试 3: 按 city 升序，然后 age 降序")
    print("=" * 60)

    multi_sorted_df = df.sort_values(by=['city', 'age'], ascending=[True, False])
    print(multi_sorted_df)

    # 测试去重
    print("\n" + "=" * 60)
    print("测试 4: 去重（基于 city 列）")
    print("=" * 60)

    # 添加重复数据
    df_with_dup = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True)
    print(f"添加重复后行数：{len(df_with_dup)}")
    print(f"重复行数：{df_with_dup.duplicated().sum()}")

    deduped_df = df_with_dup.drop_duplicates(subset=['city'], keep='first')
    print(f"去重后行数：{len(deduped_df)}")
    print(deduped_df)

    # 测试字符串筛选
    print("\n" + "=" * 60)
    print("测试 5: 字符串筛选 - name 包含 'a'")
    print("=" * 60)

    str_filtered = df[df['name'].str.contains('a', case=False, na=False)]
    print(f"筛选后行数：{len(str_filtered)}")
    print(str_filtered)

    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    test_filter_and_sort()
