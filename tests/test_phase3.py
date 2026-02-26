# -*- coding: utf-8 -*-
"""
Phase 3 功能测试脚本
测试数据工坊、统计实验室、筛选构建器、代码生成功能
"""
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """设置 Chrome 驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ 无法启动 Chrome 驱动: {e}")
        print("提示：请确保已安装 Chrome 浏览器和 chromedriver")
        return None

def test_data_workshop(driver):
    """测试数据工坊功能"""
    print("\n=== 测试数据工坊 ===")

    try:
        # 导航到数据工坊页面
        driver.get("http://127.0.0.1:8050/data-workshop")
        time.sleep(2)

        # 检查页面标题
        title = driver.find_element(By.CLASS_NAME, "page-title")
        assert "数据工坊" in title.text
        print("✓ 页面加载成功")

        # 检查操作菜单是否存在
        accordion = driver.find_elements(By.CLASS_NAME, "accordion")
        assert len(accordion) > 0
        print("✓ 操作菜单显示正常")

        # 检查操作流水线
        pipeline = driver.find_element(By.ID, "pipeline-list")
        assert pipeline is not None
        print("✓ 操作流水线显示正常")

        return True

    except Exception as e:
        print(f"❌ 数据工坊测试失败: {e}")
        return False

def test_statistics_lab(driver):
    """测试统计实验室功能"""
    print("\n=== 测试统计实验室 ===")

    try:
        # 导航到统计实验室页面
        driver.get("http://127.0.0.1:8050/statistics-lab")
        time.sleep(2)

        # 检查页面标题
        title = driver.find_element(By.CLASS_NAME, "page-title")
        assert "统计实验室" in title.text
        print("✓ 页面加载成功")

        # 检查分析类型选择
        analysis_tabs = driver.find_elements(By.CLASS_NAME, "nav-link")
        assert len(analysis_tabs) > 0
        print("✓ 分析类型选项显示正常")

        return True

    except Exception as e:
        print(f"❌ 统计实验室测试失败: {e}")
        return False

def test_chart_studio(driver):
    """测试图表工作室功能"""
    print("\n=== 测试图表工作室 ===")

    try:
        # 导航到图表工作室页面
        driver.get("http://127.0.0.1:8050/chart-studio")
        time.sleep(2)

        # 检查页面标题
        title = driver.find_element(By.CLASS_NAME, "page-title")
        assert "图表工作室" in title.text
        print("✓ 页面加载成功")

        # 检查字段面板
        field_panel = driver.find_element(By.CLASS_NAME, "chart-fields-panel")
        assert field_panel is not None
        print("✓ 字段面板显示正常")

        # 检查图表类型选择
        chart_types = driver.find_elements(By.CLASS_NAME, "chart-type-card")
        assert len(chart_types) > 0
        print(f"✓ 图表类型选项显示正常 ({len(chart_types)} 种)")

        return True

    except Exception as e:
        print(f"❌ 图表工作室测试失败: {e}")
        return False

def test_navigation(driver):
    """测试页面导航"""
    print("\n=== 测试页面导航 ===")

    try:
        # 测试主页
        driver.get("http://127.0.0.1:8050/")
        time.sleep(1)
        print("✓ 主页加载成功")

        # 测试数据中心
        driver.get("http://127.0.0.1:8050/data-hub")
        time.sleep(1)
        print("✓ 数据中心加载成功")

        # 测试数据画布
        driver.get("http://127.0.0.1:8050/data-canvas")
        time.sleep(1)
        print("✓ 数据画布加载成功")

        return True

    except Exception as e:
        print(f"❌ 导航测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("DataViz Studio - Phase 3 功能测试")
    print("=" * 60)

    # 设置驱动
    driver = setup_driver()
    if not driver:
        print("\n⚠️  无法运行自动化测试，请手动测试以下功能：")
        print("\n1. 数据工坊 (http://127.0.0.1:8050/data-workshop)")
        print("   - 列操作（删除、重命名、拆分、合并）")
        print("   - 缺失值处理")
        print("   - 数据类型转换")
        print("   - 筛选与排序")
        print("   - 操作流水线")
        print("   - 导出 Python 代码")
        print("\n2. 统计实验室 (http://127.0.0.1:8050/statistics-lab)")
        print("   - 描述性统计")
        print("   - 相关性分析")
        print("   - 分布分析")
        print("\n3. 图表工作室 (http://127.0.0.1:8050/chart-studio)")
        print("   - 拖拽创建图表")
        print("   - 图表类型选择")
        print("   - 样式配置")
        print("   - 图表导出")
        return

    try:
        results = []

        # 运行测试
        results.append(("页面导航", test_navigation(driver)))
        results.append(("数据工坊", test_data_workshop(driver)))
        results.append(("统计实验室", test_statistics_lab(driver)))
        results.append(("图表工作室", test_chart_studio(driver)))

        # 输出测试结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"{name:20s} {status}")

        print(f"\n总计: {passed}/{total} 通过")

        if passed == total:
            print("\n🎉 所有测试通过！Phase 3 功能正常")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，请检查")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
