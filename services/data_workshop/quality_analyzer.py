"""
质量分析器

生成数据质量报告：概况、列分析、异常值检测、格式一致性检查。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class QualityAnalyzer:
    """质量分析器

    职责：
    - 分析数据质量指标
    - 识别数据质量问题
    - 生成质量报告
    """

    def __init__(self):
        pass

    # ── 整体分析 ─────────────────────────────────────────

    def analyze_dataframe(self, df: pd.DataFrame) -> Dict:
        """分析整个数据框"""
        rows, cols = df.shape
        total_cells = rows * cols
        missing_cells = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

        # 列分析
        column_reports = []
        for col in df.columns:
            column_reports.append(self.analyze_column(df[col]))

        # 汇总问题
        issues = self._collect_issues(df, column_reports)
        recommendations = self._generate_recommendations(issues)

        # 质量分数 (0-100)
        completeness = 1 - (missing_cells / max(total_cells, 1))
        uniqueness = 1 - (duplicate_rows / max(rows, 1))
        consistency = self._measure_consistency(column_reports)
        quality_score = round((completeness * 40 + uniqueness * 30 + consistency * 30), 1)

        return {
            'overview': {
                'rows': rows,
                'cols': cols,
                'total_cells': total_cells,
                'missing_cells': missing_cells,
                'missing_pct': round(missing_cells / max(total_cells, 1) * 100, 2),
                'duplicate_rows': duplicate_rows,
                'duplicate_pct': round(duplicate_rows / max(rows, 1) * 100, 2),
                'memory_mb': round(memory_mb, 2),
                'quality_score': quality_score,
            },
            'columns': column_reports,
            'issues': issues,
            'recommendations': recommendations,
        }

    # ── 列分析 ───────────────────────────────────────────

    def analyze_column(self, series: pd.Series) -> Dict:
        """分析单列"""
        name = series.name
        dtype = str(series.dtype)
        total = len(series)
        missing = int(series.isnull().sum())
        missing_pct = round(missing / max(total, 1) * 100, 2)
        valid = total - missing
        unique = int(series.nunique())
        dup_count = valid - unique

        report: Dict = {
            'name': name,
            'dtype': dtype,
            'total': total,
            'missing_count': missing,
            'missing_percent': missing_pct,
            'unique_count': unique,
            'duplicate_count': dup_count,
            'statistics': None,
            'patterns': None,
            'issues': [],
        }

        # 数值列统计
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            if len(clean) > 0:
                report['statistics'] = {
                    'mean': float(clean.mean()),
                    'median': float(clean.median()),
                    'std': float(clean.std()),
                    'min': float(clean.min()),
                    'max': float(clean.max()),
                    'q1': float(clean.quantile(0.25)),
                    'q3': float(clean.quantile(0.75)),
                    'skewness': float(clean.skew()),
                    'kurtosis': float(clean.kurtosis()),
                    'zeros': int((clean == 0).sum()),
                    'negatives': int((clean < 0).sum()),
                }
                # 异常值
                outliers = self.detect_outliers(series)
                report['outlier_indices'] = outliers
                report['outlier_count'] = len(outliers)

        # 字符串列统计
        elif pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            clean = series.dropna().astype(str)
            if len(clean) > 0:
                lengths = clean.str.len()
                vc = clean.value_counts()
                report['statistics'] = {
                    'min_length': int(lengths.min()),
                    'max_length': int(lengths.max()),
                    'mean_length': round(float(lengths.mean()), 1),
                    'top_value': str(vc.index[0]),
                    'top_freq': int(vc.iloc[0]),
                    'top_pct': round(vc.iloc[0] / len(clean) * 100, 2),
                }
                report['patterns'] = self.detect_format_inconsistency(series)

        # 日期列
        elif pd.api.types.is_datetime64_any_dtype(series):
            clean = series.dropna()
            if len(clean) > 0:
                report['statistics'] = {
                    'min_date': str(clean.min()),
                    'max_date': str(clean.max()),
                    'range_days': (clean.max() - clean.min()).days,
                }

        # 质量问题检测
        if missing_pct > 50:
            report['issues'].append({'severity': 'high', 'message': f"缺失值超过50% ({missing_pct}%)"})
        elif missing_pct > 20:
            report['issues'].append({'severity': 'medium', 'message': f"缺失值较多 ({missing_pct}%)"})

        if unique == 1 and total > 1:
            report['issues'].append({'severity': 'medium', 'message': "列为常量（仅单一值）"})

        if unique == total and total > 10:
            report['issues'].append({'severity': 'info', 'message': "列值全部唯一，可能是ID列"})

        return report

    # ── 异常值检测 ────────────────────────────────────────

    def detect_outliers(self, series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> List[int]:
        """检测异常值，返回索引列表"""
        clean = pd.to_numeric(series, errors='coerce').dropna()
        if len(clean) < 4:
            return []

        if method == 'iqr':
            q1 = clean.quantile(0.25)
            q3 = clean.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            mask = (clean < lower) | (clean > upper)
        elif method == 'zscore':
            mean = clean.mean()
            std = clean.std()
            if std == 0:
                return []
            z = ((clean - mean) / std).abs()
            mask = z > threshold
        else:
            return []

        return clean[mask].index.tolist()

    # ── 格式一致性检测 ───────────────────────────────────

    def detect_format_inconsistency(self, series: pd.Series) -> Dict:
        """检测格式不一致"""
        clean = series.dropna().astype(str)
        if len(clean) == 0:
            return {}

        result: Dict = {
            'has_whitespace': bool((clean != clean.str.strip()).any()),
            'has_mixed_case': False,
            'empty_strings': int((clean == '').sum()),
            'format_groups': {},
        }

        # 大小写不一致
        lowered = clean.str.lower()
        if lowered.nunique() < clean.nunique():
            result['has_mixed_case'] = True

        # 长度分组 (识别长度分布)
        lengths = clean.str.len()
        length_counts = lengths.value_counts().head(5)
        result['length_distribution'] = {int(k): int(v) for k, v in length_counts.items()}

        # 前导/尾随空格
        leading = int(clean.str.match(r'^\s').sum())
        trailing = int(clean.str.match(r'.*\s$').sum())
        result['leading_whitespace'] = leading
        result['trailing_whitespace'] = trailing

        return result

    # ── HTML 报告 ─────────────────────────────────────────

    def generate_report_html(self, analysis: Dict) -> str:
        """生成 HTML 格式的数据质量报告"""
        ov = analysis['overview']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 质量分数颜色
        score = ov['quality_score']
        if score >= 80:
            score_color = '#22c55e'
        elif score >= 60:
            score_color = '#eab308'
        else:
            score_color = '#ef4444'

        col_rows = ""
        for col in analysis['columns']:
            issues_html = ""
            for issue in col.get('issues', []):
                sev_color = {'high': '#ef4444', 'medium': '#eab308', 'info': '#3b82f6'}.get(issue['severity'], '#888')
                issues_html += f'<span style="color:{sev_color};font-size:12px;">⚠ {issue["message"]}</span><br/>'

            col_rows += f"""
            <tr>
                <td><strong>{col['name']}</strong></td>
                <td>{col['dtype']}</td>
                <td>{col['missing_count']} ({col['missing_percent']}%)</td>
                <td>{col['unique_count']}</td>
                <td>{col['duplicate_count']}</td>
                <td>{issues_html or '✓'}</td>
            </tr>"""

        issue_items = ""
        for issue in analysis['issues']:
            sev = issue.get('severity', 'info')
            sev_emoji = {'high': '🔴', 'medium': '🟡', 'info': '🔵'}.get(sev, 'ℹ️')
            issue_items += f"<li>{sev_emoji} {issue['message']}</li>\n"

        rec_items = ""
        for rec in analysis['recommendations']:
            rec_items += f"<li>💡 {rec}</li>\n"

        html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8"/>
<title>数据质量报告</title>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f8fafc; color: #334155; }}
h1 {{ color: #1e293b; }}
h2 {{ color: #475569; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
th, td {{ border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; }}
th {{ background: #f1f5f9; font-weight: 600; }}
.score-box {{ display: inline-block; padding: 16px 32px; border-radius: 12px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }}
.score-number {{ font-size: 48px; font-weight: 700; color: {score_color}; }}
.metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 16px 0; }}
.metric-card {{ background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
.metric-label {{ font-size: 13px; color: #94a3b8; }}
.metric-value {{ font-size: 24px; font-weight: 600; color: #1e293b; }}
</style>
</head>
<body>
<h1>📊 数据质量报告</h1>
<p style="color:#94a3b8;">生成时间: {timestamp}</p>

<h2>总体概况</h2>
<div style="display:flex;align-items:center;gap:32px;margin-bottom:24px;">
  <div class="score-box">
    <div class="score-number">{score}</div>
    <div style="color:#64748b;">质量分数</div>
  </div>
  <div class="metric-grid" style="flex:1;">
    <div class="metric-card"><div class="metric-label">行数</div><div class="metric-value">{ov['rows']:,}</div></div>
    <div class="metric-card"><div class="metric-label">列数</div><div class="metric-value">{ov['cols']}</div></div>
    <div class="metric-card"><div class="metric-label">缺失单元格</div><div class="metric-value">{ov['missing_cells']:,} ({ov['missing_pct']}%)</div></div>
    <div class="metric-card"><div class="metric-label">重复行</div><div class="metric-value">{ov['duplicate_rows']:,} ({ov['duplicate_pct']}%)</div></div>
    <div class="metric-card"><div class="metric-label">内存占用</div><div class="metric-value">{ov['memory_mb']} MB</div></div>
  </div>
</div>

<h2>各列详情</h2>
<table>
<thead>
<tr><th>列名</th><th>类型</th><th>缺失值</th><th>唯一值</th><th>重复值</th><th>问题</th></tr>
</thead>
<tbody>
{col_rows}
</tbody>
</table>

<h2>发现的问题</h2>
<ul>{issue_items or '<li>✅ 未发现明显问题</li>'}</ul>

<h2>建议操作</h2>
<ul>{rec_items or '<li>数据质量良好，无额外建议</li>'}</ul>

</body>
</html>"""
        return html

    # ── 内部辅助 ──────────────────────────────────────────

    def _collect_issues(self, df: pd.DataFrame, column_reports: List[Dict]) -> List[Dict]:
        """汇总所有问题"""
        issues = []

        # 整体问题
        dup_count = int(df.duplicated().sum())
        if dup_count > 0:
            issues.append({
                'severity': 'medium',
                'message': f"数据框包含 {dup_count} 行重复数据",
                'type': 'duplicate',
            })

        # 列级问题
        for col in column_reports:
            for issue in col.get('issues', []):
                issues.append({
                    'severity': issue['severity'],
                    'message': f"[{col['name']}] {issue['message']}",
                    'type': 'column',
                    'column': col['name'],
                })

            # 异常值
            outlier_count = col.get('outlier_count', 0)
            if outlier_count > 0:
                issues.append({
                    'severity': 'info',
                    'message': f"[{col['name']}] 检测到 {outlier_count} 个异常值",
                    'type': 'outlier',
                    'column': col['name'],
                })

            # 格式不一致
            patterns = col.get('patterns') or {}
            if patterns.get('has_whitespace'):
                issues.append({
                    'severity': 'low',
                    'message': f"[{col['name']}] 包含前导/尾随空格",
                    'type': 'format',
                    'column': col['name'],
                })
            if patterns.get('has_mixed_case'):
                issues.append({
                    'severity': 'low',
                    'message': f"[{col['name']}] 大小写不一致",
                    'type': 'format',
                    'column': col['name'],
                })

        return issues

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """根据问题生成建议"""
        recs = []
        seen = set()

        for issue in issues:
            t = issue.get('type', '')
            col = issue.get('column', '')

            if t == 'duplicate' and 'dup' not in seen:
                recs.append("使用「去重」操作清除重复行")
                seen.add('dup')
            elif '缺失值超过50%' in issue['message'] and f'drop_{col}' not in seen:
                recs.append(f"考虑删除缺失率过高的列 [{col}]")
                seen.add(f'drop_{col}')
            elif '缺失值较多' in issue['message'] and f'fill_{col}' not in seen:
                recs.append(f"对 [{col}] 使用「填充缺失值」进行数据修补")
                seen.add(f'fill_{col}')
            elif t == 'format' and 'whitespace' in issue['message'] and 'strip' not in seen:
                recs.append("使用「去除空格」清理前导/尾随空白")
                seen.add('strip')
            elif t == 'format' and '大小写' in issue['message'] and 'case' not in seen:
                recs.append("使用「大小写转换」统一文本格式")
                seen.add('case')
            elif t == 'outlier' and 'outlier' not in seen:
                recs.append("检查异常值，必要时使用 Winsorize 或筛选剔除")
                seen.add('outlier')

        return recs

    def _measure_consistency(self, column_reports: List[Dict]) -> float:
        """计算一致性分数 (0-1)"""
        if not column_reports:
            return 1.0

        scores = []
        for col in column_reports:
            col_score = 1.0
            patterns = col.get('patterns') or {}
            if patterns.get('has_whitespace'):
                col_score -= 0.2
            if patterns.get('has_mixed_case'):
                col_score -= 0.2
            if patterns.get('empty_strings', 0) > 0:
                col_score -= 0.1
            scores.append(max(col_score, 0))

        return sum(scores) / len(scores)
