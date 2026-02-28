"""测试Chart Studio回调修复"""
import pandas as pd
from core.data_manager import DataManager
from pages.chart_studio import create_chart_studio_page

def test_page_initialization():
    """测试页面初始化"""
    print("测试Chart Studio页面初始化...")
    
    # 创建测试数据
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'category': ['A', 'B', 'A', 'B', 'A']
    })
    
    # 加载数据到DataManager
    dm = DataManager()
    dm.add_dataset("test_data", df, "test")
    
    try:
        # 创建页面
        page = create_chart_studio_page()
        print("   ✓ 页面创建成功")
        
        # 检查页面结构
        if page is not None:
            print("   ✓ 页面对象不为空")
            
            # 检查是否包含必要的组件ID
            page_str = str(page)
            required_ids = [
                'chart-studio-page',
                'chart-library-selector',
                'chart-type-selector',
                'params-panel-container',
                'chart-container'
            ]
            
            missing_ids = []
            for component_id in required_ids:
                if component_id not in page_str:
                    missing_ids.append(component_id)
            
            if missing_ids:
                print(f"   ✗ 缺少组件ID: {missing_ids}")
                return False
            else:
                print(f"   ✓ 所有必需组件ID都存在")
            
            # 检查param-x是否在初始布局中
            if 'param-x' in page_str:
                print("   ✓ param-x组件在初始布局中存在")
            else:
                print("   ✗ param-x组件不在初始布局中")
                return False
            
            return True
        else:
            print("   ✗ 页面对象为空")
            return False
            
    except Exception as e:
        print(f"   ✗ 页面创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Chart Studio回调修复验证")
    print("=" * 50)
    
    result = test_page_initialization()
    
    print("\n" + "=" * 50)
    if result:
        print("✓ 测试通过！param-x组件现在在初始布局中")
    else:
        print("✗ 测试失败")
    print("=" * 50)
