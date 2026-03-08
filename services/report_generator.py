# -*- coding: utf-8 -*-
"""HTML 分析报告生成器

生成独立的 HTML 分析报告文件，内嵌 CSS 和 Plotly CDN 图表。
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

from services.profiling_service import ProfilingService


class ReportGenerator:
    """HTML 分析报告生成器"""

    @staticmethod
    def generate_html_report(df: pd.DataFrame, name: str = "数据集") -> str:
        """生成独立的 HTML 分析报告

        Args:
            df: 数据框
            name: 数据集名称

        Returns:
            HTML 字符串
        """
        service = ProfilingService()
        profile = service.profile_dataframe(df)
        ov = profile["overview"]
        alerts = profile["alerts"]
        columns = profile["columns"]

        # 生成图表 HTML
        charts_html = ReportGenerator._generate_charts_html(df, columns)
        corr_html = ReportGenerator._generate_correlation_html(df)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 预警 HTML
        alerts_html = ""
        if alerts:
            alert_items = "\n".join([
                f'<div class="alert-item">{a["icon"]} <strong>{a["column"]}</strong>: {a["message"]}</div>'
                for a in alerts
            ])
            alerts_html = f'''
            <div class="section">
                <h2>⚠️ 数据质量预警 ({len(alerts)} 项)</h2>
                {alert_items}
            </div>
            '''

        # 列统计表
        cols_table = ReportGenerator._generate_columns_table(columns)

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataViz Studio - {name} 分析报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {{
            --bg: #0F1117; --bg2: #1B1D2A; --bg3: #262940;
            --accent: #6366F1; --text: #F1F5F9; --muted: #94A3B8;
            --success: #10B981; --warning: #F59E0B; --error: #EF4444;
            --border: #334155;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg); color: var(--text);
            padding: 2rem; max-width: 1200px; margin: 0 auto;
        }}
        h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
        h2 {{ font-size: 1.2rem; margin-bottom: 1rem; color: var(--accent); }}
        .subtitle {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 2rem; }}
        .section {{ background: var(--bg2); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid var(--border); }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }}
        .kpi {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; text-align: center; }}
        .kpi-value {{ font-size: 1.5rem; font-weight: 700; }}
        .kpi-label {{ font-size: 0.75rem; color: var(--muted); margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; }}
        th {{ background: var(--bg3); text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); }}
        td {{ padding: 6px 10px; border-bottom: 1px solid var(--border); }}
        tr:hover {{ background: var(--bg3); }}
        .alert-item {{ padding: 8px 12px; margin-bottom: 6px; border-left: 3px solid var(--warning); background: rgba(245,158,11,0.05); border-radius: 0 6px 6px 0; font-size: 0.85rem; }}
        .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1rem; }}
        .chart-card {{ background: var(--bg3); border-radius: 8px; padding: 0.5rem; }}
        .footer {{ text-align: center; color: var(--muted); font-size: 0.75rem; padding: 2rem 0; }}
    </style>
</head>
<body>
    <h1>{name} — 数据分析报告</h1>
    <p class="subtitle">由 DataViz Studio 生成 · {timestamp}</p>

    <div class="kpi-grid">
        <div class="kpi"><div class="kpi-value">{ov["rows"]:,}</div><div class="kpi-label">行数</div></div>
        <div class="kpi"><div class="kpi-value">{ov["cols"]}</div><div class="kpi-label">列数</div></div>
        <div class="kpi"><div class="kpi-value">{ov["missing_pct"]}%</div><div class="kpi-label">缺失率</div></div>
        <div class="kpi"><div class="kpi-value">{ov["duplicate_rows"]:,}</div><div class="kpi-label">重复行</div></div>
        <div class="kpi"><div class="kpi-value">{ov["memory_mb"]} MB</div><div class="kpi-label">内存占用</div></div>
        <div class="kpi"><div class="kpi-value">{ov["numeric_cols"]}</div><div class="kpi-label">数值列</div></div>
    </div>

    {alerts_html}

    <div class="section">
        <h2>列统计信息</h2>
        {cols_table}
    </div>

    <div class="section">
        <h2>数据分布</h2>
        <div class="charts-grid">{charts_html}</div>
    </div>

    {corr_html}

    <div class="footer">
        Generated by DataViz Studio · MIT License · {timestamp}
    </div>
</body>
</html>'''

        return html

    @staticmethod
    def _generate_columns_table(columns: dict) -> str:
        """生成列统计表 HTML"""
        rows = []
        for name, profile in columns.items():
            col_type = profile.get("type", "")
            type_badge = {"numeric": "🔢", "categorical": "🏷️", "datetime": "📅"}.get(col_type, "")
            missing_str = f'{profile["missing"]} ({profile["missing_pct"]}%)'

            extra = ""
            if col_type == "numeric":
                extra = f'均值={profile.get("mean", "")}, 标准差={profile.get("std", "")}'
            elif col_type == "categorical":
                extra = f'最频值: {profile.get("most_common", "")}'

            rows.append(f'''<tr>
                <td>{type_badge} <strong>{name}</strong></td>
                <td>{profile.get("dtype", "")}</td>
                <td>{profile["count"]:,}</td>
                <td>{missing_str}</td>
                <td>{profile["unique"]:,}</td>
                <td>{extra}</td>
            </tr>''')

        return f'''<table>
            <thead><tr><th>列名</th><th>类型</th><th>有效值</th><th>缺失</th><th>唯一值</th><th>摘要</th></tr></thead>
            <tbody>{"".join(rows)}</tbody>
        </table>'''

    @staticmethod
    def _generate_charts_html(df, columns):
        """生成分布图 HTML"""
        charts = []
        count = 0
        for col_name, profile in columns.items():
            if count >= 6:
                break
            try:
                series = df[col_name]
                fig = ProfilingService.generate_column_chart(series)
                fig.update_layout(title=col_name, title_font_size=12)
                chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
                charts.append(f'<div class="chart-card">{chart_html}</div>')
                count += 1
            except Exception:
                continue
        return "\n".join(charts) if charts else "<p>无可视化数据</p>"

    @staticmethod
    def _generate_correlation_html(df):
        """生成相关性热力图 HTML"""
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) < 2:
            return ""

        corr = numeric_df.corr().round(2)
        fig = px.imshow(
            corr, text_auto=True,
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        )
        fig.update_layout(
            template="plotly_white",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)

        return f'''
        <div class="section">
            <h2>🔗 相关性分析</h2>
            <div class="chart-card">{chart_html}</div>
        </div>'''
