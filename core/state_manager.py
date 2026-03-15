# -*- coding: utf-8 -*-
"""DataViz Studio — 状态管理器

提供 dcc.Store 的初始化和全局状态结构。
"""

from __future__ import annotations

from typing import Any


def get_initial_state() -> dict[str, Any]:
    """返回应用初始化时的全局状态。"""
    return {
        "theme": "dark",
        "sidebar_collapsed": False,
        "active_dataset": None,
        "datasets": [],         # list of dataset names
        "last_action": None,    # description of the most recent action
        "toast": None,          # {"message": str, "type": "success"|"error"|"warning"|"info"}
    }
