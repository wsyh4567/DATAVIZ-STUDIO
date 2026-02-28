"""
预览引擎

负责实时计算和显示数据变化
"""

import pandas as pd
import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple
from .operation_executor import OperationExecutor
from .models import PreviewResult


class PreviewEngine:
    """实时预览引擎
    
    职责：
    - 执行操作流水线生成预览数据
    - 限制预览行数以保证性能
    - 计算操作影响统计
    - 支持异步计算和取消
    """
    
    def __init__(self, max_preview_rows: int = 1000):
        """初始化预览引擎
        
        Args:
            max_preview_rows: 最大预览行数，默认1000
        """
        self.max_preview_rows = max_preview_rows
        self.cache: Dict[str, PreviewResult] = {}  # 步骤结果缓存
        self.cancel_flag = False
        self.executor = OperationExecutor()
    
    def compute_preview(
        self,
        df: pd.DataFrame,
        pipeline: List[Dict],
        up_to_step: Optional[int] = None
    ) -> Dict:
        """计算预览数据
        
        Args:
            df: 原始数据框
            pipeline: 操作流水线
            up_to_step: 执行到第几步（None表示全部）
        
        Returns:
            {
                'preview_df': 预览数据框（限制行数）,
                'full_rows': 完整结果行数,
                'full_cols': 完整结果列数,
                'affected_rows': 本次操作影响的行数,
                'affected_cols': 本次操作影响的列数,
                'execution_time': 执行时间（秒）
            }
        """
        start_time = time.time()
        
        # 确定要执行的步骤
        if up_to_step is not None:
            steps_to_execute = pipeline[:up_to_step + 1]
        else:
            steps_to_execute = pipeline
        
        # 如果没有步骤，直接返回原始数据
        if not steps_to_execute:
            preview_df = df.head(self.max_preview_rows).copy()
            return {
                'preview_df': preview_df,
                'full_rows': len(df),
                'full_cols': len(df.columns),
                'affected_rows': 0,
                'affected_cols': 0,
                'execution_time': time.time() - start_time,
                'is_truncated': len(df) > self.max_preview_rows
            }
        
        # 检查缓存
        cache_key = self._get_cache_key(df, steps_to_execute)
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            return {
                'preview_df': cached_result.preview_df,
                'full_rows': cached_result.full_rows,
                'full_cols': cached_result.full_cols,
                'affected_rows': cached_result.affected_rows,
                'affected_cols': cached_result.affected_cols,
                'execution_time': cached_result.execution_time,
                'is_truncated': cached_result.is_truncated
            }
        
        # 执行操作流水线
        result_df = df.copy()
        original_rows = len(df)
        original_cols = len(df.columns)
        
        for step in steps_to_execute:
            if self.cancel_flag:
                self.cancel_flag = False
                return None
            
            try:
                result_df, _ = self.executor.execute(
                    result_df,
                    step['operation'],
                    step['params']
                )
            except Exception as e:
                # 操作失败，返回错误信息
                return {
                    'error': str(e),
                    'failed_step': step
                }
        
        # 计算影响统计
        affected_rows = abs(len(result_df) - original_rows)
        affected_cols = abs(len(result_df.columns) - original_cols)
        
        # 限制预览行数
        preview_df = result_df.head(self.max_preview_rows).copy()
        is_truncated = len(result_df) > self.max_preview_rows
        
        execution_time = time.time() - start_time
        
        # 创建预览结果
        preview_result = PreviewResult(
            preview_df=preview_df,
            full_rows=len(result_df),
            full_cols=len(result_df.columns),
            affected_rows=affected_rows,
            affected_cols=affected_cols,
            execution_time=execution_time,
            is_truncated=is_truncated
        )
        
        # 缓存结果
        self.cache[cache_key] = preview_result
        
        return {
            'preview_df': preview_df,
            'full_rows': len(result_df),
            'full_cols': len(result_df.columns),
            'affected_rows': affected_rows,
            'affected_cols': affected_cols,
            'execution_time': execution_time,
            'is_truncated': is_truncated
        }
    
    def compute_with_timeout(
        self,
        df: pd.DataFrame,
        pipeline: List[Dict],
        timeout: float = 3.0
    ) -> Optional[Dict]:
        """带超时的预览计算
        
        Args:
            df: 原始数据框
            pipeline: 操作流水线
            timeout: 超时时间（秒）
        
        Returns:
            预览结果或None（超时）
        """
        import threading
        
        result = [None]
        
        def compute():
            result[0] = self.compute_preview(df, pipeline)
        
        thread = threading.Thread(target=compute)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            self.cancel_flag = True
            thread.join()
            return None
        
        return result[0]
    
    def cancel_computation(self):
        """取消当前计算"""
        self.cancel_flag = True
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
    
    def _get_cache_key(self, df: pd.DataFrame, pipeline: List[Dict]) -> str:
        """生成缓存键
        
        Args:
            df: 数据框
            pipeline: 操作流水线
        
        Returns:
            缓存键字符串
        """
        # 使用数据框的哈希和流水线的JSON表示生成缓存键
        try:
            df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()
        except:
            # 如果哈希失败，使用数据框的形状和列名
            df_hash = hashlib.md5(f"{df.shape}_{list(df.columns)}".encode()).hexdigest()
        
        pipeline_str = json.dumps(pipeline, sort_keys=True, default=str)
        pipeline_hash = hashlib.md5(pipeline_str.encode()).hexdigest()
        
        return f"{df_hash}_{pipeline_hash}"
