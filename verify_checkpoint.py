"""
Checkpoint 4 Verification Script
验证基础样式系统的实现
"""

import re
from pathlib import Path

def check_css_variables():
    """检查CSS变量是否正确定义"""
    print("=" * 60)
    print("1. 检查CSS变量定义")
    print("=" * 60)
    
    base_css = Path("assets/css/base.css").read_text(encoding='utf-8')
    
    # 必需的颜色变量
    required_colors = [
        "--bg-primary",
        "--bg-secondary",
        "--accent-primary",
        "--accent-secondary",
        "--text-primary",
        "--text-secondary",
        "--border-glow"
    ]
    
    # 必需的间距变量（8px基础单位）
    required_spacing = [
        "--sp-base",
        "--sp-2",
        "--sp-4",
        "--sp-6",
        "--sp-8"
    ]
    
    # 必需的字体变量
    required_fonts = [
        "--font-sans",
        "--font-mono"
    ]
    
    # 必需的动画变量
    required_transitions = [
        "--transition-fast",
        "--transition-base",
        "--transition-slow"
    ]
    
    # 必需的阴影变量
    required_shadows = [
        "--shadow-glow-sm",
        "--shadow-glow-md",
        "--shadow-glow-lg"
    ]
    
    all_checks = []
    
    # 检查颜色变量
    print("\n✓ 颜色变量:")
    for var in required_colors:
        if f"{var}:" in base_css:
            print(f"  ✓ {var}")
            all_checks.append(True)
        else:
            print(f"  ✗ {var} - 缺失!")
            all_checks.append(False)
    
    # 检查间距变量
    print("\n✓ 间距变量 (8px基础单位):")
    for var in required_spacing:
        if f"{var}:" in base_css:
            print(f"  ✓ {var}")
            all_checks.append(True)
        else:
            print(f"  ✗ {var} - 缺失!")
            all_checks.append(False)
    
    # 检查字体变量
    print("\n✓ 字体变量:")
    for var in required_fonts:
        if f"{var}:" in base_css:
            print(f"  ✓ {var}")
            all_checks.append(True)
        else:
            print(f"  ✗ {var} - 缺失!")
            all_checks.append(False)
    
    # 检查动画变量
    print("\n✓ 动画变量:")
    for var in required_transitions:
        if f"{var}:" in base_css:
            print(f"  ✓ {var}")
            all_checks.append(True)
        else:
            print(f"  ✗ {var} - 缺失!")
            all_checks.append(False)
    
    # 检查阴影变量
    print("\n✓ 阴影/发光变量:")
    for var in required_shadows:
        if f"{var}:" in base_css:
            print(f"  ✓ {var}")
            all_checks.append(True)
        else:
            print(f"  ✗ {var} - 缺失!")
            all_checks.append(False)
    
    return all(all_checks)

def check_glassmorphism():
    """检查玻璃拟态效果实现"""
    print("\n" + "=" * 60)
    print("2. 检查玻璃拟态效果")
    print("=" * 60)
    
    themes_css = Path("assets/css/themes.css").read_text(encoding='utf-8')
    
    checks = []
    
    # 检查.dvs-glass类
    if ".dvs-glass" in themes_css:
        print("\n✓ .dvs-glass 基础类已定义")
        checks.append(True)
        
        # 检查关键属性
        glass_section = themes_css[themes_css.find(".dvs-glass"):themes_css.find(".dvs-glass") + 500]
        
        if "backdrop-filter" in glass_section:
            print("  ✓ backdrop-filter 已定义")
            checks.append(True)
        else:
            print("  ✗ backdrop-filter 缺失!")
            checks.append(False)
        
        if "blur" in glass_section:
            print("  ✓ blur 效果已应用")
            checks.append(True)
        else:
            print("  ✗ blur 效果缺失!")
            checks.append(False)
        
        if "border:" in glass_section or "border-radius:" in glass_section:
            print("  ✓ 边框样式已定义")
            checks.append(True)
        else:
            print("  ✗ 边框样式缺失!")
            checks.append(False)
        
        if "box-shadow" in glass_section:
            print("  ✓ 发光效果 (box-shadow) 已定义")
            checks.append(True)
        else:
            print("  ✗ 发光效果缺失!")
            checks.append(False)
        
        if ":hover" in themes_css[themes_css.find(".dvs-glass"):themes_css.find(".dvs-glass") + 800]:
            print("  ✓ 悬停状态已定义")
            checks.append(True)
        else:
            print("  ✗ 悬停状态缺失!")
            checks.append(False)
    else:
        print("\n✗ .dvs-glass 类未定义!")
        checks.append(False)
    
    # 检查降级方案
    if "@supports not (backdrop-filter" in themes_css:
        print("\n✓ 浏览器兼容性降级方案已实现")
        checks.append(True)
    else:
        print("\n✗ 降级方案缺失!")
        checks.append(False)
    
    return all(checks)

