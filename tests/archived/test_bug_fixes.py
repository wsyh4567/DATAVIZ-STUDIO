"""测试bug修复"""
import pandas as pd
from services.data_workshop.type_detector import TypeDetector
from services.chart_service import ChartType, ChartLibrary, ChartService

def test_timestamp_fix():
    """测试Timestamp.strptime修复"""
    print("测试1: TypeDetector日期解析...")
    
    # 创建测试数据
    df = pd.DataFrame({
        'date_col': ['2024-01-01', '2024-01-02', '2024-01-03']
    })
    
    td = TypeDetector()
    try:
        result = td.detect_column_type(df['date_col'])
        print(f"   ✓ 日期检测成功: {result}")
        return True
    except Exception as e:
        print(f"   ✗ 日期检测失败: {e}")
        return False

def test_charttype_fix():
    """测试ChartType None值处理"""
    print("\n测试2: ChartType枚举验证...")
    
    # 测试有效的图表类型
    valid_types = ['scatter', 'line', 'bar', 'histogram']
    
    for chart_type in valid_types:
        try:
            ct = ChartType(chart_type)
            print(f"   ✓ ChartType('{chart_type}') = {ct.value}")
        except Exception as e:
            print(f"   ✗ ChartType('{chart_type}') 失败: {e}")
            return False
    
    # 测试None值
    try:
        ct = ChartType(None)
        print(f"   ✗ ChartType(None) 应该失败但成功了")
        return False
    except Exception as e:
        print(f"   ✓ ChartType(None) 正确抛出异常: {type(e).__name__}")
    
    return True

def test_chart_creation():
    """测试图表创建"""
    print("\n测试3: 图表创建...")
    
    # 创建测试数据
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10]
    })
    
    chart_service = ChartService()
    
    try:
        result = chart_service.create_chart(
            df=df,
            chart_type=ChartType('scatter'),
            params={'x': 'x', 'y': 'y'}
        )
        print(f"   ✓ 图表创建成功")
        return True
    except Exception as e:
        print(f"   ✗ 图表创建失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Bug修复验证测试")
    print("=" * 50)
    
    results = []
    results.append(test_timestamp_fix())
    results.append(test_charttype_fix())
    results.append(test_chart_creation())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败")
    print("=" * 50)
