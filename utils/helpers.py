# -*- coding: utf-8 -*-
"""DataViz Studio — 工具函数"""

from __future__ import annotations


def format_size(size_bytes: int | float) -> str:
    """将字节数转化为可读格式。"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def format_number(n: int | float) -> str:
    """千分位格式化数字。"""
    if isinstance(n, float):
        return f"{n:,.2f}"
    return f"{n:,}"
