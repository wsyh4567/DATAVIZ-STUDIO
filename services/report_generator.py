# -*- coding: utf-8 -*-
"""HTML analysis report generator."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.io as pio

from services.eda_service import EDAService


class ReportGenerator:
    """Generate a standalone HTML EDA report."""

    @staticmethod
    def generate_html_report(
        df: pd.DataFrame,
        name: str = "数据集",
        mode: str = "full",
        sample_size: Optional[int] = None,
    ) -> str:
        report = EDAService.analyze_dataset(df, mode=mode, sample_size=sample_size)
        overview = report["overview"]
        sample_meta = report["sample_meta"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        missing_bar_html = pio.to_html(
            EDAService.create_missing_bar_chart(report),
            full_html=False,
            include_plotlyjs=False,
        )
        missing_heatmap_html = pio.to_html(
            EDAService.create_missing_heatmap(report),
            full_html=False,
            include_plotlyjs=False,
        )
        corr_heatmap_html = pio.to_html(
            EDAService.create_correlation_heatmap(report),
            full_html=False,
            include_plotlyjs=False,
        )
        quick_distribution_html = ReportGenerator._generate_distribution_html(df, report)

        alert_cards = "".join(
            [
                f"""
                <div class=\"alert-card alert-{item['severity']}\">
                    <div class=\"alert-title\">{item['title']}</div>
                    <div class=\"alert-message\">{item['message']}</div>
                    <div class=\"alert-action\">建议：{item['suggested_action']}</div>
                </div>
                """
                for item in report["quality_alerts"]
            ]
        ) or '<div class="empty-text">未发现明显质量告警。</div>'

        numeric_table = ReportGenerator._render_table(
            [
                ("字段", "name"),
                ("缺失率", "missing_pct"),
                ("均值", "mean"),
                ("中位数", "median"),
                ("偏度", "skewness"),
                ("异常值%", "outlier_pct"),
            ],
            report["numeric_profiles"],
        )
        categorical_table = ReportGenerator._render_table(
            [
                ("字段", "name"),
                ("缺失率", "missing_pct"),
                ("唯一值", "unique_count"),
                ("Top 值", "top_value"),
                ("Top 占比", "top_pct"),
                ("疑似 ID", "is_id_like"),
            ],
            report["categorical_profiles"],
        )
        datetime_table = ReportGenerator._render_table(
            [
                ("字段", "name"),
                ("缺失率", "missing_pct"),
                ("最早时间", "min_date"),
                ("最晚时间", "max_date"),
                ("跨度天数", "range_days"),
                ("频率", "inferred_freq"),
            ],
            report["datetime_profiles"],
        )

        relationship_html = ReportGenerator._render_relationships(report["relationship_findings"])

        sample_summary = "全量分析"
        if sample_meta["used_sampling"]:
            sample_summary = (
                f"采样分析：样本 {sample_meta['sample_rows']:,} 行，"
                f"占全量 {sample_meta['sample_ratio'] * 100:.1f}%。"
            )

        return f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>DataViz Studio - {name} EDA 报告</title>
    <script src=\"https://cdn.plot.ly/plotly-2.35.2.min.js\"></script>
    <style>
        :root {{
            --bg: #F4F5F7;
            --surface: #FFFFFF;
            --surface-alt: #EDF2F7;
            --border: #E2E8F0;
            --text: #1A202C;
            --muted: #718096;
            --accent: #FF6B35;
            --accent-soft: rgba(255, 107, 53, 0.08);
            --success: #38A169;
            --warning: #DD6B20;
            --info: #3182CE;
            --shadow: 0 10px 20px rgba(15, 23, 42, 0.06);
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 32px;
        }}
        .page {{ max-width: 1320px; margin: 0 auto; }}
        .hero {{ margin-bottom: 24px; }}
        .hero h1 {{ margin: 0 0 8px; font-size: 32px; }}
        .subtitle {{ color: var(--muted); font-size: 14px; }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: var(--shadow);
            padding: 20px;
            margin-bottom: 20px;
        }}
        .section-title {{ margin: 0 0 6px; font-size: 20px; }}
        .section-subtitle {{ margin: 0 0 16px; color: var(--muted); font-size: 14px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; }}
        .kpi {{ background: var(--surface-alt); border: 1px solid var(--border); border-radius: 14px; padding: 16px; }}
        .kpi-label {{ color: var(--muted); font-size: 13px; margin-bottom: 8px; }}
        .kpi-value {{ font-size: 24px; font-weight: 700; }}
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 6px 10px;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--accent);
            font-size: 12px;
            font-weight: 600;
            margin-top: 12px;
        }}
        .split {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 16px; }}
        .chart-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
        .distribution-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }}
        .alert-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
        .alert-card {{ border-radius: 14px; border: 1px solid var(--border); padding: 14px; background: #FFFDFB; }}
        .alert-warning {{ border-left: 4px solid var(--warning); }}
        .alert-info {{ border-left: 4px solid var(--info); }}
        .alert-title {{ font-size: 15px; font-weight: 700; margin-bottom: 6px; }}
        .alert-message, .alert-action {{ color: var(--muted); font-size: 13px; line-height: 1.5; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); text-align: left; }}
        th {{ color: var(--muted); font-weight: 600; background: #FAFAFA; }}
        .table-wrap {{ overflow-x: auto; }}
        .list {{ margin: 0; padding-left: 18px; color: var(--text); }}
        .list li {{ margin-bottom: 8px; }}
        .empty-text {{ color: var(--muted); font-size: 14px; }}
        .footer {{ text-align: center; color: var(--muted); font-size: 12px; padding: 16px 0 8px; }}
        @media (max-width: 1100px) {{
            .kpi-grid, .distribution-grid, .chart-grid, .split, .alert-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class=\"page\">
        <div class=\"hero\">
            <h1>{name} 数据探索报告</h1>
            <div class=\"subtitle\">生成时间：{timestamp}</div>
            <div class=\"badge\">{sample_summary}</div>
        </div>

        <div class=\"card\">
            <h2 class=\"section-title\">数据总览</h2>
            <p class=\"section-subtitle\">当前分析模式、体量和基础质量指标。</p>
            <div class=\"kpi-grid\">
                <div class=\"kpi\"><div class=\"kpi-label\">行数</div><div class=\"kpi-value\">{overview['rows']:,}</div></div>
                <div class=\"kpi\"><div class=\"kpi-label\">列数</div><div class=\"kpi-value\">{overview['cols']}</div></div>
                <div class=\"kpi\"><div class=\"kpi-label\">内存</div><div class=\"kpi-value\">{overview['memory_mb']:.1f} MB</div></div>
                <div class=\"kpi\"><div class=\"kpi-label\">缺失率</div><div class=\"kpi-value\">{overview['missing_pct']:.2f}%</div></div>
                <div class=\"kpi\"><div class=\"kpi-label\">重复率</div><div class=\"kpi-value\">{overview['duplicate_pct']:.2f}%</div></div>
                <div class=\"kpi\"><div class=\"kpi-label\">质量分</div><div class=\"kpi-value\">{overview['quality_score']:.1f}</div></div>
            </div>
        </div>

        <div class=\"card\">
            <h2 class=\"section-title\">自动洞察</h2>
            <p class=\"section-subtitle\">按严重度排序的质量告警与建议动作。</p>
            <div class=\"alert-grid\">{alert_cards}</div>
        </div>

        <div class=\"card\">
            <h2 class=\"section-title\">缺失分析</h2>
            <p class=\"section-subtitle\">{report['missingness']['summary']}</p>
            <div class=\"chart-grid\">
                <div>{missing_bar_html}</div>
                <div>{missing_heatmap_html}</div>
            </div>
        </div>

        <div class=\"card\">
            <h2 class=\"section-title\">字段画像</h2>
            <p class=\"section-subtitle\">数值、类别、时间字段的核心摘要。</p>
            <div class=\"split\">
                <div class=\"table-wrap\">{numeric_table}</div>
                <div class=\"table-wrap\">{categorical_table}</div>
            </div>
            <div class=\"table-wrap\" style=\"margin-top:16px;\">{datetime_table}</div>
        </div>

        <div class=\"card\">
            <h2 class=\"section-title\">关系发现</h2>
            <p class=\"section-subtitle\">强相关数值对、类别-数值差异和类别组合热点。</p>
            <div class=\"split\">
                <div>{relationship_html}</div>
                <div>{corr_heatmap_html}</div>
            </div>
        </div>

        <div class=\"card\">
            <h2 class=\"section-title\">快速分布</h2>
            <p class=\"section-subtitle\">优先展示最值得查看的数值和类别字段分布。</p>
            <div class=\"distribution-grid\">{quick_distribution_html}</div>
        </div>

        <div class=\"footer\">Generated by DataViz Studio · {timestamp}</div>
    </div>
</body>
</html>"""

    @staticmethod
    def _render_table(columns: List[tuple[str, str]], rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return '<div class="empty-text">暂无可展示字段。</div>'
        header = "".join(f"<th>{label}</th>" for label, _ in columns)
        body_rows = []
        for row in rows:
            cells = []
            for _, key in columns:
                value = row.get(key, "-")
                if isinstance(value, float):
                    value = f"{value:.2f}"
                elif isinstance(value, bool):
                    value = "是" if value else "否"
                cells.append(f"<td>{value}</td>")
            body_rows.append(f"<tr>{''.join(cells)}</tr>")
        return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"

    @staticmethod
    def _render_relationships(relationships: Dict[str, Any]) -> str:
        sections = []
        numeric_pairs = relationships["numeric_pairs"]
        if numeric_pairs:
            sections.append(
                "<h3 style='margin:0 0 10px;font-size:16px;'>强相关数值对</h3>"
                + "<ul class='list'>"
                + "".join(
                    [
                        f"<li>{item['var1']} / {item['var2']} · r={item['correlation']:.2f} · {item['strength']}</li>"
                        for item in numeric_pairs[:6]
                    ]
                )
                + "</ul>"
            )
        category_numeric = relationships["categorical_numeric_pairs"]
        if category_numeric:
            sections.append(
                "<h3 style='margin:18px 0 10px;font-size:16px;'>类别-数值差异</h3>"
                + "<ul class='list'>"
                + "".join(
                    [
                        f"<li>{item['category']} 对 {item['numeric']} 的均值差为 {item['mean_spread']:.2f}，最高组 {item['top_group']}，最低组 {item['bottom_group']}。</li>"
                        for item in category_numeric[:5]
                    ]
                )
                + "</ul>"
            )
        category_pairs = relationships["categorical_pairs"]
        if category_pairs:
            sections.append(
                "<h3 style='margin:18px 0 10px;font-size:16px;'>类别组合热点</h3>"
                + "<ul class='list'>"
                + "".join(
                    [
                        f"<li>{item['var1']} / {item['var2']} 的高频组合是 {item['top_combination']}，出现 {item['count']} 次。</li>"
                        for item in category_pairs[:5]
                    ]
                )
                + "</ul>"
            )
        return "".join(sections) or '<div class="empty-text">暂无可展示的关系发现。</div>'

    @staticmethod
    def _generate_distribution_html(df: pd.DataFrame, report: Dict[str, Any]) -> str:
        charts = []
        for item in report["quick_distributions"]["numeric"]:
            chart_html = pio.to_html(
                EDAService.create_numeric_distribution(df[item["name"]]),
                full_html=False,
                include_plotlyjs=False,
            )
            charts.append(f"<div>{chart_html}</div>")
        for item in report["quick_distributions"]["categorical"]:
            chart_html = pio.to_html(
                EDAService.create_categorical_distribution(df[item["name"]]),
                full_html=False,
                include_plotlyjs=False,
            )
            charts.append(f"<div>{chart_html}</div>")
        return "".join(charts) or '<div class="empty-text">暂无分布图。</div>'
