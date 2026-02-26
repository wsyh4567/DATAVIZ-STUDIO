# -*- coding: utf-8 -*-
"""测试数据加载流程"""

from core.data_manager import DataManager
from services.data_loader import load_sample_dataset

# 清空数据管理器
dm = DataManager()
dm.clear()

print("1. 测试加载示例数据集...")
try:
    df = load_sample_dataset("iris")
    print(f"   ✅ 加载成功：{len(df)} 行 × {len(df.columns)} 列")
except Exception as e:
    print(f"   ❌ 加载失败：{e}")
    exit(1)

print("\n2. 测试添加到 DataManager...")
try:
    name = dm.add_dataset("iris", df, source="sample:iris")
    print(f"   ✅ 添加成功：{name}")
except Exception as e:
    print(f"   ❌ 添加失败：{e}")
    exit(1)

print("\n3. 测试获取元数据...")
try:
    meta = dm.get_meta()
    if meta:
        print(f"   ✅ 元数据获取成功：")
        print(f"      - 名称：{meta.name}")
        print(f"      - 行数：{meta.rows}")
        print(f"      - 列数：{meta.cols}")
        print(f"      - 内存：{meta.memory_mb:.2f} MB")
    else:
        print(f"   ❌ 元数据为 None")
        exit(1)
except Exception as e:
    print(f"   ❌ 获取元数据失败：{e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n4. 测试获取活跃数据集...")
try:
    active_df = dm.active_df
    if active_df is not None:
        print(f"   ✅ 活跃数据集获取成功：{len(active_df)} 行")
    else:
        print(f"   ❌ 活跃数据集为 None")
        exit(1)
except Exception as e:
    print(f"   ❌ 获取活跃数据集失败：{e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✅ 所有测试通过！")
