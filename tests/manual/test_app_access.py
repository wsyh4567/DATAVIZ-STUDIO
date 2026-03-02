"""
测试应用是否可以正常访问
"""

import requests
import time

def test_app_access():
    """测试应用访问"""
    url = "http://127.0.0.1:8050/"
    
    print("=" * 60)
    print("应用访问测试")
    print("=" * 60)
    
    try:
        print(f"\n正在访问: {url}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ 应用响应成功 (状态码: {response.status_code})")
            print(f"✅ 页面大小: {len(response.text)} 字节")
            
            # 检查是否包含关键内容
            if "DataViz Studio" in response.text:
                print("✅ 页面包含 'DataViz Studio' 标题")
            
            if "data-workshop" in response.text:
                print("✅ 页面包含数据工坊组件")
            
            # 检查是否有错误信息
            if "Duplicate callback" in response.text:
                print("❌ 页面包含重复回调错误")
                return False
            else:
                print("✅ 没有发现重复回调错误")
            
            print("\n✅ 应用运行正常!")
            return True
        else:
            print(f"❌ 应用响应异常 (状态码: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到应用 (应用可能未启动)")
        print("\n请先运行: python app.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    finally:
        print("=" * 60)

if __name__ == '__main__':
    success = test_app_access()
    exit(0 if success else 1)
