"""
验证重复回调修复
检查 data_workshop.py 中是否还有重复的回调输出
"""

import re
from collections import defaultdict

def check_duplicate_callbacks(filepath):
    """检查文件中是否有重复的回调输出"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有回调装饰器和输出
    callback_pattern = r'@callback\s*\((.*?)\)'
    output_pattern = r'Output\(["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*(?:,\s*allow_duplicate\s*=\s*True)?\)'
    
    callbacks = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        if '@callback' in lines[i]:
            # 收集回调装饰器的所有行
            callback_lines = []
            j = i
            paren_count = 0
            started = False
            
            while j < len(lines):
                line = lines[j]
                callback_lines.append(line)
                
                for char in line:
                    if char == '(':
                        paren_count += 1
                        started = True
                    elif char == ')':
                        paren_count -= 1
                
                if started and paren_count == 0:
                    break
                j += 1
            
            callback_text = '\n'.join(callback_lines)
            
            # 查找输出
            outputs = re.findall(output_pattern, callback_text)
            
            # 查找函数名
            func_line_idx = j + 1
            while func_line_idx < len(lines) and not lines[func_line_idx].strip().startswith('def '):
                func_line_idx += 1
            
            func_name = ''
            if func_line_idx < len(lines):
                func_match = re.search(r'def\s+(\w+)', lines[func_line_idx])
                if func_match:
                    func_name = func_match.group(1)
            
            callbacks.append({
                'line': i + 1,
                'outputs': outputs,
                'function': func_name
            })
            
            i = j + 1
        else:
            i += 1
    
    # 检查重复输出
    output_map = defaultdict(list)
    for cb in callbacks:
        for output in cb['outputs']:
            output_key = f"{output[0]}.{output[1]}"
            output_map[output_key].append({
                'line': cb['line'],
                'function': cb['function']
            })
    
    # 报告结果
    print("=" * 60)
    print("回调输出检查报告")
    print("=" * 60)
    print(f"\n总共找到 {len(callbacks)} 个回调函数")
    print(f"总共 {sum(len(cb['outputs']) for cb in callbacks)} 个输出")
    
    duplicates = {k: v for k, v in output_map.items() if len(v) > 1}
    
    if duplicates:
        print(f"\n⚠️  发现 {len(duplicates)} 个重复输出:")
        for output, locations in duplicates.items():
            print(f"\n  输出: {output}")
            for loc in locations:
                print(f"    - 行 {loc['line']}: {loc['function']}()")
    else:
        print("\n✅ 没有发现重复的回调输出")
    
    # 检查 close_numeric_modals 函数
    print("\n" + "=" * 60)
    print("close_numeric_modals 函数检查")
    print("=" * 60)
    
    close_numeric_count = sum(1 for cb in callbacks if cb['function'] == 'close_numeric_modals')
    print(f"\n找到 {close_numeric_count} 个 close_numeric_modals 函数")
    
    if close_numeric_count > 1:
        print("⚠️  警告: 发现多个 close_numeric_modals 函数")
        for cb in callbacks:
            if cb['function'] == 'close_numeric_modals':
                print(f"  - 行 {cb['line']}")
    elif close_numeric_count == 1:
        print("✅ 只有一个 close_numeric_modals 函数")
    else:
        print("⚠️  未找到 close_numeric_modals 函数")
    
    print("\n" + "=" * 60)
    
    return len(duplicates) == 0 and close_numeric_count == 1

if __name__ == '__main__':
    success = check_duplicate_callbacks('pages/data_workshop.py')
    
    if success:
        print("\n✅ 验证通过: 重复回调已修复")
        exit(0)
    else:
        print("\n❌ 验证失败: 仍存在问题")
        exit(1)
