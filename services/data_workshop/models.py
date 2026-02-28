"""
数据工坊数据模型

定义核心数据结构
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List
import pandas as pd


@dataclass
class Operation:
    """数据操作对象
    
    表示单个数据转换操作的完整信息
    """
    step_id: str
    operation: str  # 操作类型
    params: Dict[str, Any]  # 操作参数
    timestamp: datetime
    affected_rows: int = 0
    affected_cols: int = 0
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典
        
        Returns:
            包含所有字段的字典，timestamp转换为ISO格式字符串
        """
        return {
            'step_id': self.step_id,
            'operation': self.operation,
            'params': self.params,
            'timestamp': self.timestamp.isoformat(),
            'affected_rows': self.affected_rows,
            'affected_cols': self.affected_cols,
            'execution_time': self.execution_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Operation':
        """从字典创建Operation对象
        
        Args:
            data: 包含操作信息的字典
            
        Returns:
            Operation对象
        """
        return cls(
            step_id=data['step_id'],
            operation=data['operation'],
            params=data['params'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            affected_rows=data.get('affected_rows', 0),
            affected_cols=data.get('affected_cols', 0),
            execution_time=data.get('execution_time', 0.0)
        )


@dataclass
class PreviewResult:
    """预览结果对象
    
    包含预览数据和相关统计信息
    """
    preview_df: pd.DataFrame  # 预览数据（限制行数）
    full_rows: int  # 完整结果行数
    full_cols: int  # 完整结果列数
    affected_rows: int  # 本次操作影响的行数
    affected_cols: int  # 本次操作影响的列数
    execution_time: float  # 执行时间（秒）
    is_truncated: bool  # 是否被截断
    
    def to_dict(self) -> Dict:
        """转换为字典（用于JSON传输）
        
        Returns:
            包含预览数据和统计信息的字典
        """
        return {
            'preview_data': self.preview_df.to_dict('records'),
            'columns': list(self.preview_df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.preview_df.dtypes.items()},
            'full_rows': self.full_rows,
            'full_cols': self.full_cols,
            'affected_rows': self.affected_rows,
            'affected_cols': self.affected_cols,
            'execution_time': self.execution_time,
            'is_truncated': self.is_truncated
        }


@dataclass
class ColumnAnalysis:
    """列分析结果"""
    name: str
    dtype: str
    missing_count: int
    missing_percent: float
    unique_count: int
    duplicate_count: int
    statistics: Optional[Dict] = None  # 数值列统计
    patterns: Optional[Dict] = None  # 文本列模式
    issues: List[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """数据质量报告对象
    
    包含数据集的完整质量分析结果
    """
    total_rows: int
    total_cols: int
    memory_usage: str
    columns: List[ColumnAnalysis]
    overall_issues: List[str]
    recommendations: List[Dict]
    
    def to_dict(self) -> Dict:
        """转换为字典
        
        Returns:
            包含完整质量报告的字典
        """
        return {
            'total_rows': self.total_rows,
            'total_cols': self.total_cols,
            'memory_usage': self.memory_usage,
            'columns': [asdict(col) for col in self.columns],
            'overall_issues': self.overall_issues,
            'recommendations': self.recommendations
        }