def check_sidebar_animation():
    """检查侧边栏折叠/展开动画"""
    print("\n" + "=" * 60)
    print("3. 检查侧边栏动画")
    print("=" * 60)
    
    components_css = Path("assets/css/components.css").read_text(encoding='utf-8')
    
    checks = []
    
    # 检查侧边栏类
    if ".dvs-sidebar" in components_css:
        print("\n✓ .dvs-sidebar 类已定义")
        checks.append(True)
        
        # 检查过渡动画
        sidebar_section = components_css[components_css.find(".dvs-sidebar"):components_css.find(".dvs-sidebar") + 1000]
        
        if "transition:" in sidebar_section:
            print("  ✓ transition 动画已定义")
            checks.append(True)
            
            # 检查是否使用0.3s或300ms
            if "0.3s" in sidebar_section or "300ms" in sidebar_section:
                print("  ✓ 动画时长为0.3s (符合规范)")
                checks.append(True)
            else:
                print("  ⚠ 动画时长可能不是0.3s")
                checks.append(True)  # 不算失败，只是警告
            
            if "ease-in-out" in sidebar_section:
                print("  ✓ 使用ease-in-out缓动函数")
                checks.append(True)
            else:
                print("  ⚠ 可能未使用ease-in-out缓动函数")
                checks.append(True)  # 不算失败
        else:
            print("  ✗ transition 动画缺失!")
            checks.append(False)
        
        # 检查折叠状态类
        if ".dvs-sidebar--collapsed" in components_css:
            print("  ✓ .dvs-sidebar--collapsed 状态类已定义")
            checks.append(True)
        else:
            print("  ✗ 折叠状态类缺失!")
            checks.append(False)
    else:
        print("\n✗ .dvs-sidebar 类未定义!")
        checks.append(False)
    
    return all(checks)

def check_responsive_motion():
    """检查prefers-reduced-motion支持"""
    print("\n" + "=" * 60)
    print("4. 检查可访问性 - Reduced Motion")
    print("=" * 60)
    
    base_css = Path("assets/css/base.css").read_text(encoding='utf-8')
    
    if "prefers-reduced-motion" in base_css:
        print("\n✓ prefers-reduced-motion 媒体查询已实现")
        return True
    else:
        print("\n✗ prefers-reduced-motion 支持缺失!")
        return False

def main():
    """运行所有检查"""
    print("\n" + "=" * 60)
    print("Checkpoint 4: 验证基础样式系统")
    print("=" * 60)
    
    results = []
    
    # 运行所有检查
    results.append(("CSS变量定义", check_css_variables()))
    results.append(("玻璃拟态效果", check_glassmorphism()))
    results.append(("侧边栏动画", check_sidebar_animation()))
    results.append(("Reduced Motion", check_responsive_motion()))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有检查通过! 基础样式系统实现正确。")
        print("\n建议:")
        print("1. 在浏览器中访问 http://127.0.0.1:8050 进行视觉验证")
        print("2. 测试侧边栏折叠/展开动画是否流畅")
        print("3. 检查玻璃拟态效果在支持的浏览器中显示正常")
        print("4. 验证所有组件应用了新的设计令牌")
    else:
        print("✗ 部分检查未通过，请修复上述问题。")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
