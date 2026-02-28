# -*- coding: utf-8 -*-
"""
统计分析服务 - 提供各种统计分析功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats


class StatsService:
    """统计分析服务类"""

    @staticmethod
    def descriptive_stats(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        描述性统计

        Args:
            df: 数据框
            column: 列名

        Returns:
            统计信息字典
        """
        series = df[column]
        result = {
            'column': column,
            'dtype': str(series.dtype),
            'count': int(series.count()),
            'missing': int(series.isnull().sum()),
            'missing_pct': float(series.isnull().sum() / len(series) * 100),
        }

        # 数值列统计
        if pd.api.types.is_numeric_dtype(series):
            result.update({
                'mean': float(series.mean()),
                'median': float(series.median()),
                'std': float(series.std()),
                'min': float(series.min()),
                'max': float(series.max()),
                'q25': float(series.quantile(0.25)),
                'q75': float(series.quantile(0.75)),
                'skewness': float(series.skew()),
                'kurtosis': float(series.kurtosis()),
            })

            # 判断分布类型
            if abs(result['skewness']) < 0.5:
                result['distribution'] = '近似正态分布'
            elif result['skewness'] > 0:
                result['distribution'] = '右偏分布'
            else:
                result['distribution'] = '左偏分布'

        # 分类列统计
        elif pd.api.types.is_object_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
            value_counts = series.value_counts()
            result.update({
                'unique': int(series.nunique()),
                'top': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'top_freq': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'top_pct': float(value_counts.iloc[0] / series.count() * 100) if len(value_counts) > 0 else 0,
            })

        # 日期列统计
        elif pd.api.types.is_datetime64_any_dtype(series):
            result.update({
                'min_date': str(series.min()),
                'max_date': str(series.max()),
                'range_days': int((series.max() - series.min()).days),
            })

        return result

    @staticmethod
    def correlation_matrix(df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
        """
        计算相关矩阵

        Args:
            df: 数据框
            method: 相关系数方法 (pearson/spearman/kendall)

        Returns:
            相关矩阵
        """
        # 只选择数值列
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            raise ValueError("数据集中没有数值列")

        return numeric_df.corr(method=method)

    @staticmethod
    def correlation_pairs(df: pd.DataFrame, threshold: float = 0.5,
                         method: str = 'pearson') -> List[Dict[str, Any]]:
        """
        获取相关性强的变量对

        Args:
            df: 数据框
            threshold: 相关系数阈值
            method: 相关系数方法

        Returns:
            相关变量对列表
        """
        corr_matrix = StatsService.correlation_matrix(df, method)
        pairs = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]

                if abs(corr_value) >= threshold:
                    pairs.append({
                        'var1': col1,
                        'var2': col2,
                        'correlation': float(corr_value),
                        'abs_correlation': abs(float(corr_value)),
                        'strength': StatsService._correlation_strength(corr_value),
                    })

        # 按相关系数绝对值排序
        pairs.sort(key=lambda x: x['abs_correlation'], reverse=True)

        return pairs

    @staticmethod
    def _correlation_strength(corr: float) -> str:
        """判断相关强度"""
        abs_corr = abs(corr)
        if abs_corr >= 0.8:
            return "强相关" if corr > 0 else "强负相关"
        elif abs_corr >= 0.5:
            return "中等相关" if corr > 0 else "中等负相关"
        elif abs_corr >= 0.3:
            return "弱相关" if corr > 0 else "弱负相关"
        else:
            return "微弱相关"

    @staticmethod
    def group_aggregate(df: pd.DataFrame, group_by: List[str],
                       agg_column: str, agg_func: str) -> pd.DataFrame:
        """
        分组聚合分析

        Args:
            df: 数据框
            group_by: 分组列
            agg_column: 聚合列
            agg_func: 聚合函数 (sum/mean/median/count/min/max/std)

        Returns:
            聚合结果
        """
        agg_funcs = {
            'sum': 'sum',
            'mean': 'mean',
            'median': 'median',
            'count': 'count',
            'min': 'min',
            'max': 'max',
            'std': 'std',
        }

        if agg_func not in agg_funcs:
            raise ValueError(f"不支持的聚合函数: {agg_func}")

        result = df.groupby(group_by)[agg_column].agg(agg_funcs[agg_func]).reset_index()
        result.columns = list(group_by) + [f"{agg_column}_{agg_func}"]

        return result

    @staticmethod
    def detect_outliers(df: pd.DataFrame, column: str,
                       method: str = 'iqr') -> Dict[str, Any]:
        """
        异常值检测

        Args:
            df: 数据框
            column: 列名
            method: 检测方法 (iqr/zscore)

        Returns:
            异常值信息
        """
        series = df[column].dropna()

        if method == 'iqr':
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = series[(series < lower_bound) | (series > upper_bound)]

            return {
                'method': 'IQR',
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'outlier_count': len(outliers),
                'outlier_pct': float(len(outliers) / len(series) * 100),
                'outlier_indices': outliers.index.tolist(),
                'outlier_values': outliers.tolist(),
            }

        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(series))
            threshold = 3
            outliers = series[z_scores > threshold]

            return {
                'method': 'Z-Score',
                'threshold': threshold,
                'outlier_count': len(outliers),
                'outlier_pct': float(len(outliers) / len(series) * 100),
                'outlier_indices': outliers.index.tolist(),
                'outlier_values': outliers.tolist(),
            }

        else:
            raise ValueError(f"不支持的检测方法: {method}")

    @staticmethod
    def normality_test(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        正态性检验 (Shapiro-Wilk)

        Args:
            df: 数据框
            column: 列名

        Returns:
            检验结果
        """
        series = df[column].dropna()

        if len(series) < 3:
            return {
                'error': '样本量太小，无法进行检验'
            }

        # Shapiro-Wilk 检验
        statistic, p_value = stats.shapiro(series)

        return {
            'test': 'Shapiro-Wilk',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'is_normal': p_value > 0.05,
            'interpretation': '数据符合正态分布' if p_value > 0.05 else '数据不符合正态分布',
        }

    @staticmethod
    def t_test(df: pd.DataFrame, column: str, group_column: str) -> Dict[str, Any]:
        """
        独立样本 t 检验

        Args:
            df: 数据框
            column: 数值列
            group_column: 分组列（必须有且仅有两个组）

        Returns:
            检验结果
        """
        groups = df[group_column].unique()

        if len(groups) != 2:
            return {
                'error': '分组列必须有且仅有两个组'
            }

        group1 = df[df[group_column] == groups[0]][column].dropna()
        group2 = df[df[group_column] == groups[1]][column].dropna()

        # 独立样本 t 检验
        statistic, p_value = stats.ttest_ind(group1, group2)

        return {
            'test': '独立样本 t 检验',
            'group1': str(groups[0]),
            'group2': str(groups[1]),
            'group1_mean': float(group1.mean()),
            'group2_mean': float(group2.mean()),
            'statistic': float(statistic),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'interpretation': f"两组数据{'存在' if p_value < 0.05 else '不存在'}显著差异 (p={p_value:.4f})",
        }

    @staticmethod
    def chi_square_test(df: pd.DataFrame, col1: str, col2: str) -> Dict[str, Any]:
        """
        卡方检验（检验两个分类变量是否相关）

        Args:
            df: 数据框
            col1: 分类列1
            col2: 分类列2

        Returns:
            检验结果
        """
        # 创建交叉表
        contingency_table = pd.crosstab(df[col1], df[col2])

        # 卡方检验
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

        return {
            'test': '卡方检验',
            'variable1': col1,
            'variable2': col2,
            'chi2': float(chi2),
            'p_value': float(p_value),
            'dof': int(dof),
            'significant': p_value < 0.05,
            'interpretation': f"两个变量{'存在' if p_value < 0.05 else '不存在'}显著关联 (p={p_value:.4f})",
        }

    @staticmethod
    def generate_summary(stats_dict: Dict[str, Any]) -> str:
        """
        生成自然语言统计摘要

        Args:
            stats_dict: 统计信息字典

        Returns:
            自然语言摘要
        """
        if 'mean' in stats_dict:
            # 数值列摘要
            summary = f"该列包含 {stats_dict['count']:,} 个有效值"

            if stats_dict['missing'] > 0:
                summary += f"，{stats_dict['missing']:,} 个缺失值（{stats_dict['missing_pct']:.1f}%）"

            summary += f"。数值范围从 {stats_dict['min']:.2f} 到 {stats_dict['max']:.2f}，"
            summary += f"平均值为 {stats_dict['mean']:.2f}，中位数为 {stats_dict['median']:.2f}。"

            if stats_dict.get('distribution'):
                summary += f"数据呈{stats_dict['distribution']}。"

            return summary

        elif 'unique' in stats_dict:
            # 分类列摘要
            summary = f"该列包含 {stats_dict['count']:,} 个有效值，"
            summary += f"共有 {stats_dict['unique']} 个不同的类别。"

            if stats_dict['top']:
                summary += f"最常见的值是 '{stats_dict['top']}'，"
                summary += f"出现 {stats_dict['top_freq']:,} 次（{stats_dict['top_pct']:.1f}%）。"

            return summary

        elif 'min_date' in stats_dict:
            # 日期列摘要
            summary = f"该列包含 {stats_dict['count']:,} 个有效日期，"
            summary += f"时间范围从 {stats_dict['min_date']} 到 {stats_dict['max_date']}，"
            summary += f"跨度 {stats_dict['range_days']} 天。"

            return summary

        return "无法生成摘要"
