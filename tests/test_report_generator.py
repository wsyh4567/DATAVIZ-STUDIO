import pandas as pd

from services.report_generator import ReportGenerator


def test_html_report_uses_new_eda_sections():
    df = pd.DataFrame(
        {
            "value": [1, 2, 3, 4, None, 200],
            "category": ["A", "B", "A", "B", "C", "C"],
        }
    )

    html = ReportGenerator.generate_html_report(df, name="demo", mode="sample", sample_size=4)

    assert "自动洞察" in html
    assert "缺失分析" in html
    assert "字段画像" in html
    assert "关系发现" in html
    assert "快速分布" in html
    assert "采样分析" in html
