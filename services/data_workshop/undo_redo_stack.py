"""
撤销重做栈

管理操作历史以支持撤销和重做功能
"""

from typing import Dict, Optional, List


class UndoRedoStack:
    """撤销重做栈
    
    职责：
    - 记录操作历史状态
    - 支持撤销和重做
    - 限制历史记录数量
    - 处理分支操作
    """
    
    def __init__(self, max_history: int = 50):
        """初始化撤销重做栈
        
        Args:
            max_history: 最大历史记录数量，默认50
        """
        self.max_history = max_history
        self.history: List[Dict] = []  # 历史状态列表
        self.current_index: int = -1  # 当前位置
    
    def push_state(self, state: Dict):
        """添加新状态
        
        如果当前不在最新位置，清除后续历史
        如果超过最大历史数，删除最早的记录
        
        Args:
            state: 要保存的状态字典
        """
        # 清除当前位置之后的历史（处理分支操作）
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # 添加新状态
        self.history.append(state)
        
        # 限制历史数量
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.current_index += 1
    
    def undo(self) -> Optional[Dict]:
        """撤销操作，返回上一个状态
        
        Returns:
            上一个状态字典，如果无法撤销则返回None
        """
        if self.can_undo():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
    
    def redo(self) -> Optional[Dict]:
        """重做操作，返回下一个状态
        
        Returns:
            下一个状态字典，如果无法重做则返回None
        """
        if self.can_redo():
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def can_undo(self) -> bool:
        """是否可以撤销
        
        Returns:
            True如果可以撤销，否则False
        """
        return self.current_index > 0
    
    def can_redo(self) -> bool:
        """是否可以重做
        
        Returns:
            True如果可以重做，否则False
        """
        return self.current_index < len(self.history) - 1
    
    def get_current_state(self) -> Optional[Dict]:
        """获取当前状态
        
        Returns:
            当前状态字典，如果历史为空则返回None
        """
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None
    
    def clear(self):
        """清空历史"""
        self.history.clear()
        self.current_index = -1
    
    def get_history_size(self) -> int:
        """获取历史记录数量
        
        Returns:
            历史记录数量
        """
        return len(self.history)
