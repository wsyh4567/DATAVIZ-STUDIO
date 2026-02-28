"""
测试撤销重做栈
"""

import pytest
from services.data_workshop.undo_redo_stack import UndoRedoStack


class TestUndoRedoStack:
    """测试UndoRedoStack类"""
    
    def test_initial_state(self):
        """测试初始状态"""
        stack = UndoRedoStack()
        
        assert stack.get_history_size() == 0
        assert stack.current_index == -1
        assert not stack.can_undo()
        assert not stack.can_redo()
        assert stack.get_current_state() is None
    
    def test_push_state(self):
        """测试添加状态"""
        stack = UndoRedoStack()
        
        state1 = {'data': [1, 2, 3]}
        stack.push_state(state1)
        
        assert stack.get_history_size() == 1
        assert stack.current_index == 0
        assert stack.get_current_state() == state1
        assert not stack.can_undo()
        assert not stack.can_redo()
    
    def test_undo(self):
        """测试撤销操作"""
        stack = UndoRedoStack()
        
        state1 = {'data': [1, 2, 3]}
        state2 = {'data': [1, 2, 3, 4]}
        
        stack.push_state(state1)
        stack.push_state(state2)
        
        assert stack.can_undo()
        
        # 撤销到state1
        result = stack.undo()
        assert result == state1
        assert stack.get_current_state() == state1
        assert not stack.can_undo()
        assert stack.can_redo()
    
    def test_redo(self):
        """测试重做操作"""
        stack = UndoRedoStack()
        
        state1 = {'data': [1, 2, 3]}
        state2 = {'data': [1, 2, 3, 4]}
        
        stack.push_state(state1)
        stack.push_state(state2)
        stack.undo()
        
        assert stack.can_redo()
        
        # 重做到state2
        result = stack.redo()
        assert result == state2
        assert stack.get_current_state() == state2
        assert stack.can_undo()
        assert not stack.can_redo()
    
    def test_undo_redo_roundtrip(self):
        """测试撤销重做往返"""
        stack = UndoRedoStack()
        
        state1 = {'data': [1, 2, 3]}
        state2 = {'data': [1, 2, 3, 4]}
        
        stack.push_state(state1)
        stack.push_state(state2)
        
        # 撤销然后重做
        stack.undo()
        result = stack.redo()
        
        assert result == state2
        assert stack.get_current_state() == state2
    
    def test_branch_operation(self):
        """测试分支操作（在历史中间执行新操作）"""
        stack = UndoRedoStack()
        
        state1 = {'data': [1, 2, 3]}
        state2 = {'data': [1, 2, 3, 4]}
        state3 = {'data': [1, 2, 3, 5]}
        
        stack.push_state(state1)
        stack.push_state(state2)
        stack.undo()  # 回到state1
        
        # 在state1之后添加新状态，应该清除state2
        stack.push_state(state3)
        
        assert stack.get_history_size() == 2
        assert stack.get_current_state() == state3
        assert not stack.can_redo()  # state2应该被清除
    
    def test_max_history_limit(self):
        """测试历史记录数量限制"""
        stack = UndoRedoStack(max_history=3)
        
        # 添加4个状态
        for i in range(4):
            stack.push_state({'data': [i]})
        
        # 应该只保留最近的3个
        assert stack.get_history_size() == 3
        assert stack.get_current_state() == {'data': [3]}
        
        # 最早的状态应该被删除
        stack.undo()
        stack.undo()
        assert stack.get_current_state() == {'data': [1]}
    
    def test_clear(self):
        """测试清空历史"""
        stack = UndoRedoStack()
        
        stack.push_state({'data': [1]})
        stack.push_state({'data': [2]})
        
        stack.clear()
        
        assert stack.get_history_size() == 0
        assert stack.current_index == -1
        assert not stack.can_undo()
        assert not stack.can_redo()
    
    def test_undo_at_start(self):
        """测试在起始位置撤销"""
        stack = UndoRedoStack()
        
        stack.push_state({'data': [1]})
        
        # 无法撤销
        result = stack.undo()
        assert result is None
        assert not stack.can_undo()
    
    def test_redo_at_end(self):
        """测试在末尾位置重做"""
        stack = UndoRedoStack()
        
        stack.push_state({'data': [1]})
        stack.push_state({'data': [2]})
        
        # 无法重做
        result = stack.redo()
        assert result is None
        assert not stack.can_redo()
    
    def test_multiple_undo_redo(self):
        """测试多次撤销和重做"""
        stack = UndoRedoStack()
        
        states = [{'data': [i]} for i in range(5)]
        for state in states:
            stack.push_state(state)
        
        # 撤销3次
        stack.undo()
        stack.undo()
        stack.undo()
        assert stack.get_current_state() == states[1]
        
        # 重做2次
        stack.redo()
        stack.redo()
        assert stack.get_current_state() == states[3]
