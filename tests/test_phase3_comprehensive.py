# -*- coding: utf-8 -*-
"""
Phase 3 综合测试脚本
测试数据工坊、统计实验室和代码生成功能
"""
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Phase3Tester:
    def __init__(self):
        """初始化测试器"""
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "http://127.0.0.1:8050"
        self.test_results = []

    def log_test(self, test_name, passed, message=""):
        """记录测试结果"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message
        })

    def wait_for_element(self, by, value, timeout=10):
        """等待元素出现"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None

    def click_element(self, by, value):
        """点击元素"""
        try:
            element = self.wait_for_element(by, value)
            if element:
                element.click()
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            print(f"点击失败: {e}")
            return False

    def test_welcome_page(self):
        """测试欢迎页"""
        print("\n=== 测试欢迎页 ===")
        self.driver.get(self.base_url)
        time.sleep(2)

        # 检查页面标题
        try:
            title = self.driver.find_element(By.CLASS_NAME, "welcome-title")
            self.log_test("欢迎页标题显示", True, title.text)
        except:
            self.log_test("欢迎页标题显示", False, "未找到标题元素")

    def test_load_sample_data(self):
        """测试加载示例数据"""
        print("\n=== 测试加载示例数据 ===")

        # 点击示例数据按钮
        try:
            sample_buttons = self.driver.find_elements(By.CLASS_NAME, "sample-card")
            if sample_buttons:
                sample_buttons[0].click()
                time.sleep(2)
                self.log_test("加载示例数据", True, "成功点击示例数据")
            else:
                self.log_test("加载示例数据", False, "未找到示例数据按钮")
        except Exception as e:
            self.log_test("加载示例数据", False, str(e))

    def test_data_canvas(self):
        """测试数据画布"""
        print("\n=== 测试数据画布 ===")

        # 导航到数据画布
        try:
            nav_link = self.driver.find_element(By.XPATH, "//a[@href='/canvas']")
            nav_link.click()
            time.sleep(2)

            # 检查页面标题
            page_title = self.driver.find_element(By.CLASS_NAME, "page-title")
            self.log_test("数据画布页面加载", "数据画布" in page_title.text)

            # 检查数据表格
            try:
                table = self.driver.find_element(By.CLASS_NAME, "ag-root")
                self.log_test("数据表格显示", True, "AG Grid 已加载")
            except:
                self.log_test("数据表格显示", False, "未找到数据表格")

        except Exception as e:
            self.log_test("数据画布页面", False, str(e))

    def test_data_workshop(self):
        """测试数据工坊"""
        print("\n=== 测试数据工坊 ===")

        # 导航到数据工坊
        try:
            nav_link = self.driver.find_element(By.XPATH, "//a[@href='/workshop']")
            nav_link.click()
            time.sleep(2)

            # 检查页面标题
            page_title = self.driver.find_element(By.CLASS_NAME, "page-title")
            self.log_test("数据工坊页面加载", "数据工坊" in page_title.text)

            # 检查操作菜单
            try:
                accordion = self.driver.find_element(By.CLASS_NAME, "accordion")
                self.log_test("操作菜单显示", True, "找到操作菜单")
            except:
                self.log_test("操作菜单显示", False, "未找到操作菜单")

            # 检查操作流水线
            try:
                pipeline = self.driver.find_element(By.ID, "pipeline-list")
                self.log_test("操作流水线显示", True, "找到操作流水线")
            except:
                self.log_test("操作流水线显示", False, "未找到操作流水线")

            # 测试查看缺失值
            try:
                btn = self.driver.find_element(By.ID, "btn-view-missing")
                btn.click()
                time.sleep(2)
                self.log_test("查看缺失值功能", True, "按钮可点击")
            except Exception as e:
                self.log_test("查看缺失值功能", False, str(e))

        except Exception as e:
            self.log_test("数据工坊页面", False, str(e))

    def test_statistics_lab(self):
        """测试统计实验室"""
        print("\n=== 测试统计实验室 ===")

        # 导航到统计实验室
        try:
            nav_link = self.driver.find_element(By.XPATH, "//a[@href='/stats']")
            nav_link.click()
            time.sleep(2)

            # 检查页面标题
            page_title = self.driver.find_element(By.CLASS_NAME, "page-title")
            self.log_test("统计实验室页面加载", "统计实验室" in page_title.text)

            # 检查分析类型选择
            try:
                tabs = self.driver.find_elements(By.CLASS_NAME, "nav-link")
                self.log_test("分析类型标签显示", len(tabs) > 0, f"找到 {len(tabs)} 个标签")
            except:
                self.log_test("分析类型标签显示", False, "未找到标签")

            # 测试描述性统计
            try:
                # 查找描述性统计相关元素
                desc_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '描述性统计')]")
                if desc_elements:
                    self.log_test("描述性统计功能", True, "找到描述性统计选项")
                else:
                    self.log_test("描述性统计功能", False, "未找到描述性统计选项")
            except Exception as e:
                self.log_test("描述性统计功能", False, str(e))

            # 测试相关性分析
            try:
                corr_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '相关性分析')]")
                if corr_elements:
                    self.log_test("相关性分析功能", True, "找到相关性分析选项")
                else:
                    self.log_test("相关性分析功能", False, "未找到相关性分析选项")
            except Exception as e:
                self.log_test("相关性分析功能", False, str(e))

        except Exception as e:
            self.log_test("统计实验室页面", False, str(e))

    def test_chart_studio(self):
        """测试图表工作室"""
        print("\n=== 测试图表工作室 ===")

        # 导航到图表工作室
        try:
            nav_link = self.driver.find_element(By.XPATH, "//a[@href='/charts']")
            nav_link.click()
            time.sleep(2)

            # 检查页面标题
            page_title = self.driver.find_element(By.CLASS_NAME, "page-title")
            self.log_test("图表工作室页面加载", "图表工作室" in page_title.text)

            # 检查字段面板
            try:
                fields_panel = self.driver.find_element(By.CLASS_NAME, "fields-panel")
                self.log_test("字段面板显示", True, "找到字段面板")
            except:
                self.log_test("字段面板显示", False, "未找到字段面板")

            # 检查图表画布
            try:
                canvas = self.driver.find_element(By.ID, "chart-canvas")
                self.log_test("图表画布显示", True, "找到图表画布")
            except:
                self.log_test("图表画布显示", False, "未找到图表画布")

        except Exception as e:
            self.log_test("图表工作室页面", False, str(e))

    def test_navigation(self):
        """测试导航功能"""
        print("\n=== 测试导航功能 ===")

        pages = [
            ("/", "欢迎"),
            ("/canvas", "数据画布"),
            ("/workshop", "数据工坊"),
            ("/charts", "图表工作室"),
            ("/stats", "统计实验室"),
        ]

        for path, name in pages:
            try:
                self.driver.get(self.base_url + path)
                time.sleep(1)

                # 检查页面是否加载
                page_content = self.driver.find_element(By.CLASS_NAME, "page-container")
                self.log_test(f"导航到{name}", True, f"成功加载 {path}")
            except Exception as e:
                self.log_test(f"导航到{name}", False, str(e))

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed

        print(f"\n总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"通过率: {passed/total*100:.1f}%")

        if failed > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['name']}: {result['message']}")

    def run_all_tests(self):
        """运行所有测试"""
        try:
            print("开始 Phase 3 综合测试...")
            print("="*60)

            self.test_welcome_page()
            self.test_load_sample_data()
            self.test_navigation()
            self.test_data_canvas()
            self.test_data_workshop()
            self.test_statistics_lab()
            self.test_chart_studio()

            self.print_summary()

        except Exception as e:
            print(f"\n测试过程中发生错误: {e}")
        finally:
            print("\n测试完成，5秒后关闭浏览器...")
            time.sleep(5)
            self.driver.quit()


if __name__ == "__main__":
    print("Phase 3 综合测试")
    print("确保应用已在 http://127.0.0.1:8050 运行")
    print("按 Enter 开始测试...")
    input()

    tester = Phase3Tester()
    tester.run_all_tests()
