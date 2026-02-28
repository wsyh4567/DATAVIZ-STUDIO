"""
类型检测器

智能检测和建议数据类型转换
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


# 常见日期格式
_DATE_FORMATS = [
    '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y',
    '%m-%d-%Y', '%m/%d/%Y', '%Y%m%d',
    '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
    '%d-%m-%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S',
    '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ',
]

# 布尔值映射
_BOOLEAN_VALUES = {
    'true', 'false', 'yes', 'no', 'y', 'n',
    '1', '0', 't', 'f',
    '是', '否', '对', '错',
    'TRUE', 'FALSE', 'True', 'False',
    'Yes', 'No', 'Y', 'N',
}

_BOOLEAN_TRUE = {'true', 'yes', 'y', '1', 't', '是', '对', 'TRUE', 'True', 'Yes', 'Y', 'T'}


class TypeDetector:
    """类型检测器

    职责：
    - 检测列的实际数据类型
    - 识别类型不匹配
    - 建议类型转换
    """

    def __init__(self):
        pass

    def detect_column_type(self, series: pd.Series) -> Dict:
        """检测列的数据类型"""
        current_type = str(series.dtype)
        clean = series.dropna()

        if len(clean) == 0:
            return {
                'current_type': current_type,
                'detected_type': current_type,
                'confidence': 0.0,
                'mismatch': False,
                'suggestion': None,
            }

        # 如果已经是数值/日期/布尔，直接返回
        if pd.api.types.is_numeric_dtype(series):
            return {
                'current_type': current_type,
                'detected_type': current_type,
                'confidence': 1.0,
                'mismatch': False,
                'suggestion': None,
            }

        if pd.api.types.is_datetime64_any_dtype(series):
            return {
                'current_type': current_type,
                'detected_type': 'datetime64',
                'confidence': 1.0,
                'mismatch': False,
                'suggestion': None,
            }

        if pd.api.types.is_bool_dtype(series):
            return {
                'current_type': current_type,
                'detected_type': 'bool',
                'confidence': 1.0,
                'mismatch': False,
                'suggestion': None,
            }

        # 对于 object/string 类型，尝试推断
        is_num, num_conf = self.is_numeric_string(series)
        is_date, date_conf, date_fmt = self.is_date_string(series)
        is_bool, bool_conf = self.is_boolean_string(series)

        # 选择最高置信度的类型
        candidates = []
        if is_num:
            candidates.append(('float64', num_conf, 'numeric'))
        if is_date:
            candidates.append(('datetime64', date_conf, 'datetime'))
        if is_bool:
            candidates.append(('bool', bool_conf, 'bool'))

        if not candidates:
            return {
                'current_type': current_type,
                'detected_type': 'object',
                'confidence': 1.0,
                'mismatch': False,
                'suggestion': None,
            }

        # 按置信度排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_type, best_conf, best_kind = candidates[0]

        suggestion = self.suggest_conversion(series) if best_conf >= 0.8 else None

        return {
            'current_type': current_type,
            'detected_type': best_type,
            'confidence': best_conf,
            'mismatch': True,
            'suggestion': suggestion,
        }

    def is_numeric_string(self, series: pd.Series) -> Tuple[bool, float]:
        """检测是否为数值字符串"""
        clean = series.dropna()
        if len(clean) == 0:
            return False, 0.0

        converted = pd.to_numeric(clean, errors='coerce')
        success = converted.notna().sum()
        total = len(clean)
        confidence = success / max(total, 1)

        # 判定是否为整数
        is_integer = False
        if confidence > 0.8:
            valid = converted.dropna()
            if len(valid) > 0 and (valid == valid.astype(int)).all():
                is_integer = True

        return confidence >= 0.8, round(confidence, 3)

    def is_date_string(self, series: pd.Series) -> Tuple[bool, float, Optional[str]]:
        """检测是否为日期字符串"""
        clean = series.dropna().astype(str)
        if len(clean) == 0:
            return False, 0.0, None

        sample = clean.head(100)  # 仅检测前100个值以提高速度
        total = len(sample)

        best_format = None
        best_count = 0

        for fmt in _DATE_FORMATS:
            success = 0
            for val in sample:
                try:
                    pd.to_datetime(val.strip(), format=fmt)
                    success += 1
                except (ValueError, TypeError):
                    pass
            if success > best_count:
                best_count = success
                best_format = fmt

        confidence = best_count / max(total, 1)

        # 也尝试 pandas 自动解析
        if confidence < 0.8:
            try:
                parsed = pd.to_datetime(sample, errors='coerce', infer_datetime_format=True)
                auto_conf = parsed.notna().sum() / max(total, 1)
                if auto_conf > confidence:
                    confidence = auto_conf
                    best_format = 'auto'
            except Exception:
                pass

        return confidence >= 0.8, round(confidence, 3), best_format

    def is_boolean_string(self, series: pd.Series) -> Tuple[bool, float]:
        """检测是否为布尔字符串"""
        clean = series.dropna().astype(str).str.strip()
        if len(clean) == 0:
            return False, 0.0

        unique = set(clean.unique())
        # 完美匹配：仅包含两个值且都是已知布尔值
        if len(unique) <= 2 and unique.issubset(_BOOLEAN_VALUES):
            return True, 1.0

        # 部分匹配
        match_count = sum(1 for v in clean if v in _BOOLEAN_VALUES)
        confidence = match_count / max(len(clean), 1)
        return confidence >= 0.9, round(confidence, 3)

    def suggest_conversion(self, series: pd.Series) -> Optional[Dict]:
        """建议类型转换"""
        clean = series.dropna()
        if len(clean) == 0:
            return None

        # 检查数值
        is_num, num_conf = self.is_numeric_string(series)
        if is_num and num_conf >= 0.8:
            converted = pd.to_numeric(clean, errors='coerce')
            failures = int(converted.isna().sum())
            # 判断整数还是浮点
            valid = converted.dropna()
            if len(valid) > 0 and (valid == valid.astype(int)).all():
                target = 'int64'
                code = f"df['{series.name}'] = pd.to_numeric(df['{series.name}'], errors='coerce').astype('Int64')"
            else:
                target = 'float64'
                code = f"df['{series.name}'] = pd.to_numeric(df['{series.name}'], errors='coerce')"
            return {
                'target_type': target,
                'conversion_code': code,
                'expected_failures': failures,
                'confidence': num_conf,
            }

        # 检查日期
        is_date, date_conf, date_fmt = self.is_date_string(series)
        if is_date and date_conf >= 0.8:
            try:
                converted = pd.to_datetime(clean, errors='coerce')
                failures = int(converted.isna().sum())
            except Exception:
                failures = len(clean)
            if date_fmt and date_fmt != 'auto':
                code = f"df['{series.name}'] = pd.to_datetime(df['{series.name}'], format='{date_fmt}', errors='coerce')"
            else:
                code = f"df['{series.name}'] = pd.to_datetime(df['{series.name}'], errors='coerce')"
            return {
                'target_type': 'datetime64',
                'conversion_code': code,
                'expected_failures': failures,
                'confidence': date_conf,
            }

        # 检查布尔
        is_bool, bool_conf = self.is_boolean_string(series)
        if is_bool and bool_conf >= 0.9:
            code = f"df['{series.name}'] = df['{series.name}'].map({{'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False, '是': True, '否': False}})"
            return {
                'target_type': 'bool',
                'conversion_code': code,
                'expected_failures': 0,
                'confidence': bool_conf,
            }

        return None

    def detect_all(self, df: pd.DataFrame) -> List[Dict]:
        """检测数据框所有列的类型"""
        results = []
        for col in df.columns:
            detection = self.detect_column_type(df[col])
            detection['column'] = col
            results.append(detection)
        return results

    def get_mismatched_columns(self, df: pd.DataFrame) -> List[Dict]:
        """获取类型不匹配的列"""
        all_results = self.detect_all(df)
        return [r for r in all_results if r['mismatch'] and r['suggestion']]
