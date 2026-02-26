# -*- coding: utf-8 -*-
"""
Phase 3 自动化测试脚本
自动启动应用并测试所有功能
"""
import sys
import time
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class Phase3AutoTester:
    def __init__(self):
        self.app_process = None
        self.driver = None
        self.base_url = "http://127.0.0.1:8050"

    def start_app(self):
        """启动应用"""
        print("Starting application...")
        self.app_process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 等待应用启动
        max_wait = 30
        for i in range(max_wait):
            try:
                response = requests.get(self.base_url, timeout=1)
                if response.status_code == 200:
                    print(f"Application started successfully after {i+1} seconds")
                    return True
            except:
                time.sleep(1)

        print("Failed to start application")
        return False

    def stop_app(self):
        """停止应用"""
        if self.app_process:
            print("Stopping application...")
            self.app_process.terminate()
            self.app_process.wait(timeout=5)

    def setup_browser(self):
        """设置浏览器"""
        print("Setting up browser...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(1920, 1080)
            print("Browser setup complete")
            return True
        except Exception as e:
            print(f"Failed to setup browser: {e}")
            return False

    def test_data_loading(self):
        """测试数据加载"""
        print("\n=== Testing Data Loading ===")
        try:
            self.driver.get(self.base_url)
            time.sleep(2)

            # 检查欢迎页面
            welcome_text = self.driver.find_element(By.TAG_NAME, "h1").text
            print(f"Welcome page loaded: {welcome_text}")

            # 点击数据中心
            data_hub_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "数据中心"))
            )
            data_hub_link.click()
            time.sleep(2)

            print("✓ Data loading test passed")
            return True
        except Exception as e:
            print(f"✗ Data loading test failed: {e}")
            return False

    def test_data_workshop(self):
        """测试数据工坊"""
        print("\n=== Testing Data Workshop ===")
        try:
            # 导航到数据工坊
            workshop_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "数据工坊"))
            )
            workshop_link.click()
            time.sleep(2)

            # 检查页面元素
            page_title = self.driver.find_element(By.TAG_NAME, "h2").text
            print(f"Workshop page loaded: {page_title}")

            print("✓ Data workshop test passed")
            return True
        except Exception as e:
            print(f"✗ Data workshop test failed: {e}")
            return False

    def test_statistics_lab(self):
        """测试统计实验室"""
        print("\n=== Testing Statistics Lab ===")
        try:
            # 导航到统计实验室
            stats_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "统计实验室"))
            )
            stats_link.click()
            time.sleep(2)

            # 检查页面元素
            page_title = self.driver.find_element(By.TAG_NAME, "h2").text
            print(f"Statistics lab page loaded: {page_title}")

            print("✓ Statistics lab test passed")
            return True
        except Exception as e:
            print(f"✗ Statistics lab test failed: {e}")
            return False

    def test_chart_studio(self):
        """测试图表工作室"""
        print("\n=== Testing Chart Studio ===")
        try:
            # 导航到图表工作室
            chart_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "图表工作室"))
            )
            chart_link.click()
            time.sleep(2)

            # 检查页面元素
            page_title = self.driver.find_element(By.TAG_NAME, "h2").text
            print(f"Chart studio page loaded: {page_title}")

            print("✓ Chart studio test passed")
            return True
        except Exception as e:
            print(f"✗ Chart studio test failed: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        results = []

        try:
            # 启动应用
            if not self.start_app():
                print("Failed to start application, aborting tests")
                return

            # 设置浏览器
            if not self.setup_browser():
                print("Failed to setup browser, aborting tests")
                return

            # 运行测试
            results.append(("Data Loading", self.test_data_loading()))
            results.append(("Data Workshop", self.test_data_workshop()))
            results.append(("Statistics Lab", self.test_statistics_lab()))
            results.append(("Chart Studio", self.test_chart_studio()))

            # 打印结果
            print("\n" + "="*60)
            print("TEST RESULTS")
            print("="*60)
            for test_name, passed in results:
                status = "PASSED" if passed else "FAILED"
                print(f"{test_name}: {status}")

            passed_count = sum(1 for _, passed in results if passed)
            total_count = len(results)
            print(f"\nTotal: {passed_count}/{total_count} tests passed")
            print("="*60)

        finally:
            # 清理
            if self.driver:
                self.driver.quit()
            self.stop_app()

if __name__ == "__main__":
    print("Phase 3 Automated Testing")
    print("="*60)

    tester = Phase3AutoTester()
    tester.run_all_tests()
