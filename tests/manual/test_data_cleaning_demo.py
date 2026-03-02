#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据清洗功能演示脚本

演示新实现的数据清洗功能，包括：
- 列拆分
- 列合并
- 查找替换
- 字符串清理
"""

import pandas as pd
from services.data_cleaner import (
    ColumnSplitter,
    ColumnConcatenator,
    StringReplacer,
    StringCleaner
)

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def demo_column_splitter():
    """演示列拆分功能"""
    print_section("1. 列拆分功能演示")
    
    # 创建测试数据
    df = pd.DataFrame({
        'email': ['user1@example.com', 'admin@test.org', 'john.doe@company.net'],
        'full_name': ['张-三', '李-四', '王-五']
    })
    
    print("\n原始数据:")
    print(df)
    
    # 拆分 email 列
    print("\n拆分 email 列（按 @ 分隔）:")
    df_split = ColumnSplitter.split_column(
        df, 'email', '@', max_split=1, 
        new_names=['username', 'domain']
    )
    print(df_split[['email', 'username', 'domain']])
    
    # 生成代码
    print("\n生成的 Python 代码:")
    code = ColumnSplitter.generate_code(
        'email', '@', max_split=1, 
        new_names=['username', 'domain']
    )
    print(code)

def demo_column_concatenator():
    """演示列合并功能"""
    print_section("2. 列合并功能演示")
    
    # 创建测试数据
    df = pd.DataFrame({
        'first_name': ['John', 'Jane', 'Bob'],
        'last_name': ['Doe', 'Smith', 'Johnson'],
        'age': [30, 25, 35]
    })
    
    print("\n原始数据:")
    print(df)
    
    # 合并姓名列
    print("\n合并 first_name 和 last_name:")
    df_merged = ColumnConcatenator.concatenate_columns(
        df, ['first_name', 'last_name'], ' ', 'full_name'
    )
    print(df_merged[['first_name', 'last_name', 'full_name']])
    
    # 生成代码
    print("\n生成的 Python 代码:")
    code = ColumnConcatenator.generate_code(
        ['first_name', 'last_name'], ' ', 'full_name'
    )
    print(code)

def demo_string_replacer():
    """演示查找替换功能"""
    print_section("3. 查找替换功能演示")
    
    # 创建测试数据
    df = pd.DataFrame({
        'text': ['Hello World', 'hello python', 'HELLO DASH'],
        'code': ['test123', 'demo456', 'sample789']
    })
    
    print("\n原始数据:")
    print(df)
    
    # 不区分大小写替换
    print("\n查找替换（不区分大小写）:")
    df_replaced = StringReplacer.find_replace(
        df, 'text', 'hello', 'hi', 
        use_regex=False, case_sensitive=False
    )
    print(df_replaced[['text']])
    
    # 正则表达式替换
    print("\n正则表达式替换（数字替换为 XXX）:")
    df_regex = StringReplacer.find_replace(
        df, 'code', r'\d+', 'XXX', 
        use_regex=True
    )
    print(df_regex[['code']])
    
    # 生成代码
    print("\n生成的 Python 代码:")
    code = StringReplacer.generate_code(
        'text', 'hello', 'hi', 
        use_regex=False, case_sensitive=False
    )
    print(code)

def demo_string_cleaner():
    """演示字符串清理功能"""
    print_section("4. 字符串清理功能演示")
    
    # 创建测试数据
    df = pd.DataFrame({
        'text': ['  hello world  ', '  python  ', '  dash  '],
        'name': ['john doe', 'JANE SMITH', 'Bob Johnson']
    })
    
    print("\n原始数据:")
    print(df)
    
    # 去除空格
    print("\n去除两端空格:")
    df_stripped = StringCleaner.strip_whitespace(df, 'text', 'both')
    print(df_stripped[['text']])
    
    # 大小写转换
    print("\n转换为标题格式:")
    df_title = StringCleaner.case_conversion(df, 'name', 'title')
    print(df_title[['name']])
    
    # 提取子字符串
    print("\n提取前 5 个字符:")
    df_substr = StringCleaner.extract_substring(
        df, 'text', 0, 5, 'prefix'
    )
    print(df_substr[['text', 'prefix']])
    
    # 生成代码
    print("\n生成的 Python 代码:")
    code = StringCleaner.generate_strip_code('text', 'both')
    print(code)

def demo_code_generation():
    """演示完整的代码生成"""
    print_section("5. 完整代码生成演示")
    
    from services.code_generator import DataCleaningCodeGenerator
    
    # 模拟操作历史
    operations = [
        {
            'type': 'split_column',
            'description': '拆分 email 列',
            'column': 'email',
            'separator': '@',
            'max_split': 1,
            'new_names': ['username', 'domain']
        },
        {
            'type': 'concatenate_columns',
            'description': '合并姓名列',
            'columns': ['first_name', 'last_name'],
            'separator': ' ',
            'new_name': 'full_name',
            'drop_original': False
        },
        {
            'type': 'find_replace',
            'description': '查找替换',
            'column': 'text',
            'find_value': 'hello',
            'replace_value': 'hi',
            'use_regex': False,
            'case_sensitive': False
        },
        {
            'type': 'strip_whitespace',
            'description': '去除空格',
            'column': 'text',
            'mode': 'both'
        }
    ]
    
    # 生成完整代码
    code = DataCleaningCodeGenerator.generate_data_cleaning_code(operations)
    
    print("\n生成的完整 Python 脚本:")
    print(code)

def main():
    """主函数"""
    print("\n" + "🎨" * 30)
    print("  DataViz Studio - 数据清洗功能演示")
    print("🎨" * 30)
    
    try:
        # 运行各个演示
        demo_column_splitter()
        demo_column_concatenator()
        demo_string_replacer()
        demo_string_cleaner()
        demo_code_generation()
        
        print("\n" + "=" * 60)
        print("  ✅ 所有演示完成！")
        print("=" * 60)
        print("\n提示：")
        print("  - 所有功能都已集成到数据工坊页面")
        print("  - 可以通过 UI 界面使用这些功能")
        print("  - 所有操作都会生成可执行的 Python 代码")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
